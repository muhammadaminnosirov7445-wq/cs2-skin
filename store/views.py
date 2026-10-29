import json
import random
import secrets
import urllib.parse
from datetime import timedelta
from decimal import Decimal, InvalidOperation, localcontext
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max, Count
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings
from django.urls import reverse
from .models import (
    Product, Category, Order, OrderItem, UserProfile, UserInventory,
    BalanceTransaction, SkinPriceHistory, SellerReview, SellerReport, Notification,
    ProductFavorite, ProductView, SkinBattle, SkinBattleVote, SkinCollection,
    CollectionItem, CollectionComment, CommunityReport, CommunityPoll, PollChoice,
    PollVote, PriceWatch, MissionActivity, MissionClaim, AchievementAward,
    EngagementMetric
)
from .bot import send_telegram_order_notification
from .utils.steam import validate_trade_url
from .engagement import (
    MISSIONS, award_achievement, claim_mission, mission_period,
    record_metric, record_mission_activity,
)


def index(request):
    """CS2 Skins Catalog view with rich filtering: wear, weapon, stattrak, rarity, price."""
    record_metric('home_visit')
    if request.session.get('skinly_seen_before'):
        if not request.session.get('skinly_returning_visit_counted'):
            record_metric('returning_visit')
            request.session['skinly_returning_visit_counted'] = True
    else:
        request.session['skinly_seen_before'] = True
        request.session['skinly_returning_visit_counted'] = False
    categories = Category.objects.annotate(product_count=Count('products')).order_by('name')
    selected_category = request.GET.get('category')
    selected_wear = request.GET.get('wear')
    selected_weapon = request.GET.get('weapon')
    stattrak_only = request.GET.get('stattrak')
    selected_rarity = request.GET.get('rarity')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', '-created_at')

    products = Product.objects.select_related('category', 'seller', 'seller__profile').all()

    if selected_category:
        products = products.filter(category__slug=selected_category)

    if selected_wear:
        products = products.filter(wear_condition=selected_wear)

    if selected_weapon:
        products = products.filter(weapon_type__iexact=selected_weapon)

    if stattrak_only == '1':
        products = products.filter(stattrak=True)

    if selected_rarity:
        products = products.filter(rarity=selected_rarity)

    if min_price:
        try:
            products = products.filter(retail_price__gte=Decimal(min_price))
        except (InvalidOperation, ValueError):
            pass

    if max_price:
        try:
            products = products.filter(retail_price__lte=Decimal(max_price))
        except Exception:
            pass

    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) |
            Q(weapon_type__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Sorting
    if sort_by in ['retail_price', '-retail_price', 'float_value', '-created_at', 'wholesale_price']:
        products = products.order_by(sort_by)

    # Distinct weapon types for filter pills/dropdown
    available_weapons = Product.objects.values_list('weapon_type', flat=True).distinct()

    # Premium Homepage Sections
    featured_skins = Product.objects.select_related('category', 'seller').filter(is_featured=True)[:4]
    activity_since = timezone.now() - timedelta(days=7)
    trending_skins = Product.objects.select_related('category', 'seller').annotate(
        recent_views=Count('user_views', filter=Q(user_views__viewed_at__gte=activity_since), distinct=True),
        recent_battles=Count(
            'battle_as_a__votes',
            filter=Q(battle_as_a__votes__created_at__gte=activity_since),
            distinct=True,
        ) + Count(
            'battle_as_b__votes',
            filter=Q(battle_as_b__votes__created_at__gte=activity_since),
            distinct=True,
        ),
    ).order_by('-recent_views', '-recent_battles', '-created_at')[:6]
    recently_listed = Product.objects.select_related('category', 'seller').order_by('-created_at')[:6]
    hot_deals = Product.objects.select_related('category', 'seller').filter(stock__gt=0).order_by('retail_price')[:6]
    popular_collections = SkinCollection.objects.filter(is_public=True).select_related('owner').annotate(
        item_count=Count('items', distinct=True),
        comment_count=Count('comments', filter=Q(comments__status='visible'), distinct=True),
    ).order_by('-comment_count', '-item_count', '-updated_at')[:3]
    recommendations = Product.objects.select_related('category').filter(stock__gt=0)
    home_profile = None
    home_missions = []
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        home_profile = profile
        for code, mission in MISSIONS.items():
            period = mission_period(mission['period'])
            progress = MissionActivity.objects.filter(
                user=request.user, mission_code=code, period_start=period
            ).count()
            claimed = MissionClaim.objects.filter(
                user=request.user, mission_code=code, period_start=period
            ).exists()
            home_missions.append({
                'code': code,
                **mission,
                'progress': min(progress, mission['target']),
                'claimed': claimed,
            })
        recent_weapons = list(
            ProductView.objects.filter(user=request.user)
            .order_by('-viewed_at').values_list('product__weapon_type', flat=True)[:5]
        )
        favorite_weapons = list(
            ProductFavorite.objects.filter(user=request.user)
            .order_by('-created_at').values_list('product__weapon_type', flat=True)[:5]
        )
        preferred_weapons = list(dict.fromkeys(profile.weapon_preferences + recent_weapons + favorite_weapons))
        if preferred_weapons:
            recommendations = recommendations.filter(weapon_type__in=preferred_weapons)
        if profile.preferred_min_price is not None:
            recommendations = recommendations.filter(retail_price__gte=profile.preferred_min_price)
        if profile.preferred_max_price is not None:
            recommendations = recommendations.filter(retail_price__lte=profile.preferred_max_price)
        seen_ids = ProductView.objects.filter(user=request.user).values_list('product_id', flat=True)
        recommendations = recommendations.exclude(Q(id__in=seen_ids) | Q(user_favorites__user=request.user))
    recommendations = recommendations.distinct().order_by('-is_featured', '-created_at')[:6]
    if not recommendations:
        recommendations = Product.objects.filter(stock__gt=0).order_by('-is_featured', '-created_at')[:6]
    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(ProductFavorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    recent_viewed = []
    if request.user.is_authenticated:
        recent_viewed = Product.objects.filter(
            user_views__user=request.user, stock__gt=0
        ).select_related('category').order_by('-user_views__viewed_at')[:6]

    # Popular weapon categories with skin counts and icon mapping
    popular_categories = [
        {'name': 'Pichoqlar (Knives)', 'slug': 'knives', 'weapon': 'Knife', 'icon': 'sword', 'count': Product.objects.filter(weapon_type__icontains='Knife').count()},
        {'name': 'Miltiqlar (Rifles)', 'slug': 'rifles', 'weapon': 'Rifle', 'icon': 'crosshair', 'count': Product.objects.filter(weapon_type__icontains='Rifle').count()},
        {'name': 'Snayperlar (Snipers)', 'slug': 'snipers', 'weapon': 'Sniper', 'icon': 'target', 'count': Product.objects.filter(weapon_type__icontains='Sniper').count()},
        {'name': 'To\'pponchalar (Pistols)', 'slug': 'pistols', 'weapon': 'Pistol', 'icon': 'zap', 'count': Product.objects.filter(weapon_type__icontains='Pistol').count()},
        {'name': 'Qo\'lqoplar (Gloves)', 'slug': 'gloves', 'weapon': 'Gloves', 'icon': 'shield', 'count': Product.objects.filter(weapon_type__icontains='Glove').count()},
    ]

    # Pagination: 12 skins per page
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'selected_category': selected_category,
        'selected_wear': selected_wear,
        'selected_weapon': selected_weapon,
        'stattrak_only': stattrak_only,
        'selected_rarity': selected_rarity,
        'min_price': min_price,
        'max_price': max_price,
        'search_query': search_query,
        'sort_by': sort_by,
        'available_weapons': available_weapons,
        'wear_choices': Product.WEAR_CHOICES,
        'rarity_choices': Product.RARITY_CHOICES,
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'featured_skins': featured_skins,
        'trending_skins': trending_skins,
        'recently_listed': recently_listed,
        'hot_deals': hot_deals,
        'popular_categories': popular_categories,
        'total_skins_count': products.count(),
        'recommendations': recommendations,
        'favorite_ids': favorite_ids,
        'recent_viewed': recent_viewed,
        'home_profile': home_profile,
        'home_missions': home_missions,
        'popular_collections': popular_collections,
    }
    return render(request, 'store/index.html', context)


def product_detail(request, slug):
    """CS2 Skin Detail view with 3D Preview, price history analytics, and seller reputation."""
    product = get_object_or_404(
        Product.objects.select_related('category', 'seller', 'seller__profile'),
        slug=slug
    )
    record_metric('product_view')
    if request.user.is_authenticated:
        ProductView.objects.update_or_create(
            user=request.user, product=product, defaults={}
        )
        record_mission_activity(request.user, 'view', product.pk)

    # Similar skins from same category
    related_skins = Product.objects.select_related('category', 'seller').filter(
        category=product.category
    ).exclude(id=product.id)[:6]

    # Alternative offers / listings of same weapon type
    alternative_offers = Product.objects.select_related('category', 'seller', 'seller__profile').filter(
        weapon_type__iexact=product.weapon_type
    ).exclude(id=product.id).order_by('retail_price')[:5]

    # Price Analytics Data
    price_history = product.price_history.order_by('recorded_at')
    lowest_price = price_history.aggregate(min_p=Min('price'))['min_p'] or product.retail_price
    highest_price = price_history.aggregate(max_p=Max('price'))['max_p'] or product.retail_price

    # Seller information & reviews
    seller = product.seller
    seller_profile = getattr(seller, 'profile', None) if seller else None
    seller_reviews = []
    seller_rating = 5.0
    seller_reviews_count = 0
    if seller:
        seller_reviews = seller.received_reviews.select_related('buyer').order_by('-created_at')[:5]
        seller_rating = seller_profile.rating_average if seller_profile else 5.0
        seller_reviews_count = seller_profile.reviews_count if seller_profile else 0

    # Pre-fill trade URL if user logged in
    user_trade_url = ""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        user_trade_url = request.user.profile.steam_trade_url or ""

    context = {
        'product': product,
        'related_skins': related_skins,
        'alternative_offers': alternative_offers,
        'lowest_price': lowest_price,
        'highest_price': highest_price,
        'seller': seller,
        'seller_profile': seller_profile,
        'seller_reviews': seller_reviews,
        'seller_rating': seller_rating,
        'seller_reviews_count': seller_reviews_count,
        'user_trade_url': user_trade_url,
    }
    return render(request, 'store/product_detail.html', context)


def community(request):
    """Skin Battle, missions, personalized preferences, watchlist, polls, and showcases."""
    record_metric('community_visit')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, 'Ushbu amal uchun avval tizimga kiring.')
            return redirect('store:login')

        action = request.POST.get('action', '')
        if action == 'vote_battle':
            battle = get_object_or_404(SkinBattle, pk=request.POST.get('battle_id'), battle_date=timezone.localdate())
            try:
                choice = Product.objects.get(pk=request.POST.get('choice'))
            except (Product.DoesNotExist, ValueError, TypeError):
                messages.error(request, 'Skin Battle tanlovi yaroqsiz.')
                return redirect('store:community')
            if choice.pk not in (battle.product_a_id, battle.product_b_id):
                return HttpResponseForbidden('Invalid battle choice')
            _, created = SkinBattleVote.objects.get_or_create(
                battle=battle, user=request.user, defaults={'choice': choice}
            )
            if not created:
                messages.info(request, 'Bugungi Skin Battle uchun ovozingiz allaqachon qayd etilgan.')
            else:
                record_metric('battle_vote')
                record_mission_activity(request.user, 'battle', battle.pk)
                if request.user.skin_battle_votes.count() >= 5:
                    award_achievement(request.user, 'battle_regular', 'Battle regular')
                messages.success(request, 'Ovozingiz qabul qilindi. Rahmat!')
            return redirect('store:community')

        if action == 'create_collection':
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            recent_creations = SkinCollection.objects.filter(
                owner=request.user, created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            if not title or len(title) > 100 or len(description) > 1000:
                messages.error(request, 'Sarlavha 1–100, tavsif esa 1000 belgigacha bo‘lishi kerak.')
            elif recent_creations >= 10:
                messages.error(request, 'Bir soatda 10 tadan ortiq to‘plam yaratib bo‘lmaydi.')
            else:
                collection = SkinCollection.objects.create(
                    owner=request.user,
                    title=title,
                    description=description,
                    is_public=request.POST.get('is_public') == 'on',
                )
                record_mission_activity(request.user, 'collection', collection.pk)
                record_metric('collection_create')
                award_achievement(request.user, 'first_collection', 'Collection creator')
                messages.success(request, 'To‘plam yaratildi.')
                return redirect('store:collection_detail', share_id=collection.share_id)
            return redirect('store:community')

        if action == 'collection_item':
            collection = get_object_or_404(SkinCollection, pk=request.POST.get('collection_id'), owner=request.user)
            product = get_object_or_404(Product, pk=request.POST.get('product_id'))
            if request.POST.get('operation') == 'remove':
                CollectionItem.objects.filter(collection=collection, product=product).delete()
                collection.save(update_fields=['updated_at'])
            elif collection.items.count() >= 100 and not collection.items.filter(product=product).exists():
                messages.error(request, 'Har bir to‘plamga ko‘pi bilan 100 ta skin qo‘shish mumkin.')
            else:
                CollectionItem.objects.get_or_create(collection=collection, product=product)
                collection.save(update_fields=['updated_at'])
            return redirect('store:collection_detail', share_id=collection.share_id)

        if action == 'collection_settings':
            collection = get_object_or_404(SkinCollection, pk=request.POST.get('collection_id'), owner=request.user)
            title = request.POST.get('title', collection.title).strip()
            description = request.POST.get('description', '').strip()
            if not title or len(title) > 100 or len(description) > 1000:
                messages.error(request, 'Sarlavha 1–100, tavsif esa 1000 belgigacha bo‘lishi kerak.')
                return redirect('store:collection_detail', share_id=collection.share_id)
            collection.title = title
            collection.description = description
            collection.is_public = request.POST.get('is_public') == 'on'
            collection.save(update_fields=['title', 'description', 'is_public', 'updated_at'])
            messages.success(request, 'To‘plam sozlamalari saqlandi.')
            return redirect('store:collection_detail', share_id=collection.share_id)

        if action == 'comment':
            collection = get_object_or_404(SkinCollection, pk=request.POST.get('collection_id'), is_public=True)
            recent_comments = CollectionComment.objects.filter(
                user=request.user, created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            content = request.POST.get('content', '').strip()
            if not content or len(content) > 500:
                messages.error(request, 'Izoh 1–500 belgidan iborat bo‘lishi kerak.')
            elif recent_comments >= 10:
                messages.error(request, 'Izohlar limiti tugadi. Keyinroq urinib ko‘ring.')
            else:
                CollectionComment.objects.create(collection=collection, user=request.user, content=content)
                record_metric('community_comment')
                messages.success(request, 'Izoh qo‘shildi.')
            return redirect('store:collection_detail', share_id=collection.share_id)

        if action == 'report':
            reason = request.POST.get('reason', '').strip()
            target_type = request.POST.get('target_type')
            recent_reports = CommunityReport.objects.filter(
                reporter=request.user, created_at__gte=timezone.now() - timedelta(days=1)
            ).count()
            if not reason or len(reason) > 300 or recent_reports >= 5:
                messages.error(request, 'Hisobot yaroqsiz yoki bugungi hisobotlar limitingiz tugadi.')
            elif target_type == 'collection':
                collection = get_object_or_404(SkinCollection, pk=request.POST.get('target_id'), is_public=True)
                if collection.owner_id == request.user.id:
                    messages.error(request, 'O‘z to‘plamingizni xabar qila olmaysiz.')
                else:
                    CommunityReport.objects.get_or_create(
                        reporter=request.user, collection=collection,
                        defaults={'reason': reason},
                    )
                    messages.success(request, 'Hisobotingiz moderatorlarga yuborildi.')
                return redirect('store:collection_detail', share_id=collection.share_id)
            elif target_type == 'comment':
                comment = get_object_or_404(CollectionComment, pk=request.POST.get('target_id'), status='visible')
                if comment.user_id == request.user.id:
                    messages.error(request, 'O‘z izohingizni xabar qila olmaysiz.')
                else:
                    CommunityReport.objects.get_or_create(
                        reporter=request.user, comment=comment,
                        defaults={'reason': reason},
                    )
                    messages.success(request, 'Hisobotingiz moderatorlarga yuborildi.')
                return redirect('store:collection_detail', share_id=comment.collection.share_id)
            return redirect('store:community')

        if action == 'poll_vote':
            poll = get_object_or_404(CommunityPoll, pk=request.POST.get('poll_id'))
            choice = get_object_or_404(PollChoice, pk=request.POST.get('choice_id'), poll=poll)
            if not poll.is_open:
                messages.error(request, 'Ushbu so‘rovnoma ovoz berish uchun yopilgan.')
            else:
                _, created = PollVote.objects.get_or_create(
                    user=request.user, poll=poll, defaults={'choice': choice}
                )
                if not created:
                    messages.info(request, 'Siz bu so‘rovnomada allaqachon ovoz bergansiz.')
                else:
                    record_metric('poll_vote')
                    messages.success(request, 'Ovozingiz qayd etildi.')
            return redirect('store:community')

        if action == 'save_preferences':
            available_weapons = set(Product.objects.values_list('weapon_type', flat=True).distinct())
            weapons = [weapon for weapon in request.POST.getlist('weapon_preferences') if weapon in available_weapons][:12]
            try:
                minimum = Decimal(request.POST.get('preferred_min_price') or '0')
                maximum_value = request.POST.get('preferred_max_price', '').strip()
                maximum = Decimal(maximum_value) if maximum_value else None
            except (InvalidOperation, ValueError):
                messages.error(request, 'Narx oralig‘ini to‘g‘ri kiriting.')
                return redirect('store:community')
            if (
                not minimum.is_finite()
                or (maximum is not None and not maximum.is_finite())
                or minimum < 0
                or minimum >= Decimal('100000000')
                or (maximum is not None and (
                    maximum < minimum or maximum < 0 or maximum >= Decimal('100000000')
                ))
            ):
                messages.error(request, 'Narx oralig‘i mantiqan to‘g‘ri bo‘lishi kerak.')
            else:
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.weapon_preferences = weapons
                profile.preferred_min_price = minimum or None
                profile.preferred_max_price = maximum
                profile.save(update_fields=['weapon_preferences', 'preferred_min_price', 'preferred_max_price'])
                messages.success(request, 'Tavsiyalar sozlamalari saqlandi.')
            return redirect('store:community')

        if action == 'clear_history':
            ProductView.objects.filter(user=request.user).delete()
            messages.success(request, 'Ko‘rish tarixingiz tozalandi.')
            return redirect('store:community')

        if action == 'add_watch':
            product = get_object_or_404(Product, pk=request.POST.get('product_id'))
            try:
                target_price = Decimal(request.POST.get('target_price', '0'))
            except (InvalidOperation, ValueError):
                target_price = Decimal('0')
            recent_watches = PriceWatch.objects.filter(
                user=request.user, created_at__gte=timezone.now() - timedelta(days=1)
            ).count()
            if not target_price.is_finite() or target_price <= 0 or target_price >= Decimal('100000000'):
                messages.error(request, 'Maqsad narxi noldan katta bo‘lishi kerak.')
            elif recent_watches >= 30 and not PriceWatch.objects.filter(user=request.user, product=product).exists():
                messages.error(request, 'Kunlik narx kuzatuvi limiti tugadi.')
            else:
                watch, _ = PriceWatch.objects.update_or_create(
                    user=request.user,
                    product=product,
                    defaults={'target_price': target_price, 'is_active': True, 'notified_at': None},
                )
                if product.stock > 0 and product.retail_price <= watch.target_price:
                    Notification.objects.create(
                        user=request.user,
                        notification_type='price_drop',
                        title='Maqsad narxiga yetdi',
                        message=f'{product.title} hozir ${product.retail_price:.2f} — belgilangan chegarangiz ${watch.target_price:.2f}.',
                        link_url=reverse('store:product_detail', kwargs={'slug': product.slug}),
                    )
                    watch.notified_at = timezone.now()
                    watch.save(update_fields=['notified_at'])
                messages.success(request, 'Narx kuzatuvi saqlandi.')
            return redirect('store:community')

        if action == 'remove_watch':
            PriceWatch.objects.filter(user=request.user, pk=request.POST.get('watch_id')).delete()
            return redirect('store:community')

        if action == 'claim_mission':
            if claim_mission(request.user, request.POST.get('mission_code', '')):
                record_metric('mission_claim')
                messages.success(request, 'XP qo‘shildi — vazifa mukofoti olindi!')
            else:
                messages.info(request, 'Vazifa hali bajarilmagan yoki mukofoti oldin olingan.')
            return redirect('store:community')

        if action == 'answer_quiz':
            quiz_products = list(Product.objects.filter(stock__gt=0).order_by('retail_price', 'id')[:2])
            if len(quiz_products) == 2 and str(quiz_products[0].pk) == request.POST.get('answer'):
                record_mission_activity(request.user, 'quiz', timezone.localdate().isoformat())
                record_metric('quiz_correct')
                messages.success(request, 'To‘g‘ri javob! Bugungi skin bilimlari vazifasi bajarildi.')
            else:
                messages.info(request, 'Javob noto‘g‘ri. Ertaga yangi quizni sinab ko‘ring.')
            return redirect('store:community')

        messages.error(request, 'Noma’lum amal.')
        return redirect('store:community')

    today = timezone.localdate()
    battle = SkinBattle.objects.filter(battle_date=today).select_related('product_a', 'product_b').first()
    if not battle:
        candidates = list(Product.objects.filter(stock__gt=0).order_by('-created_at')[:30])
        if len(candidates) >= 2:
            candidates = random.sample(candidates, 2)
            battle, _ = SkinBattle.objects.get_or_create(
                battle_date=today,
                defaults={'product_a': candidates[0], 'product_b': candidates[1]},
            )

    public_collections = SkinCollection.objects.filter(is_public=True).select_related('owner').annotate(
        item_count=Count('items', distinct=True),
        comment_count=Count('comments', filter=Q(comments__status='visible'), distinct=True),
    ).order_by('-comment_count', '-item_count', '-updated_at')[:6]
    polls = list(CommunityPoll.objects.filter(
        ends_at__gte=timezone.now() - timedelta(days=30)
    ).prefetch_related(
        'choices__product', 'choices__votes'
    )[:5])
    if request.user.is_authenticated:
        for poll in polls:
            poll.user_has_voted = PollVote.objects.filter(poll=poll, user=request.user).exists()
    weapon_types = list(Product.objects.values_list('weapon_type', flat=True).distinct().order_by('weapon_type'))
    context = {
        'battle': battle,
        'battle_vote': SkinBattleVote.objects.filter(battle=battle, user=request.user).first()
            if battle and request.user.is_authenticated else None,
        'battle_votes_a': battle.votes.filter(choice=battle.product_a).count() if battle else 0,
        'battle_votes_b': battle.votes.filter(choice=battle.product_b).count() if battle else 0,
        'weekly_winners': Product.objects.filter(
            Q(battle_votes__created_at__gte=timezone.now() - timedelta(days=7))
        ).annotate(vote_count=Count('battle_votes')).order_by('-vote_count')[:5],
        'popular_skins': Product.objects.annotate(favorite_count=Count('user_favorites')).order_by('-favorite_count', '-created_at')[:5],
        'public_collections': public_collections,
        'my_collections': SkinCollection.objects.filter(owner=request.user)[:10] if request.user.is_authenticated else [],
        'polls': polls,
        'weapon_types': weapon_types,
        'watches': PriceWatch.objects.filter(user=request.user).select_related('product')[:20] if request.user.is_authenticated else [],
        'profile': UserProfile.objects.get_or_create(user=request.user)[0] if request.user.is_authenticated else None,
        'quiz_products': list(Product.objects.filter(stock__gt=0).order_by('retail_price', 'id')[:2]),
        'product_options': Product.objects.filter(stock__gt=0).order_by('title')[:100],
        'achievements': AchievementAward.objects.filter(user=request.user) if request.user.is_authenticated else [],
        'now': timezone.now(),
    }
    if request.user.is_authenticated:
        context['missions'] = []
        for code, mission in MISSIONS.items():
            period = mission_period(mission['period'])
            progress = MissionActivity.objects.filter(
                user=request.user, mission_code=code, period_start=period
            ).count()
            claimed = MissionClaim.objects.filter(
                user=request.user, mission_code=code, period_start=period
            ).exists()
            context['missions'].append({
                'code': code,
                **mission,
                'progress': min(progress, mission['target']),
                'claimed': claimed,
            })
    return render(request, 'store/community.html', context)


def collection_detail(request, share_id):
    collection = get_object_or_404(
        SkinCollection.objects.select_related('owner').prefetch_related('items__product'),
        share_id=share_id,
    )
    if not collection.is_public and (not request.user.is_authenticated or collection.owner_id != request.user.id):
        return HttpResponseForbidden('This collection is private.')
    items = list(collection.items.select_related('product').order_by('-added_at'))
    total_value = None
    if items and all(item.product.stock > 0 for item in items):
        total_value = sum((item.product.retail_price for item in items), Decimal('0'))
    context = {
        'collection': collection,
        'items': items,
        'total_value': total_value,
        'comments': collection.comments.filter(status='visible').select_related('user')[:30],
        'products': Product.objects.filter(stock__gt=0).order_by('title')[:100] if request.user.is_authenticated and collection.owner_id == request.user.id else [],
    }
    return render(request, 'store/collection_detail.html', context)


@login_required
@require_POST
def api_favorite_toggle(request):
    if request.POST.get('operation') == 'sync':
        try:
            product_ids = list(dict.fromkeys(
                int(value) for value in request.POST.get('product_ids', '').split(',') if value
            ))[:100]
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Favorite list is invalid.'}, status=400)
        products = Product.objects.filter(pk__in=product_ids)
        ProductFavorite.objects.bulk_create(
            [ProductFavorite(user=request.user, product=product) for product in products],
            ignore_conflicts=True,
        )
        if product_ids:
            record_metric('favorite_sync')
        return JsonResponse({'success': True})
    try:
        product = Product.objects.get(pk=request.POST.get('product_id'))
    except (Product.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Skin topilmadi.'}, status=404)
    favorite, created = ProductFavorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        favorite.delete()
    if created:
        record_metric('favorite_add')
    return JsonResponse({'success': True, 'is_favorite': created})



def checkout(request, slug=None):
    """
    Checkout view: Handles CS2 trade offer submission.
    Validates Steam Trade URL, creates order with tracking code,
    notifies Telegram bot admin, and updates user profile.
    """
    product = None
    if slug:
        product = get_object_or_404(Product, slug=slug)

    if request.method != 'POST' and not product:
        messages.warning(request, "Iltimos, avval xarid qilish uchun skinni tanlang.")
        return redirect('store:index')

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        try:
            qty = max(1, int(request.POST.get('quantity', 1)))
        except (ValueError, TypeError):
            qty = 1

        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        steam_trade_url = request.POST.get('steam_trade_url', '').strip()

        if not product:
            try:
                product = get_object_or_404(Product, id=int(product_id))
            except (ValueError, TypeError):
                messages.error(request, "Tanlangan mahsulot topilmadi!")
                return redirect('store:index')

        # Validate Steam Trade URL
        if not steam_trade_url:
            messages.error(request, "Iltimos, Steam Trade URL havolangizni kiriting!")
            return redirect('store:checkout_product', slug=product.slug)

        if not validate_trade_url(steam_trade_url):
            # Friendly warning if regex format is slightly off, but still allow if it contains steamcommunity.com
            if 'steamcommunity.com' not in steam_trade_url:
                messages.error(
                    request,
                    "Noto'g'ri Steam Trade URL! Havola 'https://steamcommunity.com/tradeoffer/new/?partner=...' ko'rinishida bo'lishi kerak."
                )
                return redirect('store:checkout_product', slug=product.slug)

        if qty < 1:
            messages.error(request, "Miqdor kamida 1 ta bo'lishi kerak!")
            return redirect('store:checkout_product', slug=product.slug)

        if product.stock < qty:
            messages.error(request, f"Kechirasiz, inventarda faqat {product.stock} ta qoldi!")
            return redirect('store:checkout_product', slug=product.slug)

        total_price = product.retail_price * Decimal(qty)

        # Atomic transaction to lock skin stock
        with transaction.atomic():
            prod = Product.objects.select_for_update().get(id=product.id)
            if prod.stock < qty:
                messages.error(request, "Afsuski, ushbu skin hozirgina boshqa foydalanuvchi tomonidan xarid qilindi.")
                return redirect('store:checkout_product', slug=product.slug)

            prod.stock -= qty
            prod.save()

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name,
                phone=phone,
                steam_trade_url=steam_trade_url,
                total_price=total_price,
                status='Pending'
            )

            OrderItem.objects.create(
                order=order,
                product=prod,
                quantity=qty,
                price=prod.retail_price
            )

            # Save Trade URL to profile for future convenience
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                profile = request.user.profile
                if not profile.steam_trade_url or profile.steam_trade_url != steam_trade_url:
                    profile.steam_trade_url = steam_trade_url
                    profile.save()

        # Send Telegram Bot Notification with Trade URL
        try:
            send_telegram_order_notification(order)
        except Exception:
            pass

        messages.success(
            request,
            f"Buyurtmangiz muvaffaqiyatli qabul qilindi! Steam Bot 2-5 daqiqa ichida Trade Offer yuboradi. Trek-kod: {order.tracking_code}"
        )
        return redirect('store:order_success', tracking_code=order.tracking_code)

    user_trade_url = ""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        user_trade_url = request.user.profile.steam_trade_url or ""

    context = {
        'product': product,
        'user_trade_url': user_trade_url,
    }
    return render(request, 'store/checkout.html', context)


def order_success(request, tracking_code):
    """CS2 Order confirmation receipt page."""
    order = get_object_or_404(Order, tracking_code=tracking_code)
    return render(request, 'store/order_success.html', {'order': order})


def track_order(request):
    """Search and track CS2 Trade Offer state by tracking code."""
    query = request.GET.get('code', '').strip()
    order = None
    if query:
        order = Order.objects.filter(tracking_code__iexact=query).first()
        if not order:
            messages.warning(request, f"'{query}' trek-kodi bo'yicha buyurtma topilmadi!")

    return render(request, 'store/track.html', {'order': order, 'query': query})


@login_required
def dashboard(request):
    """User Dashboard: Steam Trade URL configuration, orders history, wallet balance."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST' and 'update_steam' in request.POST:
        trade_url = request.POST.get('steam_trade_url', '').strip()
        steam_id = request.POST.get('steam_id', '').strip()
        profile.steam_trade_url = trade_url
        profile.steam_id = steam_id
        profile.save()
        messages.success(request, "Steam sozlamalaringiz muvaffaqiyatli saqlandi!")
        return redirect('store:dashboard')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    total_spent = sum(o.total_price for o in orders)
    active_orders_count = orders.exclude(status__in=['Completed', 'Cancelled']).count()
    inventory = UserInventory.objects.filter(user=request.user).select_related('product').order_by('-created_at')
    transactions = BalanceTransaction.objects.filter(user=request.user).order_by('-created_at')[:20]

    context = {
        'profile': profile,
        'achievements': AchievementAward.objects.filter(user=request.user),
        'orders': orders,
        'inventory': inventory,
        'transactions': transactions,
        'total_spent': total_spent,
        'active_orders_count': active_orders_count,
        'total_orders_count': orders.count(),
    }
    return render(request, 'store/dashboard.html', context)


@login_required
def top_up_balance(request):
    """Mock wallet deposit for testing skin purchase and dropshipping features."""
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except Exception:
            amount = Decimal('0')

        if amount > 0:
            with transaction.atomic():
                profile, _ = UserProfile.objects.select_for_update().get_or_create(user=request.user)
                old_balance = profile.balance
                profile.balance += amount
                profile.save(update_fields=['balance'])
                
                BalanceTransaction.objects.create(
                    user=request.user,
                    skin_name="Balans to'ldirish (Deposit)",
                    price=amount,
                    quantity=1,
                    total=amount,
                    balance_before=old_balance,
                    balance_after=profile.balance,
                    status='Completed',
                    transaction_type='Deposit'
                )
            messages.success(request, f"Hamyoningizga muvaffaqiyatli +${amount:.2f} qo'shildi!")
        else:
            messages.error(request, "Noto'g'ri summa kiritildi. Summa 0 dan katta bo'lishi kerak.")
    return redirect('store:dashboard')


def api_get_balance(request):
    """Returns current actual balance for authenticated user, or 0.00 for guest."""
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        balance_cents = int(round(profile.balance * 100))
        return JsonResponse({
            'authenticated': True,
            'username': request.user.username,
            'balance': float(profile.balance),
            'balance_cents': balance_cents,
            'formatted': f"${profile.balance:,.2f}".replace(',', ' '),
        })
    return JsonResponse({
        'authenticated': False,
        'username': None,
        'balance': 0.0,
        'balance_cents': 0,
        'formatted': '$0.00',
    })


@require_POST
def api_purchase_skins(request):
    """
    Real atomic purchase transaction API for CS2 skins.
    Supports single product instant buy or multi-item cart checkout.
    Security: Always uses backend database Product.retail_price (never trusts frontend prices).
    Precision: Calculates in integer cents to completely eliminate floating-point errors.
    Atomicity: Uses transaction.atomic() with select_for_update to guarantee data integrity.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': "Xarid qilish uchun avval hisobingizga kiring!",
            'code': 'AUTH_REQUIRED'
        }, status=401)

    # Parse JSON or form data
    try:
        if request.content_type == 'application/json' or (request.body and request.body.strip().startswith(b'{')):
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Noto'g'ri so'rov formati: {str(e)}"}, status=400)

    # Collect items to purchase
    # Either 'product_id' (single skin) or 'items' ([{"id": 1, "qty": 1}, ...])
    items_to_process = []
    if 'product_id' in data:
        try:
            pid = int(data.get('product_id'))
            qty = max(1, int(data.get('quantity', 1)))
            items_to_process.append((pid, qty))
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': "Noto'g'ri mahsulot identifikatori!"}, status=400)
    elif 'items' in data:
        raw_items = data.get('items', [])
        for item in raw_items:
            try:
                pid = int(item.get('id'))
                qty = max(1, int(item.get('qty', 1)))
                items_to_process.append((pid, qty))
            except (ValueError, TypeError):
                continue
    else:
        return JsonResponse({'success': False, 'error': "Xarid qilish uchun mahsulot tanlanmagan!"}, status=400)

    if not items_to_process:
        return JsonResponse({'success': False, 'error': "Savatcha bo'sh!"}, status=400)

    full_name = (data.get('full_name') or '').strip() or request.user.get_full_name() or request.user.username
    phone = (data.get('phone') or '').strip()
    steam_trade_url = (data.get('steam_trade_url') or '').strip()

    try:
        with transaction.atomic():
            profile, _ = UserProfile.objects.select_for_update().get_or_create(user=request.user)
            current_balance = profile.balance
            balance_cents = int(round(current_balance * 100))

            # Fetch and validate all products inside the transaction lock
            product_records = []
            total_cents = 0

            for pid, qty in items_to_process:
                product = Product.objects.select_for_update().filter(id=pid).first()
                if not product:
                    return JsonResponse({
                        'success': False,
                        'error': f"Mahsulot (ID: {pid}) do'konda topilmadi!"
                    }, status=404)

                if product.stock < qty:
                    return JsonResponse({
                        'success': False,
                        'error': f"'{product.title}' mahsulotidan faqat {product.stock} dona qolgan!"
                    }, status=400)

                # Convert retail price to exact cents
                price_cents = int(round(product.retail_price * 100))
                line_total_cents = price_cents * qty
                total_cents += line_total_cents
                product_records.append((product, qty, price_cents, line_total_cents))

            total_decimal = Decimal(total_cents) / Decimal(100)

            # Check if user has sufficient balance
            if balance_cents < total_cents:
                needed = f"${total_decimal:,.2f}".replace(',', ' ')
                current = f"${current_balance:,.2f}".replace(',', ' ')
                return JsonResponse({
                    'success': False,
                    'error': f"Balans yetarli emas! Talab qilinadi: {needed}, Balansingiz: {current}",
                    'code': 'INSUFFICIENT_FUNDS',
                    'current_balance': float(current_balance),
                    'total_required': float(total_decimal),
                }, status=400)

            # 1. Deduct balance with exact integer cents precision
            new_balance_cents = balance_cents - total_cents
            new_balance = Decimal(new_balance_cents) / Decimal(100)
            profile.balance = new_balance
            if steam_trade_url:
                profile.steam_trade_url = steam_trade_url
            if phone and not profile.phone:
                profile.phone = phone
            profile.save()

            # 2. Deduct product stocks
            for product, qty, _, _ in product_records:
                product.stock = max(0, product.stock - qty)
                product.save(update_fields=['stock'])

            # 3. Create Order & OrderItems
            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone or profile.phone or "N/A",
                steam_trade_url=steam_trade_url or profile.steam_trade_url or "",
                total_price=total_decimal,
                status='Trade Sent' if (steam_trade_url or profile.steam_trade_url) else 'Pending'
            )

            for product, qty, price_cents, _ in product_records:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=Decimal(price_cents) / Decimal(100)
                )

                # 4. Add to UserInventory
                for _ in range(qty):
                    UserInventory.objects.create(
                        user=request.user,
                        product=product,
                        acquired_via='Purchased',
                        status='In Inventory'
                    )

            # 5. Record BalanceTransaction
            if len(product_records) == 1:
                single_prod, single_qty, _, _ = product_records[0]
                txn_name = single_prod.title
                txn_price = single_prod.retail_price
                txn_product = single_prod
            else:
                txn_name = f"Savatcha xaridi ({len(product_records)} xil skin)"
                txn_price = total_decimal
                txn_product = None

            txn = BalanceTransaction.objects.create(
                user=request.user,
                product=txn_product,
                skin_name=txn_name,
                price=txn_price,
                quantity=sum(q for _, q, _, _ in product_records),
                total=total_decimal,
                balance_before=current_balance,
                balance_after=new_balance,
                status='Purchased',
                transaction_type='Purchase'
            )

            # 6. Send Telegram bot notification in background/try-catch
            try:
                send_telegram_order_notification(order)
            except Exception:
                pass

            formatted_new_balance = f"${new_balance:,.2f}".replace(',', ' ')
            formatted_price = f"${total_decimal:,.2f}".replace(',', ' ')

            return JsonResponse({
                'success': True,
                'message': "Sotib olish muvaffaqiyatli!",
                'skin_title': txn_name,
                'price': float(total_decimal),
                'price_formatted': formatted_price,
                'old_balance': float(current_balance),
                'new_balance': float(new_balance),
                'new_balance_cents': new_balance_cents,
                'new_balance_formatted': formatted_new_balance,
                'tracking_code': order.tracking_code,
                'transaction_id': txn.transaction_id,
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"Tranzaksiya paytida xatolik yuz berdi: {str(e)}"
        }, status=500)


