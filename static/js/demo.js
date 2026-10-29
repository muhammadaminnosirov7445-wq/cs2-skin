(() => {
  'use strict';

  const csrfToken = () => {
    const cookie = document.cookie.split('; ').find((part) => part.startsWith('csrftoken='));
    return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : '';
  };

  const toast = (message, error = false) => {
    const stack = document.querySelector('[data-toast-stack]');
    if (!stack) return;
    const node = document.createElement('div');
    node.className = `toast${error ? ' error' : ''}`;
    node.textContent = message;
    stack.appendChild(node);
    window.setTimeout(() => node.remove(), 3600);
  };

  const formatDemoCredits = (value) => Number(value).toFixed(2).replace('.', ',');

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reducedMotion) document.documentElement.classList.add('reduced-motion');
  const authenticated = document.documentElement.dataset.authenticated === 'true';
  let animationsPreference = authenticated
    ? document.documentElement.dataset.animationsEnabled
    : localStorage.getItem('skinly-demo-animations');
  if (animationsPreference === 'false' || reducedMotion) {
    document.documentElement.setAttribute('data-animations-enabled', 'false');
  }

  // Audio effects synthesizer using Web Audio API
  const soundButton = document.querySelector('[data-sound-toggle]');
  const soundPreference = authenticated
    ? document.documentElement.dataset.soundEnabled === 'true'
    : localStorage.getItem('skinly-demo-sound') === 'true';
  if (soundButton) soundButton.setAttribute('aria-pressed', String(soundPreference));

  const isSoundEnabled = () => soundButton?.getAttribute('aria-pressed') === 'true';

  const playClickSound = (freq = 900) => {
    if (!isSoundEnabled() || !window.AudioContext) return;
    try {
      const audio = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audio.createOscillator();
      const gain = audio.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, audio.currentTime);
      gain.gain.setValueAtTime(0.04, audio.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(audio.destination);
      osc.start();
      osc.stop(audio.currentTime + 0.04);
      osc.onended = () => audio.close();
    } catch (e) {}
  };

  const playRouletteSpinSound = (duration = 5800) => {
    if (!isSoundEnabled()) return;
    let elapsed = 0;
    let delay = 45;
    const tick = () => {
      playClickSound(850 + Math.random() * 250);
      elapsed += delay;
      const progress = elapsed / duration;
      delay = 45 + Math.pow(progress, 3.2) * 550;
      if (elapsed < duration - 180) {
        window.setTimeout(tick, delay);
      }
    };
    tick();
  };

  const playWinChime = () => {
    if (!isSoundEnabled() || !window.AudioContext) return;
    try {
      const audio = new (window.AudioContext || window.webkitAudioContext)();
      [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {
        const osc = audio.createOscillator();
        const gain = audio.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        const start = audio.currentTime + idx * 0.09;
        gain.gain.setValueAtTime(0.06, start);
        gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.32);
        osc.connect(gain);
        gain.connect(audio.destination);
        osc.start(start);
        osc.stop(start + 0.32);
      });
      setTimeout(() => audio.close(), 1200);
    } catch (e) {}
  };

  const playCaseUnlockSound = () => {
    if (!isSoundEnabled() || !window.AudioContext) return;
    try {
      const audio = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audio.createOscillator();
      const gain = audio.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(160, audio.currentTime);
      osc.frequency.exponentialRampToValueAtTime(360, audio.currentTime + 0.16);
      gain.gain.setValueAtTime(0.06, audio.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + 0.2);
      osc.connect(gain);
      gain.connect(audio.destination);
      osc.start();
      osc.stop(audio.currentTime + 0.2);
      setTimeout(() => audio.close(), 300);
    } catch (e) {}
  };

  soundButton?.addEventListener('click', () => {
    const enabled = soundButton.getAttribute('aria-pressed') !== 'true';
    soundButton.setAttribute('aria-pressed', String(enabled));
    localStorage.setItem('skinly-demo-sound', String(enabled));
    if (enabled) playClickSound(1000);
    toast(`Demo tovushi ${enabled ? 'yoqildi' : 'o‘chirildi'}.`);
  });

  const sidebar = document.getElementById('demo-sidebar');
  document.querySelector('[data-menu-toggle]')?.addEventListener('click', (event) => {
    const open = sidebar?.classList.toggle('is-open') || false;
    event.currentTarget.setAttribute('aria-expanded', String(open));
  });

  // 3D Card Hover & Pointer Tracking
  if (!reducedMotion && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.querySelectorAll('[data-case-card]').forEach((card) => {
      card.addEventListener('pointermove', (event) => {
        const bounds = card.getBoundingClientRect();
        const x = (event.clientX - bounds.left) / bounds.width;
        const y = (event.clientY - bounds.top) / bounds.height;
        card.style.setProperty('--pointer-x', `${(x * 100).toFixed(1)}%`);
        card.style.setProperty('--pointer-y', `${(y * 100).toFixed(1)}%`);
        card.style.setProperty('--tilt-x', `${((x - 0.5) * 6).toFixed(2)}deg`);
        card.style.setProperty('--tilt-y', `${((0.5 - y) * 6).toFixed(2)}deg`);
        card.style.setProperty('--art-x', `${((x - 0.5) * 10).toFixed(1)}px`);
        card.style.setProperty('--art-y', `${((y - 0.5) * 10).toFixed(1)}px`);
      });
      card.addEventListener('pointerleave', () => {
        ['--pointer-x', '--pointer-y', '--tilt-x', '--tilt-y', '--art-x', '--art-y']
          .forEach((property) => card.style.removeProperty(property));
      });
    });
  }

  const generateUUID = () => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      try { return crypto.randomUUID(); } catch (e) {}
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  };

  // 3-Style Theme Switcher: Cyber Neon, Obsidian Crimson, Royal Sovereign Gold
  const themeButton = document.querySelector('[data-theme-toggle]');
  const STYLES = [
    { id: 'cyber', name: 'Cyber Neon', icon: '⚡' },
    { id: 'crimson', name: 'Obsidian Crimson', icon: '🔥' },
    { id: 'gold', name: 'Royal Sovereign', icon: '👑' },
  ];
  let currentStyleIdx = 0;
  const storedStyle = localStorage.getItem('skinly-demo-style') || (authenticated ? document.documentElement.dataset.themePreference : null);
  const foundIdx = STYLES.findIndex((s) => s.id === storedStyle);
  if (foundIdx >= 0) currentStyleIdx = foundIdx;

  const applyStyle = (idx, showToast = false) => {
    const style = STYLES[idx];
    document.body.classList.remove('theme-cyber', 'theme-crimson', 'theme-gold', 'theme-arctic');
    document.body.classList.add(`theme-${style.id}`);
    document.documentElement.setAttribute('data-theme', style.id);
    localStorage.setItem('skinly-demo-style', style.id);
    if (themeButton) {
      themeButton.innerHTML = style.icon;
      themeButton.setAttribute('title', `Mavzu: ${style.name} (Almashtirish uchun bosing)`);
      themeButton.setAttribute('aria-label', `Theme: ${style.name}`);
    }
    if (showToast) {
      toast(`${style.name} mavzusi faollashtirildi.`);
      if (authenticated) {
        const payload = new URLSearchParams({ action: 'save_theme', theme: style.id });
        fetch(document.documentElement.dataset.demoActionUrl, {
          method: 'POST',
          body: payload,
          headers: { 'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest' },
          credentials: 'same-origin',
        }).catch(() => {});
      }
    }
  };

  applyStyle(currentStyleIdx, false);

  themeButton?.addEventListener('click', () => {
    currentStyleIdx = (currentStyleIdx + 1) % STYLES.length;
    applyStyle(currentStyleIdx, true);
  });

  const caseForm = document.querySelector('[data-animation="case"]');
  if (caseForm) {
    const quantityInput = caseForm.querySelector('[data-case-quantity]');
    const unitPrice = Math.round(Number(caseForm.dataset.casePrice) * 100);
    const totalOutput = caseForm.querySelector('[data-case-total]');
    const unitPriceDisplay = caseForm.querySelector('[data-case-unit-price-display]');
    const qtyDisplay = caseForm.querySelector('[data-case-qty-display]');
    const balanceNote = caseForm.querySelector('[data-case-balance-note]');
    const submitButton = caseForm.querySelector('[data-case-submit]');

    const refreshCaseCost = () => {
      const quantity = Number(quantityInput?.value || 1);
      const total = (unitPrice * quantity) / 100;
      const balance = Number(caseForm.dataset.caseBalance || 0);

      if (totalOutput) totalOutput.textContent = formatDemoCredits(total);
      if (qtyDisplay) qtyDisplay.textContent = String(quantity);
      if (unitPriceDisplay) unitPriceDisplay.textContent = formatDemoCredits(unitPrice / 100);

      const insufficient = !Number.isFinite(total) || total > balance;
      if (balanceNote) {
        balanceNote.classList.toggle('is-error', insufficient);
        balanceNote.textContent = insufficient
          ? `Insufficient demo credits. You have ${formatDemoCredits(balance)}; this opening costs ${formatDemoCredits(total)}. (Need +${formatDemoCredits(total - balance)} credits)`
          : `${formatDemoCredits(balance)} demo credits available. Ready to unbox!`;
      }
      if (submitButton && caseForm.dataset.submitting !== 'true') {
        submitButton.disabled = insufficient || caseForm.dataset.caseHasDrops !== 'true';
        const label = submitButton.querySelector('[data-button-label]');
        if (label) {
          label.textContent = `▶  Open ${quantity} ${quantity === 1 ? 'case' : 'cases'} · ${formatDemoCredits(total)} credits`;
        }
      }
      return total;
    };

    caseForm.querySelectorAll('[data-quantity-option]').forEach((option) => {
      option.addEventListener('click', () => {
        if (caseForm.dataset.submitting === 'true') return;
        const quantity = option.dataset.quantityOption;
        if (!['1', '2', '3', '4', '5', '10'].includes(quantity)) return;
        if (quantityInput) quantityInput.value = quantity;
        caseForm.querySelectorAll('[data-quantity-option]').forEach((choice) => {
          const selected = choice === option;
          choice.classList.toggle('is-selected', selected);
          choice.setAttribute('aria-pressed', String(selected));
        });
        refreshCaseCost();
        playClickSound(950);
      });
    });

    refreshCaseCost();
  }

  const caseResultsModal = document.querySelector('[data-case-results-modal]');
  const resultsTitle = document.querySelector('[data-results-title]');
  const resultsBody = document.querySelector('[data-results-body]');

  const closeModal = () => {
    if (caseResultsModal) {
      try {
        if (typeof caseResultsModal.close === 'function') caseResultsModal.close();
        else caseResultsModal.removeAttribute('open');
      } catch (e) {
        caseResultsModal.removeAttribute('open');
      }
    }
    const multiStage = document.querySelector('[data-multi-stage]');
    if (multiStage) multiStage.hidden = true;
    const carousel = document.querySelector('[data-carousel]');
    if (carousel) carousel.hidden = true;
  };

  document.querySelectorAll('[data-results-close]').forEach((button) => button.addEventListener('click', closeModal));
  caseResultsModal?.addEventListener('click', (event) => {
    if (event.target === caseResultsModal) closeModal();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeModal();
      document.querySelectorAll('dialog[open]').forEach((d) => d.close());
    }
  });

  const showResult = ({ title, summary, html, badge = 'UNBOXING SUCCESSFUL' }) => {
    playWinChime();
    if (!caseResultsModal) {
      toast(title);
      return;
    }
    const modalTitle = caseResultsModal.querySelector('[data-results-title]');
    const modalBadge = caseResultsModal.querySelector('[data-results-badge]');
    const modalSummary = caseResultsModal.querySelector('[data-results-summary]');
    const modalBody = caseResultsModal.querySelector('[data-results-body]');
    if (modalTitle) modalTitle.textContent = title;
    if (modalBadge) modalBadge.textContent = badge;
    if (modalSummary) modalSummary.innerHTML = summary || '';
    if (modalBody) modalBody.innerHTML = html;

    if (typeof caseResultsModal.showModal === 'function') {
      try {
        if (!caseResultsModal.open) caseResultsModal.showModal();
      } catch (e) {
        caseResultsModal.setAttribute('open', '');
      }
    } else {
      caseResultsModal.setAttribute('open', '');
    }
    caseResultsModal.querySelector('[data-results-close]')?.focus();
  };

  document.querySelector('[data-results-open-again]')?.addEventListener('click', () => {
    closeModal();
    const caseForm = document.querySelector('[data-animation="case"]');
    const submitBtn = caseForm?.querySelector('[data-case-submit]');
    if (submitBtn && !submitBtn.disabled) {
      submitBtn.click();
    }
  });

  const itemMarkup = (item, idx = 0) => {
    const image = String(item.image || '/static/images/placeholder.svg').replaceAll('"', '&quot;');
    const name = String(item.name || 'Demo result').replace(/[&<>"']/g, (char) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    })[char]);
    const rarity = String(item.rarity_label || item.rarity || 'Common').replace(/[&<>"']/g, (char) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    })[char]);
    const rarityKey = String(item.rarity || 'common').toLowerCase().replace(/[^a-z-]/g, '');
    const value = Number(item.demo_value);
    const valueLabel = Number.isFinite(value) ? `${formatDemoCredits(value)} credits` : '0,00 credits';
    return `<div class="result-card rarity-${rarityKey}" style="--stagger-index: ${idx};">
      <div class="result-card-glow"></div>
      <div class="result-art-wrap">
        <img src="${image}" alt="${name}" onerror="this.onerror=null;this.src='/static/images/placeholder.svg'">
      </div>
      <div class="result-meta">
        <span class="rarity-badge rarity-${rarityKey}">${rarity}</span>
        <strong class="result-name" title="${name}">${name}</strong>
        <span class="result-value">★ ${valueLabel}</span>
      </div>
    </div>`;
  };

  const animateMultiUnboxing = async (winners, caseName, caseImage) => {
    const multiStage = document.querySelector('[data-multi-stage]');
    const container = document.querySelector('[data-multi-cards-container]');
    const countLabel = document.querySelector('[data-multi-count-label]');
    if (!multiStage || !container) return;

    if (countLabel) countLabel.textContent = `UNBOXING ${winners.length} CASES...`;
    multiStage.hidden = false;
    multiStage.scrollIntoView({ behavior: 'smooth', block: 'center' });

    container.innerHTML = winners.map((winner, idx) => `
      <div class="multi-crate-slot" data-slot-idx="${idx}">
        <div class="crate-box">
          <img src="${caseImage}" alt="${caseName}" class="crate-img" onerror="this.src='/static/images/placeholder.svg'">
          <span class="crate-pulse-ring"></span>
          <span class="crate-label">CASE #${idx + 1}</span>
        </div>
        <div class="revealed-skin-card rarity-${String(winner.rarity || 'common').toLowerCase()}" hidden>
          <div class="skin-art">
            <img src="${winner.image}" alt="${winner.name}" onerror="this.src='/static/images/placeholder.svg'">
          </div>
          <div class="skin-info">
            <span class="skin-rarity-pill">${winner.rarity_label || winner.rarity || 'Common'}</span>
            <strong>${winner.name}</strong>
            <span class="skin-val">${formatDemoCredits(winner.demo_value)} cr</span>
          </div>
        </div>
      </div>
    `).join('');

    const isFast = reducedMotion || animationsPreference === 'false';
    const staggerDelay = isFast ? 50 : Math.max(120, Math.min(320, 1800 / winners.length));

    for (let i = 0; i < winners.length; i++) {
      const slot = container.querySelector(`[data-slot-idx="${i}"]`);
      if (slot) {
        slot.classList.add('is-opening');
        if (!isFast) playClickSound(800 + i * 80);
        await sleep(staggerDelay);
        const crateBox = slot.querySelector('.crate-box');
        const revealCard = slot.querySelector('.revealed-skin-card');
        if (crateBox) crateBox.hidden = true;
        if (revealCard) {
          revealCard.hidden = false;
          slot.classList.add('is-revealed');
        }
      }
    }

    playWinChime();
    if (!isFast) await sleep(800);
  };

  // Count-up number animation helper
  const animateCountUp = (element, start, end, duration = 700) => {
    if (!element) return;
    const startTime = performance.now();
    const step = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * easeOut;
      element.textContent = `${formatDemoCredits(current)} credits`;
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        element.textContent = `${formatDemoCredits(end)} credits`;
      }
    };
    requestAnimationFrame(step);
  };

  const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));

  // Battle Arena Speed Mode Preference
  const speedToggleBtn = document.querySelector('[data-battle-speed-toggle]');
  let isBattleFastMode = localStorage.getItem('skinly-battle-fast') === 'true';
  const syncSpeedToggle = () => {
    if (!speedToggleBtn) return;
    speedToggleBtn.setAttribute('aria-pressed', String(isBattleFastMode));
    const labelSpan = speedToggleBtn.querySelector('span');
    if (labelSpan) labelSpan.textContent = `Fast Mode: ${isBattleFastMode ? 'ON' : 'OFF'}`;
  };
  syncSpeedToggle();
  speedToggleBtn?.addEventListener('click', () => {
    isBattleFastMode = !isBattleFastMode;
    localStorage.setItem('skinly-battle-fast', String(isBattleFastMode));
    syncSpeedToggle();
    toast(`Case Battle Fast Mode ${isBattleFastMode ? 'yoqildi' : 'o‘chirildi'}.`);
  });

  const resetBattleArena = () => {
    document.querySelectorAll('[data-step-dot]').forEach((dot, idx) => {
      dot.classList.toggle('is-active', idx === 0);
      dot.classList.remove('is-done');
    });

    const pScoreEl = document.querySelector('[data-battle-player-score]');
    const bScoreEl = document.querySelector('[data-battle-bot-score]');
    if (pScoreEl) pScoreEl.textContent = '0,00 credits';
    if (bScoreEl) bScoreEl.textContent = '0,00 credits';

    const roundNumberEl = document.querySelector('[data-arena-round-number]');
    const statusPill = document.querySelector('[data-battle-status-pill]');
    const stageHintEl = document.querySelector('[data-arena-stage-hint]');
    const outcomeBanner = document.querySelector('[data-arena-outcome-banner]');
    if (roundNumberEl) roundNumberEl.textContent = 'ROUND 01 / 04';
    if (statusPill) {
      statusPill.textContent = 'READY TO BATTLE';
      statusPill.classList.remove('highlight');
    }
    if (stageHintEl) stageHintEl.textContent = 'Dual Cases Ready';
    if (outcomeBanner) outcomeBanner.hidden = true;

    const pCaseBox = document.querySelector('[data-player-case-box]');
    const bCaseBox = document.querySelector('[data-bot-case-box]');
    const pRouletteWin = document.querySelector('[data-player-roulette-window]');
    const bRouletteWin = document.querySelector('[data-bot-roulette-window]');
    const pRevealCard = document.querySelector('[data-player-reveal-card]');
    const bRevealCard = document.querySelector('[data-bot-reveal-card]');
    const pStage = document.querySelector('[data-player-stage]');
    const bStage = document.querySelector('[data-bot-stage]');

    if (pCaseBox) { pCaseBox.hidden = false; pCaseBox.classList.remove('is-opening'); }
    if (bCaseBox) { bCaseBox.hidden = false; bCaseBox.classList.remove('is-opening'); }
    if (pRouletteWin) pRouletteWin.hidden = true;
    if (bRouletteWin) bRouletteWin.hidden = true;
    if (pRevealCard) pRevealCard.hidden = true;
    if (bRevealCard) bRevealCard.hidden = true;
    if (pStage) pStage.classList.remove('round-winner');
    if (bStage) bStage.classList.remove('round-winner');

    document.querySelectorAll('[data-battle-rounds] .round-card').forEach((card, idx) => {
      card.classList.remove('is-active', 'is-complete', 'round-won-player', 'round-won-bot', 'round-draw');
      const pDrop = card.querySelector('[data-drop-player]');
      const bDrop = card.querySelector('[data-drop-bot]');
      const status = card.querySelector('.round-status');
      if (pDrop) {
        pDrop.innerHTML = '<span class="drop-placeholder">?</span>';
        pDrop.classList.remove('is-winner-drop');
      }
      if (bDrop) {
        bDrop.innerHTML = '<span class="drop-placeholder">?</span>';
        bDrop.classList.remove('is-winner-drop');
      }
      if (status) status.textContent = idx === 0 ? 'Ready' : 'Pending';
    });
  };

  // CS2 Pro Simultaneous Case Battle Animation
  const animateBattle = async (battleData) => {
    const rounds = battleData.rounds || [];
    const botName = battleData.bot_name || 'Opponent';
    const cards = [...document.querySelectorAll('[data-battle-rounds] .round-card')];
    const pScoreEl = document.querySelector('[data-battle-player-score]');
    const bScoreEl = document.querySelector('[data-battle-bot-score]');
    const pDeltaEl = document.querySelector('[data-player-delta]');
    const bDeltaEl = document.querySelector('[data-bot-delta]');
    const statusPill = document.querySelector('[data-battle-status-pill]');
    const roundNumberEl = document.querySelector('[data-arena-round-number]');
    const stageHintEl = document.querySelector('[data-arena-stage-hint]');
    const outcomeBanner = document.querySelector('[data-arena-outcome-banner]');
    const skipBtn = document.querySelector('[data-battle-skip-action]');
    const botDisplayName = document.querySelector('[data-bot-display-name]');
    const botStageTag = document.querySelector('[data-bot-stage-tag]');
    const stepDots = [...document.querySelectorAll('[data-step-dot]')];

    const pStage = document.querySelector('[data-player-stage]');
    const bStage = document.querySelector('[data-bot-stage]');
    const pCaseBox = document.querySelector('[data-player-case-box]');
    const bCaseBox = document.querySelector('[data-bot-case-box]');
    const pCaseImg = document.querySelector('[data-player-case-img]');
    const bCaseImg = document.querySelector('[data-bot-case-img]');
    const pCaseLabel = document.querySelector('[data-player-case-label]');
    const bCaseLabel = document.querySelector('[data-bot-case-label]');
    const pCaseState = document.querySelector('[data-player-case-state]');
    const bCaseState = document.querySelector('[data-bot-case-state]');
    const pRouletteWin = document.querySelector('[data-player-roulette-window]');
    const bRouletteWin = document.querySelector('[data-bot-roulette-window]');
    const pTrack = document.querySelector('[data-player-roulette-track]');
    const bTrack = document.querySelector('[data-bot-roulette-track]');
    const pRevealCard = document.querySelector('[data-player-reveal-card]');
    const bRevealCard = document.querySelector('[data-bot-reveal-card]');
    const pRevealImg = document.querySelector('[data-player-reveal-img]');
    const bRevealImg = document.querySelector('[data-bot-reveal-img]');
    const pRevealName = document.querySelector('[data-player-reveal-name]');
    const bRevealName = document.querySelector('[data-bot-reveal-name]');
    const pRevealRarity = document.querySelector('[data-player-reveal-rarity]');
    const bRevealRarity = document.querySelector('[data-bot-reveal-rarity]');
    const pRevealVal = document.querySelector('[data-player-reveal-val]');
    const bRevealVal = document.querySelector('[data-bot-reveal-val]');
    const pRoundStamp = document.querySelector('[data-player-round-stamp]');
    const bRoundStamp = document.querySelector('[data-bot-round-stamp]');

    if (botDisplayName) botDisplayName.textContent = `${botName} (Bot)`;
    if (botStageTag) botStageTag.textContent = `${botName} (Bot)`;

    let pTotal = 0;
    let bTotal = 0;
    if (pScoreEl) pScoreEl.textContent = '0,00 credits';
    if (bScoreEl) bScoreEl.textContent = '0,00 credits';

    // Parse skin pool for authentic roulette cards
    let pool = [];
    try {
      const rawPool = document.getElementById('battle-pool-data')?.textContent;
      if (rawPool) pool = JSON.parse(rawPool);
    } catch (e) {}
    if (!pool.length && Array.isArray(battleData.item_pool) && battleData.item_pool.length) {
      pool = battleData.item_pool;
    }
    if (!pool.length) {
      rounds.forEach((r) => {
        if (r.player_item) pool.push(r.player_item);
        if (r.bot_item) pool.push(r.bot_item);
      });
    }

    let skipRequested = false;
    if (skipBtn) {
      skipBtn.hidden = false;
      skipBtn.onclick = () => {
        skipRequested = true;
        skipBtn.hidden = true;
      };
    }

    // Process all 4 rounds sequentially
    for (let index = 0; index < rounds.length; index += 1) {
      const r = rounds[index];
      const card = cards[index];
      const roundNumStr = `ROUND 0${index + 1} / 04`;

      // 1. Update Stepper & Arena Header
      stepDots.forEach((dot, dotIdx) => {
        dot.classList.toggle('is-done', dotIdx < index);
        dot.classList.toggle('is-active', dotIdx === index);
      });

      if (roundNumberEl) roundNumberEl.textContent = roundNumStr;
      if (statusPill) {
        statusPill.textContent = `ROUND ${index + 1}: INTRODUCING CASES`;
        statusPill.classList.remove('highlight');
      }
      if (stageHintEl) stageHintEl.textContent = 'Simultaneous Case Preview';
      if (outcomeBanner) outcomeBanner.hidden = true;
      if (card) {
        card.classList.add('is-active');
        const st = card.querySelector('.round-status');
        if (st) st.textContent = 'Opening…';
      }

      // Display closed cases
      const caseName = r.case?.name || 'CS2 Weapon Cache';
      const caseImg = r.case?.image || '/static/demo/cases/arcane-cyber-cache.svg';
      if (pCaseLabel) pCaseLabel.textContent = caseName;
      if (bCaseLabel) bCaseLabel.textContent = caseName;
      if (pCaseImg) pCaseImg.src = caseImg;
      if (bCaseImg) bCaseImg.src = caseImg;
      if (pCaseState) pCaseState.textContent = 'READY';
      if (bCaseState) bCaseState.textContent = 'READY';

      if (pCaseBox) { pCaseBox.hidden = false; pCaseBox.classList.remove('is-opening'); }
      if (bCaseBox) { bCaseBox.hidden = false; bCaseBox.classList.remove('is-opening'); }
      if (pRouletteWin) pRouletteWin.hidden = true;
      if (bRouletteWin) bRouletteWin.hidden = true;
      if (pRevealCard) pRevealCard.hidden = true;
      if (bRevealCard) bRevealCard.hidden = true;
      if (pStage) pStage.classList.remove('round-winner');
      if (bStage) bStage.classList.remove('round-winner');

      const isFast = isBattleFastMode || reducedMotion;

      // Case intro wait (500–700 ms)
      if (!skipRequested && !reducedMotion) {
        await sleep(isFast ? 150 : 650);
      }

      // 2. Case opening effect (600–800 ms)
      if (statusPill) statusPill.textContent = `ROUND ${index + 1}: OPENING CASES…`;
      if (stageHintEl) stageHintEl.textContent = 'Unlocking Container Latches';
      if (pCaseState) pCaseState.textContent = 'OPENING…';
      if (bCaseState) bCaseState.textContent = 'OPENING…';
      playCaseUnlockSound();

      if (pCaseBox) pCaseBox.classList.add('is-opening');
      if (bCaseBox) bCaseBox.classList.add('is-opening');

      if (!skipRequested && !reducedMotion) {
        await sleep(isFast ? 180 : 700);
      }

      // 3. Horizontal Roulette Movement (2500–3500 ms)
      if (pCaseBox) pCaseBox.hidden = true;
      if (bCaseBox) bCaseBox.hidden = true;
      if (pRouletteWin) pRouletteWin.hidden = false;
      if (bRouletteWin) bRouletteWin.hidden = false;
      if (statusPill) statusPill.textContent = `ROUND ${index + 1}: SPINNING ROULETTE`;
      if (stageHintEl) stageHintEl.textContent = 'Roulette Decelerating to Target';

      const pTarget = r.player_item;
      const bTarget = r.bot_item;

      const buildReelItems = (targetItem) => {
        return Array.from({ length: 30 }, (_, cardIdx) => {
          if (cardIdx === 24) return targetItem;
          if (pool.length) return pool[(cardIdx + index * 7) % pool.length];
          return targetItem;
        });
      };

      const renderReelHtml = (items) => {
        return items.map((it, cardIdx) => `
          <div class="roulette-card rarity-${it.rarity || 'common'}" data-card-idx="${cardIdx}">
            <img src="${String(it.image || '/static/images/placeholder.svg').replaceAll('"', '&quot;')}" alt="${String(it.name || '').replace(/[&<>"]/g, '')}" onerror="this.src='/static/images/placeholder.svg'">
            <strong>${String(it.name || '').replace(/[&<>"]/g, '')}</strong>
            <span class="roulette-card-val">${it.demo_value || '0.00'} cr</span>
          </div>
        `).join('');
      };

      if (pTrack) {
        pTrack.style.transition = 'none';
        pTrack.style.transform = 'translateX(0)';
        pTrack.innerHTML = renderReelHtml(buildReelItems(pTarget));
      }
      if (bTrack) {
        bTrack.style.transition = 'none';
        bTrack.style.transform = 'translateX(0)';
        bTrack.innerHTML = renderReelHtml(buildReelItems(bTarget));
      }

      const itemStep = 120;
      const targetCardCenter = (24 * itemStep) + 10 + 55;
      const pViewportW = pRouletteWin?.querySelector('.roulette-track-viewport')?.clientWidth || 360;
      const bViewportW = bRouletteWin?.querySelector('.roulette-track-viewport')?.clientWidth || 360;

      const pJitter = skipRequested ? 0 : (Math.random() * 16 - 8);
      const bJitter = skipRequested ? 0 : (Math.random() * 16 - 8);

      const pOffset = Math.max(0, targetCardCenter - (pViewportW / 2) + pJitter);
      const bOffset = Math.max(0, targetCardCenter - (bViewportW / 2) + bJitter);

      if (pTrack) pTrack.getBoundingClientRect();
      if (bTrack) bTrack.getBoundingClientRect();

      const spinDuration = (skipRequested || reducedMotion) ? 0 : (isFast ? 800 : 3100);

      if (pTrack) {
        pTrack.style.transition = spinDuration ? `transform ${spinDuration}ms cubic-bezier(0.12, 0.8, 0.32, 1)` : 'none';
        pTrack.style.transform = `translateX(-${pOffset}px)`;
      }
      if (bTrack) {
        bTrack.style.transition = spinDuration ? `transform ${spinDuration}ms cubic-bezier(0.12, 0.8, 0.32, 1)` : 'none';
        bTrack.style.transform = `translateX(-${bOffset}px)`;
      }

      if (spinDuration > 0) {
        playRouletteSpinSound(spinDuration);
        await sleep(spinDuration);
      }

      // 4. Highlight target winning card (500–700 ms)
      const pWinnerCard = pTrack?.querySelector('[data-card-idx="24"]');
      const bWinnerCard = bTrack?.querySelector('[data-card-idx="24"]');
      if (pWinnerCard) pWinnerCard.classList.add('is-winner-card');
      if (bWinnerCard) bWinnerCard.classList.add('is-winner-card');
      playClickSound(1100);

      if (!skipRequested && !reducedMotion) {
        await sleep(isFast ? 150 : 600);
      }

      // 5. Reveal Items & Round Result (800–1200 ms)
      if (pRouletteWin) pRouletteWin.hidden = true;
      if (bRouletteWin) bRouletteWin.hidden = true;
      if (pRevealCard) pRevealCard.hidden = false;
      if (bRevealCard) bRevealCard.hidden = false;

      if (pRevealImg) pRevealImg.src = pTarget.image || '/static/images/placeholder.svg';
      if (pRevealName) pRevealName.textContent = pTarget.name || '';
      if (pRevealRarity) pRevealRarity.textContent = pTarget.rarity_label || pTarget.rarity || 'Common';
      if (pRevealVal) pRevealVal.textContent = `${pTarget.demo_value || '0.00'} credits`;

      if (bRevealImg) bRevealImg.src = bTarget.image || '/static/images/placeholder.svg';
      if (bRevealName) bRevealName.textContent = bTarget.name || '';
      if (bRevealRarity) bRevealRarity.textContent = bTarget.rarity_label || bTarget.rarity || 'Common';
      if (bRevealVal) bRevealVal.textContent = `${bTarget.demo_value || '0.00'} credits`;

      const pVal = Number(pTarget.demo_value || 0);
      const bVal = Number(bTarget.demo_value || 0);

      const pDrop = card?.querySelector('[data-drop-player]');
      const bDrop = card?.querySelector('[data-drop-bot]');
      const status = card?.querySelector('.round-status');

      if (pVal > bVal) {
        if (pStage) pStage.classList.add('round-winner');
        if (pRoundStamp) {
          pRoundStamp.className = 'reveal-round-stamp won';
          pRoundStamp.textContent = `ROUND WINNER (+${formatDemoCredits(pVal)})`;
        }
        if (bRoundStamp) {
          bRoundStamp.className = 'reveal-round-stamp lost';
          bRoundStamp.textContent = 'ROUND LOST';
        }
        if (outcomeBanner) {
          outcomeBanner.textContent = `ROUND ${index + 1} WON BY YOU!`;
          outcomeBanner.hidden = false;
        }
        if (card) {
          card.classList.add('round-won-player');
          if (status) status.textContent = 'Won by You';
        }
        if (pDrop) pDrop.classList.add('is-winner-drop');
        playWinChime();
      } else if (bVal > pVal) {
        if (bStage) bStage.classList.add('round-winner');
        if (bRoundStamp) {
          bRoundStamp.className = 'reveal-round-stamp won';
          bRoundStamp.textContent = `ROUND WINNER (+${formatDemoCredits(bVal)})`;
        }
        if (pRoundStamp) {
          pRoundStamp.className = 'reveal-round-stamp lost';
          pRoundStamp.textContent = 'ROUND LOST';
        }
        if (outcomeBanner) {
          outcomeBanner.textContent = `ROUND ${index + 1} WON BY ${botName.toUpperCase()}!`;
          outcomeBanner.hidden = false;
        }
        if (card) {
          card.classList.add('round-won-bot');
          if (status) status.textContent = `Won by ${botName}`;
        }
        if (bDrop) bDrop.classList.add('is-winner-drop');
        playClickSound(750);
      } else {
        if (pRoundStamp) {
          pRoundStamp.className = 'reveal-round-stamp draw';
          pRoundStamp.textContent = 'ROUND DRAW';
        }
        if (bRoundStamp) {
          bRoundStamp.className = 'reveal-round-stamp draw';
          bRoundStamp.textContent = 'ROUND DRAW';
        }
        if (outcomeBanner) {
          outcomeBanner.textContent = `ROUND ${index + 1}: DRAW (EQUAL VALUES)`;
          outcomeBanner.hidden = false;
        }
        if (card) {
          card.classList.add('round-draw');
          if (status) status.textContent = 'Draw';
        }
      }

      // Update Mini Drops
      if (pDrop) {
        pDrop.innerHTML = `<img src="${pTarget.image}" alt="" class="battle-drop-img"><div class="drop-info"><strong>${pTarget.name}</strong><small style="font-size: 8px;">${pTarget.demo_value} cr</small></div>`;
      }
      if (bDrop) {
        bDrop.innerHTML = `<img src="${bTarget.image}" alt="" class="battle-drop-img"><div class="drop-info"><strong>${bTarget.name}</strong><small style="font-size: 8px;">${bTarget.demo_value} cr</small></div>`;
      }

      // Delta Chips and Score Count-up
      if (pDeltaEl) {
        pDeltaEl.textContent = `+${formatDemoCredits(pVal)}`;
        pDeltaEl.classList.add('show');
      }
      if (bDeltaEl) {
        bDeltaEl.textContent = `+${formatDemoCredits(bVal)}`;
        bDeltaEl.classList.add('show');
      }

      const prevPTotal = pTotal;
      const prevBTotal = bTotal;
      pTotal += pVal;
      bTotal += bVal;

      animateCountUp(pScoreEl, prevPTotal, pTotal, isFast ? 300 : 700);
      animateCountUp(bScoreEl, prevBTotal, bTotal, isFast ? 300 : 700);

      window.setTimeout(() => {
        if (pDeltaEl) pDeltaEl.classList.remove('show');
        if (bDeltaEl) bDeltaEl.classList.remove('show');
      }, 1000);

      if (card) {
        card.classList.remove('is-active');
        card.classList.add('is-complete');
      }

      if (!skipRequested && !reducedMotion && index < rounds.length - 1) {
        await sleep(isFast ? 350 : 1000);
      }
    }

    stepDots.forEach((dot) => {
      dot.classList.remove('is-active');
      dot.classList.add('is-done');
    });

    if (skipBtn) skipBtn.hidden = true;
    if (statusPill) {
      statusPill.textContent = 'BATTLE CONCLUDED';
      statusPill.classList.add('highlight');
    }
  };

  // Form Submissions
  document.querySelectorAll('[data-demo-form]').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (form.dataset.submitting === 'true') return;
      const submitButton = form.querySelector('[type=submit]');
      const buttonLabel = submitButton?.querySelector('[data-button-label]');
      const originalText = buttonLabel?.textContent || submitButton?.textContent || '';
      if (submitButton) submitButton.disabled = true;
      if (form.dataset.animation === 'case') {
        form.dataset.submitting = 'true';
        form.querySelectorAll('[data-quantity-option]').forEach((option) => { option.disabled = true; });
      }
      if (buttonLabel) buttonLabel.textContent = 'Preparing demo…';

      if (form.dataset.animation === 'upgrade') {
        form.dataset.upgrading = 'true';
        form.querySelectorAll('[data-picker-open], [data-multiplier], [data-upgrade-reset]').forEach((control) => {
          control.disabled = true;
        });
        const reactor = document.querySelector('[data-upgrade-reactor]');
        const pointer = document.querySelector('[data-upgrade-pointer]');
        const indicator = document.querySelector('[data-upgrade-indicator]');
        if (reactor) reactor.removeAttribute('data-upgrade-result');
        if (pointer) {
          pointer.style.transition = 'none';
          pointer.style.setProperty('--pointer-angle', '0deg');
        }
        if (indicator) indicator.textContent = '⚡';
      }

      let reloadOnComplete = false;
      if (form.dataset.animation === 'case') {
        const carousel = document.querySelector('[data-carousel]');
        const multiStage = document.querySelector('[data-multi-stage]');
        const track = document.querySelector('[data-carousel-track]');
        const quantity = Number(form.querySelector('[data-case-quantity]')?.value || 1);

        const reqInput = form.querySelector('[name=request_id]');
        if (reqInput) reqInput.value = generateUUID();

        if (carousel && quantity === 1) {
          if (track) track.innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div>';
          carousel.hidden = false;
        } else if (carousel) {
          carousel.hidden = true;
        }
        if (multiStage && quantity > 1) {
          multiStage.hidden = false;
        } else if (multiStage) {
          multiStage.hidden = true;
        }
      }

      try {
        const response = await fetch(form.getAttribute('action'), {
          method: 'POST',
          body: new FormData(form),
          headers: {
            'X-CSRFToken': csrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
          },
          credentials: 'same-origin',
        });
        const result = await response.json();
        if (
          form.dataset.animation === 'upgrade'
          && response.status < 500
          && window.crypto?.randomUUID
        ) {
          const requestId = form.querySelector('[name=request_id]');
          if (requestId) requestId.value = window.crypto.randomUUID();
        }
        if (!response.ok || !result.ok) throw new Error(result.error || 'Demo action could not be completed.');

        if (form.dataset.animation === 'case') {
          const carousel = document.querySelector('[data-carousel]');
          const multiStage = document.querySelector('[data-multi-stage]');
          const track = document.querySelector('[data-carousel-track]');
          const winners = Array.isArray(result.results) ? result.results : [result.result];
          const quantity = Number(result.quantity || winners.length);
          const totalCost = Number(result.total_cost || 0);
          const totalValue = Number(result.total_value || winners.reduce((sum, it) => sum + Number(it.demo_value || 0), 0));
          const caseImg = form.closest('.case-detail-layout')?.querySelector('.case-hero-image')?.src || '/static/images/placeholder.svg';
          const caseName = form.closest('.case-detail-layout')?.querySelector('h1')?.textContent || 'Case';

          if (result.balance) {
            form.dataset.caseBalance = result.balance;
            document.querySelectorAll('[data-demo-balance]').forEach((el) => {
              el.textContent = formatDemoCredits(Number(result.balance));
            });
          }

          if (quantity > 1) {
            await animateMultiUnboxing(winners, caseName, caseImg);
            const netGain = totalValue - totalCost;
            const netGainText = netGain >= 0
              ? `<span style="color:#6ee7b7; font-weight:700;">+${formatDemoCredits(netGain)} credits profit!</span>`
              : `<span style="color:#f87171; font-weight:700;">-${formatDemoCredits(Math.abs(netGain))} credits</span>`;

            showResult({
              title: `${quantity} Cases Unboxed`,
              badge: `${quantity} SKINS ACQUIRED`,
              summary: `Spent <strong>${formatDemoCredits(totalCost)} credits</strong> · Total skin value: <strong>${formatDemoCredits(totalValue)} credits</strong> (${netGainText})`,
              html: `<div class="results-grid count-${quantity}">${winners.map((it, idx) => itemMarkup(it, idx)).join('')}</div>`,
            });
          } else if (carousel && track && winners[0]) {
            const winner = winners[0];
            const caption = document.querySelector('[data-carousel-caption]');
            if (caption) caption.textContent = `WINNER: ${winner.name.toUpperCase()}`;
            const previews = [...document.querySelectorAll('.item-grid .item-card')].map((card) => ({
              name: card.querySelector('strong')?.textContent || winner.name,
              image: card.querySelector('img')?.getAttribute('src') || winner.image,
              demo_value: card.querySelector('.drop-val')?.textContent || winner.demo_value || '',
              rarity: card.className.match(/rarity-([a-z]+)/)?.[1] || 'common',
            }));
            const reels = Array.from({ length: 32 }, (_, index) => {
              if (index === 27) return winner;
              return previews.length ? previews[index % previews.length] : winner;
            });
            track.innerHTML = reels.map((item) => `
              <div class="carousel-item rarity-${item.rarity || 'common'}">
                <img src="${String(item.image || '/static/images/placeholder.svg').replaceAll('"', '&quot;')}" alt="" onerror="this.src='/static/images/placeholder.svg'">
                <strong>${String(item.name).replace(/[&<>"]/g, '')}</strong>
                <span class="carousel-item-val">${item.demo_value || ''}</span>
              </div>
            `).join('');
            carousel.hidden = false;
            carousel.scrollIntoView({ behavior: 'smooth', block: 'center' });
            track.style.transition = 'none';
            track.style.transform = 'translateX(0)';

            const isFast = reducedMotion || animationsPreference === 'false';
            playRouletteSpinSound(isFast ? 100 : 5800);

            await new Promise((resolve) => {
              requestAnimationFrame(() => requestAnimationFrame(() => {
                track.style.transition = isFast ? 'none' : 'transform 5.8s cubic-bezier(0.12, 0.8, 0.32, 1)';
                const winnerCard = track.children[27];
                const center = carousel.querySelector('.carousel-window').clientWidth / 2;
                const offset = winnerCard.offsetLeft + winnerCard.clientWidth / 2 - center;
                track.style.transform = `translateX(-${Math.max(0, offset)}px)`;

                if (isFast) {
                  resolve();
                } else {
                  window.setTimeout(() => {
                    winnerCard.classList.add('winner-pulse');
                    resolve();
                  }, 5800);
                }
              }));
            });

            showResult({
              title: 'Case Opening Result',
              badge: 'ITEM UNBOXED',
              summary: `Spent <strong>${formatDemoCredits(totalCost)} credits</strong> · Received 1 exclusive skin.`,
              html: `<div class="results-single">${itemMarkup(winner, 0)}</div>`,
            });
          } else {
            showResult({
              title: 'Case Opening Result',
              badge: 'ITEM UNBOXED',
              summary: `Spent <strong>${formatDemoCredits(totalCost)} credits</strong> · Received 1 skin.`,
              html: `<div class="results-single">${itemMarkup(winners[0], 0)}</div>`,
            });
          }

          const reqInput = form.querySelector('[name=request_id]');
          if (reqInput) reqInput.value = generateUUID();
        }

        } else if (form.dataset.animation === 'battle') {
          await animateBattle(result);
          const isPlayerWinner = result.player_won;
          const isDraw = result.is_draw || (!isPlayerWinner && result.winner === 'Draw');
          const botName = result.bot_name || 'Opponent';

          let bannerClass = 'lost';
          let bannerText = `${result.winner || botName} WON THE BATTLE`;
          if (isPlayerWinner) {
            bannerClass = 'won';
            bannerText = '🏆 YOU WON THE BATTLE!';
          } else if (isDraw) {
            bannerClass = 'draw';
            bannerText = '🤝 MATCH DRAW (EQUAL TOTALS)';
          }

          const roundRowsHtml = (result.rounds || []).map((r) => {
            const pVal = Number(r.player_item?.demo_value || 0);
            const bVal = Number(r.bot_item?.demo_value || 0);
            const winnerTag = pVal > bVal
              ? '<span style="color:#5ee3b0;font-weight:800;">YOU</span>'
              : (bVal > pVal
                ? `<span style="color:#51e5e3;font-weight:800;">${botName}</span>`
                : '<span style="color:#fbbf24;font-weight:800;">DRAW</span>');
            return `
              <div class="battle-round-row">
                <span><strong>ROUND 0${r.round}</strong></span>
                <div class="skin-cell">
                  <img src="${r.player_item?.image}" alt="" onerror="this.src='/static/images/placeholder.svg'">
                  <span>${r.player_item?.name} (${r.player_item?.demo_value} cr)</span>
                </div>
                <span>vs</span>
                <div class="skin-cell">
                  <img src="${r.bot_item?.image}" alt="" onerror="this.src='/static/images/placeholder.svg'">
                  <span>${r.bot_item?.name} (${r.bot_item?.demo_value} cr)</span>
                </div>
                <div>${winnerTag}</div>
              </div>
            `;
          }).join('');

          const trophyHtml = isPlayerWinner && result.trophy ? `
            <div class="battle-trophy-callout">
              <img src="${result.trophy.image}" alt="${result.trophy.name}" onerror="this.src='/static/images/placeholder.svg'">
              <div>
                <strong>Prize Added to Inventory: ${result.trophy.name}</strong>
                <p style="margin:2px 0 0;font-size:11px;color:#838ba7;">Value: ${result.trophy.demo_value} credits · Saved to your demo inventory!</p>
              </div>
            </div>
          ` : '';

          const modalTitle = isPlayerWinner ? '🏆 Battle Victory!' : (isDraw ? '🤝 Battle Draw' : '⚔ Battle Finished');
          const modalHtml = `
            <div class="result-summary" style="text-align:center;">
              <div class="battle-winner-banner ${bannerClass}">
                <strong>${bannerText}</strong>
              </div>
              <div class="battle-final-scores-bar">
                <div class="score-item">
                  <small>YOUR TOTAL</small>
                  <strong>${formatDemoCredits(result.player_total)} cr</strong>
                </div>
                <div style="font-weight:900;color:#838ba7;">VS</div>
                <div class="score-item">
                  <small>${botName.toUpperCase()} TOTAL</small>
                  <strong>${formatDemoCredits(result.bot_total)} cr</strong>
                </div>
              </div>
              ${trophyHtml}
              <div style="margin:16px 0 8px;font-size:11px;font-weight:800;color:#838ba7;text-align:left;">ALL 8 ROUND RESULTS:</div>
              <div class="battle-rounds-table">
                ${roundRowsHtml}
              </div>
              <div class="battle-final-actions" style="margin-top:20px;">
                <button class="button button-primary" type="button" data-battle-again-btn>⚔ Battle Again</button>
                <a class="button button-quiet" href="/demo/inventory/">🎒 View Inventory</a>
                <button class="button button-quiet" type="button" data-modal-close>✕ View Arena</button>
              </div>
            </div>
          `;
          showResult(modalTitle, modalHtml);

          document.querySelector('[data-battle-again-btn]')?.addEventListener('click', () => {
            reloadAfterResult = false;
            closeModal();
            resetBattleArena();
            toast('Arena tayyor! Yangi case battle boshlashingiz mumkin.');
          });

        } else if (form.dataset.animation === 'upgrade') {
          const reactor = document.querySelector('[data-upgrade-reactor]');
          const multiplier = form.querySelector('[data-upgrade-multiplier-value]')?.value;
          const multiplierTenths = { '1.5': 15, '2': 20, '5': 50, '10': 100 }[multiplier];
          const sourceId = form.querySelector('[data-selection-input="source"]')?.value;
          const targetId = form.querySelector('[data-selection-input="target"]')?.value;
          const chanceBasisPoints = Number(result.chance_basis_points);
          const chancePercent = chanceBasisPoints / 100;
          if (
            !Number.isInteger(chanceBasisPoints)
            || chanceBasisPoints < 500
            || chanceBasisPoints > 9000
            || String(result.source_inventory_id) !== sourceId
            || String(result.target_item_id) !== targetId
            || Number(result.multiplier_tenths) !== multiplierTenths
            || result.chance !== chancePercent.toFixed(2)
            || typeof result.success !== 'boolean'
          ) {
            throw new Error('Upgrade tanlovi server tasdiqlagan item yoki ko‘paytirgich bilan mos emas. Itemlarni qayta tanlang.');
          }
          const chanceLabel = document.querySelector('[data-upgrade-chance]');
          const successLabel = document.querySelector('[data-upgrade-success]');
          const failLabel = document.querySelector('[data-upgrade-fail]');
          const ring = document.querySelector('[data-upgrade-ring]');
          if (chanceLabel) chanceLabel.textContent = `${chancePercent.toFixed(2)}%`;
          if (successLabel) successLabel.textContent = `${chancePercent.toFixed(2)}%`;
          if (failLabel) failLabel.textContent = `${(100 - chancePercent).toFixed(2)}%`;
          if (ring) ring.style.setProperty('--success-angle', `${chanceBasisPoints * 0.036}deg`);
          const pointer = document.querySelector('[data-upgrade-pointer]');
          const chanceAngle = chancePercent * 3.6;
          const landingAngle = result.success
            ? chanceAngle / 2
            : chanceAngle + ((360 - chanceAngle) / 2);
          if (reactor) {
            reactor.dataset.rolling = 'true';
            reactor.removeAttribute('data-upgrade-result');
          }
          if (pointer) {
            pointer.style.transition = 'none';
            pointer.style.setProperty('--pointer-angle', '0deg');
            pointer.getBoundingClientRect();
            if (!reducedMotion && animationsPreference !== 'false') {
              pointer.style.transition = 'transform 4.6s cubic-bezier(0.12, 0.8, 0.32, 1)';
              playRouletteSpinSound(4600);
              requestAnimationFrame(() => {
                pointer.style.setProperty('--pointer-angle', `${(6 * 360) + landingAngle}deg`);
              });
              await new Promise((resolve) => window.setTimeout(resolve, Number(form.dataset.duration) || 4800));
            } else {
              pointer.style.setProperty('--pointer-angle', `${landingAngle}deg`);
            }
          } else if (!reducedMotion && animationsPreference !== 'false') {
            await new Promise((resolve) => window.setTimeout(resolve, Number(form.dataset.duration) || 4800));
          }
          if (reactor) {
            delete reactor.dataset.rolling;
            reactor.dataset.upgradeResult = result.success ? 'success' : 'failure';
          }
          const indicator = document.querySelector('[data-upgrade-indicator]');
          if (indicator) indicator.textContent = result.success ? '✓' : '✕';
          if (result.success) {
            reloadAfterResult = true;
            showResult(
              'Upgrade successful',
              `<div class="lab-result-stamp success"><span>✓</span>UPGRADE SUCCESS</div><p class="result-summary">${chancePercent.toFixed(2)}% success chance · server-confirmed result</p>${itemMarkup(result.result)}`,
            );
          } else {
            showResult(
              'Upgrade failed',
              `<div class="lab-result-stamp failure"><span>✕</span>UPGRADE FAILED</div><p class="result-summary">${chancePercent.toFixed(2)}% success chance · your source skin remains in your inventory.</p>${itemMarkup(result.source)}`,
            );
          }

        } else if (form.dataset.animation === 'contract') {
          form.classList.add('contract-active');
          playWinChime();
          if (!reducedMotion && animationsPreference !== 'false') await new Promise((resolve) => window.setTimeout(resolve, 850));
          form.classList.remove('contract-active');
          showResult('Trade-Up Contract Complete', `<p class="result-summary">${result.message || 'New skin acquired!'}</p>${itemMarkup(result.result)}`);
          reloadAfterResult = true;

        } else if (form.dataset.animation === 'sell') {
          const balance = document.querySelector('[data-demo-balance]');
          if (balance && result.balance) balance.textContent = formatDemoCredits(Number(result.balance));
          playClickSound(1200);
          toast(result.message || 'Demo item sold for demo credits.');
          const card = form.closest('.item-card');
          if (card) {
            card.style.transition = 'all 0.35s ease';
            card.style.opacity = '0';
            card.style.transform = 'scale(0.85)';
            window.setTimeout(() => card.remove(), 350);
          } else {
            reloadOnComplete = true;
          }

        } else if (result.result) {
          showResult('Demo action complete', itemMarkup(result.result));

        } else {
          toast(result.message || (result.xp ? `+${result.xp} non-monetary demo XP recorded.` : 'Your demo change was saved.'));
          if (form.querySelector('[name=action]')?.value === 'claim_daily') window.setTimeout(() => window.location.reload(), 650);
          if (form.querySelector('[name=action]')?.value === 'save_settings') {
            const soundSetting = form.querySelector('[name=sound_enabled][type=checkbox]');
            const animationsSetting = form.querySelector('[name=animations_enabled][type=checkbox]');
            const notificationSetting = form.querySelector('[name=notifications_enabled][type=checkbox]');
            if (soundSetting) soundSettingButtonSync(soundSetting.checked);
            if (animationsSetting) {
              animationsPreference = String(animationsSetting.checked);
              localStorage.setItem('skinly-demo-animations', String(animationsSetting.checked));
              document.documentElement.setAttribute('data-animations-enabled', String(animationsSetting.checked));
            }
            const themeSetting = form.querySelector('[name=dark_theme_enabled][type=checkbox]');
            if (themeSetting) {
              document.documentElement.classList.toggle('theme-light', !themeSetting.checked);
              localStorage.setItem('skinly-demo-theme', themeSetting.checked ? 'dark' : 'light');
            }
            if (notificationSetting) localStorage.setItem('skinly-demo-notifications', String(notificationSetting.checked));
          }
          if (form.querySelector('[name=action]')?.value === 'read_notification') {
            form.closest('.notification-row')?.classList.add('is-read');
          }
        }

        if (form.querySelector('[name=action]')?.value === 'favorite_case' || form.querySelector('[name=action]')?.value === 'favorite_item') {
          toast(result.saved ? 'Added to your demo favorites.' : 'Removed from your demo favorites.');
          const favoriteButton = form.querySelector('[data-favorite-button]');
          if (favoriteButton) {
            favoriteButton.classList.toggle('is-favorite', result.saved);
            favoriteButton.setAttribute('aria-pressed', String(result.saved));
            favoriteButton.setAttribute('aria-label', result.saved ? 'Remove from favorites' : 'Add to favorites');
            favoriteButton.textContent = result.saved ? '♥' : '♡';
          }
          if (window.location.pathname === '/favorites/') window.setTimeout(() => window.location.reload(), 500);
        }
      } catch (error) {
        if (form.dataset.animation === 'case') {
          const carousel = document.querySelector('[data-carousel]');
          if (carousel) carousel.hidden = true;
        }
        toast(error.message || 'Network error. Please try again.', true);
      } finally {
        if (form.dataset.animation === 'case') {
          delete form.dataset.submitting;
          form.querySelectorAll('[data-quantity-option]').forEach((option) => { option.disabled = false; });
          const total = (Math.round(Number(form.dataset.casePrice) * 100) * Number(form.querySelector('[data-case-quantity]')?.value || 1)) / 100;
          const available = Number(form.dataset.caseBalance || 0);
          if (submitButton) {
            submitButton.disabled = total > available || form.dataset.caseHasDrops !== 'true';
            const label = submitButton.querySelector('[data-button-label]');
            const qty = form.querySelector('[data-case-quantity]')?.value || 1;
            if (label) label.textContent = `▶  Open ${qty} ${qty === '1' ? 'case' : 'cases'} · ${formatDemoCredits(total)} credits`;
          }
          const reqInput = form.querySelector('[name=request_id]');
          if (reqInput) reqInput.value = generateUUID();
        }
        if (form.dataset.animation === 'upgrade') {
          delete form.dataset.upgrading;
          form.querySelectorAll('[data-picker-open], [data-multiplier], [data-upgrade-reset]').forEach((control) => {
            control.disabled = false;
          });
          updateUpgradeSubmit();
        }
        if (form.dataset.animation === 'battle') {
          delete form.dataset.submitting;
          const skipBtn = document.querySelector('[data-battle-skip-action]');
          if (skipBtn) skipBtn.hidden = true;
          const reqInput = form.querySelector('[name=request_id]');
          if (reqInput && window.crypto?.randomUUID) {
            reqInput.value = window.crypto.randomUUID();
          }
          if (submitButton) submitButton.disabled = false;
          if (buttonLabel) buttonLabel.textContent = '⚔   Start Case Battle (Free Demo)';
        } else if (submitButton && !form.querySelector('[name=action]')?.value.includes('claim_daily')) {
          submitButton.disabled = false;
        }
        if (buttonLabel && form.dataset.animation !== 'battle' && form.dataset.animation !== 'case') buttonLabel.textContent = originalText;
        if (reloadOnComplete) window.setTimeout(() => window.location.reload(), 800);
      }
    });
  });

  function soundSettingButtonSync(enabled) {
    if (!soundButton) return;
    soundButton.setAttribute('aria-pressed', String(enabled));
    localStorage.setItem('skinly-demo-sound', String(enabled));
  }

  // Upgrade Lab Picker Logic
  const itemPicker = document.querySelector('[data-item-picker]');
  const filterPickerItems = () => {
    const query = document.querySelector('[data-picker-search]')?.value.toLowerCase().trim() || '';
    const rarity = document.querySelector('[data-picker-rarity]')?.value || '';
    const target = itemPicker?.dataset.pickerTarget || '';
    document.querySelectorAll('[data-picker-item]').forEach((item) => {
      item.hidden = item.dataset.pickerSide !== target
        || !item.dataset.name.toLowerCase().includes(query)
        || Boolean(rarity && item.dataset.rarity !== rarity);
    });
  };
  const updateUpgradeChance = () => {
    const sourceValue = Number(document.querySelector('[data-selection-image="source"]')?.dataset.demoValue);
    const targetValue = Number(document.querySelector('[data-selection-image="target"]')?.dataset.demoValue);
    const multiplier = document.querySelector('[data-upgrade-multiplier-value]')?.value || '1.5';
    const multiplierTenths = { '1.5': 15, '2': 20, '5': 50, '10': 100 }[multiplier];
    const chance = document.querySelector('[data-upgrade-chance]');
    if (!chance || !sourceValue || !targetValue || !multiplierTenths) {
      if (chance) chance.textContent = '—';
      const success = document.querySelector('[data-upgrade-success]');
      const fail = document.querySelector('[data-upgrade-fail]');
      const ring = document.querySelector('[data-upgrade-ring]');
      if (success) success.textContent = '—%';
      if (fail) fail.textContent = '—%';
      if (ring) ring.dataset.ready = 'false';
      const reactor = document.querySelector('[data-upgrade-reactor]');
      const pointer = document.querySelector('[data-upgrade-pointer]');
      const indicator = document.querySelector('[data-upgrade-indicator]');
      if (reactor) reactor.removeAttribute('data-upgrade-result');
      if (pointer) {
        pointer.style.transition = 'none';
        pointer.style.setProperty('--pointer-angle', '0deg');
      }
      if (indicator) indicator.textContent = '⚡';
      return;
    }
    const sourceCents = Math.round(sourceValue * 100);
    const targetCents = Math.round(targetValue * 100);
    const basisPoints = Math.max(500, Math.min(9000, Math.floor((sourceCents * 70000) / (targetCents * multiplierTenths))));
    const chancePercent = basisPoints / 100;
    chance.textContent = `${chancePercent.toFixed(2)}%`;
    const success = document.querySelector('[data-upgrade-success]');
    const fail = document.querySelector('[data-upgrade-fail]');
    const ring = document.querySelector('[data-upgrade-ring]');
    if (success) success.textContent = `${chancePercent.toFixed(2)}%`;
    if (fail) fail.textContent = `${(100 - chancePercent).toFixed(2)}%`;
    if (ring) {
      ring.dataset.ready = 'true';
      ring.style.setProperty('--success-angle', `${basisPoints * 0.036}deg`);
    }
    const reactor = document.querySelector('[data-upgrade-reactor]');
    const pointer = document.querySelector('[data-upgrade-pointer]');
    const indicator = document.querySelector('[data-upgrade-indicator]');
    if (reactor) reactor.removeAttribute('data-upgrade-result');
    if (pointer) {
      pointer.style.transition = 'none';
      pointer.style.setProperty('--pointer-angle', '0deg');
    }
    if (indicator) indicator.textContent = '⚡';
  };

  function updateUpgradeSubmit() {
    const form = document.querySelector('[data-animation="upgrade"]');
    const sourceSelected = Boolean(form?.querySelector('[data-selection-input="source"]')?.value);
    const targetSelected = Boolean(form?.querySelector('[data-selection-input="target"]')?.value);
    const button = form?.querySelector('[type="submit"]');
    const label = button?.querySelector('[data-button-label]');
    if (button) button.disabled = !(sourceSelected && targetSelected);
    if (label) label.textContent = sourceSelected && targetSelected
      ? 'INITIATE UPGRADE'
      : 'SELECT BOTH SKINS TO CONTINUE';
  };

  document.querySelectorAll('[data-picker-open]').forEach((button) => {
    button.addEventListener('click', () => {
      const target = button.dataset.pickerOpen || '';
      itemPicker?.setAttribute('data-picker-target', target);
      document.querySelectorAll('[data-picker-item]').forEach((item) => {
        item.hidden = item.dataset.pickerSide !== target;
      });
      filterPickerItems();
      if (typeof itemPicker?.showModal === 'function') itemPicker.showModal();
    });
  });

  document.querySelector('[data-picker-close]')?.addEventListener('click', () => itemPicker?.close());
  itemPicker?.addEventListener('click', (event) => {
    if (event.target === itemPicker) itemPicker.close();
  });
  document.querySelector('[data-picker-search]')?.addEventListener('input', filterPickerItems);
  document.querySelector('[data-picker-rarity]')?.addEventListener('change', filterPickerItems);

  document.querySelectorAll('[data-picker-item]').forEach((button) => {
    button.addEventListener('click', () => {
      const target = itemPicker?.dataset.pickerTarget;
      if (!target) return;
      const image = document.querySelector(`[data-selection-image="${target}"]`);
      const name = document.querySelector(`[data-selection-name="${target}"]`);
      const value = document.querySelector(`[data-selection-value="${target}"]`);
      const input = document.querySelector(`[data-selection-input="${target}"]`);
      if (image && name && value && input) {
        image.src = button.dataset.image;
        image.alt = button.dataset.name;
        image.hidden = false;
        const placeholder = document.querySelector(`[data-selection-placeholder="${target}"]`);
        if (placeholder) placeholder.hidden = true;
        name.textContent = button.dataset.name;
        value.textContent = `${button.dataset.value} credits`;
        input.value = button.dataset.id;
        image.dataset.demoValue = button.dataset.value;
        const rarity = document.querySelector(`[data-selection-rarity="${target}"]`);
        if (rarity) rarity.textContent = button.dataset.rarityLabel || button.dataset.rarity || 'Demo item';
        updateUpgradeChance();
        updateUpgradeSubmit();
      }
      itemPicker?.close();
    });
  });

  document.querySelectorAll('[data-multiplier]').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('[data-multiplier]').forEach((choice) => {
        choice.setAttribute('aria-pressed', String(choice === button));
      });
      const multiplier = document.querySelector('[data-upgrade-multiplier-value]');
      if (multiplier) multiplier.value = button.dataset.multiplier || '1.5';
      updateUpgradeChance();
    });
  });

  document.querySelector('[data-upgrade-reset]')?.addEventListener('click', () => {
    window.setTimeout(() => {
      document.querySelectorAll('[data-selection-image]').forEach((image) => {
        image.hidden = true;
        image.removeAttribute('src');
        delete image.dataset.demoValue;
      });
      document.querySelectorAll('[data-selection-placeholder]').forEach((placeholder) => { placeholder.hidden = false; });
      document.querySelector('[data-selection-name="source"]').textContent = 'Select your item';
      document.querySelector('[data-selection-name="target"]').textContent = 'Select a target';
      document.querySelector('[data-selection-value="source"]').textContent = '— demo points';
      document.querySelector('[data-selection-value="target"]').textContent = '— demo points';
      document.querySelector('[data-selection-rarity="source"]').textContent = 'Available demo skin';
      document.querySelector('[data-selection-rarity="target"]').textContent = 'Demo gallery item';
      document.querySelectorAll('[data-selection-input]').forEach((input) => { input.value = ''; });
      document.querySelectorAll('[data-multiplier]').forEach((button) => {
        button.setAttribute('aria-pressed', String(button.dataset.multiplier === '1.5'));
      });
      const reactor = document.querySelector('[data-upgrade-reactor]');
      const indicator = document.querySelector('[data-upgrade-indicator]');
      if (reactor) reactor.removeAttribute('data-upgrade-result');
      if (indicator) indicator.textContent = '⚡';
      const multiplier = document.querySelector('[data-upgrade-multiplier-value]');
      if (multiplier) multiplier.value = '1.5';
      updateUpgradeChance();
      updateUpgradeSubmit();
      const requestId = document.querySelector('[data-animation="upgrade"] [name=request_id]');
      if (requestId && window.crypto?.randomUUID) requestId.value = window.crypto.randomUUID();
    }, 0);
  });

  // Trade-Up Contracts Counter and Multi-selection
  const updateContractCount = () => {
    const checkboxes = document.querySelectorAll('[data-contract-item]');
    const selected = document.querySelectorAll('[data-contract-item]:checked');
    const count = selected.length;
    const countPill = document.querySelector('[data-contract-count]');
    const countLabel = document.querySelector('[data-contract-count-label]');
    const submitBtn = document.querySelector('[data-contract-submit]');

    if (countPill) countPill.textContent = `${count} / 10 selected (minimum 3)`;
    if (countLabel) {
      if (count < 3) countLabel.textContent = `Select ${3 - count} more item${3 - count === 1 ? '' : 's'} to activate contract`;
      else if (count <= 10) countLabel.textContent = `${count} skins loaded. Ready to combine!`;
    }
    if (submitBtn) submitBtn.disabled = !(count >= 3 && count <= 10);

    checkboxes.forEach((cb) => {
      cb.closest('.contract-item')?.classList.toggle('is-selected', cb.checked);
    });
  };

  document.addEventListener('change', (e) => {
    if (e.target.matches('[data-contract-item]')) {
      const checked = document.querySelectorAll('[data-contract-item]:checked');
      if (checked.length > 10) {
        e.target.checked = false;
        toast('Maksimal 10 ta item tanlash mumkin.', true);
      }
      updateContractCount();
    }
  });
  updateContractCount();

  // Top-Up Wallet and Starter Skin Action Handlers
  document.addEventListener('click', async (e) => {
    const topupBtn = e.target.closest('[data-topup-button]');
    if (topupBtn) {
      e.preventDefault();
      try {
        const payload = new URLSearchParams({ action: 'topup_wallet' });
        const res = await fetch(document.documentElement.dataset.demoActionUrl, {
          method: 'POST',
          body: payload,
          headers: { 'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest' },
        });
        const data = await res.json();
        if (data.ok) {
          playWinChime();
          document.querySelectorAll('[data-demo-balance]').forEach((el) => {
            el.textContent = formatDemoCredits(Number(data.balance));
          });
          toast(data.message || 'Demo hisobingizga +5,000 credits qo‘shildi!');
        } else {
          toast(data.error || 'Balansni to‘ldirishda xatolik', true);
        }
      } catch (err) {
        toast('Balansni to‘ldirishda xatolik yuz berdi.', true);
      }
      return;
    }

    const starterBtn = e.target.closest('[data-get-starter]');
    if (starterBtn) {
      e.preventDefault();
      try {
        const payload = new URLSearchParams({ action: 'get_starter_skin' });
        const res = await fetch(document.documentElement.dataset.demoActionUrl, {
          method: 'POST',
          body: payload,
          headers: { 'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest' },
        });
        const data = await res.json();
        if (data.ok) {
          playWinChime();
          toast(data.message || 'Starter skin inventarga qo‘shildi!');
          window.setTimeout(() => window.location.reload(), 700);
        } else {
          toast(data.error || 'Starter skin olishda xatolik', true);
        }
      } catch (err) {
        toast('Starter skin olishda xatolik yuz berdi.', true);
      }
    }
  });

  document.querySelectorAll('[data-toast]').forEach((button) => {
    button.addEventListener('click', () => toast(button.dataset.toast));
  });
})();
