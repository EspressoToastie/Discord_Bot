import discord
from discord import app_commands
from discord.ext import commands
import random
from discord.ui import Select, View, Button
from discord import Embed


class fun(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @app_commands.command(description="Flip a coin", name="flip")
    @app_commands.guilds(discord.Object(id=774417580932857856))
    async def flip(self, inter):
        flip = ["Heads", "Tails"]
        emb3 = discord.Embed(title=f"Coin Flip", colour=0xf9d8b7)
        emb3.set_footer(text=f"Used by: {inter.user.name}")
        emb3.add_field(name=f"Result: {random.choice(flip)}",
                       value=f" ")
        await inter.response.send_message(embed=emb3)

    @app_commands.command(description="Play some 8ball", name="8ball")
    @app_commands.guilds(discord.Object(id=774417580932857856))
    async def ball(self, inter, *, question: str):
        ball = [
            "As I see it, yes.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don’t count on it.", "It is certain.", "Most likely.",
            "My reply is no.", "My sources say no.", "Outlook not so good.",
            "Outlook good.", "Reply hazy, try again.", "Signs point to yes.",
            "Very doubtful.", "Without a doubt.", "Yes.", "Yes – definitely.",
            "You may rely on it."
        ]
        emb3 = discord.Embed(title=f"8ball", colour=0xf9d8b7)
        emb3.set_footer(text=f"Used by: {inter.user.name}")
        emb3.add_field(name=f"Question: {question}",
                       value=f"Answer: {random.choice(ball)}")
        await inter.response.send_message(embed=emb3)

    @app_commands.command(description="Yes/No Picker", name="yn")
    @app_commands.guilds(discord.Object(id=774417580932857856))
    async def yn(self, inter, *, question: str):
        yn = ("Yes", "No")
        emb3 = discord.Embed(title=f"Yes/No", color=0xf9d8b7)
        emb3.set_footer(text=f"Used by: {inter.user.name}")
        emb3.add_field(name=f"Question: {question}",
                       value=f"Answer: {random.choice(yn)}")
        await inter.response.send_message(embed=emb3)

    @app_commands.command(description="Percentage of ;choice; to happen",
                            name="percent")
    @app_commands.guilds(discord.Object(id=774417580932857856))
    async def percent(self, inter, *, question: str):
        percent1 = [
            "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 100%", "🟩🟩🟩🟩🟩🟩🟩🟩🟩🟥 90%", "🟩🟩🟩🟩🟩🟩🟩🟩🟥🟥 80%",
            "🟩🟩🟩🟩🟩🟩🟩🟥🟥🟥 70%", "🟩🟩🟩🟩🟩🟩🟥🟥🟥🟥 60%", "🟩🟩🟩🟩🟩🟥🟥🟥🟥🟥 50%",
            "🟩🟩🟩🟩🟥🟥🟥🟥🟥🟥 40%", "🟩🟩🟩🟥🟥🟥🟥🟥🟥🟥 30%", "🟩🟩🟥🟥🟥🟥🟥🟥🟥🟥 20%",
            "🟩🟥🟥🟥🟥🟥🟥🟥🟥🟥 10%", "🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥 0%"
        ]
        emb3 = discord.Embed(title=f"Percent", colour=0xf9d8b7)
        emb3.set_footer(text=f"Used by: {inter.user.name}")
        emb3.add_field(name=f"Question: {question}",
                       value=f"Answer: {random.choice(percent1)}")
        await inter.response.send_message(embed=emb3)

    @app_commands.command(description="Roll a dice", name="roll")
    @app_commands.guilds(discord.Object(id=774417580932857856))
    async def roll(self, inter):
        dice = [1, 2, 3, 4, 4, 5, 6]
        await inter.response.send_message(f"You got: {random.choice(dice)}")

    @app_commands.command(description="Ping Pong", name="ping")
    @app_commands.guilds(discord.Object(id=774417580932857856))
    async def ping(self, inter):
        await inter.response.send_message("Pong")

    @app_commands.command(description="Bing bong", name="bing")
    @app_commands.guilds(discord.Object(id=774417580932857856))
    async def bing(self, inter):
        await inter.response.send_message(f"bong")
            

async def setup(Bot):
    await Bot.add_cog(fun(Bot))
