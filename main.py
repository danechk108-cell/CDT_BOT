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


def _user_dict(user, prizes_count: int = 0, spin_stats: dict = None, is_admin: bool = False, admin_level: str = None) -> dict:
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
        "is_admin":      is_admin,
        "admin_level":   admin_level,
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
    admin_rec  = await db.get_admin(user_id)
    is_admin   = admin_rec is not None and admin_rec['level'] in ('head', 'admin')
    admin_lvl  = admin_rec['level'] if admin_rec else None
    return JSONResponse({"success": True, "user": _user_dict(user, len(prizes), spin_stats, is_admin, admin_lvl)})


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

    if type == 'all_or_nothing':
        user = await db.get_user(user_id)
        last_spin     = await db.get_last_spin(user_id, type)
        cooldown_secs = 0
        if last_spin:
            cooldown  = COOLDOWNS.get(type, 86400)
            next_spin = last_spin['spun_at'] + timedelta(seconds=cooldown)
            now       = datetime.now()
            if now < next_spin:
                cooldown_secs = int((next_spin - now).total_seconds())
        return JSONResponse({
            "success": True,
            "cooldown": cooldown_secs,
            "conditions_met": float(user['balance']) >= 200,
            "balance": float(user['balance']),
            "prizes": build_roulette_prizes("all_or_nothing_gold"),
        })

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
    prize_choice  = body.get('prize_choice', 'gold')  # для all_or_nothing: 'gold' или 'account'
    price_one     = None
    total_price   = 0

    if roulette_type == 'all_or_nothing':
        last_spin = await db.get_last_spin(user_id, roulette_type)
        if last_spin:
            cooldown  = COOLDOWNS.get(roulette_type, 86400)
            next_spin = last_spin['spun_at'] + timedelta(seconds=cooldown)
            if datetime.now() < next_spin:
                return JSONResponse({"success": False, "error": "Кулдаун не прошёл"})
        if float(user['balance']) < 200:
            return JSONResponse({"success": False, "error": "Недостаточно средств. Нужно 200₽"})
        await db.update_balance(user_id, -200)

    elif roulette_type != 'paid':
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

    async def _save_prize(prize: dict):
        """Сохраняет приз в БД, возвращает запись и флаг компенсации."""
        prize_rec = None
        compensated = False
        if prize['type'] == 'balance':
            await db.update_balance(user_id, prize['value'])
            prize_rec = await db.add_prize(
                user_id, 'balance', prize['name'], prize['value'],
                is_received=True, received_at=datetime.now(),
            )
        elif prize['type'] == 'account':
            account = await db.get_free_account()
            if account:
                await db.use_account(account['id'], user_id)
                prize_rec = await db.add_prize(
                    user_id, 'account', prize['name'],
                    account_email=account['email'],
                    account_password=account['password'],
                )
            else:
                compensated = True
                await db.update_balance(user_id, 50)
                prize_rec = await db.add_prize(
                    user_id, 'balance', 'Компенсация 50₽ (нет аккаунтов)', 50.0,
                    is_received=True, received_at=datetime.now(),
                )
        elif prize['type'] == 'gold':
            gold = await db.get_free_gold()
            if gold:
                await db.use_gold(gold['id'], user_id)
                prize_rec = await db.add_prize(
                    user_id, 'gold', prize['name'],
                    gold_promo=gold['promo_code'],
                )
            else:
                compensated = True
                await db.update_balance(user_id, 25)
                prize_rec = await db.add_prize(
                    user_id, 'balance', 'Компенсация 25₽ (нет голды)', 25.0,
                    is_received=True, received_at=datetime.now(),
                )
        return prize_rec, compensated

    if roulette_type != 'paid':
        spin_key = f"all_or_nothing_{prize_choice}" if roulette_type == 'all_or_nothing' else roulette_type
        prize = spin_roulette(spin_key)
        rolled_prize = prize
        await db.add_spin(
            user_id, roulette_type,
            prize['name'], prize['type'], prize['value'],
            is_paid=False,
        )
        await db.set_condition(user_id, roulette_type, False, False)
        prize_rec, comp = await _save_prize(prize)
        results.append({
            "name":  prize['name'], "type": prize['type'],
            "value": float(prize['value']),
            "prize_id":     prize_rec['id'] if prize_rec else None,
            "can_claim":    bool(prize_rec and prize['type'] in ('account', 'gold') and not comp),
            "can_transfer": bool(prize_rec and prize['type'] in ('account', 'gold') and not comp),
            "compensated":  comp,
        })
    else:
        for _ in range(spin_count):
            prize = spin_roulette("paid", paid_luck)
            rolled_prize = prize
            await db.add_spin(
                user_id, "paid",
                prize['name'], prize['type'], prize['value'],
                is_paid=True, paid_luck=paid_luck,
            )
            prize_rec, comp = await _save_prize(prize)
            results.append({
                "name":  prize['name'], "type": prize['type'],
                "value": float(prize['value']),
                "prize_id":     prize_rec['id'] if prize_rec else None,
                "can_claim":    bool(prize_rec and prize['type'] in ('account', 'gold') and not comp),
                "can_transfer": bool(prize_rec and prize['type'] in ('account', 'gold') and not comp),
                "compensated":  comp,
            })

    # ── Одно итоговое сообщение пользователю с премиум эмодзи ──────────────────
    wins = [r for r in results if r['type'] != 'nothing']
    try:
        from config import em
        if wins:
            lines = []
            for r in wins:
                if r['type'] == 'balance':
                    lines.append(f"{em('money')} <b>{r['name']}</b> — зачислено на баланс")
                elif r['type'] == 'account':
                    lines.append(f"{em('robot')} <b>Аккаунт Tank Blitz</b> — нажмите «Забрать» в профиле")
                elif r['type'] == 'gold':
                    lines.append(f"{em('star')} <b>Голда Tank Blitz</b> — нажмите «Забрать» в профиле")
            if spin_count > 1:
                header = f"{em('trophy')} <b>Результаты {spin_count} прокрутов</b>\n\n"
            else:
                header = f"{em('trophy')} <b>Поздравляем!</b>\n\n"
            await bot.send_message(
                user_id,
                header + "\n".join(lines),
                parse_mode="HTML",
            )
        else:
            if spin_count > 1:
                msg = f"{em('hmm')} <b>{spin_count} прокрутов</b> — ничего не выиграно. Попробуйте ещё!"
            else:
                msg = f"{em('hmm')} <b>Не повезло!</b> Ничего не выиграно. Попробуйте ещё раз!"
            await bot.send_message(user_id, msg, parse_mode="HTML")
    except Exception:
        pass

    # ── Уведомление администраторам одним сообщением ───────────────────────────
    if wins:
        try:
            from config import em as _em
            prize_lines = "\n".join(f"  • {r['name']}" for r in wins)
            admin_txt = (
                f"{_em('bell')} <b>Выигрыш!</b>\n"
                f"{_em('hand')} ID: {user_id}\n"
                f"{_em('gift')} Призы ({len(wins)}/{spin_count}):\n{prize_lines}"
            )
            for admin_rec in await db.get_all_admins():
                try:
                    await bot.send_message(admin_rec['telegram_id'], admin_txt, parse_mode="HTML")
                except Exception:
                    pass
        except Exception:
            pass

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


