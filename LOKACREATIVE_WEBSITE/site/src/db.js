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
CREATE TABLE IF NOT EXISTS mfa_challenges (
  id_hash TEXT PRIMARY KEY,
  admin_id INTEGER NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
  attempts INTEGER NOT NULL DEFAULT 0,
  expires_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_admin ON sessions(admin_id);
CREATE INDEX IF NOT EXISTS idx_inquiries_created ON inquiries(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);
`;

// Only facts with a source (see 01_BRAND_AND_BUSINESS/BRAND_SOURCES.md). Everything else is TBC.
// Colour: only LokaDigital has a documented brand colour; others stay neutral until supplied.
const NEUTRAL = '#8A8A8A';
// Logos: files supplied by the owner on 2026-11-25 (07_ASSETS/logos/). logo_bg = the logo file's own background colour.
// Owner asked to show only brands that have a logo for now; the others stay in the dashboard as hidden.
const SEED_BRANDS = [
  { code: 'LCV-01', slug: 'lokadigital', name: 'LokaDigital', role_line: 'Agensi digital marketing high-end',
    description: 'Strategi content dan ads berasaskan insight audience dan data.', fact_status: 'confirmed', status: 'active',
    accent: '#602AC8', logo: '/assets/brands/lokadigital.png', logo_bg: '#000000',
    instagram_url: 'https://www.instagram.com/lokadigitalmy', facebook_url: 'https://www.facebook.com/lokadigitalmy' },
  { code: 'LCV-02', slug: 'lokafoodie', name: 'LokaFoodie', role_line: 'Food review, kempen dan advertising',
    description: 'Media food review untuk audience niche: foodie, lifestyle dan travel. Berpangkalan di Kuala Lumpur.',
    fact_status: 'confirmed', status: 'active', accent: NEUTRAL, logo: '/assets/brands/lokafoodie.png', logo_bg: '#000000',
    instagram_url: 'https://www.instagram.com/lokafoodie' },
  { code: 'LCV-03', slug: 'lokadaily', name: 'LokaDaily', accent: '#055D24', logo: '/assets/brands/lokadaily.png', logo_bg: '#055D24' },
  { code: 'LCV-04', slug: 'lokatalent', name: 'LokaTalent', accent: NEUTRAL, status: 'hidden' },
  { code: 'LCV-05', slug: 'lokacommerce', name: 'LokaCommerce', accent: NEUTRAL, status: 'hidden' },
  { code: 'LCV-06', slug: 'loka-brands', name: 'Loka Brands', accent: NEUTRAL, status: 'hidden' },
  { code: 'LCV-07', slug: 'lokatrication', name: 'Lokatrication', accent: '#005D92', logo: '/assets/brands/lokatrication.png', logo_bg: '#005D92' },
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
  // Source: Canva deck "Lokacreative Ventures" (closing page) and "Rate Card LokaFoodie". Proposal until the owner confirms.
  ['contact_email', 'Emel rasmi', 'Hubungi', 'lokadigitalmy@gmail.com', 'proposal', 120],
  ['contact_phone', 'Telefon rasmi', 'Hubungi', '013-996 7524', 'proposal', 30],
  ['contact_address', 'Alamat', 'Hubungi', 'Kuala Lumpur, Malaysia', 'proposal', 300],
];

function openDb(file) {
  if (file !== ':memory:') fs.mkdirSync(path.dirname(file), { recursive: true });
  const db = new DatabaseSync(file);
  db.exec('PRAGMA foreign_keys = ON;');
  if (file !== ':memory:') db.exec('PRAGMA journal_mode = WAL;');
  db.exec(SCHEMA);
  migrate(db);
  seed(db);
  return db;
}

// Adds columns introduced after the first release, so existing databases keep working.
function migrate(db) {
  const cols = (t) => new Set(db.prepare(`PRAGMA table_info(${t})`).all().map((c) => c.name));
  const add = (t, name, def) => { if (!cols(t).has(name)) db.exec(`ALTER TABLE ${t} ADD COLUMN ${name} ${def}`); };
  add('admins', 'totp_secret_enc', "TEXT NOT NULL DEFAULT ''");
  add('admins', 'totp_pending_enc', "TEXT NOT NULL DEFAULT ''");
  add('admins', 'totp_enabled', 'INTEGER NOT NULL DEFAULT 0');
  add('admins', 'totp_last_step', 'INTEGER NOT NULL DEFAULT 0');
  add('admins', 'recovery_hashes', "TEXT NOT NULL DEFAULT '[]'");
  add('brands', 'logo', "TEXT NOT NULL DEFAULT ''");
  add('brands', 'logo_bg', "TEXT NOT NULL DEFAULT '#000000'");
}

function seed(db) {
  const now = Date.now();
  const hasBrands = db.prepare('SELECT COUNT(*) AS n FROM brands').get().n > 0;
  if (!hasBrands) {
    const ins = db.prepare(`INSERT INTO brands (code, slug, name, role_line, description, fact_status, status, accent, sort_order, instagram_url, facebook_url, logo, logo_bg, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`);
    SEED_BRANDS.forEach((b, i) => ins.run(b.code, b.slug, b.name, b.role_line || '', b.description || '',
      b.fact_status || 'tbc', b.status || 'coming_soon', b.accent, i + 1, b.instagram_url || '', b.facebook_url || '', b.logo || '', b.logo_bg || '#000000', now));
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
