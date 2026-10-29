from django.db import migrations
from django.utils.text import slugify

def generate_missing_slugs(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    for product in Product.objects.filter(slug=''):
        base_slug = slugify(product.title)
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exclude(pk=product.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        product.slug = slug
        product.save(update_fields=['slug'])

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(generate_missing_slugs, reverse_code=migrations.RunPython.noop),
    ]
