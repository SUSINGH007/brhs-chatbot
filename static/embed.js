/**
 * BRHS Chatbot – floating embed script
 * School webmaster pastes ONE line into hs.brrsd.org:
 *   <script src="https://your-server.com/static/embed.js"><\/script>
 *
 * Optional attribute on the script tag:
 *   data-api="https://your-server.com"   (defaults to same origin as this script)
 */
(function () {
  if (document.getElementById('brhs-chat-root')) return; // prevent double-load

  // Resolve the API base from the script tag's src or data-api attribute
  const scriptEl = document.currentScript ||
    [...document.querySelectorAll('script')].find(s => s.src.includes('embed.js'));
  const apiBase = (scriptEl && scriptEl.dataset.api) ||
    (scriptEl ? new URL(scriptEl.src).origin : '');

  // ── Styles ──────────────────────────────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = `
    #brhs-chat-root * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    #brhs-fab {
      position: fixed; bottom: 24px; right: 24px; z-index: 99999;
      width: 58px; height: 58px; border-radius: 50%;
      background: #002060; color: #FFB800;
      border: none; cursor: pointer; box-shadow: 0 4px 18px rgba(0,0,0,.28);
      display: flex; align-items: center; justify-content: center;
      transition: transform .2s, background .2s;
    }
    #brhs-fab:hover { background: #003080; transform: scale(1.07); }
    #brhs-fab svg  { width: 26px; height: 26px; fill: currentColor; }
    #brhs-badge {
      position: absolute; top: -3px; right: -3px;
      background: #FFB800; color: #002060;
      width: 18px; height: 18px; border-radius: 50%;
      font-size: 10px; font-weight: 800;
      display: flex; align-items: center; justify-content: center;
      display: none;
    }
    #brhs-panel {
      position: fixed; bottom: 96px; right: 24px; z-index: 99998;
      width: 380px; height: 580px; max-height: 80vh;
      border-radius: 16px; overflow: hidden;
      box-shadow: 0 12px 40px rgba(0,0,0,.22);
      transition: opacity .2s, transform .2s;
    }
    #brhs-panel.hidden { opacity: 0; transform: translateY(16px) scale(.97); pointer-events: none; }
    #brhs-panel iframe { width: 100%; height: 100%; border: none; display: block; }
    @media (max-width: 480px) {
      #brhs-panel { width: calc(100vw - 16px); right: 8px; bottom: 80px; }
    }
  `;
  document.head.appendChild(style);

  // ── FAB button ───────────────────────────────────────────────────────────────
  const root = document.createElement('div');
  root.id = 'brhs-chat-root';
  root.innerHTML = `
    <button id="brhs-fab" aria-label="Open BRHS chat assistant" title="Ask BRHS Assistant">
      <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>
      <span id="brhs-badge">1</span>
    </button>
    <div id="brhs-panel" class="hidden">
      <iframe id="brhs-iframe" src="${apiBase}/static/widget.html" title="BRHS Assistant"
        allow="clipboard-write" loading="lazy"></iframe>
    </div>`;
  document.body.appendChild(root);

  // Pass the API base into the iframe once it loads
  const iframe = document.getElementById('brhs-iframe');
  iframe.addEventListener('load', () => {
    try {
      iframe.contentWindow.BRHS_API_BASE = apiBase;
    } catch (_) {}
  });

  // ── Toggle logic ─────────────────────────────────────────────────────────────
  let open = false;
  const fab   = document.getElementById('brhs-fab');
  const panel = document.getElementById('brhs-panel');
  const badge = document.getElementById('brhs-badge');
  let unread  = false;

  // Show badge after 3 s if user hasn't opened yet
  setTimeout(() => {
    if (!open) { badge.style.display = 'flex'; unread = true; }
  }, 3000);

  fab.addEventListener('click', () => {
    open = !open;
    panel.classList.toggle('hidden', !open);
    if (open && unread) { badge.style.display = 'none'; unread = false; }
    fab.setAttribute('aria-expanded', open);
    fab.innerHTML = open
      ? `<svg viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>`
      : `<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>`;
  });

  // Close on outside click
  document.addEventListener('click', e => {
    if (open && !root.contains(e.target)) {
      open = false;
      panel.classList.add('hidden');
      fab.setAttribute('aria-expanded', false);
      fab.innerHTML = `<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>`;
    }
  });
})();
