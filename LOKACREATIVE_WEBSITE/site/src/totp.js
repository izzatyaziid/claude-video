'use strict';
// TOTP (RFC 6238, SHA-1, 30 s, 6 digits): works with Google Authenticator, Microsoft Authenticator, Authy, 1Password.
const crypto = require('node:crypto');

const ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';

function base32Encode(buf) {
  let bits = 0, value = 0, out = '';
  for (const byte of buf) {
    value = (value << 8) | byte; bits += 8;
    while (bits >= 5) { out += ALPHA[(value >>> (bits - 5)) & 31]; bits -= 5; }
  }
  if (bits > 0) out += ALPHA[(value << (5 - bits)) & 31];
  return out;
}

function base32Decode(str) {
  const clean = String(str).toUpperCase().replace(/=+$/, '').replace(/\s+/g, '');
  let bits = 0, value = 0; const out = [];
  for (const ch of clean) {
    const i = ALPHA.indexOf(ch);
    if (i < 0) throw new Error('invalid base32');
    value = (value << 5) | i; bits += 5;
    if (bits >= 8) { out.push((value >>> (bits - 8)) & 255); bits -= 8; }
  }
  return Buffer.from(out);
}

function hotp(key, counter, digits = 6) {
  const msg = Buffer.alloc(8);
  msg.writeBigUInt64BE(BigInt(counter));
  const h = crypto.createHmac('sha1', key).update(msg).digest();
  const o = h[h.length - 1] & 0x0f;
  const bin = h.readUInt32BE(o) & 0x7fffffff;
  return String(bin % 10 ** digits).padStart(digits, '0');
}

const STEP = 30;
const stepAt = (ms) => Math.floor(ms / 1000 / STEP);

function newSecret() {
  return base32Encode(crypto.randomBytes(20)); // 160-bit, as RFC 4226 recommends
}

// Returns the matched time step (to block replay), or null. Accepts ±1 step of clock drift.
function verify(secretB32, code, lastStep = 0, now = Date.now()) {
  const c = String(code || '').replace(/\s+/g, '');
  if (!/^\d{6}$/.test(c)) return null;
  const key = base32Decode(secretB32);
  const cur = stepAt(now);
  for (const s of [cur - 1, cur, cur + 1]) {
    if (s <= lastStep) continue;
    const expected = Buffer.from(hotp(key, s));
    if (crypto.timingSafeEqual(expected, Buffer.from(c))) return s;
  }
  return null;
}

function otpauthUri({ secret, account, issuer }) {
  const label = encodeURIComponent(`${issuer}:${account}`);
  return `otpauth://totp/${label}?secret=${secret}&issuer=${encodeURIComponent(issuer)}&algorithm=SHA1&digits=6&period=${STEP}`;
}

// Recovery codes: 10 one-time codes, shown once, stored only as SHA-256 hashes.
function newRecoveryCodes(n = 10) {
  return Array.from({ length: n }, () => {
    const raw = base32Encode(crypto.randomBytes(7)).slice(0, 10);
    return `${raw.slice(0, 5)}-${raw.slice(5)}`;
  });
}
const normalizeRecovery = (c) => String(c || '').toUpperCase().replace(/[^A-Z2-7]/g, '');

module.exports = { base32Encode, base32Decode, hotp, verify, newSecret, otpauthUri, newRecoveryCodes, normalizeRecovery, stepAt };
