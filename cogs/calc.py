"""
This module contains the CalcCog, which calculates Competitive OP and other stats.
"""

import math
import discord
from discord import app_commands
from discord.ext import commands


class CalcCog(commands.Cog):
    """
    A cog for calculating OP from various game statistics.
    """

    def __init__(self, bot):
        """
        Initialize the CalcCog with the bot instance.

        Args:
            bot (discord.Bot): The bot instance.
        """
        self.bot = bot

    def calculate_metrics(self, stats, sdi=1, device="pc"):
        """
        Calculate various game metrics based on provided statistics.

        Args:
            stats (dict): A dictionary containing the game statistics.
            sdi (float): SDI (Score Deviation Index), default is 1.
            device (str): The device used (e.g., "pc", "mobile", "tablet"), default is "pc".

        Returns:
            dict: A dictionary containing various calculated metrics.
        """
        rounds_played = stats["rounds_played"]
        damage_dealt = stats["damage_dealt"]
        targets_assassinated = stats["targets_assassinated"]
        target_survival = stats["target_survival"]
        free_for_all_kills = stats["free_for_all_kills"]
        free_for_all_wins = stats["free_for_all_wins"]
        infected_killed = stats["infected_killed"]
        infection_survival = stats["infection_survival"]
        infections = stats["infections"]
        escapes = stats["escapes"]
        final_shots = stats["final_shots"]
        targets_protected = stats["targets_protected"]
        epidemic = stats["epidemic"]
        xpb_minus_xpa = stats["xpb_minus_xpa"]

        # Auto penalty calculation
        auto_penalty = None
        if (targets_assassinated + target_survival) / rounds_played < 0.12:
            auto_penalty = rounds_played + 3 * (
                0.12 * rounds_played - (targets_assassinated + target_survival)
            )
            rounds_played = max(round(auto_penalty // 2 * 2), rounds_played)

        rounds_adjusted = rounds_played - escapes
        rounds_gamified = (
            rounds_adjusted
            - escapes
            - target_survival
            - epidemic
            - infection_survival
            - free_for_all_wins
        )

        s_ma = (
            (2 / 3) * (sdi - 1) + 1 if sdi >= 1 else 1 + ((2 / 3) * (sdi - 1) + 1) - 1
        )
        s_mb = (
            (4 / 3) * (sdi - 1) + 1 if sdi >= 1 else 1 + ((4 / 3) * (sdi - 1) + 1) - 1
        )

        g_os = 46 * (
            (sdi * 5 * final_shots + s_ma * 3 * targets_protected)
            / max(1, rounds_gamified)
        )

        d_avg = damage_dealt / max(
            1, (rounds_adjusted - (escapes + target_survival + epidemic))
        )

        t_p = (
            2 * rounds_adjusted * (86 * g_os + s_mb * 32 * d_avg)
            + sdi * 59 * xpb_minus_xpa
        ) / (165 * rounds_adjusted)
        z_p = (13 / rounds_adjusted) * (
            s_mb
            * (
                9 * free_for_all_kills
                + 15 * infected_killed
                + 40 * free_for_all_wins
                + 25 * infections
                + 100 * epidemic
            )
            + s_ma * 15 * infection_survival
        )
        o_p = (529 / 20) * math.sqrt(t_p + z_p)

        boost_multiplier = 1.0
        if device in ["phone", "mobile"]:
            boost_multiplier = 1.075
        elif device == "tablet":
            boost_multiplier = 1.05
        elif device == "console":
            boost_multiplier = 1.10

        boosted_o_p = o_p * boost_multiplier

        division = ""
        if boosted_o_p >= 975:
            division = "Kugelblitz (S)"
        elif boosted_o_p >= 935:
            division = "Radiance (A+)"
        elif boosted_o_p >= 870:
            division = "Firestorm (A)"
        elif boosted_o_p >= 820:
            division = "Flashover (A-)"
        elif boosted_o_p >= 765:
            division = "Magnesium (B+)"
        elif boosted_o_p >= 705:
            division = "Thermite (B)"
        elif boosted_o_p >= 635:
            division = "Propane (C)"
        elif boosted_o_p >= 560:
            division = "Wood (D)"
        else:
            division = "Ember (E)"

        x_pr = xpb_minus_xpa / max(1, rounds_adjusted)

        return {
            "OP": boosted_o_p,
            "TP": t_p,
            "SP": z_p,
            "GO": g_os,
            "AD": d_avg,
            "XPR": x_pr,
            "Division": division,
            "SDI": sdi,
            "AutoPenalty": auto_penalty,
        }

    async def handle_calc(self, stats: str, interaction=None, context=None):
        """
        Shared logic for !calc (text command) and /calc (slash command).
        """
        try:
            data = stats.split()
            if len(data) != 16:
                raise ValueError("Invalid number of parameters, expected 16 values!")

            metrics = self.calculate_metrics(
                {
                    "xpb_minus_xpa": int(data[0]),
                    "rounds_played": int(data[1]),
                    "targets_assassinated": int(data[2]),
                    "escapes": int(data[3]),
                    "targets_protected": int(data[4]),
                    "damage_dealt": int(data[5]),
                    "final_shots": int(data[6]),
                    "target_survival": int(data[7]),
                    "free_for_all_kills": int(data[8]),
                    "free_for_all_wins": int(data[9]),
                    "infected_killed": int(data[10]),
                    "infection_survival": int(data[11]),
                    "infections": int(data[12]),
                    "epidemic": int(data[13]),
                },
                sdi=float(data[14]),
                device=data[15].lower(),
            )

            auto_penalty = metrics.get("AutoPenalty")
            title = (
                f"auto-penalty: +{int(auto_penalty - int(data[1]))} rounds"
                if auto_penalty
                else ""
            )

            embed = discord.Embed(
                title=title, color=discord.Color.from_rgb(82, 146, 209)
            )
            embed.description = (
                f"```glsl\n"
                f"OP = {int(metrics['OP'])}\n"
                f"TP = {int(metrics['TP'])}, SP = {int(metrics['SP'])}\n"
                f"[GO = {int(metrics['GO'])}], [AD = {int(metrics['AD'])}], [XPR = {int(metrics['XPR'])}]\n"
                f"SDI = {metrics['SDI']:.4f}\n\n"
                f"Division: {metrics['Division']}\n"
                f"```"
            )

            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.url,
                    label="docs",
                    url="https://sethispr.github.io/nerd/",
                )
            )

            user_input_button = discord.ui.Button(
                label="", style=discord.ButtonStyle.success, emoji="📄"
            )
            trash_button = discord.ui.Button(
                label="", style=discord.ButtonStyle.danger, emoji="🗑️"
            )

            async def show_input_callback(interaction):
                input_stats = (
                    "```glsl\n"
                    + "\n".join(f"{key}: {value}" for key, value in metrics.items())
                    + "```"
                )
                await interaction.response.send_message(input_stats, ephemeral=True)

            async def clear_message_callback(interaction):
                await interaction.response.defer()
                await interaction.message.delete()

            user_input_button.callback = show_input_callback
            trash_button.callback = clear_message_callback
            view.add_item(user_input_button)
            view.add_item(trash_button)

            if interaction:
                await interaction.response.send_message(embed=embed, view=view)
            elif context:
                await context.send(embed=embed, view=view)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            if interaction:
                await interaction.response.send_message(error_message)
            elif context:
                await context.send(error_message)

    @app_commands.command(
        name="calc", description="Calculate Competitive OP from a copypasta"
    )
    async def calc_slash(self, interaction: discord.Interaction, stats: str):
        """Slash command to calculate OP.
        Args:
            interaction (discord.Interaction): The interaction object.
            stats (str): format: current xp in ss b minus xp needed to lvl up in ss a rounds played till epidemic (exclude guards killed)"""
        await self.handle_calc(stats, interaction=interaction)

    @commands.command(
        name="calc", description="Calculate Competitive OP from a copypasta"
    )
    async def calc_text(self, ctx, *, stats: str):
        """Text command to calculate OP."""
        await self.handle_calc(stats, context=ctx)


async def setup(bot):
    await bot.add_cog(CalcCog(bot))
