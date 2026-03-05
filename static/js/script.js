let voiceEnabled = true;
let isListening  = false;

function sendChip(text) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('userInput').value = text;
  sendMessage();
}

async function sendMessage() {
  const input   = document.getElementById('userInput');
  const sendBtn = document.getElementById('sendBtn');
  const message = input.value.trim();
  if (!message) return;

  const wc = document.getElementById('welcomeCard');
  if (wc) wc.style.display = 'none';

  input.value      = '';
  input.disabled   = true;
  sendBtn.disabled = true;

  appendMessage('user', message, getTime(), null, null);
  const typingId = showTyping();

  try {
    const res  = await fetch('/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message })
    });
    const data = await res.json();
    removeTyping(typingId);

    const reply  = data.response || 'Sorry, something went wrong!';
    const source = data.source   || 'intent';
    const image  = data.image    || null;

    appendMessage('bot', reply, getTime(), source, image);
    if (voiceEnabled) speakText(reply);
    loadStats();
    loadHistory();

  } catch (err) {
    removeTyping(typingId);
    appendMessage('bot', 'Connection error. Make sure Flask is running!', getTime(), 'system', null);
  }

  input.disabled   = false;
  sendBtn.disabled = false;
  input.focus();
  scrollBottom();
}

function appendMessage(sender, text, time, source, image) {
  const body = document.getElementById('chatBody');
  const div  = document.createElement('div');
  div.className = `message ${sender === 'bot' ? 'bot-msg' : 'user-msg'}`;

  if (sender === 'bot') {
    // ── No badges shown at all ──
    let imageHtml = '';
    if (image) {
      imageHtml = `
        <div class="image-card">
          <img src="${image.url}" alt="${image.label}"
               onerror="this.parentElement.style.display='none'"/>
          <div class="image-card-label">🖼️ ${image.label}</div>
        </div>`;
    }

    div.innerHTML = `
      <div class="msg-avatar">
        <img src="/static/images/nscet_logo.png" alt="NS"
             onerror="this.style.display='none';this.nextSibling.style.display='flex'"/>
        <span style="display:none;width:100%;height:100%;align-items:center;
                     justify-content:center;font-size:12px;font-weight:800;
                     color:#1e4fc2;background:white;border-radius:8px">NS</span>
      </div>
      <div class="msg-content">
        <div class="msg-bubble">${formatText(text)}</div>
        ${imageHtml}
        <div class="msg-time">${time}</div>
      </div>`;
  } else {
    div.innerHTML = `
      <div class="msg-content">
        <div class="msg-bubble">${escapeHtml(text)}</div>
        <div class="msg-time">${time}</div>
      </div>`;
  }

  body.appendChild(div);
  scrollBottom();
}