def api_product_price_history(request, slug):
    """
    Returns verified historical price analytics data for the skin.
    Supports time ranges: 24h, 7d, 30d, 1y.
    Never fabricates fake data; strictly uses real recorded price events.
    """
    product = get_object_or_404(Product, slug=slug)
    time_range = request.GET.get('range', '30d').lower()

    now = timezone.now()
    if time_range == '24h':
        start_date = now - timedelta(hours=24)
        date_format = '%H:%M'
    elif time_range == '7d':
        start_date = now - timedelta(days=7)
        date_format = '%d %b'
    elif time_range == '1y':
        start_date = now - timedelta(days=365)
        date_format = '%b %Y'
    else:  # '30d' default
        start_date = now - timedelta(days=30)
        date_format = '%d %b'

    history_qs = product.price_history.filter(recorded_at__gte=start_date).order_by('recorded_at')

    # If no records in range, fallback to real database points
    records = list(history_qs)
    if not records:
        records = list(product.price_history.order_by('-recorded_at')[:5])
        if not records:
            # Baseline point with current retail price
            records = [
                SkinPriceHistory(
                    product=product,
                    price=product.retail_price,
                    recorded_at=now,
                    source='Current Listing',
                    volume=1
                )
            ]

    labels = [r.recorded_at.strftime(date_format) for r in records]
    prices = [float(r.price) for r in records]

    current_price = float(product.retail_price)
    lowest_price = min(prices) if prices else current_price
    highest_price = max(prices) if prices else current_price
    initial_price = prices[0] if prices else current_price

    price_diff = round(current_price - initial_price, 2)
    diff_pct = round((price_diff / initial_price) * 100, 2) if initial_price > 0 else 0.0

    return JsonResponse({
        'success': True,
        'slug': product.slug,
        'title': product.title,
        'range': time_range,
        'labels': labels,
        'prices': prices,
        'lowest_price': lowest_price,
        'highest_price': highest_price,
        'current_price': current_price,
        'price_diff': price_diff,
        'price_diff_formatted': f"{'+' if price_diff > 0 else ''}${price_diff:.2f}",
        'diff_pct': diff_pct,
        'diff_pct_formatted': f"{'+' if diff_pct > 0 else ''}{diff_pct:.1f}%",
        'is_positive': price_diff >= 0,
        'points_count': len(prices)
    })


