import math
import random
from enum import Enum
from hero import *

# CONSTANTS
HP = 0
ATK = 1
SPD = 2
DEF = 3
RES = 4


class HeroModifiers:
    def __init__(self):
        # attack order
        self.brave = False

        self.vantage = False
        self.self_desperation = False
        self.other_desperation = False
        self.hardy_bearing = False

        self.potent_FU = False
        self.potent_new_percentage = -1

        # follow-ups
        self.follow_ups_skill = 0
        self.follow_ups_spd = 0
        self.follow_up_denials = 0

        # NFU
        self.prevent_foe_FU = False
        self.prevent_self_FU_denial = False

        # special
        self.special_disabled = False

        self.spGainOnAtk = 0
        self.spLossOnAtk = 0
        self.spGainWhenAtkd = 0
        self.spLossWhenAtkd = 0

        self.sp_charge_first = 0
        self.sp_charge_FU = 0
        self.sp_charge_foe_first = 0

        self.disable_foe_fastcharge = False
        self.disable_foe_guard = False

        self.double_def_sp_charge = False # negating fang ii

        self.first_sp_charge = 0

        self.special_triggered = False

        # percent damage reduction
        self.DR_all_hits_NSP = []
        self.DR_first_hit_NSP = []
        self.DR_first_strikes_NSP = []
        self.DR_second_strikes_NSP = []
        self.DR_consec_strikes_NSP = []
        self.DR_sp_trigger_next_only_NSP = []

        self.DR_all_hits_SP = []
        self.DR_sp_trigger_next_only_SP = []
        self.DR_sp_trigger_next_all_SP = []
        self.DR_sp_trigger_next_all_SP_CACHE = []

        self.DR_great_aether_SP = False

        self.damage_reduction_reduction = 1

        self.sp_pierce_DR = False
        self.pierce_DR_FU = False
        self.always_pierce_DR = False
        self.sp_pierce_after_def_sp = False # laguz friend 4
        self.sp_pierce_after_def_sp_CACHE = False

        # true damage / true reduction
        self.true_all_hits = 0
        self.true_first_hit = 0  # domain of flame
        self.true_finish = 0
        self.true_after_foe_first = 0
        self.true_sp = 0  # wo dao

        self.true_sp_next = 0  # divine pulse/negating fang
        self.true_sp_next_CACHE = 0

        self.TDR_all_hits = 0
        self.TDR_first_strikes = 0
        self.TDR_second_strikes = 0
        self.TDR_on_def_sp = 0

        self.TDR_dmg_taken_cap = 0
        self.TDR_dmg_taken_extra_stacks = 0

        self.reduce_self_sp_damage = 0  # emblem marth

        self.retaliatory_reduced = False  # enables divine recreation
        self.nonstacking_retaliatory_damage = 0  # divine recreation
        self.stacking_retaliatory_damage = 0  # ice mirror
        self.retaliatory_full_damages = []  # full retaliatory damage values for brash assault/counter roar
        self.retaliatory_full_damages_CACHE = []  # temporarily holds full retaliatory
        self.most_recent_atk = 0  # used in calculating this vvvvv
        self.retaliatory_next = 0  # brash assault/counter roar uses most recent hit's damage

        self.burn_damage = 0
        self.capped_burn_damage = 0

        # healing
        self.all_hits_heal = 0
        self.follow_up_heal = 0
        self.finish_mid_combat_heal = 0

        self.deep_wounds_allowance = 0
        self.disable_foe_healing = False

        self.surge_heal = 0

        # miracle
        self.pseudo_miracle = False
        self.circlet_miracle = False
        self.disable_foe_miracle = False


def move_letters(s, letter):
    if letter not in ['A', 'D']:
        return "Invalid letter"

    first_occurrence = s.find(letter)
    if first_occurrence == -1:
        return s

    remaining_part = s[first_occurrence + 1:]
    moved_letters = s[first_occurrence] * remaining_part.count(letter)
    new_string = s[:first_occurrence + 1] + moved_letters + remaining_part.replace(letter, '')

    return new_string


