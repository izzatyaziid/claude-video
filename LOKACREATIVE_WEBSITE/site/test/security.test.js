'use strict';
const { test, describe, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { once } = require('node:events');
const { openDb } = require('../src/db');
const { createApp } = require('../src/server');
const { hashPassword } = require('../src/security');

const OWNER = { email: 'owner@test.my', password: 'Owner-pass-123!' };
const EDITOR = { email: 'editor@test.my', password: 'Editor-pass-123!' };

async function boot(config = {}) {
  const db = openDb(':memory:');
  const ins = db.prepare('INSERT INTO admins (email, name, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)');
  ins.run(OWNER.email, 'Owner', hashPassword(OWNER.password), 'owner', Date.now());
  ins.run(EDITOR.email, 'Editor', hashPassword(EDITOR.password), 'editor', Date.now());
  const app = createApp({ db, config: { loginLimit: 1000, contactLimit: 1000, ...config } });
  const server = app.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const base = `http://127.0.0.1:${server.address().port}`;
  return { db, base, close: () => new Promise((r) => server.close(r)) };
}

function client(base) {
  const c = { cookie: '', csrf: '' };
  c.req = async (path, { method = 'GET', body, headers = {}, raw } = {}) => {
    const h = { Origin: base, ...headers };
    if (c.cookie) h.Cookie = c.cookie;
    if (body !== undefined && !raw) h['Content-Type'] = 'application/json';
    if (method !== 'GET' && c.csrf && !('X-CSRF-Token' in headers)) h['X-CSRF-Token'] = c.csrf;
    const res = await fetch(base + path, { method, headers: h, body: raw ?? (body !== undefined ? JSON.stringify(body) : undefined), redirect: 'manual' });
    const set = res.headers.getSetCookie();
    for (const s of set) { const kv = s.split(';')[0]; c.cookie = kv.endsWith('=') ? '' : kv; }
    const text = await res.text();
    let json = null; try { json = JSON.parse(text); } catch { /* html */ }
    return { status: res.status, headers: res.headers, text, json, setCookie: set };
  };
  c.login = async (who) => {
    const r = await c.req('/admin/api/login', { method: 'POST', body: who });
    if (r.json?.csrf) c.csrf = r.json.csrf;
    return r;
  };
  return c;
}

describe('security headers', () => {
  let s; before(async () => { s = await boot(); }); after(() => s.close());
  test('public page sends hardened headers and no version banner', async () => {
    const r = await client(s.base).req('/');
    assert.equal(r.status, 200);
    const csp = r.headers.get('content-security-policy');
    assert.match(csp, /default-src 'self'/);
    assert.match(csp, /script-src 'self'/);
    assert.match(csp, /frame-ancestors 'none'/);
    assert.match(csp, /object-src 'none'/);
    assert.doesNotMatch(csp, /unsafe-inline|unsafe-eval/);
    assert.equal(r.headers.get('x-content-type-options'), 'nosniff');
    assert.equal(r.headers.get('referrer-policy'), 'strict-origin-when-cross-origin');
    assert.ok(r.headers.get('permissions-policy'));
    assert.equal(r.headers.get('x-powered-by'), null);
    assert.match(r.text, /noindex/, 'draft mode must block indexing');
  });
  test('admin API responses are not cacheable', async () => {
    const r = await client(s.base).req('/admin/api/me');
    assert.equal(r.headers.get('cache-control'), 'no-store');
  });
  test('HSTS only in production config', async () => {
    const p = await boot({ isProd: true, siteOrigin: 'https://example.test' });
    const r = await fetch(p.base + '/');
    assert.match(r.headers.get('strict-transport-security') || '', /max-age=63072000/);
    await p.close();
  });
});

describe('authentication', () => {
  let s; before(async () => { s = await boot(); }); after(() => s.close());

  test('protected endpoints need a session', async () => {
    const c = client(s.base);
    for (const p of ['/admin/api/me', '/admin/api/stats', '/admin/api/inquiries', '/admin/api/brands']) {
      assert.equal((await c.req(p)).status, 401, p);
    }
  });

  test('wrong password and unknown email give the same generic error', async () => {
    const a = await client(s.base).login({ email: OWNER.email, password: 'nope-nope-nope' });
    const b = await client(s.base).login({ email: 'ghost@test.my', password: 'nope-nope-nope' });
    assert.equal(a.status, 401); assert.equal(b.status, 401);
    assert.equal(a.json.error, b.json.error);
  });

  test('SQL injection in login is inert', async () => {
    const r = await client(s.base).login({ email: "' OR 1=1 --", password: "' OR '1'='1" });
    assert.equal(r.status, 401);
  });

  test('session cookie is HttpOnly + SameSite=Strict, and rotates per login', async () => {
    const c1 = client(s.base); const r1 = await c1.login(OWNER);
    assert.equal(r1.status, 200);
    const cookie = r1.setCookie.join(';');
    assert.match(cookie, /HttpOnly/); assert.match(cookie, /SameSite=Strict/);
    const first = c1.cookie;
    await c1.login(OWNER);
    assert.notEqual(c1.cookie, first, 'new session id after login');
    const stale = client(s.base); stale.cookie = first;
    assert.equal((await stale.req('/admin/api/me')).status, 401, 'old session invalidated');
  });

  test('logout destroys the session server-side', async () => {
    const c = client(s.base); await c.login(OWNER);
    const saved = c.cookie;
    assert.equal((await c.req('/admin/api/logout', { method: 'POST', body: {} })).status, 200);
    const replay = client(s.base); replay.cookie = saved;
    assert.equal((await replay.req('/admin/api/me')).status, 401);
  });

  test('account locks after 5 failures, even with the right password', async () => {
    const db = s.db;
    db.prepare("INSERT INTO admins (email, name, password_hash, role, created_at) VALUES ('lock@test.my', 'L', ?, 'editor', ?)").run(hashPassword('Lock-pass-1234!'), Date.now());
    const c = client(s.base);
    for (let i = 0; i < 5; i++) await c.login({ email: 'lock@test.my', password: 'wrong-password-1' });
    const r = await c.login({ email: 'lock@test.my', password: 'Lock-pass-1234!' });
    assert.equal(r.status, 401);
    const row = db.prepare("SELECT locked_until FROM admins WHERE email = 'lock@test.my'").get();
    assert.ok(row.locked_until > Date.now());
  });

  test('passwords are stored as scrypt hashes', () => {
    const row = s.db.prepare('SELECT password_hash FROM admins WHERE email = ?').get(OWNER.email);
    assert.match(row.password_hash, /^scrypt\$/);
    assert.ok(!row.password_hash.includes(OWNER.password));
  });

  test('IP-based login rate limit returns 429', async () => {
    const p = await boot({ loginLimit: 3 });
    const c = client(p.base);
    const codes = [];
    for (let i = 0; i < 5; i++) codes.push((await c.login({ email: 'x@test.my', password: 'y' })).status);
    assert.deepEqual(codes.slice(-2), [429, 429]);
    await p.close();
  });
});

describe('CSRF, origin and content type', () => {
  let s, c; before(async () => { s = await boot(); c = client(s.base); await c.login(OWNER); }); after(() => s.close());
  const brandBody = { name: 'LokaFoodie', role_line: '', description: '', fact_status: 'tbc', status: 'coming_soon', accent: '#C2410C', sort_order: 2, website_url: '', instagram_url: '', facebook_url: '' };

  test('mutation without CSRF token is rejected', async () => {
    const r = await c.req('/admin/api/brands/2', { method: 'PUT', body: brandBody, headers: { 'X-CSRF-Token': '' } });
    assert.equal(r.status, 403);
  });
  test('mutation with a wrong CSRF token is rejected', async () => {
    const r = await c.req('/admin/api/brands/2', { method: 'PUT', body: brandBody, headers: { 'X-CSRF-Token': 'forged' } });
    assert.equal(r.status, 403);
  });
  test('cross-site Origin is rejected even with a valid token', async () => {
    const r = await c.req('/admin/api/brands/2', { method: 'PUT', body: brandBody, headers: { Origin: 'https://evil.example' } });
    assert.equal(r.status, 403);
  });
  test('form-encoded body is rejected on the API (415)', async () => {
    const r = await c.req('/admin/api/brands/2', { method: 'PUT', raw: 'name=x', headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
    assert.equal(r.status, 415);
  });
  test('valid request succeeds', async () => {
    const r = await c.req('/admin/api/brands/2', { method: 'PUT', body: brandBody });
    assert.equal(r.status, 200);
  });
});

describe('authorization (roles)', () => {
  let s, ed; before(async () => { s = await boot(); ed = client(s.base); await ed.login(EDITOR); }); after(() => s.close());
  test('editor cannot manage admins, read audit or delete inquiries', async () => {
    assert.equal((await ed.req('/admin/api/admins')).status, 403);
    assert.equal((await ed.req('/admin/api/audit')).status, 403);
    assert.equal((await ed.req('/admin/api/admins', { method: 'POST', body: { email: 'z@test.my', name: 'z', role: 'owner', password: 'Zzzzzzzz-123!' } })).status, 403);
    assert.equal((await ed.req('/admin/api/inquiries/1', { method: 'DELETE', body: {} })).status, 403);
  });
  test('editor can edit content', async () => {
    const r = await ed.req('/admin/api/content/about_short', { method: 'PUT', body: { value: 'Ujian', status: 'proposal' } });
    assert.equal(r.status, 200);
  });
  test('owner cannot demote or deactivate themselves', async () => {
    const o = client(s.base); const me = await o.login(OWNER);
    const r = await o.req(`/admin/api/admins/${me.json.user.id}`, { method: 'PATCH', body: { active: false } });
    assert.equal(r.status, 400);
  });
});

describe('input validation and output encoding', () => {
  let s, c; before(async () => { s = await boot(); c = client(s.base); await c.login(OWNER); }); after(() => s.close());

  test('stored XSS payload is escaped on the public site', async () => {
    const payload = '<script>alert(1)</script><img src=x onerror=alert(2)>';
    const r = await c.req('/admin/api/brands/2', { method: 'PUT', body: { name: 'LokaFoodie', role_line: payload, description: payload, fact_status: 'confirmed', status: 'active', accent: '#C2410C', sort_order: 2, website_url: '', instagram_url: '', facebook_url: '' } });
    assert.equal(r.status, 200);
    const page = await client(s.base).req('/brands/lokafoodie');
    assert.ok(!page.text.includes('<script>alert(1)'));
    assert.ok(!page.text.includes('<img src=x'));
    assert.ok(page.text.includes('&lt;script&gt;alert(1)&lt;/script&gt;'));
  });

  test('javascript: and http: links are rejected', async () => {
    for (const url of ['javascript:alert(1)', 'http://insecure.example', 'data:text/html,hi', 'https://user:pw@x.example']) {
      const r = await c.req('/admin/api/brands/3', { method: 'PUT', body: { name: 'LokaDaily', role_line: '', description: '', fact_status: 'tbc', status: 'coming_soon', accent: '#0B7285', sort_order: 3, website_url: url, instagram_url: '', facebook_url: '' } });
      assert.equal(r.status, 400, url);
    }
  });

  test('accent colour cannot inject CSS', async () => {
    const r = await c.req('/admin/api/brands/3', { method: 'PUT', body: { name: 'LokaDaily', role_line: '', description: '', fact_status: 'tbc', status: 'coming_soon', accent: 'red;}body{display:none', sort_order: 3, website_url: '', instagram_url: '', facebook_url: '' } });
    assert.equal(r.status, 400);
  });

  test('content length limits are enforced', async () => {
    const r = await c.req('/admin/api/content/hero_headline', { method: 'PUT', body: { value: 'x'.repeat(500), status: 'proposal' } });
    assert.equal(r.status, 400);
  });

  test('cannot mark a field confirmed while empty', async () => {
    const r = await c.req('/admin/api/content/vision', { method: 'PUT', body: { value: '', status: 'confirmed' } });
    assert.equal(r.status, 400);
  });

  test('oversized JSON body is rejected', async () => {
    const r = await c.req('/admin/api/content/about_long', { method: 'PUT', body: { value: 'x'.repeat(60000), status: 'proposal' } });
    assert.equal(r.status, 413);
  });

  test('invalid post slug is rejected and published post renders escaped', async () => {
    assert.equal((await c.req('/admin/api/posts', { method: 'POST', body: { title: 'T', slug: '../etc/passwd', excerpt: '', body: '', status: 'draft' } })).status, 400);
    const ok = await c.req('/admin/api/posts', { method: 'POST', body: { title: 'Ujian <b>bold</b>', slug: 'ujian', excerpt: 'x', body: 'Perenggan satu.\n\n<iframe src=x>', status: 'published' } });
    assert.equal(ok.status, 201);
    const page = await client(s.base).req('/news/ujian');
    assert.equal(page.status, 200);
    assert.ok(!page.text.includes('<iframe src=x>'));
    assert.ok(!page.text.includes('<b>bold</b>'));
  });

  test('draft posts are not public', async () => {
    await c.req('/admin/api/posts', { method: 'POST', body: { title: 'Rahsia', slug: 'rahsia', excerpt: '', body: '', status: 'draft' } });
    assert.equal((await client(s.base).req('/news/rahsia')).status, 404);
  });
});

describe('public contact form', () => {
  let s; before(async () => { s = await boot(); }); after(() => s.close());
  const form = (o) => new URLSearchParams({ name: 'Ali', email: 'ali@contoh.my', company: '', kind: 'kerjasama', message: 'Saya ingin berbincang kerjasama.', consent: '1', website: '', ...o }).toString();
  const post = (body, headers = {}) => client(s.base).req('/contact', { method: 'POST', raw: body, headers: { 'Content-Type': 'application/x-www-form-urlencoded', ...headers } });

  test('valid submission is stored with a hashed IP, not the raw IP', async () => {
    const r = await post(form());
    assert.equal(r.status, 303);
    const row = s.db.prepare('SELECT * FROM inquiries ORDER BY id DESC LIMIT 1').get();
    assert.equal(row.email, 'ali@contoh.my');
    assert.match(row.ip_hash, /^[0-9a-f]{32}$/);
    assert.ok(!row.ip_hash.includes('127.0.0.1'));
  });
  test('honeypot submissions are silently dropped', async () => {
    const before = s.db.prepare('SELECT COUNT(*) n FROM inquiries').get().n;
    const r = await post(form({ website: 'http://spam.example' }));
    assert.equal(r.status, 303);
    assert.equal(s.db.prepare('SELECT COUNT(*) n FROM inquiries').get().n, before);
  });
  test('missing consent, bad email and bad kind are rejected', async () => {
    assert.equal((await post(form({ consent: '' }))).status, 400);
    assert.equal((await post(form({ email: 'bukan-emel' }))).status, 400);
    assert.equal((await post(form({ kind: 'admin' }))).status, 400);
  });
  test('validation error page escapes echoed input', async () => {
    const r = await post(form({ email: 'x', name: '"><script>alert(1)</script>' }));
    assert.equal(r.status, 400);
    assert.ok(!r.text.includes('<script>alert(1)'));
  });
  test('cross-site form post is rejected', async () => {
    assert.equal((await post(form(), { Origin: 'https://evil.example' })).status, 403);
  });
  test('contact rate limit returns 429', async () => {
    const p = await boot({ contactLimit: 2 });
    const c = client(p.base);
    const codes = [];
    for (let i = 0; i < 3; i++) codes.push((await c.req('/contact', { method: 'POST', raw: form(), headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })).status);
    assert.equal(codes[2], 429);
    await p.close();
  });
});

describe('public pages render', () => {
  let s; before(async () => { s = await boot(); }); after(() => s.close());
  for (const p of ['/', '/brands', '/brands/lokadigital', '/about', '/news', '/contact', '/privacy']) {
    test(`GET ${p} -> 200`, async () => assert.equal((await client(s.base).req(p)).status, 200));
  }
  test('unknown page and hidden brand -> 404', async () => {
    assert.equal((await client(s.base).req('/tiada')).status, 404);
    s.db.prepare("UPDATE brands SET status = 'hidden' WHERE slug = 'lokatalent'").run();
    assert.equal((await client(s.base).req('/brands/lokatalent')).status, 404);
  });
  test('no invented facts: TBC brands show TBC, not a made-up description', async () => {
    const r = await client(s.base).req('/brands/lokadaily');
    assert.match(r.text, /TBC/);
  });
});
