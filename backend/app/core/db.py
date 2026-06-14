from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

client: AsyncIOMotorClient | None = None
db = None


async def init_db(mongo_uri: str, mongo_db: str = "asthl"):
    global client, db
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]


async def ping() -> bool:
    try:
        # server_info is synchronous; use admin command ping
        res = await client.admin.command("ping")
        return res.get("ok", 0) == 1
    except Exception:
        return False


def get_db():
    return db
