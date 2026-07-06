import asyncio
import logging
import json
import hashlib
import hmac
import urllib.parse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

import uvicorn

import database as db
from config import BOT_TOKEN, WEBAPP_URL, COOLDOWNS, PRIZE_TRANSFER_DELAY
from utils.prizes import (
    build_roulette_prizes,
    get_paid_price,
    normalize_paid_count,
    normalize_paid_luck,
    spin_roulette,
)
from utils.checks import check_subscriptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== BOT SETUP =====
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ===== ПОДКЛЮЧАЕМ РОУТЕРЫ =====
def setup_routers():
    from handlers import start, roulette, profile, admin
    dp.include_router(start.router)
    dp.include_router(roulette.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)

setup_routers()

# ===== WEBHOOK SETTINGS =====
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL  = f"{WEBAPP_URL}{WEBHOOK_PATH}"


# ===== LIFESPAN =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    logger.info("Database initialized")
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    logger.info(f"Webhook set to {WEBHOOK_URL}")
    yield
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Bot stopped")


app = FastAPI(lifespan=lifespan)

# ===== CORS (нужен для Telegram WebApp) =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="webapp/templates")


# ===== WEBHOOK ENDPOINT =====
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        data   = await request.json()
        update = Update(**data)
        await dp.feed_update(bot=bot, update=update)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
    return {"ok": True}

# Handle URL-encoded colon in webhook path (%3A)
WEBHOOK_PATH_ENCODED = WEBHOOK_PATH.replace(":", "%3A")

@app.post(WEBHOOK_PATH_ENCODED)
async def telegram_webhook_encoded(request: Request):
    return await telegram_webhook(request)


# ===== WEBAPP ROUTE =====
@app.get("/webapp", response_class=HTMLResponse)
async def webapp_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ===== AUTH HELPER =====
def _validate_init_data(init_data: str) -> bool:
    """Проверяет HMAC подпись initData от Telegram"""
    try:
        parsed        = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        received_hash = parsed.pop('hash', None)
        if not received_hash:
            return False

        data_check_string = '\n'.join(
            f"{k}={v}" for k, v in sorted(parsed.items())
        )
        secret_key    = hmac.new(b'WebAppData', BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed_hash, received_hash)
    except Exception:
        return False


async def get_tg_user(init_data: str = None):
    """Парсит и валидирует init data от Telegram"""
    if not init_data:
        return None
    try:
        if not _validate_init_data(init_data):
            logger.warning("initData HMAC validation failed")
            return None
        data      = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        user_data = data.get('user')
        if not user_data:
            return None
        return json.loads(user_data)
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return None


def _user_dict(user, prizes_count: int = 0, spin_stats: dict = None) -> dict:
    """Универсальный словарь пользователя для API-ответов"""
    return {
        "telegram_id":   user['telegram_id'],
        "username":      user['username'],
        "first_name":    user['first_name'],
        "game_id":       user['game_id'],
        "roulette_type": user['roulette_type'],
        "balance":       float(user['balance']),
        "prizes_count":  prizes_count,
        "is_blocked":    bool(user['is_blocked']),
        "created_at":    user['created_at'].strftime("%d.%m.%Y") if user['created_at'] else None,
        "spin_stats":    spin_stats or {"total": 0, "wins": 0, "biggest": 0},
    }


# ===== API ROUTES =====

