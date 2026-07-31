#!/usr/bin/env node

/**
 * Publish or schedule the approved Lajora editorial queue through the logged-in
 * Instagram web composer. Chrome must be running with
 * `--remote-debugging-port=9222`.
 *
 * Examples:
 *   node scripts/instagram_cdp_publish.mjs publish 2 9
 *   node scripts/instagram_cdp_publish.mjs schedule 10 30
 */

import fs from "node:fs";
import path from "node:path";

const ROOT = "/Users/coong/Documents/lajora-social-30days";
const PLAN_PATH =
  process.env.INSTAGRAM_PLAN_PATH || path.join(ROOT, "content-plan.json");
const STATE_PATH =
  process.env.INSTAGRAM_PROGRESS_PATH ||
  path.join(ROOT, "editorial-v4-mixed", "instagram-browser-progress.json");
const CDP_PORT = Number(process.env.INSTAGRAM_CDP_PORT || 9222);
const CDP_LIST = `http://127.0.0.1:${CDP_PORT}/json/list`;
const PROFILE_URL = "https://www.instagram.com/lajora.brands/";
const WAIT_STEP_MS = 500;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

class Cdp {
  constructor(target) {
    this.target = target;
    this.ws = null;
    this.nextId = 0;
    this.pending = new Map();
  }

