#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const planPath = path.join(root, "content-plan.json");
const graphVersion = process.env.META_GRAPH_VERSION || "v25.0";
const graphHost = process.env.META_GRAPH_HOST || "graph.instagram.com";
const graphBase = `https://${graphHost}/${graphVersion}`;
const accountId = process.env.INSTAGRAM_USER_ID;
const accessToken = process.env.META_ACCESS_TOKEN;
const assetBase = (process.env.PUBLIC_ASSET_BASE_URL || "").replace(/\/+$/, "");
const mode = argument("mode") || process.env.LAJORA_PUBLISH_MODE || "due";
const requestedId = Number(argument("post-id") || process.env.LAJORA_POST_ID || 0);
const now = new Date(process.env.LAJORA_NOW || Date.now());

function argument(name) {
  const exact = `--${name}`;
  const prefix = `${exact}=`;
  const index = process.argv.indexOf(exact);
  if (index >= 0) return process.argv[index + 1];
  const inline = process.argv.find((value) => value.startsWith(prefix));
  return inline?.slice(prefix.length);
}

function requireConfiguration() {
  const missing = [];
  if (!accountId) missing.push("INSTAGRAM_USER_ID");
  if (!accessToken) missing.push("META_ACCESS_TOKEN");
  if (!assetBase) missing.push("PUBLIC_ASSET_BASE_URL");
  if (missing.length) throw new Error(`Missing configuration: ${missing.join(", ")}`);
}

function jakartaParts(date) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Jakarta",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  }).formatToParts(date);
  return Object.fromEntries(parts.map((part) => [part.type, part.value]));
}

function dueAt(item) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(item.date || "")) return null;
  if (!/^\d{2}:\d{2}$/.test(item.time_wib || "")) return null;
  return new Date(`${item.date}T${item.time_wib}:00+07:00`);
}

function selectItem(plan) {
  if (requestedId) {
    const item = plan.find((entry) => Number(entry.id) === requestedId);
    if (!item) throw new Error(`Post ${requestedId} was not found`);
    return item;
  }
  const candidates = plan
    .filter((item) => item.status === "queued_auto")
    .map((item) => ({ item, due: dueAt(item) }))
    .filter(({ due }) => due && due <= now)
    .sort((a, b) => a.due - b.due || a.item.id - b.item.id);
  return candidates[0]?.item;
}

function assetUrl(item) {
  const relative = String(item.asset || "").replace(/^\/+/, "");
  if (!relative) throw new Error(`Post ${item.id} has no asset path`);
  return `${assetBase}/${relative}`;
}

function altText(item) {
  const title = String(item.title || "Lajora editorial artwork").replace(/\s+/g, " ").trim();
  return `${title}. Lajora editorial queue item ${String(item.id).padStart(2, "0")}.`;
}

async function responseJson(response) {
  const text = await response.text();
  let payload;
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    payload = { raw: text.slice(0, 500) };
  }
  if (!response.ok || payload.error) {
    const message =
      payload.error?.error_user_msg ||
      payload.error?.message ||
      payload.message ||
      `HTTP ${response.status}`;
    const code = payload.error?.code ? ` [code ${payload.error.code}]` : "";
    throw new Error(`${message}${code}`);
  }
  return payload;
}

async function graph(pathname, params = {}, method = "GET") {
  const url = new URL(`${graphBase}/${pathname.replace(/^\/+/, "")}`);
  const body = new URLSearchParams({ ...params, access_token: accessToken });
  if (method === "GET") {
    for (const [key, value] of body) url.searchParams.set(key, value);
    return responseJson(await fetch(url, { headers: { accept: "application/json" } }));
  }
  return responseJson(
    await fetch(url, {
      method,
      headers: {
        accept: "application/json",
        "content-type": "application/x-www-form-urlencoded",
      },
      body,
    }),
  );
}

async function verifyAsset(url) {
  const response = await fetch(url, { method: "HEAD", redirect: "follow" });
  if (!response.ok) throw new Error(`Asset returned HTTP ${response.status}: ${url}`);
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.startsWith("image/")) {
    throw new Error(`Asset is not an image (${contentType || "missing content-type"}): ${url}`);
  }
  return {
    url: response.url,
    contentType,
    contentLength: Number(response.headers.get("content-length") || 0),
  };
}

async function verifyAccount() {
  return graph(`${accountId}?fields=id,username,account_type,media_count`);
}

async function recentMedia() {
  try {
    const payload = await graph(
      `${accountId}/media?fields=id,caption,permalink,timestamp,alt_text&limit=100`,
    );
    return payload.data || [];
  } catch (error) {
    if (!/alt_text|field/i.test(error.message)) throw error;
    const payload = await graph(
      `${accountId}/media?fields=id,caption,permalink,timestamp&limit=100`,
    );
    return payload.data || [];
  }
}

async function findExisting(item) {
  const marker = `queue item ${String(item.id).padStart(2, "0")}`;
  const media = await recentMedia();
  return media.find((entry) => String(entry.alt_text || "").toLowerCase().includes(marker));
}

