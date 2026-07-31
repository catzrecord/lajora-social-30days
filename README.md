# Lajora — 30-Post English Editorial Campaign

Original project-led feed system informed by a research pass over leading creative-studio feeds: object studies, mockups, environmental graphics, behind-the-scenes frames, surreal staged imagery, and modern type-led posts.

## Current delivery

- 30 original posts at `1080 × 1350` (4:5)
- 20 image-only artworks
- 10 artworks with short English text
- 14 captionless posts
- All written captions are English
- No third-party brands, hotel names, client identities, hashtags, or excluded transactional-tech topics
- Posts 01–09 are live on `@lajora.brands`
- Posts 10–30 are queued automatically across 1–4 August 2026 (WIB)

## Main files

- `content-plan.json` — source of truth, live URLs, and automatic queue
- `content-plan.csv` — schedule overview
- `CAPTION-SIAP-POSTING.txt` — English captions and `[NO CAPTION]` markers
- `posts/editorial-20260731/` — final JPG assets used by Instagram
- `editorial-30-en/` — complete production pack, previews, PNGs, logs, and state

## Commands

```bash
npm run validate
npm run build
```

## Cloud publishing

The production queue runs on GitHub-hosted Actions, so the Mac can stay off.

- Workflow: `.github/workflows/lajora-instagram.yml`
- Publisher: `scripts/publish_due.mjs`
- Schedule: 09:07, 11:07, 13:07, 15:07, 18:07, and 21:07 WIB
- Media host: `https://lajora-social-30days.vercel.app`
- Queue ledger: successful posts update `content-plan.json` and redeploy the dashboard
- Idempotency: published media is reconciled through its queue-specific alt text

Required GitHub secrets:

- `META_ACCESS_TOKEN`
- `INSTAGRAM_USER_ID`
- `PUBLIC_ASSET_BASE_URL`
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

Repository variables:

- `META_GRAPH_VERSION=v25.0`
- `META_GRAPH_HOST=graph.facebook.com`

Manual checks:

```bash
npm run cloud:plan
gh workflow run lajora-instagram.yml -f mode=verify
```

The older Chrome/LaunchAgent runner is retained only as a rollback tool and is
unloaded after the cloud workflow passes its live verification.