  async connect() {
    this.ws = new WebSocket(this.target.webSocketDebuggerUrl);
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (!message.id || !this.pending.has(message.id)) return;
      const { resolve, reject } = this.pending.get(message.id);
      this.pending.delete(message.id);
      if (message.error) reject(new Error(JSON.stringify(message.error)));
      else resolve(message.result);
    };
    await new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });
  }

  close() {
    this.ws?.close();
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.nextId;
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async eval(expression) {
    const result = await this.send("Runtime.evaluate", {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (result.exceptionDetails) {
      throw new Error(
        result.exceptionDetails.exception?.description ||
          result.exceptionDetails.text ||
          "Runtime.evaluate failed",
      );
    }
    return result.result.value;
  }
}

async function waitFor(check, description, timeoutMs = 45_000) {
  const started = Date.now();
  let lastValue;
  while (Date.now() - started < timeoutMs) {
    try {
      lastValue = await check();
      if (lastValue) return lastValue;
    } catch {
      // React may replace the document while a navigation is settling.
    }
    await sleep(WAIT_STEP_MS);
  }
  throw new Error(
    `Timed out waiting for ${description}; last=${JSON.stringify(lastValue)}`,
  );
}

async function bodyText(cdp) {
  return (await cdp.eval("document.body?.innerText || ''")) || "";
}

async function dialogTexts(cdp) {
  return JSON.parse(
    (await cdp.eval(
      "JSON.stringify([...document.querySelectorAll('[role=dialog]')].map(d => d.innerText))",
    )) || "[]",
  );
}

async function lastDialogText(cdp) {
  const dialogs = await dialogTexts(cdp);
  return dialogs.at(-1) || "";
}

async function clickExact(cdp, text, { lastDialog = false } = {}) {
  const expression = `(() => {
    const root = ${
      lastDialog
        ? "[...document.querySelectorAll('[role=dialog]')].at(-1)"
        : "document"
    };
    if (!root) return "NO_ROOT";
    const nodes = [...root.querySelectorAll('button,[role=button],a,[role=link]')];
    const node = nodes.find(x => (x.innerText || '').trim() === ${JSON.stringify(text)});
    if (!node) return "NOT_FOUND";
    node.click();
    return "CLICKED";
  })()`;
  const result = await cdp.eval(expression);
  if (result !== "CLICKED") {
    throw new Error(`Could not click exact text ${JSON.stringify(text)}: ${result}`);
  }
}

async function navigate(cdp, url) {
  await cdp.send("Page.navigate", { url });
  await waitFor(
    async () => (await cdp.eval("document.readyState")) === "complete",
    `document complete at ${url}`,
  );
}

async function openComposer(cdp) {
  await navigate(cdp, PROFILE_URL);
  await waitFor(
    async () => (await bodyText(cdp)).includes("Edit profile"),
    "logged-in Lajora profile",
    60_000,
  );

  const newPostResult = await cdp.eval(`(() => {
    const icon = document.querySelector('svg[aria-label="New post"]');
    if (!icon) return "NO_ICON";
    let node = icon;
    while (node && node !== document.body) {
      if (
        node.tagName === "A" ||
        node.getAttribute("role") === "button" ||
        node.getAttribute("role") === "link"
      ) {
        node.click();
        return "CLICKED";
      }
      node = node.parentElement;
    }
    return "NO_PARENT";
  })()`);
  if (newPostResult !== "CLICKED") {
    throw new Error(`New post menu failed: ${newPostResult}`);
  }

  await waitFor(
    async () => {
      const text = await bodyText(cdp);
      return text.includes("Live video") && text.includes("Post");
    },
    "New post menu",
  );
  await clickExact(cdp, "Post");
  await waitFor(
    async () => (await lastDialogText(cdp)).includes("Select from computer"),
    "Instagram upload dialog",
  );
}

async function setComposerFile(cdp, filePath) {
  const document = await cdp.send("DOM.getDocument", {
    depth: -1,
    pierce: true,
  });
  const matches = await cdp.send("DOM.querySelectorAll", {
    nodeId: document.root.nodeId,
    selector: 'input[type="file"]',
  });

  let uploadNodeId = null;
  for (const nodeId of matches.nodeIds) {
    const attrsResult = await cdp.send("DOM.getAttributes", { nodeId });
    const attrs = Object.fromEntries(
      Array.from({ length: attrsResult.attributes.length / 2 }, (_, index) => [
        attrsResult.attributes[index * 2],
        attrsResult.attributes[index * 2 + 1],
      ]),
    );
    if (
      String(attrs.accept || "").includes("video/mp4") &&
      Object.hasOwn(attrs, "multiple")
    ) {
      uploadNodeId = nodeId;
    }
  }

  if (!uploadNodeId) throw new Error("Instagram composer file input not found");
  await cdp.send("DOM.setFileInputFiles", {
    files: [filePath],
    nodeId: uploadNodeId,
  });
  await waitFor(
    async () => {
      const text = await lastDialogText(cdp);
      return text.includes("Crop") && text.includes("Next");
    },
    `crop screen for ${path.basename(filePath)}`,
  );
}

async function advanceToCaption(cdp) {
  await clickExact(cdp, "Next", { lastDialog: true });
  await waitFor(
    async () => {
      const text = await lastDialogText(cdp);
      return text.includes("Edit") && text.includes("Filters");
    },
    "Instagram edit screen",
  );
  await clickExact(cdp, "Next", { lastDialog: true });
  await waitFor(
    async () =>
      await cdp.eval(
        `Boolean(document.querySelector(
          '[role=dialog] [contenteditable=true][aria-label="Write a caption..."]'
        ))`,
      ),
    "Instagram caption editor",
  );
}

async function fillCaption(cdp, caption) {
  const focusResult = await cdp.eval(`(() => {
    const node = document.querySelector(
      '[role=dialog] [contenteditable=true][aria-label="Write a caption..."]'
    );
    if (!node) return "NO_BOX";
    node.focus();
    return "FOCUSED";
  })()`);
  if (focusResult !== "FOCUSED") {
    throw new Error(`Caption focus failed: ${focusResult}`);
  }
  await cdp.send("Input.insertText", { text: caption });
  await waitFor(
    async () =>
      Number(
        await cdp.eval(
          `document.querySelector(
            '[role=dialog] [contenteditable=true][aria-label="Write a caption..."]'
          )?.innerText.length || 0`,
        ),
      ) >= Math.min(caption.length - 4, 20),
    "caption insertion",
  );
}

async function commitCaptionForImmediatePublish(cdp, caption) {
  const blurResult = await cdp.eval(`(() => {
    const node = document.querySelector(
      '[role=dialog] [contenteditable=true][aria-label="Write a caption..."]'
    );
    if (!node) return "NO_BOX";
    node.blur();
    return "BLURRED";
  })()`);
  if (blurResult !== "BLURRED") {
    throw new Error(`Caption blur failed: ${blurResult}`);
  }
  await sleep(1_500);

  // Toggling the native scheduling control forces Instagram's composer to
  // commit its current Lexical caption state before an immediate share.
  await enableScheduling(cdp);
  const disableResult = await cdp.eval(`(() => {
    const dialog = [...document.querySelectorAll('[role=dialog]')].at(-1);
    const toggle = dialog?.querySelector('input[role=switch][type=checkbox]');
    if (!toggle) return "NO_TOGGLE";
    if (toggle.getAttribute("aria-checked") === "true") toggle.click();
    return "DISABLED";
  })()`);
  if (disableResult !== "DISABLED") {
    throw new Error(`Schedule toggle reset failed: ${disableResult}`);
  }
  await waitFor(
    async () =>
      (await cdp.eval(
        `document.querySelector(
          '[role=dialog] input[role=switch][type=checkbox]'
        )?.getAttribute('aria-checked')`,
      )) === "false",
    "schedule toggle reset",
  );
  await sleep(1_500);

  const actual = await cdp.eval(`document.querySelector(
    '[role=dialog] [contenteditable=true][aria-label="Write a caption..."]'
  )?.innerText || ""`);
  if (!String(actual).includes(caption.slice(0, 40))) {
    throw new Error("Caption disappeared before immediate publish");
  }
}

async function publishCurrentComposer(cdp) {
  await clickExact(cdp, "Share", { lastDialog: true });
  await waitFor(
    async () =>
      (await dialogTexts(cdp)).some((text) =>
        text.includes("Your post has been shared."),
      ),
    "Instagram post shared confirmation",
    90_000,
  );
  await sleep(8_000);
}

async function enableScheduling(cdp) {
  const result = await cdp.eval(`(() => {
    const dialog = [...document.querySelectorAll('[role=dialog]')].at(-1);
    const toggle = dialog?.querySelector('input[role=switch][type=checkbox]');
    if (!toggle) return "NO_TOGGLE";
    if (toggle.getAttribute("aria-checked") !== "true") toggle.click();
    return "ENABLED";
  })()`);
  if (result !== "ENABLED") {
    throw new Error(`Schedule toggle failed: ${result}`);
  }
  await waitFor(
    async () =>
      (await cdp.eval(
        `document.querySelector(
          '[role=dialog] input[role=switch][type=checkbox]'
        )?.getAttribute('aria-checked')`,
      )) === "true",
    "schedule toggle",
  );
}

function desiredMonthHeader(dateString) {
  const [year, month] = dateString.split("-").map(Number);
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(year, month - 1, 15)));
}

