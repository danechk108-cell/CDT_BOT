from config import REQUIRED_CHANNELS


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
