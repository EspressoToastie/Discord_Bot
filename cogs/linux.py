import discord
from discord.ext import commands
import random
from discord import app_commands

from datetime import datetime, time as dtime, timedelta, timezone
import asyncio
import paramiko
import os 

OWNER_ID = int(os.getenv("OWNER_ID"))


class linux(commands.Cog):
    def __init__(self, Bot):
        self.bot = Bot

    def is_owner():
        async def predicate(interaction):
            return interaction.user.id == OWNER_ID
        return app_commands.check(predicate)


    def run_ssh(self, cmd: str):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            os.getenv("SSH_IP"),
            username=os.getenv("SSH_USER"),
            password=os.getenv("SSH_PW"),
            look_for_keys=False)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        ssh.close()
        return out, err


    @app_commands.command(name='docker-command')
    @is_owner()
    @app_commands.choices(
    docker=[
        app_commands.Choice(name="Vanilla", value="mc-fabric"),
        app_commands.Choice(name="Create", value="mc-allofcreate")])
    async def sudo(self, inter, docker: app_commands.Choice[str], command: str):
        out, err = self.run_ssh(f"sudo docker {command} {docker.value}")

        result = "❌" if err else "✅"
        emb3 = discord.Embed(title=f"VPS Command Ran", colour=0xf9d8b7)
        emb3.add_field(name=f"{docker.value} - {command}", value=result, inline=True)
        emb3.timestamp = datetime.now()

        await inter.response.send_message(embed=emb3)


    @app_commands.command(name='server-command')
    @is_owner()
    @app_commands.choices(
    docker=[
        app_commands.Choice(name="Vanilla", value="mc-fabric"),
        app_commands.Choice(name="Create", value="mc-allofcreate")])
    async def server(self, inter, docker: app_commands.Choice[str], command: str):
        out, err = self.run_ssh(f"sudo docker exec {docker.value} rcon-cli {command}")

        result = "❌" if err else "✅"
        emb3 = discord.Embed(title=f"VPS Command Ran", colour=0xf9d8b7)
        emb3.add_field(name=f"{docker.value} - {command}", value=result, inline=True)
        emb3.timestamp = datetime.now()

        await inter.response.send_message(embed=emb3)

async def setup(Bot):
    await Bot.add_cog(linux(Bot))