async function setScheduleDate(cdp, dateString) {
  const [year, month, day] = dateString.split("-").map(Number);
  const desiredHeader = desiredMonthHeader(dateString);
  const openResult = await cdp.eval(`(() => {
    const dialog = [...document.querySelectorAll('[role=dialog]')].at(-1);
    const button = dialog?.querySelector('[role=button][aria-haspopup=dialog]');
    if (!button) return "NO_DATE_BUTTON";
    button.click();
    return "OPENED";
  })()`);
  if (openResult !== "OPENED") {
    throw new Error(`Date picker failed: ${openResult}`);
  }

  await waitFor(
    async () =>
      await cdp.eval("Boolean(document.querySelector('[role=grid]'))"),
    "date grid",
  );

  for (let turn = 0; turn < 18; turn += 1) {
    const header = await cdp.eval(
      `([...document.querySelectorAll('[role=dialog]')].at(-1)?.innerText || "")
        .split("\\n")[0]`,
    );
    if (header === desiredHeader) break;
    const [currentMonth, currentYear] = header.split(" ");
    const current = new Date(
      `${currentMonth} 15, ${currentYear} 12:00:00Z`,
    );
    const desired = new Date(Date.UTC(year, month - 1, 15));
    const direction =
      Number.isNaN(current.getTime()) || current < desired
        ? "Next month"
        : "Previous month";
    const clicked = await cdp.eval(`(() => {
      const button = document.querySelector(
        'button[aria-label=${JSON.stringify(direction)}]'
      );
      if (!button || button.disabled) return "NO_MONTH_BUTTON";
      button.click();
      return "CLICKED";
    })()`);
    if (clicked !== "CLICKED") {
      throw new Error(`Month navigation failed: ${clicked}`);
    }
    await sleep(250);
  }

  const selected = await cdp.eval(`(() => {
    const cell = [...document.querySelectorAll('[role=gridcell]')].find(
      node =>
        (node.innerText || '').trim() === ${JSON.stringify(String(day))} &&
        node.getAttribute('aria-disabled') === 'false'
    );
    if (!cell) return "NO_DAY";
    cell.click();
    return "SELECTED";
  })()`);
  if (selected !== "SELECTED") {
    throw new Error(`Date selection failed for ${dateString}: ${selected}`);
  }
  await waitFor(
    async () =>
      !(await cdp.eval("Boolean(document.querySelector('[role=grid]'))")),
    "date picker close",
  );
}

