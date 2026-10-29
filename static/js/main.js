// Skinly CS2 Interactive Scripts & Real Transaction Engine

document.addEventListener('error', (event) => {
    const image = event.target;
    if (!(image instanceof HTMLImageElement) || image.dataset.placeholderFallback) return;
    if (new URL(image.src, window.location.origin).pathname === '/static/images/placeholder.svg') return;
    image.dataset.placeholderFallback = 'true';
    image.src = '/static/images/placeholder.svg';
}, true);

// Central State Management
const STATE = {
    balance: null,       // e.g. 1000200.00
    balanceCents: null,  // e.g. 100020000 (integer cents to eliminate floating-point bugs)
    cart: JSON.parse(localStorage.getItem('buldrop_cart')) || [],
    favorites: JSON.parse(localStorage.getItem('buldrop_favorites')) || [],
    theme: localStorage.getItem('buldrop_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),
    isPurchasing: false  // Global double-click/double-purchase lock
};

function saveState(key) {
    if (key === 'theme') {
        localStorage.setItem(`buldrop_${key}`, STATE[key]);
    } else {
        localStorage.setItem(`buldrop_${key}`, JSON.stringify(STATE[key]));
    }
}

function safeImageSource(value) {
    if (typeof value !== 'string' || !value) return '/static/images/placeholder.svg';
    try {
        const url = new URL(value, window.location.origin);
        if (url.protocol === 'https:' || url.origin === window.location.origin) return url.href;
    } catch (error) {
        console.warn('Ignored invalid image URL.');
    }
    return '/static/images/placeholder.svg';
}

// --- CSRF Helper ---
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content && meta.content.length > 10) return meta.content;
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input && input.value) return input.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
}

// --- Currency Formatting ---
function formatCurrency(amount) {
    const num = Number(amount);
    if (isNaN(num)) return '$0.00';
    return '$' + num.toFixed(2);
}

// --- Balance Management & Realtime Sync ---
function initBalance() {
    const headerEl = document.getElementById('header-user-balance');
    if (headerEl && headerEl.dataset.balance !== undefined && headerEl.dataset.balance !== '') {
        const val = parseFloat(headerEl.dataset.balance);
        if (!isNaN(val)) {
            STATE.balance = val;
            STATE.balanceCents = Math.round(val * 100);
            localStorage.setItem('buldrop_balance_cents', STATE.balanceCents);
        }
    } else {
        const cachedCents = localStorage.getItem('buldrop_balance_cents');
        if (cachedCents !== null) {
            STATE.balanceCents = parseInt(cachedCents, 10);
            STATE.balance = STATE.balanceCents / 100;
        }
    }
    updateBalanceUI();
    // Async background sync with source of truth (DB)
    fetchBalance();
}

async function fetchBalance() {
    try {
        const res = await fetch('/api/balance/');
        if (res.ok) {
            const data = await res.json();
            if (data.authenticated) {
                setBalance(data.balance);
            }
        }
    } catch (e) {
        console.warn('Balance background sync warning:', e);
    }
}

function setBalance(newBalance) {
    const num = Number(newBalance);
    if (isNaN(num)) return;
    STATE.balance = num;
    STATE.balanceCents = Math.round(num * 100);
    localStorage.setItem('buldrop_balance_cents', STATE.balanceCents);
    updateBalanceUI(true);
}

function updateBalanceUI(highlight = false) {
    if (STATE.balance === null) return;
    const formatted = formatCurrency(STATE.balance);

    const headerEl = document.getElementById('header-user-balance');
    if (headerEl) {
        headerEl.innerText = formatted;
        headerEl.dataset.balance = STATE.balance;
    }

    const mobileEl = document.getElementById('mobile-user-balance');
    if (mobileEl) {
        mobileEl.innerText = formatted;
    }

    if (highlight) {
        const card = document.getElementById('header-balance-card');
        if (card) {
            card.classList.add('ring-2', 'ring-emerald-400', 'bg-emerald-950/60');
            setTimeout(() => {
                card.classList.remove('ring-2', 'ring-emerald-400', 'bg-emerald-950/60');
            }, 1200);
        }
    }
}

