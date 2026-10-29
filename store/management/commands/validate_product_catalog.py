from collections import defaultdict
from urllib.parse import urlsplit

from django.core.management.base import BaseCommand, CommandError

from store.models import Product


def normalize_image_reference(product):
    if product.image:
        return 'file:' + product.image.name.strip().casefold()
    if not product.image_url:
        return ''
    parsed = urlsplit(product.image_url.strip())
    if parsed.scheme and parsed.netloc:
        return 'url:' + parsed.netloc.casefold() + parsed.path.rstrip('/').casefold()
    return 'url:' + product.image_url.strip().casefold()


class Command(BaseCommand):
    help = 'Validate product catalog count and unique IDs, names, prices, and image references.'

    def add_arguments(self, parser):
        parser.add_argument('--expected-count', type=int, default=100)

    def handle(self, *args, **options):
        expected_count = options['expected_count']
        if expected_count < 1:
            raise CommandError('--expected-count must be greater than zero.')

        products = list(Product.objects.only('id', 'title', 'retail_price', 'image', 'image_url'))
        errors = []
        if len(products) != expected_count:
            errors.append(f'Expected {expected_count} products, found {len(products)}.')

        identifiers = defaultdict(list)
        names = defaultdict(list)
        prices = defaultdict(list)
        images = defaultdict(list)
        for product in products:
            identifiers[product.pk].append(product.title)
            names[product.title.strip().casefold()].append(product.title)
            prices[product.retail_price].append(product.title)
            image_reference = normalize_image_reference(product)
            if image_reference:
                images[image_reference].append(product.title)
            else:
                errors.append(f'Product {product.pk} ({product.title}) has no image reference.')

        for label, values in (
            ('ID', identifiers),
            ('name', names),
            ('price', prices),
            ('image reference', images),
        ):
            for value, titles in values.items():
                if len(titles) > 1:
                    errors.append(f'Duplicate {label} {value!r}: {", ".join(titles)}.')

        if errors:
            for error in errors:
                self.stderr.write(self.style.ERROR(error))
            raise CommandError(f'Product catalog validation failed with {len(errors)} issue(s).')

        self.stdout.write(self.style.SUCCESS(
            f'Validated {len(products)} products; IDs, names, prices, and image references are unique.'
        ))
