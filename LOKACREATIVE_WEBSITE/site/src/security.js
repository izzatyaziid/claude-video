'use strict';
const crypto = require('node:crypto');

// ---------- hashing ----------
const SCRYPT = { N: 16384, r: 8, p: 1, keylen: 64 };

function hashPassword(password) {
  const salt = crypto.randomBytes(16);
  const key = crypto.scryptSync(password, salt, SCRYPT.keylen, { N: SCRYPT.N, r: SCRYPT.r, p: SCRYPT.p });
  return `scrypt$${SCRYPT.N}$${SCRYPT.r}$${SCRYPT.p}$${salt.toString('base64')}$${key.toString('base64')}`;
}

// A fixed hash so unknown emails cost the same time as known ones (no user enumeration by timing).
const DUMMY_HASH = hashPassword(crypto.randomBytes(24).toString('hex'));

function verifyPassword(password, stored) {
  const parts = String(stored || DUMMY_HASH).split('$');
  if (parts.length !== 6 || parts[0] !== 'scrypt') return false;
  const [, N, r, p, saltB64, keyB64] = parts;
  const expected = Buffer.from(keyB64, 'base64');
  const actual = crypto.scryptSync(String(password), Buffer.from(saltB64, 'base64'), expected.length,
    { N: Number(N), r: Number(r), p: Number(p) });
  return crypto.timingSafeEqual(actual, expected);
}

function sha256(s) {
  return crypto.createHash('sha256').update(s).digest('hex');
}

function hashIp(ip, salt) {
  return sha256(`${salt}:${ip || ''}`).slice(0, 32);
}

function randomToken(bytes = 32) {
  return crypto.randomBytes(bytes).toString('base64url');
}

function safeEqual(a, b) {
  const x = Buffer.from(String(a || ''));
  const y = Buffer.from(String(b || ''));
  return x.length === y.length && x.length > 0 && crypto.timingSafeEqual(x, y);
}

// ---------- password policy ----------
function passwordProblem(pw) {
  if (typeof pw !== 'string' || pw.length < 12) return 'Kata laluan mesti sekurang-kurangnya 12 aksara.';
  if (pw.length > 200) return 'Kata laluan terlalu panjang.';
  const classes = [/[a-z]/, /[A-Z]/, /[0-9]/, /[^A-Za-z0-9]/].filter((re) => re.test(pw)).length;
  if (classes < 3) return 'Guna sekurang-kurangnya 3 jenis: huruf kecil, huruf besar, nombor, simbol.';
  return null;
}

// ---------- same-origin check for state-changing requests ----------
function originAllowed(req, config) {
  const origin = req.get('origin');
  const referer = req.get('referer');
  let source = origin;
  if (!source && referer) {
    try { source = new URL(referer).origin; } catch { return false; }
  }
  if (!source) return false;
  if (config.siteOrigin) return source === config.siteOrigin;
  try { return new URL(source).host === req.get('host'); } catch { return false; }
}

function requireSameOrigin(config) {
  return (req, res, next) => {
    if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) return next();
    if (!originAllowed(req, config)) return res.status(403).json({ error: 'Permintaan ditolak (origin).' });
    next();
  };
}

// ---------- validation ----------
class ValidationError extends Error {
  constructor(message) { super(message); this.status = 400; this.expose = true; }
}

function str(v, { field, max, min = 0, required = false, multiline = false }) {
  if (v === undefined || v === null) v = '';
  if (typeof v !== 'string') throw new ValidationError(`${field}: format tidak sah.`);
  // Strip control chars (keep newlines/tabs for multiline fields).
  v = multiline ? v.replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '') : v.replace(/[\u0000-\u001F\u007F]/g, ' ');
  v = v.trim();
  if (required && !v) throw new ValidationError(`${field}: wajib diisi.`);
  if (v.length < min) throw new ValidationError(`${field}: terlalu pendek.`);
  if (v.length > max) throw new ValidationError(`${field}: maksimum ${max} aksara.`);
  return v;
}

function oneOf(v, allowed, field) {
  if (!allowed.includes(v)) throw new ValidationError(`${field}: nilai tidak sah.`);
  return v;
}

const EMAIL_RE = /^[^\s@<>()[\]\\,;:"]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$/;
function email(v, field = 'Emel', { required = true } = {}) {
  v = str(v, { field, max: 254, required });
  if (v && !EMAIL_RE.test(v)) throw new ValidationError(`${field}: format emel tidak sah.`);
  return v.toLowerCase();
}

// Only https links (blocks javascript:, data:, http:).
function httpsUrl(v, field) {
  v = str(v, { field, max: 300 });
  if (!v) return '';
  let u;
  try { u = new URL(v); } catch { throw new ValidationError(`${field}: URL tidak sah.`); }
  if (u.protocol !== 'https:' || u.username || u.password) throw new ValidationError(`${field}: mesti bermula dengan https://`);
  return u.toString();
}

function hexColor(v, field) {
  if (typeof v !== 'string' || !/^#[0-9A-Fa-f]{6}$/.test(v)) throw new ValidationError(`${field}: warna mesti format #RRGGBB.`);
  return v.toUpperCase();
}

function slug(v, field = 'Slug') {
  v = str(v, { field, max: 80, required: true }).toLowerCase();
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(v)) throw new ValidationError(`${field}: guna huruf kecil, nombor dan tanda sempang sahaja.`);
  return v;
}

function intId(v) {
  const n = Number(v);
  if (!Number.isSafeInteger(n) || n <= 0) throw new ValidationError('ID tidak sah.');
  return n;
}

module.exports = {
  hashPassword, verifyPassword, sha256, hashIp, randomToken, safeEqual, passwordProblem,
  originAllowed, requireSameOrigin, ValidationError, str, oneOf, email, httpsUrl, hexColor, slug, intId,
};
