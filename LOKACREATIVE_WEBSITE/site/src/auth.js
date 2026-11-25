'use strict';
const { sha256, randomToken, safeEqual, hashIp } = require('./security');

function cookieName(config) {
  // __Host- prefix forces Secure, Path=/ and no Domain: the cookie cannot be set by subdomains.
  return config.isProd ? '__Host-lcv_sid' : 'lcv_sid';
}

function parseCookies(header) {
  const out = {};
  for (const part of String(header || '').split(';')) {
    const i = part.indexOf('=');
    if (i < 0) continue;
    const k = part.slice(0, i).trim();
    if (k && !(k in out)) out[k] = decodeURIComponent(part.slice(i + 1).trim());
  }
  return out;
}

function setSessionCookie(res, config, value, maxAgeMs) {
  const attrs = [`${cookieName(config)}=${value}`, 'Path=/', 'HttpOnly', 'SameSite=Strict'];
  if (config.isProd) attrs.push('Secure');
  attrs.push(maxAgeMs > 0 ? `Max-Age=${Math.floor(maxAgeMs / 1000)}` : 'Max-Age=0');
  res.append('Set-Cookie', attrs.join('; '));
}

function createSession(db, config, res, adminId) {
  const sid = randomToken(32);
  const csrf = randomToken(32);
  const now = Date.now();
  db.prepare('INSERT INTO sessions (id_hash, admin_id, csrf, created_at, last_seen_at) VALUES (?, ?, ?, ?, ?)')
    .run(sha256(sid), adminId, csrf, now, now);
  setSessionCookie(res, config, sid, config.sessionMaxMs);
  return csrf;
}

function destroySession(db, config, req, res) {
  if (req.sessionIdHash) db.prepare('DELETE FROM sessions WHERE id_hash = ?').run(req.sessionIdHash);
  setSessionCookie(res, config, '', 0);
}

// Attaches req.admin and req.csrf when a valid session cookie is present.
function sessionMiddleware(db, config) {
  const find = db.prepare(`SELECT s.id_hash, s.csrf, s.created_at, s.last_seen_at,
      a.id, a.email, a.name, a.role, a.active, a.totp_enabled
    FROM sessions s JOIN admins a ON a.id = s.admin_id WHERE s.id_hash = ?`);
  const touch = db.prepare('UPDATE sessions SET last_seen_at = ? WHERE id_hash = ?');
  const del = db.prepare('DELETE FROM sessions WHERE id_hash = ?');
  const sweep = db.prepare('DELETE FROM sessions WHERE last_seen_at < ? OR created_at < ?');
  let lastSweep = 0;

  return (req, res, next) => {
    const now = Date.now();
    req.ipHash = hashIp(req.ip, config.ipSalt);
    if (now - lastSweep > 10 * 60 * 1000) {
      sweep.run(now - config.sessionIdleMs, now - config.sessionMaxMs);
      lastSweep = now;
    }
    const sid = parseCookies(req.headers.cookie)[cookieName(config)];
    if (!sid || sid.length > 100) return next();
    const idHash = sha256(sid);
    const row = find.get(idHash);
    if (!row) return next();
    const expired = now - row.last_seen_at > config.sessionIdleMs || now - row.created_at > config.sessionMaxMs;
    if (expired || !row.active) {
      del.run(idHash);
      setSessionCookie(res, config, '', 0);
      return next();
    }
    if (now - row.last_seen_at > 60 * 1000) touch.run(now, idHash);
    req.sessionIdHash = idHash;
    req.csrf = row.csrf;
    req.admin = { id: row.id, email: row.email, name: row.name, role: row.role, mfa: !!row.totp_enabled };
    next();
  };
}

function requireAuth(req, res, next) {
  if (!req.admin) return res.status(401).json({ error: 'Sila log masuk.' });
  next();
}

function requireRole(role) {
  return (req, res, next) => {
    if (!req.admin) return res.status(401).json({ error: 'Sila log masuk.' });
    if (req.admin.role !== role) return res.status(403).json({ error: 'Akses tidak dibenarkan untuk peranan anda.' });
    next();
  };
}

function requireCsrf(req, res, next) {
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) return next();
  if (!req.admin || !safeEqual(req.get('x-csrf-token'), req.csrf)) {
    return res.status(403).json({ error: 'Token CSRF tidak sah. Muat semula halaman.' });
  }
  next();
}

module.exports = {
  cookieName, parseCookies, createSession, destroySession, sessionMiddleware, requireAuth, requireRole, requireCsrf,
};
