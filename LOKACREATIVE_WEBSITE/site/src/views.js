'use strict';

// Every dynamic value goes through esc(). There is no raw-HTML path for database content.
const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '`': '&#96;' };
const esc = (v) => String(v ?? '').replace(/[&<>"'`]/g, (c) => ESC[c]);
const html = (strings, ...vals) => strings.reduce((out, s, i) => out + s + (i < vals.length ? vals[i] : ''), '');
const paragraphs = (text) => String(text || '').split(/\n{2,}/).map((p) => p.trim()).filter(Boolean)
  .map((p) => `<p>${esc(p).replace(/\n/g, '<br>')}</p>`).join('');
const fmtDate = (ms) => new Date(ms).toLocaleDateString('ms-MY', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Asia/Kuala_Lumpur' });

const STATUS_LABEL = { active: 'Aktif', coming_soon: 'Akan datang', hidden: 'Tersembunyi' };

// Renders a content field. Draft mode shows the owner what is still missing; live mode hides it.
function field(c, key, { tag = 'span', cls = '', fallback = '' } = {}, draft = true) {
  const row = c[key];
  const value = row && row.status !== 'tbc' ? row.value : '';
  if (!value) {
    if (!draft) return fallback ? `<${tag} class="${cls}">${esc(fallback)}</${tag}>` : '';
    return `<${tag} class="${cls} tbc-field"><span class="tag tag-tbc">TBC</span> ${esc(row ? row.label : key)}</${tag}>`;
  }
  const mark = draft && row.status === 'proposal' ? ' <span class="tag tag-proposal">CADANGAN</span>' : '';
  return `<${tag} class="${cls}">${esc(value)}${mark}</${tag}>`;
}

function layout({ title, description, path, body, c, draft, brands }) {
  const company = c.company_name?.value || 'LokaCreative Ventures';
  const nav = [['/', 'Utama'], ['/about', 'Tentang'], ['/brands', 'Ekosistem'], ['/news', 'Berita'], ['/contact', 'Hubungi']];
  const year = new Date().getFullYear();
  return html`<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(title ? `${title} · ${company}` : company)}</title>
<meta name="description" content="${esc(description || c.hero_sub?.value || '')}">
${draft ? '<meta name="robots" content="noindex, nofollow">' : ''}
<meta property="og:title" content="${esc(title || company)}">
<meta property="og:description" content="${esc(description || c.hero_sub?.value || '')}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Schibsted+Grotesk:wght@500;700;800&display=swap">
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/brand-colors.css">
</head>
<body>
<a class="skip" href="#main">Langkau ke kandungan</a>
${draft ? '<div class="draft-bar"><div class="wrap"><strong>DRAF</strong> · Bukan untuk umum. Teks bertanda <span class="tag tag-tbc">TBC</span> belum disahkan, <span class="tag tag-proposal">CADANGAN</span> perlu kelulusan.</div></div>' : ''}
<header class="site-header">
  <div class="wrap header-row">
    <a class="wordmark" href="/" aria-label="${esc(company)}, laman utama"><span class="wm-loka">Loka</span><span class="wm-rest">Creative Ventures</span></a>
    <nav aria-label="Utama">
      <ul class="nav">
        ${nav.map(([href, label]) => `<li><a href="${href}"${path === href || (href !== '/' && path.startsWith(href)) ? ' aria-current="page"' : ''}>${label}</a></li>`).join('')}
      </ul>
    </nav>
    <a class="btn btn-small" href="/contact?kind=kerjasama">Bincang kerjasama</a>
  </div>
</header>
<main id="main">
${body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <a class="wordmark" href="/"><span class="wm-loka">Loka</span><span class="wm-rest">Creative Ventures</span></a>
      <p class="muted">Syarikat induk ekosistem jenama Loka.</p>
    </div>
    <div>
      <h2 class="eyebrow">Ekosistem</h2>
      <ul class="plain">${brands.map((b) => `<li><a href="/brands/${esc(b.slug)}">${esc(b.name)}</a></li>`).join('')}</ul>
    </div>
    <div>
      <h2 class="eyebrow">Syarikat</h2>
      <ul class="plain"><li><a href="/about">Tentang</a></li><li><a href="/news">Berita</a></li><li><a href="/contact">Hubungi</a></li><li><a href="/privacy">Dasar privasi</a></li></ul>
    </div>
  </div>
  <div class="wrap footer-base"><span>© ${year} ${esc(company)}</span>${field(c, 'legal_name', { cls: 'muted' }, draft)}</div>
</footer>
</body>
</html>`;
}

// Orbit diagram: the group at the centre, each brand on a ring. Geometry is computed, not hand-drawn.
function orbit(brands) {
  const W = 560, cx = 280, cy = 280, R = 196;
  const n = Math.max(brands.length, 1);
  const nodes = brands.map((b, i) => {
    const a = (-90 + (360 / n) * i) * (Math.PI / 180);
    const x = +(cx + R * Math.cos(a)).toFixed(1);
    const y = +(cy + R * Math.sin(a)).toFixed(1);
    const below = Math.sin(a) > -0.2;
    const ly = below ? y + 52 : y - 44;
    return html`<g class="node b-${esc(b.slug)} ${b.status === 'active' ? 'is-active' : 'is-soon'}">
      <line class="spoke" x1="${cx}" y1="${cy}" x2="${x}" y2="${y}"></line>
      <circle class="dot" cx="${x}" cy="${y}" r="26"></circle>
      <text class="node-code" x="${x}" y="${y + 4}" text-anchor="middle">${esc(b.code.replace('LCV-', ''))}</text>
      <text class="node-name" x="${x}" y="${ly}" text-anchor="middle">${esc(b.name)}</text>
    </g>`;
  }).join('');
  return html`<svg class="orbit" viewBox="0 0 ${W} ${W}" role="img" aria-label="Peta ekosistem: LokaCreative Ventures di tengah, ${brands.length} jenama di sekelilingnya">
    <circle class="ring" cx="${cx}" cy="${cy}" r="${R}"></circle>
    <circle class="ring ring-inner" cx="${cx}" cy="${cy}" r="${R - 70}"></circle>
    ${nodes}
    <circle class="core" cx="${cx}" cy="${cy}" r="62"></circle>
    <text class="core-text" x="${cx}" y="${cy - 4}" text-anchor="middle">LCV</text>
    <text class="core-sub" x="${cx}" y="${cy + 18}" text-anchor="middle">INDUK</text>
  </svg>`;
}

function brandRow(b, draft) {
  const role = b.fact_status === 'tbc' || !b.role_line
    ? (draft ? '<span class="tag tag-tbc">TBC</span> Fungsi jenama' : 'Akan diumumkan')
    : esc(b.role_line) + (draft && b.fact_status === 'proposal' ? ' <span class="tag tag-proposal">CADANGAN</span>' : '');
  const links = [['website_url', 'Website'], ['instagram_url', 'Instagram'], ['facebook_url', 'Facebook']]
    .filter(([k]) => b[k]).map(([k, l]) => `<a href="${esc(b[k])}" rel="noopener noreferrer" target="_blank">${l}</a>`).join(' · ');
  return html`<li class="register-row b-${esc(b.slug)}">
    <span class="reg-code">${esc(b.code)}</span>
    <span class="reg-swatch" aria-hidden="true"></span>
    <a class="reg-name" href="/brands/${esc(b.slug)}">${esc(b.name)}</a>
    <span class="reg-role">${role}</span>
    <span class="reg-status"><span class="pill pill-${esc(b.status)}">${STATUS_LABEL[b.status] || ''}</span></span>
    <span class="reg-links">${links || '<span class="muted">Saluran: TBC</span>'}</span>
  </li>`;
}

function home({ c, draft, brands, posts }) {
  const active = brands.filter((b) => b.status === 'active').length;
  return html`
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">${esc(c.company_name?.value || 'LokaCreative Ventures')} · Kumpulan jenama</p>
      <h1>${field(c, 'hero_headline', {}, draft)}</h1>
      ${field(c, 'hero_sub', { tag: 'p', cls: 'lede' }, draft)}
      <div class="actions">
        <a class="btn" href="/contact?kind=kerjasama">Bincang kerjasama</a>
        <a class="btn btn-ghost" href="/brands">Lihat ekosistem</a>
      </div>
      <dl class="facts">
        <div><dt>Jenama</dt><dd>${brands.length}</dd></div>
        <div><dt>Aktif</dt><dd>${active}</dd></div>
        <div><dt>Ditubuhkan</dt><dd>${c.founded_year?.status !== 'tbc' && c.founded_year?.value ? esc(c.founded_year.value) : (draft ? '<span class="tag tag-tbc">TBC</span>' : '—')}</dd></div>
      </dl>
    </div>
    <div class="hero-visual">${orbit(brands)}</div>
  </div>
</section>

<section class="band">
  <div class="wrap split">
    <div><p class="eyebrow">Siapa kami</p><h2>Syarikat induk, bukan agensi.</h2></div>
    <div class="prose">
      ${field(c, 'about_short', { tag: 'p' }, draft)}
      <p class="muted">LokaCreative Ventures membina dan menaungi jenama dalam ekosistem Loka. Servis digital marketing ialah peranan <a href="/brands/lokadigital">LokaDigital</a>.</p>
    </div>
  </div>
</section>

<section class="band band-alt">
  <div class="wrap">
    <div class="section-head">
      <div><p class="eyebrow">Loka Index</p><h2>Ekosistem jenama</h2></div>
      <a class="link-arrow" href="/brands">Semua jenama</a>
    </div>
    <ol class="register">${brands.map((b) => brandRow(b, draft)).join('')}</ol>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Cara bekerjasama</p><h2>Tiga pintu masuk${draft ? ' <span class="tag tag-proposal">CADANGAN</span>' : ''}</h2></div></div>
    <div class="doors">
      <a class="door" href="/contact?kind=kerjasama"><span class="door-k">A</span><h3>Rakan kongsi korporat</h3><p>Kolaborasi, pelaburan atau projek bersama di peringkat kumpulan.</p><span class="link-arrow">Hubungi kumpulan</span></a>
      <a class="door" href="/brands"><span class="door-k">B</span><h3>Jenama &amp; klien</h3><p>Cari jenama Loka yang sesuai dengan keperluan anda.</p><span class="link-arrow">Terokai jenama</span></a>
      <a class="door" href="/contact?kind=kerjaya"><span class="door-k">C</span><h3>Talent &amp; kerjaya</h3><p>Sertai pasukan yang membina jenama Loka.</p><span class="link-arrow">Hantar minat</span></a>
    </div>
  </div>
</section>

<section class="band band-alt">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Terkini</p><h2>Berita kumpulan</h2></div><a class="link-arrow" href="/news">Semua berita</a></div>
    ${posts.length ? `<ul class="posts">${posts.map(postCard).join('')}</ul>` : '<p class="empty">Belum ada berita diterbitkan. Berita yang diterbitkan dari dashboard akan muncul di sini.</p>'}
  </div>
</section>

<section class="cta">
  <div class="wrap cta-row">
    <div>${field(c, 'partner_cta_title', { tag: 'h2' }, draft)}${field(c, 'partner_cta_body', { tag: 'p', cls: 'lede' }, draft)}</div>
    <a class="btn btn-invert" href="/contact?kind=kerjasama">Mulakan perbualan</a>
  </div>
</section>`;
}

function postCard(p) {
  return html`<li class="post-card"><time datetime="${new Date(p.published_at).toISOString()}">${esc(fmtDate(p.published_at))}</time>
    <h3><a href="/news/${esc(p.slug)}">${esc(p.title)}</a></h3><p>${esc(p.excerpt)}</p></li>`;
}

function brandsPage({ brands, draft }) {
  return html`<section class="page-head"><div class="wrap"><p class="eyebrow">Loka Index</p><h1>Ekosistem jenama</h1>
    <p class="lede">Setiap jenama dalam kumpulan, dengan kod register, fungsi dan saluran rasmi.</p></div></section>
    <section class="band"><div class="wrap"><ol class="register register-full">${brands.map((b) => brandRow(b, draft)).join('')}</ol></div></section>`;
}

function brandPage({ b, draft }) {
  const desc = b.fact_status === 'tbc' || !b.description
    ? (draft ? '<p class="tbc-field"><span class="tag tag-tbc">TBC</span> Penerangan jenama belum disahkan.</p>' : '<p>Maklumat lanjut akan diumumkan.</p>')
    : paragraphs(b.description);
  const links = [['website_url', 'Website rasmi'], ['instagram_url', 'Instagram'], ['facebook_url', 'Facebook']].filter(([k]) => b[k]);
  return html`<section class="page-head b-${esc(b.slug)} brand-head"><div class="wrap">
    <p class="eyebrow"><span class="reg-code">${esc(b.code)}</span> · ${STATUS_LABEL[b.status] || ''}</p>
    <h1><span class="reg-swatch big" aria-hidden="true"></span>${esc(b.name)}</h1>
    <p class="lede">${b.role_line && b.fact_status !== 'tbc' ? esc(b.role_line) : (draft ? '<span class="tag tag-tbc">TBC</span> Fungsi jenama' : '')}</p>
  </div></section>
  <section class="band"><div class="wrap split"><div class="prose">${desc}</div>
    <aside class="side-card"><h2 class="eyebrow">Saluran rasmi</h2>
      ${links.length ? `<ul class="plain">${links.map(([k, l]) => `<li><a href="${esc(b[k])}" rel="noopener noreferrer" target="_blank">${l}</a></li>`).join('')}</ul>` : `<p class="muted">${draft ? 'TBC' : 'Akan diumumkan'}</p>`}
      <p class="muted small">Sebahagian daripada <a href="/">LokaCreative Ventures</a>.</p></aside></div></section>`;
}

function aboutPage({ c, draft }) {
  const block = (key, label) => html`<div class="about-block"><h2 class="eyebrow">${label}</h2>${field(c, key, { tag: 'p', cls: 'about-val' }, draft)}</div>`;
  const story = c.about_long?.status !== 'tbc' && c.about_long?.value ? paragraphs(c.about_long.value)
    : (draft ? '<p class="tbc-field"><span class="tag tag-tbc">TBC</span> Cerita syarikat</p>' : '');
  return html`<section class="page-head"><div class="wrap"><p class="eyebrow">Tentang</p><h1>${esc(c.company_name?.value || 'LokaCreative Ventures')}</h1>
    ${field(c, 'about_short', { tag: 'p', cls: 'lede' }, draft)}</div></section>
    <section class="band"><div class="wrap split"><div class="prose">${story}</div>
      <div class="about-grid">${block('vision', 'Visi')}${block('mission', 'Misi')}${block('values', 'Nilai teras')}${block('founded_year', 'Ditubuhkan')}</div></div></section>`;
}

const KINDS = [['kerjasama', 'Kerjasama / partnership'], ['jenama', 'Pertanyaan tentang jenama'], ['media', 'Media'], ['kerjaya', 'Kerjaya'], ['lain', 'Lain-lain']];

function contactPage({ c, draft, sent, error, values = {}, kind }) {
  const v = (k) => esc(values[k] || '');
  const selected = values.kind || kind || 'kerjasama';
  return html`<section class="page-head"><div class="wrap"><p class="eyebrow">Hubungi</p><h1>Mari berbincang.</h1>
    <p class="lede">Untuk kerjasama di peringkat kumpulan, media atau kerjaya. Pertanyaan servis marketing akan disalurkan kepada LokaDigital.</p></div></section>
  <section class="band"><div class="wrap split">
    <div>
      ${sent ? '<div class="notice notice-ok" role="status">Terima kasih. Pertanyaan anda telah diterima.</div>' : ''}
      ${error ? `<div class="notice notice-err" role="alert">${esc(error)}</div>` : ''}
      <form class="form" method="post" action="/contact" novalidate>
        <div class="row2">
          <label for="f-name">Nama<input id="f-name" name="name" required maxlength="80" autocomplete="name" value="${v('name')}"></label>
          <label for="f-email">Emel<input id="f-email" name="email" type="email" required maxlength="254" autocomplete="email" value="${v('email')}"></label>
        </div>
        <div class="row2">
          <label for="f-company">Syarikat <span class="muted">(pilihan)</span><input id="f-company" name="company" maxlength="120" autocomplete="organization" value="${v('company')}"></label>
          <label for="f-kind">Jenis pertanyaan<select id="f-kind" name="kind">${KINDS.map(([k, l]) => `<option value="${k}"${k === selected ? ' selected' : ''}>${l}</option>`).join('')}</select></label>
        </div>
        <label for="f-message">Mesej<textarea id="f-message" name="message" required minlength="10" maxlength="3000" rows="6">${v('message')}</textarea></label>
        <label class="hp" for="f-website" aria-hidden="true">Website<input id="f-website" name="website" tabindex="-1" autocomplete="off"></label>
        <label class="check" for="f-consent"><input id="f-consent" name="consent" type="checkbox" value="1" required>
          <span>Saya bersetuju data ini digunakan untuk membalas pertanyaan saya, seperti dalam <a href="/privacy">dasar privasi</a>.</span></label>
        <button class="btn" type="submit">Hantar pertanyaan</button>
      </form>
    </div>
    <aside class="side-card"><h2 class="eyebrow">Maklumat rasmi</h2>
      <dl class="contact-dl"><dt>Emel</dt><dd>${field(c, 'contact_email', {}, draft)}</dd><dt>Telefon</dt><dd>${field(c, 'contact_phone', {}, draft)}</dd><dt>Alamat</dt><dd>${field(c, 'contact_address', {}, draft)}</dd></dl>
    </aside>
  </div></section>`;
}

function newsPage({ posts }) {
  return html`<section class="page-head"><div class="wrap"><p class="eyebrow">Berita</p><h1>Berita kumpulan</h1></div></section>
    <section class="band"><div class="wrap">${posts.length ? `<ul class="posts">${posts.map(postCard).join('')}</ul>` : '<p class="empty">Belum ada berita diterbitkan.</p>'}</div></section>`;
}

function postPage({ p }) {
  return html`<section class="page-head"><div class="wrap narrow"><p class="eyebrow"><a href="/news">Berita</a> · <time datetime="${new Date(p.published_at).toISOString()}">${esc(fmtDate(p.published_at))}</time></p>
    <h1>${esc(p.title)}</h1>${p.excerpt ? `<p class="lede">${esc(p.excerpt)}</p>` : ''}</div></section>
    <section class="band"><div class="wrap narrow prose">${paragraphs(p.body)}</div></section>`;
}

function privacyPage({ c, draft }) {
  return html`<section class="page-head"><div class="wrap narrow"><p class="eyebrow">Dasar privasi</p><h1>Dasar privasi</h1>
    ${draft ? '<p class="notice notice-warn">Draf templat. Perlu disemak oleh penasihat undang-undang sebelum diterbitkan (PDPA 2010).</p>' : ''}</div></section>
  <section class="band"><div class="wrap narrow prose">
    <h2>Data yang kami kumpul</h2><p>Apabila anda menghantar borang hubungi, kami menyimpan nama, emel, nama syarikat (jika diberi), jenis pertanyaan dan mesej anda. Alamat IP disimpan dalam bentuk hash sehala untuk mencegah spam. IP asal tidak disimpan.</p>
    <h2>Tujuan</h2><p>Data digunakan hanya untuk membalas pertanyaan anda dan menyalurkannya kepada jenama yang berkaitan dalam kumpulan.</p>
    <h2>Cookie</h2><p>Laman awam tidak menggunakan cookie penjejakan. Cookie sesi hanya digunakan dalam panel admin dalaman.</p>
    <h2>Hak anda</h2><p>Anda boleh meminta akses, pembetulan atau pemadaman data anda dengan menghubungi kami di ${field(c, 'contact_email', {}, draft)}.</p>
  </div></section>`;
}

function notFound() {
  return html`<section class="page-head"><div class="wrap narrow"><p class="eyebrow">404</p><h1>Halaman tidak dijumpai.</h1><p class="lede"><a href="/">Kembali ke laman utama</a></p></div></section>`;
}

function brandColorsCss(brands) {
  // accent values are validated as #RRGGBB on write; re-checked here before emitting CSS.
  return brands.filter((b) => /^#[0-9A-Fa-f]{6}$/.test(b.accent) && /^[a-z0-9-]+$/.test(b.slug))
    .map((b) => `.b-${b.slug}{--b:${b.accent}}`).join('\n');
}

module.exports = { esc, layout, home, brandsPage, brandPage, aboutPage, contactPage, newsPage, postPage, privacyPage, notFound, brandColorsCss, KINDS };
