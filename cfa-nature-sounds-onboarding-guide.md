# 🌿 Implementing Nature Sounds for Calming Onboarding

## Overview
Enhance the CFA platform's onboarding experience with immersive nature sounds to foster a calming, culturally resonant atmosphere. This feature centers community voices by allowing indigenous knowledge holders to feel welcomed and grounded. Drawing from our vision of digital sovereignty and inclusivity, we'll integrate subtle audio cues during user entry points, experimenting with sounds like gentle rain, forest whispers, or ocean waves to align with diverse traditions.

This guide provides detailed, step-by-step instructions for backend preparation (Flask), frontend integration (HTML/CSS/JS), and testing. Assumes familiarity with the existing setup from [README.md](README.md). Includes fallback to free online CC0/public domain sounds if local files fail or are not preloaded.

## 🎯 Features
- **Dynamic Sound Selection**: Users can toggle or select from a library of nature sounds during onboarding.
- **Fallback to Online Sounds**: If local audio fails (error or missing), seamlessly switch to free internet-hosted alternatives (CC0/public domain).
- **Seamless Playback**: Auto-play on load, with pause/resume controls for accessibility.
- **Community-Driven Customization**: Future-proof for uploading user-suggested audio tied to cultural contexts.
- **Performance Optimized**: Lightweight files (< 1MB); fallbacks are direct MP3s for quick load.
- **Analytics Integration**: Track engagement and fallback usage to iterate on resonant sounds (e.g., via optional Google Analytics or custom logs).
- **Error Handling**: Graceful degradation if audio is blocked or unsupported.

## 🛠 Prerequisites
- Python 3.x with Flask (from `requirements.txt`).
- Basic JS knowledge for frontend.
- Local audio files: Download free CC0 sounds (e.g., from Freesound.org or OpenGameArt.org) – place rain.mp3, forest.mp3, waves.mp3 in `/static/audio/`.
- Fallback URLs (pre-configured; all CC0/public domain):
  - Rain: https://www.soundjay.com/nature/sounds/rain-light-1.mp3 (approx. 1min loopable)
  - Forest: https://opengameart.org/sites/default/files/Forest_Ambience.mp3 (CC0, 1min+)
  - Waves: https://www.oberton.org/wp-content/uploads/190718-LV-Kolka-waves-night-CC0.mp3 (night waves, loopable)

## 🚀 Setup Instructions

### 1. Backend Preparation (Flask)
Update the Flask app to serve audio files statically and expose fallback config.

- **Add Route for Audio Serving** (in `app.py`):
  ```python
  from flask import Flask, send_from_directory, jsonify

  app = Flask(__name__)

  @app.route('/audio/<path:filename>')
  def serve_audio(filename):
      return send_from_directory('static/audio', filename)

  @app.route('/config/audio')
  def audio_config():
      return jsonify({
          'fallbacks': {
              'rain.mp3': 'https://www.soundjay.com/nature/sounds/rain-light-1.mp3',
              'forest.mp3': 'https://opengameart.org/sites/default/files/Forest_Ambience.mp3',
              'waves.mp3': 'https://www.oberton.org/wp-content/uploads/190718-LV-Kolka-waves-night-CC0.mp3'
          }
      })
  ```

- **Environment Config** (in `.env` or `config.py`):
  ```
  AUDIO_ENABLED=True
  DEFAULT_SOUND=rain.mp3
  SOUND_VOLUME=0.3
  USE_FALLBACKS=True  # Enable online fallbacks if True
  ```

- **Install Dependencies** (optional for processing):
  ```bash
  pip install pydub  # For sound trimming/compression if needed
  ```

### 2. Frontend Integration (HTML/JS)
Embed in onboarding page (e.g., `templates/onboarding.html`).

- **Update HTML Structure**:
  ```html
  <!DOCTYPE html>
  <html lang="en">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>CFA Onboarding</title>
      <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  </head>
  <body>
      <div id="onboarding-container" role="main">
          <h1 aria-label="Welcome to CFA Gateway">Welcome to CFA Gateway</h1>
          <!-- Arch symbolism: Add your gateway visual here -->
          <audio id="natureSound" preload="metadata" loop aria-label="Nature sound background">
              <source id="audioSource" type="audio/mpeg">
              Your browser does not support audio. Fallback to silence.
          </audio>
          <div class="sound-controls" role="group" aria-label="Nature sound controls">
              <button id="playPause" aria-label="Toggle nature sound" aria-pressed="false">Pause Nature</button>
              <label for="soundSelect">Select Sound:</label>
              <select id="soundSelect" aria-describedby="sound-desc">
                  <option value="rain.mp3">Gentle Rain</option>
                  <option value="forest.mp3">Forest Whispers</option>
                  <option value="waves.mp3">Ocean Waves</option>
              </select>
              <span id="status" aria-live="polite"></span>
          </div>
          <p id="sound-desc" class="sr-only">Choose a calming nature sound for onboarding.</p>
      </div>
      <script src="{{ url_for('static', filename='js/onboarding.js') }}"></script>
  </body>
  </html>
  ```

