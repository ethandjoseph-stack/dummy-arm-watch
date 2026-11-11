// Print the pitch slides to docs/pitch/pitch-deck.pdf (4 pages, 16:9) with headless Chrome.
//
//   node scripts/pitch_pdf.mjs
//
// Reads docs/pitch/pitch-deck-offline.html (made by scripts/pitch_deck.py: run that first).
// Needs Google Chrome in /Applications and Node 22 or newer (its built-in WebSocket). No libraries.
// The fonts come from Google Fonts, so with no internet the PDF is set in the Mac's own Hebrew face.
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const page = pathToFileURL(join(root, "docs", "pitch", "pitch-deck-offline.html")).href;
const out = join(root, "docs", "pitch", "pitch-deck.pdf");
const ready = "document.fonts.status === 'loaded' && document.querySelector('#plot-dance svg')";

const profile = mkdtempSync(join(tmpdir(), "pitch-pdf-"));
const port = 9300 + Math.floor(Math.random() * 500);
const chrome = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", [
  "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, "--window-size=1920,1080", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
try {
  let target;
  for (let i = 0; i < 50 && !target; i++) {
    await sleep(300);
    try { target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === "page"); } catch {}
  }
  if (!target) throw new Error("Chrome did not start");
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => (ws.onopen = r));
  let id = 0;
  const waiting = new Map();
  ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && waiting.has(d.id)) { waiting.get(d.id)(d); waiting.delete(d.id); } };
  const send = (method, params = {}) => new Promise((r) => { const i = ++id; waiting.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  await send("Page.enable");
  await send("Runtime.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
  await send("Page.navigate", { url: page });
  let ok = false;
  for (let i = 0; i < 40 && !ok; i++) {
    await sleep(750);
    const r = await send("Runtime.evaluate", { expression: `(() => { try { return !!(${ready}); } catch (e) { return false; } })()`, returnByValue: true });
    ok = r.result?.result?.value === true;
  }
  if (!ok) console.log("the page did not report its fonts and charts ready: printing it as it is");
  await sleep(800);
  const pdf = await send("Page.printToPDF", { printBackground: true, paperWidth: 13.3333, paperHeight: 7.5, marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0 });
  if (!pdf.result?.data) throw new Error("Chrome did not return a PDF");
  writeFileSync(out, Buffer.from(pdf.result.data, "base64"));
  console.log("wrote", out);
  ws.close();
} finally {
  chrome.kill();
  await sleep(300);
  rmSync(profile, { recursive: true, force: true });
}
