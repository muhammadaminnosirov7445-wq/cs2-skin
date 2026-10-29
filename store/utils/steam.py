import re

STEAM_TRADE_URL_REGEX = re.compile(
    r'^https?://steamcommunity\.com/tradeoffer/new/\?partner=\d+&token=[a-zA-Z0-9_-]+'
)


def validate_trade_url(url: str) -> bool:
    """
    Validates whether the provided string is a valid Steam Trade Offer URL.
    Example: https://steamcommunity.com/tradeoffer/new/?partner=12345678&token=AbCdEfGh
    """
    if not url:
        return False
    return bool(STEAM_TRADE_URL_REGEX.match(url.strip()))


def get_wear_badge(float_val: float) -> dict:
    """
    Returns condition name and CS2 badge color based on exact float value.
    0.00 - 0.07: Factory New
    0.07 - 0.15: Minimal Wear
    0.15 - 0.38: Field-Tested
    0.38 - 0.45: Well-Worn
    0.45 - 1.00: Battle-Scarred
    """
    if float_val <= 0.07:
        return {'name': 'Factory New', 'abbr': 'FN', 'color': '#10b981', 'glow': 'glow-emerald'}
    elif float_val <= 0.15:
        return {'name': 'Minimal Wear', 'abbr': 'MW', 'color': '#06b6d4', 'glow': 'glow-cyan'}
    elif float_val <= 0.38:
        return {'name': 'Field-Tested', 'abbr': 'FT', 'color': '#eab308', 'glow': 'glow-amber'}
    elif float_val <= 0.45:
        return {'name': 'Well-Worn', 'abbr': 'WW', 'color': '#f97316', 'glow': 'glow-orange'}
    else:
        return {'name': 'Battle-Scarred', 'abbr': 'BS', 'color': '#ef4444', 'glow': 'glow-red'}
