import { access, readFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const plan = JSON.parse(await readFile(path.join(root, "content-plan.json"), "utf8"));
if (plan.length !== 109) throw new Error(`Expected 109 posts, received ${plan.length}`);
if (new Set(plan.map((item) => item.id)).size !== 109) throw new Error("Duplicate post IDs");
if (plan.some((item) => item.approval_required !== false)) throw new Error("Approval must remain disabled");
for (const item of plan) {
  await access(path.join(root, item.asset));
  if (
    typeof item.final_caption !== "string" ||
    !item.title ||
    !item.date ||
    item.language !== "en"
  ) {
    throw new Error(`Incomplete or non-English post ${item.id}`);
  }
}
console.log("Validated 109 unique, English, approval-free campaign posts.");
