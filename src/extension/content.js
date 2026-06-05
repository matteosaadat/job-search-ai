// Runs in the page context. Captures selection on mouseup (before popup opens).
let _stored = null;

document.addEventListener('mouseup', () => {
  const sel = window.getSelection();
  if (!sel || sel.rangeCount === 0 || sel.toString().trim().length < 15) {
    _stored = null;
    return;
  }

  const range = sel.getRangeAt(0);
  const div   = document.createElement('div');
  div.appendChild(range.cloneContents());
  const html = div.innerHTML;
  const text = sel.toString();

  // Extract job-related links from the selection
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
      links.push({ url: abs, text: (a.innerText || a.textContent || '').trim().slice(0, 80) });
    }
  });

  _stored = { hasSelection: true, html, text, links };
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === 'GET_SELECTION') {
    sendResponse(_stored || { hasSelection: false, html: '', text: '', links: [] });
  }
  return true; // keep channel open for async response
});
