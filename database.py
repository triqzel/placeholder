import aiosqlite
from config import DATABASE_URL

db_path = DATABASE_URL.replace("sqlite:///", "")


async def init_db():
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                autorole_enabled INTEGER DEFAULT 0,
                autorole_id INTEGER,
                autorole_admins TEXT
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS voice_channels (
                channel_id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                owner_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


async def get_db():
    return await aiosqlite.connect(db_path)


async def set_autorole(guild_id, role_id):
    async with await get_db() as db:
        await db.execute(
            "INSERT OR REPLACE INTO guild_settings (guild_id, autorole_id, autorole_enabled) VALUES (?, ?, 1)",
            (guild_id, role_id),
        )
        await db.commit()


async def get_autorole(guild_id):
    async with await get_db() as db:
        cursor = await db.execute(
            "SELECT autorole_id FROM guild_settings WHERE guild_id = ?", (guild_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def add_voice_channel(channel_id, guild_id, owner_id):
    async with await get_db() as db:
        await db.execute(
            "INSERT INTO voice_channels (channel_id, guild_id, owner_id) VALUES (?, ?, ?)",
            (channel_id, guild_id, owner_id),
        )
        await db.commit()


async def remove_voice_channel(channel_id):
    async with await get_db() as db:
        await db.execute("DELETE FROM voice_channels WHERE channel_id = ?", (channel_id,))
        await db.commit()


async def get_voice_channel_owner(channel_id):
    async with await get_db() as db:
        cursor = await db.execute(
            "SELECT owner_id FROM voice_channels WHERE channel_id = ?", (channel_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None
