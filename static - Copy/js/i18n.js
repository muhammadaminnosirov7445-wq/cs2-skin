/**
 * Skinly CS2 Marketplace — Multi-Language Engine (UZ / RU / EN)
 * Real-time translation, localStorage persistence, and DOM updates.
 */

const TRANSLATIONS = {
    uz: {
        // Navigation & Brand
        brand_subtitle: "Premium CS2 Bozori",
        nav_catalog: "Katalog",
        nav_game: "O'yin (Dark Manga)",
        nav_track: "Buyurtmani kuzatish",
        nav_cabinet: "Kabinet",
        nav_login: "Kirish",
        nav_register: "Ro'yxatdan o'tish",
        nav_logout: "Chiqish",
        search_placeholder: "Skin qidirish (AWP, Karambit...)...",
        cart_title: "Savatcha",
        favorites_title: "Sevimlilar",
        notifications_title: "Bildirishnomalar",
        seller_title: "Sotuvchi",
        balance_label: "Balans",

        // Hero Section
        hero_tag: "Premium CS2 Skinlar Bozori",
        hero_title_1: "CS2 Skinlarning",
        hero_title_2: "Eng yaxshi narxlari",
        hero_desc: "Karambit, Butterfly, AWP Dragon Lore va boshqa nodir skinlarni eng hamyonbop narxlarda xarid qiling. Tezkor Steam Trade kafolati.",
        stat_delivery: "Yetkazish",
        stat_delivery_val: "2-5 daq",
        stat_guarantee: "Kafolat",
        stat_guarantee_val: "100%",
        stat_service: "Xizmat",
        stat_service_val: "24/7",

        // Filters
        filter_all: "Barchasi",
        filter_wear: "Holati",
        filter_weapon: "Qurol turi",
        filter_rarity: "Noyoblik",
        filter_sort: "Saralash",
        filter_stattrak: "StatTrak™",
        sort_newest: "Eng yangilar",
        sort_price_asc: "Narx: Arzon → Qimmat",
        sort_price_desc: "Narx: Qimmat → Arzon",
        sort_float: "Eng yaxshi Float",

        // Skin Cards & Details
        btn_buy: "Sotib olish",
        btn_add_cart: "Savatchaga",
        btn_view: "Batafsil",
        float_label: "Float",
        price_label: "Narx",
        status_in_stock: "Mavjud",
        status_out_stock: "Tugagan",
        empty_skins_title: "Skin topilmadi",
        empty_skins_desc: "Tanlangan filtrlar bo'yicha tovar mavjud emas.",
        btn_view_all: "Barchasini ko'rish",

        // Cart & Checkout
        cart_empty: "Savatchangiz bo'sh",
        cart_subtotal: "Jami:",
        cart_total: "To'lov:",
        btn_clear_cart: "Tozalash",
        btn_checkout: "Buyurtma berish",
        checkout_modal_title: "Buyurtmani rasmiylashtirish",
        checkout_name_label: "Ismingiz",
        checkout_phone_label: "Telefon",
        checkout_trade_url_label: "Steam Trade URL",
        checkout_notes_label: "Izoh",
        btn_confirm_pay: "To'lash va tasdiqlash",
        success_title: "Muvaffaqiyatli!",
        success_desc: "Xarid amalga oshirildi.",
        success_product: "Mahsulot:",
        success_amount: "Summa:",
        success_balance: "Yangi balans:",
        btn_continue: "Davom etish",
        btn_to_cabinet: "Kabinetga",

        // Auth: Registration
        reg_title: "Ro'yxatdan o'tish",
        reg_subtitle: "Skinly hisobini yarating va +$100.00 xarid bonusiga ega bo'ling!",
        reg_btn_demo: "1-bosishda Demo hisob ochish (+$150 Bonus)",
        reg_google: "Google orqali ro'yxatdan o'tish",
        reg_github: "GitHub orqali ro'yxatdan o'tish",
        reg_or_form: "Yoki to'g'ridan-to'g'ri forma",
        reg_username_label: "Login (Foydalanuvchi nomi)",
        reg_username_placeholder: "Masalan: Sardor99",
        reg_email_label: "Email (Ixtiyoriy)",
        reg_phone_label: "Telefon (Ixtiyoriy)",
        reg_trade_label: "Steam Trade URL (Ixtiyoriy)",
        reg_pwd_label: "Parol",
        reg_pwd_placeholder: "Istalgan parolingizni kiriting",
        reg_pwd_confirm_label: "Parolni tasdiqlang (Ixtiyoriy)",
        reg_pwd_confirm_placeholder: "Parolni qayta kiriting",
        reg_btn_submit: "Ro'yxatdan o'tish (+100$ Bonus)",
        reg_have_account: "Allaqachon hisobingiz bormi?",
        reg_link_login: "Kirish",

        // Auth: Login
        login_title: "Tizimga kirish",
        login_subtitle: "Skinly hisobingizga kiring yoki demo hisob bilan 1 bosishda sinab ko'ring",
        login_btn_demo: "Tezkor Demo hisob bilan kirish (+$200 Balans)",
        login_google: "Google orqali kirish",
        login_github: "GitHub orqali kirish",
        login_user_label: "Login yoki Email",
        login_user_placeholder: "Foydalanuvchi nomi yoki email",
        login_pwd_label: "Parol",
        login_pwd_placeholder: "Parolingizni kiriting",
        login_btn_submit: "Tizimga kirish",
        login_no_account: "Hisobingiz yo'qmi?",
        login_link_reg: "Ro'yxatdan o'ting (+100$ Bonus)",

        // Footer
        footer_brand_desc: "CS2 skinlari uchun yangi avlod premium bozori. Tezkor Steam Trade taklifi va xavfsiz to'lov kafolati.",
        footer_pages: "Sahifalar",
        footer_status_title: "Tizim holati",
        footer_bot_status: "Steam Trade Bot faol",
        footer_bot_desc: "24/7 avtomatlashtirilgan trade tizimi",
        footer_rights: "© 2026 Skinly. Barcha huquqlar himoyalangan."
    },

    ru: {
        // Navigation & Brand
        brand_subtitle: "Премиум Маркетплейс CS2",
        nav_catalog: "Каталог",
        nav_game: "Игра (Dark Manga)",
        nav_track: "Отследить заказ",
        nav_cabinet: "Кабинет",
        nav_login: "Войти",
        nav_register: "Регистрация",
        nav_logout: "Выйти",
        search_placeholder: "Поиск скинов (AWP, Керамбит...)...",
        cart_title: "Корзина",
        favorites_title: "Избранное",
        notifications_title: "Уведомления",
        seller_title: "Продавец",
        balance_label: "Баланс",

        // Hero Section
        hero_tag: "Премиум Маркетплейс CS2 Скинов",
        hero_title_1: "CS2 Скины по",
        hero_title_2: "Лучшим ценам",
        hero_desc: "Покупайте Керамбит, Бабочку, AWP Dragon Lore и другие редкие скины по выгодным ценам. Быстрый Steam Trade оффер с гарантией.",
        stat_delivery: "Доставка",
        stat_delivery_val: "2-5 мин",
        stat_guarantee: "Гарантия",
        stat_guarantee_val: "100%",
        stat_service: "Сервис",
        stat_service_val: "24/7",

        // Filters
        filter_all: "Все",
        filter_wear: "Качество",
        filter_weapon: "Оружие",
        filter_rarity: "Редкость",
        filter_sort: "Сортировка",
        filter_stattrak: "StatTrak™",
        sort_newest: "Сначала новые",
        sort_price_asc: "Цена: Сначала дешевые",
        sort_price_desc: "Цена: Сначала дорогие",
        sort_float: "Лучший Float",

        // Skin Cards & Details
        btn_buy: "Купить",
        btn_add_cart: "В корзину",
        btn_view: "Подробнее",
        float_label: "Float",
        price_label: "Цена",
        status_in_stock: "В наличии",
        status_out_stock: "Нет в наличии",
        empty_skins_title: "Скины не найдены",
        empty_skins_desc: "По выбранным фильтрам товаров не найдено.",
        btn_view_all: "Показать все",

        // Cart & Checkout
        cart_empty: "Ваша корзина пуста",
        cart_subtotal: "Итого:",
        cart_total: "К оплате:",
        btn_clear_cart: "Очистить",
        btn_checkout: "Оформить заказ",
        checkout_modal_title: "Оформление заказа",
        checkout_name_label: "Ваше имя",
        checkout_phone_label: "Телефон",
        checkout_trade_url_label: "Steam Trade URL",
        checkout_notes_label: "Примечание",
        btn_confirm_pay: "Оплатить и подтвердить",
        success_title: "Успешно!",
        success_desc: "Покупка завершена.",
        success_product: "Товар:",
        success_amount: "Сумма:",
        success_balance: "Новый баланс:",
        btn_continue: "Продолжить",
        btn_to_cabinet: "В кабинет",

        // Auth: Registration
        reg_title: "Регистрация",
        reg_subtitle: "Создайте аккаунт Skinly и получите бонус +$100.00 на баланс!",
        reg_btn_demo: "В 1 клик создать Демо-аккаунт (+$150 Бонус)",
        reg_google: "Войти через Google",
        reg_github: "Войти через GitHub",
        reg_or_form: "Или заполните форму",
        reg_username_label: "Логин (Имя пользователя)",
        reg_username_placeholder: "Например: Player2026",
        reg_email_label: "Email (Необязательно)",
        reg_phone_label: "Телефон (Необязательно)",
        reg_trade_label: "Steam Trade URL (Необязательно)",
        reg_pwd_label: "Пароль",
        reg_pwd_placeholder: "Введите любой пароль",
        reg_pwd_confirm_label: "Подтверждение пароля (Необязательно)",
        reg_pwd_confirm_placeholder: "Повторите пароль",
        reg_btn_submit: "Зарегистрироваться (+100$ Бонус)",
        reg_have_account: "Уже есть аккаунт?",
        reg_link_login: "Войти",

        // Auth: Login
        login_title: "Вход в аккаунт",
        login_subtitle: "Войдите в свой профиль или протестируйте в 1 клик с Демо-аккаунта",
        login_btn_demo: "Быстрый вход через Демо-аккаунт (+$200 Баланс)",
        login_google: "Войти через Google",
        login_github: "Войти через GitHub",
        login_user_label: "Логин или Email",
        login_user_placeholder: "Имя пользователя или почта",
        login_pwd_label: "Пароль",
        login_pwd_placeholder: "Введите ваш пароль",
        login_btn_submit: "Войти в систему",
        login_no_account: "Нет аккаунта?",
        login_link_reg: "Зарегистрироваться (+100$ Бонус)",

        // Footer
        footer_brand_desc: "Новое поколение торговой площадки CS2 скинов. Моментальный Steam Trade оффер и безопасные сделки.",
        footer_pages: "Страницы",
        footer_status_title: "Статус системы",
        footer_bot_status: "Steam Trade Бот активен",
        footer_bot_desc: "24/7 автоматизированная система обмена",
        footer_rights: "© 2026 Skinly. Все права защищены."
    },

    en: {
        // Navigation & Brand
        brand_subtitle: "Premium CS2 Marketplace",
        nav_catalog: "Catalog",
        nav_game: "Game (Dark Manga)",
        nav_track: "Track Order",
        nav_cabinet: "Dashboard",
        nav_login: "Sign In",
        nav_register: "Register",
        nav_logout: "Sign Out",
        search_placeholder: "Search skins (AWP, Karambit...)...",
        cart_title: "Shopping Cart",
        favorites_title: "Favorites",
        notifications_title: "Notifications",
        seller_title: "Seller",
        balance_label: "Balance",

        // Hero Section
        hero_tag: "Premium CS2 Skins Marketplace",
        hero_title_1: "Best Prices on",
        hero_title_2: "CS2 Skins & Knives",
        hero_desc: "Buy Karambit, Butterfly, AWP Dragon Lore and high-tier skins at the lowest market rates. Fast automated Steam Trade Offers.",
        stat_delivery: "Delivery",
        stat_delivery_val: "2-5 min",
        stat_guarantee: "Guarantee",
        stat_guarantee_val: "100%",
        stat_service: "Support",
        stat_service_val: "24/7",

        // Filters
        filter_all: "All",
        filter_wear: "Condition",
        filter_weapon: "Weapon",
        filter_rarity: "Rarity",
        filter_sort: "Sort By",
        filter_stattrak: "StatTrak™",
        sort_newest: "Newest First",
        sort_price_asc: "Price: Low to High",
        sort_price_desc: "Price: High to Low",
        sort_float: "Best Float Value",

        // Skin Cards & Details
        btn_buy: "Buy Now",
        btn_add_cart: "Add to Cart",
        btn_view: "Details",
        float_label: "Float",
        price_label: "Price",
        status_in_stock: "In Stock",
        status_out_stock: "Sold Out",
        empty_skins_title: "No Skins Found",
        empty_skins_desc: "No items match your selected filters.",
        btn_view_all: "View All",

        // Cart & Checkout
        cart_empty: "Your cart is empty",
        cart_subtotal: "Subtotal:",
        cart_total: "Total:",
        btn_clear_cart: "Clear",
        btn_checkout: "Checkout",
        checkout_modal_title: "Complete Your Order",
        checkout_name_label: "Your Name",
        checkout_phone_label: "Phone Number",
        checkout_trade_url_label: "Steam Trade URL",
        checkout_notes_label: "Order Notes",
        btn_confirm_pay: "Pay & Confirm",
        success_title: "Purchase Successful!",
        success_desc: "Your skin order has been dispatched.",
        success_product: "Product:",
        success_amount: "Amount:",
        success_balance: "New Balance:",
        btn_continue: "Continue Shopping",
        btn_to_cabinet: "My Dashboard",

        // Auth: Registration
        reg_title: "Create Account",
        reg_subtitle: "Sign up for Skinly and claim an instant +$100.00 wallet bonus!",
        reg_btn_demo: "1-Click Demo Account (+$150 Bonus)",
        reg_google: "Continue with Google",
        reg_github: "Continue with GitHub",
        reg_or_form: "Or fill the direct form",
        reg_username_label: "Username (Login)",
        reg_username_placeholder: "e.g. MasterGamer99",
        reg_email_label: "Email (Optional)",
        reg_phone_label: "Phone (Optional)",
        reg_trade_label: "Steam Trade URL (Optional)",
        reg_pwd_label: "Password",
        reg_pwd_placeholder: "Enter any password",
        reg_pwd_confirm_label: "Confirm Password (Optional)",
        reg_pwd_confirm_placeholder: "Repeat password",
        reg_btn_submit: "Register Account (+100$ Bonus)",
        reg_have_account: "Already have an account?",
        reg_link_login: "Sign In",

        // Auth: Login
        login_title: "Sign In",
        login_subtitle: "Log in to your account or try 1-click test access with Demo Account",
        login_btn_demo: "Instant Demo Sign In (+$200 Balance)",
        login_google: "Sign In with Google",
        login_github: "Sign In with GitHub",
        login_user_label: "Username or Email",
        login_user_placeholder: "Enter username or email",
        login_pwd_label: "Password",
        login_pwd_placeholder: "Enter your password",
        login_btn_submit: "Sign In",
        login_no_account: "Don't have an account?",
        login_link_reg: "Register Now (+100$ Bonus)",

        // Footer
        footer_brand_desc: "Next-generation luxury CS2 skin trading marketplace. Instant Steam Trade Offers and secured payments.",
        footer_pages: "Navigation",
        footer_status_title: "System Status",
        footer_bot_status: "Steam Trade Bot Active",
        footer_bot_desc: "24/7 Automated Skin Distribution",
        footer_rights: "© 2026 Skinly. All rights reserved."
    }
};

