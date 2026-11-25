'use strict';
// Visual language follows the owner's Canva deck "Lokacreative Ventures" (see 01_BRAND_AND_BUSINESS/BRAND_SOURCES.md):
// black #171717 / #292929, lime #D6FF3F, white; heavy uppercase headings; lime title bands with a "↗" label;
// lime-outlined pills. No invented marks: LokaCreative has no logo file yet, so its wordmark is set in type as in the deck.

// Every dynamic value goes through esc(). There is no raw-HTML path for database content.
const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '`': '&#96;' };
const esc = (v) => String(v ?? '').replace(/[&<>"'`]/g, (c) => ESC[c]);
const html = (strings, ...vals) => strings.reduce((out, s, i) => out + s + (i < vals.length ? vals[i] : ''), '');
const paragraphs = (text) => String(text || '').split(/\n{2,}/).map((p) => p.trim()).filter(Boolean)
  .map((p) => `<p>${esc(p).replace(/\n/g, '<br>')}</p>`).join('');
const fmtDate = (ms) => new Date(ms).toLocaleDateString('ms-MY', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Asia/Kuala_Lumpur' });
const safeLogo = (p) => (/^\/assets\/brands\/[a-z0-9-]+\.(png|svg|webp)$/.test(p || '') ? p : '');

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

const wordmark = () => '<span class="wordmark-text">LOKACREATIVE VENTURES</span>';

// Deck-style section head: lime band, small "↗" label, heavy uppercase title, notch into the dark area below.
function bandHead(label, title, extra = '') {
  return html`<div class="band-head"><div class="wrap">
    <p class="band-label"><span aria-hidden="true">↗</span> ${esc(label)}</p>
    <div class="band-title-row"><h2 class="band-title">${title}</h2>${extra}</div>
  </div></div>`;
}

function layout({ title, description, path, body, c, draft, brands }) {
  const company = c.company_name?.value || 'LokaCreative Ventures';
  const nav = [['/', 'Utama'], ['/about', 'Tentang'], ['/brands', 'Jenama'], ['/news', 'Berita'], ['/contact', 'Hubungi']];
  const year = new Date().getFullYear();
  return html`<!doctype html>
<html lang="ms">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(title ? `${title} · ${company}` : company)}</title>
<meta name="description" content="${esc(description || c.hero_sub?.value || '')}">
${draft ? '<meta name="robots" content="noindex, nofollow">' : ''}
<meta name="theme-color" content="#171717">
<meta property="og:title" content="${esc(title || company)}">
<meta property="og:description" content="${esc(description || c.hero_sub?.value || '')}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=League+Spartan:wght@700;800;900&family=Open+Sans:wght@400;600;700&display=swap">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a class="skip" href="#main">Langkau ke kandungan</a>
${draft ? '<div class="draft-bar"><div class="wrap"><strong>DRAF</strong> · Bukan untuk umum. <span class="tag tag-tbc">TBC</span> belum disahkan · <span class="tag tag-proposal">CADANGAN</span> perlu kelulusan.</div></div>' : ''}
<header class="site-header">
  <div class="wrap header-row">
    <a class="home-link" href="/" aria-label="${esc(company)}, laman utama">${wordmark()}</a>
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
      <a class="home-link" href="/">${wordmark()}</a>
      <p class="muted">Kumpulan jenama Loka.</p>
    </div>
    <div>
      <h2 class="foot-h">Jenama</h2>
      <ul class="plain">${brands.map((b) => `<li><a href="/brands/${esc(b.slug)}">${esc(b.name)}</a></li>`).join('')}</ul>
    </div>
    <div>
      <h2 class="foot-h">Syarikat</h2>
      <ul class="plain"><li><a href="/about">Tentang</a></li><li><a href="/news">Berita</a></li><li><a href="/contact">Hubungi</a></li><li><a href="/privacy">Dasar privasi</a></li></ul>
    </div>
  </div>
  <div class="wrap footer-base"><span>© ${year} ${esc(company)}</span>${field(c, 'legal_name', { cls: 'muted' }, draft)}</div>
</footer>
</body>
</html>`;
}

function brandLinks(b) {
  return [['website_url', 'Website'], ['instagram_url', 'Instagram'], ['facebook_url', 'Facebook']]
    .filter(([k]) => b[k]).map(([k, l]) => `<a href="${esc(b[k])}" rel="noopener noreferrer" target="_blank">${l}</a>`).join('');
}

function brandMark(b, cls = '') {
  const logo = safeLogo(b.logo);
  return logo
    ? `<img class="brand-logo ${cls}" src="${esc(logo)}" alt="Logo ${esc(b.name)}" loading="lazy" decoding="async">`
    : `<span class="brand-name-mark ${cls}">${esc(b.name)}</span>`;
}

function brandCard(b, draft) {
  const role = b.fact_status === 'tbc' || !b.role_line
    ? (draft ? '<span class="tag tag-tbc">TBC</span> Fungsi jenama' : 'Akan diumumkan')
    : esc(b.role_line) + (draft && b.fact_status === 'proposal' ? ' <span class="tag tag-proposal">CADANGAN</span>' : '');
  const links = brandLinks(b);
  return html`<li class="brand-card${b.status === 'active' ? ' is-active' : ''}">
    <a class="brand-mark-wrap" href="/brands/${esc(b.slug)}" aria-label="${esc(b.name)}">${brandMark(b)}</a>
    <div class="brand-meta">
      <span class="pill${b.status === 'active' ? ' pill-on' : ''}">${STATUS_LABEL[b.status] || ''}</span>
      ${safeLogo(b.logo) ? `<h3 class="brand-title"><a href="/brands/${esc(b.slug)}">${esc(b.name)}</a></h3>` : ''}
      <p class="brand-role">${role}</p>
      <p class="brand-links">${links || `<span class="muted">${draft ? 'Saluran: TBC' : ''}</span>`}</p>
    </div>
  </li>`;
}

function home({ c, draft, brands, posts }) {
  const active = brands.filter((b) => b.status === 'active').length;
  const founded = c.founded_year?.status !== 'tbc' && c.founded_year?.value ? esc(c.founded_year.value) : (draft ? '<span class="tag tag-tbc">TBC</span>' : '—');
  return html`
<section class="hero">
  <div class="wrap">
    <p class="hero-label">${esc(c.company_name?.value || 'LokaCreative Ventures')}</p>
    <h1 class="hero-title">${field(c, 'hero_headline', {}, draft)}</h1>
    <div class="lime-bar" aria-hidden="true"></div>
    <div class="hero-foot">
      ${field(c, 'hero_sub', { tag: 'p', cls: 'lede' }, draft)}
      <div class="actions">
        <a class="btn" href="/contact?kind=kerjasama">Bincang kerjasama</a>
        <a class="btn btn-ghost" href="/brands">Lihat jenama</a>
      </div>
    </div>
    <dl class="facts">
      <div><dt>Jenama</dt><dd>${brands.length}</dd></div>
      <div><dt>Aktif</dt><dd>${active}</dd></div>
      <div><dt>Ditubuhkan</dt><dd>${founded}</dd></div>
    </dl>
  </div>
</section>

<section class="section">
  ${bandHead('Siapa kami', 'Overview')}
  <div class="wrap dark-body prose-wide">
    ${field(c, 'about_short', { tag: 'p', cls: 'big-copy' }, draft)}
    <p class="muted">LokaCreative Ventures menaungi jenama dalam ekosistem Loka.</p>
  </div>
</section>

<section class="section">
  ${bandHead('Ekosistem', 'Jenama kami', '<a class="band-link" href="/brands">Semua jenama</a>')}
  <div class="wrap dark-body">
    <ul class="brand-grid">${brands.map((b) => brandCard(b, draft)).join('')}</ul>
  </div>
</section>

<section class="section">
  ${bandHead('Bekerjasama', `Cara bekerjasama${draft ? ' <span class="tag tag-proposal">CADANGAN</span>' : ''}`)}
  <div class="wrap dark-body">
    <div class="doors">
      <a class="door" href="/contact?kind=kerjasama"><span class="pill pill-on">Rakan kongsi korporat</span><p>Kolaborasi atau projek bersama di peringkat kumpulan.</p></a>
      <a class="door" href="/brands"><span class="pill pill-on">Jenama &amp; klien</span><p>Cari jenama Loka yang sesuai dengan keperluan anda.</p></a>
      <a class="door" href="/contact?kind=kerjaya"><span class="pill pill-on">Talent &amp; kerjaya</span><p>Sertai pasukan yang membina jenama Loka.</p></a>
    </div>
  </div>
</section>

<section class="section">
  ${bandHead('Terkini', 'Berita', '<a class="band-link" href="/news">Semua berita</a>')}
  <div class="wrap dark-body">
    ${posts.length ? `<ul class="posts">${posts.map(postCard).join('')}</ul>` : '<p class="empty">Belum ada berita diterbitkan. Berita yang diterbitkan dari dashboard akan muncul di sini.</p>'}
  </div>
</section>

${contactBlock(c, draft)}`;
}

// Closing block modelled on the deck's last page: big line on the left, labelled contact details on the right.
function contactBlock(c, draft) {
  return html`<section class="closing">
  <div class="wrap closing-row">
    <div>${field(c, 'partner_cta_title', { tag: 'h2', cls: 'closing-title' }, draft)}${field(c, 'partner_cta_body', { tag: 'p', cls: 'lede' }, draft)}
      <a class="btn" href="/contact?kind=kerjasama">Mulakan perbualan</a></div>
    <dl class="contact-dl">
      <dt>Email</dt><dd>${field(c, 'contact_email', {}, draft)}</dd>
      <dt>Mobile</dt><dd>${field(c, 'contact_phone', {}, draft)}</dd>
      <dt>Lokasi</dt><dd>${field(c, 'contact_address', {}, draft)}</dd>
    </dl>
  </div>
</section>`;
}

function postCard(p) {
  return html`<li class="post-card"><time datetime="${new Date(p.published_at).toISOString()}">${esc(fmtDate(p.published_at))}</time>
    <h3><a href="/news/${esc(p.slug)}">${esc(p.title)}</a></h3><p>${esc(p.excerpt)}</p></li>`;
}

function pageHead(label, title, lede = '') {
  return html`<section class="page-head">${bandHead(label, title)}${lede ? `<div class="wrap dark-body"><p class="lede">${lede}</p></div>` : ''}</section>`;
}

function brandsPage({ brands, draft }) {
  return html`${pageHead('Ekosistem', 'Jenama kami', 'Setiap jenama dalam kumpulan LokaCreative Ventures, dengan fungsi dan saluran rasmi.')}
    <section class="section"><div class="wrap dark-body"><ul class="brand-grid">${brands.map((b) => brandCard(b, draft)).join('')}</ul></div></section>`;
}

function brandPage({ b, draft }) {
  const desc = b.fact_status === 'tbc' || !b.description
    ? (draft ? '<p class="tbc-field"><span class="tag tag-tbc">TBC</span> Penerangan jenama belum disahkan.</p>' : '<p>Maklumat lanjut akan diumumkan.</p>')
    : paragraphs(b.description);
  const links = brandLinks(b);
  return html`<section class="page-head">${bandHead(STATUS_LABEL[b.status] || 'Jenama', esc(b.name))}</section>
  <section class="section"><div class="wrap dark-body split">
    <div>
      <div class="brand-hero-mark">${brandMark(b, 'big')}</div>
      <p class="lede">${b.role_line && b.fact_status !== 'tbc' ? esc(b.role_line) : (draft ? '<span class="tag tag-tbc">TBC</span> Fungsi jenama' : '')}</p>
      <div class="prose">${desc}</div>
    </div>
    <aside class="side-card"><h2 class="foot-h">Saluran rasmi</h2>
      ${links ? `<p class="brand-links">${links}</p>` : `<p class="muted">${draft ? 'TBC' : 'Akan diumumkan'}</p>`}
      <p class="muted small">Sebahagian daripada <a href="/">LokaCreative Ventures</a>.</p></aside>
  </div></section>`;
}

function aboutPage({ c, draft }) {
  const block = (key, label) => html`<div class="about-block"><span class="pill pill-on">${label}</span>${field(c, key, { tag: 'p', cls: 'about-val' }, draft)}</div>`;
  const story = c.about_long?.status !== 'tbc' && c.about_long?.value ? paragraphs(c.about_long.value)
    : (draft ? '<p class="tbc-field"><span class="tag tag-tbc">TBC</span> Cerita syarikat</p>' : '');
  return html`${pageHead('Tentang', esc(c.company_name?.value || 'LokaCreative Ventures'))}
    <section class="section"><div class="wrap dark-body split"><div class="prose">${field(c, 'about_short', { tag: 'p', cls: 'big-copy' }, draft)}${story}</div>
      <div class="about-grid">${block('vision', 'Visi')}${block('mission', 'Misi')}${block('values', 'Nilai teras')}${block('founded_year', 'Ditubuhkan')}</div></div></section>`;
}

const KINDS = [['kerjasama', 'Kerjasama / partnership'], ['jenama', 'Pertanyaan tentang jenama'], ['media', 'Media'], ['kerjaya', 'Kerjaya'], ['lain', 'Lain-lain']];

function contactPage({ c, draft, sent, error, values = {}, kind }) {
  const v = (k) => esc(values[k] || '');
  const selected = values.kind || kind || 'kerjasama';
  return html`${pageHead('Hubungi', 'Hubungi kami', 'Untuk kerjasama di peringkat kumpulan, media atau kerjaya.')}
  <section class="section"><div class="wrap dark-body split">
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
    <aside class="side-card"><h2 class="foot-h">Maklumat rasmi</h2>
      <dl class="contact-dl"><dt>Email</dt><dd>${field(c, 'contact_email', {}, draft)}</dd><dt>Mobile</dt><dd>${field(c, 'contact_phone', {}, draft)}</dd><dt>Lokasi</dt><dd>${field(c, 'contact_address', {}, draft)}</dd></dl>
    </aside>
  </div></section>`;
}

function newsPage({ posts }) {
  return html`${pageHead('Terkini', 'Berita')}
    <section class="section"><div class="wrap dark-body">${posts.length ? `<ul class="posts">${posts.map(postCard).join('')}</ul>` : '<p class="empty">Belum ada berita diterbitkan.</p>'}</div></section>`;
}

function postPage({ p }) {
  return html`<section class="page-head">${bandHead(fmtDate(p.published_at), esc(p.title))}</section>
    <section class="section"><div class="wrap dark-body narrow prose">${p.excerpt ? `<p class="lede">${esc(p.excerpt)}</p>` : ''}${paragraphs(p.body)}<p><a href="/news">← Semua berita</a></p></div></section>`;
}

function privacyPage({ c, draft }) {
  return html`${pageHead('Privasi', 'Dasar privasi')}
  <section class="section"><div class="wrap dark-body narrow prose">
    ${draft ? '<p class="notice notice-warn">Draf templat. Perlu disemak oleh penasihat undang-undang sebelum diterbitkan (PDPA 2010).</p>' : ''}
    <h2>Data yang kami kumpul</h2><p>Apabila anda menghantar borang hubungi, kami menyimpan nama, emel, nama syarikat (jika diberi), jenis pertanyaan dan mesej anda. Alamat IP disimpan dalam bentuk hash sehala untuk mencegah spam. IP asal tidak disimpan.</p>
    <h2>Tujuan</h2><p>Data digunakan hanya untuk membalas pertanyaan anda dan menyalurkannya kepada jenama yang berkaitan dalam kumpulan.</p>
    <h2>Cookie</h2><p>Laman awam tidak menggunakan cookie penjejakan. Cookie sesi hanya digunakan dalam panel admin dalaman.</p>
    <h2>Hak anda</h2><p>Anda boleh meminta akses, pembetulan atau pemadaman data anda dengan menghubungi kami di ${field(c, 'contact_email', {}, draft)}.</p>
  </div></section>`;
}

function notFound() {
  return html`${pageHead('404', 'Tidak dijumpai', '<a href="/">Kembali ke laman utama</a>')}`;
}

function brandColorsCss(brands) {
  // accent values are validated as #RRGGBB on write; re-checked here before emitting CSS.
  return brands.filter((b) => /^#[0-9A-Fa-f]{6}$/.test(b.accent) && /^[a-z0-9-]+$/.test(b.slug))
    .map((b) => `.b-${b.slug}{--b:${b.accent}}`).join('\n');
}

module.exports = { esc, layout, home, brandsPage, brandPage, aboutPage, contactPage, newsPage, postPage, privacyPage, notFound, brandColorsCss, KINDS };
