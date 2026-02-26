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
import os

tracemalloc.start()

cluster = MongoClient(os.getenv("MONGO_DB_URL"))


economyv = cluster["discord"]['economy']
wchoice = random.choice([
    "mechanical Engineer",
    "Electrician",
    "Judge",
    "Paralegal",
    "Medical Secretary",
    "School Counselor",
    "Computer Hardware Engineer",
    "Logistician",
    "Lawyer",
    "Registered Nurse",
    "Firefighter",
    "Computer Programmer",
    "Civil Engineer",
    "Veterinarian",
    "Professional athlete",
    "Writer",
    "Actuary",
    "Web Developer",
    "Physician",
    "Human Resources Assistant",
])

class aeconomy(commands.Cog):
    def __init__(self, Bot):
        self.bot = Bot
        self._last_member = None
        
    @commands.Cog.listener()
    async def on_member_join(member):
        stats = economyv.find_one({"id": member.id, "guild": member.guild.id})
        if not member.bot:
            if stats is None:
                newmember = {
                    "id": member.id,
                    "money": 0,
                    "guild": member.guild.id,
                    "guild name": member.guild.name,
                    "member": member.name
                }
                economyv.insert_one(newmember)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            async for member in guild.fetch_members():
                stats = economyv.find_one({
                    "id": member.id,
                    "guild": member.guild.id
                })
                if not member.bot:
                    if stats is None:
                        newmember = {
                            "id": member.id,
                            "money": 0,
                            "guild": member.guild.id,
                            "guild name": member.guild.name,
                            "member": member.name
                        }
                        economyv.insert_one(newmember)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        stats = economyv.find_one({
            "id": message.author.id,
            "guild": message.guild.id
        })
        if not message.author.bot:
            if stats is None:
                newmember = {
                    "id": message.author.id,
                    "money": 0,
                    "guild": message.guild.id,
                    "guild name": message.guild.name,
                    "member": message.author.name
                }
                economyv.insert_one(newmember)

    @discord.app_commands.command(description="Check yo Dablooms")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def balance(self, inter):
        stats = economyv.find_one({
            "id": inter.user.id,
            "guild": inter.guild.id
        })
        if not inter.user.bot:
            money = stats["money"]
            emb = discord.Embed(title=f"{inter.user}'s' Balance")
            emb.add_field(name=f"Wallet:",
                          value=f"<:Dabloom:1045788440819667045> {money}",
                          inline=True)
            emb.set_footer(text=f"Used by: {inter.user}",
                           icon_url=inter.user.avatar)
            await inter.response.send_message(embed=emb)

    @discord.app_commands.command(description="Work a job for money")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def work(self, inter):
        job = wchoice
        pay = randint(100, 600)
        stats = economyv.find_one({
            "id": inter.user.id,
            "guild": inter.guild.id
        })

        money = stats["money"] + pay
        emb = discord.Embed(title="Work Shift", colour=0xBF40BF)
        emb.add_field(name=f"{job} Shift",
                      value="The work day is over and you have been payed!")
        emb.add_field(name="Dablooms Earned:",
                      value=f"<:Dabloom:1045788440819667045> {pay}",
                      inline=False)
        emb.add_field(name=f"Wallet:",
                      value=f"<:Dabloom:1045788440819667045> {money}",
                      inline=True)
        emb.set_footer(text=f"Used by: {inter.user.name}",
                       icon_url=inter.user.avatar)

        economyv.update_one({
            "id": inter.user.id,
            "guild": inter.guild.id
        }, {"$set": {
            "money": money
        }})
        await inter.response.send_message(embed=emb)

    @discord.app_commands.command(description="Add Money to a player.")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @commands.has_permissions(manage_roles=True)
    async def add_money(self, inter, member: discord.Member, cash: int):
        stats = economyv.find_one({
            "id": inter.user.id,
            "guild": inter.guild.id
        })
        if not inter.user.bot:

            old = stats["money"]
            money = stats["money"] + cash
            economyv.update_one(
                {
                    "id": inter.user.id,
                    "guild": inter.guild.id
                }, {"$set": {
                    "money": money
                }})
            emb = discord.Embed(title=f"{member.name}'s' Balance",
                                colour=0xBF40BF)
            emb.add_field(name=f"Wallet:",
                          value=f"<:Dabloom:1045788440819667045> {money}",
                          inline=True)
            emb.add_field(name=f"Old Wallet: ",
                          value=f"<:Dabloom:1045788440819667045> {old}")
            emb.set_footer(text=f"Used by: {member.name}",
                           icon_url=member.avatar)
            await inter.response.send_message(embed=emb)

    @commands.command()
    @add_money.error
    async def add_money_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.response.send_message(error, ephemeral=True)
            
    @discord.app_commands.command(description="Remove Money to a player.")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @commands.has_permissions(manage_roles=True)
    async def remove_money(inter, member: discord.Member, cash: int):
        stats = economyv.find_one({
            "id": inter.user.id,
            "guild": inter.guild.id
        })
        if not member.bot:

            if int(stats["money"]) < cash:
                await inter.response.send_message(
                    "You have insufficient funds to remove")
            else:
                old = stats["money"]
                money = stats["money"] - cash
                economyv.update_one(
                    {
                        "id": inter.user.id,
                        "guild": inter.guild.id
                    }, {"$set": {
                        "money": money
                    }})
                emb = discord.Embed(title=f"{member.name}'s' Balance",
                                    colour=0xBF40BF)
                emb.add_field(name=f"Wallet:",
                              value=f"<:Dabloom:1045788440819667045> {money}",
                              inline=True)
                emb.add_field(name=f"Old Wallet: ",
                              value=f"<:Dabloom:1045788440819667045> {old}")
                emb.set_footer(text=f"Used by: {member.name}",
                               icon_url=member.avatar)
                await inter.response.send_message(embed=emb)
	
    @commands.command()
    @remove_money.error
    async def remove_money_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.response.send_message(error, ephemeral=True)
            
    @discord.app_commands.command(name="gamble",
                            description=f"Gamble away your money")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def gamble(self, inter, cash: int):
        stats = economyv.find_one({
            "id": inter.user.id,
            "guild": inter.guild.id
        })
        if not inter.user.bot:

            if int(stats["money"]) >= cash:
                win = random.randint(1, 2)
                if win == 1:  #You win the gamble

                    money = stats["money"] + cash * 2
                    economyv.update_one(
                        {
                            "id": inter.user.id,
                            "guild": inter.guild.id
                        }, {"$set": {
                            "money": money
                        }})
                    emb = discord.Embed(
                        title=
                        f"<:Dabloom:1045788440819667045> YOU WIN! <:Dabloom:1045788440819667045>",
                        colour=0xBF40BF)
                    emb.add_field(
                        name=f"Winning Amount",
                        value=f"<:Dabloom:1045788440819667045> {2*cash}",
                        inline=True)
                    emb.add_field(
                        name="Wallet:",
                        value=f"<:Dabloom:1045788440819667045> {money}")
                    emb.set_footer(text=f"Used by: {inter.user}",
                                   icon_url=inter.user.avatar)
                    await inter.response.send_message(embed=emb)

                if win == 2:  #You lose the gamble
                    money = stats["money"] - cash
                    economyv.update_one(
                        {
                            "id": inter.user.id,
                            "guild": inter.guild.id
                        }, {"$set": {
                            "money": money
                        }})

                    emb = discord.Embed(
                        title=
                        f"<:Dabloom:1045788440819667045> YOU LOST! <:Dabloom:1045788440819667045>",
                        colour=0xBF40BF)
                    emb.add_field(
                        name=f"Losing Amount",
                        value=f"<:Dabloom:1045788440819667045> {cash}",
                        inline=True)
                    emb.add_field(name="Wallet:",
                                  value=f"{money}",
                                  inline=True)
                    emb.set_footer(text=f"Used by: {inter.user}",
                                   icon_url=inter.user.avatar)
                    await inter.response.send_message(embed=emb)
            else:
                await inter.response.send_message(
                    f"You don't have enought money to gamble. You are missing {cash-stats['money']} <:Dabloom:1045788440819667045>"
                )

    @discord.app_commands.command(name="daily", description="Get yo daily dablooms")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    @commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
    async def daily(self, inter):
        stats = economyv.find_one({
            "id": inter.user.id,
            "guild": inter.guild.id
        })

        money = stats["money"] + 100
        economyv.update_one({
            "id": inter.user.id,
            "guild": inter.guild.id
        }, {"$set": {
            "money": money
        }})
        emb = discord.Embed(title="Daily <:Dabloom:1045788440819667045>",
                            colour=0xBF40BF)
        emb.add_field(name="Daily Dablooms",
                      value=f"+100 <:Dabloom:1045788440819667045>")
        emb.add_field(name="Wallet:",
                      value=f"{money} <:Dabloom:1045788440819667045>")
        emb.set_footer(text=f"Used by: {inter.user.name}",
                       icon_url=inter.user.avatar)
        await inter.response.send_message(embed=emb)

    @daily.error
    async def daily_error(self, ctx, error):
        if error.__class__ is commands.CommandOnCooldown:
            cd: int = int(error.retry_after)
            # send an error message, you can customize this
            await ctx.send(
                f'Sorry, you are on cooldown, which ends in **{cd//86400}d {(cd//3600)%24}h {(cd//60)%60}m {cd % 60}s**.'
            )
            return


async def setup(Bot):
    await Bot.add_cog(aeconomy(Bot))