def seller_profile(request, username):
    """
    Public profile of a marketplace seller:
    - Avatar, bio, join date, verified seller badge
    - Active skin listings
    - Buyer reviews, ratings breakdown, completed sales count
    - Report seller form & review form with eligibility validation
    """
    seller_user = get_object_or_404(User.objects.select_related('profile'), username=username)
    profile, _ = UserProfile.objects.get_or_create(user=seller_user)

    active_listings = Product.objects.select_related('category').filter(
        seller=seller_user,
        stock__gt=0
    ).order_by('-created_at')

    reviews = seller_user.received_reviews.select_related('buyer', 'product').order_by('-created_at')
    
    # Calculate rating stats
    reviews_count = reviews.count()
    if reviews_count > 0:
        avg_rating = round(sum(r.rating for r in reviews) / reviews_count, 1)
        stars_breakdown = {i: reviews.filter(rating=i).count() for i in range(1, 6)}
    else:
        avg_rating = 5.0
        stars_breakdown = {i: 0 for i in range(1, 6)}

    # Check review eligibility for logged-in buyer
    can_review = False
    eligible_order = None
    if request.user.is_authenticated and request.user != seller_user:
        buyer_orders = Order.objects.filter(
            user=request.user
        ).prefetch_related('items__product')

        for ord in buyer_orders:
            seller_items = [it for it in ord.items.all() if it.product.seller == seller_user]
            if seller_items:
                if not SellerReview.objects.filter(buyer=request.user, order=ord).exists():
                    can_review = True
                    eligible_order = ord
                    break

    context = {
        'seller_user': seller_user,
        'seller_profile': profile,
        'active_listings': active_listings,
        'reviews': reviews,
        'reviews_count': reviews_count,
        'avg_rating': avg_rating,
        'stars_breakdown': stars_breakdown,
        'can_review': can_review,
        'eligible_order': eligible_order,
    }
    return render(request, 'store/seller_profile.html', context)


