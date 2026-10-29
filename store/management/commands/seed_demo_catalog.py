from decimal import Decimal
from pathlib import Path
from xml.sax.saxutils import escape

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from store.models import DemoCase, DemoCaseItem, DemoCollection, DemoItem


CASE_STYLES = [
    ('Aurora', 'Neon', '#35d6ff'),
    ('Obsidian', 'Shadow', '#a78bfa'),
    ('Solar', 'Ember', '#ff9d55'),
    ('Glacier', 'Frost', '#6ef0d2'),
    ('Phantom', 'Spectral', '#cf7cff'),
    ('Velocity', 'Cyber', '#568bff'),
    ('Lunar', 'Celestial', '#f58bbd'),
    ('Verdant', 'Jungle', '#94e96b'),
    ('Titanium', 'Chrome', '#b4c3dc'),
    ('Arcane', 'Mystic', '#ffdf6b'),
    ('Crimson', 'Vanguard', '#ff667d'),
    ('Quantum', 'Nova', '#54ecd1'),
]

ITEMS = [
    ('Aether Prism', 'rare', 'aurora', 'A refractive crystal with cool-spectrum facets.'),
    ('Midnight Circuit', 'epic', 'cyber', 'A precision-machined neon circuit emblem.'),
    ('Solaris Edge', 'legendary', 'ember', 'A bright geometric blade-inspired art object.'),
    ('Frostline Sigil', 'rare', 'frost', 'An icy crest rendered in crystalline glass.'),
    ('Violet Specter', 'epic', 'spectral', 'A luminous abstract phantom mask.'),
    ('Blue Shift Module', 'common', 'cyber', 'A clean cobalt alloy equipment module.'),
    ('Moonfall Relic', 'legendary', 'celestial', 'A celestial keepsake with layered rings.'),
    ('Canopy Shard', 'rare', 'jungle', 'A vivid green shard framed by foliage.'),
    ('Chrome Warden', 'epic', 'chrome', 'A silver guardian insignia.'),
    ('Golden Vector', 'legendary', 'mystic', 'A warm, angular energy token.'),
    ('Crimson Relay', 'rare', 'vanguard', 'A red signal marker with a glass core.'),
    ('Nova Compass', 'epic', 'nova', 'A cosmic navigation device.'),
    ('Prismatic Coil', 'common', 'aurora', 'A spiral chromatic energy coil.'),
    ('Nightwave Badge', 'rare', 'shadow', 'A dark enamel crest with a violet glow.'),
    ('Cinder Halo', 'epic', 'ember', 'A ring of stylized ember-like glass.'),
    ('Polar Engine', 'legendary', 'frost', 'A cold-blue mechanical core.'),
    ('Dreamcatcher Array', 'rare', 'spectral', 'A delicate network of radiant strands.'),
    ('Pulse Runner', 'common', 'cyber', 'A compact electric-blue runner emblem.'),
    ('Eclipse Token', 'epic', 'celestial', 'A dark disc crossed by a moonlit arc.'),
    ('Mosslight Totem', 'rare', 'jungle', 'A carved botanical gaming collectible.'),
    ('Mercury Bloom', 'legendary', 'chrome', 'A polished sculptural chrome flower.'),
    ('Oracle Lens', 'epic', 'mystic', 'A golden lens with a precise geometric frame.'),
    ('Scarlet Beacon', 'common', 'vanguard', 'A red beacon set in a dark alloy mount.'),
    ('Stellar Key', 'legendary', 'nova', 'A star-forged key-shaped art piece.'),
    ('Rainfall Matrix', 'rare', 'aurora', 'A flowing cyan and purple data sculpture.'),
    ('Void Lantern', 'epic', 'shadow', 'A tiny lantern holding a violet glow.'),
    ('Solar Flare Crest', 'legendary', 'ember', 'A stylized solar crest in warm glass.'),
    ('Icebound Marker', 'common', 'frost', 'A minimal frost-blue tactical marker.'),
    ('Echo Moth', 'rare', 'spectral', 'An iridescent abstract moth silhouette.'),
    ('Overclock Chip', 'epic', 'cyber', 'A glowing microchip with layered traces.'),
    ('Orbit Petal', 'legendary', 'celestial', 'A petal-like form in a planetary orbit.'),
    ('Emerald Static', 'common', 'jungle', 'A bright green shard with pixel accents.'),
    ('Silver Kestrel', 'epic', 'chrome', 'A streamlined silver bird motif.'),
    ('Runic Monolith', 'legendary', 'mystic', 'A floating relic with engraved symbols.'),
    ('Redshift Emblem', 'rare', 'vanguard', 'A graphic scarlet insignia.'),
    ('Quantum Bloom', 'epic', 'nova', 'A vivid burst of crystalline color.'),
    ('Duskline Capsule', 'common', 'shadow', 'A compact dark-blue capsule collectible.'),
    ('Aurora Spindle', 'rare', 'aurora', 'A narrow spindle with a shifting gradient.'),
    ('Ashen Crown', 'legendary', 'ember', 'An abstract crown with ember-like facets.'),
    ('Tidal Shard', 'common', 'frost', 'A wave-shaped shard in polished aqua.'),
    ('Phantom Circuit', 'epic', 'spectral', 'A ghostly violet circuit crest.'),
    ('Skybreaker Node', 'rare', 'cyber', 'A compact sky-blue energy node.'),
    ('Lunar Relay', 'common', 'celestial', 'A simple lunar station token.'),
    ('Wildsignal Crest', 'epic', 'jungle', 'A botanical emblem with bright green edges.'),
    ('Titan Bloom', 'legendary', 'chrome', 'A sculptural flower in brushed silver.'),
    ('Arcflash Rune', 'rare', 'mystic', 'A gold geometric mark with sharp edges.'),
    ('Ruby Vector', 'epic', 'vanguard', 'A precise red vector graphic.'),
    ('Deep Space Dial', 'legendary', 'nova', 'A dark cosmic dial with luminous markers.'),
    ('Prism Relay', 'common', 'aurora', 'A small prism inside a neon frame.'),
]

