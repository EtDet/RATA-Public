# This file holds several methods to carry out the following functions for game.py:
# - Start of turn skills
# - Warp tiles
# - Combat Fields
# - Post-combat effects

from hero import *
from combat import CombatField

within_1_space = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
within_2_space = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
within_3_space = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 3

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
            affect_same_side = True
            effects = {"spurAtk_f": unitSkills["spurAtk"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "driveAtk" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"spurAtk_f": unitSkills["driveAtk"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "spurSpd" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"spurSpd_f": unitSkills["spurSpd"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "driveSpd" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"driveSpd_f": unitSkills["driveSpd"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "spurDef" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"spurDef_f": unitSkills["spurDef"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "driveDef" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"driveDef_f": unitSkills["driveDef"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "spurRes" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"spurRes_f": unitSkills["spurRes"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "driveRes" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"driveRes_f": unitSkills["driveRes"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "goadCav" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"goadCav_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "wardCav" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"wardCav_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "goadFly" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"goadFly_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "wardFly" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"wardFly_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "goadArmor" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"goadArmor_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "wardArmor" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"wardArmor_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "wardDragon" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"wardDragon_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "wardDragon" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"wardDragon_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # REIN SKILLS
        if "atkRein" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"atkRein_f": unitSkills["atkRein"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "spdRein" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"spdRein_f": unitSkills["spdRein"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "defRein" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"defRein_f": unitSkills["defRein"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "resRein" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"resRein_f": unitSkills["resRein"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "spdRC" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 or abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"spdRC_f": unitSkills["spdRC"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "defRC" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 or abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"defRC_f": unitSkills["defRC"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "cruxField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 or abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"cruxField_f": unitSkills["cruxField"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "infantryRush" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 0
            affect_self = False
            affect_same_side = True

            if unitSkills["infantryRush"] == 1:
                effects = {"iRush1": 0}
            elif unitSkills["infantryRush"] == 2:
                effects = {"iRush2": 0}
            else:
                effects = {"iRush3": 0}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "infantryFlash" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 0
            affect_self = False
            affect_same_side = True

            if unitSkills["infantryRush"] == 1:
                effects = {"iFlash1": 0}
            elif unitSkills["infantryRush"] == 2:
                effects = {"iFlash2": 0}
            else:
                effects = {"iFlash3": 0}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Distant Guard
        if "distGuard" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"distDef": unitSkills["distGuard"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "closeGuard" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"closeDef": unitSkills["closeGuard"]}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)


        # UNIQUE STUFF

        # Falchion (Refine Eff) - Marth
        if "driveSpectrum" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"driveAtk_f": 2, "driveSpd_f": 2, "driveDef_f": 2, "driveRes_f": 2}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Renowned Bow (Refine Eff) - Gordin
        if "gordin_field" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"atkRein_f": 4, "defRein_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Knightly/Lordly Lance (Refine Eff) - Mathilda/Clive
        if "jointSupportPartner" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: o.isSupportOf(s)
            affect_self = False
            affect_same_side = True
            effects = {"jointSupportPartner_f": 3}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Thunderhead (Refine Eff) - P!Olwen
        if "olwen_field" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"olwen_field_f": 5}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Giga Excalibur (Refine EfF) - P!Nino
        if "doing her best" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"driveAtk_f": 4, "driveSpd_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Loyal Greatlance (Refine Eff) - Oscar
        if "oscarDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 0 or o.move == 1
            affect_self = False
            affect_same_side = True
            effects = {"oscarDrive_f": 3}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Father's Tactics (Refine Eff) - F!Morgan
        if "morganJointDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"driveAtk_f": 3, "driveSpd_f": 3}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Geirskögul (Base) - B!Lucina
        if "lucinaDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.wpnType in MELEE_WEAPONS
            affect_self = False
            affect_same_side = True
            effects = {"lucinaDrive_f": 3}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "refinedLucinaDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.wpnType in PHYSICAL_WEAPONS
            affect_self = False
            affect_same_side = True
            effects = {"refinedLucinaDrive_f": 3}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Tharja's Hex (Refined Eff) - Tharja
        if "tharja_field" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"atkRein_f": 4, "spdRein_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # LORD HAVE MERCY
        if "tharjaComplexField" in unitSkills:
            range = within_3_space
            condition1 = lambda s: lambda o: len(allies_within_n(s, 3)) == 1
            condition2 = lambda s: lambda o: len(allies_within_n(s, 3)) == 2
            condition3 = lambda s: lambda o: len(allies_within_n(s, 3)) >= 3
            affect_self = False
            affect_same_side = False
            effects1 = {"complexRein1_f": 2}
            effects2 = {"complexRein2_f": 4}
            effects3 = {"complexRein3_f": 6}

            field1 = CombatField(owner, range, condition1, affect_self, affect_same_side, effects1)
            field2 = CombatField(owner, range, condition2, affect_self, affect_same_side, effects2)
            field3 = CombatField(owner, range, condition3, affect_self, affect_same_side, effects3)
            combat_fields.append(field1)
            combat_fields.append(field2)
            combat_fields.append(field3)

        if "rhajatField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"spdRein_f": 5, "resRein_f": 5}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Grimoire (Refine Eff) - H!Nowi
        if "nowiField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 3
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"nowiField_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Yato (Refine Eff) - Corrin
        if "supportThem" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.allySupport == s.intName
            affect_self = False
            affect_same_side = True
            effects = {"corrinField_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "gunterJointDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"gunterJointDrive_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "hinokaField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 3
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"hinokaField_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "camillaField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: o.move == 1 or o.move == 2
            affect_self = False
            affect_same_side = True
            effects = {"driveAtk_f": 3, "driveSpd_f": 3}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "eliseField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False
            effects = {"eliseField_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        # Flier Hinoka
        if "hinokaJointDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"driveAtk_f": 4, "driveSpd_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)

        if "veronicaField" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_self = False

            affect_same_side1 = True
            effects1 = {"driveAtk_f": 3, "driveSpd_f": 3}

            field = CombatField(owner, range, condition, affect_self, affect_same_side1, effects1)
            combat_fields.append(field)

            affect_same_side2 = False
            effects2 = {"defRein_f": 3, "resRein_f": 3}

            field = CombatField(owner, range, condition, affect_self, affect_same_side2, effects2)
            combat_fields.append(field)

        if "stupid dumb idiot field I cant code easily" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = False

            effects = {"ylgrField_f": 1}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)


        if "reginnAccel" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 or abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_same_side = True
            effects = {"reginnField_f": 4}

            field = CombatField(owner, range, condition, affect_self, affect_same_side, effects)
            combat_fields.append(field)


    return combat_fields


def start_of_turn(starting_team, waiting_team, turn):

    # Return units within a given team with the greatest of a given stat
    def units_with_extreme_stat(cur_team, stat, find_max=True):
        if not cur_team:
            return []

        extreme_stat = cur_team[0].get_visible_stat(stat)
        extreme_stat_units = [cur_team[0]]

        if len(cur_team) == 1:
            return extreme_stat_units

        for unit in cur_team[1:]:
            unit_stat = unit.get_visible_stat(stat)

            if (find_max and unit_stat == extreme_stat) or (not find_max and unit_stat == extreme_stat):
                extreme_stat_units.append(unit)

            if (find_max and unit_stat > extreme_stat) or (not find_max and unit_stat < extreme_stat):
                extreme_stat = unit_stat
                extreme_stat_units = [unit]

        return extreme_stat_units

    sp_charges = {}
    for unit in starting_team + waiting_team:
        sp_charges[unit] = 0

    # Store all buffs/debuffs for this start of turn
    units_stored_buffs = {}
    units_stored_debuffs = {}
    units_stored_statuses = {}

    for unit in starting_team + waiting_team:
        units_stored_buffs[unit] = [0] * 5
        units_stored_debuffs[unit] = [0] * 5
        units_stored_statuses[unit] = []

    def add_buff(hero, stat, val):
        units_stored_buffs[hero][stat] = max(units_stored_buffs[hero][stat], val)

    def add_debuff(hero, stat, val):
        units_stored_debuffs[hero][stat] = min(units_stored_debuffs[hero][stat], val)

    def add_status(hero, status):
        if status not in units_stored_statuses[hero]:
            units_stored_statuses[hero].append(status)

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


        unitHPGreaterEqual25Percent = unitHPCur / unitStats[0] >= 0.25
        unitHPGreaterEqual50Percent = unitHPCur / unitStats[0] >= 0.50
        unitHPGreaterEqual75Percent = unitHPCur / unitStats[0] >= 0.75
        unitHPEqual100Percent = unitHPCur == unitStats[0]

        # All allies
        allies = []
        for hero in starting_team:
            if hero is not unit:
                allies.append(hero)

        # HONE/FORTIFY
        if "honeAtk" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["honeAtk"])

        if "honeAtkW" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["honeAtkW"])

        if "honeSpd" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, unitSkills["honeSpd"])

        if "fortifyDef" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, unitSkills["fortifyDef"])

        if "fortifyRes" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, RES, unitSkills["fortifyRes"])

        if "honecav" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 1:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)

        if "forticav" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 1:
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)

        if "honefly" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 2:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)

        if "fortifly" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 2:
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)

        if "honearmor" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 3:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)

        if "fortiarmor" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 3:
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)

        if "honedragon" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.wpnType in DRAGON_WEAPONS:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)

        if "fortidragon" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.wpnType in DRAGON_WEAPONS:
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)

        # THREATEN

        if "threatenAtk" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, ATK, -unitSkills["threatenAtk"])

        if "threatenAtkW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, ATK, -unitSkills["threatenAtkW"])

        if "threatenSpd" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, SPD, -unitSkills["threatenSpd"])

        if "threatenSpdW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, SPD, -unitSkills["threatenSpdW"])

        if "threatenDef" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, DEF, -unitSkills["threatenDef"])

        if "threatenDefW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, DEF, -unitSkills["threatenDefW"])

        if "threatenRes" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, RES, -unitSkills["threatenRes"])

        if "threatenResW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, RES, -unitSkills["threatenResW"])

        # MENACE SKILLS
        if "atkDefMenace" in unitSkills:
            if nearest_foes_within_n(unit, 4):
                add_buff(unit, ATK, 6)
                add_buff(unit, DEF, 6)

                for foe in nearest_foes_within_n(unit, 4):
                    add_debuff(foe, ATK, -6)
                    add_debuff(foe, DEF, -6)

        # DEFIANT SKILLS
        def apply_defiant(defiant_type):

            if (defiant_type in unitSkills or f"{defiant_type}Se" in unitSkills) and unit.HPcur / unitStats[0] <= 0.50:

                stat = defiant_types.index(defiant_type) + 1

                if defiant_type in unitSkills:
                    add_buff(unit, stat, 2 * unitSkills[defiant_type] + 1)

                if f"{defiant_type}Se" in unitSkills:
                    add_buff(unit, stat, 2 * unitSkills[f"{defiant_type}Se"] + 1)

        defiant_types = ["defiantAtk", "defiantSpd", "defiantDef", "defiantRes"]
        for defiant in defiant_types:
            apply_defiant(defiant)


        # PLOY SKILLS
        def apply_ploy(ploy_type):
            if ploy_type in unitSkills or f"{ploy_type}W" in unitSkills:
                valid_foes = [p_tile.hero_on for p_tile in tiles_within_1_row_or_column if p_tile.hero_on is not None and p_tile.hero_on.isEnemyOf(unit)]

                for foe in valid_foes:
                    unit_res = unit.get_visible_stat(RES)
                    foe_res = foe.get_visible_stat(RES)

                    if "phantomRes" in unitSkills: unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills(): foe_res += foe.getSkills()["phantomRes"]

                    if unit_res > foe_res:
                        stat = ploy_types.index(ploy_type) + 1

                        if ploy_type in unitSkills:
                            add_debuff(foe, stat, -unitSkills[ploy_type])
                        if f"{ploy_type}W" in unitSkills:
                            add_debuff(foe, stat, -unitSkills[f"{ploy_type}W"])

        ploy_types = ["atkPloy", "spdPloy", "defPloy", "resPloy"]
        for ploy in ploy_types:
            apply_ploy(ploy)

        # Larger Area Ploy
        if "atkLargePloyW" in unitSkills:
            valid_foes = [p_tile.hero_on for p_tile in tiles_within_3_row_or_column if p_tile.hero_on is not None and p_tile.hero_on.isEnemyOf(unit)]

            for foe in valid_foes:
                unit_res = unit.get_visible_stat(RES)
                foe_res = foe.get_visible_stat(RES)

                if "phantomRes" in unitSkills: unit_res += unit.getSkills()["phantomRes"]
                if "phantomRes" in foe.getSkills(): foe_res += foe.getSkills()["phantomRes"]

                if unit_res > foe_res:
                    add_debuff(foe, ATK, -unitSkills["atkLargePloyW"])

        if "resLargePloyW" in unitSkills:
            valid_foes = [p_tile.hero_on for p_tile in tiles_within_3_row_or_column if p_tile.hero_on is not None and p_tile.hero_on.isEnemyOf(unit)]

            for foe in valid_foes:
                unit_res = unit.get_visible_stat(RES)
                foe_res = foe.get_visible_stat(RES)

                if "phantomRes" in unitSkills: unit_res += unit.getSkills()["phantomRes"]
                if "phantomRes" in foe.getSkills(): foe_res += foe.getSkills()["phantomRes"]

                if unit_res > foe_res:
                    add_debuff(foe, RES, -unitSkills["resLargePloyW"])

        if "panicPloy" in unitSkills:
            diff = 7 - unitSkills["panicPloy"] * 2
            for tile in tiles_within_1_row_or_column:
                if unit.isEnemyOf(tile.hero_on):
                    if tile.hero_on.HPcur <= unit.HPcur - diff:
                        add_status(tile.hero_on, Status.Panic)

        if "panicPloyW" in unitSkills:
            diff = 7 - unitSkills["panicPloyW"] * 2
            for tile in tiles_within_1_row_or_column:
                if unit.isEnemyOf(tile.hero_on):
                    if tile.hero_on.HPcur <= unit.HPcur - diff:
                        add_status(tile.hero_on, Status.Panic)

        # TACTIC SKILLS
        move_arrs = [[], [], [], []]
        for ally in starting_team:
            move_arrs[ally.move].append(ally)

        tactic_allies = []

        for arr in move_arrs:
            if len(arr) <= 2:
                for ally in arr:
                    tactic_allies.append(ally)

        if "atkTactic" in unitSkills:
            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, ATK, 2 * unitSkills["atkTactic"])

        if "spdTactic" in unitSkills:
            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, SPD, 2 * unitSkills["spdTactic"])

        if "defTactic" in unitSkills:
            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, DEF, 2 * unitSkills["defTactic"])

        if "resTactic" in unitSkills:
            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, RES, 2 * unitSkills["resTactic"])

        if "spdTacticW" in unitSkills:
            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, SPD, 6)

        if "resTacticW" in unitSkills:
            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, RES, 6)

        if "ostiaPulseII" in unitSkills:
            for ally in tactic_allies:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)

        # CHILL SKILLS
        if "chillAtk" in unitSkills:
            highest_atk = units_with_extreme_stat(waiting_team, ATK, find_max=True)

            debuff = -1 - 2 * unitSkills["chillAtk"]

            for foe in highest_atk:
                add_debuff(foe, ATK, debuff)

        if "chillAtkW" in unitSkills:
            highest_atk = units_with_extreme_stat(waiting_team, ATK, find_max=True)

            for foe in highest_atk:
                add_debuff(foe, ATK, -7)

        if "chillSpd" in unitSkills:
            highest_spd = units_with_extreme_stat(waiting_team, SPD, find_max=True)

            debuff = -1 - 2 * unitSkills["chillSpd"]

            for foe in highest_spd:
                add_debuff(foe, SPD, debuff)

        if "chillSpdW" in unitSkills:
            highest_spd = units_with_extreme_stat(waiting_team, SPD, find_max=True)
            for foe in highest_spd:
                add_debuff(foe, SPD, -7)

        if "chillDef" in unitSkills:
            highest_def = units_with_extreme_stat(waiting_team, DEF, find_max=True)

            debuff = -1 - 2 * unitSkills["chillDef"]

            for foe in highest_def:
                add_debuff(foe, DEF, debuff)

        if "chillDefW" in unitSkills:
            highest_def = units_with_extreme_stat(waiting_team, DEF, find_max=True)
            for foe in highest_def:
                add_debuff(foe, DEF, -7)

        if "chillRes" in unitSkills:
            highest_res = units_with_extreme_stat(waiting_team, RES, find_max=True)

            debuff = -1 - 2 * unitSkills["chillRes"]

            for foe in highest_res:
                add_debuff(foe, RES, debuff)

        if "chillResW" in unitSkills:
            highest_res = units_with_extreme_stat(waiting_team, RES, find_max=True)
            for foe in highest_res:
                add_debuff(foe, RES, -7)

        if "gunterChill" in unitSkills:
            lowest_spd = units_with_extreme_stat(waiting_team, SPD, find_max=False)
            for foe in lowest_spd:
                add_debuff(foe, ATK, -5)
                add_debuff(foe, DEF, -5)

        # Muninn's Egg (Base) - SP!Sharena
        if "sharenaChill" in unitSkills:
            lowest_spd = units_with_extreme_stat(waiting_team, SPD, find_max=False)
            for foe in lowest_spd:
                add_debuff(foe, ATK, -5)
                add_debuff(foe, RES, -5)

        if "sharenaDualChill" in unitSkills:
            highest_atk = units_with_extreme_stat(waiting_team, ATK, find_max=True)
            for foe in highest_atk:
                add_debuff(foe, ATK, -7)

            highest_res = units_with_extreme_stat(waiting_team, RES, find_max=True)
            for foe in highest_res:
                add_debuff(foe, RES, -7)

        if "catriaChill" in unitSkills:
            lowest_res = units_with_extreme_stat(waiting_team, RES, find_max=False)
            for foe in lowest_res:
                add_debuff(foe, ATK, -5)
                add_debuff(foe, DEF, -5)

        if "catriaDualChill" in unitSkills:
            highest_atk = units_with_extreme_stat(waiting_team, ATK, find_max=True)
            for foe in highest_atk:
                add_debuff(foe, ATK, -7)

            highest_spd = units_with_extreme_stat(waiting_team, SPD, find_max=True)
            for foe in highest_spd:
                add_debuff(foe, SPD, -7)

        if "gunnSeal" in unitSkills:
            lowest_def = units_with_extreme_stat(waiting_team, DEF, find_max=False)
            for foe in lowest_def:
                add_debuff(foe, ATK, -6)
                add_debuff(foe, SPD, -6)

        if "gunnSealII" in unitSkills:
            lowest_def = units_with_extreme_stat(waiting_team, DEF, find_max=False)
            for foe in lowest_def:
                add_debuff(foe, ATK, -7)
                add_debuff(foe, SPD, -7)
                add_debuff(foe, DEF, -7)
                add_debuff(foe, RES, -7)

                foes_allies = allies_within_n(foe, 2)
                for ally in foes_allies:
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, RES, -7)

        if "hridSeal" in unitSkills and unitHPGreaterEqual50Percent:
            for foe in units_with_extreme_stat(waiting_team, RES, find_max=False):
                add_debuff(foe, ATK, -6)
                add_debuff(foe, SPD, -6)

        if "hridSealII" in unitSkills:
            for foe in units_with_extreme_stat(waiting_team, RES, find_max=False):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Guard)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Guard)

        # SP CHARGE

        # Wrath
        if "wrathW" in unitSkills and unitHPCur / unitStats[0] <= unitSkills["wrathW"] * 0.25 and unit.getSpecialType() in ["Offense", "AOE"]:
            sp_charges[unit] += 1

        if "wrathSk" in unitSkills and unitHPCur / unitStats[0] <= unitSkills["wrathSk"] * 0.25 and unit.getSpecialType() in ["Offense", "AOE"]:
            sp_charges[unit] += 1

        # Time's Pulse
        if "timesPulseW" in unitSkills and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        if "timesPulseSp" in unitSkills and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # Turn 1 Pulse
        if "turn1Pulse" in unitSkills and turn == 1:
            sp_charges[unit] += unitSkills["turn1Pulse"]

        if "turn1PulseD" in unitSkills and turn == 1 and unit.getSpecialType() == "Defense": # Defensive Specials Only
            sp_charges[unit] += unitSkills["turn1PulseD"]

        if "infantryPulse" in unitSkills and turn == 1:
            for ally in waiting_team:
                if unit.HPcur - (7 * unitSkills["infantryPulse"]) > ally.HPcur and ally.move == 0 and ally != unit:
                    sp_charges[ally] += 1

        if "canasPulse" in unitSkills and turn < 4:
            sp_charges[unit] += 1

        if "ostiaPulse" in unitSkills and turn == 1:
            for ally in tactic_allies:
                if ally != unit:
                    sp_charges[ally] += 1

        if "ostiaPulseII" in unitSkills:
            for ally in tactic_allies:
                if ally.specialCount == ally.specialMax:
                    sp_charges[ally] += 1

        if "opheliaPulse" in unitSkills:
            total = 0
            for ally in waiting_team:
                if ally.wpnType in TOME_WEAPONS:
                    total += 1

            sp_charges[unit] += total

        # WAVE SKILLS
        if "oddAtkWave" in unitSkills and turn % 2 == 1:
            add_buff(unit, ATK, unitSkills["oddAtkWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["oddAtkWave"])

        if "evenAtkWave" in unitSkills and turn % 2 == 0:
            add_buff(unit, ATK, unitSkills["evenAtkWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["evenAtkWave"])

        if "oddSpdWave" in unitSkills and turn % 2 == 1:
            add_buff(unit, SPD, unitSkills["oddSpdWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, unitSkills["oddSpdWave"])

        if "evenSpdWave" in unitSkills and turn % 2 == 0:
            add_buff(unit, SPD, unitSkills["evenSpdWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, unitSkills["evenSpdWave"])

        if "oddDefWave" in unitSkills and turn % 2 == 1:
            add_buff(unit, DEF, unitSkills["oddDefWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, unitSkills["oddDefWave"])

        if "evenDefWave" in unitSkills and turn % 2 == 0:
            add_buff(unit, DEF, unitSkills["evenDefWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, unitSkills["evenDefWave"])

        if "oddResWave" in unitSkills and turn % 2 == 0:
            add_buff(unit, RES, unitSkills["oddResWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, RES, unitSkills["oddResWave"])

        if "evenResWave" in unitSkills and turn % 2 == 0:
            add_buff(unit, RES, unitSkills["evenResWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, RES, unitSkills["evenResWave"])

        if "evenAtkWaveW" in unitSkills and turn % 2 == 0:
            add_buff(unit, ATK, unitSkills["evenAtkWaveW"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["evenAtkWaveW"])

        if "premiumResWave" in unitSkills:
            add_buff(unit, RES, 6)
            for ally in allies_within_n_spaces[2]:
                add_buff(ally, RES, 6)

        # SABOTAGE SKILLS
        if "sabotageAtkW" in unitSkills:
            for foe in waiting_team:

                if allies_within_n(foe, 1):
                    unit_res = unit.get_visible_stat(RES)
                    foe_res = foe.get_visible_stat(RES)

                    if "phantomRes" in unit.getSkills():
                        unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills():
                        foe_res += foe.getSkills()["phantomRes"]

                    if foe_res <= unit_res - 3:
                        add_debuff(foe, ATK, -7)

        if "sabotageSpdW" in unitSkills:
            for foe in waiting_team:

                if allies_within_n(foe, 1):
                    unit_res = unit.get_visible_stat(RES)
                    foe_res = foe.get_visible_stat(RES)

                    if "phantomRes" in unit.getSkills():
                        unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills():
                        foe_res += foe.getSkills()["phantomRes"]

                    if foe_res <= unit_res - 3:
                        add_debuff(foe, SPD, -unitSkills["sabotageSpdW"])

        if "sabotageResW" in unitSkills:
            for foe in waiting_team:

                if allies_within_n(foe, 1):
                    unit_res = unit.get_visible_stat(RES)
                    foe_res = foe.get_visible_stat(RES)

                    if "phantomRes" in unit.getSkills():
                        unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills():
                        foe_res += foe.getSkills()["phantomRes"]

                    if foe_res <= unit_res - 3:
                        add_debuff(foe, RES, -unitSkills["sabotageResW"])

        if "juliusSabotage" in unitSkills:
            unit_res = unit.get_visible_stat(RES)
            if "phantomRes" in unit.getSkills():
                unit_res += unit.getSkills()["phantomRes"]

            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    foe_res = foe.get_visible_stat(RES)
                    if "phantomRes" in foe.getSkills():
                        foe_res += foe.getSkills()["phantomRes"]

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -5)
                        add_debuff(foe, RES, -5)

        # STATUSES
        if "armorMarch" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["armorMarch"]:
            ally_cond = False
            for ally in allies_within_n_spaces[1]:
                if ally.move == 3:

                    add_status(ally, Status.MobilityUp)
                    ally_cond = True

            if ally_cond:
                add_status(unit, Status.MobilityUp)


        # THE UNIQUE SKILL STUFF
        if "Shining Emblem" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)

        # Ardent Service/Fresh Bouquet
        if "bridalSpdBonus" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, SPD, 4)
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, 4)

        # Aura - Linde
        if "lindeAtkBuff" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                if ally.wpnType in TOME_WEAPONS or ally.wpnType == "Staff":
                    add_buff(ally, ATK, 6)

        # Dark Aura - Linde/Delthea
        if "darkAuraBuff" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                if ally.wpnType in MELEE_WEAPONS:
                    add_buff(ally, ATK, 6)


        if "Friends!!!" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, DEF, 5)
            add_buff(unit, RES, 5)

            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, 5)
                add_buff(ally, RES, 5)

        if "I love you, and all you guys!" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)

        # Eternal Breath - Fae
        if "honeFae" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 5)
            add_buff(unit, SPD, 5)
            add_buff(unit, DEF, 5)
            add_buff(unit, RES, 5)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 5)
                add_buff(ally, SPD, 5)
                add_buff(ally, DEF, 5)
                add_buff(ally, RES, 5)

        # Echesacks (Refine) - Zephiel
        if "i <3 dragons" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                if foe.wpnType not in DRAGON_WEAPONS:
                    add_debuff(foe, DEF, -6)

        # Sisterly Axe - X!Eirika
        if "sisterlyBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Dodge)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Dodge)

        # Elena's Staff (Base) - Mist
        if "mistDebuff" in unitSkills:
            i = 1
            while i <= 4:
                if not foes_within_n_spaces[i]:
                    i += 1
                else:
                    for foe in foes_within_n_spaces[i]:
                        add_debuff(foe, ATK, -7)
                        add_debuff(foe, SPD, -7)
                    break

        # Elena's Staff (Refine Eff) - Mist
        if "mistPanic" in unitSkills:
            i = 1
            while i <= 4:
                if not foes_within_n_spaces[i]:
                    i += 1
                else:
                    for foe in foes_within_n_spaces[i]:
                        add_status(foe, Status.Panic)
                    break

        # Tactical Bolt/Gale (M!/F!Robin)
        if "spectrumTactic" in unitSkills:
            move_arrs = [[], [], [], []]
            for ally in allies_within_n_spaces[2]:
                move_arrs[ally.move].append(ally)

            for arr in move_arrs:
                if len(arr) <= 2:
                    for ally in arr:
                        add_buff(ally, ATK, 4)
                        add_buff(ally, SPD, 4)
                        add_buff(ally, DEF, 4)
                        add_buff(ally, RES, 4)

        if "morganStartDebuff" in unitSkills:
            valid_foes = []

            i = 1
            while i <= 4:
                if foes_within_n_spaces[i]:
                    valid_foes = foes_within_n_spaces[i]
                    break
                i += 1

            for foe in valid_foes:
                add_debuff(foe, ATK, -5)
                add_debuff(foe, SPD, -5)
                add_debuff(foe, RES, -5)

            add_buff(unit, ATK, 5)
            add_buff(unit, SPD, 5)
            add_buff(unit, RES, 5)

        # Dignified Bow - Virion
        if "virionPanic" in unitSkills:
            for foe in waiting_team:

                if allies_within_n(foe, 1):
                    unit_hp = unit.HPcur
                    foe_hp = foe.HPcur

                    if foe_hp <= unit_hp - 1:
                        add_status(foe, Status.Panic)

        if "maribelleBuff" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_status(unit, Status.CancelAffinity)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_status(ally, Status.CancelAffinity)

        if "geromeBuff" in unitSkills and not allies_within_n_spaces[1]:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)

        if "walhartBolster" in unitSkills and foes_within_n_spaces[4]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)

        if "as I type this I have a 102 fever lol" in unitSkills:
            for foe in foes_within_n_spaces[4]:
                add_debuff(foe, ATK, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Flash)

        if "aversaSabotage" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 1) and foe.HPcur <= unit.HPcur - 3:
                    add_debuff(foe, ATK, -unitSkills["aversaSabotage"])
                    add_debuff(foe, SPD, -unitSkills["aversaSabotage"])
                    add_debuff(foe, DEF, -unitSkills["aversaSabotage"])
                    add_debuff(foe, RES, -unitSkills["aversaSabotage"])
                    add_status(foe, Status.Panic)

        # Skadi - FA!Takumi
        if "skadiDamage" in unitSkills and turn == 3:
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(3) if tile.hero_on is not None and tile.hero_on.isEnemyOf(unit)]:
                add_status(foe, Status.Panic)

        if "skadiMoreDamage" in unitSkills and (turn == 2 or turn == 3):
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(3) if tile.hero_on is not None and tile.hero_on.isEnemyOf(unit)]:
                add_status(foe, Status.Panic)

        if "gharnefDmg" in unitSkills and turn == 3:
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(5) if unit.isEnemyOf(tile.hero_on)]:
                if foe.wpnType not in TOME_WEAPONS:
                    add_status(foe, Status.Flash)

        if "camillaDebuff" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, ATK, -5)
                add_debuff(foe, SPD, -5)
                add_debuff(foe, RES, -5)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -5)
                    add_debuff(ally, SPD, -5)
                    add_debuff(ally, RES, -5)

        # Bond Blast (SU!F!Alear)
        if "summerAlearBonds" in unitSkills:
            support_partner_present = False
            for ally in allies:
                if ally.allySupport == unit.intName:
                    support_partner_present = True

            if not support_partner_present:
                highest_atk = units_with_extreme_stat(allies_within_n_spaces[2], ATK)

                for high_atk_ally in highest_atk:
                    add_status(high_atk_ally, Status.Bonded)

        # United Bouquet - Sharena
        if "bridal_shenanigans" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.MobilityUp)

        if "oddSpectrumWave" in unitSkills and turn % 2 == 1:
            add_buff(unit, ATK, 4)
            add_buff(unit, SPD, 4)
            add_buff(unit, DEF, 4)
            add_buff(unit, RES, 4)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 4)
                add_buff(ally, SPD, 4)
                add_buff(ally, DEF, 4)
                add_buff(ally, RES, 4)

        if "helbindiWave" in unitSkills and (turn % 2 == 1 or foes_within_n_spaces[4]):
            add_buff(unit, ATK, 5)
            add_buff(unit, SPD, 5)
            add_buff(unit, DEF, 5)
            add_buff(unit, RES, 5)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 5)
                add_buff(ally, SPD, 5)
                add_buff(ally, DEF, 5)
                add_buff(ally, RES, 5)

        if "laevPartner" in unitSkills:
            if allies_within_n_spaces[2]:
                add_buff(unit, ATK, 6)
                add_buff(unit, DEF, 6)

            for ally in allies_within_n_spaces[2]:
                if ally.isSupportOf(unit):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, DEF, 6)

        if "surtrMeance" in unitSkills and foes_within_n_spaces[2]:
            add_buff(unit, ATK, 4)
            add_buff(unit, SPD, 4)
            add_buff(unit, DEF, 4)
            add_buff(unit, RES, 4)

            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, ATK, -4)
                add_debuff(foe, SPD, -4)
                add_debuff(foe, DEF, -4)
                add_debuff(foe, RES, -4)

        if "lokiRanged" in unitSkills:
            for foe in [tile.hero_on for tile in tiles_within_1_row_or_column if unit.isEnemyOf(tile.hero_on)]:
                if foe.HPcur <= unit.HPcur - 3 and foe.wpnType in RANGED_WEAPONS:
                    add_status(foe, Status.Gravity)

        if "lokiMeleeRanged" in unitSkills:
            for foe in [tile.hero_on for tile in tiles_within_1_row_or_column if unit.isEnemyOf(tile.hero_on)]:
                if foe.HPcur <= unit.HPcur:
                    if foe.wpnType in MELEE_WEAPONS:
                        add_debuff(foe, ATK, -7)
                        add_status(foe, Status.Stall)
                    else:
                        add_debuff(foe, RES, -7)
                        add_status(foe, Status.Gravity)

        if "lokiGuard" in unitSkills:
            lowest_spd = units_with_extreme_stat(waiting_team, SPD, find_max=False)

            for foe in lowest_spd:
                add_status(foe, Status.Guard)
                for ally in allies_within_n(foe, 1):
                    add_status(ally, Status.Guard)

    # LOOP 1.25: APPLY BUFFS/DEBUFFS
    for unit in units_stored_buffs.keys():
        i = 1
        while i < len(units_stored_buffs[unit]):
            unit.inflictStat(i, units_stored_buffs[unit][i])
            i += 1

    for unit in units_stored_debuffs.keys():
        i = 1
        while i < len(units_stored_debuffs[unit]):
            unit.inflictStat(i, units_stored_debuffs[unit][i])
            i += 1

    for unit in units_stored_statuses.keys():
        for status in units_stored_statuses[unit]:
            unit.inflictStatus(status)

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


        unitHPGreaterEqual25Percent = unitHPCur / unitStats[0] >= 0.25
        unitHPGreaterEqual50Percent = unitHPCur / unitStats[0] >= 0.50
        unitHPGreaterEqual75Percent = unitHPCur / unitStats[0] >= 0.75
        unitHPEqual100Percent = unitHPCur == unitStats[0]

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

        # Skadi - FA!Takumi
        if "skadiDamage" in unitSkills and turn == 3:
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(3) if tile.hero_on is not None and tile.hero_on.isEnemyOf(unit)]:
                if unit not in damage_taken:
                    damage_taken[foe] = 10
                else:
                    damage_taken[foe] += 10

        if "skadiMoreDamage" in unitSkills and (turn == 2 or turn == 3):
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(3) if tile.hero_on is not None and tile.hero_on.isEnemyOf(unit)]:
                if unit not in damage_taken:
                    damage_taken[foe] = 7
                else:
                    damage_taken[foe] += 7

        if "gharnefDmg" in unitSkills and turn == 3:
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(5) if unit.isEnemyOf(tile.hero_on) and tile.hero_on.wpnType not in TOME_WEAPONS]:
                if unit not in damage_taken:
                    damage_taken[foe] = unitSkills["gharnefDmg"]
                else:
                    damage_taken[foe] += unitSkills["gharnefDmg"]

        if "sharenaHealing" in unitSkills:
            if unit not in heals_given:
                heals_given[unit] = 7
            else:
                heals_given[unit] += 7

            for ally in allies_within_n_spaces[2]:
                if ally not in heals_given:
                    heals_given[ally] = 7
                else:
                    heals_given[ally] += 7

        if "surtrBurn" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                if foe not in damage_taken:
                    damage_taken[foe] = 20
                else:
                    damage_taken[foe] += 20

        if "s_drink" in unitSkills and turn == 1:
            if unit not in heals_given:
                heals_given[unit] = 99
            else:
                heals_given[unit] += 99

        if "garonAbsorb" in unitSkills and turn == 3:
            for foe in foes_within_n_spaces[3]:
                if foe not in damage_taken:
                    damage_taken[foe] = 10
                else:
                    damage_taken[foe] += 10

            if unit not in heals_given:
                heals_given[unit] = len(foes_within_n_spaces[3]) * 5
            else:
                heals_given[unit] += len(foes_within_n_spaces[3]) * 5

        if "garonDevour" in unitSkills and (turn == 3 or turn == 4):
            for foe in foes_within_n_spaces[4]:
                if foe not in damage_taken:
                    damage_taken[foe] = 14
                else:
                    damage_taken[foe] += 14

            if unit not in heals_given:
                heals_given[unit] = len(foes_within_n_spaces[4]) * 14
            else:
                heals_given[unit] += len(foes_within_n_spaces[4]) * 14

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

