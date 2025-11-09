import aiosqlite
from datetime import datetime, timezone

async def init_db():
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                ref_code TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                name TEXT PRIMARY KEY,
                host_url TEXT,
                username TEXT,
                password TEXT,
                inbound_id INTEGER,
                price_per_day INTEGER DEFAULT 1
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_keys (
                user_id INTEGER,
                email TEXT UNIQUE,
                host_name TEXT,
                expiry_ms INTEGER,
                xui_client_uuid TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS promo_codes (
                code TEXT PRIMARY KEY,
                discount_type TEXT CHECK(discount_type IN ('fixed', 'percent')),
                value INTEGER,
                usage_limit INTEGER,
                used_count INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                referrer_id INTEGER,
                referred_id INTEGER UNIQUE,
                bonus_given BOOLEAN DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pending_payments (
                invoice_id TEXT PRIMARY KEY,
                user_id INTEGER,
                amount_rub INTEGER,
                created_at TEXT
            )
        """)
        await db.commit()

# --- Users ---
async def get_user(user_id: int):
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()

async def create_user(user_id: int):
    ref_code = f"ref_{user_id}"
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, balance, ref_code, created_at) VALUES (?, 0, ?, ?)",
            (user_id, ref_code, datetime.now(timezone.utc).isoformat())
        )
        await db.commit()

async def update_balance(user_id: int, amount: int):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

async def get_balance(user_id: int) -> int:
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else 0

# --- Servers ---
async def add_server(name, host_url, username, password, inbound_id, price_per_day):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
            INSERT OR REPLACE INTO servers (name, host_url, username, password, inbound_id, price_per_day)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, host_url, username, password, inbound_id, price_per_day))
        await db.commit()

async def get_servers():
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT name, price_per_day FROM servers")
        return await cursor.fetchall()

async def get_server(name):
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM servers WHERE name = ?", (name,))
        row = await cursor.fetchone()
        if row:
            return {
                "host_name": row[0],
                "host_url": row[1],
                "host_username": row[2],
                "host_pass": row[3],
                "host_inbound_id": row[4],
                "price_per_day": row[5]
            }
        return None

async def delete_server(name):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("DELETE FROM servers WHERE name = ?", (name,))
        await db.commit()

# --- Keys ---
async def save_key(user_id: int, email: str, host_name: str, expiry_ms: int, client_uuid: str):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
            INSERT INTO user_keys (user_id, email, host_name, expiry_ms, xui_client_uuid, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, email, host_name, expiry_ms, client_uuid, datetime.now(timezone.utc).isoformat()))
        await db.commit()

async def get_user_keys(user_id: int):
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM user_keys WHERE user_id = ?", (user_id,))
        return await cursor.fetchall()

async def get_key_by_email(email: str):
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM user_keys WHERE email = ?", (email,))
        row = await cursor.fetchone()
        if row:
            return {
                "user_id": row[0],
                "email": row[1],
                "host_name": row[2],
                "expiry_ms": row[3],
                "xui_client_uuid": row[4]
            }
        return None

# --- Promos & Refs ---
async def create_promo(code: str, discount_type: str, value: int, limit: int):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT INTO promo_codes (code, discount_type, value, usage_limit) VALUES (?, ?, ?, ?)",
            (code.upper(), discount_type, value, limit)
        )
        await db.commit()

async def use_promo(code: str, user_id: int):
    code = code.upper()
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM promo_codes WHERE code = ?", (code,))
        row = await cursor.fetchone()
        if not row or row[3] <= row[4]:
            return None
        bonus = row[2] if row[1] == "fixed" else None
        if bonus is None:
            return None
        await db.execute("UPDATE promo_codes SET used_count = used_count + 1 WHERE code = ?", (code,))
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (bonus, user_id))
        await db.commit()
        return bonus

async def add_referral(referrer_id: int, referred_id: int):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
            (referrer_id, referred_id)
        )
        await db.commit()

async def give_ref_bonus(referrer_id: int):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET balance = balance + 50 WHERE user_id = ?", (referrer_id,))
        await db.execute("UPDATE referrals SET bonus_given = 1 WHERE referrer_id = ? AND bonus_given = 0", (referrer_id,))
        await db.commit()

# --- Payments ---
async def save_pending_payment(invoice_id: str, user_id: int, amount_rub: int):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT INTO pending_payments (invoice_id, user_id, amount_rub, created_at) VALUES (?, ?, ?, ?)",
            (invoice_id, user_id, amount_rub, datetime.now(timezone.utc).isoformat())
        )
        await db.commit()

async def get_pending_payment(invoice_id: str):
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute("SELECT * FROM pending_payments WHERE invoice_id = ?", (invoice_id,))
        return await cursor.fetchone()

async def delete_pending_payment(invoice_id: str):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("DELETE FROM pending_payments WHERE invoice_id = ?", (invoice_id,))
        await db.commit()