from hero import *
from combat import CombatField

def create_combat_fields(player_team, enemy_team):
    combat_fields = []

    for unit in player_team + enemy_team:

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()

        if "spurAtk" in unitSkills:
            owner = unit
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"spurAtk_f": unitSkills["spurAtk"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "spurSpd" in unitSkills:
            owner = unit
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"spurSpd_f": unitSkills["spurSpd"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "spurDef" in unitSkills:
            owner = unit
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"spurDef_f": unitSkills["spurDef"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

        if "spurRes" in unitSkills:
            owner = unit
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_self = False
            affect_other_side = True
            effects = {"spurRes_f": unitSkills["spurRes"]}

            field = CombatField(owner, range, condition, affect_self, affect_other_side, effects)
            combat_fields.append(field)

    return combat_fields

def start_of_turn(team, turn):

    # LOOP 1: BUFFS, DEBUFFS, AND STATUS EFFECTS
    for unit in team:

        tile = unit.tile

        tiles_within_n_spaces = [[]]
        units_within_n_spaces = [[]]
        allies_within_n_spaces = [[]]
        foes_within_n_spaces = [[]]

        i = 1
        while i <= 5:
            tiles_within_n_spaces.append(tile.tilesWithinNSpaces(i))

            for tile in tiles_within_n_spaces[i]:
                units_within_n_spaces.append([])
                allies_within_n_spaces.append([])
                foes_within_n_spaces.append([])

                if tile.hero_on is not None:
                    units_within_n_spaces[i].append(tile.hero_on)

                    if unit.side == tile.hero_on.side and unit != tile.hero_on:
                        allies_within_n_spaces[i].append(tile.hero_on)
                    if unit.side != tile.hero_on.side:
                        foes_within_n_spaces[i].append(tile.hero_on)

            i += 1

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur

        atkHPGreaterEqual25Percent = unitHPCur / unitStats[0] >= 0.25
        atkHPGreaterEqual50Percent = unitHPCur / unitStats[0] >= 0.50
        atkHPGreaterEqual75Percent = unitHPCur / unitStats[0] >= 0.75
        atkHPEqual100Percent = unitHPCur == unitStats[0]

        if "honeAtk" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(ATK, unitSkills["honeAtk"])

        if "honeSpd" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(SPD, unitSkills["honeSpd"])

        if "honeDef" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(DEF, unitSkills["honeDef"])

        if "honeRes" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(RES, unitSkills["honeRes"])

        if "defiantAtk" in unitSkills and unitHPCur / unitStats[0] <= 0.50:
            unit.inflictStat(ATK, 2 * unitSkills["defiantAtk"] + 1)

        if "oddDefWave" in unitSkills and turn % 2 == 1:
            unit.inflictStat(DEF, unitSkills["oddDefWave"])
            for ally in allies_within_n_spaces[1]:
                ally.inflictStat(DEF, unitSkills["oddDefWave"])

        if "bridal_shenanigans" in unitSkills and atkHPGreaterEqual25Percent:
            unit.inflictStat(ATK, 6)
            unit.inflictStat(SPD, 6)
            unit.inflictStatus(Status.MobilityUp)

def can_be_on_terrain(terrain_int, move_type_int):
    if terrain_int == 0 or terrain_int == 3: return True
    if terrain_int == 4: return False

    if terrain_int == 1:
        if move_type_int == 1: return False
        else: return True

    if terrain_int == 2:
        if move_type_int == 2: return True
        else: return False

def get_warp_moves(unit, unit_team, enemy_team):
    unitSkills = unit.getSkills()
    unitStats = unit.getStats()

    warp_moves = []

    if "escRoute" in unitSkills:
        if unit.HPcur/unitStats[HP] <= unitSkills["escRoute"] * 0.10 + 0.20:

            for ally in unit_team:
                if ally != unit:
                    adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                    for adj_tile in adj_ally_spaces:
                        if can_be_on_terrain(adj_tile.terrain, unit.move) and adj_tile.hero_on is None:
                            warp_moves.append(adj_tile)

    if "annaSchmovement" in unitSkills and unit.HPcur/unitStats[HP] >= 0.50:
        potential_allies = unit.tile.unitsWithinNSpaces(2)
        for ally in potential_allies:
            if ally != unit and ally.side == unit.side:
                adj_ally_spaces = ally.tile.tilesWithinNSpaces(2)
                for adj_tile in adj_ally_spaces:
                    if can_be_on_terrain(adj_tile.terrain, unit.move) and adj_tile.hero_on is None:
                        warp_moves.append(adj_tile)

    warp_moves = list(set(warp_moves))

    return warp_moves

# STRING COLLECTION
# -- EFFECT TYPES --
# buff_stat   - Applies buff of stat by N (Ex. buff_atk_7, buff_spd_4)
# debuff_stat - Applies debuff of stat by N (Ex. debuff_def_6, debuff_res_3)
# status_S      - Applies status S (Ex. status_DeepWounds, status_Orders)
# damage      - Deals N damage (Ex. damage_7)
# heal        - Heals N health (Ex. heal_10)
# end_turn      - Ends action of allies

# -- GROUP TYPES --
# self                - applies to only self
# foe                 - applies to only foe
# allies              - applies to only allies
# foe_allies          - applies to only foe's allies
# self_and_allies     - applies to self and self's allies
# foe_and_foes_allies - applies to foe and foe's allies

# -- AREA TYPES --
# one                   - only one unit (used for self/foe group types)
# within_N_spaces_self  - within N spaces of self (Ex. within_2_spaces_self)
# within_N_spaces_foe   - within N spaces of foe (Ex. within_4_spaces_foe)
# nearest_N_spaces_self - nearest N spaces of self, not including self
# nearest_N_spaces_foe - nearest N spaces of foe, not including foe
# within_N_rows_self
# within_N_cols_self
# within_N_rows_or_cols_self
# within_N_rows_and_cols_self

def foes_in_group(unit, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side != x.side:
            returned_list.append(x)
    return returned_list

def end_of_combat(atk_effects, def_effects, attacker, defender):
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()

    defSkills = defender.getSkills()
    defStats = defender.getStats()

    atkAreas = {}
    atkAreas['within_2_spaces_foe'] = defender.tile.unitsWithinNSpaces(2)

    defAreas = {}
    defAreas['within_2_spaces_foe'] = attacker.tile.unitsWithinNSpaces(2)

    areaMethods = {}
    areaMethods['foe_and_foes_allies'] = foes_in_group


    for effect in atk_effects:
        units_in_area = atkAreas[effect[3]]
        unit_determine_method = areaMethods[effect[2]]
        targeted_units = unit_determine_method(attacker, units_in_area)

        if effect[0] == "debuff_def":
            for x in targeted_units:
                x.inflictStat(DEF, -effect[1])

        if effect[0] == "debuff_res":
            for x in targeted_units:
                x.inflictStat(RES, -effect[1])

    for effect in def_effects:
        units_in_area = defAreas[effect[3]]
        unit_determine_method = areaMethods[effect[2]]
        targeted_units = unit_determine_method(defender, units_in_area)

        if effect[0] == "debuff_def":
            for x in targeted_units:
                x.inflictStat(DEF, -effect[1])

        if effect[0] == "debuff_res":
            for x in targeted_units:
                x.inflictStat(RES, -effect[1])


