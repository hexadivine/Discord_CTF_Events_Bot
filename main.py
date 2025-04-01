import discord
import asyncio
import os
import time
import datetime
from flask import Flask
import threading
import uuid

from ctftime_client import filter_fetched_events, more_about_event

from config import TOKEN, THREAD_ARCHIVE_DURATION, CHANNEL_ID, FETCH_NEW_EVENTS_AFTER_DURATION
from config import CLIENT as client

from utils import format_timestamp


async def send_messages():
    await client.wait_until_ready()  
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        return

    while not client.is_closed():
        try:
            events = filter_fetched_events()

            for event in events:
                more_event_info = more_about_event(event['id'])
                prizes = ""
                if more_event_info['prizes'] != "":
                    prizes =  f"\n\n**Prizes:** \n{more_event_info['prizes']}" 

                embed = discord.Embed(
                    title=f"📌 {event['title']}",
                    description=f"**Description:**\n"
                        f"{more_event_info['description']}"
                        f"{prizes}"
                        f"\n\n**React with 🔥 if you would like play**\n\n"
                        f"🕒 **Start:** {format_timestamp(event['start'])}\n"
                        f"⏳ **End:** {format_timestamp(event['finish'])}\n\n"
                        f"🔗 [Event Link]({event['url']})",
                    color=discord.Color.green()
                )

                embed.set_image(url=more_event_info['logo'])

                await channel.send(embed=embed)

            await asyncio.sleep(FETCH_NEW_EVENTS_AFTER_DURATION) 
        except Exception as e:
            print(e)
            await asyncio.sleep(FETCH_NEW_EVENTS_AFTER_DURATION//24)


@client.event
async def on_reaction_add(reaction, user):
    """ Triggered when a user reacts to a message. """
    if user.bot:
        return

    if reaction.emoji == "🔥": 
        message = reaction.message
        channel = message.channel

        if channel.id != CHANNEL_ID:
            return

        embed = reaction.message.embeds[0] if reaction.message.embeds else None

        thread_name = f'custom-thread-by-{message.author}#{uuid.uuid4()}'
        if  embed and embed.title:
            thread_name = embed.title

        thread = await message.create_thread(name=thread_name, auto_archive_duration=THREAD_ARCHIVE_DURATION/60)
        
        await thread.send(f"Thread will auto-close in {THREAD_ARCHIVE_DURATION//(24*60*60)} Days")

        # Auto-close thread after some time
        await asyncio.sleep(THREAD_ARCHIVE_DURATION)
        await thread.edit(archived=True)
        await channel.send(f"{thread.name} Thread has been archived! 💤")


@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')
    client.loop.create_task(send_messages())


# Create a Flask web server 
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running!"


def run_flask():
    """ Runs the Flask server to keep the bot alive. """
    app.run(host="0.0.0.0", port=8080)


if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    client.run(TOKEN)