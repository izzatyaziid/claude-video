'use strict';
const express = require('express');
const { rateLimit } = require('express-rate-limit');
const {
  verifyPassword, hashPassword, passwordProblem, requireSameOrigin, ValidationError,
  str, oneOf, email, httpsUrl, hexColor, slug, intId,
} = require('../security');
const { createSession, destroySession, requireAuth, requireRole, requireCsrf } = require('../auth');
const QRCode = require('qrcode');
const totp = require('../totp');
const { makeBox } = require('../secret-box');
const { sha256, randomToken, safeEqual } = require('../security');

module.exports = function adminApi(db, config) {
  const r = express.Router();
  const box = makeBox(config);

  r.use((req, res, next) => { res.set('Cache-Control', 'no-store'); next(); });
  r.use(requireSameOrigin(config));
  // JSON only: blocks cross-site "simple" form posts even before CSRF checks.
  r.use((req, res, next) => {
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method) && !req.is('application/json')) {
      return res.status(415).json({ error: 'Content-Type mesti application/json.' });
    }
    next();
  });
  r.use(express.json({ limit: '50kb', strict: true }));

  const audit = db.prepare('INSERT INTO audit_log (admin_id, action, entity, entity_id, detail, ip_hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)');
  const log = (req, action, entity = '', entityId = '', detail = '') =>
    audit.run(req.admin ? req.admin.id : null, action, entity, String(entityId), String(detail).slice(0, 500), req.ipHash || '', Date.now());

  // ---------- auth ----------
  const loginLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, limit: config.loginLimit, standardHeaders: 'draft-8', legacyHeaders: false,
    message: { error: 'Terlalu banyak cubaan. Cuba lagi dalam 15 minit.' },
  });

  const findAdmin = db.prepare('SELECT * FROM admins WHERE email = ?');
  r.post('/login', loginLimiter, (req, res) => {
    const em = typeof req.body?.email === 'string' ? req.body.email.trim().toLowerCase().slice(0, 254) : '';
    const pw = typeof req.body?.password === 'string' ? req.body.password.slice(0, 200) : '';
    const admin = em ? findAdmin.get(em) : undefined;
    const now = Date.now();
    const fail = () => res.status(401).json({ error: 'Emel atau kata laluan salah, atau akaun dikunci sementara.' });

    const ok = verifyPassword(pw, admin?.password_hash); // always runs: constant-ish timing
    if (!admin || !admin.active) { log(req, 'login_failed', 'admin', '', 'unknown or inactive'); return fail(); }
    if (admin.locked_until && admin.locked_until > now) { log(req, 'login_locked', 'admin', admin.id); return fail(); }
    if (!ok) { recordFailure(req, admin, 'login_failed'); return fail(); }
    if (admin.totp_enabled) {
      // Step 1 passed. Issue a short-lived, single-purpose challenge token; no session yet.
      const token = randomToken(32);
      db.prepare('DELETE FROM mfa_challenges WHERE admin_id = ? OR expires_at < ?').run(admin.id, now);
      db.prepare('INSERT INTO mfa_challenges (id_hash, admin_id, expires_at) VALUES (?, ?, ?)').run(sha256(token), admin.id, now + config.mfaChallengeMs);
      log(req, 'login_password_ok', 'admin', admin.id, 'awaiting 2FA');
      return res.json({ mfa_required: true, mfa_token: token });
    }
    finishLogin(req, res, admin);
  });

  function recordFailure(req, admin, action) {
    const attempts = admin.failed_attempts + 1;
    const lock = attempts >= config.lockoutAfter ? Date.now() + config.lockoutMs : null;
    db.prepare('UPDATE admins SET failed_attempts = ?, locked_until = ? WHERE id = ?').run(lock ? 0 : attempts, lock, admin.id);
    if (lock) db.prepare('DELETE FROM mfa_challenges WHERE admin_id = ?').run(admin.id);
    log(req, lock ? 'account_locked' : action, 'admin', admin.id);
  }

  function finishLogin(req, res, admin) {
    db.prepare('UPDATE admins SET failed_attempts = 0, locked_until = NULL, last_login_at = ? WHERE id = ?').run(Date.now(), admin.id);
    // New session on every login (prevents session fixation); old session for this browser is dropped.
    if (req.sessionIdHash) db.prepare('DELETE FROM sessions WHERE id_hash = ?').run(req.sessionIdHash);
    const csrf = createSession(db, config, res, admin.id);
    req.admin = { id: admin.id };
    log(req, 'login', 'admin', admin.id, admin.totp_enabled ? '2FA' : 'password only');
    res.json({ user: publicUser(admin), csrf });
  }

  const publicUser = (a) => ({ id: a.id, email: a.email, name: a.name, role: a.role, mfa: !!a.totp_enabled, require2fa: config.require2fa });

  // Step 2: TOTP code or a one-time recovery code.
  r.post('/login/mfa', loginLimiter, (req, res) => {
    const token = typeof req.body?.mfa_token === 'string' ? req.body.mfa_token.slice(0, 100) : '';
    const now = Date.now();
    const fail = (status = 401) => res.status(status).json({ error: 'Kod pengesahan salah atau tamat tempoh. Log masuk semula jika perlu.' });
    const ch = token ? db.prepare('SELECT * FROM mfa_challenges WHERE id_hash = ?').get(sha256(token)) : undefined;
    if (!ch || ch.expires_at < now || ch.attempts >= config.mfaMaxAttempts) return fail();
    const admin = db.prepare('SELECT * FROM admins WHERE id = ?').get(ch.admin_id);
    if (!admin || !admin.active || !admin.totp_enabled || (admin.locked_until && admin.locked_until > now)) return fail();

    let okStep = null; let usedRecovery = false;
    if (req.body?.recovery) {
      const hashes = JSON.parse(admin.recovery_hashes || '[]');
      const h = sha256(totp.normalizeRecovery(req.body.recovery));
      const idx = hashes.findIndex((x) => safeEqual(x, h));
      if (idx >= 0) {
        hashes.splice(idx, 1);
        db.prepare('UPDATE admins SET recovery_hashes = ? WHERE id = ?').run(JSON.stringify(hashes), admin.id);
        usedRecovery = true;
      }
    } else {
      okStep = totp.verify(box.open(admin.totp_secret_enc), req.body?.code, admin.totp_last_step, now);
    }
    if (okStep === null && !usedRecovery) {
      db.prepare('UPDATE mfa_challenges SET attempts = attempts + 1 WHERE id_hash = ?').run(ch.id_hash);
      recordFailure(req, admin, 'mfa_failed');
      return fail();
    }
    if (okStep !== null) db.prepare('UPDATE admins SET totp_last_step = ? WHERE id = ?').run(okStep, admin.id);
    db.prepare('DELETE FROM mfa_challenges WHERE id_hash = ?').run(ch.id_hash);
    if (usedRecovery) log(req, 'recovery_code_used', 'admin', admin.id);
    finishLogin(req, res, admin);
  });

  // Everything below needs a session; mutations also need the CSRF token.
  r.use(requireAuth, requireCsrf);

  // Until an admin has enrolled in 2FA, only the enrolment endpoints are reachable.
  const ENROL_PATHS = new Set(['GET /me', 'GET /me/2fa', 'POST /logout', 'POST /me/2fa/setup', 'POST /me/2fa/enable']);
  r.use((req, res, next) => {
    if (!config.require2fa || req.admin.mfa || ENROL_PATHS.has(`${req.method} ${req.path}`)) return next();
    res.status(403).json({ error: 'Aktifkan pengesahan dua langkah (2FA) dahulu.', mfa_setup_required: true });
  });

  r.get('/me', (req, res) => res.json({ user: { ...req.admin, require2fa: config.require2fa }, csrf: req.csrf }));

  // ---------- 2FA ----------
  const adminRow = (id) => db.prepare('SELECT * FROM admins WHERE id = ?').get(id);
  const needPassword = (row, pw) => { if (!verifyPassword(String(pw || ''), row.password_hash)) throw new ValidationError('Kata laluan salah.'); };
  const needCode = (row, code) => {
    const step = totp.verify(box.open(row.totp_secret_enc), code, row.totp_last_step);
    if (step === null) throw new ValidationError('Kod 2FA salah atau sudah digunakan.');
    db.prepare('UPDATE admins SET totp_last_step = ? WHERE id = ?').run(step, row.id);
  };
  const issueRecovery = (id) => {
    const codes = totp.newRecoveryCodes();
    db.prepare('UPDATE admins SET recovery_hashes = ? WHERE id = ?').run(JSON.stringify(codes.map((c) => sha256(totp.normalizeRecovery(c)))), id);
    return codes;
  };

  r.post('/me/2fa/setup', async (req, res) => {
    const row = adminRow(req.admin.id);
    if (row.totp_enabled) throw new ValidationError('2FA sudah aktif.');
    needPassword(row, req.body?.password);
    const secret = totp.newSecret();
    db.prepare('UPDATE admins SET totp_pending_enc = ? WHERE id = ?').run(box.seal(secret), row.id);
    const uri = totp.otpauthUri({ secret, account: row.email, issuer: config.issuer });
    const svg = await QRCode.toString(uri, { type: 'svg', margin: 1, errorCorrectionLevel: 'M' });
    log(req, '2fa_setup_started', 'admin', row.id);
    res.json({ secret, uri, qr: `data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}` });
  });

  r.post('/me/2fa/enable', (req, res) => {
    const row = adminRow(req.admin.id);
    if (row.totp_enabled) throw new ValidationError('2FA sudah aktif.');
    if (!row.totp_pending_enc) throw new ValidationError('Mulakan persediaan 2FA dahulu.');
    const step = totp.verify(box.open(row.totp_pending_enc), req.body?.code, 0);
    if (step === null) throw new ValidationError('Kod salah. Pastikan masa telefon tepat dan cuba kod terbaru.');
    db.prepare("UPDATE admins SET totp_secret_enc = totp_pending_enc, totp_pending_enc = '', totp_enabled = 1, totp_last_step = ? WHERE id = ?").run(step, row.id);
    const codes = issueRecovery(row.id);
    db.prepare('DELETE FROM sessions WHERE admin_id = ? AND id_hash != ?').run(row.id, req.sessionIdHash);
    log(req, '2fa_enabled', 'admin', row.id);
    res.json({ ok: true, recovery_codes: codes });
  });

  r.post('/me/2fa/recovery', (req, res) => {
    const row = adminRow(req.admin.id);
    if (!row.totp_enabled) throw new ValidationError('2FA belum aktif.');
    needPassword(row, req.body?.password);
    needCode(row, req.body?.code);
    const codes = issueRecovery(row.id);
    log(req, '2fa_recovery_regenerated', 'admin', row.id);
    res.json({ recovery_codes: codes });
  });

  r.post('/me/2fa/disable', (req, res) => {
    const row = adminRow(req.admin.id);
    if (!row.totp_enabled) throw new ValidationError('2FA belum aktif.');
    needPassword(row, req.body?.password);
    needCode(row, req.body?.code);
    db.prepare("UPDATE admins SET totp_enabled = 0, totp_secret_enc = '', totp_pending_enc = '', recovery_hashes = '[]', totp_last_step = 0 WHERE id = ?").run(row.id);
    log(req, '2fa_disabled', 'admin', row.id);
    res.json({ ok: true });
  });

  r.get('/me/2fa', (req, res) => {
    const row = adminRow(req.admin.id);
    res.json({ enabled: !!row.totp_enabled, recovery_left: JSON.parse(row.recovery_hashes || '[]').length, required: config.require2fa });
  });

  r.post('/logout', (req, res) => {
    log(req, 'logout', 'admin', req.admin.id);
    destroySession(db, config, req, res);
    res.json({ ok: true });
  });

  r.post('/me/password', (req, res) => {
    const row = db.prepare('SELECT password_hash FROM admins WHERE id = ?').get(req.admin.id);
    if (!verifyPassword(String(req.body?.current || ''), row.password_hash)) throw new ValidationError('Kata laluan semasa salah.');
    const problem = passwordProblem(req.body?.next);
    if (problem) throw new ValidationError(problem);
    db.prepare('UPDATE admins SET password_hash = ? WHERE id = ?').run(hashPassword(req.body.next), req.admin.id);
    // Sign out every other session of this admin.
    db.prepare('DELETE FROM sessions WHERE admin_id = ? AND id_hash != ?').run(req.admin.id, req.sessionIdHash);
    log(req, 'password_changed', 'admin', req.admin.id);
    res.json({ ok: true });
  });

  // ---------- overview ----------
  r.get('/stats', (req, res) => {
    const one = (sql) => db.prepare(sql).get().n;
    res.json({
      inquiriesNew: one("SELECT COUNT(*) n FROM inquiries WHERE status = 'new'"),
      inquiriesTotal: one('SELECT COUNT(*) n FROM inquiries'),
      brands: one("SELECT COUNT(*) n FROM brands WHERE status != 'hidden'"),
      brandsTbc: one("SELECT COUNT(*) n FROM brands WHERE fact_status = 'tbc'"),
      contentTbc: one("SELECT COUNT(*) n FROM content WHERE status = 'tbc'"),
      contentProposal: one("SELECT COUNT(*) n FROM content WHERE status = 'proposal'"),
      contentTotal: one('SELECT COUNT(*) n FROM content'),
      postsPublished: one("SELECT COUNT(*) n FROM posts WHERE status = 'published'"),
      postsDraft: one("SELECT COUNT(*) n FROM posts WHERE status = 'draft'"),
      draftMode: config.draft,
      recentInquiries: db.prepare('SELECT id, name, company, kind, status, created_at FROM inquiries ORDER BY created_at DESC LIMIT 5').all(),
    });
  });

  // ---------- brands ----------
  const FACT = ['confirmed', 'proposal', 'tbc'];
  r.get('/brands', (req, res) => res.json(db.prepare('SELECT * FROM brands ORDER BY sort_order').all()));
  r.put('/brands/:id', (req, res) => {
    const id = intId(req.params.id);
    if (!db.prepare('SELECT id FROM brands WHERE id = ?').get(id)) return res.status(404).json({ error: 'Jenama tidak dijumpai.' });
    const b = req.body || {};
    const v = {
      name: str(b.name, { field: 'Nama', max: 60, required: true }),
      role_line: str(b.role_line, { field: 'Fungsi', max: 120 }),
      description: str(b.description, { field: 'Penerangan', max: 1200, multiline: true }),
      fact_status: oneOf(b.fact_status, FACT, 'Status fakta'),
      status: oneOf(b.status, ['active', 'coming_soon', 'hidden'], 'Status paparan'),
      accent: hexColor(b.accent, 'Warna'),
      sort_order: Math.max(0, Math.min(99, Number.parseInt(b.sort_order, 10) || 0)),
      website_url: httpsUrl(b.website_url, 'Website'),
      instagram_url: httpsUrl(b.instagram_url, 'Instagram'),
      facebook_url: httpsUrl(b.facebook_url, 'Facebook'),
    };
    db.prepare(`UPDATE brands SET name=?, role_line=?, description=?, fact_status=?, status=?, accent=?, sort_order=?,
      website_url=?, instagram_url=?, facebook_url=?, updated_at=? WHERE id=?`)
      .run(v.name, v.role_line, v.description, v.fact_status, v.status, v.accent, v.sort_order,
        v.website_url, v.instagram_url, v.facebook_url, Date.now(), id);
    log(req, 'brand_updated', 'brand', id, v.name);
    res.json(db.prepare('SELECT * FROM brands WHERE id = ?').get(id));
  });

  // ---------- content ----------
  r.get('/content', (req, res) => res.json(db.prepare('SELECT * FROM content ORDER BY grp, sort_order').all()));
  r.put('/content/:key', (req, res) => {
    const key = String(req.params.key);
    const row = db.prepare('SELECT * FROM content WHERE key = ?').get(key);
    if (!row) return res.status(404).json({ error: 'Medan tidak dijumpai.' });
    const value = str(req.body?.value, { field: row.label, max: row.max_len, multiline: true });
    const status = oneOf(req.body?.status, FACT, 'Status');
    if (status !== 'tbc' && !value) throw new ValidationError(`${row.label}: isi nilai sebelum tukar status.`);
    db.prepare('UPDATE content SET value = ?, status = ?, updated_at = ? WHERE key = ?').run(value, status, Date.now(), key);
    log(req, 'content_updated', 'content', key, status);
    res.json(db.prepare('SELECT * FROM content WHERE key = ?').get(key));
  });

  // ---------- posts ----------
  const readPost = (b) => ({
    title: str(b.title, { field: 'Tajuk', max: 160, required: true }),
    slug: slug(b.slug),
    excerpt: str(b.excerpt, { field: 'Ringkasan', max: 300, multiline: true }),
    body: str(b.body, { field: 'Isi', max: 20000, multiline: true }),
    status: oneOf(b.status, ['draft', 'published'], 'Status'),
  });
  r.get('/posts', (req, res) => res.json(db.prepare('SELECT * FROM posts ORDER BY updated_at DESC').all()));
  r.post('/posts', (req, res) => {
    const p = readPost(req.body || {});
    if (db.prepare('SELECT id FROM posts WHERE slug = ?').get(p.slug)) throw new ValidationError('Slug sudah digunakan.');
    const now = Date.now();
    const info = db.prepare('INSERT INTO posts (slug, title, excerpt, body, status, published_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)')
      .run(p.slug, p.title, p.excerpt, p.body, p.status, p.status === 'published' ? now : null, now, now);
    log(req, 'post_created', 'post', info.lastInsertRowid, p.title);
    res.status(201).json(db.prepare('SELECT * FROM posts WHERE id = ?').get(info.lastInsertRowid));
  });
  r.put('/posts/:id', (req, res) => {
    const id = intId(req.params.id);
    const cur = db.prepare('SELECT * FROM posts WHERE id = ?').get(id);
    if (!cur) return res.status(404).json({ error: 'Berita tidak dijumpai.' });
    const p = readPost(req.body || {});
    if (db.prepare('SELECT id FROM posts WHERE slug = ? AND id != ?').get(p.slug, id)) throw new ValidationError('Slug sudah digunakan.');
    const publishedAt = p.status === 'published' ? (cur.published_at || Date.now()) : null;
    db.prepare('UPDATE posts SET slug=?, title=?, excerpt=?, body=?, status=?, published_at=?, updated_at=? WHERE id=?')
      .run(p.slug, p.title, p.excerpt, p.body, p.status, publishedAt, Date.now(), id);
    log(req, 'post_updated', 'post', id, p.status);
    res.json(db.prepare('SELECT * FROM posts WHERE id = ?').get(id));
  });
  r.delete('/posts/:id', (req, res) => {
    const id = intId(req.params.id);
    const info = db.prepare('DELETE FROM posts WHERE id = ?').run(id);
    if (!info.changes) return res.status(404).json({ error: 'Berita tidak dijumpai.' });
    log(req, 'post_deleted', 'post', id);
    res.json({ ok: true });
  });

  // ---------- inquiries ----------
  r.get('/inquiries', (req, res) => {
    const status = ['new', 'read', 'archived'].includes(req.query.status) ? req.query.status : null;
    const rows = status
      ? db.prepare('SELECT id, name, email, company, kind, message, consent, status, created_at FROM inquiries WHERE status = ? ORDER BY created_at DESC LIMIT 500').all(status)
      : db.prepare('SELECT id, name, email, company, kind, message, consent, status, created_at FROM inquiries ORDER BY created_at DESC LIMIT 500').all();
    res.json(rows);
  });
  r.patch('/inquiries/:id', (req, res) => {
    const id = intId(req.params.id);
    const status = oneOf(req.body?.status, ['new', 'read', 'archived'], 'Status');
    const info = db.prepare('UPDATE inquiries SET status = ? WHERE id = ?').run(status, id);
    if (!info.changes) return res.status(404).json({ error: 'Pertanyaan tidak dijumpai.' });
    log(req, 'inquiry_status', 'inquiry', id, status);
    res.json({ ok: true });
  });
  r.delete('/inquiries/:id', requireRole('owner'), (req, res) => {
    const id = intId(req.params.id);
    const info = db.prepare('DELETE FROM inquiries WHERE id = ?').run(id);
    if (!info.changes) return res.status(404).json({ error: 'Pertanyaan tidak dijumpai.' });
    log(req, 'inquiry_deleted', 'inquiry', id);
    res.json({ ok: true });
  });

  // ---------- admins (owner only) ----------
  r.get('/admins', requireRole('owner'), (req, res) => {
    res.json(db.prepare('SELECT id, email, name, role, active, locked_until, created_at, last_login_at, totp_enabled FROM admins ORDER BY id').all());
  });
  r.post('/admins', requireRole('owner'), (req, res) => {
    const b = req.body || {};
    const em = email(b.email);
    const name = str(b.name, { field: 'Nama', max: 80, required: true });
    const role = oneOf(b.role, ['owner', 'editor'], 'Peranan');
    const problem = passwordProblem(b.password);
    if (problem) throw new ValidationError(problem);
    if (findAdmin.get(em)) throw new ValidationError('Emel sudah didaftarkan.');
    const info = db.prepare('INSERT INTO admins (email, name, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)')
      .run(em, name, hashPassword(b.password), role, Date.now());
    log(req, 'admin_created', 'admin', info.lastInsertRowid, role);
    res.status(201).json({ id: info.lastInsertRowid });
  });
  r.patch('/admins/:id', requireRole('owner'), (req, res) => {
    const id = intId(req.params.id);
    if (id === req.admin.id) throw new ValidationError('Anda tidak boleh ubah peranan atau status akaun sendiri.');
    const target = db.prepare('SELECT * FROM admins WHERE id = ?').get(id);
    if (!target) return res.status(404).json({ error: 'Admin tidak dijumpai.' });
    const role = oneOf(req.body?.role ?? target.role, ['owner', 'editor'], 'Peranan');
    const active = req.body?.active === undefined ? target.active : (req.body.active ? 1 : 0);
    db.prepare('UPDATE admins SET role = ?, active = ?, locked_until = CASE WHEN ? THEN NULL ELSE locked_until END, failed_attempts = 0 WHERE id = ?')
      .run(role, active, req.body?.unlock ? 1 : 0, id);
    if (req.body?.reset_2fa) {
      // Break-glass for a lost phone: the admin must enrol again at next login.
      db.prepare("UPDATE admins SET totp_enabled = 0, totp_secret_enc = '', totp_pending_enc = '', recovery_hashes = '[]', totp_last_step = 0 WHERE id = ?").run(id);
      db.prepare('DELETE FROM sessions WHERE admin_id = ?').run(id);
      log(req, '2fa_reset_by_owner', 'admin', id);
    }
    if (!active) db.prepare('DELETE FROM sessions WHERE admin_id = ?').run(id);
    log(req, 'admin_updated', 'admin', id, `role=${role} active=${active}`);
    res.json({ ok: true });
  });

  r.get('/audit', requireRole('owner'), (req, res) => {
    res.json(db.prepare(`SELECT l.id, l.action, l.entity, l.entity_id, l.detail, l.created_at, a.email AS admin_email
      FROM audit_log l LEFT JOIN admins a ON a.id = l.admin_id ORDER BY l.id DESC LIMIT 200`).all());
  });

  r.use((req, res) => res.status(404).json({ error: 'Tidak dijumpai.' }));
  // eslint-disable-next-line no-unused-vars
  r.use((err, req, res, next) => {
    if (err.type === 'entity.parse.failed') return res.status(400).json({ error: 'JSON tidak sah.' });
    if (err.type === 'entity.too.large') return res.status(413).json({ error: 'Data terlalu besar.' });
    if (err.expose && err.status < 500) return res.status(err.status).json({ error: err.message });
    console.error('[admin-api]', err);
    res.status(500).json({ error: 'Ralat pelayan.' });
  });

  return r;
};
