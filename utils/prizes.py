from copy import deepcopy
import random

from config import (
    PRIZES,
    PAID_ROULETTE_BASE,
    PAID_ROULETTE_DEFAULT_LUCK,
    PAID_ROULETTE_LEVELS,
    PAID_ROULETTE_MAX,
    PAID_ROULETTE_MAX_COUNT,
    PAID_ROULETTE_PRICES,
)


def normalize_paid_luck(luck: int | str | None) -> int:
    try:
        value = int(luck) if luck is not None else PAID_ROULETTE_DEFAULT_LUCK
    except (TypeError, ValueError):
        value = PAID_ROULETTE_DEFAULT_LUCK

    if value <= PAID_ROULETTE_LEVELS[0]:
        return PAID_ROULETTE_LEVELS[0]
    if value >= PAID_ROULETTE_LEVELS[-1]:
        return PAID_ROULETTE_LEVELS[-1]

    return min(PAID_ROULETTE_LEVELS, key=lambda n: abs(n - value))


def normalize_paid_count(count: int | str | None) -> int:
    try:
        value = int(count) if count is not None else 1
    except (TypeError, ValueError):
        value = 1

    return max(1, min(PAID_ROULETTE_MAX_COUNT, value))


def get_paid_price(luck: int | str | None = None) -> int:
    return PAID_ROULETTE_PRICES[normalize_paid_luck(luck)]


def build_roulette_prizes(roulette_type: str, luck: int | str | None = None) -> list[dict]:
    if roulette_type != "paid":
        return deepcopy(PRIZES.get(roulette_type, []))

    luck_value = normalize_paid_luck(luck)
    start = PAID_ROULETTE_LEVELS[0]
    end   = PAID_ROULETTE_LEVELS[-1]
    mix   = (luck_value - start) / (end - start) if end != start else 0

    prizes = []
    for base, premium in zip(PAID_ROULETTE_BASE, PAID_ROULETTE_MAX):
        item = deepcopy(base)
        item["chance"] = round(
            base["chance"] + (premium["chance"] - base["chance"]) * mix,
            2,
        )
        prizes.append(item)
    return prizes


def spin_roulette(roulette_type: str, luck: int | str | None = None) -> dict:
    prizes = build_roulette_prizes(roulette_type, luck)
    if not prizes:
        return {"name": "Ничего", "type": "nothing", "value": 0, "chance": 100}

    total = sum(p["chance"] for p in prizes)
    r     = random.uniform(0, total)
    cum   = 0
    for p in prizes:
        cum += p["chance"]
        if r <= cum:
            return p
    return prizes[-1]


def get_roulette_name(t: str, luck: int | str | None = None) -> str:
    if t == "paid":
        if luck is None:
            return "💎 Платная"
        luck_value = normalize_paid_luck(luck)
        return f"💎 Платная · {luck_value}% / {get_paid_price(luck_value)}₽"

    return {
        "day":        "🎯 Ежедневная",
        "three_days": "🎲 Каждые 3 дня",
        "week":       "🏆 Еженедельная",
    }.get(t, t)


def get_roulette_emoji(t: str) -> str:
    return {"day": "🎯", "three_days": "🎲", "week": "🏆", "paid": "💎"}.get(t, "🎰")


def format_prize_list(t: str, luck: int | str | None = None) -> str:
    return "".join(
        f"  • {p['name']} — {p['chance']}%\n"
        for p in build_roulette_prizes(t, luck)
    )