def simulate_combat(attacker, defender, is_in_sim, turn, spaces_moved_by_atkr, combat_effects):
    # Invalid Combat if one unit is dead
    # or if attacker does not have weapon
    if attacker.HPcur <= 0 or defender.HPcur <= 0 or attacker.weapon is None: return (-1, -1)

    # OK I gotta do some research on all cases of this
    # actually wait shouldn't this only get incremented upon the ACTUAL combat?
    # Known cases: Kvasir/NY!Kvasir, Fell Star, Resonance: Shields
    attacker.unitCombatInitiates += 1
    defender.enemyCombatInitiates += 1

    # who possesses the weapon triangle advantage
    # 0 - attacker
    # 1 - defender
    # -1 - neither
    wpnAdvHero = -1

    # lists of attacker/defender's skills & stats
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()
    atkPhantomStats = [0] * 5

    defSkills = defender.getSkills()
    defStats = defender.getStats()
    defPhantomStats = [0] * 5

    # stores important modifiers going into combat
    atkr = HeroModifiers()
    defr = HeroModifiers()

    atkHPCur = attacker.HPcur
    defHPCur = defender.HPcur

    atkSpCountCur = attacker.specialCount
    defSpCountCur = defender.specialCount

    if "phantomSpd" in atkSkills: atkPhantomStats[SPD] += max(atkSkills["phantomSpd"] * 3 + 2, 10)
    if "phantomRes" in atkSkills: atkPhantomStats[RES] += max(atkSkills["phantomRes"] * 3 + 2, 10)
    if "phantomSpd" in defSkills: defPhantomStats[SPD] += max(defSkills["phantomSpd"] * 3 + 2, 10)
    if "phantomRes" in defSkills: defPhantomStats[RES] += max(defSkills["phantomRes"] * 3 + 2, 10)

    # stored combat buffs (essentially everything)
    atkCombatBuffs = [0] * 5
    defCombatBuffs = [0] * 5

    # add effects of CombatFields
    if is_in_sim:
        atkSkills.update(e.effect for e in combat_effects if
                         e.affectedSide == 0 and e.range(attacker.tile) and e.condition(attacker) and (
                                     e.affectSelf or not e.owner == attacker))
        defSkills.update(e.effect for e in combat_effects if
                         e.affectedSide == 1 and e.range(defender.tile) and e.condition(defender) and (
                                     e.affectSelf or not e.owner == defender))

    # common position-based conditions
    atkAdjacentToAlly = 0
    atkAllyWithin2Spaces = 0
    atkAllyWithin3Spaces = 0
    atkAllyWithin4Spaces = 0
    defAdjacentToAlly = 0
    defAllyWithin2Spaces = 0
    defAllyWithin3Spaces = 0
    defAllyWithin4Spaces = 0

    if is_in_sim:
        atkAdjacentToAlly = attacker.tile.numWithinNSpaces(1, True)
        atkAllyWithin2Spaces = attacker.tile.numWithinNSpaces(2, True)
        atkAllyWithin3Spaces = attacker.tile.numWithinNSpaces(3, True)
        atkAllyWithin4Spaces = attacker.tile.numWithinNSpaces(4, True)
        defAdjacentToAlly = defender.tile.numWithinNSpaces(1, True)
        defAllyWithin2Spaces = defender.tile.numWithinNSpaces(2, True)
        defAllyWithin3Spaces = defender.tile.numWithinNSpaces(3, True)
        defAllyWithin4Spaces = defender.tile.numWithinNSpaces(4, True)

    atkFoeWithin2Spaces = 0
    defFoeWithin2Spaces = 0
    if is_in_sim:
        atkFoeWithin2Spaces = attacker.tile.numWithinNSpaces(2, False)
        defFoeWithin2Spaces = defender.tile.numWithinNSpaces(2, False)

    atk_allies_arr = []
    def_allies_arr = []

    atkInfAlliesWithin2Spaces = 0
    atkCavAlliesWithin2Spaces = 0
    atkFlyAlliesWithin2Spaces = 0
    atkArmAlliesWithin2Spaces = 0
    defInfAlliesWithin2Spaces = 0
    defCavAlliesWithin2Spaces = 0
    defFlyAlliesWithin2Spaces = 0
    defArmAlliesWithin2Spaces = 0

    if is_in_sim:
        atk_allies_arr = attacker.tile.unitsWithinNSpaces(2, True)

    for x in atk_allies_arr:
        if x.move == 0: atkInfAlliesWithin2Spaces += 1
        if x.move == 1: atkCavAlliesWithin2Spaces += 1
        if x.move == 2: atkFlyAlliesWithin2Spaces += 1
        if x.move == 3: atkArmAlliesWithin2Spaces += 1

    for x in def_allies_arr:
        if x.move == 0: defInfAlliesWithin2Spaces += 1
        if x.move == 1: defCavAlliesWithin2Spaces += 1
        if x.move == 2: defFlyAlliesWithin2Spaces += 1
        if x.move == 3: defArmAlliesWithin2Spaces += 1

    # common HP-based conditions
    atkHPGreaterEqual25Percent = atkHPCur / atkStats[0] >= 0.25
    atkHPGreaterEqual50Percent = atkHPCur / atkStats[0] >= 0.50
    atkHPGreaterEqual75Percent = atkHPCur / atkStats[0] >= 0.75
    atkHPEqual100Percent = atkHPCur == atkStats[0]

    defHPGreaterEqual25Percent = defHPCur / defStats[0] >= 0.25
    defHPGreaterEqual50Percent = defHPCur / defStats[0] >= 0.50
    defHPGreaterEqual75Percent = defHPCur / defStats[0] >= 0.75
    defHPEqual100Percent = defHPCur == defStats[0]

    # Genesis Falchion
    atkTop3AllyBuffTotal = 0
    defTop3AllyBuffTotal = 0

    # Dark Creator Sword
    atkNumAlliesHPGE90Percent = 0
    defNumAlliesHPGE90Percent = 0

    if is_in_sim:
        atkDefensiveTerrain = attacker.tile.is_def_terrain
        defDefensiveTerrain = defender.tile.is_def_terrain
    else:
        atkDefensiveTerrain = False
        defDefensiveTerrain = False

    # Panic Status Effect
    AtkPanicFactor = 1
    DefPanicFactor = 1

    # buffs + debuffs calculation
    # throughout combat, PanicFactor * buff produces the current buff value
    if Status.Panic in attacker.statusNeg: AtkPanicFactor *= -1
    if Status.Panic in defender.statusNeg: DefPanicFactor *= -1

    if Status.NullPanic in attacker.statusPos: AtkPanicFactor = 1
    if Status.NullPanic in defender.statusPos: DefPanicFactor = 1

    # apply buffs/debuffs

    atkStats[ATK] += attacker.buffs[ATK] * AtkPanicFactor + attacker.debuffs[ATK]
    atkStats[SPD] += attacker.buffs[SPD] * AtkPanicFactor + attacker.debuffs[SPD]
    atkStats[DEF] += attacker.buffs[DEF] * AtkPanicFactor + attacker.debuffs[DEF]
    atkStats[RES] += attacker.buffs[RES] * AtkPanicFactor + attacker.debuffs[RES]

    defStats[ATK] += defender.buffs[ATK] * DefPanicFactor + defender.debuffs[ATK]
    defStats[SPD] += defender.buffs[SPD] * DefPanicFactor + defender.debuffs[SPD]
    defStats[DEF] += defender.buffs[DEF] * DefPanicFactor + defender.debuffs[DEF]
    defStats[RES] += defender.buffs[RES] * DefPanicFactor + defender.debuffs[RES]

    # [Bonus] and [Penalty] conditions
    atkHasBonus = attacker.hasBonus()
    defHasBonus = defender.hasBonus()
    atkHasPenalty = attacker.hasPenalty()
    defHasPenalty = defender.hasPenalty()

    # triangle adept during combat, default of -1
    triAdept = -1

    # ignore range (distant/close counter)
    ignoreRng = False

    # prevent counterattacks from defender (sweep, flash)
    cannotCounter = False

    disableCannotcounter = False

    # cancel affinity, differs between ally and foe for
    # levels 2/3 because my life can't be easy
    atkCA = 0
    defCA = 0

    # damage done to self after combat
    atkSelfDmg = 0
    defSelfDmg = 0

    # damage done to other after combat iff self attacks other (should be added to atk/defSelfDmg)
    atkOtherDmg = 0
    defOtherDmg = 0

    # damage done to self iff self attacks other (should be added to atk/defSelfDmg)
    atkRecoilDmg = 0
    defRecoilDmg = 0

    # i dunno how to explain but i need them and to remove them i need to use a bit of brainpower
    NEWatkOtherDmg = 0
    NEWdefOtherDmg = 0

    # healing after combat, negated by deep wounds, cannot be reduced by special fighter 4
    atkPostCombatHealing = 0
    defPostCombatHealing = 0

    # special charge granted after combat (special spiral, dark mystletainn, etc.)
    atkPostCombatSpCharge = 0
    defPostCombatSpCharge = 0

    # status effects given after combat
    # 0 - given regardless
    # 1 - given if attacked by foe
    # 2 - given if attacked foe
    # ex: attacker has panic, defender is hit
    # elements of 2 with be appended to 0
    # at end of combat, all of 0 will be given to defender
    atkPostCombatStatusesApplied = [[], [], []]
    defPostCombatStatusesApplied = [[], [], []]

    atkBonusesNeutralized = [False] * 5
    defBonusesNeutralized = [False] * 5
    atkPenaltiesNeutralized = [False] * 5
    defPenaltiesNeutralized = [False] * 5

    # SOME STATUSES
    if Status.Discord in attacker.statusNeg:
        atkCombatBuffs[1] -= min(2 + atkAllyWithin2Spaces, 5)
        atkCombatBuffs[2] -= min(2 + atkAllyWithin2Spaces, 5)
        atkCombatBuffs[3] -= min(2 + atkAllyWithin2Spaces, 5)
        atkCombatBuffs[4] -= min(2 + atkAllyWithin2Spaces, 5)

    if Status.Discord in defender.statusNeg:
        defCombatBuffs[1] -= min(2 + defAllyWithin2Spaces, 5)
        defCombatBuffs[2] -= min(2 + defAllyWithin2Spaces, 5)
        defCombatBuffs[3] -= min(2 + defAllyWithin2Spaces, 5)
        defCombatBuffs[4] -= min(2 + defAllyWithin2Spaces, 5)

    # ATTACKER SKILLS -----------------------------------------------------------------------------------------------------------------------

    if "atkBlow" in atkSkills: atkCombatBuffs[1] += atkSkills["atkBlow"] * 2
    if "spdBlow" in atkSkills: atkCombatBuffs[2] += atkSkills["spdBlow"] * 2
    if "defBlow" in atkSkills: atkCombatBuffs[3] += atkSkills["defBlow"] * 2
    if "resBlow" in atkSkills: atkCombatBuffs[4] += atkSkills["resBlow"] * 2

    if "fireBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[1] += atkSkills["fireBoost"] * 2
    if "windBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[2] += atkSkills["windBoost"] * 2
    if "earthBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[3] += atkSkills["earthBoost"] * 2
    if "waterBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[4] += atkSkills["waterBoost"] * 2

    if "brazenAtk" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[1] += atkSkills["brazenAtk"]
    if "brazenSpd" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[2] += atkSkills["brazenSpd"]
    if "brazenDef" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[3] += atkSkills["brazenDef"]
    if "brazenRes" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[4] += atkSkills["brazenRes"]

    if "atkBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[1] += atkSkills["atkBond"]
    if "spdBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[2] += atkSkills["spdBond"]
    if "defBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[3] += atkSkills["defBond"]
    if "resBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[4] += atkSkills["resBond"]

    if "atkRein" in atkSkills: defCombatBuffs -= atkSkills["atkRein"]
    if "spdRein" in atkSkills: defCombatBuffs -= atkSkills["atkRein"]
    if "defRein" in atkSkills: defCombatBuffs -= atkSkills["atkRein"]
    if "resRein" in atkSkills: defCombatBuffs -= atkSkills["atkRein"]

    if "ILOVEBONUSES" in atkSkills and atkHPGreaterEqual50Percent or atkHasBonus:
        map(lambda x: x + 4, atkCombatBuffs)

    if "SEGAAAA" in atkSkills or "nintenesis" in atkSkills:
        map(lambda x: x + 5, atkCombatBuffs)
        if atkTop3AllyBuffTotal >= 10:
            atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True
            if "nintenesis" in atkSkills:
                atkr.disable_foe_guard = True
        if atkTop3AllyBuffTotal >= 25:
            atkCombatBuffs[1] += 5
            atkr.all_hits_heal += 5 + 2 * ("nintenesis" in atkSkills)

    if ("SEGAAAA" in defSkills or "nintenesis" in defSkills) and defAllyWithin2Spaces:
        map(lambda x: x + 5, defCombatBuffs)
        if defTop3AllyBuffTotal >= 10:
            defr.prevent_foe_FU, defr.prevent_self_FU_denial = True
            if "nintenesis" in defSkills:
                defr.disable_foe_guard = True
        if defTop3AllyBuffTotal >= 25:
            defCombatBuffs[1] += 5
            defr.all_hits_heal += 5 + 2 * ("nintenesis" in defSkills)
        if defTop3AllyBuffTotal >= 60:
            defr.vantage = True

    if "denesis" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.DR_first_strikes_NSP.append(40)
        atkCombatBuffs[1] += 5  # + highest atk bonus on self/allies within 2 spaces
        # and the rest of them

    if "denesis" in defSkills and defHPGreaterEqual25Percent:
        defr.DR_first_strikes_NSP.append(40)
        defCombatBuffs[1] += 5  # + highest atk bonus on self/allies within 2 spaces
        # and the rest of them

    if "caedaVantage" in defSkills and (
            attacker.wpnType in ["Sword", "Lance", "Axe", "CBow"] or attacker.move == 3 or defHPCur / defStats[
        0] <= 0.75):
        defr.vantage = True

    if "pureWing" in atkSkills and atkAllyWithin3Spaces:
        Y = min(atkAllyWithin3Spaces * 3 + 5, 14)
        atkCombatBuffs = [x + Y for x in atkCombatBuffs]
        atkr.damage_reduction_reduction *= (1-0.5)
        atkr.DR_all_hits_NSP.append(30)
        atkr.all_hits_heal += 7
        if defender.move == 3 or attacker.move == 1:
            atkr.all_hits_heal += 7

    if "guardraug" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[3] += 5
        atkPenaltiesNeutralized[ATK] = True
        atkPenaltiesNeutralized[DEF] = True

    if "guardraug" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5
        defPenaltiesNeutralized[ATK] = True
        defPenaltiesNeutralized[DEF] = True

    if "triangleAtk" in atkSkills and atkFlyAlliesWithin2Spaces >= 2:
        atkCombatBuffs = [x + 3 for x in atkCombatBuffs]
        atkr.brave = True

    if "triangleAtk" in defSkills and defFlyAlliesWithin2Spaces >= 2:
        map(lambda x: x + 3, defCombatBuffs)

    if "banana" in atkSkills and (atkInfAlliesWithin2Spaces > 0 or atkFlyAlliesWithin2Spaces > 0):
        atkCombatBuffs[1] += 4
        atkCombatBuffs[2] += 4

    if "banana" in defSkills and (defInfAlliesWithin2Spaces > 0 or defFlyAlliesWithin2Spaces > 0):
        defCombatBuffs[1] += 4
        defCombatBuffs[2] += 4

    if "bibleBros" in atkSkills:
        atkCombatBuffs[1] += max(atkAllyWithin2Spaces * 2, 6)
        atkCombatBuffs[3] += max(atkAllyWithin2Spaces * 2, 6)

    atkPhysMeleeCavWithin2Spaces = 0
    if "bibleBrosBrave" in atkSkills and atkPhysMeleeCavWithin2Spaces:
        atkr.brave = True

    if "bibleBros" in defSkills:
        defCombatBuffs[1] += max(defAllyWithin2Spaces * 2, 6)
        defCombatBuffs[3] += max(defAllyWithin2Spaces * 2, 6)

    if "BEAST MODE BABY" in atkSkills and sum(defender.debuffs) == 0:
        atkCombatBuffs[1] += 6
        atkCombatBuffs[3] += 6

    if "BEAST MODE BABY" in defSkills and sum(attacker.debuffs) == 0:
        defCombatBuffs[1] += 6
        defCombatBuffs[3] += 6

    if "mercuriusMegabuff" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "mercuriusMegabuff" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "yahoo" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[1] += 4  # plus highest atk buff among self & allies within 3 spaces
        atkCombatBuffs[2] += 4  # and so on
        atkCombatBuffs[3] += 4  # and so forth
        atkCombatBuffs[4] += 4  # for all 4 stats

    if "yahoo" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[1] += 4  # if you have panic
        defCombatBuffs[2] += 4  # and not null panic
        defCombatBuffs[3] += 4  # your buff don't count
        defCombatBuffs[4] += 4  # bottom text

    if "extraAstra" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)

    if "extraAstra" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)

    if "superExtraAstra" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkCombatBuffs[1] += min(spaces_moved_by_atkr * 2, 8)
        defCombatBuffs[3] -= min(spaces_moved_by_atkr * 2, 8)

    if "superExtraAstra" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defCombatBuffs[1] += min(spaces_moved_by_atkr * 2, 8)
        atkCombatBuffs[3] -= min(spaces_moved_by_atkr * 2, 8)

    if "shadowBlade" in atkSkills and defHPEqual100Percent:
        defCombatBuffs[1] -= 4
        defCombatBuffs[2] -= 4
        defCombatBuffs[3] -= 4
        atkPenaltiesNeutralized = [True] * 5

    if "shadowBlade" in defSkills and atkHPEqual100Percent:
        atkCombatBuffs[1] -= 4
        atkCombatBuffs[2] -= 4
        atkCombatBuffs[3] -= 4
        defPenaltiesNeutralized = [True] * 5

    if "Hello, I like money" in atkSkills:
        map(lambda x: x + 4 + (2 * attacker.flowers > 0), atkCombatBuffs)
        if attacker.flowers > 1:
            atkr.disable_foe_fastcharge = True
            atkr.disable_foe_guard = True

    if "Hello, I like money" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4 + (2 * defender.flowers > 0), defCombatBuffs)
        if defender.flowers > 1:
            defr.disable_foe_fastcharge = True
            defr.disable_foe_guard = True

    if "doubleLion" in atkSkills and atkHPEqual100Percent:  # refined eff alm
        atkr.brave = True
        atkSelfDmg += 5

    if "dracofalchion" in atkSkills and atkFoeWithin2Spaces >= atkAllyWithin2Spaces: map(lambda x: x + 5,
                                                                                         atkCombatBuffs)
    if "dracofalchion" in defSkills and defFoeWithin2Spaces >= defAllyWithin2Spaces: map(lambda x: x + 5,
                                                                                         defCombatBuffs)
    if "dracofalchionDos" in atkSkills: map(lambda x: x + 5, atkCombatBuffs)
    if "dracofalchionDos" in defSkills and defAllyWithin2Spaces: map(lambda x: x + 5, defCombatBuffs)

    if "sweeeeeeep" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        if defender.getTargetedDef() == -1 and atkPhantomStats[2] > defPhantomStats[2]:
            atkDoSkillFU = True
            cannotCounter = True

    if "sweeeeeeep" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        if attacker.getTargetedDef() == -1 and defPhantomStats[2] > atkPhantomStats[2]:
            defDoSkillFU = True

    if "grayBoost" in atkSkills and atkHPGreaterEqual50Percent: map(lambda x: x + 3, atkCombatBuffs)
    if "grayBoost" in defSkills and defHPGreaterEqual50Percent: map(lambda x: x + 3, defCombatBuffs)
    if "challenger" in atkSkills and atkAllyWithin2Spaces <= atkFoeWithin2Spaces: map(lambda x: x + 5, atkCombatBuffs)
    if "challenger" in defSkills and defAllyWithin2Spaces <= defFoeWithin2Spaces: map(lambda x: x + 5, defCombatBuffs)

    if "HPWarrior" in atkSkills and atkStats[0] >= defHPCur + 1: map(lambda x: x + 4, atkCombatBuffs)
    if "HPWarrior" in defSkills and defStats[0] >= atkHPCur + 1: map(lambda x: x + 4, defCombatBuffs)

    if ("belovedZofia" in atkSkills and atkHPEqual100Percent) or "belovedZofia2" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)
        atkRecoilDmg += 4

    if "A man has fallen into the river in LEGO City!" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkPostCombatHealing += 7

    if "ALMMM" in atkSkills and (not atkHPEqual100Percent or not defHPEqual100Percent):
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.all_hits_heal += 7

    if "SUPER MARIO!!!" in atkSkills and atkSpCountCur == 0:
        map(lambda x: x + 3, atkCombatBuffs)

    if "SUPER MARIO!!!" in defSkills and defSpCountCur == 0:
        map(lambda x: x + 3, atkCombatBuffs)
        ignoreRng = True

    if "berkutBoost" in atkSkills and defHPEqual100Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        atkCombatBuffs[2] -= 5

    # Seliph - Tyrfing - Base

    if "baseTyrfing" in atkSkills and atkHPCur / atkStats[0] <= 0.5:
        atkCombatBuffs[3] += 4

    # Seliph/Sigurd - Divine Tyrfing - Base

    if "refDivTyrfing" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[3] += 5

    if "refDivTyrfing" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5

    if ("divTyrfing" in atkSkills or "refDivTyrfing" in atkSkills) and defender.wpnType in ["RTome", "BTome", "GTome", "CTome"]:
        atkr.DR_first_hit_NSP.append(50)
    if ("divTyrfing" in defSkills or "refDivTyrfing" in defSkills) and attacker.wpnType in ["RTome", "BTome", "GTome", "CTome"]:
        defr.DR_first_hit_NSP.append(50)

    if "WE MOVE" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[3] += 5
        atkr.follow_ups_skill += 1

    if "vTyrfing" in atkSkills and not atkHPEqual100Percent:
        defCombatBuffs[1] -= 6
        defCombatBuffs[3] -= 6
        atkr.all_hits_heal += 7

    if "vTyrfing" in defSkills:
        atkCombatBuffs[1] -= 6
        atkCombatBuffs[3] -= 6
        defr.all_hits_heal += 7

    if "newVTyrfing" in atkSkills and (not atkHPEqual100Percent or defHPGreaterEqual75Percent):
        defCombatBuffs[1] -= 6
        defCombatBuffs[3] -= 6
        atkr.all_hits_heal += 8
        atkr.prevent_foe_FU = True

    if "newVTyrfing" in defSkills:
        atkCombatBuffs[1] -= 6
        atkCombatBuffs[3] -= 6
        defr.all_hits_heal += 8
        defr.prevent_foe_FU = True

    # L!Seliph - Virtuous Tyrfing - Refined Eff
    if "NO MORE LOSSES" in atkSkills:
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5
        if defender.wpnType in ["RTome", "BTome", "GTome", "CTome", "Staff"]:
            atkr.DR_all_hits_NSP.append(80)
        else:
            atkr.DR_all_hits_NSP.append(40)

    if "NO MORE LOSSES" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5
        if attacker.wpnType in ["RTome", "BTome", "GTome", "CTome", "Staff"]:
            defr.DR_all_hits_NSP.append(80)
        else:
            defr.DR_all_hits_NSP.append(40)

    if "I HATE FIRE JOKES >:(" in atkSkills and spaces_moved_by_atkr:
        map(lambda x: x + 5, atkCombatBuffs)
        if atkHPGreaterEqual25Percent:
            atkr.pseudo_miracle = True

    if "I HATE FIRE JOKES >:(" in defSkills and spaces_moved_by_atkr:
        map(lambda x: x + 5, defCombatBuffs)
        if defHPGreaterEqual25Percent:
            defr.pseudo_miracle = True

    # L!Sigurd - Hallowed Tyrfing - Base

    if "WaitIsHeAGhost" in atkSkills and defHPGreaterEqual75Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        atkr.follow_ups_skill += 1
        atkr.DR_first_hit_NSP.append(40)

    if "WaitIsHeAGhost" in defSkills and atkHPGreaterEqual75Percent:
        map(lambda x: x + 5, defCombatBuffs)
        defr.follow_ups_skill += 1
        if attacker.getRange() == 2:
            defr.DR_first_hit_NSP.append(40)

    if "I'M STRONG AND YOU'RE TOAST" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 4
        atkCombatBuffs[3] += 6
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "I'M STRONG AND YOU'RE TOAST" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[1] += 4
        defCombatBuffs[3] += 6
        atkr.spLossWhenAtkd -= 1
        atkr.spLossOnAtk -= 1

    if "Ayragate" in atkSkills and defHPGreaterEqual75Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.DR_first_hit_NSP.append(20)

    if "Ayragate" in defSkills and atkHPGreaterEqual75Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defr.DR_first_hit_NSP.append(20)

    if "balmungBoost" in atkSkills and defHPEqual100Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkPenaltiesNeutralized = [True] * 5

    if "larceiEdge" in atkSkills and (
            atkStats[SPD] + atkPhantomStats[2] > defStats[SPD] + defPhantomStats[2] or defHPEqual100Percent):
        map(lambda x: x + 4, atkCombatBuffs)
        defBonusesNeutralized = [True] * 5

    if "larceiEdge" in defSkills and (
            atkStats[2] + atkPhantomStats[2] < defStats[2] + defPhantomStats[2] or atkHPEqual100Percent):
        map(lambda x: x + 4, defCombatBuffs)
        atkBonusesNeutralized = [True] * 5

    if "larceiEdge2" in atkSkills and atkStats[2] + atkPhantomStats[2] > defStats[2] + defPhantomStats[
        2] or defHPGreaterEqual75Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        defBonusesNeutralized = [True] * 5
        atkr.disable_foe_guard = True

    if "larceiEdge2" in defSkills and defStats[2] + defPhantomStats[2] > atkStats[2] + atkPhantomStats[
        2] or atkHPGreaterEqual75Percent:
        map(lambda x: x + 4, defCombatBuffs)
        atkBonusesNeutralized = [True] * 5
        defr.disable_foe_guard = True

    if "infiniteSpecial" in atkSkills and atkHPGreaterEqual25Percent: map(lambda x: x + 4, atkCombatBuffs)
    if "infiniteSpecial" in defSkills and defHPGreaterEqual25Percent: map(lambda x: x + 4, defCombatBuffs)

    if "DRINK" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[3] += 5
        atkr.true_sp += 7

    if "AMERICA" in atkSkills:
        NEWatkOtherDmg += 10
        defPostCombatStatusesApplied[2].append(Status.Flash)

    if "AMERICA" in defSkills:
        NEWdefOtherDmg += 10
        atkPostCombatStatusesApplied[2].append(Status.Flash)

    if "FREEDOM" in atkSkills and atkHPGreaterEqual25Percent: map(lambda x: x + 4, atkCombatBuffs)
    if "FREEDOM" in defSkills and defHPGreaterEqual25Percent: map(lambda x: x + 4, defCombatBuffs)

    if "MY TRAP! 🇺🇸" in atkSkills and atkAdjacentToAlly <= 1:
        map(lambda x: x + 4, atkCombatBuffs)
        defPostCombatStatusesApplied[2].append(Status.Discord)
        atkr.DR_first_hit_NSP.append(30)

    if "MY TRAP! 🇺🇸" in defSkills and defAdjacentToAlly <= 1:
        map(lambda x: x + 4, defCombatBuffs)
        defPostCombatStatusesApplied[2].append(Status.Discord)
        defr.DR_first_hit_NSP.append(30)

    if "leafSword" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs[2] += 4
        atkCombatBuffs[3] += 4

    if "theLand" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[1] += 6
        atkCombatBuffs[2] += 6
        atkr.always_pierce_DR = True
        atkPostCombatHealing += 7
        if defender.getSpecialType() == "Defense":
            defr.special_disabled = True

    if "theLand" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[1] += 6
        defCombatBuffs[2] += 6
        defr.always_pierce_DR = True
        defPostCombatHealing += 7
        if attacker.getSpecialType() == "Defense":
            atkr.special_disabled = True

    if "bigHands" in atkSkills and defHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        defCombatBuffs[1] -= 5
        atkr.follow_up_denials -= 1

    if "swagDesp" in atkSkills and atkHPGreaterEqual50Percent:
        atkr.self_desperation = True

    if "swagDespPlus" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.self_desperation = True
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        if defStats[SPD] + defPhantomStats[SPD] > defStats[DEF] + defPhantomStats[DEF]:
            defCombatBuffs[2] -= 8
        else:
            defCombatBuffs[3] -= 8

    if "swagDespPlus" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5
        if atkStats[SPD] + defPhantomStats[SPD] > atkStats[DEF] + defPhantomStats[DEF]:
            atkCombatBuffs[2] -= 8
        else:
            atkCombatBuffs[3] -= 8

    if "swagDespPlusPlus" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        atkr.disable_foe_guard = True

    if "swagDespPlusPlus" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5
        defr.disable_foe_guard = True

    if "spectrumSolo" in atkSkills and not atkAdjacentToAlly:
        map(lambda x: x + 4, atkCombatBuffs)

    if "spectrumSolo" in defSkills and not defAdjacentToAlly:
        map(lambda x: x + 4, defCombatBuffs)

    if "NFUSolo" in atkSkills and not atkAdjacentToAlly:
        atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True

    if "NFUSolo" in defSkills and not defAdjacentToAlly:
        defr.prevent_foe_FU, defr.prevent_self_FU_denial = True

    if "mareeeeta" in atkSkills and atkAdjacentToAlly <= 1:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True
        defBonusesNeutralized[SPD], defBonusesNeutralized[DEF] = True

    if "mareeeeta" in defSkills and defAdjacentToAlly <= 1:
        map(lambda x: x + 4, defCombatBuffs)
        defr.prevent_foe_FU, defr.prevent_self_FU_denial = True
        atkBonusesNeutralized[SPD], atkBonusesNeutralized[DEF] = True

    if "moreeeeta" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.sp_pierce_DR = True
        atkr.disable_foe_guard = True

    if "moreeeeta" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defr.sp_pierce_DR = True
        defr.disable_foe_guard = True

    if "ascendingBlade" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True
        atkPostCombatSpCharge += 1

    if "ascendingBlade" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        defr.prevent_foe_FU, defr.prevent_self_FU_denial = True
        defPostCombatSpCharge += 1

    if "ROY'S OUR BOY" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1
        atkr.disable_foe_guard = True

    if "ROY'S OUR BOY" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1
        defr.disable_foe_guard = True

    if "wanderer" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "like the university" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "wanderer" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "like the university" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    if "elistats" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "elistats" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "hamburger" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)
        defBonusesNeutralized = [True] * 5

    if "hamburger" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)
        atkBonusesNeutralized = [True] * 5

    if ("curiosBoost" in atkSkills or "reduFU" in atkSkills) and turn % 2 == 1 or not defHPEqual100Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if ("curiosBoost" in defSkills or "reduFU" in defSkills) and turn % 2 == 1 or not atkHPEqual100Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "oho dad" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

        defCombatBuffs[1] -= math.trunc(atkStats[ATK] * 0.1)
        defCombatBuffs[3] -= math.trunc(atkStats[ATK] * 0.1)

        atkPostCombatHealing += 7

    if "oho dad" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

        atkCombatBuffs[1] -= math.trunc(defStats[ATK] * 0.1)
        atkCombatBuffs[3] -= math.trunc(defStats[ATK] * 0.1)

        atkPostCombatHealing += 7

    if "garbageSword" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs[1] += atkSkills["garbageSword"]
        atkCombatBuffs[2] += atkSkills["garbageSword"]

    if "Hi Nino" in atkSkills:
        allyMagic2Spaces = 0
        if allyMagic2Spaces: map(lambda x: x + 3, atkCombatBuffs)

    if "vassalBlade" in atkSkills:
        atkCombatBuffs[SPD] += 5

    if "Barry B. Benson" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True

    if "bonusInheritor" in atkSkills:  # eirika, should be highest bonus for each given stat on allies within 2 spaces
        atkCombatBuffs[1] += 0
        atkCombatBuffs[2] += 0
        atkCombatBuffs[3] += 0
        atkCombatBuffs[4] += 0

    if "stormSieglinde" in atkSkills and atkFoeWithin2Spaces >= atkAllyWithin2Spaces:
        atkCombatBuffs[3] += 3
        atkCombatBuffs[4] += 3
        atkr.spGainOnAtk += 1

    if "stormSieglinde2" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

    if "stormSieglinde2" in defSkills and not defAdjacentToAlly:
        map(lambda x: x + 4, defCombatBuffs)
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

    if "Just Lean" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "Just Lean" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "renaisTwins" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)

    if "renaisTwins" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)

    if "audBoost" in atkSkills and defHPEqual100Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    if "hey all scott here" in atkSkills:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5

    if "hey all scott here" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5

    if ("I fight for my friends" in atkSkills or "WILLYOUSURVIVE?" in atkSkills) and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)

    # CH!Ike - Sturdy War Sword - Base

    if "sturdyWarrr" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        if attacker.getSpecialType() == "Offense":
            if atkAllyWithin4Spaces >= 1:
                atkr.sp_charge_first += math.trunc(attacker.getMaxSpecialCooldown() / 2)
            if atkAllyWithin4Spaces >= 2:
                atkr.DR_first_hit_NSP.append(10 * defender.getMaxSpecialCooldown())
            if atkAllyWithin4Spaces >= 3:
                atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True

    if "sturdyWarrr" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        if defender.getSpecialType() == "Offense":
            if defAllyWithin4Spaces >= 1:
                defr.sp_charge_first += math.trunc(defender.getMaxSpecialCooldown() / 2)
            if defAllyWithin4Spaces >= 2:
                defr.DR_first_hit_NSP.append(10 * defender.getMaxSpecialCooldown())
            if defAllyWithin4Spaces >= 3:
                defr.prevent_foe_FU, defr.prevent_self_FU_denial = True

    if "BIGIKEFAN" in atkSkills and atkHPGreaterEqual25Percent:
        X = min(max(trunc(defStats[ATK] * 0.2) - 2, 6), 16)
        atkCombatBuffs[ATK] += X
        defCombatBuffs[ATK] -= X
        atkPenaltiesNeutralized = [True] * 5
        disableCannotCounter = True
        atkr.disable_foe_guard = True

    if "AETHER_GREAT" in atkSkills:
        atkr.vantage = True
        atkr.other_desperation = True
        atkr.DR_great_aether_SP = True

    if "pointySword" in atkSkills: map(lambda x: x + 5, atkCombatBuffs)
    if "pointySword" in defSkills and defAllyWithin2Spaces: map(lambda x: x + 5, atkCombatBuffs)

    if "TWO?" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[4] += 5
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

        defBonusesNeutralized[ATK] = True
        defBonusesNeutralized[DEF] = True

    if "TWO?" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[4] += 5
        defr.spGainWhenAtkd += 1
        defr.spGainOnAtk += 1
        atkBonusesNeutralized[ATK] = True
        atkBonusesNeutralized[DEF] = True

    # yeah we'll be here for a while
    if "You get NOTHING" in atkSkills:
        atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True
        defr.prevent_foe_FU, defr.prevent_self_FU_denial = True
        atkr.special_disabled = True
        defr.special_disabled = True
        atkDefensiveTerrain = False
        defDefensiveTerrain = False
        atkr.hardy_bearing = True
        defr.hardy_bearing = True
        if atkHPGreaterEqual25Percent: map(lambda x: x + 5, atkCombatBuffs)

    if "You get NOTHING" in defSkills:
        atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True
        defr.prevent_foe_FU, defr.prevent_self_FU_denial = True
        atkr.special_disabled = True
        defr.special_disabled = True
        atkDefensiveTerrain = False
        defDefensiveTerrain = False
        atkr.hardy_bearing = True
        defr.hardy_bearing = True
        if defHPGreaterEqual25Percent: map(lambda x: x + 5, defCombatBuffs)

    if "spectrumBond" in atkSkills and atkAdjacentToAlly:  # awakening falchion
        map(lambda x: x + atkSkills["spectrumBond"], atkCombatBuffs)

    if "sealedFalchion" in atkSkills and not atkHPEqual100Percent:
        map(lambda x: x + 5, atkCombatBuffs)

    if "newSealedFalchion" in atkSkills and (not atkHPEqual100Percent or atkHasBonus):
        map(lambda x: x + 5, atkCombatBuffs)

    if "I CANT STOP THIS THING" in atkSkills and defHPGreaterEqual75Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        defr.follow_up_denials -= 1

    if "refineExtra" in atkSkills and defHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5

    if "Sacred Stones Strike!" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5

    if "ancientRagnell" in atkSkills and (atkHPGreaterEqual50Percent or atkHasBonus):
        defCombatBuffs[1] -= 6
        defCombatBuffs[3] -= 6

    if "ancientRagnell" in defSkills and (defHPGreaterEqual50Percent or defHasBonus):
        atkCombatBuffs[1] -= 6
        atkCombatBuffs[3] -= 6

    if "lioness" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[1] += 6
        atkCombatBuffs[2] += 6
        atkr.sp_pierce_DR = True
        if defHPGreaterEqual75Percent:
            atkr.spGainWhenAtkd += 1
            atkr.spGainOnAtk += 1

    if "lioness" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[1] += 6
        defCombatBuffs[2] += 6
        defr.sp_pierce_DR = True
        if atkHPGreaterEqual75Percent:
            defr.spGainWhenAtkd += 1
            defr.spGainOnAtk += 1

    if "waitTurns" in atkSkills:  # ryoma
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True

    if "waitTurns" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)
        defr.prevent_foe_FU, defr.prevent_self_FU_denial = True

    if "xanderific" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5
        defr.follow_up_denials -= 1

    if "Toaster" in atkSkills and not atkAdjacentToAlly:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        atkPenaltiesNeutralized = [True] * 5

    if "lowAtkBoost" in atkSkills and defStats[ATK] + defPhantomStats[ATK] >= atkStats[ATK] + atkPhantomStats[ATK] + 3:
        map(lambda x: x + 3, atkCombatBuffs)

    if "lowAtkBoost" in defSkills and atkStats[ATK] + atkPhantomStats[ATK] >= defStats[ATK] + defPhantomStats[ATK] + 3:
        map(lambda x: x + 3, defCombatBuffs)

    # If Laslow is within 3 spaces of at least 2 allies who each have total stat buffs >= 10
    if "laslowBrave" in atkSkills:
        theLaslowCondition = False
        if theLaslowCondition:
            atkCombatBuffs[1] += 3
            atkCombatBuffs[3] += 3
            atkr.brave = True

    if "laslowBrave" in defSkills:
        theLaslowCondition = False
        if theLaslowCondition:
            defCombatBuffs[1] += 3
            defCombatBuffs[3] += 3
            defr.brave = True

    if "ladies, whats good" in atkSkills:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        atkr.spGainOnAtk += 1

    if "up b bair" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)
    if "up b bair" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)

    if "up b side b" in atkSkills or "up b bair" in defSkills:
        atkr.disable_foe_fastcharge = True
        atkr.disable_foe_guard = True

        atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True

    if "up b side b" in defSkills or "up b bair" in defSkills:
        defr.disable_foe_fastcharge = True
        defr.disable_foe_guard = True

        defr.prevent_foe_FU, defr.prevent_self_FU_denial = True

    # Byleth - Creator Sword - Refined Eff

    if "HERE'S SOMETHING TO BELIEVE IN" in atkSkills:
        atkr.sp_pierce_DR = True
        if atkHPGreaterEqual25Percent:
            map(lambda x: x + 4, atkCombatBuffs)
            atkr.DR_first_hit_NSP.append(30)

    if "HERE'S SOMETHING TO BELIEVE IN" in defSkills:
        defr.sp_pierce_DR = True
        if defHPGreaterEqual25Percent:
            map(lambda x: x + 4, defCombatBuffs)
            defr.DR_first_hit_NSP.append(30)

    # SU!Edelgard - Regal Sunshade - Base

    if "regalSunshade" in atkSkills and atkHPGreaterEqual25Percent:
        numFoesLeft = 0
        numFoesWithin3Columns3Rows = 0

        atkCombatBuffs[1] += 6
        atkCombatBuffs[3] += 6
        atkr.DR_first_hit_NSP.append(40)

        X = 1 if numFoesLeft <= 2 else (2 if 3 <= numFoesLeft <= 5 else 3)
        if X <= numFoesWithin3Columns3Rows:
            atkr.brave = True

    if "regalSunshade" in defSkills and defHPGreaterEqual25Percent:
        numFoesLeft = 0
        numFoesWithin3Columns3Rows = 0

        defCombatBuffs[1] += 6
        defCombatBuffs[3] += 6
        defr.DR_first_hit_NSP.append(40)

        X = 1 if numFoesLeft <= 2 else (2 if 3 <= numFoesLeft <= 5 else 3)
        if X <= numFoesWithin3Columns3Rows:
            defr.brave = True

    if "sling a thing" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkr.prevent_self_FU_denial = True
        atkr.DR_first_strikes_NSP.append(40)
        if Status.SpecialCharge in attacker.statusPos:
            atkr.disable_foe_guard = True

    # Reginn - Lyngheiðr - Base
    if "reginn :)" in atkSkills:
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[SPD] += 6
        atkr.DR_first_hit_NSP.append(30)

    # Catherine: Thunderbrand

    if "thundabrand" in atkSkills and defHPGreaterEqual50Percent:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        atkr.self_desperation = True
        atkDoSkillFU = True

    if "thundabrand" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[1] += 5
        defDoSkillFU = True

    # Nemesis: Dark Creator S
    if "DCSIYKYK" in atkSkills:
        atkCombatBuffs[1] += 2 * atkNumAlliesHPGE90Percent
        atkCombatBuffs[3] += 2 * defNumAlliesHPGE90Percent

    if "TMSFalchion" in atkSkills:
        atkCombatBuffs[1] += min(3 + 2 * 00000, 7)  # 00000 - number of allies who have acted
        atkCombatBuffs[3] += min(3 + 2 * 00000, 7)

    if "TMSFalchion" in defSkills:
        atkCombatBuffs[1] += max(3, 7 - 000000 * 2)  # 000000 - number of foes who have acted
        atkCombatBuffs[3] += max(3, 7 - 000000 * 2)

    # 00000 and 000000 should be equal

    if "Garfield You Fat Cat" in atkSkills:
        atkCombatBuffs[1] += min(4 + 3 * 00000, 10)  # 00000 - number of allies who have acted
        atkCombatBuffs[2] += min(4 + 3 * 00000, 10)
        atkCombatBuffs[3] += min(4 + 3 * 00000, 10)
        atkCombatBuffs[4] += min(4 + 3 * 00000, 10)
        atkPostCombatHealing += 7

    if "Garfield You Fat Cat" in defSkills:
        defCombatBuffs[1] += max(4, 10 - 000000 * 3)  # 000000 - number of foes who have acted
        defCombatBuffs[2] += max(4, 10 - 000000 * 3)
        defCombatBuffs[3] += max(4, 10 - 000000 * 3)
        defCombatBuffs[4] += max(4, 10 - 000000 * 3)
        defPostCombatHealing += 7

    # Ituski - Mirage Falchion - Refined Eff
    # If unit initiates combat or is within 2 spaces of an ally:
    #  - grants Atk/Spd/Def/Res+4 to unit
    #  - unit makes a guaranteed follow-up attack
    #  - reduces damage from first attack during combat by 30%

    if "Nintendo has forgotten about Mario…" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.follow_ups_skill += 1
        atkr.DR_first_hit_NSP.append(30)

    if "Nintendo has forgotten about Mario…" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)
        defr.follow_ups_skill += 1
        defr.DR_first_hit_NSP.append(30)

    if "BONDS OF FIIIIRE, CONNECT US" in atkSkills and atkHPGreaterEqual25Percent:
        titlesAmongAllies = 0
        atkCombatBuffs = list(map(lambda x: x + 5, atkCombatBuffs))
        defCombatBuffs[SPD] -= min(4 + titlesAmongAllies * 2, 12)
        defCombatBuffs[DEF] -= min(4 + titlesAmongAllies * 2, 12)

    if "BONDS OF FIIIIRE, CONNECT US" in defSkills and defHPGreaterEqual25Percent:
        titlesAmongAllies = 0
        map(lambda x: x + 5, defCombatBuffs)
        atkCombatBuffs[SPD] -= min(4 + titlesAmongAllies * 2, 12)
        atkCombatBuffs[DEF] -= min(4 + titlesAmongAllies * 2, 12)

    if "Mr. Fire Emblem" in atkSkills and atkHPGreaterEqual25Percent:
        titlesAmongAllies = 0
        atkr.brave = True
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        defCombatBuffs = [x - min(titlesAmongAllies * 3 + 4, 10) for x in defCombatBuffs]
        atkr.DR_first_strikes_NSP.append(50)

    if "Mr. Fire Emblem" in defSkills and defHPGreaterEqual25Percent:
        titlesAmongAllies = 0
        defr.brave = True
        defCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkCombatBuffs = [x - min(titlesAmongAllies * 3 + 4, 10) for x in defCombatBuffs]
        defr.DR_first_strikes_NSP.append(50)

    if "Miracle O' Emblems" in atkSkills:
        if atkAllyWithin3Spaces:
            atkCombatBuffs = [x + 9 for x in atkCombatBuffs]
            atkr.DR_first_strikes_NSP.append(40)

    if "Miracle O' Emblems" in defSkills:
        ignoreRng = True
        if defAllyWithin3Spaces:
            defCombatBuffs = [x + 9 for x in defCombatBuffs]
            defr.DR_first_strikes_NSP.append(40)
        if defAllyWithin3Spaces >= 3:
            defr.pseudo_miracle = True

    if "hippity-hop" in atkSkills and atkAllyWithin3Spaces:
        Y = min(atkAllyWithin3Spaces * 3 + 5, 14)
        allies = attacker.tile.unitsWithinNSpaces(3, True)
        for x in allies:
            if x.getWeaponType() in ["RDragon", "BDragon", "GDragon", "CDragon"]:
                Y = 14
        atkCombatBuffs = [x + Y for x in atkCombatBuffs]
        atkr.disable_foe_fastcharge = True
        atkr.disable_foe_guard = True
        atkr.DR_first_strikes_NSP.append(min(atkHPCur, 60))

    if "hippity-hop" in defSkills and defAllyWithin3Spaces:
        Y = min(defAllyWithin3Spaces * 3 + 5, 14)
        allies = defender.tile.unitsWithinNSpaces(3, True)
        for x in allies:
            if x.getWeaponType() in ["RDragon", "BDragon", "GDragon", "CDragon"]:
                Y = 14
        defCombatBuffs = [x + Y for x in atkCombatBuffs]
        defr.disable_foe_fastcharge = True
        defr.disable_foe_guard = True
        defr.DR_first_strikes_NSP.append(min(defHPCur, 60))

    if "LOVE PROVIIIIDES, PROTECTS US" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "LOVE PROVIIIIDES, PROTECTS US" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    if "sky-hopper" in atkSkills and atkHPGreaterEqual25Percent:
        charge_count = 0
        if is_in_sim:
            team = attacker.tile.unitsWithinNSpaces(n=20, lookForSameSide=True)
            for x in team:
                if Status.Charge in x.statusPos:
                    charge_count += 1

        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkCombatBuffs[ATK] += min(charge_count * 4, 8)
        atkCombatBuffs[SPD] += min(charge_count * 4, 8)
        atkr.damage_reduction_reduction *= 0.5

    if "sky-hopper" in defSkills and defHPGreaterEqual25Percent:
        charge_count = 0
        if is_in_sim:
            team = defender.tile.unitsWithinNSpaces(n=20, lookForSameSide=True)
            for x in team:
                if Status.Charge in x.statusPos:
                    charge_count += 1

        defCombatBuffs = [x + 5 for x in defCombatBuffs]
        defCombatBuffs[ATK] += min(charge_count * 4, 8)
        defCombatBuffs[SPD] += min(charge_count * 4, 8)
        defr.damage_reduction_reduction *= 0.5

    if "laevBoost" in atkSkills and (atkHasBonus or atkHPGreaterEqual50Percent):
        atkCombatBuffs[1] += 5
        atkCombatBuffs[3] += 5

    if "laevPartner" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5

    if "niuBoost" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True

    if "niuBoost" in defSkills and defHPGreaterEqual25Percent:
        defr.prevent_foe_FU, defr.prevent_self_FU_denial = True
        map(lambda x: x + 4, defCombatBuffs)

    if "ICE UPON YOU" in atkSkills and defHasPenalty:
        atkr.follow_ups_skill += 1
        defr.follow_up_denials -= 1

    if "ICE UPON YOU" in defSkills and atkHasPenalty:
        defr.follow_ups_skill += 1
        atkr.follow_up_denials -= 1

    if "FREEZE NOW" in atkSkills and (atkHPGreaterEqual25Percent or defHasPenalty):
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5

    if "FREEZE NOW" in defSkills and (defHPGreaterEqual25Percent or atkHasPenalty):
        atkCombatBuffs[1] -= 5
        atkCombatBuffs[3] -= 5

    if "hikamiThreaten2" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[1] -= 4
        defCombatBuffs[2] -= 4
        defCombatBuffs[3] -= 4

    if "hikamiThreaten2" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[1] -= 4
        atkCombatBuffs[2] -= 4
        atkCombatBuffs[3] -= 4

    if "https://youtu.be/eVTXPUF4Oz4?si=RkBGT1Gf1bGBxOPK" in atkSkills and atkAllyWithin3Spaces:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.follow_ups_skill += 1

    if "https://youtu.be/eVTXPUF4Oz4?si=RkBGT1Gf1bGBxOPK" in defSkills and defAllyWithin3Spaces:
        map(lambda x: x + 4, defCombatBuffs)
        defr.follow_ups_skill += 1

    if "https://www.youtube.com/watch?v=Gd9OhYroLN0&pp=ygUUY3Jhd2xpbmcgbGlua2luIHBhcms%3D" in atkSkills and atkAllyWithin4Spaces:
        map(lambda x: x + 6, atkCombatBuffs)
        atkr.follow_ups_skill += 1
        atkr.true_finish += 5
        atkr.finish_mid_combat_heal += 7

    if "https://www.youtube.com/watch?v=Gd9OhYroLN0&pp=ygUUY3Jhd2xpbmcgbGlua2luIHBhcms%3D" in defSkills and defAllyWithin4Spaces:
        map(lambda x: x + 6, defCombatBuffs)
        defr.follow_ups_skill += 1
        defr.true_finish += 5
        defr.finish_mid_combat_heal += 7

    if "ow" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.DR_first_hit_NSP.append(30)

    if "ow" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defr.DR_first_hit_NSP.append(30)

    if "zzzzzzzzzzzzzzzz" in atkSkills and (defender.hasPenalty() or defHPGreaterEqual75Percent):
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5

    if "zzzzzzzzzzzzzzzz" in defSkills and (attacker.hasPenalty() or atkHPGreaterEqual75Percent):
        atkCombatBuffs[1] -= 5
        atkCombatBuffs[3] -= 5

    if "sleepy head" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5
        atkr.follow_ups_skill += 1
        defPostCombatStatusesApplied[2].append(Status.Flash)

    if "sleepy head" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[1] -= 5
        atkCombatBuffs[3] -= 5
        defr.follow_ups_skill += 1
        atkPostCombatStatusesApplied[2].append(Status.Flash)

    if "daydream_egg" in atkSkills and defHPGreaterEqual75Percent or defHasPenalty:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkCombatBuffs[RES] += 5

    if "the_dose" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.capped_burn_damage = max(atkr.capped_burn_damage, 8)
        X = trunc(atkStats[DEF] * 0.2) + 6
        defCombatBuffs[ATK] -= X
        defCombatBuffs[DEF] -= X
        atkr.damage_reduction_reduction *= (1 - 0.5)
        atkr.true_all_hits += trunc(defStats[HP] * 0.3)
        atkr.TDR_dmg_taken_cap = 20
        if defender.getSpecialType() == "Offense":
            atkr.TDR_dmg_taken_extra_stacks += 1

        # reduce damage by Y
        # Y = damage dealt to foe, max 20
        # if hit by offensive special, reduce damage by 2Y

    if "Mario":
        "only Bros!"

    if "selfDmg" in atkSkills:  # damage to self after combat always
        atkSelfDmg += atkSkills["selfDmg"]

    if "atkOnlySelfDmg" in atkSkills:  # damage to attacker after combat iff attacker had attacked
        atkRecoilDmg += atkSkills["atkOnlySelfDmg"]

    if "atkOnlyOtherDmg" in atkSkills:  # damage to other unit after combat iff attacker had attacked
        NEWatkOtherDmg += atkSkills["atkOnlyOtherDmg"]

    if "triAdeptS" in atkSkills and atkSkills["triAdeptS"] > triAdept: triAdept = atkSkills["triAdeptS"]
    if "triAdeptW" in atkSkills and atkSkills["triAdeptW"] > triAdept: triAdept = atkSkills["triAdeptW"]

    if "owlBoost" in atkSkills:
        map(lambda x: x + 2 * atkAdjacentToAlly, atkCombatBuffs)

    if "FollowUpEph" in atkSkills and atkHPCur / atkStats[0] > 0.90:
        atkr.follow_ups_skill += 1

    if "BraveAW" in atkSkills or "BraveAS" in atkSkills or "BraveBW" in atkSkills:
        atkr.brave = True

    if "swordBreak" in atkSkills and defender.wpnType == "Sword" and atkHPCur / atkStats[0] > 1.1 - (
            atkSkills["swordBreak"] * 0.2): atkr.follow_ups_skill += 1; defr.follow_up_denials -= 1
    if "lanceBreak" in atkSkills and defender.wpnType == "Lance" and atkHPCur / atkStats[0] > 1.1 - (
            atkSkills["lanceBreak"] * 0.2): atkr.follow_ups_skill += 1; defr.follow_up_denials -= 1
    if "axeBreak" in atkSkills and defender.wpnType == "Axe" and atkHPCur / atkStats[0] > 1.1 - (
            atkSkills["axeBreak"] * 0.2): atkr.follow_ups_skill += 1; defr.follow_up_denials -= 1
    if "rtomeBreak" in atkSkills and defender.wpnType == "RTome" and atkHPCur / atkStats[0] > 1.1 - (
            atkSkills["rtomeBreak"] * 0.2): atkr.follow_ups_skill += 1; defr.follow_up_denials -= 1
    if "btomeBreak" in atkSkills and defender.wpnType == "BTome" and atkHPCur / atkStats[0] > 1.1 - (
            atkSkills["btomeBreak"] * 0.2): atkr.follow_ups_skill += 1; defr.follow_up_denials -= 1
    if "gtomeBreak" in atkSkills and defender.wpnType == "GTome" and atkHPCur / atkStats[0] > 1.1 - (
            atkSkills["gtomeBreak"] * 0.2): atkr.follow_ups_skill += 1; defr.follow_up_denials -= 1
    if "cBowBreak" in atkSkills and defender.wpnType == "CBow" and atkHPCur / atkStats[0] > 1.1 - (
            atkSkills["cBowBreak"] * 0.2): atkr.follow_ups_skill += 1; defr.follow_up_denials -= 1
    if "cDaggerBreak" in atkSkills and defender.wpnType == "CDagger" and atkHPCur / atkStats[0] > 1.1 - (
            atkSkills["cDaggerBreak"] * 0.2): atkr.follow_ups_skill += 1; defr.follow_up_denials -= 1

    if "spDamageAdd" in atkSkills:
        atkr.true_sp += atkSkills["spDamageAdd"]

    if "firesweep" in atkSkills or "firesweep" in defSkills:
        cannotCounter = True

    if "hardyBearing" in atkSkills:
        atkr.hardy_bearing = True
        defr.hardy_bearing = atkHPCur / atkStats[0] >= 1.5 - (atkSkills["hardyBearing"] * .5)

    if "hardyBearing" in defSkills:
        defr.hardy_bearing = True
        atkr.hardy_bearing = defHPCur / defStats[0] >= 1.5 - (defSkills["hardyBearing"] * .5)

    if "cancelTA" in atkSkills:
        atkCA = atkSkills["cancelTA"]

    # pseudo-miracle (the seliph zone)

    if "pseudoMiracle" in atkSkills and atkHPGreaterEqual50Percent:
        atkr.pseudo_miracle = True

    if "NO MORE LOSSES" in defSkills and defAllyWithin3Spaces and defHPGreaterEqual50Percent:
        defr.pseudo_miracle = True

    atkSpEffects = {}

    for key in atkSkills:
        # special tags
        if key == "healSelf": atkSpEffects.update({"healSelf": atkSkills[key]})
        if key == "defReduce": atkSpEffects.update({"defReduce": atkSkills[key]})
        if key == "dmgBoost": atkSpEffects.update({"dmgBoost": atkSkills[key]})
        if key == "atkBoostSp": atkSpEffects.update({"atkBoost": atkSkills[key]})
        if key == "spdBoostSp": atkSpEffects.update({"spdBoost": atkSkills[key]})
        if key == "defBoostSp": atkSpEffects.update({"defBoost": atkSkills[key]})
        if key == "resBoostSp": atkSpEffects.update({"resBoost": atkSkills[key]})
        if key == "closeShield": atkSpEffects.update({"closeShield": atkSkills[key]})
        if key == "distantShield": atkSpEffects.update({"distantShield": atkSkills[key]})
        if key == "miracleSP": atkSpEffects.update({"distantShield": atkSkills[key]})
        if key == "numFoeAtkBoostSp": atkSpEffects.update({"NumAtkBoost": atkSkills[key]})

    if "atkStance" in defSkills: defCombatBuffs[1] += defSkills["atkStance"] * 2
    if "spdStance" in defSkills: defCombatBuffs[2] += defSkills["spdStance"] * 2
    if "defStance" in defSkills: defCombatBuffs[3] += defSkills["defStance"] * 2
    if "resStance" in defSkills: defCombatBuffs[4] += defSkills["resStance"] * 2
    if "draugBlade" in defSkills: atkCombatBuffs[ATK] -= 6

    if "fireBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[1] += defSkills["fireBoost"] * 2
    if "windBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[2] += defSkills["windBoost"] * 2
    if "earthBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[3] += defSkills["earthBoost"] * 2
    if "waterBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[4] += defSkills["waterBoost"] * 2

    if "closeDef" in defSkills and attacker.weapon.range == 1:
        defCombatBuffs[3] += defSkills["distDef"] * 2
        defCombatBuffs[4] += defSkills["distDef"] * 2

    if "distDef" in defSkills and attacker.weapon.range == 2:
        defCombatBuffs[3] += defSkills["distDef"] * 2
        defCombatBuffs[4] += defSkills["distDef"] * 2

    if "brazenAtk" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[1] += defSkills["brazenAtk"]
    if "brazenSpd" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[2] += defSkills["brazenSpd"]
    if "brazenDef" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[3] += defSkills["brazenDef"]
    if "brazenRes" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[4] += defSkills["brazenRes"]

    if "ILOVEBONUSES" in defSkills and defHPGreaterEqual50Percent or atkHasBonus:  # UPDATE WITH DEF SKILLS
        map(lambda x: x + 4, defCombatBuffs)

    if "spectrumBond" in defSkills and defAdjacentToAlly:
        map(lambda x: x + defSkills["spectrumBond"], defCombatBuffs)

    if ("belovedZofia" in defSkills and defHPEqual100Percent) or "belovedZofia2" in defSkills:
        map(lambda x: x + 4, defCombatBuffs)
        defRecoilDmg += 4

    if "ALMMM" in defSkills and (not atkHPEqual100Percent or not defHPEqual100Percent):
        map(lambda x: x + 4, defCombatBuffs)
        defr.all_hits_heal += 7

    if "A man has fallen into the river in LEGO City!" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defPostCombatHealing += 7

    if "berkutBoost" in defSkills:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5
        defCombatBuffs[4] += 5

    if "baseTyrfing" in defSkills and defHPCur / defStats[0] <= 0.5:
        defCombatBuffs[3] += 4

    if "WE MOVE" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5
        defr.follow_ups_skill += 1

    if "DRINK" in defSkills:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5
        defr.true_sp += 7

    if "leafSword" in defSkills and atkHPEqual100Percent:
        defCombatBuffs[2] += 4
        defCombatBuffs[3] += 4

    if "bigHands" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        atkCombatBuffs[1] -= 5

    if "garbageSword" in defSkills and atkHPEqual100Percent:
        defCombatBuffs[1] += defSkills["garbageSword"]
        defCombatBuffs[2] += defSkills["garbageSword"]

    if "Hi Nino" in defSkills:
        allyMagic2Spaces = 0
        if allyMagic2Spaces: map(lambda x: x + 3, defCombatBuffs)

    if "vassalBlade" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[2] += 5

    if "Barry B. Benson" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5
        defr.prevent_foe_FU, defr.prevent_self_FU_denial = True

    if "bonusInheritor" in defSkills:  # eirika, should be highest bonus for each given stat on allies within 2 spaces
        defCombatBuffs[1] += 0
        defCombatBuffs[2] += 0
        defCombatBuffs[3] += 0
        defCombatBuffs[4] += 0

    if "stormSieglinde" in defSkills and defFoeWithin2Spaces >= defAllyWithin2Spaces:
        defCombatBuffs[3] += 3
        defCombatBuffs[4] += 3
        defr.spGainOnAtk += 1

    if "audBoost" in defSkills:
        map(lambda x: x + 4, defCombatBuffs)

    if ("I fight for my friends" in defSkills or "WILLYOUSURVIVE?" in defSkills) and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)

    if "sealedFalchion" in defSkills and not atkHPEqual100Percent:
        map(lambda x: x + 5, defCombatBuffs)

    if "newSealedFalchion" in defSkills and (not defHPEqual100Percent or defHasBonus):
        map(lambda x: x + 5, defCombatBuffs)

    if "I CANT STOP THIS THING" in defSkills and atkHPGreaterEqual75Percent:
        map(lambda x: x + 5, defCombatBuffs)
        atkr.follow_up_denials -= 1

    if "refineExtra" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5

    if "Sacred Stones Strike!" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5

    if "amatsuDC" in defSkills and defHPGreaterEqual50Percent:
        ignoreRng = True

    if "xanderific" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[1] -= 5
        atkCombatBuffs[3] -= 5
        atkr.follow_up_denials -= 1

    if "Toaster" in defSkills and not defAdjacentToAlly:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5
        defPenaltiesNeutralized = [True] * 5

    if "laevBoost" in defSkills and (defHasBonus or atkHPGreaterEqual50Percent):
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5

    if "laevPartner" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[1] += 5
        defCombatBuffs[3] += 5

    if "triAdeptS" in defSkills and defSkills["triAdeptS"] > triAdept: triAdept = defSkills["triAdeptS"]
    if "triAdeptW" in defSkills and defSkills["triAdeptW"] > triAdept: triAdept = defSkills["triAdeptW"]

    if "cCounter" in defSkills or "dCounter" in defSkills: ignoreRng = True
    if "BraveDW" in defSkills or "BraveBW" in defSkills:
        defr.brave = True

    if "selfDmg" in defSkills: defSelfDmg += defSkills["selfDmg"]

    if "atkOnlySelfDmg" in defSkills: defRecoilDmg += defSkills["atkOnlySelfDmg"]
    if "atkOnlyOtherDmg" in defSkills: NEWdefOtherDmg += defSkills["atkOnlyOtherDmg"]

    if "QRW" in defSkills and defHPCur / defStats[0] >= 1.0 - (defSkills["QRW"] * 0.1): defr.follow_ups_skill += 1
    if "QRS" in defSkills and defHPCur / defStats[0] >= 1.0 - (defSkills["QRS"] * 0.1): defr.follow_ups_skill += 1

    if "desperation" in defSkills and defHPCur / defStats[0] <= 0.25 * defSkills["desperation"]:
        atkr.self_desperation = True

    if "swordBreak" in defSkills and attacker.wpnType == "Sword": defr.follow_ups_skill += 1; atkr.follow_up_denials -= 1
    if "lanceBreak" in defSkills and attacker.wpnType == "Lance": defr.follow_ups_skill += 1; atkr.follow_up_denials -= 1
    if "axeBreak" in defSkills and attacker.wpnType == "Axe": defr.follow_ups_skill += 1; atkr.follow_up_denials -= 1
    if "rtomeBreak" in defSkills and attacker.wpnType == "RTome": defr.follow_ups_skill += 1; atkr.follow_up_denials -= 1
    if "btomeBreak" in defSkills and attacker.wpnType == "BTome": defr.follow_ups_skill += 1; atkr.follow_up_denials -= 1
    if "gtomeBreak" in defSkills and attacker.wpnType == "GTome": defr.follow_ups_skill += 1; atkr.follow_up_denials -= 1
    if "cBowBreak" in defSkills and attacker.wpnType == "CBow": defr.follow_ups_skill += 1; atkr.follow_up_denials -= 1
    if "cDaggerBreak" in defSkills and attacker.wpnType == "CDagger": defr.follow_ups_skill += 1; atkr.follow_up_denials -= 1

    if "spDamageAdd" in defSkills:
        defr.true_sp += defSkills["spDamageAdd"]

    if "vantage" in defSkills and defHPCur / defStats[0] <= 0.75 - (0.25 * (3 - defSkills["vantage"])):
        defr.vantage = True

    if Status.Vantage in defender.statusNeg:
        defr.vantage = True

    if "cancelTA" in defSkills:
        defCA = defSkills["cancelTA"]

    if "pseudoMiracle" in defSkills and defHPGreaterEqual50Percent:
        defr.pseudo_miracle = True

    # PART 1
    if "laguz_friend" in atkSkills:
        skill_lvl = atkSkills["laguz_friend"]
        if skill_lvl == 4: defStats[ATK] -= 5

        if attacker.getMaxSpecialCooldown() >= 3 and attacker.getSpecialType() == "Offense" or attacker.getSpecialType() == "Defense":
            atkr.damage_reduction_reduction *= 0.5
            atkr.sp_charge_foe_first += 2


    defSpEffects = {}
    for key in defSkills:
        if key == "healSelf": defSpEffects.update({"healSelf": defSkills[key]})
        if key == "defReduce": defSpEffects.update({"defReduce": defSkills[key]})
        if key == "dmgBoost": defSpEffects.update({"dmgBoost": defSkills[key]})
        if key == "resBoostSp": defSpEffects.update({"resBoost": defSkills[key]})
        if key == "closeShield": defSpEffects.update({"closeShield": defSkills[key]})
        if key == "distantShield": defSpEffects.update({"distantShield": defSkills[key]})
        if key == "miracleSP": defSpEffects.update({"miracleSP": defSkills[key]})

    # LITERALLY EVERYTHING THAT USES EXACT BONUS AND PENALTY VALUES GOES HERE
    # YEAH I GOTTA GET RID!!!!

    # THIS ISN'T WHAT DOMINANCE DOES, FIX!!!!!

    if "dominance" in atkSkills and AtkPanicFactor == 1:
        for i in range(1, 5): atkCombatBuffs[1] += attacker.buffs[i] * atkBonusesNeutralized[i]

    if "dominance" in defSkills and DefPanicFactor == 1:
        for i in range(1, 5): defCombatBuffs[1] += defender.buffs[i] * defBonusesNeutralized[i]

    if "bonusDoublerW" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += math.trunc(
                max(AtkPanicFactor * attacker.buffs[i] * atkBonusesNeutralized[i], 0) * 0.25 * atkSkills[
                    "bonusDoublerW"] + 0.25)

    if "bonusDoublerSk" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += math.trunc(
                max(AtkPanicFactor * attacker.buffs[i] * atkBonusesNeutralized[i], 0) * 0.25 * atkSkills[
                    "bonusDoublerSk"] + 0.25)

    if "bonusDoublerSe" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += math.trunc(
                max(AtkPanicFactor * attacker.buffs[i] * atkBonusesNeutralized[i], 0) * 0.25 * atkSkills[
                    "bonusDoublerSe"] + 0.25)

    if Status.BonusDoubler in attacker.statusPos:
        for i in range(1, 5):
            atkCombatBuffs[i] += max(AtkPanicFactor * attacker.buffs[i] * atkBonusesNeutralized[i], 0)

    if "bonusDoublerW" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += math.trunc(
                max(DefPanicFactor * defender.buffs[i] * defBonusesNeutralized[i], 0) * 0.25 * defSkills[
                    "bonusDoublerW"] + 0.25)

    if "bonusDoublerSk" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += math.trunc(
                max(DefPanicFactor * defender.buffs[i] * defBonusesNeutralized[i], 0) * 0.25 * defSkills[
                    "bonusDoublerSk"] + 0.25)

    if "bonusDoublerSe" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += math.trunc(
                max(DefPanicFactor * defender.buffs[i] * defBonusesNeutralized[i], 0) * 0.25 * defSkills[
                    "bonusDoublerSe"] + 0.25)

    if Status.BonusDoubler in defender.statusPos:
        for i in range(1, 5):
            defCombatBuffs[i] += max(DefPanicFactor * defender.buffs[i] * defBonusesNeutralized[i], 0)

    if "I think that enemy got THE POINT" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        for i in range(1, 5): atkCombatBuffs[i] += max(attacker.buffs[i] * AtkPanicFactor * atkBonusesNeutralized[i], 0)
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "I think that enemy got THE POINT" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        for i in range(1, 5): defCombatBuffs[i] += max(defender.buffs[i] * DefPanicFactor * defBonusesNeutralized[i], 0)
        atkr.spLossWhenAtkd -= 1
        atkr.spLossOnAtk -= 1

    if "gregorSword!" in atkSkills:
        atkr.DR_first_hit_NSP.append(40)
        for i in range(1, 5):
            defCombatBuffs -= 5 + max(defender.debuffs[i] * defPenaltiesNeutralized[i] * -1, 0) + max(
                defender.buffs[i] * DefPanicFactor * defPenaltiesNeutralized[i] * -1, 0)

    if "gregorSword!" in defSkills and defAllyWithin2Spaces:
        defr.DR_first_hit_NSP.append(40)
        for i in range(1, 5):
            atkCombatBuffs -= 5 + max(attacker.debuffs[i] * atkPenaltiesNeutralized[i] * -1, 0) + max(
                attacker.buffs[i] * AtkPanicFactor * atkPenaltiesNeutralized[i] * -1, 0)

    if "GiveMeYourBonuses" in atkSkills and DefPanicFactor == 1:
        totalBonuses = 0
        for i in range(1, 5): totalBonuses += defender.buffs[i] * defBonusesNeutralized[i]
        map(lambda x: x + math.trunc(totalBonuses / 2), atkCombatBuffs)

    if "ILoveBonusesAndWomenAndI'mAllOutOfBonuses" in atkSkills:
        tempAtkBonuses = 0
        tempDefBonuses = 0
        if AtkPanicFactor == 1:
            for i in range(1, 5): tempAtkBonuses += attacker.buffs[i] + atkBonusesNeutralized[i]
        if DefPanicFactor == 1:
            for i in range(1, 5): tempDefBonuses += defender.buffs[i] + defBonusesNeutralized[i]
        tempTotalBonuses = min(10, math.trunc((tempAtkBonuses + tempDefBonuses) * 0.4))
        map(lambda x: x + tempTotalBonuses, atkCombatBuffs)

    if "GiveMeYourBonuses" in defSkills and AtkPanicFactor == 1:
        totalBonuses = 0
        for i in range(1, 5): totalBonuses += attacker.buffs[i] * atkBonusesNeutralized[i]
        map(lambda x: x + math.trunc(totalBonuses * 0.5), defCombatBuffs)

    if "ILoveBonusesAndWomenAndI'mAllOutOfBonuses" in defSkills:
        tempAtkBonuses = 0
        tempDefBonuses = 0
        if AtkPanicFactor == 1:
            for i in range(1, 5): tempAtkBonuses += attacker.buffs[i] * atkBonusesNeutralized[i]
        if DefPanicFactor == 1:
            for i in range(1, 5): tempDefBonuses += defender.buffs[i] * defBonusesNeutralized[i]
        tempTotalBonuses = min(10, math.trunc((tempAtkBonuses + tempDefBonuses) * 0.4))
        map(lambda x: x + tempTotalBonuses, defCombatBuffs)

    if "beeeg debuff" in atkSkills:
        defCombatBuffs[1] -= 4
        defCombatBuffs[2] -= 4
        defCombatBuffs[3] -= 4
        for i in range(1, 5):
            atkCombatBuffs[ATK] += min(defender.debuffs[i] * defPenaltiesNeutralized[i], 0) * -1 + min(
                defender.buffs[i] * DefPanicFactor * defPenaltiesNeutralized[i], 0) * -1

    if "beeeg debuff" in defSkills and defAllyWithin2Spaces:
        atkCombatBuffs[1] -= 4
        atkCombatBuffs[2] -= 4
        atkCombatBuffs[3] -= 4
        for i in range(1, 5):
            defCombatBuffs[ATK] += min(attacker.debuffs[i] * atkPenaltiesNeutralized[i], 0) * -1 + min(
                attacker.buffs[i] * AtkPanicFactor * atkPenaltiesNeutralized[i], 0) * -1

    if "spectrumUnityMarth" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += 4 + (
                        (min(attacker.debuffs[i], 0) * -2) + (min(AtkPanicFactor * attacker.buffs[i], 0) * -2)) * (
                                     not atkPenaltiesNeutralized[i])

    if "spectrumUnityMarth" in defSkills and defAllyWithin2Spaces:
        for i in range(1, 5):
            defCombatBuffs[i] += 4 + (
                        (min(defender.debuffs[i], 0) * -2) + (min(DefPanicFactor * defender.buffs[i], 0) * -2)) * (
                                     not defPenaltiesNeutralized[i])

    if "penaltyReverse" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += ((min(attacker.debuffs[i], 0) * -2) + (
                        min(AtkPanicFactor * attacker.buffs[i], 0) * -2)) * (not atkPenaltiesNeutralized[i])

    if "penaltyReverse" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += ((min(defender.debuffs[i], 0) * -2) + (
                        min(DefPanicFactor * defender.buffs[i], 0) * -2)) * (not defPenaltiesNeutralized[i])

    if "Minecraft Gaming" in atkSkills:
        for i in range(1, 5):
            defCombatBuffs[i] -= 5 + (max(DefPanicFactor * defender.buffs[i], 0) * -2) * (not defBonusesNeutralized[i])

    if "Minecraft Gaming" in defSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] -= 5 + (max(AtkPanicFactor * attacker.buffs[i], 0) * -2) * (not atkBonusesNeutralized[i])

    # WHERE BONUSES AND PENALTIES ARE NEUTRALIZED
    for i in range(1, 5):
        atkCombatBuffs[i] -= atkPenaltiesNeutralized[i] * (
                    attacker.debuffs[i] + max(attacker.buffs[i] * AtkPanicFactor, 0))
        atkCombatBuffs[i] += atkBonusesNeutralized[i] * min(attacker.buffs[i] * AtkPanicFactor, 0)
        defCombatBuffs[i] -= defPenaltiesNeutralized[i] * (
                    defender.debuffs[i] + max(defender.buffs[i] * DefPanicFactor, 0))
        defCombatBuffs[i] += defBonusesNeutralized[i] * min(defender.buffs[i] * DefPanicFactor, 0)

    # add combat buffs to stats

    i = 0
    while i < 5:
        atkStats[i] += atkCombatBuffs[i]
        defStats[i] += defCombatBuffs[i]
        i += 1

    i = 0
    while i < 5:
        atkPhantomStats[i] += atkStats[i]
        defPhantomStats[i] += defStats[i]
        i += 1

    # From this point on, use atkStats/defStats for getting direct values in combat
    # Use atkPhantomStats/defPhantomStats for comparisons
    # END OF STAT MODIFICATION SKILLS, NO MORE SHOULD EXIST BENEATH THIS LINE

    # SPECIAL CHARGE MODIFICATION

    if "heavyBlade" in atkSkills and atkPhantomStats[1] > defPhantomStats[1] + max(-2 * atkSkills["heavyBlade"] + 7, 1):
        atkr.spGainOnAtk += 1
    if "heavyBlade" in defSkills and defPhantomStats[1] > atkPhantomStats[1] + max(-2 * defSkills["heavyBlade"] + 7, 1):
        defr.spGainOnAtk += 1

    if "royalSword" in atkSkills and atkAllyWithin2Spaces or "royalSword2" in atkSkills:
        atkr.spGainOnAtk += 1
    if ("royalSword" in defSkills or "royalSword2" in defSkills) and defAllyWithin2Spaces:
        defr.spGainOnAtk += 1

    if "ourBoyBlade" in atkSkills:
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "wanderer" in atkSkills and defHPGreaterEqual75Percent and atkPhantomStats[SPD] > defPhantomStats[SPD]:
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

    if "wanderer" in defSkills and atkHPGreaterEqual75Percent and defPhantomStats[SPD] > atkPhantomStats[SPD]:
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

    if "audBoost" in atkSkills and defHPEqual100Percent:
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "audBoost" in defSkills:
        atkr.spLossWhenAtkd -= 1
        atkr.spLossOnAtk -= 1

    # M!Shez - Crimson Blades - Base
    # Grants Spd+5. Inflicts Def/Res-5. Unit attacks twice.
    # At start of combat, grants the following based on unit's HP:
    #  - if ≥ 20%, grants Special cooldown charge +1 to unit per attack
    #  - if ≥ 40%, reduces damage from first attack during combat by 40%
    if "shez!" in atkSkills:
        if atkHPCur / atkStats[0] >= 0.2:
            atkr.spGainOnAtk += 1
            atkr.spGainWhenAtkd += 1
        if atkHPCur / atkStats[0] >= 0.4:
            atkr.DR_first_hit_NSP.append(40)

    if "shez!" in defSkills:
        if defHPCur / defStats[0] >= 0.2:
            defr.spGainOnAtk += 1
            defr.spGainWhenAtkd += 1
        if defHPCur / defStats[0] >= 0.4:
            defr.DR_first_hit_NSP.append(40)

    if "BY MISSILETAINN!!!" in atkSkills:
        atkr.spGainWhenAtkd += 1

    if "BY MISSILETAINN!!!" in defSkills:
        defr.spGainWhenAtkd += 1

    if "flashingBlade" in atkSkills and atkPhantomStats[2] > defPhantomStats[2] + max(
            -2 * atkSkills["flashingBlade"] + 7, 1):
        atkr.spGainOnAtk += 1
    if "flashingBlade" in defSkills and defPhantomStats[2] > atkPhantomStats[2] + max(
            -2 * defSkills["flashingBlade"] + 7, 1):
        defr.spGainOnAtk += 1

    if "guardHP" in atkSkills and atkHPCur / atkStats[0] >= atkSkills["guardHP"]:
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    # TEMPO WEAPONS/SKILLS

    if "tempo" in atkSkills:
        atkr.disable_foe_fastcharge = True
        atkr.disable_foe_guard = True

    if "tempo" in defSkills:
        defr.disable_foe_fastcharge = True
        defr.disable_foe_guard = True

    if atkr.disable_foe_guard:
        atkr.spLossOnAtk = 0
        atkr.spLossWhenAtkd = 0

    if atkr.disable_foe_fastcharge:
        defr.spGainOnAtk = 0
        defr.spGainWhenAtkd = 0

    if defr.disable_foe_guard:
        defr.spLossOnAtk = 0
        defr.spLossWhenAtkd = 0

    if defr.disable_foe_fastcharge:
        atkr.spGainOnAtk = 0
        atkr.spGainWhenAtkd = 0

    atkr.spGainOnAtk = min(atkr.spGainOnAtk, 1) + max(atkr.spLossOnAtk, -1)
    atkr.spGainWhenAtkd = min(atkr.spGainWhenAtkd, 1) + max(atkr.spLossWhenAtkd, -1)
    defr.spGainOnAtk = min(defr.spGainOnAtk, 1) + max(defr.spLossOnAtk, -1)
    defr.spGainWhenAtkd = min(defr.spGainWhenAtkd, 1) + max(defr.spLossWhenAtkd, -1)

    # Pre-strike SP charge/slow

    if "Mr. Fire Emblem" in atkSkills and atkHPGreaterEqual25Percent and defender.getSpecialType() == "Offense" and \
            atkPhantomStats[RES] >= defPhantomStats[RES]:
        defr.sp_charge_first -= 1

    if "Mr. Fire Emblem" in defSkills and defHPGreaterEqual25Percent and attacker.getSpecialType() == "Offense" and \
            defPhantomStats[RES] >= atkPhantomStats[RES]:
        atkr.sp_charge_first -= 1

    # weird niche stuff

    if "windsweep" in atkSkills:
        atkr.follow_up_denials -= 1
        if atkPhantomStats[2] > defPhantomStats[2] + (
                -2 * atkSkills["windsweep"] + 7) and defender.getTargetedDef() == -1:
            cannotCounter = True

    # I hate this skill up until level 4 why does it have all those conditions
    if "brashAssault" in atkSkills and (
            cannotCounter or not (attacker.getRange() == defender.getRange() or ignoreRng)) and atkHPCur / atkStats[
        0] <= 0.1 * atkSkills["brashAssault"] + 0.2:
        atkr.follow_ups_skill += 1

    # NFU
    if Status.NullFollowUp in attacker.statusPos and atkPhantomStats[2] > defPhantomStats[2]:
        atkr.prevent_foe_FU, atkr.prevent_self_FU_denial = True

    if Status.NullFollowUp in defender.statusPos and defPhantomStats[2] > atkPhantomStats[2]:
        defr.prevent_foe_FU, defr.prevent_self_FU_denial = True

    if atkr.prevent_foe_FU: defr.follow_ups_skill = 0
    if defr.prevent_foe_FU: atkr.follow_ups_skill = 0
    if atkr.prevent_self_FU_denial: atkr.follow_up_denials = 0
    if defr.prevent_self_FU_denial: defr.follow_up_denials = 0

    # TRUE DAMAGE ADDITION
    if "SpdDmg" in atkSkills and atkPhantomStats[2] > defPhantomStats[2]:
        atkr.true_all_hits += min(math.trunc((atkPhantomStats[2] - defPhantomStats[2]) * 0.1 * atkSkills["SpdDmg"]),
                                  atkSkills["SpdDmg"])
    if "SpdDmg" in defSkills and defPhantomStats[2] > atkPhantomStats[2]:
        defr.true_all_hits += min(math.trunc((defPhantomStats[2] - atkPhantomStats[2]) * 0.1 * defSkills["SpdDmg"]),
                                  defSkills["SpdDmg"])

    if "moreeeeta" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.true_all_hits += math.trunc(atkStats[SPD] * 0.1)
    if "moreeeeta" in defSkills and defHPGreaterEqual25Percent:
        defr.true_all_hits += math.trunc(atkStats[SPD] * 0.1)

    if "thraicaMoment" in atkSkills and defStats[3] >= defStats[4] + 5:
        atkr.true_all_hits += 7
    if "thraciaMoment" in defSkills and atkStats[3] >= atkStats[4] + 5:
        defr.true_all_hits += 7

    if "LOVE PROVIIIIDES, PROTECTS US" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.true_all_hits += math.trunc(atkStats[2] * 0.15)
    if "LOVE PROVIIIIDES, PROTECTS US" in defSkills and defHPGreaterEqual25Percent:
        defr.true_all_hits += math.trunc(defStats[2] * 0.15)

    if "vassalBlade" in atkSkills:
        atkr.true_all_hits += math.trunc(atkStats[2] * 0.15)
    if "vassalBlade" in defSkills and defAllyWithin2Spaces:
        defr.true_all_hits += math.trunc(defStats[2] * 0.15)

    if "infiniteSpecial" in atkSkills:
        atkr.true_all_hits += math.trunc(atkStats[2] * 0.15)
    if "infiniteSpecial" in defSkills:
        defr.true_all_hits += math.trunc(defStats[2] * 0.15)

    if "newVTyrfing" in atkSkills and (not atkHPEqual100Percent or defHPGreaterEqual75Percent):
        atkr.true_all_hits += math.trunc(atkStats[ATK] * 0.15)
    if "newVTyrfing" in defSkills:
        defr.true_all_hits += math.trunc(defStats[ATK] * 0.15)

    if "hamburger" in atkSkills:
        atkr.true_all_hits += math.trunc(atkStats[DEF] * 0.15)
    if "hamburger" in atkSkills and defAllyWithin2Spaces:
        defr.true_all_hits += math.trunc(defStats[DEF] * 0.15)

    if "I HATE FIRE JOKES >:(" in atkSkills and spaces_moved_by_atkr:
        atkr.true_all_hits += math.trunc(math.trunc(defStats[DEF] * 0.10 * min(spaces_moved_by_atkr, 4)))
    if "I HATE FIRE JOKES >:(" in defSkills and spaces_moved_by_atkr:
        defr.true_all_hits += math.trunc(atkStats[DEF] * 0.10 * min(spaces_moved_by_atkr, 4))

    if "renaisTwins" in atkSkills and (atkHasBonus or atkHasPenalty):
        atkr.true_all_hits += math.trunc(defStats[3] * 0.20)
        atkr.all_hits_heal += math.trunc(defStats[3] * 0.20)

    if "renaisTwins" in defSkills and defAllyWithin2Spaces and (defHasBonus or defHasPenalty):
        defr.true_all_hits += math.trunc(atkStats[3] * 0.20)
        defr.all_hits_heal += math.trunc(defStats[3] * 0.20)

    if "megaAstra" in atkSkills and atkPhantomStats[1] > defPhantomStats[3]:
        atkr.true_all_hits += max(math.trunc((atkStats[1] - defStats[3]) * 0.5), 0)

    if "megaAstra" in defSkills and defPhantomStats[1] > atkPhantomStats[3]:
        defr.true_all_hits += max(math.trunc((defStats[1] - atkStats[3]) * 0.5), 0)

    if "Sacred Stones Strike!" in atkSkills and atkAllyWithin3Spaces:
        atkSpEffects.update({"spMissiletainn": 0})

    if "Sacred Stones Strike!" in defSkills and defAllyWithin3Spaces:
        defSpEffects.update({"spMissiletainn": 0})

    if "sky-hopper" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.true_all_hits += trunc(0.2 * atkStats[SPD])

    if "sky-hopper" in defSkills and defHPGreaterEqual25Percent:
        defr.true_all_hits += trunc(0.2 * defStats[SPD])

    # TRUE DAMAGE SUBTRACTION

    if "daydream_egg" in atkSkills and defHPGreaterEqual75Percent:
        atkr.TDR_all_hits += trunc(0.2 * atkStats[RES])

    if "daydream_egg" in defSkills and atkHPGreaterEqual75Percent:
        defr.TDR_all_hits += trunc(0.2 * defStats[RES])

    # PART 2
    if "laguz_friend" in atkSkills:
        skill_lvl = atkSkills["laguz_friend"]

        if attacker.getMaxSpecialCooldown() >= 3 and attacker.getSpecialType() == "Offense" or attacker.getSpecialType() == "Defense":
            atkr.TDR_all_hits += trunc(0.05 * skill_lvl * max(atkStats[DEF], atkStats[RES]))

        if attacker.getMaxSpecialCooldown() >= 3 and attacker.getSpecialType() == "Offense":
            atkr.true_sp += trunc(0.05 * skill_lvl * max(atkStats[DEF], atkStats[RES]))
            if skill_lvl == 4: atkr.sp_pierce_DR = True
        if attacker.getSpecialType() == "Defense":
            atkr.true_sp_next += trunc(0.05 * skill_lvl * max(atkStats[DEF], atkStats[RES]))
            if skill_lvl == 4: atkr.sp_pierce_after_DSP = True

    # EFFECTIVENESS CHECK

    oneEffAtk = False
    oneEffDef = False

    if "effInf" in atkSkills and defender.move == 0: oneEffAtk = True
    if "effInf" in defSkills and attacker.move == 0: oneEffDef = True

    if "effCav" in atkSkills and "nullEffCav" not in defSkills and defender.move == 1: oneEffAtk = True
    if "effCav" in defSkills and "nullEffCav" not in atkSkills and attacker.move == 1: oneEffDef = True

    if "effFly" in atkSkills and "nullEffFly" not in defSkills and defender.move == 2: oneEffAtk = True
    if "effFly" in defSkills and "nullEffFly" not in atkSkills and attacker.move == 2: oneEffDef = True

    if "effArm" in atkSkills and "nullEffArm" not in defSkills and defender.move == 3: oneEffAtk = True
    if "effArm" in defSkills and "nullEffArm" not in atkSkills and attacker.move == 3: oneEffDef = True

    if ("effDrg" in atkSkills or Status.EffDragons in attacker.statusPos) and "nullEffDrg" not in defSkills and (
            defender.getTargetedDef() == 0 or "loptous" in defSkills):
        oneEffAtk = True
    if ("effDrg" in defSkills or Status.EffDragons in defender.statusPos) and "nullEffDrg" not in atkSkills and (
            attacker.getTargetedDef() == 0 or "loptous" in atkSkills):
        oneEffDef = True

    if "effMagic" in atkSkills and defender.wpnType in ["RTome", "BTome", "GTome", "CTome"]: oneEffAtk = True
    if "effMagic" in defSkills and attacker.wpnType in ["RTome", "BTome", "GTome", "CTome"]: oneEffDef = True

    if "effBeast" in atkSkills and defender.wpnType in ["RBeast", "BBeast", "GBeast", "CBeast"]:
        oneEffAtk = True
    if "effBeast" in defSkills and attacker.wpnType in ["RBeast", "BBeast", "GBeast", "CBeast"]:
        oneEffDef = True

    if "effCaeda" in atkSkills and (defender.wpnType in ["Sword", "Lance", "Axe", "CBow"] or (
            defender.move == 3 and "nullEffArm" not in defSkills)):
        oneEffAtk = True
    if "effCaeda" in defSkills and (attacker.wpnType in ["Sword", "Lance", "Axe", "CBow"] or (
            attacker.move == 3 and "nullEffArm" not in atkSkills)):
        oneEffDef = True

    if "effShez" in atkSkills:
        if defender.move == 0 and defender.wpnType not in ["RDragon", "BDragon", "GDragon", "CDragon", "RBeast",
                                                           "BBeast", "GBeast", "CBeast"]:
            threshold = defPhantomStats[2] + 20
        else:
            threshold = defPhantomStats[2] + 5

        if atkPhantomStats[2] >= threshold:
            oneEffAtk = True

    if defender.wpnType == "BTome" and "haarEff" in atkSkills:
        oneEffDef = True
    if attacker.wpnType == "BTome" and "haarEff" in defSkills:
        oneEffAtk = True

    if oneEffAtk: atkStats[1] += math.trunc(atkStats[1] * 0.5)
    if oneEffDef: defStats[1] += math.trunc(defStats[1] * 0.5)

    # COLOR ADVANTAGE

    if (attacker.getColor() == "Red" and defender.getColor() == "Green") or (
            attacker.getColor() == "Green" and defender.getColor() == "Blue") or \
            (attacker.getColor() == "Blue" and defender.getColor() == "Red") or (
            defender.getColor() == "Colorless" and "colorlessAdv" in atkSkills):

        if (atkCA == 1 or defCA == 1) and triAdept != -1: triAdept = -1
        if defCA == 2 and triAdept != -1: triAdept = -1
        if atkCA == 3 and triAdept != -1: triAdept = -5

        atkStats[1] += math.trunc(atkStats[1] * (0.25 + .05 * triAdept))
        defStats[1] -= math.trunc(defStats[1] * (0.25 + .05 * triAdept))

        wpnAdvHero = 0

    if (attacker.getColor() == "Blue" and defender.getColor() == "Green") or (
            attacker.getColor() == "Red" and defender.getColor() == "Blue") or \
            (attacker.getColor() == "Green" and defender.getColor() == "Red") or (
            attacker.getColor() == "Colorless" and "colorlessAdv" in defSkills):

        if (atkCA == 1 or defCA == 1) and triAdept != -1: triAdept = -1
        if atkCA == 2 and triAdept != -1: triAdept = -1
        if atkCA == 3 and triAdept != -1: triAdept = -5
        atkStats[1] -= math.trunc(atkStats[1] * (0.25 + .05 * triAdept))
        defStats[1] += math.trunc(defStats[1] * (0.25 + .05 * triAdept))

        wpnAdvHero = 1

    # WHICH DEFENSE ARE WE TARGETING?

    atkTargetingDefRes = int(attacker.getTargetedDef() == 1)

    if attacker.getTargetedDef() == 0 and "dragonCheck" in atkSkills:
        if defender.getRange() == 2 and defStats[3] > defStats[4]:
            atkTargetingDefRes += 1
        elif defender.getRange() != 2:
            atkTargetingDefRes += 1

    defTargetingDefRes = int(defender.getTargetedDef() == 1)

    if defender.getTargetedDef() == 0 and "dragonCheck" in defSkills:
        if attacker.getRange() == 2 and atkStats[3] > atkStats[4]:
            defTargetingDefRes += 1
        elif attacker.getRange() != 2:
            defTargetingDefRes += 1

    if "permHexblade" in atkSkills: defTargetingDefRes = int(defStats[3] < defStats[4])
    if "permHexblade" in defSkills: atkTargetingDefRes = int(atkStats[3] < atkStats[4])

    # additional follow-up granted by outspeeding
    outspeedFactor = 5

    atkOutspeedFactor = 5
    defOutspeedFactor = 5

    atkPotentIndex = -1
    defPotentIndex = -1

    if "FOR THE PRIDE OF BRODIA" in atkSkills:
        atkOutspeedFactor += 20
        defOutspeedFactor += 20
    if "FOR THE PRIDE OF BRODIA" in defSkills:
        atkOutspeedFactor += 20
        defOutspeedFactor += 20

    if "wyvernRift" in atkSkills and atkStats[SPD] + atkStats[DEF] >= defStats[SPD] + defStats[DEF] - 10:
        defOutspeedFactor += 20

    if "wyvernRift" in defSkills and defStats[SPD] + defStats[DEF] >= atkStats[SPD] + atkStats[DEF] - 10:
        atkOutspeedFactor += 20

    if "potentStrike" in atkSkills and atkStats[SPD] >= defStats[SPD] + (atkOutspeedFactor - 25):
        atkr.potent_FU = True

    if "potentStrike" in defSkills and defStats[SPD] >= atkStats[SPD] + (defOutspeedFactor - 25):
        defr.potent_FU = True

    if "potentFix" in atkSkills:
        atkr.potent_new_percentage = atkSkills["potentFix"]

    if "potentFix" in defSkills:
        defr.potent_new_percentage = defSkills["potentFix"]

    if (atkStats[SPD] >= defStats[SPD] + atkOutspeedFactor): atkr.follow_ups_spd += 1
    if (defStats[SPD] >= atkStats[SPD] + defOutspeedFactor): defr.follow_ups_spd += 1

    atkAlive = True
    defAlive = True

    # wow this needs a rework
    def getSpecialDamage(effs, initStats, initHP, otherStats, defOrRes, base_damage, num_foe_atks):
        total = 0

        if "atkBoost" in effs:
            total += math.trunc(initStats[ATK] * .10 * effs["atkBoost"])

        if "spdBoost" in effs:
            total += math.trunc(initStats[SPD] * .10 * effs["spdBoost"])

        if "defBoost" in effs:
            total += math.trunc(initStats[SPD] * .10 * effs["defBoost"])

        if "resBoost" in effs:
            total += math.trunc(initStats[RES] * .10 * effs["resBoost"])

        if "rupturedSky" in effs:
            total += math.trunc(otherStats[1] * .10 * effs["rupturedSky"])

        if "staffRes" in effs:
            total += math.trunc(otherStats[4] * .10 * effs["staffRes"])

        if "retaliatoryBoost" in effs:
            total += math.trunc((initHP / initStats[HP]) * 0.10 * effs["retaliatoryBoost"])

        if "dmgBoost" in effs:
            total += math.trunc(base_damage * 0.1 * effs["dmgBoost"])

        targeted_defense = otherStats[defOrRes + 3]
        if "defReduce" in effs:
            reduced_def = targeted_defense - math.trunc(targeted_defense * .10 * effs["defReduce"])
            attack = initStats[ATK] - reduced_def
            total += attack - base_damage

        if "spMissiletainn" in effs:
            total += min(initStats[HP] - initHP, 30)

        if "spTimerra" in effs:
            total += math.trunc(initStats[SPD] * .10 * effs["spTimerra"])

        if "NumAtkBoost" in effs:
            total += math.trunc((effs["NumAtkBoost"] + num_foe_atks) * 0.10 * initStats[ATK])

        return total

    # COMPUTE TURN ORDER

    cannotCounterFinal = (cannotCounter and not disableCannotCounter) or not (attacker.getRange() == defender.getRange() or ignoreRng)
    # Will never counter if defender has no weapon
    if defender.getWeapon() == NIL_WEAPON: cannotCounterFinal = True

    # Follow-Up Granted if sum of allowed - denied follow-ups is > 0
    followupA = atkr.follow_ups_spd + atkr.follow_ups_skill + atkr.follow_up_denials > 0
    followupD = defr.follow_ups_spd + defr.follow_ups_skill + defr.follow_up_denials > 0

    # hardy bearing
    if atkr.hardy_bearing:
        atkr.self_desperation = False
        atkr.other_desperation = False
        atkr.vantage = False

    if defr.hardy_bearing:
        defr.self_desperation = False
        defr.other_desperation = False
        defr.vantage = False

    if atkr.vantage or defr.vantage:
        startString = "DA"
        if followupD:
            startString += "D"
        if followupA:
            startString += "A"
    else:
        startString = "AD"
        if followupA:
            startString += "A"
        if followupD:
            startString += "D"

    if startString[0] == 'A':
        firstCheck = atkr.self_desperation or defr.other_desperation
        secondCheck = defr.self_desperation or atkr.other_desperation
    else:
        firstCheck = defr.self_desperation or atkr.other_desperation
        secondCheck = atkr.self_desperation or defr.other_desperation

    if firstCheck:
        startString = move_letters(startString, startString[0])
    if secondCheck:
        startString = move_letters(startString, {"A", "D"}.difference([startString[0]]).pop())

    newString = ""

    # duplicate letters if Brave Eff
    # it makes zero sense how two D's need to be added, but only one A, but I don't care it works
    for c in startString:
        if c == 'A' and atkr.brave:
            newString += c
        if c == 'D' and defr.brave:
            newString += c * 2
        else:
            newString += c

    # potent strike
    if atkr.potent_FU:
        last_a_index = newString.rfind('A')
        newString = newString[:last_a_index + 1] + 'A' + newString[last_a_index + 1:]

    if defr.potent_FU:
        last_a_index = newString.rfind('D')
        newString = newString[:last_a_index + 1] + 'D' + newString[last_a_index + 1:]

        defPotentIndex = newString.rfind('D')

    if atkr.potent_FU:
        atkPotentIndex = newString.rfind('A')

    # code don't work without these
    startString = newString
    startString2 = startString

    if cannotCounterFinal: startString2 = startString.replace("D", "")

    # list of attack objects
    attackList = []
    A_Count = 0
    D_Count = 0
    i = 0

    while i < len(startString2):
        if startString2[i] == "A":
            A_Count += 1
            isFollowUp = A_Count == 2 and (followupA or atkr.potent_FU) and not atkr.brave or A_Count in [3, 4, 5]
            isConsecutive = True if A_Count >= 2 and startString2[i - 1] == "A" else False
            potentRedu = 100
            if "potentStrike" in atkSkills and i == atkPotentIndex:
                potentRedu = 10 * atkSkills["potentStrike"] + 40 * int(not (atkr.brave or followupA))
            attackList.append(Attack(0, isFollowUp, isConsecutive, A_Count, A_Count + D_Count,
                                     None if A_Count + D_Count == 1 else attackList[i - 1], potentRedu))
        else:
            D_Count += 1
            isFollowUp = D_Count == 2 and (followupD or defr.potent_FU) and not defr.brave or D_Count in [3, 4, 5]
            isConsecutive = True if D_Count >= 2 and startString2[i - 1] == "D" else False
            potentRedu = 100
            if "potentStrike" in defSkills and i == defPotentIndex:
                potentRedu = 10 * atkSkills["potentStrike"] + 40 * int(not (defr.brave or followupD))
            attackList.append(Attack(1, isFollowUp, isConsecutive, D_Count, A_Count + D_Count,
                                     None if A_Count + D_Count == 1 else attackList[i - 1], potentRedu))
        i += 1

    # Damage reduction calculated based on a difference between two stats (Dodge, etc.)

    if "Just Lean" in atkSkills and atkHPGreaterEqual25Percent and atkPhantomStats[2] > defPhantomStats[2]:
        atkr.DR_all_hits_NSP.append(min(4 * (atkPhantomStats[2] - defPhantomStats[2], 40)))

    if "Just Lean" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[2] > atkPhantomStats[2]:
        defr.DR_all_hits_NSP.append(min(4 * (defPhantomStats[2] - atkPhantomStats[2], 40)))

    # Rutger - Wanderer Blade - Refined Eff
    if "like the university" in atkSkills and atkHPGreaterEqual25Percent and atkPhantomStats[2] > defPhantomStats[2]:
        atkr.DR_all_hits_NSP.append(min(4 * (atkPhantomStats[2] - defPhantomStats[2], 40)))

    if "like the university" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[2] > atkPhantomStats[2]:
        defr.DR_all_hits_NSP.append(min(4 * (defPhantomStats[2] - atkPhantomStats[2], 40)))

    if "BONDS OF FIIIIRE, CONNECT US" in atkSkills and atkHPGreaterEqual25Percent and atkPhantomStats[2] > \
            defPhantomStats[2]:
        atkr.DR_all_hits_NSP.append(min(4 * (atkPhantomStats[2] - defPhantomStats[2], 40)))

    if "BONDS OF FIIIIRE, CONNECT US" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[2] > \
            atkPhantomStats[2]:
        defr.DR_all_hits_NSP.append(min(4 * (defPhantomStats[2] - atkPhantomStats[2], 40)))

    if "LOVE PROVIIIIDES, PROTECTS US" in atkSkills and atkHPGreaterEqual25Percent and atkPhantomStats[2] > \
            defPhantomStats[2]:
        atkr.DR_all_hits_NSP.append(min(4 * (atkPhantomStats[2] - defPhantomStats[2], 40)))

    if "LOVE PROVIIIIDES, PROTECTS US" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[2] > \
            atkPhantomStats[2]:
        defr.DR_all_hits_NSP.append(min(4 * (defPhantomStats[2] - atkPhantomStats[2], 40)))

    if Status.Dodge in atkSkills and atkPhantomStats[2] > defPhantomStats[2]:
        atkr.DR_all_hits_NSP.append(min(4 * (atkPhantomStats[2] - defPhantomStats[2], 40)))

    if Status.Dodge in defSkills and defPhantomStats[2] > atkPhantomStats[2]:
        defr.DR_all_hits_NSP.append(min(4 * (defPhantomStats[2] - atkPhantomStats[2], 40)))

    if "reduFU" in atkSkills and (turn % 2 == 1 or not defHPEqual100Percent):
        atkr.DR_first_hit_NSP.append(30 * (1 + int(followupD)))

    if "reduFU" in defSkills and (turn % 2 == 1 or not atkHPEqual100Percent):
        defr.DR_first_hit_NSP.append(30 * (1 + int(followupA)))

    # post combat charge
    if "A man has fallen into the river in LEGO City!" in atkSkills and atkHPGreaterEqual25Percent:
        atkPostCombatSpCharge += 1

    if "A man has fallen into the river in LEGO City!" in defSkills and defHPGreaterEqual25Percent:
        defPostCombatSpCharge += 1

    if "shine on" in atkSkills and atkr.brave:
        atkr.reduce_self_sp_damage += 8

    if "shine on" in defSkills and defr.brave:
        defr.reduce_self_sp_damage += 8

    # method to attack
    def attack(striker, strikee, stkSpEffects, steSpEffects, stkStats, steStats, defOrRes, curReduction,
               curSpecialReduction, stkHPCur, steHPCur, stkSpCount, steSpCount, I_stkr, I_ster, curAttack):

        dmgBoost = 0

        # has special triggered due to this hit
        stkr_sp_triggered = False
        ster_sp_triggered = False

        # attack minus defense or resistance
        attack = stkStats[1] - steStats[3 + defOrRes]

        if attack < 0: attack = 0

        if stkSpCount == 0 and striker.getSpecialType() == "Offense" and not I_stkr.special_disabled:
            if not is_in_sim: print(striker.getName() + " procs " + striker.getSpName() + ".")
            num_foe_atks = curAttack.attackNumAll - curAttack.attackNumSelf
            dmgBoost = getSpecialDamage(stkSpEffects, stkStats, stkHPCur, steStats, defOrRes, attack, num_foe_atks)

            if I_stkr.brave:  # emblem marth effect
                dmgBoost = max(dmgBoost - I_stkr.reduce_self_sp_damage, 0)

            I_stkr.special_triggered = True
            stkr_sp_triggered = True

        attack += dmgBoost  # true damage by specials
        attack += I_stkr.true_all_hits  # true damage on all hits

        attack += I_stkr.true_sp_next_CACHE
        I_stkr.true_sp_next_CACHE = 0

        if curAttack.attackNumSelf == 1:
            attack += I_stkr.true_first_hit

        if curAttack.attackNumSelf != curAttack.attackNumAll:
            attack += I_stkr.true_after_foe_first
            I_stkr.true_after_foe_first = 0

        if stkr_sp_triggered:
            attack += I_stkr.true_sp

        if I_stkr.special_triggered or stkSpCount == 0:  # special-enabled true damage (finish)
            attack += I_stkr.true_finish

        attack += I_stkr.stacking_retaliatory_damage
        attack += I_stkr.nonstacking_retaliatory_damage

        for x in I_stkr.retaliatory_full_damages_CACHE:
            attack += math.trunc(I_stkr.most_recent_atk * (x / 100))

        # half damage if staff user without wrathful staff
        if striker.getSpecialType() == "Staff": attack = math.trunc(attack * 0.5)

        # potent FU reduction
        attack = trunc(attack * curAttack.potentRedu / 100)

        # the final attack in all it's glory
        full_atk = attack
        I_ster.most_recent_atk = attack

        # damage reduction
        total_reduction = 1

        if not (I_stkr.always_pierce_DR or
                (stkr_sp_triggered and I_stkr.sp_pierce_DR) or
                (curAttack.isFollowUp and I_stkr.pierce_DR_FU) or
                (I_stkr.sp_pierce_after_def_sp_CACHE)):
            for x in curReduction:
                total_reduction *= 1 - (x / 100 * I_stkr.damage_reduction_reduction)  # change by redu factor

        I_stkr.sp_pierce_after_def_sp_CACHE = False

        for x in curSpecialReduction:
            total_reduction *= 1 - (x / 100)

        # defensive specials
        if steSpCount == 0 and strikee.getSpecialType() == "Defense" and not I_ster.special_disabled:
            if striker.getRange() == 1 and "closeShield" in steSpEffects:
                if not is_in_sim: print(strikee.getName() + " procs " + strikee.getSpName() + ".")
                total_reduction *= 1 - (0.10 * steSpEffects["closeShield"])
                if I_ster.double_def_sp_charge:
                    total_reduction *= 1 - (0.10 * steSpEffects["closeShield"])

            elif striker.getRange() == 2 and "distantShield" in steSpEffects:
                if not is_in_sim: print(strikee.getName() + " procs " + strikee.getSpName() + ".")
                total_reduction *= 1 - (0.10 * steSpEffects["distantShield"])
                if I_ster.double_def_sp_charge:
                    total_reduction *= 1 - (0.10 * steSpEffects["distantShield"])

            I_ster.special_triggered = True
            ster_sp_triggered = True

        # rounded attack damage
        rounded_DR = (trunc(total_reduction * 100)) / 100
        attack = math.ceil(attack * rounded_DR)

        attack = max(attack - I_ster.TDR_all_hits, 0)

        if not curAtk.isFollowUp:
            attack = max(attack - I_ster.TDR_first_strikes, 0)
        else:
            attack = max(attack - I_ster.TDR_second_strikes, 0)

        if ster_sp_triggered: attack = max(attack - I_ster.TDR_on_def_sp, 0)

        curMiracleTriggered = False

        circlet_of_bal_cond = stkSpCount == 0 or steSpCount == 0 or I_stkr.special_triggered or I_ster.special_triggered

        # non-special Miracle
        if ((I_ster.pseudo_miracle or circlet_of_bal_cond and I_ster.circlet_miracle) and steHPCur - attack < 1 and steHPCur > 1) and not I_ster.disable_foe_miracle:
            attack = steHPCur - 1
            curMiracleTriggered = True

        # special Miracle
        if steSpCount == 0 and "miracleSP" in steSpEffects and steHPCur - attack < 1 and steHPCur > 1 and not I_ster.pseudo_miracle:
            if not is_in_sim: print(strikee.getName() + " procs " + strikee.getSpName() + ".")
            attack = steHPCur - 1
            I_ster.special_triggered = True
            ster_sp_triggered = True

        # non-special miracle has triggered
        if curMiracleTriggered:
            I_ster.pseudo_miracle = False

        # reduced atk
        I_ster.most_recent_reduced_atk = full_atk - attack

        # reset all retaliatory true damages
        I_stkr.stacking_retaliatory_damage = 0
        I_stkr.nonstacking_retaliatory_damage = 0
        I_stkr.retaliatory_full_damages_CACHE = []

        # set for foe

        # ice mirror i & ii, negating fang, etc.
        if "iceMirror" in steSpEffects and ster_sp_triggered:
            I_ster.stacking_retaliatory_damage += full_atk - attack

        # divine recreation, ginnungagap (weapon)
        if I_ster.retaliatory_reduced:
            I_ster.nonstacking_retaliatory_damage = full_atk - attack

        # brash assault, counter roar
        I_ster.retaliatory_full_damages_CACHE = I_ster.retaliatory_full_damages[:]

        # the attack™
        steHPCur -= attack  # goodness gracious

        if not is_in_sim: print(
            striker.getName() + " attacks " + strikee.getName() + " for " + str(attack) + " damage.")  # YES THEY DID

        # used for determining full attack damage
        presented_attack = attack
        # to evaluate noontime heal on hit that kills
        if steHPCur < 1: attack += steHPCur

        stkSpCount = max(stkSpCount - (1 + I_stkr.spGainOnAtk), 0)
        steSpCount = max(steSpCount - (1 + I_ster.spGainWhenAtkd), 0)

        if stkr_sp_triggered:
            stkSpCount = striker.specialMax
            if I_stkr.first_sp_charge != 0:
                stkSpCount -= I_stkr.first_sp_charge
                stkSpCount = max(stkSpCount, 0)
                I_stkr.first_sp_charge = 0

            I_stkr.true_sp_next_CACHE = I_stkr.true_sp_next

            for x in I_stkr.DR_sp_trigger_next_all_SP:
                I_stkr.DR_sp_trigger_next_all_SP_CACHE.append(x)

        if ster_sp_triggered:
            steSpCount = striker.specialMax
            if I_ster.first_sp_charge != 0:
                steSpCount -= I_ster.first_sp_charge
                steSpCount = max(steSpCount, 0)
                I_ster.first_sp_charge = 0

            I_ster.true_sp_next_CACHE = I_ster.true_sp_next

            if I_ster.sp_pierce_after_def_sp:
                I_ster.sp_pierce_after_def_sp_CACHE = True

        # healing

        totalHealedAmount = 0

        mid_combat_skill_dmg = I_stkr.all_hits_heal + I_stkr.finish_mid_combat_heal * (
                    stkSpCount == 0 or I_stkr.special_triggered)
        surge_heal = I_stkr.surge_heal

        # save for skills
        # += trunc(stkStats[0] * (min(striker.getMaxSpecialCooldown() * 20 + 10, 100) / 100))

        totalHealedAmount += mid_combat_skill_dmg

        if curAttack.isFollowUp:
            totalHealedAmount += I_stkr.follow_up_heal

        if "absorb" in striker.getSkills():
            totalHealedAmount += math.trunc(attack * 0.5)
        if stkr_sp_triggered:
            totalHealedAmount += surge_heal

            if "healSelf" in stkSpEffects:
                totalHealedAmount += math.trunc(attack * 0.1 * stkSpEffects["healSelf"])

        if Status.DeepWounds in striker.statusNeg or I_ster.disable_foe_healing:
            totalHealedAmount -= totalHealedAmount * math.trunc(1 - I_stkr.deep_wounds_allowance)

        stkHPCur += totalHealedAmount
        if not is_in_sim and totalHealedAmount: print(
            striker.getName() + " heals " + str(totalHealedAmount) + " HP during combat.")

        if stkHPCur > stkStats[0]: stkHPCur = stkStats[0]

        return stkHPCur, steHPCur, stkSpCount, steSpCount, presented_attack, totalHealedAmount

    # pre-combat damage

    defHPCur = max(defHPCur - atkr.burn_damage, 1)
    atkHPCur = max(atkHPCur - defr.burn_damage, 1)

    # PERFORM THE ATTACKS

    i = 0
    while i < len(attackList) and (atkAlive and defAlive or is_in_sim):
        curAtk = attackList[i]

        # recoil damage
        if curAtk.attackOwner == 0 and curAtk.attackNumSelf == 1 and atkRecoilDmg > 0: atkSelfDmg += atkRecoilDmg
        if curAtk.attackOwner == 0 and curAtk.attackNumSelf == 1 and NEWatkOtherDmg > 0: atkOtherDmg += NEWatkOtherDmg
        if curAtk.attackOwner == 1 and curAtk.attackNumSelf == 1 and defRecoilDmg > 0: defSelfDmg += defRecoilDmg
        if curAtk.attackOwner == 1 and curAtk.attackNumSelf == 1 and NEWdefOtherDmg > 0: defOtherDmg += NEWdefOtherDmg

        # post-combat status effects & mid-combat special charges
        if curAtk.attackOwner == 0 and curAtk.attackNumSelf == 1:
            atkPostCombatStatusesApplied[0] = atkPostCombatStatusesApplied[0] + atkPostCombatStatusesApplied[1]
            defPostCombatStatusesApplied[0] = defPostCombatStatusesApplied[0] + defPostCombatStatusesApplied[2]

            atkSpCountCur = max(0, atkSpCountCur - atkr.sp_charge_first)
            atkSpCountCur = min(atkSpCountCur, attacker.specialMax)

        if curAtk.attackOwner == 0 and (
                curAtk.attackNumSelf == 2 and not atkr.brave or curAtk.attackNumSelf == 3 and atkr.brave):
            atkSpCountCur = max(0, atkSpCountCur - atkr.sp_charge_FU)
            atkSpCountCur = min(atkSpCountCur, attacker.specialMax)

        if curAtk.attackOwner == 1 and curAtk.attackNumSelf == 1:
            defPostCombatStatusesApplied[0] = defPostCombatStatusesApplied[0] + defPostCombatStatusesApplied[1]
            atkPostCombatStatusesApplied[0] = atkPostCombatStatusesApplied[0] + atkPostCombatStatusesApplied[2]

            defSpCountCur = max(0, defSpCountCur - defr.sp_charge_first)
            defSpCountCur = min(defSpCountCur, defender.specialMax)

        if curAtk.attackOwner == 1 and (
                curAtk.attackNumSelf == 2 and not defr.brave or curAtk.attackNumSelf == 3 and defr.brave):
            defSpCountCur = max(0, defSpCountCur - defr.sp_charge_FU)
            defSpCountCur = min(defSpCountCur, defender.specialMax)

        if (atkr.special_triggered or atkSpCountCur == 0) and atkr.potent_new_percentage != -1 and i == atkPotentIndex:
            curAtk.potentRedu = 100

        if (defr.special_triggered or defSpCountCur == 0) and defr.potent_new_percentage != -1 and i == defPotentIndex:
            curAtk.potentRedu = 100

        # damage reductions
        damage_reductions = []
        special_damage_reductions = []

        if curAtk.attackOwner == 0:
            damage_reductions += defr.DR_all_hits_NSP
            special_damage_reductions += defr.DR_all_hits_SP

            if defr.DR_great_aether_SP:
                if curAtk.isConsecutive:
                    special_damage_reductions.append(70 - (defSpCountCur * 10))
                else:
                    special_damage_reductions.append(40 - (defSpCountCur * 10))

            if curAtk.attackNumSelf == 1:
                damage_reductions += defr.DR_first_hit_NSP
                damage_reductions += defr.DR_first_strikes_NSP

            if curAtk.attackNumSelf == 2:
                if atkr.brave:
                    damage_reductions += defr.DR_first_strikes_NSP
                else:
                    damage_reductions += defr.DR_second_strikes_NSP

            if curAtk.attackNumSelf >= 3:
                damage_reductions += defr.DR_second_strikes_NSP
            if curAtk.isConsecutive:
                damage_reductions += defr.DR_consec_strikes_NSP

            if defr.special_triggered and defender.getSpecialType() == "Offense":
                damage_reductions += defr.DR_sp_trigger_next_only_NSP
                defr.DR_sp_trigger_next_only_NSP = []

                special_damage_reductions += defr.DR_sp_trigger_next_only_SP
                defr.DR_sp_trigger_next_only_SP = []

                special_damage_reductions += defr.DR_sp_trigger_next_all_SP_CACHE
                defr.DR_sp_trigger_next_all_SP_CACHE = []

        if curAtk.attackOwner == 1:
            damage_reductions += atkr.DR_all_hits_NSP
            special_damage_reductions += atkr.DR_all_hits_SP

            if atkr.DR_great_aether_SP:
                if curAtk.isConsecutive:
                    special_damage_reductions.append(70 - (atkSpCountCur * 10))
                else:
                    special_damage_reductions.append(40 - (atkSpCountCur * 10))

            if curAtk.attackNumSelf == 1:
                damage_reductions += atkr.DR_first_hit_NSP
                damage_reductions += atkr.DR_first_strikes_NSP

            if curAtk.attackNumSelf == 2:
                if defr.brave:
                    damage_reductions += atkr.DR_first_strikes_NSP
                else:
                    damage_reductions += atkr.DR_second_strikes_NSP

            if curAtk.attackNumSelf >= 3:
                damage_reductions += atkr.DR_second_strikes_NSP
            if curAtk.isConsecutive:
                damage_reductions += atkr.DR_consec_strikes_NSP

            if atkr.special_triggered and attacker.getSpecialType() == "Offense":
                damage_reductions += atkr.DR_sp_trigger_next_only_NSP
                atkr.DR_sp_trigger_next_only_NSP = []

                special_damage_reductions += atkr.DR_sp_trigger_next_only_SP
                atkr.DR_sp_trigger_next_only_SP = []

        # print(damage_reductions)

        # this should've been done at the start of the program
        roles = [attacker, defender]
        effects = [atkSpEffects, defSpEffects]
        stats = [atkStats, defStats]
        checkedDefs = [atkTargetingDefRes, defTargetingDefRes]
        curHPs = [atkHPCur, defHPCur]
        curSpCounts = [atkSpCountCur, defSpCountCur]

        # SpongebobPatrick
        spongebob = curAtk.attackOwner
        patrick = int(not curAtk.attackOwner)

        modifiers = [atkr, defr]

        strikeResult = attack(roles[spongebob], roles[patrick], effects[spongebob], effects[patrick], stats[spongebob],
                              stats[patrick], checkedDefs[spongebob],
                              damage_reductions, special_damage_reductions, curHPs[spongebob], curHPs[patrick],
                              curSpCounts[spongebob], curSpCounts[patrick],
                              modifiers[spongebob], modifiers[patrick], curAtk)

        atkHPCur = strikeResult[spongebob]
        defHPCur = strikeResult[patrick]

        atkSpCountCur = strikeResult[spongebob + 2]
        defSpCountCur = strikeResult[patrick + 2]

        damageDealt = strikeResult[4]
        healthHealed = strikeResult[5]

        curAtk.impl_atk(damageDealt, healthHealed, (atkHPCur, defHPCur), (atkSpCountCur, defSpCountCur))

        # print(strikeResult)

        # I am dead
        if atkHPCur <= 0:
            atkHPCur = 0
            atkAlive = False
            if not is_in_sim: print(attacker.name + " falls.")
            curAtk.is_finisher = True

        if defHPCur <= 0:
            defHPCur = 0
            defAlive = False
            if not is_in_sim: print(defender.name + " falls.")
            curAtk.is_finisher = True

        i += 1  # increment buddy!

    # post combat healing/damage, should move to its own process
    if atkAlive and (atkSelfDmg != 0 or defOtherDmg != 0 or atkPostCombatHealing):
        resultDmg = ((atkSelfDmg + defOtherDmg) - atkPostCombatHealing * int(
            not (Status.DeepWounds in attacker.statusNeg)))
        atkHPCur -= resultDmg
        if resultDmg > 0:
            print(attacker.getName() + " takes " + str(resultDmg) + " damage after combat.")
        else:
            print(attacker.getName() + " heals " + str(resultDmg) + " health after combat.")
        if atkHPCur < 1: atkHPCur = 1
        if atkHPCur > atkStats[0]: atkHPCur = atkStats[0]

    if defAlive and (defSelfDmg != 0 or atkOtherDmg != 0 or defPostCombatHealing):
        resultDmg = ((defSelfDmg + atkOtherDmg) - defPostCombatHealing * int(
            not (Status.DeepWounds in defender.statusNeg)))
        defHPCur -= resultDmg
        if resultDmg > 0:
            print(defender.getName() + " takes " + str(defSelfDmg + atkOtherDmg) + " damage after combat.")
        else:
            print(defender.getName() + " heals " + str(defSelfDmg + atkOtherDmg) + " health after combat.")
        if defHPCur < 1: defHPCur = 1
        if defHPCur > defStats[0]: defHPCur = defStats[0]

    # post combat special incrementation, again move to seperate process
    if "specialSpiralW" in atkSkills and atkr.special_triggered:
        atkPostCombatSpCharge += math.ceil(atkSkills["specialSpiralW"] / 2)

    if "specialSpiralW" in defSkills and defSkills["specialSpiral"] > 1 and defr.special_triggered:
        defPostCombatSpCharge += math.ceil(defSkills["specialSpiralW"] / 2)

    if "specialSpiralS" in atkSkills and atkr.special_triggered:
        atkPostCombatSpCharge += math.ceil(atkSkills["specialSpiralS"] / 2)

    if "specialSpiralS" in defSkills and defSkills["specialSpiral"] > 1 and defr.special_triggered:
        defPostCombatSpCharge += math.ceil(defSkills["specialSpiralS"] / 2)

    if "infiniteSpecial" and atkHPGreaterEqual25Percent and attacker.specialCount == attacker.specialMax:
        atkPostCombatSpCharge += 1

    if "infiniteSpecial" and defHPGreaterEqual25Percent and defender.specialCount == defender.specialMax:
        defPostCombatSpCharge += 1

    if atkAlive: attacker.chargeSpecial(atkPostCombatSpCharge)
    if defAlive: defender.chargeSpecial(defPostCombatSpCharge)

    # here ya go
    if atkAlive:
        for m in atkPostCombatStatusesApplied[0]:
            attacker.inflict(m)

    if defAlive:
        for n in defPostCombatStatusesApplied[0]:
            attacker.inflict(n)

    atkFehMath = min(max(atkStats[ATK] - defStats[atkTargetingDefRes + 3], 0) + atkr.true_all_hits, 99)
    defFehMath = min(max(defStats[ATK] - atkStats[defTargetingDefRes + 3], 0) + defr.true_all_hits, 99)

    atkHitCount = startString2.count("A")
    defHitCount = startString2.count("D")

    return atkHPCur, defHPCur, atkCombatBuffs, defCombatBuffs, wpnAdvHero, oneEffAtk, oneEffDef, attackList, atkFehMath, atkHitCount, defFehMath, defHitCount