// --- Theme Management ---
function applyTheme() {
    const htmlClass = document.documentElement.classList;
    if (STATE.theme === 'dark') {
        htmlClass.add('dark');
        htmlClass.remove('light');
    } else {
        htmlClass.add('light');
        htmlClass.remove('dark');
    }
    updateThemeIcon();
}

function toggleTheme() {
    STATE.theme = STATE.theme === 'dark' ? 'light' : 'dark';
    saveState('theme');
    applyTheme();
}

function updateThemeIcon() {
    const icon = document.getElementById('theme-toggle-icon');
    if (icon) {
        if (STATE.theme === 'dark') {
            icon.setAttribute('data-lucide', 'sun');
            icon.classList.replace('text-slate-400', 'text-amber-400');
        } else {
            icon.setAttribute('data-lucide', 'moon');
            icon.classList.replace('text-amber-400', 'text-slate-600');
        }
        if (window.lucide) window.lucide.createIcons();
    }
}

// --- Favorites Management ---
async function toggleFavorite(id, title, price, image) {
    const idx = STATE.favorites.findIndex(item => String(item.id) === String(id));
    if (window.skinlyAuthenticated) {
        try {
            const body = new URLSearchParams({ product_id: String(id) });
            const response = await fetch(window.skinlyFavoriteUrl, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/x-www-form-urlencoded' },
                body
            });
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || 'Favorite could not be saved.');
            if (result.is_favorite && idx === -1) {
                STATE.favorites.push({ id, title, price, image });
                showToast('Skin sevimlilarga qo\'shildi', 'success');
            } else if (!result.is_favorite && idx > -1) {
                STATE.favorites.splice(idx, 1);
                showToast('Skin sevimlilardan o\'chirildi', 'info');
            }
        } catch (error) {
            showToast('Sevimli skinni saqlab bo\'lmadi. Qayta urinib ko\'ring.', 'error');
            console.error('Favorite sync failed:', error);
            return;
        }
    } else if (idx > -1) {
        STATE.favorites.splice(idx, 1);
        showToast('Skin sevimlilardan o\'chirildi', 'info');
    } else {
        STATE.favorites.push({ id, title, price, image });
        showToast('Skin sevimlilarga qo\'shildi', 'success');
    }
    saveState('favorites');
    updateFavoritesUI();
    renderFavoritesSidebar();
}

async function syncFavoritesToAccount() {
    if (!window.skinlyAuthenticated) return;
    const syncKey = `skinly_favorites_synced_${window.skinlyUsername || 'account'}`;
    const favoriteIds = STATE.favorites.map(item => String(item.id));
    const fingerprint = favoriteIds.join(',');
    if (sessionStorage.getItem(syncKey) === fingerprint) return;
    try {
        const body = new URLSearchParams({
            operation: 'sync',
            product_ids: fingerprint
        });
        const response = await fetch(window.skinlyFavoriteUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrfToken(), 'Content-Type': 'application/x-www-form-urlencoded' },
            body
        });
        const result = await response.json();
        if (!response.ok || !result.success) throw new Error(result.error || 'Favorite sync failed.');
        sessionStorage.setItem(syncKey, fingerprint);
    } catch (error) {
        console.error('Favorite sync failed:', error);
    }
}

function updateFavoritesUI() {
    const count = STATE.favorites.length;
    document.querySelectorAll('.favorites-count-badge').forEach(el => {
        el.innerText = count;
        el.style.display = count > 0 ? 'flex' : 'none';
    });

    document.querySelectorAll('.btn-favorite').forEach(btn => {
        const id = btn.getAttribute('data-id');
        const icon = btn.querySelector('i');
        if (icon) {
            if (STATE.favorites.find(item => String(item.id) === String(id))) {
                icon.classList.add('fill-rose-500', 'text-rose-500');
                icon.classList.remove('text-slate-400');
            } else {
                icon.classList.remove('fill-rose-500', 'text-rose-500');
                icon.classList.add('text-slate-400');
            }
        }
    });
}

