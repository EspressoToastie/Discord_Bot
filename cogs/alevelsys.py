import pymongo
from pymongo import MongoClient
import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import tracemalloc
import random
from random import randint

tracemalloc.start()

cluster = MongoClient(os.getenv("MONGO_DB_URL"))

leveling = cluster["discord"]['leveling']
guildid = cluster["discord"]['xpchannel']
blguildid = cluster["discord"]['xpguild']
blevelup = cluster["discord"]['level up channel']

class alevelsys(commands.Cog):
    def __init__(self, Bot):
        self.bot = Bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

            channel = guildid.find_one({"channelblacklisted": message.channel.id})
        levelup = blevelup.find_one({"guildid": message.guild.id})
        try:
            levelch = int(levelup['channel'])
        except (TypeError, ValueError, KeyError):
            levelch = None
        if levelch is not None:
            channel = discord.utils.get(message.guild.channels, id=levelch)
        guild = blguildid.find_one({"guildid": message.guild.id})
        if str(message.channel.id) in str(channel):
            return
      
        if str(message.guild.id) in str(guild):
            return
        
        if not message.author.bot:
                stats = leveling.find_one({
                    "id": message.author.id,
                    "guild": message.guild.id
                })		
                if stats is None:
                    newuser = {
                        "id": message.author.id,
                        "guild": message.guild.id,
                        "xp": 0,
                        "user": message.author.name,
                        "guild name": message.guild.name
                    }
                    leveling.insert_one(newuser)
                    
                else:
                    xp = stats["xp"] + 50
                    leveling.update_one(
                        {
                            "id": message.author.id,
                            "guild": message.guild.id
                        }, {"$set": {
                            "xp": xp
                        }})
                    lvl = 0
                    while True:
                        if xp < ((50 * (lvl**2)) + (50 * (lvl - 1))):
                            break
                        lvl += 1
                    xp -= ((50 * ((lvl - 1)**2)) + (50 * (lvl - 1)))
                    if xp == 0:
                        levelchannel = blevelup.find_one({
                        "guild": message.guild.id
                        })
                        if levelchannel is None:
                            await message.channel.send(
                                f"Well done {message.author.mention}! You have leveled up to **Level: {lvl}**"
                            )
                        else:
                            await channel.send(
                                f"Well done {message.author.mention}! You have leveled up to **Level: {lvl}**"
                            )

    @discord.app_commands.command(description="Check your rank", name="level")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def level(self, inter):
            stats = leveling.find_one({
                "id": inter.user.id,
                "guild": inter.guild.id
            })
            if stats is None:
                embed = discord.Embed(
                    description=
                    "You haven't sent any messages, You have no rank!")
                await inter.response.send_message(embed=embed)
            else:
                xp = stats["xp"]
                lvl = 0
                rank = 0
                while True:
                    if xp < ((50 * (lvl**2)) + (50 * lvl)):
                        break
                    lvl += 1
                xp -= ((50 * ((lvl - 1)**2)) + (50 * (lvl - 1)))
                boxes = int((xp / (200 * ((1 / 2) * lvl))) * 20)
                rankings = leveling.find().sort("xp", -1)
                for x in rankings:
                    rank += 1
                    if stats["id"] == x["id"]:
                        break
                embed = discord.Embed(
                    title="{}'s level stats".format(inter.user.name))
                embed.add_field(name="Name",
                                value=inter.user.mention,
                                inline=True)
                embed.add_field(name="XP",
                                value=f"{xp}/{int(200*((1/2)*lvl))}",
                                inline=True)
                embed.add_field(name="LEVEL", value=f"{lvl}", inline=True)
                embed.add_field(name="Progress Bar [lvl]",
                                value=boxes * ":blue_square:" +
                                (20 - boxes) * ":white_large_square:",
                                inline=False)
                embed.set_thumbnail(url=inter.user.avatar)
                await inter.response.send_message(embed=embed)

    @discord.app_commands.command(description="Check the leaderboard",
                            name="leaderboard")
    async def leaderboard(self, inter):

        guild = guildid.find_one({"channelblacklisted": inter.channel.id})
        if str(inter.channel.id) is str(guild):
            return
        rankings = leveling.find().sort("xp", -1)
        i = 1
        embed = discord.Embed(title="Rankings:")
        for x in rankings:
            try:
                temp = inter.guild.get_members(x["id"])
                tempxp = x["xp"]
                embed.add_field(name=f"{i}: {temp.name}",
                                value=f"Total XP: {tempxp}",
                                inline=False)
                i += 1
            except:
                pass
            if i == 11:
                break
        await inter.response.send_message(embed=embed)

    @discord.app_commands.command(
        description="Prevents xp being earned in blacklisted channels",
        name="blacklist-channel")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @commands.has_permissions(manage_guild=True)
    async def blacklistchannel(self, inter,  channel: discord.channel.TextChannel):
        bchannel = guildid.find_one({"guildid": inter.guild.id, "channelblacklisted": channel.id})
        if str(channel.id) in str(bchannel):
            await inter.send("channel already xp blacklisted")
            return
        else:
            blacklist = {
            "guild": inter.guild.name,
            "guildid": inter.guild.id,
            "channelblacklisted": channel.id}
            guildid.insert_one(blacklist)
            await inter.response.send_message(
            f"{channel} was blacklisted, To remove a channel from blacklisted, Do /unblacklist-channel"
        )

    @discord.app_commands.command(
        description="Resume's xp being earned in blacklisted channels",
        name="unblacklist-channel")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @commands.has_permissions(manage_guild=True)
    async def removeblacklist(self, inter, channel: discord.channel.TextChannel):
        bchannel = guildid.find_one({"guildid": inter.guild.id, "channelblacklisted": channel.id})
        if str(channel.id) not in str(bchannel):
            await inter.send("This channel is not xp blacklisted")
            return
        else:
            blacklist = {
            "guild": inter.guild.name,
            "guildid": inter.guild.id,
            "channelblacklisted": channel.id}
            guildid.delete_one(blacklist)
            await inter.response.send_message(
            f"{channel} was unblacklisted, To add a channel to blacklisted, Do /blacklist-channel"
        )

    @discord.app_commands.command(
        description="Prevents xp being earned in blacklisted guild",
        name="blacklist-guild")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @commands.has_permissions(manage_guild=True)
    async def blacklistguild(self, inter):
        guild = inter.guild.id
        bguild = guildid.find_one({"guildid": guild})
        if str(inter.guild.id) in str(bguild):
            await inter.response.send_message("Guild already xp blacklisted")
            return
        else:

            blacklist = {
            "guild": inter.guild.name,
            "guildid": inter.guild.id}
            blguildid.insert_one(blacklist)
            await inter.response.send_message(
            f"{inter.guild.name} was blacklisted, To remove a guild from blacklisted, Do /unblacklist-guild"
        )
           
    @discord.app_commands.command(
        description="Prevents xp being earned in blacklisted guild",
        name="unblacklist-guild")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @commands.has_permissions(manage_guild=True)
    async def unblacklistguild(self, inter):
        guild = inter.guild.id
        bguild = blguildid.find_one({"guildid": inter.guild.id})
        if str(inter.guild.id) not in str(bguild):
            await inter.send("Guild isn't xp blacklisted")
            return
        else:
            blacklist = {
            "guild": inter.guild.name,
            "guildid": inter.guild.id}
            blguildid.delete_one(blacklist)
            await inter.response.send_message(
            f"{inter.guild.name} was unblacklisted, To add a guild to blacklisted, Do /blacklist-guild")
      
    @discord.app_commands.command(
        description="Level Up Channel",
        name="level-up-channel")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @commands.has_permissions(manage_guild=True)
    async def levelupchannel(self, inter, channel: discord.channel.TextChannel):
        levelup = blevelup.find_one({"guildid": inter.guild.id, "channel": channel.id})
        if str(channel.id) in str(blevelup):
            await inter.send(f"Replacing previous Level Up Channel")
            return
        else:
            rankup = {
            "guild": inter.guild.name,
            "guildid": inter.guild.id,
            "channel": channel.id}
            blevelup.insert_one(rankup)
            await inter.response.send_message(
            f"{channel} was made into the Level Up Channel"
        )

async def setup(Bot):
    await Bot.add_cog(alevelsys(Bot))