from datetime import timedelta
from decimal import Decimal, InvalidOperation
import json
import secrets
import uuid

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Max, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from urllib.parse import urlencode

from .models import (
    DemoActivity, DemoCase, DemoCaseItem, DemoCollection, DemoDailyClaim,
    DemoFavorite, DemoInventory, DemoItem, DemoUserSettings, UserProfile,
    DemoWallet, DemoWalletTransaction,
)


SECTIONS = {
    'battles': ('Case battles', 'A round-by-round multiplayer-inspired preview. Every outcome is preselected.'),
    'upgrade': ('Upgrade demo', 'Use an item from your own inventory in a server-resolved demo upgrade.'),
    'contracts': ('Contracts', 'Combine at least three showcase items to preview a fixed collection result.'),
    'inventory': ('Demo inventory', 'Your private gallery of non-transferable demo items.'),
    'profile': ('Player profile', 'Your account details, demo progress and recent activity.'),
    'favorites': ('Favorites', 'The cases and showcase items you have bookmarked.'),
    'history': ('Demo history', 'A private timeline of your case previews and simulations.'),
    'daily-rewards': ('Daily rewards', 'Claim a small amount of non-transferable demo XP once per day.'),
    'missions': ('Missions', 'Complete demo activities to earn non-monetary XP.'),
    'leaderboard': ('Leaderboard', 'A public ranking based only on demo activity and XP.'),
    'collections': ('Collections', 'Browse curated themes and their showcase galleries.'),
    'settings': ('Settings', 'Manage your profile, sound, animation and notification preferences.'),
    'notifications': ('Notifications', 'Review notifications addressed to your account.'),
    'items': ('Item gallery', 'Browse distinctive, purely illustrative demo items.'),
}

NAVIGATION = [
    ('home', 'Home', 'demo_home'),
    ('cases', 'Cases', 'demo_cases'),
    ('battles', 'Case battles', 'demo_battles'),
    ('upgrade', 'Upgrade demo', 'demo_upgrade'),
    ('contracts', 'Contracts', 'demo_contracts'),
    ('inventory', 'Inventory', 'demo_inventory'),
    ('profile', 'Profile', 'demo_profile'),
    ('favorites', 'Favorites', 'demo_favorites'),
    ('history', 'History', 'demo_history'),
    ('daily-rewards', 'Daily rewards', 'demo_daily_rewards'),
    ('missions', 'Missions', 'demo_missions'),
    ('leaderboard', 'Leaderboard', 'demo_leaderboard'),
    ('collections', 'Collections', 'demo_collections'),
    ('settings', 'Settings', 'demo_settings'),
    ('notifications', 'Notifications', 'demo_notifications'),
    ('items', 'Items', 'demo_items'),
]

SECTION_URLS = {
    'battles': 'demo_battles',
    'upgrade': 'demo_upgrade',
    'contracts': 'demo_contracts',
    'inventory': 'demo_inventory',
    'profile': 'demo_profile',
    'favorites': 'demo_favorites',
    'history': 'demo_history',
    'daily-rewards': 'demo_daily_rewards',
    'missions': 'demo_missions',
    'leaderboard': 'demo_leaderboard',
    'collections': 'demo_collections',
    'settings': 'demo_settings',
    'notifications': 'demo_notifications',
    'items': 'demo_items',
}


def _base_context(active, user):
    context = {'navigation': NAVIGATION, 'active_section': active}
    if user.is_authenticated:
        context['settings_obj'] = _get_settings(user)
        context['demo_wallet'] = _get_wallet(user)
    return context


def _get_wallet(user):
    wallet, _ = DemoWallet.objects.get_or_create(user=user)
    return wallet


def _parse_demo_value_range(minimum, maximum):
    try:
        minimum_value = Decimal(minimum) if minimum else None
        maximum_value = Decimal(maximum) if maximum else None
        if (
            (minimum_value is not None and (not minimum_value.is_finite() or minimum_value < 0))
            or (maximum_value is not None and (not maximum_value.is_finite() or maximum_value < 0))
            or (
                minimum_value is not None
                and maximum_value is not None
                and minimum_value > maximum_value
            )
        ):
            raise InvalidOperation
    except InvalidOperation:
        return None, None, 'Enter a valid non-negative demo value range.'
    return minimum_value, maximum_value, ''


def home(request):
    context = _base_context('home', request.user)
    context.update({
        'featured_cases': DemoCase.objects.filter(is_featured=True)[:6],
        'new_cases': DemoCase.objects.order_by('-created_at')[:6],
        'popular_items': DemoItem.objects.order_by('-demo_value')[:8],
        'case_count': DemoCase.objects.count(),
        'item_count': DemoItem.objects.count(),
    })
    return render(request, 'demo/home.html', context)


