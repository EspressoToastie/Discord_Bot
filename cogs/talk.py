import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import openai
import os

class talk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversation_history = []

        openai.api_key = os.getenv("OPENAI_KEY")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if the message is from the desired channel
        if message.content == "clear123":
            self.conversation_history = []
        if message.channel.id == 958869500378353705:
            # Check if the message is from the bot to avoid an infinite loop
            if message.author == self.bot.user:
                return
            input_text = message.content
            self.conversation_history.append({"role": "user", "content": input_text})
            assistant_response = await self.summarize_with_gpt3(self.conversation_history)  # Await the async call
            await message.channel.send(assistant_response)

    # Make this function async
    async def summarize_with_gpt3(self, text):
        response = await openai.ChatCompletion.acreate(  # Use 'acreate' for async API calls
            model="gpt-4o-mini",  # Use the chat model
            messages=[
                {"role": "system", "content": "Let’s have some fun! Keep things light, humorous, and engaging!"},
                *self.conversation_history
            ],
            max_tokens=400,  # Adjust as needed
            temperature=1.25,  # Adjust as needed
        )
        assistant_reply = response['choices'][0]['message']['content'].strip()
        self.conversation_history.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply

# Use async setup
async def setup(Bot):
    await Bot.add_cog(talk(Bot))
