# This file holds several methods to carry out the following functions for game.py:
# - Start of turn skills
# - Warp tiles
# - Combat Fields
# - Post-combat effects
# - Checking conditions for Duo/Harmonic skills to activate

from hero import *
from combat import CombatField
from collections import deque

within_1_space = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 1
within_2_space = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
within_3_space = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 3
within_4_space = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 4

within_1_row_or_col = lambda s: lambda o: abs(s[0] - o[0]) == 0 or abs(s[1] - o[1]) == 0
within_3_rows_or_cols = lambda s: lambda o: abs(s[0] - o[0]) <= 1 or abs(s[1] - o[1]) <= 1

global_range = lambda s: lambda o: True

DESTROYABLE_STRUCTS = ["Bolt Tower", "Tactics Room", "Healing Tower", "Panic Manor", "Catapult",
                       "Bright Shrine", "Dark Shrine", "Safety Fence", "Duo's Indulgence", "Duo's Hinderance",
                       "Infantry School", "Cavalry School", "Flier School", "Armor School", "Safety Fence"]

# Bolt Tower, Healing Tower
def get_tower_hp_change(level):
    if 1 <= level <= 9:
        return level * 5 + 5
    else:
        return level * 2 + 32

# Panic Manor, Tactics Room, Heavy Trap, Hex Trap
def get_tower_hp_threshold(level):
    if 1 <= level <= 9:
        return level * 5 + 35
    else:
        return level * 2 + 62

