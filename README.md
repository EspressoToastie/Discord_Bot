# Discord Bot

A feature-rich Discord bot built with Python and discord.py.

## Features
- Modular cog-based structure for easy feature management
- Commands for greetings, economy, games, moderation, and more

## Project Structure
```
Discord_Bot/
├── main.py          # Bot entry point
├── requirements.txt # Dependencies
├── cogs/            # Feature modules
│   ├── acommands.py
│   ├── aeconomy.py
│   ├── agreetings.py
│   ├── alevelsys.py
│   ├── aminigames.py
│   ├── fun.py
│   ├── mod.py
│   └── utils.py
└── data/            # Bot data storage
```

## Setup
1. Clone the repo
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Create a `.env` file with your bot token:
```
   TOKEN=your_discord_bot_token
   OWNER_ID=your_discord_id
   GUILD_ID=optional
   MONGO_DB_URL=optional_for_economy
```
4. Run the bot:
```bash
   python main.py
```

## Requirements
- Python 3.8+
- discord.py