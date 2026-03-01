import discord
from discord.ext import commands, tasks
import os
import tracemalloc
from pymongo import MongoClient
from mcstatus import JavaServer
import asyncpg
import asyncio
import pytz

from datetime import datetime, time as dtime, timedelta, timezone
tracemalloc.start()


# Get Token from environment variable
TOKEN = os.getenv("TOKEN")

# MongoDB connection
cluster = MongoClient(os.getenv("MONGO_DB_URL"))
economyv = cluster["discord"]['economy']

GUILD_ID = int(os.getenv("GUILD_ID"))   # Add your own guild id into .env
OWNER_ID = int(os.getenv("OWNER_ID"))   # Add your own user id into .env


intents = discord.Intents.all()
intents.guilds = True
intents.messages = True
intents.presences = True
intents.members = True

Bot = commands.Bot(command_prefix='T.',
                    activity=discord.Activity(type=discord.ActivityType.listening, name="For FAQ's"),
                    intents=intents, owner_id=OWNER_ID)
Bot.remove_command('help')

cogs = ["cogs.utils", "cogs.fun", "cogs.mod",
        "cogs.agreetings", "cogs.aeconomy", "cogs.aminigames", "cogs.acommands"]

@Bot.event
async def on_ready():

    print(f'{Bot.user.name} has connected to Discord!')

    if not check_reminders.is_running():
        check_reminders.start()
    # Load all cogs
    for cog in cogs:
        try:
            await Bot.load_extension(cog)
            print(f"Loaded Cog {cog}")
        except commands.ExtensionError as e:
            print(f'Failed to load extension {cog}: {e}')

    try:
        await Bot.tree.sync()
        print("✅ Global commands synced!")
    except Exception as e:
        print(f"⚠️ Failed to sync commands: {e}")

@Bot.event
async def on_message(message):
    print(f"{message.author}: {message.content}")
    await Bot.process_commands(message)


@Bot.event
async def on_member_update(before, after):
    print(f"Member update event triggered for {after.name}.")
    print(f"Before: {before.status} -> After: {after.status}")



############################################
# Commands Starting Here#
############################################
# -
# -
############################################
# - Slash Commands
############################################

@Bot.command()
async def tempremove(ctx):
    if ctx.author.id == OWNER_ID:
        role = ctx.guild.get_role(1200159291991150653)
        guild = ctx.guild
        for member in guild.members:
            await member.remove_roles(role)
        await ctx.send(f"Removed from {len(guild.members)} members")


@Bot.command()
async def coglist(ctx):
    if ctx.author.id == OWNER_ID:
        await ctx.send(f"cog list: {cogs}. To load/unload a cog do T.cog [name]")
    else:
        ctx.send("You don't have permission")


@Bot.command()
async def cog(ctx: commands.Context, message):
    if ctx.author.id == OWNER_ID:
        loaded_cogs = [cog.lower() for cog in Bot.cogs]
        if message in loaded_cogs:
            # Unload the 'cogs.talk' cog
            await Bot.unload_extension(f"cogs.{message}")
            await ctx.send(f"cogs.{message} has been unloaded.")
        else:
            # Load the 'cogs.talk' cog
            await Bot.load_extension(f'cogs.{message}')
            await ctx.send(f"cogs.{message} has been loaded.")
    else:
        ctx.send("You don't have permission")


@Bot.command(name="ping")
async def ping(ctx: discord.interactions.Interaction):
    await ctx.response.send_message(f'Pong! {Bot.latency}')


@Bot.command()
async def leave(ctx, guildid):
    if ctx.author.id == OWNER_ID:
        guild = Bot.get_guild(int(guildid))
        await guild.leave()
        await ctx.send(f"Left {guild.name}")


@Bot.command()
async def ToastInvite(ctx):
    if ctx.author.id == OWNER_ID:
        invites = []

        for guild in Bot.guilds:
            if c.permissions_for(guild.me).create_instant_invite:  # make sure the bot can actually create an invite
                invite = await c.create_invite()
                invites.append(invite)
    await ctx.channel.send(invites)


@Bot.command()
async def ToastServerCheck(ctx):
    if ctx.author.id == OWNER_ID:
        invites = []

        for guild in Bot.guilds:
            server = [guild.name, guild.id]
            invites.append(server)
    await ctx.channel.send(invites)


@Bot.command()
async def invite(ctx):
    """Create instant invite"""
    link = await ctx.channel.create_invite(max_age=0)  # 0 = never expire
    await ctx.send(f"Here is an instant invite to your server: {link}")


@Bot.command()
async def avatar(ctx, member: discord.Member):
    if member is None:
        member = ctx.author.user
    emb3 = discord.Embed(title=f"Avatar", color=0xf9d8b7)
    emb3.set_image(url=member.avatar)
    await ctx.channel.send(embed=emb3)


@tasks.loop(seconds=60)
async def check_reminders():
    now = datetime.now(timezone.utc)

    rows = await Bot.pg_con.fetch(
        "SELECT id, name, remindertime, channel, userid, messageid, guildid, private FROM pages_remindr WHERE completed = FALSE AND remindertime <= $1",
        now
    )

    for row in rows:
        channel_id = int(row['channel'])
        user_id = int(row['userid'])
        timer = row['remindertime']
        guild_id = int(row['guildid'])
        reminderTime = timer.strftime('%Y-%m-%d %H:%M')
        private = bool(row['private'])
        
        channel = Bot.get_channel(channel_id)
        user = Bot.get_user(user_id)

        if private:
            if user:
                try:
                    await user.send(f":alarm_clock: Reminder: {row['name']} (scheduled for {reminderTime})")
                except Exception as e:
                    print(f"Failed to DM user {user_id}: {e}")
            else:
                print(f"User {user_id} not found.")
        else:
            if channel:
                await channel.send(f":alarm_clock: {user.mention} Reminder: {row['name']}. Scheduled for {reminderTime})")
            else:
                await user.send(f":alarm_clock: Reminder: {row['name']} (scheduled for {reminderTime})")

        # Mark reminder complete
        await Bot.pg_con.execute(
            "UPDATE pages_remindr SET completed = TRUE WHERE id = $1", row['id']
        )

#########################################################
# Sync

@Bot.command(name="sync_commands", help="Sync global and guild commands.")
@commands.is_owner()  # Ensures only the bot owner can use this command
async def sync_commands(ctx):
    await ctx.send("🔄 Syncing commands...")

    # Sync global commands
    try:
        await ctx.bot.tree.sync()
        print("✅ Global commands synced!")
        await ctx.send("✅ Global commands synced!")
    except Exception as e:
        print(f"⚠️ Failed to sync global commands: {e}")
        await ctx.send(f"⚠️ Failed to sync global commands: {e}")

    # Sync guild commands for each server the bot is in
    for guild in ctx.bot.guilds:
        try:
            guild_obj = discord.Object(id=guild.id)
            await ctx.bot.tree.sync(guild=guild_obj)
            print(f"✅ Synced guild commands for {guild.name} ({guild.id})!")
            await ctx.send(f"✅ Synced guild commands for {guild.name} ({guild.id})!")
        except Exception as e:
            print(f"⚠️ Failed to sync guild commands for {guild.name} ({guild.id}): {e}")
            await ctx.send(f"⚠️ Failed to sync guild commands for {guild.name} ({guild.id}): {e}")

    await ctx.send("✅ Command sync complete!")


Bot.run(TOKEN)