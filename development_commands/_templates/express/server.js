/**
 * server.js - Entry point
 *
 *
 * Responsibilities:
 *   - Bootstrap Express with middleware
 *   - Mount all route modules
 *   - Start HTTPS (or HTTP fallback) server
 *
 * Everything else lives in routes/.
 */
import 'dotenv/config';
import fs from 'fs';
import path from 'path';
import http from 'http';
import https from 'https';
import express from 'express';

import { fileURLToPath } from 'url';


const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = parseInt(process.env.PORT || '3000', 10);
const USE_HTTPS = process.env.USE_HTTPS === 'true'


////////////////////////////////////////
// Middleware
////////////////////////////////////////
app.use(express.json());
app.use(express.urlencoded({ extended: true }));


////////////////////////////////////////
// Routes
////////////////////////////////////////
app.use(express.static(path.join(__dirname, 'public')));
// app.get('/', (req, res) => { res.sendFile('index.html'); });
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});
app.get('/api', (req, res) => {
  res.json({ message: 'API working' });
});
app.post('/api/data', (req, res) => {
  res.status(201).json({ received: req.body });
});
app.use((req, res) => {
  res.status(404).json({ error: 'Not Found' });
});


////////////////////////////////////////
// Server
////////////////////////////////////////
if (USE_HTTPS) {
  const options = {
    key: fs.readFileSync(process.env.SSL_KEY_PATH),
    cert: fs.readFileSync(process.env.SSL_CERT_PATH),
  };

  https.createServer(options, app).listen(PORT, () => {
    console.log(`HTTPS server running on https://localhost:${PORT}`);
  });
} else {
  http.createServer(app).listen(PORT, () => {
    console.log(`HTTP server running on http://localhost:${PORT}`);
  });
}


process.on('SIGINT', () => {
  console.log('\nGoodbye!');
  process.exit(0);
});