"""
Main bot script to initialize and run Nerd bot.

This script includes event handlers for the bot lifecycle,
custom command synchronization, and error handling logic.
"""

import logging
import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load bot token from .env file
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Set up bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)


async def load_extensions():
    """Load bot extensions."""
    extensions = ["cogs.calc", "cogs.ping", "cogs.casual"]
    for extension in extensions:
        try:
            await bot.load_extension(extension)
        except ModuleNotFoundError as ex:
            logging.error("Extension not found: %s", ex)
        except ImportError as ex:
            logging.error("Failed to import extension: %s", ex)
        except Exception as ex:  # Retain as fallback for unexpected errors
            logging.error("Failed to load extension '%s': %s", extension, ex)


async def sync_commands():
    """Synchronize application commands."""
    try:
        await bot.tree.sync()
        logging.info("Application commands synced successfully.")
    except discord.Forbidden as ex:
        logging.error("Sync failed due to insufficient permissions: %s", ex)
    except Exception as ex:  # Retain as fallback for unexpected errors
        logging.error("Failed to sync commands: %s", ex)


@bot.event
async def on_ready():
    """Triggered when the bot is ready."""
    await load_extensions()
    await sync_commands()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name=".calc stats"
        )
    )
    logging.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use `/help` to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the required permissions to use this command.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have the required permissions to execute this command.")
    else:
        logging.error("Unhandled error: %s", error)
        await ctx.send("An unexpected error occurred. Please try again later.")


if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if BOT_TOKEN is None:
        logging.critical("Bot token not found. Please set BOT_TOKEN in your .env file.")
        sys.exit(1)

    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        logging.critical("Invalid bot token provided. Please check your .env file.")
    except Exception as ex:
        logging.critical("An error occurred while starting the bot: %s", ex)
