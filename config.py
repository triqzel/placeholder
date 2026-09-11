import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot.db")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN not set in .env file")