def cases(request):
    queryset = DemoCase.objects.prefetch_related('drops__item').all()
    query = request.GET.get('q', '').strip()[:100]
    category = request.GET.get('category', '').strip()[:40]
    theme = request.GET.get('theme', '').strip()[:40]
    rarity = request.GET.get('rarity', '').strip()[:20]
    minimum = request.GET.get('min_price', '').strip()[:24]
    maximum = request.GET.get('max_price', '').strip()[:24]
    ordering = request.GET.get('sort', 'featured')
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(theme__icontains=query)
            | Q(category__icontains=query)
        )
    if theme:
        queryset = queryset.filter(theme__iexact=theme)
    elif category:
        queryset = queryset.filter(category__iexact=category)
    if rarity in dict(DemoItem.RARITY_CHOICES):
        queryset = queryset.filter(drops__item__rarity=rarity).distinct()
    minimum_value, maximum_value, filter_error = _parse_demo_value_range(
        minimum, maximum,
    )
    if minimum_value is not None:
        queryset = queryset.filter(demo_price__gte=minimum_value)
    if maximum_value is not None:
        queryset = queryset.filter(demo_price__lte=maximum_value)
    sort_options = {
        'featured': ('-is_featured', 'demo_price', 'name'),
        'price_low': ('demo_price', 'name'),
        'price_high': ('-demo_price', 'name'),
        'newest': ('-created_at', 'name'),
        'name': ('name',),
    }
    queryset = queryset.order_by(*sort_options.get(ordering, sort_options['featured']))
    page_obj = Paginator(queryset, 12).get_page(request.GET.get('page'))
    favorite_case_ids = set()
    if request.user.is_authenticated:
        favorite_case_ids = set(
            DemoFavorite.objects.filter(
                user=request.user,
                case__in=page_obj.object_list,
            ).values_list('case_id', flat=True),
        )
    for case in page_obj.object_list:
        case.is_favorite = case.pk in favorite_case_ids
    context = _base_context('cases', request.user)
    context.update({
        'cases': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'selected_category': category,
        'selected_theme': theme,
        'selected_rarity': rarity,
        'selected_sort': ordering if ordering in sort_options else 'featured',
        'min_price': minimum if not filter_error else '',
        'max_price': maximum if not filter_error else '',
        'filter_error': filter_error,
        'themes': DemoCase.objects.order_by().values_list('theme', flat=True).distinct(),
        'favorite_case_ids': favorite_case_ids,
    })
    return render(request, 'demo/cases.html', context)


def case_detail(request, slug):
    case = get_object_or_404(
        DemoCase.objects.prefetch_related('drops__item'), slug=slug,
    )
    result = case.drops.filter(is_demo_result=True).select_related('item').first()
    context = _base_context('cases', request.user)
    context.update({
        'case': case,
        'is_favorite': (
            request.user.is_authenticated
            and DemoFavorite.objects.filter(user=request.user, case=case).exists()
        ),
        'items': [drop.item for drop in case.drops.all()],
        'drops': list(case.drops.all()),
        'demo_result': result.item if result else None,
        'request_id': uuid.uuid4(),
    })
    total_weight = sum(drop.drop_weight for drop in context['drops'])
    for drop in context['drops']:
        drop.demo_chance = (
            Decimal(drop.drop_weight * 100) / Decimal(total_weight)
            if total_weight else Decimal('0')
        ).quantize(Decimal('0.01'))
    return render(request, 'demo/case_detail.html', context)


def _get_settings(user):
    settings_obj, _ = DemoUserSettings.objects.get_or_create(user=user)
    return settings_obj


