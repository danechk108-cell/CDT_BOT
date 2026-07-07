from aiogram import Router, F, Bot
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
            f'{em("rocket")} <b>Панель администратора</b>\n\n'
            f'Уровень: <b>{LEVEL_NAMES.get(lvl, lvl)}</b>\n'
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
            f'{em("rocket")} <b>Панель администратора</b>\n\n'
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
            f'{em("check")} <b>Аккаунт добавлен!</b>\n\n'
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
            f'👤 <b>@{name}</b>\n'
            f'🆔 <code>{uid}</code>\n'
            f'🎮 Game ID: <code>{u.get("game_id", "—")}</code>\n'
            f'{em("money")} Баланс: <b>{u["balance"]:.2f}₽</b>\n'
            f'📊 Статус: {status}'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Баланс", callback_data=f"adm_ba_{uid}"),
                InlineKeyboardButton(text="➖ Баланс", callback_data=f"adm_br_{uid}"),
            ],
            [InlineKeyboardButton(text="🎁 Забрать приз",  callback_data=f"adm_tp_{uid}")],
            [InlineKeyboardButton(text="🎀 Выдать приз",   callback_data=f"adm_gp_{uid}")],
            [InlineKeyboardButton(text="📋 История призов", callback_data=f"adm_ph_{uid}_0")],
            [InlineKeyboardButton(
                text="✅ Разблокировать" if u["is_blocked"] else "🚫 Заблокировать",
                callback_data=f"adm_bl_{uid}",
            )],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adm_users")],
        ]),
        parse_mode="HTML",
    )


# ── prize history for admin ────────────────────────────────────────────────────

PRIZES_PER_PAGE = 8

