import uuid
import random
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='sword', help_text="Lucide icon name")

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    WEAR_CHOICES = [
        ('Factory New', 'Factory New (FN)'),
        ('Minimal Wear', 'Minimal Wear (MW)'),
        ('Field-Tested', 'Field-Tested (FT)'),
        ('Well-Worn', 'Well-Worn (WW)'),
        ('Battle-Scarred', 'Battle-Scarred (BS)'),
    ]

    RARITY_CHOICES = [
        ('covert', 'Covert (Red / Extraordinary)'),
        ('classified', 'Classified (Pink)'),
        ('restricted', 'Restricted (Purple)'),
        ('mil-spec', 'Mil-Spec (Blue)'),
        ('extraordinary', '★ Rare Special Item (Gold)'),
    ]

    title = models.CharField(max_length=255, help_text="Masalan: ★ Karambit | Doppler (Factory New)")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    weapon_type = models.CharField(max_length=100, default='Rifle', help_text="Masalan: AWP, AK-47, M4A4, Karambit, Butterfly Knife")
    wear_condition = models.CharField(max_length=50, choices=WEAR_CHOICES, default='Factory New')
    float_value = models.FloatField(default=0.015, help_text="Float qiymati: 0.000 dan 1.000 gacha")
    stattrak = models.BooleanField(default=False, verbose_name="StatTrak™")
    rarity = models.CharField(max_length=30, choices=RARITY_CHOICES, default='covert')
    description = models.TextField(blank=True, default="Counter-Strike 2 rasmiy inventar skin to'plamidan.")
    
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Tannarx (Dropshipping)")
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Sotuv narxi")
    stock = models.PositiveIntegerField(default=1)
    
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='listed_products', help_text="Skin egasi / Sotuvchi")
    pattern_template = models.PositiveIntegerField(default=1, help_text="Paint Seed / Pattern template (1-1000)")
    model_3d_file = models.FileField(upload_to='models_3d/', blank=True, null=True, help_text="CS2 3D Model (.glb / .gltf)")
    model_3d_url = models.URLField(max_length=600, blank=True, null=True, help_text="CS2 3D Model havola (GLB/GLTF)")

    image = models.ImageField(upload_to='skins/', blank=True, null=True)
    image_url = models.URLField(max_length=600, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['retail_price']),
            models.Index(fields=['weapon_type']),
            models.Index(fields=['wear_condition']),
            models.Index(fields=['rarity']),
            models.Index(fields=['-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def price(self):
        return self.retail_price

    @property
    def estimated_profit(self):
        return self.retail_price - self.wholesale_price

    @property
    def display_image(self):
        if self.image:
            try:
                return self.image.url
            except ValueError:
                pass
        if self.image_url:
            return self.image_url
        return '/static/images/placeholder.svg'

    @property
    def rarity_color(self):
        mapping = {
            'extraordinary': '#ffd700',
            'covert': '#eb4b4b',
            'classified': '#d32ce6',
            'restricted': '#8847ff',
            'mil-spec': '#4b69ff',
        }
        return mapping.get(self.rarity, '#eb4b4b')

    @property
    def float_percentage(self):
        return min(max(self.float_value * 100, 0), 100)

    @property
    def seller_name(self):
        if self.seller:
            return self.seller.username
        return "Skinly Vault (Official)"

    @property
    def seller_is_verified(self):
        if self.seller and hasattr(self.seller, 'profile'):
            return self.seller.profile.is_verified_seller
        return True

    @property
    def seller_rating(self):
        if self.seller and hasattr(self.seller, 'profile'):
            return self.seller.profile.rating_average
        return 5.0

    def __str__(self):
        st = "StatTrak™ " if self.stattrak else ""
        return f"{st}{self.title} ({self.wear_condition}) - ${self.retail_price}"


class Case(models.Model):
    name = models.CharField(max_length=200, help_text="Masalan: Chroma Dreams Case")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Case ochish narxi")
    image_url = models.URLField(max_length=600, blank=True, null=True)
    image = models.ImageField(upload_to='cases/', blank=True, null=True)
    description = models.TextField(blank=True, default="Noyob CS2 pichoqlari va elita qurollari to'plami.")
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    skins = models.ManyToManyField(Product, through='CaseItem', related_name='cases')

    class Meta:
        ordering = ['price']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Case.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL1m5fn8Sdk7vORbqhsLfWAMWuZxuZi_uI_TX6wxxkjsGXXnImsJ37COlUoWcByEOMOtxa5kdXmNu3htVPZjN1bjXKpkHLRfQU"

    def get_items(self):
        return self.case_items.select_related('product', 'product__category').order_by('-product__retail_price')

    def get_top_drops(self, count=4):
        return self.skins.order_by('-retail_price')[:count]

    def roll_skin(self):
        items = list(self.case_items.select_related('product').all())
        if not items:
            return None
        weights = [max(item.drop_weight, 1) for item in items]
        chosen = random.choices(items, weights=weights, k=1)[0]
        return chosen.product

    def update_chances(self):
        items = list(self.case_items.all())
        total_weight = sum(item.drop_weight for item in items)
        if total_weight > 0:
            for item in items:
                item.drop_chance = round((item.drop_weight / total_weight) * 100, 2)
                item.save(update_fields=['drop_chance'])

    def __str__(self):
        return f"{self.name} (${self.price})"


class CaseItem(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='case_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_case_items')
    drop_weight = models.PositiveIntegerField(default=100, help_text="Ehtimollik og'irligi")
    drop_chance = models.FloatField(default=0.0, help_text="Hisoblangan ehtimollik %")

    class Meta:
        ordering = ['-drop_weight', '-product__retail_price']
        unique_together = ('case', 'product')

    def __str__(self):
        return f"{self.case.name} -> {self.product.title} (weight: {self.drop_weight})"


class UpgradeGame(models.Model):
    STATUS_CHOICES = [
        ('Won', 'Yutdi (Won)'),
        ('Lost', 'Yutqazdi (Lost)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upgrades')
    input_item = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='upgrade_inputs', help_text="Tikilgan skin")
    target_item = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='upgrade_targets', help_text="Yutib olish uchun mo'ljallangan skin")
    multiplier = models.FloatField(help_text="Ko'paytiruvchi koeffitsiyenti (masalan: 2x)")
    chance_percentage = models.FloatField(help_text="Yutish ehtimoli foizi (%)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Lost')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} Upgrade: {self.input_item.title} -> {self.target_item.title} [{self.status}]"



class UserInventory(models.Model):
    ACQUIRED_CHOICES = [
        ('Purchased', 'Do\'kondan sotib olingan (Purchased)'),
        ('Case Opening', 'Keys ochishdan yutib olingan (Case Opening)'),
        ('Upgrade', 'Upgrade orqali qo\'lga kiritilgan (Upgrade)'),
    ]

    STATUS_CHOICES = [
        ('In Inventory', 'Inventarda mavjud'),
        ('Withdrawn', 'Steam orqali chiqarilgan (Withdrawn)'),
        ('Upgraded', 'Upgrade jarayonida ishlatilgan (Consumed)'),
        ('Sold', 'Balansga sotilgan (Sold)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    acquired_via = models.CharField(max_length=50, choices=ACQUIRED_CHOICES, default='Purchased')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='In Inventory')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.product.title} [{self.status}]"


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Kutilmoqda (Pending)'),
        ('Bot Processing', 'Bot inventarni tekshirmoqda'),
        ('Trade Sent', 'Steam Trade Taklif yuborildi'),
        ('Completed', 'Bitim muvaffaqiyatli yakunlandi'),
        ('Cancelled', 'Bekor qilindi'),
    ]

    tracking_code = models.CharField(max_length=30, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    steam_trade_url = models.URLField(max_length=500, default='', help_text="Mijozning Steam Trade URL havolasi")
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = f"SKN-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} [{self.tracking_code}] - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_cost(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(max_length=600, blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    is_verified_seller = models.BooleanField(default=False, help_text="Tasdiqlangan sotuvchi nishoni faqat haqiqiy verifikatsiyadan o'tganda beriladi")
    sales_count = models.PositiveIntegerField(default=0, help_text="Muvaffaqiyatli sotuvlar soni")
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    steam_id = models.CharField(max_length=50, blank=True, null=True, help_text="Steam ID64")
    steam_trade_url = models.URLField(max_length=500, blank=True, null=True, help_text="Standart Steam Trade URL")
    weapon_preferences = models.JSONField(default=list, blank=True)
    preferred_min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    experience_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def display_avatar(self):
        if self.avatar:
            try:
                return self.avatar.url
            except ValueError:
                pass
        if self.avatar_url:
            return self.avatar_url
        return f"https://api.dicebear.com/7.x/bottts/svg?seed={self.user.username}&backgroundColor=0b0e1d,10152b"

    @property
    def rating_average(self):
        reviews = self.user.received_reviews.all()
        if not reviews.exists():
            return 5.0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    @property
    def reviews_count(self):
        return self.user.received_reviews.count()

    def __str__(self):
        return f"{self.user.username} (Balance: ${self.balance})"

    @property
    def level(self):
        return self.experience_points // 100 + 1


class ProductFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skin_favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='user_favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_product_favorite'),
        ]


class ProductView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skin_views')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='user_views')
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_product_view'),
        ]
        indexes = [models.Index(fields=['user', '-viewed_at'])]


class SkinBattle(models.Model):
    product_a = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='battle_as_a')
    product_b = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='battle_as_b')
    battle_date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-battle_date', '-created_at']
        constraints = [
            models.UniqueConstraint(fields=['battle_date'], name='unique_daily_skin_battle'),
        ]


