import asyncio
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

def roulette_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Ежедневная",     callback_data="rt_day")],
        [InlineKeyboardButton(text="🎲 Каждые 3 дня",   callback_data="rt_three_days")],
        [InlineKeyboardButton(text="🏆 Еженедельная",    callback_data="rt_week")],
        [InlineKeyboardButton(text="💎 Платная · 150₽", callback_data="rt_paid")],
    ])


def back_roulette_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 К рулеткам", callback_data="menu_roulette")],
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
        f'{em("bell")} <b>Выдан приз!</b>\n\n'
        f'👤 {who}\n'
        f'{em("star")} <b>{prize_name}</b>'
    )
    for a in await db.get_all_admins():
        try:
            await bot.send_message(a["telegram_id"], txt, parse_mode="HTML")
        except Exception:
            pass


async def _apply(uid: int, prize: dict, bot: Bot):
    """
    Применяет приз: сохраняет в БД, уведомляет админов.
    Возвращает (prize_text: str, extra_kb_rows: list).
    Никаких отдельных сообщений пользователю — всё будет в одном финальном.
    """
    t = prize["type"]

    # ── баланс ────────────────────────────────────────────────────────────────
    if t == "balance":
        await db.update_balance(uid, prize["value"])
        await db.add_prize(uid, "balance", prize["name"], prize["value"])
        await _notify_admins(bot, uid, prize["name"])
        return (
            f'{em("money")} На ваш баланс зачислено <b>{prize["value"]}₽</b>.',
            [],
        )

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
            pid  = rec["id"]
            rows = [[
                InlineKeyboardButton(text="📥 Получить данные",   callback_data=f"receive_prize_{pid}"),
                InlineKeyboardButton(text="📤 Передать (через 2ч)", callback_data=f"transfer_init_{pid}"),
            ]]
            return (
                f'{em("robot")} Вы выиграли <b>аккаунт Tank Blitz</b>!\n'
                f'Нажмите <b>«Получить данные»</b> чтобы узнать логин и пароль,\n'
                f'или <b>«Передать»</b> другому игроку (доступно через 2 часа).',
                rows,
            )
        await db.update_balance(uid, 50)
        return (
            f'{em("robot")} Аккаунтов сейчас нет в наличии.\n'
            f'Начислено <b>50₽</b> компенсации на ваш баланс.',
            [],
        )

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
            pid  = rec["id"]
            rows = [[
                InlineKeyboardButton(text="🥇 Получить промокод",  callback_data=f"receive_prize_{pid}"),
                InlineKeyboardButton(text="📤 Передать (через 2ч)", callback_data=f"transfer_init_{pid}"),
            ]]
            return (
                f'{em("star")} Вы выиграли <b>Голду Tank Blitz</b>!\n'
                f'Нажмите <b>«Получить промокод»</b> чтобы получить код,\n'
                f'или <b>«Передать»</b> другому игроку (доступно через 2 часа).',
                rows,
            )
        await db.update_balance(uid, 25)
        return (
            f'{em("star")} Промокодов сейчас нет в наличии.\n'
            f'Начислено <b>25₽</b> компенсации на ваш баланс.',
            [],
        )

    return ("", [])


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

    # Убираем кнопки с текущего сообщения
    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    if prize["prize_type"] == "account":
        txt = (
            f'{em("robot")} <b>Данные аккаунта Tank Blitz</b>\n\n'
            f'📧 Email: <code>{prize["account_email"]}</code>\n'
            f'🔑 Пароль: <code>{prize["account_password"]}</code>\n\n'
            f'{em("warn")} Сразу смените пароль!'
        )
    elif prize["prize_type"] == "gold":
        txt = (
            f'{em("star")} <b>Промокод на Голду Tank Blitz</b>\n\n'
            f'🎟️ Код: <code>{prize["gold_promo"]}</code>\n\n'
            f'Введите промокод в игре!'
        )
    else:
        txt = f'{em("check")} Приз получен: <b>{prize["prize_name"]}</b>'

    await bot.send_photo(
        cb.from_user.id,
        photo=IMG_USER,
        caption=txt,
        parse_mode="HTML",
    )
    await cb.answer("✅ Данные отправлены!", show_alert=True)

    for a in await db.get_all_admins():
        try:
            await bot.send_message(
                a["telegram_id"],
                f'{em("bell")} Приз получен\n👤 {cb.from_user.id}\n{prize["prize_name"]}',
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

    try:
        await cb.message.edit_caption(
            caption=(
                f'{em("rocket")} <b>Передача приза</b>\n\n'
                f'Приз: <b>{prize["prize_name"]}</b>\n\n'
                f'Отправьте команду:\n'
                f'<code>/transfer_{pid}_@username</code>\n\n'
                f'Или укажите Telegram ID:\n'
                f'<code>/transfer_{pid}_123456789</code>'
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="menu_profile")]
            ]),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()


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

    try:
        await bot.send_photo(
            to_usr["telegram_id"],
            photo=IMG_USER,
            caption=(
                f'{em("star")} <b>Вам передан приз!</b>\n\n'
                f'От: @{msg.from_user.username or msg.from_user.id}\n'
                f'Приз: <b>{prize["prize_name"]}</b>'
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass

    for a in await db.get_all_admins():
        try:
            await bot.send_message(
                a["telegram_id"],
                f'{em("bell")} Передача приза\n'
                f'От: {msg.from_user.id} → {to_usr["telegram_id"]}\n'
                f'{prize["prize_name"]}',
                parse_mode="HTML",
            )
        except Exception:
            pass

    await msg.answer_photo(
        photo=IMG_USER,
        caption=(
            f'{em("check")} <b>Приз передан!</b>\n\n'
            f'<b>{prize["prize_name"]}</b> отправлен игроку '
            f'@{to_usr.get("username") or to_usr["telegram_id"]}'
        ),
        parse_mode="HTML",
    )


# ── roulette menu ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "menu_roulette")
async def menu_roulette(cb: CallbackQuery):
    u = await db.get_user(cb.from_user.id)
    if u and u["is_blocked"]:
        return await cb.answer("🚫 Вы заблокированы в боте.", show_alert=True)
    bal = float(u["balance"]) if u else 0
    try:
        await cb.message.edit_caption(
            caption=(
                f'{em("star")} <b>Выберите тип рулетки</b>\n\n'
                f'{em("money")} Баланс: <b>{bal:.2f}₽</b>\n\n'
                f'🎯 Ежедневная  •  🎲 3 дня\n'
                f'🏆 Неделя  •  💎 Платная'
            ),
            reply_markup=roulette_menu_kb(),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()


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
        try:
            await cb.message.edit_caption(
                caption=(
                    f'{em("star")} <b>Платная рулетка</b>\n\n'
                    f'{em("money")} Баланс: <b>{bal:.2f}₽</b> / нужно <b>150₽</b>\n\n'
                    f'🎁 Призы:\n{format_prize_list("paid")}'
                ),
                reply_markup=kb,
                parse_mode="HTML",
            )
        except Exception:
            pass
        return await cb.answer()

    # Бесплатные рулетки
    can_spin, left = await _cooldown(uid, rt)
    prizes_txt     = format_prize_list(rt)
    name           = get_roulette_name(rt)
    ico            = get_roulette_emoji(rt)

    if not can_spin:
        try:
            await cb.message.edit_caption(
                caption=(
                    f'{ico} <b>{name}</b>\n\n'
                    f'⏳ Следующий прокрут через: <b>{_fmt(left)}</b>\n\n'
                    f'🎁 Призы:\n{prizes_txt}'
                ),
                reply_markup=back_roulette_kb(),
                parse_mode="HTML",
            )
        except Exception:
            pass
        return await cb.answer()

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
        try:
            await cb.message.edit_caption(
                caption=(
                    f'{ico} <b>{name}</b>\n\n'
                    f'📋 <b>Выполните условия для прокрута:</b>\n\n'
                    f'{fs} Подписаться на каналы\n'
                    f'{ff} Переслать сообщение 3 пользователям\n\n'
                    f'🎁 Призы:\n{prizes_txt}'
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=ch_btns),
                parse_mode="HTML",
            )
        except Exception:
            pass
        return await cb.answer()

    try:
        await cb.message.edit_caption(
            caption=(
                f'{ico} <b>{name}</b>\n\n'
                f'✅ Все условия выполнены!\n\n'
                f'🎁 Призы:\n{prizes_txt}'
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎰 КРУТИТЬ!", callback_data=f"spin_{rt}")],
                [InlineKeyboardButton(text="◀️ Назад",   callback_data="menu_roulette")],
            ]),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()


@router.callback_query(F.data.startswith("chk_"))
async def check_sub(cb: CallbackQuery, bot: Bot):
    rt  = cb.data[4:]
    uid = cb.from_user.id
    ok, not_sub = await check_subscriptions(bot, uid)

    if not ok:
        return await cb.answer(
            "❌ Не подписаны:\n" + "\n".join(ch["title"] for ch in not_sub),
            show_alert=True,
        )

    cond = await db.get_condition(uid, rt)
    fwd  = bool(cond and cond["is_forwarded"])
    await db.set_condition(uid, rt, True, fwd)

    if not fwd:
        try:
            await cb.message.edit_caption(
                caption=(
                    f'{em("check")} <b>Подписка подтверждена!</b>\n\n'
                    f'Теперь перешли это сообщение 3 пользователям и нажми кнопку:'
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Переслал(а)!", callback_data=f"fwd_{rt}")],
                    [InlineKeyboardButton(text="◀️ Назад",        callback_data="menu_roulette")],
                ]),
                parse_mode="HTML",
            )
        except Exception:
            pass
        return await cb.answer()

    try:
        await cb.message.edit_caption(
            caption=f'{em("check")} <b>Все условия выполнены!</b>',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎰 КРУТИТЬ!", callback_data=f"spin_{rt}")],
                [InlineKeyboardButton(text="◀️ Назад",   callback_data="menu_roulette")],
            ]),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()


@router.callback_query(F.data.startswith("fwd_"))
async def confirm_fwd(cb: CallbackQuery):
    rt   = cb.data[4:]
    uid  = cb.from_user.id
    cond = await db.get_condition(uid, rt)
    sub  = bool(cond and cond["is_subscribed"])
    await db.set_condition(uid, rt, sub, True)

    if not sub:
        return await cb.answer("❌ Сначала подпишитесь на каналы!", show_alert=True)

    try:
        await cb.message.edit_caption(
            caption=f'{em("check")} <b>Все условия выполнены! Жми крутить:</b>',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎰 КРУТИТЬ!", callback_data=f"spin_{rt}")],
                [InlineKeyboardButton(text="◀️ Назад",   callback_data="menu_roulette")],
            ]),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()


