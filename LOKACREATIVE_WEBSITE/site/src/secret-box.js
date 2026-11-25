'use strict';
// AES-256-GCM encryption for secrets at rest (2FA seeds). A database leak alone does not reveal them.
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

function loadKey(config) {
  if (config.dataKey) {
    const k = Buffer.from(config.dataKey, 'hex');
    if (k.length !== 32) throw new Error('DATA_ENC_KEY mesti 64 aksara hex (32 bait).');
    return k;
  }
  if (config.isProd) throw new Error('DATA_ENC_KEY diperlukan dalam production.');
  // Development: keep a key file beside the database so 2FA survives restarts. Never commit it.
  if (config.dbFile === ':memory:') return crypto.randomBytes(32);
  const file = path.join(path.dirname(config.dbFile), '.dev-data-key');
  if (!fs.existsSync(file)) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, crypto.randomBytes(32).toString('hex'), { mode: 0o600 });
  }
  return Buffer.from(fs.readFileSync(file, 'utf8').trim(), 'hex');
}

function makeBox(config) {
  const key = loadKey(config);
  return {
    seal(plain) {
      const iv = crypto.randomBytes(12);
      const c = crypto.createCipheriv('aes-256-gcm', key, iv);
      const ct = Buffer.concat([c.update(String(plain), 'utf8'), c.final()]);
      return `v1.${iv.toString('base64url')}.${c.getAuthTag().toString('base64url')}.${ct.toString('base64url')}`;
    },
    open(sealed) {
      const [v, iv, tag, ct] = String(sealed || '').split('.');
      if (v !== 'v1' || !iv || !tag || !ct) throw new Error('sealed value invalid');
      const d = crypto.createDecipheriv('aes-256-gcm', key, Buffer.from(iv, 'base64url'));
      d.setAuthTag(Buffer.from(tag, 'base64url'));
      return Buffer.concat([d.update(Buffer.from(ct, 'base64url')), d.final()]).toString('utf8');
    },
  };
}

module.exports = { makeBox };
