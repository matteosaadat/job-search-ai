const API = 'http://localhost:8001';

let _type     = 'single';
let _html     = '';
let _text     = '';
let _links    = [];
let _url      = '';
let _hasSelection = false;

async function init() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  _url = tab.url || '';
  document.getElementById('page-url').textContent = _url || '(no URL)';

  // 1. Try content script message (fastest — has stored selection from mouseup)
  try {
    const data = await chrome.tabs.sendMessage(tab.id, { type: 'GET_SELECTION' });
    _hasSelection = data.hasSelection || false;
    _html = data.html || '';
    _text = data.text || '';
    _links = data.links || [];
    renderPreview();
    return;
  } catch (_) { /* content script not injected yet — fall through */ }

  // 2. Content script wasn't loaded — read selection directly from the page DOM.
  //    The selection is still in the DOM even though popup has focus.
  try {
    const result = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        const sel = window.getSelection();
        if (!sel || sel.rangeCount === 0 || sel.toString().trim().length < 10) {
          return { hasSelection: false, html: '', text: '', links: [] };
        }
        const range = sel.getRangeAt(0);
        const div   = document.createElement('div');
        div.appendChild(range.cloneContents());
        const html = div.innerHTML;
        const text = sel.toString();
        const base = location.origin;
        const seen = new Set();
        const links = [];
        div.querySelectorAll('a[href]').forEach(a => {
          const href = a.href || a.getAttribute('href') || '';
          if (!href || href.startsWith('javascript:') || href.startsWith('#')) return;
          const abs = href.startsWith('http') ? href : base + href;
          if (!abs.match(/jobs?\/|\/view\/|\/posting\/|rc\/clk|job-listing|job_id|jk=/i)) return;
          if (!seen.has(abs)) {
            seen.add(abs);
            links.push({ url: abs, text: (a.innerText || '').trim().slice(0, 80) });
          }
        });
        return { hasSelection: true, html, text, links };
      },
    });
    const data = result[0]?.result || { hasSelection: false, html: '', text: '', links: [] };
    _hasSelection = data.hasSelection;
    _html  = data.html;
    _text  = data.text;
    _links = data.links;
    renderPreview();
  } catch (e) {
    document.getElementById('sel-badge').textContent = 'Restricted page';
    document.getElementById('sel-badge').className   = 'badge badge-warn';
    document.getElementById('preview').innerHTML =
      '<span style="color:#555">Cannot access this page (browser internal pages only).</span>';
    document.getElementById('capture-btn').disabled = true;
  }
}

function renderPreview() {
  const preview  = document.getElementById('preview');
  const selBadge = document.getElementById('sel-badge');
  const linkBadge = document.getElementById('link-badge');
  const btn      = document.getElementById('capture-btn');

  if (!_hasSelection) {
    selBadge.textContent  = 'No selection';
    selBadge.className    = 'badge badge-warn';
    linkBadge.style.display = 'none';
    preview.innerHTML     = '<span style="color:#f59e0b">Select text on the page first, then re-open the extension.</span>';
    btn.disabled = true;
    return;
  }

  selBadge.textContent  = 'Selection captured';
  selBadge.className    = 'badge badge-ok';

  if (_links.length) {
    linkBadge.textContent = `${_links.length} link${_links.length !== 1 ? 's' : ''}`;
    linkBadge.style.display = 'inline-block';
  } else {
    linkBadge.style.display = 'none';
  }

  // Preview: show first ~300 chars of plain text, highlight links inline
  const lines = _text.split('\n').map(l => l.trim()).filter(Boolean).slice(0, 12);
  const previewText = lines.join('\n');
  const truncated   = previewText.length > 300 ? previewText.slice(0, 300) + '…' : previewText;

  let linkList = '';
  if (_links.length) {
    linkList = '<div class="link-list">' +
      _links.slice(0, 5).map(l =>
        `<div class="link-item" title="${escHtml(l.url)}">↗ ${escHtml(l.text || l.url.split('/').pop())}</div>`
      ).join('') +
      (_links.length > 5 ? `<div class="link-item" style="opacity:.5">+${_links.length - 5} more</div>` : '') +
      '</div>';
  }

  preview.innerHTML = `<pre class="preview-text">${escHtml(truncated)}</pre>${linkList}`;
  btn.disabled = false;
}

function setType(t) {
  _type = t;
  document.getElementById('btn-single').classList.toggle('active', t === 'single');
  document.getElementById('btn-list').classList.toggle('active', t === 'list');
  document.getElementById('result').style.display = 'none';
}

async function capture() {
  const btn = document.getElementById('capture-btn');
  btn.disabled    = true;
  btn.textContent = 'Capturing…';
  showOk('Sending to Job Hunt…');

  try {
    const links = _links.map(l => typeof l === 'string' ? l : l.url).filter(Boolean);
    const r = await fetch(`${API}/api/jobs/intake`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: _text,
        html: _html,
        source_url: _url,
        job_type: _type,
        links,
      }),
    });
    const data = await r.json();
    if (r.ok) {
      const id     = data.job_id || data.batch_id || 'captured';
      const label  = data.job_id ? 'Job captured' : 'Batch captured';
      const queued = data.auto_queued
        ? '<span class="result-sub">Claude is processing…</span>'
        : '<span class="result-sub">Open Job Hunt to continue.</span>';
      showOk(`${label} <span class="result-id">${id}</span><br>${queued}`);
    } else {
      showErr(data.detail || `Server error ${r.status}`);
    }
  } catch (e) {
    console.error('capture error:', e);
    const msg = e.message || String(e);
    const offline = msg.includes('fetch') || msg.includes('Failed') || msg.includes('network');
    showErr(offline ? 'Job Hunt server offline — is it running on port 8001?' : msg);
  }

  btn.textContent = 'Capture Selection';
  btn.disabled    = false;
}

function showOk(html) {
  const el = document.getElementById('result');
  el.className = 'result ok'; el.innerHTML = html; el.style.display = 'block';
}
function showErr(html) {
  const el = document.getElementById('result');
  el.className = 'result err'; el.innerHTML = html; el.style.display = 'block';
}
function escHtml(s) {
  return (s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

document.getElementById('capture-btn').addEventListener('click', capture);
document.getElementById('btn-single').addEventListener('click', () => setType('single'));
document.getElementById('btn-list').addEventListener('click', () => setType('list'));

init();