# ── do spin ────────────────────────────────────────────────────────────────────

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

    # Показываем анимацию кручения — НЕ удаляем кнопки, просто меняем caption
    try:
        await cb.message.edit_caption(
            caption=(
                f'{em("rocket")} <b>Крутим рулетку...</b>\n\n'
                f'🎲 Определяем приз...'
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()

    await asyncio.sleep(2)

    prize = spin_roulette(rt)
    await db.add_spin(uid, rt, prize["name"], prize["type"], prize["value"])
    await db.set_condition(uid, rt, False, False)
    prize_text, extra_rows = await _apply(uid, prize, bot)

    nxt = datetime.now() + timedelta(seconds=COOLDOWNS.get(rt, 86400))

    if prize["type"] == "nothing":
        caption = (
            f'😔 <b>Не повезло в этот раз!</b>\n\n'
            f'Ничего не выпало. Попробуй позже!\n\n'
            f'⏰ Следующий прокрут: <b>{nxt.strftime("%d.%m в %H:%M")}</b>'
        )
        kb_rows = []
    else:
        caption = (
            f'🎉 <b>Поздравляем!</b>\n\n'
            f'Вы выиграли: <b>{prize["name"]}</b>\n\n'
            f'{prize_text}\n\n'
            f'⏰ Следующий прокрут: <b>{nxt.strftime("%d.%m в %H:%M")}</b>'
        )
        kb_rows = extra_rows

    kb_rows += back_roulette_kb().inline_keyboard

    try:
        await cb.message.edit_caption(
            caption=caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows),
            parse_mode="HTML",
        )
    except Exception:
        pass


# ── paid roulette ──────────────────────────────────────────────────────────────

@router.callback_query(F.data == "paid_confirm")
async def paid_confirm(cb: CallbackQuery):
    try:
        await cb.message.edit_caption(
            caption=f'{em("warn")} Потратить <b>150₽</b> на прокрут?',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="✅ Да, крутить!", callback_data="spin_paid"),
                InlineKeyboardButton(text="❌ Отмена",       callback_data="rt_paid"),
            ]]),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()


