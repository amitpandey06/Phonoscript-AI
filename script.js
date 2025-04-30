async function summarizeText() {
    const text = document.getElementById('textResult').innerText;
    const response = await fetch('/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text }),
    });
    const result = await response.json();
    document.getElementById('textResult').innerText = result.summary || result.error;
}

async function correctGrammar() {
    const text = document.getElementById('textResult').innerText;
    const response = await fetch('/correct-grammar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text }),
    });
    const result = await response.json();
    document.getElementById('textResult').innerText = result.corrected_text || result.error;
}
// In your existing script
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
    dropZone.style.animation = "pulseBorder 1.5s infinite"; // Add this linex
  });
  
  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
    dropZone.style.animation = ""; // Reset animation
  });
  // Initialize Waveform with animation
const wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: 'rgba(255, 255, 255, 0.2)',
    progressColor: 'var(--primary)',
    cursorColor: 'transparent',
    height: 100,
    responsive: true,
    normalize: true,
    interact: false, // Disable seeking
  });
  
  // Add progress animation during recording
  let progressInterval;
  document.getElementById('recordButton').addEventListener('click', () => {
    progressInterval = setInterval(() => {
      const progress = Math.random() * 100; // Simulate processing
      wavesurfer.seekTo(progress / 100);
    }, 100);
  });
  
  document.getElementById('stopButton').addEventListener('click', () => {
    clearInterval(progressInterval);
  });
  // In handleImageUpload/voice processing functions
async function handleImageUpload(file) {
    // Show loading
    document.querySelector('.processing-overlay').style.display = 'flex';
    
    // Process file...
  
    // Hide loading
    document.querySelector('.processing-overlay').style.display = 'none';
    
    // Animate result
    document.getElementById('textResult').style.animation = 'fadeIn 0.5s ease';
  }