function openFavorites() {
    const sidebar = document.getElementById('favorites-sidebar');
    if (sidebar) sidebar.classList.remove('translate-x-full');
    renderFavoritesSidebar();
}

function closeFavorites() {
    const sidebar = document.getElementById('favorites-sidebar');
    if (sidebar) sidebar.classList.add('translate-x-full');
}

function renderFavoritesSidebar() {
    const container = document.getElementById('favorites-items-container');
    if (!container) return;
    container.replaceChildren();

    if (STATE.favorites.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'flex flex-col items-center justify-center h-full text-slate-500 space-y-3';
        empty.innerHTML = '<i data-lucide="heart" class="w-12 h-12 mb-2 opacity-50"></i>';
        const text = document.createElement('p');
        text.className = 'text-sm font-medium';
        text.textContent = "Sevimlilar ro'yxati bo'sh";
        empty.appendChild(text);
        container.appendChild(empty);
        if (window.lucide) window.lucide.createIcons();
        return;
    }

    STATE.favorites.forEach(item => {
        const row = document.createElement('div');
        row.className = 'flex items-center gap-3 p-3 bg-csdark-900 rounded-xl border border-white/5 relative group';
        const image = document.createElement('img');
        image.src = safeImageSource(item.image);
        image.alt = String(item.title || '');
        image.className = 'w-14 h-14 object-contain bg-csdark-950 rounded-lg p-1';
        image.onerror = () => { image.src = '/static/images/placeholder.svg'; };
        const details = document.createElement('div');
        details.className = 'flex-1';
        const title = document.createElement('h4');
        title.className = 'text-xs font-bold text-white line-clamp-1';
        title.textContent = String(item.title || '');
        const price = document.createElement('p');
        price.className = 'text-xs font-extrabold text-orange-400 mt-1';
        price.textContent = `$${String(item.price || '')}`;
        details.append(title, price);
        const remove = document.createElement('button');
        remove.className = 'text-slate-500 hover:text-rose-500 transition-colors p-1';
        remove.type = 'button';
        remove.setAttribute('aria-label', 'Remove from favorites');
        remove.innerHTML = '<i data-lucide="trash-2" class="w-4 h-4"></i>';
        remove.addEventListener('click', () => toggleFavorite(item.id, '', '', ''));
        row.append(image, details, remove);
        container.appendChild(row);
    });
    if (window.lucide) window.lucide.createIcons();
}

// --- Cart Management ---
function addToCart(id, title, price, image) {
    const parsedPrice = parseFloat(price);
    const idx = STATE.cart.findIndex(item => String(item.id) === String(id));
    if (idx > -1) {
        STATE.cart[idx].qty += 1;
    } else {
        STATE.cart.push({ id, title, price: isNaN(parsedPrice) ? 0 : parsedPrice, image, qty: 1 });
    }
    saveState('cart');
    updateCartUI();
    showToast('Savatchaga qo\'shildi!', 'success');
}

function updateCartQuantity(id, delta) {
    const idx = STATE.cart.findIndex(item => String(item.id) === String(id));
    if (idx > -1) {
        STATE.cart[idx].qty += delta;
        if (STATE.cart[idx].qty <= 0) {
            STATE.cart.splice(idx, 1);
        }
        saveState('cart');
        updateCartUI();
        renderCartSidebar();
    }
}

function clearCart() {
    STATE.cart = [];
    saveState('cart');
    updateCartUI();
    renderCartSidebar();
}

