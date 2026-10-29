from django.contrib import admin
from .models import (
    Category, Product, Case, CaseItem, UserInventory, Order, OrderItem,
    UserProfile, BalanceTransaction, UpgradeGame, SkinPriceHistory,
    SellerReview, SellerReport, Notification, ProductFavorite, ProductView,
    SkinBattle, SkinBattleVote, SkinCollection,
    CollectionItem, CollectionComment, CommunityReport, CommunityPoll, PollChoice,
    PollVote, PriceWatch, MissionActivity, MissionClaim, AchievementAward,
    EngagementMetric
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'seller', 'category', 'weapon_type', 'wear_condition', 'float_value', 'pattern_template', 'stattrak', 'rarity', 'wholesale_price', 'retail_price', 'stock', 'is_featured')
    list_filter = ('category', 'weapon_type', 'wear_condition', 'stattrak', 'rarity', 'is_featured', 'seller')
    search_fields = ('title', 'weapon_type', 'description')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('wholesale_price', 'retail_price', 'stock', 'is_featured')


class CaseItemInline(admin.TabularInline):
    model = CaseItem
    extra = 1
    autocomplete_fields = ['product']
    fields = ('product', 'drop_weight', 'drop_chance')


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'is_featured', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_featured')
    inlines = [CaseItemInline]


@admin.register(CaseItem)
class CaseItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'case', 'product', 'drop_weight', 'drop_chance')
    list_filter = ('case', 'product__rarity')
    search_fields = ('case__name', 'product__title')


@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'acquired_via', 'status', 'created_at')
    list_filter = ('acquired_via', 'status', 'created_at')
    search_fields = ('user__username', 'product__title')
    list_editable = ('status',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total_cost')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'tracking_code', 'user', 'full_name', 'phone', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('tracking_code', 'full_name', 'phone', 'steam_trade_url')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    readonly_fields = ('tracking_code', 'created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance', 'is_verified_seller', 'sales_count', 'steam_id', 'telegram_id', 'phone', 'created_at')
    list_filter = ('is_verified_seller', 'created_at')
    search_fields = ('user__username', 'user__email', 'steam_id', 'steam_trade_url', 'telegram_id', 'phone')
    list_editable = ('balance', 'is_verified_seller', 'sales_count')


@admin.register(BalanceTransaction)
class BalanceTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'skin_name', 'transaction_type', 'total', 'balance_after', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('transaction_id', 'user__username', 'skin_name')
    readonly_fields = ('transaction_id', 'created_at')


@admin.register(UpgradeGame)
class UpgradeGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'input_item', 'target_item', 'multiplier', 'chance_percentage', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'input_item__title', 'target_item__title')


@admin.register(SkinPriceHistory)
class SkinPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'price', 'volume', 'source', 'recorded_at')
    list_filter = ('source', 'recorded_at')
    search_fields = ('product__title', 'source')
    readonly_fields = ('recorded_at',)


@admin.register(SellerReview)
class SellerReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'seller', 'buyer', 'product', 'rating', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('seller__username', 'buyer__username', 'comment')


@admin.register(SellerReport)
class SellerReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'seller', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = ('reporter__username', 'seller__username', 'details')
    list_editable = ('status',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    list_editable = ('is_read',)


@admin.register(SkinCollection)
class SkinCollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_public', 'created_at', 'updated_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'owner__username', 'description')


@admin.register(CollectionComment)
class CollectionCommentAdmin(admin.ModelAdmin):
    list_display = ('collection', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('collection__title', 'user__username', 'content')
    list_editable = ('status',)


@admin.register(CommunityReport)
class CommunityReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'collection', 'comment', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('reporter__username', 'reason', 'collection__title', 'comment__content')
    list_editable = ('status',)


class PollChoiceInline(admin.TabularInline):
    model = PollChoice
    extra = 2


@admin.register(CommunityPoll)
class CommunityPollAdmin(admin.ModelAdmin):
    list_display = ('title', 'starts_at', 'ends_at')
    search_fields = ('title', 'description')
    inlines = [PollChoiceInline]


admin.site.register((SkinBattle, SkinBattleVote, ProductFavorite, ProductView, CollectionItem,
                     PollVote, PriceWatch, MissionActivity, MissionClaim,
                     AchievementAward, EngagementMetric))
