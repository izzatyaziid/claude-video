'use strict';
// Creates (or resets) an admin account. There is no default password anywhere in the code.
// Usage: ADMIN_EMAIL=you@domain ADMIN_NAME="Nama" ADMIN_PASSWORD='...' [ADMIN_ROLE=owner|editor] npm run create-admin
const { baseConfig } = require('../src/config');
const { openDb } = require('../src/db');
const { hashPassword, passwordProblem, email } = require('../src/security');

function main() {
  const em = email(process.env.ADMIN_EMAIL || '');
  const name = (process.env.ADMIN_NAME || '').trim() || em.split('@')[0];
  const role = process.env.ADMIN_ROLE === 'editor' ? 'editor' : 'owner';
  const pw = process.env.ADMIN_PASSWORD || '';
  const problem = passwordProblem(pw);
  if (problem) throw new Error(problem);

  const db = openDb(baseConfig.dbFile);
  const existing = db.prepare('SELECT id FROM admins WHERE email = ?').get(em);
  if (existing) {
    db.prepare('UPDATE admins SET password_hash = ?, role = ?, active = 1, failed_attempts = 0, locked_until = NULL WHERE id = ?')
      .run(hashPassword(pw), role, existing.id);
    db.prepare('DELETE FROM sessions WHERE admin_id = ?').run(existing.id);
    console.log(`Admin ${em} dikemas kini (peranan: ${role}). Semua sesi lama ditamatkan.`);
  } else {
    db.prepare('INSERT INTO admins (email, name, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)')
      .run(em, name, hashPassword(pw), role, Date.now());
    console.log(`Admin ${em} dicipta (peranan: ${role}).`);
  }
}

try { main(); } catch (err) { console.error('Gagal:', err.message); process.exit(1); }