@app.get("/api/user/me")
async def api_user_me(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")

    user_id = tg_user['id']
    user    = await db.get_user(user_id)

    if not user:
        await db.create_user(
            user_id,
            tg_user.get('username'),
            tg_user.get('first_name', ''),
            tg_user.get('last_name'),
        )
        user = await db.get_user(user_id)

    # Заблокированный пользователь — возвращаем 200 с blocked:true,
    # чтобы фронт гарантированно получил JSON (403 может перехватываться прокси/WebView)
    if user['is_blocked']:
        return JSONResponse(
            {"success": False, "blocked": True, "error": "Вы заблокированы"},
            status_code=200,
        )

    prizes     = await db.get_user_prizes(user_id)
    spin_stats = await db.get_user_spin_stats(user_id)
    return JSONResponse({"success": True, "user": _user_dict(user, len(prizes), spin_stats)})


@app.post("/api/user/set-game-id")
async def api_set_game_id(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")

    body    = await request.json()
    game_id = body.get('game_id', '').strip()

    if len(game_id) < 3:
        return JSONResponse({"success": False, "error": "Некорректный ID"})

    user_id = tg_user['id']
    await db.update_game_id(user_id, game_id)
    user = await db.get_user(user_id)

    return JSONResponse({"success": True, "user": _user_dict(user)})


@app.post("/api/user/set-roulette-type")
async def api_set_roulette_type(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")

    body          = await request.json()
    roulette_type = body.get('roulette_type', '').strip()

    if roulette_type not in ('day', 'three_days', 'week'):
        return JSONResponse({"success": False, "error": "Некорректный тип рулетки"})

    user_id = tg_user['id']
    await db.update_roulette_type(user_id, roulette_type)
    user = await db.get_user(user_id)

    return JSONResponse({"success": True, "user": _user_dict(user)})


@app.get("/api/roulette/status")
async def api_roulette_status(request: Request, type: str = "day", luck: int | None = None, count: int = 1):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")

    user_id = tg_user['id']

    if type != 'paid':
        last_spin    = await db.get_last_spin(user_id, type)
        cooldown_secs = 0

        if last_spin:
            cooldown  = COOLDOWNS.get(type, 86400)
            next_spin = last_spin['spun_at'] + timedelta(seconds=cooldown)
            now       = datetime.now()
            if now < next_spin:
                cooldown_secs = int((next_spin - now).total_seconds())

        condition      = await db.get_condition(user_id, type)
        conditions_met = bool(
            condition and condition['is_subscribed'] and condition['is_forwarded']
        )

        return JSONResponse({
            "success": True,
            "cooldown": cooldown_secs,
            "conditions_met": conditions_met,
            "prizes": build_roulette_prizes(type),
        })
    else:
        user = await db.get_user(user_id)
        luck_value  = normalize_paid_luck(luck)
        count_value = normalize_paid_count(count)
        price_one   = get_paid_price(luck_value)
        total_price = price_one * count_value
        return JSONResponse({
            "success": True,
            "cooldown": 0,
            "conditions_met": float(user['balance']) >= total_price,
            "price": price_one,
            "total_price": total_price,
            "luck": luck_value,
            "count": count_value,
            "prizes": build_roulette_prizes("paid", luck_value),
        })


@app.post("/api/roulette/check-conditions")
async def api_check_conditions(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")

    user_id       = tg_user['id']
    body          = await request.json()
    roulette_type = body.get('type', 'day')
    forwarded     = body.get('forwarded', False)

    subscribed, _ = await check_subscriptions(bot, user_id)
    condition     = await db.get_condition(user_id, roulette_type)
    was_forwarded = (condition and condition['is_forwarded']) or forwarded

    await db.set_condition(user_id, roulette_type, subscribed, was_forwarded)
    conditions_met = subscribed and was_forwarded

    return JSONResponse({
        "success": True,
        "subscribed": subscribed,
        "forwarded": was_forwarded,
        "conditions_met": conditions_met,
    })


@app.post("/api/roulette/spin")
async def api_spin(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")

    user_id = tg_user['id']
    user    = await db.get_user(user_id)

    if not user or user['is_blocked']:
        return JSONResponse({"success": False, "error": "Доступ запрещён"})

    body          = await request.json()
    roulette_type = body.get('type', 'day')
    paid_luck     = normalize_paid_luck(body.get('luck'))
    spin_count    = normalize_paid_count(body.get('count')) if roulette_type == 'paid' else 1
    price_one     = None
    total_price   = 0

    if roulette_type != 'paid':
        if body.get("count") not in (None, 1, "1"):
            return JSONResponse({"success": False, "error": "Множественное открытие доступно только для платной рулетки"})
        last_spin = await db.get_last_spin(user_id, roulette_type)
        if last_spin:
            cooldown  = COOLDOWNS.get(roulette_type, 86400)
            next_spin = last_spin['spun_at'] + timedelta(seconds=cooldown)
            if datetime.now() < next_spin:
                return JSONResponse({"success": False, "error": "Кулдаун не прошёл"})

        condition           = await db.get_condition(user_id, roulette_type)
        subscribed, _       = await check_subscriptions(bot, user_id)
        if not subscribed or not condition or not condition['is_forwarded']:
            return JSONResponse({"success": False, "error": "Условия не выполнены"})
    else:
        price_one   = get_paid_price(paid_luck)
        total_price = price_one * spin_count
        if float(user['balance']) < total_price:
            return JSONResponse({"success": False, "error": "Недостаточно средств"})
        await db.update_balance(user_id, -total_price)

    results = []
    rolled_prize = None

    async def _save_and_notify(prize: dict, paid_luck_value: int):
        prize_rec = None
        if prize['type'] == 'balance':
            await db.update_balance(user_id, prize['value'])
            prize_rec = await db.add_prize(
                user_id, 'balance', prize['name'], prize['value'],
                is_received=True, received_at=datetime.now(),
            )
            try:
                await bot.send_message(
                    user_id,
                    f"🎁 <b>Вы выиграли {prize['name']}!</b>\n\n💰 Зачислено на баланс!",
                    parse_mode="HTML",
                )
            except Exception:
                pass

        elif prize['type'] == 'account':
            account = await db.get_free_account()
            if account:
                await db.use_account(account['id'], user_id)
                prize_rec = await db.add_prize(
                    user_id, 'account', prize['name'],
                    account_email=account['email'],
                    account_password=account['password'],
                )
                try:
                    await bot.send_message(
                        user_id,
                        f"🎮 <b>Вы выиграли аккаунт Tank Blitz!</b>\n\n"
                        f"Нажмите <b>Забрать</b> в профиле, чтобы получить данные.",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass

        elif prize['type'] == 'gold':
            gold = await db.get_free_gold()
            if gold:
                await db.use_gold(gold['id'], user_id)
                prize_rec = await db.add_prize(
                    user_id, 'gold', prize['name'],
                    gold_promo=gold['promo_code'],
                )
                try:
                    await bot.send_message(
                        user_id,
                        f"🥇 <b>Вы выиграли Голду Tank Blitz!</b>\n\n"
                        f"Нажмите <b>Забрать</b> в профиле, чтобы получить промокод.",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass

        if prize['type'] != 'nothing':
            admins = await db.get_all_admins()
            for admin_rec in admins:
                try:
                    await bot.send_message(
                        admin_rec['telegram_id'],
                        f"🎰 <b>Выигрыш!</b>\n👤 ID: {user_id}\n🎁 Приз: {prize['name']}",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass

        return {
            "name":      prize['name'],
            "type":      prize['type'],
            "value":     float(prize['value']),
            "prize_id":  prize_rec['id'] if prize_rec else None,
            "can_claim": bool(prize_rec and prize['type'] in ('account', 'gold')),
            "can_transfer": bool(prize_rec and prize['type'] in ('account', 'gold')),
        }

    if roulette_type != 'paid':
        prize = spin_roulette(roulette_type)
        rolled_prize = prize
        await db.add_spin(
            user_id, roulette_type,
            prize['name'], prize['type'], prize['value'],
            is_paid=False,
        )
        await db.set_condition(user_id, roulette_type, False, False)
        results.append(await _save_and_notify(prize, paid_luck))
    else:
        for _ in range(spin_count):
            prize = spin_roulette("paid", paid_luck)
            rolled_prize = prize
            await db.add_spin(
                user_id, "paid",
                prize['name'], prize['type'], prize['value'],
                is_paid=True, paid_luck=paid_luck,
            )
            results.append(await _save_and_notify(prize, paid_luck))

    updated_user = await db.get_user(user_id)
    first_prize = results[0] if results else {
        "name": "Ничего",
        "type": "nothing",
        "value": 0,
        "prize_id": None,
        "can_claim": False,
        "can_transfer": False,
    }
    return JSONResponse({
        "success": True,
        "prize": first_prize,
        "results": results,
        "paid_luck": paid_luck if roulette_type == 'paid' else None,
        "count": spin_count if roulette_type == 'paid' else 1,
        "price": price_one,
        "total_price": total_price,
        "user": {"balance": float(updated_user['balance'])},
    })


@app.get("/api/user/prizes")
async def api_user_prizes(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")

    user_id = tg_user['id']
    prizes  = await db.get_user_prizes(user_id)

    result = []
    for prize in prizes:
        can_transfer = (
            not prize['is_received']
            and prize['prize_type'] != 'nothing'
            and datetime.now() - prize['won_at'] >= timedelta(seconds=PRIZE_TRANSFER_DELAY)
        )
        # prize_value может быть None для account/gold — приводим безопасно
        raw_value = prize['prize_value']
        result.append({
            "id":          prize['id'],
            "prize_name":  prize['prize_name'],
            "prize_type":  prize['prize_type'],
            "prize_value": float(raw_value) if raw_value is not None else 0.0,
            "is_received": prize['is_received'],
            "won_at":      prize['won_at'].isoformat(),
            "can_transfer": can_transfer,
        })

    return JSONResponse({"success": True, "prizes": result})


@app.post("/api/user/transfer-prize")
async def api_transfer_prize(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")

    user_id  = tg_user['id']
    body     = await request.json()
    prize_id = body.get('prize_id')
    target   = body.get('target', '').strip().replace('@', '')

    prize = await db.get_prize(prize_id)
    if not prize or prize['user_id'] != user_id:
        return JSONResponse({"success": False, "error": "Приз не найден"})
    if prize['prize_type'] not in ('account', 'gold'):
        return JSONResponse({"success": False, "error": "Передача доступна только для аккаунта и голды"})
    if prize['is_received']:
        return JSONResponse({"success": False, "error": "Приз уже получен"})

    elapsed = datetime.now() - prize['won_at']
    if elapsed < timedelta(seconds=PRIZE_TRANSFER_DELAY):
        remaining = PRIZE_TRANSFER_DELAY - int(elapsed.total_seconds())
        h = remaining // 3600
        m = (remaining % 3600) // 60
        return JSONResponse({"success": False, "error": f"Передача возможна через {h}ч {m}м"})

    all_users   = await db.get_all_users()
    target_user = next(
        (u for u in all_users
         if str(u['telegram_id']) == target
         or (u.get('username') and u['username'].lower() == target.lower())),
        None,
    )
    if not target_user:
        return JSONResponse({"success": False, "error": "Пользователь не найден"})

    await db.transfer_prize(prize_id, target_user['telegram_id'])

    try:
        await bot.send_message(
            target_user['telegram_id'],
            f"🎁 Вам передан приз!\n\nПриз: <b>{prize['prize_name']}</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass

    admins = await db.get_all_admins()
    for admin_rec in admins:
        try:
            await bot.send_message(
                admin_rec['telegram_id'],
                f"📤 Передача приза\nОт: {user_id}\nКому: {target_user['telegram_id']}\nПриз: {prize['prize_name']}",
                parse_mode="HTML",
            )
        except Exception:
            pass

    return JSONResponse({"success": True})


@app.post("/api/user/claim-prize")
async def api_claim_prize(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")

    user_id  = tg_user['id']
    body     = await request.json()
    prize_id = body.get('prize_id')

    prize = await db.get_prize(prize_id)
    if not prize or prize['user_id'] != user_id:
        return JSONResponse({"success": False, "error": "Приз не найден"})
    if prize['is_received']:
        return JSONResponse({"success": False, "error": "Приз уже получен"})

    await db.mark_prize_received(prize_id)

    response_data = {"success": True, "data": {}}

    if prize['prize_type'] == 'account':
        response_data['data'] = {
            "text": f"Аккаунт Tank Blitz:\nEmail: {prize['account_email']}\nПароль: {prize['account_password']}",
            "email": prize['account_email'],
            "password": prize['account_password'],
        }
        try:
            await bot.send_message(
                user_id,
                f"🎮 <b>Данные аккаунта Tank Blitz</b>\n\n"
                f"📧 Email: <code>{prize['account_email']}</code>\n"
                f"🔑 Пароль: <code>{prize['account_password']}</code>\n\n"
                f"⚠️ Сразу смените пароль!",
                parse_mode="HTML",
            )
        except Exception:
            pass
    elif prize['prize_type'] == 'gold':
        response_data['data'] = {
            "text": f"Промокод на Голду:\n{prize['gold_promo']}",
            "promo": prize['gold_promo'],
        }
        try:
            await bot.send_message(
                user_id,
                f"🥇 <b>Промокод на Голду Tank Blitz</b>\n\n"
                f"🎟️ Код: <code>{prize['gold_promo']}</code>\n\n"
                f"Введите промокод в игре!",
                parse_mode="HTML",
            )
        except Exception:
            pass

    # Notify admins
    admins = await db.get_all_admins()
    for admin_rec in admins:
        try:
            await bot.send_message(
                admin_rec['telegram_id'],
                f"📥 Приз получен\n👤 ID: {user_id}\n🎁 {prize['prize_name']}",
                parse_mode="HTML",
            )
        except Exception:
            pass

    return JSONResponse(response_data)


@app.get("/api/leaders")
async def api_leaders(request: Request):
    users       = await db.get_all_users()
    sorted_users = sorted(users, key=lambda u: u['balance'], reverse=True)[:10]
    result = [
        {
            "telegram_id": u['telegram_id'],
            "username":    u['username'],
            "first_name":  u['first_name'],
            "balance":     float(u['balance']),
            "game_id":     u['game_id'],
        }
        for u in sorted_users
    ]
    return JSONResponse({"success": True, "leaders": result})

@app.get("/health")
async def health():
    return {"status": "ok"}