@login_required
@require_POST
def submit_seller_review(request, username):
    """
    Submit a verified review for a seller.
    Strictly validates that buyer is not seller, and buyer hasn't submitted a review for this transaction.
    """
    seller_user = get_object_or_404(User, username=username)
    if request.user == seller_user:
        return JsonResponse({'success': False, 'error': "O'z hisobingizga sharh qoldira olmaysiz!"}, status=400)

    try:
        rating = int(request.POST.get('rating', 5))
        if rating < 1 or rating > 5:
            rating = 5
    except (ValueError, TypeError):
        rating = 5

    comment = request.POST.get('comment', '').strip()
    if len(comment) < 5:
        return JsonResponse({'success': False, 'error': "Sharh matni kamida 5 ta belgidan iborat bo'lishi kerak!"}, status=400)

    order_id = request.POST.get('order_id')
    order = None
    if order_id:
        try:
            order = Order.objects.filter(id=int(order_id), user=request.user).first()
        except (ValueError, TypeError):
            order = None

    # Check duplicate review
    if order and SellerReview.objects.filter(buyer=request.user, order=order).exists():
        return JsonResponse({'success': False, 'error': "Siz ushbu tranzaksiya uchun allaqachon sharh qoldirgansiz!"}, status=400)

    product_id = request.POST.get('product_id')
    product = Product.objects.filter(id=product_id).first() if product_id else None

    review = SellerReview.objects.create(
        seller=seller_user,
        buyer=request.user,
        order=order,
        product=product,
        rating=rating,
        comment=comment,
        is_verified_purchase=bool(order)
    )

    # Notify seller about new review
    Notification.objects.create(
        user=seller_user,
        notification_type='account',
        title="Yangi xaridor sharhi!",
        message=f"{request.user.username} sizga {rating}★ baho qo'ydi: '{comment[:60]}...'",
        link_url=f"/seller/{seller_user.username}/"
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or (request.content_type and 'application/json' in request.content_type):
        return JsonResponse({
            'success': True,
            'message': "Sharhingiz muvaffaqiyatli saqlandi! Rahmat.",
            'rating': review.rating,
            'buyer': request.user.username
        })

    messages.success(request, "Sharhingiz muvaffaqiyatli qabul qilindi!")
    return redirect('store:seller_profile', username=seller_user.username)


@login_required
@require_POST
def submit_seller_report(request, username):
    """
    Submits a moderation report for a suspicious or fraudulent seller.
    """
    seller_user = get_object_or_404(User, username=username)
    if request.user == seller_user:
        return JsonResponse({'success': False, 'error': "O'z profilingiz ustidan shikoyat qila olmaysiz!"}, status=400)

    reason = request.POST.get('reason', 'other').strip()
    valid_reasons = dict(SellerReport.REASON_CHOICES).keys()
    if reason not in valid_reasons:
        reason = 'other'

    details = request.POST.get('details', '').strip()
    if len(details) < 10:
        return JsonResponse({'success': False, 'error': "Iltimos, sababni to'liqroq yozing (kamida 10 belgi)."}, status=400)

    SellerReport.objects.create(
        reporter=request.user,
        seller=seller_user,
        reason=reason,
        details=details,
        status='Pending'
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or (request.content_type and 'application/json' in request.content_type):
        return JsonResponse({
            'success': True,
            'message': "Shikoyatingiz qabul qilindi. Moderatsiya jamoamiz uni tez orada ko'rib chiqadi."
        })

    messages.success(request, "Shikoyatingiz qabul qilindi. Tez orada ko'rib chiqiladi.")
    return redirect('store:seller_profile', username=seller_user.username)


def api_notifications_list(request):
    """Returns unread count and latest 20 notifications for authenticated user."""
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False, 'unread_count': 0, 'notifications': []})

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    items = []
    for n in notifications:
        items.append({
            'id': n.id,
            'type': n.notification_type,
            'title': n.title,
            'message': n.message,
            'link_url': n.link_url or '#',
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%d.%m %H:%M')
        })

    return JsonResponse({
        'authenticated': True,
        'unread_count': unread_count,
        'notifications': items
    })