def _section_data(request, slug):
    context = {}
    user = request.user
    if slug == 'inventory':
        inventory_sort = request.GET.get('sort', 'newest')
        inventory_query = request.GET.get('q', '').strip()[:100]
        inventory_rarity = request.GET.get('rarity', '').strip()[:20]
        inventory_orders = {
            'newest': ('-created_at',),
            'name': ('item__name',),
            'rarity': ('item__rarity', 'item__name'),
            'value': ('-item__demo_value',),
        }
        if inventory_sort not in inventory_orders:
            inventory_sort = 'newest'
        inv_qs = DemoInventory.objects.filter(user=user).select_related('item')
        if inventory_query:
            inv_qs = inv_qs.filter(Q(item__name__icontains=inventory_query) | Q(item__theme__icontains=inventory_query))
        if inventory_rarity in dict(DemoItem.RARITY_CHOICES):
            inv_qs = inv_qs.filter(item__rarity=inventory_rarity)
        context['inventory'] = inv_qs.order_by(*inventory_orders[inventory_sort])
        favorite_item_ids = set(
            DemoFavorite.objects.filter(
                user=user,
                item__in=context['inventory'].values('item_id'),
            ).values_list('item_id', flat=True),
        )
        for entry in context['inventory']:
            entry.sell_request_id = uuid.uuid4()
            entry.item.is_favorite = entry.item_id in favorite_item_ids
        context['inventory_sort'] = inventory_sort
        context['inventory_query'] = inventory_query
        context['inventory_rarity'] = inventory_rarity
    elif slug == 'favorites':
        favorites = DemoFavorite.objects.filter(user=user).select_related('case', 'item')
        context['favorites'] = favorites
        context['case_favorites'] = favorites.filter(case__isnull=False)
        context['item_favorites'] = favorites.filter(item__isnull=False)
    elif slug == 'history':
        context['activities'] = DemoActivity.objects.filter(user=user)[:50]
        context['wallet_transactions'] = DemoWalletTransaction.objects.filter(
            wallet__user=user,
        )[:50]
    elif slug == 'profile':
        context.update({
            'profile': UserProfile.objects.get_or_create(user=user)[0],
            'settings_obj': _get_settings(user),
            'activities': DemoActivity.objects.filter(user=user)[:10],
            'inventory_count': DemoInventory.objects.filter(user=user).count(),
            'favorite_count': DemoFavorite.objects.filter(user=user).count(),
            'cases_opened_count': DemoActivity.objects.filter(
                user=user,
                activity_type='case_open',
            ).count(),
        })
    elif slug == 'upgrade':
        context['inventory'] = DemoInventory.objects.filter(user=user).select_related(
            'item',
        ).order_by('-created_at') if user.is_authenticated else DemoInventory.objects.none()
        context['items'] = DemoItem.objects.all()
        context['request_id'] = uuid.uuid4()
    elif slug == 'contracts':
        context['items'] = DemoItem.objects.all()
        context['inventory'] = DemoInventory.objects.filter(user=user).select_related(
            'item',
        ).order_by('-created_at') if user.is_authenticated else DemoInventory.objects.none()
        context['request_id'] = uuid.uuid4()
    elif slug == 'battles':
        all_items = list(DemoItem.objects.all())
        context['items'] = DemoItem.objects.order_by('-demo_value')[:8]
        context['featured_cases'] = DemoCase.objects.all()[:6]
        context['request_id'] = uuid.uuid4()
        context['all_items_json'] = json.dumps([_item_json(i) for i in all_items[:30]])
        context['cases_json'] = json.dumps([
            {'name': c.name, 'image': _asset_url(c.cover_image)}
            for c in DemoCase.objects.all()[:8]
        ])
    elif slug == 'items':
        search = request.GET.get('q', '').strip()[:100]
        rarity = request.GET.get('rarity', '').strip()[:20]
        theme = request.GET.get('theme', '').strip()[:40]
        ordering = request.GET.get('sort', 'featured')
        minimum = request.GET.get('min_price', '').strip()[:24]
        maximum = request.GET.get('max_price', '').strip()[:24]
        queryset = DemoItem.objects.all()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(theme__icontains=search))
        if rarity in dict(DemoItem.RARITY_CHOICES):
            queryset = queryset.filter(rarity=rarity)
        if theme:
            queryset = queryset.filter(theme__iexact=theme)
        minimum_value, maximum_value, filter_error = _parse_demo_value_range(
            minimum, maximum,
        )
        if minimum_value is not None:
            queryset = queryset.filter(demo_value__gte=minimum_value)
        if maximum_value is not None:
            queryset = queryset.filter(demo_value__lte=maximum_value)
        item_orderings = {
            'featured': ('-demo_value', 'name'),
            'name': ('name',),
            'value_low': ('demo_value', 'name'),
            'value_high': ('-demo_value', 'name'),
        }
        if ordering not in item_orderings:
            ordering = 'featured'
        queryset = queryset.order_by(*item_orderings[ordering])
        favorite_item_ids = set()
        if user.is_authenticated:
            favorite_item_ids = set(
                DemoFavorite.objects.filter(
                    user=user,
                    item__in=queryset.values('pk'),
                ).values_list('item_id', flat=True),
            )
        items = list(queryset)
        for item in items:
            item.is_favorite = item.pk in favorite_item_ids
        context.update({
            'items': items,
            'item_query': search,
            'selected_rarity': rarity,
            'selected_theme': theme,
            'selected_sort': ordering,
            'min_price': minimum if not filter_error else '',
            'max_price': maximum if not filter_error else '',
            'filter_error': filter_error,
            'themes': DemoItem.objects.order_by().values_list('theme', flat=True).distinct(),
            'favorite_item_ids': favorite_item_ids,
        })
    elif slug == 'daily-rewards':
        today = timezone.localdate()
        context['claimed_today'] = DemoDailyClaim.objects.filter(user=user, claimed_on=today).exists()
        context['recent_claims'] = DemoDailyClaim.objects.filter(user=user)[:7]
    elif slug == 'missions':
        activities = DemoActivity.objects.filter(user=user)
        context['missions'] = [
            {'title': 'Preview 3 cases', 'progress': min(activities.filter(activity_type='case_open').count(), 3), 'target': 3, 'xp': 25},
            {'title': 'Try 2 simulations', 'progress': min(activities.filter(activity_type__in=['upgrade', 'battle', 'contract']).count(), 2), 'target': 2, 'xp': 20},
            {'title': 'Explore 5 unique cases', 'progress': min(activities.filter(activity_type='case_open').values('details__case_id').distinct().count(), 5), 'target': 5, 'xp': 35},
        ]
    elif slug == 'leaderboard':
        context['leaders'] = User.objects.filter(
            demo_activities__isnull=False,
        ).annotate(
            demo_score=Count('demo_activities'),
            xp=Max('profile__experience_points'),
        ).order_by('-xp', '-demo_score', 'username').distinct()[:20]
    elif slug == 'collections':
        context['collections'] = DemoCollection.objects.prefetch_related('items').annotate(
            item_count=Count('items'),
        )
    elif slug == 'notifications':
        from .models import Notification
        context['notifications'] = Notification.objects.filter(user=user)[:40]
    elif slug == 'settings':
        context['settings_obj'] = _get_settings(user)
        context['profile'] = UserProfile.objects.get_or_create(user=user)[0]
    return context


