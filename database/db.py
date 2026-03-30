import aiosqlite
from datetime import datetime, timezone
from config import settings

DB_PATH = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER NOT NULL,
                username  TEXT,
                message   TEXT NOT NULL,
                language  TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        await db.commit()


async def save_message(user_id: int, username: str | None, message: str, language: str):
    ts = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (user_id, username, message, language, timestamp) VALUES (?,?,?,?,?)",
            (user_id, username or "", message, language, ts),
        )
        await db.commit()


async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Total unique users
        async with db.execute("SELECT COUNT(DISTINCT user_id) AS c FROM messages") as cur:
            total_users = (await cur.fetchone())["c"]

        # Messages all time
        async with db.execute("SELECT COUNT(*) AS c FROM messages") as cur:
            total_all = (await cur.fetchone())["c"]

        # Messages today
        async with db.execute(
            "SELECT COUNT(*) AS c FROM messages WHERE date(timestamp) = date('now')"
        ) as cur:
            total_today = (await cur.fetchone())["c"]

        # Messages this week
        async with db.execute(
            "SELECT COUNT(*) AS c FROM messages WHERE timestamp >= datetime('now', '-7 days')"
        ) as cur:
            total_week = (await cur.fetchone())["c"]

        # Top languages
        async with db.execute(
            "SELECT language, COUNT(*) AS c FROM messages GROUP BY language ORDER BY c DESC"
        ) as cur:
            lang_rows = await cur.fetchall()
        top_langs = [(r["language"], r["c"]) for r in lang_rows]

        # Most active users (top 5)
        async with db.execute(
            "SELECT username, user_id, COUNT(*) AS c FROM messages "
            "GROUP BY user_id ORDER BY c DESC LIMIT 5"
        ) as cur:
            user_rows = await cur.fetchall()
        top_users = [(r["username"] or str(r["user_id"]), r["c"]) for r in user_rows]

    return {
        "total_users": total_users,
        "total_all": total_all,
        "total_today": total_today,
        "total_week": total_week,
        "top_langs": top_langs,
        "top_users": top_users,
    }


async def get_recent_logs(limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT username, user_id, message, timestamp "
            "FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        ) as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_recent_users(limit: int = 10) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT username, user_id, COUNT(*) AS msg_count, MAX(timestamp) AS last_seen "
            "FROM messages GROUP BY user_id ORDER BY last_seen DESC LIMIT ?",
            (limit,),
        ) as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]
