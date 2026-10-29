
from django.core.management.base import BaseCommand
from store.models import DemoCase
from decimal import Decimal

class Command(BaseCommand):
    help = 'Updates demo case prices to a more premium range.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Updating demo case prices...'))

        # Define new prices for existing cases.
        # This is an example and assumes some cases exist.
        # You might need to adjust case names/slugs based on your actual data.
        price_updates = {
            'aurora-neon-cache': Decimal('99.00'),
            'aurora-ember-cache': Decimal('149.00'),
            'aurora-cyber-cache': Decimal('199.00'),
            'aurora-spectral-cache': Decimal('249.00'),
            'aurora-shadow-cache': Decimal('299.00'),
            'aurora-frost-cache': Decimal('349.00'),
            'aurora-celestial-cache': Decimal('399.00'),
            'aurora-jungle-cache': Decimal('449.00'),
            'aurora-chrome-cache': Decimal('499.00'),
            'aurora-mystic-cache': Decimal('549.00'),

            'obsidian-neon-cache': Decimal('599.00'),
            'obsidian-ember-cache': Decimal('649.00'),
            'obsidian-cyber-cache': Decimal('699.00'),
            'obsidian-spectral-cache': Decimal('749.00'),
            'obsidian-shadow-cache': Decimal('799.00'),
            'obsidian-frost-cache': Decimal('849.00'),
            'obsidian-celestial-cache': Decimal('899.00'),
            'obsidian-jungle-cache': Decimal('949.00'),
            'obsidian-chrome-cache': Decimal('999.00'),
            'obsidian-mystic-cache': Decimal('1049.00'),

            'solar-neon-cache': Decimal('1099.00'),
            'solar-ember-cache': Decimal('1149.00'),
            'solar-cyber-cache': Decimal('1199.00'),
            'solar-spectral-cache': Decimal('1249.00'),
            'solar-shadow-cache': Decimal('1299.00'),
            'solar-frost-cache': Decimal('1349.00'),
            'solar-celestial-cache': Decimal('1399.00'),
            'solar-jungle-cache': Decimal('1449.00'),
            'solar-chrome-cache': Decimal('1499.00'),
            'solar-mystic-cache': Decimal('1549.00'),

            'glacier-neon-cache': Decimal('1599.00'),
            'glacier-ember-cache': Decimal('1649.00'),
            'glacier-cyber-cache': Decimal('1699.00'),
            'glacier-spectral-cache': Decimal('1749.00'),
            'glacier-shadow-cache': Decimal('1799.00'),
            'glacier-frost-cache': Decimal('1849.00'),
            'glacier-celestial-cache': Decimal('1899.00'),
            'glacier-jungle-cache': Decimal('1949.00'),
            'glacier-chrome-cache': Decimal('1999.00'),
            'glacier-mystic-cache': Decimal('2049.00'),

            'phantom-neon-cache': Decimal('2099.00'),
            'phantom-ember-cache': Decimal('2149.00'),
            'phantom-cyber-cache': Decimal('2199.00'),
            'phantom-spectral-cache': Decimal('2249.00'),
            'phantom-shadow-cache': Decimal('2299.00'),
            'phantom-frost-cache': Decimal('2349.00'),
            'phantom-celestial-cache': Decimal('2399.00'),
            'phantom-jungle-cache': Decimal('2449.00'),
            'phantom-chrome-cache': Decimal('2499.00'),
            'phantom-mystic-cache': Decimal('2549.00'),

            'velocity-neon-cache': Decimal('2599.00'),
            'velocity-ember-cache': Decimal('2649.00'),
            'velocity-cyber-cache': Decimal('2699.00'),
            'velocity-spectral-cache': Decimal('2749.00'),
            'velocity-shadow-cache': Decimal('2799.00'),
            'velocity-frost-cache': Decimal('2849.00'),
            'velocity-celestial-cache': Decimal('2899.00'),
            'velocity-jungle-cache': Decimal('2949.00'),
            'velocity-chrome-cache': Decimal('2999.00'),
            'velocity-mystic-cache': Decimal('3049.00'),

            'lunar-neon-cache': Decimal('3099.00'),
            'lunar-ember-cache': Decimal('3149.00'),
            'lunar-cyber-cache': Decimal('3199.00'),
            'lunar-spectral-cache': Decimal('3249.00'),
            'lunar-shadow-cache': Decimal('3299.00'),
            'lunar-frost-cache': Decimal('3349.00'),
            'lunar-celestial-cache': Decimal('3399.00'),
            'lunar-jungle-cache': Decimal('3449.00'),
            'lunar-chrome-cache': Decimal('3499.00'),
            'lunar-mystic-cache': Decimal('3549.00'),

            'verdant-neon-cache': Decimal('3599.00'),
            'verdant-ember-cache': Decimal('3649.00'),
            'verdant-cyber-cache': Decimal('3699.00'),
            'verdant-spectral-cache': Decimal('3749.00'),
            'verdant-shadow-cache': Decimal('3799.00'),
            'verdant-frost-cache': Decimal('3849.00'),
            'verdant-celestial-cache': Decimal('3899.00'),
            'verdant-jungle-cache': Decimal('3949.00'),
            'verdant-chrome-cache': Decimal('3999.00'),
            'verdant-mystic-cache': Decimal('4049.00'),

            'titanium-neon-cache': Decimal('4099.00'),
            'titanium-ember-cache': Decimal('4149.00'),
            'titanium-cyber-cache': Decimal('4199.00'),
            'titanium-spectral-cache': Decimal('4249.00'),
            'titanium-shadow-cache': Decimal('4299.00'),
            'titanium-frost-cache': Decimal('4349.00'),
            'titanium-celestial-cache': Decimal('4399.00'),
            'titanium-jungle-cache': Decimal('4449.00'),
            'titanium-chrome-cache': Decimal('4499.00'),
            'titanium-mystic-cache': Decimal('4549.00'),

            'arcane-neon-cache': Decimal('4599.00'),
            'arcane-ember-cache': Decimal('4649.00'),
            'arcane-cyber-cache': Decimal('4699.00'),
            'arcane-spectral-cache': Decimal('4749.00'),
            'arcane-shadow-cache': Decimal('4799.00'),
            'arcane-frost-cache': Decimal('4849.00'),
            'arcane-celestial-cache': Decimal('4899.00'),
            'arcane-jungle-cache': Decimal('4949.00'),
            'arcane-chrome-cache': Decimal('4999.00'),
            'arcane-mystic-cache': Decimal('5049.00'),

            'crimson-neon-cache': Decimal('5099.00'),
            'crimson-ember-cache': Decimal('5149.00'),
            'crimson-cyber-cache': Decimal('5199.00'),
            'crimson-spectral-cache': Decimal('5249.00'),
            'crimson-shadow-cache': Decimal('5299.00'),
            'crimson-frost-cache': Decimal('5349.00'),
            'crimson-celestial-cache': Decimal('5399.00'),
            'crimson-jungle-cache': Decimal('5449.00'),
            'crimson-chrome-cache': Decimal('5499.00'),
            'crimson-mystic-cache': Decimal('5549.00'),

            'quantum-neon-cache': Decimal('5599.00'),
            'quantum-ember-cache': Decimal('5649.00'),
            'quantum-cyber-cache': Decimal('5699.00'),
            'quantum-spectral-cache': Decimal('5749.00'),
            'quantum-shadow-cache': Decimal('5799.00'),
            'quantum-frost-cache': Decimal('5849.00'),
            'quantum-celestial-cache': Decimal('5899.00'),
            'quantum-jungle-cache': Decimal('5949.00'),
            'quantum-chrome-cache': Decimal('5999.00'),
            'quantum-mystic-cache': Decimal('6049.00'),
        }

        updated_count = 0
        for slug, new_price in price_updates.items():
            try:
                case = DemoCase.objects.get(slug=slug)
                if case.demo_price != new_price:
                    case.demo_price = new_price
                    case.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated case "{case.name}" price to {new_price}'))
                    updated_count += 1
                else:
                    self.stdout.write(self.style.NOTICE(f'Case "{case.name}" already has price {new_price}, skipping.'))
            except DemoCase.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Case with slug "{slug}" not found, skipping.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating case with slug "{slug}": {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully updated prices for {updated_count} demo cases.'))
