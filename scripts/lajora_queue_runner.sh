#!/bin/zsh

set -u

ROOT="/Users/coong/Documents/lajora-social-30days"
PROFILE="/Users/coong/.codex/lajora-instagram-automation"
PORT="9224"
LOCK="/tmp/lajora-instagram-queue.lock"
LOG_DIR="$ROOT/editorial-30-en/automation-logs"

mkdir -p "$LOG_DIR"
if ! mkdir "$LOCK" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

POST_ID="$(/usr/local/bin/node "$ROOT/scripts/lajora_queue_due.mjs")"
if [[ -z "$POST_ID" ]]; then
  exit 0
fi

started_browser=0
if ! /usr/bin/curl -fsS "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then
  /usr/bin/open -na "Google Chrome" --args \
    "--remote-debugging-port=$PORT" \
    "--user-data-dir=$PROFILE" \
    "--profile-directory=Default" \
    "--no-first-run" \
    "--no-default-browser-check" \
    "--window-position=-10000,-10000" \
    "https://www.instagram.com/lajora.brands/"
  started_browser=1
fi

ready=0
for _ in {1..60}; do
  if /usr/bin/curl -fsS "http://127.0.0.1:$PORT/json/list" >/dev/null 2>&1; then
    ready=1
    break
  fi
  /bin/sleep 1
done

stamp="$(/bin/date +%Y%m%d-%H%M%S)"
if [[ "$ready" != "1" ]]; then
  print -r -- "Chrome CDP belum siap untuk post $POST_ID" \
    >> "$LOG_DIR/$stamp-post-$POST_ID.log"
  exit 1
fi

(
  cd "$ROOT" || exit 1
  INSTAGRAM_CDP_PORT="$PORT" \
  INSTAGRAM_PROGRESS_PATH="$ROOT/editorial-30-en/instagram-browser-progress.json" \
    /usr/local/bin/node "$ROOT/scripts/instagram_publish_range.mjs" \
      "$POST_ID" "$POST_ID"
) >> "$LOG_DIR/$stamp-post-$POST_ID.log" 2>&1
result=$?

if [[ "$started_browser" == "1" ]]; then
  /usr/local/bin/node "$ROOT/scripts/close_cdp_browser.mjs" "$PORT" \
    >> "$LOG_DIR/$stamp-post-$POST_ID.log" 2>&1 || true
fi

exit "$result"