def section(request, slug):
    if slug in {
        'contracts', 'upgrade', 'inventory', 'profile', 'favorites', 'history', 'daily-rewards',
        'missions', 'settings', 'notifications',
    } and not request.user.is_authenticated:
        return redirect(f"{reverse('store:login')}?{urlencode({'next': request.get_full_path()})}")
    title, description = SECTIONS[slug]
    context = _base_context(slug, request.user)
    context.update({
        'section_title': title,
        'section_description': description,
        **_section_data(request, slug),
    })
    if slug == 'history':
        context['activities'] = context['activities'][:50]
    return render(request, 'demo/section.html', context)


def action(request):
    if request.method != 'POST':
        return redirect('store:demo_cases')
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Sign in to save your private demo progress.'}, status=401)
    action_name = request.POST.get('action', '')
    user = request.user
    _get_wallet(user)
    if action_name in ('favorite_case', 'favorite_item'):
        try:
            target_id = int(request.POST.get('target_id', ''))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Tanlangan yozuv noto‘g‘ri.'}, status=400)
        target_field = 'case' if action_name == 'favorite_case' else 'item'
        target_model = DemoCase if target_field == 'case' else DemoItem
        target = target_model.objects.filter(pk=target_id).first()
        if target is None:
            return JsonResponse({'error': 'Demo favorite target was not found.'}, status=404)
        favorite, created = DemoFavorite.objects.get_or_create(
            user=user, **{target_field: target},
        )
        if not created:
            favorite.delete()
        return JsonResponse({'ok': True, 'saved': created})

    if action_name == 'save_settings':
        settings_obj = _get_settings(user)
        for field in (
            'sound_enabled', 'animations_enabled', 'notifications_enabled',
            'dark_theme_enabled',
        ):
            value = request.POST.get(field)
            if value not in ('true', 'false'):
                return JsonResponse({'error': 'Sozlama qiymatlari noto‘g‘ri.'}, status=400)
            setattr(settings_obj, field, value == 'true')
        display_name = request.POST.get('display_name', '').strip()
        bio = request.POST.get('bio', '').strip()
        if len(display_name) > 30 or len(bio) > 500:
            return JsonResponse({'error': 'Ism yoki bio belgilangan uzunlikdan oshdi.'}, status=400)
        settings_obj.display_name = display_name
        settings_obj.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.bio = bio
        profile.save(update_fields=['bio'])
        return JsonResponse({'ok': True, 'message': 'Sozlamalar saqlandi.'})

    if action_name == 'save_theme':
        theme = request.POST.get('theme')
        if theme not in ('dark', 'light', 'cyber', 'crimson', 'gold'):
            return JsonResponse({'error': 'Ko‘rinish sozlamasi noto‘g‘ri.'}, status=400)
        settings_obj = _get_settings(user)
        settings_obj.dark_theme_enabled = theme != 'light'
        settings_obj.save(update_fields=['dark_theme_enabled', 'updated_at'])
        return JsonResponse({'ok': True, 'theme': theme})

    if action_name == 'case_open':
        try:
            case_id = int(request.POST.get('case_id', ''))
            request_id = uuid.UUID(request.POST.get('request_id', ''))
            quantity = int(request.POST.get('quantity', '1'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Case yoki so‘rov identifikatori noto‘g‘ri.'}, status=400)
        if quantity not in (1, 2, 3, 4, 5, 10):
            return JsonResponse({'error': 'Case opening quantity must be 1, 2, 3, 4, 5, or 10.'}, status=400)
        case = DemoCase.objects.filter(pk=case_id).first()
        if case is None:
            return JsonResponse({'error': 'Demo case was not found.'}, status=404)
        previous = DemoActivity.objects.filter(user=user, request_id=request_id).first()
        if previous:
            return _case_open_replay_response(previous, case.pk, quantity)
        try:
            with transaction.atomic():
                wallet = DemoWallet.objects.select_for_update().get(user=user)
                previous = DemoActivity.objects.filter(user=user, request_id=request_id).first()
                if previous:
                    return _case_open_replay_response(previous, case.pk, quantity)
                total_cost = case.demo_price * quantity
                if wallet.balance < total_cost:
                    return JsonResponse({
                        'error': 'Demo balans yetarli emas.',
                        'balance': str(wallet.balance),
                        'required': str(total_cost),
                    }, status=409)
                drops = list(
                    DemoCaseItem.objects.select_for_update().filter(case=case).select_related('item'),
                )
                total_weight = sum(drop.drop_weight for drop in drops)
                if not drops or total_weight <= 0:
                    return JsonResponse({'error': 'Bu case uchun item drop sozlanmagan.'}, status=409)
                results = []
                inventory_ids = []
                for _ in range(quantity):
                    ticket = secrets.randbelow(total_weight)
                    for chosen in drops:
                        if ticket < chosen.drop_weight:
                            break
                        ticket -= chosen.drop_weight
                    inventory_entry = DemoInventory.objects.create(
                        user=user, item=chosen.item, source='case',
                    )
                    results.append(_item_json(chosen.item))
                    inventory_ids.append(inventory_entry.pk)

                wallet.balance -= total_cost
                wallet.save(update_fields=['balance', 'updated_at'])
                total_value = sum(Decimal(r['demo_value']) for r in results)
                response_data = {
                    'ok': True,
                    'result': results[0],
                    'results': results,
                    'quantity': quantity,
                    'price_per_case': str(case.demo_price),
                    'total_cost': str(total_cost),
                    'total_value': str(total_value),
                    'balance': str(wallet.balance),
                    'inventory_ids': inventory_ids,
                    'inventory_id': inventory_ids[0],
                }
                DemoWalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='case_open',
                    amount=-total_cost,
                    balance_after=wallet.balance,
                    request_id=request_id,
                    details={
                        'case_id': case.pk,
                        'case_name': case.name,
                        'quantity': quantity,
                        'price_per_case': str(case.demo_price),
                    },
                )
                DemoActivity.objects.create(
                    user=user,
                    activity_type='case_open',
                    request_id=request_id,
                    details={
                        'case_id': case.pk,
                        'case_name': case.name,
                        'item_name': results[0]['name'],
                        'item_id': results[0]['id'],
                        'quantity': quantity,
                        'price': str(case.demo_price),
                        'total_cost': str(total_cost),
                        'response': response_data,
                    },
                )
            return JsonResponse(response_data)
        except IntegrityError:
            previous = DemoActivity.objects.filter(user=user, request_id=request_id).first()
            if previous:
                return _case_open_replay_response(previous, case.pk, quantity)
            raise

    if action_name == 'upgrade':
        try:
            inventory_id = int(request.POST.get('source_id', ''))
            target = DemoItem.objects.get(pk=int(request.POST.get('target_id', '')))
            request_id = uuid.UUID(request.POST.get('request_id', ''))
        except (DemoItem.DoesNotExist, TypeError, ValueError):
            return JsonResponse({'error': 'Inventardagi item, maqsad yoki so‘rov identifikatori noto‘g‘ri.'}, status=400)
        multiplier = request.POST.get('multiplier', '1.5')
        multiplier_tenths = {'1.5': 15, '2': 20, '5': 50, '10': 100}.get(multiplier)
        if multiplier_tenths is None:
            return JsonResponse({'error': 'Upgrade demo ko‘paytirgichi noto‘g‘ri.'}, status=400)
        replay = _upgrade_replay_response(
            user, request_id, inventory_id, target.pk, multiplier_tenths,
        )
        if replay:
            return replay
        try:
            with transaction.atomic():
                wallet = DemoWallet.objects.select_for_update().get(user=user)
                replay = _upgrade_replay_response(
                    user, request_id, inventory_id, target.pk, multiplier_tenths,
                )
                if replay:
                    return replay
                entry = DemoInventory.objects.select_for_update().filter(
                    pk=inventory_id, user=user,
                ).select_related('item').first()
                if entry is None:
                    return JsonResponse({'error': 'Bu item sizning demo inventaringizda topilmadi.'}, status=404)
                source = entry.item
                if target.demo_value <= 0:
                    return JsonResponse({'error': 'Maqsad itemning demo qiymati noto‘g‘ri.'}, status=400)
                source_cents = int(source.demo_value * 100)
                target_cents = int(target.demo_value * 100)
                chance_basis_points = max(
                    500,
                    min(9000, source_cents * 70000 // (target_cents * multiplier_tenths)),
                )
                chance = Decimal(chance_basis_points) / Decimal('100')
                succeeded = secrets.randbelow(10000) < chance_basis_points
                response_data = {
                    'ok': True,
                    'success': succeeded,
                    'chance': f'{chance:.2f}',
                    'chance_basis_points': chance_basis_points,
                    'multiplier': multiplier,
                    'multiplier_tenths': multiplier_tenths,
                    'source_inventory_id': inventory_id,
                    'source_item_id': source.pk,
                    'target_item_id': target.pk,
                    'source': _item_json(source),
                    'result': _item_json(target) if succeeded else None,
                    'message': (
                        'Upgrade muvaffaqiyatli yakunlandi.'
                        if succeeded else 'Upgrade amalga oshmadi — item inventaringizda qoldi.'
                    ),
                }
                if succeeded:
                    entry.delete()
                    DemoInventory.objects.create(user=user, item=target, source='upgrade')
                DemoActivity.objects.create(
                    user=user,
                    activity_type='upgrade',
                    request_id=request_id,
                    details={
                        'source_name': source.name,
                        'source_inventory_id': inventory_id,
                        'target_name': target.name,
                        'target_item_id': target.pk,
                        'chance': f'{chance:.2f}',
                        'multiplier': multiplier,
                        'multiplier_tenths': multiplier_tenths,
                        'success': succeeded,
                        'response': response_data,
                    },
                )
            return JsonResponse(response_data)
        except IntegrityError:
            replay = _upgrade_replay_response(
                user, request_id, inventory_id, target.pk, multiplier_tenths,
            )
            if replay:
                return replay
            raise

    if action_name == 'inventory_sell':
        try:
            inventory_id = int(request.POST.get('inventory_id', ''))
            request_id = uuid.UUID(request.POST.get('request_id', ''))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Inventar itemi yoki so‘rov identifikatori noto‘g‘ri.'}, status=400)
        previous = DemoActivity.objects.filter(user=user, request_id=request_id).first()
        if previous:
            return _inventory_sell_replay_response(previous, inventory_id)
        try:
            with transaction.atomic():
                wallet = DemoWallet.objects.select_for_update().get(user=user)
                previous = DemoActivity.objects.filter(user=user, request_id=request_id).first()
                if previous:
                    return _inventory_sell_replay_response(previous, inventory_id)
                entry = DemoInventory.objects.select_for_update().filter(
                    pk=inventory_id, user=user,
                ).select_related('item').first()
                if entry is None:
                    return JsonResponse({'error': 'Ushbu item sizning demo inventaringizda topilmadi.'}, status=404)
                item = entry.item
                wallet.balance += item.demo_value
                wallet.save(update_fields=['balance', 'updated_at'])
                response_data = {
                    'ok': True,
                    'message': f'{item.name} demo balansga sotildi.',
                    'balance': str(wallet.balance),
                    'sold_value': str(item.demo_value),
                }
                DemoWalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='inventory_sale',
                    amount=item.demo_value,
                    balance_after=wallet.balance,
                    request_id=request_id,
                    details={'item_id': item.pk, 'item_name': item.name},
                )
                entry.delete()
                DemoActivity.objects.create(
                    user=user,
                    activity_type='inventory_sale',
                    request_id=request_id,
                    details={
                        'inventory_id': inventory_id,
                        'item_id': item.pk,
                        'item_name': item.name,
                        'sold_value': str(item.demo_value),
                        'response': response_data,
                    },
                )
            return JsonResponse(response_data)
        except IntegrityError:
            previous = DemoActivity.objects.filter(user=user, request_id=request_id).first()
            if previous:
                return _inventory_sell_replay_response(previous, inventory_id)
            raise

    if action_name == 'battle':
        raw_request_id = request.POST.get('request_id', '')
        request_id = None
        if raw_request_id:
            try:
                request_id = uuid.UUID(raw_request_id)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Noto‘g‘ri so‘rov identifikatori.'}, status=400)
            previous = DemoActivity.objects.filter(user=user, request_id=request_id).first()
            if previous:
                if previous.activity_type == 'battle' and 'response' in previous.details:
                    return JsonResponse(previous.details['response'])
                return JsonResponse({'error': 'This request ID was already used for a different demo action.'}, status=409)

        all_items = list(DemoItem.objects.all())
        if not all_items:
            return JsonResponse({'error': 'Battle uchun kamida 1 demo item kerak.'}, status=409)
        import random
        pool = all_items if len(all_items) >= 8 else (all_items * 4)
        player_picks = [random.choice(pool) for _ in range(4)]
        bot_picks = [random.choice(pool) for _ in range(4)]
        player_total = sum(i.demo_value for i in player_picks)
        bot_total = sum(i.demo_value for i in bot_picks)
        is_draw = (player_total == bot_total)
        player_won = player_total > bot_total
        bot_name = random.choice(['Nova', 'Cipher', 'Spectre', 'Vex'])
        winner = 'Draw' if is_draw else (user.username if player_won else bot_name)
        cases = list(DemoCase.objects.all())
        rounds = []
        for index in range(4):
            p_item = player_picks[index]
            b_item = bot_picks[index]
            round_case = cases[index % len(cases)] if cases else None
            case_name = round_case.name if round_case else 'CS2 Weapon Cache'
            case_image = _asset_url(round_case.cover_image) if (round_case and round_case.cover_image) else '/static/demo/cases/arcane-cyber-cache.svg'
            rounds.append({
                'round': index + 1,
                'item': p_item.name,
                'player_item': _item_json(p_item),
                'bot_item': _item_json(b_item),
                'opponent': bot_name,
                'case': {
                    'name': case_name,
                    'image': case_image,
                },
            })
        trophy = None
        if player_won:
            trophy = max(player_picks, key=lambda it: it.demo_value)
            DemoInventory.objects.create(user=user, item=trophy, source='battle')
        resp_data = {
            'ok': True,
            'rounds': rounds,
            'winner': winner,
            'player_won': player_won,
            'is_draw': is_draw,
            'player_total': str(player_total),
            'bot_total': str(bot_total),
            'bot_name': bot_name,
            'trophy': _item_json(trophy) if trophy else None,
            'item_pool': [_item_json(i) for i in pool[:24]],
        }
        DemoActivity.objects.create(
            user=user,
            activity_type='battle',
            request_id=request_id,
            details={
                'rounds': rounds,
                'winner': winner,
                'player_won': player_won,
                'is_draw': is_draw,
                'player_total': str(player_total),
                'bot_total': str(bot_total),
                'mode': 'simulated-battle',
                'response': resp_data,
            },
        )
        return JsonResponse(resp_data)

    if action_name == 'contract':
        raw_ids = request.POST.getlist('inventory_ids') or request.POST.getlist('item_ids')
        if not 3 <= len(raw_ids) <= 10 or len(set(raw_ids)) != len(raw_ids):
            return JsonResponse({'error': '3–10 ta takrorlanmagan demo item tanlang.'}, status=400)
        try:
            int_ids = [int(value) for value in raw_ids]
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Item tanlovi noto‘g‘ri.'}, status=400)

        with transaction.atomic():
            user_entries = list(
                DemoInventory.objects.select_for_update()
                .filter(user=user, pk__in=int_ids)
                .select_related('item')
            )
            if len(user_entries) == len(int_ids):
                # Contract from user inventory
                input_items = [e.item for e in user_entries]
                avg_val = sum(it.demo_value for it in input_items) / len(input_items)
                target_val = avg_val * Decimal('1.25')
                candidates = DemoItem.objects.filter(demo_value__gte=target_val).order_by('demo_value')
                result = candidates.first()
                if not result:
                    result = DemoItem.objects.filter(demo_value__gte=avg_val).order_by('demo_value').first()
                if not result:
                    result = DemoItem.objects.order_by('-demo_value').first()
                DemoInventory.objects.filter(user=user, pk__in=int_ids).delete()
                DemoInventory.objects.create(user=user, item=result, source='contract')
                DemoActivity.objects.create(
                    user=user,
                    activity_type='contract',
                    details={'input_count': len(user_entries), 'result_name': result.name, 'mode': 'tradeup-contract'},
                )
                return JsonResponse({'ok': True, 'result': _item_json(result), 'message': f'Trade-Up muvaffaqiyatli! {result.name} qo‘lga kiritildi.'})
            else:
                # Direct DemoItem fallback
                selected = sorted(
                    DemoItem.objects.filter(pk__in=int_ids),
                    key=lambda item: item.pk,
                )
                if len(selected) != len(int_ids):
                    return JsonResponse({'error': 'Tanlangan demo item topilmadi.'}, status=400)
                result = selected[sum(item.pk for item in selected) % len(selected)]
                DemoInventory.objects.create(user=user, item=result, source='contract')
                DemoActivity.objects.create(
                    user=user,
                    activity_type='contract',
                    details={'input_count': len(selected), 'result_name': result.name, 'mode': 'preselected-demo'},
                )
                return JsonResponse({'ok': True, 'result': _item_json(result)})

    if action_name == 'topup_wallet':
        wallet = _get_wallet(user)
        topup_amount = Decimal('5000.00')
        wallet.balance += topup_amount
        wallet.save(update_fields=['balance', 'updated_at'])
        req_id = uuid.uuid4()
        DemoWalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='case_open',
            amount=topup_amount,
            balance_after=wallet.balance,
            request_id=req_id,
            details={'note': 'Demo balans to‘ldirildi (+5,000)'},
        )
        return JsonResponse({
            'ok': True,
            'message': 'Hisobingizga +5,000 demo credits muvaffaqiyatli qo‘shildi!',
            'balance': str(wallet.balance),
        })

    if action_name == 'get_starter_skin':
        starter_item = DemoItem.objects.filter(rarity='common').order_by('demo_value').first() or DemoItem.objects.first()
        if starter_item:
            entry = DemoInventory.objects.create(user=user, item=starter_item, source='starter')
            return JsonResponse({
                'ok': True,
                'message': f'{starter_item.name} demo inventaringizga qo‘shildi!',
                'inventory_id': entry.pk,
                'item': _item_json(starter_item),
            })
        return JsonResponse({'error': 'Starter item topilmadi.'}, status=404)

    if action_name == 'claim_daily':
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        prior_claim = DemoDailyClaim.objects.filter(user=user, claimed_on=yesterday).first()
        streak = min((prior_claim.streak + 1) if prior_claim else 1, 7)
        try:
            with transaction.atomic():
                DemoDailyClaim.objects.create(
                    user=user, claimed_on=today, streak=streak, xp_awarded=10,
                )
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.experience_points += 10
                profile.save(update_fields=['experience_points'])
                DemoActivity.objects.create(
                    user=user, activity_type='daily_reward',
                    details={'xp': 10, 'streak': streak},
                )
        except IntegrityError:
            return JsonResponse({'error': 'Bugungi demo mukofoti avval olingan.'}, status=409)
        return JsonResponse({'ok': True, 'xp': 10, 'streak': streak})

    if action_name == 'claim_mission':
        mission = request.POST.get('mission', '')
        specs = {
            'cases': ('case_open', 3, 25),
            'simulations': ('simulation', 2, 20),
            'explorer': ('case_open', 5, 35),
        }
        if mission not in specs:
            return JsonResponse({'error': 'Topshiriq topilmadi.'}, status=400)
        kind, target, xp = specs[mission]
        activities = DemoActivity.objects.filter(user=user)
        if mission == 'simulations':
            progress = activities.filter(activity_type__in=['upgrade', 'battle', 'contract']).count()
        elif mission == 'explorer':
            progress = activities.filter(activity_type='case_open').values(
                'details__case_id',
            ).distinct().count()
        else:
            progress = activities.filter(activity_type=kind).count()
        if progress < target:
            return JsonResponse({'error': 'Topshiriq hali bajarilmagan.'}, status=400)
        today = timezone.localdate()
        claimed_key = f'mission_{mission}_{today.isoformat()}'
        request_id = uuid.uuid5(
            uuid.NAMESPACE_URL,
            f'skinly-demo-mission:{user.pk}:{claimed_key}',
        )
        previous = DemoActivity.objects.filter(
            user=user,
            request_id=request_id,
        ).first()
        if previous:
            return JsonResponse(previous.details['response'])
        try:
            with transaction.atomic():
                profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)
                previous = DemoActivity.objects.filter(
                    user=user,
                    request_id=request_id,
                ).first()
                if previous:
                    return JsonResponse(previous.details['response'])
                response_data = {'ok': True, 'xp': xp}
                profile.experience_points += xp
                profile.save(update_fields=['experience_points'])
                DemoActivity.objects.create(
                    user=user,
                    activity_type='daily_reward',
                    request_id=request_id,
                    details={
                        'mission_key': claimed_key,
                        'xp': xp,
                        'response': response_data,
                    },
                )
            return JsonResponse(response_data)
        except IntegrityError:
            previous = DemoActivity.objects.filter(
                user=user,
                request_id=request_id,
            ).first()
            if previous:
                return JsonResponse(previous.details['response'])
            raise

    if action_name == 'read_notification':
        from .models import Notification
        try:
            notification_id = int(request.POST.get('notification_id', ''))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Notification ID is invalid.'}, status=400)
        notification = Notification.objects.filter(pk=notification_id, user=user).first()
        if notification is None:
            return JsonResponse({'error': 'Notification was not found.'}, status=404)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return JsonResponse({'ok': True})

    return JsonResponse({'error': 'Amal qo‘llab-quvvatlanmaydi.'}, status=400)