async function spinValue(cdp, label) {
  return Number(
    await cdp.eval(
      `document.querySelector(
        'input[role=spinbutton][aria-label=${JSON.stringify(label)}]'
      )?.getAttribute('aria-valuenow')`,
    ),
  );
}

async function pressSpinArrow(cdp, label, direction) {
  const keyCode = direction === "ArrowUp" ? 38 : 40;
  const result = await cdp.eval(`(() => {
    const input = document.querySelector(
      'input[role=spinbutton][aria-label=${JSON.stringify(label)}]'
    );
    if (!input) return "NO_SPIN";
    input.focus();
    for (const type of ["keydown", "keyup"]) {
      input.dispatchEvent(new KeyboardEvent(type, {
        key: ${JSON.stringify(direction)},
        code: ${JSON.stringify(direction)},
        keyCode: ${keyCode},
        which: ${keyCode},
        bubbles: true,
        cancelable: true
      }));
    }
    return "PRESSED";
  })()`);
  if (result !== "PRESSED") {
    throw new Error(`Spin control ${label} failed: ${result}`);
  }
}

async function setSpinValue(cdp, label, target, min, max) {
  const size = max - min + 1;
  for (let iteration = 0; iteration < size + 2; iteration += 1) {
    const current = await spinValue(cdp, label);
    if (current === target) return;
    if (!Number.isFinite(current)) {
      throw new Error(`Spin control ${label} has no numeric value`);
    }
    const upDistance = (target - current + size) % size;
    const downDistance = (current - target + size) % size;
    const direction = upDistance <= downDistance ? "ArrowUp" : "ArrowDown";
    const expected =
      direction === "ArrowUp"
        ? current === max
          ? min
          : current + 1
        : current === min
          ? max
          : current - 1;
    await pressSpinArrow(cdp, label, direction);
    await waitFor(
      async () => (await spinValue(cdp, label)) === expected,
      `${label} to move from ${current} to ${expected}`,
      3_000,
    );
  }
  throw new Error(`Could not set ${label} to ${target}`);
}

async function setScheduleTime(cdp, timeWib) {
  const [hour24, minute] = timeWib.split(":").map(Number);
  const hour12 = hour24 % 12 || 12;
  const amPm = hour24 >= 12 ? 1 : 0;
  await setSpinValue(cdp, "Hours", hour12, 1, 12);
  await setSpinValue(cdp, "Minutes", minute, 0, 59);
  await setSpinValue(cdp, "AM PM", amPm, 0, 1);
}

async function scheduleCurrentComposer(cdp, post) {
  await enableScheduling(cdp);
  await setScheduleDate(cdp, post.date);
  await setScheduleTime(cdp, post.time_wib);

  const values = {
    hours: await spinValue(cdp, "Hours"),
    minutes: await spinValue(cdp, "Minutes"),
    amPm: await spinValue(cdp, "AM PM"),
  };
  const hour24 = Number(post.time_wib.slice(0, 2));
  const expected = {
    hours: hour24 % 12 || 12,
    minutes: Number(post.time_wib.slice(3, 5)),
    amPm: hour24 >= 12 ? 1 : 0,
  };
  if (JSON.stringify(values) !== JSON.stringify(expected)) {
    throw new Error(
      `Schedule time mismatch for ${post.id}: ${JSON.stringify(values)}`,
    );
  }

  await clickExact(cdp, "Schedule", { lastDialog: true });
  const confirmation = await waitFor(
    async () => {
      const dialogs = await dialogTexts(cdp);
      if (
        dialogs.some((text) =>
          text.includes("Your post has been scheduled."),
        )
      ) {
        return "SCHEDULED";
      }
      if (
        dialogs.some((text) =>
          text.includes("Your post could not be scheduled."),
        )
      ) {
        return "ERROR";
      }
      return false;
    },
    `scheduled confirmation for post ${post.id}`,
    90_000,
  );
  if (confirmation === "ERROR") {
    throw new Error(`Instagram rejected schedule for post ${post.id}`);
  }
}

async function latestProfilePost(cdp) {
  await navigate(cdp, PROFILE_URL);
  return waitFor(
    async () => {
      const raw = await cdp.eval(`JSON.stringify({
        text: document.body?.innerText?.slice(0, 700) || "",
        links: [...document.querySelectorAll('a[href*="/p/"]')].map(a => a.href)
      })`);
      if (!raw) return false;
      const result = JSON.parse(raw);
      return result.links.length ? result : false;
    },
    "published post on Lajora profile",
    60_000,
  );
}

