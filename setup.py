# setup_bot.py
# Запуск: python setup_bot.py

import os

def write(path, content):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ {path}")

# ══════════════════════════════════════════════════════════════════════════════
write("requirements.txt", """aiogram==3.7.0
asyncpg==0.29.0
fastapi==0.111.0
uvicorn==0.30.1
jinja2==3.1.4
python-multipart==0.0.9
aiofiles==23.2.1
""")

# ══════════════════════════════════════════════════════════════════════════════
write("render.yaml", """services:
  - type: web
    name: tank-blitz-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: BOT_TOKEN
        sync: false
      - key: WEBAPP_URL
        sync: false
      - key: DATABASE_URL
        value: postgresql://cdtdf:RmqUhxcbM6UkQQmDQNLdzg9IeZCD29u0@dpg-d92l6b3tqb8s73e638cg-a.ohio-postgres.render.com/niomero
    healthCheckPath: /health
""")

# ══════════════════════════════════════════════════════════════════════════════
write("config.py", """import os

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
IMG_ADMIN = "https://i.postimg.cc/tCbg0Yq7/flux-2-pro-a-%27%CC%B1eper%27-sntzu-dobav%27.jpg"
""")

# ══════════════════════════════════════════════════════════════════════════════
write("database.py", """import asyncpg
from datetime import datetime
from config import DATABASE_URL, OWNER_ID

pool = None


async def init_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    await _create_tables()


async def _create_tables():
    async with pool.acquire() as c:
        await c.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS users (
                id          BIGSERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username    TEXT,
                first_name  TEXT,
                last_name   TEXT,
                game_id     TEXT,
                balance     FLOAT   DEFAULT 0.0,
                is_blocked  BOOLEAN DEFAULT FALSE,
                created_at  TIMESTAMP DEFAULT NOW(),
                updated_at  TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS roulette_spins (
                id            BIGSERIAL PRIMARY KEY,
                user_id       BIGINT REFERENCES users(telegram_id),
                roulette_type TEXT NOT NULL,
                prize_name    TEXT,
                prize_type    TEXT,
                prize_value   FLOAT   DEFAULT 0,
                is_paid       BOOLEAN DEFAULT FALSE,
                spun_at       TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS prizes (
                id               BIGSERIAL PRIMARY KEY,
                user_id          BIGINT REFERENCES users(telegram_id),
                prize_type       TEXT NOT NULL,
                prize_name       TEXT,
                prize_value      FLOAT DEFAULT 0,
                account_email    TEXT,
                account_password TEXT,
                gold_promo       TEXT,
                is_received      BOOLEAN   DEFAULT FALSE,
                received_at      TIMESTAMP,
                won_at           TIMESTAMP DEFAULT NOW(),
                transferred_to   BIGINT,
                transferred_at   TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS accounts_pool (
                id       BIGSERIAL PRIMARY KEY,
                email    TEXT NOT NULL,
                password TEXT NOT NULL,
                is_used  BOOLEAN   DEFAULT FALSE,
                added_by BIGINT,
                added_at TIMESTAMP DEFAULT NOW(),
                used_at  TIMESTAMP,
                used_by  BIGINT
            );
            CREATE TABLE IF NOT EXISTS gold_pool (
                id         BIGSERIAL PRIMARY KEY,
                promo_code TEXT NOT NULL,
                is_used    BOOLEAN   DEFAULT FALSE,
                added_by   BIGINT,
                added_at   TIMESTAMP DEFAULT NOW(),
                used_at    TIMESTAMP,
                used_by    BIGINT
            );
            CREATE TABLE IF NOT EXISTS admins (
                id          BIGSERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username    TEXT,
                level       TEXT NOT NULL,
                added_by    BIGINT,
                added_at    TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS roulette_conditions (
                id            BIGSERIAL PRIMARY KEY,
                user_id       BIGINT REFERENCES users(telegram_id),
                roulette_type TEXT NOT NULL,
                is_subscribed BOOLEAN DEFAULT FALSE,
                is_forwarded  BOOLEAN DEFAULT FALSE,
                condition_met_at TIMESTAMP,
                UNIQUE(user_id, roulette_type)
            );
        \"\"\")
        await c.execute(\"\"\"
            INSERT INTO admins (telegram_id, username, level, added_by)
            VALUES ($1, 'owner', 'head', $1)
            ON CONFLICT (telegram_id) DO NOTHING
        \"\"\", OWNER_ID)


# ── users ──────────────────────────────────────────────────────────────────────

async def get_user(telegram_id):
    async with pool.acquire() as c:
        return await c.fetchrow("SELECT * FROM users WHERE telegram_id=$1", telegram_id)

async def create_user(telegram_id, username, first_name, last_name=None):
    async with pool.acquire() as c:
        return await c.fetchrow(\"\"\"
            INSERT INTO users (telegram_id,username,first_name,last_name)
            VALUES ($1,$2,$3,$4)
            ON CONFLICT (telegram_id) DO UPDATE
              SET username=$2,first_name=$3,last_name=$4,updated_at=NOW()
            RETURNING *
        \"\"\", telegram_id, username, first_name, last_name)

async def update_game_id(telegram_id, game_id):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE users SET game_id=$1,updated_at=NOW() WHERE telegram_id=$2",
            game_id, telegram_id)

async def update_balance(telegram_id, amount):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE users SET balance=balance+$1,updated_at=NOW() WHERE telegram_id=$2",
            amount, telegram_id)

async def block_user(telegram_id, blocked=True):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE users SET is_blocked=$1 WHERE telegram_id=$2",
            blocked, telegram_id)

async def get_all_users():
    async with pool.acquire() as c:
        return await c.fetch("SELECT * FROM users ORDER BY created_at DESC")


# ── spins ──────────────────────────────────────────────────────────────────────

async def get_last_spin(user_id, roulette_type):
    async with pool.acquire() as c:
        return await c.fetchrow(\"\"\"
            SELECT * FROM roulette_spins
            WHERE user_id=$1 AND roulette_type=$2
            ORDER BY spun_at DESC LIMIT 1
        \"\"\", user_id, roulette_type)

async def add_spin(user_id, roulette_type, prize_name, prize_type, prize_value, is_paid=False):
    async with pool.acquire() as c:
        return await c.fetchrow(\"\"\"
            INSERT INTO roulette_spins
              (user_id,roulette_type,prize_name,prize_type,prize_value,is_paid)
            VALUES ($1,$2,$3,$4,$5,$6) RETURNING *
        \"\"\", user_id, roulette_type, prize_name, prize_type, prize_value, is_paid)


# ── conditions ─────────────────────────────────────────────────────────────────

async def get_condition(user_id, roulette_type):
    async with pool.acquire() as c:
        return await c.fetchrow(
            "SELECT * FROM roulette_conditions WHERE user_id=$1 AND roulette_type=$2",
            user_id, roulette_type)

async def set_condition(user_id, roulette_type, subscribed, forwarded):
    met = datetime.now() if (subscribed and forwarded) else None
    async with pool.acquire() as c:
        await c.execute(\"\"\"
            INSERT INTO roulette_conditions
              (user_id,roulette_type,is_subscribed,is_forwarded,condition_met_at)
            VALUES ($1,$2,$3,$4,$5)
            ON CONFLICT (user_id,roulette_type) DO UPDATE
              SET is_subscribed=$3,is_forwarded=$4,condition_met_at=$5
        \"\"\", user_id, roulette_type, subscribed, forwarded, met)


# ── prizes ─────────────────────────────────────────────────────────────────────

async def add_prize(user_id, prize_type, prize_name, prize_value=0,
                    account_email=None, account_password=None, gold_promo=None):
    async with pool.acquire() as c:
        return await c.fetchrow(\"\"\"
            INSERT INTO prizes
              (user_id,prize_type,prize_name,prize_value,
               account_email,account_password,gold_promo)
            VALUES ($1,$2,$3,$4,$5,$6,$7) RETURNING *
        \"\"\", user_id, prize_type, prize_name, prize_value,
            account_email, account_password, gold_promo)

async def get_user_prizes(user_id):
    async with pool.acquire() as c:
        return await c.fetch(
            "SELECT * FROM prizes WHERE user_id=$1 ORDER BY won_at DESC", user_id)

async def get_prize(prize_id):
    async with pool.acquire() as c:
        return await c.fetchrow("SELECT * FROM prizes WHERE id=$1", prize_id)

async def remove_prize(prize_id):
    async with pool.acquire() as c:
        await c.execute("DELETE FROM prizes WHERE id=$1", prize_id)

async def mark_prize_received(prize_id):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE prizes SET is_received=TRUE,received_at=NOW() WHERE id=$1",
            prize_id)

async def transfer_prize(prize_id, to_user_id):
    async with pool.acquire() as c:
        await c.execute(\"\"\"
            UPDATE prizes
            SET user_id=$1,transferred_to=$1,transferred_at=NOW()
            WHERE id=$2
        \"\"\", to_user_id, prize_id)

async def get_prizes_stats():
    async with pool.acquire() as c:
        not_recv = await c.fetch(
            "SELECT * FROM prizes WHERE is_received=FALSE AND prize_type!='nothing'")
        recv = await c.fetch("SELECT * FROM prizes WHERE is_received=TRUE")
        return not_recv, recv


# ── accounts pool ──────────────────────────────────────────────────────────────

async def add_account(email, password, added_by):
    async with pool.acquire() as c:
        return await c.fetchrow(
            "INSERT INTO accounts_pool (email,password,added_by) VALUES ($1,$2,$3) RETURNING *",
            email, password, added_by)

async def get_free_account():
    async with pool.acquire() as c:
        return await c.fetchrow("SELECT * FROM accounts_pool WHERE is_used=FALSE LIMIT 1")

async def use_account(account_id, user_id):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE accounts_pool SET is_used=TRUE,used_at=NOW(),used_by=$1 WHERE id=$2",
            user_id, account_id)


# ── gold pool ──────────────────────────────────────────────────────────────────

async def add_gold_promo(promo, added_by):
    async with pool.acquire() as c:
        return await c.fetchrow(
            "INSERT INTO gold_pool (promo_code,added_by) VALUES ($1,$2) RETURNING *",
            promo, added_by)

async def get_free_gold():
    async with pool.acquire() as c:
        return await c.fetchrow("SELECT * FROM gold_pool WHERE is_used=FALSE LIMIT 1")

async def use_gold(gold_id, user_id):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE gold_pool SET is_used=TRUE,used_at=NOW(),used_by=$1 WHERE id=$2",
            user_id, gold_id)


# ── admins ─────────────────────────────────────────────────────────────────────

async def get_admin(telegram_id):
    async with pool.acquire() as c:
        return await c.fetchrow("SELECT * FROM admins WHERE telegram_id=$1", telegram_id)

async def get_all_admins():
    async with pool.acquire() as c:
        return await c.fetch("SELECT * FROM admins ORDER BY level DESC")

async def add_admin(telegram_id, username, level, added_by):
    async with pool.acquire() as c:
        await c.execute(\"\"\"
            INSERT INTO admins (telegram_id,username,level,added_by)
            VALUES ($1,$2,$3,$4)
            ON CONFLICT (telegram_id) DO UPDATE SET level=$3,username=$2
        \"\"\", telegram_id, username, level, added_by)

async def remove_admin(telegram_id):
    async with pool.acquire() as c:
        await c.execute("DELETE FROM admins WHERE telegram_id=$1", telegram_id)


# ── statistics ─────────────────────────────────────────────────────────────────

async def get_general_stats():
    async with pool.acquire() as c:
        return {
            "total_users":         await c.fetchval("SELECT COUNT(*) FROM users"),
            "total_spins":         await c.fetchval("SELECT COUNT(*) FROM roulette_spins"),
            "total_prizes":        await c.fetchval(
                "SELECT COUNT(*) FROM prizes WHERE prize_type!='nothing'"),
            "total_balance_given": float(await c.fetchval(
                "SELECT COALESCE(SUM(prize_value),0) FROM prizes WHERE prize_type='balance'")),
        }
""")