function updateCartUI() {
    const count = STATE.cart.reduce((sum, item) => sum + item.qty, 0);
    document.querySelectorAll('.cart-count-badge').forEach(el => {
        el.innerText = count;
        el.style.display = count > 0 ? 'flex' : 'none';
    });
}

function openCart() {
    const sidebar = document.getElementById('cart-sidebar');
    if (sidebar) sidebar.classList.remove('translate-x-full');
    renderCartSidebar();
}

function closeCart() {
    const sidebar = document.getElementById('cart-sidebar');
    if (sidebar) sidebar.classList.add('translate-x-full');
}

function renderCartSidebar() {
    const container = document.getElementById('cart-items-container');
    const footer = document.getElementById('cart-footer');
    if (!container || !footer) return;

    if (STATE.cart.length === 0) {
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-slate-500 space-y-3">
                <i data-lucide="shopping-cart" class="w-12 h-12 mb-2 opacity-50"></i>
                <p class="text-sm font-medium">Savatcha bo'sh</p>
                <button onclick="closeCart()" class="mt-4 px-4 py-2 bg-orange-500 text-black text-xs font-bold rounded-xl hover:bg-orange-400">Haridni davom ettirish</button>
            </div>
        `;
        footer.classList.add('hidden');
        if (window.lucide) window.lucide.createIcons();
        return;
    }

    footer.classList.remove('hidden');
    container.innerHTML = STATE.cart.map(item => `
        <div class="flex items-center gap-3 p-3 bg-csdark-900 rounded-xl border border-white/5 relative group">
            <img src="${item.image}" alt="${item.title}" class="w-14 h-14 object-contain bg-csdark-950 rounded-lg p-1" onerror="this.src='/static/images/placeholder.png'">
            <div class="flex-1">
                <h4 class="text-xs font-bold text-white line-clamp-1">${item.title}</h4>
                <p class="text-xs font-extrabold text-emerald-400 mt-1">$${(item.price).toFixed(2)}</p>
                <div class="flex items-center space-x-2 mt-2">
                    <button onclick="updateCartQuantity('${item.id}', -1)" class="w-6 h-6 rounded-md bg-white/10 text-white flex items-center justify-center hover:bg-orange-500 hover:text-black">-</button>
                    <span class="text-xs font-bold w-4 text-center">${item.qty}</span>
                    <button onclick="updateCartQuantity('${item.id}', 1)" class="w-6 h-6 rounded-md bg-white/10 text-white flex items-center justify-center hover:bg-orange-500 hover:text-black">+</button>
                </div>
            </div>
            <button onclick="updateCartQuantity('${item.id}', -999)" class="text-slate-500 hover:text-rose-500 transition-colors p-1 self-start">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        </div>
    `).join('');

    const subtotal = STATE.cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
    const formattedSubtotal = '$' + subtotal.toFixed(2);
    const subtotalEl = document.getElementById('cart-subtotal');
    const totalEl = document.getElementById('cart-total');
    if (subtotalEl) subtotalEl.innerText = formattedSubtotal;
    if (totalEl) totalEl.innerText = formattedSubtotal;

    if (window.lucide) window.lucide.createIcons();
}

// --- Checkout Modal ---
function openCheckoutModal() {
    if (STATE.cart.length === 0) return;
    closeCart();

    const modal = document.getElementById('checkout-modal');
    if (!modal) return;

    const summary = document.getElementById('checkout-summary');
    if (summary) {
        summary.innerHTML = STATE.cart.map(item => `
            <div class="flex justify-between text-xs mb-1">
                <span class="text-slate-300 truncate max-w-[240px]">${item.qty}x ${item.title}</span>
                <span class="text-emerald-400 font-bold font-mono">$${(item.price * item.qty).toFixed(2)}</span>
            </div>
        `).join('');
    }

    const subtotal = STATE.cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
    const checkoutTotal = document.getElementById('checkout-total');
    if (checkoutTotal) checkoutTotal.innerText = '$' + subtotal.toFixed(2);

    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeCheckoutModal() {
    const modal = document.getElementById('checkout-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

// --- Double-Purchase Protected Cart Checkout ---
async function submitCheckout(e) {
    if (e && e.preventDefault) e.preventDefault();

    if (STATE.cart.length === 0) {
        showToast('Savatchangiz bo\'sh!', 'error');
        return;
    }

    if (STATE.isPurchasing) return; // Prevent double trigger

    // Calculate cart total in cents
    const cartTotalCents = STATE.cart.reduce((sum, item) => {
        const itemCents = Math.round((parseFloat(item.price) || 0) * 100);
        return sum + (itemCents * (item.qty || 1));
    }, 0);

    // Front-end pre-check for fast feedback
    if (STATE.balanceCents !== null && STATE.balanceCents < cartTotalCents) {
        showToast('Balans yetarli emas! Hamyonni to\'ldiring.', 'error');
        return;
    }

    const btn = document.getElementById('checkout-submit-btn');
    const originalText = btn ? btn.innerHTML : '';
    STATE.isPurchasing = true;

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i data-lucide="loader" class="w-4 h-4 animate-spin mr-1.5"></i> <span>Buying...</span>';
        if (window.lucide) window.lucide.createIcons();
    }

    const payload = {
        items: STATE.cart.map(item => ({ id: item.id, qty: item.qty })),
        full_name: document.getElementById('checkout-name')?.value || '',
        phone: document.getElementById('checkout-phone')?.value || '',
        steam_trade_url: document.getElementById('checkout-trade-url')?.value || '',
    };

    try {
        const response = await fetch('/api/purchase/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            const errorMsg = data.error || 'Xarid amalga oshmadi!';
            showToast(errorMsg, 'error');
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalText;
                if (window.lucide) window.lucide.createIcons();
            }
            STATE.isPurchasing = false;
            return;
        }

        // Purchase Success: update balance, clear cart, show modal
        setBalance(data.new_balance);
        clearCart();
        closeCheckoutModal();

        if (btn) {
            btn.innerHTML = '<i data-lucide="check" class="w-4 h-4 mr-1.5"></i> <span>Purchased ✓</span>';
            if (window.lucide) window.lucide.createIcons();
        }

        showPurchaseSuccessModal(data.skin_title, data.price_formatted, data.new_balance_formatted);
        showToast('Buyurtma muvaffaqiyatli qabul qilindi! Balansdan yechildi.', 'success');

        setTimeout(() => {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalText;
                if (window.lucide) window.lucide.createIcons();
            }
            STATE.isPurchasing = false;
        }, 1500);

    } catch (err) {
        console.error('Checkout error:', err);
        showToast('Server bilan aloqa uzildi. Pul yechilmadi.', 'error');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalText;
            if (window.lucide) window.lucide.createIcons();
        }
        STATE.isPurchasing = false;
    }
}

// --- Double-Purchase Protected Instant Single Skin Purchase ---
async function buySkin(productId, btnElement) {
    if (!productId) return;

    if (STATE.isPurchasing) return; // Prevent double click
    if (btnElement && btnElement.disabled) return;

    // Check client balance first if known
    if (btnElement && btnElement.dataset.price && STATE.balanceCents !== null) {
        const priceCents = Math.round(parseFloat(btnElement.dataset.price) * 100);
        if (STATE.balanceCents < priceCents) {
            showToast('Balans yetarli emas!', 'error');
            return;
        }
    }

    STATE.isPurchasing = true;
    let originalHtml = '';

    if (btnElement) {
        btnElement.disabled = true;
        originalHtml = btnElement.innerHTML;
        btnElement.innerHTML = '<i data-lucide="loader" class="w-3.5 h-3.5 animate-spin"></i> <span>Buying...</span>';
        if (window.lucide) window.lucide.createIcons();
    }

    try {
        const response = await fetch('/api/purchase/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            const errorMsg = data.error || 'Xarid amalga oshmadi!';
            showToast(errorMsg, 'error');

            if (btnElement) {
                btnElement.disabled = false;
                btnElement.innerHTML = originalHtml;
                if (window.lucide) window.lucide.createIcons();
            }
            STATE.isPurchasing = false;
            return;
        }

        // Purchase succeeded
        setBalance(data.new_balance);

        if (btnElement) {
            btnElement.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5 text-black"></i> <span>Purchased ✓</span>';
            btnElement.classList.remove('bg-gradient-to-r', 'from-orange-500', 'to-amber-500');
            btnElement.classList.add('bg-emerald-400', 'text-black');
            if (window.lucide) window.lucide.createIcons();
        }

        showPurchaseSuccessModal(data.skin_title, data.price_formatted, data.new_balance_formatted);
        showToast(`Xarid muvaffaqiyatli! Balans: ${data.new_balance_formatted}`, 'success');

        setTimeout(() => {
            if (btnElement) {
                btnElement.disabled = false;
                btnElement.innerHTML = originalHtml;
                btnElement.classList.remove('bg-emerald-400', 'text-black');
                btnElement.classList.add('bg-gradient-to-r', 'from-orange-500', 'to-amber-500');
                if (window.lucide) window.lucide.createIcons();
            }
            STATE.isPurchasing = false;
        }, 2200);

    } catch (err) {
        console.error('Purchase error:', err);
        showToast('Server bilan aloqa uzildi. Pul yechilmadi.', 'error');
        if (btnElement) {
            btnElement.disabled = false;
            btnElement.innerHTML = originalHtml;
            if (window.lucide) window.lucide.createIcons();
        }
        STATE.isPurchasing = false;
    }
}

// --- Purchase Success Modal UI ---
function showPurchaseSuccessModal(skinTitle, priceFormatted, newBalanceFormatted) {
    const modal = document.getElementById('purchase-success-modal');
    if (!modal) return;

    const titleEl = document.getElementById('success-skin-title');
    const priceEl = document.getElementById('success-skin-price');
    const balEl = document.getElementById('success-new-balance');

    if (titleEl) titleEl.innerText = skinTitle || 'CS2 Skin';
    if (priceEl) priceEl.innerText = priceFormatted || '$0.00';
    if (balEl) balEl.innerText = newBalanceFormatted || '$0.00';

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    if (window.lucide) window.lucide.createIcons();
}

function closePurchaseSuccessModal() {
    const modal = document.getElementById('purchase-success-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

// --- Image Fallback globally ---
document.addEventListener('error', function (event) {
    var elm = event.target;
    if (elm.tagName === 'IMG' && !elm.dataset.failed) {
        elm.dataset.failed = 'true';
        elm.src = "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovbSsLQJf1f_BYQJB-dChgL-GkvP9JrafwDMHscYh2-2V94in31Xk-UVkYm_yd9eddwc2YQ7T-VfsyO_o05S-757Nyydk7HQ8pSGKEV2S0wY/360fx360f";
    }
}, true);

// --- Toast Utility ---
function showToast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const colorClass = type === 'success' ? 'bg-emerald-950/90 border-emerald-500/40 text-emerald-200' :
                       type === 'error' ? 'bg-rose-950/90 border-rose-500/40 text-rose-200' :
                       'bg-orange-950/90 border-orange-500/40 text-orange-200';

    const iconName = type === 'success' ? 'check-circle' :
                     type === 'error' ? 'alert-triangle' : 'info';

    toast.className = `alert-banner p-4 rounded-xl shadow-2xl backdrop-blur-xl border flex items-center justify-between pointer-events-auto ${colorClass}`;
    toast.innerHTML = `
        <div class="flex items-center space-x-3">
            <i data-lucide="${iconName}" class="w-5 h-5 shrink-0"></i>
            <p class="text-xs font-semibold leading-relaxed">${msg}</p>
        </div>
        <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white ml-2">
            <i data-lucide="x" class="w-4 h-4"></i>
        </button>
    `;
    container.appendChild(toast);
    if (window.lucide) window.lucide.createIcons();

    setTimeout(() => {
        toast.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => toast.remove(), 500);
    }, 3500);
}

// --- Notification Center Engine ---
let notificationsOpen = false;

function toggleNotificationsDropdown() {
    const dropdown = document.getElementById('notifications-dropdown');
    if (!dropdown) return;
    notificationsOpen = !notificationsOpen;
    if (notificationsOpen) {
        dropdown.classList.remove('hidden');
        fetchNotifications();
    } else {
        dropdown.classList.add('hidden');
    }
}

// Close notification dropdown when clicking outside
document.addEventListener('click', function(e) {
    const wrapper = document.getElementById('notifications-wrapper');
    const dropdown = document.getElementById('notifications-dropdown');
    if (wrapper && dropdown && !wrapper.contains(e.target)) {
        dropdown.classList.add('hidden');
        notificationsOpen = false;
    }
});

async function fetchNotifications() {
    try {
        const res = await fetch('/api/notifications/');
        if (!res.ok) return;
        const data = await res.json();
        if (data.authenticated) {
            renderNotifications(data.notifications, data.unread_count);
        }
    } catch (e) {
        console.warn('Notifications fetch error:', e);
    }
}

function renderNotifications(items, unreadCount) {
    const badge = document.getElementById('notif-count-badge');
    if (badge) {
        badge.innerText = unreadCount;
        badge.style.display = unreadCount > 0 ? 'flex' : 'none';
    }

    const list = document.getElementById('notifications-list');
    if (!list) return;

    if (!items || items.length === 0) {
        list.innerHTML = `
            <div class="py-8 text-center text-slate-500 text-xs">
                <i data-lucide="bell-off" class="w-8 h-8 mx-auto mb-2 opacity-40"></i>
                <p>Yangi bildirishnomalar yo'q</p>
            </div>
        `;
        if (window.lucide) window.lucide.createIcons();
        return;
    }

    list.innerHTML = items.map(n => {
        const iconName = n.type === 'price_drop' ? 'trending-down' :
                         n.type === 'order_status' ? 'package' :
                         n.type === 'listing_created' ? 'tag' : 'bell';
        const iconColor = n.type === 'price_drop' ? 'text-cyan-400' :
                          n.type === 'order_status' ? 'text-emerald-400' :
                          n.type === 'listing_created' ? 'text-purple-400' : 'text-amber-400';
        const unreadBg = !n.is_read ? 'bg-cyan-500/[0.08] border-cyan-400/30' : 'bg-csdark-950/60 border-white/[0.04]';

        return `
            <div class="p-3 rounded-xl border ${unreadBg} transition-all hover:bg-white/[0.06] flex items-start justify-between gap-2.5 group">
                <div class="flex items-start space-x-2.5 flex-1 cursor-pointer" onclick="markNotificationRead(${n.id}, '${n.link_url}')">
                    <div class="p-1.5 rounded-lg bg-white/5 shrink-0 mt-0.5">
                        <i data-lucide="${iconName}" class="w-3.5 h-3.5 ${iconColor}"></i>
                    </div>
                    <div class="space-y-0.5 flex-1">
                        <div class="flex items-center justify-between">
                            <h5 class="text-xs font-bold text-white leading-tight">${n.title}</h5>
                            <span class="text-[9px] text-slate-500 font-mono">${n.created_at}</span>
                        </div>
                        <p class="text-[11px] text-slate-400 leading-snug line-clamp-2">${n.message}</p>
                    </div>
                </div>
                ${!n.is_read ? `
                <button onclick="markNotificationRead(${n.id}, null)" class="text-slate-500 hover:text-cyan-400 p-1 shrink-0" title="O'qilgan deb belgilash">
                    <i data-lucide="check" class="w-3 h-3"></i>
                </button>
                ` : ''}
            </div>
        `;
    }).join('');

    if (window.lucide) window.lucide.createIcons();
}

async function markNotificationRead(id, linkUrl) {
    try {
        const csrf = getCsrfToken();
        const res = await fetch(`/api/notifications/${id}/read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrf,
                'Content-Type': 'application/json'
            }
        });
        if (res.ok) {
            fetchNotifications();
            if (linkUrl && linkUrl !== '#' && linkUrl !== 'null') {
                window.location.href = linkUrl;
            }
        }
    } catch(e) {
        console.warn('Mark read error:', e);
    }
}

