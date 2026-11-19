// Persistent CDP bridge: one connection to the user's Chrome (port from DevToolsActivePort),
// exposes a local HTTP endpoint so short-lived clients don't trigger a new permission prompt.
// Only attaches to tabs explicitly requested (never to all tabs).
const fs = require('fs');
const http = require('http');
const path = require('path');

const PORT_FILE = path.join(process.env.LOCALAPPDATA, 'Google', 'Chrome', 'User Data', 'DevToolsActivePort');
const HTTP_PORT = 9555;
const LOG_FILE = path.join(__dirname, 'bridge.log');
const _log = console.log;
console.log = (...a) => { _log(...a); try { fs.appendFileSync(LOG_FILE, new Date().toISOString() + ' ' + a.join(' ') + '\n'); } catch {} };

const [port, wsPath] = fs.readFileSync(PORT_FILE, 'utf8').trim().split(/\r?\n/);
const ws = new WebSocket(`ws://127.0.0.1:${port}${wsPath}`);
let nextId = 1;
const pending = new Map();
let ready = false;

ws.onopen = () => { ready = true; console.log('connected to Chrome'); };
ws.onclose = () => { console.log('Chrome connection closed'); process.exit(1); };
ws.onerror = (e) => console.log('ws error', e.message || e);
ws.onmessage = (ev) => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve } = pending.get(msg.id);
    pending.delete(msg.id);
    resolve(msg);
  }
};

function cdp(method, params = {}, sessionId, timeoutMs = 60000) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    const t = setTimeout(() => { pending.delete(id); reject(new Error(`timeout ${method}`)); }, timeoutMs);
    pending.set(id, { resolve: (m) => { clearTimeout(t); resolve(m); } });
    const msg = { id, method, params };
    if (sessionId) msg.sessionId = sessionId;
    ws.send(JSON.stringify(msg));
  });
}

async function handle(req) {
  switch (req.op) {
    case 'cdp':
      return cdp(req.method, req.params, req.sessionId, req.timeoutMs);
    case 'eval': {
      const r = await cdp('Runtime.evaluate', {
        expression: req.expression, awaitPromise: true, returnByValue: true,
      }, req.sessionId, req.timeoutMs || 120000);
      if (req.saveBase64To && r.result && r.result.result && typeof r.result.result.value === 'string') {
        const b64 = r.result.result.value.replace(/^data:[^,]+,/, '');
        fs.writeFileSync(req.saveBase64To, Buffer.from(b64, 'base64'));
        return { saved: req.saveBase64To, bytes: fs.statSync(req.saveBase64To).size };
      }
      return r;
    }
    case 'screenshot': {
      const r = await cdp('Page.captureScreenshot', { format: 'png' }, req.sessionId);
      fs.writeFileSync(req.path, Buffer.from(r.result.data, 'base64'));
      return { saved: req.path };
    }
    default:
      throw new Error('unknown op ' + req.op);
  }
}

http.createServer((rq, rs) => {
  let body = '';
  rq.on('data', (c) => (body += c));
  rq.on('end', async () => {
    try {
      if (!ready) throw new Error('not connected yet (approve the Chrome prompt)');
      const out = await handle(JSON.parse(body));
      rs.end(JSON.stringify(out));
    } catch (e) {
      rs.statusCode = 500;
      rs.end(JSON.stringify({ error: e.message }));
    }
  });
}).listen(HTTP_PORT, '127.0.0.1', () => console.log('bridge on', HTTP_PORT));