def create_combat_fields(player_team, enemy_team):
    combat_fields = []

    cohorts = []
    for unit in player_team:
        if unit.pair_up_obj:
            cohorts.append(unit.pair_up_obj)

    for unit in player_team + enemy_team + cohorts:

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()

        owner = unit

        # Anathema
        if True:
            range = within_3_space
            condition = lambda s: lambda o: Status.Anathema in s.statusPos
            affect_same_side = False
            effects = {"spdRein_f": 4, "defRein_f": 4, "resRein_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "spurAtk" in unitSkills:
            range = within_1_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": unitSkills["spurAtk"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "driveAtk" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": unitSkills["driveAtk"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "spurSpd" in unitSkills:
            range = within_1_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"spdCombat": unitSkills["spurSpd"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "driveSpd" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"spdCombat": unitSkills["driveSpd"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "spurDef" in unitSkills:
            range = within_1_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"defCombat": unitSkills["spurDef"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "driveDef" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"defCombat": unitSkills["driveDef"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "spurRes" in unitSkills:
            range = within_1_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"resCombat": unitSkills["spurRes"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "driveRes" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"resCombat": unitSkills["driveRes"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Cross Spurs
        if "crossSpurAtk" in unitSkills:
            range = within_1_row_or_col
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": unitSkills["crossSpurAtk"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "crossSpurSpd" in unitSkills:
            range = within_1_row_or_col
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"spdCombat": unitSkills["crossSpurSpd"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "crossSpurDef" in unitSkills:
            range = within_1_row_or_col
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"defCombat": unitSkills["crossSpurDef"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "crossSpurRes" in unitSkills:
            range = within_1_row_or_col
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"resCombat": unitSkills["crossSpurRes"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "goadCav" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 1
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "wardCav" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 1
            affect_same_side = True
            effects = {"defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "goadFly" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 2
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "wardFly" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 2
            affect_same_side = True
            effects = {"defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "goadArmor" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 3
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "wardArmor" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 3
            affect_same_side = True
            effects = {"defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "goadDragon" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.wpnType in DRAGON_WEAPONS
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "wardDragon" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.wpnType in DRAGON_WEAPONS
            affect_same_side = True
            effects = {"defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "goadBeast" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.wpnType in BEAST_WEAPONS
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "wardBeast" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.wpnType in BEAST_WEAPONS
            affect_same_side = True
            effects = {"defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # REIN SKILLS
        if "atkRein" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": unitSkills["atkRein"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "spdRein" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdRein_f": unitSkills["spdRein"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "defRein" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"defRein_f": unitSkills["defRein"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "resRein" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"resRein_f": unitSkills["resRein"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # HOLD SKILLS
        if "atkHold" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": unitSkills["atkHold"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "spdHold" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdRein_f": unitSkills["spdHold"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "defHold" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"defRein_f": unitSkills["defHold"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "resHold" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"resRein_f": unitSkills["resHold"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # REIN CRUX SKILLS
        if "atkRC" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": unitSkills["atkRC"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "spdRC" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdRein_f": unitSkills["spdRC"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "defRC" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"defRein_f": unitSkills["defRC"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "resRC" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"resRein_f": unitSkills["resRC"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "cruxField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 or abs(s[1] - o[1]) <= 1
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"cruxField_f": unitSkills["cruxField"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "infantryRush" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 0
            affect_same_side = True

            if unitSkills["infantryRush"] == 1:
                effects = {"iRush1": 0}
            elif unitSkills["infantryRush"] == 2:
                effects = {"iRush2": 0}
            else:
                effects = {"iRush3": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "infantryRushSe" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 0
            affect_same_side = True

            if unitSkills["infantryRushSe"] == 1:
                effects = {"iRush1": 0}
            elif unitSkills["infantryRushSe"] == 2:
                effects = {"iRush2": 0}
            else:
                effects = {"iRush3": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "infantryFlash" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 0
            affect_same_side = True

            if unitSkills["infantryFlash"] == 1:
                effects = {"iFlash1": 0}
            elif unitSkills["infantryFlash"] == 2:
                effects = {"iFlash2": 0}
            else:
                effects = {"iFlash3": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "infantryBreath" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 0
            affect_same_side = True
            effects = {"iBreath_f": 1, "defStance": unitSkills["infantryBreath"], "resStance": unitSkills["infantryBreath"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "infHexblade" in unitSkills:
            range = within_1_space
            condition = lambda s: lambda o: o.wpnType in PHYSICAL_WEAPONS and o.move == 0
            affect_same_side = True
            effects = {"adjHexblade": 1, "atkCombat": unitSkills["infHexblade"], "spdCombat": unitSkills["infHexblade"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Distant Guard
        if "distGuard" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"distGuard_f": unitSkills["distGuard"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Barricade
        if "barricade" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"defCombat": 4, "resCombat": 4, "barricade_dull": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "closeGuard" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"closeGuard_f": unitSkills["closeGuard"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "guidance4" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 0 or o.move == 3
            affect_same_side = True
            effects = {"atkCombat": 3, "spdCombat": 3, "speedNFU": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "soaring_guidance" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 0 or o.move == 2
            affect_same_side = True
            effects = {"atkCombat": 3, "spdCombat": 3, "speedNFU": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "respiteField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"defCombat": 2, "resCombat": 2, "uncondGuard": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Breath of Life 4
        if "breath_of_life4" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"breath_of_life4_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Atk/Res Detect
        if "atkResDetect" in unitSkills:
            range = global_range
            condition = lambda s: lambda o: Status.Exposure in o.statusNeg
            affect_same_side = False
            effects = {"atkRein_f": 5, "resRein_f": 5, "dullAtkRes_f": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Spd/Def Detect
        if "spdDefDetect" in unitSkills:
            range = global_range
            condition = lambda s: lambda o: Status.Exposure in o.statusNeg
            affect_same_side = False
            effects = {"spdRein_f": 5, "defRein_f": 5, "dullSpdDef_f": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Called to Serve
        if "calledToServe" in unitSkills:
            range = global_range
            condition = lambda s: lambda o: Status.NullBonuses in o.statusNeg
            affect_same_side = True
            effects = {"trueAllHits": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Spring-Air Axe/Egg
        if "springAirBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkCombat": -5, "spdCombat": -5, "defCombat": -5, "resCombat": -5, "springAirTempo_f": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # UNIQUE STUFF

        # Falchion (Refine Eff) - Marth
        if "driveSpectrum" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 2, "spdCombat": 2, "defCombat": 2, "resCombat": 2}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Sword of Peace - FE!Marth
        if "The guy from Smash Bros" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "spdCombat": 5, "postCombatHeal_f": 10, "drivePreempt_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Renowned Bow (Refine Eff) - Gordin
        if "gordin_field" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 4, "defRein_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Sacrifice Staff (Base) - FA!Maria
        if "sacrificeStaff" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 2, "spdCombat": 2, "defCombat": 2, "resCombat": 2, "sacrificeStaff_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Martyr's Staff - FA!Lena
        if "martyrsStaff" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "resCombat": 5, "martyrsStaff_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "nagaRefineBoost" in unitSkills:
            range = within_4_space
            condition = lambda s: lambda o: Status.EffDragons in o.statusPos
            affect_same_side = True
            effects = {"atkCombat": 3, "spdCombat": 3, "defCombat": 3, "resCombat": 3}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Love for All! - Dragon Tiki
        if "loveForAll!" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "spdCombat": 5, "defCombat": 5, "resCombat": 5, "loveJump_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Opposing Stones - H!Nagi
        if "hNagiBoost" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "defCombat": 4, "resCombat": 4, "postCombatHeal_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Staff of Lilies (Refine Eff) - Silque
        if "silqueField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"silqueField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Knightly/Lordly Lance (Refine Eff) - Mathilda/Clive
        if "jointSupportPartner" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.isSupportOf(s)
            affect_same_side = True
            effects = {"jointSupportPartner_f": 3}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Toasty Skewer
        if "toastyField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"defStance": 3, "resStance": 3}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Prior's Tome - Nomah
        if "nomahBoost" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "resCombat": 5, "postCombatHeal_f": 7, "nomahNullPenalty": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Nurturing Breath (Base) - Mila
        if "milaBoost" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 3 and abs(s[1] - o[1]) <= 3
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 2, "spdCombat": 2, "defCombat": 2, "resCombat": 2}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Nurturing Breath (Refine Base) - Mila
        if "milaRefineBoost" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 3 and abs(s[1] - o[1]) <= 3
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Nurturing Breath (Refine Eff) - Mila
        if "rejoice" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 3 and abs(s[1] - o[1]) <= 3
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"rejoice_f": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Spirit Forest Writ (Refine Eff) - L!Deirdre
        if "Jovial Merryment" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"connectedWorld_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Heavenly Icicle (Base) - Díthorba
        if "dithorbaField" in unitSkills:
            range = lambda s: lambda o: within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdRein_f": 5, "defRein_f": 5, "fuDenialRein_f": 1, "cruxField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Thunderhead (Refine Eff) - P!Olwen
        if "olwen_field" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"olwen_field_f": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Indignant Bow (Refine Eff) - Ronan
        if "about half done, and there's still so many" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "spdCombat": 5, "resCombat": 5, "ronanField_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Kia Staff (Refine Eff) - Sara
        if "kiaRecoveryPlus" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "spdCombat": 5, "speedNFU": 0, "postCombatHeal_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Repair - Safy
        if "repair" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Thief - Tina
        if "tinaBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 4, "spdRein_f": 4, "defRein_f": 4, "resRein_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Crimson Lance (Refine Eff) - Melady
        if "crimsonLance" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 4, "spdRein_f": 4, "defRein_f": 4, "guardRein_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "galleField" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 4, "defRein_f": 4, "guardRein_f": 1, "cruxField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Dazzling Breath (Refine Base) - L!Fae
        if "LFaeRefine" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 5, "spdRein_f": 5, "defRein_f": 5, "resRein_f": 5, "nullSelfBonuses": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Bern's New Way - L!Guinivere
        if "bernsNewWay" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"postCombatHeal_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Holy Ground - Elimine
        if "holyGround" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"flaynField_f": 1, "defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "holyGroundPlus" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"flaynField_f": 1, "defCombat": 5, "resCombat": 5, "holyGroundPlus_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Tailwind Shuriken (Refine Eff) - NI!Lyn
        if "fwam" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdRein_f": 5, "defRein_f": 5, "reinHalfDR_f": 1, "cruxField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Giga Excalibur (Refine EfF) - P!Nino
        if "doing her best" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Noble Bow - Louise
        if "louiseBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkCombat": -5, "spdCombat": -5, "defCombat": -5, "resCombat": -5, "nullSelfBonuses": 0, "louiseHealDisable": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Blessed Aureola - Athos
        if "athosBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "defCombat": 5, "resCombat": 5, "athosJump_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Righteous Lance - V!Ephraim
        if "Oh, I insist!" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "defCombat": 4, "postCombatHeal_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Exotic Fruit Juice - SU!SS!Selena
        if "suSelenaField" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdRein_f": 6, "resRein_f": 6}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Sunstone's Blade - Glen
        if "glenBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "defCombat": 4, "postCombatHeal_f": 10}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "obsidianField" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 6, "defRein_f": 6, "duesselField_f": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Laconic Axe - DE!Marisa
        if "deMarisaBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4, "deMarisaBraveTarget": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Godly Breath - L!Myrrh
        if "the orbs" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkCombat": -5, "spdCombat": -5, "defCombat": -5, "resCombat": -5, "driveHalfDR_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Loyal Greatlance (Refine Eff) - Oscar
        if "oscarDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.move == 0 or o.move == 1
            affect_same_side = True
            effects = {"atkCombat": 3, "spdCombat": 3}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Fluttering Fan - SF!Nephenee
        if "sfNepheneeBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"sfNepheneeBoost_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "tannenbatonField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"defCombat": 2, "resCombat": 2, "uncondGuard": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Gurgurant (Refine Base) - Ashnard
        if "bigRein" in unitSkills:
            range = within_4_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 5, "defRein_f": 5, "ashnardField_f": 1}
            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "ranulfField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 2, "defCombat": 2}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "jorgeFields" in unitSkills:
            range = within_4_space
            condition = lambda s: lambda o: True

            affect_same_side1 = True
            effects1 = {"atkCombat": 5, "defCombat": 5}

            affect_same_side2 = True
            effects2 = {"atkRein_f": 5, "defRein_f": 5, "cruxField_f": 1}

            field1 = CombatField(owner, range, condition, affect_same_side1, effects1)
            combat_fields.append(field1)

            field2 = CombatField(owner, range, condition, affect_same_side2, effects2)
            combat_fields.append(field2)

        if "ranulfRefineField" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "defCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Heart of Crimea
        if "heartOCrimea" in unitSkills:
            range = within_4_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 4, "spdRein_f": 4, "defRein_f": 4, "resRein_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Moonless Breath (Refine Eff) - H!F!Grima
        if "hfGrimaScowl" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side1 = True
            effects1 = {"atkCombat": 3, "defCombat": 3, "resCombat": 3}

            affect_same_side2 = False
            effects2 = {"hfGrimaScowl_f": 1}

            field1 = CombatField(owner, range, condition, affect_same_side1, effects1)
            combat_fields.append(field1)

            field2 = CombatField(owner, range, condition, affect_same_side2, effects2)
            combat_fields.append(field2)

        # Achimenes Furl (Base) - V!F!Robin
        if "vRobinEffects" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True

            affect_same_side1 = False
            affect_same_side2 = True

            effects1 = {"vRobinRein": 5}
            effects2 = {"vRobinHeal": 5}

            field1 = CombatField(owner, range, condition, affect_same_side1, effects1)
            combat_fields.append(field1)

            field2 = CombatField(owner, range, condition, affect_same_side2, effects2)
            combat_fields.append(field2)

        # Father's Tactics (Refine Eff) - F!Morgan
        if "morganJointDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 3, "spdCombat": 3}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Geirskögul (Base) - B!Lucina
        if "lucinaDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.wpnType in MELEE_WEAPONS
            affect_same_side = True
            effects = {"lucinaDrive_f": 3}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "refinedLucinaDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.wpnType in PHYSICAL_WEAPONS
            affect_same_side = True
            effects = {"refinedLucinaDrive_f": 3}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Exalt's War Staff - CH!Emmeryn
        if "chEmmerynBoost" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4, "postCombatHeal_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Tharja's Hex (Refined Eff) - Tharja
        if "tharja_field" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 4, "spdRein_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # LORD HAVE MERCY
        if "tharjaComplexField" in unitSkills:
            range = within_3_space
            condition1 = lambda s: lambda o: len(allies_within_n(s, 3)) == 1
            condition2 = lambda s: lambda o: len(allies_within_n(s, 3)) == 2
            condition3 = lambda s: lambda o: len(allies_within_n(s, 3)) >= 3
            affect_same_side = False
            effects1 = {"complexRein1_f": 2}
            effects2 = {"complexRein2_f": 4}
            effects3 = {"complexRein3_f": 6}

            field1 = CombatField(owner, range, condition1, affect_same_side, effects1)
            field2 = CombatField(owner, range, condition2, affect_same_side, effects2)
            field3 = CombatField(owner, range, condition3, affect_same_side, effects3)
            combat_fields.append(field1)
            combat_fields.append(field2)
            combat_fields.append(field3)

        if "rhajatField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdRein_f": 5, "resRein_f": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Grimoire (Refine Eff) - H!Nowi
        if "nowiField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 3
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"nowiField_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Yato (Refine Eff) - Corrin
        if "supportThem" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.allySupport == s.intName
            affect_same_side = True
            effects = {"corrinField_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Ice-Tribe Axe - FF!Felicia
        if "iceFeliciaBoost" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: Status.NullEffDragons in o.statusPos
            affect_same_side = True
            effects = {"iceFelicia_f": 1, "spdCombat": 5, "resCombat": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "gunterJointDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"gunterJointDrive_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "hinokaField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 3
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"hinokaField_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Rallying Cry - L!Hinoka
        if "rallyingCry" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: o.move != 2
            affect_same_side = False
            effects = {"spdRein_f": 5, "defRein_f": 5, "resRein_f": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Quiet Strength - L!Sakura
        if "quietStrength" in unitSkills:
            range = global_range
            condition = lambda s: lambda o: Status.Salvage in o.statusPos
            affect_same_side = True
            effects = {"atkCombat": 5, "spdCombat": 5, "defCombat": 5, "resCombat": 5, "sakuraField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Sword of Dusk - CH!Xander
        if "chXanderBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkCombat": -5, "spdCombat": -5, "defCombat": -5, "springAirTempo_f": 1, "cruxField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "camillaField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: o.move == 1 or o.move == 2
            affect_same_side = True
            effects = {"driveAtk_f": 3, "driveSpd_f": 3}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "eliseField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"eliseField_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Flier Hinoka
        if "hinokaJointDrive" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"driveAtk_f": 4, "driveSpd_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "kadenField" in unitSkills or "kadenField2" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True

            effects = {"kadenField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "kadenSupport" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True

            effects = {"kadenSupport_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "nyVelouriaBoost" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.isSupportOf(s)
            affect_same_side = True
            effects = {"fastCharge": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "yukimuraBoost" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 3 and abs(s[1] - o[1]) <= 3
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "defCombat": 4, "resCombat": 4, "drPierce30_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "LMBylethBoost" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"speedNFU": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "LMBylethRefine" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"speedNFU": 1, "driveAtk_f": 5, "driveSpd_f": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "YOU CANNOT STOP THE FLOW OF TIME" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"LBylethPenaltyNull": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "suFBylethRefine" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"driveAtk_f": 4, "driveSpd_f": 4, "driveHalfDR_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "LFBylethBoost" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"tempo": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "LFBylethRefine" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"tempo": 0, "atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Guide's Hourglass (Base) - DE!M!Byleth
        if "deBylethBoost" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "the nair landing hitbox has won me many a game" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdRein_f": 5, "defRein_f": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Lúin (Refine Eff) - Ingrid
        if "shadow the hedgehog" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdRein_f": 5, "defRein_f": 5, "cruxField_f": 1, "nullSelfBonuses": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Just Bow - Ashe
        if "asheBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4, "asheBoost_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "hildaField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.get_visible_stat(DEF) > s.get_visible_stat(DEF)
            affect_same_side = True
            effects = {"driveAtk_f": 4, "driveSpd_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "hildaRefineField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.get_visible_stat(DEF) > s.get_visible_stat(DEF) or s.unitCombatInitiates == 0
            affect_same_side = True
            effects = {"driveAtk_f": 4, "driveSpd_f": 4, "driveDef_f": 4, "driveRes_f": 4, "allyFoeDenial_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "suHildaBoost" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"fastCharge_f": 1, "driveAtk_f": 6}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "aHildaBoost" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: o.get_visible_stat(DEF) > s.get_visible_stat(DEF) or s.unitCombatInitiates == 0
            affect_same_side = True
            effects = {"atkCombat": 3, "spdCombat": 3, "defCombat": 3, "resCombat": 3, "aHildaDR_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "flaynField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"flaynField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "flaynRefineField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"flaynField_f": 1, "driveAtk_f": 4, "driveRes_f": 4, "uncondGuard": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Kitty-Cat Parasol
        if "hFlaynBoost" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"fastCharge_f": 0, "nullFoeBonuses": 0, "flaynField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Spear of Assal (Refine Base) - Seteth
        if "Flayn's got us trapped in the McDonald's playplace" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"driveAtk_f": 4, "driveSpd_f": 4, "driveDef_f": 4, "driveRes_f": 4, "nullFoeBonuses": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Spear of Assal (Refine Eff) - Seteth
        if "Please get us out. We haven't eaten our order yet." in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"driveAtk_f": 4, "driveSpd_f": 4, "driveDef_f": 4, "driveRes_f": 4, "setethField_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Devoted Breath - V!Rhea
        if "vRheaBoost" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True

            effects1 = {"driveDef_f": 4, "driveRes_f": 4, "vRheaDR_f": 7}

            field1 = CombatField(owner, range, condition, affect_same_side, effects1)
            combat_fields.append(field1)

            effects2 = {"vRheaMiracle_f": 1}

            field2 = CombatField(owner, range, condition, affect_same_side, effects2)
            combat_fields.append(field2)

        # Wings of Light - Seiros
        if "wingsOfLight" in unitSkills:
            range = global_range
            condition = lambda s: lambda o: o.blessing and o.blessing.element >= 4 and o.blessing.boostType != 0
            affect_same_side = True
            effects = {"wingsOfLight_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Wings of Light+ - Seiros
        if "wingsOfLightPlus" in unitSkills:
            affect_same_side = True

            range1 = global_range
            condition1 = lambda s: lambda o: o.blessing and o.blessing.element >= 4 and o.blessing.boostType != 0
            effects1 = {"wingsOfLightPlus_f": 1}

            range2 = within_3_rows_or_cols
            condition2 = lambda s: lambda o: True
            effects2 = {"atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4, "fastCharge": 0}

            field1 = CombatField(owner, range1, condition1, affect_same_side, effects1)
            combat_fields.append(field1)

            field2 = CombatField(owner, range2, condition2, affect_same_side, effects2)
            combat_fields.append(field2)

        # Charging Horn (Base/Refine Base) - Gatekeeper
        if "gatekeeperBoost" in unitSkills or "gatekeeperRefine" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "spdCombat": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Charging Horn (Refine Eff) - Gatekeeper
        if "Greetings!" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"defCombat": 5, "resCombat": 5, "postCombatHeal_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Fetters of Dromi - L!Yuri
        if "fettersODromi" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 4, "spdRein_f": 4, "defRein_f": 4, "resRein_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Dual Sword - L!M!Shez
        if "SHEZ! ultimate" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"dualSword_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "kiriaField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkRein_f": 6, "resRein_f": 6}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "mamoriromam" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"mamoriromam_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Dragon Blast
        if "bidenBlast" in unitSkills:
            range = global_range
            condition = lambda s: lambda o: o.isSupportOf(s)
            affect_same_side = True
            effects = {"DamageReductionPierce": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Bond Blast
        if "bidenBlast" in unitSkills:
            range = global_range
            condition = lambda s: lambda o: o.isSupportOf(s) or Status.Bonded in o.statusPos
            affect_same_side = True
            effects = {"tropicalBidenBlast": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Fell Child's Blade - FA!M!Alear
        if "that is also stupid" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkCombat": -5, "spdCombat": -5, "defCombat": -5, "resCombat": -5, "nullSelfBonuses": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Dragon Monarch
        if "dragonMonarch" in unitSkills or "corruptedDragon" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 2 and abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4, "sothisTempo": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Hippity-Hop Axe - SP!Framme
        if "It's a shuffling in the seat." in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4, "frammeChainGuard_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Joyous Tome - Céline
        if "célineBoost" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"postCombatHeal_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Scroll of Teas - NI!Céline
        if "niCelineBoost" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"postCombatHeal_f": 10, "spdCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Arcane Charmer
        if "charmer" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"postCombatHeal_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Diva-Pair Parasol
        if "suGoldmaryBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: o.get_visible_stat(DEF) <= s.get_visible_stat(DEF) + 5
            affect_same_side = False
            effects = {"goldmaryDebuff_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Desert Spear - Timerra
        if "timerraBoost" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdCombat": 4, "defCombat": 4, "timerraBoost_f": 10}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "fellProtection" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True

            affect_same_side1 = True
            effects1 = {"atkCombat": 4, "resCombat": 4, "flaynField_f": 1}

            affect_same_side2 = False
            effects2 = {"fellProtection_f": 1}

            field1 = CombatField(owner, range, condition, affect_same_side1, effects1)
            combat_fields.append(field1)

            field2 = CombatField(owner, range, condition, affect_same_side2, effects2)
            combat_fields.append(field2)

        if "if you don't have a cinnamon roll, you're of no use to me" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"flaynField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "fellSuccessor" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True

            affect_same_side1 = True
            effects1 = {"atkCombat": 4, "defCombat": 4, "resCombat": 4}

            affect_same_side2 = False
            effects2 = {"fellSuccessor_f": 1}

            field1 = CombatField(owner, range, condition, affect_same_side1, effects1)
            combat_fields.append(field1)

            field2 = CombatField(owner, range, condition, affect_same_side2, effects2)
            combat_fields.append(field2)

        if "fellMajesty" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True

            affect_same_side1 = True
            effects1 = {"atkCombat": 5, "defCombat": 5, "resCombat": 5, "fellMajestyFirstDR_f": 7}

            affect_same_side2 = False
            effects2 = {"fellSuccessor_f": 1}

            field1 = CombatField(owner, range, condition, affect_same_side1, effects1)
            combat_fields.append(field1)

            field2 = CombatField(owner, range, condition, affect_same_side2, effects2)
            combat_fields.append(field2)

        if "veronicaField" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True

            affect_same_side1 = True
            effects1 = {"driveAtk_f": 3, "driveSpd_f": 3}

            field = CombatField(owner, range, condition, affect_same_side1, effects1)
            combat_fields.append(field)

            affect_same_side2 = False
            effects2 = {"defRein_f": 3, "resRein_f": 3}

            field = CombatField(owner, range, condition, affect_same_side2, effects2)
            combat_fields.append(field)

        # Protective - Nel
        if "protective" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkCombat": -5, "spdCombat": -5, "defCombat": -5, "resCombat": -5, "nullSelfBonuses": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Fell Slaystone - Rafal
        if "rafalBoost" in unitSkills:
            range = within_3_space
            affect_same_side = True

            condition1 = lambda s: lambda o: True
            effects1 = {"atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4, "uncondGuard": 0}

            field1 = CombatField(owner, range, condition1, affect_same_side, effects1)
            combat_fields.append(field1)

            condition2 = lambda s: lambda o: o.emblem
            effects2 = {"atkCombat": 4, "spdCombat": 4, "defCombat": 4, "resCombat": 4}

            field2 = CombatField(owner, range, condition2, affect_same_side, effects2)
            combat_fields.append(field2)

        # Gjallarbrú (Refine Eff) - BR!Fjorm
        if "brFjormField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"driveAtk_f": 4, "driveSpd_f": 4, "driveNullPenalties": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "stupid dumb idiot field I cant code easily" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"ylgrField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "niflField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"niflField_f": 1, "driveSpd_f": 4, "driveRes_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "muspellField" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"muspellField_f": 1, "driveAtk_f": 4, "driveDef_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "eirField" in unitSkills:
            range = lambda s: lambda o: True
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"eirField_f": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "everlivingDomain" in unitSkills:
            range = lambda s: lambda o: True
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"everlivingDomain_f": 1, "defCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "peonyCrossSpur" in unitSkills:
            range = within_1_row_or_col
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "spdCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "nyPeonyField" in unitSkills:
            range = within_1_row_or_col
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 6}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Flower of Caring - X!Peony
        if "jokerrrrrrrr" in unitSkills:
            range = within_1_row_or_col
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "spdCombat": 5, "postCombatHeal_f": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Flower of Ease (Base) - Mirabilis
        if "zzzzZZZZzzzzz" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"zzzzZZZZzzzzz_f": 3}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Flower of Ease (Refine Base) - Mirabilis
        if "zzzzzzzzzzzzzzzz" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"zzzzzzzzzzzzzzzz_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Dreamflake (Base) - WI!Mirabilis
        if "wiMirabilisField" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"wiMirabilisField_f": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Daydream Egg - SP!Mirabilis
        if "daydream_egg" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spMirabilisField_f": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Flower of Plenty (Base) - Plumeria
        if "plumeriaField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 and abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 3, "resCombat": 3}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "plumeriaRefineField" in unitSkills:
            range = lambda s: lambda o: abs(s[0] - o[0]) <= 1 and abs(s[1] - o[1]) <= 2
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 4, "resCombat": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # First-Dream Bow (Base) - NY!Plumeria
        if "nyPlumeriaFields" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True

            affect_same_side1 = True
            effects1 = {"atkCombat": 4}

            affect_same_side2 = False
            effects2 = {"atkRein_f": 4}

            field1 = CombatField(owner, range, condition, affect_same_side1, effects1)
            combat_fields.append(field1)

            field2 = CombatField(owner, range, condition, affect_same_side2, effects2)
            combat_fields.append(field2)

        # Springing Spear - SP!Plumeria
        if "spPlumeriaBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "defCombat": 5, "resCombat": 5, "spPlumeriaField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Flower of Sorrow (Base) - Triandra
        if "triandraField" in unitSkills:
            range = within_1_row_or_col
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"defRein_f": unitSkills["triandraField"], "resRein_f": unitSkills["triandraField"]}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Flower of Tribute - X!Triandra
        if "xTriandraBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spdRein_f": 5, "defRein_f": 5, "xTriDmg_f": 5}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Petaldream Horn - SP!Eitr
        if "spEitrBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"spEitrField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "reginnAccel" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"reginnField_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Iron Hreiðmarr - Fáfnir
        if "THE FAFNIR IS REAL" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkCombat": -5, "spdCombat": -5, "defCombat": -5, "guardRein_f": 1, "cruxField_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "openRetainerPlus" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"atkCombat": 5, "spdCombat": 5, "defCombat": 5, "resCombat": 5, "nullFoeBonuses": 0, "allHitHeal": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Horn of Harvest - H!Askr
        if "hAskrBoost" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"hAskrBoost_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Connected World - H!Askr
        if "connectedWorld" in unitSkills:
            range = within_3_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"connectedWorld_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Jaws of Closure - Elm
        if "elmBoost" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = False
            effects = {"atkCombat": -6, "spdCombat": -6, "defCombat": -6, "resCombat": -6, "reinHalfDR_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        # Thorr
        if "worldbreaker" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"fastCharge": 0}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "worldbreakerPlus" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"WBP_f": 5, "fastCharge": 0, "driveAtk_f": 4, "driveDef_f": 4, "driveRes_f": 4}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "loveONerþuz" in unitSkills:
            range = within_3_rows_or_cols
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"loveONerþuz_f": 1}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

        if "it's her!" in unitSkills:
            range = within_2_space
            condition = lambda s: lambda o: True
            affect_same_side = True
            effects = {"postCombatHeal_f": 7}

            field = CombatField(owner, range, condition, affect_same_side, effects)
            combat_fields.append(field)

    return combat_fields

def start_of_turn(starting_team, waiting_team, turn, season, game_mode, game_map, ally_defeated, ar_struct_tiles=None):

    # Advances "Will not trigger again for X turns after triggering" effects
    for unit in starting_team:
        for tag in ["disableWeapon", "disableAssist", "disableSpecial", "disableASkill", "disableBSkill", "disableCSkill", "disableEmblem"]:
            if tag in unit.statusOther:
                unit.statusOther[tag] -= 1

                if unit.statusOther[tag] == 0:
                    unit.statusOther.pop(tag)

            if unit.pair_up_obj:
                if tag in unit.pair_up_obj.statusOther:
                    unit.pair_up_obj.statusOther[tag] -= 1

                    if unit.pair_up_obj.statusOther[tag] == 0:
                        unit.pair_up_obj.statusOther.pop(tag)

    if not ar_struct_tiles:
        ar_struct_tiles = []

    # Return units within a given team with the greatest of a given stat
    def units_with_extreme_stat(cur_team, stat, find_max=True, exclude=None):
        filtered_team = [unit for unit in cur_team if unit != exclude]

        if not filtered_team:
            return []

        extreme_stat = filtered_team[0].get_visible_stat(stat)
        extreme_stat_units = [filtered_team[0]]

        if len(filtered_team) == 1:
            return extreme_stat_units

        for unit in filtered_team[1:]:
            unit_stat = unit.get_visible_stat(stat)

            if (find_max and unit_stat == extreme_stat) or (not find_max and unit_stat == extreme_stat):
                extreme_stat_units.append(unit)

            if (find_max and unit_stat > extreme_stat) or (not find_max and unit_stat < extreme_stat):
                extreme_stat = unit_stat
                extreme_stat_units = [unit]

        return extreme_stat_units

    def units_with_extreme_stat_pairing_sum(cur_team, stat1, stat2, find_max=True, exclude=None):
        filtered_team = [unit for unit in cur_team if unit != exclude]

        if not filtered_team:
            return []

        extreme_stat = filtered_team[0].get_visible_stat(stat1) + filtered_team[0].get_visible_stat(stat2)
        extreme_stat_units = [filtered_team[0]]

        if len(filtered_team) == 1:
            return extreme_stat_units

        for unit in filtered_team[1:]:
            unit_stat = unit.get_visible_stat(stat1) + unit.get_visible_stat(stat2)

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
    units_stored_great_talent = {}
    units_stored_statuses = {}

    for unit in starting_team + waiting_team:
        units_stored_buffs[unit] = [0] * 5
        units_stored_debuffs[unit] = [0] * 5
        units_stored_statuses[unit] = []
        units_stored_great_talent[unit] = []

    def add_buff(hero, stat, val):
        if stat == OMNI:
            units_stored_buffs[hero][ATK] = max(units_stored_buffs[hero][ATK], val)
            units_stored_buffs[hero][SPD] = max(units_stored_buffs[hero][SPD], val)
            units_stored_buffs[hero][DEF] = max(units_stored_buffs[hero][DEF], val)
            units_stored_buffs[hero][RES] = max(units_stored_buffs[hero][RES], val)

        else:
            units_stored_buffs[hero][stat] = max(units_stored_buffs[hero][stat], val)

    def add_debuff(hero, stat, val):
        if stat == OMNI:
            units_stored_debuffs[hero][ATK] = min(units_stored_debuffs[hero][ATK], val)
            units_stored_debuffs[hero][SPD] = min(units_stored_debuffs[hero][SPD], val)
            units_stored_debuffs[hero][DEF] = min(units_stored_debuffs[hero][DEF], val)
            units_stored_debuffs[hero][RES] = min(units_stored_debuffs[hero][RES], val)

        else:
            units_stored_debuffs[hero][stat] = min(units_stored_debuffs[hero][stat], val)

    def add_status(hero, status):
        if status not in units_stored_statuses[hero]:
            units_stored_statuses[hero].append(status)

    def add_great_talent(hero, stat, val, cap):
        units_stored_great_talent[hero].append((stat, val, cap))

    # Arrays of start-of-turn cleansing
    clear_bonus_statuses = []
    clear_bonus_stats = []

    clear_penalty_statuses = []
    clear_penalty_stats = []

    # Determine which side structures should be activated
    if starting_team:
        SIDE = starting_team[0].side
    else:
        SIDE = abs(waiting_team[0].side - 1)

    # Catapult Effect
    for struct_tile in ar_struct_tiles:
        struct = struct_tile.structure_on
        is_active_phase = struct.struct_type == SIDE + 1
        struct_not_destroyed = struct.health != 0

        if struct.name == "Catapult" and is_active_phase and struct_not_destroyed:
            area = struct_tile.tilesWithinNCols(1)

            for tile in area:
                cur_struct = tile.structure_on

                if cur_struct and cur_struct.struct_type != struct.struct_type and cur_struct.name in DESTROYABLE_STRUCTS and struct.level >= cur_struct.level:
                    tile.structure_on.health = 0

    # Upheaval - CAN BE STOPPED WITH FALSE START
    structs_to_be_destroyed = []

    if turn == 1 and ANIMA in season and game_mode == GameMode.AetherRaids and SIDE == 1:
        for unit in starting_team:

            # Upheaval
            if "ARDestroyColumn" in unit.getSkills():
                area = unit.tile.tilesWithinNCols(1)

                for tile in area:
                    cur_struct = tile.structure_on

                    if cur_struct and cur_struct.struct_type == 1 and cur_struct.name in DESTROYABLE_STRUCTS:
                        structs_to_be_destroyed.append(cur_struct)

            # Upheaval+
            elif "ARDestroyNearest" in unit.getSkills():
                southernmost_tile = unit.tile

                while southernmost_tile.south is not None:
                    southernmost_tile = southernmost_tile.south

                if southernmost_tile.structure_on and southernmost_tile.structure_on.struct_type == 1 and southernmost_tile.structure_on.name in DESTROYABLE_STRUCTS:
                    structs_to_be_destroyed.append(southernmost_tile.structure_on)
                else:
                    west_tile = southernmost_tile.west
                    east_tile = southernmost_tile.east

                    struct_found = False

                    while (west_tile is not None or east_tile is not None) and not struct_found:
                        if west_tile and west_tile.structure_on and west_tile.structure_on.struct_type == 1 and west_tile.structure_on.name in DESTROYABLE_STRUCTS:
                            structs_to_be_destroyed.append(west_tile.structure_on)
                            struct_found = True
                        else:
                            if west_tile: west_tile = west_tile.west

                        if east_tile and east_tile.structure_on and east_tile.structure_on.struct_type == 1 and east_tile.structure_on.name in DESTROYABLE_STRUCTS:
                            structs_to_be_destroyed.append(east_tile.structure_on)
                            struct_found = True
                        else:
                            if east_tile: east_tile = east_tile.east

        for struct in structs_to_be_destroyed:
            struct.health = 0

    # BEAST TRANSFORMATION
    for unit in starting_team:
        can_transform = False

        for condition in unit.get_transform_conditions():
            if condition == "DEFAULT-BEAST" and all(ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS for ally in allies_within_n(unit, 1)):
                can_transform = True
            if condition == "MUARIM-TURNS" and turn != 1 and turn != 3:
                can_transform = True
            if condition == "NO-CONDITIONS":
                can_transform = True
            if condition == "NO-CONDITIONS-100" and unit.HPcur / unit.getStats()[HP] == 1.00:
                can_transform = True
            if condition == "NO-CONDITIONS-50" and unit.HPcur / unit.getStats()[HP] >= 0.50:
                can_transform = True
            if condition == "ASKR-OTHERWORLD" and any([ally for ally in allies_within_n(unit, 2) if ally.primary_game != unit.primary_game or (ally.secondary_game != unit.primary_game and ally.secondary_game != -1)]):
                can_transform = True
            if condition == "FORTUNE-BEAST" and (any([ally for ally in allies_within_n(unit, 2) if ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS]) or
                                                 len([ally for ally in allies_within_n(unit, 1) if ally.wpnType not in DRAGON_WEAPONS + BEAST_WEAPONS]) <= 2):
                can_transform = True

        if can_transform:
            unit.transformed = True
        else:
            unit.transformed = False

    for unit in waiting_team:
        can_transform = False

        for condition in unit.get_transform_conditions():
            if condition == "DEFAULT-BEAST" and all(ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS for ally in allies_within_n(unit, 1)):
                can_transform = True
            if condition == "MUARIM-TURNS" and turn != 1 and turn != 3:
                can_transform = True
            if condition == "NO-CONDITIONS":
                can_transform = True
            if condition == "NO-CONDITIONS-100" and unit.HPcur / unit.getStats()[HP] == 1.00:
                can_transform = True
            if condition == "NO-CONDITIONS-50" and unit.HPcur / unit.getStats()[HP] >= 0.50:
                can_transform = True
            if condition == "ASKR-OTHERWORLD" and any([ally for ally in allies_within_n(unit, 2) if ally.primary_game != unit.primary_game or (ally.secondary_game != unit.primary_game and ally.secondary_game != -1)]):
                can_transform = True
            if condition == "FORTUNE-BEAST" and (any([ally for ally in allies_within_n(unit, 2) if ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS]) or
                                                 len([ally for ally in allies_within_n(unit, 1) if ally.wpnType not in DRAGON_WEAPONS + BEAST_WEAPONS]) <= 2):
                can_transform = True

        if can_transform and game_mode == GameMode.AetherRaids and turn == 1 and "AR-TRANSFORM" in unit.get_transform_conditions():
            unit.transformed = True


    # LOOP 1: BUFFS, DEBUFFS, AND STATUS EFFECTS
    for unit in starting_team:

        if Status.FalseStart in unit.statusNeg:
            continue

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

        unitHPGreaterEqual25Percent = unitHPCur / unitStats[HP] >= 0.25
        unitHPGreaterEqual50Percent = unitHPCur / unitStats[HP] >= 0.50
        unitHPGreaterEqual75Percent = unitHPCur / unitStats[HP] >= 0.75
        unitHPEqual100Percent = unitHPCur == unitStats[HP]

        # All allies
        allies = []
        for hero in starting_team:
            if hero is not unit:
                allies.append(hero)

        # HONE/FORTIFY
        if "honeAtk" in unitSkills or "honeAtkSe" in unitSkills:
            buff = max(unitSkills.get("honeAtk", 0), unitSkills.get("honeAtkSe", 0))

            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, buff)

        if "honeAtkW" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["honeAtkW"])

        if "honeSpd" in unitSkills or "honeSpdSe" in unitSkills:
            buff = max(unitSkills.get("honeSpd", 0), unitSkills.get("honeSpdSe", 0))

            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, buff)

        if "fortifyDef" in unitSkills or "fortifyDefSe" in unitSkills:
            buff = max(unitSkills.get("fortifyDef", 0), unitSkills.get("fortifyDefSe", 0))

            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, buff)

        if "fortifyRes" in unitSkills or "fortifyResSe" in unitSkills:
            buff = max(unitSkills.get("fortifyRes", 0), unitSkills.get("fortifyResSe", 0))

            for ally in allies_within_n_spaces[1]:
                add_buff(ally, RES, buff)

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

        if "honebeast" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.wpnType in BEAST_WEAPONS:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)

        if "fortibeast" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.wpnType in BEAST_WEAPONS:
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)

        # JOINT HONE
        if "jointHoneAtk" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, ATK, 5)

            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, 5)

        if "jointHoneSpd" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, SPD, 5)

            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, 5)

        if "jointHoneDef" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, DEF, 5)

            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, 5)

        if "jointHoneRes" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, RES, 5)

            for ally in allies_within_n_spaces[1]:
                add_buff(ally, RES, 5)

        # INCITE HONE
        if "atkSpdInciteHone" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Incited)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Incited)

        if "atkResInciteHone" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Incited)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.Incited)

        # THREATEN
        if "threatenAtk" in unitSkills or "threatenAtkSe" in unitSkills:
            debuff = max(unitSkills.get("threatenAtk", 0), unitSkills.get("threatenAtkSe", 0))

            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, ATK, -debuff)

        if "threatenAtkW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, ATK, -unitSkills["threatenAtkW"])

        if "threatenSpd" in unitSkills or "threatenSpdSe" in unitSkills:
            debuff = max(unitSkills.get("threatenSpd", 0), unitSkills.get("threatenSpdSe", 0))

            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, SPD, -debuff)

        if "threatenSpdW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, SPD, -unitSkills["threatenSpdW"])

        if "threatenDef" in unitSkills or "threatenDefSe" in unitSkills:
            debuff = max(unitSkills.get("threatenDef", 0), unitSkills.get("threatenDefSe", 0))

            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, DEF, -debuff)

        if "threatenDefW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, DEF, -unitSkills["threatenDefW"])

        if "threatenRes" in unitSkills or "threatenResSe" in unitSkills:
            debuff = max(unitSkills.get("threatenRes", 0), unitSkills.get("threatenResSe", 0))

            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, RES, -debuff)

        if "threatenResW" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, RES, -unitSkills["threatenResW"])

        # TIER 4 THREATEN
        if "threatAtkSpd" in unitSkills:
            if foes_within_n_spaces[2]:
                add_buff(unit, ATK, 5)
                add_buff(unit, SPD, 5)

        if "threatAtkDef" in unitSkills:
            if foes_within_n_spaces[2]:
                add_buff(unit, ATK, 5)
                add_buff(unit, DEF, 5)

        if "threatAtkRes" in unitSkills:
            if foes_within_n_spaces[2]:
                add_buff(unit, ATK, 5)
                add_buff(unit, RES, 5)

        # MENACE SKILLS
        if "atkSpdMenace" in unitSkills:
            if nearest_foes_within_n(unit, 4):
                add_buff(unit, ATK, 6)
                add_buff(unit, SPD, 6)

                for foe in nearest_foes_within_n(unit, 4):
                    add_debuff(foe, ATK, -6)
                    add_debuff(foe, SPD, -6)

        if "atkDefMenace" in unitSkills:
            if nearest_foes_within_n(unit, 4):
                add_buff(unit, ATK, 6)
                add_buff(unit, DEF, 6)

                for foe in nearest_foes_within_n(unit, 4):
                    add_debuff(foe, ATK, -6)
                    add_debuff(foe, DEF, -6)

        if "atkResMenace" in unitSkills:
            if nearest_foes_within_n(unit, 4):
                add_buff(unit, ATK, 6)
                add_buff(unit, RES, 6)

                for foe in nearest_foes_within_n(unit, 4):
                    add_debuff(foe, ATK, -6)
                    add_debuff(foe, RES, -6)

        if "spdDefMenace" in unitSkills:
            if nearest_foes_within_n(unit, 4):
                add_buff(unit, SPD, 6)
                add_buff(unit, DEF, 6)

                for foe in nearest_foes_within_n(unit, 4):
                    add_debuff(foe, SPD, -6)
                    add_debuff(foe, DEF, -6)

        if "spdResMenace" in unitSkills:
            if nearest_foes_within_n(unit, 4):
                add_buff(unit, SPD, 6)
                add_buff(unit, RES, 6)

                for foe in nearest_foes_within_n(unit, 4):
                    add_debuff(foe, SPD, -6)
                    add_debuff(foe, RES, -6)

        if "defResMenace" in unitSkills:
            if nearest_foes_within_n(unit, 4):
                add_buff(unit, DEF, 6)
                add_buff(unit, RES, 6)

                for foe in nearest_foes_within_n(unit, 4):
                    add_debuff(foe, DEF, -6)
                    add_debuff(foe, RES, -6)

        # BEAST THREATEN
        if "beastThreaten" in unitSkills:
            if foes_within_n_cardinal(unit, 3):

                add_buff(unit, ATK, 6)
                if unit.specialCount == unit.specialMax:
                    sp_charges[unit] += 1

                for foe in foes_within_n_cardinal(unit, 3):
                    add_debuff(foe, DEF, -7)
                    add_status(foe, Status.Panic)

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
            if ploy_type in unitSkills or f"{ploy_type}W" in unitSkills or f"{ploy_type}S" in unitSkills:
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
                        if f"{ploy_type}S" in unitSkills:
                            add_debuff(foe, stat, -unitSkills[f"{ploy_type}S"])

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

        # Tier 4 Ploy Skills
        if "atkSpdPloy" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, SPD, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Ploy)

        if "atkResPloy" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Ploy)

        if "spdResPloy" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, SPD, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Ploy)

        if "defResPloy" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, DEF, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Ploy)

        if "pulseUpPloy" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Ploy)

        if "panicPloy" in unitSkills:
            diff = 7 - unitSkills["panicPloy"] * 2

            for foe in foes_within_n_cardinal(unit, 1):
                if foe.HPcur <= unit.HPcur - diff:
                    add_status(foe, Status.Panic)

        if "panicPloyW" in unitSkills:
            diff = 7 - unitSkills["panicPloyW"] * 2

            for foe in foes_within_n_cardinal(unit, 1):
                if foe.HPcur <= unit.HPcur - diff:
                    add_status(foe, Status.Panic)

        if "panicPloySe" in unitSkills:
            diff = 7 - unitSkills["panicPloySe"] * 2

            for foe in foes_within_n_cardinal(unit, 1):
                if foe.HPcur <= unit.HPcur - diff:
                    add_status(foe, Status.Panic)

        if "stallPloy" in unitSkills:
            diff = 7 - unitSkills["stallPloy"] * 2

            for foe in foes_within_n_cardinal(unit, 1):
                if foe.HPcur <= unit.HPcur - diff:
                    add_status(foe, Status.Stall)

        # TACTIC SKILLS
        move_arrs = [[], [], [], []]
        for ally in starting_team:
            move_arrs[ally.move].append(ally)

        tactic_allies = []

        for arr in move_arrs:
            if len(arr) <= 2:
                for ally in arr:
                    tactic_allies.append(ally)

        if "atkTactic" in unitSkills or "atkTacticSe" in unitSkills:
            skill_lvl = max(unitSkills.get("atkTactic", 0), unitSkills.get("atkTacticSe", 0))

            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, ATK, 2 * skill_lvl)

        if "spdTactic" in unitSkills or "spdTacticSe" in unitSkills:
            skill_lvl = max(unitSkills.get("spdTactic", 0), unitSkills.get("spdTacticSe", 0))

            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, SPD, 2 * skill_lvl)

        if "defTactic" in unitSkills or "defTacticSe" in unitSkills:
            skill_lvl = max(unitSkills.get("defTactic", 0), unitSkills.get("defTacticSe", 0))

            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, DEF, 2 * skill_lvl)

        if "resTactic" in unitSkills or "resTacticSe" in unitSkills:
            skill_lvl = max(unitSkills.get("resTactic", 0), unitSkills.get("resTacticSe", 0))

            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, RES, 2 * skill_lvl)

        if "spdTacticW" in unitSkills:
            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, SPD, 6)

        if "resTacticW" in unitSkills:
            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit:
                    add_buff(ally, RES, 6)

        if "infNullFollowTactic" in unitSkills:
            for ally in tactic_allies:
                if ally in allies_within_n_spaces[2] and ally != unit and ally.move == 0:
                    add_status(ally, Status.NullFollowUp)

        if "ostiaPulseII" in unitSkills:
            for ally in tactic_allies:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)

        # CHILL SKILLS
        if "chillAtk" in unitSkills or "chillAtkSe" in unitSkills:
            level = max(unitSkills.get("chillAtk", 0), unitSkills.get("chillAtkSe", 0))

            for foe in units_with_extreme_stat(waiting_team, ATK):
                add_debuff(foe, ATK, -1 - 2 * level)

        if "chillAtkW" in unitSkills:
            for foe in units_with_extreme_stat(waiting_team, ATK):
                add_debuff(foe, ATK, -7)

        if "chillSpd" in unitSkills or "chillSpdSe" in unitSkills:
            level = max(unitSkills.get("chillSpd", 0), unitSkills.get("chillSpdSe", 0))

            for foe in units_with_extreme_stat(waiting_team, SPD):
                add_debuff(foe, SPD, -1 - 2 * level)

        if "chillSpdW" in unitSkills:
            highest_spd = units_with_extreme_stat(waiting_team, SPD, find_max=True)
            for foe in highest_spd:
                add_debuff(foe, SPD, -7)

        if "chillDef" in unitSkills or "chillDefSe" in unitSkills:
            level = max(unitSkills.get("chillDef", 0), unitSkills.get("chillDefSe", 0))

            for foe in units_with_extreme_stat(waiting_team, DEF):
                add_debuff(foe, DEF, -1 - 2 * level)

        if "chillDefW" in unitSkills:
            highest_def = units_with_extreme_stat(waiting_team, DEF, find_max=True)
            for foe in highest_def:
                add_debuff(foe, DEF, -7)

        if "chillRes" in unitSkills or "chillResSe" in unitSkills:
            level = max(unitSkills.get("chillRes", 0), unitSkills.get("chillResSe", 0))

            for foe in units_with_extreme_stat(waiting_team, RES):
                add_debuff(foe, RES, -1 - 2 * level)

        if "chillResW" in unitSkills:
            highest_res = units_with_extreme_stat(waiting_team, RES, find_max=True)
            for foe in highest_res:
                add_debuff(foe, RES, -7)

        if "chillAtkSpd" in unitSkills or "chillAtkSpdSe" in unitSkills:
            debuff = max(unitSkills.get("chillAtkSpd", 0), unitSkills.get("chillAtkSpdSe", 0))

            for foe in units_with_extreme_stat_pairing_sum(waiting_team, ATK, SPD):
                add_debuff(foe, ATK, -debuff)
                add_debuff(foe, SPD, -debuff)

        if "chillAtkDef" in unitSkills or "chillAtkDefSe" in unitSkills:
            debuff = max(unitSkills.get("chillAtkDef", 0), unitSkills.get("chillAtkDefSe", 0))

            for foe in units_with_extreme_stat_pairing_sum(waiting_team, ATK, DEF):
                add_debuff(foe, ATK, -debuff)
                add_debuff(foe, DEF, -debuff)

        if "chillAtkRes" in unitSkills or "chillAtkResSe" in unitSkills:
            debuff = max(unitSkills.get("chillAtkRes", 0), unitSkills.get("chillAtkResSe", 0))

            for foe in units_with_extreme_stat_pairing_sum(waiting_team, ATK, RES):
                add_debuff(foe, ATK, -debuff)
                add_debuff(foe, RES, -debuff)

                if debuff == 6:
                    for ally in allies_within_n(foe, 2):
                        add_debuff(ally, ATK, -debuff)
                        add_debuff(ally, RES, -debuff)

        if "chillSpdDef" in unitSkills or "chillSpdDefSe" in unitSkills:
            debuff = max(unitSkills.get("chillSpdDef", 0), unitSkills.get("chillSpdDefSe", 0))

            for foe in units_with_extreme_stat_pairing_sum(waiting_team, SPD, DEF):
                add_debuff(foe, SPD, -debuff)
                add_debuff(foe, DEF, -debuff)

        if "chillSpdRes" in unitSkills or "chillSpdResSe" in unitSkills:
            debuff = max(unitSkills.get("chillSpdRes", 0), unitSkills.get("chillSpdResSe", 0))

            for foe in units_with_extreme_stat_pairing_sum(waiting_team, SPD, RES):
                add_debuff(foe, SPD, -debuff)
                add_debuff(foe, RES, -debuff)

                if debuff == 6:
                    for ally in allies_within_n(foe, 2):
                        add_debuff(ally, SPD, -debuff)
                        add_debuff(ally, RES, -debuff)

        if "chillDefRes" in unitSkills or "chillDefResSe" in unitSkills:
            debuff = max(unitSkills.get("chillDefRes", 0), unitSkills.get("chillDefResSe", 0))

            for foe in units_with_extreme_stat_pairing_sum(waiting_team, DEF, RES):
                add_debuff(foe, DEF, -debuff)
                add_debuff(foe, RES, -debuff)

                if debuff == 6:
                    for ally in allies_within_n(foe, 2):
                        add_debuff(ally, DEF, -debuff)
                        add_debuff(ally, RES, -debuff)

        if "gunterChill" in unitSkills:
            lowest_spd = units_with_extreme_stat(waiting_team, SPD, find_max=False)
            for foe in lowest_spd:
                add_debuff(foe, ATK, -5)
                add_debuff(foe, DEF, -5)

        if "kumadeChill" in unitSkills:
            for foe in units_with_extreme_stat(waiting_team, DEF):
                add_debuff(foe, ATK, -unitSkills["kumadeChill"])
                add_debuff(foe, SPD, -unitSkills["kumadeChill"])

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

        if "hikamiThreaten" in unitSkills:
            for foe in nearest_foes_within_n(unit, 4):
                add_debuff(foe, ATK, -4)
                add_debuff(foe, SPD, -4)
                add_debuff(foe, DEF, -4)
                add_debuff(foe, RES, -4)

        if "hikamiThreaten2" in unitSkills:
            for foe in nearest_foes_within_n(unit, 4):
                add_debuff(foe, ATK, -6)
                add_debuff(foe, SPD, -6)
                add_debuff(foe, DEF, -6)
                add_debuff(foe, RES, -6)

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

        if "timesPulseSk" in unitSkills and (turn-1) % (4 - unitSkills["timesPulseSk"]) == 0 and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        if "timesPulseSe" in unitSkills and (turn-1) % (4 - unitSkills["timesPulseSe"]) == 0 and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        if "timePulseEcho" in unitSkills and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # Turn 1 Pulse
        if "turn1Pulse" in unitSkills and turn == 1:
            sp_charges[unit] += unitSkills["turn1Pulse"]

        if "turn1PulseD" in unitSkills and turn == 1 and unit.getSpecialType() == "Defense": # Defensive Specials Only
            sp_charges[unit] += unitSkills["turn1PulseD"]

        if "infantryPulse" in unitSkills and turn == 1:
            for ally in starting_team:
                if unit.HPcur - (7 - (2 * unitSkills["infantryPulse"])) > ally.HPcur and ally.move == 0 and ally != unit:
                    sp_charges[ally] += 1

        if "infPulse4" in unitSkills:
            for ally in starting_team:
                if ally != unit and ally.visible_stats[HP] < unit.visible_stats[HP]:
                    sp_charges[ally] += 1

        # Pulse Up
        if "pulseUp" in unitSkills:
            sp_charges[unit] += 1

        # Pulse Tie
        if "oddPulseTie" in unitSkills and turn % 2 == 1:
            valid_foes = []

            for foe in waiting_team:
                if foe.HPcur + (7 - (2 * unitSkills["oddPulseTie"])) <= unit.HPcur and foe.specialCount == 0:
                    if not valid_foes or valid_foes[0].HPcur == foe.HPcur:
                        valid_foes.append(foe)
                    elif valid_foes[0].HPcur > foe.HPcur:
                        valid_foes = [foe]

            for foe in valid_foes:
                sp_charges[foe] -= 2

        if "evenPulseTie" in unitSkills and turn % 2 == 0:
            valid_foes = []

            for foe in waiting_team:
                if foe.HPcur + (7 - (2 * unitSkills["evenPulseTie"])) <= unit.HPcur and foe.specialCount == 0:
                    if not valid_foes or valid_foes[0].HPcur == foe.HPcur:
                        valid_foes.append(foe)
                    elif valid_foes[0].HPcur > foe.HPcur:
                        valid_foes = [foe]

            for foe in valid_foes:
                sp_charges[foe] -= 2

        # PRF Pulse
        if "rafielPulse" in unitSkills and turn == 1:
            for ally in starting_team:
                if unit.isSupportOf(ally):
                    sp_charges[ally] += 1

        if ("velouriaPulse" in unitSkills or "velouriaPulse2" in unitSkills) and turn == 1:
            sp_charges[unit] += 2

            for ally in starting_team:
                if unit.isSupportOf(ally):
                    sp_charges[ally] += 2

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

        if "reginnPulse" in unitSkills and turn == 4:
            sp_charges[unit] += 3

        if "nyReginnBoost" in unitSkills and (turn == 1 or turn == 4):
            sp_charges[unit] += 3

        # WAVE SKILLS
        if "oddAtkWave" in unitSkills and turn % 2 == 1:
            add_buff(unit, ATK, unitSkills["oddAtkWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["oddAtkWave"])

        if "oddAtkWaveSe" in unitSkills and turn % 2 == 1:
            add_buff(unit, ATK, unitSkills["oddAtkWaveSe"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["oddAtkWaveSe"])

        if "evenAtkWave" in unitSkills and turn % 2 == 0:
            add_buff(unit, ATK, unitSkills["evenAtkWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["evenAtkWave"])

        if "evenAtkWaveSe" in unitSkills and turn % 2 == 0:
            add_buff(unit, ATK, unitSkills["evenAtkWaveSe"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["evenAtkWaveSe"])

        if "oddSpdWave" in unitSkills and turn % 2 == 1:
            add_buff(unit, SPD, unitSkills["oddSpdWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, unitSkills["oddSpdWave"])

        if "oddSpdWaveSe" in unitSkills and turn % 2 == 1:
            add_buff(unit, SPD, unitSkills["oddSpdWaveSe"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, unitSkills["oddSpdWaveSe"])

        if "evenSpdWave" in unitSkills and turn % 2 == 0:
            add_buff(unit, SPD, unitSkills["evenSpdWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, unitSkills["evenSpdWave"])

        if "evenSpdWaveSe" in unitSkills and turn % 2 == 0:
            add_buff(unit, SPD, unitSkills["evenSpdWaveSe"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, unitSkills["evenSpdWaveSe"])

        if "oddDefWave" in unitSkills and turn % 2 == 1:
            add_buff(unit, DEF, unitSkills["oddDefWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, unitSkills["oddDefWave"])

        if "oddDefWaveSe" in unitSkills and turn % 2 == 1:
            add_buff(unit, DEF, unitSkills["oddDefWaveSe"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, unitSkills["oddDefWaveSe"])

        if "evenDefWave" in unitSkills and turn % 2 == 0:
            add_buff(unit, DEF, unitSkills["evenDefWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, unitSkills["evenDefWave"])

        if "evenDefWaveSe" in unitSkills and turn % 2 == 0:
            add_buff(unit, DEF, unitSkills["evenDefWaveSe"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, unitSkills["evenDefWaveSe"])

        if "oddResWave" in unitSkills and turn % 2 == 0:
            add_buff(unit, RES, unitSkills["oddResWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, RES, unitSkills["oddResWave"])

        if "oddResWaveSe" in unitSkills and turn % 2 == 0:
            add_buff(unit, RES, unitSkills["oddResWaveSe"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, RES, unitSkills["oddResWaveSe"])

        if "evenResWave" in unitSkills and turn % 2 == 0:
            add_buff(unit, RES, unitSkills["evenResWave"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, RES, unitSkills["evenResWave"])

        if "evenResWaveSe" in unitSkills and turn % 2 == 0:
            add_buff(unit, RES, unitSkills["evenResWaveSe"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, RES, unitSkills["evenResWaveSe"])

        if "evenAtkWaveW" in unitSkills and turn % 2 == 0:
            add_buff(unit, ATK, unitSkills["evenAtkWaveW"])
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, ATK, unitSkills["evenAtkWaveW"])

        # Tier 4 Wave Skills
        if "premiumAtkWave" in unitSkills:
            add_buff(unit, ATK, 6)
            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)

        if "premiumSpdWave" in unitSkills:
            add_buff(unit, SPD, 6)
            for ally in allies_within_n_spaces[2]:
                add_buff(ally, SPD, 6)

        if "premiumDefWave" in unitSkills:
            add_buff(unit, DEF, 6)
            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)

        if "premiumResWave" in unitSkills:
            add_buff(unit, RES, 6)
            for ally in allies_within_n_spaces[2]:
                add_buff(ally, RES, 6)

        # SABOTAGE SKILLS
        if "sabotageAtk" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    unit_res = unit.get_visible_stat(RES)
                    foe_res = foe.get_visible_stat(RES)

                    if "phantomRes" in unit.getSkills():
                        unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills():
                        foe_res += foe.getSkills()["phantomRes"]

                    if foe_res <= unit_res - 3:
                        add_debuff(foe, ATK, -unitSkills["sabotageAtk"])

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

        if "sabotageSpd" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res <= unit_res - 3:
                        add_debuff(foe, SPD, -unitSkills["sabotageSpd"])

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

        if "sabotageDef" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    unit_res = unit.get_visible_stat(RES)
                    foe_res = foe.get_visible_stat(RES)

                    if "phantomRes" in unit.getSkills(): unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills(): foe_res += foe.getSkills()["phantomRes"]

                    if foe_res <= unit_res - 3:
                        add_debuff(foe, DEF, -unitSkills["sabotageDef"])

        if "sabotageDefW" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res <= unit_res - 3:
                        add_debuff(foe, DEF, -unitSkills["sabotageDefW"])

        if "sabotageRes" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    unit_res = unit.get_visible_stat(RES)
                    foe_res = foe.get_visible_stat(RES)

                    if "phantomRes" in unit.getSkills():
                        unit_res += unit.getSkills()["phantomRes"]
                    if "phantomRes" in foe.getSkills():
                        foe_res += foe.getSkills()["phantomRes"]

                    if foe_res <= unit_res - 3:
                        add_debuff(foe, RES, -unitSkills["sabotageRes"])

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

        if "sabotageAtkDef" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    if foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) < unit.get_visible_stat(RES) + unit.get_phantom_stat(RES):
                        add_debuff(foe, ATK, -6)
                        add_debuff(foe, DEF, -6)

        if "sabotageAtkRes" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    if foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) < unit.get_visible_stat(RES) + unit.get_phantom_stat(RES):
                        add_debuff(foe, ATK, -6)
                        add_debuff(foe, RES, -6)

        if "sabotageSpdRes" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    if foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) < unit.get_visible_stat(RES) + unit.get_phantom_stat(RES):
                        add_debuff(foe, SPD, -6)
                        add_debuff(foe, RES, -6)

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

        # Yune's Whispers - BR!Micaiah
        if "micaiahSabotage" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -6)
                        add_debuff(foe, SPD, -6)


        # DISCORD SKILLS
        if "atkResDiscord" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in waiting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -6)
                        add_debuff(foe, RES, -6)
                        add_status(foe, Status.Discord)

        if "spdResDiscord" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in waiting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, SPD, -6)
                        add_debuff(foe, RES, -6)
                        add_status(foe, Status.Discord)

        if "defResDiscord" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in waiting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, DEF, -6)
                        add_debuff(foe, RES, -6)
                        add_status(foe, Status.Discord)

        if "dazzlingDiscord" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in nearest_foes_within_n(unit, 5):
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_status(foe, Status.Discord)

                    for ally in allies_within_n(foe, 2):
                        foe_ally_res = ally.get_visible_stat(RES) + ally.get_phantom_stat(RES)

                        if foe_ally_res < unit_res:
                            add_status(ally, Status.Discord)

        # HAVOC SKILLS
        if "atkResHavoc" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in waiting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -7)
                        add_debuff(foe, RES, -7)
                        add_status(foe, Status.Sabotage)
                        add_status(foe, Status.Schism)

        # OPENING SKILLS
        if "atkOpening" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, ATK, exclude=unit):
                add_buff(ally, ATK, unitSkills["atkOpening"])

        if "atkOpeningSe" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, ATK, exclude=unit):
                add_buff(ally, ATK, unitSkills["atkOpeningSe"])

        if "spdOpening" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, SPD, exclude=unit):
                add_buff(ally, SPD, unitSkills["spdOpening"])

        if "spdOpeningSe" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, SPD, exclude=unit):
                add_buff(ally, SPD, unitSkills["spdOpeningSe"])

        if "defOpening" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, DEF, exclude=unit):
                add_buff(ally, DEF, unitSkills["defOpening"])

        if "defOpeningSe" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, DEF, exclude=unit):
                add_buff(ally, DEF, unitSkills["defOpeningSe"])

        if "resOpening" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, RES, exclude=unit):
                add_buff(ally, RES, unitSkills["resOpening"])

        if "resOpeningSe" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, RES, exclude=unit):
                add_buff(ally, RES, unitSkills["resOpeningSe"])

        # GAP SKILLS
        if "atkSpdGap" in unitSkills:
            for ally in units_with_extreme_stat_pairing_sum(starting_team, ATK, SPD, exclude=unit):
                add_buff(ally, ATK, unitSkills["atkSpdGap"])
                add_buff(ally, SPD, unitSkills["atkSpdGap"])

        if "atkDefGap" in unitSkills:
            for ally in units_with_extreme_stat_pairing_sum(starting_team, ATK, DEF, exclude=unit):
                add_buff(ally, ATK, unitSkills["atkDefGap"])
                add_buff(ally, DEF, unitSkills["atkDefGap"])

        if "atkResGap" in unitSkills:
            for ally in units_with_extreme_stat_pairing_sum(starting_team, ATK, RES, exclude=unit):
                add_buff(ally, ATK, unitSkills["atkResGap"])
                add_buff(ally, RES, unitSkills["atkResGap"])

        if "spdDefGap" in unitSkills:
            for ally in units_with_extreme_stat_pairing_sum(starting_team, SPD, DEF, exclude=unit):
                add_buff(ally, SPD, unitSkills["spdDefGap"])
                add_buff(ally, DEF, unitSkills["spdDefGap"])

        if "spdResGap" in unitSkills:
            for ally in units_with_extreme_stat_pairing_sum(starting_team, SPD, RES, exclude=unit):
                add_buff(ally, SPD, unitSkills["spdResGap"])
                add_buff(ally, RES, unitSkills["spdResGap"])

        if "defResGap" in unitSkills:
            for ally in units_with_extreme_stat_pairing_sum(starting_team, DEF, RES, exclude=unit):
                add_buff(ally, DEF, unitSkills["defResGap"])
                add_buff(ally, RES, unitSkills["defResGap"])

        # OATH
        if "atkOath" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, ATK, unitSkills["atkOath"])
        if "spdOath" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, SPD, unitSkills["spdOath"])
        if "defOath" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, DEF, unitSkills["defOath"])
        if "resOath" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, RES, unitSkills["resOath"])

        if "atkOathSe" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, ATK, unitSkills["atkOathSe"])
        if "spdOathSe" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, SPD, unitSkills["spdOathSe"])
        if "defOathSe" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, DEF, unitSkills["defOathSe"])
        if "resOathSe" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, RES, unitSkills["resOathSe"])

        if "atkSpdOath" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Orders)

        if "atkSpdPledge" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.SpecialCharge)

        if "atkDefOath" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.Orders)

        if "atkResOath" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Orders)

        if "defResOath" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Orders)

        if "defResPledge" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.SpecialCharge)

        if "atkOathEcho" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_status(unit, Status.Orders)

        # ROUSE
        if "atkRouse" in unitSkills and not allies_within_n_spaces[1]:
            add_buff(unit, ATK, unitSkills["atkRouse"])
        if "spdRouse" in unitSkills and not allies_within_n_spaces[1]:
            add_buff(unit, SPD, unitSkills["spdRouse"])
        if "defRouse" in unitSkills and not allies_within_n_spaces[1]:
            add_buff(unit, DEF, unitSkills["defRouse"])
        if "resRouse" in unitSkills and not allies_within_n_spaces[1]:
            add_buff(unit, RES, unitSkills["resRouse"])

        if "atkRouseSe" in unitSkills and not allies_within_n_spaces[1]:
            add_buff(unit, ATK, unitSkills["atkRouseSe"])
        if "spdRouseSe" in unitSkills and not allies_within_n_spaces[1]:
            add_buff(unit, SPD, unitSkills["spdRouseSe"])
        if "defRouseSe" in unitSkills and not allies_within_n_spaces[1]:
            add_buff(unit, DEF, unitSkills["defRouseSe"])
        if "resRouseSe" in unitSkills and not allies_within_n_spaces[1]:
            add_buff(unit, RES, unitSkills["resRouseSe"])

        if "nullPanicRouse" in unitSkills and not allies_within_n_spaces[1]:
            add_status(unit, Status.NullPanic)

        if "alarmAtkSpd" in unitSkills and len(allies_within_n_spaces[1]) <= 2:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Canto1)

        if "alarmAtkDef" in unitSkills and len(allies_within_n_spaces[1]) <= 2:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.Canto1)

        if "alarmSpdDef" in unitSkills and len(allies_within_n_spaces[1]) <= 2:
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.Canto1)

        if "alarmDefRes" in unitSkills and len(allies_within_n_spaces[1]) <= 2:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Canto1)

        if "inciteAtkSpd" in unitSkills and len(allies_within_n_spaces[1]) <= 2:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Incited)

        if "inciteAtkRes" in unitSkills and len(allies_within_n_spaces[1]) <= 2:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Incited)

        if "inciteSpdDef" in unitSkills and len(allies_within_n_spaces[1]) <= 2:
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.Incited)

        # REIN SNAP
        if "reinSnap" in unitSkills and "refresh" not in unitSkills:
            cond = False

            for ally in allies_within_n_spaces[2]:
                if ally.move == 3 or (ally.move == 0 and ally.wpnType in MELEE_WEAPONS):
                    cond = True
                    add_status(ally, Status.MobilityUp)

            if cond: add_status(unit, Status.MobilityUp)

        # RECOVERY
        if "odd_recovery" in unitSkills and turn % 2 == 1:
            for ally in allies_within_n(unit, 2):
                clear_penalty_statuses.append(ally)
                clear_penalty_stats.append(ally)

        if "even_recovery" in unitSkills and turn % 2 == 0:
            for ally in allies_within_n(unit, 2):
                clear_penalty_statuses.append(ally)
                clear_penalty_stats.append(ally)

        # STATUSES
        if "armorMarch" in unitSkills or "armorMarchSe" in unitSkills:
            skill_lvl = max(unitSkills.get("armorMarch", 0), unitSkills.get("armorMarchSe", 0))

            if unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * skill_lvl:
                ally_cond = False

                for ally in allies_within_n_spaces[1]:
                    if ally.move == 3:
                        add_status(ally, Status.MobilityUp)
                        ally_cond = True

                if ally_cond:
                    add_status(unit, Status.MobilityUp)

        if "armorStride" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["armorStride"] and not allies_within_n_spaces[1]:
            add_status(unit, Status.MobilityUp)

        if "armoredBoots" in unitSkills and unit.HPcur == unit.visible_stats[HP]:
            add_status(unit, Status.MobilityUp)

        if "odd_tempest" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["odd_tempest"] and turn % 2 == 1:
            add_status(unit, Status.MobilityUp)

        if "odd_tempestSe" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["odd_tempestSe"] and turn % 2 == 1:
            add_status(unit, Status.MobilityUp)

        if "even_tempest" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["even_tempest"] and turn % 2 == 0:
            add_status(unit, Status.MobilityUp)

        if "even_tempestSe" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["even_tempestSe"] and turn % 2 == 0:
            add_status(unit, Status.MobilityUp)

        if "endlessTempest" in unitSkills:
            add_status(unit, Status.MobilityUp)

        if "brutalTempest" in unitSkills:
            add_status(unit, Status.MobilityUp)

        if "air_orders" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["air_orders"]:
            for ally in allies_within_n_spaces[1]:
                if ally.move == 2:
                    add_status(ally, Status.Orders)

        if "air_ordersSe" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["air_ordersSe"]:
            for ally in allies_within_n_spaces[1]:
                if ally.move == 2:
                    add_status(ally, Status.Orders)

        if "air_orders4" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Orders)
            add_status(unit, Status.Charge)

            for ally in allies_within_n_spaces[2]:
                if ally.move == 2:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    add_status(ally, Status.Orders)
                    add_status(ally, Status.Charge)

        if "ground_orders" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["ground_orders"]:
            for ally in allies_within_n_spaces[1]:
                if ally.move != 2:
                    add_status(ally, Status.Orders)

        if "ground_ordersSe" in unitSkills and unit.HPcur / unit.visible_stats[HP] >= 1.5 - 0.5 * unitSkills["ground_ordersSe"]:
            for ally in allies_within_n_spaces[1]:
                if ally.move != 2:
                    add_status(ally, Status.Orders)

        if "hexbladeSkill" in unitSkills:
            magic_cond = False

            for ally in allies_within_n_spaces[2]:
                if ally.wpnType in TOME_WEAPONS:
                    magic_cond = True
                    break

            if magic_cond:
                add_status(unit, Status.Hexblade)

        if "flierBeastA" in unitSkills and unit.transformed:
            add_status(unit, Status.MobilityUp)

        if "assaultTroop" in unitSkills or "assaultTroopSe" in unitSkills:
            skill_lvl = max(unitSkills.get("assaultTroop", 0), unitSkills.get("assaultTroopSe", 0))

            if skill_lvl == 1:
                cond = foes_within_n_cardinal(unit, 1)
            elif skill_lvl == 2:
                cond = foes_within_n_cardinal(unit, 3)
            elif skill_lvl == 3:
                cond = bool(foes_within_n_cardinal(unit, 3) or unitHPEqual100Percent)
            else:
                cond = False

            if cond:
                add_status(unit, Status.Charge)

        if "assaultRush" in unitSkills and (foes_within_n_cardinal(unit, 3) or unitHPEqual100Percent):
            add_buff(unit, ATK, 6)
            add_status(unit, Status.Charge)
            add_status(unit, Status.MobilityUp)

        if "infNullFollow" in unitSkills:
            if unitSkills["infNullFollow"] == 1 and unitHPGreaterEqual50Percent:
                ally_group = allies_within_n_spaces[1]
            elif unitSkills["infNullFollow"] == 2:
                ally_group = allies_within_n_spaces[1]
            elif unitSkills["infNullFollow"] == 3:
                ally_group = allies_within_n_spaces[2]
            else:
                ally_group = []

            for ally in ally_group:
                add_status(ally, Status.NullFollowUp)

        if "INFU4" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.NullFollowUp)
            add_status(unit, Status.Orders)

        # GREAT TALENT
        if "speedtaker" in unitSkills:
            add_great_talent(unit, SPD, 1, unitSkills["speedtaker"])

        # INHERITABLE/SEASONAL WEAPONS
        if "lionBoost" in unitSkills:
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, RES, 6)

        if "rapportOpening" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, SPD, exclude=unit):
                add_buff(ally, ATK, unitSkills["rapportOpening"])
                add_buff(ally, DEF, unitSkills["rapportOpening"])

        if "joyousStat" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, ATK, exclude=unit):
                add_buff(ally, DEF, unitSkills["joyousStat"])
                add_buff(ally, RES, unitSkills["joyousStat"])

        # Ardent Service/Fresh Bouquet
        if "bridalSpdBonus" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, SPD, 4)
            for ally in allies_within_n_spaces[1]:
                add_buff(ally, SPD, 4)

        # Grandscratcher
        if "highAtkCharge" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, ATK, exclude=unit):
                sp_charges[ally] += 1

        # Trident
        if "summerAllyAtk" in unitSkills and allies_within_n_spaces[3]:
            add_buff(unit, ATK, 6)

        # Shellpoint Lance
        if "summerAllyDef" in unitSkills and allies_within_n_spaces[3]:
            add_buff(unit, DEF, 6)

        if "lanternTome" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.TraverseTerrain)
            add_status(unit, Status.SpecialCharge)

        # Sunlight/Seaside Parasol
        if "sunlight" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_status(foe, Status.Guard)

                for ally in allies_within_n(foe, 2):
                    if "nearSavior" in ally.getSkills() or "farSavior" in ally.getSkills():
                        add_status(ally, Status.Guard)

        # Whitewind Bow, Lucrative Bow/Dagger
        if "whitewindBow" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.NullFollowUp)
            add_status(unit, Status.NullPanic)

        # Farmer's Tool, Doubler Sword/Lance/Bow
        if "doublerBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, DEF, 6)

        # Pumpkin Stem
        if "doublerBoostRes" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)

        # Nabata Lance / Hexblade Weapons
        if "hexbladeWeapon" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.Hexblade)
            add_status(unit, Status.TraverseTerrain)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.Hexblade)
                add_status(ally, Status.TraverseTerrain)

        # Nabata Beacon
        if "nabataBeacon" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.Desperation)
            add_status(unit, Status.TraverseTerrain)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.Desperation)
                add_status(ally, Status.TraverseTerrain)

        # Carrot Bow
        if "carrotBow" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                if foe.get_visible_stat(DEF) + foe.get_phantom_stat(DEF) < unit.get_visible_stat(DEF) + unit.get_phantom_stat(DEF) + 5:
                    add_debuff(unit, ATK, 7)
                    add_debuff(unit, RES, 7)
                    add_status(foe, Status.Discord)

        # Sea Tambourine
        if "seaTembourine" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)

        # Tropical Conch
        if "tropicalConch" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, DEF, 6)

        # Devoted Cup
        if "devotedCup" in unitSkills:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Discord)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Discord)

        # Crab Tomes
        if "giantEnemyCrab" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_status(unit, Status.Pursual)

        # THE UNIQUE SKILL STUFF

        # Shining Emblem - L!Marth
        if "Shining Emblem" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)

        # The Fire Emblem - FE!Marth
        if "THE Fire Emblem" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, OMNI, 7)
            add_status(unit, Status.NullPanic)
            add_status(unit, Status.FireEmblem)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, OMNI, 7)
                add_status(ally, Status.NullPanic)
                add_status(ally, Status.FireEmblem)

        # Wing-Lifted Spear (Refine Eff) - L!Caeda
        if "LCaedaRefineEffect" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.SpecialCharge)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.SpecialCharge)
                add_status(ally, Status.NullPenalties)

        # Pure-Wing Spear - X!Caeda
        if "pureWing" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Orders)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Orders)

        # Celestial Globe (Base) - DE!Linde
        if "deLindeBoost" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.TraverseTerrain)
            add_status(unit, Status.NullFollowUp)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.TraverseTerrain)
                add_status(ally, Status.NullFollowUp)

        # Lightburst Tome - Arlen
        if "arlenBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.TraverseTerrain)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_buff(ally, DEF, 6)
                add_status(ally, Status.TraverseTerrain)

        # Eagle's Egg (Refine Eff) - SP!Est
        if "EST BEST TIME ZONE" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, DEF, -6)
                add_debuff(foe, RES, -6)
                add_status(foe, Status.Exposure)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, DEF, -6)
                    add_debuff(ally, RES, -6)
                    add_status(ally, Status.Exposure)

        # Dragoon's Axe (Refine Eff) - CH!Minerva
        if "I think I'm starting to lose it" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.SpecialCharge)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.SpecialCharge)

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

        # Martyr's Staff - FA!Lena
        if "martyrsStaff" in unitSkills and allies_within_n_spaces[3]:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.BonusDoubler)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n_spaces[3]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.BonusDoubler)
                add_status(ally, Status.NullPenalties)

        # With Everyone!
        if "Friends!!!" in unitSkills and allies_within_n_spaces[1]:
            add_buff(unit, DEF, 5)
            add_buff(unit, RES, 5)

            for ally in allies_within_n_spaces[1]:
                add_buff(ally, DEF, 5)
                add_buff(ally, RES, 5)

        # With Everyone! II - L!Y!Tiki/H!Y!Tiki
        if "I love you, and all you guys!" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)

        # Solitary Dream - FA!Y!Tiki
        if "solitaryDream" in unitSkills and all([ally.wpnType in DRAGON_WEAPONS for ally in allies_within_n(unit, 1)]):
            add_buff(unit, ATK, 4)
            add_buff(unit, SPD, 4)
            add_buff(unit, DEF, 4)
            add_buff(unit, RES, 4)

        # Frostfire Breath (Refine Eff) - H!Y!Tiki
        if "frostfire" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.BonusDoubler)
            add_status(unit, Status.NullPanic)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.BonusDoubler)
                add_status(ally, Status.NullPanic)

        # Ancient Voice - Dragon Tiki
        if "yyTikiBoost" in unitSkills and allies_within_n(unit, 2):
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.Bulwark)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, SPD, 6)
                add_buff(ally, DEF, 6)
                add_status(ally, Status.Bulwark)
                add_status(ally, Status.NullPenalties)

        if "mercuriusBuff" in unitSkills and unitHPGreaterEqual50Percent:
            add_buff(unit, OMNI, 4)

            for ally in allies_within_n_spaces[2]:
                if ally.wpnType in PHYSICAL_WEAPONS:
                    add_buff(ally, OMNI, 4)

        if "mercuriusMegabuff" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, OMNI, 6)

            for ally in allies_within_n_spaces[2]:
                if ally.wpnType in PHYSICAL_WEAPONS:
                    add_buff(ally, OMNI, 6)

        # Coyote's Lance (Base) - Hardin
        if "CH 6P > 236S > RC > 66 > [5D] > c.S > 66 > !S > 5H > 236H > WS > 6H" in unitSkills and allies_within_n_spaces[3]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Pursual)

            for ally in allies_within_n_spaces[3]:
                if ally.move == 1:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    add_status(ally, Status.Pursual)

        # Swirling Scimitar - DE!Malice
        if ("deMaliceBoost" in unitSkills or "jehannaBoost" in unitSkills) and allies_within_n(unit, 2):
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Dodge)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Dodge)
                add_status(ally, Status.NullPenalties)

        # Jokers Wild (Base) - H!Xane
        if "xaneStuff!" in unitSkills:
            for ally in allies_within_n_spaces[3]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.Hexblade)
                add_status(ally, Status.NullPanic)

        # Ancient Trickery - Dragon Xane
        if "xanerific" in unitSkills:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Sabotage)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Sabotage)

        # Brilliant Starlight (Base) - Gotoh
        if "gotohBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.AOEReduce80Percent)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.AOEReduce80Percent)

        # Fundament - Dragon Gotoh
        if "fundies" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.AOEReduce80Percent)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.AOEReduce80Percent)
                add_status(ally, Status.NullBonuses)

        # Gift of Guidance - Dragon Gotoh
        if "giftOGuidance" in unitSkills and unitHPGreaterEqual25Percent:
            sp_charges[unit] += 2

            for ally in allies_within_n_spaces[2]:
                sp_charges[unit] += 1

                if ally.wpnType in TOME_WEAPONS or ally.wpnType == "Staff":
                    sp_charges[unit] += 1

        # Divine Fang(+) - Naga
        if "grantEffDragon" in unitSkills:
            for ally in allies_within_n(unit, 1):
                add_status(ally, Status.EffDragons)

        if "divineFangPlus" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Pursual)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Pursual)

        # Ancient Majesty - Dragon Naga
        if "nagaaaaa" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Frozen)
                add_status(foe, Status.Guard)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Frozen)
                    add_status(ally, Status.Guard)

        # Divine God Fang - Dragon Naga
        if "divineGodFang" in unitSkills and allies_within_n(unit, 2):
            add_status(unit, Status.EffDragons)
            add_status(unit, Status.NullEffDragons)
            add_status(unit, Status.Empathy)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.EffDragons)
                add_status(ally, Status.NullEffDragons)
                add_status(ally, Status.Empathy)

        # Shadow Breath (Base) - Medeus
        if "medeusBoost" in unitSkills:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.EnGarde)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.EnGarde)

        # Ancient Betrayal - Dragon Medeus
        if "dragonMedeusBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.EnGarde)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.EnGarde)
                add_status(ally, Status.NullBonuses)

        # Opposing Stones - H!Nagi
        if "hNagiBoost" in unitSkills and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # True-Bond Bow - X!Alm
        if "xAlmBoost" in unitSkills and allies_within_n_spaces[2]:
            add_great_talent(unit, ATK, 2, 10)
            add_great_talent(unit, SPD, 2, 10)

            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 2

            if unit.specialCount == unit.specialMax - 1:
                sp_charges[unit] += 1

            for ally in allies_within_n_spaces[2]:
                add_great_talent(ally, ATK, 2, 10)
                add_great_talent(ally, SPD, 2, 10)

                if ally.specialCount == ally.specialMax:
                    sp_charges[ally] += 2

                if ally.specialCount == ally.specialMax - 1:
                    sp_charges[ally] += 1

        # Worldly Lance - Mycen
        if "mycenBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.NullBonuses)

        # Saintly Seraphim (Refine Eff) - L!Celica
        if "Garfield 2025" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.SpecialCharge)

            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 1

        # Wedding-Bell Axe (Base) - BR!Catria
        if "weddingBellAxe" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.Orders)
            add_status(unit, Status.TriangleAttack)

            for ally in allies_within_n_spaces[2]:
                add_status(unit, Status.Orders)
                add_status(ally, Status.TriangleAttack)

        # Beyond Witchery - R!Sonya
        if "beyondWitchery" in unitSkills:
            if turn == 1:
                sp_charges[unit] += 2
            else:
                sp_charges[unit] += 1

        # Proud Spear (Refine Eff) - Fernand
        if "fernandBoost" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Discord)
                add_status(foe, Status.Stall)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Discord)
                    add_status(ally, Status.Stall)

        # Arcane Medusa
        if "arcaneMedusa" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.Anathema)

        # Mounting Fear - Nuibaba
        if "mountingFear" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in waiting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_status(foe, Status.Panic)
                        add_status(foe, Status.Exposure)
                        add_status(foe, Status.DeepWounds)

        # Mila's Turnwheel - Mila
        if "milasTurnwheel" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 1):
                if foe.get_visible_stat(DEF) + foe.get_phantom_stat(DEF) < unit.get_visible_stat(DEF) + unit.get_phantom_stat(DEF):
                    add_status(foe, Status.Isolation)

        if "milasTurnwheelII" in unitSkills:
            add_status(unit, Status.DenyFollowUp)

            for foe in foes_within_n_cardinal(unit, 1):
                if foe.get_visible_stat(DEF) + foe.get_phantom_stat(DEF) < unit.get_visible_stat(DEF) + unit.get_phantom_stat(DEF):
                    add_status(foe, Status.Isolation)
                    add_status(foe, Status.Guard)

        # Holy-Knight Aura - L!Sigurd
        if "holyKnight" in unitSkills:
            add_status(unit, Status.MobilityUp)

        # Holy-Knight II - L!Sigurd
        if "holyKnightII" in unitSkills:
            add_status(unit, Status.MobilityUp)
            add_status(unit, Status.FirstReduce40)

        # Holy-War Spear - E!Sigurd
        if "eSigurdBoost" in unitSkills:
            add_status(unit, Status.Gallop)

        # Sigurd Ring
        if "provide for us" in unitSkills and not(unit.move == 1 and unit.wpnType in RANGED_WEAPONS):
            add_status(unit, Status.MobilityUp)

        # Heir to Light - B!Seliph
        if "heirToLight" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.MobilityUp)
            add_status(unit, Status.NullFollowUp)

        # Spirit Forest Writ (Refine Eff) - L!Deirdre
        if "Jovial Merryment" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.NullPenalties)

            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 1

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.NullPenalties)

                if ally.specialCount == ally.specialMax:
                    sp_charges[ally] += 1

        # Dark Scripture (Base) - FA!Julia
        if "juliaFallenRefine" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                if foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) < unit.get_visible_stat(RES) + unit.get_phantom_stat(RES):
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Sabotage)
                    add_status(foe, Status.DeepWounds)
                    add_status(foe, Status.NullMiracle)

        # Winds of Silesse (Refine Eff) - Ced
        if "cedEffects" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Desperation)
            add_status(unit, Status.SpecialCharge)

        if "ascCedBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            sp_charges[unit] += 1

        # Sword of Isaach - L!Ayra
        if "LAyraBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.PotentFollow)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.PotentFollow)
                add_status(ally, Status.NullBonuses)

        # Larcei's Edge (Refine Eff) - Larcei
        if "infiniteSpecial" in unitSkills and unitHPGreaterEqual25Percent and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # Aerial Longsword (Base) - Annand
        if "annandBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.NullFollowUp)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.NullFollowUp)
                add_status(ally, Status.NullPenalties)

        # Silesse Frost (Refine Eff) - Erinys
        if "stabbitystabbitystabstab" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.SpecialCharge)
            add_status(unit, Status.Dodge)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.SpecialCharge)
                add_status(ally, Status.Dodge)

        # Sparking Tome (Refine Eff) - Azelle
        if "Spark!" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.DamageReductionPierce50)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.DamageReductionPierce50)

        # Thunderer Tome (Base) - Tine
        if "tineBoost" in unitSkills and (turn <= 3 or not unitHPEqual100Percent):
            sp_charges[unit] += 1

        if "evilHildaBoost" in unitSkills and foes_within_n_spaces[4]:
            add_status(unit, Status.Dominance)

            for foe in nearest_foes_within_n(unit, 4):
                add_debuff(foe, ATK, 6)
                add_debuff(foe, RES, 6)

        # Heired Gungnir - Arion
        if "neat" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.Charge)

            for ally in allies_within_n_spaces[2]:
                if ally.move == 2:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, DEF, 6)
                    add_status(ally, Status.Charge)

        # Divine Yewfelle - Brigid
        if "brigidBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Orders)
            add_status(unit, Status.Incited)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Orders)
                add_status(ally, Status.Incited)

        # I Remember... - Brigid
        if "iRememberYou'reNeutrals" in unitSkills and allies_within_n_spaces[2]:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Panic)
                add_status(foe, Status.Sabotage)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Panic)
                    add_status(ally, Status.Sabotage)

        # Rampart Bow - Midir
        if "midirBoost" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Exposure)
                add_status(foe, Status.DeepWounds)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Exposure)
                    add_status(ally, Status.DeepWounds)

        # Diplomacy Staff (Base) - August
        if "diplomacyStaff" in unitSkills:
            for ally in allies_within_n(unit, 20):
                if ally.isSupportOf(unit):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)
                    add_status(unit, Status.Pursual)

                    if ally_defeated:
                        sp_charges[ally] += 2
                        add_status(unit, Status.DenyFollowUp)

        # Grafcalibur (Refine Eff) - Asbel
        if "asbelFollowUp" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Sabotage)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Sabotage)

        # Kia Staff (Base) - Sara
        if "kiaRecovery" in unitSkills:
            penalty_condition = False

            for ally in allies_within_n_spaces[4]:
                if ally.hasPenalty():
                    penalty_condition = True
                    break

            valid_allies = []

            for ally in allies_within_n_spaces[4]:
                if not valid_allies or (ally.HPcur == valid_allies[0].HPcur and (not penalty_condition or ally.hasPenalty())):
                    valid_allies.append(ally)
                elif ally.HPcur < valid_allies[0].HPcur and (not penalty_condition or ally.hasPenalty()):
                    valid_allies = [ally]

            for ally in valid_allies:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                clear_penalty_statuses.append(ally)
                clear_penalty_stats.append(ally)

        # Kia Staff (Refine Eff) - Sara
        if "kiaRecoveryPlus" in unitSkills and allies_within_n_spaces[3]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Hexblade)
            clear_penalty_statuses.append(unit)
            clear_penalty_stats.append(unit)

            for ally in allies_within_n_spaces[3]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Hexblade)
                clear_penalty_statuses.append(ally)
                clear_penalty_stats.append(ally)

        # Tome of Fury (Refine Eff) - Miranda
        if "youRudeCreature" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Hexblade)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.Hexblade)
                add_status(ally, Status.NullBonuses)

        # Thief - Tina
        if "tinaBoost" in unitSkills:
            most_bonuses = []

            for foe in waiting_team:
                if not most_bonuses or len(foe.statusPos) == len(most_bonuses[0].statusPos):
                    most_bonuses.append(foe)
                elif len(foe.statusPos) >= len(most_bonuses[0].statusPos):
                    most_bonuses = [foe]

            if any([Status.Dosage in foe.statusPos for foe in most_bonuses]):
                clear_bonus_statuses.append(unit)
                clear_bonus_stats.append(unit)
            else:
                for foe in most_bonuses:
                    add_buff(unit, ATK, foe.buffs[ATK])
                    add_buff(unit, SPD, foe.buffs[SPD])
                    add_buff(unit, DEF, foe.buffs[DEF])
                    add_buff(unit, RES, foe.buffs[RES])

                    for ally in allies_within_n_spaces[2]:
                        add_buff(ally, ATK, foe.buffs[ATK])
                        add_buff(ally, SPD, foe.buffs[SPD])
                        add_buff(ally, DEF, foe.buffs[DEF])
                        add_buff(ally, RES, foe.buffs[RES])

                    for status in foe.statusPos:
                        add_status(unit, status)

                        for ally in allies_within_n_spaces[2]:
                            add_status(ally, status)

                    clear_bonus_statuses.append(foe)
                    clear_bonus_stats.append(foe)

        # Blade Royale - Perne
        if "perneBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.NullPenalties)

        # Petrify (Base) - Veld
        if "veldPetrify" in unitSkills:
            valid_foes = []

            if turn == 1:
                for foe in waiting_team:
                    if not valid_foes or foe.HPcur == valid_foes[0].HPcur:
                        valid_foes.append(foe)
                    elif foe.HPcur < valid_foes[0].HPcur:
                        valid_foes = [foe]

            if 2 <= turn <= 5:
                valid_foes = units_with_extreme_stat(waiting_team, turn - 1, find_max=False)

            for foe in valid_foes:
                add_debuff(foe, ATK, -7)
                add_debuff(foe, SPD, -7)
                add_status(foe, Status.Gravity)

        # Petrify (Refine Base) - Veld
        if "veldRefinePetrify" in unitSkills:
            valid_foes = []

            if turn == 1:
                for foe in waiting_team:
                    if not valid_foes or foe.HPcur == valid_foes[0].HPcur:
                        valid_foes.append(foe)
                    elif foe.HPcur < valid_foes[0].HPcur:
                        valid_foes = [foe]

            if 2 <= turn <= 5:
                valid_foes = units_with_extreme_stat(waiting_team, turn - 1, find_max=False)

                for foe in valid_foes:
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, SPD, -7)
                    add_status(foe, Status.Gravity)
                    add_status(foe, Status.Sabotage)

                    for ally in allies_within_n(foe, 2):
                        add_debuff(ally, ATK, -7)
                        add_debuff(ally, SPD, -7)
                        add_status(ally, Status.Sabotage)

        # Human Virtue - L!Roy
        if "humanVirtue" in unitSkills:
            condition = False

            for ally in allies_within_n(unit, 1):
                if ally.wpnType not in DRAGON_WEAPONS + BEAST_WEAPONS:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    condition = True

            if condition:
                add_buff(unit, ATK, 6)
                add_buff(unit, SPD, 6)

        if "humanVir2" in unitSkills:
            condition = False

            for ally in allies_within_n(unit, 2):
                if ally.wpnType not in DRAGON_WEAPONS + BEAST_WEAPONS:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    condition = True

            if condition:
                add_buff(unit, ATK, 6)
                add_buff(unit, SPD, 6)

        # Faith in Humanity
        if "faithInHumanity" in unitSkills:
            condition = False

            for ally in allies_within_n(unit, 3):
                if ally.wpnType not in DRAGON_WEAPONS + BEAST_WEAPONS:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    condition = True

            if condition:
                add_buff(unit, ATK, 6)
                add_buff(unit, SPD, 6)

        # Arcane Truthfire
        if "truthfire" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_status(unit, Status.Orders)

        if "lughBuffs" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)

        # Thea
        if "I LOVE MY FLOWERSSSSSSS" in unitSkills and unit.flowers >= 10:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)

        # Vassal-Saint Steel - A!Fir
        if "godSword" in unitSkills and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # Ilian Merc Lance - Noah
        if "insert Xenoblade 3 thingy" in unitSkills and len(allies_within_n_spaces[1]) <= 1:
            add_status(unit, Status.Dodge)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n_spaces[2]:
                if ally.isSupportOf(unit):
                    add_status(ally, Status.Dodge)
                    add_status(ally, Status.NullBonuses)

        # Aureola (Refine Eff) - Guinivere
        if "guinivereStuff" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, SPD, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, SPD, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.NullPenalties)

        # Sandglass Bow - DE!Igrene
        if "deIgreneBoost" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.TraverseTerrain)
            add_status(unit, Status.MobilityUp)

            for ally in allies_within_n_spaces[2]:
                if ally.move == 0 or ally.move == 3:
                    add_status(ally, Status.TraverseTerrain)
                    add_status(ally, Status.MobilityUp)

        # Light of Etruria - Elffin
        if "elffinBoost" in unitSkills:
            add_buff(unit, SPD, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Hexblade)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, SPD, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.Hexblade)

            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Guard)

        # Blade of Sands - DE!Juno
        if "bladeofsans" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.BonusDoubler)
            add_status(unit, Status.NullPanic)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, SPD, 6)
                add_buff(ally, DEF, 6)
                add_status(ally, Status.BonusDoubler)
                add_status(ally, Status.NullPanic)

        # Ilian Frost Blade - FF!Thea
        if "iceTheaBoost" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.TriangleAttack)
            add_status(unit, Status.Canto1)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.TriangleAttack)
                add_status(ally, Status.Canto1)

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

        # Staff of the Saint - Elimine
        if "FREYR WHERE YOU AT?" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)

            for foe in foes_within_n_cardinal(unit, 1):
                if foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) < unit.get_visible_stat(RES) + unit.get_phantom_stat(RES):
                    add_status(unit, Status.FalseStart)

        if "the BONUS she gives in mario kart DOUBLE dash" in unitSkills:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.BonusDoubler)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.BonusDoubler)

            for foe in foes_within_n_cardinal(unit, 1):
                if foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) < unit.get_visible_stat(RES) + unit.get_phantom_stat(RES):
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, RES, -7)
                    add_status(unit, Status.FalseStart)

        # Ardent Durandal - L!Eliwood
        if "bonus4you" in unitSkills:
            for ally in units_with_extreme_stat(starting_team, ATK, exclude=unit):
                add_status(ally, Status.BonusDoubler)

        # Vision of Arcadia - L!Eliwood
        if "visionOfArcadia" in unitSkills:
            condition = False

            for ally in starting_team:
                if ally != unit and ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS:
                    condition = True

            if condition:
                for ally in units_with_extreme_stat(starting_team, ATK, exclude=unit):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, DEF, 6)

        # Vision of Arcadia II
        if "visionOfArcadiaPlus" in unitSkills:
            condition = False

            for ally in starting_team:
                if ally != unit and ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS:
                    condition = True

            if condition:
                add_buff(unit, ATK, 6)
                add_buff(unit, SPD, 6)
                add_buff(unit, DEF, 6)
                add_status(unit, Status.NullPanic)
                add_status(unit, Status.Canto1)

                for ally in units_with_extreme_stat(starting_team, ATK, exclude=unit):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    add_buff(ally, DEF, 6)
                    add_status(ally, Status.NullPanic)
                    add_status(ally, Status.Canto1)

        # Inborn Idealism - CH!Eliwood
        if "inbornIdealism" in unitSkills:
            condition = False

            for ally in starting_team:
                if ally != unit and ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS:
                    condition = True

            if condition:
                add_buff(unit, ATK, 6)
                add_buff(unit, SPD, 6)
                add_buff(unit, DEF, 6)
                add_status(unit, Status.NullPanic)
                add_status(unit, Status.BonusDoubler)

                for ally in units_with_extreme_stat(starting_team, ATK, exclude=unit):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    add_buff(ally, DEF, 6)
                    add_status(ally, Status.NullPanic)
                    add_status(ally, Status.BonusDoubler)

        # Lady's Bow - E!Lyn
        if "eLynBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Desperation)
            add_status(unit, Status.PreemptPulse)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Desperation)
                add_status(ally, Status.PreemptPulse)

        # Fellowship Blade - X!Hector
        if "xHectorBoost" in unitSkills and allies_within_n(unit, 2):
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.NullPanic)
            add_status(unit, Status.Bulwark)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.NullPanic)
                add_status(ally, Status.Bulwark)

        # Total War Tome (Base) - CH!Mark
        if "oh hi mark" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, OMNI, -5)
                add_status(foe, Status.Sabotage)
                add_status(foe, Status.Stall)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, OMNI, -5)
                    add_status(ally, Status.Sabotage)
                    add_status(ally, Status.Stall)

        # Gusty War Bow (Base) - CH!Rebecca
        if "chRebeccaBoost" in unitSkills and allies_within_n_spaces[3] and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # Mystic War Staff (Base) - CH!Lucius
        if "chLuciusBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.DenyFollowUp)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.DenyFollowUp)

        # Constant Dagger (Base) - Leila
        if "leilaBoost" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, SPD, -6)
                add_debuff(foe, DEF, -6)
                add_status(foe, Status.Discord)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -6)
                    add_debuff(ally, DEF, -6)
                    add_status(ally, Status.Discord)

        # Dark Perfume - R!Leila
        if "darkPerfume" in unitSkills:
            sp_charges[unit] += 1

            for foe in nearest_foes_within_n(unit, 20):
                add_status(foe, Status.Undefended)
                add_status(foe, Status.Flash)

                for ally in allies_within_n(foe, 2):
                    add_status(ally, Status.Undefended)
                    add_status(ally, Status.Flash)

        # Frost Breath (Base) - Nils
        if "nilsPlay" in unitSkills:
            for foe in nearest_foes_within_n(unit, 4):
                add_debuff(foe, OMNI, -4)

        # Corsair Cleaver - Fargus
        if "donkey kong is versing jokerrrrrr" in unitSkills and allies_within_n_spaces[3]:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.Orders)

            for ally in allies_within_n_spaces[3]:
                add_buff(ally, ATK, 6)
                add_buff(ally, DEF, 6)
                add_status(ally, Status.Orders)

        # Child's Compass (Base) - DE!Nino
        if "deNinoBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.TraverseTerrain)
            add_status(unit, Status.MobilityUp)

        # Göndul - X!Nino
        if "xNinoBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)

        # Fleeting Echo - X!Nino
        if "fangedTies" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.Canto1)
            add_status(unit, Status.MobilityUp)

            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 2
            if unit.specialCount == unit.specialMax - 1:
                sp_charges[unit] += 1

        # Crow's Crystal (Base) - DE!Ursula
        if "deUrsulaBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.TraverseTerrain)
            add_status(unit, Status.Desperation)
            add_status(unit, Status.Dominance)

        # Dead-Crow Tome - FA!Ursula
        if "faUrsulaBoost" in unitSkills and unitHPGreaterEqual25Percent:
            sp_charges[unit] += 1

            if unitHPEqual100Percent:
                sp_charges[unit] += 1

            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Desperation)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Desperation)

        # Dead-Wolf Blade - FA!Lloyd
        if "LaLoyd" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.FoePenaltyDoubler)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.FoePenaltyDoubler)

            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, DEF, -7)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, DEF, -7)

        # Tome of Reglay (Base) - Pent
        if "pentBoost" in unitSkills:
            if unit.specialCount == unit.specialMax and unit.wpnType in TOME_WEAPONS:
                sp_charges[unit] += 1

            for ally in allies_within_n_spaces[2]:
                if ally.specialCount == ally.specialMax and ally.wpnType in TOME_WEAPONS:
                    sp_charges[ally] += 1

        # Sisterly War Axe (Base) - SP!Karla
        if "DK, are you gonna eat BK after you win this?" in unitSkills and turn % 2 == 1:
            sp_charges[unit] += 2

        # Spear - Vaida
        if "vaidaBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.NullEffFliers)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, DEF, 6)
                add_status(ally, Status.NullEffFliers)
                add_status(ally, Status.NullBonuses)

        # Fimbulvetr Morn (Refine Eff) - Sonia
        if "yoink!" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.BonusDoubler)
            add_status(unit, Status.EssenceDrain)

            support_found = False

            for ally in allies_within_n_spaces[2]:
                if unit.isSupportOf(ally):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, RES, 6)
                    add_status(ally, Status.BonusDoubler)
                    add_status(ally, Status.EssenceDrain)
                    support_found = True

            if not support_found:
                for ally in units_with_extreme_stat(allies_within_n_spaces[2], ATK):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, RES, 6)
                    add_status(ally, Status.BonusDoubler)
                    add_status(ally, Status.EssenceDrain)

        # Ereshkigal - Nergal
        if "My name is Nergal. I made the morphs. It was difficult to put the quintessence together." in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.EssenceDrain)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.EssenceDrain)

        # Sisterly Axe - X!Eirika
        if "who's vince?" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Dodge)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Dodge)

        if "eEirikaBoost" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.Empathy)
            add_status(unit, Status.SpecialCharge)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.Empathy)
                add_status(ally, Status.SpecialCharge)

        # Reginleif - Duo Ephraim
        if "OH MY GOODNESS" in unitSkills and turn % 2 == 0:
            add_status(unit, Status.MobilityUp)

        # Seafoam Splitter - SU!Ephraim
        if "DK BK DK's eating BK when he wins this" in unitSkills and len(allies_within_n_spaces[1]) <= 2:
            add_status(unit, Status.MobilityUp)

        if "gerikBoost" in unitSkills:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.NullPenalties)
            add_status(unit, Status.NullPanic)

            for ally in starting_team:
                if ally != unit or ally.HPcur < unit.HPcur:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    add_status(unit, Status.NullPenalties)
                    add_status(unit, Status.NullPanic)

            if turn == 1:
                sp_charges[unit] += 1

                for ally in starting_team:
                    if ally != unit or ally.HPcur < unit.HPcur:
                        sp_charges[ally] += 1

        # Staff of Rausten (Base) - CH!L'Arachel
        if "chL'ArachelBoost" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, RES, -6)
                add_status(foe, Status.Flash)

        # Lance of Frelia (Refine Base) - CH!Tana
        if "ffTanaBoost" in unitSkills:
            add_status(unit, Status.Canto1)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.Canto1)

        # Bow of Frelia (Refine Eff) - Innes
        if "c zachary chad" in unitSkills:
            sp_charges[unit] += 1

        # Lance of Grado - A!Amelia
        if "ascAmeliaBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.SpecialCharge)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.SpecialCharge)
                add_status(ally, Status.NullBonuses)

        # Tome of Storms (Refine Eff) - SS!Selena
        if "theDayTheEarthBlewUp" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Exposure)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Exposure)

        # Exotic Fruit Juice (refine Eff) - SU!SS!Selena
        if "suSelenaHexblade" in unitSkills:
            if foes_within_n_spaces[5]:
                add_buff(unit, ATK, 6)
                add_buff(unit, SPD, 6)
                add_status(unit, Status.Hexblade)

                for ally in allies_within_n_spaces[2]:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    add_status(ally, Status.Hexblade)

            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Flash)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Flash)

        # Dark Monograph (Refine Eff) - Knoll
        if "knollStuff" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Panic)
                add_status(foe, Status.DeepWounds)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Flash)
                    add_status(ally, Status.DeepWounds)

        # Tiger-Eye Axe (Base) - Caellach
        if "caellachBoost" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Discord)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Discord)

        # Rapid-Crier Bow (Base) - Neimi
        if "neimiBoost" in unitSkills:
            for ally in units_with_extreme_stat_pairing_sum(starting_team, ATK, SPD, exclude=unit):
                add_buff(unit, ATK, 6)
                add_buff(unit, SPD, 6)

        # Frelian Lance (Base) - Gilliam
        if "Official Nintendo Licensed Product" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                if ally.move == 2:
                    add_status(ally, Status.NullEffFliers)

        # Wild Wind Sword - Forde
        if "fordeBoost" in unitSkills:
            add_debuff(unit, SPD, -7)
            add_debuff(unit, DEF, -7)

        # Argent Aura (Base) - Riev
        if "rievBoost" in unitSkills:
            for foe in units_with_extreme_stat(waiting_team, SPD, find_max=False):
                add_debuff(foe, OMNI, -7)
                add_status(foe, Status.Stall)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, OMNI, -7)
                    add_status(ally, Status.Stall)

        # Blood Tome (Refine Eff) - FA!Lyon
        if "betaFomortiis" in unitSkills:
            add_status(unit, Status.CancelAffinity)

            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.TriangleAdept)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.TriangleAdept)

        # Icy Ravager - WI!Fomortiis
        if "satanSavesChristmas" in unitSkills and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # Bereft Lance (Refine Eff) - Orson
        if "or Son" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Exposure)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Exposure)

        # Darkling Guardian - L!Myrrh
        if "darklingGuardian" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.DenyFollowUp)
            add_status(unit, Status.WarpBubble)

        # Darkling Guard II - L!Myrrh
        if "darklingGuardianII" in unitSkills:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.DenyFollowUp)
            add_status(unit, Status.NullEffFliers)
            add_status(unit, Status.WarpBubble)
            add_status(unit, Status.Bulwark)

            if any([unit.isSupportOf(ally) for ally in starting_team]):
                for ally in allies_within_n_spaces[3]:
                    if unit.isSupportOf(ally):
                        add_buff(ally, DEF, 6)
                        add_buff(ally, RES, 6)
                        add_status(ally, Status.DenyFollowUp)
                        add_status(ally, Status.NullEffFliers)
                        add_status(ally, Status.WarpBubble)
                        add_status(ally, Status.Bulwark)

            else:
                for ally in units_with_extreme_stat(starting_team, DEF, exclude=unit):
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)
                    add_status(ally, Status.DenyFollowUp)
                    add_status(ally, Status.NullEffFliers)
                    add_status(ally, Status.WarpBubble)
                    add_status(ally, Status.Bulwark)

        # Darkling Dragon - V!Myrrh
        if "darklingDragon" in unitSkills:
            if allies_within_n_spaces[2]:
                add_buff(unit, DEF, 6)
                add_buff(unit, RES, 6)
                add_status(unit, Status.WarpBubble)

            if any([unit.isSupportOf(ally) for ally in starting_team]):
                for ally in allies_within_n_spaces[2]:
                    if unit.isSupportOf(ally):
                        add_status(ally, Status.WarpBubble)
                        add_buff(ally, DEF, 6)
                        add_buff(ally, RES, 6)

            else:
                for ally in units_with_extreme_stat(allies_within_n_spaces[2], DEF):
                    add_status(ally, Status.WarpBubble)
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)

        # Swirling Lance - DE!Ike
        if "jehannaIkeBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.Outspeeding)
            add_status(unit, Status.NullPanic)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, SPD, 6)
                add_buff(ally, DEF, 6)
                add_status(ally, Status.Outspeeding)
                add_status(ally, Status.NullPanic)

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

        # Arch-Sage Tome (Base) - B!Soren
        if "bSorenBoost" in unitSkills:
            if any([unit.isSupportOf(ally) for ally in starting_team]):
                for ally in allies_within_n_spaces[2]:
                    if unit.isSupportOf(ally):
                        add_status(ally, Status.AssignDecoy)
                        add_buff(ally, OMNI, 6)

            else:
                for ally in units_with_extreme_stat(allies_within_n_spaces[2], DEF):
                    add_status(ally, Status.AssignDecoy)
                    add_buff(ally, OMNI, 6)


        # Summer Strikers (Refine Eff) - SU!Mia
        if "summerMiaPulse" in unitSkills:
            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 1

                for ally in allies_within_n_spaces[2]:
                    if ally.specialCount == ally.specialMax:
                        sp_charges[ally] += 1

        # Sharp War Sword (Base) - CH!Mia
        if "pointySword" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.NullFollowUp)
            add_status(unit, Status.Dodge)

        # Summertime Axe - SF!Mia
        if "sfMiaBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.NullEffFliers)
            add_status(unit, Status.DamageReductionPierce50)

        # Crimean Scepter (Base) - A!Elincia
        if "aElinciaBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Pursual)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Pursual)

        # Heart of Crimea - L!Elincia
        if "heartOCrimea" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.NullFollowUp)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.NullFollowUp)

        # Talregan Axe (Refine Eff) - Jill
        if "jillSomething" in unitSkills and [ally for ally in allies_within_n_spaces[3] if ally.wpnType in MELEE_WEAPONS]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.MobilityUp)
            add_status(unit, Status.NullFollowUp)

            for ally in allies_within_n_spaces[3]:
                if ally.wpnType in MELEE_WEAPONS:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    add_status(unit, Status.MobilityUp)
                    add_status(unit, Status.NullFollowUp)

        # Chaos Named - Yune
        if "chaosNamed" in unitSkills:
            valid_area_foes = foes_within_n_columns(unit, 3)

            for foe in valid_area_foes:
                unit_res = unit.get_visible_stat(RES)
                foe_res = foe.get_visible_stat(RES)

                if "phantomRes" in unit.getSkills():
                    unit_res += unit.getSkills()["phantomRes"]
                if "phantomRes" in foe.getSkills():
                    foe_res += foe.getSkills()["phantomRes"]

                if foe_res <= unit_res - 3:
                    highest_stat = max(foe.get_visible_stat(ATK) - 15, foe.get_visible_stat(SPD), foe.get_visible_stat(DEF), foe.get_visible_stat(RES))

                    i = 1
                    while i < 5:
                        cur_stat = foe.get_visible_stat(i)
                        if i == ATK: cur_stat -= 15

                        if cur_stat == highest_stat:
                            add_debuff(foe, i, -5)
                        i += 1

        # Chaos Named+ - Yune
        if "chaosNamedFinger:" in unitSkills:
            i = 1
            while i < 5:
                for foe in units_with_extreme_stat(waiting_team, i):
                    add_debuff(foe, i, -7)
                    add_status(foe, Status.Panic)

                    for ally in allies_within_n(foe, 2):
                        add_debuff(ally, i, -7)

                    i += 1

        # Prescience II - L!Micaiah
        if "prescienceII" in unitSkills:
            for i in range(1, 5):
                for foe in units_with_extreme_stat(waiting_team, i):
                    add_debuff(foe, i, -7)
                    add_status(foe, Status.Panic)
                    add_status(foe, Status.Sabotage)

                    for ally in allies_within_n(foe, 2):
                        add_debuff(ally, i, -7)

        # Yune's Protection - X!Micaiah
        if "yunesProtection" in unitSkills:
            for i in range(1, 5):
                for foe in units_with_extreme_stat(waiting_team, i):
                    add_debuff(foe, i, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Discord)

                    for ally in allies_within_n(foe, 2):
                        add_debuff(ally, i, -7)

        # Order's Restraint - Ashera
        if "ordersRestraint" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.NullPanic)

            if len(allies_within_n_spaces[2]) >= 3:
                add_buff(unit, ATK, 6)
                add_buff(unit, RES, 6)
                add_status(unit, Status.NullPanic)

        # Order's Restraint+ - Ashera
        if "ordersRestraintPlus" in unitSkills:
            for ally in allies_within_n_spaces[3]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.NullPanic)
                add_status(ally, Status.NullFollowUp)
                add_status(ally, Status.Hexblade)

            if len(allies_within_n_spaces[3]) >= 3:
                add_buff(unit, ATK, 6)
                add_buff(unit, RES, 6)
                add_status(unit, Status.NullPanic)
                add_status(unit, Status.NullFollowUp)
                add_status(unit, Status.DamageReductionPierce50)

        # Joyful Vows (Refine Eff) - BR!Micaiah
        if "micaiahLove" in unitSkills:
            i = 1
            while i < 5:
                for foe in units_with_extreme_stat(waiting_team, i):
                    add_debuff(foe, i, -7)
                    add_status(foe, Status.Sabotage)

                    for ally in allies_within_n(foe, 2):
                        add_debuff(ally, i, -7)

                    i += 1

        # Arcane Tempest
        if "arcaneTempest" in unitSkills and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # Sky-Pirate Claw (Refine Eff) - PI!Tibarn
        if "skyPirate" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Exposure)
                add_status(foe, Status.Frozen)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Exposure)
                    add_status(ally, Status.Frozen)

        # Bride's Fang (Refine Eff) - BR!Nailah
        if "limitRocket" in unitSkills and unit.transformed:
            add_status(unit, Status.MobilityUp)
            add_status(unit, Status.TraverseTerrain)

        # Wild Tiger Fang (Base) - FA!Muarim
        if "faMuarimBoost" in unitSkills:
            for foe in foes_within_n_spaces[4]:
                add_debuff(foe, OMNI, -6)

        # Daniel-Made Bow (Refine Eff) - Jorge
        if "WE'RE ALL GOING DOWN TO MEMPHIS" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Hexblade)
            add_status(unit, Status.SpecialCharge)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Hexblade)
                add_status(ally, Status.SpecialCharge)

        # Arcane Þrima
        if "thrima" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -6)
                add_debuff(foe, DEF, -6)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -6)
                    add_debuff(ally, DEF, -6)

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

        # Master's Tactics (Base) - L!M!Robin
        if "THIS IS THE GREATEST PLAAAAAN" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.GrandStrategy)
            add_debuff(unit, OMNI, -4)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.GrandStrategy)

                ally_stats = [ally.get_visible_stat(ATK) - 15, ally.get_visible_stat(SPD), ally.get_visible_stat(DEF), ally.get_visible_stat(RES)]
                unique_sorted = sorted(set(ally_stats), reverse=True)[:2]
                top_indicies = [i for i, v in enumerate(unique_sorted) if v in unique_sorted]

                for i in top_indicies:
                    add_debuff(ally, i + 1, -6)

            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, OMNI, -3)

                for ally in allies_within_n(foe, 3):
                    add_debuff(ally, OMNI, -3)

        # Tip the Scales! - B!M!Robin
        if "tipTheScales" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.RallySpectrum)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.RallySpectrum)

        # According to Plan - B!F!Robin
        if "accordingToPlan" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Canto1)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Canto1)

            for foe in nearest_foes_within_n(unit, 20):
                add_status(foe, Status.HushSpectrum)
                add_status(foe, Status.Panic)

                for ally in allies_within_n(foe, 2):
                    add_status(ally, Status.HushSpectrum)
                    add_status(ally, Status.Panic)

        # Grima's Truth (Refine Base) - M!Morgan
        if "morganStartDebuff" in unitSkills:
            for foe in nearest_foes_within_n(unit, 4):
                add_debuff(foe, ATK, -5)
                add_debuff(foe, SPD, -5)
                add_debuff(foe, RES, -5)

            add_buff(unit, ATK, 5)
            add_buff(unit, SPD, 5)
            add_buff(unit, RES, 5)

        # Tome of Despair - FA!M!Morgan
        if "among uhhs" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.HushSpectrum)
                add_status(foe, Status.Ploy)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.HushSpectrum)
                    add_status(ally, Status.Ploy)

        # Apotheosis Spear (Refine Base) - Awakening Anna
        if "One time offer, restrictions may apply" in unitSkills:
            if len(allies_within_n_spaces[2]) >= 1:
                add_status(unit, Status.Canto1)

                for ally in allies_within_n_spaces[2]:
                    add_status(ally, Status.Canto1)

            if len(allies_within_n_spaces[2]) >= 2:
                add_status(unit, Status.Dodge)

                for ally in allies_within_n_spaces[2]:
                    add_status(ally, Status.Dodge)

        # Heavy War Axe - CH!Frederick
        if "He's gotta get his head in the game." in unitSkills:
            if allies_within_n_spaces[2]:
                add_buff(unit, ATK, 6)
                add_buff(unit, DEF, 6)
                add_status(unit, Status.BonusDoubler)
                add_status(unit, Status.DenyFollowUp)

            if any([unit.isSupportOf(ally) for ally in starting_team]):
                for ally in allies_within_n_spaces[2]:
                    if unit.isSupportOf(ally):
                        add_buff(ally, ATK, 6)
                        add_buff(ally, DEF, 6)
                        add_status(ally, Status.BonusDoubler)
                        add_status(ally, Status.DenyFollowUp)

            else:
                for ally in units_with_extreme_stat(allies_within_n_spaces[2], DEF):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, DEF, 6)
                    add_status(ally, Status.BonusDoubler)
                    add_status(ally, Status.DenyFollowUp)

        # Inseverable Spear (Base) - WI!Cordelia
        if "is chrismaaas" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.Orders)
            add_status(unit, Status.DualStrike)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.Orders)
                add_status(ally, Status.DualStrike)

        # Plegian War Axe (Base) - Mustafa
        if "mustafaBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.DenyFollowUp)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.DenyFollowUp)

        # Scroll of Curses - NI!Tharja
        if "niTharjaBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Anathema)
            add_status(unit, Status.SpecialCharge)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Anathema)
                add_status(ally, Status.SpecialCharge)

        # Levin Dagger (Refine Base) - Gangrel
        if "gangrelBoost" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Guard)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Guard)

        # Sudden Panic
        if "suddenPanicSk" in unitSkills:
            for foe in waiting_team:

                if allies_within_n(foe, 1):
                    unit_hp = unit.HPcur
                    foe_hp = foe.HPcur

                    if foe_hp <= unit_hp - (7 - unitSkills["suddenPanicSk"] * 2):
                        add_status(foe, Status.Panic)

        # Dignified Bow - Virion
        if "suddenPanicW" in unitSkills:
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

        # Full Rabbit Fang - H!Yarne
        if "hYarneBoost" in unitSkills:
            non_dragon_beast = 0

            for ally in allies_within_n_spaces[1]:
                if ally.wpnType not in DRAGON_WEAPONS + BEAST_WEAPONS:
                    non_dragon_beast += 1

            if non_dragon_beast <= 1 or unit.transformed:
                sp_charges[unit] += 1

        # Oracle's Breath (Refine Eff) - Nah
        if "nahI'dWin" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.SpecialCharge)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.SpecialCharge)

        # Stone of Delights - H!Nah
        if "hNahBoost" in unitSkills:
            for ally in allies_within_n(unit, 20):
                if ally.visible_stats[HP] < unit.visible_stats[HP]:
                    sp_charges[ally] += 1

        # Blade of Favors (Base) - Gregor
        if "gregorSword!" in unitSkills and foes_within_n_cardinal(unit, 3):
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)

            for foe in foes_within_n_cardinal(unit, 3):
                add_debuff(foe, ATK, -6)
                add_debuff(foe, SPD, -6)
                add_debuff(foe, DEF, -6)

        # Grimleal Text - Validar
        if "validarFINALLY" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                if unit.get_visible_stat(RES) + unit.get_phantom_stat(RES) > foe.get_visible_stat(RES) + foe.get_phantom_stat(RES):
                    add_debuff(foe, DEF, -6)
                    add_debuff(foe, RES, -6)
                    add_status(foe, Status.Panic)
                    add_status(foe, Status.Discord)

        # Brutal Breath (Refine Eff) - FA!M!Corrin
        if "corrinHike" in unitSkills and len(allies_within_n_spaces[2]) <= 2:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Dodge)
            add_status(unit, Status.NullBonuses)

        # Primordial Breath (Refine Eff) - L!F!Corrin
        if "primordia" in unitSkills and turn == 1 and unit.getSpecialType() == "Defense":
            sp_charges[unit] += 2

        # Hoshido's Breath - L!M!Corrin
        if "HoshidosBreath" in unitSkills and unitHPGreaterEqual25Percent and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # Duskstone - CH!M!Corrin
        if "chCorrinBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.DraconicHex)

            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 1

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.DraconicHex)

        # Prayer Wheel (Refine Eff) - L!Azura
        if "azuraTriangle" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                add_buff(ally, SPD, 6)

        # Tri-Path Splitter - X!Azura
        if "Vince" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.NullFollowUp)
            add_status(unit, Status.NullPanic)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.NullFollowUp)
                add_status(ally, Status.NullPanic)

        # Ice-Tribe Axe - FF!Felicia
        if "iceFeliciaBoost" in unitSkills:
            if any([unit.isSupportOf(ally) for ally in starting_team]):
                for ally in allies_within_n_spaces[3]:
                    if unit.isSupportOf(ally):
                        add_status(ally, Status.NullEffDragons)

            else:
                for ally in units_with_extreme_stat(allies_within_n_spaces[3], RES):
                    add_status(ally, Status.NullEffDragons)

        # Skadi - FA!Takumi
        if "skadiDamage" in unitSkills and turn == 3:
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(3) if tile.hero_on is not None and tile.hero_on.isEnemyOf(unit)]:
                add_status(foe, Status.Panic)

        if "skadiMoreDamage" in unitSkills and (turn == 2 or turn == 3):
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(3) if tile.hero_on is not None and tile.hero_on.isEnemyOf(unit)]:
                add_status(foe, Status.Panic)

        # Ebon Bölverk (Base) - L!Xander
        if "LXanderBoost" in unitSkills and len(allies_within_n_spaces[2]) >= 2:
            add_status(unit, Status.SpecialCharge)
            add_status(unit, Status.NullFollowUp)

        # Ebon Bölverk (Refine Base) - L!Xander
        if "LXanderRefine" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.SpecialCharge)
            add_status(unit, Status.NullFollowUp)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.SpecialCharge)
                add_status(ally, Status.NullFollowUp)

            if len(allies_within_n_spaces[2]) >= 2:
                add_status(unit, Status.MobilityUp)

        # Lucky Bow (Refine Eff) - Midori
        if "Medicine!" in unitSkills and allies_within_n(unit, 2):
            clear_penalty_statuses.append(unit)
            clear_penalty_stats.append(unit)

            for ally in allies_within_n(unit, 2):
                clear_penalty_statuses.append(ally)
                clear_penalty_stats.append(ally)

        # Iago's Tome (Base) - Iago
        if "iagoTome" in unitSkills:
            if turn % 2 == 1:
                for foe in waiting_team:
                    if not allies_within_n(foe, 1) and foe.HPcur <= unit.HPcur - 3:
                        add_debuff(foe, ATK, -4)
                        add_debuff(foe, SPD, -4)
                        add_status(foe, Status.Guard)
            else:
                for foe in waiting_team:
                    if allies_within_n(foe, 1) and foe.HPcur <= unit.HPcur - 3:
                        add_debuff(foe, DEF, -4)
                        add_debuff(foe, RES, -4)
                        add_status(foe, Status.Panic)

        if "iagoRefine" in unitSkills:
            if turn % 2 == 1:
                for foe in waiting_team:
                    if not allies_within_n(foe, 1) and foe.HPcur <= unit.HPcur - 3:
                        add_debuff(foe, ATK, -6)
                        add_debuff(foe, SPD, -6)
                        add_status(foe, Status.Guard)
            else:
                for foe in waiting_team:
                    if allies_within_n(foe, 1) and foe.HPcur <= unit.HPcur - 3:
                        add_debuff(foe, DEF, -6)
                        add_debuff(foe, RES, -6)
                        add_status(foe, Status.Panic)

        if "iagoWHEEEEEEE" in unitSkills:
            if turn % 2 == 1:
                add_buff(unit, DEF, 6)
                add_buff(unit, RES, 6)
                add_status(unit, Status.DenyFollowUp)
                add_status(unit, Status.NullBonuses)

                for ally in allies_within_n_spaces[2]:
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)
                    add_status(ally, Status.DenyFollowUp)
                    add_status(ally, Status.NullBonuses)

            else:
                add_buff(unit, ATK, 6)
                add_buff(unit, SPD, 6)
                add_status(unit, Status.Pursual)
                add_status(unit, Status.Hexblade)

                for ally in allies_within_n_spaces[2]:
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    add_status(ally, Status.Pursual)
                    add_status(ally, Status.Hexblade)

        if "gharnefDmg" in unitSkills and turn == 3:
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(5) if unit.isEnemyOf(tile.hero_on)]:
                if foe.wpnType not in TOME_WEAPONS:
                    add_status(foe, Status.Flash)

        # Rallying Cry - L!Hinoka
        if "rallyingCry" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.SpecialCharge)
            add_status(unit, Status.Charge)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.SpecialCharge)

                if ally.move == 2:
                    add_status(ally, Status.Charge)

        # Salvage - L!Sakura
        if "LSakuraBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Orders)
            add_status(unit, Status.Salvage)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Orders)
                add_status(ally, Status.Salvage)

        # Book of Dreams (Refine Eff) - Adrift Camilla
        if "camillaDebuff" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, ATK, -5)
                add_debuff(foe, SPD, -5)
                add_debuff(foe, RES, -5)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -5)
                    add_debuff(ally, SPD, -5)
                    add_debuff(ally, RES, -5)

        # Sanngriðr	(Refine Eff) - B!Camilla
        if "braveCamillaDebuff" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                add_debuff(foe, DEF, -7)
                add_debuff(foe, RES, -7)

        # Spoil Rotten - L!Camilla
        if "spoilRotten" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Sabotage)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Sabotage)

            add_status(unit, Status.DamageReductionPierce50)
            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.DamageReductionPierce50)

        # Axe of Dusk - CH!Camilla
        if "chCamillaBoost" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 2):
                    add_debuff(foe, SPD, -7)
                    add_debuff(foe, DEF, -7)
                    add_status(foe, Status.Discord)
                    add_status(foe, Status.DeepWounds)

        # Tut-Tut! - CH!Camilla
        if "tut-tut" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.DamageReductionPierce50)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.DamageReductionPierce50)

        # Duskbloom Bow (Base) - V!Leo
        if "vLeoBoost" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 1):
                if unit.get_visible_stat(RES) + unit.get_phantom_stat(RES) > foe.get_visible_stat(RES) + foe.get_phantom_stat(RES):
                    add_debuff(foe, DEF, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Gravity)

        # Baton of Dusk - CH!Elise
        if "chEliseBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Treachery)
            add_status(unit, Status.SpecialCharge)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Treachery)
                add_status(unit, Status.SpecialCharge)

        if "velouriaBoost" in unitSkills:
            self_cond = False

            for ally in allies_within_n(unit, 3):
                if unit.isSupportOf(ally):
                    self_cond = True
                    add_status(ally, Status.NullBonuses)

            if self_cond:
                add_status(unit, Status.NullBonuses)

        # Astral Breath (Refine Base) - Lilith
        if "lilithRefineWarp" in unitSkills and any([ally.isSupportOf(unit) for ally in allies_within_n_spaces[3]]):
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Dodge)

            for ally in allies_within_n_spaces[3]:
                if ally.isSupportOf(unit):
                    add_buff(ally, SPD, 6)
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)
                    add_status(ally, Status.Dodge)

        # Silent Power (Base) - FA!Lilith
        if "faLilithBoost" in unitSkills and any([ally.isSupportOf(unit) for ally in allies_within_n_spaces[3]]):
            add_status(unit, Status.NullFollowUp)

            for ally in allies_within_n_spaces[3]:
                if ally.isSupportOf(unit):
                    add_status(ally, Status.NullFollowUp)

        # Tome of Grief (Base) - Arete
        if "areteDebuff" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Flash)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Flash)

        # Goddess Bearer - L!Byleth
        if "goddessBearer" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 7)
            add_buff(unit, SPD, 7)
            add_status(unit, Status.NullFollowUp)
            add_status(unit, Status.Orders)

        if "goddessBearerII" in unitSkills and allies_within_n_cardinal(unit, 3):
            add_buff(unit, ATK, 7)
            add_buff(unit, SPD, 7)
            add_status(unit, Status.NullFollowUp)
            add_status(unit, Status.Orders)

        # Inner Wellspring (Base) - B!F!Byleth
        if ("bfBylethBoost" in unitSkills or "bfBylethRefine" in unitSkills) and allies_within_n_spaces[2]:
            add_status(unit, Status.NullFollowUp)

            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 1

        # Guide's Hourglass (Base) - DE!M!Byleth
        if "deBylethBoost" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.Dodge)
            add_status(unit, Status.TraverseTerrain)

        # Breaker Lance (Base) - Jeralt
        if "he lives" in unitSkills:
            for foe in units_with_extreme_stat_pairing_sum(waiting_team, DEF, RES):
                add_debuff(foe, ATK, -6)
                add_debuff(foe, DEF, -6)
                add_status(foe, Status.Panic)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -6)
                    add_debuff(ally, DEF, -6)
                    add_status(ally, Status.Panic)

        # Flower Hauteclere (Base) - B!Edelgard
        if "flowerEdelgard" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.MobilityUp)
            add_status(unit, Status.Orders)

        # Raging Tempest - WI!Edelgard
        if "ragingTempest" in unitSkills and (foes_within_n_cardinal(unit, 3) or unitHPEqual100Percent):
            add_status(unit, Status.MobilityUp)
            add_status(unit, Status.Charge)

        # Pure Storm - V!Edelgard
        if "pureStorm" in unitSkills:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Sabotage)
                add_status(foe, Status.Exposure)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Sabotage)
                    add_status(ally, Status.Exposure)

        # Flame Battleaxe (Refine Eff) - Flame Emperor
        if "Some kind of twisted joke?" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                add_debuff(foe, ATK, -7)
                add_status(foe, Status.Sabotage)

        # Persecution Bow (Refine Eff) - Bernadetta
        if "rock" in unitSkills and allies_within_n_spaces[2]:
            sp_charges[unit] += 1

        # Hrist (Refine Base) - WI!Bernadetta
        if "wiBernieRefine" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.Paranoia)
            add_status(unit, Status.SpecialCharge)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.Paranoia)
                add_status(ally, Status.SpecialCharge)

        # Paranoia - B!Bernadetta
        if "paranoia" in unitSkills:
            add_status(unit, Status.NullFollowUp)
            add_status(unit, Status.Paranoia)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.Paranoia)

            if foes_within_n(unit, 5):
                for foe in nearest_foes_within_n(unit, 5):
                    for status in unit.statusNeg:
                        add_status(foe, status)

                    for i in range(1, 5):
                        add_debuff(foe, i, unit.debuffs[i])

                    for ally in allies_within_n(foe, 2):
                        for status in unit.statusNeg:
                            add_status(ally, status)

                        for i in range(1, 5):
                            add_debuff(ally, i, unit.debuffs[i])

                clear_penalty_statuses.append(unit)
                clear_penalty_stats.append(unit)

        # Fell Candelabra (Base) - DE!Dorothea
        if "deDorotheaTarget" in unitSkills:
            for i in range(1, 5):
                for foe in units_with_extreme_stat(waiting_team, i):
                    add_debuff(foe, i, -6)

        # Blue Yule Axe - WI!Dimitri
        if "Are you gonna release the demon wra-" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.NullFollowUp)

        # Lion's Heart - V!Dimitri
        if "vDimitriBoost" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.NullPenalties)
            add_status(unit, Status.SpecialCharge)
            add_status(unit, Status.MobilityUp)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.NullPenalties)
                add_status(ally, Status.SpecialCharge)

        # Starpoint Lance (Refine Eff) - SU!Ingrid
        if "suIngidStuff" in unitSkills and any([ally for ally in allies_within_n_spaces[2] if ally.move == 3 or (ally.wpnType in MELEE_WEAPONS and (ally.move == 0 or ally.move == 2))]):
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.MobilityUp)
            add_status(unit, Status.Canto1)

            for ally in allies_within_n_spaces[2]:
                if ally.move == 3 or (ally.wpnType in MELEE_WEAPONS and (ally.move == 0 or ally.move == 2)):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, SPD, 6)
                    add_status(ally, Status.MobilityUp)
                    add_status(ally, Status.Canto1)

        # Lone-Wolf Blade (Base) - Felix
        if ">:(" in unitSkills and unitHPGreaterEqual25Percent:
            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 2
            if unit.specialCount == unit.specialMax - 1:
                sp_charges[unit] += 1

        # Cunning Bow (Refine Eff) - Claude
        if "three houses discourse" in unitSkills and foes_within_n_cardinal(unit, 3):
            add_buff(unit, ATK, 6)

            for foe in foes_within_n_cardinal(unit, 3):
                add_debuff(foe, DEF, -7)

        # Failnaught (Refine Base) - L!Claude
        if "LClaudeRefine" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Guard)
                add_status(foe, Status.Sabotage)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Guard)
                    add_status(ally, Status.Sabotage)

        # Deer's Heart - V!Claude
        if "vClaudeBoost" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.NullFollowUp)
            add_status(unit, Status.PreemptPulse)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.Orders)
                add_status(ally, Status.PreemptPulse)

        # Icy Fimbulvetr (Refine Base) - Marianne
        if "marianneCanto" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in waiting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -7)
                        add_debuff(foe, RES, -7)
                        add_status(foe, Status.Exposure)
                        add_status(foe, Status.Guard)

        # Dark Spikes T (Refine Eff) - B!Lysithea
        if "lysitheaSchmovement" in unitSkills:
            add_status(unit, Status.Orders)

        # Baked Treats - T!Lysithea
        if "tLysitheaBoost" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, SPD, -6)
                add_debuff(foe, RES, -6)
                add_status(foe, Status.Sabotage)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -6)
                    add_debuff(ally, RES, -6)
                    add_status(ally, Status.Sabotage)

        # Honorable Blade (Base) - Yuri
        if "yuriBoost" in unitSkills:
            add_status(unit, Status.MobilityUp)

        if "fettersODromi" in unitSkills:
            add_status(unit, Status.MobilityUp)

        # Thunderbrand (Refine Base) - Catherine
        if "catherineRefine" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Treachery)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Treachery)

        # Survivalist Bow (Refine Eff) - Shamir
        if "survivialist" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, DEF, -7)
                add_status(unit, Status.Sabotage)

        if "the two" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_status(unit, Status.Panic)
                add_status(unit, Status.Discord)

                for ally in allies_within_n(foe, 2):
                    add_status(ally, Status.Panic)
                    add_status(ally, Status.Discord)

        # Caduceus Staff (Refine Eff) - Flayn
        if "The girl who like the fish" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.SpecialCharge)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.SpecialCharge)

        # Asclepius (Base) - Cornelia
        if "there is a camera and microphone in this device" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in waiting_team:
                if allies_within_n(foe, 1):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -6)
                        add_debuff(foe, RES, -6)
                        add_status(foe, Status.Flash)

        # Banshee Θ (Base) - Solon
        if "solonDebuffs" in unitSkills and (turn == 3 or turn == 4):
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, OMNI, -unitSkills["solonDebuffs"])
                add_status(foe, Status.Gravity)
                add_status(foe, Status.Guard)
                add_status(foe, Status.Flash)

        # Banshee Θ (Refine Eff) - Solon
        if "So joining Smash consumes even the darkness itself?" in unitSkills:
            for foe in waiting_team:
                if foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) < unit.get_visible_stat(RES) + unit.get_phantom_stat(RES) and allies_within_n(foe, 2):
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Sabotage)

        # Red-Fist Blades - WI!F!Shez
        if "merryShez!mas" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Incited)
            add_status(unit, Status.SpecialCharge)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Incited)
                add_status(ally, Status.SpecialCharge)

        # Rite of Souls (Base) - Arval
        if "arvalBoost" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                if foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) < unit.get_visible_stat(RES) + unit.get_phantom_stat(RES):
                    add_status(foe, Status.Guard)

        # Wind Genesis (Base) - Monica
        if "monicaBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Desperation)

        # Kiria (Refine Eff) - Kiria
        if "kiriaSabotage" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                add_debuff(foe, ATK, -6)
                add_debuff(foe, RES, -6)
                add_status(unit, Status.Sabotage)

        # ENGAGE

        # Libération (Base) - F!Alear
        if "BONDS OF FIIIIRE, CONNECT US" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.Charge)

            for ally in allies_within_n_spaces[3]:
                if ally.isSupportOf(unit):
                    add_status(ally, Status.Charge)

        # Bond Blast (SU!F!Alear)
        if "summerAlearBonds" in unitSkills:
            if not any([unit.isSupportOf(ally) for ally in starting_team]):
                for ally in units_with_extreme_stat(allies_within_n_spaces[2], ATK):
                    add_status(ally, Status.Bonded)

        # Wintery Arts - WI!M!Alear
        if "wiAlearBoost" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.DivinelyInspiring)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.DivinelyInspiring)

        # Fell Blast - FA!F!Alear
        if "fellBlast" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.FellSpirit)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.FellSpirit)

        # Bond Breaker - FA!M!Alear
        if "bondBreaker" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.FellSpirit)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.FellSpirit)

            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, SPD, -7)
                add_status(foe, Status.Schism)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, SPD, -7)
                    add_status(ally, Status.Schism)

        # Obscurité - Veyle
        if "veyleBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.ResonanceBlades)
            add_status(unit, Status.ResonanceShields)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.ResonanceBlades)
                add_status(ally, Status.ResonanceShields)

        # Gentle Fell Egg - SP!Veyle
        if "spVeyleBoost" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.AOEReduce80Percent)
            add_status(unit, Status.ResonanceBlades)
            add_status(unit, Status.ResonanceShields)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.AOEReduce80Percent)
                add_status(ally, Status.ResonanceBlades)
                add_status(ally, Status.ResonanceShields)

        # Sky-Hopper Egg - SP!Chloé
        if "sky-hopper" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Charge)
            add_status(unit, Status.FirstReduce40)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Charge)
                add_status(ally, Status.FirstReduce40)

            n = len(starting_team)
            for i in range(n):
                for j in range(i + 1, n):
                    if starting_team[i].isSupportOf(starting_team[j]) and starting_team[i] != unit and starting_team[j] != unit:

                        add_buff(starting_team[i], ATK, 6)
                        add_buff(starting_team[i], SPD, 6)
                        add_status(starting_team[i], Status.Charge)
                        add_status(starting_team[i], Status.FirstReduce40)

                        add_buff(starting_team[j], ATK, 6)
                        add_buff(starting_team[j], SPD, 6)
                        add_status(starting_team[j], Status.Charge)
                        add_status(starting_team[j], Status.FirstReduce40)

        # Tome of Luxuries - Cirtinne
        if "citrinneBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.Pursual)

        # Hidden Blade - Yunaka
        if "hiyaPapaya" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Sabotage)
                add_status(foe, Status.Discord)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Sabotage)
                    add_status(ally, Status.Discord)

        # Icebound Tome - Ivy
        if "ivyBoost" in unitSkills and unitHPGreaterEqual25Percent:
            if not any([unit.isSupportOf(ally) for ally in starting_team]):
                add_status(unit, Status.MobilityUp)

        # Glittering Anima - Hortensia
        if "glitteringAnima" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Canto1)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n_spaces[3]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Canto1)
                add_status(ally, Status.NullPenalties)

            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -6)
                add_debuff(foe, RES, -6)
                add_status(foe, Status.Discord)
                add_status(foe, Status.Panic)

                for ally in allies_within_n(foe, 3):
                    add_debuff(ally, SPD, -6)
                    add_debuff(ally, RES, -6)
                    add_status(ally, Status.Discord)
                    add_status(ally, Status.Panic)

        # Twinkling Anima - WI!Hortensia
        if "twinklingAnima" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Canto1)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n_spaces[3]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Canto1)
                add_status(ally, Status.NullPenalties)

            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Discord)
                add_status(foe, Status.Panic)

                for ally in allies_within_n(foe, 3):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Discord)
                    add_status(ally, Status.Panic)

        # Inspirited Spear - H!Timerra
        if "meat" in unitSkills and foes_within_n_cardinal(unit, 3):
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, SPD, 6)
                add_buff(ally, DEF, 6)

        # Berserker Axe - Panette
        if "hmm today I will crash the game" in unitSkills:
            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 1

            for ally in allies_within_n_spaces[2]:
                if ally.specialCount == unit.specialMax:
                    sp_charges[ally] += 1

        # Packleader Tome - Zephia
        if "zephiaBoost" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, SPD, -6)
                add_debuff(foe, RES, -6)
                add_status(foe, Status.Pursual)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -6)
                    add_debuff(ally, RES, -6)
                    add_status(ally, Status.Pursual)

        # Penitent Lance - Mauvier
        if "mauvierBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.Hexblade)
            add_status(unit, Status.NullPanic)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.Hexblade)
                add_status(ally, Status.NullPanic)

        # Praise-Piner Axe - Marni
        if "marniBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.NullBonuses)

        # Payday Pouch - H!E!Anna
        if "hAnnaBoost" in unitSkills:
            if len(allies_within_n_spaces[2]) >= 1:
                add_status(unit, Status.NullFollowUp)
            if len(allies_within_n_spaces[2]) >= 2:
                add_status(unit, Status.Hexblade)

        # Majestic Glitnir - B!Alfonse
        if "bAlfonseBoost" in unitSkills and allies_within_n_cardinal(unit, 3):
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.MobilityUp)

            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 1

        # Makings of a King - B!Alfonse
        if "makingsOfAKing" in unitSkills:
            add_great_talent(unit, ATK, 2, 20)
            add_great_talent(unit, DEF, 2, 20)
            add_great_talent(unit, RES, 2, 20)

            for ally in allies_within_n_spaces[2]:
                add_great_talent(ally, ATK, 1, 10)
                add_great_talent(ally, DEF, 1, 10)
                add_great_talent(ally, RES, 1, 10)

        # United Bouquet - BR!Sharena
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

        if "spVeronicaOrders" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Orders)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Orders)

        # Gate-Anchor Axe (Refine Eff) - PI!Veronica
        if "veronicaAnchor" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Feud)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Feud)

        # Gjallarbrú (Base/Refine Base) - BR!Fjorm
        if "brFjormIsolate" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 1):
                if foe.HPcur <= unit.HPcur - unitSkills["brFjormIsolate"]:
                    add_status(foe, Status.Isolation)

        # Ice Prince's Seal - SU!Hríd
        if "icePrinceSeal" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Guard)
                add_status(foe, Status.Frozen)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(foe, Status.Guard)
                    add_status(foe, Status.Frozen)

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

        if "wolf back air" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.NullBonuses)
            add_status(unit, Status.NullPanic)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, DEF, 6)
                add_status(ally, Status.NullBonuses)
                add_status(ally, Status.NullPanic)

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

        if "surtrPortent" in unitSkills and foes_within_n_spaces[4]:
            add_buff(unit, OMNI, 5)

            for foe in foes_within_n_spaces[2]:
                add_debuff(foe, OMNI, -5)

        if "Won't you just die?" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_status(foe, Status.Exposure)

                for ally in allies_within_n(foe, 2):
                    add_status(ally, Status.Exposure)

        # Springing Spear - SP!Plumeria
        if "spPlumeriaBoost" in unitSkills:
            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.Canto1)

        # Dream Deliverer - Freyr
        if "dreamDeliverer" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.ResonanceShields)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.ResonanceShields)

        # Ruler of Nihility - Ginnungagap
        if "arcaneVoid" in unitSkills:
            for foe in nearest_foes_within_n(unit, 5):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Discord)
                add_status(foe, Status.Flash)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Discord)
                    add_status(ally, Status.Flash)

        # Niðavellir Ballista - Niðavellir
        if "niðavellirBoost" in unitSkills and turn <= 4:
            sp_charges[unit] += 3
            add_status(unit, Status.Hexblade)

            for ally in allies_within_n_spaces[2]:
                sp_charges[ally] += 1
                add_status(ally, Status.Hexblade)

        # Grim Brokkr (Refine Eff) - Eitri
        if "book 5 sure was a book" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Sabotage)
                add_status(foe, Status.Schism)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Sabotage)
                    add_status(ally, Status.Schism)

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

        # Supreme Thökk - Loki
        if "supremeThokk" in unitSkills and unitHPGreaterEqual25Percent:
            sp_charges[unit] += 1

        # Divine Deceit - Loki
        if "divineDeceit" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            n_cardinal_1 = foes_within_n_cardinal(unit, 1)

            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_status(foe, Status.Ploy)
                    add_status(foe, Status.Exposure)

                    if foe in n_cardinal_1:
                        add_status(foe, Status.Gravity)

        # Divine Whimsy (Base) - SU!Thorr
        if "suThorrBoost" in unitSkills:
            for foe in units_with_extreme_stat(waiting_team, SPD, find_max=False):
                add_status(foe, Status.Exposure)
                add_status(foe, Status.Stall)

                for ally in allies_within_n(foe, 2):
                    add_status(ally, Status.Exposure)
                    add_status(ally, Status.Stall)

            if allies_within_n_spaces[2]:
                sp_charges[unit] += 1

        # Auto-Lofnheiðr (Refine Eff) - Ótr
        if "F Tier Banner Sales" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.TraverseTerrain)
            add_status(unit, Status.Incited)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.TraverseTerrain)
                add_status(ally, Status.Incited)

        # Skinfaxi (Refine Base) - Dagr / Twin-Sky Wing - FF!Dagr
        if "dagrRefineBoost" in unitSkills or "twinSkyWing" in unitSkills:
            valid_ally = None

            for ally in starting_team:
                if ally.isSupportOf(unit):
                    if valid_ally is None:
                        valid_ally = ally
                    else:
                        valid_ally = None
                        break

            if valid_ally is not None:
                add_status(valid_ally, Status.Pathfinder)

        # Veðrfölnir's Edge	- AI!Dagr
        if "aiDagrBoost" in unitSkills and allies_within_n_cardinal(unit, 3):
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.NullFollowUp)

            for ally in allies_within_n_cardinal(unit, 3):
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.NullFollowUp)

        # Veðrfölnir's Wing - AI!Dagr
        if "veðrfolnirsWing" in unitSkills:
            if any([ally for ally in starting_team if unit.isSupportOf(ally)]):
                if len([ally for ally in starting_team if unit.isSupportOf(ally)]) == 1:
                    valid_ally = [ally for ally in starting_team if unit.isSupportOf(ally)][0]

                    add_status(valid_ally, Status.NullFollowUp)
            else:
                if len(units_with_extreme_stat(starting_team, DEF, exclude=unit)) == 1:
                    valid_ally = units_with_extreme_stat(starting_team, DEF, exclude=unit)[0]

                    add_status(valid_ally, Status.NullFollowUp)

        # Hrímfaxi (Refine Base) - Nótt
        if "nottRefine" in unitSkills and unitHPGreaterEqual25Percent:
            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.Incited)

        # Opened Domain - Askr
        if "openedDomain" in unitSkills:
            ally_cond = False

            for ally in allies_within_n_spaces[2]:
                if ally.primary_game != unit.primary_game or (ally.secondary_game != unit.primary_game and ally.secondary_game != -1):
                    ally_cond = True
                    break

            if ally_cond:
                add_status(unit, Status.ResonanceBlades)
                add_status(unit, Status.ResonanceShields)

                if unit.specialCount == unit.specialMax:
                    sp_charges[unit] += 1

                for ally in allies_within_n_spaces[2]:
                    add_status(ally, Status.ResonanceBlades)
                    add_status(ally, Status.ResonanceShields)

                    if ally.specialCount == ally.specialMax:
                        sp_charges[ally] += 1

        # Brutal Ferocity - Þjazi
        if "brutalFerocity" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 1):
                if foe.HPcur < unit.get_visible_stat(HP):
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, DEF, -7)
                    add_status(foe, Status.Gravity)

        # Connected World - H!Askr
        if "connectedWorld" in unitSkills:
            ally_cond = False

            for ally in allies_within_n(unit, 3):
                if ally.primary_game != unit.primary_game or (ally.secondary_game != unit.primary_game and ally.secondary_game != -1):
                    ally_cond = True
                    break

            if ally_cond:
                add_buff(unit, ATK, 6)
                add_buff(unit, DEF, 6)
                add_status(unit, Status.ResonanceBlades)
                add_status(unit, Status.ResonanceShields)
                add_status(unit, Status.DamageReductionPierce50)

                if unit.specialCount == unit.specialMax:
                    sp_charges[unit] += 1

                for ally in allies_within_n(unit, 3):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, DEF, 6)
                    add_status(ally, Status.ResonanceBlades)
                    add_status(ally, Status.ResonanceShields)
                    add_status(ally, Status.DamageReductionPierce50)

                    if ally.specialCount == ally.specialMax:
                        sp_charges[ally] += 1

        # Severance - Embla
        if "severance" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                add_status(foe, Status.Undefended)
                add_status(foe, Status.Feud)

            if foes_within_n_cardinal(unit, 3):
                clear_penalty_statuses.append(unit)
                clear_penalty_stats.append(unit)
                add_status(unit, Status.Dodge)

        # Closing Florets - BR!Embla
        if "brEmblaBoost" in unitSkills and unitHPGreaterEqual25Percent:
            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 2
            elif unit.specialCount == unit.specialMax - 1:
                sp_charges[unit] += 1

            if any([unit.isSupportOf(ally) for ally in starting_team]):
                for ally in allies_within_n_spaces[2]:
                    if unit.isSupportOf(ally) and ally.specialCount == ally.specialMax:
                        sp_charges[ally] += 2
                    elif unit.isSupportOf(ally) and ally.specialCount == ally.specialMax - 1:
                        sp_charges[ally] += 1

            else:
                for ally in units_with_extreme_stat(allies_within_n_spaces[2], DEF):
                    if ally.specialCount == ally.specialMax:
                        sp_charges[ally] += 2
                    elif ally.specialCount == ally.specialMax - 1:
                        sp_charges[ally] += 1

        # Absolute Closure - BR!Embla
        if "absoluteClosure" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                add_status(foe, Status.Undefended)
                add_status(foe, Status.Feud)

            if foes_within_n_cardinal(unit, 3):
                clear_penalty_statuses.append(unit)
                clear_penalty_stats.append(unit)
                add_status(unit, Status.Dodge)

        # Seiðr (Base) - Seiðr
        if "seiðrBoost" in unitSkills and allies_within_n_spaces[2]:
            add_status(unit, Status.DenyFollowUp)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.DenyFollowUp)

        # Goddess Temari - NY!Seiðr
        if "nySeiðrBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.DenyFollowUp)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.DenyFollowUp)

        # Quieting Antler - Eikþyrnir
        if ("eikBoost" in unitSkills or "wiEikBoost" in unitSkills) and allies_within_n_spaces[2]:
            add_buff(unit, ATK, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.BonusDoubler)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, ATK, 6)
                add_buff(ally, DEF, 6)
                add_status(ally, Status.BonusDoubler)

        # Nectar Horn - Heiðrún
        if "heiðrúnBoost" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, DEF, -7)
                    add_status(foe, Status.Discord)
                    add_status(foe, Status.DeepWounds)
                    add_status(foe, Status.NullMiracle)

        # Divine Nectar - Heiðrún
        if ("divineNectar" in unitSkills or "nectarsMagic" in unitSkills) and allies_within_n_spaces[2]:
            add_status(unit, Status.DivineNectar)

            for ally in allies_within_n_spaces[2]:
                add_status(ally, Status.DivineNectar)

        # Quieting Claw - Hræsvelgr
        if "hræsvelgrBoost" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Exposure)
                add_status(foe, Status.NullMiracle)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, DEF, -7)
                    add_status(ally, Status.Exposure)
                    add_status(ally, Status.NullMiracle)

        # Divine Talon - Hræsvelgr
        if "divineTalon" in unitSkills:
            clear_penalty_stats.append(unit)
            clear_penalty_statuses.append(unit)

            for ally in allies_within_n(unit, 2):
                clear_penalty_stats.append(ally)
                clear_penalty_statuses.append(ally)

                if ally.move == 0 or ally.move == 3 or ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS:
                    add_status(ally, Status.MobilityUp)

        # New Year Talon - NY!Hræsvelgr
        if "nyHraesBoost" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 2):
                    add_debuff(foe, SPD, -7)
                    add_debuff(foe, DEF, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Sabotage)

        # Enticing Dose - Níðhöggr
        if "God's strongest drunk driver" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, DEF, -7)
                add_status(foe, Status.Sabotage)

        # Divine Toxin - Níðhöggr
        if "divineToxin" in unitSkills:
            add_status(unit, Status.Dosage)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.Dosage)

        # New Year Fang - NY!Níðhöggr
        if "nySnakeBoost" in unitSkills and allies_within_n_spaces[2]:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Hexblade)
            add_status(unit, Status.DamageReductionPierce50)

            for ally in allies_within_n_spaces[2]:
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.Hexblade)
                add_status(ally, Status.DamageReductionPierce50)

        # Quieting Branch - Læraðr
        if "treePowerActivate" in unitSkills:
            affected_foes = []

            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, DEF, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Panic)
                add_status(foe, Status.Sabotage)

                affected_foes.append(foe)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, DEF, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Panic)
                    add_status(ally, Status.Sabotage)

                    affected_foes.append(ally)

            affected_foes = list(set(affected_foes))

            affected_melee = []
            affected_ranged = []

            for foe in affected_foes:
                if foe.wpnType in MELEE_WEAPONS:
                    affected_melee.append(foe)
                else:
                    affected_ranged.append(foe)

            for foe in units_with_extreme_stat(affected_melee, DEF, find_max=False):
                add_status(foe, Status.Flash)
                add_status(foe, Status.AssignDecoy)

            for foe in units_with_extreme_stat(affected_ranged, DEF, find_max=False):
                add_status(foe, Status.Flash)
                add_status(foe, Status.AssignDecoy)

        # Yggdrasill's Alter - Læraðr
        if "yggdrasillsAlter" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in waiting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -7)
                        add_debuff(foe, DEF, -7)
                        add_status(foe, Status.Discord)

        # Óðr of Creation - Rune
        if "runeBoost" in unitSkills and allies_within_n(unit, 2):
            add_status(unit, Status.Orders)
            add_status(unit, Status.Empathy)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.Orders)
                add_status(ally, Status.Empathy)

        # Font of Wisdom - Rune
        if "fontOfWisdom" in unitSkills:
            for foe in waiting_team:
                if allies_within_n(foe, 2):
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, SPD, -7)
                    add_debuff(foe, RES, -7)

        # Dusk Rifle - Höðr
        if "höðrBoost" in unitSkills:
            add_buff(unit, RES, 6)
            add_status(unit, Status.DamageReductionPierce50)
            add_status(unit, Status.BonusDoubler)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, RES, 6)
                add_status(ally, Status.DamageReductionPierce50)
                add_status(ally, Status.BonusDoubler)

    # Non-HP based AR Structures
    for struct_tile in ar_struct_tiles:
        struct = struct_tile.structure_on
        is_active_phase = struct.struct_type == SIDE + 1
        struct_not_destroyed = struct.health != 0

        if starting_team:
            if starting_team[0].side == 0:
                enemy_team = waiting_team
            else:
                enemy_team = starting_team
        else:
            if waiting_team[0].side == 0:
                enemy_team = starting_team
            else:
                enemy_team = waiting_team

        if struct.name == "Tactics Room" and is_active_phase and struct_not_destroyed:
            if struct.struct_type == 1:
                area = struct_tile.tilesWithinNCols(1)
            else:
                area = struct_tile.tilesWithinNRowsAndCols(7, 3)

            for tile in area:
                if tile.hero_on and tile.hero_on.side + 1 != struct.struct_type and tile.hero_on.HPcur <= get_tower_hp_threshold(struct.level) and tile.hero_on.wpnType in RANGED_WEAPONS:
                    add_status(tile.hero_on, Status.Gravity)

        if struct.name == "Panic Manor" and is_active_phase and struct_not_destroyed:
            if struct.struct_type == 1:
                area = struct_tile.tilesWithinNCols(3)
            else:
                area = struct_tile.tilesWithinNRowsAndCols(7, 3)

            for tile in area:
                if tile.hero_on and tile.hero_on.side + 1 != struct.struct_type and tile.hero_on.HPcur <= get_tower_hp_threshold(struct.level):
                    add_status(tile.hero_on, Status.Panic)

        if struct.name == "Bright Shrine" and is_active_phase and struct_not_destroyed:
            for foe in units_with_extreme_stat_pairing_sum(enemy_team, ATK, SPD):
                add_debuff(foe, ATK, -struct.level - 1)
                add_debuff(foe, SPD, -struct.level - 1)

        if struct.name == "Dark Shrine" and is_active_phase and struct_not_destroyed:
            for foe in units_with_extreme_stat_pairing_sum(enemy_team, DEF, RES):
                add_debuff(foe, DEF, -struct.level - 1)
                add_debuff(foe, RES, -struct.level - 1)

        if struct.name == "Infantry School" and is_active_phase and struct_not_destroyed:
            area = struct_tile.tilesWithinNCols(3)

            for tile in area:
                if tile.hero_on and tile.hero_on.side + 1 != struct.struct_type and tile.hero_on.move == 0:
                    foe = tile.hero_on

                    add_debuff(foe, ATK, -struct.level - 1)
                    add_debuff(foe, SPD, -struct.level - 1)
                    add_debuff(foe, DEF, -struct.level - 1)
                    add_debuff(foe, RES, -struct.level - 1)

        if struct.name == "Cavalry School" and is_active_phase and struct_not_destroyed:
            area = struct_tile.tilesWithinNCols(3)

            for tile in area:
                if tile.hero_on and tile.hero_on.side + 1 != struct.struct_type and tile.hero_on.move == 1:
                    foe = tile.hero_on

                    add_debuff(foe, ATK, -struct.level - 1)
                    add_debuff(foe, SPD, -struct.level - 1)
                    add_debuff(foe, DEF, -struct.level - 1)
                    add_debuff(foe, RES, -struct.level - 1)

        if struct.name == "Flier School" and is_active_phase and struct_not_destroyed:
            area = struct_tile.tilesWithinNCols(3)

            for tile in area:
                if tile.hero_on and tile.hero_on.side + 1 != struct.struct_type and tile.hero_on.move == 2:
                    foe = tile.hero_on

                    add_debuff(foe, ATK, -struct.level - 1)
                    add_debuff(foe, SPD, -struct.level - 1)
                    add_debuff(foe, DEF, -struct.level - 1)
                    add_debuff(foe, RES, -struct.level - 1)

        if struct.name == "Armor School" and is_active_phase and struct_not_destroyed:
            area = struct_tile.tilesWithinNCols(3)

            for tile in area:
                if tile.hero_on and tile.hero_on.side + 1 != struct.struct_type and tile.hero_on.move == 3:
                    foe = tile.hero_on

                    add_debuff(foe, ATK, -struct.level - 1)
                    add_debuff(foe, SPD, -struct.level - 1)
                    add_debuff(foe, DEF, -struct.level - 1)
                    add_debuff(foe, RES, -struct.level - 1)

    # LOOP 2: ENEMY SKILLS
    for unit in waiting_team:
        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur

        unitHPGreaterEqual25Percent = unitHPCur / unitStats[HP] >= 0.25
        unitHPGreaterEqual50Percent = unitHPCur / unitStats[HP] >= 0.50
        unitHPGreaterEqual75Percent = unitHPCur / unitStats[HP] >= 0.75
        unitHPEqual100Percent = unitHPCur == unitStats[HP]

        # PLOY
        if "atkSpdPloy" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, SPD, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Ploy)

        if "atkResPloy" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Ploy)

        if "spdResPloy" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, SPD, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Ploy)

        if "defResPloy" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, DEF, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Ploy)

        if "pulseUpPloy" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Ploy)

        # DISCORD
        if "atkResDiscord" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in starting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -6)
                        add_debuff(foe, RES, -6)
                        add_status(foe, Status.Discord)

        if "spdResDiscord" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in starting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, SPD, -6)
                        add_debuff(foe, RES, -6)
                        add_status(foe, Status.Discord)

        if "defResDiscord" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in starting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, DEF, -6)
                        add_debuff(foe, RES, -6)
                        add_status(foe, Status.Discord)

        # HAVOC
        if "atkResHavoc" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in starting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -7)
                        add_debuff(foe, RES, -7)
                        add_status(foe, Status.Sabotage)
                        add_status(foe, Status.Schism)

        # Carrot Bow
        if "carrotBow" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                if foe.get_visible_stat(DEF) + foe.get_phantom_stat(DEF) < unit.get_visible_stat(DEF) + unit.get_phantom_stat(DEF) + 5:
                    add_debuff(unit, ATK, 7)
                    add_debuff(unit, RES, 7)
                    add_status(foe, Status.Discord)

        # The Fire Emblem - FE!Marth
        if "THE Fire Emblem" in unitSkills and allies_within_n(unit, 2):
            add_buff(unit, OMNI, 7)
            add_status(unit, Status.NullPanic)
            add_status(unit, Status.FireEmblem)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, OMNI, 7)
                add_status(ally, Status.NullPanic)
                add_status(ally, Status.FireEmblem)

        # Wing-Lifted Spear (Refine Eff) - Caeda
        if "LCaedaRefineEffect" in unitSkills and allies_within_n(unit, 2):
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.SpecialCharge)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.SpecialCharge)
                add_status(ally, Status.NullPenalties)

        # Martyr's Staff - FA!Lena
        if "martyrsStaff" in unitSkills and allies_within_n(unit, 3):
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.BonusDoubler)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n(unit, 3):
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.BonusDoubler)
                add_status(ally, Status.NullPenalties)

        # Fundament - Dragon Gotoh
        if "fundies" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.AOEReduce80Percent)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.AOEReduce80Percent)
                add_status(ally, Status.NullBonuses)

        # Ancient Majesty - Dragon Naga
        if "nagaaaaa" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Frozen)
                add_status(foe, Status.Guard)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Frozen)
                    add_status(ally, Status.Guard)

        # Divine God Fang - Dragon Naga
        if "divineGodFang" in unitSkills and allies_within_n(unit, 2):
            add_status(unit, Status.EffDragons)
            add_status(unit, Status.NullEffDragons)
            add_status(unit, Status.Empathy)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.EffDragons)
                add_status(ally, Status.NullEffDragons)
                add_status(ally, Status.Empathy)

        # Ancient Voice - Dragon Tiki
        if "yyTikiBoost" in unitSkills and allies_within_n(unit, 2):
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.Bulwark)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, SPD, 6)
                add_buff(ally, DEF, 6)
                add_status(ally, Status.Bulwark)
                add_status(ally, Status.NullPenalties)

        # Ancient Betrayal - Dragon Medeus
        if "dragonMedeusBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.EnGarde)
            add_status(unit, Status.NullBonuses)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.EnGarde)
                add_status(ally, Status.NullBonuses)

        # Swirling Scimitar - DE!Malice, Jehanna Lance/Dagger
        if ("deMaliceBoost" in unitSkills or "jehannaBoost" in unitSkills) and allies_within_n(unit, 2):
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.Dodge)
            add_status(unit, Status.NullPenalties)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.Dodge)
                add_status(ally, Status.NullPenalties)

        # Jokers Wild (Refine Eff) - Xane
        if "xaneStuff!" in unitSkills:
            for ally in allies_within_n(unit, 3):
                add_buff(ally, OMNI, 6)
                add_status(ally, Status.Hexblade)
                add_status(ally, Status.NullPanic)

        # Ancient Trickery - Dragon Xane
        if "xanerific" in unitSkills:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Sabotage)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Sabotage)

        # Spirit Forest Writ (Refine Eff) - L!Deirdre
        if "Jovial Merryment" in unitSkills and allies_within_n(unit, 2):
            add_buff(unit, ATK, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.NullPenalties)

            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 1

            for ally in allies_within_n(unit, 2):
                add_buff(ally, ATK, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.NullPenalties)

                if ally.specialCount == ally.specialMax:
                    sp_charges[ally] += 1

        # Dark Scripture (Refine Base) - FA!Julia
        if "juliaFallenRefine" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                if foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) < unit.get_visible_stat(RES) + unit.get_phantom_stat(RES):
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Sabotage)
                    add_status(foe, Status.DeepWounds)
                    add_status(foe, Status.NullMiracle)

        # Silesse Frost (Refine Eff) - Erinys
        if "stabbitystabbitystabstab" in unitSkills and allies_within_n(unit, 2):
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_status(unit, Status.SpecialCharge)
            add_status(unit, Status.Dodge)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, ATK, 6)
                add_buff(ally, SPD, 6)
                add_status(ally, Status.SpecialCharge)
                add_status(ally, Status.Dodge)

        # I Remember... - Brigid
        if "iRememberYou'reNeutrals" in unitSkills and allies_within_n(unit, 2):
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, SPD, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.Panic)
                add_status(foe, Status.Sabotage)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, SPD, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.Panic)
                    add_status(ally, Status.Sabotage)

        # Light of Etruria - Elffin
        if "elffinBoost" in unitSkills:
            add_buff(unit, SPD, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Hexblade)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, SPD, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.Hexblade)

            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Guard)

        # Fellowship Blade - X!Hector
        if "xHectorBoost" in unitSkills and allies_within_n(unit, 2):
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.NullPanic)
            add_status(unit, Status.Bulwark)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.NullPanic)
                add_status(ally, Status.Bulwark)

        # Wild Wind Sword - Forde
        if "fordeBoost" in unitSkills:
            add_debuff(unit, SPD, -7)
            add_debuff(unit, DEF, -7)

        # Darkling Guard II - L!Myrrh
        if "darklingGuardianII" in unitSkills:
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.DenyFollowUp)
            add_status(unit, Status.NullEffFliers)
            add_status(unit, Status.WarpBubble)
            add_status(unit, Status.Bulwark)

            if any([unit.isSupportOf(ally) for ally in waiting_team]):
                for ally in allies_within_n(unit, 3):
                    if unit.isSupportOf(ally):
                        add_buff(ally, DEF, 6)
                        add_buff(ally, RES, 6)
                        add_status(ally, Status.DenyFollowUp)
                        add_status(ally, Status.NullEffFliers)
                        add_status(ally, Status.WarpBubble)
                        add_status(ally, Status.Bulwark)

            else:
                for ally in units_with_extreme_stat(waiting_team, DEF, exclude=unit):
                    add_buff(ally, DEF, 6)
                    add_buff(ally, RES, 6)
                    add_status(ally, Status.DenyFollowUp)
                    add_status(ally, Status.NullEffFliers)
                    add_status(ally, Status.WarpBubble)
                    add_status(ally, Status.Bulwark)

        # Icy Ravager - WI!Fomortiis
        if "satanSavesChristmas" in unitSkills and unit.specialCount == unit.specialMax:
            sp_charges[unit] += 1

        # Swirling Lance - DE!Ike
        if "jehannaIkeBoost" in unitSkills and allies_within_n(unit, 2):
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)
            add_status(unit, Status.Outspeeding)
            add_status(unit, Status.NullPanic)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, SPD, 6)
                add_buff(ally, DEF, 6)
                add_status(ally, Status.Outspeeding)
                add_status(ally, Status.NullPanic)

        # Tome of Despair - FA!M!Morgan
        if "among uhhs" in unitSkills and unitHPGreaterEqual25Percent:
            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, RES, -7)
                add_status(foe, Status.HushSpectrum)
                add_status(foe, Status.Ploy)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, RES, -7)
                    add_status(ally, Status.HushSpectrum)
                    add_status(ally, Status.Ploy)

        # Blade of Favors (Base) - Gregor
        if "gregorSword!" in unitSkills and foes_within_n_cardinal(unit, 3):
            add_buff(unit, ATK, 6)
            add_buff(unit, SPD, 6)
            add_buff(unit, DEF, 6)

            for foe in foes_within_n_cardinal(unit, 3):
                add_debuff(foe, ATK, -6)
                add_debuff(foe, SPD, -6)
                add_debuff(foe, DEF, -6)

        # Duskstone - CH!M!Corrin
        if "chCorrinBoost" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.DraconicHex)

            if unit.specialCount == unit.specialMax:
                sp_charges[unit] += 1

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.DraconicHex)

        # Axe of Dusk - CH!Camilla
        if "chCamillaBoost" in unitSkills:
            for foe in starting_team:
                if allies_within_n(foe, 2):
                    add_debuff(foe, SPD, -7)
                    add_debuff(foe, DEF, -7)
                    add_status(foe, Status.Discord)
                    add_status(foe, Status.DeepWounds)

        # Duskbloom Bow (Base) - V!Leo
        if "vLeoBoost" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 1):
                if unit.get_visible_stat(RES) + unit.get_phantom_stat(RES) > foe.get_visible_stat(RES) + foe.get_phantom_stat(RES):
                    add_debuff(foe, DEF, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Gravity)

        # Icy Fimbulvetr (Refine Base) - Marianne
        if "marianneCanto" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in starting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -7)
                        add_debuff(foe, RES, -7)
                        add_status(foe, Status.Exposure)
                        add_status(foe, Status.Guard)

        # Banshee Θ (Refine Eff) - Solon
        if "So joining Smash consumes even the darkness itself?" in unitSkills:
            for foe in starting_team:
                if foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) < unit.get_visible_stat(RES) + unit.get_phantom_stat(RES) and allies_within_n(foe, 2):
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, RES, -7)
                    add_status(foe, Status.Sabotage)

        # Fell Blast - FA!F!Alear
        if "fellBlast" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.FellSpirit)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.FellSpirit)

        # Bond Breaker - FA!M!Alear
        if "bondBreaker" in unitSkills and unitHPGreaterEqual25Percent:
            add_status(unit, Status.FellSpirit)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.FellSpirit)

            for foe in nearest_foes_within_n(unit, 20):
                add_debuff(foe, ATK, -7)
                add_debuff(foe, SPD, -7)
                add_status(foe, Status.Schism)

                for ally in allies_within_n(foe, 2):
                    add_debuff(ally, ATK, -7)
                    add_debuff(ally, SPD, -7)
                    add_status(ally, Status.Schism)

        # Gentle Fell Egg - SP!Veyle
        if "spVeyleBoost" in unitSkills and allies_within_n(unit, 2):
            add_status(unit, Status.AOEReduce80Percent)
            add_status(unit, Status.ResonanceBlades)
            add_status(unit, Status.ResonanceShields)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.AOEReduce80Percent)
                add_status(ally, Status.ResonanceBlades)
                add_status(ally, Status.ResonanceShields)

        # Inspirited Spear - H!Timerra
        if "meat" in unitSkills:
            unit_def = unit.get_visible_stat(DEF) + unit.get_phantom_stat(DEF)

            for foe in foes_within_n_cardinal(unit, 3):
                add_status(foe, Status.Guard)

                foe_def = foe.get_visible_stat(DEF) + foe.get_phantom_stat(DEF)

                if foe_def < unit_def and foe.getSpecialType() in ["Offense", "AOE"] and foe.specialCount <= 1:
                    sp_charges[foe] -= 1

        # Connected World - H!Askr
        if "connectedWorld" in unitSkills:
            ally_cond = False

            for ally in allies_within_n(unit, 3):
                if ally.primary_game != unit.primary_game or (ally.secondary_game != unit.primary_game and ally.secondary_game != -1):
                    ally_cond = True
                    break

            if ally_cond:
                add_buff(unit, ATK, 6)
                add_buff(unit, DEF, 6)
                add_status(unit, Status.ResonanceBlades)
                add_status(unit, Status.ResonanceShields)
                add_status(unit, Status.DamageReductionPierce50)

                if unit.specialCount == unit.specialMax:
                    sp_charges[unit] += 1

                for ally in allies_within_n(unit, 3):
                    add_buff(ally, ATK, 6)
                    add_buff(ally, DEF, 6)
                    add_status(ally, Status.ResonanceBlades)
                    add_status(ally, Status.ResonanceShields)
                    add_status(ally, Status.DamageReductionPierce50)

                    if ally.specialCount == ally.specialMax:
                        sp_charges[ally] += 1

        # Divine Deceit - Loki
        if "divineDeceit" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)
            n_cardinal_1 = foes_within_n_cardinal(unit, 1)

            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_status(foe, Status.Ploy)
                    add_status(foe, Status.Exposure)

                    if foe in n_cardinal_1:
                        add_status(foe, Status.Gravity)

        # Nectar Horn - Heiðrún
        if "heiðrúnBoost" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, DEF, -7)
                    add_status(foe, Status.Discord)
                    add_status(foe, Status.DeepWounds)
                    add_status(foe, Status.NullMiracle)

        # Divine Nectar - Heiðrún
        if ("divineNectar" in unitSkills or "nectarsMagic" in unitSkills) and allies_within_n(unit, 2):
            add_status(unit, Status.DivineNectar)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.DivineNectar)

        # New Year Talon - NY!Hræsvelgr
        if "nyHraesBoost" in unitSkills:
            for foe in starting_team:
                if allies_within_n(foe, 2):
                    add_debuff(foe, SPD, -7)
                    add_debuff(foe, DEF, -7)
                    add_status(foe, Status.Exposure)
                    add_status(foe, Status.Sabotage)

        # Divine Toxin - Níðhöggr
        if "divineToxin" in unitSkills:
            add_status(unit, Status.Dosage)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.Dosage)

        # New Year Fang - NY!Níðhöggr
        if "nySnakeBoost" in unitSkills and allies_within_n(unit, 2):
            add_buff(unit, DEF, 6)
            add_buff(unit, RES, 6)
            add_status(unit, Status.Hexblade)
            add_status(unit, Status.DamageReductionPierce50)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, DEF, 6)
                add_buff(ally, RES, 6)
                add_status(ally, Status.Hexblade)
                add_status(ally, Status.DamageReductionPierce50)

        # Yggdrasill's Alter - Læraðr
        if "yggdrasillsAlter" in unitSkills:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in starting_team:
                if allies_within_n(foe, 2):
                    foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                    if foe_res < unit_res:
                        add_debuff(foe, ATK, -7)
                        add_debuff(foe, DEF, -7)
                        add_status(foe, Status.Discord)

        # Óðr of Creation - Rune
        if "runeBoost" in unitSkills and allies_within_n(unit, 2):
            add_status(unit, Status.Orders)
            add_status(unit, Status.Empathy)

            for ally in allies_within_n(unit, 2):
                add_status(ally, Status.Orders)
                add_status(ally, Status.Empathy)

        # Font of Wisdom - Rune
        if "fontOfWisdom" in unitSkills:
            for foe in starting_team:
                if allies_within_n(foe, 2):
                    add_debuff(foe, ATK, -7)
                    add_debuff(foe, SPD, -7)
                    add_debuff(foe, RES, -7)

        # Dusk Rifle - Höðr
        if "höðrBoost" in unitSkills:
            add_buff(unit, RES, 6)
            add_status(unit, Status.DamageReductionPierce50)
            add_status(unit, Status.BonusDoubler)

            for ally in allies_within_n(unit, 2):
                add_buff(ally, RES, 6)
                add_status(ally, Status.DamageReductionPierce50)
                add_status(ally, Status.BonusDoubler)

    # Clear bonuses/penalties at start of turn (but not during)
    for unit in clear_bonus_stats:
        unit.buffs = [0] * 5

    for unit in clear_bonus_statuses:
        unit.statusPos = []

    for unit in clear_penalty_stats:
        unit.debuffs = [0] * 5

    for unit in clear_penalty_statuses:
        unit.statusNeg = []

    # Apply stat buffs to all affected units
    for unit in units_stored_buffs.keys():
        i = 1
        while i < len(units_stored_buffs[unit]):
            unit.inflictStat(i, units_stored_buffs[unit][i])
            i += 1

    # Apply stat debuffs to all affected units
    for unit in units_stored_debuffs.keys():
        i = 1
        while i < len(units_stored_debuffs[unit]):
            unit.inflictStat(i, units_stored_debuffs[unit][i])
            i += 1

    # Apply status effects to all affected units
    for unit in units_stored_statuses.keys():
        for status in units_stored_statuses[unit]:
            unit.inflictStatus(status)

    # Apply special count changes to all affected units
    for unit in sp_charges:
        unit.chargeSpecial(sp_charges[unit])

    # Apply Great Talent
    for unit in units_stored_great_talent:
        great_talent_arr = sorted(units_stored_great_talent[unit], key=lambda x: x[2])

        for stat, val, cap in great_talent_arr:
            unit.inflictGreatTalent(stat, val, cap)

    # LOOP 3: CLEANSING SKILLS, PLAYER TEAM
    # These apply at start of turn and apply to any effects "that take effect on unit at this time"
    for unit in starting_team:

        if Status.FalseStart in unit.statusNeg:
            continue

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur

        if "l&d_detox" in unitSkills:
            unit.debuffs[ATK] = 0
            unit.debuffs[SPD] = 0

            if Status.Panic in unit.statusNeg:
                unit.statusNeg.remove(Status.Panic)

        if "sw_detox" in unitSkills:
            unit.debuffs[ATK] = 0
            unit.debuffs[RES] = 0

            if Status.Panic in unit.statusNeg:
                unit.statusNeg.remove(Status.Panic)

        if "fdr_detox" in unitSkills:
            unit.debuffs[DEF] = 0
            unit.debuffs[RES] = 0

            if Status.Panic in unit.statusNeg:
                unit.statusNeg.remove(Status.Panic)

        if "giantAxe" in unitSkills:
            unit.debuffs[ATK] = 0
            unit.debuffs[DEF] = 0

            if Status.Panic in unit.statusNeg:
                unit.statusNeg.remove(Status.Panic)

        # Dream Deliverer
        if "dreamDeliverer" in unitSkills and allies_within_n(unit, 2):
            unit.debuffs = [0, 0, 0, 0, 0]
            unit.statusNeg.clear()

            for ally in allies_within_n(unit, 2):
                ally.debuffs = [0, 0, 0, 0, 0]
                ally.statusNeg.clear()

    # LOOP 4: CLEANSING SKILLS, ENEMY TEAM
    for unit in waiting_team:

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur

        if "l&d_detox" in unitSkills:
            unit.debuffs[ATK] = 0
            unit.debuffs[SPD] = 0

            if Status.Panic in unit.statusNeg:
                unit.statusNeg.remove(Status.Panic)

        if "sw_detox" in unitSkills:
            unit.debuffs[ATK] = 0
            unit.debuffs[RES] = 0

            if Status.Panic in unit.statusNeg:
                unit.statusNeg.remove(Status.Panic)

        if "fdr_detox" in unitSkills:
            unit.debuffs[DEF] = 0
            unit.debuffs[RES] = 0

            if Status.Panic in unit.statusNeg:
                unit.statusNeg.remove(Status.Panic)

        if "giantAxe" in unitSkills:
            unit.debuffs[ATK] = 0
            unit.debuffs[DEF] = 0

            if Status.Panic in unit.statusNeg:
                unit.statusNeg.remove(Status.Panic)

        # Dream Deliverer
        if "dreamDeliverer" in unitSkills and allies_within_n(unit, 2):
            unit.debuffs = [0, 0, 0, 0, 0]
            unit.statusNeg.clear()

            for ally in allies_within_n(unit, 2):
                ally.debuffs = [0, 0, 0, 0, 0]
                ally.statusNeg.clear()

    # Set defaults
    damage_taken = {}
    heals_given = {}

    for unit in starting_team + waiting_team:
        damage_taken[unit] = 0
        heals_given[unit] = 0

    # LOOP 5: DAMAGE AND HEALING, PLAYER TEAM
    for unit in starting_team:
        if Status.FalseStart in unit.statusNeg:
            continue

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

        # Divine Vein Flame
        if unit.tile.divine_vein == DV_FLAME and unit.tile.divine_vein_side != unit.side and unit.tile.divine_vein_turn > 0:
            damage_taken[unit] += 7

        # Renewal
        if "recoverW" in unitSkills:
            if (turn - 1) % (5 - unitSkills["recoverW"]) == 0:
                heals_given[unit] += 10

        if "recoverSk" in unitSkills:
            if (turn - 1) % (5 - unitSkills["recoverSk"]) == 0:
                heals_given[unit] += 10

        if "recoverSe" in unitSkills:
            if (turn - 1) % (5 - unitSkills["recoverSe"]) == 0:
                heals_given[unit] += 10

        # Odd Recovery
        if "odd_recovery" in unitSkills and turn % 2 == 1:
            for ally in allies_within_n_spaces[2]:
                heals_given[ally] += unitSkills["odd_recovery"]

        if "even_recovery" in unitSkills and turn % 2 == 0:
            for ally in allies_within_n_spaces[2]:
                heals_given[ally] += unitSkills["even_recovery"]

        # Ovoid Staff
        if "ovoidHeal" in unitSkills:
            heals_given[unit] += unitSkills["ovoidHeal"]

            for ally in allies_within_n_spaces[1]:
                heals_given[ally] += unitSkills["ovoidHeal"]

        # Luminous Grace/Drifting Grace
        if "crusaderBoost" in unitSkills:
            heals_given[unit] += 10

        # Imhullu - Gharnef
        if "gharnefDmg" in unitSkills and turn == 3:
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(5) if unit.isEnemyOf(tile.hero_on) and tile.hero_on.wpnType not in TOME_WEAPONS]:
                damage_taken[foe] += unitSkills["gharnefDmg"]

        # Beyond Witchery
        if "beyondWitchery" in unitSkills:
            if turn == 1:
                damage_taken[unit] += 2
            else:
                damage_taken[unit] += 1

        # Upheaval(+) - Duma
        if "upheaval" in unitSkills and turn == 1:
            for foe in waiting_team:
                damage_taken[foe] += unitSkills["upheaval"]

        # S Drink - Leif/L!Leif
        if "s_drink" in unitSkills and turn == 1:
            heals_given[unit] += 99

        # Heron Wing - Reyson/Leanne
        if "heronHeal" in unitSkills:
            for ally in allies_within_n_spaces[2]:
                heals_given[ally] += 7

        # Skadi - FA!Takumi
        if "skadiDamage" in unitSkills and turn == 3:
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(3) if tile.hero_on is not None and tile.hero_on.isEnemyOf(unit)]:
                damage_taken[foe] += 10

        if "skadiMoreDamage" in unitSkills and (turn == 2 or turn == 3):
            for foe in [tile.hero_on for tile in tile.tilesWithinNCols(3) if tile.hero_on is not None and tile.hero_on.isEnemyOf(unit)]:
                damage_taken[foe] += 7

        # Lucky Bow (Refine Eff) - Midori
        if "Medicine!" in unitSkills and allies_within_n_spaces[2]:
            heals_given[unit] += 10

            for ally in allies_within_n_spaces[2]:
                heals_given[ally] += 10

        if "garonAbsorb" in unitSkills and turn == 3:
            for foe in foes_within_n_spaces[3]:
                damage_taken[foe] += 10

            heals_given[unit] += len(foes_within_n_spaces[3]) * 5

        if "garonDevour" in unitSkills and (turn == 3 or turn == 4):
            for foe in foes_within_n_spaces[4]:
                damage_taken[foe] += 14

            heals_given[unit] += len(foes_within_n_spaces[4]) * 14

        # Persecution Bow (Refine Eff) - Bernadetta
        if "rock" in unitSkills and allies_within_n_spaces[2]:
            damage_taken[unit] += 1

            for ally in allies_within_n_spaces[2]:
                damage_taken[ally] += 1

        # Hrist (Base) - WI!Bernadetta
        if "wiBernieBoost" in unitSkills and unitHPEqual100Percent and allies_within_n_spaces[2]:
            damage_taken[unit] += 1

            for ally in allies_within_n_spaces[2]:
                damage_taken[ally] += 1

        # Hrist (Refine Base) - WI!Bernadetta
        if "wiBernieRefine" in unitSkills and allies_within_n_spaces[2]:
            damage_taken[unit] += 1

            for ally in allies_within_n_spaces[2]:
                damage_taken[ally] += 1

        # Paranoia - B!Bernadetta
        if "paranoia" in unitSkills:
            damage_taken[unit] += 1

            for ally in allies_within_n_spaces[2]:
                damage_taken[ally] += 1

        # Bow of Repose (Base) - SP!Bernadetta
        if "spBernieBoost" in unitSkills and unitHPEqual100Percent and allies_within_n_spaces[2]:
            damage_taken[unit] += 1

            for ally in allies_within_n_spaces[2]:
                damage_taken[ally] += 1

        # Dark Spikes T (Refine Eff) - B!Lysithea
        if "lysitheaSchmovement" in unitSkills:
            damage_taken[unit] += 1

        # Mastermind - T!Lysithea
        if "mastermind" in unitSkills:
            damage_taken[unit] += 1

        if "sharenaHealing" in unitSkills:
            heals_given[unit] += 7

            for ally in allies_within_n_spaces[2]:
                heals_given[ally] += 7

        # True Dragon Wall - Rhea/FA!Rhea
        if "trueDragonWall" in unitSkills and any([ally.wpnType in DRAGON_WEAPONS for ally in allies_within_n(unit, 20)]):
            heals_given[unit] += 7

        # Pure Dragon Wall - V!Rhea
        if "pureDragonWall" in unitSkills and any([ally.wpnType in DRAGON_WEAPONS for ally in allies_within_n(unit, 20)]):
            heals_given[unit] += 10

        # Joyous Tome (Base) - Céline
        if "célineBoost" in unitSkills and allies_within_n_spaces[3]:
            heals_given[unit] += 7

            for ally in allies_within_n_spaces[3]:
                heals_given[ally] += 7

        # Hippity-Hop Axe - SP!Framme
        if "It's a shuffling in the seat." in unitSkills and allies_within_n_spaces[2]:
            heals_given[unit] += 7

            for ally in allies_within_n_spaces[2]:
                heals_given[ally] += 7

        # Sinmara (Base) - Surtr
        if "surtrBurn" in unitSkills:
            for foe in foes_within_n_spaces[2]:
                damage_taken[foe] += 20

        # Sparkling Boost - Eir
        if "sparklingBoost" in unitSkills:
            most_hp_missing = 0
            affected_units = []

            for ally in starting_team:
                if ally != unit:
                    if ally.visible_stats[HP] - ally.HPcur < most_hp_missing:
                        affected_units.clear()
                        affected_units.append(ally)
                    elif ally.visible_stats[HP] - ally.HPcur == most_hp_missing:
                        affected_units.append(ally)

            if most_hp_missing != 0:
                for ally in affected_units:
                    heals_given[ally] += unitSkills["sparklingBoost"]

        # Divine Talon - Hræsvelgr
        if "divineTalon" in unitSkills:
            damage_taken[unit] += 1

            for ally in allies_within_n(unit, 2):
                damage_taken[ally] += 1

    # LOOP 6: DAMAGE AND HEALING, ENEMY TEAM
    for unit in waiting_team:
        if Status.FalseStart in unit.statusNeg: continue

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur

        unitHPGreaterEqual25Percent = unitHPCur / unitStats[0] >= 0.25
        unitHPGreaterEqual50Percent = unitHPCur / unitStats[0] >= 0.50
        unitHPGreaterEqual75Percent = unitHPCur / unitStats[0] >= 0.75
        unitHPEqual100Percent = unitHPCur == unitStats[0]

        # Scroll of Teas - NI!Céline
        if "niCelineBoost" in unitSkills:
            heals_given[unit] += 10

            for ally in allies_within_n(unit, 3):
                heals_given[ally] += 10

        if "silverOfDawn" in unitSkills:
            heals_given[unit] += 10

            for ally in allies_within_n(unit, 2):
                heals_given[ally] += 10

    # if Status.FalseStart in unit.statusNeg: continue

    # Damage-based start-of-turn structures
    for struct_tile in ar_struct_tiles:
        struct = struct_tile.structure_on

        if struct.name == "Bolt Tower" and turn == 3 and struct.struct_type == SIDE + 1 and struct.health != 0:
            if struct.struct_type == 1:
                area = struct_tile.tilesWithinNCols(3)
            else:
                area = struct_tile.tilesWithinNRowsAndCols(7, 3)

            for tile in area:
                if tile.hero_on and tile.hero_on.side + 1 != struct.struct_type:
                    damage_taken[tile.hero_on] += get_tower_hp_change(struct.level)

        if struct.name == "Healing Tower" and struct.struct_type == SIDE + 1 and struct.health != 0:
            if struct.struct_type == 1:
                area = struct_tile.tilesWithinNRowsAndCols(3, 5)
            else:
                area = struct_tile.tilesWithinNRowsAndCols(5, 5)

            for tile in area:
                if tile.hero_on and tile.hero_on.side + 1 == struct.struct_type:
                    heals_given[tile.hero_on] += get_tower_hp_change(struct.level)

    # Set damage taken/heals given to empty values if no damage done
    for unit in starting_team + waiting_team:
        if damage_taken[unit] == 0:
            damage_taken[unit] = -1
        if heals_given[unit] == 0:
            heals_given[unit] = -1

    # Deal start-of-turn damage
    for unit in starting_team + waiting_team:
        heal_amount = 0
        damage_amount = 0

        if unit in heals_given and heals_given[unit] != -1 and Status.DeepWounds not in unit.statusNeg:
            heal_amount = heals_given[unit]

        if unit in damage_taken and damage_taken[unit] != -1 and Status.EnGarde not in unit.statusPos:
            damage_amount = damage_taken[unit]

        if damage_amount >= heal_amount and (damage_amount > 0 or heal_amount > 0):
            unit.HPcur = max(1, unit.HPcur + (heal_amount - damage_amount))
        elif damage_amount < heal_amount and (damage_amount > 0 or heal_amount > 0):
            unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + (heal_amount - damage_amount))


    # Store all buffs/debuffs for after start of turn
    units_stored_buffs = {}
    units_stored_debuffs = {}
    units_stored_statuses = {}

    for unit in starting_team + waiting_team:
        units_stored_buffs[unit] = [0] * 5
        units_stored_debuffs[unit] = [0] * 5
        units_stored_statuses[unit] = []

    clear_bonus_statuses = []
    clear_bonus_stats = []

    clear_penalty_statuses = []
    clear_penalty_stats = []

    # LOOP 7: AFTER START OF TURN SKILLS, PLAYER TEAM
    for unit in starting_team:

        if Status.FalseStart in unit.statusNeg: continue

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur

        # Havoc
        if "atkResHavoc" in unitSkills:
            foe_count = 0

            for foe in waiting_team:
                if Status.Sabotage in foe.statusNeg:
                    foe_count += 1

            if foe_count >= 2:
                add_status(unit, Status.Canto1)

        if "fettersODromi" in unitSkills and Status.Stall in unit.statusNeg and Status.MobilityUp in unit.statusPos:
            unit.statusNeg.remove(Status.MobilityUp)

        # Tome of Luxuries - Cirtinne
        if "citrinneBoost" in unitSkills and unitHPCur / unitStats[HP] >= 0.25:
            for status in unit.statusPos:
                if status != Status.MobilityUp and status != Status.Pathfinder:
                    for ally in allies_within_n(unit, 2):
                        add_status(ally, status)

        # Divine Deceit - Loki
        if "divineDeceit" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                if len(foe.statusPos) >= 3 and foe not in clear_bonus_statuses:
                    clear_bonus_statuses.append(foe)

        # Quieting Antler - Eikþyrnir
        if ("eikBoost" in unitSkills or "wiEikBoost" in unitSkills) and allies_within_n(unit, 2):
            for i in range(1, 5):
                if unit.buffs[i]:
                    add_buff(unit, i, min(unit.buffs[i] + 3, 10))

            for ally in allies_within_n(unit, 2):
                for i in range(1, 5):
                    if ally.buffs[i]:
                        add_buff(ally, i, min(ally.buffs[i] + 3, 10))

        # Divine Strength - Eikþyrnir
        if "divineStrength" in unitSkills:
            clear_penalty_statuses.append(unit)
            clear_penalty_stats.append(unit)

    # LOOP 8: AFTER START OF TURN SKILLS, ENEMY TEAM
    for unit in waiting_team:

        if Status.FalseStart in unit.statusNeg: continue

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur

        # Silver of Dawn - X!Micaiah
        if "silverOfDawn" in unitSkills:
            first_two_debuffs = sorted(unit.statusNeg, key=lambda e: e.value)[:2]

            for status in first_two_debuffs:
                unit.statusNeg.remove(status)

            for i in range(1, 5):
                add_buff(unit, i, -unit.debuffs[i])

            if unit not in clear_penalty_stats:
                clear_penalty_stats.append(unit)

            for ally in allies_within_n(unit, 2):
                first_two_debuffs = sorted(ally.statusNeg, key=lambda e: e.value)[:2]

                for status in first_two_debuffs:
                    ally.statusNeg.remove(status)

                for i in range(1, 5):
                    add_buff(ally, i, -ally.debuffs[i])

                if ally not in clear_penalty_stats:
                    clear_penalty_stats.append(ally)

        # Scroll of Teas - NI!Céline
        if "niCelineBoost" in unitSkills:
            first_two_debuffs = sorted(unit.statusNeg, key=lambda e: e.value)[:2]

            for status in first_two_debuffs:
                unit.statusNeg.remove(status)

            for i in range(1, 5):
                add_buff(unit, i, -unit.debuffs[i])

            if unit not in clear_penalty_stats:
                clear_penalty_stats.append(unit)

            for ally in allies_within_n(unit, 3):
                first_two_debuffs = sorted(ally.statusNeg, key=lambda e: e.value)[:2]

                for status in first_two_debuffs:
                    ally.statusNeg.remove(status)

                for i in range(1, 5):
                    add_buff(ally, i, -ally.debuffs[i])

                if ally not in clear_penalty_stats:
                    clear_penalty_stats.append(ally)

        # Divine Deceit - Loki
        if "divineDeceit" in unitSkills:
            for foe in foes_within_n_cardinal(unit, 3):
                if len(foe.statusPos) >= 3 and foe not in clear_bonus_statuses:
                    clear_bonus_statuses.append(foe)

        # Divine Strength - Eikþyrnir
        if "divineStrength" in unitSkills:
            clear_penalty_statuses.append(unit)
            clear_penalty_stats.append(unit)

        # Sun Sword - Baldr
        if "DESUWA" in unitSkills:
            for foe in nearest_foes_within_n(unit, 20):
                clear_bonus_stats.append(foe)
                for i in range(1, 5):
                    add_debuff(foe, i, -foe.buffs[i])

                for ally in allies_within_n(foe, 2):
                    clear_bonus_stats.append(ally)
                    for i in range(1, 5):
                        add_debuff(ally, i, -ally.buffs[i])

        # Dusk Rifle - Höðr
        if "höðrBoost" in unitSkills:
            first_two_debuffs = sorted(unit.statusNeg, key=lambda e: e.value)[:2]

            for status in first_two_debuffs:
                unit.statusNeg.remove(status)

            for i in range(1, 5):
                add_buff(unit, i, -unit.debuffs[i])

            if unit not in clear_penalty_stats:
                clear_penalty_stats.append(unit)

            for ally in allies_within_n(unit, 2):
                first_two_debuffs = sorted(ally.statusNeg, key=lambda e: e.value)[:2]

                for status in first_two_debuffs:
                    ally.statusNeg.remove(status)

                for i in range(1, 5):
                    add_buff(ally, i, -ally.debuffs[i])

                if ally not in clear_penalty_stats:
                    clear_penalty_stats.append(ally)

    for unit in clear_bonus_stats:
        unit.buffs = [0] * 5

    for unit in clear_bonus_statuses:
        unit.statusPos = []

    for unit in clear_penalty_stats:
        unit.debuffs = [0] * 5

    for unit in clear_penalty_statuses:
        unit.statusNeg = []

    # Apply stat buffs to all affected units after start-of-turn
    for unit in units_stored_buffs.keys():
        i = 1
        while i < len(units_stored_buffs[unit]):
            unit.inflictStat(i, units_stored_buffs[unit][i])
            i += 1

    # Apply stat debuffs to all affected units after start-of-turn
    for unit in units_stored_debuffs.keys():
        i = 1
        while i < len(units_stored_debuffs[unit]):
            unit.inflictStat(i, units_stored_debuffs[unit][i])
            i += 1

    # Apply status effects given after start-of-turn
    for unit in units_stored_statuses.keys():
        for status in units_stored_statuses[unit]:
            unit.inflictStatus(status)

    divine_veins = {}

    # DIVINE VEINS
    for unit in starting_team:
        if Status.FalseStart in unit.statusNeg: continue

        unitSkills = unit.getSkills()

        # Tut-Tut! - CH!Camilla
        if "tut-tut" in unitSkills and unit.HPcur / unit.get_visible_stat(HP) >= 0.25:
            if (unit.side, "haze") not in divine_veins:
                divine_veins[(unit.side, "haze")] = []

            for foe in nearest_foes_within_n(unit, 5):
                for tile in foe.tile.tilesWithinNSpaces(2):
                    divine_veins[(unit.side, "haze")].append(tile.tileNum)

    for unit in waiting_team:
        if Status.FalseStart in unit.statusNeg: continue

        unitSkills = unit.getSkills()

        # Oath of Ostia - X!Hector
        if "oathOfOstia" in unitSkills and game_mode == GameMode.AetherRaids:
            if (unit.side, "stone") not in divine_veins:
                divine_veins[(unit.side, "stone")] = []

            for tile in unit.tile.tilesWithinNSpaces(2):
                divine_veins[(unit.side, "stone")].append(tile.tileNum)

        # Exalt's Tactics - B!F!Robin
        if "exaltsTactics" in unitSkills and game_mode == GameMode.AetherRaids:
            ice_present = False

            for tile in unit.tile.tilesWithinNSpaces(20):
                if tile.divine_vein == DV_ICE and tile.divine_vein_side == unit.side and tile.divine_vein_turn > 0:
                    ice_present = True

            if not ice_present:
                if (unit.side, "ice") not in divine_veins:
                    divine_veins[(unit.side, "ice")] = []

                for tile in unit.tile.tilesNSpacesAway(2):
                    divine_veins[(unit.side, "ice")].append(tile.tileNum)

        # Taciturn Axe (Refine Eff) - Dedue
        if "taciturnAxe" in unitSkills and game_mode == GameMode.AetherRaids:
            if (unit.side, "stone") not in divine_veins:
                divine_veins[(unit.side, "stone")] = []

            for tile in unit.tile.tilesWithinNSpaces(2):
                divine_veins[(unit.side, "stone")].append(tile.tileNum)

    # END ACTION EFFECTS
    cancel_action = []

    # Safety Fence
    trigger_safety_fence = False

    # LOOP 9: END ACTION EFFECTS, STARTING TEAM
    # i think it's just the CancelAction status, so yeah
    for unit in starting_team:
        if Status.CancelAction in unit.statusNeg and not any([ally for ally in (allies_within_n(unit, 3) + [unit]) if "cantoCurbStomp" in ally.getSkills()]):
            cancel_action.append(unit)
            unit.statusNeg.remove(Status.CancelAction)

    for struct_tile in ar_struct_tiles:
        struct = struct_tile.structure_on

        if struct.name == "Safety Fence" and turn <= struct.level and SIDE == 1 and struct.health != 0:
            trigger_safety_fence = True

            # Calculate threat range of each unit on defending team
            for unit in starting_team:
                if unit.weapon is None: # ignore unarmed units
                    continue

                move_tiles = get_regular_moves(unit, starting_team, waiting_team)[0]

                for movement in move_tiles:
                    atk_range_at_movement = game_map.tiles[movement].tilesNSpacesAway(unit.weapon.range)

                    for atk_tile in atk_range_at_movement:
                        if unit.isEnemyOf(atk_tile.hero_on) and not (abs(atk_tile.x_coord - struct_tile.x_coord) <= 3 and abs(atk_tile.y_coord - struct_tile.y_coord) <= 1):
                            trigger_safety_fence = False

                style_present, style_name = unit.get_style_conditions(turn)

                if len(style_name) == 1:
                    style = style_name[0]

                    style_move_tiles = get_regular_moves(unit, starting_team, waiting_team, style=style)[0]

                    for movement in move_tiles:
                        attack_range = []

                        if style == "ASTRA-STORM":
                            attack_range = list(set(game_map.tiles[movement].tilesWithinNSpaces(6)) & set(game_map.tiles[movement].tilesWithinNRowsOrCols(3, 3)))
                        elif style == "EMBLEM-LYN":
                            attack_range = list(set(game_map.tiles[movement].tilesWithinNSpaces(5)) & set(game_map.tiles[movement].tilesWithinNRowsOrCols(3, 3)))
                        elif style == "WIND-SWORD":
                            attack_range = game_map.tiles[movement].tilesNSpacesAway(2)

                        for atk_tile in attack_range:
                            if unit.isEnemyOf(atk_tile.hero_on) and not (abs(atk_tile.x_coord - struct_tile.x_coord) <= 3 and abs(atk_tile.y_coord - struct_tile.y_coord) <= 1):
                                trigger_safety_fence = False

    if trigger_safety_fence:
        for unit in starting_team:
            cancel_action.append(unit)

    # LOOP 10: END ACTION EFFECTS, ENEMY TEAM
    for unit in waiting_team:

        if Status.FalseStart in unit.statusNeg: continue

        unitSkills = unit.getSkills()
        unitStats = unit.getStats()
        unitHPCur = unit.HPcur

        if "futureFocused" in unitSkills and turn % 2 == 1:
            min_dist = 100
            targeted_foes = []

            for foe in foes_within_n_cardinal(unit, 1):
                distance = abs(foe.tile.x_coord - unit.tile.x_coord) + abs(foe.tile.y_coord - unit.tile.y_coord)

                if distance < min_dist:
                    targeted_foes = [foe]
                    min_dist = distance
                elif distance == min_dist:
                    targeted_foes.append(foe)

            for foe in targeted_foes:
                if unit.get_visible_stat(RES) + unit.get_phantom_stat(RES) >= foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) + (min_dist * 3):
                    if not any([ally for ally in (allies_within_n(foe, 3) + [foe]) if "cantoCurbStomp" in ally.getSkills()]):
                        cancel_action.append(foe)

        if "futureSighted" in unitSkills:
            min_dist = 100
            targeted_foes = []

            for foe in foes_within_n_cardinal(unit, 1):
                distance = abs(foe.tile.x_coord - unit.tile.x_coord) + abs(foe.tile.y_coord - unit.tile.y_coord)

                if distance < min_dist:
                    targeted_foes = [foe]
                    min_dist = distance
                elif distance == min_dist:
                    targeted_foes.append(foe)

            for foe in targeted_foes:
                if unit.get_visible_stat(RES) + unit.get_phantom_stat(RES) >= foe.get_visible_stat(RES) + foe.get_phantom_stat(RES) + (min_dist * 3) - 5 and Status.TimesGrip not in foe.statusNeg:
                    if not any([ally for ally in (allies_within_n(foe, 3) + [foe]) if "cantoCurbStomp" in ally.getSkills()]):
                        cancel_action.append(foe)
                        foe.inflictStatus(Status.TimesGrip)

    cancel_action = list(set(cancel_action))

    # Invincible Seals
    for unit in damage_taken:
        if "invincible" in unit.getSkills() and damage_taken[unit] > 0:
            damage_taken[unit] = 0

    # return hash maps of units who have had damage dealt or healed, or if their special cooldown was modified
    return damage_taken, heals_given, cancel_action, divine_veins

