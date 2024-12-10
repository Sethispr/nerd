require 'mathn'

# The GameMetricsCalculator class calculates various performance metrics
# based on user input related to in-game statistics.
#
# It uses the provided statistics to calculate overall performance points (OP),
# target protection (TP), survival points (SP), and other important metrics
# that can be used to determine the player's in-game division.
#
# It also takes into account the device type for calculating a device multiplier.
class GameMetricsCalculator
  # Device multipliers for various platforms.
  DEVICE_MULTIPLIERS = {
    'phone' => 1.075,
    'mobile' => 1.075,
    'tablet' => 1.05,
    'console' => 1.10,
    'pc' => 1.0,
    'laptop' => 1.0,
    'ps' => 1.10,
    'xbox' => 1.10
  }.freeze

  # Calculates various game metrics based on the provided stats, SDI, and device.
  #
  # @param stats [Hash] The in-game statistics including damage dealt, rounds played, etc.
  # @param sdi [Float] The SDI (Skill Development Index) value, default is 1.
  # @param device [String] The device used to play the game, default is 'pc'.
  # @return [Hash] A hash containing calculated metrics like OP, TP, SP, etc.
  def calculate_metrics(stats, sdi = 1, device = 'pc')
    rounds_played = stats[:rounds_played]
    damage_dealt = stats[:damage_dealt]
    targets_assassinated = stats[:targets_assassinated]
    target_survival = stats[:target_survival]
    free_for_all_kills = stats[:free_for_all_kills]
    free_for_all_wins = stats[:free_for_all_wins]
    infected_killed = stats[:infected_killed]
    infection_survival = stats[:infection_survival]
    infections = stats[:infections]
    escapes = stats[:escapes]
    final_shots = stats[:final_shots]
    targets_protected = stats[:targets_protected]
    epidemic = stats[:epidemic]
    xpb_minus_xpa = stats[:xpb_minus_xpa]

    auto_penalty = calculate_auto_penalty(targets_assassinated, target_survival, rounds_played)

    rounds_adjusted = rounds_played - escapes
    rounds_gamified = rounds_adjusted - escapes - target_survival - epidemic - infection_survival - free_for_all_wins

    s_ma = calculate_s_ma(sdi)
    s_mb = calculate_s_mb(sdi)

    g_os = calculate_g_os(sdi, final_shots, s_ma, targets_protected, rounds_gamified)
    d_avg = calculate_d_avg(damage_dealt, rounds_adjusted, escapes, target_survival, epidemic)
    t_p = calculate_t_p(rounds_adjusted, g_os, s_mb, d_avg, xpb_minus_xpa)
    z_p = calculate_z_p(rounds_adjusted, s_mb, free_for_all_kills, infected_killed, free_for_all_wins, infections, epidemic, s_ma, infection_survival)

    o_p = calculate_o_p(t_p, z_p)

    boosted_o_p = o_p * device_multiplier(device)

    division = determine_division(boosted_o_p)

    x_pr = xpb_minus_xpa / [1, rounds_adjusted].max

    {
      OP: boosted_o_p,
      TP: t_p,
      SP: z_p,
      GO: g_os,
      AD: d_avg,
      XPR: x_pr,
      Division: division,
      SDI: sdi,
      AutoPenalty: auto_penalty
    }
  end

  private

  # Calculates the auto penalty for a player based on their targets assassinated,
  # target survival, and the total number of rounds played.
  #
  # @param targets_assassinated [Integer] The number of targets assassinated.
  # @param target_survival [Integer] The number of rounds the player survived.
  # @param rounds_played [Integer] The total number of rounds played.
  # @return [Integer, nil] The calculated auto penalty, or nil if no penalty applies.
  def calculate_auto_penalty(targets_assassinated, target_survival, rounds_played)
    if (targets_assassinated + target_survival) / rounds_played < 0.12
      auto_penalty = rounds_played + 3 * (0.12 * rounds_played - (targets_assassinated + target_survival))
      return [round(auto_penalty / 2.0) * 2, rounds_played].max
    end
    nil
  end

  # Calculates the S_ma value based on the provided SDI.
  #
  # @param sdi [Float] The SDI value.
  # @return [Float] The calculated S_ma value.
  def calculate_s_ma(sdi)
    return (2.0 / 3) * (sdi - 1) + 1 if sdi >= 1

    1 + ((2.0 / 3) * (sdi - 1) + 1) - 1
  end

  # Calculates the S_mb value based on the provided SDI.
  #
  # @param sdi [Float] The SDI value.
  # @return [Float] The calculated S_mb value.
  def calculate_s_mb(sdi)
    return (4.0 / 3) * (sdi - 1) + 1 if sdi >= 1

    1 + ((4.0 / 3) * (sdi - 1) + 1) - 1
  end

  # Calculates the game score (G_os) based on the provided SDI, final shots, 
  # S_ma, targets protected, and adjusted rounds.
  #
  # @param sdi [Float] The SDI value.
  # @param final_shots [Integer] The number of final shots.
  # @param s_ma [Float] The S_ma value.
  # @param targets_protected [Integer] The number of targets protected.
  # @param rounds_gamified [Integer] The number of gamified rounds.
  # @return [Float] The calculated game score (G_os).
  def calculate_g_os(sdi, final_shots, s_ma, targets_protected, rounds_gamified)
    46 * ((sdi * 5 * final_shots + s_ma * 3 * targets_protected) / [1, rounds_gamified].max)
  end

  # Calculates the average damage dealt per round, adjusted for escapes and survival.
  #
  # @param damage_dealt [Integer] The total damage dealt.
  # @param rounds_adjusted [Integer] The number of adjusted rounds.
  # @param escapes [Integer] The number of escapes.
  # @param target_survival [Integer] The number of rounds survived.
  # @param epidemic [Integer] The number of epidemic rounds.
  # @return [Float] The average damage dealt per round.
  def calculate_d_avg(damage_dealt, rounds_adjusted, escapes, target_survival, epidemic)
    damage_dealt / [1, rounds_adjusted - (escapes + target_survival + epidemic)].max
  end

  # Calculates the target protection (TP) based on various game factors.
  #
  # @param rounds_adjusted [Integer] The number of adjusted rounds.
  # @param g_os [Float] The game score.
  # @param s_mb [Float] The S_mb value.
  # @param d_avg [Float] The average damage dealt.
  # @param xpb_minus_xpa [Integer] The XPB minus XPA value.
  # @return [Float] The calculated target protection value.
  def calculate_t_p(rounds_adjusted, g_os, s_mb, d_avg, xpb_minus_xpa)
    (2 * rounds_adjusted * (86 * g_os + s_mb * 32 * d_avg) + sdi * 59 * xpb_minus_xpa) / (165 * rounds_adjusted)
  end

  # Calculates the survival points (SP) based on various factors like free-for-all kills,
  # infected kills, and infections.
  #
  # @param rounds_adjusted [Integer] The number of adjusted rounds.
  # @param s_mb [Float] The S_mb value.
  # @param free_for_all_kills [Integer] The number of free-for-all kills.
  # @param infected_killed [Integer] The number of infected killed.
  # @param free_for_all_wins [Integer] The number of free-for-all wins.
  # @param infections [Integer] The number of infections.
  # @param epidemic [Integer] The number of epidemic rounds.
  # @param s_ma [Float] The S_ma value.
  # @param infection_survival [Integer] The infection survival value.
  # @return [Float] The calculated survival points.
  def calculate_z_p(rounds_adjusted, s_mb, free_for_all_kills, infected_killed, free_for_all_wins, infections, epidemic, s_ma, infection_survival)
    (13 / rounds_adjusted) * (
      s_mb * (9 * free_for_all_kills + 15 * infected_killed + 40 * free_for_all_wins + 25 * infections + 100 * epidemic) +
      s_ma * 15 * infection_survival
    )
  end

  # Calculates the overall performance points (OP) based on target protection and survival points.
  #
  # @param t_p [Float] The target protection value.
  # @param z_p [Float] The survival points value.
  # @return [Float] The overall performance points (OP).
  def calculate_o_p(t_p, z_p)
    (529 / 20) * Math.sqrt(t_p + z_p)
  end

  # Multiplies the overall performance points (OP) by a device multiplier.
  #
  # @param device [String] The device name.
  # @return [Float] The device multiplier, or 1.0 if no multiplier is found.
  def device_multiplier(device)
    DEVICE_MULTIPLIERS[device] || 1.0
  end

  # Determines the player's division based on the overall performance points (OP).
  #
  # @param boosted_o_p [Float] The boosted overall performance points (OP).
  # @return [String] The determined division.
  def determine_division(boosted_o_p)
    case boosted_o_p
    when 975..Float::INFINITY then 'Kugelblitz (S)'
    when 935...975 then 'Radiance (A+)'
    when 870...935 then 'Firestorm (A)'
    when 820...870 then 'Flashover (A-)'
    when 765...820 then 'Magnesium (B+)'
    when 705...765 then 'Thermite (B)'
    when 635...705 then 'Propane (C)'
    when 560...635 then 'Wood (D)'
    else 'Ember (E)'
    end
  end
end
