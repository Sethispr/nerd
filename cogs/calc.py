"""
This module contains the CalcCog, which provides a command to calculate OP (Overall Performance)
from various statistics in a game, including rounds played, kills, damage dealt, and more.
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
            auto_penalty = rounds_played + 3 * (0.12 * rounds_played - (targets_assassinated + target_survival))
            rounds_played = max(round(auto_penalty // 2 * 2), rounds_played)

        rounds_adjusted = rounds_played - escapes
        rounds_gamified = rounds_adjusted - escapes - target_survival - epidemic - infection_survival - free_for_all_wins

        s_ma = (2 / 3) * (sdi - 1) + 1 if sdi >= 1 else 1 + ((2 / 3) * (sdi - 1) + 1) - 1
        s_mb = (4 / 3) * (sdi - 1) + 1 if sdi >= 1 else 1 + ((4 / 3) * (sdi - 1) + 1) - 1

        g_os = 46 * ((sdi * 5 * final_shots + s_ma * 3 * targets_protected) / max(1, rounds_gamified))

        d_avg = damage_dealt / max(1, (rounds_adjusted - (escapes + target_survival + epidemic)))

        t_p = (2 * rounds_adjusted * (86 * g_os + s_mb * 32 * d_avg) + sdi * 59 * xpb_minus_xpa) / (165 * rounds_adjusted)
        z_p = (13 / rounds_adjusted) * (s_mb * (9 * free_for_all_kills + 15 * infected_killed + 40 * free_for_all_wins + 25 * infections + 100 * epidemic) + s_ma * 15 * infection_survival)
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
            "AutoPenalty": auto_penalty
        }

    @app_commands.command(name="calc", description="Calculate OP from a copypasta")
    @app_commands.describe(
        stats="Format: exp rounds played till epidemics sdi device"
    )
    async def calc(self, interaction: discord.Interaction, stats: str):
        """
        Calculate the OP from a set of game statistics.

        Args:
            interaction (discord.Interaction): The interaction object.
            stats (str): A string containing the game statistics in a specific format.
        """
        try:
            data = stats.split()
            if len(data) != 16:
                raise ValueError("invalid number of parameters, expected 16 values!!1~!1!!!")

            xpb_minus_xpa = int(data[0])
            rounds_played = int(data[1])
            targets_assassinated = int(data[2])
            escapes = int(data[3])
            targets_protected = int(data[4])
            damage_dealt = int(data[5])
            final_shots = int(data[6])
            target_survival = int(data[7])
            free_for_all_kills = int(data[8])
            free_for_all_wins = int(data[9])
            infected_killed = int(data[10])
            infection_survival = int(data[11])
            infections = int(data[12])
            epidemic = int(data[13])
            sdi = float(data[14])
            device = data[15].lower()

            if device == "laptop":
                device = "pc"

            metrics = self.calculate_metrics(
                {
                    "rounds_played": rounds_played,
                    "targets_assassinated": targets_assassinated,
                    "escapes": escapes,
                    "targets_protected": targets_protected,
                    "damage_dealt": damage_dealt,
                    "final_shots": final_shots,
                    "target_survival": target_survival,
                    "free_for_all_kills": free_for_all_kills,
                    "free_for_all_wins": free_for_all_wins,
                    "infected_killed": infected_killed,
                    "infection_survival": infection_survival,
                    "infections": infections,
                    "epidemic": epidemic,
                    "xpb_minus_xpa": xpb_minus_xpa
                },
                sdi=sdi,
                device=device
            )

            if metrics:
                auto_penalty = metrics.get("AutoPenalty")
                title = ""
                if auto_penalty:
                    title = f"auto-penalty: +{int(auto_penalty - rounds_played)} rounds"

                embed = discord.Embed(
                    title=title,
                    color=discord.Color.from_rgb(82,146,209)
                )

                formatted_message = (
                    f"```glsl\n"
                    f"OP = {int(metrics['OP'])}\n"
                    f"TP = {int(metrics['TP'])}, SP = {int(metrics['SP'])}\n"
                    f"[GO = {int(metrics['GO'])}], [AD = {int(metrics['AD'])}], [XPR = {int(metrics['XPR'])}]\n"
                    f"SDI = {metrics['SDI']:.4f}\n\n"
                    f"Division: {metrics['Division']}\n"
                    f"```"
                )

                embed.description = formatted_message

                seths_button = discord.ui.Button(style=discord.ButtonStyle.url, label="web", url="https://sethispr.github.io/fos/")
                user_input_button = discord.ui.Button(label="", style=discord.ButtonStyle.success, emoji="📄")
                trash_button = discord.ui.Button(label="", style=discord.ButtonStyle.danger, emoji="🗑️")

                async def show_input_callback(interaction):
                    input_stats_message = (
                        f"```glsl\n"
                        f"Experience: {xpb_minus_xpa}\n"
                        f"Rounds Played: {rounds_played}\n"
                        f"Targets Assassinated: {targets_assassinated}\n"
                        f"Escapes: {escapes}\n"
                        f"Targets Protected: {targets_protected}\n"
                        f"Damage Dealt: {damage_dealt}\n"
                        f"Final Shots: {final_shots}\n"
                        f"Target Survivals: {target_survival}\n"
                        f"Free For All Kills: {free_for_all_kills}\n"
                        f"Free For All Wins: {free_for_all_wins}\n"
                        f"Infected Killed: {infected_killed}\n"
                        f"Infection Survival: {infection_survival}\n"
                        f"Infections: {infections}\n"
                        f"Epidemic: {epidemic}\n"
                        f"SDI: {sdi}\n"
                        f"Device: {device}\n"
                        f"```"
                    )
                    await interaction.response.send_message(input_stats_message, ephemeral=True)

                async def clear_message_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    await interaction.message.delete()

                user_input_button.callback = show_input_callback
                trash_button.callback = clear_message_callback

                view = discord.ui.View()
                view.add_item(seths_button)
                view.add_item(user_input_button)
                view.add_item(trash_button)

                await interaction.response.send_message(embed=embed, view=view)

            else:
                await interaction.response.send_message("invalid calculation, please check your input.")

        except Exception as e:
            await interaction.response.send_message(f"ULTRA RARE ERROR: {str(e)}")

async def setup(bot):
    """
    Setup function to add the CalcCog to the bot.

    Args:
        bot (discord.Bot): The bot instance.
    """
    await bot.add_cog(CalcCog(bot))
