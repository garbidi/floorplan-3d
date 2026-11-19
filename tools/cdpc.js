// Client for cdp_bridge.js. Usage: node cdpc.js <request.json>
const fs = require('fs');
const body = fs.readFileSync(process.argv[2], 'utf8');
fetch('http://127.0.0.1:9555', { method: 'POST', body })
  .then((r) => r.text())
  .then((t) => process.stdout.write(t))
  .catch((e) => { process.stdout.write(JSON.stringify({ error: e.message })); });
