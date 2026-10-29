import asyncio
from django.core.management.base import BaseCommand
from store.bot import run_aiogram_bot


class Command(BaseCommand):
    help = 'Runs the Aiogram Telegram bot for Bulldrop store'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Bulldrop Aiogram Telegram Bot..."))
        try:
            asyncio.run(run_aiogram_bot())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Bot stopped."))
