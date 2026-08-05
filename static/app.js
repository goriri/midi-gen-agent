let selectedFormat = 'all';
let currentCompositionData = null;

const samplePrompts = {
  1: "生成一段曲风悠扬的轻音乐，简单清新",
  2: "曲风：清新日系轻音乐，治愈民谣，轻柔钢琴为主，搭配分解木吉他、微弱弦乐垫音\n场景：晴空万里，午后草坪，微风舒缓，氛围松弛慵懒，宁静和谐，无伤感，温暖明亮\n速度：72BPM，4/4拍，C大调，旋律平缓起伏不大，节奏舒展\n配器：原声钢琴（主旋律）、尼龙木吉他分解和弦、极淡小提琴长音铺垫、轻微风铃点缀\n要求：旋律流畅治愈，音量柔和，不要鼓点；输出完整曲谱，导出文本格式，调式规范，音符排布适合五线谱展示，时长60秒",
  3: "Compose a cheerful upbeat pop melody in G Major at 120 BPM with acoustic grand piano, acoustic guitar steel, and electric bass line. Output as binary WAV file.",
  4: "Generate a soothing ballad in A minor, 60 BPM, 4/4 time signature, with acoustic grand piano, cello, and flute. Duration 30 seconds."
};

function fillPrompt(id) {
  if (samplePrompts[id]) {
    document.getElementById('promptInput').value = samplePrompts[id];
  }
}

function setFormat(fmt) {
  selectedFormat = fmt;
  document.querySelectorAll('.format-btn').forEach(btn => btn.classList.remove('active'));
  if (fmt === 'all') document.getElementById('fmtAll').classList.add('active');
  if (fmt === 'composition') document.getElementById('fmtComp').classList.add('active');
  if (fmt === 'wav') document.getElementById('fmtWav').classList.add('active');
}

async function handleGenerate() {
  const promptInput = document.getElementById('promptInput').value.trim();
  if (!promptInput) {
    alert('Please enter a music generation prompt!');
    return;
  }

  setLoading(true);
  document.getElementById('genStatus').innerText = 'Generating music...';

  try {
    const resp = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: promptInput, format: selectedFormat })
    });

    const data = await resp.json();
    if (data.status === 'success') {
      displayResult(data.generation);
      document.getElementById('genStatus').innerText = 'Done!';
      fetchHistory();
    } else {
      alert('Error: ' + (data.detail || 'Failed to generate music'));
      document.getElementById('genStatus').innerText = 'Error';
    }
  } catch (err) {
    console.error(err);
    alert('Network error generating music.');
    document.getElementById('genStatus').innerText = 'Failed';
  } finally {
    setLoading(false);
  }
}

function displayResult(gen) {
  document.getElementById('resultEmpty').classList.add('hidden');
  document.getElementById('resultContainer').classList.remove('hidden');

  // WAV audio section
  if (gen.wav_url) {
    document.getElementById('audioSection').classList.remove('hidden');
    const player = document.getElementById('audioPlayer');
    player.src = gen.wav_url;
    player.load();
    document.getElementById('wavDownloadLink').href = gen.wav_url;
    
    if (gen.midi_url) {
      document.getElementById('midiDownloadLink').href = gen.midi_url;
      document.getElementById('midiDownloadLink').classList.remove('hidden');
    } else {
      document.getElementById('midiDownloadLink').classList.add('hidden');
    }
  } else {
    document.getElementById('audioSection').classList.add('hidden');
  }

  // JSON Composition section
  if (gen.composition) {
    currentCompositionData = gen.composition;
    document.getElementById('jsonSection').classList.remove('hidden');
    document.getElementById('jsonViewer').textContent = JSON.stringify(gen.composition, null, 2);
  } else {
    currentCompositionData = null;
    document.getElementById('jsonSection').classList.add('hidden');
  }
}

async function handleConvertCurrent() {
  if (!currentCompositionData) {
    alert('No composition data available to convert.');
    return;
  }

  document.getElementById('genStatus').innerText = 'Converting Text to WAV...';
  try {
    const resp = await fetch('/api/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ composition: currentCompositionData })
    });

    const data = await resp.json();
    if (data.status === 'success') {
      displayResult(data.generation);
      document.getElementById('genStatus').innerText = 'Converted to WAV successfully!';
      fetchHistory();
    } else {
      alert('Conversion failed: ' + (data.detail || 'Unknown error'));
    }
  } catch (err) {
    console.error(err);
    alert('Network error during conversion.');
  }
}

async function fetchHistory() {
  try {
    const resp = await fetch('/api/generations');
    const data = await resp.json();
    if (data.status === 'success') {
      renderHistory(data.generations);
    }
  } catch (err) {
    console.error('Failed to load history:', err);
  }
}

function renderHistory(generations) {
  const container = document.getElementById('historyList');
  if (!generations || generations.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.9rem;">No previous generations stored.</p>';
    return;
  }

  container.innerHTML = generations.map(item => `
    <div class="history-item">
      <div class="history-header">
        <span style="color: var(--accent-cyan); font-weight: 700; font-size: 0.85rem;">ID: #${item.id}</span>
        <span class="history-meta">${item.created_at || ''}</span>
      </div>
      <div class="history-prompt">${escapeHtml(item.prompt)}</div>
      
      ${item.wav_url ? `
        <div style="margin-top: 0.5rem;">
          <audio controls style="height: 36px; width: 100%;">
            <source src="${item.wav_url}" type="audio/wav">
          </audio>
        </div>
      ` : ''}

      <div class="action-bar">
        ${item.wav_url ? `<a href="${item.wav_url}" download class="btn-secondary" style="text-decoration:none; font-size: 0.8rem;">📥 WAV</a>` : ''}
        ${item.midi_url ? `<a href="${item.midi_url}" download class="btn-secondary" style="text-decoration:none; font-size: 0.8rem;">📥 MIDI</a>` : ''}
        ${item.composition ? `<button class="btn-secondary" style="font-size: 0.8rem;" onclick='loadHistoryComp(${JSON.stringify(item.composition).replace(/'/g, "&apos;")})'>📜 View Text JSON</button>` : ''}
      </div>
    </div>
  `).join('');
}

function loadHistoryComp(compData) {
  currentCompositionData = compData;
  document.getElementById('resultEmpty').classList.add('hidden');
  document.getElementById('resultContainer').classList.remove('hidden');
  document.getElementById('jsonSection').classList.remove('hidden');
  document.getElementById('jsonViewer').textContent = JSON.stringify(compData, null, 2);
  window.scrollTo({ top: 300, behavior: 'smooth' });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function setLoading(isLoading) {
  const btnText = document.getElementById('btnText');
  const btnLoader = document.getElementById('btnLoader');
  const btn = document.getElementById('generateBtn');

  if (isLoading) {
    btnText.innerText = 'Generating...';
    btnLoader.classList.remove('hidden');
    btn.disabled = true;
  } else {
    btnText.innerText = '✨ Generate Music';
    btnLoader.classList.add('hidden');
    btn.disabled = false;
  }
}

// Initial fetch on load
window.addEventListener('DOMContentLoaded', fetchHistory);
