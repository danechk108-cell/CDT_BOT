import os

BOT_TOKEN    = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
OWNER_ID     = 8565986003
WEBAPP_URL   = os.getenv("WEBAPP_URL", "https://your-service.onrender.com")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cdtdf:RmqUhxcbM6UkQQmDQNLdzg9IeZCD29u0@dpg-d92l6b3tqb8s73e638cg-a.ohio-postgres.render.com/niomero"
)

REQUIRED_CHANNELS = [
    {"id": "@CodeTMG",          "url": "https://t.me/CodeTMG",          "title": "CodeTMG"},
    {"id": "@SuperStarsChanell","url": "https://t.me/SuperStarsChanell","title": "SuperStars"},
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

PAID_ROULETTE_PRICE  = 150
PRIZE_TRANSFER_DELAY = 7200  # 2 часа в секундах

# Premium Emoji IDs
PE = {
    "money":  "5244731629120820298",
    "heart":  "5242497898234550654",
    "wave":   "5244988141747606686",
    "cash":   "5244806842588108571",
    "wallet": "5244615046528538427",
    "hmm":    "5244866250575745199",
    "basket": "5244531539479403887",
    "rocket": "5242361404173884147",
    "robot":  "5242741281146311218",
    "warn":   "5244738303499996306",
    "check":  "5244736662822490269",
    "globe":  "5244570443293169562",
    "bell":   "5242551190188760981",
    "star":   "5244628777538984321",
}
PE_FALLBACK = {
    "money":"💰","heart":"❤️","wave":"👋","cash":"💸",
    "wallet":"👛","hmm":"🤨","basket":"🧺","rocket":"🚀",
    "robot":"🤖","warn":"⚠️","check":"✅","globe":"🌐",
    "bell":"🔔","star":"⭐",
}
def em(key: str) -> str:
    eid = PE.get(key, PE["star"])
    fb  = PE_FALLBACK.get(key, "⭐")
    return f'<tg-emoji emoji-id="{eid}">{fb}</tg-emoji>'

IMG_USER  = "https://i.postimg.cc/NMt62Q8t/flux-2-pro-a-Pomenaj-mad-max-na-F.jpg"
IMG_ADMIN = "https://i.postimg.cc/sgvK5LsP/image-39904039-706d-4dd6-9e75-c86001ecf24a.jpg"
