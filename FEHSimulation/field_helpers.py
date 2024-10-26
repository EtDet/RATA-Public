# This file holds several methods to carry out the following functions for game.py:
# - Start of turn skills
# - Warp tiles
# - Combat Fields
# - Post-combat effects

from hero import *
from combat import CombatField

within_1_space = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
within_2_space = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2

def create_combat_fields(player_team, enemy_team):
    combat_fields = []

    for unit in player_team + enemy_team:

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()

        owner = unit

        if "spurAtk" in unitSkills:
            range = within_1_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"spurAtk_f": unitSkills["spurAtk"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "driveAtk" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"spurAtk_f": unitSkills["driveAtk"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "spurSpd" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"spurSpd_f": unitSkills["spurSpd"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "driveSpd" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"driveSpd_f": unitSkills["driveSpd"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "spurDef" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"spurDef_f": unitSkills["spurDef"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "driveDef" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"driveDef_f": unitSkills["driveDef"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "spurRes" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"spurRes_f": unitSkills["spurRes"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "driveRes" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"driveRes_f": unitSkills["driveRes"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "goadCav" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"goadCav_f": 0}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "wardCav" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"wardCav_f": 0}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "goadFly" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"goadFly_f": 0}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "wardFly" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"wardFly_f": 0}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "goadArmor" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"goadArmor_f": 0}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "wardArmor" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"wardArmor_f": 0}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "spdRC" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 or abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = False
            effects = {"spdRC_f": unitSkills["spdRC"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "defRC" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 or abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = False
            effects = {"defRC_f": unitSkills["defRC"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "cruxField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 or abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = False
            effects = {"cruxField_f": unitSkills["cruxField"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        # UNIQUE STUFF

        if "driveSpectrum" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"driveSpectrum_f": unitSkills["driveSpectrum"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "gordin_field" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = False
            effects = {"gordin_field_f": unitSkills["gordin_field"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        # Mathilda/Clive
        if "jointSupportPartner" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: o.isSupportOf(s)
            affect_self = False
            affect_other_side = True
            effects = {"jointSupportPartner_f": 3}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "oscarDrive" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: o.move == 0 or o.move == 1
            affect_self = False
            affect_other_side = True
            effects = {"oscarDrive_f": unitSkills["oscarDrive"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        # B!Lucina
        if "lucinaDrive" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: o.wpnType in MELEE_WEAPONS
            affect_self = False
            affect_other_side = True
            effects = {"lucinaDrive": unitSkills["lucinaDrive_f"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "refinedLucinaDrive" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: o.wpnType in PHYSICAL_WEAPONS
            affect_self = False
            affect_other_side = True
            effects = {"refinedLucinaDrive": unitSkills["refinedLucinaDrive_f"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "tharja_field" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = False
            effects = {"tharja_field_f": unitSkills["tharja_field"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        # H!Nowi
        if "nowiField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 3
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = False
            effects = {"nowiField_f": unitSkills["nowiField"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)


        if "supportThem" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: o.allySupport == s.intName
            affect_self = False
            affect_other_side = True
            effects = {"corrinField_f": unitSkills["supportThem"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "gunterJointDrive" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"gunterJointDrive_f": 5}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "camillaField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"camillaField_f": unitSkills["camillaField"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "eliseField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = False
            effects = {"eliseField_f": unitSkills["eliseField"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "reginnAccel" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 or abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"reginnField_f": unitSkills["reginnAccel"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)


    return combat_fields

def start_of_turn(starting_team, waiting_team, turn):

    # Return units within a given team with the greatest of a given stat
    def units_with_extreme_stat(cur_team, stat, find_max=True):
        if not cur_team:
            return []

        extreme_stat = cur_team[0].visible_stats[stat]
        extreme_stat_units = [cur_team[0]]

        for unit in cur_team[1:]:
            unit_stat = unit.visible_stats[stat]

            if (find_max and unit_stat == extreme_stat) or (not find_max and unit_stat == extreme_stat):
                extreme_stat_units.append(unit)

            if (find_max and unit_stat > extreme_stat) or (not find_max and unit_stat < extreme_stat):
                extreme_stat = unit_stat
                extreme_stat_units = [unit]

        return extreme_stat_units

    sp_charges = {}
    for unit in starting_team + waiting_team:
        sp_charges[unit] = 0

    # LOOP 1: BUFFS, DEBUFFS, AND STATUS EFFECTS
    for unit in starting_team:
        tile = unit.tile

        tiles_within_n_spaces = [[]]
        units_within_n_spaces = [[]]
        allies_within_n_spaces = [[]]
        foes_within_n_spaces = [[]]

        i = 1
        while i <= 5:
            tiles_within_n_spaces.append(tile.tilesWithinNSpaces(i))

            units_within_n_spaces.append([])
            allies_within_n_spaces.append([])
            foes_within_n_spaces.append([])

            for tile_within in tiles_within_n_spaces[i]:

                if tile_within.hero_on is not None:
                    units_within_n_spaces[i].append(tile_within.hero_on)

                    if unit.side == tile_within.hero_on.side and unit != tile_within.hero_on:
                        allies_within_n_spaces[i].append(tile_within.hero_on)
                    if unit.side != tile_within.hero_on.side:
                        foes_within_n_spaces[i].append(tile_within.hero_on)

            i += 1

        tiles_within_1_col = tile.tilesWithinNCols(1)
        tiles_within_1_row = tile.tilesWithinNRows(1)
        tiles_within_1_row_or_column = list(set(tiles_within_1_col) | set(tiles_within_1_row))

        tiles_within_3_col = tile.tilesWithinNCols(3)
        tiles_within_3_row = tile.tilesWithinNRows(3)
        tiles_within_3_row_or_column = list(set(tiles_within_3_col) | set(tiles_within_3_row))

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur


        atkHPGreaterEqual25Percent = unitHPCur / unitStats[0] >= 0.25
        atkHPGreaterEqual50Percent = unitHPCur / unitStats[0] >= 0.50
        atkHPGreaterEqual75Percent = unitHPCur / unitStats[0] >= 0.75
        atkHPEqual100Percent = unitHPCur == unitStats[0]

        # All allies
        allies = []
        for hero in starting_team:
            if hero is not unit:
                allies.append(hero)

        # HONE/FORTIFY

        if "honeAtk" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(ATK, unitSkills["honeAtk"])

        if "honeAtkW" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(ATK, unitSkills["honeAtkW"])

        if "honeSpd" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(SPD, unitSkills["honeSpd"])

        if "fortifyDef" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(DEF, unitSkills["fortifyDef"])

        if "fortifyRes" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(RES, unitSkills["fortifyRes"])

        if "honecav" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 1:
                    ally.inflictStat(ATK, 6)
                    ally.inflictStat(SPD, 6)

        if "forticav" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 1:
                    ally.inflictStat(DEF, 6)
                    ally.inflictStat(RES, 6)

        if "honefly" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 2:
                    ally.inflictStat(ATK, 6)
                    ally.inflictStat(SPD, 6)

        if "fortifly" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 2:
                    ally.inflictStat(DEF, 6)
                    ally.inflictStat(RES, 6)

        if "honearmor" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 3:
                    ally.inflictStat(ATK, 6)
                    ally.inflictStat(SPD, 6)

        if "fortiarmor" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 3:
                    ally.inflictStat(DEF, 6)
                    ally.inflictStat(RES, 6)

        if "honedragon" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.wpnType in DRAGON_WEAPONS:
                    ally.inflictStat(ATK, 6)
                    ally.inflictStat(SPD, 6)

        if "fortidragon" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.wpnType in DRAGON_WEAPONS:
                    ally.inflictStat(DEF, 6)
                    ally.inflictStat(RES, 6)

        # THREATEN

        if "threatenAtk" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                foe.inflictStat(ATK, -unitSkills["threatenAtk"])

        if "threatenAtkW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                foe.inflictStat(ATK, -unitSkills["threatenAtkW"])

        if "threatenSpd" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                foe.inflictStat(SPD, -unitSkills["threatenSpd"])

        if "threatenSpdW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                foe.inflictStat(SPD, -unitSkills["threatenSpdW"])

        if "threatenDef" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                foe.inflictStat(DEF, -unitSkills["threatenDef"])

        if "threatenDefW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                foe.inflictStat(DEF, -unitSkills["threatenDefW"])

        if "threatenRes" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                foe.inflictStat(RES, -unitSkills["threatenRes"])

        if "threatenResW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                foe.inflictStat(RES, -unitSkills["threatenResW"])

        # DEFIANT SKILLS
        def apply_defiant(defiant_type):

            if (defiant_type in unitSkills or f"{defiant_type}Se" in unitSkills) and unit.HPcur / unitStats[0] <= 0.50:

                stat = defiant_types.index(defiant_type) + 1

                if defiant_type in unitSkills: unit.inflictStat(stat, 2 * unitSkills[defiant_type] + 1)
                if f"{defiant_type}Se" in unitSkills: unit.inflictStat(stat, 2 * unitSkills[f"{defiant_type}Se"] + 1)

        defiant_types = ["defiantAtk", "defiantSpd", "defiantDef", "defiantRes"]
        for defiant in defiant_types:
            apply_defiant(defiant)


        # PLOY SKILLS
        def apply_ploy(ploy_type):
            if ploy_type in unitSkills or f"{ploy_type}W" in unitSkills:
                valid_foes = [p_tile.hero_on for p_tile in tiles_within_1_row_or_column if p_tile.hero_on is not None and p_tile.hero_on.isEnemyOf(unit)]

                for foe in valid_foes:
                    unit_res = unit.visible_stats[RES]
                    foe_res = foe.visible_stats[RES]

                    if "phantomRes" in unitSkills: unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills(): foe_res += foe.getSkills()["phantomRes"]

                    if unit_res > foe_res:
                        stat = ploy_types.index(ploy_type) + 1

                        if ploy_type in unitSkills: foe.inflictStat(stat, -unitSkills[ploy_type])
                        if f"{ploy_type}W" in unitSkills: foe.inflictStat(stat, -unitSkills[f"{ploy_type}W"])

        ploy_types = ["atkPloy", "spdPloy", "defPloy", "resPloy"]
        for ploy in ploy_types:
            apply_ploy(ploy)

        if "atkLargePloyW" in unitSkills:
            valid_foes = [p_tile.hero_on for p_tile in tiles_within_3_row_or_column if p_tile.hero_on is not None and p_tile.hero_on.isEnemyOf(unit)]

            for foe in valid_foes:
                unit_res = unit.visible_stats[RES]
                foe_res = foe.visible_stats[RES]

                if "phantomRes" in unitSkills: unit_res += unit.getSkills()["phantomRes"]
                if "phantomRes" in foe.getSkills(): foe_res += foe.getSkills()["phantomRes"]

                if unit_res > foe_res:
                    foe.inflictStat(ATK, -unitSkills["atkLargePloyW"])

        if "resLargePloyW" in unitSkills:
            valid_foes = [p_tile.hero_on for p_tile in tiles_within_3_row_or_column if p_tile.hero_on is not None and p_tile.hero_on.isEnemyOf(unit)]

            for foe in valid_foes:
                unit_res = unit.visible_stats[RES]
                foe_res = foe.visible_stats[RES]

                if "phantomRes" in unitSkills: unit_res += unit.getSkills()["phantomRes"]
                if "phantomRes" in foe.getSkills(): foe_res += foe.getSkills()["phantomRes"]

                if unit_res > foe_res:
                    foe.inflictStat(RES, -unitSkills["resLargePloyW"])

        if "panicPloy" in unitSkills:
            diff = 7 - unitSkills["panicPloy"] * 2
            for tile in tiles_within_1_row_or_column:
                if tile.hero_on is not None and tile.hero_on.side != unit.side:
                    if tile.hero_on.HPcur <= unit.HPcur - diff:
                        tile.hero_on.inflictStatus(Status.Panic)

        if "panicPloyW" in unitSkills:
            diff = 7 - unitSkills["panicPloyW"] * 2
            for tile in tiles_within_1_row_or_column:
                if tile.hero_on is not None and tile.hero_on.side != unit.side:
                    if tile.hero_on.HPcur <= unit.HPcur - diff:
                        tile.hero_on.inflictStatus(Status.Panic)

        # TACTIC SKILLS
        if "spdTacticW" in unitSkills:
            move_arrs = [[], [], [], []]
            for ally in allies_within_n_spaces[2]:
                move_arrs[ally.move].append(ally)

            for arr in move_arrs:
                if len(arr) <= 2:
                    for ally in arr:
                        ally.inflictStat(SPD, 6)

        if "resTacticW" in unitSkills:
            move_arrs = [[], [], [], []]
            for ally in allies_within_n_spaces[2]:
                move_arrs[ally.move].append(ally)

            for arr in move_arrs:
                if len(arr) <= 2:
                    for ally in arr:
                        ally.inflictStat(RES, 6)

        # CHILL SKILLS
        if "chillAtkW" in unitSkills:
            highest_atk = units_with_extreme_stat(waiting_team, ATK, find_max=True)
            for foe in highest_atk:
                foe.inflictStat(ATK, -7)

        if "chillDefW" in unitSkills:
            highest_def = units_with_extreme_stat(waiting_team, DEF, find_max=True)
            for foe in highest_def:
                foe.inflictStat(DEF, -7)

        if "chillResW" in unitSkills:
            highest_res = units_with_extreme_stat(waiting_team, RES, find_max=True)
            for foe in highest_res:
                foe.inflictStat(RES, -7)

        if "gunterChill" in unitSkills:
            lowest_spd = units_with_extreme_stat(waiting_team, SPD, find_max=False)
            for foe in lowest_spd:
                foe.inflictStat(ATK, -5)
                foe.inflictStat(DEF, -5)

        # SP CHARGE

        # Wrath
        if "wrathW" in unitSkills and unitHPCur / unitStats[0] <= unitSkills["wrathW"] * 0.25 and unit.getSpecialType() in ["Offense", "AOE"]:
            sp_charges[unit] += 1

        if "wrathSk" in unitSkills and unitHPCur / unitStats[0] <= unitSkills["wrathSk"] * 0.25 and unit.getSpecialType() in ["Offense", "AOE"]:
            sp_charges[unit] += 1

        # Time's Pulse
        if "timesPulseSp" in unitSkills and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # Turn 1 Pulse
        if "turn1Pulse" in unitSkills and turn == 1:
            sp_charges[unit] += unitSkills["turn1Pulse"]

        if "turn1PulseD" in unitSkills and turn == 1 and unit.getSpecialType() == "Defense": # Defensive Specials Only
            sp_charges[unit] += unitSkills["turn1PulseD"]

        if "infantryPulse" in unitSkills and turn == 1:
            for ally in waiting_team:
                if unit.HPcur - (7 * unitSkills["infantryPulse"]) > ally.HPcur and ally.move == 0:
                    sp_charges[ally] += 1

        # WAVE SKILLS
        if "evenAtkWaveW" in unitSkills and turn % 2 == 0:
            unit.inflictStat(ATK, unitSkills["evenAtkWaveW"])
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(ATK, unitSkills["evenAtkWaveW"])

        if "oddDefWave" in unitSkills and turn % 2 == 1:
            unit.inflictStat(DEF, unitSkills["oddDefWave"])
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(DEF, unitSkills["oddDefWave"])

        if "premiumResWave" in unitSkills:
            unit.inflictStat(RES, 6)
            for ally in allies_within_n_spaces[2]:
                ally.inflictStat(RES, 6)

        # SABOTAGE SKILLS

        if "sabotageAtkW" in unitSkills:
            for foe in waiting_team:

                if allies_within_n(foe, 1):
                    unit_res = unit.visible_stats[RES]
                    foe_res = foe.visible_stats[RES]

                    if "phantomRes" in unit.getSkills():
                        unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills():
                        foe_res += foe.getSkills()["phantomRes"]

                    if foe_res <= unit_res - 3:
                        foe.inflictStat(ATK, -7)

        if "sabotageSpdW" in unitSkills:
            for foe in waiting_team:

                if allies_within_n(foe, 1):
                    unit_res = unit.visible_stats[RES]
                    foe_res = foe.visible_stats[RES]

                    if "phantomRes" in unit.getSkills():
                        unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills():
                        foe_res += foe.getSkills()["phantomRes"]

                    if foe_res <= unit_res - 3:
                        foe.inflictStat(SPD, -unitSkills["sabotageSpdW"])

        if "sabotageResW" in unitSkills:
            for foe in waiting_team:

                if allies_within_n(foe, 1):
                    unit_res = unit.visible_stats[RES]
                    foe_res = foe.visible_stats[RES]

                    if "phantomRes" in unit.getSkills():
                        unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills():
                        foe_res += foe.getSkills()["phantomRes"]

                    if foe_res <= unit_res - 3:
                        foe.inflictStat(SPD, -unitSkills["sabotageResW"])

        # STATUSES
        if "armorMarch" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["armorMarch"]:
            ally_cond = False
            for ally in allies_within_n_spaces[1]:
                if ally.move == 3:

                    ally.inflictStatus(Status.MobilityUp)
                    ally_cond = True

            if ally_cond:
                unit.inflictStatus(Status.MobilityUp)




        # THE UNIQUE SKILL STUFF

        # Aura - Linde
        if "lindeAtkBuff" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                if ally.wpnType in TOME_WEAPONS or ally.wpnType == "Staff":
                    ally.inflictStat(ATK, 6)

        # Dark Aura - Linde/Delthea
        if "darkAuraBuff" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                if ally.wpnType in MELEE_WEAPONS:
                    ally.inflictStat(ATK, 6)

        # Eternal Breath - Fae
        if "honeFae" in unitSkills and allies_within_n_spaces[2]:
            unit.inflictStat(ATK, 5)
            unit.inflictStat(SPD, 5)
            unit.inflictStat(DEF, 5)
            unit.inflictStat(RES, 5)

            for ally in allies_within_n_spaces[2]:
                ally.inflictStat(ATK, 5)
                ally.inflictStat(SPD, 5)
                ally.inflictStat(DEF, 5)
                ally.inflictStat(RES, 5)

        # Echesacks (Refine) - Zephiel
        if "i <3 dragons" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                if foe.wpnType not in DRAGON_WEAPONS:
                    foe.inflictStat(DEF, -6)

        # Sisterly Axe - X!Eirika
        if "sisterlyBoost" in unitSkills and allies_within_n_spaces[2]:
            unit.inflictStat(ATK, 6)
            unit.inflictStat(SPD, 6)
            unit.inflictStatus(Status.Dodge)

            for ally in allies_within_n_spaces[2]:
                ally.inflictStat(ATK, 6)
                ally.inflictStat(SPD, 6)
                ally.inflictStatus(Status.Dodge)

        # Elena's Staff (Base) - Mist
        if "mistDebuff" in unitSkills:
            i = 1
            while i <= 4:
                if not foes_within_n_spaces[i]:
                    i += 1
                else:
                    for foe in foes_within_n_spaces[i]:
                        foe.inflictStat(ATK, -7)
                        foe.inflictStat(SPD, -7)
                    break

        # Elena's Staff (Refine Eff) - Mist
        if "mistPanic" in unitSkills:
            i = 1
            while i <= 4:
                if not foes_within_n_spaces[i]:
                    i += 1
                else:
                    for foe in foes_within_n_spaces[i]:
                        foe.inflictStatus(Status.Panic)
                    break

        # Tactical Bolt/Gale (M!/F!Robin)
        if "spectrumTactic" in unitSkills:
            move_arrs = [[], [], [], []]
            for ally in allies_within_n_spaces[2]:
                move_arrs[ally.move].append(ally)

            for arr in move_arrs:
                if len(arr) <= 2:
                    for ally in arr:
                        ally.inflictStat(ATK, 4)
                        ally.inflictStat(SPD, 4)
                        ally.inflictStat(DEF, 4)
                        ally.inflictStat(RES, 4)

        # Dignified Bow - Virion
        if "virionPanic" in unitSkills:
            for foe in waiting_team:

                if allies_within_n(foe, 1):
                    unit_hp = unit.HPcur
                    foe_hp = foe.HPcur

                    if foe_hp <= unit_hp - 1:
                        foe.inflictStatus(Status.Panic)

        # Bond Blast (SU!F!Alear)
        if "summerAlearBonds" in unitSkills:
            support_partner_present = False
            for ally in allies:
                if ally.allySupport == unit.intName:
                    support_partner_present = True

            if not support_partner_present:
                highest_atk = units_with_extreme_stat(allies_within_n_spaces[2], ATK)

                for high_atk_ally in highest_atk:
                    high_atk_ally.inflictStatus(Status.Bonded)

        # United Bouquet - Sharena
        if "bridal_shenanigans" in unitSkills and atkHPGreaterEqual25Percent:
            unit.inflictStat(ATK, 6)
            unit.inflictStat(SPD, 6)
            unit.inflictStatus(Status.MobilityUp)

    # LOOP 1.5: APPLY SUMMED SP CHARGES
    for unit in sp_charges:
        unit.chargeSpecial(sp_charges[unit])

    # LOOP 2: DAMAGE AND HEALING
    damage_taken = {}
    heals_given = {}

    for unit in starting_team:
        tile = unit.tile

        tiles_within_n_spaces = [[]]
        units_within_n_spaces = [[]]
        allies_within_n_spaces = [[]]
        foes_within_n_spaces = [[]]

        i = 1
        while i <= 5:
            tiles_within_n_spaces.append(tile.tilesWithinNSpaces(i))

            units_within_n_spaces.append([])
            allies_within_n_spaces.append([])
            foes_within_n_spaces.append([])

            for tile_within in tiles_within_n_spaces[i]:

                if tile_within.hero_on is not None:
                    units_within_n_spaces[i].append(tile_within.hero_on)

                    if unit.side == tile_within.hero_on.side and unit != tile_within.hero_on:
                        allies_within_n_spaces[i].append(tile_within.hero_on)
                    if unit.side != tile_within.hero_on.side:
                        foes_within_n_spaces[i].append(tile_within.hero_on)

            i += 1

        tiles_within_1_col = tile.tilesWithinNCols(1)
        tiles_within_1_row = tile.tilesWithinNRows(1)
        tiles_within_1_row_or_column = list(set(tiles_within_1_col) | set(tiles_within_1_row))

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur


        atkHPGreaterEqual25Percent = unitHPCur / unitStats[0] >= 0.25
        atkHPGreaterEqual50Percent = unitHPCur / unitStats[0] >= 0.50
        atkHPGreaterEqual75Percent = unitHPCur / unitStats[0] >= 0.75
        atkHPEqual100Percent = unitHPCur == unitStats[0]

        if "recoverW" in unitSkills:
            if (turn - 1) % (5 - unitSkills["recoverW"]) == 0:
                if unit not in heals_given:
                    heals_given[unit] = 10
                else:
                    heals_given[unit] += 10

        if "recoverSk" in unitSkills:
            if (turn - 1) % (5 - unitSkills["recoverSk"]) == 0:
                if unit not in heals_given:
                    heals_given[unit] = 10
                else:
                    heals_given[unit] += 10

        if "recoverSe" in unitSkills:
            if (turn - 1) % (5 - unitSkills["recoverSe"]) == 0:
                if unit not in heals_given:
                    heals_given[unit] = 10
                else:
                    heals_given[unit] += 10

    # LOOP 3: AFTER START OF TURN SKILLS
    for unit in starting_team:

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur

        if "l&d_detox" in unitSkills:
            unit.debuffs[ATK] = 0
            unit.debuffs[SPD] = 0

            if Status.Panic in unit.statusNeg:
                unit.statusNeg.remove(Status.Panic)

    # LOOP 4: AFTER START OF TURN SKILLS, ENEMY SKILLS
    for unit in waiting_team:
        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur

        if "l&d_detox" in unitSkills:

            unit.debuffs[ATK] = 0
            unit.debuffs[SPD] = 0

            if Status.Panic in unit.statusNeg:
                unit.statusNeg.remove(Status.Panic)


    # return hash maps of units who have had damage dealt or healed, or if their special cooldown was modified
    return damage_taken, heals_given

# Allies within N spaces of unit
def allies_within_n(unit, n):
    unit_list = unit.tile.unitsWithinNSpaces(n)
    returned_list = []

    for x in unit_list:
        if x != unit and unit.side == x.side:
            returned_list.append(x)

    return returned_list

def can_be_on_terrain(terrain_int, move_type_int):
    if terrain_int == 0 or terrain_int == 3: return True
    if terrain_int == 4: return False

    if terrain_int == 1:
        if move_type_int == 1: return False
        else: return True

    if terrain_int == 2:
        if move_type_int == 2: return True
        else: return False

def can_be_on_tile(tile, move_type_int):
    if tile.structure_on is not None:
        # Destructable wall
        if tile.structure_on.struct_type == 0 and tile.structure_on.health != 0:
            return 0

    if tile.terrain == 0 or tile.terrain == 3: return True
    if tile.terrain == 4: return False

    if tile.terrain == 1:
        if move_type_int == 1: return False
        else: return True

    if tile.terrain == 2:
        if move_type_int == 2: return True
        else: return False


def get_warp_moves(unit, unit_team, enemy_team):
    unitSkills = unit.getSkills()
    unitStats = unit.getStats()

    warp_moves = []

    if "wingsOfMercy" in unitSkills:
        for ally in unit_team:
            ally_hp = ally.HPcur/ally.getStats()[HP]
            if ally != unit and ally_hp <= unitSkills["wingsOfMercy"] * 0.10 + 0.20:
                adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                for adj_tile in adj_ally_spaces:
                    if can_be_on_tile(adj_tile, unit.move):
                        warp_moves.append(adj_tile)

    if "escRoute" in unitSkills:
        if unit.HPcur/unitStats[HP] <= unitSkills["escRoute"] * 0.10 + 0.20:
            for ally in unit_team:
                if ally != unit:
                    adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                    for adj_tile in adj_ally_spaces:
                        if can_be_on_tile(adj_tile, unit.move):
                            warp_moves.append(adj_tile)

    # Flier Formation
    # Warp to adj. spaces to flying ally within 2 spaces
    if "flierFormation" in unitSkills:
        if unit.HPcur/unitStats[HP] >= 1.5 - 0.5 * unitSkills["flierFormation"]:
            for ally in unit.tile.unitsWithinNSpaces(2):
                if ally.isAllyOf(unit) and ally.move == 2:
                    adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                    for adj_tile in adj_ally_spaces:
                        if can_be_on_tile(adj_tile, unit.move):
                            warp_moves.append(adj_tile)

    if "annaSchmovement" in unitSkills and unit.HPcur/unitStats[HP] >= 0.50:
        potential_allies = unit.tile.unitsWithinNSpaces(2)
        for ally in potential_allies:
            if ally != unit and ally.side == unit.side:
                adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                for adj_tile in adj_ally_spaces:
                    if can_be_on_tile(adj_tile, unit.move) and adj_tile.hero_on is None:
                        warp_moves.append(adj_tile)

    if "nowiSchmovement" in unitSkills:
        potential_allies = unit.tile.unitsWithinNSpaces(2)
        for ally in potential_allies:
            if ally != unit and ally.side == unit.side:
                close_ally_spaces = ally.tile.tilesWithinNSpaces(2)
                for adj_tile in close_ally_spaces:
                    if can_be_on_tile(adj_tile, unit.move) and adj_tile.hero_on is None:
                        warp_moves.append(adj_tile)

    if "summerPetraBoost" in unitSkills:
        potential_allies = unit.tile.unitsWithinNSpaces(2)
        for ally in potential_allies:
            if ally != unit and ally.side == unit.side:
                close_ally_spaces = ally.tile.tilesWithinNSpaces(2)
                for adj_tile in close_ally_spaces:
                    if can_be_on_tile(adj_tile, unit.move) and adj_tile.hero_on is None:
                        warp_moves.append(adj_tile)

    if "eCelicaWarp" in unitSkills:
        potential_foes = unit.tile.unitsWithinNSpaces(6)
        for foe in potential_foes:
            if foe.side != unit.side:
                adj_foe_spaces = foe.tile.tilesWithinNSpaces(2)

                nearest_tile_dist = 20
                nearest_tiles = []

                for warp_tile in adj_foe_spaces:
                    dist = abs(warp_tile.x_coord - unit.tile.x_coord) + abs(warp_tile.y_coord - unit.tile.y_coord)

                    # If closer than current closest tile
                    if dist < nearest_tile_dist:
                        nearest_tiles = [warp_tile]
                        nearest_tile_dist = dist

                    # If as close as current closest tile
                    elif dist == nearest_tile_dist:
                        nearest_tiles.append(warp_tile)


                for adj_tile in nearest_tiles:
                    if can_be_on_tile(adj_tile, unit.move) and adj_tile.hero_on is None and adj_tile not in foe.tile.tilesWithinNSpaces(1):
                        warp_moves.append(adj_tile)

    # Ally skills which enable warping
    for ally in unit_team:
        allySkills = ally.getSkills()
        allyStats = ally.getStats()

        # Hinoka's Spear
        if "refineNaginata" in allySkills and (unit.move == 0 or unit.move == 2):
            units_within_2 = allies_within_n(ally, 2)
            if unit in units_within_2:

                local_spaces = ally.tile.tilesWithinNSpaces(1)
                for tile in local_spaces:
                    if can_be_on_tile(tile, unit.move):
                        warp_moves.append(tile)

        # Guidance
        # Inf and Armor allies can move to a space adj. to flier w/ skill
        if "guidance" in allySkills and ally.HPcur / allyStats[HP] >= 1.5 - 0.5 * allySkills["guidance"]:
            if unit.move == 0 or unit.move == 3:
                units_within_2 = allies_within_n(ally, 2)
                if unit in units_within_2:

                    local_spaces = ally.tile.tilesWithinNSpaces(1)
                    for tile in local_spaces:
                        if can_be_on_tile(tile, unit.move):
                            warp_moves.append(tile)


    # Remove duplicates
    warp_moves = list(set(warp_moves))

    # Remove tiles other heroes are on
    result_warp_moves = []
    for tile in warp_moves:
        if tile.hero_on is None:
            result_warp_moves.append(tile)

    return result_warp_moves



# STRING COLLECTION
# -- EFFECT TYPES --
# buff_stat   - Applies buff of stat by value
# debuff_stat - Applies debuff of stat by value
# status      - Applies status given by value
# damage      - Deals N damage given by value
# heal        - Heals N health given by value
# end_turn    - Ends action

# -- GROUP TYPES --
# self                - applies to only self
# foe                 - applies to only foe
# allies              - applies to only allies
# foes_allies          - applies to only foe's allies
# self_and_allies     - applies to self and self's allies
# foe_and_foes_allies - applies to foe and foe's allies
# all                 - any unit

# -- AREA TYPES --
# one                   - only one unit (used for self/foe group types)
# within_N_spaces_self  - within N spaces of self (Ex. within_2_spaces_self)
# within_N_spaces_foe   - within N spaces of foe (Ex. within_4_spaces_foe)
# nearest_N_spaces_self - nearest N spaces of self, not including self
# nearest_N_spaces_foe  - nearest N spaces of foe, not including foe
# within_N_rows_self
# within_N_cols_self
# within_N_rows_or_cols_self
# within_N_rows_and_cols_self

def get_self(unit, other, units_in_area):
    return [units_in_area[0]]

def get_foe(unit, other, units_in_area):
    return [units_in_area[1]]

def foes_in_group(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side != x.side:
            returned_list.append(x)
    return returned_list

def allies_in_group(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side and x != unit:
            returned_list.append(x)

    return returned_list

def allies_plus_unit(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side:
            returned_list.append(x)

    return returned_list

def foes_minus_other(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side != x.side and x != other:
            returned_list.append(x)
    return returned_list

def end_of_combat(atk_effects, def_effects, attacker, defender):
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()

    defSkills = defender.getSkills()
    defStats = defender.getStats()

    damage_taken = {}
    heals_given = {}
    sp_charges = {}

    atkAreas = {}
    atkAreas['one'] = [attacker, defender]
    atkAreas['within_1_spaces_self'] = attacker.tile.unitsWithinNSpaces(1)
    atkAreas['within_2_spaces_self'] = attacker.tile.unitsWithinNSpaces(2)
    atkAreas['within_1_spaces_foe'] = defender.tile.unitsWithinNSpaces(1)
    atkAreas['within_2_spaces_foe'] = defender.tile.unitsWithinNSpaces(2)
    atkAreas['within_4_spaces_foe'] = defender.tile.unitsWithinNSpaces(4)

    defAreas = {}
    defAreas['one'] = [defender, attacker]
    defAreas['within_1_spaces_self'] = defender.tile.unitsWithinNSpaces(1)
    defAreas['within_2_spaces_self'] = defender.tile.unitsWithinNSpaces(2)
    defAreas['within_1_spaces_foe'] = attacker.tile.unitsWithinNSpaces(1)
    defAreas['within_2_spaces_foe'] = attacker.tile.unitsWithinNSpaces(2)
    defAreas['within_4_spaces_foe'] = attacker.tile.unitsWithinNSpaces(4)

    areaMethods = {}
    areaMethods['self'] = get_self
    areaMethods['foe'] = get_foe
    areaMethods['allies'] = allies_in_group
    areaMethods['self_and_allies'] = allies_plus_unit
    areaMethods['foes_allies'] = foes_minus_other
    areaMethods['foe_and_foes_allies'] = foes_in_group

    combined = atk_effects + def_effects

    i = 0
    while i < len(atk_effects + def_effects):
        if i < len(atk_effects):
            area = atkAreas
            unit = attacker
            other = defender
        else:
            area = defAreas
            unit = defender
            other = attacker


        effect = combined[i]

        units_in_area = area[effect[3]]
        unit_determine_method = areaMethods[effect[2]]
        targeted_units = unit_determine_method(unit, other, units_in_area)

        if effect[0] == "seal_atk":
            for x in targeted_units:
                if x.side == attacker.side and defender.HPcur > 0:
                    x.inflictStat(ATK, -effect[1])
                if x.side == defender.side and attacker.HPcur > 0:
                    x.inflictStat(ATK, -effect[1])

        if effect[0] == "seal_spd":
            for x in targeted_units:
                if x.side == attacker.side and defender.HPcur > 0:
                    x.inflictStat(SPD, -effect[1])
                if x.side == defender.side and attacker.HPcur > 0:
                    x.inflictStat(SPD, -effect[1])

        if effect[0] == "seal_def":
            for x in targeted_units:
                if x.side == attacker.side and defender.HPcur > 0:
                    x.inflictStat(DEF, -effect[1])
                if x.side == defender.side and attacker.HPcur > 0:
                    x.inflictStat(DEF, -effect[1])

        if effect[0] == "seal_res":
            for x in targeted_units:
                if x.side == attacker.side and defender.HPcur > 0:
                    x.inflictStat(RES, -effect[1])
                if x.side == defender.side and attacker.HPcur > 0:
                    x.inflictStat(RES, -effect[1])

        if effect[0] == "buff_atk":
            for x in targeted_units:
                x.inflictStat(ATK, effect[1])

        if effect[0] == "buff_spd":
            for x in targeted_units:
                x.inflictStat(SPD, effect[1])

        if effect[0] == "buff_def":
            for x in targeted_units:
                x.inflictStat(DEF, effect[1])

        if effect[0] == "buff_res":
            for x in targeted_units:
                x.inflictStat(RES, effect[1])

        if effect[0] == "debuff_atk":
            for x in targeted_units:
                x.inflictStat(ATK, -effect[1])

        if effect[0] == "debuff_spd":
            for x in targeted_units:
                x.inflictStat(SPD, -effect[1])

        if effect[0] == "debuff_def":
            for x in targeted_units:
                x.inflictStat(DEF, -effect[1])

        if effect[0] == "debuff_res":
            for x in targeted_units:
                x.inflictStat(RES, -effect[1])

        if effect[0] == "damage":
            for x in targeted_units:
                if x.HPcur != 0:
                    x.HPcur = max(x.HPcur - effect[1], 1)

                    if x not in damage_taken:
                        damage_taken[x] = effect[1]
                    else:
                        damage_taken[x] += effect[1]

        if effect[0] == "heal":
            for x in targeted_units:
                if x.HPcur != 0:
                    x.HPcur = min(x.HPcur + effect[1], x.visible_stats[HP])

                    if x not in damage_taken:
                        heals_given[x] = effect[1]
                    else:
                        heals_given[x] += effect[1]

        if effect[0] == "status":
            for x in targeted_units:
                x.inflictStatus(effect[1])

        if effect[0] == "sp_charge":
            for x in targeted_units:
                if x not in sp_charges:
                    sp_charges[x] = 0
                sp_charges[x] += effect[1]

        i += 1

    return damage_taken, heals_given, sp_charges
