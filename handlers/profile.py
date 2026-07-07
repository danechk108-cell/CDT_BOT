from datetime import datetime, timedelta

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
        [InlineKeyboardButton(text="🎰 Открыть рулетку",  callback_data="open_webapp")],
    ])


async def _send_profile(bot: Bot, chat_id: int, user_id: int, tg_user):
    """Отправляет профиль новым сообщением (используется как надёжный fallback)."""
    u  = await db.get_user(user_id)
    un = f"@{tg_user.username}" if tg_user.username else "—"
    caption = (
        f'━━━━━━━━━━━━━━━━━\n'
        f'       👤 <b>ПРОФИЛЬ</b>\n'
        f'━━━━━━━━━━━━━━━━━\n\n'
        f'       🎮 <b>{u.get("game_id", "Не указан")}</b>\n\n'
        f'━━━━━━━━━━━━━━━━━\n\n'
        f'📛 Имя: <b>{tg_user.first_name}</b>\n'
        f'🔗 Username: <b>{un}</b>\n'
        f'🆔 ID: <code>{user_id}</code>\n'
        f'{em("money")} Баланс: <b>{u["balance"]:.2f}₽</b>\n'
        f'📅 В боте с: <b>{u["created_at"].strftime("%d.%m.%Y")}</b>\n\n'
        f'━━━━━━━━━━━━━━━━━'
    )
    await bot.send_photo(
        chat_id,
        photo=IMG_USER,
        caption=caption,
        reply_markup=_profile_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "menu_profile")
async def show_profile(cb: CallbackQuery, bot: Bot):
    u = await db.get_user(cb.from_user.id)
    if not u:
        return await cb.answer("❌ Профиль не найден. Напишите /start", show_alert=True)
    if u["is_blocked"]:
        return await cb.answer("🚫 Вы заблокированы в боте.", show_alert=True)

    tg = cb.from_user
    un = f"@{tg.username}" if tg.username else "—"
    caption = (
        f'━━━━━━━━━━━━━━━━━\n'
        f'       👤 <b>ПРОФИЛЬ</b>\n'
        f'━━━━━━━━━━━━━━━━━\n\n'
        f'       🎮 <b>{u.get("game_id", "Не указан")}</b>\n\n'
        f'━━━━━━━━━━━━━━━━━\n\n'
        f'📛 Имя: <b>{tg.first_name}</b>\n'
        f'🔗 Username: <b>{un}</b>\n'
        f'🆔 ID: <code>{tg.id}</code>\n'
        f'{em("money")} Баланс: <b>{u["balance"]:.2f}₽</b>\n'
        f'📅 В боте с: <b>{u["created_at"].strftime("%d.%m.%Y")}</b>\n\n'
        f'━━━━━━━━━━━━━━━━━'
    )
    try:
        await cb.message.edit_caption(
            caption=caption,
            reply_markup=_profile_kb(),
            parse_mode="HTML",
        )
    except Exception:
        # Если редактировать нельзя (сообщение без фото / уже удалено) — шлём новое
        try:
            await cb.message.delete()
        except Exception:
            pass
        await bot.send_photo(
            cb.from_user.id,
            photo=IMG_USER,
            caption=caption,
            reply_markup=_profile_kb(),
            parse_mode="HTML",
        )
    await cb.answer()


@router.callback_query(F.data == "open_webapp")
async def open_webapp_hint(cb: CallbackQuery):
    """Подсказка: кнопка WebApp открывается только через InlineKeyboardButton с web_app."""
    await cb.answer("Используйте кнопку 🎰 в главном меню (/start)", show_alert=True)


@router.callback_query(F.data == "prof_change_id")
async def change_id_start(cb: CallbackQuery, state: FSMContext):
    u = await db.get_user(cb.from_user.id)
    try:
        await cb.message.edit_caption(
            caption=(
                f'✏️ Текущий ID: <code>{u.get("game_id", "—")}</code>\n\n'
                f'Введите новый Game ID:'
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="menu_profile")]
            ]),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await state.set_state(ProfState.new_game_id)
    await cb.answer()


@router.message(ProfState.new_game_id)
async def save_new_id(msg: Message, state: FSMContext, bot: Bot):
    nid = msg.text.strip()
    if len(nid) < 3:
        return await msg.answer(
            f'{em("warn")} Некорректный ID. Попробуйте снова:',
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
        try:
            await cb.message.edit_caption(
                caption=(
                    f'{em("star")} <b>Призов пока нет</b>\n\n'
                    f'Крутите рулетку и выигрывайте!'
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="◀️ Назад", callback_data="menu_profile")],
                ]),
                parse_mode="HTML",
            )
        except Exception:
            pass
        return await cb.answer()

    now = datetime.now()
    kb  = []
    txt = f'{em("star")} <b>Ваши призы:</b>\n\n'

    for p in prizes[:10]:
        if p["prize_type"] == "nothing":
            continue
        st   = "✅" if p["is_received"] else "🎁"
        txt += f"{st} <b>{p['prize_name']}</b> — {p['won_at'].strftime('%d.%m')}\n"
        can  = (
            not p["is_received"]
            and now - p["won_at"] >= timedelta(seconds=PRIZE_TRANSFER_DELAY)
        )
        if can:
            kb.append([InlineKeyboardButton(
                text=f"📤 Передать: {p['prize_name'][:20]}",
                callback_data=f"tr_{p['id']}",
            )])

    kb.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu_profile")])
    try:
        await cb.message.edit_caption(
            caption=txt,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()


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

    try:
        await cb.message.edit_caption(
            caption=(
                f'{em("rocket")} <b>Передача приза</b>\n\n'
                f'Приз: <b>{prize["prize_name"]}</b>\n\n'
                f'Отправьте команду:\n'
                f'<code>/transfer_{pid}_@username</code>\n\n'
                f'Или через Telegram ID:\n'
                f'<code>/transfer_{pid}_123456789</code>'
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="prof_prizes")]
            ]),
            parse_mode="HTML",
        )
    except Exception:
        pass
    await cb.answer()