class SkinBattleVote(models.Model):
    battle = models.ForeignKey(SkinBattle, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skin_battle_votes')
    choice = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='battle_votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['battle', 'user'], name='unique_user_battle_vote'),
        ]
        indexes = [models.Index(fields=['created_at', 'choice'])]


class SkinCollection(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skin_collections')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, blank=True)
    share_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class CollectionItem(models.Model):
    collection = models.ForeignKey(SkinCollection, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='collection_items')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']
        constraints = [
            models.UniqueConstraint(fields=['collection', 'product'], name='unique_collection_product'),
        ]


class CollectionComment(models.Model):
    STATUS_CHOICES = [('visible', 'Visible'), ('hidden', 'Hidden')]
    collection = models.ForeignKey(SkinCollection, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collection_comments')
    content = models.CharField(max_length=500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='visible')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['collection', 'status', '-created_at'])]


class CommunityReport(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('reviewed', 'Reviewed'), ('dismissed', 'Dismissed')]
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_reports')
    collection = models.ForeignKey(SkinCollection, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    comment = models.ForeignKey(CollectionComment, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    reason = models.CharField(max_length=300)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['reporter', 'collection'], condition=models.Q(collection__isnull=False), name='unique_collection_report'),
            models.UniqueConstraint(fields=['reporter', 'comment'], condition=models.Q(comment__isnull=False), name='unique_comment_report'),
        ]


