import discord
from discord.ext import commands
import random

from discord.utils import get
from discord.ui import Select, View, Button
from discord import Embed
from pymongo import MongoClient
import asyncio
from discord import app_commands
import os

cluster = MongoClient(os.getenv("MONGO_DB_URL"))
games = cluster["discord"]['hangman']
words = cluster["discord"]['words']
guildid = cluster["discord"]['xpchannel']

def get_revealed_word(game, guess=None):
    revealed_word = ''
    for letter in game['word']:
        if guess == letter or letter in game['guesses']:
            revealed_word += letter
        else:
            revealed_word += '_'
    return revealed_word

class RView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accept!", style=discord.ButtonStyle.green)
    async def second_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("You accepted the challenge!")


class aminigames(commands.Cog):
    def __init__(self, Bot):
        self.bot = Bot

        
    @app_commands.command(name='test1')
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def test1(self, inter):
        await inter.response.send_message("Test1")
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        # Find the game document for this channel
        game = games.find_one({'channel_id': message.channel.id})
        if not game:
            return
           
        # Split the message into words
        guild = message.guild
        channel = get(guild.text_channels, name='hangman-lobby')
        guess = message.content
        if len(guess) == 1:
            # Count the message as a single letter guess
            games.update_one({'_id': game['_id']}, {'$push': {'guesses': guess}})
            revealed_word = get_revealed_word(game, guess)
            if revealed_word == game['word']:
                # The whole word has been correctly guessed
                await message.channel.send(f'Congratulations {message.author.mention}! You **correctly** guessed the word: ```{revealed_word}```')
                games.delete_one({'_id': game['_id']})
                await message.channel.edit(slowmode_delay=0)
                blacklist = {
            "guild": inter.guild.name,
            "guild id": inter.guild.id,
            "channelblacklisted": channel.id}
                guildid.delete_one(blacklist)
                
            elif '_' not in revealed_word:
                # All letters have been correctly guessed
                await message.channel.send(f'Congratulations {message.author.mention}! You **correctly** guessed the word: ```{revealed_word}```')
                games.delete_one({'_id': game['_id']})
                await message.channel.edit(slowmode_delay=0)
                blacklist = {
            "guild": inter.guild.name,
            "guild id": inter.guild.id,
            "channelblacklisted": channel.id}
                guildid.delete_one(blacklist)
                
            else:
                await message.channel.send(f'{message.author.name} guessed {guess}. ```{revealed_word}```')
        elif len(guess) > 1:
               # Check if the message is a guess for the whole word
            if guess == game['word']:
                revealed_word = guess
                await message.channel.send(f'Congratulations {message.author.mention}! You guessed the word **correctly**: ```{revealed_word}```')
                games.delete_one({'_id': game['_id']})
                await message.channel.edit(slowmode_delay=0)
                
                blacklist = {
            "guild": message.guild.name,
            "guild id": message.guild.id,
            "channelblacklisted": channel.id}
                guildid.delete_one(blacklist)
                
            else:
                revealed_word = get_revealed_word(game, guess)
                await message.channel.send(f'{message.author.mention} guessed the **wrong** word. ```Word: {revealed_word}```')
                
    
    @app_commands.command(name='hangman-start', description='Start a hangman game with a random word, /guess (letter), /guess-word (word)')
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def solo_start_game(self, inter):
        guild = inter.guild
        channel = get(guild.text_channels, name='hangman-lobby')
        if channel is None:
            category_id = inter.channel.category.id
            category = inter.guild.get_channel(category_id)
            channel = await inter.guild.create_text_channel(name=f'hangman-lobby', category=category)
        word_doc = random.choice(list(words.find()))
        word = word_doc['word']
        
        game_id = games.insert_one({
            'channel_id': channel.id,
            'name': "hangman-lobby",
            'guild': inter.guild.id,
            'player': inter.user.id,
            'word': word,
            'guesses': [],
            'word_revealed': '_' * len(word)}).inserted_id
        
        blacklist = {
            "guild": inter.guild.name,
            "guild id": inter.guild.id,
            "channelblacklisted": inter.channel.id}
        
        guildid.insert_one(blacklist)

        # Find the game document for this channel
        game = games.find_one({'name': "hangman-lobby", 'guild': inter.guild.id})
    
        # Send the starting message
        await channel.edit(slowmode_delay=1)
        await channel.send(f'Hangman game started! The word to guess is ```{get_revealed_word(game)}```')
        if inter.channel.id == game['channel_id']:   
            return
        else:
            await inter.response.send_message(f'Hangman game started! Move over to {channel.mention}')
  
    
    @app_commands.command(name="hangman-delete", description="Stop the current game of hangman, Must have started game!")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def hangmandelete(self, inter):
        guild = inter.guild
        game = games.find_one({'name': "hangman-lobby", 'guild': inter.guild.id, 'channel_id': inter.channel.id})
        channel = get(guild.text_channels, name='hangman-lobby')
        if channel is None:
            await inter.response.send_message("There is no current game to delete", ephemeral=True)
            return
        if inter.user.guild_permissions.manage_channels:
            await inter.response.send_message("Deleting game of Hangman in 5 seconds")
            await asyncio.sleep(5)
            await channel.delete()
        else:
            await inter.send("You don't have permission to delete game of Hangman", ephemeral=True)
        if game is not None:
            games.delete_one({'_id': game['_id']})
            

    
    @app_commands.command(name='hangman-hint',description='Apart of Hangman games, /start (word), /guess (letter)')
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def hint(self, inter):
  # Find the game document for this channel
        game = games.find_one({'name': "hangman-lobby", 'guild': inter.guild.id, 'channel_id': inter.channel.id})
        if not game:
            await inter.response.send_message('There is no ongoing game in this channel!')
            return

  # Get the word and the revealed word so far
        word = game['word']
        revealed_word = get_revealed_word(game)

  # Find a random letter that has not been revealed yet
        unrevealed_letters = [i for i, letter in enumerate(word) if letter != revealed_word[i]]
        if not unrevealed_letters:
            await inter.response.send_message('All letters have already been revealed!')
            return
        i = random.choice(unrevealed_letters)
        letter = word[i]

  # Update the revealed word and the guesses
        games.update_one({'_id': game['_id']}, {'$push': {'guesses': letter}})
        revealed_word = get_revealed_word(game, letter)
        if revealed_word == word:
            await inter.send(f"No-one won the Game, The Word: {revealed_word}")
            games.delete_one({'_id': game['_id']})
            await inter.channel.edit(slowmode_delay=0)
            blacklist = {
      "guild": inter.guild.name,
      "guild id": inter.guild.id,
      "channelblacklisted": message.channel.id}
            guildid.delete_one(blacklist)
        else:
            guesses_str = " ".join(game["guesses"])
            await inter.response.send_message(f'One letter has been revealed: {letter} ```{revealed_word}```')

    @app_commands.command(name="rps", description="Play a game of Rock Paper Scissors with another user")
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def rps(self, inter, member: discord.Member):
        select = Select(placeholder="Rock Paper Scissors Options!",options=[
            discord.SelectOption(label="Rock", value="0x1", emoji="🪨", description=" "),
            discord.SelectOption(label="Paper", value="0x2", emoji="📄",description=" "),
            discord.SelectOption(label="Scissors", value="Ox3", emoji="✂️", description=" ")],)
        
        select2 = Select(placeholder="Rock Paper Scissors Options!", options=[
            discord.SelectOption(label="Rock", value="1x1", emoji="🪨", description=" "),
            discord.SelectOption(label="Paper", value="1x2", emoji="📄",description=" "),
            discord.SelectOption(label="Scissors", value="1x3", emoji="✂️", description=" ")],)

        async def my_callback(interaction):
            svalue = next(option for option in select.options if option.value == select.values[0])
            semoji = svalue.emoji
            slabel = svalue.label

            if select.values[0] != None:
                button = discord.ui.Button(style=discord.ButtonStyle.green, label="Accept!")
                async def button_callback(interaction):
                    if interaction.user != member:
                        await interaction.edit_original_response(content=f"{interaction.user.mention}, you are not the challenger!")
                        return      

                    async def final_callback(interaction):
                        if select.values[0] == "0x1" and select2.values[0] == "1x1" or select.values[0] == "0x2" and select2.values[0] == "1x2" or select.values[0] == "0x3" and select2.values[0] == "1x3":
                            await interaction.response.send_message(content="The Game ended in a tie.")
                        if select.values[0] == "0x1" and select2.values[0] == "1x3" or select.values[0] == "0x2" and select2.values[0] == "1x1" or select.values[0] == "0x3" and select2.values[0] == "1x2":
                            await interaction.response.send_messagee(content=f"{inter.user.mention} Won Rock Paper Scissors, Against <@{member.id}>")
                        if select2.values[0] == "1x1" and select.values[0] == "0x3" or select2.values[0] == "1x2" and select.values[0] == "0x1" or select2.values[0] == "1x3" and select.values[0] == "0x2":
                            await interaction.response.send_message(content=f"<@{member.id}> Won Rock Paper Scissors, Against {inter.user.mention}")
                    
                    view2 = discord.ui.View()
                    view2.add_item(select2)
                    select2.callback = final_callback
                    test = await interaction.response.send_message(f"Pick your option <@{member.id}>",view=view2,ephemeral=True)
                   

                view = discord.ui.View()
                button.callback = button_callback
                view.add_item(button)

                msg = await interaction.channel.send(f"Rock Paper Scissor's Challenge for {member.mention}\n-# Sent By: {inter.user.mention}",view=view)

        select.callback = my_callback
        view = discord.ui.View(timeout=None)
        view.add_item(select)

        await inter.response.send_message("Rock Paper Scissors Game!", view=view, ephemeral=True)

        
    def check_winner(area):
        # Check rows
        for row in area:
            if row[0] == row[1] == row[2] and row[0] in ("x", "o"):
                return row[0]  # Return the winner ("x" or "o")

           # Check columns
        for col in range(3):
              if area[0][col] == area[1][col] == area[2][col] and area[0][col] in ("x", "o"):
                return area[0][col]  # Return the winner
        return None  # No winner yet

    @app_commands.command(name="ttt", description="Play a game of TicTacToe")    
    @app_commands.guilds(discord.Object(id=int(os.getenv("GUILD_ID"))))
    async def tictactoe(self, inter, member: discord.Member):
        player_1 = inter.user
        player_2 = member
        area = [["1","2","3"],["4","5","6"],["7","8","9"]]
        count = 0
        for a in area:
            row = []
            for b in a:
                row.append(f"|{b}|")
                await inter.channel.send(row)
        game = False
        
        while not game:
            if count % 2 == 0:
                player = "x"
            else:
                player = "o"
            guess = int(input("Enter box 1-9: "))
            while guess < 1 or guess > 9:
                guess = int(input("Invalid number, Enter between 1-9: "))
            row, col = (guess - 1) // 3, (guess - 1) % 3  # Calculate the correct position
        
            while area[row][col] in ("x", "o"):  # Check only the chosen position
                guess = int(input("Value already in box, Pick another box: "))
                row, col = (guess - 1) // 3, (guess - 1) % 3
            else:
                area[row][col] = player
        
            for a in area:
                for b in a:
                    for c in b:
                        print(f"|{c}|", end="")
                print()
        
            count += 1
            winner = check_winner(area)
        
            if winner is not False:
                print(f"The winner is {winner}")

async def setup(Bot):
    await Bot.add_cog(aminigames(Bot))