class SkinlyI18n {
    constructor() {
        this.currentLang = localStorage.getItem('skinly_lang') || 'uz';
        this.init();
    }

    init() {
        this.applyLanguage(this.currentLang);
    }

    setLanguage(lang) {
        if (!TRANSLATIONS[lang]) return;
        this.currentLang = lang;
        localStorage.setItem('skinly_lang', lang);
        document.cookie = `skinly_lang=${lang}; path=/; max-age=31536000`;
        this.applyLanguage(lang);
    }

    t(key) {
        const langData = TRANSLATIONS[this.currentLang] || TRANSLATIONS['uz'];
        return langData[key] || TRANSLATIONS['uz'][key] || key;
    }

    applyLanguage(lang) {
        const dict = TRANSLATIONS[lang] || TRANSLATIONS['uz'];

        // Update <html> lang attribute
        document.documentElement.lang = lang;

        // Update language indicator in dropdown
        const flagMap = { uz: '🇺🇿 UZ', ru: '🇷🇺 RU', en: '🇬🇧 EN' };
        const labelEl = document.getElementById('current-lang-label');
        if (labelEl) {
            labelEl.innerText = flagMap[lang] || '🇺🇿 UZ';
        }

        // Translate all elements with [data-i18n]
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) {
                el.innerText = dict[key];
            }
        });

        // Translate all elements with [data-i18n-placeholder]
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (dict[key]) {
                el.placeholder = dict[key];
            }
        });

        // Translate all elements with [data-i18n-title]
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.getAttribute('data-i18n-title');
            if (dict[key]) {
                el.title = dict[key];
            }
        });
    }
}

// Global instance
window.skinlyI18n = new SkinlyI18n();

// Global helper for language change
function setSiteLanguage(lang) {
    if (window.skinlyI18n) {
        window.skinlyI18n.setLanguage(lang);
    }
    const dropdown = document.getElementById('lang-dropdown-menu');
    if (dropdown) dropdown.classList.add('hidden');
}

function toggleLangDropdown() {
    const dropdown = document.getElementById('lang-dropdown-menu');
    if (dropdown) dropdown.classList.toggle('hidden');
}

// Close language dropdown on outside click
document.addEventListener('click', (e) => {
    const wrapper = document.getElementById('lang-selector-wrapper');
    const dropdown = document.getElementById('lang-dropdown-menu');
    if (wrapper && dropdown && !wrapper.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});
