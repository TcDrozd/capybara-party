"use strict";


let isGenerating = false;

// New: refreshAndReload hard reloads the page after generating new content
async function refreshAndReload() {
  if (isGenerating) return;
  const btn = document.getElementById('refresh-btn');
  const overlay = document.getElementById('loading-overlay');
  const loadingText = overlay ? overlay.querySelector('.loading-text') : null;

  isGenerating = true;
  if (btn) { btn.disabled = true; btn.textContent = '🔄 Generating...'; }
  if (overlay) { overlay.style.display = 'flex'; if (loadingText) loadingText.textContent = 'Waking the capybaras…'; }

  try {
    const res = await fetch('/api/refresh', { method: 'POST', headers: { 'Content-Type': 'application/json' }, cache: 'no-store' });
    if (!res.ok) throw new Error('Failed to refresh content');
    // Hard reload so the image + counter are always in sync
    window.location.reload();
  } catch (e) {
    console.error('Refresh failed:', e);
    if (loadingText) loadingText.textContent = '😔 Oops! The capybaras need a moment...';
    isGenerating = false;
    if (btn) { btn.disabled = false; btn.textContent = '🔄 Generate New'; }
    if (overlay) { setTimeout(() => { overlay.style.display = 'none'; }, 1500); }
  }
}

async function refreshContent() {
  if (isGenerating) return;

  const btn = document.getElementById('refresh-btn');
  const overlay = document.getElementById('loading-overlay');     // <— changed
  const loadingText = overlay ? overlay.querySelector('.loading-text') : null;
  const image = document.getElementById('capybara-image');
  const quote = document.getElementById('daily-quote');

  isGenerating = true;
  if (btn) {
    btn.disabled = true;
    btn.textContent = '🔄 Generating...';
  }
  if (overlay) {
    overlay.style.display = 'flex';  // <— show the overlay
    if (loadingText) loadingText.textContent = 'Waking the capybaras…';
  }

  try {
    const response = await fetch('/api/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store'
    });
    if (!response.ok) throw new Error('Failed to refresh content');

    const data = await response.json();

    if (data.quote && quote) quote.textContent = `"${data.quote}"`;

    if (data.image_filename && image) {
      const imageUrl = `/static/images/daily/${data.image_filename}?t=${Date.now()}`;
      const newImg = new Image();
      newImg.onload = function () {
        image.src = imageUrl;
        image.classList.add('fade-in');
        setTimeout(() => image.classList.remove('fade-in'), 400);
      };
      newImg.src = imageUrl;
    }

    if (loadingText) loadingText.textContent = '✨ New capybara wisdom generated!';

  } catch (err) {
    console.error('Refresh failed:', err);
    if (loadingText) loadingText.textContent = '😔 Oops! The capybaras need a moment...';
  } finally {
    isGenerating = false;
    if (btn) {
      btn.disabled = false;
      btn.textContent = '🔄 Generate New';
    }
    if (overlay) {
      setTimeout(() => { overlay.style.display = 'none'; }, 1500);
    }
  }
}

function shareContent() {
  const quoteEl = document.getElementById('daily-quote');
  const quote = quoteEl ? quoteEl.textContent || '' : '';
  const url = window.location.href;

  if (navigator.share) {
    navigator.share({ title: 'Capybara Party - Daily Zen', text: quote, url }).catch(() => {});
  } else {
    navigator.clipboard.writeText(`${quote} - ${url}`)
      .then(() => alert('Copied to clipboard! 📋'))
      .catch(() => alert('Visit: ' + url));
  }
}

async function checkStatus() {
  try {
    const response = await fetch('/api/status', { cache: 'no-store' });
    if (!response.ok) return;
    const data = await response.json();
    const statusEl = document.getElementById('status');
    if (!statusEl) return;
    const allOnline = data.a1111 && data.ollama && data.flask;
    statusEl.innerHTML = allOnline
      ? '<span class="status-dot status-online"></span>All systems zen'
      : '<span class="status-dot status-offline"></span>Some capybaras are napping';
  } catch (_) {}
}

document.addEventListener('DOMContentLoaded', () => {
  console.log('[capybara.js] loaded');
  const refreshBtn = document.getElementById('refresh-btn');
  if (refreshBtn) refreshBtn.addEventListener('click', refreshAndReload);
  const shareBtn = document.getElementById('share-btn');
  if (shareBtn) shareBtn.addEventListener('click', shareContent);

  const image = document.getElementById('capybara-image');
  if (image) {
    image.addEventListener('click', function () {
      this.style.transform = 'scale(0.95)';
      setTimeout(() => { this.style.transform = 'scale(1)'; }, 150);
    });
  }

  checkStatus();
  setInterval(checkStatus, 30000);

  // Expose for inline use
  window.capyRefresh = refreshAndReload;
});