# ══════════════════════════════════════════════════════════════════════════════
write("utils/__init__.py", "")

write("utils/prizes.py", """import random
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
        f"  • {p['name']} — {p['chance']}%\\n"
        for p in PRIZES.get(t, []))
""")

write("utils/checks.py", """from config import REQUIRED_CHANNELS


async def check_subscriptions(bot, user_id: int):
    not_sub = []
    for ch in REQUIRED_CHANNELS:
        try:
            m = await bot.get_chat_member(ch["id"], user_id)
            if m.status in ("left", "kicked", "banned"):
                not_sub.append(ch)
        except Exception:
            not_sub.append(ch)
    return len(not_sub) == 0, not_sub
""")

# ══════════════════════════════════════════════════════════════════════════════
write("handlers/__init__.py", "")

# ══════════════════════════════════════════════════════════════════════════════
write("handlers/start.py", """from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import WEBAPP_URL, em, IMG_USER


router = Router()


class Reg(StatesGroup):
    game_id   = State()
    interface = State()


def _start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🌐 Web App",       callback_data="use_webapp"),
        InlineKeyboardButton(text="💬 Сообщения",     callback_data="use_messages"),
    ]])


def _webapp_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎰 Открыть рулетку",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/webapp"),
        )],
        [InlineKeyboardButton(text="💬 Через сообщения", callback_data="use_messages")],
    ])


@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    user = await db.get_user(msg.from_user.id)
    if not user:
        await db.create_user(
            msg.from_user.id, msg.from_user.username,
            msg.from_user.first_name, msg.from_user.last_name,
        )
        user = await db.get_user(msg.from_user.id)

    if user["is_blocked"]:
        return await msg.answer(
            f'{em("warn")} <b>Вы заблокированы в боте.</b>',
            parse_mode="HTML",
        )

    caption = (
        f'{em("wave")} <b>Привет, {msg.from_user.first_name}!</b>\\n\\n'
        f'{em("star")} Добро пожаловать в <b>Tank Blitz Roulette</b>!\\n'
        f'{em("rocket")} Крути рулетку — выигрывай призы!\\n\\n'
        f'{em("globe")} Выбери способ использования:'
    )
    await msg.answer_photo(
        photo=IMG_USER,
        caption=caption,
        reply_markup=_start_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "use_webapp")
async def use_webapp(cb: CallbackQuery, state: FSMContext):
    user = await db.get_user(cb.from_user.id)
    if not user.get("game_id"):
        await cb.message.edit_caption(
            caption=f'{em("rocket")} <b>Введите ваш Game ID в Tank Blitz:</b>',
            parse_mode="HTML",
        )
        await state.set_state(Reg.game_id)
        await state.update_data(interface="webapp")
    else:
        await cb.message.edit_caption(
            caption=f'{em("star")} <b>Открываю Web App...</b>',
            reply_markup=_webapp_kb(),
            parse_mode="HTML",
        )


@router.callback_query(F.data == "use_messages")
async def use_messages(cb: CallbackQuery, state: FSMContext):
    user = await db.get_user(cb.from_user.id)
    if not user.get("game_id"):
        await cb.message.edit_caption(
            caption=f'{em("rocket")} <b>Введите ваш Game ID в Tank Blitz:</b>',
            parse_mode="HTML",
        )
        await state.set_state(Reg.game_id)
        await state.update_data(interface="messages")
    else:
        from handlers.roulette import main_menu_kb
        await cb.message.edit_caption(
            caption=f'{em("star")} <b>Главное меню</b>',
            reply_markup=main_menu_kb(),
            parse_mode="HTML",
        )


@router.message(Reg.game_id)
async def process_game_id(msg: Message, state: FSMContext):
    gid = msg.text.strip()
    if len(gid) < 3:
        return await msg.answer_photo(
            photo=IMG_USER,
            caption=f'{em("warn")} <b>Некорректный ID!</b> Введите снова:',
            parse_mode="HTML",
        )
    await db.update_game_id(msg.from_user.id, gid)
    data = await state.get_data()
    await state.clear()

    if data.get("interface") == "webapp":
        from handlers.start import _webapp_kb
        await msg.answer_photo(
            photo=IMG_USER,
            caption=(
                f'{em("check")} ID <code>{gid}</code> сохранён!\\n'
                f'{em("rocket")} Открывайте Web App:'
            ),
            reply_markup=_webapp_kb(),
            parse_mode="HTML",
        )
    else:
        from handlers.roulette import main_menu_kb
        await msg.answer_photo(
            photo=IMG_USER,
            caption=(
                f'{em("check")} ID <code>{gid}</code> сохранён!\\n'
                f'{em("star")} <b>Главное меню</b>'
            ),
            reply_markup=main_menu_kb(),
            parse_mode="HTML",
        )
""")

