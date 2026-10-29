from decimal import Decimal
from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command, CommandError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .engagement import claim_mission, record_mission_activity
from .models import (
    CollectionComment, CommunityPoll, Notification, PollChoice, PollVote,
    PriceWatch, Product, ProductFavorite, ProductView, SkinBattle,
    SkinBattleVote, SkinCollection, SkinPriceHistory, UserProfile,
)


class EngagementFeatureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='collector', password='safe-test-password')
        self.other_user = User.objects.create_user(username='viewer', password='safe-test-password')
        self.skin_a = self.make_product('AK-47 | Neon Rider', 'Rifle', '12.00')
        self.skin_b = self.make_product('AWP | Neo-Noir', 'Sniper', '18.00')

    def make_product(self, title, weapon, price):
        return Product.objects.create(
            title=title,
            weapon_type=weapon,
            wholesale_price=Decimal(price),
            retail_price=Decimal(price),
            stock=1,
        )

    def test_battle_vote_is_auth_only_and_once_per_daily_match(self):
        battle = SkinBattle.objects.create(
            product_a=self.skin_a,
            product_b=self.skin_b,
            battle_date=timezone.localdate(),
        )
        anonymous_response = self.client.post(reverse('store:community'), {
            'action': 'vote_battle', 'battle_id': battle.pk, 'choice': self.skin_a.pk,
        })
        self.assertEqual(anonymous_response.status_code, 302)
        self.client.force_login(self.user)
        first = self.client.post(reverse('store:community'), {
            'action': 'vote_battle', 'battle_id': battle.pk, 'choice': self.skin_a.pk,
        })
        second = self.client.post(reverse('store:community'), {
            'action': 'vote_battle', 'battle_id': battle.pk, 'choice': self.skin_b.pk,
        })
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(SkinBattleVote.objects.filter(user=self.user, battle=battle).count(), 1)

    def test_homepage_and_community_render_from_live_catalog(self):
        self.assertEqual(self.client.get(reverse('store:index')).status_code, 200)
        self.assertEqual(self.client.get(reverse('store:community')).status_code, 200)
        self.assertContains(self.client.get(reverse('store:community')), 'Skin Battle')

    def test_skin_upgrade_uses_catalog_items_without_mutating_user_data(self):
        response = self.client.get(reverse('store:skin_upgrade'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Skin Upgrade Simulation')
        self.assertContains(response, 'Choose Your Skin')
        self.assertContains(response, 'Choose Target Skin')
        self.assertContains(response, reverse('store:api_upgrade_skins'))
        self.assertContains(response, '10%')
        self.assertContains(response, '75%')
        self.assertContains(response, 'gauge-result-success')
        self.assertContains(response, 'gauge-result-fail')
        self.assertEqual(self.user.profile.balance, Decimal('0.00'))
        self.assertFalse(self.user.inventory.exists())

    def test_product_without_an_image_uses_placeholder_not_another_skin(self):
        product = self.make_product('Skin without image', 'Rifle', '25.00')
        self.assertEqual(product.display_image, '/static/images/placeholder.svg')

    def test_product_catalog_validator_reports_duplicate_names_prices_and_images(self):
        self.skin_a.image_url = 'https://images.example.test/skins/neon-rider.png'
        self.skin_a.save(update_fields=['image_url'])
        duplicate = self.make_product(self.skin_a.title, 'Rifle', '12.00')
        duplicate.image_url = self.skin_a.image_url
        duplicate.save(update_fields=['image_url'])

        errors = StringIO()
        with self.assertRaises(CommandError):
            call_command('validate_product_catalog', stderr=errors)

        report = errors.getvalue()
        self.assertIn('Duplicate name', report)
        self.assertIn('Duplicate price', report)
        self.assertIn('Duplicate image reference', report)

    def test_product_catalog_validator_accepts_one_hundred_unique_products(self):
        Product.objects.all().delete()
        for index in range(100):
            product = self.make_product(f'Unique skin {index}', 'Rifle', f'{index + 1}.00')
            product.image_url = f'https://images.example.test/skins/{index}.png'
            product.save(update_fields=['image_url'])

        output = StringIO()
        call_command('validate_product_catalog', stdout=output)
        self.assertIn('Validated 100 products', output.getvalue())

        catalog = self.client.get(reverse('store:index'), {
            'q': 'Unique skin',
            'min_price': '50',
            'max_price': '60',
            'sort': 'retail_price',
            'page': '1',
        })
        self.assertEqual(catalog.status_code, 200)
        self.assertEqual(catalog.context['total_skins_count'], 11)
        self.assertEqual(catalog.context['products'][0].retail_price, Decimal('50.00'))
        self.assertEqual(catalog.context['page_obj'].paginator.num_pages, 1)

        detail = self.client.get(reverse('store:product_detail', kwargs={'slug': 'unique-skin-0'}))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, 'Unique skin 0')

    def test_upgrade_skin_api_returns_catalog_and_applies_search_filters(self):
        url = reverse('store:api_upgrade_skins')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {skin['title'] for skin in response.json()['skins']},
            {self.skin_a.title, self.skin_b.title},
        )
        first_skin = response.json()['skins'][0]
        self.assertEqual(first_skin['price'], str(Product.objects.get(pk=first_skin['id']).retail_price))
        self.assertIn('rarity', first_skin)
        self.assertIn('wear', first_skin)
        self.assertIn('weapon', first_skin)
        self.assertEqual(
            [skin['title'] for skin in self.client.get(url, {'q': 'Neon', 'weapon': 'Rifle'}).json()['skins']],
            [self.skin_a.title],
        )
        self.assertEqual(
            [skin['title'] for skin in self.client.get(url, {'min_price': '15'}).json()['skins']],
            [self.skin_b.title],
        )

    def test_upgrade_skin_api_rejects_invalid_price_filters(self):
        url = reverse('store:api_upgrade_skins')
        self.assertEqual(self.client.get(url, {'min_price': '-1'}).status_code, 400)
        self.assertEqual(self.client.get(url, {'min_price': '20', 'max_price': '10'}).status_code, 400)
        self.assertEqual(self.client.post(url).status_code, 405)

    def test_upgrade_chance_uses_live_prices_and_caps_at_one_hundred(self):
        endpoint = reverse('store:api_upgrade_chance')
        examples = [
            ('150.00', '200.00', '75.00000000'),
            ('150.00', '300.00', '50.00000000'),
            ('150.00', '600.00', '25.00000000'),
            ('150.00', '1500.00', '10.00000000'),
            ('10.00', '500.00', '2.00000000'),
            ('1000.00', '100.00', '100.00000000'),
            ('175.00', '5800.00', '3.01724138'),
            ('12.40', '100.00', '12.40000000'),
            ('74.60', '100.00', '74.60000000'),
            ('99.80', '100.00', '99.80000000'),
        ]
        for index, (source_price, target_price, expected_chance) in enumerate(examples):
            with self.subTest(source=source_price, target=target_price):
                source = self.make_product(f'Chance source {index}', 'Rifle', source_price)
                target = self.make_product(f'Chance target {index}', 'Sniper', target_price)
                response = self.client.get(endpoint, {
                    'source_id': source.pk,
                    'target_id': target.pk,
                })
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['chance'], expected_chance)
                self.assertEqual(response.json()['source_price'], source_price)
                self.assertEqual(response.json()['target_price'], target_price)

    def test_upgrade_chance_rejects_missing_same_or_invalid_price_skins(self):
        endpoint = reverse('store:api_upgrade_chance')
        self.assertEqual(self.client.get(endpoint).status_code, 400)
        self.assertEqual(self.client.get(endpoint, {
            'source_id': self.skin_a.pk,
            'target_id': self.skin_a.pk,
        }).status_code, 400)
        self.assertEqual(self.client.get(endpoint, {
            'source_id': self.skin_a.pk,
            'target_id': 999999,
        }).status_code, 404)
        free_skin = self.make_product('Invalid zero price', 'Rifle', '0.00')
        self.assertEqual(self.client.get(endpoint, {
            'source_id': free_skin.pk,
            'target_id': self.skin_a.pk,
        }).status_code, 400)

    def test_private_collection_is_visible_only_to_owner(self):
        collection = SkinCollection.objects.create(
            owner=self.user, title='Private loadout', is_public=False,
        )
        url = reverse('store:collection_detail', kwargs={'share_id': collection.share_id})
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_collection_creation_and_product_management_persist(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('store:community'), {
            'action': 'create_collection',
            'title': 'My AWP skins',
            'description': 'Favorites for a loadout',
            'is_public': 'on',
        })
        self.assertEqual(response.status_code, 302)
        collection = SkinCollection.objects.get(owner=self.user)
        self.client.post(reverse('store:community'), {
            'action': 'collection_item',
            'collection_id': collection.pk,
            'product_id': self.skin_b.pk,
        })
        self.assertEqual(collection.items.count(), 1)

    def test_weekly_poll_only_accepts_one_vote_per_user(self):
        poll = CommunityPoll.objects.create(
            title='Pick the skin of the week',
            starts_at=timezone.now(),
            ends_at=timezone.now() + timedelta(days=3),
        )
        choice_a = PollChoice.objects.create(poll=poll, product=self.skin_a)
        PollChoice.objects.create(poll=poll, product=self.skin_b)
        self.client.force_login(self.user)
        for _ in range(2):
            response = self.client.post(reverse('store:community'), {
                'action': 'poll_vote', 'poll_id': poll.pk, 'choice_id': choice_a.pk,
            })
            self.assertEqual(response.status_code, 302)
        self.assertEqual(PollVote.objects.filter(poll=poll, user=self.user).count(), 1)

    def test_preferences_persist_and_browsing_history_can_be_cleared(self):
        self.client.force_login(self.user)
        ProductView.objects.create(user=self.user, product=self.skin_a)
        self.client.post(reverse('store:community'), {
            'action': 'save_preferences',
            'weapon_preferences': ['Rifle'],
            'preferred_min_price': '5.00',
            'preferred_max_price': '50.00',
        })
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.weapon_preferences, ['Rifle'])
        self.assertEqual(profile.preferred_min_price, Decimal('5.00'))
        self.client.post(reverse('store:community'), {'action': 'clear_history'})
        self.assertFalse(ProductView.objects.filter(user=self.user).exists())

    def test_comment_output_is_escaped(self):
        collection = SkinCollection.objects.create(owner=self.user, title='Showcase')
        CollectionComment.objects.create(
            collection=collection,
            user=self.other_user,
            content='<script>alert("skinly")</script>',
        )
        response = self.client.get(
            reverse('store:collection_detail', kwargs={'share_id': collection.share_id})
        )
        self.assertContains(response, '&lt;script&gt;alert(&quot;skinly&quot;)&lt;/script&gt;', html=False)
        self.assertNotContains(response, '<script>alert("skinly")</script>', html=False)

    def test_mission_xp_awarded_once_after_real_progress(self):
        third_skin = self.make_product('M4A1-S | Decimator', 'Rifle', '9.00')
        for skin in (self.skin_a, self.skin_b, third_skin):
            record_mission_activity(self.user, 'view', skin.pk)
        self.assertTrue(claim_mission(self.user, 'daily_views'))
        self.assertFalse(claim_mission(self.user, 'daily_views'))
        profile = UserProfile.objects.get(user=self.user)
        profile.refresh_from_db()
        self.assertEqual(profile.experience_points, 20)
        self.assertEqual(self.user.mission_claims.count(), 1)

    def test_price_watch_alert_uses_actual_price_change_once(self):
        watch = PriceWatch.objects.create(
            user=self.user, product=self.skin_a, target_price=Decimal('10.00'),
        )
        self.skin_a.retail_price = Decimal('8.00')
        self.skin_a.save()
        self.assertEqual(
            Notification.objects.filter(user=self.user, notification_type='price_drop').count(),
            1,
        )
        history_count = SkinPriceHistory.objects.filter(product=self.skin_a).count()
        self.skin_a.description = 'Description-only edit'
        self.skin_a.save()
        self.assertEqual(SkinPriceHistory.objects.filter(product=self.skin_a).count(), history_count)
        self.assertEqual(
            Notification.objects.filter(user=self.user, notification_type='price_drop').count(),
            1,
        )
        watch.refresh_from_db()
        self.assertIsNotNone(watch.notified_at)

    def test_favorite_toggle_is_csrf_protected_and_persisted(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        url = reverse('store:api_favorite_toggle')
        self.assertEqual(csrf_client.post(url, {'product_id': self.skin_a.pk}).status_code, 403)
        self.client.force_login(self.user)
        add = self.client.post(url, {'product_id': self.skin_a.pk})
        remove = self.client.post(url, {'product_id': self.skin_a.pk})
        self.assertTrue(add.json()['is_favorite'])
        self.assertFalse(remove.json()['is_favorite'])
        self.assertFalse(ProductFavorite.objects.filter(user=self.user, product=self.skin_a).exists())
