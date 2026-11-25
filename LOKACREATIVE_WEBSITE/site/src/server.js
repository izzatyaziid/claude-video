'use strict';
const path = require('node:path');
const express = require('express');
const helmet = require('helmet');
const { baseConfig, assertProdConfig } = require('./config');
const { openDb, contentMap } = require('./db');
const { sessionMiddleware } = require('./auth');
const publicRoutes = require('./routes/public');
const adminApi = require('./routes/admin-api');
const views = require('./views');

const ROOT = path.join(__dirname, '..');

function createApp({ db, config: overrides = {} } = {}) {
  const config = { ...baseConfig, ...overrides };
  const app = express();
  app.disable('x-powered-by');
  app.set('trust proxy', config.trustProxy ? 1 : false);

  app.use(helmet({
    contentSecurityPolicy: {
      useDefaults: false,
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'", 'https://fonts.googleapis.com'],
        fontSrc: ['https://fonts.gstatic.com'],
        imgSrc: ["'self'", 'data:'],
        connectSrc: ["'self'"],
        formAction: ["'self'"],
        frameAncestors: ["'none'"],
        baseUri: ["'none'"],
        objectSrc: ["'none'"],
        ...(config.isProd ? { upgradeInsecureRequests: [] } : {}),
      },
    },
    strictTransportSecurity: config.isProd ? { maxAge: 63072000, includeSubDomains: true } : false,
    crossOriginEmbedderPolicy: false,
    referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
  }));
  app.use((req, res, next) => {
    res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=(), usb=()');
    next();
  });

  const staticOpts = { index: false, dotfiles: 'deny', maxAge: config.isProd ? '1d' : 0 };
  app.use('/assets', express.static(path.join(ROOT, 'public', 'assets'), staticOpts));
  app.use('/admin/assets', express.static(path.join(ROOT, 'public', 'admin'), { ...staticOpts, maxAge: 0 }));

  app.use(sessionMiddleware(db, config));
  app.use('/admin/api', adminApi(db, config));
  app.get('/admin', (req, res) => {
    res.set('Cache-Control', 'no-store').set('X-Robots-Tag', 'noindex, nofollow');
    res.sendFile(path.join(ROOT, 'public', 'admin', 'index.html'));
  });
  app.use(publicRoutes(db, config));

  app.use((req, res) => res.status(404).type('html').send(views.layout({
    title: 'Tidak dijumpai', body: views.notFound(), c: contentMap(db), draft: config.draft, path: req.path,
    brands: db.prepare("SELECT slug, name FROM brands WHERE status != 'hidden' ORDER BY sort_order").all(),
  })));
  // eslint-disable-next-line no-unused-vars
  app.use((err, req, res, next) => {
    if (err.type === 'entity.too.large') return res.status(413).type('text').send('Data terlalu besar.');
    if (err.status && err.status < 500 && err.expose) return res.status(err.status).type('text').send(err.message);
    console.error('[server]', err);
    res.status(500).type('text').send('Ralat pelayan.');
  });
  return app;
}

if (require.main === module) {
  assertProdConfig(baseConfig);
  const db = openDb(baseConfig.dbFile);
  createApp({ db }).listen(baseConfig.port, () => {
    console.log(`LokaCreative website: http://localhost:${baseConfig.port}  (admin: /admin)  draft=${baseConfig.draft}`);
  });
}

module.exports = { createApp };
