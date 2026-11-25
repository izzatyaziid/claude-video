'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { DatabaseSync } = require('node:sqlite');

const SCHEMA = `
CREATE TABLE IF NOT EXISTS admins (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE COLLATE NOCASE,
  name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('owner','editor')),
  active INTEGER NOT NULL DEFAULT 1,
  failed_attempts INTEGER NOT NULL DEFAULT 0,
  locked_until INTEGER,
  created_at INTEGER NOT NULL,
  last_login_at INTEGER
);
CREATE TABLE IF NOT EXISTS sessions (
  id_hash TEXT PRIMARY KEY,
  admin_id INTEGER NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
  csrf TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  last_seen_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS brands (
  id INTEGER PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  role_line TEXT NOT NULL DEFAULT '',
  description TEXT NOT NULL DEFAULT '',
  fact_status TEXT NOT NULL DEFAULT 'tbc' CHECK (fact_status IN ('confirmed','proposal','tbc')),
  status TEXT NOT NULL DEFAULT 'coming_soon' CHECK (status IN ('active','coming_soon','hidden')),
  accent TEXT NOT NULL DEFAULT '#4A4E55',
  sort_order INTEGER NOT NULL DEFAULT 0,
  website_url TEXT NOT NULL DEFAULT '',
  instagram_url TEXT NOT NULL DEFAULT '',
  facebook_url TEXT NOT NULL DEFAULT '',
  updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS content (
  key TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  grp TEXT NOT NULL,
  value TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'tbc' CHECK (status IN ('confirmed','proposal','tbc')),
  max_len INTEGER NOT NULL DEFAULT 600,
  sort_order INTEGER NOT NULL DEFAULT 0,
  updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  excerpt TEXT NOT NULL DEFAULT '',
  body TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','published')),
  published_at INTEGER,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS inquiries (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  company TEXT NOT NULL DEFAULT '',
  kind TEXT NOT NULL,
  message TEXT NOT NULL,
  consent INTEGER NOT NULL,
  ip_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new','read','archived')),
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY,
  admin_id INTEGER,
  action TEXT NOT NULL,
  entity TEXT NOT NULL DEFAULT '',
  entity_id TEXT NOT NULL DEFAULT '',
  detail TEXT NOT NULL DEFAULT '',
  ip_hash TEXT NOT NULL DEFAULT '',
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_admin ON sessions(admin_id);
CREATE INDEX IF NOT EXISTS idx_inquiries_created ON inquiries(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);
`;

// Only facts recorded in LOKACREATIVE_WEBSITE docs (W01–W03). Everything else is TBC.
const SEED_BRANDS = [
  { code: 'LCV-01', slug: 'lokadigital', name: 'LokaDigital', role_line: 'Agensi digital marketing high-end',
    description: 'Strategi content dan ads berasaskan insight audience dan data.', fact_status: 'confirmed', status: 'active',
    accent: '#602AC8', instagram_url: 'https://www.instagram.com/lokadigitalmy', facebook_url: 'https://www.facebook.com/lokadigitalmy' },
  { code: 'LCV-02', slug: 'lokafoodie', name: 'LokaFoodie', accent: '#C2410C' },
  { code: 'LCV-03', slug: 'lokadaily', name: 'LokaDaily', accent: '#0B7285' },
  { code: 'LCV-04', slug: 'lokatalent', name: 'LokaTalent', accent: '#A61E4D' },
  { code: 'LCV-05', slug: 'lokacommerce', name: 'LokaCommerce', accent: '#2B8A3E' },
  { code: 'LCV-06', slug: 'loka-brands', name: 'Loka Brands', accent: '#5C5F66' },
];

// [key, label, group, value, status, max_len]
const SEED_CONTENT = [
  ['company_name', 'Nama syarikat', 'Syarikat', 'LokaCreative Ventures', 'confirmed', 80],
  ['legal_name', 'Nama entiti berdaftar', 'Syarikat', '', 'tbc', 120],
  ['founded_year', 'Tahun ditubuhkan', 'Syarikat', '', 'tbc', 4],
  ['hero_headline', 'Headline hero', 'Laman utama', 'Satu kumpulan. Banyak jenama.', 'proposal', 80],
  ['hero_sub', 'Subteks hero', 'Laman utama', 'Syarikat induk di sebalik ekosistem jenama Loka.', 'proposal', 200],
  ['about_short', 'Siapa kami (ringkas)', 'Tentang', '', 'tbc', 400],
  ['about_long', 'Cerita syarikat', 'Tentang', '', 'tbc', 3000],
  ['vision', 'Visi', 'Tentang', '', 'tbc', 300],
  ['mission', 'Misi', 'Tentang', '', 'tbc', 300],
  ['values', 'Nilai teras', 'Tentang', '', 'tbc', 400],
  ['proof_note', 'Bukti / pencapaian yang boleh disahkan', 'Laman utama', '', 'tbc', 400],
  ['partner_cta_title', 'Tajuk CTA kerjasama', 'Laman utama', 'Mari bina sesuatu bersama.', 'proposal', 80],
  ['partner_cta_body', 'Teks CTA kerjasama', 'Laman utama', '', 'tbc', 300],
  ['contact_email', 'Emel rasmi', 'Hubungi', '', 'tbc', 120],
  ['contact_phone', 'Telefon rasmi', 'Hubungi', '', 'tbc', 30],
  ['contact_address', 'Alamat', 'Hubungi', '', 'tbc', 300],
];

function openDb(file) {
  if (file !== ':memory:') fs.mkdirSync(path.dirname(file), { recursive: true });
  const db = new DatabaseSync(file);
  db.exec('PRAGMA foreign_keys = ON;');
  if (file !== ':memory:') db.exec('PRAGMA journal_mode = WAL;');
  db.exec(SCHEMA);
  seed(db);
  return db;
}

function seed(db) {
  const now = Date.now();
  const hasBrands = db.prepare('SELECT COUNT(*) AS n FROM brands').get().n > 0;
  if (!hasBrands) {
    const ins = db.prepare(`INSERT INTO brands (code, slug, name, role_line, description, fact_status, status, accent, sort_order, instagram_url, facebook_url, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`);
    SEED_BRANDS.forEach((b, i) => ins.run(b.code, b.slug, b.name, b.role_line || '', b.description || '',
      b.fact_status || 'tbc', b.status || 'coming_soon', b.accent, i + 1, b.instagram_url || '', b.facebook_url || '', now));
  }
  const insC = db.prepare(`INSERT OR IGNORE INTO content (key, label, grp, value, status, max_len, sort_order, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)`);
  SEED_CONTENT.forEach((c, i) => insC.run(c[0], c[1], c[2], c[3], c[4], c[5], i + 1, now));
}

function contentMap(db) {
  const out = {};
  for (const r of db.prepare('SELECT key, value, status, label FROM content').all()) out[r.key] = r;
  return out;
}

module.exports = { openDb, contentMap };