# new combat function needs to return the following:
# attack values for all attacks in combat, regardless of a unit's death ✓
# which attack finishes a unit ✓
# FEH Math calculation (have to redo true damage calculation)
# special cooldowns after each attack ✓
# hashmap of post-combat effects (oooo we'll get there don't need now)
# weapon triangle advantage ✓
# combat buffs ✓

# FEH Math
# Atk - Def/Res + True Damage applied for all hits

# function should not deal damage to units/charge special/do post-combat things,
# these will be handled by wherever after the combat function is called

class Attack():
    def __init__(self, attackOwner, isFollowUp, isConsecutive, attackNumSelf, attackNumAll, prevAttack, potentRedu):
        self.attackOwner = attackOwner
        self.isFollowUp = isFollowUp
        self.isConsecutive = isConsecutive
        self.attackNumSelf = attackNumSelf
        self.attackNumAll = attackNumAll
        self.prevAttack = prevAttack

        self.damage = -1
        self.spCharges = (-1, -1)
        self.curHPs = (-1, -1)
        self.healed = -1

        self.potentRedu = potentRedu

        self.is_finisher = False

    def impl_atk(self, damage, healed, spCharges, curHPs):
        self.damage = damage
        self.spCharges = spCharges
        self.curHPs = curHPs
        self.healed = healed