# Allies within N spaces of unit
def allies_within_n(unit, n):
    unit_list = unit.tile.unitsWithinNSpaces(n)
    returned_list = []

    for x in unit_list:
        if x != unit and unit.side == x.side:
            returned_list.append(x)

    return returned_list

# Nearest allies within N spaces of unit
def nearest_allies_within_n(unit, n):
    i = 1
    while i <= n:
        if allies_within_n(unit, i):
            return allies_within_n(unit, i)
        else:
            i += 1

    return []

# Allies within N rows or columns of unit
def allies_within_n_cardinal(unit, n):
    unit_list = [tile.hero_on for tile in unit.tile.tilesWithinNRowsOrCols(n, n) if tile.hero_on is not None]
    returned_list = []

    for x in unit_list:
        if x.isAllyOf(unit):
            returned_list.append(x)

    return returned_list

# Allies within N rows and columns of unit
def allies_within_n_box(unit, n):
    unit_list = [tile.hero_on for tile in unit.tile.tilesWithinNRowsAndCols(n, n) if tile.hero_on is not None]
    returned_list = []

    for x in unit_list:
        if x.isAllyOf(unit):
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

def foes_within_n_columns(unit, n):
    unit_list = [tile.hero_on for tile in unit.tile.tilesWithinNCols(n, n) if tile.hero_on is not None]
    returned_list = []

    for x in unit_list:
        if x.isEnemyOf(unit):
            returned_list.append(x)

    return returned_list

