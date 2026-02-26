import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import datetime, math
from datetime import datetime, timedelta
import time
import random
from math import ceil, floor
import os 



class mod(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot
        self._last_member = None

    @app_commands.command(name="add_role", description=f"Add role to member")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @app_commands.checks.has_permissions(manage_roles=True)
    async def add_role(self, inter, role: discord.Role, member: discord.Member):
        await member.add_roles(role, reason="Added Through Slash Command")
        await inter.response.send_message(f"Added the role {role} to {member}!")
         
    @add_role.error
    async def add_role_error(self, ctx, error):
        if isinstance(error, app_commands.MissingRequiredArgument):
            await ctx.response.send_message(error, ephemeral=True)
            
    @app_commands.command(name="remove_role",
                            description=f"Remove role to member")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @app_commands.checks.has_permissions(manage_roles=True)
    async def remove_role(self, inter, role: discord.Role,
                          member: discord.Member):
        await member.remove_roles(role, reason="Added Through Slash Command")
        await inter.response.send_message(
            f"Removed the role {role} to {member}!")

    @remove_role.error
    async def remove_role_error(self, ctx, error):
        if isinstance(error, app_commands.MissingRequiredArgument):
            await ctx.response.send_message(error, ephemeral=True)
            
    @app_commands.command(description="Purge away the crimes", name="purge")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, ctx, *, amount: int):
        await ctx.channel.purge(limit=amount)
        await ctx.response.send_message(f"{(amount)} messages purged!")

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, app_commands.MissingRequiredArgument):
            await ctx.response.send_message(error, ephemeral=True)

    @app_commands.command(description="Move all users to another vc", name="vc")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @app_commands.checks.has_permissions(manage_messages=True)
    async def vc(ctx, move: discord.VoiceChannel):
        voiceget = ctx.author.voice.channel
        if voiceget == None:
            await ctx.response.send_message("You are not in a vc", ephemeraL=True)
        members = voiceget.members #finds members connected to the channel
        await ctx.response.send_message(f"Moving users to <#{move.id}>")
        memids = [] #(list)
        for member in members:
            memids.append(member.id)
            await member.move_to(move)
      
    @vc.error
    async def vc_error(self, ctx, error):
        if isinstance(error, app_commands.MissingRequiredArgument):
            await ctx.response.send_message(error, ephemeral=True)

    @app_commands.command(description="Split Players evenly into two teams", name="team-split")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @app_commands.checks.has_permissions(manage_messages=True)
    async def teamsplit(ctx, team1 : discord.VoiceChannel, team2 : discord.VoiceChannel):
        if team1 == team2:
            await ctx.response.send_message("You choose two of the same vc's", ephemeral=True)
            return
        
        if ctx.author.voice is None:
            await ctx.response.send_message("You are not in a vc", ephemeral=True)
            return
        
        members = ctx.author.voice.channel.members #finds members connected to the channel
        await ctx.response.send_message(f"Spliting teams now")
        mteam1 = []
        mteam2 = []
        for member in members:
            if len(mteam1) < len(mteam2):
                mteam1.append(member)
                await member.move_to(team1)
            else:
                mteam2.append(member)
                await member.move_to(team2)

    @teamsplit.error
    async def teamsplit_error(self, ctx, error):
        if isinstance(error, app_commands.MissingRequiredArgument):
            await ctx.response.send_message(error, ephemeral=True)
        
    @app_commands.command(description="List all users in a vc", name="vc-list")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def vclist(self, interaction: discord.Interaction):
        voice_channel = interaction.user.voice.channel if interaction.user.voice else None
        
        if voice_channel:
            # Get members in the voice channel
            members = voice_channel.members
            memnames = [member.name for member in members]
            random.shuffle(memnames)

            await interaction.response.send_message(content='\n'.join(memnames),ephemeral=True)
        else:
            # Edit the original response if not in a voice channel
            await interaction.response.send_message(content="You are not in a voice channel.",ephemeral=True)
            
            
async def setup(Bot):
    await Bot.add_cog(mod(Bot))