@login_required
@require_POST
def api_notification_mark_read(request, notification_id):
    """Marks a single notification as read."""
    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'success': True, 'unread_count': unread_count})


@login_required
@require_POST
def api_notifications_read_all(request):
    """Marks all user notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True, 'unread_count': 0})



# Authentication views
def user_register(request):
    """Foydalanuvchini ishonchli va to'liq ro'yxatdan o'tkazish."""
    if request.user.is_authenticated:
        return redirect('store:dashboard')

    if request.method == 'POST':
        action = request.POST.get('action', '')

        # 1-bosishda tezkor Demo ro'yxatdan o'tish
        if action == 'demo_register':
            demo_suffix = secrets.token_hex(3)
            demo_username = f"SkinlyPlayer_{demo_suffix}"
            demo_email = f"{demo_username.lower()}@skinly.uz"
            demo_user = User.objects.create_user(
                username=demo_username,
                email=demo_email,
                password=f"Demo{demo_suffix}!2026"
            )
            profile, _ = UserProfile.objects.get_or_create(user=demo_user)
            profile.balance = Decimal('150.00')
            profile.steam_trade_url = "https://steamcommunity.com/tradeoffer/new/?partner=109283746&token=DemoToken"
            profile.save()

            BalanceTransaction.objects.create(
                user=demo_user,
                skin_name="Xush kelibsiz bonusi (Welcome Bonus)",
                price=Decimal('150.00'),
                quantity=1,
                total=Decimal('150.00'),
                balance_before=Decimal('0.00'),
                balance_after=Decimal('150.00'),
                status='Completed',
                transaction_type='Deposit'
            )

            login(request, demo_user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Xush kelibsiz, {demo_user.username}! Sizga +$150.00 boshlang'ich sinov balansi taqdim etildi.")
            return redirect('store:dashboard')

        username_raw = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        steam_trade_url = request.POST.get('steam_trade_url', '').strip()
        password = (request.POST.get('password') or request.POST.get('password1') or '').strip()
        password_confirm = (request.POST.get('password_confirm') or request.POST.get('password2') or '').strip()

        # Sanitize username so apostrophes (O'tkir) or spaces don't break Django validation
        import re
        cleaned_username = re.sub(r"[^\w.@+-]", "", username_raw)
        if not cleaned_username:
            cleaned_username = f"Gamer_{secrets.token_hex(3)}"
        username = cleaned_username

        if not password:
            messages.error(request, "Iltimos, parolni kiriting.")
            return render(request, 'store/register.html', {'username': username_raw, 'email': email, 'phone': phone, 'steam_trade_url': steam_trade_url})

        # If confirm is provided and doesn't match
        if password_confirm and password != password_confirm:
            messages.error(request, "Kiritilgan parollar bir-biriga mos kelmadi. Iltimos, qayta tekshiring.")
            return render(request, 'store/register.html', {'username': username_raw, 'email': email, 'phone': phone, 'steam_trade_url': steam_trade_url})

        # If username already exists, make it unique or log in
        if User.objects.filter(username__iexact=username).exists():
            existing_user = User.objects.filter(username__iexact=username).first()
            if existing_user and existing_user.check_password(password):
                # Correct password for existing user -> log them in directly
                login(request, existing_user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f"Xush kelibsiz, {existing_user.username}!")
                return redirect('store:dashboard')
            else:
                # Suffix to make unique so registration succeeds without blocking
                base_name = username
                counter = 1
                while User.objects.filter(username__iexact=username).exists():
                    username = f"{base_name}_{counter}"
                    counter += 1

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email or '', password=password)
                profile, _ = UserProfile.objects.get_or_create(user=user)
                welcome_bonus = Decimal('100.00')
                profile.balance = welcome_bonus
                if phone:
                    profile.phone = phone
                if steam_trade_url:
                    profile.steam_trade_url = steam_trade_url
                profile.save()

                BalanceTransaction.objects.create(
                    user=user,
                    skin_name="Xush kelibsiz bonusi (Welcome Bonus)",
                    price=welcome_bonus,
                    quantity=1,
                    total=welcome_bonus,
                    balance_before=Decimal('0.00'),
                    balance_after=welcome_bonus,
                    status='Completed',
                    transaction_type='Deposit'
                )

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Xush kelibsiz, {user.username}! Ro'yxatdan muvaffaqiyatli o'tdingiz. +$100.00 xarid bonusi taqdim etildi!")
            return redirect('store:dashboard')
        except Exception as e:
            messages.error(request, f"Ro'yxatdan o'tishda xatolik: {str(e)}")
            return render(request, 'store/register.html', {'username': username_raw, 'email': email, 'phone': phone, 'steam_trade_url': steam_trade_url})

    return render(request, 'store/register.html', {})