async function verifyLiveCaption(cdp, instagramUrl, caption) {
  await navigate(cdp, instagramUrl);
  const expected = caption.slice(0, 48);
  return waitFor(
    async () => {
      const text = await bodyText(cdp);
      return text.includes(expected) ? true : false;
    },
    `live caption at ${instagramUrl}`,
    60_000,
  );
}

function loadState() {
  if (!fs.existsSync(STATE_PATH)) {
    return {
      username: "lajora.brands",
      cdp_port: CDP_PORT,
      published: [],
      scheduled: [],
    };
  }
  return JSON.parse(fs.readFileSync(STATE_PATH, "utf8"));
}

function saveState(state) {
  state.updated_at = new Date().toISOString();
  fs.writeFileSync(STATE_PATH, `${JSON.stringify(state, null, 2)}\n`);
}

async function publishRange(cdp, posts, startId, endId) {
  const state = loadState();
  for (const post of posts.filter(
    (item) => item.id >= startId && item.id <= endId,
  )) {
    if (state.published.some((item) => item.id === post.id)) {
      console.log(`[${post.id}] already recorded as published; skip`);
      continue;
    }

    const filePath = path.join(ROOT, post.asset);
    console.log(`[${post.id}] composing ${path.basename(filePath)}`);
    await openComposer(cdp);
    await setComposerFile(cdp, filePath);
    await advanceToCaption(cdp);
    await fillCaption(cdp, post.final_caption);
    await commitCaptionForImmediatePublish(cdp, post.final_caption);
    await publishCurrentComposer(cdp);
    const profile = await latestProfilePost(cdp);
    const instagramUrl = profile.links[0];
    await verifyLiveCaption(cdp, instagramUrl, post.final_caption);
    state.published.push({
      id: post.id,
      instagram_url: instagramUrl,
      caption_verified: true,
      confirmed: true,
      published_at: new Date().toISOString(),
    });
    saveState(state);
    console.log(
      `[${post.id}] published: ${instagramUrl} | ${profile.text.split("\n")[2] || ""}`,
    );
    await sleep(2_000);
  }
}

async function scheduleRange(cdp, posts, startId, endId) {
  const state = loadState();
  for (const post of posts.filter(
    (item) => item.id >= startId && item.id <= endId,
  )) {
    if (state.scheduled.some((item) => item.id === post.id)) {
      console.log(`[${post.id}] already recorded as scheduled; skip`);
      continue;
    }

    const filePath = path.join(ROOT, post.asset);
    console.log(
      `[${post.id}] scheduling ${path.basename(filePath)} at ${post.date} ${post.time_wib} WIB`,
    );
    await openComposer(cdp);
    await setComposerFile(cdp, filePath);
    await advanceToCaption(cdp);
    await fillCaption(cdp, post.final_caption);
    await scheduleCurrentComposer(cdp, post);
    state.scheduled.push({
      id: post.id,
      date: post.date,
      time_wib: post.time_wib,
      timezone: post.timezone,
      confirmed: true,
      scheduled_at: new Date().toISOString(),
    });
    saveState(state);
    console.log(
      `[${post.id}] scheduled: ${post.date} ${post.time_wib} ${post.timezone}`,
    );
    await sleep(1_500);
  }
}

async function main() {
  const [mode, startRaw, endRaw] = process.argv.slice(2);
  const startId = Number(startRaw);
  const endId = Number(endRaw);
  if (!["publish", "schedule"].includes(mode) || !startId || !endId) {
    throw new Error(
      "Usage: instagram_cdp_publish.mjs <publish|schedule> <start-id> <end-id>",
    );
  }

  const targets = await fetch(CDP_LIST).then((response) => response.json());
  const target = targets.find(
    (item) => item.type === "page" && item.url.includes("instagram.com"),
  );
  if (!target) throw new Error("No Instagram CDP page found on port 9222");

  const cdp = new Cdp(target);
  await cdp.connect();
  try {
    const posts = JSON.parse(fs.readFileSync(PLAN_PATH, "utf8"));
    if (mode === "publish") {
      await publishRange(cdp, posts, startId, endId);
    } else {
      await scheduleRange(cdp, posts, startId, endId);
    }
  } finally {
    cdp.close();
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
