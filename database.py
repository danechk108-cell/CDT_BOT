import asyncpg
from datetime import datetime
from config import DATABASE_URL, OWNER_ID

pool = None


async def init_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    await _create_tables()


async def _create_tables():
    async with pool.acquire() as c:
        await c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            BIGSERIAL PRIMARY KEY,
                telegram_id   BIGINT UNIQUE NOT NULL,
                username      TEXT,
                first_name    TEXT,
                last_name     TEXT,
                game_id       TEXT,
                roulette_type TEXT,
                balance       FLOAT   DEFAULT 0.0,
                is_blocked    BOOLEAN DEFAULT FALSE,
                created_at    TIMESTAMP DEFAULT NOW(),
                updated_at    TIMESTAMP DEFAULT NOW()
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
                id               BIGSERIAL PRIMARY KEY,
                user_id          BIGINT REFERENCES users(telegram_id),
                roulette_type    TEXT NOT NULL,
                is_subscribed    BOOLEAN DEFAULT FALSE,
                is_forwarded     BOOLEAN DEFAULT FALSE,
                condition_met_at TIMESTAMP,
                UNIQUE(user_id, roulette_type)
            );
        """)
        # Миграция: добавляем roulette_type если колонки ещё нет
        await c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS roulette_type TEXT")
        await c.execute("""
            INSERT INTO admins (telegram_id, username, level, added_by)
            VALUES ($1, 'owner', 'head', $1)
            ON CONFLICT (telegram_id) DO NOTHING
        """, OWNER_ID)


# ── users ──────────────────────────────────────────────────────────────────────

async def get_user(telegram_id):
    async with pool.acquire() as c:
        return await c.fetchrow("SELECT * FROM users WHERE telegram_id=$1", telegram_id)

async def create_user(telegram_id, username, first_name, last_name=None):
    async with pool.acquire() as c:
        return await c.fetchrow("""
            INSERT INTO users (telegram_id,username,first_name,last_name)
            VALUES ($1,$2,$3,$4)
            ON CONFLICT (telegram_id) DO UPDATE
              SET username=$2,first_name=$3,last_name=$4,updated_at=NOW()
            RETURNING *
        """, telegram_id, username, first_name, last_name)

async def update_game_id(telegram_id, game_id):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE users SET game_id=$1,updated_at=NOW() WHERE telegram_id=$2",
            game_id, telegram_id)

async def update_roulette_type(telegram_id, roulette_type):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE users SET roulette_type=$1,updated_at=NOW() WHERE telegram_id=$2",
            roulette_type, telegram_id)

async def update_balance(telegram_id, amount):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE users SET balance=balance+$1,updated_at=NOW() WHERE telegram_id=$2",
            amount, telegram_id)

async def block_user(telegram_id, blocked=True):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE users SET is_blocked=$1,updated_at=NOW() WHERE telegram_id=$2",
            blocked, telegram_id)

async def get_all_users():
    async with pool.acquire() as c:
        return await c.fetch("SELECT * FROM users ORDER BY created_at DESC")


# ── spins ──────────────────────────────────────────────────────────────────────

async def get_last_spin(user_id, roulette_type):
    async with pool.acquire() as c:
        return await c.fetchrow("""
            SELECT * FROM roulette_spins
            WHERE user_id=$1 AND roulette_type=$2
            ORDER BY spun_at DESC LIMIT 1
        """, user_id, roulette_type)

async def get_user_spin_stats(user_id):
    """Возвращает статистику спинов пользователя: total, wins, biggest_win."""
    async with pool.acquire() as c:
        total = await c.fetchval(
            "SELECT COUNT(*) FROM roulette_spins WHERE user_id=$1", user_id) or 0
        wins = await c.fetchval(
            "SELECT COUNT(*) FROM roulette_spins WHERE user_id=$1 AND prize_type!='nothing'", user_id) or 0
        biggest = await c.fetchval(
            "SELECT MAX(prize_value) FROM roulette_spins WHERE user_id=$1 AND prize_type='balance'", user_id) or 0
        return {"total": int(total), "wins": int(wins), "biggest": float(biggest)}

async def add_spin(user_id, roulette_type, prize_name, prize_type, prize_value, is_paid=False):
    async with pool.acquire() as c:
        return await c.fetchrow("""
            INSERT INTO roulette_spins
              (user_id,roulette_type,prize_name,prize_type,prize_value,is_paid)
            VALUES ($1,$2,$3,$4,$5,$6) RETURNING *
        """, user_id, roulette_type, prize_name, prize_type, prize_value, is_paid)


# ── conditions ─────────────────────────────────────────────────────────────────

async def get_condition(user_id, roulette_type):
    async with pool.acquire() as c:
        return await c.fetchrow(
            "SELECT * FROM roulette_conditions WHERE user_id=$1 AND roulette_type=$2",
            user_id, roulette_type)

async def set_condition(user_id, roulette_type, subscribed, forwarded):
    met = datetime.now() if (subscribed and forwarded) else None
    async with pool.acquire() as c:
        await c.execute("""
            INSERT INTO roulette_conditions
              (user_id,roulette_type,is_subscribed,is_forwarded,condition_met_at)
            VALUES ($1,$2,$3,$4,$5)
            ON CONFLICT (user_id,roulette_type) DO UPDATE
              SET is_subscribed=$3,is_forwarded=$4,condition_met_at=$5
        """, user_id, roulette_type, subscribed, forwarded, met)


# ── prizes ─────────────────────────────────────────────────────────────────────

async def add_prize(user_id, prize_type, prize_name, prize_value=0,
                    account_email=None, account_password=None, gold_promo=None):
    async with pool.acquire() as c:
        return await c.fetchrow("""
            INSERT INTO prizes
              (user_id,prize_type,prize_name,prize_value,
               account_email,account_password,gold_promo)
            VALUES ($1,$2,$3,$4,$5,$6,$7) RETURNING *
        """, user_id, prize_type, prize_name, prize_value,
            account_email, account_password, gold_promo)

async def get_user_prizes(user_id):
    async with pool.acquire() as c:
        return await c.fetch(
            "SELECT * FROM prizes WHERE user_id=$1 ORDER BY won_at DESC", user_id)

async def get_all_user_prizes_history(user_id):
    """Все призы пользователя за всё время (включая переданные и ничего)."""
    async with pool.acquire() as c:
        return await c.fetch(
            "SELECT * FROM prizes WHERE user_id=$1 OR transferred_to=$1 ORDER BY won_at DESC",
            user_id)

async def get_prize(prize_id):
    async with pool.acquire() as c:
        return await c.fetchrow("SELECT * FROM prizes WHERE id=$1", prize_id)

async def remove_prize(prize_id):
    async with pool.acquire() as c:
        await c.execute("DELETE FROM prizes WHERE id=$1", prize_id)

async def mark_prize_received(prize_id):
    async with pool.acquire() as c:
        await c.execute(
            "UPDATE prizes SET is_received=TRUE,received_at=NOW() WHERE id=$1", prize_id)

async def transfer_prize(prize_id, to_user_id):
    async with pool.acquire() as c:
        await c.execute("""
            UPDATE prizes
            SET user_id=$1,transferred_to=$1,transferred_at=NOW()
            WHERE id=$2
        """, to_user_id, prize_id)

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
        await c.execute("""
            INSERT INTO admins (telegram_id,username,level,added_by)
            VALUES ($1,$2,$3,$4)
            ON CONFLICT (telegram_id) DO UPDATE SET level=$3,username=$2
        """, telegram_id, username, level, added_by)

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
