import discord, os
from discord.ext import commands

from dotenv import load_dotenv

# Globals:
load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT = commands.Bot(command_prefix="!" , intents=discord.Intents().all())

# Methods:

# Commands:

# Main execution:
if __name__ == "__main__":
    BOT.run(BOT_TOKEN)