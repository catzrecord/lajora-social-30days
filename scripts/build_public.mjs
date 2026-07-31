import { cp, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const publicDir = path.join(root, "public");
await mkdir(path.join(publicDir, "posts"), { recursive: true });
await cp(path.join(root, "posts"), path.join(publicDir, "posts"), {
  recursive: true,
  force: true,
});
await cp(path.join(root, "content-plan.json"), path.join(publicDir, "content-plan.json"), {
  force: true,
});

const plan = JSON.parse(await readFile(path.join(root, "content-plan.json"), "utf8"));
const publishedCount = plan.filter((item) => item.status === "published").length;
const queuedCount = plan.filter((item) => item.status === "queued_auto").length;
const blankCaptionCount = plan.filter((item) => !item.final_caption).length;
const imageOnlyCount = plan.filter((item) => !item.contains_text).length;
const rows = plan.map((item) => `
  <article class="${item.status}">
    <img src="/${item.asset}" alt="">
    <div>
      <small><em>${item.status === "published" ? "LIVE" : "QUEUED"}</em> · ${item.date}${item.status === "published" ? "" : ` · ${item.time_wib} WIB`}</small>
      <strong>${item.title.replaceAll("\n", " ")}</strong>
      <span>${item.pillar}</span>
    </div>
  </article>`).join("");

const html = `<!doctype html>
<html lang="id">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lajora · 30-Day Social Queue</title>
<style>
:root{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display",sans-serif;color:#f4f0e8;background:#11110f}
*{box-sizing:border-box}body{margin:0;padding:48px}header{max-width:1200px;margin:0 auto 42px}h1{margin:12px 0;font-size:clamp(36px,7vw,82px);letter-spacing:-.065em;line-height:.9}p{color:#aaa}b{color:#c9f47d}.grid{display:grid;max-width:1200px;margin:auto;grid-template-columns:repeat(4,1fr);gap:14px}article{overflow:hidden;border:1px solid #2d2d29;border-radius:16px;background:#191916}img{width:100%;display:block}article div{display:grid;gap:8px;padding:14px}small,span{color:#898984;font-size:10px;text-transform:uppercase;letter-spacing:.08em}strong{font-size:14px}@media(max-width:800px){body{padding:24px}.grid{grid-template-columns:repeat(2,1fr)}} 
em{font-style:normal;color:#c9f47d}.published{border-color:#536633}.published em{color:#f2a65a}.queued_auto{border-color:#394d2c}
</style>
<header><small>LAJORA · PROJECT-LED EDITORIAL CAMPAIGN</small><h1>${publishedCount} live now.<br><b>${queuedCount} next.</b></h1><p>30 original visuals · ${imageOnlyCount} image-only posts · ${blankCaptionCount} captionless posts · English throughout</p></header>
<main class="grid">${rows}</main>
</html>`;

await writeFile(path.join(publicDir, "index.html"), html);
console.log(`Prepared ${plan.length} campaign assets in public/`);
