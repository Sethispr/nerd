import discord
from discord.ext import commands

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("PingCog is ready.")

    @discord.app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency is {latency}ms. <:ping:1315726966036496536>",
            color=discord.Color.from_rgb(250, 254, 99)
        )
        embed.set_footer(icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(PingCog(bot))