# ===== SUPPORT TICKETS =====

TICKET_CATEGORIES = [
    "Проблема с призом",
    "Проблема с балансом",
    "Технический вопрос",
    "Жалоба",
    "Другое",
]

@app.get("/api/support/categories")
async def api_ticket_categories(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")
    return JSONResponse({"success": True, "categories": TICKET_CATEGORIES})

@app.post("/api/support/create")
async def api_create_ticket(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")

    user_id = tg_user['id']
    body    = await request.json()
    category = body.get('category', '').strip()
    message  = body.get('message', '').strip()

    if not category or category not in TICKET_CATEGORIES:
        return JSONResponse({"success": False, "error": "Выберите категорию"})
    if len(message) < 10:
        return JSONResponse({"success": False, "error": "Опишите проблему подробнее (мин. 10 символов)"})
    if len(message) > 1000:
        return JSONResponse({"success": False, "error": "Сообщение слишком длинное (макс. 1000 символов)"})

    ticket = await db.create_ticket(user_id, category, message)
    user   = await db.get_user(user_id)

    # Уведомляем всех администраторов
    from config import em
    who = f"@{user['username']}" if user and user.get('username') else str(user_id)
    admin_txt = (
        f"{em('bell')} <b>Новый тикет поддержки #{ticket['id']}</b>\n\n"
        f"{em('hand')} Пользователь: {who} (ID: {user_id})\n"
        f"{em('search')} Категория: <b>{category}</b>\n\n"
        f"{em('hmm')} Сообщение:\n{message}"
    )
    for admin_rec in await db.get_all_admins():
        try:
            await bot.send_message(admin_rec['telegram_id'], admin_txt, parse_mode="HTML")
        except Exception:
            pass

    return JSONResponse({"success": True, "ticket_id": ticket['id']})

@app.get("/api/support/my")
async def api_my_tickets(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")
    tickets = await db.get_user_tickets(tg_user['id'])
    result = [
        {
            "id":          t['id'],
            "category":    t['category'],
            "message":     t['message'],
            "status":      t['status'],
            "admin_reply": t['admin_reply'] if 'admin_reply' in t.keys() else None,
            "replied_at":  t['replied_at'].isoformat() if t.get('replied_at') else None,
            "created_at":  t['created_at'].isoformat(),
        }
        for t in tickets
    ]
    return JSONResponse({"success": True, "tickets": result})


# ===== ADMIN PANEL API =====

async def _require_admin(request: Request):
    tg_user = await get_tg_user(request.headers.get('x-telegram-init-data'))
    if not tg_user:
        raise HTTPException(401, "Unauthorized")
    admin_rec = await db.get_admin(tg_user['id'])
    if not admin_rec or admin_rec['level'] not in ('head', 'admin'):
        raise HTTPException(403, "Forbidden")
    return tg_user, admin_rec

@app.get("/api/admin/stats")
async def api_admin_stats(request: Request):
    await _require_admin(request)
    stats   = await db.get_general_stats()
    tickets = await db.get_all_tickets('open')
    return JSONResponse({
        "success": True,
        "stats": stats,
        "open_tickets": len(tickets),
    })

@app.get("/api/admin/tickets")
async def api_admin_tickets(request: Request):
    await _require_admin(request)
    tickets = await db.get_all_tickets()
    result = [
        {
            "id":          t['id'],
            "user_id":     t['user_id'],
            "category":    t['category'],
            "message":     t['message'],
            "status":      t['status'],
            "admin_reply": t['admin_reply'] if 'admin_reply' in t.keys() else None,
            "created_at":  t['created_at'].isoformat(),
        }
        for t in tickets
    ]
    return JSONResponse({"success": True, "tickets": result})

@app.post("/api/admin/ticket/close")
async def api_admin_close_ticket(request: Request):
    await _require_admin(request)
    body = await request.json()
    tid  = body.get('ticket_id')
    if not tid:
        return JSONResponse({"success": False, "error": "ticket_id required"})
    await db.close_ticket(tid)
    return JSONResponse({"success": True})

@app.get("/api/admin/users")
async def api_admin_users(request: Request):
    await _require_admin(request)
    users = await db.get_all_users()
    result = [
        {
            "telegram_id": u['telegram_id'],
            "username":    u['username'],
            "first_name":  u['first_name'],
            "balance":     float(u['balance']),
            "is_blocked":  bool(u['is_blocked']),
            "created_at":  u['created_at'].isoformat() if u['created_at'] else None,
        }
        for u in users[:50]
    ]
    return JSONResponse({"success": True, "users": result})

@app.post("/api/admin/user/block")
async def api_admin_block(request: Request):
    tg_user, _ = await _require_admin(request)
    body   = await request.json()
    target = body.get('telegram_id')
    block  = body.get('block', True)
    if not target:
        return JSONResponse({"success": False, "error": "telegram_id required"})
    await db.block_user(int(target), block)
    return JSONResponse({"success": True})


@app.post("/api/admin/user/balance")
async def api_admin_balance(request: Request):
    tg_user, _ = await _require_admin(request)
    body   = await request.json()
    target = body.get('telegram_id')
    amount = body.get('amount')
    if not target or amount is None:
        return JSONResponse({"success": False, "error": "telegram_id и amount обязательны"})
    await db.update_balance(int(target), float(amount))
    user = await db.get_user(int(target))
    if not user:
        return JSONResponse({"success": False, "error": "Пользователь не найден"})
    try:
        from config import em
        sign = '+' if float(amount) >= 0 else ''
        await bot.send_message(
            int(target),
            f"{em('cash')} Ваш баланс изменён администратором: <b>{sign}{float(amount):.2f}₽</b>\n"
            f"{em('wallet')} Новый баланс: <b>{float(user['balance']):.2f}₽</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass
    return JSONResponse({"success": True, "new_balance": float(user['balance'])})


@app.post("/api/admin/user/give-prize")
async def api_admin_give_prize(request: Request):
    tg_user, admin_rec = await _require_admin(request)
    body       = await request.json()
    target_id  = body.get('telegram_id')
    prize_type = body.get('prize_type')  # 'account' or 'gold'
    if not target_id or prize_type not in ('account', 'gold'):
        return JSONResponse({"success": False, "error": "Неверные параметры"})
    target = await db.get_user(int(target_id))
    if not target:
        return JSONResponse({"success": False, "error": "Пользователь не найден"})
    prize_rec = None
    if prize_type == 'account':
        account = await db.get_free_account()
        if not account:
            return JSONResponse({"success": False, "error": "Нет аккаунтов в пуле"})
        await db.use_account(account['id'], int(target_id))
        prize_rec = await db.add_prize(
            int(target_id), 'account', 'Аккаунт Tank Blitz',
            account_email=account['email'], account_password=account['password'],
        )
    else:
        gold = await db.get_free_gold()
        if not gold:
            return JSONResponse({"success": False, "error": "Нет промокодов в пуле"})
        await db.use_gold(gold['id'], int(target_id))
        prize_rec = await db.add_prize(
            int(target_id), 'gold', 'Голда Tank Blitz',
            gold_promo=gold['promo_code'],
        )
    try:
        from config import em
        await bot.send_message(
            int(target_id),
            f"{em('gift')} Администратор выдал вам приз: <b>{'Аккаунт Tank Blitz' if prize_type=='account' else 'Голда Tank Blitz'}</b>!\n"
            f"Нажмите «Забрать» в профиле.",
            parse_mode="HTML",
        )
    except Exception:
        pass
    return JSONResponse({"success": True, "prize_id": prize_rec['id'] if prize_rec else None})


@app.post("/api/admin/user/remove-prize")
async def api_admin_remove_prize(request: Request):
    tg_user, _ = await _require_admin(request)
    body     = await request.json()
    prize_id = body.get('prize_id')
    if not prize_id:
        return JSONResponse({"success": False, "error": "prize_id обязателен"})
    prize = await db.get_prize(prize_id)
    if not prize:
        return JSONResponse({"success": False, "error": "Приз не найден"})
    await db.remove_prize(prize_id)
    return JSONResponse({"success": True})


@app.post("/api/admin/ticket/reply")
async def api_admin_reply_ticket(request: Request):
    tg_user, admin_rec = await _require_admin(request)
    body  = await request.json()
    tid   = body.get('ticket_id')
    reply = body.get('reply', '').strip()
    if not tid or not reply:
        return JSONResponse({"success": False, "error": "ticket_id и reply обязательны"})
    ticket = await db.reply_ticket(int(tid), tg_user['id'], reply)
    if not ticket:
        return JSONResponse({"success": False, "error": "Тикет не найден"})
    # Уведомляем пользователя в боте
    try:
        from config import em
        await bot.send_message(
            ticket['user_id'],
            f"{em('bell')} <b>Ответ поддержки на тикет #{tid}</b>\n\n"
            f"{em('check')} {reply}",
            parse_mode="HTML",
        )
    except Exception:
        pass
    return JSONResponse({"success": True})


@app.post("/api/admin/broadcast")
async def api_admin_broadcast(request: Request):
    tg_user, admin_rec = await _require_admin(request)
    body = await request.json()
    text = body.get('text', '').strip()
    if not text:
        return JSONResponse({"success": False, "error": "Текст рассылки не может быть пустым"})
    if len(text) > 4096:
        return JSONResponse({"success": False, "error": "Текст слишком длинный (макс. 4096 символов)"})
    users = await db.get_all_users()
    sent = 0
    failed = 0
    for u in users:
        if u['is_blocked']:
            continue
        try:
            await bot.send_message(u['telegram_id'], text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
    return JSONResponse({"success": True, "sent": sent, "failed": failed})


# ===== ADMIN MANAGEMENT (head only) =====

async def _require_head(request: Request):
    tg_user, admin_rec = await _require_admin(request)
    if admin_rec['level'] != 'head':
        raise HTTPException(403, "Only head admin can manage admins")
    return tg_user, admin_rec


@app.get("/api/admin/admins")
async def api_admin_list_admins(request: Request):
    await _require_head(request)
    admins = await db.get_all_admins()
    result = [
        {
            "telegram_id": a['telegram_id'],
            "level":       a['level'],
            "username":    a.get('username'),
            "first_name":  a.get('first_name'),
        }
        for a in admins
    ]
    return JSONResponse({"success": True, "admins": result})


@app.post("/api/admin/admin/add")
async def api_admin_add(request: Request):
    tg_user, _ = await _require_head(request)
    body = await request.json()
    tid   = body.get('telegram_id')
    level = body.get('level', 'admin')
    if not tid:
        return JSONResponse({"success": False, "error": "telegram_id обязателен"})
    if level not in ('admin', 'head'):
        return JSONResponse({"success": False, "error": "level должен быть admin или head"})
    username = body.get('username') or None
    await db.add_admin(int(tid), username, level, tg_user['id'])
    return JSONResponse({"success": True})


@app.post("/api/admin/admin/update")
async def api_admin_update(request: Request):
    tg_user, _ = await _require_head(request)
    body = await request.json()
    tid   = body.get('telegram_id')
    level = body.get('level')
    if not tid or level not in ('admin', 'head'):
        return JSONResponse({"success": False, "error": "Неверные параметры"})
    existing = await db.get_admin(int(tid))
    username = existing['username'] if existing else None
    await db.add_admin(int(tid), username, level, tg_user['id'])
    return JSONResponse({"success": True})


@app.post("/api/admin/admin/remove")
async def api_admin_remove(request: Request):
    tg_user, _ = await _require_head(request)
    body = await request.json()
    tid  = body.get('telegram_id')
    if not tid:
        return JSONResponse({"success": False, "error": "telegram_id обязателен"})
    if int(tid) == tg_user['id']:
        return JSONResponse({"success": False, "error": "Нельзя удалить самого себя"})
    await db.remove_admin(int(tid))
    return JSONResponse({"success": True})


# ===== PRIZE POOL MANAGEMENT =====

@app.get("/api/admin/pool/accounts")
async def api_admin_pool_accounts(request: Request):
    await _require_admin(request)
    rows = await db.get_all_accounts_pool()
    return JSONResponse({"success": True, "accounts": [
        {"id": r['id'], "email": r['email'], "password": r['password'],
         "is_used": r['is_used'],
         "added_at": r['added_at'].isoformat() if r.get('added_at') else None}
        for r in rows
    ]})

@app.post("/api/admin/pool/accounts/add")
async def api_admin_pool_accounts_add(request: Request):
    tg_user, _ = await _require_admin(request)
    body = await request.json()
    email    = (body.get('email') or '').strip()
    password = (body.get('password') or '').strip()
    if not email or not password:
        return JSONResponse({"success": False, "error": "email и password обязательны"})
    await db.add_account(email, password, tg_user['id'])
    return JSONResponse({"success": True})

@app.post("/api/admin/pool/accounts/delete")
async def api_admin_pool_accounts_delete(request: Request):
    await _require_admin(request)
    body = await request.json()
    aid = body.get('id')
    if not aid:
        return JSONResponse({"success": False, "error": "id обязателен"})
    await db.delete_account_pool(int(aid))
    return JSONResponse({"success": True})

@app.get("/api/admin/pool/gold")
async def api_admin_pool_gold(request: Request):
    await _require_admin(request)
    rows = await db.get_all_gold_pool()
    return JSONResponse({"success": True, "gold": [
        {"id": r['id'], "promo_code": r['promo_code'], "is_used": r['is_used'],
         "added_at": r['added_at'].isoformat() if r.get('added_at') else None}
        for r in rows
    ]})

@app.post("/api/admin/pool/gold/add")
async def api_admin_pool_gold_add(request: Request):
    tg_user, _ = await _require_admin(request)
    body = await request.json()
    promo = (body.get('promo_code') or '').strip()
    if not promo:
        return JSONResponse({"success": False, "error": "promo_code обязателен"})
    await db.add_gold_promo(promo, tg_user['id'])
    return JSONResponse({"success": True})

@app.post("/api/admin/pool/gold/delete")
async def api_admin_pool_gold_delete(request: Request):
    await _require_admin(request)
    body = await request.json()
    gid = body.get('id')
    if not gid:
        return JSONResponse({"success": False, "error": "id обязателен"})
    await db.delete_gold_pool(int(gid))
    return JSONResponse({"success": True})