COLLECTIONS = [
    ('Neon Afterglow', 'A high-energy gallery of luminous cyber and aurora-inspired items.', 'Cyber'),
    ('Cold Front', 'Cool-spectrum glass, frost motifs and clean crystalline forms.', 'Frost'),
    ('Celestial Archive', 'Orbiting relics, moonlit tokens and star-forged silhouettes.', 'Celestial'),
    ('Verdant Protocol', 'Bright botanical emblems and jungle-green abstract collectibles.', 'Jungle'),
    ('Chrome Atelier', 'Sculptural metallic finishes and polished silver artwork.', 'Chrome'),
    ('Arcane Signals', 'Mystical geometry, golden runes and luminous abstract marks.', 'Mystic'),
]


def svg_art(title, hue, index, item=False):
    safe_title = escape(title)
    rotation = (index * 29) % 360
    center = 256
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{hue}" stop-opacity=".92"/><stop offset="1" stop-color="#12172e"/></linearGradient><radialGradient id="r"><stop stop-color="{hue}" stop-opacity=".52"/><stop offset="1" stop-color="#090c18" stop-opacity="0"/></radialGradient></defs>
<rect width="512" height="512" rx="48" fill="#090c18"/><rect width="512" height="512" rx="48" fill="url(#g)" opacity=".22"/><circle cx="{center}" cy="{center}" r="220" fill="url(#r)"/>
<g transform="rotate({rotation} 256 256)" fill="none" stroke="{hue}" stroke-opacity=".82">
<path d="M256 52 420 152v190L256 436 92 342V152z" stroke-width="{5 + index % 5}"/><path d="M256 100 378 174v142l-122 72-122-72V174z" stroke-width="2" opacity=".7"/>
<circle cx="256" cy="256" r="{52 + (index * 13) % 85}" stroke-width="3"/><path d="M256 90v332M90 256h332M138 138l236 236m0-236L138 374" stroke-width="1.5" opacity=".65"/>
</g>
<path d="M256 154 337 256l-81 102-81-102z" fill="url(#g)" stroke="{hue}" stroke-width="3" opacity=".88"/>
<text x="256" y="465" text-anchor="middle" fill="#eef4ff" font-family="Arial,sans-serif" font-size="{19 if len(title) < 20 else 15}" font-weight="700" letter-spacing="1.3">{safe_title}</text>
<text x="256" y="42" text-anchor="middle" fill="{hue}" font-family="Arial,sans-serif" font-size="11" letter-spacing="4">{'SHOWCASE ITEM' if item else 'SKINLY DEMO VAULT'}</text>
</svg>'''


class Command(BaseCommand):
    help = 'Create the local 120-case and 49-item cosmetic-only demo catalog.'

    @transaction.atomic
    def handle(self, *args, **options):
        cases_dir = Path(settings.BASE_DIR) / 'static' / 'demo' / 'cases'
        items_dir = Path(settings.BASE_DIR) / 'static' / 'demo' / 'items'
        cases_dir.mkdir(parents=True, exist_ok=True)
        items_dir.mkdir(parents=True, exist_ok=True)
        hue_palette = [style[2] for style in CASE_STYLES]
        demo_items = []
        for index, (name, rarity, theme, description) in enumerate(ITEMS):
            slug = slugify(name)
            image = f'demo/items/{slug}.svg'
            (items_dir / f'{slug}.svg').write_text(
                svg_art(name, hue_palette[index % len(hue_palette)], index, item=True),
                encoding='utf-8',
            )
            item, _ = DemoItem.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': description,
                    'image': image,
                    'demo_value': Decimal(5 + ((index * 47) % 890)).quantize(Decimal('0.01')),
                    'rarity': rarity,
                    'theme': theme,
                },
            )
            demo_items.append(item)

        colors = {style: hue for _, style, hue in CASE_STYLES}
        case_index = 0
        categories = ['Neon', 'Shadow', 'Ember', 'Frost', 'Spectral', 'Cyber',
                      'Celestial', 'Jungle', 'Chrome', 'Mystic']
        for prefix, theme, _ in CASE_STYLES:
            for suffix_index, category in enumerate(categories):
                name = f'{prefix} {category} Cache'
                slug = slugify(name)
                image = f'demo/cases/{slug}.svg'
                hue = colors[theme]
                (cases_dir / f'{slug}.svg').write_text(
                    svg_art(name, hue, case_index),
                    encoding='utf-8',
                )
                price = Decimal('99') + (Decimal('50') * case_index)
                case, _ = DemoCase.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'description': (
                            f'A {category.lower()}-inspired {theme.lower()} collection '
                            'with locally illustrated demo items and a predetermined reveal.'
                        ),
                        'category': category,
                        'theme': theme,
                        'cover_image': image,
                        'demo_price': price.quantize(Decimal('0.01')),
                        'is_featured': case_index < 6,
                    },
                )
                DemoCaseItem.objects.filter(case=case).delete()
                for drop_index in range(4):
                    item_index = (case_index * 3 + suffix_index + drop_index * 7) % len(demo_items)
                    DemoCaseItem.objects.create(
                        case=case,
                        item=demo_items[item_index],
                        is_demo_result=drop_index == 0,
                    )
                case_index += 1

        for title, description, theme in COLLECTIONS:
            collection, _ = DemoCollection.objects.update_or_create(
                slug=slugify(title),
                defaults={'title': title, 'description': description, 'theme': theme},
            )
            collection.items.set(
                [item for item in demo_items if item.theme == theme.lower()][:8],
            )
        self.stdout.write(self.style.SUCCESS(
            f'Seeded {DemoCase.objects.count()} unique demo cases, '
            f'{DemoItem.objects.count()} showcase items and '
            f'{DemoCollection.objects.count()} collections.'
        ))