def foes_within_n_cardinal(unit, n):
    unit_list = [tile.hero_on for tile in unit.tile.tilesWithinNRowsOrCols(n, n) if tile.hero_on is not None]
    returned_list = []

    for x in unit_list:
        if x.isEnemyOf(unit):
            returned_list.append(x)

    return returned_list

def foes_within_n_box(unit, n):
    unit_list = [tile.hero_on for tile in unit.tile.tilesWithinNRowsAndCols(n, n) if tile.hero_on is not None]
    returned_list = []

    for x in unit_list:
        if x.isEnemyOf(unit):
            returned_list.append(x)

    return returned_list

# If unit's movement type allows them to be on a certain type of terrain
def can_be_on_terrain(terrain_int, move_type_int):
    if terrain_int == 0 or terrain_int == 3: return True
    if terrain_int == 4: return False

    if terrain_int == 1:
        if move_type_int == 1: return False
        else: return True

    if terrain_int == 2:
        if move_type_int == 2: return True
        else: return False

# If unit can be on a tile, given terrain or structures
def can_be_on_tile(tile, unit):
    move_type_int = unit.move

    if tile.structure_on:
        if tile.structure_on.health != 0 and ("Trap" not in tile.structure_on.name and "Calling" not in tile.structure_on.name):
            return False

    if tile.divine_vein == DV_ICE and tile.divine_vein_side != unit.side and tile.divine_vein_turn > 0:
        return False

    # Regular ground/trenches
    if tile.terrain == 0 or tile.terrain == 3: return True

    # Impassible terrain
    if tile.terrain == 4: return False

    # Forests
    if tile.terrain == 1:
        if move_type_int == 1: return False
        else: return True

    # Flier-Only
    if tile.terrain == 2:
        if move_type_int == 2: return True
        else: return False

    return True

