import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View, Button
import random
import requests
from pymongo import MongoClient
import asyncio
import os

cluster = MongoClient(os.getenv("MONGO_DB_URL"))

economyv = cluster["discord"]['economy']
leveling = cluster["discord"]['leveling']
    
class utils(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @app_commands.command(description="Valorant Options",
                   name="valorant")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def valorant(self, inter):
        select = Select(
        placeholder="Valorant Options!",
        options=[
            discord.SelectOption(label="Agent Radomizer",
                                 value="0x1",
                                 emoji="<:ValorantAgent:1042132928982954106>",
                                 description="Randomizer for Agent Selection"),
            discord.SelectOption(
                label="Match Challenge",
                value="0x2",
                emoji="<:ValorantChallenge:1042130053183569920>",
                description="Randomizer for Challenge Selection"),
        ],
    )

        async def my_callback(interaction):
            if select.values[0] == "0x1":
                with open('data/vAgent.txt', 'r') as f:
                    mylines = []
                    for myline in f:
                        mylines.append(myline)
                    lines = random.choice(mylines)
                    agent, pic = lines.split(' ')
                    print(agent)
                    print(pic)
                emb5 = discord.Embed(title=f"Agent Randomizer", colour=0xf9d8b7)
                emb5.set_image(url=f"{pic}")
                emb5.set_footer(text=f"Used by: {inter.user.name}")
                emb5.add_field(name=f"Agent:", value=f"{agent}")
                await interaction.response.send_message(embed=emb5)

            if select.values[0] == "0x2":
                mylines = []
                with open('data/vChallenges.txt', 'rt') as myfile:
                    for myline in myfile:
                        mylines.append(myline)
                        challenge = random.choice(mylines)
                embed1 = discord.Embed(title="Valorant Match Challenge",
                                   colour=0xf9d8b7)
                embed1.add_field(name=f"Challenge for the game is: ",
                             value=f"{challenge}",
                             inline=False)
                embed1.set_footer(text=f"Used by: {inter.user.name}")
                await interaction.response.send_message(embed=embed1)

        select.callback = my_callback
        view = discord.ui.View(timeout=None)
        view.add_item(select)

        await inter.response.send_message("Valorant Options", view=view)
        
    @app_commands.command(name="poll", description="Create a poll")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx, *, question: str):
        emb = discord.Embed(title="Poll", description=f"{question}", colour=0xf9d8b7)
        emb.set_footer(text=f"Used by:{ctx.user.name}")
        await ctx.response.send_message(embed=emb)
        message = await ctx.original_response()
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        

async def setup(Bot):
    await Bot.add_cog(utils(Bot))
