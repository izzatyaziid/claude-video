'use strict';
const express = require('express');
const { rateLimit } = require('express-rate-limit');
const { contentMap } = require('../db');
const v = require('../views');
const { originAllowed, str, email, oneOf, ValidationError } = require('../security');

module.exports = function publicRoutes(db, config) {
  const r = express.Router();
  const draft = config.draft;

  const visibleBrands = () => db.prepare("SELECT * FROM brands WHERE status != 'hidden' ORDER BY sort_order, id").all();
  const published = (limit) => db.prepare("SELECT * FROM posts WHERE status = 'published' ORDER BY published_at DESC LIMIT ?").all(limit);

  function page(res, req, opts, status = 200) {
    const c = contentMap(db);
    const brands = opts.brands || visibleBrands();
    res.status(status).type('html').send(v.layout({ ...opts, c, draft, brands, path: req.path }));
  }

  r.get('/brand-colors.css', (req, res) => {
    res.type('text/css').set('Cache-Control', 'no-cache').send(v.brandColorsCss(db.prepare('SELECT slug, accent, logo_bg FROM brands').all()));
  });

  r.get('/', (req, res) => {
    const brands = visibleBrands();
    page(res, req, { brands, body: v.home({ c: contentMap(db), draft, brands, posts: published(3) }) });
  });

  r.get('/brands', (req, res) => {
    const brands = visibleBrands();
    page(res, req, { title: 'Ekosistem jenama', brands, body: v.brandsPage({ brands, draft }) });
  });

  r.get('/brands/:slug', (req, res) => {
    const b = db.prepare("SELECT * FROM brands WHERE slug = ? AND status != 'hidden'").get(String(req.params.slug));
    if (!b) return page(res, req, { title: 'Tidak dijumpai', body: v.notFound() }, 404);
    page(res, req, { title: b.name, description: b.fact_status !== 'tbc' ? b.role_line : '', body: v.brandPage({ b, draft }) });
  });

  r.get('/about', (req, res) => page(res, req, { title: 'Tentang', body: v.aboutPage({ c: contentMap(db), draft }) }));
  r.get('/news', (req, res) => page(res, req, { title: 'Berita', body: v.newsPage({ posts: published(50) }) }));
  r.get('/news/:slug', (req, res) => {
    const p = db.prepare("SELECT * FROM posts WHERE slug = ? AND status = 'published'").get(String(req.params.slug));
    if (!p) return page(res, req, { title: 'Tidak dijumpai', body: v.notFound() }, 404);
    page(res, req, { title: p.title, description: p.excerpt, body: v.postPage({ p }) });
  });
  r.get('/privacy', (req, res) => page(res, req, { title: 'Dasar privasi', body: v.privacyPage({ c: contentMap(db), draft }) }));

  r.get('/contact', (req, res) => {
    const kind = v.KINDS.some(([k]) => k === req.query.kind) ? req.query.kind : undefined;
    page(res, req, { title: 'Hubungi', body: v.contactPage({ c: contentMap(db), draft, sent: req.query.sent === '1', kind }) });
  });

  const contactLimiter = rateLimit({
    windowMs: 60 * 60 * 1000, limit: config.contactLimit, standardHeaders: 'draft-8', legacyHeaders: false,
    handler: (req, res) => page(res, req, { title: 'Hubungi', body: v.contactPage({ c: contentMap(db), draft, error: 'Terlalu banyak pertanyaan dari rangkaian ini. Cuba lagi dalam sejam.' }) }, 429),
  });

  r.post('/contact', express.urlencoded({ extended: false, limit: '10kb', parameterLimit: 20 }), contactLimiter, (req, res) => {
    const body = req.body || {};
    if (!originAllowed(req, config)) return res.status(403).type('text').send('Permintaan ditolak.');
    // Honeypot: real visitors never see this field. Pretend success so bots learn nothing.
    if (body.website) return res.redirect(303, '/contact?sent=1');
    try {
      const rec = {
        name: str(body.name, { field: 'Nama', max: 80, required: true }),
        email: email(body.email),
        company: str(body.company, { field: 'Syarikat', max: 120 }),
        kind: oneOf(body.kind, v.KINDS.map(([k]) => k), 'Jenis pertanyaan'),
        message: str(body.message, { field: 'Mesej', max: 3000, min: 10, required: true, multiline: true }),
      };
      if (body.consent !== '1') throw new ValidationError('Sila tandakan persetujuan privasi.');
      db.prepare('INSERT INTO inquiries (name, email, company, kind, message, consent, ip_hash, created_at) VALUES (?, ?, ?, ?, ?, 1, ?, ?)')
        .run(rec.name, rec.email, rec.company, rec.kind, rec.message, req.ipHash, Date.now());
      return res.redirect(303, '/contact?sent=1');
    } catch (err) {
      if (!(err instanceof ValidationError)) throw err;
      const values = { name: body.name, email: body.email, company: body.company, kind: body.kind, message: body.message };
      return page(res, req, { title: 'Hubungi', body: v.contactPage({ c: contentMap(db), draft, error: err.message, values }) }, 400);
    }
  });

  return r;
};
