import discord
from discord.ext import commands
import random
from discord import app_commands
import requests
import io
import openai

import asyncpg
import asyncio
import pytz

from datetime import datetime, time as dtime, timedelta, timezone
import pymongo
from pymongo import MongoClient
import os


cluster = MongoClient(os.getenv("MONGO_DB_URL"))

history = cluster["global_commands"]['chat_history_commands']

class acommands(commands.Cog):
    def __init__(self, Bot):
        self.bot = Bot
        self.conversation_history = []
        self.flux_temperature = 1.25
        self.flux_token = 250


    @app_commands.command(name='cat')
    async def cat(self, inter):
        cat = random.randint(1, 1000)
        url = (f"https://cataas.com/cat?random={cat}")
        print(url)
        image = requests.get(url).content
        file = discord.File(fp=io.BytesIO(image), filename="cat.png")
        emb3 = discord.Embed(title=f"Silly Cat", colour=0xf9d8b7)
        emb3.set_image(url="attachment://cat.png")
        emb3.timestamp = datetime.now()
        await inter.response.send_message(embed=emb3, file=file)


    @app_commands.command(name='chat')
    async def chat(self, inter, topic: str):
        await inter.response.defer()
        self.conversation_history.append({"role": "user", "content": topic})
        assistant_response = await self.summarize_with_gpt3(self.conversation_history)
        await inter.followup.send(assistant_response)

 
    @app_commands.command(name='remindr')
    async def remindr(self, inter: discord.Interaction, 
                        remind: str, time: str, private: bool = True):
        try:
            # parse your "HH:MM"
            reminder_hour, reminder_minute = map(int, time.split(":"))

            # Get local timezone
            local_tz = pytz.timezone("Europe/Dublin")
            now_local = datetime.now(local_tz)

            # Build local reminder time
            reminder_local = now_local.replace(hour=reminder_hour, minute=reminder_minute, second=0, microsecond=0)

            # If reminder time is earlier than now (already passed today), schedule for tomorrow
            if reminder_local < now_local:
                reminder_local += timedelta(days=1)

            # Convert to UTC for DB storage
            reminder_utc = reminder_local.astimezone(pytz.utc)

            await inter.response.send_message(f"Reminder '{remind}' set for {reminder_local.strftime('%Y-%m-%d %H:%M')}", ephemeral=private)
            message = await inter.original_response()
            message_id = message.id

            await self.bot.pg_con.execute(
                "INSERT INTO pages_remindr (name, remindertime, created, userid, channel, guildid, messageid, private, completed) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)",
                remind, reminder_utc, datetime.now(timezone.utc), str(inter.user.id), str(inter.channel.id), str(inter.guild.id), str(message_id), private, False
            )

        except Exception as e:
            await inter.response.send_message(f"Failed to set reminder: {e}")

#####################################################################


    openai.api_key = os.getenv("OPENAI_KEY")

    # Make this function async
    async def summarize_with_gpt3(self, text):
        response = await openai.ChatCompletion.acreate(  # Use 'acreate' for async API calls
            model="gpt-4o-mini",  # Use the chat model
            messages=[
                {"role": "system", "content": "Let’s have some fun! Keep things light, humorous, and engaging!"},
                *self.conversation_history
            ],
            max_tokens=self.flux_token,  # Adjust as needed
            temperature=self.flux_temperature,  # Adjust as needed
        )
        assistant_reply = response['choices'][0]['message']['content'].strip()
        self.conversation_history.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply

    
#####################################################################

async def setup(Bot):
    await Bot.add_cog(acommands(Bot))
