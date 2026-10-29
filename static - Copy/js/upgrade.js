(function () {
    'use strict';

    const page = document.querySelector('.upgrade-page');
    if (!page) return;

    const fallbackImage = page.dataset.fallbackImage;
    const historyKey = 'skinly-upgrade-demo-history-v1';
    const skinsUrl = page.dataset.skinsUrl;
    const chanceUrl = page.dataset.chanceUrl;
    const panels = {
        source: {
            image: document.getElementById('source-image'),
            name: document.getElementById('source-name'),
            rarity: document.getElementById('source-rarity'),
            price: document.getElementById('source-price'),
            wear: document.getElementById('source-wear'),
        },
        target: {
            image: document.getElementById('target-image'),
            name: document.getElementById('target-name'),
            rarity: document.getElementById('target-rarity'),
            price: document.getElementById('target-price'),
            wear: document.getElementById('target-wear'),
        },
    };
    const result = document.getElementById('upgrade-result');
    const resultTitle = document.getElementById('result-title');
    const resultMessage = document.getElementById('result-message');
    const tryButton = document.getElementById('try-upgrade');
    const historyList = document.getElementById('history-list');
    const historyError = document.getElementById('history-error');
    const catalogGrid = document.getElementById('demo-skin-grid');
    const catalogStatus = document.getElementById('catalog-status');
    const catalogCount = document.getElementById('catalog-count');
    const searchInput = document.getElementById('skin-search');
    const weaponFilter = document.getElementById('weapon-filter');
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const workbench = document.querySelector('.upgrade-workbench');
    const chanceGauge = document.getElementById('chance-gauge');
    const chanceValue = document.getElementById('chance-value');
    const gaugeProgress = document.getElementById('gauge-progress');
    const needle = document.getElementById('gauge-needle');
    let skins = [];
    let skinById = new Map();
    let sourceId = null;
    let targetId = null;
    let activeRole = 'source';
    let chance = null;
    let rolling = false;
    let currentRotation = 0;
    let runId = 0;
    let needleAnimation = null;
    let requestController = null;
    let chanceController = null;
    let chanceRequestId = 0;
    let searchTimer = null;

    function displayError(message) {
        historyError.textContent = message;
        historyError.hidden = false;
    }

    function clearError() {
        historyError.textContent = '';
        historyError.hidden = true;
    }

    function setResult(title, message, state) {
        resultTitle.textContent = title;
        resultMessage.textContent = message;
        result.classList.remove('is-success', 'is-fail', 'is-error', 'result-reveal');
        chanceGauge.classList.toggle('has-success-result', state === 'is-success');
        chanceGauge.classList.toggle('has-fail-result', state === 'is-fail');
        if (state) result.classList.add(state);
    }

    function setCatalogStatus(message, state) {
        catalogStatus.textContent = message;
        catalogStatus.classList.toggle('is-error', state === 'error');
        catalogStatus.hidden = !message;
    }

    function setPanel(role, skin) {
        const panel = panels[role];
        panel.image.onerror = function () {
            panel.image.onerror = null;
            panel.image.src = fallbackImage;
        };
        panel.image.src = skin.image || fallbackImage;
        panel.image.alt = skin.title;
        panel.name.textContent = skin.title;
        panel.rarity.textContent = skin.rarity;
        panel.price.textContent = '$' + skin.price;
        panel.wear.textContent = skin.weapon + ' · ' + skin.wear + ' · demo selection only';
        panel.image.closest('.skin-preview').classList.add('has-skin');
    }

    function clearPanel(role) {
        const panel = panels[role];
        panel.image.onerror = null;
        panel.image.src = fallbackImage;
        panel.image.alt = '';
        panel.name.textContent = role === 'source' ? 'Select your demo skin' : 'Select a target skin';
        panel.rarity.textContent = 'Choose a catalog skin';
        panel.price.textContent = '—';
        panel.wear.textContent = role === 'source'
            ? 'No source item selected · simulation only'
            : 'No target item selected · simulation only';
        panel.image.closest('.skin-preview').classList.remove('has-skin');
    }

    function updatePanels() {
        if (sourceId && skinById.has(sourceId)) setPanel('source', skinById.get(sourceId));
        else clearPanel('source');
        if (targetId && skinById.has(targetId)) setPanel('target', skinById.get(targetId));
        else clearPanel('target');
    }

    function updateSelectionButtons() {
        catalogGrid.querySelectorAll('.select-skin-button').forEach((button) => {
            const id = button.dataset.skinId;
            const selectedId = button.dataset.role === 'source' ? sourceId : targetId;
            const otherId = button.dataset.role === 'source' ? targetId : sourceId;
            const selected = id === selectedId;
            button.classList.toggle('is-selected', selected);
            button.setAttribute('aria-pressed', String(selected));
            button.disabled = Boolean(otherId && id === otherId);
            button.title = button.disabled ? 'Choose a different skin for each side.' : '';
        });
        catalogGrid.querySelectorAll('.demo-skin-card').forEach((card) => {
            card.classList.toggle('is-source', card.dataset.skinId === sourceId);
            card.classList.toggle('is-target', card.dataset.skinId === targetId);
        });
    }

    function updateTryButton() {
        const sourceValid = sourceId && skinById.has(sourceId);
        const targetValid = targetId && skinById.has(targetId);
        tryButton.disabled = rolling || chance === null || !sourceValid || !targetValid || sourceId === targetId;
    }

    function formatChance(value) {
        return new Intl.NumberFormat(undefined, {maximumFractionDigits: 0}).format(Math.round(value)) + '%';
    }

    function setChance(value) {
        const numericChance = value === null ? null : Number(value);
        if (numericChance !== null && (!Number.isFinite(numericChance) || numericChance <= 0 || numericChance > 100)) {
            chance = null;
            chanceGauge.style.setProperty('--chance', '0');
            chanceGauge.style.setProperty('--chance-color', '#64748b');
            chanceGauge.setAttribute('aria-label', 'Chance unavailable because a skin price is invalid.');
            chanceValue.textContent = '—';
            gaugeProgress.style.strokeDashoffset = '471.24';
            return;
        }

        chance = numericChance;
        const color = chance === null ? '#64748b'
            : chance >= 75 ? '#22C55E'
                : chance >= 50 ? '#FACC15'
                    : '#EF4444';
        chanceGauge.style.setProperty('--chance', chance === null ? '0' : String(chance));
        chanceGauge.style.setProperty('--chance-color', color);
        chanceValue.textContent = chance === null ? '—' : formatChance(chance);
        chanceGauge.setAttribute(
            'aria-label',
            chance === null ? 'Chance unavailable until both skins are selected.'
                : 'Illustrative probability ' + chanceValue.textContent
        );
        gaugeProgress.style.strokeDashoffset = String(471.24 * (1 - (chance || 0) / 100));
        if (!rolling) {
            currentRotation = chance === null ? 0 : chance / 100 * 360;
            needle.style.transform = 'rotate(' + currentRotation + 'deg)';
        }
    }

    function updatePairMessage() {
        if (rolling) return;
        if (!sourceId || !targetId) {
            const missing = [];
            if (!sourceId) missing.push('your skin');
            if (!targetId) missing.push('a target skin');
            setResult('Choose both skins', 'Select ' + missing.join(' and ') + ' to start the free simulation.', 'is-error');
        } else if (sourceId === targetId) {
            setResult('Choose another target', 'The source and target must be different catalog skins.', 'is-error');
        } else if (chance === null) {
            setResult('Calculating chance', 'Checking both current skin prices from the catalog.', '');
        } else {
            setResult('Ready when you are', 'Price-based demo chance: ' + chanceValue.textContent + '. Free simulation only.', '');
        }
    }

    async function recalculateChance() {
        const requestId = ++chanceRequestId;
        if (chanceController) chanceController.abort();
        chanceController = null;

        if (!sourceId || !targetId || sourceId === targetId) {
            setChance(null);
            updateTryButton();
            updatePairMessage();
            return;
        }

        setChance(null);
        updateTryButton();
        updatePairMessage();
        chanceController = new AbortController();
        const query = new URLSearchParams({source_id: sourceId, target_id: targetId});
        try {
            const response = await fetch(chanceUrl + '?' + query.toString(), {
                headers: {'Accept': 'application/json'},
                signal: chanceController.signal,
            });
            const payload = await response.json();
            if (requestId !== chanceRequestId) return;
            if (!response.ok) throw new Error(payload.error || 'Could not calculate the upgrade chance.');
            if (String(payload.source_id) !== sourceId || String(payload.target_id) !== targetId) {
                throw new Error('The chance response did not match the selected skins.');
            }
            const source = skinById.get(sourceId);
            const target = skinById.get(targetId);
            if (!source || !target || Number(payload.source_price) <= 0 || Number(payload.target_price) <= 0) {
                throw new Error('Both selected skins must have valid prices greater than zero.');
            }
            if (!Number.isFinite(Number(payload.chance)) || Number(payload.chance) <= 0 || Number(payload.chance) > 100) {
                throw new Error('The catalog returned an invalid upgrade probability.');
            }
            source.price = payload.source_price;
            target.price = payload.target_price;
            panels.source.price.textContent = '$' + payload.source_price;
            panels.target.price.textContent = '$' + payload.target_price;
            setChance(payload.chance);
            updateTryButton();
            updatePairMessage();
            clearError();
        } catch (error) {
            if (error.name === 'AbortError' || requestId !== chanceRequestId) return;
            setChance(null);
            updateTryButton();
            displayError(error.message || 'Could not calculate the upgrade chance.');
            setResult('Chance unavailable', error.message || 'Could not verify current skin prices.', 'is-error');
        }
    }

    function buildSkinCard(skin) {
        const card = document.createElement('article');
        card.className = 'demo-skin-card';
        card.dataset.skinId = String(skin.id);

        const imageWrap = document.createElement('div');
        imageWrap.className = 'catalog-image';
        const image = document.createElement('img');
        image.src = skin.image || fallbackImage;
        image.alt = skin.title;
        image.loading = 'lazy';
        image.onerror = function () {
            image.onerror = null;
            image.src = fallbackImage;
        };
        imageWrap.append(image);

        const info = document.createElement('div');
        info.className = 'catalog-card-info';
        const title = document.createElement('h3');
        title.textContent = skin.title;
        const details = document.createElement('span');
        details.textContent = skin.rarity + ' · ' + skin.wear;
        const weapon = document.createElement('span');
        weapon.textContent = skin.weapon;
        const price = document.createElement('strong');
        price.textContent = '$' + skin.price;
        info.append(title, details, weapon, price);

        const actions = document.createElement('div');
        actions.className = 'catalog-card-actions';
        [['source', 'Your skin', false], ['target', 'Target', true]].forEach(([role, label, isTarget]) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'select-skin-button' + (isTarget ? ' target-select' : '');
            button.dataset.role = role;
            button.dataset.skinId = String(skin.id);
            button.textContent = label;
            button.addEventListener('click', () => selectSkin(role, String(skin.id)));
            actions.append(button);
        });
        card.addEventListener('click', (event) => {
            if (!event.target.closest('button')) selectSkin(activeRole, String(skin.id));
        });
        card.append(imageWrap, info, actions);
        return card;
    }

    function renderSkins() {
        catalogGrid.replaceChildren();
        if (!skins.length) {
            setCatalogStatus('No catalog skins match these filters. Try a different search or price range.', 'empty');
            catalogCount.textContent = '0 catalog skins';
            updatePanels();
            updateTryButton();
            return;
        }
        setCatalogStatus('', '');
        catalogCount.textContent = skins.length + ' catalog skin' + (skins.length === 1 ? '' : 's');
        const fragment = document.createDocumentFragment();
        skins.forEach((skin) => fragment.append(buildSkinCard(skin)));
        catalogGrid.append(fragment);
        updateSelectionButtons();
        updatePanels();
        updateTryButton();
    }

    function populateWeaponOptions(weapons) {
        const current = weaponFilter.value;
        weaponFilter.replaceChildren();
        const all = document.createElement('option');
        all.value = '';
        all.textContent = 'All weapons';
        weaponFilter.append(all);
        weapons.forEach((weapon) => {
            const option = document.createElement('option');
            option.value = weapon;
            option.textContent = weapon;
            weaponFilter.append(option);
        });
        weaponFilter.value = weapons.includes(current) ? current : '';
    }

    async function loadSkins() {
        if (requestController) requestController.abort();
        requestController = new AbortController();
        const query = new URLSearchParams();
        const search = searchInput.value.trim();
        const weapon = weaponFilter.value;
        const minPrice = minPriceInput.value.trim();
        const maxPrice = maxPriceInput.value.trim();
        if (search) query.set('q', search);
        if (weapon) query.set('weapon', weapon);
        if (minPrice) query.set('min_price', minPrice);
        if (maxPrice) query.set('max_price', maxPrice);

        setCatalogStatus('Loading catalog skins…', 'loading');
        catalogGrid.replaceChildren();
        try {
            const response = await fetch(skinsUrl + (query.size ? '?' + query.toString() : ''), {
                headers: {'Accept': 'application/json'},
                signal: requestController.signal,
            });
            const payload = await response.json();
            if (!response.ok) throw new Error(payload.error || 'Could not load catalog skins.');
            if (!payload || !Array.isArray(payload.skins) || !Array.isArray(payload.weapons)) {
                throw new Error('The skin catalog returned an invalid response.');
            }
            skins = payload.skins;
            skins.forEach((skin) => skinById.set(String(skin.id), skin));
            populateWeaponOptions(payload.weapons);
            renderSkins();
            clearError();
            if ((sourceId && !skinById.has(sourceId)) || (targetId && !skinById.has(targetId))) {
                updateTryButton();
            }
            updatePairMessage();
        } catch (error) {
            if (error.name === 'AbortError') return;
            setCatalogStatus(error.message || 'Could not load catalog skins. Please try again.', 'error');
            catalogGrid.replaceChildren();
            displayError(error.message || 'Catalog loading failed. Please try again.');
        }
    }

    function selectSkin(role, id) {
        if (rolling) return;
        if (!skinById.has(id)) {
            displayError('That catalog skin is no longer available. Refresh the catalog and try again.');
            return;
        }
        if ((role === 'source' && id === targetId) || (role === 'target' && id === sourceId)) {
            setResult('Choose another skin', 'The source and target must be different catalog skins.', 'is-error');
            return;
        }
        if (role === 'source') sourceId = id;
        else targetId = id;
        clearError();
        updateSelectionButtons();
        updatePanels();
        updateTryButton();
        recalculateChance();
    }

    function readHistory() {
        try {
            const stored = window.localStorage.getItem(historyKey);
            if (!stored) return [];
            const history = JSON.parse(stored);
            if (!Array.isArray(history)) throw new Error('Invalid demo history');
            return history.slice(0, 8);
        } catch (error) {
            displayError('Demo history could not be read from this browser. You can still run the simulation.');
            return [];
        }
    }

    function renderHistory() {
        const history = readHistory();
        historyList.replaceChildren();
        if (!history.length) {
            const empty = document.createElement('div');
            empty.className = 'history-empty';
            const icon = document.createElement('span');
            icon.className = 'history-empty-icon';
            icon.textContent = '↻';
            const title = document.createElement('strong');
            title.textContent = 'No demo attempts yet';
            const hint = document.createElement('span');
            hint.textContent = 'Your simulation results will appear here.';
            empty.append(icon, title, hint);
            historyList.append(empty);
            return;
        }
        history.forEach((entry) => {
            const row = document.createElement('div');
            row.className = 'history-entry';
            const pair = document.createElement('div');
            pair.className = 'history-pair';
            pair.append(document.createTextNode(entry.source + ' '));
            const arrow = document.createElement('span');
            arrow.textContent = '→';
            pair.append(arrow, document.createTextNode(' ' + entry.target));
            const meta = document.createElement('span');
            meta.className = 'history-meta';
            const recordedChance = Number(entry.chance);
            const chanceLabel = Number.isFinite(recordedChance)
                ? formatChance(recordedChance)
                : entry.chance_label || '—';
            meta.textContent = chanceLabel + ' chance · ' + new Date(entry.timestamp).toLocaleString();
            const outcome = document.createElement('span');
            outcome.className = 'history-outcome ' + (entry.success ? 'is-success' : 'is-fail');
            outcome.textContent = entry.success ? 'SIMULATED SUCCESS' : 'TRY AGAIN';
            row.append(pair, meta, outcome);
            historyList.append(row);
        });
    }

    function saveAttempt(attempt) {
        try {
            const updated = [attempt, ...readHistory()].slice(0, 8);
            window.localStorage.setItem(historyKey, JSON.stringify(updated));
            clearError();
            renderHistory();
        } catch (error) {
            displayError('The simulation completed, but this browser could not save demo history.');
        }
    }

    function secureRoll() {
        if (!window.crypto || typeof window.crypto.getRandomValues !== 'function') {
            throw new Error('Secure random numbers are unavailable. Open this page over HTTPS or localhost to use the demo.');
        }
        const limit = Math.floor(0x100000000 / 10000) * 10000;
        const value = new Uint32Array(1);
        do {
            window.crypto.getRandomValues(value);
        } while (value[0] >= limit);
        return value[0];
    }

    async function animateNeedle(finalRoll, thisRun) {
        const finalAngle = finalRoll / 0x100000000 * 360;
        const currentAngle = ((currentRotation % 360) + 360) % 360;
        const endRotation = currentRotation + 360 * 5 + ((finalAngle - currentAngle + 360) % 360);
        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (reduceMotion || typeof needle.animate !== 'function') {
            currentRotation = endRotation;
            needle.style.transform = 'rotate(' + endRotation + 'deg)';
            return thisRun === runId;
        }
        needleAnimation = needle.animate(
            [{transform: 'rotate(' + currentRotation + 'deg)'}, {transform: 'rotate(' + endRotation + 'deg)'}],
            {duration: 4800, easing: 'cubic-bezier(.12,.72,.12,1)', fill: 'forwards'}
        );
        try {
            await needleAnimation.finished;
        } catch (error) {
            if (thisRun === runId) throw error;
            return false;
        }
        if (thisRun !== runId) return false;
        currentRotation = endRotation;
        needle.style.transform = 'rotate(' + endRotation + 'deg)';
        needleAnimation.cancel();
        needleAnimation = null;
        return true;
    }

    async function runDemo() {
        if (rolling) return;
        if (!sourceId || !targetId || chance === null) {
            updatePairMessage();
            return;
        }
        if (sourceId === targetId) {
            setResult('Choose another target', 'The source and target must be different catalog skins.', 'is-error');
            return;
        }
        const source = skinById.get(sourceId);
        const target = skinById.get(targetId);
        if (!source || !target) {
            setResult('Refresh the catalog', 'A selected skin is no longer in the current catalog results.', 'is-error');
            return;
        }
        let roll;
        try {
            roll = secureRoll();
        } catch (error) {
            displayError(error.message);
            setResult('Simulation unavailable', error.message, 'is-error');
            return;
        }
        const thisRun = ++runId;
        const attemptChance = chance;
        rolling = true;
        updateTryButton();
        tryButton.querySelector('span').textContent = 'Simulating…';
        workbench.classList.add('is-rolling');
        setResult('Simulation in progress', 'The needle is spinning. No real item or balance is involved.', '');
        try {
            const finished = await animateNeedle(roll, thisRun);
            if (!finished || thisRun !== runId) return;
            const success = roll / 0x100000000 * 100 < attemptChance;
            setResult(
                success ? 'UPGRADE SUCCESS!' : 'UPGRADE FAILED',
                success
                    ? 'Target: ' + target.title + ' · Simulation only; no skin was awarded and no inventory changed.'
                    : 'Simulation only — no skin was lost and no balance changed.',
                success ? 'is-success' : 'is-fail'
            );
            result.classList.add('result-reveal');
            saveAttempt({
                source: source.title,
                target: target.title,
                chance: attemptChance,
                chance_label: chanceValue.textContent,
                success: success,
                timestamp: new Date().toISOString(),
            });
        } catch (error) {
            if (thisRun === runId) {
                displayError('The demo animation could not finish. Please try again.');
                setResult('Simulation error', 'No real items or balance were changed.', 'is-error');
            }
        } finally {
            if (thisRun === runId) {
                rolling = false;
                workbench.classList.remove('is-rolling');
                tryButton.querySelector('span').textContent = 'Try Demo';
                updateTryButton();
            }
        }
    }

    document.querySelectorAll('[data-choose-role]').forEach((button) => {
        button.addEventListener('click', () => {
            if (rolling) return;
            activeRole = button.dataset.chooseRole;
            searchInput.focus({preventScroll: true});
            document.getElementById('demo-skin-grid').scrollIntoView({behavior: 'smooth', block: 'center'});
            setCatalogStatus('Choose a skin below for ' + (activeRole === 'source' ? 'Your Skin.' : 'Target Skin.'), 'info');
        });
    });

    document.getElementById('filter-skins').addEventListener('click', loadSkins);
    searchInput.addEventListener('input', () => {
        window.clearTimeout(searchTimer);
        searchTimer = window.setTimeout(loadSkins, 250);
    });
    weaponFilter.addEventListener('change', loadSkins);
    [minPriceInput, maxPriceInput].forEach((input) => {
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') loadSkins();
        });
    });
    tryButton.addEventListener('click', runDemo);

    document.getElementById('reset-upgrade').addEventListener('click', () => {
        runId += 1;
        if (needleAnimation) {
            needleAnimation.cancel();
            needleAnimation = null;
        }
        rolling = false;
        workbench.classList.remove('is-rolling');
        currentRotation = 0;
        needle.style.transform = 'rotate(0deg)';
        sourceId = null;
        targetId = null;
        if (chanceController) chanceController.abort();
        chanceController = null;
        chanceRequestId += 1;
        setChance(null);
        tryButton.querySelector('span').textContent = 'Try Demo';
        clearError();
        try {
            window.localStorage.removeItem(historyKey);
        } catch (error) {
            displayError('Demo settings were reset, but browser history could not be cleared.');
        }
        updateSelectionButtons();
        updatePanels();
        updateTryButton();
        setResult('Choose your skins', 'Select both skins to start the free simulation.', '');
        renderHistory();
    });

    setChance(null);
    updatePanels();
    updateTryButton();
    renderHistory();
    loadSkins();
}());
