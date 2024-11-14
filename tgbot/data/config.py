import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv('BOT_TOKEN')
CHANNEL_ID: str = os.getenv('CHANNEL_ID')
NOTION_TOKEN: str = os.getenv("NOTION_API_TOKEN")
NOTION_DATABASE_ID: str = os.getenv("NOTION_DATABASE_ID")