async function createContainer(item, imageUrl) {
  const params = {
    image_url: imageUrl,
    alt_text: altText(item),
  };
  const caption = String(item.final_caption || "").trim();
  if (caption) params.caption = caption;
  if (process.env.META_DISCLOSE_AI !== "false") params.is_ai_generated = "true";

  try {
    return await graph(`${accountId}/media`, params, "POST");
  } catch (error) {
    if (!/is_ai_generated|parameter/i.test(error.message) || !params.is_ai_generated) throw error;
    delete params.is_ai_generated;
    return graph(`${accountId}/media`, params, "POST");
  }
}

async function waitForContainer(containerId) {
  const deadline = Date.now() + 120_000;
  while (Date.now() < deadline) {
    const status = await graph(`${containerId}?fields=status_code,status`);
    if (status.status_code === "FINISHED") return status;
    if (status.status_code === "ERROR" || status.status_code === "EXPIRED") {
      throw new Error(`Meta media container ${status.status_code}: ${status.status || "unknown"}`);
    }
    await new Promise((resolve) => setTimeout(resolve, 5000));
  }
  throw new Error("Timed out waiting for the Meta media container");
}

async function updatePlan(plan, item, media, state) {
  const target = plan.find((entry) => Number(entry.id) === Number(item.id));
  target.status = "published";
  target.instagram_media_id = media.id;
  if (media.permalink) target.instagram_url = media.permalink;
  target.published_at = media.timestamp || new Date().toISOString();
  target.published_via = state;
  await fs.writeFile(planPath, `${JSON.stringify(plan, null, 2)}\n`);
}

async function setOutput(values) {
  const lines = Object.entries(values).map(([key, value]) => {
    const text = typeof value === "string" ? value : JSON.stringify(value);
    return `${key}=${text.replaceAll("\n", " ")}`;
  });
  if (process.env.GITHUB_OUTPUT) {
    await fs.appendFile(process.env.GITHUB_OUTPUT, `${lines.join("\n")}\n`);
  }
  for (const line of lines) console.log(line);
}

async function main() {
  const plan = JSON.parse(await fs.readFile(planPath, "utf8"));
  const item = selectItem(plan);
  const stamp = jakartaParts(now);
  const currentWib = `${stamp.year}-${stamp.month}-${stamp.day} ${stamp.hour}:${stamp.minute}:${stamp.second} WIB`;

  if (mode === "plan") {
    await setOutput({
      result: item ? "post_selected" : "no_post_due",
      post_id: item?.id || "",
      now_wib: currentWib,
    });
    return;
  }

  requireConfiguration();
  const account = await verifyAccount();

  if (mode === "verify") {
    const next = item || plan.find((entry) => entry.status === "queued_auto");
    const asset = next ? await verifyAsset(assetUrl(next)) : null;
    await setOutput({
      result: "verified",
      username: account.username || "",
      account_type: account.account_type || "",
      media_count: account.media_count ?? "",
      post_id: next?.id || "",
      asset_url: asset?.url || "",
      now_wib: currentWib,
    });
    return;
  }

  if (mode === "deploy") {
    const next = item || plan.find((entry) => entry.status === "queued_auto");
    const asset = next ? await verifyAsset(assetUrl(next)) : null;
    await setOutput({
      result: "deploy_ready",
      username: account.username || "",
      account_type: account.account_type || "",
      post_id: next?.id || "",
      asset_url: asset?.url || "",
      now_wib: currentWib,
    });
    return;
  }

  if (mode === "preflight") {
    const next = item || plan.find((entry) => entry.status === "queued_auto");
    if (!next) {
      await setOutput({ result: "no_post_due", now_wib: currentWib });
      return;
    }
    const imageUrl = assetUrl(next);
    await verifyAsset(imageUrl);
    const container = await createContainer(next, imageUrl);
    await waitForContainer(container.id);
    await setOutput({
      result: "preflight_ready",
      username: account.username || "",
      account_type: account.account_type || "",
      post_id: next.id,
      container_id: container.id,
      asset_url: imageUrl,
      now_wib: currentWib,
    });
    return;
  }

  if (!item) {
    await setOutput({ result: "no_post_due", now_wib: currentWib });
    return;
  }
  if (item.status === "published") {
    await setOutput({
      result: "already_recorded",
      post_id: item.id,
      instagram_url: item.instagram_url || "",
    });
    return;
  }

  const imageUrl = assetUrl(item);
  await verifyAsset(imageUrl);
  const existing = await findExisting(item);
  if (existing) {
    await updatePlan(plan, item, existing, "github_actions_reconciled");
    await setOutput({
      result: "already_published",
      post_id: item.id,
      instagram_url: existing.permalink || "",
    });
    return;
  }

  const container = await createContainer(item, imageUrl);
  await waitForContainer(container.id);
  const published = await graph(
    `${accountId}/media_publish`,
    { creation_id: container.id },
    "POST",
  );
  const media = await graph(`${published.id}?fields=id,permalink,timestamp`);
  await updatePlan(plan, item, media, "github_actions_graph_api");
  await setOutput({
    result: "published",
    post_id: item.id,
    instagram_media_id: media.id,
    instagram_url: media.permalink || "",
  });
}

main().catch(async (error) => {
  console.error(`publisher_error=${error.message}`);
  await setOutput({ result: "failed", error: error.message });
  process.exitCode = 1;
});
