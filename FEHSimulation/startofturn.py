from hero import *

def start_of_turn(team):

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

        if "bridal_shenanigans" in unitSkills and atkHPGreaterEqual25Percent:
            unit.inflictStat(ATK, 6)
            unit.inflictStat(SPD, 6)
            unit.inflictStatus(Status.MobilityUp)
