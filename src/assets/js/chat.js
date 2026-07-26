// SAYHITOFIT — site assistant widget (injected on every page)
document.addEventListener('DOMContentLoaded', () => {
  const STORAGE_KEY = 'shf-chat';
  const GREETING = "Hi — I'm the SAYHITOFIT assistant. Ask me about the programs, the Body Analyzer, or training in general.";
  const STARTERS = [
    'Which program suits a beginner?',
    'What does the Body Analyzer do?',
    'Should I bulk or cut?'
  ];

  // ---------- markup ----------
  const root = document.createElement('div');
  root.className = 'chat-widget';
  root.innerHTML = `
    <button class="chat-fab" id="chat-fab" aria-expanded="false" aria-controls="chat-panel">
      <span class="chat-fab-label">Ask us</span>
    </button>
    <div class="chat-panel" id="chat-panel" role="dialog" aria-label="SAYHITOFIT assistant" hidden>
      <div class="chat-head">
        <div>
          <p class="chat-title">SAYHITOFIT assistant</p>
          <p class="chat-sub">Answers about programs and training</p>
        </div>
        <button class="chat-close" id="chat-close" aria-label="Close chat">&times;</button>
      </div>
      <div class="chat-log" id="chat-log" aria-live="polite"></div>
      <div class="chat-starters" id="chat-starters"></div>
      <form class="chat-form" id="chat-form">
        <label class="visually-hidden" for="chat-input">Your question</label>
        <input id="chat-input" type="text" autocomplete="off" maxlength="1000"
               placeholder="Ask a question…">
        <button type="submit" class="chat-send" id="chat-send" aria-label="Send">→</button>
      </form>
      <p class="chat-disclaimer">AI assistant — general guidance only, not medical advice.</p>
    </div>`;
  document.body.appendChild(root);

  const fab = root.querySelector('#chat-fab');
  const panel = root.querySelector('#chat-panel');
  const closeBtn = root.querySelector('#chat-close');
  const log = root.querySelector('#chat-log');
  const form = root.querySelector('#chat-form');
  const input = root.querySelector('#chat-input');
  const sendBtn = root.querySelector('#chat-send');
  const starterWrap = root.querySelector('#chat-starters');

  // ---------- state ----------
  let history = [];
  try {
    history = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '[]');
  } catch { history = []; }

  const save = () => {
    try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(history)); } catch {}
  };

  function addBubble(role, text, opts = {}) {
    const el = document.createElement('div');
    el.className = `chat-msg chat-${role}` + (opts.muted ? ' chat-muted' : '');
    el.textContent = text;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  function renderStarters() {
    starterWrap.innerHTML = '';
    if (history.length) return;                 // only on an empty conversation
    STARTERS.forEach(q => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'chat-starter';
      b.textContent = q;
      b.addEventListener('click', () => send(q));
      starterWrap.appendChild(b);
    });
  }

  function renderHistory() {
    log.innerHTML = '';
    addBubble('assistant', GREETING);
    history.forEach(m => addBubble(m.role, m.content));
    renderStarters();
  }

  // ---------- sending ----------
  let pending = false;

  async function send(text) {
    const message = text.trim();
    if (!message || pending) return;

    pending = true;
    input.value = '';
    sendBtn.disabled = true;
    history.push({ role: 'user', content: message });
    addBubble('user', message);
    save();
    renderStarters();

    const typing = addBubble('assistant', 'Typing…', { muted: true });

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: history.slice(-10) })
      });
      const data = await res.json();
      typing.remove();

      if (!res.ok) throw new Error(data.detail || 'Request failed');

      addBubble('assistant', data.reply);
      history.push({ role: 'assistant', content: data.reply });
      save();
    } catch (err) {
      typing.remove();
      addBubble('assistant', 'Something went wrong reaching the assistant. Please try again, or use the contact form.', { muted: true });
      console.error(err);
    } finally {
      pending = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  form.addEventListener('submit', e => {
    e.preventDefault();
    send(input.value);
  });

  // ---------- open / close ----------
  function openPanel() {
    panel.hidden = false;
    fab.setAttribute('aria-expanded', 'true');
    root.classList.add('open');
    input.focus();
    log.scrollTop = log.scrollHeight;
  }

  function closePanel() {
    panel.hidden = true;
    fab.setAttribute('aria-expanded', 'false');
    root.classList.remove('open');
    fab.focus();
  }

  fab.addEventListener('click', () => (panel.hidden ? openPanel() : closePanel()));
  closeBtn.addEventListener('click', closePanel);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !panel.hidden) closePanel();
  });

  renderHistory();
});