# effects distributed to allies/foes within their combats
# this is a demo, final version should be placed within the map and initialized at the start of game

exRange1 = lambda s: lambda o: abs(s[0] - o[0]) <= 1  # within 3 columns centers on unit
exRange2 = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2  # within 2 spaces
exCondition = lambda s: lambda o: o.hasPenalty()
exEffect = {"atkRein": 5, "defRein": 5}
flowerofease_base = {"atkRein": 3, "defRein": 3, "resRein": 3}
flowerofease_ref = {"atkRein": 4, "defRein": 4, "resRein": 4}


class EffectField():
    def __init__(self, owner, range, condition, affectSelf, affectedSide, effect):
        self.owner = owner
        self.range = range(owner.tile)
        self.condition = condition(owner)
        self.affectSelf = affectSelf
        self.affectedSide = affectedSide  # 0 for same as owner, 1 otherwise
        self.effect = effect


# flowerOfEaseField = EffectField(mirabilis, exRange1, exCondition, False, True, flowerofease_base)

# SPECIALS
daylight = Special("Daylight", "Restores HP = 30% of damage dealt.", {"healSelf": 3}, 3, SpecialType.Offense)
noontime = Special("Noontime", "Restores HP = 30% of damage dealt.", {"healSelf": 3}, 2, SpecialType.Offense)
sol = Special("Sol", "Restores HP = 50% of damage dealt.", {"healSelf": 5}, 3, SpecialType.Offense)
aether = Special("Aether",
                 "Treats foe's Def/Res as if reduced by 50% during combat. Restores HP = half of damage dealt.",
                 {"defReduce": 5, "healSelf": 5}, 5, SpecialType.Offense)