# ══════════════════════════════════════════════════════════════════════════════
write("handlers/roulette.py", """import asyncio
import re
from datetime import datetime, timedelta

from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

import database as db
from config import COOLDOWNS, PAID_ROULETTE_PRICE, PRIZE_TRANSFER_DELAY, em, IMG_USER
from utils.prizes import spin_roulette, get_roulette_name, get_roulette_emoji, format_prize_list
from utils.checks import check_subscriptions

router = Router()


# ── keyboards ──────────────────────────────────────────────────────────────────

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎰 Рулетка", callback_data="menu_roulette"),
            InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile"),
        ],
        [
            InlineKeyboardButton(text="🏆 Лидеры",  callback_data="menu_leaders"),
            InlineKeyboardButton(text="❓ Помощь",   callback_data="menu_help"),
        ],
    ])


def roulette_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Ежедневная",      callback_data="rt_day")],
        [InlineKeyboardButton(text="🎲 Каждые 3 дня",    callback_data="rt_three_days")],
        [InlineKeyboardButton(text="🏆 Еженедельная",     callback_data="rt_week")],
        [InlineKeyboardButton(text="💎 Платная · 150₽",  callback_data="rt_paid")],
        [InlineKeyboardButton(text="◀️ Назад",            callback_data="back_main")],
    ])


def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 К рулеткам", callback_data="menu_roulette")],
        [InlineKeyboardButton(text="🏠 Меню",        callback_data="back_main")],
    ])


# ── helpers ────────────────────────────────────────────────────────────────────

def _fmt(s: int) -> str:
    h, m = s // 3600, (s % 3600) // 60
    return f"{h}ч {m}м" if h else f"{m}м {s % 60}с" if m else f"{s}с"


async def _cooldown(uid: int, rt: str):
    ls = await db.get_last_spin(uid, rt)
    if not ls:
        return True, 0
    nxt  = ls["spun_at"] + timedelta(seconds=COOLDOWNS.get(rt, 86400))
    left = int((nxt - datetime.now()).total_seconds())
    return left <= 0, max(left, 0)


async def _notify_admins(bot: Bot, uid: int, prize_name: str):
    user = await db.get_user(uid)
    who  = f"@{user['username']}" if user.get("username") else str(uid)
    txt  = (
        f'{em("bell")} <b>Выдан приз!</b>\\n\\n'
        f'👤 {who}\\n'
        f'{em("star")} <b>{prize_name}</b>'
    )
    for a in await db.get_all_admins():
        try:
            await bot.send_message(a["telegram_id"], txt, parse_mode="HTML")
        except Exception:
            pass


async def _apply(uid: int, prize: dict, bot: Bot) -> str:
    t = prize["type"]

    # ── баланс ────────────────────────────────────────────────────────────────
    if t == "balance":
        await db.update_balance(uid, prize["value"])
        await db.add_prize(uid, "balance", prize["name"], prize["value"])
        await _notify_admins(bot, uid, prize["name"])
        try:
            await bot.send_message(
                uid,
                f'{em("money")} На баланс зачислено <b>{prize["value"]}₽</b>!',
                parse_mode="HTML",
            )
        except Exception:
            pass
        return f'{em("money")} <b>{prize["value"]}₽</b> зачислено на баланс!'

    # ── аккаунт ───────────────────────────────────────────────────────────────
    if t == "account":
        acc = await db.get_free_account()
        if acc:
            await db.use_account(acc["id"], uid)
            rec = await db.add_prize(
                uid, "account", prize["name"],
                account_email=acc["email"],
                account_password=acc["password"],
            )
            await _notify_admins(bot, uid, prize["name"])
            pid = rec["id"]
            kb  = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="📥 Получить данные",
                    callback_data=f"receive_prize_{pid}",
                ),
                InlineKeyboardButton(
                    text="📤 Передать (через 2ч)",
                    callback_data=f"transfer_init_{pid}",
                ),
            ]])
            try:
                await bot.send_photo(
                    uid,
                    photo=IMG_USER,
                    caption=(
                        f'{em("robot")} <b>Вы выиграли аккаунт Tank Blitz!</b>\\n\\n'
                        f'Нажмите <b>Получить</b> — узнаете данные прямо сейчас.\\n'
                        f'Или <b>Передать</b> другому игроку (доступно через 2 часа).'
                    ),
                    reply_markup=kb,
                    parse_mode="HTML",
                )
            except Exception:
                pass
            return f'{em("robot")} Аккаунт выигран! Проверьте сообщения.'
        await db.update_balance(uid, 50)
        return f'{em("robot")} Аккаунтов нет. Начислено 50₽ компенсации.'

    # ── голда ─────────────────────────────────────────────────────────────────
    if t == "gold":
        g = await db.get_free_gold()
        if g:
            await db.use_gold(g["id"], uid)
            rec = await db.add_prize(
                uid, "gold", prize["name"],
                gold_promo=g["promo_code"],
            )
            await _notify_admins(bot, uid, prize["name"])
            pid = rec["id"]
            kb  = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="🥇 Получить промокод",
                    callback_data=f"receive_prize_{pid}",
                ),
                InlineKeyboardButton(
                    text="📤 Передать (через 2ч)",
                    callback_data=f"transfer_init_{pid}",
                ),
            ]])
            try:
                await bot.send_photo(
                    uid,
                    photo=IMG_USER,
                    caption=(
                        f'{em("star")} <b>Вы выиграли Голду Tank Blitz!</b>\\n\\n'
                        f'Нажмите <b>Получить</b> — получите промокод сейчас.\\n'
                        f'Или <b>Передать</b> другому игроку (доступно через 2 часа).'
                    ),
                    reply_markup=kb,
                    parse_mode="HTML",
                )
            except Exception:
                pass
            return f'{em("star")} Голда выиграна! Проверьте сообщения.'
        await db.update_balance(uid, 25)
        return f'{em("star")} Промокодов нет. Начислено 25₽ компенсации.'

    return ""


# ── receive prize ──────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("receive_prize_"))
async def receive_prize(cb: CallbackQuery, bot: Bot):
    pid   = int(cb.data.replace("receive_prize_", ""))
    prize = await db.get_prize(pid)

    if not prize or prize["user_id"] != cb.from_user.id:
        return await cb.answer("❌ Приз не найден!", show_alert=True)
    if prize["is_received"]:
        return await cb.answer("✅ Приз уже получен!", show_alert=True)

    await db.mark_prize_received(pid)
    await cb.message.edit_reply_markup(reply_markup=None)

    if prize["prize_type"] == "account":
        txt = (
            f'{em("robot")} <b>Данные аккаунта Tank Blitz</b>\\n\\n'
            f'📧 Email: <code>{prize["account_email"]}</code>\\n'
            f'🔑 Пароль: <code>{prize["account_password"]}</code>\\n\\n'
            f'{em("warn")} Сразу смените пароль!'
        )
    elif prize["prize_type"] == "gold":
        txt = (
            f'{em("star")} <b>Промокод на Голду Tank Blitz</b>\\n\\n'
            f'🎟️ Код: <code>{prize["gold_promo"]}</code>\\n\\n'
            f'Введите промокод в игре!'
        )
    else:
        txt = f'{em("check")} Приз получен: <b>{prize["prize_name"]}</b>'

    try:
        await bot.send_photo(
            cb.from_user.id,
            photo=IMG_USER,
            caption=txt,
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer("✅ Данные отправлены!", show_alert=True)

    for a in await db.get_all_admins():
        try:
            await bot.send_message(
                a["telegram_id"],
                f'{em("bell")} Приз получен\\n👤 {cb.from_user.id}\\n{prize["prize_name"]}',
                parse_mode="HTML",
            )
        except Exception:
            pass


# ── transfer init ──────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("transfer_init_"))
async def transfer_init(cb: CallbackQuery):
    pid   = int(cb.data.replace("transfer_init_", ""))
    prize = await db.get_prize(pid)

    if not prize or prize["user_id"] != cb.from_user.id:
        return await cb.answer("❌ Приз не найден!", show_alert=True)
    if prize["is_received"]:
        return await cb.answer("❌ Приз уже получен — передача невозможна!", show_alert=True)

    elapsed = (datetime.now() - prize["won_at"]).total_seconds()
    if elapsed < PRIZE_TRANSFER_DELAY:
        left = int(PRIZE_TRANSFER_DELAY - elapsed)
        h, m = left // 3600, (left % 3600) // 60
        return await cb.answer(
            f"⏳ Передача будет доступна через {h}ч {m}м",
            show_alert=True,
        )

    await cb.message.edit_caption(
        caption=(
            f'{em("rocket")} <b>Передача приза</b>\\n\\n'
            f'Приз: <b>{prize["prize_name"]}</b>\\n\\n'
            f'Отправьте команду:\\n'
            f'<code>/transfer_{pid}_@username</code>\\n\\n'
            f'Или укажите Telegram ID:\\n'
            f'<code>/transfer_{pid}_123456789</code>'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="menu_profile")]
        ]),
        parse_mode="HTML",
    )


@router.message(F.text.regexp(r"^/transfer_(\d+)_@?(\S+)$"))
async def do_transfer_cmd(msg: Message, bot: Bot):
    m      = re.match(r"^/transfer_(\d+)_@?(\S+)$", msg.text)
    pid    = int(m.group(1))
    target = m.group(2)
    prize  = await db.get_prize(pid)

    if not prize or prize["user_id"] != msg.from_user.id:
        return await msg.answer(f'{em("warn")} Приз не найден!', parse_mode="HTML")
    if prize["is_received"]:
        return await msg.answer(f'{em("warn")} Приз уже получен!', parse_mode="HTML")

    elapsed = (datetime.now() - prize["won_at"]).total_seconds()
    if elapsed < PRIZE_TRANSFER_DELAY:
        left = int(PRIZE_TRANSFER_DELAY - elapsed)
        h, m2 = left // 3600, (left % 3600) // 60
        return await msg.answer(
            f'{em("warn")} Подождите ещё <b>{h}ч {m2}м</b>',
            parse_mode="HTML",
        )

    all_u  = await db.get_all_users()
    to_usr = next(
        (u for u in all_u
         if str(u["telegram_id"]) == target
         or u.get("username", "").lower() == target.lower()),
        None,
    )
    if not to_usr:
        return await msg.answer(
            f'{em("warn")} Пользователь не найден! Убедитесь что он запускал бота.',
            parse_mode="HTML",
        )

    await db.transfer_prize(pid, to_usr["telegram_id"])

    # Уведомление получателю
    try:
        await bot.send_photo(
            to_usr["telegram_id"],
            photo=IMG_USER,
            caption=(
                f'{em("star")} <b>Вам передан приз!</b>\\n\\n'
                f'От: @{msg.from_user.username or msg.from_user.id}\\n'
                f'Приз: <b>{prize["prize_name"]}</b>'
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass

    # Уведомление администраторам
    for a in await db.get_all_admins():
        try:
            await bot.send_message(
                a["telegram_id"],
                f'{em("bell")} Передача приза\\n'
                f'От: {msg.from_user.id} → {to_usr["telegram_id"]}\\n'
                f'{prize["prize_name"]}',
                parse_mode="HTML",
            )
        except Exception:
            pass

    await msg.answer_photo(
        photo=IMG_USER,
        caption=(
            f'{em("check")} <b>Приз передан!</b>\\n\\n'
            f'<b>{prize["prize_name"]}</b> отправлен игроку '
            f'@{to_usr.get("username") or to_usr["telegram_id"]}'
        ),
        parse_mode="HTML",
    )


# ── navigation ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "back_main")
async def back_main(cb: CallbackQuery):
    await cb.message.edit_caption(
        caption=f'{em("rocket")} <b>Главное меню Tank Blitz Roulette</b>',
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "menu_roulette")
async def menu_roulette(cb: CallbackQuery):
    u   = await db.get_user(cb.from_user.id)
    bal = float(u["balance"]) if u else 0
    await cb.message.edit_caption(
        caption=(
            f'{em("star")} <b>Выберите тип рулетки</b>\\n\\n'
            f'{em("money")} Баланс: <b>{bal:.2f}₽</b>\\n\\n'
            f'🎯 Ежедневная  •  🎲 3 дня\\n'
            f'🏆 Неделя  •  💎 Платная'
        ),
        reply_markup=roulette_menu_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "menu_help")
async def menu_help(cb: CallbackQuery):
    await cb.message.edit_caption(
        caption=(
            f'{em("globe")} <b>Помощь</b>\\n\\n'
            f'<b>Бесплатная рулетка:</b>\\n'
            f'• Подписаться на 2 канала\\n'
            f'• Переслать сообщение 3 пользователям\\n\\n'
            f'<b>Платная рулетка:</b> 150₽ за прокрут\\n\\n'
            f'<b>Передача приза:</b> через 2 часа после выигрыша\\n\\n'
            f'📞 Поддержка: @CodeTMG'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "menu_leaders")
async def menu_leaders(cb: CallbackQuery):
    users  = sorted(await db.get_all_users(), key=lambda u: u["balance"], reverse=True)[:10]
    medals = ["🥇", "🥈", "🥉"]
    lines  = "\\n".join(
        f"{medals[i] if i < 3 else str(i + 1) + '.'} "
        f"<b>{u['first_name'] or u['username'] or 'Игрок'}</b> — {u['balance']:.2f}₽"
        for i, u in enumerate(users)
    )
    await cb.message.edit_caption(
        caption=f'{em("star")} <b>Топ игроков</b>\\n\\n{lines or "Пока никого нет"}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
        ]),
        parse_mode="HTML",
    )


# ── roulette types ─────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("rt_"))
async def choose_roulette(cb: CallbackQuery, bot: Bot):
    rt  = cb.data[3:]
    uid = cb.from_user.id
    u   = await db.get_user(uid)

    if not u or u["is_blocked"]:
        return await cb.answer("❌ Доступ запрещён", show_alert=True)

    # Платная рулетка
    if rt == "paid":
        bal = float(u["balance"])
        can = bal >= PAID_ROULETTE_PRICE
        kb  = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="💎 Крутить за 150₽" if can else "💳 Пополнить баланс",
                callback_data="paid_confirm" if can else "topup",
            )],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_roulette")],
        ])
        await cb.message.edit_caption(
            caption=(
                f'{em("star")} <b>Платная рулетка</b>\\n\\n'
                f'{em("money")} Баланс: <b>{bal:.2f}₽</b> / нужно <b>150₽</b>\\n\\n'
                f'🎁 Призы:\\n{format_prize_list("paid")}'
            ),
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    # Бесплатные рулетки
    can_spin, left = await _cooldown(uid, rt)
    prizes_txt     = format_prize_list(rt)
    name           = get_roulette_name(rt)
    ico            = get_roulette_emoji(rt)

    if not can_spin:
        return await cb.message.edit_caption(
            caption=(
                f'{ico} <b>{name}</b>\\n\\n'
                f'⏳ Следующий прокрут через: <b>{_fmt(left)}</b>\\n\\n'
                f'🎁 Призы:\\n{prizes_txt}'
            ),
            reply_markup=back_kb(),
            parse_mode="HTML",
        )

    cond    = await db.get_condition(uid, rt)
    ok, not_sub = await check_subscriptions(bot, uid)
    cond_ok = ok and bool(cond and cond["is_forwarded"])

    if not cond_ok:
        ch_btns = [
            [InlineKeyboardButton(text=f"📢 {ch['title']}", url=ch["url"])]
            for ch in not_sub
        ]
        ch_btns += [
            [InlineKeyboardButton(text="✅ Проверить подписку", callback_data=f"chk_{rt}")],
            [InlineKeyboardButton(text="◀️ Назад",              callback_data="menu_roulette")],
        ]
        fs = "✅" if ok else "❌"
        ff = "✅" if (cond and cond["is_forwarded"]) else "❌"
        return await cb.message.edit_caption(
            caption=(
                f'{ico} <b>{name}</b>\\n\\n'
                f'📋 <b>Выполните условия для прокрута:</b>\\n\\n'
                f'{fs} Подписаться на каналы\\n'
                f'{ff} Переслать сообщение 3 пользователям\\n\\n'
                f'🎁 Призы:\\n{prizes_txt}'
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=ch_btns),
            parse_mode="HTML",
        )

    await cb.message.edit_caption(
        caption=(
            f'{ico} <b>{name}</b>\\n\\n'
            f'✅ Все условия выполнены!\\n\\n'
            f'🎁 Призы:\\n{prizes_txt}'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎰 КРУТИТЬ!", callback_data=f"spin_{rt}")],
            [InlineKeyboardButton(text="◀️ Назад",   callback_data="menu_roulette")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("chk_"))
async def check_sub(cb: CallbackQuery, bot: Bot):
    rt  = cb.data[4:]
    uid = cb.from_user.id
    ok, not_sub = await check_subscriptions(bot, uid)

    if not ok:
        return await cb.answer(
            "❌ Не подписаны:\\n" + "\\n".join(ch["title"] for ch in not_sub),
            show_alert=True,
        )

    cond = await db.get_condition(uid, rt)
    fwd  = bool(cond and cond["is_forwarded"])
    await db.set_condition(uid, rt, True, fwd)

    if not fwd:
        return await cb.message.edit_caption(
            caption=(
                f'{em("check")} <b>Подписка подтверждена!</b>\\n\\n'
                f'Теперь перешли это сообщение 3 пользователям и нажми кнопку:'
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Переслал(а)!", callback_data=f"fwd_{rt}")],
                [InlineKeyboardButton(text="◀️ Назад",        callback_data="menu_roulette")],
            ]),
            parse_mode="HTML",
        )

    await cb.message.edit_caption(
        caption=f'{em("check")} <b>Все условия выполнены!</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎰 КРУТИТЬ!", callback_data=f"spin_{rt}")],
            [InlineKeyboardButton(text="◀️ Назад",   callback_data="menu_roulette")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("fwd_"))
async def confirm_fwd(cb: CallbackQuery):
    rt   = cb.data[4:]
    uid  = cb.from_user.id
    cond = await db.get_condition(uid, rt)
    sub  = bool(cond and cond["is_subscribed"])
    await db.set_condition(uid, rt, sub, True)

    if not sub:
        return await cb.answer("❌ Сначала подпишитесь на каналы!", show_alert=True)

    await cb.message.edit_caption(
        caption=f'{em("check")} <b>Все условия выполнены! Жми крутить:</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎰 КРУТИТЬ!", callback_data=f"spin_{rt}")],
            [InlineKeyboardButton(text="◀️ Назад",   callback_data="menu_roulette")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("spin_"))
async def do_spin(cb: CallbackQuery, bot: Bot):
    rt  = cb.data[5:]
    uid = cb.from_user.id

    can, left = await _cooldown(uid, rt)
    if not can:
        return await cb.answer(f"⏳ Через {_fmt(left)}", show_alert=True)

    cond = await db.get_condition(uid, rt)
    ok, _ = await check_subscriptions(bot, uid)
    if not ok or not cond or not cond["is_forwarded"]:
        return await cb.answer("❌ Условия не выполнены!", show_alert=True)

    await cb.message.edit_caption(
        caption=f'{em("rocket")} <b>Крутим рулетку...</b>',
        parse_mode="HTML",
    )
    await asyncio.sleep(2)

    prize = spin_roulette(rt)
    await db.add_spin(uid, rt, prize["name"], prize["type"], prize["value"])
    await db.set_condition(uid, rt, False, False)
    msg_txt = await _apply(uid, prize, bot)

    nxt = datetime.now() + timedelta(seconds=COOLDOWNS.get(rt, 86400))

    if prize["type"] == "nothing":
        caption = (
            f'😔 <b>Не повезло в этот раз!</b>\\n\\n'
            f'Попробуй ещё раз позже.\\n\\n'
            f'⏰ Следующий: <b>{nxt.strftime("%d.%m %H:%M")}</b>'
        )
    else:
        caption = (
            f'🎉 <b>Поздравляем!</b>\\n\\n'
            f'Вы выиграли: <b>{prize["name"]}</b>\\n'
            f'{msg_txt}\\n\\n'
            f'⏰ Следующий: <b>{nxt.strftime("%d.%m %H:%M")}</b>'
        )

    await cb.message.edit_caption(
        caption=caption,
        reply_markup=back_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "paid_confirm")
async def paid_confirm(cb: CallbackQuery):
    await cb.message.edit_caption(
        caption=f'{em("warn")} Потратить <b>150₽</b> на прокрут?',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Да, крутить!", callback_data="spin_paid"),
            InlineKeyboardButton(text="❌ Отмена",       callback_data="rt_paid"),
        ]]),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "topup")
async def topup(cb: CallbackQuery):
    await cb.message.edit_caption(
        caption=(
            f'{em("money")} <b>Пополнение баланса</b>\\n\\n'
            f'Обратитесь к администратору: @CodeTMG'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "spin_paid")
async def spin_paid(cb: CallbackQuery, bot: Bot):
    uid = cb.from_user.id
    u   = await db.get_user(uid)

    if float(u["balance"]) < PAID_ROULETTE_PRICE:
        return await cb.answer("❌ Недостаточно средств!", show_alert=True)

    await db.update_balance(uid, -PAID_ROULETTE_PRICE)
    await cb.message.edit_caption(
        caption=f'{em("rocket")} <b>Крутим платную рулетку...</b>',
        parse_mode="HTML",
    )
    await asyncio.sleep(2)

    prize   = spin_roulette("paid")
    await db.add_spin(uid, "paid", prize["name"], prize["type"], prize["value"], is_paid=True)
    msg_txt = await _apply(uid, prize, bot)
    uu      = await db.get_user(uid)

    await cb.message.edit_caption(
        caption=(
            f'🎉 <b>{prize["name"]}</b>\\n'
            f'{msg_txt}\\n\\n'
            f'{em("money")} Баланс: <b>{uu["balance"]:.2f}₽</b>'
        ),
        reply_markup=back_kb(),
        parse_mode="HTML",
    )
""")

