import os
from typing import Optional
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
from utils.logger import setup_logger

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup logging
logger = setup_logger()

# Bot configuration
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    description="A moderation bot with member management commands"
)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    try:
        await bot.load_extension('cogs.moderation')
        logger.info('Loaded moderation cog')
        await bot.load_extension('cogs.music')
        logger.info('Loaded music cog')
    except Exception as e:
        logger.error(f'Failed to load cogs: {e}')

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use !help to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f}s")
    else:
        logger.error(f'Error occurred: {error}')
        await ctx.send("An error occurred while processing the command.")

if __name__ == '__main__':
    if not TOKEN:
        logger.error("No Discord token found in environment variables")
        exit(1)
    bot.run(TOKEN)