# The distance a unit can move on a given turn
def allowed_movement(unit):
    move_type = unit.move

    spaces_allowed = 3 - abs(move_type - 1)

    status_bonus_move = 0

    # Movement increased by positive status effects
    if Status.MobilityUp in unit.statusPos:
        status_bonus_move = 1
    if Status.Gallop in unit.statusPos:
        status_bonus_move = 2

    spaces_allowed += status_bonus_move

    # Movement set to 1 by negative status effects
    if Status.Gravity in unit.statusNeg or (Status.MobilityUp in unit.statusPos and Status.Stall in unit.statusNeg):
        spaces_allowed = 1

    return spaces_allowed

def get_obstruct_tiles(unit, enemy_team):
    all_obstruct_tiles = []
    for enemy in enemy_team:
        enemy_skills = enemy.getSkills()

        obstruct_cond = False # within 1 space
        bulwark_cond = False # within 2 space

        if "obstruct" in enemy_skills and enemy.HPcur / enemy.visible_stats[HP] >= 1.1 - enemy_skills["obstruct"] * 0.2:
            obstruct_cond = True
        if "obstructSe" in enemy_skills and enemy.HPcur / enemy.visible_stats[HP] >= 1.1 - enemy_skills["obstructSe"] * 0.2:
            obstruct_cond = True

        if "bulwark" in enemy_skills or Status.Bulwark in enemy.statusPos:
            if unit.wpnType in MELEE_WEAPONS:
                obstruct_cond = True
            else:
                bulwark_cond = True

        tiles = []

        if obstruct_cond:
            tiles = enemy.tile.tilesWithinNSpaces(1)

        if bulwark_cond:
            tiles = enemy.tile.tilesWithinNSpaces(2)

        for x in tiles:
            if x not in all_obstruct_tiles:
                all_obstruct_tiles.append(x)

    return all_obstruct_tiles