# ══════════════════════════════════════════════════════════════════════════════
write("handlers/profile.py", """from datetime import datetime, timedelta

from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery, Message,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import PRIZE_TRANSFER_DELAY, em, IMG_USER

router = Router()


class ProfState(StatesGroup):
    new_game_id = State()


def _profile_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить Game ID", callback_data="prof_change_id")],
        [InlineKeyboardButton(text="🎁 Мои призы",        callback_data="prof_prizes")],
        [InlineKeyboardButton(text="◀️ Назад",             callback_data="back_main")],
    ])


@router.callback_query(F.data == "menu_profile")
async def show_profile(cb: CallbackQuery):
    u  = await db.get_user(cb.from_user.id)
    tg = cb.from_user
    un = f"@{tg.username}" if tg.username else "—"

    await cb.message.edit_caption(
        caption=(
            f'━━━━━━━━━━━━━━━━━\\n'
            f'       👤 <b>ПРОФИЛЬ</b>\\n'
            f'━━━━━━━━━━━━━━━━━\\n\\n'
            f'       🎮 <b>{u.get("game_id", "Не указан")}</b>\\n\\n'
            f'━━━━━━━━━━━━━━━━━\\n\\n'
            f'📛 Имя: <b>{tg.first_name}</b>\\n'
            f'🔗 Username: <b>{un}</b>\\n'
            f'🆔 ID: <code>{tg.id}</code>\\n'
            f'{em("money")} Баланс: <b>{u["balance"]:.2f}₽</b>\\n'
            f'📅 В боте с: <b>{u["created_at"].strftime("%d.%m.%Y")}</b>\\n\\n'
            f'━━━━━━━━━━━━━━━━━'
        ),
        reply_markup=_profile_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "prof_change_id")
async def change_id_start(cb: CallbackQuery, state: FSMContext):
    u = await db.get_user(cb.from_user.id)
    await cb.message.edit_caption(
        caption=(
            f'✏️ Текущий ID: <code>{u.get("game_id", "—")}</code>\\n\\n'
            f'Введите новый Game ID:'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="menu_profile")]
        ]),
        parse_mode="HTML",
    )
    await state.set_state(ProfState.new_game_id)


@router.message(ProfState.new_game_id)
async def save_new_id(msg: Message, state: FSMContext):
    nid = msg.text.strip()
    if len(nid) < 3:
        return await msg.answer_photo(
            photo=IMG_USER,
            caption=f'{em("warn")} Некорректный ID. Попробуйте снова:',
            parse_mode="HTML",
        )
    await db.update_game_id(msg.from_user.id, nid)
    await state.clear()
    await msg.answer_photo(
        photo=IMG_USER,
        caption=f'{em("check")} Game ID обновлён: <code>{nid}</code>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile")]
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "prof_prizes")
async def show_prizes(cb: CallbackQuery):
    prizes = await db.get_user_prizes(cb.from_user.id)

    if not prizes:
        return await cb.message.edit_caption(
            caption=(
                f'{em("star")} <b>Призов пока нет</b>\\n\\n'
                f'Крутите рулетку и выигрывайте!'
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎰 Рулетка", callback_data="menu_roulette")],
                [InlineKeyboardButton(text="◀️ Назад",   callback_data="menu_profile")],
            ]),
            parse_mode="HTML",
        )

    now = datetime.now()
    kb  = []
    txt = f'{em("star")} <b>Ваши призы:</b>\\n\\n'

    for p in prizes[:10]:
        st   = "✅" if p["is_received"] else "🎁"
        txt += f"{st} {p['prize_name']} — {p['won_at'].strftime('%d.%m')}\\n"
        can  = (
            not p["is_received"]
            and p["prize_type"] != "nothing"
            and now - p["won_at"] >= timedelta(seconds=PRIZE_TRANSFER_DELAY)
        )
        if can:
            kb.append([InlineKeyboardButton(
                text=f"📤 Передать: {p['prize_name'][:20]}",
                callback_data=f"tr_{p['id']}",
            )])

    kb.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu_profile")])
    await cb.message.edit_caption(
        caption=txt,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("tr_"))
async def transfer_start(cb: CallbackQuery):
    pid   = int(cb.data[3:])
    prize = await db.get_prize(pid)

    if not prize or prize["user_id"] != cb.from_user.id:
        return await cb.answer("❌ Приз не найден!", show_alert=True)

    now     = datetime.now()
    elapsed = (now - prize["won_at"]).total_seconds()

    if elapsed < PRIZE_TRANSFER_DELAY:
        left = int(PRIZE_TRANSFER_DELAY - elapsed)
        h, m = left // 3600, (left % 3600) // 60
        return await cb.answer(
            f"⏳ Передача доступна через {h}ч {m}м",
            show_alert=True,
        )

    await cb.message.edit_caption(
        caption=(
            f'{em("rocket")} <b>Передача приза</b>\\n\\n'
            f'Приз: <b>{prize["prize_name"]}</b>\\n\\n'
            f'Отправьте команду:\\n'
            f'<code>/transfer_{pid}_@username</code>\\n\\n'
            f'Или через Telegram ID:\\n'
            f'<code>/transfer_{pid}_123456789</code>'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="prof_prizes")]
        ]),
        parse_mode="HTML",
    )
""")