@router.callback_query(F.data == "topup")
async def topup(cb: CallbackQuery):
    try:
        await cb.message.edit_caption(
            caption=(
                f'{em("money")} <b>Пополнение баланса</b>\n\n'
                f'Обратитесь к администратору: @CodeTMG'
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_roulette")]
            ]),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()


@router.callback_query(F.data == "spin_paid")
async def spin_paid(cb: CallbackQuery, bot: Bot):
    uid = cb.from_user.id
    u   = await db.get_user(uid)

    if float(u["balance"]) < PAID_ROULETTE_PRICE:
        return await cb.answer("❌ Недостаточно средств!", show_alert=True)

    await db.update_balance(uid, -PAID_ROULETTE_PRICE)

    try:
        await cb.message.edit_caption(
            caption=(
                f'{em("rocket")} <b>Крутим платную рулетку...</b>\n\n'
                f'🎲 Определяем приз...'
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()

    await asyncio.sleep(2)

    prize = spin_roulette("paid")
    await db.add_spin(uid, "paid", prize["name"], prize["type"], prize["value"], is_paid=True)
    prize_text, extra_rows = await _apply(uid, prize, bot)
    uu = await db.get_user(uid)

    if prize["type"] == "nothing":
        caption = (
            f'😔 <b>Не повезло в этот раз!</b>\n\n'
            f'Ничего не выпало. Попробуй ещё раз!\n\n'
            f'{em("money")} Баланс: <b>{uu["balance"]:.2f}₽</b>'
        )
        kb_rows = []
    else:
        caption = (
            f'🎉 <b>Поздравляем!</b>\n\n'
            f'Вы выиграли: <b>{prize["name"]}</b>\n\n'
            f'{prize_text}\n\n'
            f'{em("money")} Баланс: <b>{uu["balance"]:.2f}₽</b>'
        )
        kb_rows = extra_rows

    kb_rows += back_roulette_kb().inline_keyboard

    try:
        await cb.message.edit_caption(
            caption=caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows),
            parse_mode="HTML",
        )
    except Exception:
        pass