- **CSS Styling** (in `static/css/style.css`):
  ```css
  /* Calming theme with accessibility */
  #onboarding-container {
      text-align: center;
      background: linear-gradient(to bottom, #e0f7fa, #b2dfdb);
      padding: 2rem;
      font-family: 'Arial', sans-serif;
      min-height: 100vh;
  }

  .sound-controls {
      margin-top: 1rem;
      display: flex;
      justify-content: center;
      gap: 1rem;
      align-items: center;
  }

  button, select, label {
      padding: 0.5rem 1rem;
      border: 1px solid #4caf50;
      border-radius: 4px;
      background: #e8f5e8;
      cursor: pointer;
      font-size: 1rem;
  }

  button:hover, select:hover {
      background: #c8e6c9;
  }

  button:focus, select:focus {
      outline: 2px solid #4caf50;
      outline-offset: 2px;
  }

  /* High contrast mode */
  @media (prefers-contrast: high) {
      button, select { 
          border-color: #000; 
          background: #fff; 
          color: #000;
      }
  }

  /* Screen reader only */
  .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
  }

  #status {
      font-size: 0.875rem;
      color: #2e7d32;
  }
  ```

- **JavaScript Logic** (in `static/js/onboarding.js`): Professional, with error handling, fallbacks, and accessibility updates.
  ```javascript
  /**
   * CFA Onboarding Nature Sounds Module
   * Handles audio playback with local/fallback sources, user controls, and error handling.
   * @version 1.1 - Added fallbacks and improved accessibility
   */

  (function() {
      'use strict';

      // DOM elements
      const audio = document.getElementById('natureSound');
      const source = document.getElementById('audioSource');
      const playPauseBtn = document.getElementById('playPause');
      const soundSelect = document.getElementById('soundSelect');
      const status = document.getElementById('status');

      // Config (fetch from backend)
      let config = {
          enabled: true,  // {{ AUDIO_ENABLED | tojson }} - Render via Jinja
          defaultSound: 'rain.mp3',
          volume: 0.3,
          useFallbacks: true
      };

      // Fetch fallback config asynchronously
      async function loadFallbacks() {
          try {
              const response = await fetch('/config/audio');
              const data = await response.json();
              config.fallbacks = data.fallbacks;
          } catch (e) {
              console.warn('Fallback config load failed:', e);
              // Hardcoded defaults as last resort
              config.fallbacks = {
                  'rain.mp3': 'https://www.soundjay.com/nature/sounds/rain-light-1.mp3',
                  'forest.mp3': 'https://opengameart.org/sites/default/files/Forest_Ambience.mp3',
                  'waves.mp3': 'https://www.oberton.org/wp-content/uploads/190718-LV-Kolka-waves-night-CC0.mp3'
              };
          }
      }

      // Update status for screen readers
      function updateStatus(message, isError = false) {
          status.textContent = message;
          status.className = isError ? 'error' : '';
          // Trigger live region
          status.setAttribute('aria-live', 'polite');
      }

      // Load audio source with fallback
      async function loadAudio(soundFile) {
          const localSrc = `/audio/${soundFile}`;
          const fallbackSrc = config.fallbacks[soundFile];

          // Try local first
          source.src = localSrc;
          audio.load();

          audio.addEventListener('error', async (e) => {
              console.warn('Local audio failed:', e);
              if (config.useFallbacks && fallbackSrc) {
                  updateStatus(`Switching to online ${soundFile}...`);
                  source.src = fallbackSrc;
                  audio.load();
                  try {
                      await audio.play();
                      updateStatus(`Playing online ${soundFile} for calm onboarding.`);
                  } catch (playErr) {
                      updateStatus('Audio unavailable; continuing silently.', true);
                  }
              } else {
                  updateStatus('Local audio unavailable; continuing silently.', true);
              }
          }, { once: true });

          audio.addEventListener('loadstart', () => updateStatus('Loading sound...'));
          audio.addEventListener('canplay', () => updateStatus(`Ready: ${soundFile}`));
      }

      // Initialize on DOM ready
      if ('loading' === document.readyState) {
          document.addEventListener('DOMContentLoaded', init);
      } else {
          init();
      }

      async function init() {
          if (!config.enabled) return;

          await loadFallbacks();

          audio.volume = config.volume;
          await loadAudio(config.defaultSound);
          await audio.play().catch(e => {
              console.log('Autoplay prevented; requires user gesture:', e);
              playPauseBtn.textContent = 'Play Nature';
              playPauseBtn.setAttribute('aria-pressed', 'false');
          });

          // Play/Pause toggle with accessibility
          playPauseBtn.addEventListener('click', async () => {
              const isPaused = audio.paused;
              try {
                  if (isPaused) {
                      await audio.play();
                      playPauseBtn.textContent = 'Pause Nature';
                      playPauseBtn.setAttribute('aria-pressed', 'true');
                  } else {
                      audio.pause();
                      playPauseBtn.textContent = 'Play Nature';
                      playPauseBtn.setAttribute('aria-pressed', 'false');
                  }
                  updateStatus(isPaused ? 'Nature sound playing' : 'Nature sound paused');
              } catch (e) {
                  updateStatus('Playback error occurred.', true);
              }
          });

          // Sound selection change
          soundSelect.addEventListener('change', async (e) => {
              const newSound = e.target.value;
              await loadAudio(newSound);
              await audio.play();
              updateStatus(`Switched to ${newSound}`);
              // Optional analytics log
              console.log('Sound selected:', newSound);  // Replace with fetch to /log-sound
          });

          // Auto-pause on page unload
          window.addEventListener('beforeunload', () => audio.pause());

          // Keyboard accessibility
          [playPauseBtn, soundSelect].forEach(el => {
              el.addEventListener('keydown', (e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      el.click();
                  }
              });
          });
      }
  })();
  ```

