import discord
from discord import app_commands
from discord.ext import commands
import math

class CalcCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def calculate_metrics(self, rounds_played, targets_assassinated, escapes, targets_protected,
                          damage_dealt, final_shots, target_survival, free_for_all_kills,
                          free_for_all_wins, infected_killed, infection_survival, infections,
                          epidemic, xpb_minus_xpa, sdi=1, device="pc"):
        R = rounds_played
        D = damage_dealt
        T = targets_assassinated
        t = target_survival
        F = free_for_all_kills
        w = free_for_all_wins
        i = infected_killed
        s = infection_survival
        I = infections
        E = escapes
        Sf = final_shots
        P = targets_protected
        e_p = epidemic
        X_T = xpb_minus_xpa

        auto_penalty = None
        if (T + t) / R < 0.12:
            auto_penalty = R + 3 * (0.12 * R - (T + t))
            R = max(round(auto_penalty // 2 * 2), R)

        R_ad = R - E
        R_g = R_ad - E - t - e_p - s - w

        S_ma = (2 / 3) * (sdi - 1) + 1 if sdi >= 1 else 1 + ((2 / 3) * (sdi - 1) + 1) - 1
        S_mb = (4 / 3) * (sdi - 1) + 1 if sdi >= 1 else 1 + ((4 / 3) * (sdi - 1) + 1) - 1

        g_os = 46 * ((sdi * 5 * Sf + S_ma * 3 * P) / max(1, R_g))

        D_avg = D / max(1, (R_ad - (E + t + e_p)))

        t_p = (2 * R_ad * (86 * g_os + S_mb * 32 * D_avg) + sdi * 59 * X_T) / (165 * R_ad)
        z_p = (13 / R_ad) * (S_mb * (9 * F + 15 * i + 40 * w + 25 * I + 100 * e_p) + S_ma * 15 * s)
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

        x_pr = X_T / max(1, R_ad)

        return {
            "OP": boosted_o_p,
            "TP": t_p,
            "SP": z_p,
            "GO": g_os,
            "AD": D_avg,
            "XPR": x_pr,
            "Division": division,
            "SDI": sdi,
            "AutoPenalty": auto_penalty
        }

    @app_commands.command(name="calc", description="Calculate OP from a copypasta")
    @app_commands.describe(
        stats=(
            "Format: exp rounds played till epidemics sdi device"
        )
    )
    async def calc(self, interaction: discord.Interaction, stats: str):
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
                rounds_played, targets_assassinated, escapes, targets_protected,
                damage_dealt, final_shots, target_survival, free_for_all_kills,
                free_for_all_wins, infected_killed, infection_survival, infections,
                epidemic, xpb_minus_xpa, sdi, device
            )

            if metrics:
                auto_penalty = metrics.get("AutoPenalty")
                title = ""
                if auto_penalty:
                    title = f"auto-penalty: +{int(auto_penalty - rounds_played)} rounds"

                embed = discord.Embed(
                    title=title,
                    color=discord.Color.from_rgb(250, 254, 99)
                )

                formatted_message = (
                    f"```glsl\n"
                    f"OP = {int(metrics['OP'])}\n"
                    f"TP = {int(metrics['TP'])}, SP = {int(metrics['SP'])}\n"
                    f"[GO = {int(metrics['GO'])}], [AD = {int(metrics['AD'])}], [XPR = {int(metrics['XPR'])}]\n"
                    f"SDI = {metrics['SDI']:.4f}\n\n"
                    f"Division: {metrics['Division']}\n"
                    f"```")

                embed.description = formatted_message

                desmos_button = discord.ui.Button(style=discord.ButtonStyle.url, label="desmos", url="https://www.desmos.com/calculator/m60vove8wv")
                seths_button = discord.ui.Button(style=discord.ButtonStyle.url, label="web", url="https://sethispr.github.io/fos/")
                user_input_button = discord.ui.Button(label="show input", style=discord.ButtonStyle.primary)
                
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
                        f"```")
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
    await bot.add_cog(CalcCog(bot))
