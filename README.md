<div align="center">
  
  # Nerd Bot
  
[![Better Stack Badge](https://uptime.betterstack.com/status-badges/v3/monitor/1p3v3.svg)](https://fos.betteruptime.com/)
</div>

[![Github Pages](https://img.shields.io/badge/github%20pages-121013?style=for-the-badge&logo=github&logoColor=white)](https://sethispr.github.io/nerd/) 


Welcome to the documentation for **Nerd Bot** – a Discord bot to calculate your in-game statistics. This guide will help you get started and make the most out of Nerd Bot's one literal command /calc.

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Parameters Explained](#parameters-explained)
3. [Example Usage](#example-usage)
4. [Understanding Results](#understanding-results)

---

## 2. Basic Usage

The primary command to interact with Nerd Bot is `/calc`. This command processes your in-game statistics* (as an input) and returns the formatted calculations back to you.

### Command Format:
```glsl
/calc [experience] [rounds] [targets] [escapes] [protected] [damage] [final shots] [survival] [ffa kills] [ffa wins] [infected killed] [infection survival] [infections] [epidemic] [sdi] [device]
```

---

## 3. Parameters Explained

Here’s a breakdown of the parameters you need to input when using the `/calc` command:

- **Experience (XP)**: Your experience values, typically represented as XPB minus XPA, or second screenshot XP left needed to level up minus first screenshot current XP gained
- **In-game stats**: Rounds played stat till Epidemic stat
- **SDI (Server Difficulty Index)**: A value reflecting the server's difficulty level (usually between 0.9 and 1.3).
- **Device**: The platform you are playing on (pc/laptop, phone, tablet, console).

---

## 4. Example Usage

To use Nerd Bot, simply type the `/calc` command then the press the "Enter" key and followed by your in-game statistics, formatted like so:

```
/calc 92086 221 3 3 72 120133 45 25 441 16 321 14 30 3 0.9992 pc
```

### Notes:
- Ensure that you input all stats in the correct order and format.
- Hit "Enter" after typing the `/calc` command followed by your stats.

---

## 5. Understanding Results

Once you run the `/calc` command with your stats, Nerd Bot will return results similar to the following:

```glsl
OP = 905
TP = 534, SP = 636
[GO = 129], [AD = 642], [XPR = 422]
SDI = 0.9992
Division: Firestorm (A)
```

### Metrics Explained:

- **OP (Overall Performance)**: Your total performance score combining all game stats
- **TP (Tactical Performance)**: Score based on your tactical gameplay
- **SP (Special Performance)**: Score reflecting your performance in special game modes (e.g. FFA, Infection)
- **SDI (Server Difficulty Index)**: Reflects the difficulty level of the server you're playing on
- **Division**: Your ranking division based on your OP score (e.g. Firestorm Division A)

---

For any further assistance or questions, feel free to reach out to the @Nerds or @sethyl

---
