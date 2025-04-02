import discord
import os
from dotenv import load_dotenv


def __initialize_discord_bot():
    intents = discord.Intents.default()
    intents.messages = True  
    intents.guilds = True
    intents.message_content = True

    client = discord.Client(intents=intents)
    return client


CLIENT = __initialize_discord_bot()

THREAD_ARCHIVE_DURATION = 7*24*60*60
FETCH_OFFSET_DAYS = 5
FETCH_NEW_EVENTS_AFTER_DURATION = 24*60*60

load_dotenv()

CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
TOKEN = os.getenv('TOKEN')