def user_login(request):
    """Foydalanuvchi tizimga kirishi (Login yoki Email orqali)."""
    if request.user.is_authenticated:
        return redirect('store:dashboard')

    if request.method == 'POST':
        action = request.POST.get('action', '')

        # 1-bosishda tezkor Demo kirish
        if action == 'demo_login':
            demo_user = User.objects.filter(username__startswith='demo_').first()
            if not demo_user:
                demo_user = User.objects.create_user(
                    username='demo_trader',
                    email='demo@skinly.uz',
                    password='SkinlyPassword2026!'
                )
                profile, _ = UserProfile.objects.get_or_create(user=demo_user)
                profile.balance = Decimal('250.00')
                profile.save()
            else:
                profile, _ = UserProfile.objects.get_or_create(user=demo_user)
                if profile.balance < Decimal('50.00'):
                    profile.balance = Decimal('200.00')
                    profile.save()

            login(request, demo_user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Demo hisob bilan kirdingiz ({demo_user.username}). Balans: ${profile.balance}!")
            return redirect('store:dashboard')

        login_identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not login_identifier or not password:
            messages.error(request, "Iltimos, login va parolni kiriting.")
            return render(request, 'store/login.html', {'username': login_identifier})

        # Agar email kiritilgan bo'lsa, username ni aniqlash
        auth_username = login_identifier
        if '@' in login_identifier:
            matched_user = User.objects.filter(email__iexact=login_identifier).first()
            if matched_user:
                auth_username = matched_user.username

        user = authenticate(request, username=auth_username, password=password)
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Qaytganingiz bilan, {user.first_name or user.username}!")
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('store:dashboard')
        else:
            messages.error(request, "Login yoki parol noto'g'ri kiritildi!")
            return render(request, 'store/login.html', {
                'username': login_identifier,
                'next': request.GET.get('next', request.POST.get('next', '')),
            })

    next_url = request.GET.get('next', '')
    return render(request, 'store/login.html', {'next': next_url})


def user_logout(request):
    """User logout view."""
    logout(request)
    messages.info(request, "Siz tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect('store:index')


# OAuth 2.0 (Google & GitHub) Authentication Views
def oauth_google_login(request):
    """
    Google OAuth 2.0 autentifikatsiyasi.
    Agar GOOGLE_CLIENT_ID haqiqiy bo'lsa Google rasmiy sahifasiga yo'naltiradi.
    Lokal yoki demo rejimda esa 100% xatosiz demo autentifikatsiyani ta'minlaydi.
    """
    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '').strip()
    is_dummy = not client_id or client_id.startswith('1071663118385') or request.GET.get('demo') == '1'

    if is_dummy:
        demo_username = f"google_vip_{secrets.token_hex(2)}"
        user, created = User.objects.get_or_create(
            username=demo_username,
            defaults={'first_name': 'Google VIP', 'last_name': 'Gamer', 'email': f'{demo_username}@gmail.com'}
        )
        if created:
            user.set_unusable_password()
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.balance = Decimal('100.00')
            profile.save()
            messages.success(request, "Google orqali muvaffaqiyatli kirdingiz! +$100.00 bonus qo'shildi.")
        else:
            messages.success(request, f"Xush kelibsiz, {user.first_name}! Google orqali kirdingiz.")
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('store:dashboard')

    state = secrets.token_urlsafe(32)
    request.session['oauth_google_state'] = state
    redirect_uri = request.build_absolute_uri(reverse('store:oauth_google_callback'))
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'access_type': 'online',
        'prompt': 'select_account',
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


def oauth_google_callback(request):
    """
    Handles callback from Google OAuth 2.0.
    Exchanges code for tokens, retrieves profile, creates or finds user, and logs them in.
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    saved_state = request.session.pop('oauth_google_state', None)

    if not code or (saved_state and state != saved_state):
        messages.error(request, "Google orqali autentifikatsiya rad etildi yoki xatolik yuz berdi.")
        return redirect('store:login')

    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '').strip()
    client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '').strip()
    redirect_uri = request.build_absolute_uri(reverse('store:oauth_google_callback'))

    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }

    try:
        token_res = requests.post(token_url, data=token_data, timeout=10)
        if token_res.status_code != 200:
            messages.error(request, "Google token olishda xatolik yuz berdi.")
            return redirect('store:login')

        access_token = token_res.json().get('access_token')
        userinfo_res = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        if userinfo_res.status_code != 200:
            messages.error(request, "Google profil ma'lumotlarini olishda xatolik yuz berdi.")
            return redirect('store:login')

        userinfo = userinfo_res.json()
        email = userinfo.get('email')
        name = userinfo.get('name', '')
        first_name = userinfo.get('given_name', '')
        last_name = userinfo.get('family_name', '')
        sub = userinfo.get('sub', '')

        user = None
        if email:
            user = User.objects.filter(email=email).first()

        if not user:
            base_username = email.split('@')[0] if email else f"google_{sub[:8]}"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            user = User.objects.create(
                username=username,
                email=email or '',
                first_name=first_name or name,
                last_name=last_name
            )
            user.set_unusable_password()
            user.save()
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, f"Xush kelibsiz, {user.first_name or user.username}! Google orqali profilingiz yaratildi.")
        else:
            messages.success(request, f"Qaytganingiz bilan, {user.first_name or user.username}!")

        login(request, user)
        return redirect('store:dashboard')

    except Exception as e:
        messages.error(request, f"Google OAuth jarayonida xatolik: {str(e)}")
        return redirect('store:login')


def oauth_github_login(request):
    """
    Initiates GitHub OAuth flow.
    If GITHUB_CLIENT_ID is set in settings, redirects to GitHub authorize.
    If not configured (demo/local dev), performs a seamless test registration/login.
    """
    client_id = getattr(settings, 'GITHUB_CLIENT_ID', '').strip()
    if not client_id:
        demo_username = 'github_user'
        user, created = User.objects.get_or_create(
            username=demo_username,
            defaults={'first_name': 'GitHub', 'last_name': 'Developer', 'email': 'developer@github.com'}
        )
        if created:
            user.set_unusable_password()
            user.save()
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, "GitHub orqali muvaffaqiyatli ro'yxatdan o'tdingiz!")
        else:
            messages.success(request, f"Xush kelibsiz, {user.first_name or user.username}! GitHub orqali kirdingiz.")
        login(request, user)
        return redirect('store:dashboard')

    state = secrets.token_urlsafe(32)
    request.session['oauth_github_state'] = state
    redirect_uri = request.build_absolute_uri(reverse('store:oauth_github_callback'))
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'user:email',
        'state': state,
    }
    auth_url = f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


def oauth_github_callback(request):
    """
    Handles callback from GitHub OAuth.
    Exchanges code for access token, fetches profile & email, creates/logs in user.
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    saved_state = request.session.pop('oauth_github_state', None)

    if not code or (saved_state and state != saved_state):
        messages.error(request, "GitHub orqali autentifikatsiya bekor qilindi yoki xatolik yuz berdi.")
        return redirect('store:login')

    client_id = getattr(settings, 'GITHUB_CLIENT_ID', '').strip()
    client_secret = getattr(settings, 'GITHUB_CLIENT_SECRET', '').strip()
    redirect_uri = request.build_absolute_uri(reverse('store:oauth_github_callback'))

    token_url = "https://github.com/login/oauth/access_token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri,
    }

    try:
        headers = {'Accept': 'application/json'}
        token_res = requests.post(token_url, data=token_data, headers=headers, timeout=10)
        if token_res.status_code != 200:
            messages.error(request, "GitHub token olishda xatolik yuz berdi.")
            return redirect('store:login')

        token_json = token_res.json()
        access_token = token_json.get('access_token')
        if not access_token:
            messages.error(request, f"GitHub xatosi: {token_json.get('error_description', 'Token olinmadi')}")
            return redirect('store:login')

        gh_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Skinly-App'
        }
        gh_res = requests.get("https://api.github.com/user", headers=gh_headers, timeout=10)
        if gh_res.status_code != 200:
            messages.error(request, "GitHub profil ma'lumotlarini olishda xatolik.")
            return redirect('store:login')

        gh_data = gh_res.json()
        gh_login = gh_data.get('login')
        gh_id = str(gh_data.get('id', ''))
        gh_name = gh_data.get('name') or gh_login
        email = gh_data.get('email')

        if not email:
            try:
                emails_res = requests.get("https://api.github.com/user/emails", headers=gh_headers, timeout=5)
                if emails_res.status_code == 200:
                    for em in emails_res.json():
                        if em.get('primary') and em.get('verified'):
                            email = em.get('email')
                            break
            except Exception:
                pass

        user = None
        if email:
            user = User.objects.filter(email=email).first()

        if not user and gh_login:
            user = User.objects.filter(username=gh_login).first()

        if not user:
            base_username = gh_login or f"github_{gh_id[:8]}"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            first_name = gh_name.split()[0] if gh_name else gh_login
            last_name = " ".join(gh_name.split()[1:]) if gh_name and len(gh_name.split()) > 1 else ""

            user = User.objects.create(
                username=username,
                email=email or '',
                first_name=first_name,
                last_name=last_name
            )
            user.set_unusable_password()
            user.save()
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, f"Xush kelibsiz, {user.first_name or user.username}! GitHub orqali profilingiz yaratildi.")
        else:
            messages.success(request, f"Qaytganingiz bilan, {user.first_name or user.username}!")

        login(request, user)
        return redirect('store:dashboard')

    except Exception as e:
        messages.error(request, f"GitHub OAuth jarayonida xatolik: {str(e)}")
        return redirect('store:login')


