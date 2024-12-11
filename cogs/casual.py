"""
This module contains the CasualCalcCog, which calculates Casual and Lifetime OP and other stats.
"""

import math
import discord
from discord import app_commands
from discord.ext import commands


class CasualCalcCog(commands.Cog):
    """
    A cog for calculating Casual OP from various game statistics.
    """

    def __init__(self, bot):
        """
        Initialize the CasualCalcCog with the bot instance.

        Args:
            bot (discord.Bot): The bot instance.
        """
        self.bot = bot

    def calculate_metrics(self, stats):
        """
        Calculate various game metrics for Casual OP based on provided statistics.

        Args:
            stats (dict): A dictionary containing the game statistics.

        Returns:
            dict: A dictionary containing various calculated metrics.
        """
        # Extract stats
        level_a = stats["lva"]
        experience_a = stats["xpa"]
        level_b = stats["lvb"]
        experience_b = stats["xpb"]
        rounds_played = stats["rounds_played"]
        escapes = stats["escapes"]
        guards_killed = stats["guards_killed"]
        targets_protected = stats["targets_protected"]
        damage_dealt = stats["damage_dealt"]
        final_shots = stats["final_shots"]
        target_survivals = stats["target_survivals"]
        ffa_kills = stats["ffa_kills"]
        ffa_wins = stats["ffa_wins"]
        infected_killed = stats["infected_killed"]
        infection_survival = stats["infection_survival"]
        infections = stats["infections"]
        epidemics = stats["epidemics"]

        def calculate_total_experience(level, experience):
            return experience + sum(
                math.floor((n - 1) * (2.46 * (1.02**n)) * 10) * 10
                for n in range(1, level + 1)
            )

        adjusted_rounds = rounds_played - escapes
        total_experience_a = calculate_total_experience(level_a, experience_a)
        total_experience_b = calculate_total_experience(level_b, experience_b)
        experience_difference = total_experience_b - total_experience_a

        rounds_with_goals = (
            adjusted_rounds
            - escapes
            - target_survivals
            - infection_survival
            - ffa_wins
            - epidemics
        )
        experience_per_round = experience_difference / max(1, adjusted_rounds)

        average_damage = damage_dealt / max(
            1, adjusted_rounds - (escapes + target_survivals + epidemics)
        )

        assassin_aggression = 100 * (
            (2 * escapes + guards_killed) / max(1, adjusted_rounds)
        )
        guard_objective = 45 * (
            (5 * final_shots + 3 * targets_protected) / max(1, rounds_with_goals)
        )

        z_factor = (12 / adjusted_rounds) * (
            9 * ffa_kills
            + 14 * infected_killed
            + 40 * ffa_wins
            + 16 * infection_survival
            + 25 * infections
            + 100 * epidemics
        )

        performance_score = (
            adjusted_rounds
            * (154 * (guard_objective + assassin_aggression) + 47 * average_damage)
            + 52 * experience_difference
        ) / (165 * adjusted_rounds)

        overall_performance = (55 / 2) * math.sqrt(performance_score + z_factor)

        return {
            "op": overall_performance,
            "experience_difference": experience_difference,
            "adjusted_rounds": adjusted_rounds,
            "experience_per_round": experience_per_round,
            "average_damage": average_damage,
            "guard_objective": guard_objective,
            "z_factor": z_factor,
            "assassin_aggression": assassin_aggression,
            "performance_score": performance_score,
            "division": self.get_division(overall_performance),
        }

    def get_division(self, overall_performance):
        """
        Determine division based on OP score.

        Args:
            overall_performance (float): The calculated OP score.

        Returns:
            str: The corresponding division.
        """
        if overall_performance >= 945:
            return "Kugelblitz (S)"
        if overall_performance >= 900:
            return "Radiance (A+)"
        if overall_performance >= 840:
            return "Firestorm (A)"
        if overall_performance >= 785:
            return "Flashover (A-)"
        if overall_performance >= 735:
            return "Magnesium (B+)"
        if overall_performance >= 670:
            return "Thermite (B)"
        if overall_performance >= 605:
            return "Propane (C)"
        if overall_performance >= 535:
            return "Wood (D)"
        return "Ember (E)"

    async def handle_calc(self, stats: str, interaction=None, context=None):
        """
        Shared logic for !casual (text command) and /casual (slash command).

        Args:
            stats (str): The statistics as a space-separated string.
            interaction (discord.Interaction): The interaction object (optional).
            context (discord.Context): The context object (optional).
        """
        try:
            data = stats.split()

            metrics = self.calculate_metrics(
                {
                    "lva": int(data[0]),
                    "xpa": int(data[1]),
                    "lvb": int(data[2]),
                    "xpb": int(data[3]),
                    "rounds_played": int(data[4]),
                    "targets_assassinated": int(data[5]),
                    "escapes": int(data[6]),
                    "guards_killed": int(data[7]),
                    "targets_protected": int(data[8]),
                    "damage_dealt": int(data[9]),
                    "final_shots": int(data[10]),
                    "target_survivals": int(data[11]),
                    "ffa_kills": int(data[12]),
                    "ffa_wins": int(data[13]),
                    "infected_killed": int(data[14]),
                    "infection_survival": int(data[15]),
                    "infections": int(data[16]),
                    "epidemics": int(data[17]),
                }
            )

            # Determine embed title based on rounds played
            rounds_played = int(data[4])
            title = (
                "lifetime stats"
                if rounds_played >= 9216
                else "casual stats"
                if rounds_played >= 1536
                else "competitive stats"
            )

            embed = discord.Embed(
                title=title, color=discord.Color.from_rgb(82, 146, 209)
            )

            embed.description = (
                f"```glsl\n"
                f"OP = {metrics['op']:.0f}\n"
                f"TP = {metrics['performance_score']:.0f}, SP = {metrics['z_factor']:.0f}\n"
                f"[GO = {metrics['guard_objective']:.0f}], [AA = {metrics['assassin_aggression']:.0f}], [AD = {metrics['average_damage']:.0f}], [XPR = {metrics['experience_per_round']:.0f}]\n\n"
                f"Division: {metrics['division']}\n"
                f"```"
            )

            # Add Clear Button
            view = discord.ui.View()

            class ClearButton(discord.ui.Button):
                """A button to clear the calculation."""

                async def callback(self, interaction: discord.Interaction):
                    await interaction.response.edit_message(
                        content="In order to make your stats private, delete your prompt too!!1",
                        embed=None,
                        view=None,
                    )

            view.add_item(
                ClearButton(label="", style=discord.ButtonStyle.danger, emoji="🗑️")
            )

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
        name="casual", description="Calculate casual/lifetime OP from a copypasta"
    )
    async def casual_calc_slash(self, interaction: discord.Interaction, stats: str):
        """
        Slash command to calculate Casual/Lifetime OP.

        Args:
            interaction (discord.Interaction): The interaction object.
            stats (str): format: lva xpa lvb xpb rounds played to epidemic
        """
        await self.handle_calc(stats, interaction=interaction)

    @commands.command(
        name="casual", description="Calculate casual/lifetime OP from a copypasta"
    )
    async def casual_calc_text(self, ctx, *, stats: str):
        """
        Text command to calculate Casual OP.

        Args:
            ctx (discord.Context): The context object.
            stats (str): format: lva xpa lvb xpb rounds played to epidemic
        """
        await self.handle_calc(stats, context=ctx)


async def setup(bot):
    """
    Setup function to add the cog to the bot.

    Args:
        bot (discord.Bot): The bot instance.
    """
    await bot.add_cog(CasualCalcCog(bot))
