#!/usr/bin/env node

const port = Number(process.argv[2] || 9224);
const version = await fetch(`http://127.0.0.1:${port}/json/version`).then(
  (response) => response.json(),
);
const ws = new WebSocket(version.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  ws.onopen = resolve;
  ws.onerror = reject;
});
ws.send(JSON.stringify({ id: 1, method: "Browser.close" }));
await new Promise((resolve) => setTimeout(resolve, 500));
