from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, Order, BalanceTransaction, Product, Notification, SkinPriceHistory, PriceWatch


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        # Welcome notification
        Notification.objects.create(
            user=instance,
            notification_type='account',
            title="Skinly bozoriga xush kelibsiz!",
            message="CS2 nodir skinlarini eng yaxshi narxlarda xarid qiling yoki o'z inventaringizni soting.",
            link_url='/dashboard/'
        )


@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, created, **kwargs):
    if not instance.user:
        return
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type='order_status',
            title=f"Buyurtma qabul qilindi: #{instance.id}",
            message=f"Trek-kod: {instance.tracking_code}. Steam Bot trade tayyorlamoqda.",
            link_url=f"/track/?code={instance.tracking_code}"
        )
    else:
        if instance.status == 'Trade Sent':
            Notification.objects.create(
                user=instance.user,
                notification_type='order_status',
                title=f"Steam Trade Taklif yuborildi! ({instance.tracking_code})",
                message="Iltimos, Steam profilingizda trade taklifini tasdiqlang.",
                link_url=f"/track/?code={instance.tracking_code}"
            )
        elif instance.status == 'Completed':
            Notification.objects.create(
                user=instance.user,
                notification_type='order_status',
                title=f"Buyurtma muvaffaqiyatli yakunlandi! ({instance.tracking_code})",
                message="Skin Steam inventaringizga yetkazildi. Rahmat!",
                link_url=f"/track/?code={instance.tracking_code}"
            )


@receiver(post_save, sender=BalanceTransaction)
def balance_deposit_notification(sender, instance, created, **kwargs):
    if created and instance.transaction_type == 'Deposit':
        Notification.objects.create(
            user=instance.user,
            notification_type='account',
            title="Balans to'ldirildi",
            message=f"Hamyoningizga +${instance.total:.2f} muvaffaqiyatli qo'shildi. Joriy balans: ${instance.balance_after:.2f}",
            link_url="/dashboard/"
        )


@receiver(pre_save, sender=Product)
def remember_previous_listing(sender, instance, **kwargs):
    if instance.pk:
        instance._previous_listing = Product.objects.filter(pk=instance.pk).values(
            'retail_price', 'stock'
        ).first()
    else:
        instance._previous_listing = None


@receiver(post_save, sender=Product)
def product_price_and_listing_tracker(sender, instance, created, **kwargs):
    previous = getattr(instance, '_previous_listing', None)
    price_changed = created or previous is None or previous['retail_price'] != instance.retail_price
    availability_changed = created or previous is None or previous['stock'] != instance.stock
    if price_changed:
        SkinPriceHistory.objects.create(
            product=instance,
            price=instance.retail_price,
            recorded_at=timezone.now(),
            source="Listing Creation" if created else "Price Update",
            volume=1,
        )

    if (price_changed or availability_changed) and instance.stock > 0:
        watches = PriceWatch.objects.filter(
            product=instance, is_active=True, target_price__gte=instance.retail_price
        ).select_related('user')
        for watch in watches:
            if watch.notified_at:
                continue
            Notification.objects.create(
                user=watch.user,
                notification_type='price_drop',
                title='Skin narxi maqsadingizga yetdi',
                message=f'{instance.title} endi ${instance.retail_price:.2f} — belgilangan chegarangiz ${watch.target_price:.2f}.',
                link_url=f"/product/{instance.slug}/",
            )
            watch.notified_at = timezone.now()
            watch.save(update_fields=['notified_at'])

    if price_changed:
        PriceWatch.objects.filter(
            product=instance, is_active=True, target_price__lt=instance.retail_price
        ).exclude(notified_at=None).update(notified_at=None)

    # Notify seller upon listing creation
    if created and instance.seller:
        Notification.objects.create(
            user=instance.seller,
            notification_type='listing_created',
            title="Skin e'loni joylashtirildi",
            message=f"'{instance.title}' (${instance.retail_price}) muvaffaqiyatli bozorda e'lon qilindi.",
            link_url=f"/product/{instance.slug}/"
        )
