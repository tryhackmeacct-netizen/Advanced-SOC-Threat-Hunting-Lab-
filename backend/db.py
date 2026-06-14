import os
from typing import Optional
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
db = None

def init_db():
    global client, db
    if MONGO_URI:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        # default database name fallback
        dbname = os.getenv("MONGO_DB", "advanced_soc")
        db = client[dbname]
    else:
        db = None

def close_db():
    global client
    if client:
        client.close()