# ══════════════════════════════════════════════════════════════════════════════
write("handlers/admin.py", """from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import OWNER_ID, em, IMG_ADMIN, IMG_USER

router = Router()

LEVELS      = {"youtuber": 1, "admin": 2, "head": 3}
LEVEL_NAMES = {"youtuber": "🎬 Ютубер", "admin": "⚙️ Админ", "head": "👑 Глава"}


async def is_adm(uid: int, min_level: str = "youtuber") -> bool:
    if uid == OWNER_ID:
        return True
    a = await db.get_admin(uid)
    return bool(a and LEVELS.get(a["level"], 0) >= LEVELS.get(min_level, 1))


async def adm_level(uid: int) -> str | None:
    if uid == OWNER_ID:
        return "head"
    a = await db.get_admin(uid)
    return a["level"] if a else None


def _main_kb(is_head: bool = False):
    rows = [
        [InlineKeyboardButton(text="🎁 Управление призами",        callback_data="adm_prizes")],
        [InlineKeyboardButton(text="👥 Управление пользователями", callback_data="adm_users")],
        [InlineKeyboardButton(text="📊 Статистика",                callback_data="adm_stats")],
    ]
    if is_head:
        rows.append([InlineKeyboardButton(
            text="🛡️ Администраторы",
            callback_data="adm_admins",
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


class Adm(StatesGroup):
    acc_email   = State()
    acc_pass    = State()
    gold_promo  = State()
    bal_amount  = State()
    give_acc_em = State()
    give_acc_pw = State()
    give_gold   = State()
    new_adm_id  = State()
    new_adm_lvl = State()


# ── entry ──────────────────────────────────────────────────────────────────────

@router.message(Command("cdta"))
async def admin_panel(msg: Message):
    if not await is_adm(msg.from_user.id):
        return await msg.answer(
            f'{em("warn")} <b>Нет доступа к панели.</b>',
            parse_mode="HTML",
        )
    lvl     = await adm_level(msg.from_user.id)
    is_head = lvl == "head"
    await msg.answer_photo(
        photo=IMG_ADMIN,
        caption=(
            f'{em("rocket")} <b>Панель администратора</b>\\n\\n'
            f'Уровень: <b>{LEVEL_NAMES.get(lvl, lvl)}</b>\\n'
            f'ID: <code>{msg.from_user.id}</code>'
        ),
        reply_markup=_main_kb(is_head),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_back_main")
async def adm_back(cb: CallbackQuery):
    lvl     = await adm_level(cb.from_user.id)
    is_head = lvl == "head"
    await cb.message.edit_caption(
        caption=(
            f'{em("rocket")} <b>Панель администратора</b>\\n\\n'
            f'Уровень: <b>{LEVEL_NAMES.get(lvl, lvl)}</b>'
        ),
        reply_markup=_main_kb(is_head),
        parse_mode="HTML",
    )


# ── prizes ─────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_prizes")
async def adm_prizes(cb: CallbackQuery):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌ Нет прав!", show_alert=True)
    await cb.message.edit_caption(
        caption=f'{em("star")} <b>Управление призами</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить аккаунт",       callback_data="adm_add_acc")],
            [InlineKeyboardButton(text="🥇 Добавить промокод голды", callback_data="adm_add_gold")],
            [InlineKeyboardButton(text="◀️ Назад",                   callback_data="adm_back_main")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_add_acc")
async def adm_add_acc(cb: CallbackQuery, state: FSMContext):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌", show_alert=True)
    await cb.message.edit_caption(
        caption='📧 Введите <b>email</b> аккаунта:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="adm_prizes")]
        ]),
        parse_mode="HTML",
    )
    await state.set_state(Adm.acc_email)


@router.message(Adm.acc_email)
async def s_acc_email(msg: Message, state: FSMContext):
    await state.update_data(email=msg.text.strip())
    await msg.answer('🔑 Введите <b>пароль</b> аккаунта:', parse_mode="HTML")
    await state.set_state(Adm.acc_pass)


@router.message(Adm.acc_pass)
async def s_acc_pass(msg: Message, state: FSMContext):
    d = await state.get_data()
    await db.add_account(d["email"], msg.text.strip(), msg.from_user.id)
    await state.clear()
    await msg.answer_photo(
        photo=IMG_ADMIN,
        caption=(
            f'{em("check")} <b>Аккаунт добавлен!</b>\\n\\n'
            f'📧 {d["email"]}'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Ещё",   callback_data="adm_add_acc")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adm_prizes")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_add_gold")
async def adm_add_gold(cb: CallbackQuery, state: FSMContext):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌", show_alert=True)
    await cb.message.edit_caption(
        caption='🥇 Отправьте <b>промокод</b> на голду:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="adm_prizes")]
        ]),
        parse_mode="HTML",
    )
    await state.set_state(Adm.gold_promo)


@router.message(Adm.gold_promo)
async def s_gold(msg: Message, state: FSMContext):
    await db.add_gold_promo(msg.text.strip(), msg.from_user.id)
    await state.clear()
    await msg.answer_photo(
        photo=IMG_ADMIN,
        caption=f'{em("check")} Промокод <code>{msg.text.strip()}</code> добавлен!',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Ещё",   callback_data="adm_add_gold")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adm_prizes")],
        ]),
        parse_mode="HTML",
    )


# ── users ──────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_users")
async def adm_users(cb: CallbackQuery):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌", show_alert=True)
    users = await db.get_all_users()
    kb    = []
    for u in users[:20]:
        name = f"@{u['username']}" if u.get("username") else u.get("first_name", "?")
        kb.append([InlineKeyboardButton(
            text=f"{name} — {u['balance']:.1f}₽",
            callback_data=f"adm_u_{u['telegram_id']}",
        )])
    kb.append([InlineKeyboardButton(text="◀️ Назад", callback_data="adm_back_main")])
    await cb.message.edit_caption(
        caption=f'{em("globe")} <b>Пользователи</b> ({len(users)}):',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_u_"))
async def adm_user(cb: CallbackQuery):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌", show_alert=True)
    uid = int(cb.data[6:])
    u   = await db.get_user(uid)
    if not u:
        return await cb.answer("Не найден!", show_alert=True)
    name   = u.get("username") or u.get("first_name", "?")
    status = "🔴 Заблокирован" if u["is_blocked"] else "🟢 Активен"
    await cb.message.edit_caption(
        caption=(
            f'👤 <b>@{name}</b>\\n'
            f'🆔 <code>{uid}</code>\\n'
            f'🎮 Game ID: <code>{u.get("game_id", "—")}</code>\\n'
            f'{em("money")} Баланс: <b>{u["balance"]:.2f}₽</b>\\n'
            f'📊 Статус: {status}'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Баланс", callback_data=f"adm_ba_{uid}"),
                InlineKeyboardButton(text="➖ Баланс", callback_data=f"adm_br_{uid}"),
            ],
            [InlineKeyboardButton(text="🎁 Забрать приз",  callback_data=f"adm_tp_{uid}")],
            [InlineKeyboardButton(text="🎀 Выдать приз",   callback_data=f"adm_gp_{uid}")],
            [InlineKeyboardButton(
                text="✅ Разблокировать" if u["is_blocked"] else "🚫 Заблокировать",
                callback_data=f"adm_bl_{uid}",
            )],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adm_users")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_ba_") | F.data.startswith("adm_br_"))
async def adm_bal(cb: CallbackQuery, state: FSMContext):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌", show_alert=True)
    add = cb.data.startswith("adm_ba_")
    uid = int(cb.data[7:])
    await state.update_data(bal_uid=uid, bal_add=add)
    await state.set_state(Adm.bal_amount)
    await cb.message.edit_caption(
        caption=f'{em("money")} {"Сколько добавить?" if add else "Сколько убрать?"} (₽):',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"adm_u_{uid}")]
        ]),
        parse_mode="HTML",
    )


@router.message(Adm.bal_amount)
async def s_bal(msg: Message, state: FSMContext, bot: Bot):
    try:
        amt = float(msg.text.strip())
    except ValueError:
        return await msg.answer("❌ Введите числовое значение!")
    d    = await state.get_data()
    uid  = d["bal_uid"]
    val  = amt if d["bal_add"] else -amt
    await db.update_balance(uid, val)
    await state.clear()
    u    = await db.get_user(uid)
    sign = "+" if val > 0 else ""
    await msg.answer_photo(
        photo=IMG_ADMIN,
        caption=(
            f'{em("money")} <b>Баланс изменён</b>\\n\\n'
            f'Изменение: <b>{sign}{val}₽</b>\\n'
            f'Новый баланс: <b>{u["balance"]:.2f}₽</b>'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ К пользователю", callback_data=f"adm_u_{uid}")]
        ]),
        parse_mode="HTML",
    )
    try:
        await bot.send_message(
            uid,
            f'{em("money")} Баланс изменён администратором: <b>{sign}{abs(val)}₽</b>\\n'
            f'Текущий: <b>{u["balance"]:.2f}₽</b>',
            parse_mode="HTML",
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("adm_bl_"))
async def adm_block(cb: CallbackQuery, bot: Bot):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌", show_alert=True)
    uid = int(cb.data[7:])
    u   = await db.get_user(uid)
    nb  = not u["is_blocked"]
    await db.block_user(uid, nb)
    await cb.answer(f'{"🚫 Заблокирован" if nb else "✅ Разблокирован"}', show_alert=True)
    try:
        await bot.send_message(
            uid,
            "🚫 Вы были заблокированы в боте." if nb else "✅ Вы были разблокированы.",
        )
    except Exception:
        pass
    cb.data = f"adm_u_{uid}"
    await adm_user(cb)


@router.callback_query(F.data.startswith("adm_tp_"))
async def adm_take_prize(cb: CallbackQuery):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌", show_alert=True)
    uid    = int(cb.data[7:])
    prizes = [p for p in await db.get_user_prizes(uid)
              if not p["is_received"] and p["prize_type"] != "nothing"]
    if not prizes:
        return await cb.answer("Нет активных призов!", show_alert=True)
    kb = [
        [InlineKeyboardButton(
            text=f"❌ {p['prize_name']}",
            callback_data=f"adm_rp_{p['id']}_{uid}",
        )]
        for p in prizes[:10]
    ]
    kb.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"adm_u_{uid}")])
    await cb.message.edit_caption(
        caption="Выберите приз для удаления:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
    )


@router.callback_query(F.data.startswith("adm_rp_"))
async def adm_remove_prize(cb: CallbackQuery, bot: Bot):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌", show_alert=True)
    parts       = cb.data[7:].split("_")
    pid, uid    = int(parts[0]), int(parts[1])
    p           = await db.get_prize(pid)
    await db.remove_prize(pid)
    await cb.answer("✅ Приз удалён!", show_alert=True)
    try:
        await bot.send_message(
            uid,
            f'{em("warn")} Администратор отозвал приз: <b>{p["prize_name"]}</b>',
            parse_mode="HTML",
        )
    except Exception:
        pass
    for a in await db.get_all_admins():
        try:
            await bot.send_message(
                a["telegram_id"],
                f'{em("bell")} Приз отозван\\n'
                f'Администратор: {cb.from_user.id}\\n'
                f'У пользователя: {uid}\\n'
                f'Приз: {p["prize_name"]}',
                parse_mode="HTML",
            )
        except Exception:
            pass
    cb.data = f"adm_u_{uid}"
    await adm_user(cb)


@router.callback_query(F.data.startswith("adm_gp_"))
async def adm_give_prize(cb: CallbackQuery, state: FSMContext):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌", show_alert=True)
    uid = int(cb.data[7:])
    await state.update_data(gp_uid=uid)
    await cb.message.edit_caption(
        caption=f'{em("star")} <b>Выберите тип приза:</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎮 Аккаунт", callback_data=f"adm_gpa_{uid}"),
                InlineKeyboardButton(text="🥇 Голда",   callback_data=f"adm_gpg_{uid}"),
            ],
            [InlineKeyboardButton(text="◀️ Назад", callback_data=f"adm_u_{uid}")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_gpa_"))
async def adm_gpa(cb: CallbackQuery, state: FSMContext):
    uid = int(cb.data[8:])
    await state.update_data(gp_uid=uid, gp_type="account")
    await cb.message.edit_caption(caption="📧 Введите email аккаунта:")
    await state.set_state(Adm.give_acc_em)


@router.message(Adm.give_acc_em)
async def s_give_em(msg: Message, state: FSMContext):
    await state.update_data(gp_email=msg.text.strip())
    await msg.answer("🔑 Введите пароль:")
    await state.set_state(Adm.give_acc_pw)


@router.message(Adm.give_acc_pw)
async def s_give_pw(msg: Message, state: FSMContext, bot: Bot):
    d   = await state.get_data()
    uid = d["gp_uid"]
    pwd = msg.text.strip()
    await db.add_prize(
        uid, "account", "Аккаунт (ручная выдача)",
        account_email=d["gp_email"],
        account_password=pwd,
    )
    await state.clear()
    try:
        await bot.send_photo(
            uid,
            photo=IMG_USER,
            caption=(
                f'{em("robot")} <b>Администратор выдал вам аккаунт!</b>\\n\\n'
                f'📧 Email: <code>{d["gp_email"]}</code>\\n'
                f'🔑 Пароль: <code>{pwd}</code>\\n\\n'
                f'{em("warn")} Немедленно смените пароль!'
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass
    for a in await db.get_all_admins():
        try:
            await bot.send_message(
                a["telegram_id"],
                f'{em("bell")} Аккаунт выдан вручную\\n'
                f'Администратор: {msg.from_user.id}\\n'
                f'Кому: {uid}',
                parse_mode="HTML",
            )
        except Exception:
            pass
    await msg.answer_photo(
        photo=IMG_ADMIN,
        caption=f'{em("check")} <b>Аккаунт выдан пользователю {uid}!</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ К пользователю", callback_data=f"adm_u_{uid}")]
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_gpg_"))
async def adm_gpg(cb: CallbackQuery, state: FSMContext):
    uid = int(cb.data[8:])
    await state.update_data(gp_uid=uid)
    await cb.message.edit_caption(caption="🥇 Введите промокод на голду:")
    await state.set_state(Adm.give_gold)


@router.message(Adm.give_gold)
async def s_give_gold(msg: Message, state: FSMContext, bot: Bot):
    d     = await state.get_data()
    uid   = d["gp_uid"]
    promo = msg.text.strip()
    await db.add_prize(uid, "gold", "Голда (ручная выдача)", gold_promo=promo)
    await state.clear()
    try:
        await bot.send_photo(
            uid,
            photo=IMG_USER,
            caption=(
                f'{em("star")} <b>Администратор выдал вам Голду!</b>\\n\\n'
                f'🎟️ Промокод: <code>{promo}</code>'
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass
    for a in await db.get_all_admins():
        try:
            await bot.send_message(
                a["telegram_id"],
                f'{em("bell")} Голда выдана вручную\\n'
                f'Администратор: {msg.from_user.id}\\n'
                f'Кому: {uid}',
                parse_mode="HTML",
            )
        except Exception:
            pass
    await msg.answer_photo(
        photo=IMG_ADMIN,
        caption=f'{em("check")} <b>Голда выдана пользователю {uid}!</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ К пользователю", callback_data=f"adm_u_{uid}")]
        ]),
        parse_mode="HTML",
    )


# ── statistics ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_stats")
async def adm_stats(cb: CallbackQuery):
    if not await is_adm(cb.from_user.id):
        return await cb.answer("❌", show_alert=True)
    await cb.message.edit_caption(
        caption=f'{em("globe")} <b>Статистика</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📈 Общая",         callback_data="adm_st_gen")],
            [InlineKeyboardButton(text="🛡️ Администрация", callback_data="adm_st_adm")],
            [InlineKeyboardButton(text="🎁 Призы",         callback_data="adm_st_prizes")],
            [InlineKeyboardButton(text="◀️ Назад",         callback_data="adm_back_main")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_st_gen")
async def st_gen(cb: CallbackQuery):
    s = await db.get_general_stats()
    await cb.message.edit_caption(
        caption=(
            f'{em("globe")} <b>Общая статистика</b>\\n\\n'
            f'👥 Пользователей: <b>{s["total_users"]}</b>\\n'
            f'🎰 Прокрутов: <b>{s["total_spins"]}</b>\\n'
            f'🎁 Призов выдано: <b>{s["total_prizes"]}</b>\\n'
            f'{em("money")} Баланса выдано: <b>{s["total_balance_given"]:.2f}₽</b>'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adm_stats")]
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_st_adm")
async def st_adm(cb: CallbackQuery):
    admins = await db.get_all_admins()
    lines  = "\\n".join(
        f'{LEVEL_NAMES.get(a["level"], a["level"])} — '
        f'@{a["username"] or a["telegram_id"]}'
        for a in admins
    )
    await cb.message.edit_caption(
        caption=f'🛡️ <b>Администраторы ({len(admins)})</b>\\n\\n{lines or "Список пуст"}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adm_stats")]
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_st_prizes")
async def st_prizes(cb: CallbackQuery):
    await cb.message.edit_caption(
        caption=f'{em("star")} <b>Статистика призов</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Выигранные (не получены)", callback_data="adm_sp_0")],
            [InlineKeyboardButton(text="✅ Выигранные (получены)",    callback_data="adm_sp_1")],
            [InlineKeyboardButton(text="◀️ Назад",                    callback_data="adm_stats")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_sp_"))
async def st_prizes_type(cb: CallbackQuery):
    r     = cb.data[7:]
    label = "получены" if r == "1" else "не получены"
    await cb.message.edit_caption(
        caption=f'🎁 Выигранные ({label}) — выберите тип:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🥇 Голда",    callback_data=f"adm_spl_gold_{r}"),
                InlineKeyboardButton(text="🎮 Аккаунты", callback_data=f"adm_spl_account_{r}"),
            ],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adm_st_prizes")],
        ]),
    )


@router.callback_query(F.data.startswith("adm_spl_"))
async def st_prizes_list(cb: CallbackQuery):
    parts        = cb.data[8:].rsplit("_", 1)
    ptype, r     = parts[0], parts[1]
    received     = r == "1"
    not_recv, recv = await db.get_prizes_stats()
    src          = recv if received else not_recv
    items        = [p for p in src if p["prize_type"] == ptype]
    label        = "получены" if received else "не получены"
    tname        = {"gold": "🥇 Голда", "account": "🎮 Аккаунты"}.get(ptype, ptype)
    lines        = "\\n".join(
        f'• {p["user_id"]} — {p["won_at"].strftime("%d.%m.%Y")}'
        for p in items[:15]
    )
    await cb.message.edit_caption(
        caption=(
            f'{tname} ({label})\\n\\n'
            f'Всего: <b>{len(items)}</b>\\n\\n'
            f'{lines or "Пусто"}'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data=f"adm_sp_{r}")]
        ]),
        parse_mode="HTML",
    )


# ── admin management ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm_admins")
async def adm_admins(cb: CallbackQuery):
    if await adm_level(cb.from_user.id) != "head":
        return await cb.answer("❌ Только для главы!", show_alert=True)
    admins = await db.get_all_admins()
    kb     = []
    for a in admins:
        if a["telegram_id"] == OWNER_ID:
            continue
        name  = f"@{a['username']}" if a.get("username") else str(a["telegram_id"])
        level = LEVEL_NAMES.get(a["level"], a["level"])
        kb.append([InlineKeyboardButton(
            text=f"{level} {name}",
            callback_data=f"adm_adm_info_{a['telegram_id']}",
        )])
    kb.append([InlineKeyboardButton(text="➕ Добавить", callback_data="adm_adm_add")])
    kb.append([InlineKeyboardButton(text="◀️ Назад",    callback_data="adm_back_main")])
    await cb.message.edit_caption(
        caption=f'🛡️ <b>Администраторы ({len(admins)}):</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_adm_info_"))
async def adm_adm_info(cb: CallbackQuery):
    if await adm_level(cb.from_user.id) != "head":
        return await cb.answer("❌", show_alert=True)
    tid   = int(cb.data.replace("adm_adm_info_", ""))
    admin = await db.get_admin(tid)
    if not admin:
        return await cb.answer("Не найден!", show_alert=True)
    name  = f"@{admin['username']}" if admin.get("username") else str(tid)
    level = LEVEL_NAMES.get(admin["level"], admin["level"])
    lvl_btns = []
    for lk, ln in LEVEL_NAMES.items():
        if lk != admin["level"] and lk != "head":
            lvl_btns.append(InlineKeyboardButton(
                text=f"🔄 {ln}",
                callback_data=f"adm_adm_setlvl_{tid}_{lk}",
            ))
    await cb.message.edit_caption(
        caption=(
            f'🛡️ <b>{name}</b>\\n'
            f'🆔 <code>{tid}</code>\\n'
            f'📌 Уровень: {level}\\n'
            f'📅 Добавлен: {admin["added_at"].strftime("%d.%m.%Y")}'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            lvl_btns,
            [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"adm_adm_del_{tid}")],
            [InlineKeyboardButton(text="◀️ Назад",    callback_data="adm_admins")],
        ]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_adm_setlvl_"))
async def adm_set_level(cb: CallbackQuery, bot: Bot):
    if await adm_level(cb.from_user.id) != "head":
        return await cb.answer("❌", show_alert=True)
    parts     = cb.data.replace("adm_adm_setlvl_", "").rsplit("_", 1)
    tid       = int(parts[0])
    new_level = parts[1]
    if new_level not in LEVELS:
        return await cb.answer("❌ Неверный уровень!", show_alert=True)
    old = await db.get_admin(tid)
    await db.add_admin(tid, old["username"] if old else None, new_level, cb.from_user.id)
    await cb.answer(f"✅ Уровень: {LEVEL_NAMES[new_level]}", show_alert=True)
    try:
        await bot.send_message(
            tid,
            f'{em("bell")} Ваш уровень изменён: <b>{LEVEL_NAMES[new_level]}</b>',
            parse_mode="HTML",
        )
    except Exception:
        pass
    cb.data = "adm_admins"
    await adm_admins(cb)


@router.callback_query(F.data.startswith("adm_adm_del_"))
async def adm_adm_delete(cb: CallbackQuery):
    if await adm_level(cb.from_user.id) != "head":
        return await cb.answer("❌", show_alert=True)
    tid   = int(cb.data.replace("adm_adm_del_", ""))
    if tid == OWNER_ID:
        return await cb.answer("❌ Нельзя удалить владельца!", show_alert=True)
    admin = await db.get_admin(tid)
    name  = f"@{admin['username']}" if admin and admin.get("username") else str(tid)
    await cb.message.edit_caption(
        caption=(
            f'{em("warn")} <b>Удалить администратора?</b>\\n\\n'
            f'👤 {name}\\n'
            f'📌 {LEVEL_NAMES.get(admin["level"] if admin else "", "?")}'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"adm_adm_delconf_{tid}"),
            InlineKeyboardButton(text="❌ Отмена",      callback_data=f"adm_adm_info_{tid}"),
        ]]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm_adm_delconf_"))
async def adm_adm_delconf(cb: CallbackQuery, bot: Bot):
    if await adm_level(cb.from_user.id) != "head":
        return await cb.answer("❌", show_alert=True)
    tid = int(cb.data.replace("adm_adm_delconf_", ""))
    if tid == OWNER_ID:
        return await cb.answer("❌ Нельзя!", show_alert=True)
    await db.remove_admin(tid)
    await cb.answer("✅ Администратор удалён!", show_alert=True)
    try:
        await bot.send_message(
            tid,
            f'{em("warn")} <b>Вы были сняты с должности администратора.</b>',
            parse_mode="HTML",
        )
    except Exception:
        pass
    cb.data = "adm_admins"
    await adm_admins(cb)


@router.callback_query(F.data == "adm_adm_add")
async def adm_adm_add(cb: CallbackQuery, state: FSMContext):
    if await adm_level(cb.from_user.id) != "head":
        return await cb.answer("❌", show_alert=True)
    await cb.message.edit_caption(
        caption=(
            f'{em("globe")} <b>Добавление администратора</b>\\n\\n'
            f'Введите Telegram ID или @username:'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="adm_admins")]
        ]),
        parse_mode="HTML",
    )
    await state.set_state(Adm.new_adm_id)


@router.message(Adm.new_adm_id)
async def s_new_adm_id(msg: Message, state: FSMContext):
    if await adm_level(msg.from_user.id) != "head":
        return
    raw    = msg.text.strip().replace("@", "")
    users  = await db.get_all_users()
    target = next(
        (u for u in users
         if str(u["telegram_id"]) == raw
         or u.get("username", "").lower() == raw.lower()),
        None,
    )
    if not target:
        return await msg.answer(
            f'{em("warn")} Пользователь не найден!\\n'
            f'Убедитесь что он запускал бота. Введите снова:',
            parse_mode="HTML",
        )
    existing = await db.get_admin(target["telegram_id"])
    if existing:
        return await msg.answer(
            f'{em("warn")} Уже является администратором: '
            f'<b>{LEVEL_NAMES.get(existing["level"], "?")}</b>',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ К списку", callback_data="adm_admins")]
            ]),
            parse_mode="HTML",
        )
    name = f"@{target['username']}" if target.get("username") else target.get("first_name", "?")
    await state.update_data(
        new_adm_tid=target["telegram_id"],
        new_adm_uname=target.get("username"),
    )
    await msg.answer_photo(
        photo=IMG_ADMIN,
        caption=(
            f'👤 <b>{name}</b> (<code>{target["telegram_id"]}</code>)\\n\\n'
            f'Выберите уровень:'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎬 Ютубер", callback_data="pick_lvl_youtuber")],
            [InlineKeyboardButton(text="⚙️ Админ",  callback_data="pick_lvl_admin")],
            [InlineKeyboardButton(text="❌ Отмена",  callback_data="adm_admins")],
        ]),
        parse_mode="HTML",
    )
    await state.set_state(Adm.new_adm_lvl)


@router.callback_query(F.data.startswith("pick_lvl_"), Adm.new_adm_lvl)
async def pick_level(cb: CallbackQuery, state: FSMContext, bot: Bot):
    if await adm_level(cb.from_user.id) != "head":
        return await cb.answer("❌", show_alert=True)
    lvl   = cb.data.replace("pick_lvl_", "")
    data  = await state.get_data()
    tid   = data["new_adm_tid"]
    uname = data.get("new_adm_uname")
    await db.add_admin(tid, uname, lvl, cb.from_user.id)
    await state.clear()
    name = f"@{uname}" if uname else str(tid)
    await cb.message.edit_caption(
        caption=(
            f'{em("check")} <b>Администратор добавлен!</b>\\n\\n'
            f'👤 {name}\\n'
            f'📌 {LEVEL_NAMES[lvl]}'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛡️ К списку", callback_data="adm_admins")]
        ]),
        parse_mode="HTML",
    )
    try:
        await bot.send_photo(
            tid,
            photo=IMG_ADMIN,
            caption=(
                f'{em("bell")} <b>Вы назначены администратором!</b>\\n\\n'
                f'📌 Уровень: <b>{LEVEL_NAMES[lvl]}</b>\\n\\n'
                f'Используйте /cdta для входа в панель.'
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass
""")

