from aiogram import Router, F
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
    game_id = State()


def _main_kb():
    """Главная клавиатура: WebApp + Профиль."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎰 Открыть рулетку",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/webapp"),
        )],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile")],
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

    if user and user["is_blocked"]:
        return await msg.answer(
            f"{em('warn')} <b>Вы заблокированы.</b>\n\nОбратитесь к администратору: @CodeTMG",
            parse_mode="HTML",
        )

    # Если Game ID ещё не задан — просим ввести
    if not user.get("game_id"):
        await msg.answer_photo(
            photo=IMG_USER,
            caption=(
                f'{em("wave")} <b>Привет, {msg.from_user.first_name}!</b>\n\n'
                f'{em("star")} Добро пожаловать в <b>Tank Blitz Roulette</b>!\n\n'
                f'{em("rocket")} Для начала введите ваш <b>Game ID</b> в Tank Blitz:'
            ),
            parse_mode="HTML",
        )
        await state.set_state(Reg.game_id)
        return

    await msg.answer_photo(
        photo=IMG_USER,
        caption=(
            f'{em("wave")} <b>Привет, {msg.from_user.first_name}!</b>\n\n'
            f'{em("star")} Добро пожаловать в <b>Tank Blitz Roulette</b>!\n'
            f'{em("rocket")} Крути рулетку — выигрывай призы!'
        ),
        reply_markup=_main_kb(),
        parse_mode="HTML",
    )


@router.message(Reg.game_id)
async def process_game_id(msg: Message, state: FSMContext):
    gid = msg.text.strip()
    if len(gid) < 3:
        return await msg.answer(
            f'{em("warn")} <b>Некорректный ID!</b> Введите снова:',
            parse_mode="HTML",
        )
    await db.update_game_id(msg.from_user.id, gid)
    await state.clear()
    await msg.answer_photo(
        photo=IMG_USER,
        caption=(
            f'{em("check")} Game ID <code>{gid}</code> сохранён!\n\n'
            f'{em("star")} Теперь можете открыть рулетку:'
        ),
        reply_markup=_main_kb(),
        parse_mode="HTML",
    )
