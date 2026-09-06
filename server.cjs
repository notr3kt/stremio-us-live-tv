// Tiny static file server with CORS for the US Live TV Stremio addon. Usage: node server.js [port] [dir]
const http = require('http'), fs = require('fs'), path = require('path');
const port = +(process.argv[2] || 7101), root = path.resolve(process.argv[3] || path.join(__dirname, 'dist'));
http.createServer((req, res) => {
  const urlPath = decodeURIComponent(req.url.split('?')[0]);
  let file = path.normalize(path.join(root, urlPath));
  if (!file.startsWith(root)) { res.writeHead(403); return res.end(); }
  if (!path.extname(file)) file += '.json';
  fs.readFile(file, (err, data) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', '*');
    if (err) { res.writeHead(404, { 'Content-Type': 'application/json' }); return res.end('{"error":"not found"}'); }
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'max-age=3600' });
    res.end(data);
  });
}).listen(port, '127.0.0.1', () => console.log('US Live TV addon on http://127.0.0.1:' + port + '/manifest.json'));
