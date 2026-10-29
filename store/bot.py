
import os
import asyncio
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE'))
TELEGRAM_ADMIN_CHAT_ID = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', os.getenv('TELEGRAM_ADMIN_CHAT_ID', 'YOUR_CHAT_ID_HERE'))


def format_cs2_order_message(order) -> str:
    """Format a CS2 skin trade order into a rich Telegram admin notification."""
    items_text = ""
    for idx, item in enumerate(order.items.all(), 1):
        st = "🔥 [StatTrak™] " if item.product.stattrak else ""
        items_text += (
            f"  {idx}. <b>{st}{item.product.title}</b>\n"
            f"     🎯 Holat: <code>{item.product.wear_condition}</code> | Float: <code>{item.product.float_value:.4f}</code>\n"
            f"     📦 Miqdor: {item.quantity} dona | Narxi: ${item.price}\n"
            f"     🖼 <a href='{item.product.display_image}'>[Steam HD Skin Render]</a>\n"
        )

    msg = (
        f"⚡️ <b>YANGI CS2 SKIN BUYURTMASI! [SKINLY]</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷 <b>Buyurtma ID:</b> <code>{order.tracking_code}</code>\n"
        f"👤 <b>Xaridor:</b> {order.full_name}\n"
        f"📞 <b>Telefon:</b> <code>{order.phone}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>Steam Trade URL:</b>\n"
        f"<a href='{order.steam_trade_url}'>{order.steam_trade_url}</a>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔫 <b>Buyurtma qilingan skinlar:</b>\n{items_text or '  Skin maʼlumoti mavjud emas'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Jami to'lov:</b> <b>${order.total_price}</b>\n"
        f"📊 <b>Status:</b> 🟡 <i>{order.get_status_display()}</i>\n"
        f"⏱ <b>Vaqt:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
    )
    if order.user:
        msg += f"💼 <b>Mijoz akkaunti:</b> @{order.user.username}\n"

    msg += "\n🚀 <i>Steam Bot orqali Trade Offer yuborishga tayyor!</i>"
    return msg


def send_telegram_order_notification(order):
    """
    Sends a formatted notification to Telegram Admin/Channel.
    Attempts to send with skin photo if available, or text message.
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', TELEGRAM_BOT_TOKEN)
    chat_id = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', TELEGRAM_ADMIN_CHAT_ID)

    if not token or token == 'YOUR_BOT_TOKEN_HERE' or not chat_id or chat_id == 'YOUR_CHAT_ID_HERE':
        logger.warning(
            f"[Telegram Bot] Token yoki Chat ID sozlanmagan. "
            f"CS2 Buyurtma #{order.tracking_code} haqida xabar konsolga chiqarildi:\n"
            f"{format_cs2_order_message(order)}"
        )
        return False

    first_item = order.items.first()
    image_url = first_item.product.display_image if first_item else None

    # Try sending photo with caption if image available
    if image_url and image_url.startswith('http'):
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": image_url,
            "caption": format_cs2_order_message(order),
            "parse_mode": "HTML",
        }
    else:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": format_cs2_order_message(order),
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }

    try:
        response = requests.post(url, json=payload, timeout=6)
        if response.status_code == 200:
            logger.info(f"[Telegram Bot] Notification successfully sent for {order.tracking_code}")
            return True
        else:
            # Fallback to plain text if sendPhoto fails
            url_msg = f"https://api.telegram.org/bot{token}/sendMessage"
            payload_msg = {
                "chat_id": chat_id,
                "text": format_cs2_order_message(order),
                "parse_mode": "HTML",
            }
            res2 = requests.post(url_msg, json=payload_msg, timeout=5)
            return res2.status_code == 200
    except Exception as e:
        logger.error(f"[Telegram Bot Exception] {str(e)}")
        return False


# Aiogram 3 Integration for standalone bot execution
async def run_aiogram_bot():
    """
    Aiogram 3 standalone bot runner with CS2 trade checking commands.
    """
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command
    from aiogram.enums import ParseMode

    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', TELEGRAM_BOT_TOKEN)
    if not token or token == 'YOUR_BOT_TOKEN_HERE':
        print("Please configure TELEGRAM_BOT_TOKEN in settings.py or .env")
        return

    bot = Bot(token=token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(
            f"👋 Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n"
            f"<b>Skinly — CS2 Skins Dropshipping & Trade</b> botiga xush kelibsiz.\n"
            f"Sizning Telegram ID: <code>{message.from_user.id}</code>\n"
            f"Buyurtmalarni ko'rish uchun /orders buyrug'ini yuboring.",
            parse_mode=ParseMode.HTML
        )

    @dp.message(Command("orders"))
    async def cmd_orders(message: types.Message):
        from .models import Order
        recent_orders = Order.objects.all()[:5]
        if not recent_orders:
            await message.answer("📭 Hozircha yangi CS2 buyurtmalari yo'q.")
            return

        text = "🎯 <b>Oxirgi 5 ta CS2 buyurtma:</b>\n\n"
        for o in recent_orders:
            text += f"• <code>{o.tracking_code}</code> — {o.full_name} (${o.total_price})\n  Holat: {o.status}\n  Trade URL: {o.steam_trade_url}\n\n"
        await message.answer(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    print("🤖 Skinly CS2 Aiogram bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(run_aiogram_bot())
