from disnake.ext import commands
import os
from dotenv import load_dotenv
import config

load_dotenv()

bot = commands.Bot()

@bot.event
async def on_ready():
    print("The bot is ready!")

for cog in config.cogs:
    bot.load_extension(f"cogs.{cog}")

bot.run(os.environ["TOKEN"])