newMoon = Special("New Moon", "Treats foe's Def/Res as if reduced by 30% during combat.", {"defReduce": 3}, 3,
                  SpecialType.Offense)
moonbow = Special("Moonbow", "Treats foe's Def/Res as if reduced by 30% during combat.", {"defReduce": 3}, 2,
                  SpecialType.Offense)
luna = Special("Luna", "Treats foe's Def/Res as if reduced by 50% during combat.", {"defReduce": 5}, 3,
               SpecialType.Offense)
lethality = Special("Lethality",
                    "When Special triggers, treats foe's Def/Res as if reduced by 75% during combat. Disables non-Special skills that \"reduce damage by X%.\"",
                    {"defReduce": 7.5, "spIgnorePercDmgReduc": 0}, 4, SpecialType.Offense)

nightSky = Special("Night Sky", "Boosts damage dealt by 50%.", {"dmgBoost": 5}, 3, SpecialType.Offense)
glimmer = Special("Glimmer", "Boosts damage dealt by 50%.", {"dmgBoost": 5}, 2, SpecialType.Offense)
astra = Special("Astra", "Boosts damage dealt by 150%.", {"dmgBoost": 15}, 4, SpecialType.Offense)

dragonGaze = Special("Dragon Gaze", "Boosts damage by 30% of unit's Atk.", {"atkBoostSp": 3}, 4, SpecialType.Offense)
draconicAura = Special("Draconic Aura", "Boosts damage by 30% of unit's Atk.", {"atkBoostSp": 3}, 3,
                       SpecialType.Offense)