function showTyping() {
  const id   = 'typing-' + Date.now();
  const body = document.getElementById('chatBody');
  const div  = document.createElement('div');
  div.id        = id;
  div.className = 'message bot-msg typing-bubble';
  div.innerHTML = `
    <div class="msg-avatar">
      <img src="/static/images/nscet_logo.png" alt="NS"
           onerror="this.style.display='none'"/>
    </div>
    <div class="msg-content">
      <div class="msg-bubble">
        <div class="dots"><span></span><span></span><span></span></div>
      </div>
    </div>`;
  body.appendChild(div);
  scrollBottom();
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function clearChat() {
  document.getElementById('chatBody').innerHTML = `
    <div class="welcome-card" id="welcomeCard">
      <div class="welcome-icon">
        <img src="/static/images/nscet_logo.png" alt="NSCET"
             onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"/>
        <div class="welcome-fallback">🎓</div>
      </div>
      <h3>Vanakkam! Welcome to NSCET</h3>
      <p>Ask me anything about NSCET or any general question!</p>
      <div class="welcome-chips">
        <button class="chip" onclick="sendChip('Tell me about NSCET')">🏛️ About College</button>
        <button class="chip" onclick="sendChip('what courses are available')">📚 Courses</button>
        <button class="chip" onclick="sendChip('how to get admission')">📝 Admission</button>
        <button class="chip" onclick="sendChip('placement record')">💼 Placements</button>
      </div>
    </div>`;
}

function speakText(text) {
  if (!voiceEnabled || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();

  const clean = text
    .replace(/[*_`#•]/g, '')
    .replace(/:/g, ',')
    .replace(/https?:\/\/\S+/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  if (!clean) return;

  const sentences = clean.match(/[^.!?]+[.!?]*/g) || [clean];
  let index = 0;

  function speakNext() {
    if (index >= sentences.length || !voiceEnabled) return;

    const sentence = sentences[index].trim();
    if (!sentence) { index++; speakNext(); return; }

    const utt = new SpeechSynthesisUtterance(sentence);
    utt.lang   = 'en-IN';
    utt.rate   = 0.88;
    utt.pitch  = 1.2;
    utt.volume = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const female = voices.find(v =>
      (v.name.includes('Zira') || v.name.includes('Heera') ||
       v.name.includes('Female') || v.name.includes('female')) &&
      v.lang.startsWith('en')
    ) || voices.find(v => v.lang === 'en-IN')
      || voices.find(v => v.lang.startsWith('en'));

    if (female) utt.voice = female;

    utt.onend   = () => { index++; speakNext(); };
    utt.onerror = () => { index++; speakNext(); };

    window.speechSynthesis.speak(utt);
  }

  const voices = window.speechSynthesis.getVoices();
  if (voices.length === 0) {
    window.speechSynthesis.onvoiceschanged = () => speakNext();
  } else {
    speakNext();
  }
}

async function startVoiceInput() {
  const voiceBtn = document.getElementById('voiceBtn');
  const input    = document.getElementById('userInput');

  if (isListening) {
    isListening = false;
    voiceBtn.textContent = '🎙️';
    voiceBtn.classList.remove('listening');
    input.placeholder = 'Ask about NSCET or anything else...';
    return;
  }

  isListening = true;
  voiceBtn.textContent = '🔴';
  voiceBtn.classList.add('listening');
  input.value       = '';
  input.placeholder = '🎙️ Recording for 7 seconds... speak now!';

  try {
    const res  = await fetch('/voice', { method: 'POST' });
    const data = await res.json();

    if (data.status === 'ok' && data.text) {
      input.value = data.text;
      input.placeholder = 'Ask about NSCET or anything else...';
      isListening = false;
      voiceBtn.textContent = '🎙️';
      voiceBtn.classList.remove('listening');
      setTimeout(() => sendMessage(), 500);
    } else {
      input.placeholder = '⚠️ ' + (data.message || 'Could not hear. Try again!');
      setTimeout(() => { input.placeholder = 'Ask about NSCET or anything else...'; }, 3000);
      isListening = false;
      voiceBtn.textContent = '🎙️';
      voiceBtn.classList.remove('listening');
    }
  } catch (err) {
    input.placeholder = '⚠️ Voice error. Make sure Flask is running!';
    setTimeout(() => { input.placeholder = 'Ask about NSCET or anything else...'; }, 3000);
    isListening = false;
    voiceBtn.textContent = '🎙️';
    voiceBtn.classList.remove('listening');
  }
}

async function loadStats() {
  try {
    const d = await (await fetch('/stats')).json();
    const t = document.getElementById('statTotal');
    const g = document.getElementById('statGemini');
    const i = document.getElementById('statIntent');
    if (t) t.textContent = d.total;
    if (g) g.textContent = d.gemini;
    if (i) i.textContent = d.intent;
  } catch {}
}

async function loadHistory() {
  const listEl = document.getElementById('historyList');
  if (!listEl) return;
  try {
    const rows = await (await fetch('/history')).json();
    if (!rows.length) {
      listEl.innerHTML = '<p class="history-empty">No history yet!</p>';
      return;
    }
    listEl.innerHTML = rows.slice(0, 15).map(r => `
      <div class="history-item"
        onclick="document.getElementById('userInput').value='${esc(r.user_input)}';
                 document.getElementById('userInput').focus()">
        <div class="history-q">💬 ${esc(r.user_input)}</div>
        <div class="history-a">${esc(r.bot_response.substring(0, 55))}...</div>
      </div>`).join('');
  } catch {
    listEl.innerHTML = '<p class="history-empty" style="color:#ef4444">Failed to load</p>';
  }
}

function getTime() {
  return new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

function formatText(t) {
  return t
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

function escapeHtml(t) {
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;')
          .replace(/>/g,'&gt;').replace(/\n/g,'<br>');
}

function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function scrollBottom() {
  const body = document.getElementById('chatBody');
  if (body) body.scrollTo({ top: body.scrollHeight, behavior: 'smooth' });
}

document.addEventListener('DOMContentLoaded', function () {
  const input    = document.getElementById('userInput');
  const voiceBtn = document.getElementById('voiceBtn');
  const speakBtn = document.getElementById('speakToggle');
  const histBtn  = document.getElementById('historyToggle');
  const clearBtn = document.getElementById('clearHistoryBtn');

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  if (voiceBtn) voiceBtn.addEventListener('click', startVoiceInput);

  if (speakBtn) {
    speakBtn.addEventListener('click', function () {
      voiceEnabled = !voiceEnabled;
      this.textContent = voiceEnabled ? '🔊' : '🔇';
      this.style.background = voiceEnabled ? '' : 'rgba(239,68,68,0.2)';
    });
  }

  if (histBtn) {
    histBtn.addEventListener('click', () => {
      document.getElementById('sidebar').classList.toggle('sidebar-open');
      loadHistory();
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', async () => {
      if (!confirm('Clear all chat history?')) return;
      await fetch('/clear-history', { method: 'POST' });
      loadHistory();
      loadStats();
    });
  }

  input.focus();
  loadStats();
  loadHistory();
});