# given an adjacent tile and hero, calculate the movement cost to get to it
def get_tile_cost(tile, unit):
    cost = 1
    move_type = unit.move

    # cases in which units cannot go to tile
    if tile.terrain == 1 and move_type == 1: return -1  # cavalry & forests
    if tile.terrain == 2 and move_type != 2: return -1  # nonfliers & water/mountains
    if tile.terrain == 4: return -1  # impassible terrain for anyone
    if tile.structure_on is not None and tile.structure_on.health != 0 and ("Trap" not in tile.structure_on.name and "Calling" not in tile.structure_on.name): return -1  # structure currently on
    if tile.divine_vein == DV_ICE and tile.divine_vein_side != unit.side and tile.divine_vein_turn > 0: return -1 # divine vein: ice currently on

    # Difficult terrain
    if tile.terrain == 1 and move_type == 0: cost = 2
    if tile.terrain == 3 and move_type == 1: cost = 3
    if (tile.divine_vein == DV_FLAME or tile.divine_vein == DV_WATER) and tile.divine_vein_side != unit.side and unit.getRange() == 2:
        if unit.move != 3:
            cost = 2
        else:
            cost = 1

    # Ignore difficult terrain
    if Status.TraverseTerrain in unit.statusPos: cost = 1
    if "cannotStopTakumi" in unit.getSkills() and unit.HPcur / unit.visible_stats[HP] >= 0.50: cost = 1

    # Pathfinder
    if tile.hero_on and tile.hero_on.side == unit.side and ("pathfinder" in tile.hero_on.getSkills() or (Status.Pathfinder in tile.hero_on.statusPos and Status.Schism not in tile.hero_on.statusNeg)):
        cost = 0

    return cost

# Get all non-warp tiles to move to + the path to get to them
def get_nonwarp_moves(unit, other_team, spaces_allowed=None):
    tile = unit.tile

    if spaces_allowed is None:
        spaces_allowed = allowed_movement(unit)

    visited = set() # tiles that have already been visited
    queue = deque([(tile, 0, "")]) # array of tuples of potential movement tiles, current costs, and current optimal pattern

    possible_tiles = [] # unique, possible tiles, to be returned
    optimal_moves = [] # shortest possible string to get to corresponding possible_move at index i

    char_arr = ['N', 'S', 'E', 'W']

    pass_cond = False
    if "passSk" in unit.getSkills():
        pass_cond = unit.HPcur >= 1 - 0.25 * unit.getSkills()["passSk"]
    if "passW" in unit.getSkills() and not pass_cond:
        pass_cond = unit.HPcur >= 1 - 0.25 * unit.getSkills()["passW"]

    if "shadowSlide" in unit.getSkills() and any([ally.unitCombatInitiates > 0 for ally in allies_within_n(unit, 20)]):
        pass_cond = True

    # all tiles which can obstruct non-warping movement
    obstruct_tiles = get_obstruct_tiles(unit, other_team)
    possible_obstruct_tiles = [] # obstruct tiles that can be moved to
    optimal_obstruct_moves = [] # paths to each obstruct tile

    while queue:
        # get current tuple
        current_tile, cost, path_str = queue.popleft()

        # not possible if too far, break since this is a BFS
        if current_tile in visited:
            continue

        visited.add(current_tile)

        if cost > spaces_allowed:
            continue

        if current_tile in obstruct_tiles and not pass_cond and current_tile != tile:
            possible_obstruct_tiles.append(current_tile)
            optimal_obstruct_moves.append(path_str)
            continue

        possible_tiles.append(current_tile)
        optimal_moves.append(path_str)

        current_neighbors = []
        for x in (current_tile.north, current_tile.south, current_tile.east, current_tile.west):
            current_neighbors.append(x)

        i = 0
        for x in current_neighbors:
            if x not in visited and x is not None:

                neighbor_cost = get_tile_cost(x, unit)

                within_allowed_cost = cost + neighbor_cost <= spaces_allowed

                if within_allowed_cost and neighbor_cost >= 0 and (x.hero_on is None or unit.isAllyOf(x.hero_on) or pass_cond):
                    new_entry = (x, cost + neighbor_cost, path_str + char_arr[i])
                    if neighbor_cost == 0:
                        queue.appendleft(new_entry)  # Prioritize 0-cost moves
                    else:
                        queue.append(new_entry)
            i += 1

    final_possible_tiles = []
    final_optimal_moves = []

    final_possible_obstruct_tiles = []
    final_optimal_obstruct_moves = []

    if possible_tiles:
        final_possible_tiles.append(possible_tiles[0])
        final_optimal_moves.append(optimal_moves[0])

    # remove tiles with other units on as valid moves
    i = 1
    while i < len(possible_tiles):
        if possible_tiles[i].hero_on is None:
            final_possible_tiles.append(possible_tiles[i])
            final_optimal_moves.append(optimal_moves[i])
        i += 1

    i = 0
    while i < len(possible_obstruct_tiles):
        if possible_obstruct_tiles[i].hero_on is None:
            final_possible_obstruct_tiles.append(possible_obstruct_tiles[i])
            final_optimal_obstruct_moves.append(optimal_obstruct_moves[i])
        i += 1

    return final_possible_tiles, final_optimal_moves, final_possible_obstruct_tiles, final_optimal_obstruct_moves

