import discord
import asyncio
from flask import Flask
import threading
import uuid
from datetime import datetime, timezone

from ctftime_client import initial_run_filter_fetched_events, filter_fetched_events, more_about_event

from config import TOKEN, FETCH_OFFSET_DAYS, CHANNEL_ID, FETCH_NEW_EVENTS_AFTER_DURATION
from config import CLIENT as client

from utils import format_timestamp, utc_to_syd_time

from discord.ui import View, Button
import random

class JoinEventView(View):
    def __init__(self, event):
        super().__init__(timeout=None) 
        self.message = None
        self.clicked_users = set()
        self.event = event

    @discord.ui.button(label="I'll play", style=discord.ButtonStyle.green)
    async def join_event(self, interaction: discord.Interaction, button: Button):
        user = interaction.user
      
        if user in self.clicked_users:
            await interaction.response.send_message(f"<@{user.id}> you've already joined the event!", ephemeral=True)
            return

        self.clicked_users.add(user)
        await interaction.response.defer()
        # Select a random emoji from the list for fun
        emoji_list = [
            "😎", "🔥", "🎉", "💻", "🔓", "🕵️‍♂️", "👾", "🏆", "🎮", "⚡", "🤖", "🛠️", "🕒",  
            "🧠", "🔑", "🚀", "💣", "📜", "🔍", "📡", "🛡️", "💀", "🎯", "📟", "🧑‍💻",  
            "📡", "🗝️", "⚙️", "🖥️", "📁", "🔧", "🔬", "📲", "🔗", "🎲", "🕶️"
        ]
        random_emoji = random.choice(emoji_list)
        if self.message:
            await self.message.add_reaction(random_emoji)
            if self.message.thread:
                await self.message.thread.send(f'<@{user.id}> added to this thread.')
                return
            
            embed = self.message.embeds[0] if self.message.embeds else None
            thread_name = f'custom-thread#{str(uuid.uuid4())[0:4]}'
            if  embed and embed.title:
                thread_name = embed.title

            thread = await self.message.create_thread(name=thread_name)
            await thread.send(f"A thread has been created for this CTF.")
            await thread.send(f'<@{user.id}> added to this thread.')
    
            now_utc = datetime.now(timezone.utc)
            syd_start_datetime = utc_to_syd_time(self.event['start']) 
            # syd_start_datetime = utc_to_syd_time('2025-04-08T00:00:00+00:00') 
            current_syd_time = utc_to_syd_time(now_utc.isoformat())
            delay_seconds = int((syd_start_datetime - current_syd_time).total_seconds()) - 60*60

            delay_seconds = max(delay_seconds, 0)

            if (delay_seconds > 0):
                await asyncio.sleep(delay_seconds)
                await interaction.response.send_message(f"<@{user.id}>: `{self.event['title'][2:]}` CTF will start soon...", ephemeral=True)

                # players = ""
                # for user in self.clicked_users:
                #     players += f"<@{user.id}>, "
                # await thread.send(f"{players[:-2]} CTF will start in 1 hour...", )

            await asyncio.sleep(10*24*60*60)
            del self


    @discord.ui.button(label="Show players", style=discord.ButtonStyle.green)
    async def show_players(self, interaction: discord.Interaction, button: Button):
        players = ""
        for user in self.clicked_users:
            players += f"<@{user.id}>, "

        if players != "":
            await interaction.response.send_message(f"Below {len(self.clicked_users)} player{'s' if len(self.clicked_users) > 1 else ''} will participate...\n\n{players[:-2]}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Be the first to join this event", ephemeral=True)


initial_run = True
async def send_messages():
    global initial_run
    await client.wait_until_ready()  
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        return

    while not client.is_closed():
        try:
            events = []
            if initial_run:
               print('yes')
               events = initial_run_filter_fetched_events()
               initial_run = False
            else:
                events = filter_fetched_events()

            for event in events:
                more_event_info = more_about_event(event['id'])
                prizes = ""
                if more_event_info['prizes'] != "":
                    prizes =  f"🏆 **Prizes:** \n{more_event_info['prizes'][0:500]}{'...' if len(prizes) > 500 else ''} \n\n" 

                embed = discord.Embed(
                    title=f"📌 {event['title']}",
                    url=event['url'],
                    description=f"\n📑 **Description:**\n"
                        f"{more_event_info['description'][:500]}{'...' if len(more_event_info['description']) > 500 else ''} \n\n"
                        f"{prizes}"
                        f"🕒 **Start:** {format_timestamp(event['start'])}\n"
                        f"⏳ **End:** {format_timestamp(event['finish'])}\n\n"
                        f"🔗 [Event Link]({event['url']})\n\n"
                        f"|| Made with ♥️ by [hexadivine](https://hexadivine.vercel.app/) ||",
                    color=discord.Color.green()
                )
                view = JoinEventView(event) 

                embed.set_image(url=more_event_info['logo'])
                message = await channel.send(embed=embed, view=view)
                view.message = message 

            await asyncio.sleep(FETCH_NEW_EVENTS_AFTER_DURATION) 
        except Exception as e:
            print(e)
            await asyncio.sleep(FETCH_NEW_EVENTS_AFTER_DURATION//24)

"""
@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    channel = message.channel

    if channel.id != CHANNEL_ID:
        return
    if message.thread:
        return

    embed = reaction.message.embeds[0] if reaction.message.embeds else None

    thread_name = f'custom-thread#{str(uuid.uuid4())[0:4]}'
    if  embed and embed.title:
        thread_name = embed.title

    thread = await message.create_thread(name=thread_name)

    await thread.send(f"A thread has been created for this CTF.")
    await thread.send(f'<@{user.id}> added to this thread.')

    # Auto-close thread after some time
    await asyncio.sleep(FETCH_OFFSET_DAYS*23*60*60)
    await thread.send(f"CTF will start soon...")
"""

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')
    client.loop.create_task(send_messages())


# Create a Flask web server 
#app = Flask(__name__)


#@app.route("/")
#def home():
#    return "Bot is running!"


#def run_flask():
#    """ Runs the Flask server to keep the bot alive. """
#    app.run(host="0.0.0.0", port=8080)


if __name__ == '__main__':
#    flask_thread = threading.Thread(target=run_flask, daemon=True)
#    flask_thread.start()
    client.run(TOKEN)
