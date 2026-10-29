from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, UserProfile


class Command(BaseCommand):
    help = 'Seeds realistic Counter-Strike 2 (CS2) skins and categories into Skinly'

    def handle(self, *args, **options):
        self.stdout.write("Populating CS2 Skinly skins collection...")

        # 1. Categories
        categories_data = [
            {'name': 'Knives (Pichoqlar)', 'slug': 'knives', 'icon': 'sword'},
            {'name': 'Gloves (Qo‘lqoplar)', 'slug': 'gloves', 'icon': 'hand'},
            {'name': 'Sniper Rifles (Snayper)', 'slug': 'snipers', 'icon': 'crosshair'},
            {'name': 'Rifles (Avtomatlar)', 'slug': 'rifles', 'icon': 'target'},
            {'name': 'Pistols (To‘pponchalar)', 'slug': 'pistols', 'icon': 'zap'},
        ]

        cats = {}
        for c in categories_data:
            cat, _ = Category.objects.get_or_create(slug=c['slug'], defaults={'name': c['name'], 'icon': c['icon']})
            cats[c['slug']] = cat

        # 2. Authentic CS2 Skins Dataset
        skins_data = [
            {
                'category': cats['knives'],
                'title': '★ Butterfly Knife | Fade',
                'weapon_type': 'Butterfly Knife',
                'wear_condition': 'Factory New',
                'float_value': 0.0124,
                'stattrak': True,
                'rarity': 'extraordinary',
                'description': 'Afsonaviy Butterfly pichoq, 99.8% Fade naqshiga ega. Yuqori sifatli animatsiya va Counter-Strike 2 Source 2 dvigatelida to\'liq aks etuvchi yaltiroq xrom korpus.',
                'wholesale_price': Decimal('2800.00'),
                'retail_price': Decimal('3450.00'),
                'stock': 2,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovbSsLQJf1f_BYQJB-dChgL-GkvP9JrafwDMHscYh2-2V94in31Xk-UVkYm_yd9eddwc2YQ7T-VfsyO_o05S-757Nyydk7HQ8pSGKEV2S0wY/360fx360f',
                'is_featured': True
            },
            {
                'category': cats['knives'],
                'title': '★ Karambit | Doppler Phase 2',
                'weapon_type': 'Karambit',
                'wear_condition': 'Factory New',
                'float_value': 0.0089,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Karambit Doppler Phase 2 ("Pink Galaxy"). Toza burchak (Clean corner) va kamyob qirmizi-pushti rang kombinatsiyasi. CS2 da o\'ta mashhur.',
                'wholesale_price': Decimal('1400.00'),
                'retail_price': Decimal('1820.00'),
                'stock': 3,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovbSsLQJf2PLacDBA5ciJlY20hPbkI7fUqWZU7Mxkh6eSoommigfl8hJsNTiiJNPEd1A7MF_R-FS8xr2-h8Dt7pnIzndjvyN3-z-DyG2NqTf0/360fx360f',
                'is_featured': True
            },
            {
                'category': cats['snipers'],
                'title': 'AWP | Dragon Lore',
                'weapon_type': 'AWP',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1850,
                'stattrak': False,
                'rarity': 'covert',
                'description': 'Counter-Strike tarixidagi eng afsonaviy snayper quroli. Qadimgi ajdaho nafasi tasvirlangan. Har bir kolleksionerning orzusi.',
                'wholesale_price': Decimal('4500.00'),
                'retail_price': Decimal('5800.00'),
                'stock': 1,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot621FAR17PLfYQJD_9W7m5a0n_L1JaKfzzoGuMl03-rE89Sn2wW3-kdtam-mddfAcVU7Z1vV-VW4yO3t18W47ZSan3Rhv3V35XnemB3i1B5SLrs4VbkqT9M/360fx360f',
                'is_featured': True
            },
            {
                'category': cats['rifles'],
                'title': 'AK-47 | Fire Serpent',
                'weapon_type': 'AK-47',
                'wear_condition': 'Minimal Wear',
                'float_value': 0.0820,
                'stattrak': True,
                'rarity': 'covert',
                'description': 'StatTrak™ hisoblagichiga ega Bravo to\'plami afsonasi. Old yog\'och qismida mayya uslubidagi olovli ilon chizilgan.',
                'wholesale_price': Decimal('850.00'),
                'retail_price': Decimal('1150.00'),
                'stock': 5,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV19m5h5SEhePLP7LWnn8fscEm07zH89St0Qe3r0s5ZzuncdeccANoMl-DrFS8wbzvjcS8vZ2anCRluCN37X_cnBWzi0pSLrs44n-67hQ/360fx360f',
                'is_featured': True
            },
            {
                'category': cats['rifles'],
                'title': 'M4A4 | Howl',
                'weapon_type': 'M4A4',
                'wear_condition': 'Factory New',
                'float_value': 0.0350,
                'stattrak': False,
                'rarity': 'covert',
                'description': 'Kamyob "Contraband" toifasidagi yagona qurol. Qizil olovli bo\'ri naqshi CS2 yorug\'lik nurlari ostida hayratlanarli darajada porlaydi.',
                'wholesale_price': Decimal('4200.00'),
                'retail_price': Decimal('5300.00'),
                'stock': 1,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou-6kejhjxszFJTwW09izh4-GkvP9JrafwDMHscR33-qUp9Sg2wbs-EJkZ2-hIdOWdgBsZgnSq1W8yejqh5G-uJ7OzXdhunUr-z-DyC8r_Gk0/360fx360f',
                'is_featured': True
            },
            {
                'category': cats['gloves'],
                'title': '★ Sport Gloves | Vice',
                'weapon_type': 'Sport Gloves',
                'wear_condition': 'Field-Tested',
                'float_value': 0.2210,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Neon ko\'k va yorqin pushti rangdagi sport qo\'lqoplari. Karambit yoki Butterfly Fade bilan ideal kombinatsiya hosil qiladi.',
                'wholesale_price': Decimal('1100.00'),
                'retail_price': Decimal('1450.00'),
                'stock': 4,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DAQ1h3LndbyP supervisor_image/vice_gloves/360fx360f',
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovbSsLQJfxuHbZC597c2JmImMn-O6N7rDkGdf7cNxjO3-_Y33i1WyphooZ2mhLdCRcwVtNFiG_Ae4kOm8gJ60vs6fmnQyvCMr7HnVyhXln1gSOV-JvA_w/360fx360f',
                'is_featured': False
            },
            {
                'category': cats['pistols'],
                'title': 'Desert Eagle | Printstream',
                'weapon_type': 'Desert Eagle',
                'wear_condition': 'Factory New',
                'float_value': 0.0210,
                'stattrak': True,
                'rarity': 'covert',
                'description': 'Oq emal va marvariddek kamalak nur qaytaruvchi tekstura. StatTrak™ bilan har bir yutuqli o\'q hisobda bo\'ladi.',
                'wholesale_price': Decimal('95.00'),
                'retail_price': Decimal('140.00'),
                'stock': 12,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgposr-kLAtl7PDdTjlH_9mkgL-OlvD4NoTck29Y_cg_3u3Hot2ijVHm-RdpNT36JY-RI1VoY1GCrAC-wL3mhsK4v5TPmnFh63J27X6PnAv330_Z8vL3dQ/360fx360f',
                'is_featured': False
            },
            {
                'category': cats['rifles'],
                'title': 'AK-47 | Vulcan',
                'weapon_type': 'AK-47',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1650,
                'stattrak': False,
                'rarity': 'covert',
                'description': 'Futuristik sport uslubidagi oq, ko\'k va qora uglerod tolalari uyg\'unligi. CS2 hamjamiyatida eng uzoq yillik klassika.',
                'wholesale_price': Decimal('180.00'),
                'retail_price': Decimal('260.00'),
                'stock': 8,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV1924mIGZqOT8PLHeqWNU6dNoxOvD8N6m2wXm_0dpY2D7IoWRelc6N1qGqFm4kOjugpe6vZufy3IxvnYq-z-DyMvHlQ9Z/360fx360f',
                'is_featured': False
            },
            {
                'category': cats['snipers'],
                'title': 'AWP | Asiimov',
                'weapon_type': 'AWP',
                'wear_condition': 'Field-Tested',
                'float_value': 0.2450,
                'stattrak': True,
                'rarity': 'covert',
                'description': 'Sci-Fi ilmiy-fantastik dizayndagi to\'q sariq va oq geometrik naqsh. StatTrak™ texnologiyasi bilan jihozlangan.',
                'wholesale_price': Decimal('120.00'),
                'retail_price': Decimal('175.00'),
                'stock': 15,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot621FAR17P7NdTRH-t26q4SZlvD7PYTQgXtu5Mx2gv2Po9WkiwLm-UdrYTv6INeTI1A8YV7T_FO7kunmhZW8vpWan3dmvCA8pSGK6wP2W6A/360fx360f',
                'is_featured': False
            },
            {
                'category': cats['pistols'],
                'title': 'USP-S | Kill Confirmed',
                'weapon_type': 'USP-S',
                'wear_condition': 'Minimal Wear',
                'float_value': 0.0980,
                'stattrak': False,
                'rarity': 'covert',
                'description': 'O\'q bosh suyagiga tegib parchalanayotgan lahzani aks ettiruvchi dramatik illyustratsiya. Ovoz so\'ndiruvchi (silencer) bilan.',
                'wholesale_price': Decimal('110.00'),
                'retail_price': Decimal('165.00'),
                'stock': 9,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpoo6m1FBRp3_bGcjhQ09-jq5WYh8j_OrfdqWhe5sN4mOTE8bP4jVC9vh5yZmigdtOSewc4N1_X_VS5wrvo15a6vsmbyCE3viAn-z-DyF98616Y/360fx360f',
                'is_featured': False
            },
            {
                'category': cats['knives'],
                'title': '★ M9 Bayonet | Lore',
                'weapon_type': 'M9 Bayonet',
                'wear_condition': 'Field-Tested',
                'float_value': 0.1920,
                'stattrak': False,
                'rarity': 'extraordinary',
                'description': 'Oltinrang qoplama va tig\' bo\'ylab yugurgan nafis tugunli o\'yma naqshlar. Qadimiy skandinav mifologiyasi uslubida.',
                'wholesale_price': Decimal('950.00'),
                'retail_price': Decimal('1280.00'),
                'stock': 3,
                'image_url': 'https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovbSsLQJfxuHbZC597dGJjoWJhfb4PLXFhGpC4cZih-zF8o_321K2_EJoYGHxJoecJAc7N16F-1W3x7_rh5ftup_KznJhv3Vy7X7ZzAv3309W30Xf/360fx360f',
                'is_featured': False
            },
        ]

        for s in skins_data:
            Product.objects.create(**s)

        # 3. Create Demo Superuser/Dropshipper
        if not User.objects.filter(username='admin').exists():
            u = User.objects.create_superuser('admin', 'admin@skinly.uz', 'admin123')
            profile, _ = UserProfile.objects.get_or_create(user=u)
            profile.balance = Decimal('1500.00')
            profile.steam_id = '76561198000000000'
            profile.steam_trade_url = 'https://steamcommunity.com/tradeoffer/new/?partner=12345678&token=AbCdEfGh'
            profile.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: 'admin' / 'admin123' with $1,500.00 balance!"))

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(skins_data)} authentic CS2 skins!"))