# List possible tiles to warp to
def get_warp_moves(unit, unit_team, other_team):
    unitSkills = unit.getSkills()
    unitStats = unit.getStats()

    warp_moves = []

    all_allies = [ally for ally in unit_team if ally != unit]

    if "wingsOfMercy" in unitSkills:
        for ally in all_allies:
            if ally.HPcur/ally.getStats()[HP] <= unitSkills["wingsOfMercy"] * 0.10 + 0.20:
                for adj_tile in ally.tile.tilesWithinNSpaces(1):
                    warp_moves.append(adj_tile)

    if "mercyWingEcho" in unitSkills:
        for ally in all_allies:
            if ally.HPcur/ally.getStats()[HP] <= 0.50:
                for adj_tile in ally.tile.tilesWithinNSpaces(1):
                    warp_moves.append(adj_tile)

    if "WoM4" in unitSkills:
        for ally in all_allies:
            if ally in allies_within_n(unit, 3):
                if ally.HPcur/ally.getStats()[HP] <= 0.99:
                    for adj_tile in ally.tile.tilesWithinNSpaces(1):
                        warp_moves.append(adj_tile)

            if ally.HPcur/ally.getStats()[HP] <= 0.60:
                for adj_tile in ally.tile.tilesWithinNSpaces(2):
                    warp_moves.append(adj_tile)

    # Sumia
    if "sumiaMovement" in unitSkills:
        for ally in unit_team:
            ally_hp = ally.HPcur/ally.getStats()[HP]
            if ally != unit and ally_hp <= 0.80:
                adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                for adj_tile in adj_ally_spaces:
                    warp_moves.append(adj_tile)

    # Cynthia
    if "weMovingPlenty" in unitSkills:
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
                    for adj_tile in ally.tile.tilesWithinNSpaces(1):
                        warp_moves.append(adj_tile)

    if "escRoutePlus" in unitSkills:
        if unit.HPcur / unitStats[HP] <= 0.99:
            for ally in allies_within_n(unit, 3):
                for adj_tile in ally.tile.tilesWithinNSpaces(1):
                    warp_moves.append(adj_tile)

    # Flier Formation
    # Warp to adj. spaces to flying ally within 2 spaces
    if "flierFormation" in unitSkills or "flierFormationSe" in unitSkills:
        skill_lvl = max(unitSkills.get("flierFormation", 0), unitSkills.get("flierFormationSe", 0))

        if unit.HPcur/unitStats[HP] >= 1.5 - 0.5 * skill_lvl:
            for ally in unit.tile.unitsWithinNSpaces(2):
                if ally.isAllyOf(unit) and ally.move == 2:
                    for adj_tile in ally.tile.tilesWithinNSpaces(1):
                        warp_moves.append(adj_tile)

    # Aerobatics
    # Ward to adj. spaces to non-flying ally within 2 spaces
    if "aerobatics" in unitSkills or "aerobaticsSe" in unitSkills:
        skill_lvl = max(unitSkills.get("aerobatics", 0), unitSkills.get("aerobaticsSe", 0))

        if unit.HPcur/unitStats[HP] >= 1.5 - 0.5 * skill_lvl:
            for ally in unit.tile.unitsWithinNSpaces(2):
                if ally.isAllyOf(unit) and ally.move != 2:
                    for adj_tile in ally.tile.tilesWithinNSpaces(1):
                        warp_moves.append(adj_tile)

    # Aerial Maneuvers
    if "aerialManeuvers" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    # Hold Guide
    if "holdGuide" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    # True-Bond Bow - X!Alm
    if "xAlmBoost" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    # Aerial Longsword (Refine Eff) - Annand
    if "aerialLongsword" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    # Staff of Yngvi - Edain
    if "edainBoost" in unitSkills:
        for ally in allies_within_n(unit, 5):
            for adj_tile in ally.tile.tilesWithinNSpaces(1):
                warp_moves.append(adj_tile)

    # Lance of Frelia (Base) - CH!Tana
    if "they fly now?" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    # Soaring Wings (Base) - R!Tana
    if "soaringWings" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    if "igreneWarp" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    # Magic Rabbits (Base) - SP!Sonya
    if "WOE, RABBITS UNTO YOU" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    # Kumo Yumi/Naginata
    if "kumoBoost" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(1):
                warp_moves.append(adj_tile)

    # Warp Powder
    if "warpPowder" in unitSkills and unit.HPcur/unitStats[HP] >= 0.80:
        for ally in allies_within_n(unit, 2):
            adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
            for adj_tile in adj_ally_spaces:
                warp_moves.append(adj_tile)

    # Warping adjacent to allies within 2 spaces
    if "annaSchmovement" in unitSkills and unit.HPcur/unitStats[HP] >= 0.50:
        potential_allies = unit.tile.unitsWithinNSpaces(2)
        for ally in potential_allies:
            if ally != unit and ally.side == unit.side:
                adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                for adj_tile in adj_ally_spaces:
                    warp_moves.append(adj_tile)

    # Tip the Scales!
    if "tipTheScales" in unitSkills:
        for ally in allies_within_n(unit, 5):
            if Status.RallySpectrum in ally.statusPos:
                for adj_tile in ally.tile.tilesWithinNSpaces(1):
                    warp_moves.append(adj_tile)

    # Awakening Anna
    if "On the house" in unitSkills or "One time offer, restrictions may apply" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(1):
                warp_moves.append(adj_tile)

    # Warping to ally within 2 spaces any space within 2 spaces of that ally
    if "nowiSchmovement" in unitSkills:
        potential_allies = unit.tile.unitsWithinNSpaces(2)
        for ally in potential_allies:
            if ally != unit and ally.side == unit.side:
                close_ally_spaces = ally.tile.tilesWithinNSpaces(2)
                for adj_tile in close_ally_spaces:
                    warp_moves.append(adj_tile)

    # Tut-Tut! - CH!Camilla
    if "tut-tut" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

        for vein_tile in unit.tile.tilesWithinNSpaces(5):
            if vein_tile.divine_vein_turn > 0:
                warp_moves.append(vein_tile)

    if "summerPetraBoost" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    # For the True King - FA!Dedue
    if "forTheTrueKing" in unitSkills:
        if any([ally.isSupportOf(unit) for ally in allies_within_n(unit, 20)]):
            for ally in allies_within_n(unit, 20):
                if ally.isSupportOf(unit):
                    for adj_tile in ally.tile.tilesWithinNSpaces(2):
                        warp_moves.append(adj_tile)
        else:
            highest_atk = []

            for ally in allies_within_n(unit, 20):
                if not highest_atk or ally.get_visible_stat(ATK) == highest_atk[0].get_visible_stat(ATK):
                    highest_atk.append(ally)
                elif ally.get_visible_stat(ATK) > highest_atk[0].get_visible_stat(ATK):
                    highest_atk = [ally]

            for ally in highest_atk:
                for adj_tile in ally.tile.tilesWithinNSpaces(2):
                    warp_moves.append(adj_tile)

    if "shadowSlide" in unitSkills:
        for ally in allies_within_n(unit, 20):
            if ally.unitCombatInitiates > 0 or ally in allies_within_n(unit, 2):
                for adj_tile in ally.tile.tilesWithinNSpaces(2):
                    warp_moves.append(adj_tile)

    # Scroll of Teas - NI!Céline
    if "niCelineBoost" in unitSkills:
        for ally in unit.tile.unitsWithinNSpaces(2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    # Trained to Kill - Yunaka
    if "trainedToKill" in unitSkills:
        for tile in unit.tile.tilesWithinNSpaces(2):
            if unit.isAllyOf(tile.hero_on) or tile.is_difficult_terrain() or tile.is_def_terrain or tile.has_divine_vein():
                warp_moves.append(tile)

                for adj_tile in tile.tilesWithinNSpaces(2):
                    warp_moves.append(adj_tile)

    # Warp Ragnarok
    if "eCelicaWarp" in unitSkills:
        for foe in foes_within_n(unit, 6):

            nearest_tile_dist = 20
            nearest_tiles = []

            for warp_tile in foe.tile.tilesNSpacesAway(2):
                dist = abs(warp_tile.x_coord - unit.tile.x_coord) + abs(warp_tile.y_coord - unit.tile.y_coord)

                # If closer than current closest tile
                if dist < nearest_tile_dist:
                    nearest_tiles = [warp_tile]
                    nearest_tile_dist = dist

                # If as close as current closest tile
                elif dist == nearest_tile_dist:
                    nearest_tiles.append(warp_tile)

            for adj_tile in nearest_tiles:
                warp_moves.append(adj_tile)

    # Celica Ring
    if "care for us" in unitSkills:
        for foe in foes_within_n(unit, 5):

            nearest_tile_dist = 20
            nearest_tiles = []

            if unit.wpnType in MELEE_WEAPONS:
                foe_tiles = foe.tile.tilesNSpacesAway(1)
            else:
                foe_tiles = foe.tile.tilesNSpacesAway(2)

            for warp_tile in foe_tiles:
                dist = abs(warp_tile.x_coord - unit.tile.x_coord) + abs(warp_tile.y_coord - unit.tile.y_coord)

                # If closer than current closest tile
                if dist < nearest_tile_dist:
                    nearest_tiles = [warp_tile]
                    nearest_tile_dist = dist

                # If as close as current closest tile
                elif dist == nearest_tile_dist:
                    nearest_tiles.append(warp_tile)

            for adj_tile in nearest_tiles:
                warp_moves.append(adj_tile)

    # Snowman Staff - WI!Hortensia
    if "wiHortensiaBoost" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for adj_tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(adj_tile)

    # Nova - Griss
    if "grissBoost" in unitSkills:
        for foe in foes_within_n(unit, 5):

            nearest_tile_dist = 20
            nearest_tiles = []

            for warp_tile in foe.tile.tilesNSpacesAway(2):
                dist = abs(warp_tile.x_coord - unit.tile.x_coord) + abs(warp_tile.y_coord - unit.tile.y_coord)

                # If closer than current closest tile
                if dist < nearest_tile_dist:
                    nearest_tiles = [warp_tile]
                    nearest_tile_dist = dist

                # If as close as current closest tile
                elif dist == nearest_tile_dist:
                    nearest_tiles.append(warp_tile)

            for adj_tile in nearest_tiles:
                warp_moves.append(adj_tile)

    # Inevitable Death+
    if "inevitableII" in unitSkills:
        for foe in foes_within_n(unit, 4):
            nearest_tile_dist = 20
            nearest_tiles = []

            for warp_tile in foe.tile.tilesWithinNSpaces(1):
                dist = abs(warp_tile.x_coord - unit.tile.x_coord) + abs(warp_tile.y_coord - unit.tile.y_coord)

                # If closer than current closest tile
                if dist < nearest_tile_dist:
                    nearest_tiles = [warp_tile]
                    nearest_tile_dist = dist

                # If as close as current closest tile
                elif dist == nearest_tile_dist:
                    nearest_tiles.append(warp_tile)

            for adj_tile in nearest_tiles:
                warp_moves.append(adj_tile)

    # Troubling Blade
    if "bomba" in unitSkills:
        for foe in foes_within_n(unit, 4):
            nearest_tile_dist = 20
            nearest_tiles = []

            for warp_tile in foe.tile.tilesWithinNSpaces(1):
                dist = abs(warp_tile.x_coord - unit.tile.x_coord) + abs(warp_tile.y_coord - unit.tile.y_coord)

                # If closer than current closest tile
                if dist < nearest_tile_dist:
                    nearest_tiles = [warp_tile]
                    nearest_tile_dist = dist

                # If as close as current closest tile
                elif dist == nearest_tile_dist:
                    nearest_tiles.append(warp_tile)

            for adj_tile in nearest_tiles:
                warp_moves.append(adj_tile)

    # Death (Refine Eff) - FA!Delthea
    if "deathOrders" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for tile in ally.tile.tilesWithinNSpaces(1):
                warp_moves.append(tile)

    # Astra Blade (Refine Eff) - Valentia Catria
    if "superExtraAstra" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

    # Convoy Dagger (Base) - Merlinus
    if "merlinusWarp" in unitSkills:
        for ally in unit_team:
            if ally != unit:
                for adj_tile in ally.tile.tilesWithinNSpaces(1):
                    warp_moves.append(adj_tile)

    # Dazzling Shift
    if "dazzlingShift" in unitSkills:
        for ally in allies_within_n(unit, 2):
            for tile in ally.tile.tilesWithinNSpaces(1):
                warp_moves.append(tile)

    # Tome of Favors (Refine Eff) - Oliver
    if "I cannot blame you for wanting to touch something so alluring as myself." in unitSkills:
        for ally in unit_team:
            if ally.wpnType in BEAST_WEAPONS and ally.refresh_type != 0:
                adj_ally_spaces = ally.tile.tilesWithinNSpaces(1)
                for adj_tile in adj_ally_spaces:
                    warp_moves.append(adj_tile)

    # Astral Breath (Base) - Lilith
    if "lilithWarp" in unitSkills:
        for ally in unit_team:
            if ally.isSupportOf(unit):
                for adj_tile in ally.tile.tilesWithinNSpaces(1):
                    warp_moves.append(adj_tile)

    if "lilithRefineWarp" in unitSkills or "faLilithBoost" in unitSkills:
        for ally in unit_team:
            if ally.isSupportOf(unit):
                for adj_tile in ally.tile.tilesWithinNSpaces(2):
                    warp_moves.append(adj_tile)

    # Divine Draught - SU!Ivy / Icebound Tome - Ivy
    if "suIvyBoost" in unitSkills or "ivyBoost" in unitSkills:
        for ally in allies_within_n(unit, 3):
            if ally.isSupportOf(unit):
                for adj_tile in ally.tile.tilesWithinNSpaces(2):
                    warp_moves.append(adj_tile)

    # Orders Status
    if Status.Orders in unit.statusPos:
        for ally in allies_within_n(unit, 2):
            for tile in ally.tile.tilesWithinNSpaces(1):
                warp_moves.append(tile)

    # Pass Condition
    pass_cond = False
    if "passSk" in unit.getSkills():
        pass_cond = unit.HPcur >= 1 - 0.25 * unit.getSkills()["passSk"]
    if "passW" in unit.getSkills() and not pass_cond:
        pass_cond = unit.HPcur >= 1 - 0.25 * unit.getSkills()["passW"]

    if "shadowSlide" in unit.getSkills() and any([ally.unitCombatInitiates > 0 for ally in allies_within_n(unit, 20)]):
        pass_cond = True

    # Charge Status
    if Status.Charge in unit.statusPos:
        i = 0
        cur_tile = unit.tile.north
        while i < 3 and cur_tile is not None:
            if can_be_on_tile(cur_tile, unit) and (not cur_tile.hero_on or (cur_tile.hero_on and unit.isAllyOf(cur_tile.hero_on))):
                warp_moves.append(cur_tile)

                if cur_tile in get_obstruct_tiles(unit, other_team) and not pass_cond:
                    i = 3
                else:
                    cur_tile = cur_tile.north
                    i += 1

            else:
                i = 3

        i = 0
        cur_tile = unit.tile.south
        while i < 3 and cur_tile is not None:
            if can_be_on_tile(cur_tile, unit) and (not cur_tile.hero_on or (cur_tile.hero_on and unit.isAllyOf(cur_tile.hero_on))):
                warp_moves.append(cur_tile)

                if cur_tile in get_obstruct_tiles(unit, other_team) and not pass_cond:
                    i = 3
                else:
                    cur_tile = cur_tile.south
                    i += 1

            else:
                i = 3

        i = 0
        cur_tile = unit.tile.east
        while i < 3 and cur_tile is not None:
            if can_be_on_tile(cur_tile, unit) and (not cur_tile.hero_on or (cur_tile.hero_on and unit.isAllyOf(cur_tile.hero_on))):
                warp_moves.append(cur_tile)

                if cur_tile in get_obstruct_tiles(unit, other_team) and not pass_cond:
                    i = 3
                else:
                    cur_tile = cur_tile.east
                    i += 1
            else:
                i = 3

        i = 0
        cur_tile = unit.tile.west
        while i < 3 and cur_tile is not None:
            if can_be_on_tile(cur_tile, unit) and (not cur_tile.hero_on or (cur_tile.hero_on and unit.isAllyOf(cur_tile.hero_on))):
                warp_moves.append(cur_tile)

                if cur_tile in get_obstruct_tiles(unit, other_team) and not pass_cond:
                    i = 3
                else:
                    cur_tile = cur_tile.west
                    i += 1
            else:
                i = 3


    # Ally skills which enable warping
    for ally in unit_team:
        allySkills = ally.getSkills()
        allyStats = ally.getStats()

        # Time's Gate
        if Status.TimesGate in ally.statusPos and unit in allies_within_n(ally, 4):
            for tile in ally.tile.tilesWithinNSpaces(1):
                warp_moves.append(tile)

        # Hinoka's Spear
        if "refineNaginata" in allySkills and (unit.move == 0 or unit.move == 2):
            units_within_2 = allies_within_n(ally, 2)
            if unit in units_within_2:

                local_spaces = ally.tile.tilesWithinNSpaces(1)
                for tile in local_spaces:
                    warp_moves.append(tile)

        # Guidance
        # Inf and Armor allies can move to a space adj. to flier w/ skill
        if "guidance" in allySkills and ally.HPcur / allyStats[HP] >= 1.5 - 0.5 * allySkills["guidance"]:
            if unit.move == 0 or unit.move == 3:
                if unit in allies_within_n(ally, 2):
                    for tile in ally.tile.tilesWithinNSpaces(1):
                        warp_moves.append(tile)

        if "guidanceSe" in allySkills and ally.HPcur / allyStats[HP] >= 1.5 - 0.5 * allySkills["guidanceSe"]:
            if unit.move == 0 or unit.move == 3:
                if unit in allies_within_n(ally, 2):
                    for tile in ally.tile.tilesWithinNSpaces(1):
                        warp_moves.append(tile)

        # Guidance 4
        if "guidance4" in allySkills and (unit.move == 0 or unit.move == 3) and unit in allies_within_n(ally, 2):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        # Hold Guide
        if "holdGuide" in allySkills and unit in allies_within_n(ally, 2):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        # Prior's Tome - Nomah
        if "nomahBoost" in allySkills:
            trap_cond = False

            for tile in ally.tile.tilesWithinNSpaces(2):
                if tile.structure_on and "Trap" in tile.structure_on.name:
                    trap_cond = True
                    break

            if trap_cond or unit in allies_within_n(ally, 2):
                for tile in ally.tile.tilesWithinNSpaces(2):
                    warp_moves.append(tile)

        # Fruit of Iðunn (Base) - SU!Tana
        if "SUTanaWarp" in allySkills and ally.HPcur / allyStats[HP] >= 1.5 - 0.5 * allySkills["SUTanaWarp"]:
            if unit in allies_within_n(ally, 2):
                for tile in ally.tile.tilesWithinNSpaces(1):
                    warp_moves.append(tile)

        # Snaking Sword - NY!Tana
        if "nyTanaBoost" in allySkills:
            if unit in allies_within_n(ally, 2) or ally.unitCombatInitiates > 0 or ally.assistTargetedOther > 0:
                for tile in ally.tile.tilesWithinNSpaces(1):
                    warp_moves.append(tile)

        # Silver of Dawn - X!Micaiah
        if "silverOfDawn" in allySkills and unit in allies_within_n(ally, 2):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        # Divine God Fang - Dragon Naga
        if "divineGodFang" in allySkills and unit in allies_within_n(ally, 2):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        # Exalt's War Staff - CH!Emmeryn
        if "chEmmerynBoost" in allySkills and (ally.HPcur / allyStats[HP] <= 0.60 or ally.unitCombatInitiates >= 1 or ally.assistTargetedOther >= 1):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        # Caduceus Staff (Refine Eff) - Flayn
        if "The girl who like the fish" in allySkills and unit in allies_within_n(ally, 2):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        # Wildflower Edge - BR!Lapis
        if "wildflowerEdge" in allySkills and ally.unitCombatInitiates >= 1 and unit in allies_within_n(ally, 5):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        # Opening Retainer(+) - Ash
        if "ashGuidance" in allySkills and unit in allies_within_n(ally, 2):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        # Worldbreaker+ - Thórr
        if "worldbreakerPlus" in allySkills and unit in allies_within_n(ally, 2):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        # Flier Guidance
        # Flier allies can move to a space adj. to flier w/ skill
        if "flier_guidance" in allySkills and ally.HPcur / allyStats[HP] >= 1.5 - 0.5 * allySkills["flier_guidance"]:
            if unit.move == 2:
                if unit in allies_within_n(ally, 2):
                    for tile in ally.tile.tilesWithinNSpaces(1):
                        warp_moves.append(tile)

        if "flier_guidanceSe" in allySkills and ally.HPcur / allyStats[HP] >= 1.5 - 0.5 * allySkills["flier_guidanceSe"]:
            if unit.move == 2:
                if unit in allies_within_n(ally, 2):
                    for tile in ally.tile.tilesWithinNSpaces(1):
                        warp_moves.append(tile)

        # Soaring Guidance / Soaring Echo
        if ("soaring_guidance" in allySkills or "soaringEcho" in allySkills) and (unit.move == 2 or unit.move == 0) and unit in allies_within_n(ally, 2):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        if "heartOCrimea" in allySkills and unit in allies_within_n(ally, 2):
            for tile in ally.tile.tilesWithinNSpaces(2):
                warp_moves.append(tile)

        if "aFlorinaBoost" in allySkills:
            if unit in allies_within_n(ally, 2):
                for tile in ally.tile.tilesWithinNSpaces(2):
                    warp_moves.append(tile)

            elif ally.HPcur / allyStats[HP] <= 0.60:
                for tile in ally.tile.tilesWithinNSpaces(1):
                    warp_moves.append(tile)

    # Remove duplicates
    warp_moves = list(set(warp_moves))

    # Remove tiles other heroes are on
    result_warp_moves = []
    for tile in warp_moves:
        if tile.hero_on is None and can_be_on_tile(tile, unit):
            result_warp_moves.append(tile)

    blocked_warp_moves = remove_blocked_warp_tiles(unit, other_team, result_warp_moves)

    return blocked_warp_moves

def remove_blocked_warp_tiles(unit, other_team, cur_warp_moves):
    pass_cond = False
    if "passSk" in unit.getSkills():
        pass_cond = unit.HPcur >= 1 - 0.25 * unit.getSkills()["passSk"]
    if "passW" in unit.getSkills() and not pass_cond:
        pass_cond = unit.HPcur >= 1 - 0.25 * unit.getSkills()["passW"]

    if "shadowSlide" in unit.getSkills() and any([ally.unitCombatInitiates > 0 for ally in allies_within_n(unit, 20)]):
        pass_cond = True

    if pass_cond:
        return cur_warp_moves

    # Divine Vein Green
    if unit.tile.divine_vein == DV_GREEN and unit.tile.divine_vein_turn >= 1 and unit.tile.divine_vein_side != unit.side:
        return []

    cur_warp_green = []

    for tile in cur_warp_moves[:]:
        if not(tile.divine_vein == DV_GREEN and tile.divine_vein_turn >= 1 and tile.divine_vein_side != unit.side):
            cur_warp_green.append(tile)

    cur_warp_moves = cur_warp_green

    # Antiwarp Skills on defending team
    for foe in other_team:
        foeSkills = foe.getSkills()
        foeStats = foe.getStats()

        if "detailedReport" in foeSkills:
            for tile in foe.tile.tilesWithinNSpaces(4):
                if tile in cur_warp_moves:
                    cur_warp_moves.remove(tile)

        if Status.WarpBubble in foe.statusPos:
            for tile in foe.tile.tilesWithinNSpaces(4):
                if tile in cur_warp_moves:
                    cur_warp_moves.remove(tile)

        if "highDragonWall" in foeSkills and unit.wpnType in RANGED_WEAPONS:
            for tile in foe.tile.tilesWithinNSpaces(4):
                if tile in cur_warp_moves:
                    cur_warp_moves.remove(tile)

        if "barricade" in foeSkills:
            if unit.wpnType in RANGED_WEAPONS:
                for tile in foe.tile.tilesWithinNSpaces(4):
                    if tile in cur_warp_moves:
                        cur_warp_moves.remove(tile)
            else:
                for tile in foe.tile.tilesWithinNSpaces(3):
                    if tile in cur_warp_moves:
                        cur_warp_moves.remove(tile)

        # Higher Ground/Lower Ground
        if "notMiddleGround" in foeSkills:
            if unit.wpnType in RANGED_WEAPONS:
                for tile in foe.tile.tilesWithinNSpaces(4):
                    if tile in cur_warp_moves:
                        cur_warp_moves.remove(tile)
            else:
                for tile in foe.tile.tilesWithinNSpaces(3):
                    if tile in cur_warp_moves:
                        cur_warp_moves.remove(tile)

    return cur_warp_moves

# Given an attacker and defender on the field, return single savior unit that can cover the defender, otherwise None
def get_savior(defender, attacker):
    attacking_range = attacker.getRange()

    defender_allies = allies_within_n(defender, 20)

    valid_saviors = []

    for ally in defender_allies:
        allySkills = ally.getSkills()

        if Status.AssignDecoy not in ally.statusPos:
            if "nearSavior" in allySkills and attacking_range == 1 and ally in allies_within_n(defender, allySkills["nearSavior"]):
                    valid_saviors.append(ally)

            elif "farSavior" in allySkills and attacking_range == 2 and ally in allies_within_n(defender, allySkills["farSavior"]):
                    valid_saviors.append(ally)

            elif "forTheTrueKing" in allySkills and ally in allies_within_n(defender, 4):
                if any([def_ally.isSupportOf(defender) for def_ally in defender_allies]):
                    if ally.isSupportOf(defender):
                        valid_saviors.append(ally)
                else:
                    highest_atk = []

                    for def_ally in allies_within_n(ally, 20):
                        if not highest_atk or def_ally.get_visible_stat(ATK) == highest_atk[0].get_visible_stat(ATK):
                            highest_atk.append(def_ally)
                        elif def_ally.get_visible_stat(ATK) > highest_atk[0].get_visible_stat(ATK):
                            highest_atk = [def_ally]

                    if defender in highest_atk:
                        valid_saviors.append(ally)

        else:
            if "nearSavior" not in allySkills and "farSavior" not in allySkills and attacking_range == ally.getRange():
                valid_saviors.append(ally)

    disable_savior = bool("disableFoeSavior" in attacker.getSkills() or Status.Undefended in defender.statusNeg)

    if len(valid_saviors) != 1 or disable_savior:
        return None
    else:
        return valid_saviors[0]

# A possible movement action by a unit
class Move():
    def __init__(self, dest, num_moved, is_warp, trav_str):
        self.destination = dest  # tile ID
        self.num_moved = num_moved  # num tiles between start and this tile
        self.is_warp = is_warp  # does this move use a warp space?
        self.trav_string = trav_str  # traversal string, holds default optimal path

def get_regular_moves(unit, unit_team, other_team, style=None):
    tile = unit.tile

    final_dests = []
    final_paths = []
    final_move_Objs = []

    if style == "ASTRA-STORM" or style == "EMBLEM-LYN":
        moves, paths, obst_moves, obst_paths = get_nonwarp_moves(unit, other_team, spaces_allowed=0)
        warp_tiles = []
    else:
        moves, paths, obst_moves, obst_paths = get_nonwarp_moves(unit, other_team)
        warp_tiles = get_warp_moves(unit, unit_team, other_team)

    for i in range(0, len(moves)):
        final_dests.append(moves[i].tileNum)
        final_paths.append(paths[i])

        end = moves[i].tileNum
        distance = abs(end % 6 - tile.x_coord) + abs(end // 6 - tile.y_coord % 6)

        final_move_Objs.append(Move(end, num_moved=distance, is_warp=False, trav_str=paths[i]))

    for i in range(0, len(obst_moves)):
        if obst_moves[i].tileNum not in final_dests:
            final_dests.append(obst_moves[i].tileNum)
            final_paths.append(obst_paths[i])

            end = obst_moves[i].tileNum
            distance = abs(end % 6 - tile.x_coord) + abs(end // 6 - tile.y_coord % 6)

            final_move_Objs.append(Move(end, num_moved=distance, is_warp=False, trav_str=obst_paths[i]))

    for i in range(0, len(warp_tiles)):
        if warp_tiles[i].tileNum not in final_dests:
            final_dests.append(warp_tiles[i].tileNum)
            final_paths.append("WARP")

            end = warp_tiles[i].tileNum
            distance = abs(end % 6 - tile.x_coord) + abs(end // 6 - tile.y_coord % 6)

            final_move_Objs.append(Move(end, num_moved=distance, is_warp=True, trav_str="WARP"))

    return final_dests, final_paths, final_move_Objs

def get_canto_moves(unit, unit_team, other_team, distance_traveled, allowed_movement, action, turn, starting_tile, has_unit_warped):
    tile = unit.tile

    INVALID = -1
    ATTACK = 0
    ASSIST = 1
    BREAK = 2
    MOVE = 3

    # array of all canto distances given by skills, only max is taken
    possible_move_vals = [0]

    unitSkills = unit.getSkills()

    if Status.Canto1 in unit.statusPos:
        possible_move_vals.append(1)

    if Status.FutureWitness in unit.statusPos:
        possible_move_vals.append(2)

    if Status.Salvage in unit.statusPos:
        possible_move_vals.append(2)

    remaining_movement = allowed_movement - distance_traveled

    if has_unit_warped:
        remaining_movement = 0

    # General
    if "canto1" in unitSkills:
        possible_move_vals.append(1)

    if "canto2" in unitSkills:
        possible_move_vals.append(2)

    if "canto3" in unitSkills:
        possible_move_vals.append(3)

    if "cantoRem" in unitSkills:
        possible_move_vals.append(remaining_movement)

    if "cantoRemMin1" in unitSkills:
        possible_move_vals.append(max(remaining_movement, 1))

    if "cantoRemPlus1" in unitSkills:
        possible_move_vals.append(remaining_movement + 1)

    if "cantoRemPlus1Min2" in unitSkills:
        possible_move_vals.append(max(remaining_movement + 1, 2))

    if "cantoDistPlus1Max4" in unitSkills:
        possible_move_vals.append(min(distance_traveled + 1, 4))

    if "cantoDistMax3" in unitSkills:
        possible_move_vals.append(min(distance_traveled, 3))

    # Skills
    if "tier4DanceCanto" in unitSkills and action == ASSIST:
        possible_move_vals.append(1)

    if "escRoutePlus" in unitSkills and unit.HPcur / unit.visible_stats[HP] <= 0.99:
        possible_move_vals.append(1)

    if "atkSpdMastery" in unitSkills and unit.unitCombatInitiates >= 1:
        possible_move_vals.append(2)

    if "gait" in unitSkills and action == ASSIST:
        possible_move_vals.append(1)

    # Bestial Assault
    if "definitelyNotBeastAssault" in unitSkills and unit.transformed:
        possible_move_vals.append(max(remaining_movement + 1, 2))

    # Bestial Agility
    if "bestialAgility" in unitSkills and unit.transformed:
        possible_move_vals.append(max(remaining_movement + 1, 2))

    # Feather Sword (Refine Eff) - CH!Caeda
    if "refinedFeather" in unitSkills:
        possible_move_vals.append(2)

    # Wing-Lifted Spear
    if "https://www.youtube.com/watch?v=NqDawnpxcgc" in unitSkills or "LCaedaRefine" in unitSkills or "LCaedaRefineEffect" in unitSkills:
        possible_move_vals.append(2)

    # Whitedown Spear (Refine Eff) - CH!Palla - REM+1
    if "RATHER THAN, THE BREATHLESS VASTNESS OF THE WORLD" in unitSkills and [ally for ally in allies_within_n(unit, 3) if ally.move == 2]:
        possible_move_vals.append(remaining_movement + 1)

    # Frostfire Breath (Refine Eff) - H!Y!Tiki
    if "frostfire" in unitSkills:
        possible_move_vals.append(2)

    # Hallowed Tyrfing (Refine Eff) - L!Sigurd
    if "FE4 Remake When?" in unitSkills:
        possible_move_vals.append(remaining_movement + 1)

    # Heavenly Icicle
    if "dithorbaStuff" in unitSkills:
        possible_move_vals.append(remaining_movement + 1)

    # Reginleif - REM+1
    if "OH MY GOODNESS" in unitSkills and unit.hasBonus():
        possible_move_vals.append(remaining_movement + 1)

    # Obsidian Lance (Refine Base) - Duessel
    if "duesselRefine" in unitSkills:
        possible_move_vals.append(2)

    if "theDayTheEarthBlewUp" in unitSkills:
        possible_move_vals.append(1)

    # Talregan Axe - REM+1
    if "jillSomething" in unitSkills:
        possible_move_vals.append(remaining_movement + 1)

    # Wolf Queen Fang - REM+1
    if "nailahCanto" in unitSkills and unit.transformed:
        possible_move_vals.append(remaining_movement + 1)

    # Bride's Fang - REM+1
    if "limitRocket" in unitSkills and unit.transformed:
        possible_move_vals.append(remaining_movement + 1)

    # Royal Hatari Fang - REM+1
    if "deNailahBoost" in unitSkills and unit.transformed:
        possible_move_vals.append(remaining_movement + 1)

    # Queenslance - REM+1
    if "geoffreyBoost" in unitSkills and unit.hasBonus():
        possible_move_vals.append(remaining_movement + 1)

    # Failnaught
    if "the nair landing hitbox has won me many a game" in unitSkills:
        possible_move_vals.append(1)

    # Mirage Feather
    if "KOWASHITAI" in unitSkills:
        possible_move_vals.append(2)

    # Payday Pouch - H!E!Anna
    if "hAnnaBoost" in unitSkills and len(unit.statusPos) >= 3:
        possible_move_vals.append(2)

    # Icy Fimbulvetr (Refine Base) - Marianne
    if "marianneCanto" in unitSkills and any([ally for ally in unit_team if ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS or ally.move == 1 or ally.move == 2]):
        possible_move_vals.append(2)

    # Requiem Prayer - R!Marianne
    if "requiemPrayer" in unitSkills and unit.specialTriggeredThisTurn:
        possible_move_vals.append(2)

    # Gate-Anchor Axe (Refine Base) - PI!Veronica - DIST+1, MAX 4
    if "piVeronicaCanto" in unitSkills:
        possible_move_vals.append(min(distance_traveled + 1, 4))

    # Twin Star Axe (Refine Eff) - NI!Laevatein
    if "wolf back air" in unitSkills:
        possible_move_vals.append(2)

    # Nightmare Horn (Refine Eff) - Freyja - REM+1
    if "freyjaRefineEff" in unitSkills:
        possible_move_vals.append(remaining_movement + 1)

    # Lyngheiðr - Reginn
    if "reginnCanto" in unitSkills and turn <= 4:
        possible_move_vals.append(3)

    # Dvergr Wayfinder DIST+2, MAX 5
    if "reginnAccel" in unitSkills and turn <= 4:
        possible_move_vals.append(min(distance_traveled + 2, 5))

    # Iron Hreiðmarr DIST+2, MAX 5
    if "THE FAFNIR IS REAL" in unitSkills and turn <= 4:
        possible_move_vals.append(min(distance_traveled + 2, 5))

    # Niðavellir Ballista DIST+1, MAX 4
    if "niðavellirBoost" in unitSkills and turn <= 4:
        possible_move_vals.append(min(distance_traveled + 1, 4))

    # Grim Brokkr - Eitri
    if "eitriCanto" in unitSkills and turn <= 4:
        possible_move_vals.append(2)

    # Goddess Temari - NY!Seiðr
    if "nySeiðrBoost" in unitSkills and turn >= 2:
        possible_move_vals.append(1)

    # War-God Mjölnir (Refine Eff) - Thórr
    if "im eating an apple rn" in unitSkills:
        possible_move_vals.append(2)

    # Sigurd Ring
    if "provide for us" in unitSkills:
        if unit.wpnType in MELEE_WEAPONS:
            possible_move_vals.append(3)
        else:
            possible_move_vals.append(2)

    # take max, value is used for canto distance
    base_move = max(possible_move_vals)

    # Warp-exclusive cantos
    warp_exclusive_canto = False

    if "cantoUnit3x3" in unitSkills:
        warp_exclusive_canto = True

    if "cantoRecall" in unitSkills:
        warp_exclusive_canto = True

    if "cantoAlly2" in unitSkills and allies_within_n(unit, 2):
        warp_exclusive_canto = True

    if "cantoAlly5" in unitSkills and allies_within_n(unit, 5):
        warp_exclusive_canto = True

    # CANTO CONTROL
    if Status.CantoControl in unit.statusNeg:
        warp_exclusive_canto = False

        if unit.wpnType in MELEE_WEAPONS:
            base_move = 1
        if unit.wpnType in RANGED_WEAPONS:
            base_move = 0

        if Status.Salvage in unit.statusPos:
            base_move += 1

    # Canto does not trigger at all, occurs under the following conditions:
    # - Canto Dist. with 0 spaces traveled
    # - Canto Rem. with max spaces traveled
    # - Canto Ally 2 with no allies in range (will still work if there are allies, but no spaces to warp to)
    # - Unit does not meet any conditions to activate any type of canto
    # In these cases, Canto Control cannot be applied by a foe, and unit can still
    # activate Canto elsewhere if given another action.

    if base_move == 0 and not warp_exclusive_canto:
        return [], [], []

    canto_dests = []
    canto_paths = []
    canto_move_Objs = []

    moves, paths, obst_moves, obst_paths = get_nonwarp_moves(unit, other_team, base_move)

    warp_tiles = []
    special_warp_tiles = []

    if warp_exclusive_canto:
        if "cantoUnit3x3" in unitSkills:
            special_warp_tiles = list(set(unit.tile.tilesWithinNRows(3)) & set(unit.tile.tilesWithinNCols(3)))

        elif "cantoAlly2" in unitSkills:
            special_warp_tiles = []

            for ally in allies_within_n(unit, 2):
                for tile in ally.tile.tilesWithinNSpaces(1):
                    if tile not in special_warp_tiles:
                        special_warp_tiles.append(tile)

        elif "cantoAlly5" in unitSkills:
            special_warp_tiles = []

            for ally in allies_within_n(unit, 5):
                for tile in ally.tile.tilesWithinNSpaces(1):
                    if tile not in special_warp_tiles:
                        special_warp_tiles.append(tile)

        elif "cantoRecall" in unitSkills:
            special_warp_tiles = [starting_tile]

        else:
            special_warp_tiles = []

    # Salvage - L!Sakura
    for ally in allies_within_n(unit, 6):
        if "LSakuraBoost" in ally.getSkills():
            for tile in ally.tile.tilesWithinNSpaces(2):
                special_warp_tiles.append(tile)

    # Clear tiles with other units on them/invalid terrain
    temp_warp_tiles = []

    for tile in special_warp_tiles:
        if not tile.hero_on and can_be_on_tile(tile, unit):
            temp_warp_tiles.append(tile)

    special_warp_tiles = list(set(temp_warp_tiles))

    # Apply skills that block warping
    special_warp_tiles = remove_blocked_warp_tiles(unit, other_team, special_warp_tiles)

    if base_move > 0:
        warp_tiles = get_warp_moves(unit, unit_team, other_team)

    # Standard movements
    for i in range(0, len(moves)):
        canto_dests.append(moves[i].tileNum)
        canto_paths.append(paths[i])

        end = moves[i].tileNum
        distance = abs(end % 6 - tile.x_coord) + abs(end // 6 - tile.y_coord % 6)

        canto_move_Objs.append(Move(end, num_moved=distance, is_warp=False, trav_str=paths[i]))

    # Movement to an obstruct tile
    for i in range(0, len(obst_moves)):
        if obst_moves[i].tileNum not in canto_dests:
            canto_dests.append(obst_moves[i].tileNum)
            canto_paths.append(obst_paths[i])

            end = obst_moves[i].tileNum
            distance = abs(end % 6 - tile.x_coord) + abs(end // 6 - tile.y_coord % 6)

            canto_move_Objs.append(Move(end, num_moved=distance, is_warp=False, trav_str=obst_paths[i]))

    # Warping granted by standard skills
    for i in range(0, len(warp_tiles)):
        if warp_tiles[i].tileNum not in canto_dests:
            end = warp_tiles[i].tileNum
            distance = abs(end % 6 - tile.x_coord) + abs(end // 6 - tile.y_coord % 6)

            # If warp is not within allowed number of spaces and not using warp-based canto, do not consider this movement
            if distance > base_move and base_move != -1:
                continue

            canto_dests.append(warp_tiles[i].tileNum)
            canto_paths.append("WARP")

            canto_move_Objs.append(Move(end, num_moved=distance, is_warp=True, trav_str="WARP"))

    # From special types of canto, ignore range limitation
    for i in range(0, len(special_warp_tiles)):
        if special_warp_tiles[i].tileNum not in canto_dests:
            end = special_warp_tiles[i].tileNum
            distance = abs(end % 6 - tile.x_coord) + abs(end // 6 - tile.y_coord % 6)

            canto_dests.append(special_warp_tiles[i].tileNum)
            canto_paths.append("WARP")

            canto_move_Objs.append(Move(end, num_moved=distance, is_warp=True, trav_str="WARP"))

    return canto_dests, canto_paths, canto_move_Objs

# Get tile moved to if unit at u_tile used reposition on ally at a_tile
def final_reposition_tile(u_tile, a_tile):
    if u_tile == -1 or a_tile == -1:
        return -1

    bottom_row = (0, 1, 2, 3, 4, 5)
    if u_tile in bottom_row and a_tile == u_tile + 6: return -1

    top_row = (42, 43, 44, 45, 46, 47)
    if u_tile in top_row and a_tile == u_tile - 6: return -1

    left_column = (0, 6, 12, 18, 24, 30, 36, 42)
    if u_tile in left_column and a_tile == u_tile + 1: return -1

    right_column = (5, 11, 17, 23, 29, 35, 41, 47)
    if u_tile in right_column and a_tile == u_tile - 1: return -1

    final_tile = -1

    if u_tile > a_tile:
        final_tile = a_tile + 2 * (u_tile - a_tile)

    if u_tile < a_tile:
        final_tile = a_tile - 2 * (a_tile - u_tile)

    return final_tile

aoe_patterns = {
    1: [-2, -1, 0, 1, 2],  # Rising/Blazing Flame
    2: [-7, -5, 0, 5, 7],  # Rising/Blazing Light
    3: [-12, -6, 0, 6, 12],  # Rising/Blazing Thunder
    4: [-6, -1, 0, 1, 6],  # Rising/Blazing Wind & Gifted Magic (I & II)

    11: [-7, -5, -2, -1, 0, 1, 2, 5, 7],  # Growing Flame
    12: [-12, -7, -5, -2, 0, 2, 5, 7, 12],  # Growing Light
    13: [-18, -12, -6, -1, 0, 1, 6, 12, 18],  # Growing Thunder
    14: [-7, -6, -5, -1, 0, 1, 5, 6, 7],  # Growing Wind

    21: [-1, 0, 1, 5, 6, 7, 11, 12, 13],  # Override, Facing North
    22: [-1, 0, 1, -5, -6, -7, -11, -12, -13],  # Override, Facing South
    23: [-6, -5, -4, 0, 1, 2, 6, 7, 8], # Override, Facing East
    24: [-8, -7, -6, -2, -1, 0, 4, 5, 6], # Override, Facing East
}

# Under assumption of 6x8 map
# Constants to assume whether a tile is valid for AOE targeting (not off map)
tile_conditions = {
    -18: lambda x: 0 <= x <= 48,
    -12: lambda x: 0 <= x <= 48,
    -7: lambda x: 0 <= x <= 48 and (x - 1) % 6 < 5,
    -6: lambda x: 0 <= x <= 48,
    -5: lambda x: 0 <= x <= 48 and (x + 1) % 6 > 0,
    -2: lambda x: (x - 2) % 6 < 4,
    -1: lambda x: (x - 1) % 6 < 5,
    0: lambda x: True,
    1: lambda x: (x + 1) % 6 > 0,
    2: lambda x: (x + 2) % 6 > 1,
    5: lambda x: 0 <= x <= 48 and (x - 1) % 6 < 5,
    6: lambda x: 0 <= x <= 48,
    7: lambda x: 0 <= x <= 48 and (x + 1) % 6 > 0,
    12: lambda x: 0 <= x <= 48,
    18: lambda x: 0 <= x <= 48,
}


# Returns all tiles to be targeted by an AOE move given a certain position and tile range
def aoe_tiles(user_tile, target_tile, aoe_range_num):
    if aoe_range_num != 30:
        pattern = aoe_patterns[aoe_range_num]
    else:
        pattern = aoe_patterns[14]

    final_tiles = []

    for tile in pattern:
        if tile_conditions[tile](target_tile) and tile + target_tile >= 0 and tile + target_tile <= 47:
            final_tiles.append(tile + target_tile)

    override_tiles = []
    if aoe_range_num == 30:

        is_alligned_vertical = user_tile % 6 == target_tile % 6

        for tile in final_tiles:
            if is_alligned_vertical:

                if user_tile > target_tile:
                    change = -6
                else:
                    change = 6

                if 0 <= (tile + change) // 6 <= 7:
                    override_tiles.append(tile + change)

            else:
                if user_tile > target_tile:
                    change = -1
                else:
                    change = 1

                if 0 <= (tile % 6 + change) <= 5:
                    override_tiles.append(tile + change)

        final_tiles = override_tiles

    return final_tiles

def get_aoe_precharge(unit, spaces_moved):
    total_precharge = 0

    unitSkills = unit.getSkills()

    if "momentumCharge" in unitSkills and spaces_moved > 0 and unit.getSpecialType() == "AOE":
        if spaces_moved >= 3:
            total_precharge += 2
        else:
            total_precharge += 1

    if "truthfire" in unitSkills and unit.HPcur / unit.get_visible_stat(HP) >= 0.25 and unit.getSpecialType() == "AOE":
        total_precharge += 1

    if "nectarsMagic" in unitSkills and unit.getSpecialType() == "AOE":
        total_precharge += 1

    return total_precharge

def get_aoe_disable(unit, enemy):
    aoe_disabled = False

    unitSkills = unit.getSkills()
    enemySkills = enemy.getSkills()

    if "You get NOTHING" in unitSkills or "You get NOTHING" in enemySkills:
        aoe_disabled = True

    if "sfLuciaBoost" in unitSkills or "sfLuciaBoost" in enemySkills:
        aoe_disabled = True

    if "fogadoBoost" in enemySkills and unit.wpnType in RANGED_WEAPONS:
        aoe_disabled = True

    return aoe_disabled

# STRING COLLECTION
# -- EFFECT TYPES --
# buff_stat   - Applies buff of stat by value
# debuff_stat - Applies debuff of stat by value
# status      - Applies status given by value
# damage      - Deals N damage given by value
# heal        - Heals N health given by value
# end_action    - Ends action

# -- GROUP TYPES --
# self                - applies to only self
# foe                 - applies to only foe
# allies              - applies to only self's allies
# foes_allies         - applies to only foe's allies
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

def foes_in_group_ranged_nonflier(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side != x.side and x.wpnType in RANGED_WEAPONS and x.move != 2:
            returned_list.append(x)
    return returned_list

def allies_in_group(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side and x != unit:
            returned_list.append(x)

    return returned_list

def ally_marias(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side and x != unit and ("sacrificeStaff" in x.getSkills()):
            returned_list.append(x)

    return returned_list

def ally_lenas(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side and x != unit and ("martyrsStaff" in x.getSkills()):
            returned_list.append(x)

    return returned_list

def ally_rheas(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side and x != unit and "vRheaBoost" in x.getSkills():
            returned_list.append(x)

    return returned_list

def foe_frammes(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side != x.side and x != other and "It's a shuffling in the seat." in x.getSkills():
            returned_list.append(x)

    return returned_list

def allies_plus_unit(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side:
            returned_list.append(x)

    return returned_list

def essence_drainers_plus_unit(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side and Status.EssenceDrain in x.statusPos:
            returned_list.append(x)

    return returned_list

def allies_infantry_plus_unit(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side and x.move == 0:
            returned_list.append(x)

    return returned_list

def allies_flying_plus_unit(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side and x.move == 2:
            returned_list.append(x)

    return returned_list

def allies_infantry_armored_plus_unit(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side and (x.move == 0 or x.move == 3):
            returned_list.append(x)

    return returned_list

def allies_flying_armored_plus_unit(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side == x.side and (x.move == 2 or x.move == 3):
            returned_list.append(x)

    return returned_list

def allies_same_game_plus_unit(unit, other, units_in_area):
    returned_list = [unit]

    for x in units_in_area:
        if unit.isAllyOf(x) and unit.isSameGameAs(x):
            returned_list.append(x)

    return returned_list

def foes_minus_other(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side != x.side and x != other:
            returned_list.append(x)
    return returned_list

def highest_spd_foes_allies(unit, other, units_in_area):
    returned_list = []

    for x in units_in_area:
        if unit.side != x.side and x != other:
            returned_list.append(x)

    fastest_units = []
    for x in returned_list:
        if not fastest_units or x.get_visible_stat(SPD) == fastest_units[0].get_visible_stat(SPD):
            fastest_units.append(x)
        elif x.get_visible_stat(SPD) > fastest_units[0].get_visible_stat(SPD):
            fastest_units = [x]

    return fastest_units

def end_of_combat(atk_effects, def_effects, attacker, defender, savior_unit, units_to_move):
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()

    defSkills = defender.getSkills()
    defStats = defender.getStats()

    damage_taken = {}
    heals_given = {}
    absolute_heals_given = {}

    heals_disabled = []

    sp_charges = {}
    end_actions = []

    # key: type ("flame", "haze", etc.)
    # value: arr of tile ints for that DV
    divine_veins = {}

    atkAreas = {}
    atkAreas['one'] = [attacker, defender]
    atkAreas['within_1_spaces_self'] = attacker.tile.unitsWithinNSpaces(1)
    atkAreas['within_2_spaces_self'] = attacker.tile.unitsWithinNSpaces(2)
    atkAreas['within_3_spaces_self'] = attacker.tile.unitsWithinNSpaces(3)
    atkAreas['within_4_spaces_self'] = attacker.tile.unitsWithinNSpaces(4)
    atkAreas['within_1_rows_cols_self'] = [tile.hero_on for tile in attacker.tile.tilesWithinNRowsOrCols(1, 1) if tile.hero_on is not None]
    atkAreas['within_3_rows_cols_self'] = [tile.hero_on for tile in attacker.tile.tilesWithinNRowsOrCols(3, 3) if tile.hero_on is not None]
    atkAreas['within_3_columns_self']: attacker.tile.unitsWithinNCols(3)
    atkAreas['within_1_spaces_foe'] = defender.tile.unitsWithinNSpaces(1)
    atkAreas['within_2_spaces_foe'] = defender.tile.unitsWithinNSpaces(2)
    atkAreas['within_3_spaces_foe'] = defender.tile.unitsWithinNSpaces(3)
    atkAreas['within_4_spaces_foe'] = defender.tile.unitsWithinNSpaces(4)
    atkAreas['nearest_self'] = nearest_allies_within_n(attacker, 16) + nearest_foes_within_n(attacker, 16) + [attacker]
    atkAreas['global'] = attacker.tile.unitsWithinNSpaces(16)

    defAreas = {}
    defAreas['one'] = [defender, attacker]
    defAreas['within_1_spaces_self'] = defender.tile.unitsWithinNSpaces(1)
    defAreas['within_2_spaces_self'] = defender.tile.unitsWithinNSpaces(2)
    defAreas['within_3_spaces_self'] = defender.tile.unitsWithinNSpaces(3)
    defAreas['within_4_spaces_self'] = defender.tile.unitsWithinNSpaces(4)
    defAreas['within_1_rows_cols_self'] = [tile.hero_on for tile in defender.tile.tilesWithinNRowsOrCols(1, 1) if tile.hero_on is not None]
    defAreas['within_3_rows_cols_self'] = [tile.hero_on for tile in defender.tile.tilesWithinNRowsOrCols(3, 3) if tile.hero_on is not None]
    defAreas['within_3_columns_self']: defender.tile.unitsWithinNCols(3)
    defAreas['within_1_spaces_foe'] = attacker.tile.unitsWithinNSpaces(1)
    defAreas['within_2_spaces_foe'] = attacker.tile.unitsWithinNSpaces(2)
    defAreas['within_3_spaces_foe'] = attacker.tile.unitsWithinNSpaces(3)
    defAreas['within_4_spaces_foe'] = attacker.tile.unitsWithinNSpaces(4)
    defAreas['nearest_self'] = nearest_allies_within_n(defender, 16) + nearest_foes_within_n(defender, 16) + [defender]
    defAreas['global'] = defender.tile.unitsWithinNSpaces(16)

    defAreas['nearest_within_4_spaces_foe'] = []

    for i in range(1, 5):
        if nearest_allies_within_n(attacker, i) and any([foe for foe in nearest_allies_within_n(attacker, i) if foe in units_to_move]):
            defAreas['nearest_within_4_spaces_foe'] = nearest_allies_within_n(attacker, i)
            break

    areaMethods = {'self': get_self,
                   'foe': get_foe,
                   'allies': allies_in_group,
                   'ally_marias': ally_marias,
                   'ally_lenas': ally_lenas,
                   'ally_rheas': ally_rheas,
                   'foe_frammes': foe_frammes,
                   'self_and_allies': allies_plus_unit,
                   'self_and_essence_drainers': essence_drainers_plus_unit,
                   'foes_allies': foes_minus_other,
                   'foe_and_foes_allies': foes_in_group,
                   'highest_spd_foes_ally': highest_spd_foes_allies
                   }

    combined = atk_effects + def_effects

    # Apply Essence Drain first
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

        # Hey, when you're here for Dimitri's Pure Atrocity, his bonus removal happens after this.

        if effect[0] == "essence_drain":
            bonus_receivers = [ally for ally in allies_within_n(unit, 20) if Status.EssenceDrain in ally.statusPos] + [unit]

            if any([Status.Dosage in foe.statusPos for foe in targeted_units]):
                unit.statusPos.clear()
                unit.buffs = [0, 0, 0, 0, 0]
            else:
                for foe in targeted_units:
                    for ally in bonus_receivers:
                        for status in foe.statusPos:
                            ally.inflictStatus(status)
                            ally.inflictStatus(status)

                        ally.buffs[ATK] = max(ally.buffs[ATK], foe.buffs[ATK])
                        ally.buffs[SPD] = max(ally.buffs[SPD], foe.buffs[SPD])
                        ally.buffs[DEF] = max(ally.buffs[DEF], foe.buffs[DEF])
                        ally.buffs[RES] = max(ally.buffs[RES], foe.buffs[RES])

                    foe.statusPos.clear()
                    foe.buffs = [0, 0, 0, 0, 0]

        i += 1

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

        if effect[0] == "buff_omni":
            for x in targeted_units:
                x.inflictStat(ATK, effect[1])
                x.inflictStat(SPD, effect[1])
                x.inflictStat(DEF, effect[1])
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

        if effect[0] == "great_talent_atk":
            for x in targeted_units:
                x.inflictGreatTalent(ATK, effect[1][0], effect[1][1])

        if effect[0] == "great_talent_spd":
            for x in targeted_units:
                x.inflictGreatTalent(SPD, effect[1][0], effect[1][1])

        if effect[0] == "great_talent_def":
            for x in targeted_units:
                x.inflictGreatTalent(DEF, effect[1][0], effect[1][1])

        if effect[0] == "great_talent_res":
            for x in targeted_units:
                x.inflictGreatTalent(RES, effect[1][0], effect[1][1])

        if effect[0] == "debuff_omni":
            for x in targeted_units:
                x.inflictStat(ATK, -effect[1])
                x.inflictStat(SPD, -effect[1])
                x.inflictStat(DEF, -effect[1])
                x.inflictStat(RES, -effect[1])

        if effect[0] == "damage":
            for x in targeted_units:
                if x.HPcur != 0:
                    if x not in damage_taken:
                        damage_taken[x] = effect[1]
                    else:
                        damage_taken[x] += effect[1]

        if effect[0] == "heal":
            for x in targeted_units:
                if x.HPcur != 0:
                    if x not in heals_given:
                        heals_given[x] = effect[1]
                    else:
                        heals_given[x] += effect[1]

        # Unaffected by Deep Wounds
        if effect[0] == "absolute_heal":
            for x in targeted_units:
                if x.HPcur != 0:
                    if x not in absolute_heals_given:
                        absolute_heals_given[x] = effect[1]
                    else:
                        absolute_heals_given[x] += effect[1]

        # Disable healing
        if effect[0] == "disable_heal":
            for x in targeted_units:
                heals_disabled.append(x)

        if effect[0] == "status":
            for x in targeted_units:
                if not(effect[1] == Status.CancelAction and any([ally for ally in (allies_within_n(x, 3) + [x]) if "cantoCurbStomp" in ally.getSkills()])):
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

        if effect[0] == "end_action":
            for x in targeted_units:
                if not any([ally for ally in (allies_within_n(x, 3) + [x]) if "cantoCurbStomp" in ally.getSkills()]):
                    end_actions.append(x)

        if effect[0] == "enable_once_per_map":
            for x in targeted_units:
                x.once_per_map_cond = True

        if effect[0] == "enable_once_per_turn":
            for x in targeted_units:
                x.assist_galeforce_triggered = True

        if effect[0] == "disable_weapon":
            for x in targeted_units:
                x.statusOther["disableWeapon"] = effect[1]

        if effect[0] == "disable_special":
            for x in targeted_units:
                x.statusOther["disableSpecial"] = effect[1]

        if effect[0] == "disable_bskill":
            for x in targeted_units:
                x.statusOther["disableBSkill"] = effect[1]

        if effect[0] == "disable_emblem":
            for x in targeted_units:
                x.statusOther["disableEmblem"] = effect[1]

        if effect[0] == "dv_haze":
            if (unit, "haze") not in divine_veins:
                divine_veins[(unit, "haze")] = []

            for tile in defender.tile.tilesWithinNSpaces(effect[1]):
                divine_veins[(unit, "haze")].append(tile.tileNum)

        if effect[0] == "dv_water":
            if (unit, "water") not in divine_veins:
                divine_veins[(unit, "water")] = []

            for tile in targeted_units[0].tile.tilesWithinNSpaces(effect[1]):
                divine_veins[(unit, "water")].append(tile.tileNum)

        if effect[0] == "dv_flame":
            if (unit, "flame") not in divine_veins:
                divine_veins[(unit, "flame")] = []

            # Ranged Units cannot create 2 rows of Flame
            if not(unit.wpnType in RANGED_WEAPONS and effect[1] == 2):
                divine_veins[(unit, "flame")].append(defender.tile.tileNum)

                # Both units are in same row
                if unit.tile.y_coord == defender.tile.y_coord:

                    if defender.tile.north:
                        divine_veins[(unit, "flame")].append(defender.tile.north.tileNum)

                        if defender.tile.north.north:
                            divine_veins[(unit, "flame")].append(defender.tile.north.north.tileNum)

                    if defender.tile.south:
                        divine_veins[(unit, "flame")].append(defender.tile.south.tileNum)

                        if defender.tile.south.south:
                            divine_veins[(unit, "flame")].append(defender.tile.south.south.tileNum)

                    # Make two lines
                    if effect[1] == 2:
                        atk_east_of_def = unit.tile.x_coord > defender.tile.x_coord

                        if atk_east_of_def:
                            cur_tile = defender.tile.west
                        else:
                            cur_tile = defender.tile.east

                        if cur_tile:
                            divine_veins[(unit, "flame")].append(cur_tile.tileNum)

                            if cur_tile.north:
                                divine_veins[(unit, "flame")].append(cur_tile.north.tileNum)

                                if cur_tile.north.north:
                                    divine_veins[(unit, "flame")].append(cur_tile.north.north.tileNum)

                            if cur_tile.south:
                                divine_veins[(unit, "flame")].append(cur_tile.south.tileNum)

                                if cur_tile.south.south:
                                    divine_veins[(unit, "flame")].append(cur_tile.south.south.tileNum)

                # Both units are in the same column
                elif unit.tile.x_coord == defender.tile.x_coord:
                    if defender.tile.east:
                        divine_veins[(unit, "flame")].append(defender.tile.east.tileNum)

                        if defender.tile.east.east:
                            divine_veins[(unit, "flame")].append(defender.tile.east.east.tileNum)

                    if defender.tile.west:
                        divine_veins[(unit, "flame")].append(defender.tile.west.tileNum)

                        if defender.tile.west.west:
                            divine_veins[(unit, "flame")].append(defender.tile.west.west.tileNum)

                    # Make two lines
                    if effect[1] == 2:
                        atk_north_of_def = unit.tile.y_coord > defender.tile.y_coord

                        if atk_north_of_def:
                            cur_tile = defender.tile.south
                        else:
                            cur_tile = defender.tile.north

                        if cur_tile:
                            divine_veins[(unit, "flame")].append(cur_tile.tileNum)

                            if cur_tile.east:
                                divine_veins[(unit, "flame")].append(cur_tile.east.tileNum)

                                if cur_tile.east.east:
                                    divine_veins[(unit, "flame")].append(cur_tile.east.east.tileNum)

                            if cur_tile.west:
                                divine_veins[(unit, "flame")].append(cur_tile.west.tileNum)

                                if cur_tile.west.west:
                                    divine_veins[(unit, "flame")].append(cur_tile.west.west.tileNum)

                # Attacker southwest or northeast of target
                elif (unit.tile.x_coord < defender.tile.x_coord and unit.tile.y_coord < defender.tile.y_coord) or (unit.tile.x_coord > defender.tile.x_coord and unit.tile.y_coord > defender.tile.y_coord):
                    if defender.tile.north and defender.tile.north.west:
                        divine_veins[(unit, "flame")].append(defender.tile.north.west.tileNum)

                        if defender.tile.north.west.north and defender.tile.north.west.north.west:
                            divine_veins[(unit, "flame")].append(defender.tile.north.west.north.west.tileNum)

                    if defender.tile.south and defender.tile.south.east:
                        divine_veins[(unit, "flame")].append(defender.tile.south.east.tileNum)

                        if defender.tile.south.east.south and defender.tile.south.east.south.east:
                            divine_veins[(unit, "flame")].append(defender.tile.south.east.south.east.tileNum)

                # Attacker southeast or northwest of target
                else:
                    if defender.tile.north and defender.tile.north.east:
                        divine_veins[(unit, "flame")].append(defender.tile.north.east.tileNum)

                        if defender.tile.north.east.north and defender.tile.north.east.north.east:
                            divine_veins[(unit, "flame")].append(defender.tile.north.east.north.east.tileNum)

                    if defender.tile.south and defender.tile.south.west:
                        divine_veins[(unit, "flame")].append(defender.tile.south.west.tileNum)

                        if defender.tile.south.west.south and defender.tile.south.west.south.west:
                            divine_veins[(unit, "flame")].append(defender.tile.south.west.south.west.tileNum)

        if effect[0] == "remove_bonuses":
            for x in targeted_units:
                for j in range(0, effect[1]):
                    first_two_buffs = sorted(x.statusPos, key=lambda e: e.value)[:2]

                    for status in first_two_buffs:
                        unit.statusPos.remove(status)

        i += 1

    # Invincible Seals
    for unit in damage_taken:
        if "invincible" in unit.getSkills():
            damage_taken[unit] = 0

    for unit in heals_given:
        if unit in heals_disabled:
            heals_given[unit] = 0

    return damage_taken, heals_given, absolute_heals_given, sp_charges, divine_veins, end_actions

def get_after_assist_veins(unit, target):
    divine_veins = {}

    unitSkills = unit.getSkills()
    unitStats = unit.getStats()

    # Ice Lock(+)
    if "iceLock" in unitSkills or "iceLockPlus" in unitSkills:
        ice_present = False

        for tile in unit.tile.tilesWithinNSpaces(20):
            if tile.divine_vein == DV_ICE and tile.divine_vein_side == unit.side and tile.divine_vein_turn > 0:
                ice_present = True

        if not ice_present:
            if "ice" not in divine_veins:
                divine_veins["ice"] = []

            for tile in target.tile.tilesNSpacesAway(2):
                divine_veins["ice"].append(tile.tileNum)

    # Exalt's Tactics - B!F!Robin
    if "exaltsTactics" in unitSkills:
        ice_present = False

        for tile in unit.tile.tilesWithinNSpaces(20):
            if tile.divine_vein == DV_ICE and tile.divine_vein_side == unit.side and tile.divine_vein_turn > 0:
                ice_present = True

        if not ice_present:
            if "ice" not in divine_veins:
                divine_veins["ice"] = []

            for tile in target.tile.tilesNSpacesAway(2):
                divine_veins["ice"].append(tile.tileNum)

    return divine_veins

def get_after_action_veins(unit, is_canto):
    divine_veins = {}

    unitSkills = unit.getSkills()
    unitStats = unit.getStats()

    # Fortifications
    if "fortificationStone" in unitSkills and not is_canto and unit.unitCombatInitiates > 0:
        if "stone" not in divine_veins:
            divine_veins["stone"] = []

        for tile in unit.tile.tilesWithinNSpaces(2):
            divine_veins["stone"].append(tile.tileNum)

    # Oath of Ostia (Refine Eff) - Dedue
    if "oathOfOstia" in unitSkills and not is_canto:
        if "stone" not in divine_veins:
            divine_veins["stone"] = []

        for tile in unit.tile.tilesWithinNSpaces(2):
            divine_veins["stone"].append(tile.tileNum)

    # Vallastone (Base) - B!F!Corrin
    if "NOT THE DYNAMIC TILES" in unitSkills and not is_canto:
        if "stone" not in divine_veins:
            divine_veins["stone"] = []

        for tile in unit.tile.tilesWithinNSpaces(2):
            divine_veins["stone"].append(tile.tileNum)

    # Taciturn Axe (Refine Eff) - Dedue
    if "taciturnAxe" in unitSkills and not is_canto:
        if "stone" not in divine_veins:
            divine_veins["stone"] = []

        for tile in unit.tile.tilesWithinNSpaces(2):
            divine_veins["stone"].append(tile.tileNum)

    # Dragon Monarch - MY!Lumera
    if ("dragonMonarch" in unitSkills or "corruptedDragon" in unitSkills) and not is_canto:
        if "stone" not in divine_veins:
            divine_veins["stone"] = []

        tiles_within_5_row = unit.tile.tilesWithinNRows(5)
        tiles_within_5_col = unit.tile.tilesWithinNCols(5)
        tiles_within_5_row_and_column = list(set(tiles_within_5_row) & set(tiles_within_5_col))

        for tile in tiles_within_5_row_and_column:
            divine_veins["stone"].append(tile.tileNum)

    # Mending Heart - Ratatoskr
    if "it's her!" in unitSkills:
        if "green" not in divine_veins:
            divine_veins["green"] = []

        for tile in unit.tile.tilesWithinNSpaces(2):
            divine_veins["green"].append(tile.tileNum)

    # Exalt's Tactics - B!F!Robin
    if "exaltsTactics" in unitSkills and not is_canto:
        ice_present = False

        for tile in unit.tile.tilesWithinNSpaces(20):
            if tile.divine_vein == DV_ICE and tile.divine_vein_side == unit.side and tile.divine_vein_turn > 0:
                ice_present = True

        if not ice_present:
            if "ice" not in divine_veins:
                divine_veins["ice"] = []

            for tile in unit.tile.tilesNSpacesAway(2):
                divine_veins["ice"].append(tile.tileNum)

    return divine_veins

def apply_after_action_stats(unit, is_canto):
    unitSkills = unit.getSkills()

    # Tome of Dusk - CH!Leo
    if "chLeoBoost" in unitSkills and not is_canto:
        unit.chargeSpecial(1)

        if unit.unitCombatInitiates + unit.assistTargetedOther + unit.moveOrDestroyActions <= 2:
            unit_res = unit.get_visible_stat(RES) + unit.get_phantom_stat(RES)

            for foe in foes_within_n_cardinal(unit, 3):
                foe_res = foe.get_visible_stat(RES) + foe.get_phantom_stat(RES)

                if foe_res < unit_res + 5:
                    foe.inflictStat(ATK, -7)
                    foe.inflictStat(RES, -7)
                    foe.inflictStatus(Status.Sabotage)

                    if foe in foes_within_n_cardinal(unit, 1):
                        foe.inflictStatus(Status.Gravity)

    # Pure Storm - V!Edelgard
    if "pureStorm" in unitSkills and not is_canto:
        affected_foes = []

        for foe in nearest_foes_within_n(unit, 20):
            if foe not in affected_foes:
                affected_foes.append(foe)

            for ally in allies_within_n(foe, 2):
                if ally not in affected_foes:
                    affected_foes.append(ally)

        for foe in affected_foes:
            foe.inflictStat(ATK, -7)
            foe.inflictStat(DEF, -7)
            foe.inflictStatus(Status.Sabotage)
            foe.inflictStatus(Status.Exposure)

    # Brutal Ferocity - Þjazi
    if "brutalFerocity" in unitSkills and not is_canto:
        for foe in foes_within_n_cardinal(unit, 1):
            if foe.HPcur < unit.get_visible_stat(HP):
                foe.inflictStat(ATK, -7)
                foe.inflictStat(DEF, -7)
                foe.inflictStatus(Status.Gravity)

    # Jaws of Closure - Elm
    if "elmBoost" in unitSkills and not is_canto:
        for foe in nearest_foes_within_n(unit, 5):
            foe.inflictStatus(Status.Undefended)

    # Enticing Dose - Níðhöggr
    if "God's strongest drunk driver" in unitSkills and not is_canto:
        for foe in foes_within_n_cardinal(unit, 3):
            foe.inflictStat(ATK, -7)
            foe.inflictStat(DEF, -7)
            foe.inflictStatus(Status.Sabotage)

    return

# Returns True if duo skill can be used by unit, False otherwise
def can_use_duo_skill(unit, units_to_move):
    if not unit.duo_skill:
        return False

    unitAreas = {'one': [unit],
                 'within_1_spaces': unit.tile.unitsWithinNSpaces(1),
                 'within_2_spaces': unit.tile.unitsWithinNSpaces(2),
                 'within_3_spaces': unit.tile.unitsWithinNSpaces(2),
                 'within_4_spaces': unit.tile.unitsWithinNSpaces(4),
                 'nearest_self': nearest_allies_within_n(unit, 16) + nearest_foes_within_n(unit, 16),
                 'within_3_columns': unit.tile.unitsWithinNCols(3),
                 'within_3_rows': unit.tile.unitsWithinNCols(3),
                 'within_1_rows_or_cols': allies_within_n_cardinal(unit, 1) + foes_within_n_cardinal(unit, 1),
                 'within_1_rows_or_cols_or_has_penalty': allies_within_n_cardinal(unit, 1) + foes_within_n_cardinal(unit, 1),
                 'within_3_rows_or_cols': allies_within_n_cardinal(unit, 3) + foes_within_n_cardinal(unit, 3),
                 'within_5_rows_and_cols': allies_within_n_box(unit, 5) + foes_within_n_box(unit, 5),
                 'within_5_rows_or_cols': allies_within_n_cardinal(unit, 5) + foes_within_n_cardinal(unit, 5),
                 'within_7_rows_and_cols': allies_within_n_box(unit, 7) + foes_within_n_box(unit, 7),
                 'global': unit.tile.unitsWithinNSpaces(16)
                 }

    areaMethods = {'self': get_self,
                   'allies': allies_in_group,
                   'self_and_allies': allies_plus_unit,
                   'self_and_allies_infantry': allies_infantry_plus_unit,
                   'self_and_allies_flying': allies_flying_plus_unit,
                   'self_and_allies_infantry_armored': allies_infantry_armored_plus_unit,
                   'self_and_allies_flying_armored': allies_flying_armored_plus_unit,
                   'self_and_same_game_allies': allies_same_game_plus_unit,
                   'foes': foes_in_group,
                   'foes_ranged_nonflier': foes_in_group_ranged_nonflier
                   }

    result = False

    for effect in unit.duo_skill.effects:
        # Call methods
        units_in_area = unitAreas[effect['area']]
        unit_determine_method = areaMethods[effect['targets']]

        targeted_units = unit_determine_method(unit, None, units_in_area)
        # If effect grants effect to self, can be used at any time.
        if ("self" in effect['targets'] and effect["effect"] != "galeforce" and effect["effect"] != "dance") or "global" in effect['area'] or (targeted_units and effect['effect'] != "repo"):
            result = True

        elif effect["effect"] == "galeforce" or effect["effect"] == "galeforce_plus_canto_better":
            if unit.unitCombatInitiates >= 1 and unit not in units_to_move:
                result = True

        elif effect["effect"] == "galeforce_plus_canto":
            if unit not in units_to_move and any([ally for ally in allies_within_n(unit, 3) if ally.unitCombatInitiates >= 1]):
                result = True

        elif effect["effect"] == "dance":
            highest_hp_allies = []

            for x in targeted_units:
                if x not in units_to_move and x != unit:
                    if not highest_hp_allies or highest_hp_allies[0].HPcur == x.HPcur:
                        highest_hp_allies.append(x)
                    elif highest_hp_allies[0].HPcur < x.HPcur:
                        highest_hp_allies = [x]

            if len(highest_hp_allies) == 1:
                result = True

        # DA!Sigurd
        elif effect['effect'] == "repo":
            vertical_allies = list(set(allies_within_n(unit, 1)) & set(unit.tile.unitsWithinNCols(1)))

            if len(vertical_allies) == 1:
                ally = vertical_allies[0]

                if ally.tile == unit.tile.north:
                    repo_tile = unit.tile.south
                else:
                    repo_tile = unit.tile.north

                if repo_tile and not repo_tile.hero_on and can_be_on_tile(repo_tile, ally):
                    result = True

            horizontal_allies = list(set(allies_within_n(unit, 1)) & set(unit.tile.unitsWithinNRows(1)))

            if len(horizontal_allies) == 1:
                ally = horizontal_allies[0]

                if ally.tile == unit.tile.east:
                    repo_tile = unit.tile.west
                else:
                    repo_tile = unit.tile.east

                if repo_tile and not repo_tile.hero_on and can_be_on_tile(repo_tile, ally):
                    result = True

        #else:
            #result = False

    return result