dragonFang = Special("Dragon Fang", "Boosts damage by 50% of unit's Atk.", {"atkBoostSp": 5}, 4, SpecialType.Offense)

lunarFlash = Special("Lunar Flash",
                     "Treats foe’s Def/Res as if reduced by 20% during combat. Boosts damage by 20% of unit's Spd.",
                     {"defReduce": 2, "spdBoostSp": 2}, 2, SpecialType.Offense)

bonfire = Special("Bonfire", "Boosts damage by 50% of unit's Def.", {"defBoostSp": 5}, 3, SpecialType.Offense)
ignis = Special("Ignis", "Boost damage by 80% of unit's Def.", {"defBoostSp": 8}, 4, SpecialType.Offense)

iceberg = Special("Iceberg", "Boosts damage by 50% of unit's Res.", {"resBoostSp": 5}, 3, SpecialType.Offense)
glacies = Special("Glacies", "Boosts damage by 80% of unit's Res.", {"resBoostSp": 8}, 4, SpecialType.Offense)

buckler = Special("Buckler", "Reduces damage from an adjacent foe's attack by 30%.", {"closeShield": 3}, 3,
                  SpecialType.Defense)
pavise = Special("Pavise", "Reduces damage from an adjacent foe's attack by 50%.", {"closeShield": 5}, 3,
                 SpecialType.Defense)