async function markAllNotificationsRead() {
    try {
        const csrf = getCsrfToken();
        const res = await fetch('/api/notifications/read-all/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrf,
                'Content-Type': 'application/json'
            }
        });
        if (res.ok) {
            fetchNotifications();
            showToast("Barcha bildirishnomalar o'qilgan deb belgilandi", 'info');
        }
    } catch(e) {
        console.warn('Mark all read error:', e);
    }
}

// --- Recently Viewed Skins (Dynamic Rendering on Homepage) ---
function renderRecentlyViewed() {
    const container = document.getElementById('recently-viewed-container');
    const wrapper = document.getElementById('recently-viewed-section');
    if (!container || !wrapper) return;
    if (document.getElementById('account-recently-viewed')) {
        wrapper.classList.add('hidden');
        return;
    }

    try {
        const recent = JSON.parse(localStorage.getItem('skinly_recent_views') || '[]');
        if (!recent || recent.length === 0) {
            wrapper.classList.add('hidden');
            return;
        }

        wrapper.classList.remove('hidden');
        container.replaceChildren();
        recent.slice(0, 6).forEach(item => {
            const slug = String(item.slug || '').replace(/[^a-zA-Z0-9-]/g, '');
            if (!slug) return;
            const link = document.createElement('a');
            link.href = `/product/${encodeURIComponent(slug)}/`;
            link.className = 'group rounded-2xl glass-panel luxury-card p-3 border border-indigo-500/20 block transition-all duration-300';
            const imageWrap = document.createElement('div');
            imageWrap.className = 'aspect-square w-full rounded-xl overflow-hidden bg-gradient-to-b from-[#111736] to-[#070914] flex items-center justify-center p-2';
            const image = document.createElement('img');
            image.src = safeImageSource(item.image);
            image.alt = String(item.title || '');
            image.className = 'w-full h-full object-contain group-hover:scale-110 transition-transform duration-700';
            image.onerror = () => { image.src = '/static/images/placeholder.svg'; };
            imageWrap.appendChild(image);
            const details = document.createElement('div');
            details.className = 'mt-2.5';
            const title = document.createElement('h4');
            title.className = 'text-xs font-bold text-white group-hover:text-cyan-400 transition-colors truncate';
            title.textContent = String(item.title || '');
            const meta = document.createElement('div');
            meta.className = 'flex items-center justify-between mt-1';
            const wear = document.createElement('span');
            wear.className = 'text-[10px] text-slate-500 truncate max-w-[80px]';
            wear.textContent = String(item.wear || '');
            const price = document.createElement('p');
            price.className = 'text-xs font-extrabold text-cyan-400 font-mono';
            price.textContent = `$${String(item.price || '')}`;
            meta.append(wear, price);
            details.append(title, meta);
            link.append(imageWrap, details);
            container.appendChild(link);
        });

        if (window.lucide) window.lucide.createIcons();
    } catch (e) {
        console.warn('Recently viewed error:', e);
    }
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    applyTheme();
    initBalance();
    updateCartUI();
    updateFavoritesUI();
    syncFavoritesToAccount();
    fetchNotifications();
    renderRecentlyViewed();

    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', submitCheckout);
    }
});
