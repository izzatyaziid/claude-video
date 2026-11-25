'use strict';
const path = require('node:path');
const crypto = require('node:crypto');

const isProd = process.env.NODE_ENV === 'production';

const baseConfig = {
  isProd,
  port: Number(process.env.PORT) || 3000,
  dbFile: process.env.DB_FILE || path.join(__dirname, '..', 'data', 'lokacreative.db'),
  // Draft mode shows TBC / CADANGAN markers on the public site. Turn off only after content is approved.
  draft: process.env.SITE_DRAFT !== '0',
  // Exact public origin, e.g. https://lokacreative.com.my. Required in production for Origin checks.
  siteOrigin: process.env.SITE_ORIGIN || '',
  trustProxy: process.env.TRUST_PROXY === '1',
  // Salt for hashing visitor IPs (PDPA: no raw IPs stored). Random per boot in development.
  ipSalt: process.env.IP_HASH_SALT || crypto.randomBytes(16).toString('hex'),
  sessionIdleMs: 30 * 60 * 1000,
  sessionMaxMs: 8 * 60 * 60 * 1000,
  loginLimit: 10, // login attempts per IP per 15 minutes
  lockoutAfter: 5, // failed attempts before an account is locked
  lockoutMs: 15 * 60 * 1000,
  contactLimit: 5, // contact form posts per IP per hour
  // 32-byte hex key encrypting 2FA secrets at rest. Required in production; dev keeps a key file beside the DB.
  dataKey: process.env.DATA_ENC_KEY || '',
  // Every admin must enrol in 2FA before using the dashboard. Set REQUIRE_2FA=0 only for local testing.
  require2fa: process.env.REQUIRE_2FA !== '0',
  mfaChallengeMs: 5 * 60 * 1000,
  mfaMaxAttempts: 5,
  issuer: 'LokaCreative Ventures',
};

function assertProdConfig(c) {
  if (!c.isProd) return;
  const missing = [];
  if (!/^https:\/\/[^/]+$/.test(c.siteOrigin)) missing.push('SITE_ORIGIN (https://domain, no trailing slash)');
  if (!process.env.IP_HASH_SALT || process.env.IP_HASH_SALT.length < 16) missing.push('IP_HASH_SALT (min 16 chars)');
  if (!/^[0-9a-fA-F]{64}$/.test(c.dataKey)) missing.push('DATA_ENC_KEY (64 hex chars)');
  if (!c.require2fa) missing.push('REQUIRE_2FA must not be 0 in production');
  if (missing.length) throw new Error('Missing production config: ' + missing.join(', '));
}

module.exports = { baseConfig, assertProdConfig };
