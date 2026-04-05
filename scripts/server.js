/**
 * server.js
 * Servidor HTTP estático mínimo para servir el sitio de muestra durante las pruebas.
 * No requiere dependencias externas — usa únicamente módulos de Node.js.
 */

'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const SITE_DIR = path.resolve(__dirname, '..', 'sample-site');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.svg':  'image/svg+xml',
};

const server = http.createServer((req, res) => {
  const urlPath = req.url === '/' ? '/index.html' : req.url.split('?')[0];
  const filePath = path.normalize(path.join(SITE_DIR, urlPath));
  const ext = path.extname(filePath);

  // Prevent path traversal: reject any path outside SITE_DIR
  if (!filePath.startsWith(SITE_DIR + path.sep) && filePath !== SITE_DIR) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not Found');
      return;
    }
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(data);
  });
});

server.listen(PORT, '127.0.0.1', () => {
  // Signal readiness for Playwright webServer
  process.stdout.write(`Servidor listo en http://127.0.0.1:${PORT}\n`);
});
