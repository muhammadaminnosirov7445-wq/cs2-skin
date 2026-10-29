from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import translation

from .models import (
    DemoActivity, DemoCase, DemoCaseItem, DemoCollection, DemoDailyClaim,
    DemoFavorite, DemoInventory, DemoItem, DemoUserSettings, UserProfile,
    DemoWallet, DemoWalletTransaction,
)


class DemoPlatformTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='demo-player', password='safe-test-password')
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)
        self.item = DemoItem.objects.create(
            name='Aurora Prism',
            slug='aurora-prism',
            description='A refractive showcase object.',
            image='demo/items/aurora-prism.svg',
            demo_value=Decimal('125.00'),
            rarity='rare',
            theme='aurora',
        )
        self.other_item = DemoItem.objects.create(
            name='Chrome Warden',
            slug='chrome-warden',
            description='A polished showcase object.',
            image='demo/items/chrome-warden.svg',
            demo_value=Decimal('240.00'),
            rarity='epic',
            theme='chrome',
        )
        self.case = DemoCase.objects.create(
            name='Aurora Neon Cache',
            slug='aurora-neon-cache',
            description='A predetermined demo case.',
            category='Neon',
            theme='Neon',
            cover_image='demo/cases/aurora-neon-cache.svg',
            demo_price=Decimal('25.00'),
        )
        DemoCaseItem.objects.create(case=self.case, item=self.item, is_demo_result=True)
        DemoCaseItem.objects.create(case=self.case, item=self.other_item)

    def test_demo_home_and_case_detail_render_without_external_assets(self):
        self.assertEqual(self.client.get(reverse('store:demo_home')).status_code, 200)
        detail = self.client.get(reverse('store:demo_case_detail', args=[self.case.slug]))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, 'DROP TABLE')
        self.assertEqual(
            {drop.demo_chance for drop in detail.context['drops']},
            {Decimal('50.00')},
        )
        self.assertContains(detail, 'Sign in to open with demo credits')

    def test_case_detail_renders_quantity_controls_and_cost_preview(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('store:demo_case_detail', args=[self.case.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-case-quantity')
        for quantity in (1, 2, 3, 4, 5, 10):
            with self.subTest(quantity=quantity):
                self.assertContains(response, f'data-quantity-option="{quantity}"')
        self.assertContains(response, 'data-case-total')

    def test_game_page_uses_shared_demo_styles_and_local_catalog_art(self):
        self.case.is_featured = True
        self.case.save(update_fields=['is_featured'])
        response = self.client.get(reverse('store:game'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/static/css/demo.css"')
        self.assertContains(response, 'href="/static/css/skinly-immersive.css"')
        self.assertNotContains(response, 'cdn.tailwindcss.com')
        self.assertContains(response, f'/static/{self.case.cover_image}')
        self.assertContains(response, f'/static/{self.item.image}')

    def test_upgrade_lab_uses_shared_visuals_and_demo_multipliers(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('store:demo_upgrade'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-upgrade-reactor')
        self.assertContains(response, 'PROTOCOL')
        self.assertNotContains(response, 'class="page-intro"')
        self.assertContains(response, 'data-upgrade-pointer')
        self.assertContains(response, 'data-upgrade-success')
        self.assertContains(response, 'data-upgrade-fail')
        self.assertContains(response, 'data-duration="4800"')
        for multiplier in ('1.5', '2', '5', '10'):
            with self.subTest(multiplier=multiplier):
                self.assertContains(response, f'data-multiplier="{multiplier}"')
        self.assertContains(response, 'skinly-immersive.css')

    def test_upgrade_selector_values_are_unlocalized_for_javascript_number_parsing(self):
        self.client.force_login(self.user)
        with translation.override('uz'):
            response = self.client.get(reverse('store:demo_upgrade'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-value="125.00"')
        self.assertContains(response, 'data-value="240.00"')

    def test_case_search_filter_sort_and_pagination(self):
        for index in range(13):
            DemoCase.objects.create(
                name=f'Neon Case {index:02d}',
                slug=f'neon-case-{index:02d}',
                description='Independent catalog entry.',
                category='Neon' if index < 8 else 'Frost',
                theme='Neon',
                cover_image=f'demo/cases/neon-case-{index:02d}.svg',
                demo_price=Decimal(index + 1),
            )
        response = self.client.get(reverse('store:demo_cases'), {
            'q': 'Neon Case', 'category': 'Neon', 'sort': 'price_high',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 8)
        self.assertEqual(response.context['cases'][0].demo_price, Decimal('8.00'))
        page = self.client.get(reverse('store:demo_cases'), {'page': '2'})
        self.assertEqual(page.context['page_obj'].number, 2)
        self.assertEqual(list(page.context['cases'])[-1].slug, self.case.slug)

    def test_demo_item_catalog_filters_theme_rarity_price_and_sort_together(self):
        third = DemoItem.objects.create(
            name='Aurora Spindle',
            slug='aurora-spindle',
            description='A cyan spindle.',
            image='demo/items/aurora-spindle.svg',
            demo_value=Decimal('80.00'),
            rarity='rare',
            theme='aurora',
        )
        response = self.client.get(reverse('store:demo_items'), {
            'q': 'aurora',
            'theme': 'aurora',
            'rarity': 'rare',
            'min_price': '80',
            'max_price': '130',
            'sort': 'value_low',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item.pk for item in response.context['items']],
            [third.pk, self.item.pk],
        )
        invalid = self.client.get(reverse('store:demo_items'), {
            'min_price': '130', 'max_price': '80',
        })
        self.assertContains(invalid, 'valid non-negative demo value range')
        self.assertEqual(invalid.context['min_price'], '')

    def test_case_theme_filter_and_favorite_state_are_rendered(self):
        alternate_theme = DemoCase.objects.create(
            name='Aurora Frost Cache',
            slug='aurora-frost-cache',
            description='A cold-spectrum demo collection.',
            category='Frost',
            theme='Aurora',
            cover_image='demo/cases/aurora-frost-cache.svg',
            demo_price=Decimal('40.00'),
        )
        DemoCaseItem.objects.create(case=alternate_theme, item=self.item)
        response = self.client.get(reverse('store:demo_cases'), {'theme': 'Aurora'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['cases']), [alternate_theme])
        self.client.force_login(self.user)
        self.client.post(reverse('store:demo_action'), {
            'action': 'favorite_case',
            'target_id': alternate_theme.pk,
        })
        favorites = self.client.get(reverse('store:demo_cases'), {'theme': 'Aurora'})
        self.assertContains(favorites, 'aria-pressed="true"')
        self.assertContains(favorites, 'Remove from favorites')

    def test_private_sections_redirect_anonymous_users_to_login(self):
        for route_name in ('demo_upgrade', 'demo_inventory'):
            with self.subTest(route=route_name):
                path = reverse(f'store:{route_name}')
                response = self.client.get(path)
                self.assertRedirects(response, f"{reverse('store:login')}?next={path}")

    def test_anonymous_demo_actions_and_invalid_targets_return_json_errors(self):
        endpoint = reverse('store:demo_action')
        anonymous = self.client.post(endpoint, {'action': 'case_open', 'case_id': self.case.pk})
        self.assertEqual(anonymous.status_code, 401)
        self.assertIn('error', anonymous.json())
        self.client.force_login(self.user)
        invalid = self.client.post(endpoint, {
            'action': 'case_open', 'case_id': 'not-an-id', 'request_id': str(uuid4()),
        })
        missing = self.client.post(endpoint, {
            'action': 'case_open', 'case_id': 987654321, 'request_id': str(uuid4()),
        })
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(missing.status_code, 404)
        self.assertIn('error', missing.json())

    def test_all_demo_sections_render_for_signed_in_user(self):
        self.client.force_login(self.user)
        route_names = [
            'demo_battles', 'demo_upgrade', 'demo_contracts', 'demo_inventory',
            'demo_profile', 'demo_favorites', 'demo_history', 'demo_daily_rewards',
            'demo_missions', 'demo_leaderboard', 'demo_collections', 'demo_settings',
            'demo_notifications', 'demo_items',
        ]
        for route_name in route_names:
            with self.subTest(route=route_name):
                response = self.client.get(reverse(f'store:{route_name}'))
                self.assertEqual(response.status_code, 200)

    def test_case_open_uses_demo_wallet_inventory_and_persistent_history(self):
        self.client.force_login(self.user)
        wallet, _ = DemoWallet.objects.get_or_create(user=self.user)
        before = wallet.balance
        request_id = uuid4()
        response = self.client.post(reverse('store:demo_action'), {
            'action': 'case_open', 'case_id': self.case.pk, 'request_id': str(request_id),
        })
        self.assertEqual(response.status_code, 200)
        result_id = response.json()['result']['id']
        self.assertIn(result_id, [self.item.pk, self.other_item.pk])
        self.assertEqual(Decimal(response.json()['balance']), before - self.case.demo_price)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, before - self.case.demo_price)
        self.assertEqual(DemoWalletTransaction.objects.filter(wallet=wallet).count(), 1)
        self.assertTrue(DemoInventory.objects.filter(user=self.user, item_id=result_id).exists())
        self.assertEqual(
            DemoActivity.objects.filter(user=self.user, activity_type='case_open').count(), 1,
        )
        replay = self.client.post(reverse('store:demo_action'), {
            'action': 'case_open', 'case_id': self.case.pk, 'request_id': str(request_id),
        })
        self.assertEqual(replay.status_code, 200)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, before - self.case.demo_price)
        self.assertEqual(DemoWalletTransaction.objects.filter(wallet=wallet).count(), 1)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.balance, Decimal('0.00'))
        self.assertTrue(DemoActivity.objects.filter(user=self.user, activity_type='case_open').exists())

    def test_case_open_supports_every_quantity_and_charges_once_per_case(self):
        self.client.force_login(self.user)
        wallet, _ = DemoWallet.objects.get_or_create(user=self.user)
        for quantity in (1, 2, 3, 4, 5, 10):
            with self.subTest(quantity=quantity):
                request_id = uuid4()
                response = self.client.post(reverse('store:demo_action'), {
                    'action': 'case_open',
                    'case_id': self.case.pk,
                    'quantity': str(quantity),
                    'request_id': str(request_id),
                })
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data['quantity'], quantity)
                self.assertEqual(len(data['results']), quantity)
                self.assertEqual(len(data['inventory_ids']), quantity)
                self.assertEqual(Decimal(data['total_cost']), self.case.demo_price * quantity)
                self.assertEqual(
                    Decimal(data['balance']),
                    wallet.balance - self.case.demo_price * quantity,
                )
                wallet.refresh_from_db()
        self.assertEqual(
            DemoInventory.objects.filter(user=self.user).count(),
            sum((1, 2, 3, 4, 5, 10)),
        )
        self.assertEqual(DemoWalletTransaction.objects.filter(wallet=wallet).count(), 6)
        history = self.client.get(reverse('store:demo_history'))
        self.assertEqual(history.status_code, 200)
        self.assertContains(history, self.case.name)

    def test_case_open_rejects_unsupported_quantities_without_mutating_state(self):
        self.client.force_login(self.user)
        wallet, _ = DemoWallet.objects.get_or_create(user=self.user)
        starting_balance = wallet.balance
        for quantity in ('0', '6', '-1', '1.5', 'invalid'):
            with self.subTest(quantity=quantity):
                response = self.client.post(reverse('store:demo_action'), {
                    'action': 'case_open',
                    'case_id': self.case.pk,
                    'quantity': quantity,
                    'request_id': str(uuid4()),
                })
                self.assertEqual(response.status_code, 400)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, starting_balance)
        self.assertFalse(DemoInventory.objects.filter(user=self.user).exists())
        self.assertFalse(DemoWalletTransaction.objects.filter(wallet=wallet).exists())

    def test_case_open_replay_cannot_change_quantity_or_charge_twice(self):
        self.client.force_login(self.user)
        wallet, _ = DemoWallet.objects.get_or_create(user=self.user)
        request_id = uuid4()
        endpoint = reverse('store:demo_action')
        payload = {
            'action': 'case_open',
            'case_id': self.case.pk,
            'quantity': '3',
            'request_id': str(request_id),
        }
        first = self.client.post(endpoint, payload)
        replay = self.client.post(endpoint, payload)
        changed_quantity = self.client.post(endpoint, {**payload, 'quantity': '2'})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(replay.status_code, 200)
        self.assertEqual(replay.json(), first.json())
        self.assertEqual(changed_quantity.status_code, 409)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal('10000.00') - self.case.demo_price * 3)
        self.assertEqual(DemoInventory.objects.filter(user=self.user).count(), 3)
        self.assertEqual(DemoWalletTransaction.objects.filter(wallet=wallet).count(), 1)

    def test_case_open_with_insufficient_demo_balance_changes_nothing(self):
        self.client.force_login(self.user)
        wallet, _ = DemoWallet.objects.get_or_create(user=self.user)
        wallet.balance = Decimal('0.00')
        wallet.save(update_fields=['balance', 'updated_at'])
        response = self.client.post(reverse('store:demo_action'), {
            'action': 'case_open',
            'case_id': self.case.pk,
            'request_id': str(uuid4()),
        })
        self.assertEqual(response.status_code, 409)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal('0.00'))
        self.assertFalse(DemoInventory.objects.filter(user=self.user).exists())
        self.assertFalse(DemoWalletTransaction.objects.filter(wallet=wallet).exists())
        self.assertFalse(DemoActivity.objects.filter(user=self.user, activity_type='case_open').exists())

    def test_case_open_checks_balance_against_total_quantity_cost(self):
        self.client.force_login(self.user)
        wallet, _ = DemoWallet.objects.get_or_create(user=self.user)
        wallet.balance = self.case.demo_price
        wallet.save(update_fields=['balance', 'updated_at'])
        response = self.client.post(reverse('store:demo_action'), {
            'action': 'case_open',
            'case_id': self.case.pk,
            'quantity': '2',
            'request_id': str(uuid4()),
        })
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['required'], str(self.case.demo_price * 2))
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, self.case.demo_price)
        self.assertFalse(DemoInventory.objects.filter(user=self.user).exists())

    def test_case_open_request_id_cannot_be_replayed_for_another_case(self):
        self.client.force_login(self.user)
        another_case = DemoCase.objects.create(
            name='Shadow Frost Cache',
            slug='shadow-frost-cache',
            description='Another demo collection.',
            category='Frost',
            theme='Shadow',
            cover_image='demo/cases/shadow-frost-cache.svg',
            demo_price=Decimal('10.00'),
        )
        DemoCaseItem.objects.create(case=another_case, item=self.item)
        request_id = uuid4()
        endpoint = reverse('store:demo_action')
        first = self.client.post(endpoint, {
            'action': 'case_open', 'case_id': self.case.pk, 'request_id': str(request_id),
        })
        replay = self.client.post(endpoint, {
            'action': 'case_open', 'case_id': another_case.pk, 'request_id': str(request_id),
        })
        self.assertEqual(first.status_code, 200)
        self.assertEqual(replay.status_code, 409)
        self.assertEqual(DemoWalletTransaction.objects.count(), 1)
        self.assertEqual(DemoInventory.objects.filter(user=self.user).count(), 1)

    def test_case_open_request_id_cannot_be_replayed_as_inventory_sale(self):
        self.client.force_login(self.user)
        endpoint = reverse('store:demo_action')
        request_id = uuid4()
        opened = self.client.post(endpoint, {
            'action': 'case_open',
            'case_id': self.case.pk,
            'request_id': str(request_id),
        })
        wallet, _ = DemoWallet.objects.get_or_create(user=self.user)
        balance_after_open = wallet.balance
        conflict = self.client.post(endpoint, {
            'action': 'inventory_sell',
            'inventory_id': opened.json()['inventory_id'],
            'request_id': str(request_id),
        })
        self.assertEqual(conflict.status_code, 409)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, balance_after_open)

    def test_demo_actions_retain_csrf_protection(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        endpoint = reverse('store:demo_action')
        payload = {'action': 'case_open', 'case_id': self.case.pk, 'request_id': str(uuid4())}
        self.assertEqual(client.post(endpoint, payload).status_code, 403)
        client.get(reverse('store:demo_case_detail', args=[self.case.slug]))
        csrf_token = client.cookies['csrftoken'].value
        accepted = client.post(endpoint, payload, HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(accepted.status_code, 200)

    def test_successful_upgrade_consumes_only_owned_source_and_adds_target(self):
        self.client.force_login(self.user)
        wallet, _ = DemoWallet.objects.get_or_create(user=self.user)
        starting_balance = wallet.balance
        source_entry = DemoInventory.objects.create(
            user=self.user, item=self.item, source='case',
        )
        request_id = uuid4()
        payload = {
            'action': 'upgrade',
            'source_id': source_entry.pk,
            'target_id': self.other_item.pk,
            'request_id': str(request_id),
            'multiplier': '2',
        }
        with patch('store.demo_views.secrets.randbelow', return_value=0):
            response = self.client.post(reverse('store:demo_action'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['chance'], '18.22')
        self.assertEqual(response.json()['multiplier'], '2')
        self.assertEqual(response.json()['result']['id'], self.other_item.pk)
        self.assertFalse(DemoInventory.objects.filter(pk=source_entry.pk).exists())
        self.assertTrue(DemoInventory.objects.filter(user=self.user, item=self.other_item).exists())
        self.assertTrue(DemoActivity.objects.filter(user=self.user, activity_type='upgrade').exists())
        self.assertEqual(self.profile.balance, Decimal('0.00'))
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, starting_balance)
        replay = self.client.post(reverse('store:demo_action'), payload)
        self.assertEqual(replay.status_code, 200)
        self.assertEqual(replay.json(), response.json())
        self.assertEqual(DemoInventory.objects.filter(user=self.user, item=self.other_item).count(), 1)
        changed_payload = {**payload, 'multiplier': '5'}
        conflict = self.client.post(reverse('store:demo_action'), changed_payload)
        self.assertEqual(conflict.status_code, 409)

    def test_failed_upgrade_preserves_source_item_and_never_accepts_other_users_inventory(self):
        self.client.force_login(self.user)
        other = User.objects.create_user(username='inventory-owner', password='safe-test-password')
        other_entry = DemoInventory.objects.create(user=other, item=self.item, source='case')
        response = self.client.post(reverse('store:demo_action'), {
            'action': 'upgrade', 'source_id': other_entry.pk,
            'target_id': self.other_item.pk, 'request_id': str(uuid4()),
        })
        self.assertEqual(response.status_code, 404)
        source_entry = DemoInventory.objects.create(user=self.user, item=self.item, source='case')
        with patch('store.demo_views.secrets.randbelow', return_value=9999):
            failed = self.client.post(reverse('store:demo_action'), {
                'action': 'upgrade', 'source_id': source_entry.pk,
                'target_id': self.other_item.pk, 'request_id': str(uuid4()),
            })
        self.assertEqual(failed.status_code, 200)
        self.assertFalse(failed.json()['success'])
        self.assertGreater(Decimal(failed.json()['chance']), Decimal('0'))
        self.assertTrue(DemoInventory.objects.filter(pk=source_entry.pk, user=self.user).exists())

    def test_upgrade_multiplier_is_validated_and_probability_is_server_calculated(self):
        self.client.force_login(self.user)
        source_entry = DemoInventory.objects.create(user=self.user, item=self.item, source='case')
        endpoint = reverse('store:demo_action')
        invalid = self.client.post(endpoint, {
            'action': 'upgrade',
            'source_id': source_entry.pk,
            'target_id': self.other_item.pk,
            'request_id': str(uuid4()),
            'multiplier': '999',
        })
        self.assertEqual(invalid.status_code, 400)
        self.assertIn('ko‘paytirgichi', invalid.json()['error'])
        with patch('store.demo_views.secrets.randbelow', return_value=9999):
            response = self.client.post(endpoint, {
                'action': 'upgrade',
                'source_id': source_entry.pk,
                'target_id': self.other_item.pk,
                'request_id': str(uuid4()),
                'multiplier': '10',
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['chance'], '5.00')
        self.assertTrue(DemoInventory.objects.filter(pk=source_entry.pk, user=self.user).exists())

    def test_every_supported_multiplier_uses_server_chance_calculation(self):
        self.client.force_login(self.user)
        source_entry = DemoInventory.objects.create(user=self.user, item=self.item, source='case')
        expected = {
            '1.5': ('15', '24.30'),
            '2': ('20', '18.22'),
            '5': ('50', '7.29'),
            '10': ('100', '5.00'),
        }
        for multiplier, (multiplier_tenths, chance) in expected.items():
            with self.subTest(multiplier=multiplier):
                with patch('store.demo_views.secrets.randbelow', return_value=9999):
                    response = self.client.post(reverse('store:demo_action'), {
                        'action': 'upgrade',
                        'source_id': source_entry.pk,
                        'target_id': self.other_item.pk,
                        'request_id': str(uuid4()),
                        'multiplier': multiplier,
                    })
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['multiplier_tenths'], int(multiplier_tenths))
                self.assertEqual(response.json()['chance'], chance)
                self.assertEqual(
                    response.json()['chance_basis_points'],
                    int(Decimal(chance) * 100),
                )
    def test_upgrade_25_50_and_75_percent_server_outcomes_match_inventory_updates(self):
        self.client.force_login(self.user)
        DemoItem.objects.filter(pk=self.item.pk).update(demo_value=Decimal('100.00'))
        source_item = DemoItem.objects.get(pk=self.item.pk)
        endpoint = reverse('store:demo_action')
        chance_targets = {
            '25.00': Decimal('186.66'),
            '50.00': Decimal('93.33'),
            '75.00': Decimal('62.22'),
        }
        for expected_chance, target_value in chance_targets.items():
            with self.subTest(chance=expected_chance):
                DemoItem.objects.filter(pk=self.other_item.pk).update(demo_value=target_value)
                target = DemoItem.objects.get(pk=self.other_item.pk)
                source_entry = DemoInventory.objects.create(
                    user=self.user, item=source_item, source='case',
                )
                basis_points = int(Decimal(expected_chance) * 100)
                success_payload = {
                    'action': 'upgrade',
                    'source_id': source_entry.pk,
                    'target_id': target.pk,
                    'request_id': str(uuid4()),
                    'multiplier': '1.5',
                    'success': 'false',
                }
                with patch('store.demo_views.secrets.randbelow', return_value=basis_points - 1):
                    success_response = self.client.post(endpoint, success_payload)
                self.assertEqual(success_response.status_code, 200)
                self.assertEqual(success_response.json()['chance'], expected_chance)
                self.assertTrue(success_response.json()['success'])
                self.assertFalse(DemoInventory.objects.filter(pk=source_entry.pk).exists())
                self.assertTrue(DemoInventory.objects.filter(user=self.user, item=target).exists())

                retained_source = DemoInventory.objects.create(
                    user=self.user, item=source_item, source='case',
                )
                failure_payload = {
                    **success_payload,
                    'source_id': retained_source.pk,
                    'request_id': str(uuid4()),
                    'success': 'true',
                }
                with patch('store.demo_views.secrets.randbelow', return_value=basis_points):
                    failure_response = self.client.post(endpoint, failure_payload)
                self.assertEqual(failure_response.status_code, 200)
                self.assertEqual(failure_response.json()['chance'], expected_chance)
                self.assertFalse(failure_response.json()['success'])
                self.assertTrue(
                    DemoInventory.objects.filter(pk=retained_source.pk, user=self.user).exists(),
                )

    def test_inventory_sale_credits_demo_wallet_once_and_is_user_scoped(self):
        self.client.force_login(self.user)
        wallet, _ = DemoWallet.objects.get_or_create(user=self.user)
        before = wallet.balance
        other = User.objects.create_user(username='sale-owner', password='safe-test-password')
        other_entry = DemoInventory.objects.create(user=other, item=self.item, source='case')
        unauthorized = self.client.post(reverse('store:demo_action'), {
            'action': 'inventory_sell',
            'inventory_id': other_entry.pk,
            'request_id': str(uuid4()),
        })
        self.assertEqual(unauthorized.status_code, 404)
        other_wallet, _ = DemoWallet.objects.get_or_create(user=other)
        other_balance = other_wallet.balance
        other_wallet.refresh_from_db()
        self.assertEqual(other_wallet.balance, other_balance)
        entry = DemoInventory.objects.create(user=self.user, item=self.item, source='case')
        request_id = uuid4()
        payload = {
            'action': 'inventory_sell',
            'inventory_id': entry.pk,
            'request_id': str(request_id),
        }
        response = self.client.post(reverse('store:demo_action'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(DemoInventory.objects.filter(pk=entry.pk).exists())
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, before + self.item.demo_value)
        self.assertEqual(DemoWalletTransaction.objects.filter(wallet=wallet).count(), 1)
        replay = self.client.post(reverse('store:demo_action'), payload)
        self.assertEqual(replay.status_code, 200)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, before + self.item.demo_value)
        other_entry_for_user = DemoInventory.objects.create(
            user=self.user,
            item=self.other_item,
            source='case',
        )
        mismatched_replay = self.client.post(reverse('store:demo_action'), {
            **payload,
            'inventory_id': other_entry_for_user.pk,
        })
        self.assertEqual(mismatched_replay.status_code, 409)
        self.assertTrue(DemoInventory.objects.filter(pk=other_entry_for_user.pk).exists())
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.balance, Decimal('0.00'))

    def test_favorites_are_user_scoped_and_persist(self):
        other = User.objects.create_user(username='other-player', password='safe-test-password')
        self.client.force_login(self.user)
        response = self.client.post(reverse('store:demo_action'), {
            'action': 'favorite_case', 'target_id': self.case.pk,
        })
        self.assertTrue(response.json()['saved'])
        self.assertEqual(DemoFavorite.objects.filter(user=self.user).count(), 1)
        self.assertFalse(DemoFavorite.objects.filter(user=other).exists())
        self.client.post(reverse('store:demo_action'), {
            'action': 'favorite_case', 'target_id': self.case.pk,
        })
        self.assertFalse(DemoFavorite.objects.filter(user=self.user).exists())

    def test_daily_reward_and_settings_are_database_backed(self):
        self.client.force_login(self.user)
        action_url = reverse('store:demo_action')
        reward = self.client.post(action_url, {'action': 'claim_daily'})
        self.assertEqual(reward.status_code, 200)
        self.assertEqual(reward.json()['xp'], 10)
        duplicate = self.client.post(action_url, {'action': 'claim_daily'})
        self.assertEqual(duplicate.status_code, 409)
        settings_response = self.client.post(action_url, {
            'action': 'save_settings',
            'dark_theme_enabled': 'true',
            'sound_enabled': 'false',
            'animations_enabled': 'true',
            'notifications_enabled': 'false',
            'display_name': 'Demo Pilot',
            'bio': 'Private demo profile',
        })
        self.assertEqual(settings_response.status_code, 200)
        saved_settings = DemoUserSettings.objects.get(user=self.user)
        self.assertEqual(saved_settings.display_name, 'Demo Pilot')
        self.assertTrue(saved_settings.dark_theme_enabled)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.experience_points, 10)
        self.assertEqual(self.profile.bio, 'Private demo profile')
        self.assertEqual(DemoDailyClaim.objects.filter(user=self.user).count(), 1)
        theme = self.client.post(action_url, {'action': 'save_theme', 'theme': 'light'})
        self.assertEqual(theme.status_code, 200)
        self.assertFalse(DemoUserSettings.objects.get(user=self.user).dark_theme_enabled)

    def test_mission_claim_is_idempotent_and_records_demo_xp_once(self):
        self.client.force_login(self.user)
        for index in range(3):
            DemoActivity.objects.create(
                user=self.user,
                activity_type='case_open',
                details={'case_id': self.case.pk + index},
            )
        endpoint = reverse('store:demo_action')
        payload = {'action': 'claim_mission', 'mission': 'cases'}
        first = self.client.post(endpoint, payload)
        replay = self.client.post(endpoint, payload)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(replay.status_code, 200)
        self.assertEqual(first.json(), replay.json())
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.experience_points, 25)
        self.assertEqual(
            DemoActivity.objects.filter(
                user=self.user,
                activity_type='daily_reward',
                details__mission_key__startswith='mission_cases_',
            ).count(),
            1,
        )

    def test_contract_requires_three_unique_items_and_records_valid_preview(self):
        third = DemoItem.objects.create(
            name='Lunar Relay', slug='lunar-relay', description='A lunar token.',
            image='demo/items/lunar-relay.svg', demo_value=Decimal('45.00'),
            rarity='common', theme='celestial',
        )
        self.client.force_login(self.user)
        endpoint = reverse('store:demo_action')
        invalid = self.client.post(endpoint, {
            'action': 'contract', 'item_ids': [self.item.pk, self.other_item.pk],
        })
        self.assertEqual(invalid.status_code, 400)
        valid = self.client.post(endpoint, {
            'action': 'contract',
            'item_ids': [self.item.pk, self.other_item.pk, third.pk],
        })
        self.assertEqual(valid.status_code, 200)
        self.assertEqual(valid.json()['result']['id'], self.item.pk)
        self.assertTrue(DemoActivity.objects.filter(user=self.user, activity_type='contract').exists())

    def test_seed_collections_are_registered_as_database_records(self):
        DemoCollection.objects.create(
            title='Neon Afterglow', slug='neon-afterglow',
            description='A gallery.', theme='Cyber',
        )
        response = self.client.get(reverse('store:demo_collections'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Neon Afterglow')

    def test_contract_with_user_inventory_consumes_inputs_and_grants_output(self):
        self.client.force_login(self.user)
        i1 = DemoInventory.objects.create(user=self.user, item=self.item, source='case')
        i2 = DemoInventory.objects.create(user=self.user, item=self.other_item, source='case')
        third = DemoItem.objects.create(
            name='Lunar Relay Beta', slug='lunar-relay-beta', description='Token',
            image='demo/items/lunar-relay.svg', demo_value=Decimal('50.00'),
            rarity='common', theme='celestial',
        )
        i3 = DemoInventory.objects.create(user=self.user, item=third, source='case')

        res = self.client.post(reverse('store:demo_action'), {
            'action': 'contract',
            'inventory_ids': [i1.pk, i2.pk, i3.pk],
        })
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['ok'])
        # Original 3 items consumed
        self.assertFalse(DemoInventory.objects.filter(pk__in=[i1.pk, i2.pk, i3.pk]).exists())
        # New contract item exists in user inventory
        self.assertTrue(DemoInventory.objects.filter(user=self.user, source='contract').exists())

    def test_case_battle_simulation_returns_four_rounds_and_winner(self):
        self.client.force_login(self.user)
        res = self.client.post(reverse('store:demo_action'), {'action': 'battle'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['ok'])
        self.assertEqual(len(data['rounds']), 4)
        self.assertIn('winner', data)
        self.assertIn('case', data['rounds'][0])
        self.assertIn('name', data['rounds'][0]['case'])
        self.assertTrue(DemoActivity.objects.filter(user=self.user, activity_type='battle').exists())

    def test_case_battle_with_request_id_and_replay_idempotency(self):
        self.client.force_login(self.user)
        req_id = str(uuid4())
        res1 = self.client.post(reverse('store:demo_action'), {'action': 'battle', 'request_id': req_id})
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertTrue(data1['ok'])

        # Replay with same request_id must return identical response without duplicate records
        count_before = DemoActivity.objects.filter(user=self.user, activity_type='battle').count()
        res2 = self.client.post(reverse('store:demo_action'), {'action': 'battle', 'request_id': req_id})
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data1['winner'], data2['winner'])
        self.assertEqual(data1['player_total'], data2['player_total'])
        self.assertEqual(data1['bot_total'], data2['bot_total'])
        count_after = DemoActivity.objects.filter(user=self.user, activity_type='battle').count()
        self.assertEqual(count_before, count_after)

    def test_case_battle_page_renders_stepper_and_dual_arena(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse('store:demo_battles'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'data-battle-stage')
        self.assertContains(res, 'data-battle-stepper')
        self.assertContains(res, 'data-battle-live-arena')
        self.assertContains(res, 'data-battle-speed-toggle')
        self.assertContains(res, 'ROUND 01')
        self.assertContains(res, 'ROUND 04')

    def test_wallet_topup_adds_credits_and_records_transaction(self):
        self.client.force_login(self.user)
        wallet = DemoWallet.objects.get_or_create(user=self.user)[0]
        initial = wallet.balance
        res = self.client.post(reverse('store:demo_action'), {'action': 'topup_wallet'})
        self.assertEqual(res.status_code, 200)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, initial + Decimal('5000.00'))
        self.assertTrue(DemoWalletTransaction.objects.filter(wallet=wallet, amount=Decimal('5000.00')).exists())

    def test_get_starter_skin_adds_inventory_item(self):
        self.client.force_login(self.user)
        res = self.client.post(reverse('store:demo_action'), {'action': 'get_starter_skin'})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['ok'])
        self.assertTrue(DemoInventory.objects.filter(user=self.user, source='starter').exists())

    def test_inventory_filtering_by_query_and_rarity(self):
        self.client.force_login(self.user)
        DemoInventory.objects.create(user=self.user, item=self.item, source='case')
        DemoInventory.objects.create(user=self.user, item=self.other_item, source='case')
        res = self.client.get(reverse('store:demo_inventory'), {'q': 'Aurora', 'rarity': 'rare'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['inventory']), 1)
        self.assertEqual(res.context['inventory'][0].item.name, 'Aurora Prism')

    def test_demo_action_rejects_get_request_and_redirects(self):
        """Verify non-POST request to /demo/action/ redirects cleanly without exposing JSON."""
        res = self.client.get(reverse('store:demo_action'))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('store:demo_cases'), res.headers['Location'])

    def test_case_detail_has_onsubmit_prevention_and_multi_stage(self):
        """Ensure case_detail.html contains inline submit prevention to prevent raw JSON navigation."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('store:demo_case_detail', args=[self.case.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'onsubmit="event.preventDefault(); return false;"')
        self.assertContains(response, 'data-multi-stage')
        self.assertContains(response, 'data-case-quantity')

    def test_save_theme_supports_custom_styles(self):
        """Ensure save_theme action supports cyber, crimson, and gold themes."""
        self.client.force_login(self.user)
        endpoint = reverse('store:demo_action')
        for theme_name in ('cyber', 'crimson', 'gold'):
            with self.subTest(theme=theme_name):
                res = self.client.post(endpoint, {'action': 'save_theme', 'theme': theme_name})
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertTrue(data['ok'])
                self.assertEqual(data['theme'], theme_name)
                self.assertTrue(DemoUserSettings.objects.get(user=self.user).dark_theme_enabled)

    def test_case_open_json_includes_total_value_and_inventory_records(self):
        """Verify case_open returns total_value along with results."""
        self.client.force_login(self.user)
        res = self.client.post(reverse('store:demo_action'), {
            'action': 'case_open',
            'case_id': self.case.pk,
            'quantity': '2',
            'request_id': str(uuid4()),
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('total_value', data)
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 2)
        expected_total = sum(Decimal(r['demo_value']) for r in data['results'])
        self.assertEqual(Decimal(data['total_value']), expected_total)

