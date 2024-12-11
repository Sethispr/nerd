"""
This module contains the PingCog, which includes a command to check the bot's latency.
It also defines a listener to print a message when the cog is ready.
"""

import discord
from discord.ext import commands


class PingCog(commands.Cog):
    """
    A cog for handling ping-related commands and events for the bot.
    """

    def __init__(self, bot):
        """
        Initialize the PingCog with the bot instance.

        Args:
            bot (discord.Bot): The bot instance.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Called when the bot is ready and the cog is loaded.
        This listener will print a message to the console.
        """
        print("PingCog is ready.")

    @discord.app_commands.command(name="ping", description="Check the bot's latency")
    async def ping_slash(self, interaction: discord.Interaction):
        """
        Respond with the bot's latency in milliseconds for slash commands.

        Args:
            interaction (discord.Interaction): The interaction object representing the command.
        """
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency is {latency}ms. <:ping:1315726966036496536>",
            color=discord.Color.from_rgb(250, 254, 99),
        )
        embed.set_footer(
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="ping")
    async def ping_text(self, ctx):
        """
        Respond with the bot's latency in ms for prefix text commands.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency is {latency}ms. <:ping:1315726966036496536>",
            color=discord.Color.from_rgb(250, 254, 99),
        )
        embed.set_footer(
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)


async def setup(bot):
    """
    Setup function to add the PingCog to the bot.

    Args:
        bot (discord.Bot): The bot instance to add the cog to.
    """
    await bot.add_cog(PingCog(bot))