escutcheon = Special("Escutcheon", "Reduces damage from an adjacent foe's attack by 30%.", {"closeShield": 3}, 2,
                     SpecialType.Defense)

holyVestiments = Special("Holy Vestments", "If foe is 2 spaces from unit, reduces damage from foe's attack by 30%.",
                         {"distantShield": 3}, 3, SpecialType.Defense)
sacredCowl = Special("Sacred Cowl", "If foe is 2 spaces from unit, reduces damage from foe's attack by 30%.",
                     {"distantShield": 3}, 2, SpecialType.Defense)
aegis = Special("Aegis", "If foe is 2 spaces from unit, reduces damage from foe's attack by 50%.", {"distantShield": 5},
                3, SpecialType.Defense)

miracle = Special("Miracle", "If unit's HP > 1 and foe would reduce unit's HP to 0, unit survives with 1 HP.",
                  {"miracleSP": 0}, 5, SpecialType.Defense)

# A SKILLS

fury4 = Skill("Fury 4", "Grants Atk/Spd/Def/Res+4. After combat, deals 8 damage to unit.",
              {"atkBoost": 4, "spdBoost": 4, "defBoost": 4, "resBoost": 4, "selfDmg": 8})

# HIGHEST TRIANGLE ADEPT LEVEL USED
# SMALLER LEVELS DO NOT STACK WITH ONE ANOTHER
# ONLY HIGHEST LEVEL USED