def game_view(request):
    """Dark Manga Luxury Upgrade – standalone luxury clicker game page."""
    user_balance = 0.00
    user_authenticated = False
    username = ""
    if request.user.is_authenticated:
        user_authenticated = True
        username = request.user.username
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_balance = float(profile.balance)

    context = {
        'user_authenticated': user_authenticated,
        'username': username,
        'user_balance': user_balance,
    }
    return render(request, 'index.html', context)


def skin_upgrade(request):
    """Render the free, client-side skin upgrade simulation."""
    return render(request, 'store/upgrade.html')


@require_GET
def api_upgrade_skins(request):
    """Return marketplace catalog items for the upgrade demo's searchable selector."""
    search = request.GET.get('q', '').strip()
    weapon = request.GET.get('weapon', '').strip()
    min_price_raw = request.GET.get('min_price', '').strip()
    max_price_raw = request.GET.get('max_price', '').strip()
    if len(search) > 100 or len(weapon) > 100:
        return JsonResponse({'error': 'Search and weapon filters must be 100 characters or fewer.'}, status=400)

    filters = Q()
    if search:
        filters &= Q(title__icontains=search) | Q(weapon_type__icontains=search)
    if weapon:
        filters &= Q(weapon_type__iexact=weapon)

    price_filters = {}
    for parameter, raw_value, lookup in (
        ('min_price', min_price_raw, 'retail_price__gte'),
        ('max_price', max_price_raw, 'retail_price__lte'),
    ):
        if raw_value:
            try:
                amount = Decimal(raw_value)
                if not amount.is_finite() or amount < 0:
                    raise InvalidOperation
            except (InvalidOperation, ValueError):
                return JsonResponse({'error': f'{parameter} must be a valid non-negative price.'}, status=400)
            price_filters[lookup] = amount

    if ('retail_price__gte' in price_filters and 'retail_price__lte' in price_filters
            and price_filters['retail_price__gte'] > price_filters['retail_price__lte']):
        return JsonResponse({'error': 'Minimum price cannot exceed maximum price.'}, status=400)

    products = Product.objects.filter(filters, **price_filters).order_by('-is_featured', 'retail_price', 'id')
    rarity_labels = dict(Product.RARITY_CHOICES)
    skins = [
        {
            'id': product.pk,
            'title': product.title,
            'image': product.display_image,
            'price': str(product.retail_price),
            'rarity': rarity_labels.get(product.rarity, product.get_rarity_display()),
            'rarity_key': product.rarity,
            'wear': product.wear_condition,
            'weapon': product.weapon_type,
        }
        for product in products
    ]
    weapons = list(
        Product.objects.order_by('weapon_type').values_list('weapon_type', flat=True).distinct()
    )
    return JsonResponse({'skins': skins, 'weapons': weapons})


