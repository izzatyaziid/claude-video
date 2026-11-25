'use strict';
/* LokaCreative admin dashboard. No innerHTML with data: every value is set through textContent / attributes. */
(() => {
  const state = { user: null, csrf: '', view: 'overview' };
  const $ = (sel) => document.querySelector(sel);

  // ---------- DOM helper ----------
  function el(tag, attrs = {}, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === false || v === null || v === undefined) continue;
      if (k === 'class') n.className = v;
      else if (k === 'text') n.textContent = v;
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
      else if (k === 'value') n.value = v;
      else if (k === 'checked' || k === 'selected' || k === 'disabled') n[k] = !!v;
      else n.setAttribute(k, v === true ? '' : String(v));
    }
    for (const kid of kids.flat()) if (kid !== null && kid !== undefined && kid !== false) n.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
    return n;
  }
  const fmt = (ms) => (ms ? new Date(ms).toLocaleString('ms-MY', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Kuala_Lumpur' }) : '—');
  let uid = 0; const nid = (p) => `${p}-${++uid}`;

  function toast(msg, kind = 'ok') {
    const t = $('#toast');
    t.textContent = msg; t.className = `toast toast-${kind}`; t.hidden = false;
    clearTimeout(toast._t); toast._t = setTimeout(() => { t.hidden = true; }, 3200);
  }

  // ---------- API ----------
  async function api(path, { method = 'GET', body } = {}) {
    const headers = { Accept: 'application/json' };
    if (method !== 'GET') { headers['Content-Type'] = 'application/json'; headers['X-CSRF-Token'] = state.csrf; }
    const res = await fetch(`/admin/api${path}`, { method, headers, credentials: 'same-origin', body: body ? JSON.stringify(body) : undefined });
    let data = null;
    try { data = await res.json(); } catch { /* empty */ }
    if (res.status === 401 && !path.startsWith('/login')) { showLogin(); throw new Error('Sesi tamat. Sila log masuk semula.'); }
    if (res.status === 403 && data && data.mfa_setup_required && state.view !== 'account') { location.hash = '#account'; }
    if (!res.ok) throw new Error((data && data.error) || `Ralat ${res.status}`);
    return data;
  }
  const run = (fn, okMsg) => async (...a) => {
    try { await fn(...a); if (okMsg) toast(okMsg); } catch (e) { toast(e.message, 'err'); }
  };

  // ---------- auth ----------
  function showLogin() {
    state.user = null; state.csrf = ''; state.mfaToken = '';
    $('#app-view').hidden = true; $('#login-view').hidden = false;
    $('#mfa-form').hidden = true; $('#login-form').hidden = false;
    $('#login-email').focus();
  }
  function showMfa(token) {
    state.mfaToken = token; state.useRecovery = false;
    $('#login-form').hidden = true; $('#mfa-form').hidden = false;
    $('#mfa-code').value = ''; $('#mfa-recovery').value = ''; $('#mfa-error').hidden = true;
    setRecoveryMode(false);
  }
  function setRecoveryMode(on) {
    state.useRecovery = on;
    $('#mfa-code-label').hidden = on; $('#mfa-recovery-label').hidden = !on;
    $('#mfa-toggle').textContent = on ? 'Guna kod authenticator' : 'Guna kod pemulihan';
    $('#mfa-hint').textContent = on ? 'Masukkan satu kod pemulihan. Setiap kod hanya boleh digunakan sekali.' : 'Masukkan kod 6 digit daripada aplikasi authenticator anda.';
    (on ? $('#mfa-recovery') : $('#mfa-code')).focus();
  }
  $('#mfa-toggle').addEventListener('click', () => setRecoveryMode(!state.useRecovery));
  $('#mfa-back').addEventListener('click', showLogin);
  $('#mfa-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const err = $('#mfa-error'); err.hidden = true;
    const btn = e.target.querySelector('button[type="submit"]'); btn.disabled = true;
    try {
      const body = state.useRecovery ? { mfa_token: state.mfaToken, recovery: $('#mfa-recovery').value } : { mfa_token: state.mfaToken, code: $('#mfa-code').value.trim() };
      const d = await api('/login/mfa', { method: 'POST', body });
      state.user = d.user; state.csrf = d.csrf; state.mfaToken = '';
      showApp();
    } catch (ex) { err.textContent = ex.message; err.hidden = false; } finally { btn.disabled = false; }
  });
  function showApp() {
    $('#login-view').hidden = true; $('#app-view').hidden = false;
    $('#who').textContent = `${state.user.name} · ${state.user.role === 'owner' ? 'Owner' : 'Editor'}`;
    document.querySelectorAll('[data-owner]').forEach((n) => { n.hidden = state.user.role !== 'owner'; });
    route();
  }
  $('#login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const err = $('#login-error'); err.hidden = true;
    const btn = e.submitter || e.target.querySelector('button'); btn.disabled = true;
    try {
      const d = await api('/login', { method: 'POST', body: { email: $('#login-email').value, password: $('#login-password').value } });
      $('#login-password').value = '';
      if (d.mfa_required) { showMfa(d.mfa_token); return; }
      state.user = d.user; state.csrf = d.csrf;
      showApp();
    } catch (ex) { err.textContent = ex.message; err.hidden = false; } finally { btn.disabled = false; }
  });
  $('#logout').addEventListener('click', run(async () => { await api('/logout', { method: 'POST' }); showLogin(); }, 'Anda telah log keluar.'));

  // ---------- router ----------
  const VIEWS = {};
  function route() {
    if (!state.user) return;
    let v = (location.hash || '#overview').slice(1);
    if (!VIEWS[v] || (['admins', 'audit'].includes(v) && state.user.role !== 'owner')) v = 'overview';
    const mustEnrol = state.user.require2fa && !state.user.mfa;
    if (mustEnrol) v = 'account';
    document.querySelectorAll('#nav a').forEach((a) => { a.toggleAttribute('aria-disabled', mustEnrol && a.dataset.view !== 'account'); });
    state.view = v;
    document.querySelectorAll('#nav a').forEach((a) => { if (a.dataset.view === v) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    const main = $('#main'); main.replaceChildren(el('p', { class: 'muted', text: 'Memuatkan…' }));
    VIEWS[v](main).catch((e) => main.replaceChildren(el('p', { class: 'form-error', text: e.message })));
    refreshBadge();
  }
  window.addEventListener('hashchange', route);
  async function refreshBadge() {
    if (state.user.require2fa && !state.user.mfa) return;
    try { const s = await api('/stats'); const b = $('#badge-new'); b.textContent = s.inquiriesNew; b.hidden = !s.inquiriesNew; } catch { /* ignore */ }
  }
  const head = (title, sub, ...actions) => el('header', { class: 'view-head' }, el('div', {}, el('h1', { text: title }), sub ? el('p', { class: 'muted', text: sub }) : null), el('div', { class: 'head-actions' }, actions));
  const statusTag = (s) => el('span', { class: `tag tag-${s}`, text: { confirmed: 'Disahkan', proposal: 'Cadangan', tbc: 'TBC' }[s] || s });
  function confirmButton(label, onConfirm) {
    // In-page two-step confirm (the viewer blocks confirm()).
    const b = el('button', { class: 'btn btn-danger btn-small', type: 'button', text: label });
    let armed = false, t;
    b.addEventListener('click', async () => {
      if (!armed) { armed = true; b.textContent = 'Sahkan?'; t = setTimeout(() => { armed = false; b.textContent = label; }, 4000); return; }
      clearTimeout(t); b.disabled = true; await onConfirm(); b.disabled = false; armed = false; b.textContent = label;
    });
    return b;
  }
  function selectEl(id, options, value) {
    return el('select', { id }, options.map(([v, l]) => el('option', { value: v, text: l, selected: v === value })));
  }

  // ---------- overview ----------
  VIEWS.overview = async (main) => {
    const s = await api('/stats');
    const filled = s.contentTotal - s.contentTbc;
    const pct = s.contentTotal ? Math.round((filled / s.contentTotal) * 100) : 0;
    const tile = (label, value, note, href) => el('a', { class: 'tile', href }, el('span', { class: 'tile-label', text: label }), el('span', { class: 'tile-value', text: value }), el('span', { class: 'tile-note', text: note }));
    main.replaceChildren(
      head('Ringkasan', s.draftMode ? 'Laman dalam mod DRAF: penanda TBC/CADANGAN dipaparkan dan enjin carian disekat.' : 'Laman dalam mod LIVE.'),
      el('div', { class: 'tiles' },
        tile('Pertanyaan baru', s.inquiriesNew, `${s.inquiriesTotal} jumlah`, '#inquiries'),
        tile('Kandungan TBC', s.contentTbc, `${s.contentProposal} cadangan menunggu kelulusan`, '#content'),
        tile('Jenama TBC', s.brandsTbc, `${s.brands} jenama dipaparkan`, '#brands'),
        tile('Berita diterbitkan', s.postsPublished, `${s.postsDraft} draf`, '#news')),
      el('section', { class: 'panel' },
        el('div', { class: 'panel-head' }, el('h2', { text: 'Kesempurnaan kandungan' }), el('span', { class: 'mono', text: `${filled}/${s.contentTotal} medan · ${pct}%` })),
        el('div', { class: 'meter', role: 'progressbar', 'aria-valuemin': 0, 'aria-valuemax': 100, 'aria-valuenow': pct, 'aria-label': 'Kesempurnaan kandungan' }, el('span', { class: 'meter-fill', style: null, 'data-pct': pct })),
        el('p', { class: 'muted small', text: 'Medan TBC tidak dipaparkan apabila mod draf dimatikan. Isi dan sahkan sebelum pelancaran.' })),
      el('section', { class: 'panel' },
        el('div', { class: 'panel-head' }, el('h2', { text: 'Pertanyaan terkini' }), el('a', { href: '#inquiries', text: 'Lihat semua' })),
        s.recentInquiries.length
          ? el('div', { class: 'table-wrap' }, el('table', {}, el('thead', {}, el('tr', {}, ['Tarikh', 'Nama', 'Syarikat', 'Jenis', 'Status'].map((h) => el('th', { text: h })))),
            el('tbody', {}, s.recentInquiries.map((q) => el('tr', {}, el('td', { text: fmt(q.created_at) }), el('td', { text: q.name }), el('td', { text: q.company || '—' }), el('td', { text: q.kind }), el('td', {}, el('span', { class: `pill pill-${q.status}`, text: { new: 'Baru', read: 'Dibaca', archived: 'Arkib' }[q.status] || q.status })))))))
          : el('p', { class: 'empty', text: 'Belum ada pertanyaan. Borang di /contact akan muncul di sini.' })),
    );
    // width via CSSOM (allowed by CSP, unlike inline style attributes)
    main.querySelector('.meter-fill').style.width = `${pct}%`;
  };

  // ---------- inquiries ----------
  VIEWS.inquiries = async (main) => {
    const filter = VIEWS.inquiries.filter || '';
    const rows = await api(`/inquiries${filter ? `?status=${filter}` : ''}`);
    const tabs = el('div', { class: 'tabs', role: 'tablist' }, [['', 'Semua'], ['new', 'Baru'], ['read', 'Dibaca'], ['archived', 'Arkib']].map(([k, l]) =>
      el('button', { type: 'button', role: 'tab', class: 'tab', 'aria-selected': String(k === filter), text: l, onclick: () => { VIEWS.inquiries.filter = k; route(); } })));
    const setStatus = (id, status) => run(async () => { await api(`/inquiries/${id}`, { method: 'PATCH', body: { status } }); route(); }, 'Status dikemas kini.');
    main.replaceChildren(head('Pertanyaan', 'Dari borang hubungi. Data peribadi: guna hanya untuk membalas (PDPA).'), tabs,
      rows.length ? el('ul', { class: 'inq-list' }, rows.map((q) => el('li', { class: `inq inq-${q.status}` },
        el('details', {}, el('summary', {},
          el('span', { class: 'inq-name', text: q.name }), el('span', { class: 'muted', text: q.company || '' }),
          el('span', { class: 'tag', text: q.kind }), el('span', { class: 'mono small muted', text: fmt(q.created_at) })),
        el('div', { class: 'inq-body' },
          el('p', { class: 'mono small' }, 'Emel: ', el('span', { class: 'selectable', text: q.email })),
          el('p', { class: 'inq-msg', text: q.message }),
          el('div', { class: 'row-actions' },
            q.status !== 'read' ? el('button', { class: 'btn btn-small', type: 'button', text: 'Tanda dibaca', onclick: setStatus(q.id, 'read') }) : null,
            q.status !== 'archived' ? el('button', { class: 'btn btn-ghost btn-small', type: 'button', text: 'Arkib', onclick: setStatus(q.id, 'archived') }) : null,
            q.status !== 'new' ? el('button', { class: 'btn btn-ghost btn-small', type: 'button', text: 'Tanda baru', onclick: setStatus(q.id, 'new') }) : null,
            state.user.role === 'owner' ? confirmButton('Padam', run(async () => { await api(`/inquiries/${q.id}`, { method: 'DELETE' }); route(); }, 'Pertanyaan dipadam.')) : null))))))
        : el('p', { class: 'empty', text: 'Tiada pertanyaan dalam kategori ini.' }));
  };

  // ---------- brands ----------
  VIEWS.brands = async (main) => {
    const brands = await api('/brands');
    main.replaceChildren(head('Jenama', 'Register ekosistem. Hanya isi fakta yang disahkan; selebihnya biarkan TBC.'),
      el('div', { class: 'stack' }, brands.map((b) => brandForm(b))));
  };
  function brandForm(b) {
    const ids = {}; const f = (k) => (ids[k] = nid(`b${b.id}-${k}`));
    const form = el('form', { class: 'panel form', novalidate: true },
      el('div', { class: 'panel-head' }, el('h2', {}, el('span', { class: 'mono muted', text: `${b.code} ` }), b.name), statusTag(b.fact_status)),
      el('div', { class: 'grid2' },
        el('label', { for: f('name') }, 'Nama', el('input', { id: ids.name, value: b.name, maxlength: 60, required: true })),
        el('label', { for: f('role') }, 'Fungsi (1 ayat)', el('input', { id: ids.role, value: b.role_line, maxlength: 120 }))),
      el('label', { for: f('desc') }, 'Penerangan', el('textarea', { id: ids.desc, rows: 3, maxlength: 1200, value: b.description })),
      el('div', { class: 'grid4' },
        el('label', { for: f('fact') }, 'Status fakta', selectEl(ids.fact, [['confirmed', 'Disahkan'], ['proposal', 'Cadangan'], ['tbc', 'TBC']], b.fact_status)),
        el('label', { for: f('status') }, 'Paparan', selectEl(ids.status, [['active', 'Aktif'], ['coming_soon', 'Akan datang'], ['hidden', 'Sembunyi']], b.status)),
        el('label', { for: f('accent') }, 'Warna jenama', el('input', { id: ids.accent, type: 'color', value: b.accent })),
        el('label', { for: f('order') }, 'Susunan', el('input', { id: ids.order, type: 'number', min: 0, max: 99, value: b.sort_order }))),
      el('div', { class: 'grid3' },
        el('label', { for: f('web') }, 'Website (https)', el('input', { id: ids.web, type: 'url', value: b.website_url, placeholder: 'https://' })),
        el('label', { for: f('ig') }, 'Instagram (https)', el('input', { id: ids.ig, type: 'url', value: b.instagram_url, placeholder: 'https://' })),
        el('label', { for: f('fb') }, 'Facebook (https)', el('input', { id: ids.fb, type: 'url', value: b.facebook_url, placeholder: 'https://' }))),
      el('div', { class: 'row-actions' }, el('button', { class: 'btn', type: 'submit', text: 'Simpan' }), el('a', { class: 'small', href: `/brands/${encodeURIComponent(b.slug)}`, target: '_blank', rel: 'noopener', text: 'Lihat halaman' })));
    form.addEventListener('submit', run(async (e) => {
      e.preventDefault();
      const v = (k) => document.getElementById(ids[k]).value;
      await api(`/brands/${b.id}`, { method: 'PUT', body: { name: v('name'), role_line: v('role'), description: v('desc'), fact_status: v('fact'), status: v('status'), accent: v('accent'), sort_order: v('order'), website_url: v('web'), instagram_url: v('ig'), facebook_url: v('fb') } });
      route();
    }, `${b.name} disimpan.`));
    return form;
  }

  // ---------- content ----------
  VIEWS.content = async (main) => {
    const rows = await api('/content');
    const groups = {};
    rows.forEach((r) => (groups[r.grp] = groups[r.grp] || []).push(r));
    main.replaceChildren(head('Kandungan', 'Teks laman. Status: Disahkan (fakta), Cadangan (perlu kelulusan), TBC (belum ada).'),
      ...Object.entries(groups).map(([g, items]) => el('section', { class: 'panel' }, el('h2', { text: g }), el('div', { class: 'stack' }, items.map(contentRow)))));
  };
  function contentRow(r) {
    const vid = nid('c'), sid = nid('s');
    const long = r.max_len > 200;
    const input = long ? el('textarea', { id: vid, rows: r.max_len > 1000 ? 6 : 3, maxlength: r.max_len, value: r.value }) : el('input', { id: vid, maxlength: r.max_len, value: r.value });
    const count = el('span', { class: 'mono small muted', text: `${r.value.length}/${r.max_len}` });
    input.addEventListener('input', () => { count.textContent = `${input.value.length}/${r.max_len}`; });
    const form = el('form', { class: 'content-row form', novalidate: true },
      el('label', { for: vid }, el('span', { class: 'label-line' }, r.label, statusTag(r.status)), input),
      el('div', { class: 'row-actions' },
        el('label', { for: sid, class: 'inline' }, 'Status', selectEl(sid, [['confirmed', 'Disahkan'], ['proposal', 'Cadangan'], ['tbc', 'TBC']], r.status)),
        count, el('button', { class: 'btn btn-small', type: 'submit', text: 'Simpan' })));
    form.addEventListener('submit', run(async (e) => {
      e.preventDefault();
      await api(`/content/${encodeURIComponent(r.key)}`, { method: 'PUT', body: { value: input.value, status: document.getElementById(sid).value } });
      route();
    }, `${r.label} disimpan.`));
    return form;
  }

  // ---------- news ----------
  VIEWS.news = async (main) => {
    const posts = await api('/posts');
    const editor = el('div', { id: 'post-editor' });
    main.replaceChildren(head('Berita', 'Isi berita ialah teks biasa (tiada HTML). Perenggan dipisahkan dengan baris kosong.',
      el('button', { class: 'btn', type: 'button', text: 'Berita baru', onclick: () => editor.replaceChildren(postForm()) })), editor,
    posts.length ? el('div', { class: 'table-wrap' }, el('table', {}, el('thead', {}, el('tr', {}, ['Tajuk', 'Status', 'Dikemas kini', ''].map((h) => el('th', { text: h })))),
      el('tbody', {}, posts.map((p) => el('tr', {}, el('td', { text: p.title }), el('td', {}, el('span', { class: `pill pill-${p.status}`, text: p.status === 'published' ? 'Diterbitkan' : 'Draf' })), el('td', { text: fmt(p.updated_at) }),
        el('td', { class: 'row-actions' }, el('button', { class: 'btn btn-ghost btn-small', type: 'button', text: 'Sunting', onclick: () => { editor.replaceChildren(postForm(p)); editor.scrollIntoView({ behavior: 'smooth' }); } }),
          confirmButton('Padam', run(async () => { await api(`/posts/${p.id}`, { method: 'DELETE' }); route(); }, 'Berita dipadam.'))))))))
      : el('p', { class: 'empty', text: 'Belum ada berita.' }));
  };
  function postForm(p = { title: '', slug: '', excerpt: '', body: '', status: 'draft' }) {
    const ids = { t: nid('pt'), s: nid('ps'), e: nid('pe'), b: nid('pb'), st: nid('pst') };
    const slugify = (t) => t.toLowerCase().normalize('NFKD').replace(/[^\w\s-]/g, '').trim().replace(/[\s_]+/g, '-').replace(/-+/g, '-').slice(0, 80);
    const title = el('input', { id: ids.t, value: p.title, maxlength: 160, required: true });
    const slug = el('input', { id: ids.s, value: p.slug, maxlength: 80, required: true, pattern: '[a-z0-9]+(-[a-z0-9]+)*' });
    if (!p.id) title.addEventListener('input', () => { slug.value = slugify(title.value); });
    const form = el('form', { class: 'panel form', novalidate: true },
      el('h2', { text: p.id ? 'Sunting berita' : 'Berita baru' }),
      el('div', { class: 'grid2' }, el('label', { for: ids.t }, 'Tajuk', title), el('label', { for: ids.s }, 'Slug (URL)', slug)),
      el('label', { for: ids.e }, 'Ringkasan', el('textarea', { id: ids.e, rows: 2, maxlength: 300, value: p.excerpt })),
      el('label', { for: ids.b }, 'Isi', el('textarea', { id: ids.b, rows: 10, maxlength: 20000, value: p.body })),
      el('div', { class: 'row-actions' }, el('label', { for: ids.st, class: 'inline' }, 'Status', selectEl(ids.st, [['draft', 'Draf'], ['published', 'Terbitkan']], p.status)),
        el('button', { class: 'btn', type: 'submit', text: 'Simpan' }), el('button', { class: 'btn btn-ghost', type: 'button', text: 'Batal', onclick: () => form.remove() })));
    form.addEventListener('submit', run(async (e) => {
      e.preventDefault();
      const body = { title: title.value, slug: slug.value, excerpt: document.getElementById(ids.e).value, body: document.getElementById(ids.b).value, status: document.getElementById(ids.st).value };
      await api(p.id ? `/posts/${p.id}` : '/posts', { method: p.id ? 'PUT' : 'POST', body });
      route();
    }, 'Berita disimpan.'));
    return form;
  }

  // ---------- admins ----------
  VIEWS.admins = async (main) => {
    const admins = await api('/admins');
    const ids = { e: nid('ae'), n: nid('an'), r: nid('ar'), p: nid('ap') };
    const form = el('form', { class: 'panel form', novalidate: true }, el('h2', { text: 'Tambah admin' }),
      el('div', { class: 'grid4' },
        el('label', { for: ids.n }, 'Nama', el('input', { id: ids.n, maxlength: 80, required: true })),
        el('label', { for: ids.e }, 'Emel', el('input', { id: ids.e, type: 'email', maxlength: 254, required: true, autocomplete: 'off' })),
        el('label', { for: ids.r }, 'Peranan', selectEl(ids.r, [['editor', 'Editor'], ['owner', 'Owner']], 'editor')),
        el('label', { for: ids.p }, 'Kata laluan sementara', el('input', { id: ids.p, type: 'password', minlength: 12, maxlength: 200, required: true, autocomplete: 'new-password' }))),
      el('p', { class: 'muted small', text: 'Min 12 aksara, 3 jenis aksara. Editor boleh urus kandungan dan pertanyaan; hanya Owner boleh urus admin, log audit dan padam pertanyaan.' }),
      el('button', { class: 'btn', type: 'submit', text: 'Tambah' }));
    form.addEventListener('submit', run(async (e) => {
      e.preventDefault();
      const v = (k) => document.getElementById(ids[k]).value;
      await api('/admins', { method: 'POST', body: { name: v('n'), email: v('e'), role: v('r'), password: v('p') } });
      route();
    }, 'Admin ditambah.'));
    const patch = (id, body, msg) => run(async () => { await api(`/admins/${id}`, { method: 'PATCH', body }); route(); }, msg);
    main.replaceChildren(head('Pengguna admin', 'Prinsip akses minimum: beri peranan Editor melainkan perlu.'),
      el('div', { class: 'table-wrap' }, el('table', {}, el('thead', {}, el('tr', {}, ['Nama', 'Emel', 'Peranan', 'Status', '2FA', 'Log masuk terakhir', ''].map((h) => el('th', { text: h })))),
        el('tbody', {}, admins.map((a) => {
          const self = a.id === state.user.id;
          const locked = a.locked_until && a.locked_until > Date.now();
          return el('tr', {}, el('td', { text: a.name + (self ? ' (anda)' : '') }), el('td', { text: a.email }), el('td', { text: a.role }),
            el('td', {}, el('span', { class: `pill pill-${a.active ? (locked ? 'locked' : 'active') : 'archived'}`, text: a.active ? (locked ? 'Dikunci' : 'Aktif') : 'Dinyahaktif' })),
            el('td', {}, el('span', { class: `pill ${a.totp_enabled ? 'pill-active' : 'pill-new'}`, text: a.totp_enabled ? 'Aktif' : 'Belum' })),
            el('td', { text: fmt(a.last_login_at) }),
            el('td', { class: 'row-actions' }, self ? null : [
              a.totp_enabled ? confirmButton('Reset 2FA', patch(a.id, { reset_2fa: true }, '2FA direset. Admin perlu daftar semula.')) : null,
              el('button', { class: 'btn btn-ghost btn-small', type: 'button', text: a.role === 'owner' ? 'Jadikan Editor' : 'Jadikan Owner', onclick: patch(a.id, { role: a.role === 'owner' ? 'editor' : 'owner' }, 'Peranan dikemas kini.') }),
              locked ? el('button', { class: 'btn btn-ghost btn-small', type: 'button', text: 'Buka kunci', onclick: patch(a.id, { unlock: true }, 'Akaun dibuka.') }) : null,
              a.active ? confirmButton('Nyahaktif', patch(a.id, { active: false }, 'Akaun dinyahaktif.')) : el('button', { class: 'btn btn-small', type: 'button', text: 'Aktifkan', onclick: patch(a.id, { active: true }, 'Akaun diaktifkan.') }),
            ]));
        })))), form);
  };

  // ---------- audit ----------
  VIEWS.audit = async (main) => {
    const rows = await api('/audit');
    main.replaceChildren(head('Log audit', '200 peristiwa terkini: log masuk, perubahan kandungan dan akaun.'),
      el('div', { class: 'table-wrap' }, el('table', {}, el('thead', {}, el('tr', {}, ['Masa', 'Admin', 'Tindakan', 'Entiti', 'Butiran'].map((h) => el('th', { text: h })))),
        el('tbody', {}, rows.map((r) => el('tr', { class: /fail|lock/.test(r.action) ? 'row-warn' : '' }, el('td', { class: 'mono small', text: fmt(r.created_at) }), el('td', { text: r.admin_email || '—' }),
          el('td', { class: 'mono small', text: r.action }), el('td', { text: `${r.entity} ${r.entity_id}`.trim() }), el('td', { class: 'small', text: r.detail })))))));
  };

  // ---------- account ----------
  VIEWS.account = async (main) => {
    const ids = { c: nid('pc'), n: nid('pn'), r: nid('pr') };
    const form = el('form', { class: 'panel form narrow-form', novalidate: true }, el('h2', { text: 'Tukar kata laluan' }),
      el('label', { for: ids.c }, 'Kata laluan semasa', el('input', { id: ids.c, type: 'password', autocomplete: 'current-password', required: true, maxlength: 200 })),
      el('label', { for: ids.n }, 'Kata laluan baru', el('input', { id: ids.n, type: 'password', autocomplete: 'new-password', required: true, minlength: 12, maxlength: 200 })),
      el('label', { for: ids.r }, 'Ulang kata laluan baru', el('input', { id: ids.r, type: 'password', autocomplete: 'new-password', required: true, maxlength: 200 })),
      el('p', { class: 'muted small', text: 'Selepas tukar, semua sesi lain akaun ini akan ditamatkan.' }),
      el('button', { class: 'btn', type: 'submit', text: 'Tukar kata laluan' }));
    form.addEventListener('submit', run(async (e) => {
      e.preventDefault();
      const v = (k) => document.getElementById(ids[k]).value;
      if (v('n') !== v('r')) throw new Error('Kata laluan baru tidak sama.');
      await api('/me/password', { method: 'POST', body: { current: v('c'), next: v('n') } });
      form.reset();
    }, 'Kata laluan ditukar.'));
    const mfa = await api('/me/2fa');
    const mustEnrol = mfa.required && !mfa.enabled;
    main.replaceChildren(...[
      head('Akaun saya', `${state.user.email} · ${state.user.role}`),
      mustEnrol ? el('div', { class: 'callout', role: 'alert' }, el('strong', { text: 'Langkah wajib: aktifkan 2FA.' }), ' Dashboard dikunci sehingga pengesahan dua langkah diaktifkan untuk akaun ini.') : null,
      twoFactorPanel(mfa),
      mustEnrol ? null : form].filter(Boolean));
  };

  function copyButton(getText, label = 'Salin') {
    const b = el('button', { class: 'btn btn-ghost btn-small', type: 'button', text: label });
    b.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(getText()); toast('Disalin.'); } catch { toast('Tidak dapat menyalin: pilih teks dan salin secara manual.', 'err'); }
    });
    return b;
  }

  function recoveryBlock(codes) {
    const text = codes.join('\n');
    return el('div', { class: 'recovery' },
      el('h3', { text: 'Kod pemulihan' }),
      el('p', { class: 'muted small', text: 'Simpan di tempat selamat (contoh: pengurus kata laluan). Setiap kod boleh digunakan sekali jika telefon hilang. Kod ini tidak akan dipaparkan lagi.' }),
      el('ol', { class: 'codes selectable' }, codes.map((c) => el('li', { class: 'mono', text: c }))),
      el('div', { class: 'row-actions' }, copyButton(() => text, 'Salin semua kod'),
        el('button', { class: 'btn btn-small', type: 'button', text: 'Saya sudah simpan', onclick: () => { state.user.mfa = true; location.hash = '#overview'; route(); } })));
  }

  function twoFactorPanel(mfa) {
    const panel = el('section', { class: 'panel' });
    const title = el('div', { class: 'panel-head' }, el('h2', { text: 'Pengesahan dua langkah (2FA)' }),
      el('span', { class: `pill ${mfa.enabled ? 'pill-active' : 'pill-new'}`, text: mfa.enabled ? 'Aktif' : 'Belum aktif' }));

    if (!mfa.enabled) {
      const pw = nid('tp');
      const start = el('form', { class: 'form narrow-form', novalidate: true },
        el('p', { class: 'muted small', text: 'Guna aplikasi authenticator seperti Google Authenticator, Microsoft Authenticator atau Authy. Sahkan kata laluan untuk mula.' }),
        el('label', { for: pw }, 'Kata laluan semasa', el('input', { id: pw, type: 'password', autocomplete: 'current-password', required: true, maxlength: 200 })),
        el('button', { class: 'btn', type: 'submit', text: 'Mula persediaan' }));
      start.addEventListener('submit', run(async (e) => {
        e.preventDefault();
        const d = await api('/me/2fa/setup', { method: 'POST', body: { password: document.getElementById(pw).value } });
        const code = nid('tc');
        const verify = el('form', { class: 'form', novalidate: true },
          el('ol', { class: 'steps' },
            el('li', {}, 'Imbas kod QR ini dengan aplikasi authenticator.'),
            el('li', {}, 'Tidak boleh imbas? Masukkan kunci ini secara manual: ', el('code', { class: 'selectable', text: d.secret.replace(/(.{4})/g, '$1 ').trim() }), ' ', copyButton(() => d.secret)),
            el('li', {}, 'Masukkan kod 6 digit yang dipaparkan oleh aplikasi.')),
          el('div', { class: 'qr-row' }, el('img', { class: 'qr', src: d.qr, alt: 'Kod QR untuk aplikasi authenticator', width: 200, height: 200 }),
            el('div', { class: 'form' },
              el('label', { for: code }, 'Kod 6 digit', el('input', { id: code, inputmode: 'numeric', autocomplete: 'one-time-code', maxlength: 6, required: true })),
              el('button', { class: 'btn', type: 'submit', text: 'Sahkan & aktifkan' }))));
        verify.addEventListener('submit', run(async (ev) => {
          ev.preventDefault();
          const r = await api('/me/2fa/enable', { method: 'POST', body: { code: document.getElementById(code).value.trim() } });
          panel.replaceChildren(title, el('p', { class: 'notice-ok', text: '2FA diaktifkan.' }), recoveryBlock(r.recovery_codes));
          title.querySelector('.pill').className = 'pill pill-active'; title.querySelector('.pill').textContent = 'Aktif';
        }, '2FA diaktifkan.'));
        start.replaceWith(verify);
        document.getElementById(code).focus();
      }));
      panel.append(title, start);
      return panel;
    }

    const pw = nid('tp'); const code = nid('tc');
    const manage = el('form', { class: 'form narrow-form', novalidate: true },
      el('p', { class: 'muted small', text: `${mfa.recovery_left} kod pemulihan berbaki. Untuk jana kod baru atau nyahaktif, sahkan kata laluan dan kod 2FA.` }),
      el('label', { for: pw }, 'Kata laluan semasa', el('input', { id: pw, type: 'password', autocomplete: 'current-password', maxlength: 200 })),
      el('label', { for: code }, 'Kod 6 digit', el('input', { id: code, inputmode: 'numeric', autocomplete: 'one-time-code', maxlength: 6 })),
      el('div', { class: 'row-actions' },
        el('button', { class: 'btn btn-small', type: 'button', text: 'Jana kod pemulihan baru', onclick: run(async () => {
          const r = await api('/me/2fa/recovery', { method: 'POST', body: { password: document.getElementById(pw).value, code: document.getElementById(code).value.trim() } });
          manage.replaceWith(recoveryBlock(r.recovery_codes));
        }, 'Kod pemulihan baru dijana.') }),
        mfa.required ? null : confirmButton('Nyahaktif 2FA', run(async () => {
          await api('/me/2fa/disable', { method: 'POST', body: { password: document.getElementById(pw).value, code: document.getElementById(code).value.trim() } });
          state.user.mfa = false; route();
        }, '2FA dinyahaktif.'))));
    panel.append(title, manage);
    return panel;
  }

  // ---------- boot ----------
  api('/me').then((d) => { state.user = d.user; state.csrf = d.csrf; showApp(); }).catch(() => showLogin());
})();