# ══════════════════════════════════════════════════════════════════════════════
write("main.py", """import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import database as db
from config import BOT_TOKEN
from handlers import start, roulette, profile, admin as admin_h

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ── Bot ────────────────────────────────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

dp.include_router(start.router)
dp.include_router(roulette.router)
dp.include_router(profile.router)
dp.include_router(admin_h.router)


# ── App ────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    log.info("✅ Database ready")
    task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
    log.info("✅ Bot polling started")
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await bot.session.close()
    log.info("Bot stopped")


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


@app.get("/")
async def root():
    return JSONResponse({"status": "Tank Blitz Roulette Bot is running"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000, reload=False)
""")

# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 55)
print("  ✅  ПРОЕКТ СОЗДАН!")
print("=" * 55)
print()
print("📁 Файлы:")
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs
               if d not in ("__pycache__", ".git", "venv", ".venv")]
    lvl    = root.replace(".", "").count(os.sep)
    indent = "  " * lvl
    if lvl > 0:
        print(f"{indent}📂 {os.path.basename(root)}/")
    for f in sorted(files):
        if not f.endswith(".pyc"):
            print(f"{'  ' * (lvl + 1)}📄 {f}")

print()
print("🚀 Запуск:")
print("  pip install -r requirements.txt")
print("  export BOT_TOKEN=ваш_токен")
print("  export WEBAPP_URL=https://ваш-сервис.onrender.com")
print("  python main.py")
print()
print("📌 На Render:")
print("  Build:  pip install -r requirements.txt")
print("  Start:  python main.py")
print("  Envs:   BOT_TOKEN, WEBAPP_URL")