svalinnShield = Skill("Svalinn Shield", "Neutralizes \"effective against armored\" bonuses.", {"nullEffArm": 0})
graniShield = Skill("Grani's Shield", "Neutralizes \"effective against cavalry\" bonuses.", {"nullEffCav": 0})
ioteShield = Skill("Iote's Shield", "Neutralizes \"effective against fliers\" bonuses.", {"nullEffFly": 0})

bonusDoubler1 = Skill("Bonus Doubler 1",
                      "Grants bonus to Atk/Spd/Def/Res during combat = 50% of current bonus on each of unit’s stats. Calculates each stat bonus independently.",
                      {"bonusDoublerSk": 1})
bonusDoubler2 = Skill("Bonus Doubler 2",
                      "Grants bonus to Atk/Spd/Def/Res during combat = 75% of current bonus on each of unit’s stats. Calculates each stat bonus independently.",
                      {"bonusDoublerSk": 2})
bonusDoubler3 = Skill("Bonus Doubler 3",
                      "Grants bonus to Atk/Spd/Def/Res during combat = current bonus on each of unit’s stats. Calculates each stat bonus independently.",
                      {"bonusDoublerSk": 3})

sorceryBlade1 = Skill("Sorcery Blade 1",
                      "At start of combat, if unit’s HP = 100% and unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.",
                      {"sorceryBlade": 1})
sorceryBlade2 = Skill("Sorcery Blade 2",
                      "At start of combat, if unit’s HP ≥ 50% and unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.",
                      {"sorceryBlade": 2})
sorceryBlade3 = Skill("Sorcery Blade 3",
                      "At start of combat, if unit is adjacent to a magic ally, calculates damage using the lower of foe’s Def or Res.",
                      {"sorceryBlade": 3})

# B SKILLS

specialSpiral3 = Skill("Special Spiral 3", "I dunno", {"specialSpiralS": 3})

vantage1 = Skill("Vantage 1",
                 "If unit's HP ≤ 25% and foe initiates combat, unit can counterattack before foe's first attack.",
                 {"vantage": 1})
vantage2 = Skill("Vantage 2",
                 "If unit's HP ≤ 50% and foe initiates combat, unit can counterattack before foe's first attack.",
                 {"vantage": 2})
vantage3 = Skill("Vantage 3",
                 "If unit's HP ≤ 75% and foe initiates combat, unit can counterattack before foe's first attack.",
                 {"vantage": 3})

quickRiposte1 = Skill("Quick Riposte 1",
                      "If unit's HP ≥ 90% and foe initiates combat, unit makes a guaranteed follow-up attack.",
                      {"QRS": 1})
quickRiposte2 = Skill("Quick Riposte 2",
                      "If unit's HP ≥ 80% and foe initiates combat, unit makes a guaranteed follow-up attack.",
                      {"QRS": 2})
quickRiposte3 = Skill("Quick Riposte 3",
                      "If unit's HP ≥ 70% and foe initiates combat, unit makes a guaranteed follow-up attack.",
                      {"QRS": 3})

cancelAffinity1 = Skill("Cancel Affinity 1",
                        "Neutralizes all weapon-triangle advantage granted by unit's and foe's skills.",
                        {"cancelTA": 1})
cancelAffinity2 = Skill("Cancel Affinity 2",
                        "Neutralizes weapon-triangle advantage granted by unit's skills. If unit has weapon-triangle disadvantage, neutralizes weapon-triangle advantage granted by foe's skills.",
                        {"cancelTA": 2})
cancelAffinity3 = Skill("Cancel Affinity 3",
                        "Neutralizes weapon-triangle advantage granted by unit's skills. If unit has weapon-triangle disadvantage, reverses weapon-triangle advantage granted by foe's skills.",
                        {"cancelTA": 3})

guard1 = Skill("Guard 1",
               "At start of combat, if unit's HP = 100%, inflicts Special cooldown charge -1 on foe per attack. (Only highest value applied. Does not stack.)",
               {"guardHP": 1})
guard2 = Skill("Guard 2",
               "At start of combat, if unit's HP ≥ 90%, inflicts Special cooldown charge -1 on foe per attack. (Only highest value applied. Does not stack.)",
               {"guardHP": 0.9})
guard3 = Skill("Guard 3",
               "At start of combat, if unit's HP ≥ 80%, inflicts Special cooldown charge -1 on foe per attack. (Only highest value applied. Does not stack.)",
               {"guardHP": 0.8})
guard4 = Skill("Guard 4",
               "At start of combat, if unit's HP ≥ 25%, inflicts Atk-4 and Special cooldown charge -1 on foe per attack during combat (only highest value applied; does not stack) and reduces damage from foe's first attack during combat by 30%.",
               {"guardHP": 0.25, "lullAtk": 4, "reduceFirst": 30})

# C SKILLS

spurRes3 = Skill("Spur Res 3", "Grants Res+4 to adjacent allies during combat.", {"spurRes": 4})
wardCavalry = Skill("Ward Cavalry", "Grants Def/Res+4 to cavalry allies within 2 spaces during combat.", {"ward": 1})
goadArmor = Skill("Goad Armor", "Grants Atk/Spd+4 to armored allies within 2 spaces during combat.", {"goad": 3})

# noah = Hero("Noah", 40, 42, 45, 35, 25, "Sword", 0, marthFalchion, luna, None, None, None)
# mio = Hero("Mio", 38, 39, 47, 27, 29, "BDagger", 0, tacticalBolt, moonbow, None, None, None)

player = Hero("Marth", "E!Marth", 0, "Sword", 0, [41, 45, 47, 33, 27], [50, 80, 90, 55, 40], 5, 165)
enemy = Hero("Lucina", "B!Lucina", 0, "Lance", 0, [41, 34, 36, 27, 19], [50, 60, 60, 45, 35], 30, 165)

player_weapon = Weapon("Hero-King Sword", "Hero-King Sword", "", 16, 1, "Sword", {"slaying": 1, "effDragon": 0}, {})
enemy_weapon = Weapon("Iron Lance", "Iron Lance", "", 6, 1, "Lance", {"shez!": 0}, {})

ragnell = Weapon("Emblem Ragnell", "Emblem Ragnell", "", 16, 1, "Sword", {"slaying": 1, "dCounter": 0, "BIGIKEFAN": 1018}, {})
GREAT_AETHER = Special("Great Aether", "", {"numFoeAtkBoostSp": 4, "AETHER_GREAT": 1018}, 4, SpecialType.Offense)

lodestar_rush = Special("Lodestar Rush", "", {"spdBoostSp": 4, "tempo": 0, "potentFix": 100}, 2, SpecialType.Offense)

player.set_skill(ragnell, WEAPON)
enemy.set_skill(enemy_weapon, WEAPON)

player.set_skill(GREAT_AETHER, SPECIAL)

potent1 = Skill("Potent 1", "", {"potentStrike": 4})
laguz_friend4 = Skill("Laguz Friend 4", "", {"laguz_friend": 4})
defStance = Skill("Thing", "", {"defStance": 3})

player.set_skill(laguz_friend4, BSKILL)
enemy.set_skill(defStance, ASKILL)

player.chargeSpecial(1)

final_result = simulate_combat(player, enemy, 0, 1, 2, [])

#print((final_result[0], final_result[1]))

# alpha.inflict(Status.Panic)
# alpha.inflictStat(ATK,+7)
# omega.inflictStat(RES,-1)
# omega.chargeSpecial(0)

# combatEffects = []

# ATK AND WEAPON SKILLS DO STACK W/ HOW PYTHON MERGES DICTIONARIES
# JUST KEEP IN MIND ONCE YOU GET TO THAT BRIDGE WITH SKILLS NOT MEANT TO STACK

# OR WHAT IF I WANT THAT SOMETIMES >:]