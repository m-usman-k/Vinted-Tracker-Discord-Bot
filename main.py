import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# Globals:
load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT = commands.Bot(command_prefix="!", intents=discord.Intents().all())

@BOT.event
async def on_ready():
    print(f'Logged in as {BOT.user} (ID: {BOT.user.id})')
    print('------')
    
    await BOT.load_extension('extensions.Tracker')
    
    await BOT.tree.sync()
    print('Command tree synced.')

# Main execution:
if __name__ == "__main__":
    BOT.run(BOT_TOKEN)