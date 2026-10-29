
from django.core.management.base import BaseCommand
from store.models import DemoCase

class Command(BaseCommand):
    help = 'Lists all demo cases with their current prices.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Listing all demo cases...'))

        cases = DemoCase.objects.all().order_by('name')

        if not cases.exists():
            self.stdout.write(self.style.WARNING('No demo cases found in the database.'))
            return

        for case in cases:
            self.stdout.write(f'Name: {case.name}, Slug: {case.slug}, Current Price: {case.demo_price}')

        self.stdout.write(self.style.SUCCESS('Finished listing demo cases.'))
