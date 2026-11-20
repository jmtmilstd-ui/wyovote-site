// Render script-built public pages in a throwaway headless Chrome and print their text.
//   node render_pages.mjs <urls.json> [parallel=4] [wait_ms=5000] [out.json]
// Output (to out.json, else stdout): JSON list of {url, ok, ms, text, links:[[text,href]...], error}.
// Own temporary profile; never touches any signed-in browser.
import {spawn} from 'child_process';
import fs from 'fs';
const [,, listPath, P0, W0, OUT] = process.argv;
const emit = v => { const t = JSON.stringify(v); if (OUT) fs.writeFileSync(OUT, t); else process.stdout.write(t); };
const urls = JSON.parse(fs.readFileSync(listPath, 'utf8'));
const PAR = parseInt(P0 || '4'), WAIT = parseInt(W0 || '5000');
const port = 9800 + Math.floor(Math.random() * 150);
const prof = '/tmp/wyovote-spider-' + port;
const ch = spawn('google-chrome', ['--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
  `--remote-debugging-port=${port}`, '--user-data-dir=' + prof, 'about:blank'], {stdio: 'ignore'});
const sleep = ms => new Promise(r => setTimeout(r, ms));
const done = () => { try { ch.kill(); } catch (e) {} try { fs.rmSync(prof, {recursive: true, force: true}); } catch (e) {} };
let ok = false;
for (let i = 0; i < 75; i++) { try { await (await fetch(`http://127.0.0.1:${port}/json/version`)).json(); ok = true; break; } catch (e) { await sleep(200); } }
if (!ok) { emit(urls.map(u => ({url: u, ok: false, error: 'chrome did not start'}))); done(); process.exit(0); }
async function one(url) {
  const t0 = Date.now();
  const tab = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, {method: 'PUT'})).json();
  const ws = new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  let id = 0; const pend = {};
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend[m.id]) { pend[m.id](m); delete pend[m.id]; } };
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({id: i, method, params})); });
  try {
    await send('Page.enable');
    await send('Page.navigate', {url});
    await sleep(WAIT);
    const expr = `JSON.stringify({text: document.body ? document.body.innerText : '', links: [...document.querySelectorAll('a[href]')].slice(0, 400).map(a => [a.innerText.trim().slice(0, 120), a.href])})`;
    const r = await send('Runtime.evaluate', {expression: expr, returnByValue: true});
    const v = JSON.parse(r.result.result.value || '{}');
    return {url, ok: true, ms: Date.now() - t0, text: (v.text || '').slice(0, 30000), links: v.links || []};
  } catch (e) {
    return {url, ok: false, ms: Date.now() - t0, error: String(e)};
  } finally {
    try { ws.close(); } catch (e) {}
    try { await fetch(`http://127.0.0.1:${port}/json/close/${tab.id}`); } catch (e) {}
  }
}
const out = new Array(urls.length); let next = 0;
async function worker() { while (next < urls.length) { const i = next++; out[i] = await Promise.race([one(urls[i]), sleep(WAIT + 20000).then(() => ({url: urls[i], ok: false, error: 'timeout'}))]); } }
const hard = setTimeout(() => { emit(out.map((o, i) => o || {url: urls[i], ok: false, error: 'not reached'})); done(); process.exit(0); }, 150000);
await Promise.all(Array.from({length: Math.min(PAR, urls.length)}, worker));
clearTimeout(hard);
emit(out);
done(); process.exit(0);