@router.callback_query(F.data.startswith("adm_ph_"))
async def adm_prize_history(cb: CallbackQuery):
    if not await is_adm(cb.from_user.id, "admin"):
        return await cb.answer("❌", show_alert=True)

    parts = cb.data[7:].split("_")
    uid   = int(parts[0])
    page  = int(parts[1]) if len(parts) > 1 else 0

    prizes = await db.get_all_user_prizes_history(uid)
    u      = await db.get_user(uid)
    name   = u.get("username") or u.get("first_name", str(uid)) if u else str(uid)

    if not prizes:
        return await cb.message.edit_caption(
            caption=f'📋 <b>@{name}</b> — призов нет за всё время.',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Назад", callback_data=f"adm_u_{uid}")]
            ]),
            parse_mode="HTML",
        )

    total  = len(prizes)
    pages  = (total + PRIZES_PER_PAGE - 1) // PRIZES_PER_PAGE
    page   = max(0, min(page, pages - 1))
    chunk  = prizes[page * PRIZES_PER_PAGE : (page + 1) * PRIZES_PER_PAGE]

    type_icons = {"balance": "💰", "account": "🤖", "gold": "⭐", "nothing": "😔"}
    lines = []
    for p in chunk:
        icon   = type_icons.get(p["prize_type"], "🎁")
        status = "✅" if p["is_received"] else ("🎁" if p["prize_type"] != "nothing" else "—")
        date   = p["won_at"].strftime("%d.%m.%y %H:%M")
        lines.append(f'{icon} {status} <b>{p["prize_name"]}</b>\n      📅 {date}')

    caption = (
        f'📋 <b>История призов: @{name}</b>\n'
        f'Всего: {total} | Страница {page + 1}/{pages}\n\n'
        + "\n\n".join(lines)
    )

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"adm_ph_{uid}_{page - 1}"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"adm_ph_{uid}_{page + 1}"))

    kb_rows = []
    if nav:
        kb_rows.append(nav)
    kb_rows.append([InlineKeyboardButton(text="◀️ К профилю", callback_data=f"adm_u_{uid}")])

    await cb.message.edit_caption(
        caption=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows),
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
            f'{em("money")} <b>Баланс изменён</b>\n\n'
            f'Изменение: <b>{sign}{val}₽</b>\n'
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
            f'{em("money")} Баланс изменён администратором: <b>{sign}{abs(val)}₽</b>\n'
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
    # Обновляем экран пользователя напрямую без мутации cb.data
    u2     = await db.get_user(uid)
    name2  = u2.get('username') or u2.get('first_name', '?')
    status2 = '🔴 Заблокирован' if u2['is_blocked'] else '🟢 Активен'
    await cb.message.edit_caption(
        caption=(
            f'👤 <b>@{name2}</b>\n'
            f'🆔 <code>{uid}</code>\n'
            f'🎮 Game ID: <code>{u2.get("game_id", "—")}</code>\n'
            f'{em("money")} Баланс: <b>{u2["balance"]:.2f}₽</b>\n'
            f'📊 Статус: {status2}'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Баланс", callback_data=f"adm_ba_{uid}"),
                InlineKeyboardButton(text="➖ Баланс", callback_data=f"adm_br_{uid}"),
            ],
            [InlineKeyboardButton(text="🎁 Забрать приз",  callback_data=f"adm_tp_{uid}")],
            [InlineKeyboardButton(text="🎀 Выдать приз",   callback_data=f"adm_gp_{uid}")],
            [InlineKeyboardButton(text="📋 История призов", callback_data=f"adm_ph_{uid}_0")],
            [InlineKeyboardButton(
                text="✅ Разблокировать" if u2["is_blocked"] else "🚫 Заблокировать",
                callback_data=f"adm_bl_{uid}",
            )],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adm_users")],
        ]),
        parse_mode="HTML",
    )


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
                f'{em("bell")} Приз отозван\n'
                f'Администратор: {cb.from_user.id}\n'
                f'У пользователя: {uid}\n'
                f'Приз: {p["prize_name"]}',
                parse_mode="HTML",
            )
        except Exception:
            pass
    # Обновляем экран пользователя напрямую без мутации cb.data
    u2     = await db.get_user(uid)
    name2  = u2.get('username') or u2.get('first_name', '?')
    status2 = '🔴 Заблокирован' if u2['is_blocked'] else '🟢 Активен'
    await cb.message.edit_caption(
        caption=(
            f'👤 <b>@{name2}</b>\n'
            f'🆔 <code>{uid}</code>\n'
            f'🎮 Game ID: <code>{u2.get("game_id", "—")}</code>\n'
            f'{em("money")} Баланс: <b>{u2["balance"]:.2f}₽</b>\n'
            f'📊 Статус: {status2}'
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Баланс", callback_data=f"adm_ba_{uid}"),
                InlineKeyboardButton(text="➖ Баланс", callback_data=f"adm_br_{uid}"),
            ],
            [InlineKeyboardButton(text="🎁 Забрать приз",  callback_data=f"adm_tp_{uid}")],
            [InlineKeyboardButton(text="🎀 Выдать приз",   callback_data=f"adm_gp_{uid}")],
            [InlineKeyboardButton(text="📋 История призов", callback_data=f"adm_ph_{uid}_0")],
            [InlineKeyboardButton(
                text="✅ Разблокировать" if u2["is_blocked"] else "🚫 Заблокировать",
                callback_data=f"adm_bl_{uid}",
            )],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="adm_users")],
        ]),
        parse_mode="HTML",
    )


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
                f'{em("robot")} <b>Администратор выдал вам аккаунт!</b>\n\n'
                f'📧 Email: <code>{d["gp_email"]}</code>\n'
                f'🔑 Пароль: <code>{pwd}</code>\n\n'
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
                f'{em("bell")} Аккаунт выдан вручную\n'
                f'Администратор: {msg.from_user.id}\n'
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
                f'{em("star")} <b>Администратор выдал вам Голду!</b>\n\n'
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
                f'{em("bell")} Голда выдана вручную\n'
                f'Администратор: {msg.from_user.id}\n'
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
            f'{em("globe")} <b>Общая статистика</b>\n\n'
            f'👥 Пользователей: <b>{s["total_users"]}</b>\n'
            f'🎰 Прокрутов: <b>{s["total_spins"]}</b>\n'
            f'🎁 Призов выдано: <b>{s["total_prizes"]}</b>\n'
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
    lines  = "\n".join(
        f'{LEVEL_NAMES.get(a["level"], a["level"])} — '
        f'@{a["username"] or a["telegram_id"]}'
        for a in admins
    )
    await cb.message.edit_caption(
        caption=f'🛡️ <b>Администраторы ({len(admins)})</b>\n\n{lines or "Список пуст"}',
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
    lines        = "\n".join(
        f'• {p["user_id"]} — {p["won_at"].strftime("%d.%m.%Y")}'
        for p in items[:15]
    )
    await cb.message.edit_caption(
        caption=(
            f'{tname} ({label})\n\n'
            f'Всего: <b>{len(items)}</b>\n\n'
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
            f'🛡️ <b>{name}</b>\n'
            f'🆔 <code>{tid}</code>\n'
            f'📌 Уровень: {level}\n'
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
    # Обновляем список без мутации cb.data
    admins2 = await db.get_all_admins()
    kb2 = []
    for a in admins2:
        if a['telegram_id'] == OWNER_ID:
            continue
        name3  = f"@{a['username']}" if a.get('username') else str(a['telegram_id'])
        level3 = LEVEL_NAMES.get(a['level'], a['level'])
        kb2.append([InlineKeyboardButton(
            text=f"{level3} {name3}",
            callback_data=f"adm_adm_info_{a['telegram_id']}",
        )])
    kb2.append([InlineKeyboardButton(text='➕ Добавить', callback_data='adm_adm_add')])
    kb2.append([InlineKeyboardButton(text='◀️ Назад',    callback_data='adm_back_main')])
    await cb.message.edit_caption(
        caption=f'🛡️ <b>Администраторы ({len(admins2)}):</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb2),
        parse_mode='HTML',
    )


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
            f'{em("warn")} <b>Удалить администратора?</b>\n\n'
            f'👤 {name}\n'
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
    # Обновляем список без мутации cb.data
    admins2 = await db.get_all_admins()
    kb2 = []
    for a in admins2:
        if a['telegram_id'] == OWNER_ID:
            continue
        name3  = f"@{a['username']}" if a.get('username') else str(a['telegram_id'])
        level3 = LEVEL_NAMES.get(a['level'], a['level'])
        kb2.append([InlineKeyboardButton(
            text=f"{level3} {name3}",
            callback_data=f"adm_adm_info_{a['telegram_id']}",
        )])
    kb2.append([InlineKeyboardButton(text='➕ Добавить', callback_data='adm_adm_add')])
    kb2.append([InlineKeyboardButton(text='◀️ Назад',    callback_data='adm_back_main')])
    await cb.message.edit_caption(
        caption=f'🛡️ <b>Администраторы ({len(admins2)}):</b>',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb2),
        parse_mode='HTML',
    )


@router.callback_query(F.data == "adm_adm_add")
async def adm_adm_add(cb: CallbackQuery, state: FSMContext):
    if await adm_level(cb.from_user.id) != "head":
        return await cb.answer("❌", show_alert=True)
    await cb.message.edit_caption(
        caption=(
            f'{em("globe")} <b>Добавление администратора</b>\n\n'
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
            f'{em("warn")} Пользователь не найден!\n'
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
            f'👤 <b>{name}</b> (<code>{target["telegram_id"]}</code>)\n\n'
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
            f'{em("check")} <b>Администратор добавлен!</b>\n\n'
            f'👤 {name}\n'
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
                f'{em("bell")} <b>Вы назначены администратором!</b>\n\n'
                f'📌 Уровень: <b>{LEVEL_NAMES[lvl]}</b>\n\n'
                f'Используйте /cdta для входа в панель.'
            ),
            parse_mode="HTML",
        )
    except Exception:
        pass
