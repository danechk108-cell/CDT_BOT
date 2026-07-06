import os

BOT_TOKEN    = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
OWNER_ID     = 8565986003
WEBAPP_URL   = os.getenv("WEBAPP_URL", "https://your-service.onrender.com")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cdtdf:RmqUhxcbM6UkQQmDQNLdzg9IeZCD29u0@dpg-d92l6b3tqb8s73e638cg-a.ohio-postgres.render.com/niomero"
)

REQUIRED_CHANNELS = [
    {"id": "@hilonchennel",     "url": "https://t.me/hilonchennel",     "title": "HilonChannel"},
    {"id": "@SuperStarsChanell","url": "https://t.me/SuperStarsChanell","title": "SuperStars"},
    {"id": "@CeedRoulet",       "url": "https://t.me/CeedRoulet",       "title": "CeedRoulet"},
]

PRIZES = {
    "day": [
        {"name": "10₽ на баланс",  "type": "balance", "value": 10.0, "chance": 5},
        {"name": "5₽ на баланс",   "type": "balance", "value": 5.0,  "chance": 10},
        {"name": "1₽ на баланс",   "type": "balance", "value": 1.0,  "chance": 25},
        {"name": "0.1₽ на баланс", "type": "balance", "value": 0.1,  "chance": 40},
        {"name": "Ничего",         "type": "nothing",  "value": 0,    "chance": 20},
    ],
    "three_days": [
        {"name": "20₽ на баланс", "type": "balance", "value": 20.0, "chance": 5},
        {"name": "10₽ на баланс", "type": "balance", "value": 10.0, "chance": 10},
        {"name": "5₽ на баланс",  "type": "balance", "value": 5.0,  "chance": 25},
        {"name": "1₽ на баланс",  "type": "balance", "value": 1.0,  "chance": 40},
        {"name": "Ничего",        "type": "nothing",  "value": 0,    "chance": 20},
    ],
    "week": [
        {"name": "30₽ на баланс",  "type": "balance", "value": 30.0, "chance": 3},
        {"name": "20₽ на баланс",  "type": "balance", "value": 20.0, "chance": 7},
        {"name": "10₽ на баланс",  "type": "balance", "value": 10.0, "chance": 15},
        {"name": "5₽ на баланс",   "type": "balance", "value": 5.0,  "chance": 25},
        {"name": "2.5₽ на баланс", "type": "balance", "value": 2.5,  "chance": 30},
        {"name": "Ничего",         "type": "nothing",  "value": 0,    "chance": 20},
    ],
    "paid": [
        {"name": "Аккаунт",       "type": "account", "value": 0,    "chance": 5},
        {"name": "Голда",         "type": "gold",    "value": 0,    "chance": 10},
        {"name": "50₽ на баланс", "type": "balance", "value": 50.0, "chance": 15},
        {"name": "25₽ на баланс", "type": "balance", "value": 25.0, "chance": 30},
        {"name": "15₽ на баланс", "type": "balance", "value": 15.0, "chance": 40},
    ],
}

COOLDOWNS = {
    "day":        86400,
    "three_days": 259200,
    "week":       604800,
}

PAID_ROULETTE_LEVELS = [20, 30, 40, 50, 60, 70]
PAID_ROULETTE_PRICES = {
    20: 50,
    30: 100,
    40: 150,
    50: 200,
    60: 250,
    70: 300,
}
PAID_ROULETTE_DEFAULT_LUCK = 20
PAID_ROULETTE_MAX_COUNT = 5

PAID_ROULETTE_BASE = [
    {"name": "Аккаунт",       "type": "account", "value": 0,    "chance": 5},
    {"name": "Голда",         "type": "gold",    "value": 0,    "chance": 10},
    {"name": "50₽ на баланс", "type": "balance", "value": 50.0, "chance": 15},
    {"name": "25₽ на баланс", "type": "balance", "value": 25.0, "chance": 30},
    {"name": "15₽ на баланс", "type": "balance", "value": 15.0, "chance": 40},
]
PAID_ROULETTE_MAX = [
    {"name": "Аккаунт",       "type": "account", "value": 0,    "chance": 20},
    {"name": "Голда",         "type": "gold",    "value": 0,    "chance": 30},
    {"name": "50₽ на баланс", "type": "balance", "value": 50.0, "chance": 25},
    {"name": "25₽ на баланс", "type": "balance", "value": 25.0, "chance": 15},
    {"name": "15₽ на баланс", "type": "balance", "value": 15.0, "chance": 10},
]
PRIZE_TRANSFER_DELAY = 7200  # 2 часа в секундах

# Premium Emoji IDs
PE = {
    # Набор 1 (оригинальные)
    "money":   "5244731629120820298",
    "heart":   "5242497898234550654",
    "wave":    "5244988141747606686",
    "cash":    "5244806842588108571",
    "wallet":  "5244615046528538427",
    "hmm":     "5244866250575745199",
    "basket":  "5244531539479403887",
    "rocket":  "5242361404173884147",
    "robot":   "5242741281146311218",
    "warn":    "5244738303499996306",
    "check":   "5244736662822490269",
    "globe":   "5244570443293169562",
    "bell":    "5242551190188760981",
    "star":    "5244628777538984321",
    # Набор 2 (новые)
    "hmm2":    "5244917511010423957",
    "shake":   "5244943791915307751",
    "fire":    "5244508634418810670",
    "hand":    "5242335234938148811",
    "target":  "5242421722694586441",
    "check2":  "5244732999215389039",
    "ok":      "5244685307898530090",
    "gift":    "5242531476288871394",
    "trophy":  "5242555253227822585",
    "lock":    "5244615707953503500",
    "search":  "5242702905613521577",
    "diamond": "5244590775668350292",
}
PE_FALLBACK = {
    "money":"💰","heart":"❤️","wave":"👋","cash":"💸",
    "wallet":"👛","hmm":"🤨","basket":"🧺","rocket":"🚀",
    "robot":"🤖","warn":"⚠️","check":"✅","globe":"🌐",
    "bell":"🔔","star":"⭐",
    "hmm2":"🤨","shake":"🤝","fire":"🤨","hand":"👇",
    "target":"🤨","check2":"✅","ok":"🤨","gift":"🏆",
    "trophy":"🏆","lock":"🔒","search":"🔎","diamond":"💎",
}
def em(key: str) -> str:
    eid = PE.get(key, PE["star"])
    fb  = PE_FALLBACK.get(key, "⭐")
    return f'<tg-emoji emoji-id="{eid}">{fb}</tg-emoji>'

IMG_USER  = "https://i.postimg.cc/Rhj1Z3zj/5359573969834547905.jpg"
IMG_ADMIN = "https://i.postimg.cc/Rhj1Z3zj/5359573969834547905.jpg"
