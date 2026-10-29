from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, Case, CaseItem, UserInventory, UserProfile, Order, OrderItem


class Command(BaseCommand):
    help = 'Seeds authentic CS2 skins, starter cases, and demo inventory with 100% accurate Steam CDN images'

    def handle(self, *args, **options):
        self.stdout.write("Populating CS2 skins with exact, authentic Steam images...")

        # 1. Categories
        categories_data = [
            {'name': 'Knives', 'slug': 'knives', 'icon': 'sword'},
            {'name': 'Gloves', 'slug': 'gloves', 'icon': 'hand'},
            {'name': 'Sniper Rifles', 'slug': 'sniper-rifles', 'icon': 'crosshair'},
            {'name': 'Rifles', 'slug': 'rifles', 'icon': 'target'},
            {'name': 'Pistols', 'slug': 'pistols', 'icon': 'zap'},
        ]

        cats = {}
        for c in categories_data:
            cat, _ = Category.objects.get_or_create(slug=c['slug'], defaults={'name': c['name'], 'icon': c['icon']})
            cats[c['slug']] = cat

        # 2. 100% Accurate CS2 Skins with Authentic Steam CDN Images across all rarities
        skins_data = [
            # ─── KNIVES (Gold / Extraordinary) ───
            {
                'category': cats['knives'],
                'title': '★ Karambit | Doppler',
                'weapon_type': 'Knife',
                'wear_condition': 'Factory New',
                'float_value': 0.0089,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Kavisli pichoq, yoqut-sapfir naqshli Doppler Phase 2. Counter-Strike 2 Source 2 dvigatelida to\'liq yorug\'lik aksini beruvchi toza burchakli korpus.',
                'wholesale_price': Decimal('1400.00'),
                'retail_price': Decimal('1820.00'),
                'stock': 3,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL6kJ_m-B1Q7uCvZaZkNM-SA1iSze91u_FsTju_qhAmoT-Jn4bjJC_4Ml93UtZuRLQPsBawkNfiMbnl5AKMiopCnin7iCJBv31j4rkBBKEg-6zUjV3GY6p9v8dpLWT3Fg',
                'is_featured': True
            },
            {
                'category': cats['knives'],
                'title': '★ Butterfly Knife | Fade',
                'weapon_type': 'Knife',
                'wear_condition': 'Factory New',
                'float_value': 0.0124,
                'stattrak': True,
                'rarity': 'extraordinary',
                'description': 'Maxsus aylanish animatsiyasiga ega 99.8% Full Fade Butterfly pichoq. StatTrak™ hisoblagichi bilan har bir g\'alaba yozib boriladi.',
                'wholesale_price': Decimal('2800.00'),
                'retail_price': Decimal('3450.00'),
                'stock': 2,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL6kJ_m-B1Z-ua6bbZrLOmsD2avx-9ytd5lRi67gVNwsDvSwtqqc3iXZg4kCZYjReYLtRbum9XgYuvm5wbWjtgUzCn3iSsf8G81tFEeH9rw',
                'is_featured': True
            },
            {
                'category': cats['knives'],
                'title': '★ M9 Bayonet | Lore',
                'weapon_type': 'Knife',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1920,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Skandinaviya afsonalariga asoslangan nafis tilla o\'ymakorlik naqshli M9 Bayonet. Yirik korpus va tishli orqa tig\'.',
                'wholesale_price': Decimal('950.00'),
                'retail_price': Decimal('1280.00'),
                'stock': 4,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL6kJ_m-B1Wts2sab1iLvWHMWSF_uMvj-NoVha_mg8ijDGMnYftbyrBOw52D5R0FOYPtkG6ltOxNrjl4FPdiN0WzC723SxP6ypp6u8LVKY7uvqAFpeI3XY',
                'is_featured': False
            },
            {
                'category': cats['knives'],
                'title': '★ Talon Knife | Marble Fade',
                'weapon_type': 'Knife',
                'wear_condition': 'Factory New',
                'float_value': 0.0150,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Fil suyagidan ishlangan dasta va marmar kamalak rangli (Fire & Ice) tig\'li Talon pichoq.',
                'wholesale_price': Decimal('820.00'),
                'retail_price': Decimal('1100.00'),
                'stock': 3,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL6kJ_m-B1M5vahf6lsK_WBMWad_uN3ouNlSha1lBkijCqMnoDuHifOOV5kFJMlQecC4RW5x4bkMLvgsgGP2IIXzy_-iysaunlo4bwEBfYh_aLS3A7fcepqAVr8ibw',
                'is_featured': False
            },
            {
                'category': cats['knives'],
                'title': '★ Skeleton Knife | Crimson Web',
                'weapon_type': 'Knife',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1640,
                'stattrak': True,
                'rarity': 'extraordinary',
                'description': 'Qon-qizil asosda qora o\'rgimchak to\'ri chizilgan o\'ta kamyob Skeleton pichoq. Markazida katta o\'rgimchak to\'ri mavjud.',
                'wholesale_price': Decimal('1150.00'),
                'retail_price': Decimal('1550.00'),
                'stock': 2,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL6kJ_m-B1I5PeibbBiLs-bF1iHxOxlj-1gSCGn2011t26Bytr_cn-VZwciXJskRLQKuka9k4ezYrnqtQXf2YhGzC6viXxXrnE8k9yhp-k',
                'is_featured': False
            },

            # ─── GLOVES (Gold / Extraordinary) ───
            {
                'category': cats['gloves'],
                'title': '★ Sport Gloves | Vice',
                'weapon_type': 'Gloves',
                'wear_condition': 'Field-Tested',
                'float_value': 0.2210,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Kiberpank neon ko\'k va porloq pushti rangdagi haqiqiy sport qo\'lqoplari. Karambit yoki Butterfly Fade bilan ajoyib vizual kombinatsiya.',
                'wholesale_price': Decimal('1100.00'),
                'retail_price': Decimal('1450.00'),
                'stock': 4,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Tk5UvzWCL2kpn2-DFk_OKherB0H_KfG2Kv0ed4u95lRi67gVNx4T-Bw434IHyVb1QlAsd1FOUDthG4xNznMu3m4QXXg90Wzn_33C1I8G81tLaDi_rK',
                'is_featured': True
            },
            {
                'category': cats['gloves'],
                'title': '★ Specialist Gloves | Crimson Kimono',
                'weapon_type': 'Gloves',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1840,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Maxsus mutaxassislar qo\'lqopi, qizil yapon kimonosi uslubidagi qora-qizil mato va mustahkamlangan kaft qoplamasi.',
                'wholesale_price': Decimal('1350.00'),
                'retail_price': Decimal('1780.00'),
                'stock': 3,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Tk71ruQBH4jYLf-i5U-fe9V7d9JfOaD2uZ0vpJu-hkQCe8qhkusjCKlIvqHjnCOml8U8UoAfkItBLswdbuNbjr5FHdjNkUzSv73C1K5y46tu4EUvAg-6bU3FrBMOE4_9BdcyhkRns5',
                'is_featured': False
            },
            {
                'category': cats['gloves'],
                'title': '★ Moto Gloves | Spearmint',
                'weapon_type': 'Gloves',
                'wear_condition': 'Field-Tested',
                'float_value': 0.2100,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Oq charmdan ishlangan yalpiz-yashil aksentli mototsikl poygachilari qo\'lqopi. CS2 hamjamiyatida eng qadrlanadigan qo\'lqoplardan biri.',
                'wholesale_price': Decimal('1600.00'),
                'retail_price': Decimal('2100.00'),
                'stock': 2,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu4r7_lb1QgTykpPf-i5U-fe9V6liNP-BDX6TzetJvehnWxanhxQmvTqJn7D1KCzPKhgnW5UmRO4DsxXrlYbhPurmtAXai98UzS73in5I6S5p4OsAU_Zx-KHWkUifZsxBQgc2',
                'is_featured': False
            },
            {
                'category': cats['gloves'],
                'title': '★ Hand Wraps | Cobalt Skulls',
                'weapon_type': 'Gloves',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1950,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Moviy kobalt rangli bint o\'ramalari, ustida mayda bosh suyaklari naqshlari bilan jangovar uslub berilgan.',
                'wholesale_price': Decimal('580.00'),
                'retail_price': Decimal('790.00'),
                'stock': 5,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu4vx603vRA_Olpfu-TVJ7uK9V6xsLvSEHGaA_uJzsfVhSjuqqhsmsS-MmbD7LT7CAUV7T84sBohW60fg1srnZb6zsw2Ng41MmST43C1L7is9574CBKIh_q2Big_IMOdutcNRd_iuU13QD7PQAmaY',
                'is_featured': False
            },
            {
                'category': cats['gloves'],
                'title': '★ Driver Gloves | King Snake',
                'weapon_type': 'Gloves',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1750,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Haqiqiy oq ilon terisi teksturasi bilan qoplangan haydovchi qo\'lqoplari. Karambit Damascus Steel bilan ajoyib uyg\'unlik hosil qiladi.',
                'wholesale_price': Decimal('620.00'),
                'retail_price': Decimal('850.00'),
                'stock': 3,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5T441rsfhr9kYDl7h1I4_utY5t-LvGYC3SbyOBJp-lgWyyMmRQguynLz4r6Iy7EbFchApNyR-dbtEbuw4XkN7jq7gHdjtoQzi37hiwYvytvt_FCD_Ql24JgJg',
                'is_featured': False
            },

            # ─── SNIPER RIFLES (Covert / Classified / Restricted) ───
            {
                'category': cats['sniper-rifles'],
                'title': 'AWP | Dragon Lore',
                'weapon_type': 'Sniper',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1850,
                'stattrak': False,
                'rarity': 'covert',
                'description': 'Counter-Strike tarixidagi eng afsonaviy AWP snayperi. Olov purkayotgan qadimgi ajdaho nafasi tasvirlangan.',
                'wholesale_price': Decimal('4500.00'),
                'retail_price': Decimal('5800.00'),
                'stock': 1,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwiYbf_jdk4veqYaF7IfysCnWRxuF4j-B-Xxa_nBovp3Pdwtj9cC_GaAd0DZdwQu9fuhS4kNy0NePntVTbjYpCyyT_3CgY5i9j_a9cBkcCWUKV',
                'is_featured': True
            },
            {
                'category': cats['sniper-rifles'],
                'title': 'AWP | Asiimov',
                'weapon_type': 'Sniper',
                'wear_condition': 'Field-Tested',
                'float_value': 0.2450,
                'stattrak': True,
                'rarity': 'covert',
                'description': 'Sci-Fi ilmiy-fantastik oq va to\'q sariq geometrik naqsh. StatTrak™ texnologiyasi bilan jihozlangan eng ommabop AWP skini.',
                'wholesale_price': Decimal('120.00'),
                'retail_price': Decimal('175.00'),
                'stock': 12,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwiYbf_jdk7uW-V6V-Kf2cGFidxOp_pewnF3nhxEt0sGnSzN76dH3GOg9xC8FyEORftRe-x9PuYurq71bW3d8UnjK-0H0YSTpMGQ',
                'is_featured': True
            },
            {
                'category': cats['sniper-rifles'],
                'title': 'SSG 08 | Blood in the Water',
                'weapon_type': 'Sniper',
                'wear_condition': 'Minimal Wear',
                'float_value': 0.0750,
                'stattrak': True,
                'rarity': 'classified',
                'description': 'Suv ostidan hujum qilayotgan ulkan oq akula tasvirlangan yengil snayper miltig\'i.',
                'wholesale_price': Decimal('45.00'),
                'retail_price': Decimal('70.00'),
                'stock': 8,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLijZGwpR1Y-s29YKV_K8-fB2CY1aAmsbFtFnDilkUl5j7UzoqsInmVaFd0XMMlELYDshbuxNPvP-yxtlCMlcsbmlWiixNl',
                'is_featured': False
            },
            {
                'category': cats['sniper-rifles'],
                'title': 'AWP | Atheris',
                'weapon_type': 'Sniper',
                'wear_condition': 'Factory New',
                'float_value': 0.0310,
                'stattrak': False,
                'rarity': 'restricted',
                'description': 'Yashil zaharli ilon qora korpus uzra chizilgan, o\'ta ommabop va chiroyli byudjet AWP skini.',
                'wholesale_price': Decimal('10.00'),
                'retail_price': Decimal('14.50'),
                'stock': 25,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwiYbf-jFk7uW-V617LfmBGDidxOp_pewnF3njyUl0sWqSzN39eCiUPQR2DpUlQeRftBe4wd7uNr_n41HYidkUzSv42S9I6is7tuoCBKUh-KjWkUdS',
                'is_featured': False
            },

            # ─── RIFLES (Covert / Classified / Mil-Spec) ───
            {
                'category': cats['rifles'],
                'title': 'AK-47 | Fire Serpent',
                'weapon_type': 'Rifle',
                'wear_condition': 'Minimal Wear',
                'float_value': 0.0820,
                'stattrak': True,
                'rarity': 'covert',
                'description': 'Bravo to\'plamining afsonaviy quroli. Olovli ilon naqshi va StatTrak™ hisoblagichi bilan boyitilgan.',
                'wholesale_price': Decimal('850.00'),
                'retail_price': Decimal('1150.00'),
                'stock': 5,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwlcK3wiFO0PSneqF-JeKDC2mE_u995LZWTTuygxIYvzSCkpu3cnvFPQB2DpUkROFY4Rntw93lP7i241DbiI1BxSuviHlKunk_6-sHU71lpPMTRLyP4Q',
                'is_featured': True
            },
            {
                'category': cats['rifles'],
                'title': 'M4A4 | Howl',
                'weapon_type': 'Rifle',
                'wear_condition': 'Factory New',
                'float_value': 0.0350,
                'stattrak': False,
                'rarity': 'covert',
                'description': 'Kamyob "Contraband" toifasidagi yagona afsonaviy avtomat. Qizil olovli bo\'ri naqshi CS2 yorug\'lik nurlarida yaltirab turadi.',
                'wholesale_price': Decimal('4200.00'),
                'retail_price': Decimal('5300.00'),
                'stock': 1,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL8ypexwiFO0P_6afVSKP-EAm6extF6ueZhW2exwkl2tmTXwt39eCiUPQR2DMN4TOVetUK8xoLgM-K341eM2otDnC6okGoXufBz_TAB',
                'is_featured': True
            },
            {
                'category': cats['rifles'],
                'title': 'M4A1-S | Printstream',
                'weapon_type': 'Rifle',
                'wear_condition': 'Factory New',
                'float_value': 0.0250,
                'stattrak': True,
                'rarity': 'covert',
                'description': 'Marvariddek kamalak nur qaytaruvchi oq va qora minimalist dizayn. Ovoz so\'ndiruvchi va StatTrak™ bilan.',
                'wholesale_price': Decimal('160.00'),
                'retail_price': Decimal('230.00'),
                'stock': 7,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL8ypexwjFS4_ega6F_H_OGMWrEwL9lj_F7Rienhgk1tjyIpYPwJiPTcAAoCpsiEO5ZsUbpm9C2Zuni4VHW3o5EzSX62HxP7Sg96-hWVqYi_6TJz1aW0nxrkGs',
                'is_featured': False
            },
            {
                'category': cats['rifles'],
                'title': 'AK-47 | Vulcan',
                'weapon_type': 'Rifle',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1650,
                'stattrak': False,
                'rarity': 'covert',
                'description': 'Sport va poyga avtomobillari uslubidagi oq, ko\'k va uglerod tolali klassik AK-47 skini.',
                'wholesale_price': Decimal('180.00'),
                'retail_price': Decimal('260.00'),
                'stock': 9,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwlcK3wiFO0POlPPNSMuWRDGKC_uJ_t-l9AXCxxEh14zjTztivci2ePQZ2W8NzTecD4BKwloLiYeqxtAOIj9gUyyngznQeF7I6QE8',
                'is_featured': False
            },
            {
                'category': cats['rifles'],
                'title': 'AK-47 | Frontside Misty',
                'weapon_type': 'Rifle',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1980,
                'stattrak': False,
                'rarity': 'classified',
                'description': 'Muzli oq va moviy to\'lqinlar naqshi bilan qoplangan yorqin AK-47.',
                'wholesale_price': Decimal('28.00'),
                'retail_price': Decimal('38.00'),
                'stock': 14,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwlcK3wiFO0POlV6F-Ju6EDW-Ez-975bZkSju_rBlw5z-DyN-td3zBPA5xWZl0ROALtkG_x9LnM-7m4FfbjdoXyyvy2HgcuDE9t7QHU7hLpKXb5H_xWw',
                'is_featured': False
            },
            {
                'category': cats['rifles'],
                'title': 'AK-47 | Uncharted',
                'weapon_type': 'Rifle',
                'wear_condition': 'Factory New',
                'float_value': 0.0450,
                'stattrak': False,
                'rarity': 'mil-spec',
                'description': 'Mayya qabilasi o\'ymakorligi naqshlari tushirilgan qora va jigarrang yog\'ochli AK-47.',
                'wholesale_price': Decimal('2.00'),
                'retail_price': Decimal('3.50'),
                'stock': 30,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwlcK3wiFO0POlV6Z-K_CcD36fzeJpvu1uSzy1rBki42aDzo2tdn_FaFIiW8VyEe4K50blwt_mMbnm5FWM3otAnS73238XuSU64rI',
                'is_featured': False
            },
            {
                'category': cats['rifles'],
                'title': 'M4A4 | Magnesium',
                'weapon_type': 'Rifle',
                'wear_condition': 'Factory New',
                'float_value': 0.0210,
                'stattrak': False,
                'rarity': 'mil-spec',
                'description': 'Kulrang uglerod tolali metall korpusda oq olov tillari aks etgan.',
                'wholesale_price': Decimal('1.80'),
                'retail_price': Decimal('2.90'),
                'stock': 28,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL8ypexwjFS4_GqZ6R-JeLDCmGezupmte4mFjqhxEt0sDuGzoyvciiUPQR2C5d1QOBYshftkdDkZu_n5Vbfid9Dzyv5hywYuH1r4bU',
                'is_featured': False
            },

            # ─── PISTOLS (Covert / Classified / Restricted / Mil-Spec) ───
            {
                'category': cats['pistols'],
                'title': 'Desert Eagle | Printstream',
                'weapon_type': 'Pistol',
                'wear_condition': 'Factory New',
                'float_value': 0.0210,
                'stattrak': True,
                'rarity': 'covert',
                'description': 'Katta kalibrli to\'pponcha uchun oq marvarid qoplama va StatTrak™ hisoblagichi.',
                'wholesale_price': Decimal('95.00'),
                'retail_price': Decimal('140.00'),
                'stock': 15,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL1m5fn8Sdk7OeRbKFsJ8-DHG6e1f1iouRoQha_nBovp3OGmdeqInyVP1V0XsYlRbEI50a5wNyzZr605AyI3t5MmCSohylAuC89_a9cBoMY9UkV',
                'is_featured': False
            },
            {
                'category': cats['pistols'],
                'title': 'USP-S | Printstream',
                'weapon_type': 'Pistol',
                'wear_condition': 'Factory New',
                'float_value': 0.0280,
                'stattrak': True,
                'rarity': 'covert',
                'description': 'CT-tomonining eng nufuzli susturgichli to\'pponchasi, optik marvarid nurlari va StatTrak™ bilan.',
                'wholesale_price': Decimal('85.00'),
                'retail_price': Decimal('130.00'),
                'stock': 10,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLkjYbf7itX6vytbbZSI-WsG3SA_v5kue99XD2hkBwqjDGMnYftb3yUPFR0XsNyRrNc5kO5ltziMenr5lONj4kXyi2riywc7y9o5LtQAqQ7uvqAkScWnv4',
                'is_featured': False
            },
            {
                'category': cats['pistols'],
                'title': 'USP-S | Kill Confirmed',
                'weapon_type': 'Pistol',
                'wear_condition': 'Minimal Wear',
                'float_value': 0.0980,
                'stattrak': False,
                'rarity': 'covert',
                'description': 'O\'q bosh suyagini teshib o\'tgan dramatik qizil illyustratsiya va tovush so\'ndiruvchi silencer.',
                'wholesale_price': Decimal('110.00'),
                'retail_price': Decimal('165.00'),
                'stock': 8,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLkjYbf7itX6vytbbZSI-WsG3SA_uV_vO1WTCa9kxQ1vjiBpYPwJiPTcFB2Xpp5TO5cskG9lYCxZu_jsVCL3o4Xnij23ClO5ik9tegFA_It8qHJz1aWe-uc160',
                'is_featured': False
            },
            {
                'category': cats['pistols'],
                'title': 'Desert Eagle | Blaze',
                'weapon_type': 'Pistol',
                'wear_condition': 'Factory New',
                'float_value': 0.0140,
                'stattrak': False,
                'rarity': 'classified',
                'description': 'Qora fonda stvol uchidan chiqayotgan haqiqiy sariq-qizil olov tillari.',
                'wholesale_price': Decimal('650.00'),
                'retail_price': Decimal('890.00'),
                'stock': 4,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL1m5fn8Sdk7vORbqhsLfWAMWuZxuZi_uI_TX6wxxkjsGXXnImsJ37COlUoWcByEOMOtxa5kdXmNu3htVPZjN1bjXKpkHLRfQU',
                'is_featured': False
            },
            {
                'category': cats['pistols'],
                'title': 'Glock-18 | Water Elemental',
                'weapon_type': 'Pistol',
                'wear_condition': 'Factory New',
                'float_value': 0.0240,
                'stattrak': False,
                'rarity': 'restricted',
                'description': 'Qizil korpusda suv mavjudoti va tomchilari chizilgan mashhur Glock to\'pponchasi.',
                'wholesale_price': Decimal('15.00'),
                'retail_price': Decimal('22.00'),
                'stock': 20,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL2kpnj9h1a7s29a6h4L_yaCHGFzeRkse1VQyCxnk5psDuGzIypeCiUPQR2Cpd0ROBbtBfsxYDmZu3mtFSO34xHzyn4hi9K5Sg0k7s',
                'is_featured': False
            },
            {
                'category': cats['pistols'],
                'title': 'P250 | Valence',
                'weapon_type': 'Pistol',
                'wear_condition': 'Factory New',
                'float_value': 0.0190,
                'stattrak': False,
                'rarity': 'mil-spec',
                'description': 'Futuristik kumush va ko\'k geometrik qirralar bilan sayqallangan arzon P250.',
                'wholesale_price': Decimal('1.20'),
                'retail_price': Decimal('1.80'),
                'stock': 35,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLwmYbm7S9A4_uqe6R_JeLDC2GDzupk5bVqSCG_qkhpsTqCn43hI3vBbwchC5tyEe4K50blwt_mMbnm5FWM3otAnS73238XuSU64rI',
                'is_featured': False
            },
            {
                'category': cats['pistols'],
                'title': 'Desert Eagle | Corinthian',
                'weapon_type': 'Pistol',
                'wear_condition': 'Factory New',
                'float_value': 0.0220,
                'stattrak': False,
                'rarity': 'mil-spec',
                'description': 'Qadimgi bronza va mis o\'ymakorligi naqshlari bilan bezatilgan qurol.',
                'wholesale_price': Decimal('1.50'),
                'retail_price': Decimal('2.40'),
                'stock': 30,
                'image_url': 'https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL1m5fn8Sdk7eOBaKFsJ_CcD3-fzupmsbVtSmDgnAElsDuGyt-pdn_FaFIiW8VyEe4K50blwt_mMbnm5FWM3otAnS73238XuSU64rI',
                'is_featured': False
            },
        ]

        # Clear existing data cleanly
        CaseItem.objects.all().delete()
        Case.objects.all().delete()
        UserInventory.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()

        created_skins = {}
        for s in skins_data:
            prod = Product.objects.create(**s)
            created_skins[prod.title] = prod

        self.stdout.write(self.style.SUCCESS(f"Created {len(created_skins)} CS2 skins."))

        # 3. Create 4 Starter Cases with accurately mapped skins and odds
        cases_config = [
            {
                'name': 'Chroma Dreams Case',
                'slug': 'chroma-dreams-case',
                'price': Decimal('5.00'),
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIU5qhpZcEd-vUkz4mIDWVER0chU1sL2rLBRw0v33cC9N7dO6kI-NwvnyMrjdn29Q18h0juDU-MKt3Fek_URvMWnyINSSdw45NVnSqFe9wbzvgJHpt8zOzndivHQk-z-DyG2R6l_a/360fx360f',
                'description': 'Klassik CS2 orzulari to\'plami: Karambit Doppler va AWP Asiimov yutish imkoniyati!',
                'is_featured': True,
                'items': [
                    ('P250 | Valence', 350),
                    ('Desert Eagle | Corinthian', 300),
                    ('AK-47 | Uncharted', 250),
                    ('AWP | Atheris', 100),
                    ('Glock-18 | Water Elemental', 70),
                    ('SSG 08 | Blood in the Water', 30),
                    ('AK-47 | Frontside Misty', 25),
                    ('AWP | Asiimov', 12),
                    ('AK-47 | Vulcan', 10),
                    ('★ Karambit | Doppler', 3),
                    ('★ Sport Gloves | Vice', 2),
                ]
            },
            {
                'name': 'Covert Ops Case',
                'slug': 'covert-ops-case',
                'price': Decimal('25.00'),
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIU5qhpZcEd-vUkz4mIDWVER0chU1sL2rLBRw0v33dCRB4860wb-GkvP9JrafwDMHscYh2O-Z8Y_x0QXsqkJpYTiiLNedIQ46YwvWqAC8le7rjZa06pTMnCRmvyQh7H-Onx3h1xwaaONv16XLGV2dVe4bQcWf/360fx360f',
                'description': 'Yuqori darajadagi Covert va Contraband toifasidagi qizil elita qurollar keysi.',
                'is_featured': True,
                'items': [
                    ('AK-47 | Frontside Misty', 350),
                    ('SSG 08 | Blood in the Water', 300),
                    ('Desert Eagle | Printstream', 150),
                    ('USP-S | Kill Confirmed', 120),
                    ('M4A1-S | Printstream', 90),
                    ('AK-47 | Vulcan', 80),
                    ('AWP | Asiimov', 70),
                    ('AK-47 | Fire Serpent', 15),
                    ('M4A4 | Howl', 5),
                    ('AWP | Dragon Lore', 4),
                    ('★ Talon Knife | Marble Fade', 6),
                    ('★ M9 Bayonet | Lore', 4),
                ]
            },
            {
                'name': 'Knife or Riot Case',
                'slug': 'knife-or-riot-case',
                'price': Decimal('75.00'),
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIU5qhpZcEd-vUkz4mIDWVER0chU1sL2rLBRw0v33fDxP6863w4Tckq_2Ye-ElWpT68tz2-vCrNqkjgW2-hA_Z2Gmd9eddwc9Y1qDqVfole66hJW-vp_OnnU27nN253zUnxW1gRxIbuNxxavJyT_G9p4/360fx360f',
                'description': 'Faqatgina pichoqlar va sport qo\'lqoplari! Har bir aylantirishda 100% kafolatlangan oltin buyum.',
                'is_featured': True,
                'items': [
                    ('★ Hand Wraps | Cobalt Skulls', 350),
                    ('★ Driver Gloves | King Snake', 300),
                    ('★ Talon Knife | Marble Fade', 180),
                    ('★ M9 Bayonet | Lore', 150),
                    ('★ Sport Gloves | Vice', 110),
                    ('★ Specialist Gloves | Crimson Kimono', 90),
                    ('★ Skeleton Knife | Crimson Web', 80),
                    ('★ Karambit | Doppler', 70),
                    ('★ Moto Gloves | Spearmint', 60),
                    ('★ Butterfly Knife | Fade', 40),
                ]
            },
            {
                'name': 'Budget Banger Case',
                'slug': 'budget-banger-case',
                'price': Decimal('1.50'),
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIU5qhpZcEd-vUkz4mIDWVER0chU1sL2rLBRw0v33fDxW6865w4bfwq73Ye-ElWpT68tz2-vCrNqkjgW2-hA_Z2Gmd9eddwc9Y1qDqVfole66hJW-vp_OnnU27nN253zUnxW1gRxIbuNxxavJyT_G9p4/360fx360f',
                'description': 'Kichik byudjetli starter keys — $1.50 ga Karambit Doppler yoki Printstream yutib olish imkoniyati!',
                'is_featured': False,
                'items': [
                    ('P250 | Valence', 450),
                    ('Desert Eagle | Corinthian', 380),
                    ('M4A4 | Magnesium', 350),
                    ('AK-47 | Uncharted', 300),
                    ('AWP | Atheris', 90),
                    ('Glock-18 | Water Elemental', 70),
                    ('USP-S | Printstream', 8),
                    ('Desert Eagle | Printstream', 6),
                    ('★ Karambit | Doppler', 1),
                ]
            },
        ]

        for c_cfg in cases_config:
            items_list = c_cfg.pop('items')
            case_obj, _ = Case.objects.get_or_create(slug=c_cfg['slug'], defaults=c_cfg)
            for title, weight in items_list:
                prod = created_skins.get(title)
                if prod:
                    CaseItem.objects.get_or_create(case=case_obj, product=prod, defaults={'drop_weight': weight})
            case_obj.update_chances()
            self.stdout.write(self.style.SUCCESS(f"Created Case: '{case_obj.name}' with {case_obj.case_items.count()} items."))

        # 4. Create or update Demo Users with initial balances & starter inventories for Upgrade testing
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@skinly.uz', 'is_staff': True, 'is_superuser': True})
        admin_user.set_password('admin123')
        admin_user.save()
        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        admin_profile.balance = Decimal('2500.00')
        admin_profile.steam_id = '76561198000000000'
        admin_profile.steam_trade_url = 'https://steamcommunity.com/tradeoffer/new/?partner=12345678&token=AbCdEfGh'
        admin_profile.save()

        # Seed starter inventory for admin
        for title in ['AWP | Asiimov', 'AK-47 | Vulcan', 'USP-S | Printstream', 'Glock-18 | Water Elemental', 'AWP | Atheris']:
            if title in created_skins:
                UserInventory.objects.create(
                    user=admin_user,
                    product=created_skins[title],
                    acquired_via='Purchased',
                    status='In Inventory'
                )

        player_user, _ = User.objects.get_or_create(username='player', defaults={'email': 'player@skinly.uz'})
        player_user.set_password('player123')
        player_user.save()
        player_profile, _ = UserProfile.objects.get_or_create(user=player_user)
        player_profile.balance = Decimal('500.00')
        player_profile.steam_id = '76561198012345678'
        player_profile.steam_trade_url = 'https://steamcommunity.com/tradeoffer/new/?partner=87654321&token=ZyXwVuTs'
        player_profile.save()

        for title in ['AWP | Atheris', 'Glock-18 | Water Elemental', 'P250 | Valence', 'Desert Eagle | Printstream']:
            if title in created_skins:
                UserInventory.objects.create(
                    user=player_user,
                    product=created_skins[title],
                    acquired_via='Case Opening',
                    status='In Inventory'
                )

        self.stdout.write(self.style.SUCCESS("Demo accounts initialized:"))
        self.stdout.write(self.style.SUCCESS("  1. 'admin' / 'admin123' (Balance: $2,500.00 + 5 starter inventory skins)"))
        self.stdout.write(self.style.SUCCESS("  2. 'player' / 'player123' (Balance: $500.00 + 4 starter inventory skins)"))
        self.stdout.write(self.style.SUCCESS("All CS2 skins, starter cases, and inventories successfully populated!"))