class CommunityPoll(models.Model):
    title = models.CharField(max_length=160)
    description = models.CharField(max_length=500, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-starts_at']

    @property
    def is_open(self):
        now = timezone.now()
        return self.starts_at <= now < self.ends_at


class PollChoice(models.Model):
    poll = models.ForeignKey(CommunityPoll, on_delete=models.CASCADE, related_name='choices')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='poll_choices')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['poll', 'product'], name='unique_poll_product'),
        ]


class PollVote(models.Model):
    poll = models.ForeignKey(CommunityPoll, on_delete=models.CASCADE, related_name='votes')
    choice = models.ForeignKey(PollChoice, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['poll', 'user'], name='unique_user_poll_vote'),
        ]


class PriceWatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_watches')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_watches')
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    notified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_price_watch'),
        ]


class MissionActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mission_activities')
    mission_code = models.CharField(max_length=30)
    period_start = models.DateField()
    object_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'mission_code', 'period_start', 'object_key'], name='unique_mission_activity'),
        ]
        indexes = [models.Index(fields=['user', 'period_start', 'mission_code'])]


class MissionClaim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mission_claims')
    mission_code = models.CharField(max_length=30)
    period_start = models.DateField()
    experience_awarded = models.PositiveIntegerField()
    claimed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'mission_code', 'period_start'], name='unique_mission_claim'),
        ]


class AchievementAward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievement_awards')
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=100)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-earned_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'code'], name='unique_user_achievement'),
        ]


class EngagementMetric(models.Model):
    metric = models.CharField(max_length=40)
    day = models.DateField()
    count = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['metric', 'day'], name='unique_daily_engagement_metric'),
        ]


class BalanceTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('Purchase', 'Xarid (Purchase)'),
        ('Deposit', 'Balans to\'ldirish (Deposit)'),
        ('Refund', 'Qaytarish (Refund)'),
    ]

    STATUS_CHOICES = [
        ('Purchased', 'Muvaffaqiyatli (Purchased)'),
        ('Completed', 'Bajarildi (Completed)'),
        ('Failed', 'Bekor qilindi (Failed)'),
    ]

    transaction_id = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balance_transactions')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    skin_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Purchased')
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES, default='Purchase')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.skin_name} (${self.total}) [{self.status}]"


class SkinPriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField()
    source = models.CharField(max_length=60, default='Market Transaction')
    volume = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['recorded_at']
        indexes = [
            models.Index(fields=['product', 'recorded_at']),
        ]

    def __str__(self):
        return f"{self.product.title} - ${self.price} @ {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"


class SellerReview(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i} yulduz") for i in range(1, 6)], default=5)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('buyer', 'order')

    def __str__(self):
        return f"Review by {self.buyer.username} for {self.seller.username} ({self.rating}★)"


class SellerReport(models.Model):
    REASON_CHOICES = [
        ('fake_listing', "Soxta yoki mavjud bo'lmagan skin"),
        ('scam_attempt', "Steam Trade taklifini buzish yoki firibgarlik"),
        ('inappropriate_profile', "Nomunosib profil ma'lumotlari"),
        ('price_manipulation', "Sun'iy narx ko'tarish"),
        ('other', "Boshqa sabab"),
    ]
    STATUS_CHOICES = [
        ('Pending', "Kutilmoqda"),
        ('Investigating', "Ko'rib chiqilmoqda"),
        ('Resolved', "Hal qilindi"),
        ('Dismissed', "Rad etildi"),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='filed_reports')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, default='other')
    details = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} on {self.seller.username} by {self.reporter.username}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('price_drop', "Narx pasayishi"),
        ('new_listing', "Yangi e'lon"),
        ('order_status', "Buyurtma holati"),
        ('listing_created', "E'lon yaratildi"),
        ('account', "Hisob bildirishnomasi"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='account')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link_url = models.CharField(max_length=300, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.notification_type}] {self.user.username}: {self.title}"