def _asset_url(path):
    if not path:
        return '/static/images/placeholder.svg'
    if path.startswith('http') or path.startswith('/static/'):
        return path
    clean = path.lstrip('/')
    return f'/static/{clean}'


def _item_json(item):
    return {
        'id': item.pk, 'name': item.name, 'image': _asset_url(item.image),
        'demo_value': str(item.demo_value), 'rarity': item.rarity,
        'rarity_label': item.get_rarity_display(),
        'theme': item.theme,
    }


def _case_open_replay_response(activity, case_id, quantity):
    if (
        activity.activity_type == 'case_open'
        and activity.details.get('case_id') == case_id
        and activity.details.get('quantity', 1) == quantity
    ):
        return JsonResponse(activity.details['response'])
    return JsonResponse(
        {'error': 'This request ID was already used for a different demo action.'},
        status=409,
    )


def _inventory_sell_replay_response(activity, inventory_id):
    if (
        activity.activity_type == 'inventory_sale'
        and activity.details.get('inventory_id') == inventory_id
    ):
        return JsonResponse(activity.details['response'])
    return JsonResponse(
        {'error': 'This request ID was already used for a different demo action.'},
        status=409,
    )


def _upgrade_replay_response(user, request_id, inventory_id, target_id, multiplier_tenths):
    previous = DemoActivity.objects.filter(user=user, request_id=request_id).first()
    if previous is None:
        return None
    details = previous.details
    if (
        previous.activity_type == 'upgrade'
        and details.get('source_inventory_id') == inventory_id
        and details.get('target_item_id') == target_id
        and details.get('multiplier_tenths') == multiplier_tenths
    ):
        return JsonResponse(details['response'])
    return JsonResponse(
        {'error': 'This request ID was already used for different upgrade choices. Please retry.'},
        status=409,
    )


def item_detail(request, slug):
    item = get_object_or_404(DemoItem, slug=slug)
    context = _base_context('items', request.user)
    context.update({
        'item': item,
        'is_favorite': (
            request.user.is_authenticated
            and DemoFavorite.objects.filter(user=request.user, item=item).exists()
        ),
    })
    return render(request, 'demo/item_detail.html', context)
