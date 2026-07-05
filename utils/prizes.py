import random
from config import PRIZES


def spin_roulette(roulette_type: str) -> dict:
    prizes = PRIZES.get(roulette_type, [])
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


def get_roulette_name(t: str) -> str:
    return {
        "day":        "🎯 Ежедневная",
        "three_days": "🎲 Рулетка 3 дня",
        "week":       "🏆 Недельная",
        "paid":       "💎 Платная (150₽)",
    }.get(t, t)


def get_roulette_emoji(t: str) -> str:
    return {"day":"🎯","three_days":"🎲","week":"🏆","paid":"💎"}.get(t, "🎰")


def format_prize_list(t: str) -> str:
    return "".join(
        f"  • {p['name']} — {p['chance']}%\n"
        for p in PRIZES.get(t, []))
