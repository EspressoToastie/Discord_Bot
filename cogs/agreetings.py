import discord
from discord.ext import commands
from discord import app_commands

class agreetings(commands.Cog):
    def __init__(self, Bot):
        self.bot = Bot
        self._last_member = None


    @app_commands.command()
    @app_commands.guilds(discord.Object(id=774417580932857856))
    async def hello(self, inter):
        """Says hello"""
        member = inter.user
        await inter.response.send_message(f'Hello {member.name}')



async def setup(Bot):
    await Bot.add_cog(agreetings(Bot))
