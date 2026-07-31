#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const ROOT = "/Users/coong/Documents/lajora-social-30days";
const PLAN_PATH = path.join(ROOT, "content-plan.json");
const STATE_PATH = path.join(
  ROOT,
  "editorial-30-en",
  "instagram-browser-progress.json",
);

const plan = JSON.parse(fs.readFileSync(PLAN_PATH, "utf8"));
const state = fs.existsSync(STATE_PATH)
  ? JSON.parse(fs.readFileSync(STATE_PATH, "utf8"))
  : { published: [] };
const completed = new Set((state.published || []).map((item) => item.id));

const now = process.env.LAJORA_QUEUE_NOW
  ? new Date(process.env.LAJORA_QUEUE_NOW)
  : new Date();
const due = plan
  .filter(
    (post) =>
      post.status === "queued_auto" &&
      !completed.has(post.id) &&
      /^\d{2}:\d{2}$/.test(post.time_wib),
  )
  .map((post) => ({
    ...post,
    dueAt: new Date(`${post.date}T${post.time_wib}:00+07:00`),
  }))
  .filter((post) => post.dueAt <= now)
  .sort((a, b) => a.dueAt - b.dueAt || a.id - b.id);

if (due.length) process.stdout.write(String(due[0].id));