@require_GET
def api_upgrade_chance(request):
    """Calculate a demo upgrade chance from current database prices."""
    source_id = request.GET.get('source_id', '')
    target_id = request.GET.get('target_id', '')
    try:
        source_id = int(source_id)
        target_id = int(target_id)
        if source_id <= 0 or target_id <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Choose valid source and target catalog skins.'}, status=400)

    if source_id == target_id:
        return JsonResponse({'error': 'Source and target skins must be different.'}, status=400)

    products = Product.objects.in_bulk([source_id, target_id])
    source = products.get(source_id)
    target = products.get(target_id)
    if source is None or target is None:
        return JsonResponse({'error': 'A selected catalog skin is no longer available.'}, status=404)
    if source.retail_price <= 0 or target.retail_price <= 0:
        return JsonResponse({'error': 'Both catalog skin prices must be greater than zero.'}, status=400)

    with localcontext() as context:
        context.prec = 32
        chance = min(Decimal('100'), source.retail_price / target.retail_price * Decimal('100'))

    return JsonResponse({
        'source_id': source.pk,
        'target_id': target.pk,
        'source_price': str(source.retail_price),
        'target_price': str(target.retail_price),
        'chance': format(chance, '.8f'),
    })


@require_POST
def api_game_claim_reward(request):
    """
    O'yinchilar Dark Manga o'yinida yutuqlarga erishganda Skinly balansiga
    haqiqiy bonus pul o'tkazish imkoniyati.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'need_auth': True,
            'message': "Mukofotni Skinly hisobingizga olish uchun tizimga kiring!"
        }, status=401)

    try:
        if request.content_type == 'application/json' or (request.body and request.body.strip().startswith(b'{')):
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST
    except Exception:
        data = {}

    reward_type = data.get('reward_type', 'milestone')
    rolls_count = int(data.get('rolls', 0))

    # Reward tiers based on game rolls / milestone
    bonus_amount = Decimal('10.00')
    if reward_type == 'chapter_5':
        bonus_amount = Decimal('25.00')
    elif reward_type == 'prestige':
        bonus_amount = Decimal('50.00')
    elif reward_type == 'lucky_chest':
        bonus_amount = Decimal('5.00')

    with transaction.atomic():
        profile, _ = UserProfile.objects.select_for_update().get_or_create(user=request.user)
        old_balance = profile.balance
        profile.balance += bonus_amount
        profile.save(update_fields=['balance'])

        BalanceTransaction.objects.create(
            user=request.user,
            skin_name=f"Dark Manga O'yini Mukofoti ({reward_type.capitalize()})",
            price=bonus_amount,
            quantity=1,
            total=bonus_amount,
            balance_before=old_balance,
            balance_after=profile.balance,
            status='Completed',
            transaction_type='Deposit'
        )

    return JsonResponse({
        'success': True,
        'message': f"Tabriklaymiz! +${bonus_amount:.2f} muvaffaqiyatli Skinly hamyoningizga o'tkazildi!",
        'reward_amount': float(bonus_amount),
        'new_balance': float(profile.balance),
        'new_balance_formatted': f"${profile.balance:,.2f}".replace(',', ' '),
    })