### 3. Route Integration (Flask)
Link to onboarding in main app:
```python
from flask import render_template

@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html', 
                          AUDIO_ENABLED=os.getenv('AUDIO_ENABLED', 'True') == 'True',
                          DEFAULT_SOUND=os.getenv('DEFAULT_SOUND', 'rain.mp3'),
                          SOUND_VOLUME=float(os.getenv('SOUND_VOLUME', 0.3)))
```
- Call this route on first-time user login or app entry. Use `os` import for env vars.

## 🧪 Testing & Experimentation
- **Local Testing**:
  1. Run `flask run`.
  2. Visit `http://127.0.0.1:5000/onboarding`.
  3. Verify local audio plays; simulate error by removing file – check fallback loads.
  4. Test controls, status updates, keyboard nav on mobile/desktop.

- **Cross-Browser Compatibility**:
  - Chrome/Edge/Firefox: Full support with muted autoplay fallback.
  - Safari: User gesture for play.
  - Use `audio.canPlayType('audio/mpeg')` for MP3 check if needed.

- **User Resonance Testing**:
  - Deploy to staging (e.g., Railway).
  - A/B test: Track fallback usage via logs (add `/log-sound` endpoint).
  - Feedback form: "How did the sound make you feel? (Calm/Neutral/Distracting/Fallback used?)"

- **Accessibility & Security Checks**:
  - ARIA: Controls announced; test with NVDA/VoiceOver.
  - Mute default; no CORS issues on fallbacks (public URLs).
  - Cultural: Consult elders; ensure sounds are neutral/positive.

## 🔍 Potential Enhancements
- **Volume Fade**: Use Web Audio API for smooth transitions.
- **Offline Support**: Cache fallbacks via Service Worker.
- **ML Suggestions**: Suggest based on user prefs (scikit-learn backend).
- **DB Logging**: PostgreSQL for prefs: `INSERT INTO sound_logs (user_id, sound, fallback_used, timestamp) VALUES (?, ?, ?, ?)`.

## 🤝 Contribution
Follow [contribution workflow](README.md#🤝-community--contribution). PRs with `#nature-sounds`. Reference community input; ethically source all audio.

## 📄 License
MIT – Adapt freely with attribution. #community #indigenous #calm #onboarding

---

*Like, Share & Join the movement! 🌍❤️*