def foes_within_n(unit, n):
    unit_list = unit.tile.unitsWithinNSpaces(n)
    returned_list = []

    for x in unit_list:
        if x.isEnemyOf(unit):
            returned_list.append(x)

    return returned_list

def nearest_foes_within_n(unit, n):
    i = 1
    while i <= n:
        if foes_within_n(unit, i):
            return foes_within_n(unit, i)
        else:
            i += 1

    return []

def foes_within_n_cardinal(unit, n):
    unit_list = [tile.hero_on for tile in unit.tile.tilesWithinNRowsOrCols(n) if tile.hero_on is not None]
    returned_list = []

    for x in unit_list:
        if x.isEnemyOf(unit):
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

    if "sumiaMovement" in unitSkills:
        for ally in unit_team:
            ally_hp = ally.HPcur/ally.getStats()[HP]
            if ally != unit and ally_hp <= 0.80:
                adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                for adj_tile in adj_ally_spaces:
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

    # Aerobatics
    # Ward to adj. spaces to non-flying ally within 2 spaces
    if "aerobatics" in unitSkills:
        if unit.HPcur/unitStats[HP] >= 1.5 - 0.5 * unitSkills["aerobatics"]:
            for ally in unit.tile.unitsWithinNSpaces(2):
                if ally.isAllyOf(unit) and ally.move != 2:
                    adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                    for adj_tile in adj_ally_spaces:
                        warp_moves.append(adj_tile)

    # Warp Powder
    if "warpPowder" in unitSkills and unit.HPcur/unitStats[HP] >= 0.80:
        for ally in allies_within_n(unit, 2):
            adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
            for adj_tile in adj_ally_spaces:
                if can_be_on_tile(adj_tile, unit.move) and adj_tile.hero_on is None:
                    warp_moves.append(adj_tile)

    # Warping adjacent to allies within 2 spaces
    if "annaSchmovement" in unitSkills and unit.HPcur/unitStats[HP] >= 0.50:
        potential_allies = unit.tile.unitsWithinNSpaces(2)
        for ally in potential_allies:
            if ally != unit and ally.side == unit.side:
                adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                for adj_tile in adj_ally_spaces:
                    if can_be_on_tile(adj_tile, unit.move) and adj_tile.hero_on is None:
                        warp_moves.append(adj_tile)

    # Warping to ally within 2 spaces any space within 2 spaces of that ally
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

    # Tome of Favors
    if "I cannot blame you for wanting to touch something so alluring as myself." in unitSkills:
        for ally in unit_team:
            if ally.wpnType in BEAST_WEAPONS and ally.refresh_type != 0:
                adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                for adj_tile in adj_ally_spaces:
                    if can_be_on_tile(adj_tile, unit.move) and adj_tile.hero_on is None:
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

        # Fruit of Iðunn (Base) - SU!Tana
        if "SUTanaWarp" in allySkills and ally.HPcur / allyStats[HP] >= 1.5 - 0.5 * allySkills["SUTanaWarp"]:
            if unit in allies_within_n(ally, 2):
                for tile in ally.tile.tilesWithinNSpaces(1):
                    warp_moves.append(tile)

        # Flier Guidance
        # Flier allies can move to a space adj. to flier w/ skill
        if "flier_guidance" in allySkills and ally.HPcur / allyStats[HP] >= 1.5 - 0.5 * allySkills["flier_guidance"]:
            if unit.move == 2:
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
        if tile.hero_on is None and can_be_on_tile(tile, unit.move):
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
# global                - the whole damn map

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

def end_of_combat(atk_effects, def_effects, attacker, defender, savior_unit):
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
    atkAreas['global'] = attacker.tile.unitsWithinNSpaces(16)

    defAreas = {}
    defAreas['one'] = [defender, attacker]
    defAreas['within_1_spaces_self'] = defender.tile.unitsWithinNSpaces(1)
    defAreas['within_2_spaces_self'] = defender.tile.unitsWithinNSpaces(2)
    defAreas['within_1_spaces_foe'] = attacker.tile.unitsWithinNSpaces(1)
    defAreas['within_2_spaces_foe'] = attacker.tile.unitsWithinNSpaces(2)
    defAreas['within_4_spaces_foe'] = attacker.tile.unitsWithinNSpaces(4)
    defAreas['global'] = defender.tile.unitsWithinNSpaces(16)

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

        # Savior protects defender from post-combat effects
        if savior_unit is not None and defender in targeted_units:
            targeted_units.remove(defender)

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

        if effect[0] == "sp_reset":
            for x in targeted_units:
                if x not in sp_charges:
                    sp_charges[x] = 0
                sp_charges[x] -= 99

        i += 1

    return damage_taken, heals_given, sp_charges
