import math
from heapq import nlargest

from hero import *

# CONSTANTS
HP = 0
ATK = 1
SPD = 2
DEF = 3
RES = 4

UNCONDITIONAL = 0
GIVEN_UNIT_ATTACKED = 2


# A set of modifiers that change how combat and attacks work
# One is held by each unit in combat and keeps track of their effects
class HeroModifiers:
    def __init__(self):
        # Exact HP and Special counts at start of combat, before burn damage/healing
        self.start_of_combat_HP: int = -1
        self.start_of_combat_special: int = -1

        # Attack stat preserved before being modified by the weapon triangle
        # Used for calculating special damage
        self.preTriangleAtk: int = 0
        self.preDefenseTerrain: int = 0
        self.preResistTerrain: int = 0

        # Triangle Adept Skill Level (as decimal)
        self.triangle_adept_level = 0

        # Cancel Affinity Level
        # 0 - no effect on TA skills
        # 1 - disable all TA skills
        # 2 - disable self TA skills, disable foe's TA skills if at WP disadvantage
        # 3 - disable self TA skills, reverse foe's TA skills if at WP disadvantage
        self.cancel_affinity_level = 0

        # Attack twice per hit
        self.brave: bool = False

        # Enables defender to attack first
        self.vantage: bool = False
        self.self_desperation: bool = False
        self.other_desperation: bool = False

        # Disable's this unit's skills that change attack ordering (vantage & desperation)
        self.hardy_bearing: bool = False

        # Perform potent follow up
        self.potent_FU = False
        self.potent_new_percentage = -1  # Special-enabled potent percentage increase (Lodestar Rush)

        # Follow-ups
        self.follow_ups_skill = 0  # granted by skills
        self.follow_ups_spd = 0  # granted by speed
        self.follow_up_denials = 0  # granted by skills

        # Null Follow-Up (NFU)
        self.defensive_NFU = False  # Disables skills that guarantee foe's skill-based follow-ups
        self.offensive_NFU = False  # Disable skills that deny self's skill-based follow-ups

        # If special disabled during combat
        self.special_disabled = False

        # Increased/decreased special charge gain per hit
        self.spGainOnAtk = 0  # when self attacks
        self.spLossOnAtk = 0
        self.spGainWhenAtkd = 0  # when self is attacked
        self.spLossWhenAtkd = 0

        # Pre-hit special jumps
        self.sp_charge_first = 0  # before this unit's first attack
        self.sp_charge_FU = 0  # before this unit's first follow-up

        self.sp_charge_foe_first = 0  # before foe's first attack
        self.sp_charge_foe_first_brave = 0  # before foe's first brave attack
        self.sp_charge_foe_first_FU = 0  # before foe's first follow-up attack

        # Disable increased/decreased special charge gain (Tempo)
        self.defensive_tempo = False  # foe +1 charge per attack
        self.offensive_tempo = False  # self -1 charge per attack

        # Charge give charge immediately after first defensive special activation (Negating Fang II)
        self.double_def_sp_charge = False

        # Charge give charge immediately after first offensive special activation (Supreme Astra)
        self.triggered_sp_charge = 0

        # If special has been triggered any time before or during this combat
        self.special_triggered = False

        # Non-special percentage-based damage reduction
        self.DR_all_hits_NSP = []  # present on all hits
        self.DR_first_hit_NSP = []  # present on first hit
        self.DR_first_strikes_NSP = []  # present on first hit (first two if foe has Brave enabled)
        self.DR_second_strikes_NSP = []  # present on follow-up and potent hits
        self.DR_consec_strikes_NSP = []  # present on second hit onwards iff consecutive
        self.DR_sp_trigger_next_only_NSP = []  # present only after first special activation

        # Special percentage-based damage reduction
        self.DR_all_hits_SP = []  # present on all hits
        self.DR_sp_trigger_next_only_SP = []  # present on next hit once per combat
        self.DR_sp_trigger_next_all_SP = []  # present on next hit, can trigger multiple times
        self.DR_sp_trigger_next_all_SP_CACHE = []

        # Armored Beacon/Floe/Blaze, Supreme Heaven, Emblem Ike Ring, etc.
        self.DR_sp_trigger_by_any_special_SP = []  # present after unit or foe's special is ready or triggered

        # DR specific to Great Aether
        self.DR_great_aether_SP = False  # based on special count and if hits are consecutive

        # Stat-scaling Damage Reduction, (SPD, 4) in this array means: grants all hits DR = difference between self and foe's SPD * 4%, (max 40%)
        self.stat_scaling_DR = []

        # Damage reduction reduction (partial DR pierce)
        # Each source of non-special damage reduction is reduced by each value in this array * 100%
        self.damage_reduction_reduction = []

        # Damage reduction piercing (full DR pierce)
        self.sp_pierce_DR = False  # DR pierce on offensive special
        self.pierce_DR_FU = False  # DR pierce on follow-up
        self.always_pierce_DR = False  # DR pierce on any hit
        self.sp_pierce_after_def_sp = False  # DR pierce on next hit after defensive special trigger (laguz friend)
        self.sp_pierce_after_def_sp_CACHE = False # cache to store if the next hit should pierce

        # True damage
        self.true_all_hits = 0  # damage added to all hits
        self.true_first_hit = 0  # damage added on only first hit
        self.true_finish = 0  # added after special is currently ready or has triggered
        self.true_after_foe_first = 0  # added after foe's first attack
        self.true_sp = 0  # added only on offensive special trigger

        self.true_sp_next = 0  # damage added after each special trigger (divine pulse/negating fang)
        self.true_sp_next_CACHE = 0  #

        # An array to easily store true damage given by a particular stat (ex. (20, RES) means "deals damage = 20% of unit's Res")
        self.true_stat_damages = []

        # Same as above, but for using foe's stats for true damage
        self.true_stat_damages_from_foe = []

        # Enables extra true damage and DR piercing based on current HP
        self.resonance = False

        # True damage reduction
        self.TDR_all_hits = 0
        self.TDR_first_strikes = 0
        self.TDR_second_strikes = 0
        self.TDR_on_def_sp = 0

        # Same as true_stat_damages for true damage reduction
        self.TDR_stats = []

        # Niðhöggr
        self.TDR_dmg_taken_cap = 0
        self.TDR_dmg_taken_extra_stacks = 0

        self.reduce_self_sp_damage = 0  # emblem marth

        self.retaliatory_reduced = 0  # enables divine recreation
        self.nonstacking_retaliatory_damage = 0  # divine recreation
        self.stacking_retaliatory_damage = 0  # ice mirror
        self.retaliatory_full_damages = []  # full retaliatory damage values for brash assault/counter roar
        self.retaliatory_full_damages_CACHE = []  # temporarily holds full retaliatory
        self.most_recent_atk = 0  # used in calculating this vvvvv
        self.retaliatory_next = 0  # brash assault/counter roar uses most recent hit's damage

        # no chat, I'm not calling it "precombat damage"
        self.self_burn_damage = 0
        self.foe_burn_damage = 0
        self.capped_foe_burn_damage = 0

        # healing
        self.all_hits_heal = 0
        self.follow_up_heal = 0
        self.finish_mid_combat_heal = 0  # heal applied to all hits granted that special is ready or triggered

        # reduces the effect of deep wounds
        self.deep_wounds_allowance = []
        self.disable_foe_healing = False

        self.surge_heal = 0  # healing when triggering a special

        self.initial_heal = 0  # BoL 4

        # miracle
        self.pseudo_miracle = False
        self.circlet_miracle = False
        self.disable_foe_miracle = False

        # staff
        self.wrathful_staff = False
        self.disable_foe_wrathful = False

        # hexblade
        self.hexblade = False
        self.disable_foe_hexblade = False


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


# Perform a combat between two heroes
def simulate_combat(attacker, defender, is_in_sim, turn, spaces_moved_by_atkr, combat_effects, aoe_triggered, savior_triggered, ar_structs=None, atkHPCur=None, defHPCur=None):

    # Invalid Combat if one unit is dead
    # or if attacker does not have weapon
    if attacker.HPcur <= 0 or defender.HPcur <= 0 or attacker.weapon is None:
        raise Exception("Invalid Combat: One hero is either already dead, or the attacker has no weapon.")

    # who possesses the weapon triangle advantage
    # 0 - attacker
    # 1 - defender
    # -1 - neither
    wpnAdvHero: int = -1

    # lists of attacker/defender's skills & stats
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()
    atkPhantomStats = [0] * 5

    defSkills = defender.getSkills()
    defStats = defender.getStats()
    defPhantomStats = [0] * 5

    atkSpEffects = {}
    defSpEffects = {}

    # stores important modifiers going into combat
    atkr = HeroModifiers()
    defr = HeroModifiers()

    # atk/defHPCur used for forecasts, attacker/defender.HPcur otherwise
    if atkHPCur is None: atkHPCur = attacker.HPcur
    if defHPCur is None: defHPCur = defender.HPcur

    # stores HP value at the start of combat
    atkr.start_of_combat_HP = atkHPCur
    defr.start_of_combat_HP = defHPCur

    # Tracks special count
    atkSpCountCur = attacker.specialCount
    defSpCountCur = defender.specialCount

    # Stores special count value at the start of combat
    atkr.start_of_combat_special = atkSpCountCur
    defr.start_of_combat_special = defSpCountCur

    # Special is counted as triggered if the AOE triggered
    atkr.special_triggered = aoe_triggered

    # Count add Phantom stats
    if "phantomSpd" in atkSkills: atkPhantomStats[SPD] += atkSkills["phantomSpd"]
    if "phantomRes" in atkSkills: atkPhantomStats[RES] += atkSkills["phantomRes"]
    if "phantomSpd" in defSkills: defPhantomStats[SPD] += defSkills["phantomSpd"]
    if "phantomRes" in defSkills: defPhantomStats[RES] += defSkills["phantomRes"]

    # stored temporary buffs (essentially everything)
    atkCombatBuffs = [0] * 5
    defCombatBuffs = [0] * 5

    # Nice convenient methods
    def allies_within_n(unit, tile, n):
        unit_list = tile.unitsWithinNSpaces(n)
        returned_list = []

        for x in unit_list:
            if unit.isAllyOf(x):
                returned_list.append(x)

        return returned_list

    def foes_within_n(unit, tile, n):
        unit_list = tile.unitsWithinNSpaces(n)
        returned_list = []

        for x in unit_list:
            if unit.isEnemyOf(x):
                returned_list.append(x)

        return returned_list

    # CONDITIONS

    # common position-based conditions
    atkAdjacentToAlly = []
    atkAllyWithin2Spaces = []
    atkAllyWithin3Spaces = []
    atkAllyWithin4Spaces = []

    defAdjacentToAlly = []
    defAllyWithin2Spaces = []
    defAllyWithin3Spaces = []
    defAllyWithin4Spaces = []

    atkAllyWithin3RowsCols = []
    defAllyWithin3RowsCols = []

    atkAllAllies = []
    defAllAllies = []

    atkWithin1SpaceOfSupportPartner = False
    atkWithin2SpaceOfSupportPartner = False

    defWithin1SpaceOfSupportPartner = False
    defWithin2SpaceOfSupportPartner = False

    if is_in_sim:
        atkAdjacentToAlly = allies_within_n(attacker, attacker.attacking_tile, 1)
        atkAllyWithin2Spaces = allies_within_n(attacker, attacker.attacking_tile, 2)
        atkAllyWithin3Spaces = allies_within_n(attacker, attacker.attacking_tile, 3)
        atkAllyWithin4Spaces = allies_within_n(attacker, attacker.attacking_tile, 4)

        atkAllAllies = allies_within_n(attacker, attacker.attacking_tile, 25)

        defAdjacentToAlly = allies_within_n(defender, defender.tile, 1)
        defAllyWithin2Spaces = allies_within_n(defender, defender.tile, 2)
        defAllyWithin3Spaces = allies_within_n(defender, defender.tile, 3)
        defAllyWithin4Spaces = allies_within_n(defender, defender.tile, 4)

        defAllAllies = allies_within_n(defender, defender.tile, 25)

        tiles_within_3_col = attacker.attacking_tile.tilesWithinNCols(3)
        tiles_within_3_row = attacker.attacking_tile.tilesWithinNRows(3)
        tiles_within_3_row_or_column = list(set(tiles_within_3_col) | set(tiles_within_3_row))

        for tile in tiles_within_3_row_or_column:
            if tile.hero_on is not None and tile.hero_on.isAllyOf(attacker):
                atkAllyWithin3RowsCols.append(tile.hero_on)

        tiles_within_3_col = defender.tile.tilesWithinNCols(3)
        tiles_within_3_row = defender.tile.tilesWithinNRows(3)
        tiles_within_3_row_or_column = list(set(tiles_within_3_col) | set(tiles_within_3_row))

        for tile in tiles_within_3_row_or_column:
            if tile.hero_on is not None and tile.hero_on.isAllyOf(defender):
                defAllyWithin3RowsCols.append(tile.hero_on)

        # Support partner
        for ally in atkAdjacentToAlly:
            if ally.intName == attacker.allySupport:
                atkWithin1SpaceOfSupportPartner = True

        for ally in atkAllyWithin2Spaces:
            if ally.intName == attacker.allySupport:
                atkWithin2SpaceOfSupportPartner = True

        for ally in defAdjacentToAlly:
            if ally.intName == defender.allySupport:
                defWithin1SpaceOfSupportPartner = True

        for ally in defAllyWithin2Spaces:
            if ally.intName == defender.allySupport:
                defWithin2SpaceOfSupportPartner = True

    atkFoeWithin2Spaces = []  # Includes opposing unit in combat!
    defFoeWithin2Spaces = []  # Includes opposing unit in combat!

    if is_in_sim:
        atkFoeWithin2Spaces = foes_within_n(attacker, attacker.attacking_tile, 2)
        defFoeWithin2Spaces = foes_within_n(defender, defender.tile, 2)

    # Allies of a certain movment type within 2 spaces
    atkInfAlliesWithin2Spaces = []
    atkCavAlliesWithin2Spaces = []
    atkFlyAlliesWithin2Spaces = []
    atkArmAlliesWithin2Spaces = []

    defInfAlliesWithin2Spaces = []
    defCavAlliesWithin2Spaces = []
    defFlyAlliesWithin2Spaces = []
    defArmAlliesWithin2Spaces = []

    atk2SpaceMovementArr = [atkInfAlliesWithin2Spaces, atkCavAlliesWithin2Spaces, atkFlyAlliesWithin2Spaces, atkArmAlliesWithin2Spaces]
    def2SpaceMovementArr = [defInfAlliesWithin2Spaces, defCavAlliesWithin2Spaces, defFlyAlliesWithin2Spaces, defArmAlliesWithin2Spaces]

    for x in atkAllyWithin2Spaces: atk2SpaceMovementArr[x.move].append(x)
    for x in defAllyWithin2Spaces: def2SpaceMovementArr[x.move].append(x)

    # common HP-based conditions
    atkHPGreaterEqual25Percent = atkHPCur / atkStats[HP] >= 0.25
    atkHPGreaterEqual50Percent = atkHPCur / atkStats[HP] >= 0.50
    atkHPGreaterEqual75Percent = atkHPCur / atkStats[HP] >= 0.75
    atkHPEqual100Percent = atkHPCur == atkStats[HP]

    defHPGreaterEqual25Percent = defHPCur / defStats[HP] >= 0.25
    defHPGreaterEqual50Percent = defHPCur / defStats[HP] >= 0.50
    defHPGreaterEqual75Percent = defHPCur / defStats[HP] >= 0.75
    defHPEqual100Percent = defHPCur == defStats[HP]

    # AR Structures
    cur_ar_structs_standing = -1
    cur_ar_structs_destroyed = -1

    VALID_DEF_STRUCTS = ["Fortress", "Bolt Tower", "Tactics Room", "Healing Tower", "Panic Manor",
                         "Catapult", "Duo's Hindrance", "Calling Circle", "Bright Shrine", "Dark Shrine"]

    if ar_structs:
        cur_ar_structs_standing = 0
        cur_ar_structs_destroyed = 0

        for struct in ar_structs:
            if struct.struct_type == 2 and struct.health != 0 and (struct.name in VALID_DEF_STRUCTS or "School" in struct.name):
                cur_ar_structs_standing += 1
            elif struct.struct_type == 2 and struct.health == 0 and (struct.name in VALID_DEF_STRUCTS or "School" in struct.name):
                cur_ar_structs_destroyed += 1



    # HANDLING OF COMBATFIELDS
    # ----------------------------------------------------------

    # disable foe skills (feud effect)
    atkHasFeud = False
    defHasFeud = False

    # Skills that have feud in them:

    # General unconditional feud effect (Used currently for L!Lyn's Swift Mulagir)
    if "within3Feud" in atkSkills and atkAllyWithin3Spaces: defHasFeud = True
    if "within3Feud" in defSkills and defAllyWithin3Spaces: atkHasFeud = True

    # I hate Sylgr
    # These arrays store values when Sylgr user is nearby, but not in combat
    atkYlgrStats = [[], [], [], []]
    defYlgrStats = [[], [], [], []]

    # And now I hate Kitsune Fang too
    atkKadenStats = [[], [], [], []]
    defKadenStats = [[], [], [], []]

    # add effects of CombatFields
    if is_in_sim:

        # Get positioning of either unit
        atkr_x = attacker.attacking_tile.x_coord
        atkr_y = attacker.attacking_tile.y_coord
        atkr_coords = (atkr_x, atkr_y)

        defr_x = defender.tile.x_coord
        defr_y = defender.tile.y_coord
        defr_coords = (defr_x, defr_y)

        # Iterate through all possible combat fields
        for e in combat_effects:

            # If not on canvas (Dead, Cohort)
            if not e.owner.tile:
                continue

            # Owner location
            owner_x = e.owner.tile.x_coord
            owner_y = e.owner.tile.y_coord

            # Correction for forecast involving the attacker's movement
            if e.owner == attacker:
                owner_x = atkr_x
                owner_y = atkr_y

            owner_coords = (owner_x, owner_y)

            targeted_side = int(e.owner.side == e.affectedSide)

            if e.owner.side == attacker.side:
                feud_present = atkHasFeud
            else:
                feud_present = defHasFeud

            if targeted_side == attacker.side:
                coords = atkr_coords
                updated_skills = atkSkills
                afflicted = attacker

                ylgr_stats = atkYlgrStats
                kaden_stats = atkKadenStats
            else:
                coords = defr_coords
                updated_skills = defSkills
                afflicted = defender

                ylgr_stats = defYlgrStats
                kaden_stats = defKadenStats

            condition = e.condition(afflicted)
            in_range = e.range(coords)(owner_coords)
            feud_not_present = not feud_present or e.owner in [attacker, defender] # Disables skill of all foes excluding foe in combat

            if in_range and ((e.owner == afflicted) == False) and condition and feud_not_present:

                # Sylgr (Refine Eff) - Ylgr
                # Sets values in the Ylgr arrays equal to the current bonus of the field owner, not subject to neutralization
                # Only for cases where the field owner is not in combat and is instead only near them
                if "ylgrField_f" in e.effect:
                    if Status.Panic not in e.owner.statusNeg or Status.NullPanic in e.owner.statusPos:
                        i = 1
                        while i < 5:
                            ylgr_stats[i - 1].append(e.owner.buffs[i])
                            i += 1

                elif "kadenField_f" in e.effect:
                    if Status.Panic not in e.owner.statusNeg or Status.NullPanic in e.owner.statusPos:
                        i = 1
                        while i < 5:
                            kaden_stats[i - 1].append(e.owner.buffs[i])
                            i += 1

                else:
                    updated_skills = {x: updated_skills.get(x, 0) + e.effect.get(x, 0) for x in set(updated_skills).union(e.effect)}

            # Add to the dict of skills
            if targeted_side == attacker.side:
                atkSkills = updated_skills
            if targeted_side == defender.side:
                defSkills = updated_skills

    # Unit's special is triggered by unit's attack (Offense, AOE)
    atkSpTriggeredByAttack = attacker.special is not None and attacker.special.type in ["Offensive", "AOE"]
    defSpTriggeredByAttack = defender.special is not None and defender.special.type in ["Offensive", "AOE"]


    # Apply defensive terrain
    if is_in_sim:
        atkDefensiveTerrain = attacker.attacking_tile.is_def_terrain
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

    # apply buffs/debuffs to base stats before combat
    atkStats[ATK] += attacker.buffs[ATK] * AtkPanicFactor + attacker.debuffs[ATK]
    atkStats[SPD] += attacker.buffs[SPD] * AtkPanicFactor + attacker.debuffs[SPD]
    atkStats[DEF] += attacker.buffs[DEF] * AtkPanicFactor + attacker.debuffs[DEF]
    atkStats[RES] += attacker.buffs[RES] * AtkPanicFactor + attacker.debuffs[RES]

    defStats[ATK] += defender.buffs[ATK] * DefPanicFactor + defender.debuffs[ATK]
    defStats[SPD] += defender.buffs[SPD] * DefPanicFactor + defender.debuffs[SPD]
    defStats[DEF] += defender.buffs[DEF] * DefPanicFactor + defender.debuffs[DEF]
    defStats[RES] += defender.buffs[RES] * DefPanicFactor + defender.debuffs[RES]

    # Ignore range (distant/close counter)
    ignore_range = False

    # prevent counterattacks from defender (sweep, flash)
    cannotCounter = False
    disableCannotCounter = False

    # each array within the array holds a set with 4 components:
    # index 0 - what effect is given out? (buffs, debuffs, damage, healing, end turn)
    # index 1 - what is the level of this effect, or what status? (+7 spd buff, 10 damage, Status.Gravity, etc.)
    # index 2 - who is it being given to? (self, only allies, target and their allies, etc.)
    # index 3 - across what area? (only self, adjacent to self, 2 spaces of foe, 3 rows or 3 columns or self, etc.)
    atkPostCombatEffs = [[], [], []]
    defPostCombatEffs = [[], [], []]

    # Which bonuses and penalties are neutralized
    atkBonusesNeutralized = [False] * 5
    defBonusesNeutralized = [False] * 5
    atkPenaltiesNeutralized = [False] * 5
    defPenaltiesNeutralized = [False] * 5

    # SKILLS (LET THE MAYHEM BEGIN)  -----------------------------------------------------------------------------------------------------------------------

    # BUT FIRST, SOME STATUSES
    if Status.Discord in attacker.statusNeg:
        value = min(2 + len(atkAllyWithin2Spaces), 5)
        atkCombatBuffs = [x - value for x in atkCombatBuffs]

    if Status.Discord in defender.statusNeg:
        value = min(2 + len(defAllyWithin2Spaces), 5)
        defCombatBuffs = [x - value for x in defCombatBuffs]

    # Support partner effects
    if atkWithin1SpaceOfSupportPartner and not atkWithin2SpaceOfSupportPartner:
        atkCombatBuffs = [x + 2 for x in atkCombatBuffs]

    if atkWithin2SpaceOfSupportPartner:
        atkCombatBuffs = [x + 1 for x in atkCombatBuffs]

    if defWithin1SpaceOfSupportPartner and not defWithin2SpaceOfSupportPartner:
        defCombatBuffs = [x + 2 for x in defCombatBuffs]

    if defWithin2SpaceOfSupportPartner:
        defCombatBuffs = [x + 1 for x in defCombatBuffs]

    # BLOW SKILLS (Death Blow, Mirror Strike, etc.)
    if "atkBlow" in atkSkills: atkCombatBuffs[ATK] += atkSkills["atkBlow"]
    if "spdBlow" in atkSkills: atkCombatBuffs[SPD] += atkSkills["spdBlow"]
    if "defBlow" in atkSkills: atkCombatBuffs[DEF] += atkSkills["defBlow"]
    if "resBlow" in atkSkills: atkCombatBuffs[RES] += atkSkills["resBlow"]

    # All stats on player initiation
    if "spectrumBlow" in atkSkills:
        atkCombatBuffs = [x + defSkills["spectrumBlow"] for x in atkCombatBuffs]

    # Follow-up denial on player initiation (Sturdy Impact, etc.)
    if "impactDenial" in atkSkills:
        defr.follow_up_denials -= 1

    # STANCE SKILLS (Warding Stance, Steady Posture, etc.)
    if "atkStance" in defSkills: defCombatBuffs[1] += defSkills["atkStance"]
    if "spdStance" in defSkills: defCombatBuffs[2] += defSkills["spdStance"]
    if "defStance" in defSkills: defCombatBuffs[3] += defSkills["defStance"]
    if "resStance" in defSkills: defCombatBuffs[4] += defSkills["resStance"]

    # All stats on enemy initiation
    if "spectrumStance" in defSkills:
        defCombatBuffs = [x + defSkills["spectrumStance"] for x in defCombatBuffs]

    # SPUR / DRIVE / GOAD / WARD SKILLS
    if "spurAtk_f" in atkSkills: atkCombatBuffs[ATK] += atkSkills["spurAtk_f"]
    if "spurSpd_f" in atkSkills: atkCombatBuffs[SPD] += atkSkills["spurSpd_f"]
    if "spurDef_f" in atkSkills: atkCombatBuffs[DEF] += atkSkills["spurDef_f"]
    if "spurRes_f" in atkSkills: atkCombatBuffs[RES] += atkSkills["spurRes_f"]

    if "spurAtk_f" in defSkills: defCombatBuffs[ATK] += defSkills["spurAtk_f"]
    if "spurSpd_f" in defSkills: defCombatBuffs[SPD] += defSkills["spurSpd_f"]
    if "spurDef_f" in defSkills: defCombatBuffs[DEF] += defSkills["spurDef_f"]
    if "spurRes_f" in defSkills: defCombatBuffs[RES] += defSkills["spurRes_f"]

    if "driveAtk_f" in atkSkills: atkCombatBuffs[ATK] += atkSkills["driveAtk_f"]
    if "driveSpd_f" in atkSkills: atkCombatBuffs[SPD] += atkSkills["driveSpd_f"]
    if "driveDef_f" in atkSkills: atkCombatBuffs[DEF] += atkSkills["driveDef_f"]
    if "driveRes_f" in atkSkills: atkCombatBuffs[RES] += atkSkills["driveRes_f"]

    if "driveAtk_f" in defSkills: defCombatBuffs[ATK] += defSkills["driveAtk_f"]
    if "driveSpd_f" in defSkills: defCombatBuffs[SPD] += defSkills["driveSpd_f"]
    if "driveDef_f" in defSkills: defCombatBuffs[DEF] += defSkills["driveDef_f"]
    if "driveRes_f" in defSkills: defCombatBuffs[RES] += defSkills["driveRes_f"]

    # Null penalties given out via ally
    if "driveNullPenalties" in atkSkills: atkPenaltiesNeutralized = [True] * 5
    if "driveNullPenalties" in defSkills: defPenaltiesNeutralized = [True] * 5

    # Joint Drive Skills
    if atkAllyWithin2Spaces:
        if "jointAtk" in atkSkills: atkCombatBuffs[ATK] += 4
        if "jointSpd" in atkSkills: atkCombatBuffs[SPD] += 4
        if "jointDef" in atkSkills: atkCombatBuffs[DEF] += 4
        if "jointRes" in atkSkills: atkCombatBuffs[RES] += 4

    if defAllyWithin2Spaces:
        if "jointAtk" in defSkills: defCombatBuffs[ATK] += 4
        if "jointSpd" in defSkills: defCombatBuffs[SPD] += 4
        if "jointDef" in defSkills: defCombatBuffs[DEF] += 4
        if "jointRes" in defSkills: defCombatBuffs[RES] += 4

    # Goad and Ward skills, given to only certain types of movement per CombatFields
    if "goad_f" in atkSkills:
        atkCombatBuffs[ATK] += atkSkills["goad_f"]
        atkCombatBuffs[SPD] += atkSkills["goad_f"]

    if "goad_f" in defSkills:
        defCombatBuffs[ATK] += defSkills["goad_f"]
        defCombatBuffs[SPD] += defSkills["goad_f"]

    if "ward_f" in atkSkills:
        atkCombatBuffs[ATK] += atkSkills["ward_f"]
        atkCombatBuffs[SPD] += atkSkills["ward_f"]

    if "ward_f" in defSkills:
        defCombatBuffs[ATK] += defSkills["ward_f"]
        defCombatBuffs[SPD] += defSkills["ward_f"]

    # LULL SKILLS
    if "lullAtk" in atkSkills:
        defCombatBuffs[ATK] -= atkSkills["lullAtk"]
        defBonusesNeutralized[ATK] = True

    if "lullSpd" in atkSkills:
        defCombatBuffs[SPD] -= atkSkills["lullSpd"]
        defBonusesNeutralized[SPD] = True

    if "lullDef" in atkSkills:
        defCombatBuffs[DEF] -= atkSkills["lullDef"]
        defBonusesNeutralized[DEF] = True

    if "lullRes" in atkSkills:
        defCombatBuffs[RES] -= atkSkills["lullRes"]
        defBonusesNeutralized[RES] = True

    if "lullAtk" in defSkills:
        atkCombatBuffs[ATK] -= defSkills["lullAtk"]
        atkBonusesNeutralized[ATK] = True

    if "lullSpd" in defSkills:
        atkCombatBuffs[SPD] -= defSkills["lullSpd"]
        atkBonusesNeutralized[SPD] = True

    if "lullDef" in defSkills:
        atkCombatBuffs[DEF] -= defSkills["lullDef"]
        atkBonusesNeutralized[DEF] = True

    if "lullRes" in defSkills:
        atkCombatBuffs[RES] -= defSkills["lullRes"]
        atkBonusesNeutralized[RES] = True

    # BOOST SKILLS
    if "fireBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[ATK] += atkSkills["fireBoost"] * 2
    if "windBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[SPD] += atkSkills["windBoost"] * 2
    if "earthBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[DEF] += atkSkills["earthBoost"] * 2
    if "waterBoost" in atkSkills and atkHPCur >= defHPCur + 3: atkCombatBuffs[RES] += atkSkills["waterBoost"] * 2

    if "fireBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[ATK] += defSkills["fireBoost"] * 2
    if "windBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[SPD] += defSkills["windBoost"] * 2
    if "earthBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[DEF] += defSkills["earthBoost"] * 2
    if "waterBoost" in defSkills and defHPCur >= atkHPCur + 3: defCombatBuffs[RES] += defSkills["waterBoost"] * 2

    # BRAZEN SKILLS
    if "brazenAtk" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[ATK] += atkSkills["brazenAtk"]
    if "brazenSpd" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[SPD] += atkSkills["brazenSpd"]
    if "brazenDef" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[DEF] += atkSkills["brazenDef"]
    if "brazenRes" in atkSkills and atkHPCur / atkStats[HP] <= 0.8: atkCombatBuffs[RES] += atkSkills["brazenRes"]

    if "brazenAtk" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[ATK] += defSkills["brazenAtk"]
    if "brazenSpd" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[SPD] += defSkills["brazenSpd"]
    if "brazenDef" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[DEF] += defSkills["brazenDef"]
    if "brazenRes" in defSkills and defHPCur / defStats[HP] <= 0.8: defCombatBuffs[RES] += defSkills["brazenRes"]

    # BOND SKILLS
    if "atkBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[ATK] += atkSkills["atkBond"]
    if "spdBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[SPD] += atkSkills["spdBond"]
    if "defBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[DEF] += atkSkills["defBond"]
    if "resBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs[RES] += atkSkills["resBond"]

    if "atkBond" in defSkills and defAdjacentToAlly: defCombatBuffs[ATK] += defSkills["atkBond"]
    if "spdBond" in defSkills and defAdjacentToAlly: defCombatBuffs[SPD] += defSkills["spdBond"]
    if "defBond" in defSkills and defAdjacentToAlly: defCombatBuffs[DEF] += defSkills["defBond"]
    if "resBond" in defSkills and defAdjacentToAlly: defCombatBuffs[RES] += defSkills["resBond"]

    if "spectrumBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs = [x + atkSkills["spectrumBond"] for x in atkCombatBuffs]
    if "spectrumBond" in defSkills and defAdjacentToAlly: defCombatBuffs = [x + defSkills["spectrumBond"] for x in defCombatBuffs]

    # Penalty Neutralization from Tier 4 Bond Skills
    if "ABPenalty" in atkSkills and atkAdjacentToAlly: atkPenaltiesNeutralized[ATK] = True
    if "SBPenalty" in atkSkills and atkAdjacentToAlly: atkPenaltiesNeutralized[SPD] = True
    if "DBPenalty" in atkSkills and atkAdjacentToAlly: atkPenaltiesNeutralized[DEF] = True
    if "RBPenalty" in atkSkills and atkAdjacentToAlly: atkPenaltiesNeutralized[RES] = True

    if "ABPenalty" in defSkills and defAdjacentToAlly: defPenaltiesNeutralized[ATK] = True
    if "SBPenalty" in defSkills and defAdjacentToAlly: defPenaltiesNeutralized[SPD] = True
    if "DBPenalty" in defSkills and defAdjacentToAlly: defPenaltiesNeutralized[DEF] = True
    if "RBPenalty" in defSkills and defAdjacentToAlly: defPenaltiesNeutralized[RES] = True

    # SOLO SKILLS
    if "atkSolo" in atkSkills and not atkAdjacentToAlly: atkCombatBuffs[ATK] += atkSkills["atkSolo"]
    if "spdSolo" in atkSkills and not atkAdjacentToAlly: atkCombatBuffs[SPD] += atkSkills["spdSolo"]
    if "defSolo" in atkSkills and not atkAdjacentToAlly: atkCombatBuffs[DEF] += atkSkills["defSolo"]
    if "resSolo" in atkSkills and not atkAdjacentToAlly: atkCombatBuffs[RES] += atkSkills["resSolo"]

    if "atkSolo" in defSkills and not defAdjacentToAlly: defCombatBuffs[ATK] += defSkills["atkSolo"]
    if "spdSolo" in defSkills and not defAdjacentToAlly: defCombatBuffs[SPD] += defSkills["spdSolo"]
    if "defSolo" in defSkills and not defAdjacentToAlly: defCombatBuffs[DEF] += defSkills["defSolo"]
    if "resSolo" in defSkills and not defAdjacentToAlly: defCombatBuffs[RES] += defSkills["resSolo"]

    if "spectrumSolo" in atkSkills and not atkAdjacentToAlly: atkCombatBuffs = [x + atkSkills["spectrumSolo"] for x in atkCombatBuffs]
    if "spectrumSolo" in defSkills and not defAdjacentToAlly: defCombatBuffs = [x + defSkills["spectrumSolo"] for x in defCombatBuffs]

    # PUSH SKILLS
    if "atkPush" in atkSkills and atkHPEqual100Percent: atkCombatBuffs[ATK] += atkSkills["atkPush"]
    if "spdPush" in atkSkills and atkHPEqual100Percent: atkCombatBuffs[ATK] += atkSkills["spdPush"]
    if "defPush" in atkSkills and atkHPEqual100Percent: atkCombatBuffs[ATK] += atkSkills["defPush"]
    if "resPush" in atkSkills and atkHPEqual100Percent: atkCombatBuffs[ATK] += atkSkills["resPush"]

    if "atkPush" in defSkills and defHPEqual100Percent: defCombatBuffs[ATK] += defSkills["atkPush"]
    if "spdPush" in defSkills and defHPEqual100Percent: defCombatBuffs[ATK] += defSkills["spdPush"]
    if "defPush" in defSkills and defHPEqual100Percent: defCombatBuffs[ATK] += defSkills["defPush"]
    if "resPush" in defSkills and defHPEqual100Percent: defCombatBuffs[ATK] += defSkills["resPush"]

    if "pushDmg" in atkSkills and atkHPEqual100Percent: atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 1, "self", "one"))
    if "pushDmg" in defSkills and defHPEqual100Percent: defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 1, "self", "one"))

    if "atkPush4" in atkSkills and atkHPGreaterEqual25Percent: atkCombatBuffs[ATK] += 7
    if "spdPush4" in atkSkills and atkHPGreaterEqual25Percent: atkCombatBuffs[SPD] += 7
    if "defPush4" in atkSkills and atkHPGreaterEqual25Percent: atkCombatBuffs[DEF] += 7
    if "resPush4" in atkSkills and atkHPGreaterEqual25Percent: atkCombatBuffs[RES] += 7

    if "atkPush4" in defSkills and defHPGreaterEqual25Percent: defCombatBuffs[ATK] += 7
    if "spdPush4" in defSkills and defHPGreaterEqual25Percent: defCombatBuffs[SPD] += 7
    if "defPush4" in defSkills and defHPGreaterEqual25Percent: defCombatBuffs[DEF] += 7
    if "resPush4" in defSkills and defHPGreaterEqual25Percent: defCombatBuffs[RES] += 7

    if "pushDmgPlus" in atkSkills and atkHPGreaterEqual25Percent: atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 5, "self", "one"))
    if "pushDmgPlus" in defSkills and defHPGreaterEqual25Percent: defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 5, "self", "one"))

    # FORM SKILLS
    if "atkForm" in atkSkills and atkAllyWithin2Spaces:
        if atkSkills["atkForm"] == 1: atkCombatBuffs[ATK] += min(len(atkAllyWithin2Spaces), 3)
        elif atkSkills["atkForm"] == 2: atkCombatBuffs[ATK] += min(len(atkAllyWithin2Spaces) + 2, 5)
        elif atkSkills["atkForm"] == 3: atkCombatBuffs[ATK] += min(2 * len(atkAllyWithin2Spaces) + 1, 7)

    if "spdForm" in atkSkills and atkAllyWithin2Spaces:
        if atkSkills["spdForm"] == 1: atkCombatBuffs[SPD] += min(len(atkAllyWithin2Spaces), 3)
        elif atkSkills["spdForm"] == 2: atkCombatBuffs[SPD] += min(len(atkAllyWithin2Spaces) + 2, 5)
        elif atkSkills["spdForm"] == 3: atkCombatBuffs[SPD] += min(2 * len(atkAllyWithin2Spaces) + 1, 7)

    if "defForm" in atkSkills and atkAllyWithin2Spaces:
        if atkSkills["defForm"] == 1: atkCombatBuffs[DEF] += min(len(atkAllyWithin2Spaces), 3)
        elif atkSkills["defForm"] == 2: atkCombatBuffs[DEF] += min(len(atkAllyWithin2Spaces) + 2, 5)
        elif atkSkills["defForm"] == 3: atkCombatBuffs[DEF] += min(2 * len(atkAllyWithin2Spaces) + 1, 7)

    if "resForm" in atkSkills and atkAllyWithin2Spaces:
        if atkSkills["resForm"] == 1: atkCombatBuffs[RES] += min(len(atkAllyWithin2Spaces), 3)
        elif atkSkills["resForm"] == 2: atkCombatBuffs[RES] += min(len(atkAllyWithin2Spaces) + 2, 5)
        elif atkSkills["resForm"] == 3: atkCombatBuffs[RES] += min(2 * len(atkAllyWithin2Spaces) + 1, 7)

    if "atkForm" in defSkills and defAllyWithin2Spaces:
        if defSkills["atkForm"] == 1: defCombatBuffs[ATK] += min(len(defAllyWithin2Spaces), 3)
        elif defSkills["atkForm"] == 2: defCombatBuffs[ATK] += min(len(defAllyWithin2Spaces) + 2, 5)
        elif defSkills["atkForm"] == 3: defCombatBuffs[ATK] += min(2 * len(defAllyWithin2Spaces) + 1, 7)

    if "spdForm" in defSkills and defAllyWithin2Spaces:
        if defSkills["spdForm"] == 1: defCombatBuffs[SPD] += min(len(defAllyWithin2Spaces), 3)
        elif defSkills["spdForm"] == 2: defCombatBuffs[SPD] += min(len(defAllyWithin2Spaces) + 2, 5)
        elif defSkills["spdForm"] == 3: defCombatBuffs[SPD] += min(2 * len(defAllyWithin2Spaces) + 1, 7)

    if "defForm" in defSkills and defAllyWithin2Spaces:
        if defSkills["defForm"] == 1: defCombatBuffs[DEF] += min(len(defAllyWithin2Spaces), 3)
        elif defSkills["defForm"] == 2: defCombatBuffs[DEF] += min(len(defAllyWithin2Spaces) + 2, 5)
        elif defSkills["defForm"] == 3: defCombatBuffs[DEF] += min(2 * len(defAllyWithin2Spaces) + 1, 7)

    if "resForm" in defSkills and defAllyWithin2Spaces:
        if defSkills["resForm"] == 1: defCombatBuffs[RES] += min(len(defAllyWithin2Spaces), 3)
        elif defSkills["resForm"] == 2: defCombatBuffs[RES] += min(len(defAllyWithin2Spaces) + 2, 5)
        elif defSkills["resForm"] == 3: defCombatBuffs[RES] += min(2 * len(defAllyWithin2Spaces) + 1, 7)

    # REIN SKILLS
    if "atkRein_f" in atkSkills: atkCombatBuffs[ATK] -= atkSkills["atkRein_f"]
    if "spdRein_f" in atkSkills: atkCombatBuffs[SPD] -= atkSkills["spdRein_f"]
    if "defRein_f" in atkSkills: atkCombatBuffs[DEF] -= atkSkills["defRein_f"]
    if "resRein_f" in atkSkills: atkCombatBuffs[RES] -= atkSkills["resRein_f"]

    if "atkRein_f" in defSkills: defCombatBuffs[ATK] -= defSkills["atkRein_f"]
    if "spdRein_f" in defSkills: defCombatBuffs[SPD] -= defSkills["spdRein_f"]
    if "defRein_f" in defSkills: defCombatBuffs[DEF] -= defSkills["defRein_f"]
    if "resRein_f" in defSkills: defCombatBuffs[RES] -= defSkills["resRein_f"]

    # CRUX SKILLS
    if "spdRC_f" in atkSkills: atkCombatBuffs[SPD] -= atkSkills["spdRC_f"]
    if "defRC_f" in atkSkills: atkCombatBuffs[DEF] -= atkSkills["defRC_f"]

    if "spdRC_f" in defSkills: defCombatBuffs[SPD] -= defSkills["spdRC_f"]
    if "defRC_f" in defSkills: defCombatBuffs[DEF] -= defSkills["defRC_f"]

    if "cruxField_f" in atkSkills:
        defr.follow_ups_skill += atkSkills["cruxField_f"]

    if "cruxField_f" in defSkills:
        atkr.follow_ups_skill += defSkills["cruxField_f"]

    # CLASH SKILLS
    if "atkClash" in atkSkills and spaces_moved_by_atkr > 0:
        atkCombatBuffs[ATK] += min(atkSkills["atkClash"], spaces_moved_by_atkr) + min(2 * atkSkills["atkClash"] - 1, 6)

    if "spdClash" in atkSkills and spaces_moved_by_atkr > 0:
        atkCombatBuffs[SPD] += min(atkSkills["spdClash"], spaces_moved_by_atkr) + min(2 * atkSkills["spdClash"] - 1, 6)

    if "defClash" in atkSkills and spaces_moved_by_atkr > 0:
        atkCombatBuffs[DEF] += min(atkSkills["defClash"], spaces_moved_by_atkr) + min(2 * atkSkills["defClash"] - 1, 6)

    if "atkClash" in defSkills and spaces_moved_by_atkr > 0:
        defCombatBuffs[ATK] += min(defSkills["atkClash"],spaces_moved_by_atkr) + min(2 * defSkills["atkClash"] - 1, 6)

    if "spdClash" in defSkills and spaces_moved_by_atkr > 0:
        defCombatBuffs[SPD] += min(defSkills["spdClash"],spaces_moved_by_atkr) + min(2 * defSkills["spdClash"] - 1, 6)

    if "defClash" in defSkills and spaces_moved_by_atkr > 0:
        defCombatBuffs[DEF] += min(defSkills["defClash"],spaces_moved_by_atkr) + min(2 * defSkills["defClash"] - 1, 6)

    # EXCEL SKILLS
    if "atk_spd_dashing_defense" in atkSkills:
        if spaces_moved_by_atkr > 0:
            atkr.TDR_all_hits += 3 * min(spaces_moved_by_atkr, 4)
        if defSpTriggeredByAttack:
            atkr.TDR_all_hits += 3 * min(spaces_moved_by_atkr, 4) # revise

    if "atk_spd_dashing_defense" in defSkills:
        if atkSpTriggeredByAttack:
            atkr.TDR_all_hits += 3 * min(spaces_moved_by_atkr, 4)

    # FINISH SKILLS
    if "atkFinish" in atkSkills and atkAllyWithin3Spaces: atkCombatBuffs[ATK] += min(atkSkills["atkFinish"] * 2, 7)
    if "spdFinish" in atkSkills and atkAllyWithin3Spaces: atkCombatBuffs[SPD] += min(atkSkills["spdFinish"] * 2, 7)
    if "defFinish" in atkSkills and atkAllyWithin3Spaces: atkCombatBuffs[DEF] += min(atkSkills["defFinish"] * 2, 7)
    if "resFinish" in atkSkills and atkAllyWithin3Spaces: atkCombatBuffs[RES] += min(atkSkills["resFinish"] * 2, 7)

    if "finishDmg" in atkSkills and atkAllyWithin3Spaces: atkr.true_finish += atkSkills["finishDmg"]
    if "finishHeal" in atkSkills and atkAllyWithin3Spaces: atkr.finish_mid_combat_heal += 7

    if "atkFinish" in defSkills and defAllyWithin3Spaces: defCombatBuffs[ATK] += min(defSkills["atkFinish"] * 2, 7)
    if "spdFinish" in defSkills and defAllyWithin3Spaces: defCombatBuffs[SPD] += min(defSkills["spdFinish"] * 2, 7)
    if "defFinish" in defSkills and defAllyWithin3Spaces: defCombatBuffs[DEF] += min(defSkills["defFinish"] * 2, 7)
    if "resFinish" in defSkills and defAllyWithin3Spaces: defCombatBuffs[RES] += min(defSkills["resFinish"] * 2, 7)

    if "finishDmg" in defSkills and defAllyWithin3Spaces: defr.true_finish += defSkills["finishDmg"]
    if "finishHeal" in defSkills and defAllyWithin3Spaces: defr.finish_mid_combat_heal += 7

    # (PREMIUM) WAVE SKILLS
    if "premiumEvenRes" in atkSkills and turn % 2 == 0: atkCombatBuffs[RES] += 6
    if "premiumEvenRes" in defSkills and turn % 2 == 0: defCombatBuffs[RES] += 6

    # AR SKILLS
    AR_STRUCT_STATS = {
        ">=5": {1: 4, 2: 7, 3: 10, 4: 11},
        "4": {1: 3, 2: 5, 3: 7, 4: 7},
        "3": {1: 2, 2: 3, 3: 4, 4: 3},
        "<=2": {1: 1, 2: 1, 3: 1, 4: 3}
    }

    if cur_ar_structs_standing >= 5:
        ard_str = ">=5"
    elif cur_ar_structs_standing == 4:
        ard_str = "4"
    elif cur_ar_structs_standing == 3:
        ard_str = "3"
    else:
        ard_str = "<=2"

    if cur_ar_structs_destroyed >= 5:
        aro_str = ">=5"
    elif cur_ar_structs_destroyed == 4:
        aro_str = "4"
    elif cur_ar_structs_destroyed == 3:
        aro_str = "3"
    else:
        aro_str = "<=2"

    # AR-D SKILLS
    if cur_ar_structs_standing != -1 and attacker.side == 1:
        if "atkARD" in atkSkills: atkCombatBuffs[ATK] += AR_STRUCT_STATS[ard_str][atkSkills["atkARD"]]
        if "spdARD" in atkSkills: atkCombatBuffs[ATK] += AR_STRUCT_STATS[ard_str][atkSkills["spdARD"]]
        if "defARD" in atkSkills: atkCombatBuffs[ATK] += AR_STRUCT_STATS[ard_str][atkSkills["defARD"]]
        if "resARD" in atkSkills: atkCombatBuffs[ATK] += AR_STRUCT_STATS[ard_str][atkSkills["resARD"]]

    if cur_ar_structs_standing != -1 and defender.side == 1:
        if "atkARD" in defSkills: defCombatBuffs[ATK] += AR_STRUCT_STATS[ard_str][defSkills["atkARD"]]
        if "spdARD" in defSkills: defCombatBuffs[ATK] += AR_STRUCT_STATS[ard_str][defSkills["spdARD"]]
        if "defARD" in defSkills: defCombatBuffs[ATK] += AR_STRUCT_STATS[ard_str][defSkills["defARD"]]
        if "resARD" in defSkills: defCombatBuffs[ATK] += AR_STRUCT_STATS[ard_str][defSkills["resARD"]]

    # AR-O Skills
    if cur_ar_structs_destroyed != -1 and attacker.side == 0:
        if "atkARO" in atkSkills: atkCombatBuffs[ATK] += AR_STRUCT_STATS[aro_str][atkSkills["atkARD"]]
        if "spdARO" in atkSkills: atkCombatBuffs[ATK] += AR_STRUCT_STATS[aro_str][atkSkills["spdARD"]]
        if "defARO" in atkSkills: atkCombatBuffs[ATK] += AR_STRUCT_STATS[aro_str][atkSkills["defARD"]]
        if "resARO" in atkSkills: atkCombatBuffs[ATK] += AR_STRUCT_STATS[aro_str][atkSkills["resARD"]]

    if cur_ar_structs_destroyed != -1 and defender.side == 0:
        if "atkARO" in defSkills: defCombatBuffs[ATK] += AR_STRUCT_STATS[aro_str][defSkills["atkARD"]]
        if "spdARO" in defSkills: defCombatBuffs[ATK] += AR_STRUCT_STATS[aro_str][defSkills["spdARD"]]
        if "defARO" in defSkills: defCombatBuffs[ATK] += AR_STRUCT_STATS[aro_str][defSkills["defARD"]]
        if "resARO" in defSkills: defCombatBuffs[ATK] += AR_STRUCT_STATS[aro_str][defSkills["resARD"]]

    # START OF UNIT-EXCLUSIVE WEAPONS/SKILLS

    # Base - Unrefined weapon
    # Refined Base - Updated base effect granted for refining a weapon in any way
    # Refined Eff - Added effect added by choosing the Effect refine

    # Binding Shield - L!Marth
    if "bindingShield" in atkSkills and defender.wpnType in DRAGON_WEAPONS:
        atkr.follow_ups_skill += 1
        defr.follow_up_denials -= 1
        cannotCounter = True

    if "bindingShield" in defSkills and attacker.wpnType in DRAGON_WEAPONS:
        defr.follow_ups_skill += 1
        atkr.follow_up_denials -= 1

    # Genesis Falchion (unsorted, does not work)
    if "SEGAAAA" in atkSkills or "nintenesis" in atkSkills:
        map(lambda x: x + 5, atkCombatBuffs)

    if ("SEGAAAA" in defSkills or "nintenesis" in defSkills) and defAllyWithin2Spaces:
        map(lambda x: x + 5, defCombatBuffs)

    if "denesis" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.DR_first_strikes_NSP.append(40)
        atkCombatBuffs[1] += 5  # + highest atk bonus on self/allies within 2 spaces
        # and the rest of them

    if "denesis" in defSkills and defHPGreaterEqual25Percent:
        defr.DR_first_strikes_NSP.append(40)
        defCombatBuffs[1] += 5  # + highest atk bonus on self/allies within 2 spaces
        # and the rest of them

    # Extra Effects within Potent
    if "potentExtras" in atkSkills:
        if atkSkills["potentExtras"] == 4:
            defCombatBuffs[SPD] -= 4
            defCombatBuffs[DEF] -= 4

        if atkSkills["potentExtras"] > 1:
            atkr.DR_all_hits_NSP.append((atkSkills["potentExtras"] - 1) * 10)

    if "caedaVantage" in defSkills and (attacker.wpnType in ["Sword", "Lance", "Axe", "CBow"] or attacker.move == 3 or defHPCur / defStats[0] <= 0.75):
        defr.vantage = True

    # Pure-Wing Spear (Base) - X!Caeda
    if "pureWing" in atkSkills and atkAllyWithin3Spaces:
        Y = min(atkAllyWithin3Spaces * 3 + 5, 14)
        atkCombatBuffs = [x + Y for x in atkCombatBuffs]
        atkr.damage_reduction_reduction.append(50)
        atkr.DR_all_hits_NSP.append(30)
        atkr.all_hits_heal += 7
        if defender.move == 3 or attacker.move == 1:
            atkr.all_hits_heal += 7

    # Breath of Fog (Refine Eff) - Y!Tiki/A!Tiki
    if "tikiBoost" in atkSkills:
        if any(ally.wpnType == "Sword" or ally.wpnType in DRAGON_WEAPONS for ally in atkAllyWithin2Spaces):
            atkCombatBuffs[ATK] += 5
            atkCombatBuffs[DEF] += 5

    if "tikiBoost" in defSkills:
        if any(ally.wpnType == "Sword" or ally.wpnType in DRAGON_WEAPONS for ally in defAllyWithin2Spaces):
            defCombatBuffs[ATK] += 5
            defCombatBuffs[DEF] += 5

    # Summer's Breath (Refine Base)
    if "SUTikiBoost" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.spGainWhenAtkd += 1
        atkr.spGainOnAtk += 1

    if "SUTikiBoost" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.spGainWhenAtkd += 1
        defr.spGainOnAtk += 1

    # Summer's Breath (Refine Eff)
    if "SUTikiDamage" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "SUTikiDamage" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Veteran Lance (Base) - Jagen
    if "old" in atkSkills and defHPCur / defStats[HP] >= 0.70:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5

    if "old" in defSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5

    # Stalwart Sword (Base) - Draug
    if "draugBlade" in defSkills:
        atkCombatBuffs[ATK] -= 6

    # Stalwart Sword (Refine Eff) - Draug
    if "guardraug" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkPenaltiesNeutralized[ATK] = True
        atkPenaltiesNeutralized[DEF] = True

    if "guardraug" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        defPenaltiesNeutralized[ATK] = True
        defPenaltiesNeutralized[DEF] = True

    # Devil Axe (Base) - Barst
    if "devilAxe" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
    if "devilAxe" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Parthia (Refine Base) - Jeorge
    if "parthiaRedu" in atkSkills and defender.wpnType in TOME_WEAPONS:
        atkr.DR_first_hit_NSP.append(30)

    if "parthiaRedu" in defSkills and attacker.wpnType in TOME_WEAPONS:
        defr.DR_first_hit_NSP.append(30)

    # Parthia (Refine Eff) - Jeorge
    if "parthia2RangeBoost" in atkSkills and defender.wpnType in RANGED_WEAPONS:
        atkCombatBuffs[ATK] += 6

    if "parthia2RangeBoost" in defSkills and attacker.wpnType in RANGED_WEAPONS:
        defCombatBuffs[ATK] += 6

    # Aura (Linde) / Excalibur (Merric)
    if "lindeBoost" in atkSkills:
        if any(ally.wpnType in TOME_WEAPONS or ally.wpnType == "Staff" for ally in atkAllyWithin2Spaces):
            atkCombatBuffs[ATK] += 5
            atkCombatBuffs[SPD] += 5

    if "lindeBoost" in defSkills:
        if any(ally.wpnType in TOME_WEAPONS or ally.wpnType == "Staff" for ally in defAllyWithin2Spaces):
            defCombatBuffs[ATK] += 5
            defCombatBuffs[SPD] += 5

    # Dark Aura (Linde/Delthea)
    if "darkAuraBoost" in atkSkills:
        if any(ally.wpnType in MELEE_WEAPONS for ally in atkAllyWithin2Spaces):
            atkCombatBuffs[ATK] += 5
            atkCombatBuffs[SPD] += 5

    if "darkAuraBoost" in defSkills:
        if any(ally.wpnType in MELEE_WEAPONS for ally in defAllyWithin2Spaces):
            defCombatBuffs[ATK] += 5
            defCombatBuffs[SPD] += 5

    # Pegasus Sisters (Palla, Catria, Est)
    if "triangleAtk" in atkSkills and atkFlyAlliesWithin2Spaces >= 2:
        atkCombatBuffs = [x + 3 for x in atkCombatBuffs]
        atkr.brave = True

    if "triangleAtk" in defSkills and defFlyAlliesWithin2Spaces >= 2:
        defCombatBuffs = [x + 3 for x in defCombatBuffs]

    # Huginn's Egg (Base Refine) - SP!Catria
    if "catriaDualChill" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "catriaDualChill" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Huginn's Egg (Base Eff) - SP!Catria
    if "catriaBoost" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.DR_first_hit_NSP.append(30)

    if "catriaBoost" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.DR_first_hit_NSP.append(30)

    # Gladiator's Blade (Refine Eff) - Ogma
    if "ogmaBoost" in atkSkills and (atkInfAlliesWithin2Spaces or atkFlyAlliesWithin2Spaces):
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "ogmaBoost" in defSkills and (defInfAlliesWithin2Spaces or defFlyAlliesWithin2Spaces):
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    # Cain, Abel
    if "bibleBros" in atkSkills:
        atkCombatBuffs[ATK] += min(len(atkAllyWithin2Spaces) * 2, 6)
        atkCombatBuffs[DEF] += min(len(atkAllyWithin2Spaces) * 2, 6)

    if "bibleBros" in defSkills:
        defCombatBuffs[ATK] += min(len(defAllyWithin2Spaces) * 2, 6)
        defCombatBuffs[DEF] += max(len(defAllyWithin2Spaces) * 2, 6)

    # Cain, Abel, Stahl, Sully
    if "bibleBrosBrave" in atkSkills:
        for ally in atkAllyWithin2Spaces:
            if ally.move == 1 and (ally.wpnType == "Sword" or ally.wpnType == "Lance" or ally.wpnType == "Axe"):
                atkr.brave = True

    # Crimson Axe (Refine Eff)
    if "sheenaBoost" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "sheenaBoost" in defSkills and atkHPEqual100Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Volunteer Bow (Base) - Norne
    if "norneBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        if defender.wpnType in RANGED_WEAPONS:
            defCombatBuffs[ATK] -= 5
            defCombatBuffs[SPD] -= 5
            defBonusesNeutralized = [True] * 5

    if "norneBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

        if attacker.wpnType in RANGED_WEAPONS:
            atkCombatBuffs[ATK] -= 5
            atkCombatBuffs[SPD] -= 5
            atkBonusesNeutralized = [True] * 5

    # Volunteer Bow (Refine Eff) - Norne
    if "A Pinch of Salt" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    if "A Pinch of Salt" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    # Gradivus (Refine Eff) - Camus/FA!Hardin
    if "gradivu" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.all_hits_heal += 7

    if "gradivu" in defSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.all_hits_heal += 7

    # Sable Lance (Refine Base) - Sirius
    if "siriusSolo" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.offensive_NFU = True
        atkr.defensive_NFU = True

    if "siriusSolo" in defSkills and not defAdjacentToAlly:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.offensive_NFU = True
        defr.defensive_NFU = True

    # Sable Lance (Refine Eff) - Sirius
    if "siriusClash" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + min(spaces_moved_by_atkr * 2 + 4, 10) for x in atkCombatBuffs]
        atkr.DR_first_hit_NSP.append(30)

    if "siriusClash" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + min(spaces_moved_by_atkr * 2 + 4, 10) for x in defCombatBuffs]
        defr.DR_first_hit_NSP.append(30)

    # Mercurius (Refine Base)
    if "mercuriusMegabuff" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "mercuriusMegabuff" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Astra Blade (Refine Base) - P!Catria
    if "extraAstra" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "extraAstra" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Astra Blade (Refine Eff) - P!Catria
    if "superExtraAstra" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkCombatBuffs[ATK] += min(spaces_moved_by_atkr * 2, 8)
        defCombatBuffs[DEF] -= min(spaces_moved_by_atkr * 2, 8)

    if "superExtraAstra" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defCombatBuffs[ATK] += min(spaces_moved_by_atkr * 2, 8)
        atkCombatBuffs[DEF] -= min(spaces_moved_by_atkr * 2, 8)

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
            atkr.defensive_tempo = True
            atkr.offensive_tempo = True

    if "Hello, I like money" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4 + (2 * defender.flowers > 0), defCombatBuffs)
        if defender.flowers > 1:
            defr.defensive_tempo = True
            defr.offensive_tempo = True

    # Sneering Axe (Refine Eff) - Legion
    if "legionBoost" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.spGainOnAtk += 1

    if "legionBoost" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.spGainOnAtk += 1

    # Clarisse's Bow+ (Refine)
    if "clarisseDebuffB" in atkSkills:
        atkPostCombatEffs[2].append(("debuff_atk", 5, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("debuff_spd", 5, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "clarisseDebuffB" in defSkills:
        defPostCombatEffs[2].append(("debuff_atk", 5, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("debuff_spd", 5, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Sniper's Bow (Base) - Clarisse
    if "clarisseDebuffC" in atkSkills:
        atkPostCombatEffs[2].append(("damage", 7, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("debuff_atk", 7, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("debuff_spd", 7, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "clarisseDebuffC" in defSkills:
        defPostCombatEffs[2].append(("damage", 7, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("debuff_atk", 7, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("debuff_spd", 7, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Sniper's Bow (Refine Eff) - Clarisse
    if "clarisseBoost" in atkSkills:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

        if any(attacker.isSupportOf(ally) for ally in atkAllyWithin2Spaces):
            cannotCounter = True

    if "clarisseBoost" in defSkills:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    # Imhullu (Refine Base) - Gharnef
    if "gharnefDmg" in atkSkills and atkSkills["gharnefDmg"] == 7:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "gharnefDmg" in defSkills and defSkills["gharnefDmg"] == 7:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Imhullu (Refine Eff) - Gharnef
    if "gharnefBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        if defender.wpnType not in TOME_WEAPONS:
            atkr.DR_all_hits_NSP.append(30)

    if "gharnefBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        if attacker.wpnType not in TOME_WEAPONS:
            defr.DR_all_hits_NSP.append(30)

    # Divine Breath (Base) - Naga
    if "nagaBoost" in atkSkills:
        num_allies = 0
        for ally in atkAllyWithin2Spaces:
            if Status.EffDragons in ally.statusPos:
                num_allies += 1

        atkCombatBuffs = [x + min(num_allies * 3, 9) for x in atkCombatBuffs]

    if "nagaBoost" in defSkills:
        num_allies = 0
        for ally in defAllyWithin2Spaces:
            if Status.EffDragons in ally.statusPos:
                num_allies += 1

        defCombatBuffs = [x + min(num_allies * 3, 9) for x in defCombatBuffs]

    # Divine Breath (Refine Base) - Naga
    if "nagaRefineBoost" in atkSkills:
        num_allies = 0
        for ally in atkAllyWithin4Spaces:
            if Status.EffDragons in ally.statusPos:
                num_allies += 1

        atkCombatBuffs = [x + min(num_allies * 3, 9) for x in atkCombatBuffs]

    if "nagaRefineBoost" in defSkills:
        num_allies = 0
        for ally in defAllyWithin4Spaces:
            if Status.EffDragons in ally.statusPos:
                num_allies += 1

        defCombatBuffs = [x + min(num_allies * 3, 9) for x in defCombatBuffs]

    # Divine Breath (Refine Eff) - Naga
    if "a bit insane" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_first_hit_NSP.append(25)

    if "a bit insane" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_first_hit_NSP.append(25)

    # Ethereal Breath (Refine Base) - Nagi
    if "nagiRefineBoost" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[RES] -= 5
        atkr.all_hits_heal += 7

    if "nagiRefineBoost" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[RES] -= 5
        defr.all_hits_heal += 7

    # Ethereal Breath (Refine Eff) - Nagi
    if "nagiReduction" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[RES] -= 5
        atkr.stat_scaling_DR.append((RES, 40))

    if "nagiReduction" in defSkills:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[RES] -= 5
        defr.stat_scaling_DR.append((RES, 40))

    # Falchion (Refine Eff) - Alm
    if "almDoubler" in atkSkills and atkHPEqual100Percent:
        atkr.brave = True
        atkPostCombatEffs[0].append(("damage", 5, "self", "one"))

    # Luna Arc (Base) - L!Alm
    if "lunaArcDmg" in atkSkills:
        atkr.true_stat_damages_from_foe.append((DEF, 25))

    # Luna Arc (Refine Base) - L!Alm
    if "refineArcDmg" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.true_stat_damages_from_foe.append((DEF, 25))

    if "refineArcDmg" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.true_stat_damages_from_foe.append((DEF, 25))

    # Luna Arc (Refine Eff) - L!Alm
    if "legendAlmSweep" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.offensive_tempo = True

    if "legendAlmSweep" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.offensive_tempo = True

    # Dracofalchion (Base) - B!Alm
    if "dracofalchion" in atkSkills and len(atkFoeWithin2Spaces) - 1 >= len(atkAllyWithin2Spaces):
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

    if "dracofalchion" in defSkills and len(defFoeWithin2Spaces) - 1 >= len(defAllyWithin2Spaces):
        defCombatBuffs = [x + 5 for x in defCombatBuffs]

    # Dracofalchion (Refine Base) - B!Alm
    if "dracofalchionDos" in atkSkills:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

    if "dracofalchionDos" in defSkills and not defAdjacentToAlly:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]

    # Dracofalchion (Refine Eff) - B!Alm
    if "sweeeeeeep" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

    if "sweeeeeeep" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]

    # Scendscale - B!Alm
    if "TrueDamageAlm" in atkSkills:
        atkr.true_stat_damages.append((ATK, 25))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 7, "self", "one"))

    if "TrueDamageAlm" in defSkills:
        defr.true_stat_damages.append((ATK, 25))
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 7, "self", "one"))

    # Bow of Devotion (Refine) - Faye
    if "fayeBoost" in defSkills and defender.wpnType in RANGED_WEAPONS:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Laid-Back Blade (Base) - Gray
    if "grayBoost" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs = [x + 3 for x in atkCombatBuffs]

    if "grayBoost" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs = [x + 3 for x in defCombatBuffs]

    # Laid-Back Blade (Refine Eff) - Gray
    if "challenger" in atkSkills and len(atkAllyWithin2Spaces) <= len(atkFoeWithin2Spaces) - 1:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

    if "challenger" in defSkills and len(defAllyWithin2Spaces) <= len(defFoeWithin2Spaces) - 1:
        defCombatBuffs = [x + 3 for x in defCombatBuffs]

    # Jubilent Blade (Refine Eff) - Tobin / Dignified Bow (Refine Eff) - Virion
    if "HPWarrior" in atkSkills and atkStats[0] >= defHPCur + 1: atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
    if "HPWarrior" in defSkills and defStats[0] >= atkHPCur + 1: defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Sagittae (Base) - Kliff
    if "kliffBoost" in atkSkills and defStats[ATK] + defPhantomStats[ATK] >= atkStats[ATK] + atkPhantomStats[ATK] - 5:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

    if "kliffBoost" in defSkills and atkStats[ATK] + atkPhantomStats[ATK] >= defStats[ATK] + defPhantomStats[ATK] - 5:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]

    # Sagittae (Base Refine) - Kliff
    if "kliffBoostRefine" in atkSkills and defStats[ATK] + defPhantomStats[ATK] > atkStats[ATK] + atkPhantomStats[ATK]:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkr.true_stat_damages_from_foe.append((ATK, 15))

    if "kliffBoostRefine" in defSkills and atkStats[ATK] + atkPhantomStats[ATK] > defStats[ATK] + defPhantomStats[ATK]:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]
        defr.true_stat_damages_from_foe.append((ATK, 15))

    # Sagittae (Base Eff) - Kliff
    if "undersn" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "undersn" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkr.spLossWhenAtkd -= 1
        atkr.spLossOnAtk -= 1

    # Sol Lance (Base/Refine Base) - Forsyth
    if "I LOVE HEALING!!!!" in atkSkills: atkr.all_hits_heal += atkSkills["I LOVE HEALING!!!!"]
    if "I LOVE HEALING!!!!" in defSkills: defr.all_hits_heal += defSkills["I LOVE HEALING!!!!"]

    # Sol Lance (Refine Base) - Forsyth
    if "forsythBoost" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        atkr.deep_wounds_allowance.append(50)

    if "forsythBoost" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        defr.deep_wounds_allowance.append(50)

    # Sol Lance (Refine Eff) - Forsyth
    if "AtDailyForsyth" in atkSkills and atkAllyWithin3Spaces:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        defr.follow_up_denials -= 1

        if atkHPGreaterEqual50Percent:
            atkr.DR_first_hit_NSP.append(30)

    if "AtDailyForsyth" in defSkills and defAllyWithin3Spaces:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        atkr.follow_up_denials -= 1

        if defHPGreaterEqual50Percent:
            defr.DR_first_hit_NSP.append(30)

    # Snide Bow (Base) - Python
    if "pythonBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.true_all_hits += 7

    if "pythonBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.true_all_hits += 7

    # Staff of Lilies (Base) - Silque
    if "silqueBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "silqueBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Staff of Lilies (Refine Eff) - Silque
    if "silqueField" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_atk", 6, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_spd", 6, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "silqueField" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_atk", 6, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_spd", 6, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "silqueField_f" in atkSkills:
        atkSkills[DEF] += 4 * atkSkills["silqueField_f"]
        atkSkills[RES] += 4 * atkSkills["silqueField_f"]
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7 * atkSkills["silqueField_f"], "self", "one"))

    if "silqueField_f" in defSkills:
        defSkills[DEF] += 4 * defSkills["silqueField_f"]
        defSkills[RES] += 4 * defSkills["silqueField_f"]
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7 * defSkills["silqueField_f"], "self", "one"))

    # Knightly Lance (Refine Eff) - Mathilda / Lordly Lance (Refine Eff) - Clive
    if "jointSupportPartner" in atkSkills:
        if any(attacker.isSupportOf(ally) for ally in atkAllyWithin2Spaces):
            atkCombatBuffs = [x + 3 for x in atkCombatBuffs]

    if "jointSupportPartner" in defSkills:
        if any(defender.isSupportOf(ally) for ally in defAllyWithin2Spaces):
            defCombatBuffs = [x + 3 for x in defCombatBuffs]

    if "jointSupportPartner_f" in atkSkills:
        atkCombatBuffs = [x + atkSkills["jointSupportPartner_f"] for x in atkCombatBuffs]

    if "jointSupportPartner_f" in defSkills:
        defCombatBuffs = [x + defSkills["jointSupportPartner_f"] for x in defCombatBuffs]

    # Death (Base) - FA!Delthea
    if "deltheaDeath" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 4, "self", "one"))

    if "deltheaDeath" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 4, "self", "one"))

    # Death (Refine Base) - FA!Delthea
    if "deltheaRefineDeath" in atkSkills:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

        defCombatBuffs[SPD] -= max(attacker.specialMax + 1, 1)
        defCombatBuffs[RES] -= max(attacker.specialMax + 1, 1)

        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 4, "self", "one"))

    if "deltheaRefineDeath" in defSkills:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]

        atkCombatBuffs[SPD] -= max(attacker.specialMax + 1, 1)
        atkCombatBuffs[RES] -= max(attacker.specialMax + 1, 1)

        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 4, "self", "one"))

    # Death (Refine Eff) - FA!Delthea
    if "deathOrders" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
    if "deathOrders" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs = [x + 4 for x in atkCombatBuffs]

    # Ragnarok (Base) - Celica
    if "celicaBoost100" in atkSkills and atkHPEqual100Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkPostCombatEffs[2].append(("damage", 5, "self", "one"))

    if "celicaBoost100" in defSkills and defHPEqual100Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defPostCombatEffs[2].append(("damage", 5, "self", "one"))

    # Ragnarok (Refine) - Celica
    if "celicaBoost5" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkPostCombatEffs[2].append(("damage", 5, "self", "one"))

    if "celicaBoost5" in defSkills:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defPostCombatEffs[2].append(("damage", 5, "self", "one"))

    # Beloved Zofia (Base/Refine Base) - FA!Celica
    if ("belovedZofia" in atkSkills and atkHPEqual100Percent) or "belovedZofia2" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkPostCombatEffs[2].append(("damage", 4, "self", "one"))

    if ("belovedZofia" in defSkills and defHPEqual100Percent) or "belovedZofia2" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defPostCombatEffs[2].append(("damage", 4, "self", "one"))

    # Beloved Zofia (Refine Eff) - FA!Celica
    if "ALMMM" in atkSkills and (not atkHPEqual100Percent or not defHPEqual100Percent):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.all_hits_heal += 7

    if "ALMMM" in defSkills and (not atkHPEqual100Percent or not defHPEqual100Percent):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.all_hits_heal += 7

    # Royal Sword (Base/Base Refine) - B!Celica
    if "royalSword" in atkSkills and atkAllyWithin2Spaces or "royalSword2" in atkSkills: atkr.spGainOnAtk += 1
    if ("royalSword" in defSkills or "royalSword2" in defSkills) and defAllyWithin2Spaces: defr.spGainOnAtk += 1

    # Royal Sword (Refine Eff) - B!Celica
    if "A man has fallen into the river in LEGO City!" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))
        atkPostCombatEffs[UNCONDITIONAL].append(("sp_charge", 1, "self", "one"))

    if "A man has fallen into the river in LEGO City!" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))
        defPostCombatEffs[UNCONDITIONAL].append(("sp_charge", 1, "self", "one"))

    # Double Lion - B!Celica
    if "double_lion" in atkSkills and atkHPEqual100Percent:
        atkr.brave = True
        atkPostCombatEffs[UNCONDITIONAL].append(("damage", 1, "self", "one"))

    # Caring Magic (Base)
    if "eCelicaBoost" in atkSkills:
        atkCombatBuffs[ATK] += 6 + trunc(atkStats[SPD] * 0.2)
        atkCombatBuffs[SPD] += 6 + trunc(atkStats[SPD] * 0.2)

        atkr.true_stat_damages.append((SPD, 20))

        defBonusesNeutralized[SPD] = True
        defBonusesNeutralized[RES] = True

        atkr.sp_charge_FU += 1

        atkr.self_desperation = True

    if "eCelicaBoost" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 6 + trunc(defStats[SPD] * 0.2)
        defCombatBuffs[SPD] += 6 + trunc(defStats[SPD] * 0.2)

        defr.true_stat_damages.append((SPD, 20))

        atkBonusesNeutralized[SPD] = True
        atkBonusesNeutralized[RES] = True

        defr.sp_charge_FU += 1

    # Springtime Staff (Refine Eff) - Genny
    if "gennyBoost" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5

        atkPostCombatEffs[0].append(("heal", 7, "self_and_allies", "within_2_spaces_self"))

    if "gennyBoost" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[RES] += 5

        defPostCombatEffs[0].append(("heal", 7, "self_and_allies", "within_2_spaces_self"))

    # Golden Dagger (Refine Eff) - Saber
    if "SUPER MARIO!!!" in atkSkills and atkSpCountCur == 0:
        atkCombatBuffs = [x + 3 for x in atkCombatBuffs]

    if "SUPER MARIO!!!" in defSkills and defSpCountCur == 0:
        defCombatBuffs = [x + 3 for x in defCombatBuffs]
        ignore_range = True

    # Bow of Beauty (Refine Eff) - Leon
    if "leonBoost" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4
        atkCombatBuffs[DEF] += 4
        defr.follow_up_denials -= 1

    if "leonBoost" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4
        defCombatBuffs[DEF] += 4
        atkr.follow_up_denials -= 1

    # Valbar's Lance (Base) - Valbar
    if "it's his lance" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5

    if "it's his lance" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        defr.DR_second_strikes_NSP.append(60)

    # Valbar's Lance (Refine Eff) - Valbar
    if "valbarBoost" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    if "valbarBoost" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    # Dark Royal Spear (Base) - Berkut
    if "berkutBoost" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkCombatBuffs[RES] += 5

    if "berkutBoost" in defSkills:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        defCombatBuffs[RES] += 5

    # Kriemhild (Base) - FA!Berkut
    if "I miss my wife, Tails" in defSkills and defAllyWithin2Spaces and attacker.wpnType in RANGED_WEAPONS:
        ignore_range = True
        atkr.follow_up_denials -= 1

        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 20, "allies", "nearest_self"))

    # Kriemhild (Refine Base) - FA!Berkut
    if "hi MTHW" in defSkills and defAllyWithin3Spaces:
        ignore_range = True
        atkr.follow_up_denials -= 1

        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 20, "allies", "nearest_self"))

    # Kriemhild (Refine Eff) - FA!Berkut
    if "evilBerkutRef" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        atkr.follow_ups_skill += 1

    if "evilBerkutRef" in defSkills:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        defr.follow_ups_skill += 1

    # Masked Lance (Base) - Conrad
    if "how can a lance be masked" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        defCombatBuffs[ATK] -= trunc(0.20 * atkStats[RES])
        defCombatBuffs[DEF] -= trunc(0.20 * atkStats[RES])
        defCombatBuffs[RES] -= trunc(0.20 * atkStats[RES])

    if "how can a lance be masked" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

        atkCombatBuffs[ATK] -= trunc(0.20 * defStats[RES])
        atkCombatBuffs[DEF] -= trunc(0.20 * defStats[RES])
        atkCombatBuffs[RES] -= trunc(0.20 * defStats[RES])

    # Masked Lance (Refine Eff) - Conrad
    if "mmm melon collie" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.stat_scaling_DR.append((RES, 40))

    if "mmm melon collie" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.stat_scaling_DR.append((RES, 40))

    # Fell Breath (Base) - Duma
    if "dumaBoost" in atkSkills and not defHPEqual100Percent:
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[RES] += 6
        defr.follow_up_denials -= 1

    if "dumaBoost" in defSkills and not atkHPEqual100Percent:
        defCombatBuffs[ATK] += 6
        defCombatBuffs[RES] += 6
        atkr.follow_up_denials -= 1

    # Fell Breath (Refine Base) - Duma
    if "dumaRefineBoost" in atkSkills and (not defHPEqual100Percent or atkStats[ATK] + atkPhantomStats[ATK] > defStats[ATK] + defPhantomStats[ATK]):
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[RES] += 6
        defr.follow_up_denials -= 1

    if "dumaRefineBoost" in defSkills and (not atkHPEqual100Percent or defStats[ATK] + defPhantomStats[ATK] > atkStats[ATK] + atkPhantomStats[ATK]):
        defCombatBuffs[ATK] += 6
        defCombatBuffs[RES] += 6
        atkr.follow_up_denials -= 1

    # Fell Breath (Refine Eff) - Duma
    if "Twilight of the Gods is so peak" in atkSkills:
        atkCombatBuffs[ATK] += 5
        defCombatBuffs[ATK] -= 5
        atkr.DR_first_hit_NSP.append(30)

    if "Twilight of the Gods is so peak" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        atkCombatBuffs[ATK] -= 5
        defr.DR_first_hit_NSP.append(30)

    # Upheaval+ - Duma
    if "ARDestroyNearest" in atkSkills and (not defHPEqual100Percent or atkStats[ATK] + atkPhantomStats[ATK] > defStats[ATK] + defPhantomStats[ATK]):
        defBonusesNeutralized = [True] * 5

    if "ARDestroyNearest" in defSkills and (not atkHPEqual100Percent or defStats[ATK] + defPhantomStats[ATK] > atkStats[ATK] + atkPhantomStats[ATK]):
        atkBonusesNeutralized = [True] * 5

    # Tyrfing (Base) - Seliph
    if "baseTyrfing" in atkSkills and atkHPCur / atkStats[0] <= 0.5:
        atkCombatBuffs[3] += 4

    if "baseTyrfing" in defSkills and defHPCur / defStats[0] <= 0.5:
        defCombatBuffs[3] += 4

    # Tyrfing (Refine Base) - Seliph
    if "pseudoMiracle" in atkSkills and atkHPGreaterEqual50Percent:
        atkr.pseudo_miracle = True

    if "pseudoMiracle" in defSkills and defHPGreaterEqual50Percent:
        defr.pseudo_miracle = True

    # Divine Tyrfing (Refine Base) - Seliph/Sigurd
    if "refDivTyrfing" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5

    if "refDivTyrfing" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5

    # Divine Tyrfing (Refine Eff) - Seliph/Sigurd
    if "WE MOVE" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkr.follow_ups_skill += 1

    if "WE MOVE" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        defr.follow_ups_skill += 1

    # Divine Tyrfing (Base & Refine) - Seliph/Sigurd
    if ("divTyrfing" in atkSkills or "refDivTyrfing" in atkSkills) and defender.wpnType in TOME_WEAPONS: atkr.DR_first_hit_NSP.append(50)
    if ("divTyrfing" in defSkills or "refDivTyrfing" in defSkills) and attacker.wpnType in TOME_WEAPONS: defr.DR_first_hit_NSP.append(50)

    # Crusader's Ward - Sigurd/L!Sigurd
    if "deflectRanged" in atkSkills and defender.wpnType in RANGED_WEAPONS:
        atkr.DR_consec_strikes_NSP.append(80)

    if "deflectRanged" in defSkills and attacker.wpnType in RANGED_WEAPONS:
        defr.DR_consec_strikes_NSP.append(80)

    # Virtuous Tyrfing
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
        atkr.defensive_NFU = True

    if "newVTyrfing" in defSkills:
        atkCombatBuffs[1] -= 6
        atkCombatBuffs[3] -= 6
        defr.all_hits_heal += 8
        defr.defensive_NFU = True

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

    # Naga (Refine Eff) - Julia
    if "nagaAntiDragon" in atkSkills and defender.wpnType in DRAGON_WEAPONS:
        atkr.disable_foe_hexblade = True

    if "nagaAntiDragon" in defSkills and attacker.wpnType in DRAGON_WEAPONS:
        defr.disable_foe_hexblade = True
        ignore_range = True

    # Divine Naga (Base) - Julia/Deirdre
    if "nullFoeBonuses" in atkSkills: defBonusesNeutralized = [True] * 5
    if "nullFoeBonuses" in defSkills: atkBonusesNeutralized = [True] * 5

    # General disable Hexblade and Wrathful Staff
    if "disableFoeHexblade" in atkSkills: atkr.disable_foe_hexblade = True
    if "disableFoeHexblade" in defSkills: defr.disable_foe_hexblade = True
    if "disableWrathful" in atkSkills: atkr.disable_wrathful = True
    if "disableWrathful" in defSkills: defr.disable_wrathful = True

    # Virtuous Naga (Base) - L!Julia
    if "LJuliaBoost" in atkSkills and atkStats[ATK] + atkPhantomStats[ATK] > defStats[DEF] + defPhantomStats[DEF]:
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[RES] += 6

    if "LJuliaBoost" in defSkills and defStats[ATK] + defPhantomStats[ATK] > atkStats[DEF] + atkPhantomStats[DEF]:
        defCombatBuffs[ATK] += 6
        defCombatBuffs[RES] += 6

    # Virtuous Naga (Refine Base) - L!Julia
    if "LJuliaRefineBoost" in atkSkills and (atkStats[ATK] + atkPhantomStats[ATK] > defStats[DEF] + defPhantomStats[DEF] or defHPGreaterEqual75Percent):
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[RES] += 6
        atkr.stat_scaling_DR.append((RES, 40))

    if "LJuliaRefineBoost" in defSkills and (defStats[ATK] + defPhantomStats[ATK] > atkStats[DEF] + atkPhantomStats[DEF] or atkHPGreaterEqual75Percent):
        defCombatBuffs[ATK] += 6
        defCombatBuffs[RES] += 6
        defr.stat_scaling_DR.append((RES, 40))

    # Virtuous Naga (Refine Eff) - L!Julia
    if "I call on the divine light!" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.follow_ups_skill += 1

    if "I call on the divine light!" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.follow_ups_skill += 1

        if attacker.wpnType in DRAGON_WEAPONS:
            ignore_range = True

    # Light and Dark - L!Julia
    if "lightAndDark" in atkSkills:
        defCombatBuffs = [x - 2 for x in defCombatBuffs]
        defBonusesNeutralized = [True] * 5
        atkr.disable_foe_hexblade = True

    if "lightAndDark" in defSkills:
        atkCombatBuffs = [x - 2 for x in atkCombatBuffs]
        atkBonusesNeutralized = [True] * 5
        defr.disable_foe_hexblade = True

    # Light and Dark II - L!Julia
    if "lightAndDark2" in atkSkills:
        defCombatBuffs = [x - 5 for x in defCombatBuffs]
        defBonusesNeutralized = [True] * 5
        atkPenaltiesNeutralized = [True] * 5
        atkr.disable_foe_hexblade = True

    if "lightAndDark2" in defSkills:
        atkCombatBuffs = [x - 5 for x in atkCombatBuffs]
        atkBonusesNeutralized = [True] * 5
        defPenaltiesNeutralized = [True] * 5
        defr.disable_foe_hexblade = True

    # Splashy Bucket
    if "bucket" in atkSkills:
        atkr.disable_foe_hexblade = True
        atkr.disable_wrathful = True

    if "bucket" in defSkills:
        defr.disable_foe_hexblade = True
        defr.disable_wrathful = True

    # Mystic Boost
    if "mysticBoost" in atkSkills:
        atkr.disable_foe_hexblade = True
        atkr.disable_foe_wrathful = True
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", atkSkills["mysticBoost"] * 2, "self", "one"))

    if "mysticBoost" in defSkills:
        defr.disable_foe_hexblade = True
        defr.disable_foe_wrathful = True
        defPostCombatEffs[UNCONDITIONAL].append(("heal", defSkills["mysticBoost"] * 2, "self", "one"))

    # Divine Naga (Refine Eff) - Julia/Deirdre
    if "divineNagaBoost" in atkSkills and atkStats[RES] + atkPhantomStats[RES] >= defStats[RES] + defPhantomStats[RES] + 3:
        atkCombatBuffs = [x + 3 for x in atkCombatBuffs]

    if "divineNagaBoost" in defSkills and defStats[RES] + defPhantomStats[RES] >= atkStats[RES] + atkPhantomStats[RES] + 3:
        defCombatBuffs = [x + 3 for x in defCombatBuffs]

    # Arden's Blade (Refine Eff) - Arden
    if "I'M STRONG AND YOU'RE TOAST" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[DEF] += 6
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "I'M STRONG AND YOU'RE TOAST" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[DEF] += 6
        atkr.spLossWhenAtkd -= 1
        atkr.spLossOnAtk -= 1

    # Follow-Up Ring - Arden
    if "ardenFollowUp" in atkSkills and atkHPGreaterEqual50Percent: atkr.follow_ups_skill += 1
    if "ardenFollowUp" in defSkills and defHPGreaterEqual50Percent: defr.follow_ups_skill += 1

    # Ayra's Blade (Refine Eff) - Ayra
    if "Ayragate" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_first_hit_NSP.append(20)

    if "Ayragate" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_first_hit_NSP.append(20)

    # Balmung - Shannan
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

    if "larceiEdge2" in atkSkills and (atkStats[2] + atkPhantomStats[2] > defStats[2] + defPhantomStats[2] or defHPGreaterEqual75Percent):
        map(lambda x: x + 4, atkCombatBuffs)
        defBonusesNeutralized = [True] * 5
        atkr.offensive_tempo = True

    if "larceiEdge2" in defSkills and (defStats[2] + defPhantomStats[2] > atkStats[2] + atkPhantomStats[2] or atkHPGreaterEqual75Percent):
        map(lambda x: x + 4, defCombatBuffs)
        atkBonusesNeutralized = [True] * 5
        defr.offensive_tempo = True

    if "infiniteSpecial" in atkSkills and atkHPGreaterEqual25Percent: map(lambda x: x + 4, atkCombatBuffs)
    if "infiniteSpecial" in defSkills and defHPGreaterEqual25Percent: map(lambda x: x + 4, defCombatBuffs)

    # Dark Mystletainn (Refine Eff) - Eldigan/Ares
    if "DRINK" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkr.true_sp += 7

    if "DRINK" in defSkills:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        defr.true_sp += 7

    # Mjölnir (Refine Base) - Ishtar
    if "mjolnirSolo" in defSkills and not defAdjacentToAlly:
        defCombatBuffs[SPD] += 6

    # Mjölnir (Refine Eff) - Ishtar
    if "ishtarBoost" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.offensive_NFU = True

    if "ishtarBoost" in defSkills and not defAdjacentToAlly:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.offensive_NFU = True

    # Loptous (Base) - Julius
    if "juliusDebuff" in atkSkills and not ("effDragon" in defSkills or Status.EffDragons in defender.statusPos):
        defCombatBuffs[ATK] -= 6

    if "juliusDebuff" in defSkills and not ("effDragon" in atkSkills or Status.EffDragons in attacker.statusPos):
        atkCombatBuffs[ATK] -= 6

    # Loptous (Refine Base) - Julius
    dragon_eff_strs = ["effDragon", "effDragonBeast", "nagiAOEReduce", "nagiRefineBoost"]
    if "juliusDebuffPlus" in atkSkills and not (any(dragon_eff_strs == skill for skill in defSkills) or Status.EffDragons in defender.statusPos):
        defCombatBuffs[ATK] -= 6
        defCombatBuffs[RES] -= 6
        atkr.stat_scaling_DR.append((RES, 40))

    if "juliusDebuffPlus" in defSkills and not (any(dragon_eff_strs == skill for skill in atkSkills) or Status.EffDragons in attacker.statusPos):
        atkCombatBuffs[ATK] -= 6
        atkCombatBuffs[RES] -= 6
        defr.stat_scaling_DR.append((RES, 40))

    # Loptous (Refine Eff) - Julius
    if "juliusSabotage" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[RES] -= 5

    if "juliusSabotage" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[RES] -= 5

    # Bow of Verdane (Base) - Jamke
    if "jamkeBoost" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "jamkeBoost" in defSkills and not defAdjacentToAlly:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Bow of Verdane (Refine Eff) - Jamke
    if "jamkeEffects" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "jamkeEffects" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Gáe Bolg (Base) - Quan
    if "noooo fliers pls" in atkSkills and defender.moveType != 2:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5

    if "noooo fliers pls" in defSkills and attacker.moveType != 2:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5

    # Gáe Bolg (Refine Eff) - Quan
    if "refMeleeMoves" in atkSkills:
        condition = False
        for ally in atkAllAllies:
            if ally.wpnType in ["Sword", "Lance", "Axe"] or ally.move == 1:
                condition = True

        if condition:
            atkCombatBuffs[ATK] += 5
            atkCombatBuffs[DEF] += 5

    if "refMeleeMoves" in defSkills:
        condition = False
        for ally in defAllAllies:
            if ally.wpnType in ["Sword", "Lance", "Axe"] or ally.move == 1:
                condition = True

        if condition:
            defCombatBuffs[ATK] += 5
            defCombatBuffs[DEF] += 5

    # Forseti (Base) - Lewyn
    if "lewynDesp" in atkSkills and atkHPGreaterEqual50Percent:
        atkr.self_desperation = True

    # Forseti (Refine Base) - Lewyn
    if "lewynDesp2" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4
        atkr.self_desperation = True

    # Forseti (Refine Eff) - Lewyn
    if "lewynBoost" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

        atkPenaltiesNeutralized[ATK] = True
        atkPenaltiesNeutralized[SPD] = True
        defBonusesNeutralized[ATK] = True
        defBonusesNeutralized[SPD] = True

    if "lewynBoost" in atkSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

        defPenaltiesNeutralized[ATK] = True
        defPenaltiesNeutralized[SPD] = True
        atkBonusesNeutralized[ATK] = True
        atkBonusesNeutralized[SPD] = True

    # Venin Edge - (Kempf)
    if "AMERICA" in atkSkills:
        print("inflict flash")

    if "AMERICA" in defSkills:
        print("inflict flash")

    if "FREEDOM" in atkSkills and atkHPGreaterEqual25Percent: map(lambda x: x + 4, atkCombatBuffs)
    if "FREEDOM" in defSkills and defHPGreaterEqual25Percent: map(lambda x: x + 4, defCombatBuffs)

    if "MY TRAP! 🇺🇸" in atkSkills and atkAdjacentToAlly <= 1:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.DR_first_hit_NSP.append(30)

    if "MY TRAP! 🇺🇸" in defSkills and defAdjacentToAlly <= 1:
        map(lambda x: x + 4, defCombatBuffs)
        defr.DR_first_hit_NSP.append(30)

    # Light Brand (Refine Eff) - Leif
    if "leafSword" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs[SPD] += 4
        atkCombatBuffs[DEF] += 4

    if "leafSword" in defSkills and atkHPEqual100Percent:
        defCombatBuffs[SPD] += 4
        defCombatBuffs[DEF] += 4

    # Meisterbogen (Base) - L!Leif
    if "leifBowFU" in atkSkills and attacker.side == 0:
        defr.follow_up_denials -= 1

    # Meisterbogen (Refine Eff) - L!Leif
    if "leifWhyDoesHeHaveAOEDamageOnThis" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.true_stat_damages_from_foe.append((ATK, 10))
        atkr.offensive_tempo = True

    if "leifWhyDoesHeHaveAOEDamageOnThis" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.true_stat_damages_from_foe.append((ATK, 10))
        defr.offensive_tempo = True

    # Loyalty Spear (Refine Eff) - Finn
    if "finnBoost" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 4
        defCombatBuffs[SPD] -= 4
        defCombatBuffs[DEF] -= 4

        defBonusesNeutralized[ATK] = True
        defBonusesNeutralized[DEF] = True

    if "finnBoost" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 4
        atkCombatBuffs[SPD] -= 4
        atkCombatBuffs[DEF] -= 4

        atkBonusesNeutralized[ATK] = True
        atkBonusesNeutralized[DEF] = True

    if "theLand" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[1] += 6
        atkCombatBuffs[2] += 6
        atkr.always_pierce_DR = True
        #atkPostCombatHealing += 7
        if defender.getSpecialType() == "Defense":
            defr.special_disabled = True

    if "theLand" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[1] += 6
        defCombatBuffs[2] += 6
        defr.always_pierce_DR = True
        #defPostCombatHealing += 7
        if attacker.getSpecialType() == "Defense":
            atkr.special_disabled = True

    # Meisterschwert (Refine Eff) - Sword Reinhardt
    if "bigHands" in atkSkills and defHPGreaterEqual50Percent:
        atkCombatBuffs[ATK] += 5
        defCombatBuffs[ATK] -= 5
        defr.follow_up_denials -= 1

    if "bigHands" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[ATK] += 5
        atkCombatBuffs[ATK] -= 5

    # Thunderhead (Refine Eff) - P!Olwen
    if "olwen_field_f" in defSkills:
        defCombatBuffs[SPD] -= defSkills["olwen_field_f"]
        defCombatBuffs[RES] -= defSkills["olwen_field_f"]

    # Shadow Sword (Base) - FA!Mareeta
    if "swagDesp" in atkSkills and atkHPGreaterEqual50Percent:
        atkr.self_desperation = True

    # Shadow Sword (Refine Base) - FA!Mareeta
    if "swagDespPlus" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.self_desperation = True
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "swagDespPlus" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Shadow Sword (Refine Eff) - FA!Mareeta
    if "swagDespPlusPlus" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.offensive_tempo = True

        if defStats[SPD] > defStats[DEF]:
            defCombatBuffs[SPD] -= 8
        else:
            defCombatBuffs[DEF] -= 8

    if "swagDespPlusPlus" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.offensive_tempo = True

        if atkStats[SPD] > atkStats[DEF]:
            atkCombatBuffs[SPD] -= 8
        else:
            atkCombatBuffs[DEF] -= 8

    # Mareeta's Sword (Base) - Mareeta
    if "NFUSolo" in atkSkills and not atkAdjacentToAlly:
        atkr.defensive_NFU, atkr.offensive_NFU = True

    if "NFUSolo" in defSkills and not defAdjacentToAlly:
        defr.defensive_NFU, defr.offensive_NFU = True

    if "mareeeeta" in atkSkills and atkAdjacentToAlly <= 1:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.defensive_NFU, atkr.offensive_NFU = True
        defBonusesNeutralized[SPD], defBonusesNeutralized[DEF] = True

    if "mareeeeta" in defSkills and defAdjacentToAlly <= 1:
        map(lambda x: x + 4, defCombatBuffs)
        defr.defensive_NFU, defr.offensive_NFU = True
        atkBonusesNeutralized[SPD], atkBonusesNeutralized[DEF] = True

    if "moreeeeta" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 4, atkCombatBuffs)
        atkr.sp_pierce_DR = True
        atkr.offensive_tempo = True

    if "moreeeeta" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 4, defCombatBuffs)
        defr.sp_pierce_DR = True
        defr.offensive_tempo = True

    if "ascendingBlade" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        atkr.defensive_NFU, atkr.offensive_NFU = True

    if "ascendingBlade" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        defr.defensive_NFU, defr.offensive_NFU = True

    # Blazing Durandal (Refine) - B!Roy/Eliwood
    if "ourBoyBlade" in atkSkills:
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    # Blazing Durandal (Refine Eff) - B!Roy/Eliwood
    if "roys" in atkSkills:
        atkCombatBuffs[SPD] += 7
        atkCombatBuffs[DEF] += 10
        defr.follow_up_denials -= 1

    # Dragonbind (Refine Eff) - L!Roy
    if "ROY'S OUR BOY" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1
        atkr.offensive_tempo = True

    if "ROY'S OUR BOY" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1
        defr.offensive_tempo = True

    # Human Virtue II - L!Roy
    if "humanVir2" in atkSkills:
        highest_stats = [0, 0, 0, 0, 0]
        bonus_totals = []

        for ally in atkAllyWithin2Spaces:
            bonus_total = 0

            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic or ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS: continue

            i = 1
            while i < 5:
                cur_buff = ally.buffs[i]
                bonus_total += cur_buff
                highest_stats[i] = max(highest_stats[i], cur_buff)
                i += 1

            bonus_totals.append(bonus_total)

        i = 1
        while i < 5:
            atkCombatBuffs[i] += highest_stats[i]
            i += 1

        atkr.DR_first_hit_NSP.append(min(nlargest(3, bonus_totals), 40))

    if "humanVir2" in defSkills:
        highest_stats = [0, 0, 0, 0, 0]
        bonus_totals = []

        for ally in defAllyWithin2Spaces:
            bonus_total = 0

            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic or ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS: continue

            i = 1
            while i < 5:
                cur_buff = ally.buffs[i]
                bonus_total += cur_buff
                highest_stats[i] = max(highest_stats[i], cur_buff)
                i += 1

            bonus_totals.append(bonus_total)

        i = 1
        while i < 5:
            defCombatBuffs[i] += highest_stats[i]
            i += 1

        defr.DR_first_hit_NSP.append(min(nlargest(3, bonus_totals), 40))

    # Weighted Lance (Base) - Gwendolyn
    if "gwendyBoost" in atkSkills and atkHPGreaterEqual50Percent:
        atkr.spGainWhenAtkd += 1

        atkCombatBuffs[DEF] += 4
        atkCombatBuffs[RES] += 4

    if "gwendyBoost" in defSkills and defHPGreaterEqual50Percent:
        defr.spGainWhenAtkd += 1

        defCombatBuffs[DEF] += 4
        defCombatBuffs[RES] += 4

    # Light Breath (Base) - Fae, Ninian
    if "light_buff" in atkSkills:
        atkPostCombatEffs[0].append(("buff_def", 4, "allies", "within_1_spaces_self"))
        atkPostCombatEffs[0].append(("buff_res", 4, "allies", "within_1_spaces_self"))

    # Light Breath (Refine) - Fae, Ninian
    if "super_light_buff" in atkSkills:
        atkPastCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_omni", 4, "self_and_allies", "within_2_spaces_self"))

    if "super_light_buff" in defSkills:
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_omni", 4, "self_and_allies", "within_2_spaces_self"))

    # Glittering Breath/Goodie Boot (Base) - WI!Fae/WI!Cecilia
    if "winterForm" in atkSkills:
        atkCombatBuffs[DEF] += min(2 * len(atkAllyWithin2Spaces), 6)
        atkCombatBuffs[RES] += min(2 * len(atkAllyWithin2Spaces), 6)

    if "winterForm" in defSkills:
        defCombatBuffs[DEF] += min(2 * len(defAllyWithin2Spaces), 6)
        defCombatBuffs[RES] += min(2 * len(defAllyWithin2Spaces), 6)

    # Wanderer Blade (Base) - Rutger
    if "wandererer" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "wandererer" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    # Wanderer Blade (Refine Eff) - Rutger
    if "like the university" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.stat_scaling_DR.append((SPD, 40))

    if "like the university" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.stat_scaling_DR.append((SPD, 40))

    # Tome of Reason (Base) - Lugh
    if "lughBuffs" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "lughBuffs" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Tome of Reason (Refine Eff) - Lugh
    if "lughBonus" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "lughBonus" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Icy Maltet (Base) - Thea
    if "I LOVE MY FLOWERSSSSSSS" in atkSkills and defHPGreaterEqual75Percent:
        if attacker.flowers >= 1:
            atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        else:
            atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        if attacker.flowers >= 5:
            defr.spLossOnAtk -= 1
            defr.spLossWhenAtkd -= 1

    if "I LOVE MY FLOWERSSSSSSS" in defSkills:
        if defender.flowers >= 1:
            defCombatBuffs = [x + 5 for x in defCombatBuffs]
        else:
            defCombatBuffs = [x + 4 for x in defCombatBuffs]

        if defender.flowers >= 5:
            atkr.spLossOnAtk -= 1
            atkr.spLossWhenAtkd -= 1

    # Quick Mulagir (Base) - Sue
    if "sueSweep" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "sueSweep" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Quick Mulagir (Refine Eff) - Sue
    if "sueScatter" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

        atkPostCombatEffs.append(("damage", 7, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "sueScatter" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Western Axe (Base) - Echidna
    if "echidnaBoost" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_first_hit_NSP.append(30)
        atkr.retaliatory_reduced += 1
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    if "echidnaBoost" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_first_hit_NSP.append(30)
        defr.retaliatory_reduced += 1
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    # Hoo boy
    # https://feheroes.fandom.com/wiki/Regarding_an_Issue_with_the_Description_of_the_Guardian%27s_Bow_Skill_and_How_It_Will_Be_Addressed_(Notification)
    atkIgreneTriggered = False
    defIgreneTriggered = False

    # Guardian's Bow (Base) - Igrene
    if "what the hell????" in atkSkills and atkStats[SPD] + atkPhantomStats[SPD] > defStats[SPD] + defPhantomStats[SPD]:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[SPD] -= 5
        defCombatBuffs[DEF] -= 5
        atkIgreneTriggered = True

    if "what the hell????" in defSkills and defStats[SPD] + defPhantomStats[SPD] > atkStats[SPD] + atkPhantomStats[SPD]:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[SPD] -= 5
        atkCombatBuffs[DEF] -= 5
        defIgreneTriggered = False

    # Guardian's Bow (Refine Base) - Igrene
    if "yay its gone" in atkSkills:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[SPD] -= 5
        defCombatBuffs[DEF] -= 5
        atkr.DR_first_hit_NSP.append(30)

    if "yay its gone" in defSkills and defStats[SPD] + defPhantomStats[SPD] > atkStats[SPD] + atkPhantomStats[SPD] - 7:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[SPD] -= 5
        atkCombatBuffs[DEF] -= 5
        defr.DR_first_hit_NSP.append(30)

    # Guardian's Bow (Refine Eff) - Igrene
    if "igreneBoost" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.true_stat_damages.append((SPD, 10))
        atkr.offensive_tempo = True
        defBonusesNeutralized[SPD] = True
        defBonusesNeutralized[DEF] = True

    if "igreneBoost" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.true_stat_damages.append((SPD, 10))
        defr.offensive_tempo = True
        atkBonusesNeutralized[SPD] = True
        atkBonusesNeutralized[DEF] = True

    # Prized Lance (Base) - Perceval
    if "percyBoost" in atkSkills and not defHPEqual100Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "percyBoost" in defSkills and not atkHPEqual100Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Prized Lance (Refine Base) - Perceval
    if "percyRefineBoost" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "percyRefineBoost" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Prized Lance (Refine Eff) - Perceval
    if "power wave" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.true_stat_damages.append((SPD, 15))
        atkr.offensive_NFU = True
        atkr.offensive_tempo = True

    if "power wave" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.true_stat_damages.append((SPD, 15))
        defr.offensive_NFU = True
        defr.offensive_tempo = True

    # Runeaxe (Base) - Narcian
    if "runeaxeHeal" in atkSkills: atkr.all_hits_heal += 7
    if "runeaxeHeal" in defSkills: defr.all_hits_heal += 7

    # Fimbulvetr (Base) - Brunnya
    if "brunnyaBoost" in atkSkills and (attacker.hasPenalty() or not atkHPEqual100Percent):
        atkPenaltiesNeutralized = [True] * 5
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "brunnyaBoost" in defSkills and (defender.hasPenalty() or not defHPEqual100Percent):
        defPenaltiesNeutralized = [True] * 5
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Fimbulvetr (Refine Base) - Brunnya
    if "brunnyaRefineBoost" in atkSkills and (attacker.hasPenalty() or defHPGreaterEqual75Percent or not atkHPEqual100Percent):
        atkPenaltiesNeutralized = [True] * 5
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "brunnyaRefineBoost" in defSkills and (defender.hasPenalty() or atkHPGreaterEqual75Percent or not defHPEqual100Percent):
        defPenaltiesNeutralized = [True] * 5
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Fimbulvetr (Refine Eff) - Brunnya
    if "brunnyaWhatTheHell" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defCombatBuffs[ATK] -= max(10 - (defender.specialMax * 2), 2) if defender.specialMax != -1 else 2
        defCombatBuffs[RES] -= max(10 - (defender.specialMax * 2), 2) if defender.specialMax != -1 else 2

        for ally in atkAllyWithin3Spaces:
            if attacker.isSupportOf(ally):
                atkr.follow_ups_skill += 1
                break

    if "brunnyaWhatTheHell" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkCombatBuffs[ATK] -= max(10 - (attacker.specialMax * 2), 2) if attacker.specialMax != -1 else 2
        atkCombatBuffs[RES] -= max(10 - (attacker.specialMax * 2), 2) if attacker.specialMax != -1 else 2

        for ally in defAllyWithin3Spaces:
            if defender.isSupportOf(ally):
                defr.follow_ups_skill += 1
                break

    # Demonic Breath (Base, Refine Base) - Idunn
    if ("idunnBoost" in atkSkills or "idunnRefineBoost" in atkSkills) and (attacker.hasPenalty() or not atkHPEqual100Percent):
        atkPenaltiesNeutralized = [True] * 5
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if ("idunnBoost" in defSkills and (defender.hasPenalty() or not defHPEqual100Percent)) or "idunnRefineBoost" in defSkills:
        defPenaltiesNeutralized = [True] * 5
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Demonic Breath (Refine Eff) - Idunn
    if "idunnDR" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        defCombatBuffs[ATK] -= 5

    if "idunnDR" in defSkills:
        defCombatBuffs[ATK] += 5
        atkCombatBuffs[ATK] -= 5

    # Ardent Durandal (Refine Base) - L!Eliwood
    if "elistats" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "elistats" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Ardent Durandal (Refine Eff) - L!Eliwood
    if "hamburger" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defBonusesNeutralized = [True] * 5
        atkr.true_stat_damages_from_foe.append((DEF, 15))

    if "hamburger" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkBonusesNeutralized = [True] * 5
        defr.true_stat_damages_from_foe.append((DEF, 15))

    # Nini's Ice Lance (Refine Base) - B!Eliwood
    if "niniRef" in atkSkills:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkr.offensive_NFU = True

    if "niniRef" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]
        defr.offensive_NFU = True

    # Nini's Ice Lance (Refine Eff) - B!Eliwood
    if "nininiRef" in atkSkills:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkr.stat_scaling_DR.append((SPD, 40))

    if "nininiRef" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]
        defr.stat_scaling_DR.append((SPD, 40))

    # Mulagir (Refine Eff) - B!Lyn
    if "blynBoost" in atkSkills and atkStats[SPD] + atkPhantomStats[SPD] > defStats[SPD] + defPhantomStats[SPD]:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "blynBoost" in defSkills and defStats[SPD] + defPhantomStats[SPD] > atkStats[SPD] + atkPhantomStats[SPD]:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Sacae's Blessing - B!Lyn
    if "sacaeSweep" in atkSkills and defender.wpnType in ["Sword", "Lance", "Axe"]:
        cannotCounter = True

    # Swift Mulagir (Base) - L!Lyn
    if "lynBoost" in atkSkills and len(atkAllyWithin2Spaces) > len(atkFoeWithin2Spaces) - 1:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "lynBoost" in defSkills and len(defAllyWithin2Spaces) > len(defFoeWithin2Spaces) - 1:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Swift Mulagir (Refine Base) - L!Lyn
    if "betterLynBoost" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "betterLynBoost" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Swift Mulagir (Refine Eff) - L!Lyn
    if "i got her from my first AHR summon and foddered her immediately" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.true_stat_damages.append((SPD, 15))

    if "i got her from my first AHR summon and foddered her immediately" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.true_stat_damages.append((SPD, 15))

    # Deep-Blue Bow (Base) - SU!Lyn
    if "summerLynBoost" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    # Deep-Blue Bow (Refine Base) - SU!Lyn
    if "summerLynRefine" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.offensive_NFU = True
        atkr.offensive_tempo = True

    if "summerLynRefine" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.offensive_NFU = True
        defr.offensive_tempo = True

    # Deep-Blue Bow (Refine Eff) - SU!Lyn
    if "summerLynSweep" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "summerLynSweep" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Laws of Sacae - L!Lyn
    # No, like legitimately what were they going for in this kit when she first released? She has a skill that forces enemy phase, which she doesn't seem likely to survive with
    # 21/27 defenses, and boy o boy does that +3 visible Res from the weapon help! She comes with Desperation 3 for player phase so she can do something both phases I guess?
    # Atk/Spd boosts for herself in the weapon, in her weapon, Spd/Def/Res stat boosts in her assist and C skill for support, she's trying to do everything at once and
    # can't focus on just killing the foe!!! DEAD ON ARRIVAL GOT DAMNIT!!!!!!
    if "What were they cooking???" in defSkills and len(defAllyWithin2Spaces) >= 2:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Laws of Sacae II - L!Lyn
    if "That's a bit better" in atkSkills:
        atkCombatBuffs = [x + 6 for x in atkCombatBuffs]

    if "That's a bit better" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 6 for x in atkCombatBuffs]

    # Florina's Lance (Refine Eff) - Florina
    if "closeSpectrum" in defSkills and attacker.wpnType in MELEE_WEAPONS:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Berserk Armads (Refine Eff) - Hector/V!Hector
    if "oho ono" in atkSkills and defHPEqual100Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        atkr.surge_heal += trunc(atkStats[HP] * 0.30)

    if "oho ono" in defSkills:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        defr.surge_heal += trunc(defStats[HP] * 0.30)

    # Thunder Armads (Base) - L!Hector
    if "hectorFUDenial" in atkSkills and len(atkAllyWithin2Spaces) > len(atkFoeWithin2Spaces) - 1:
        defr.follow_up_denials -= 1
    if "hectorFUDenial" in defSkills and len(defAllyWithin2Spaces) > len(defFoeWithin2Spaces) - 1:
        atkr.follow_up_denials -= 1

    # Thunder Armads (Refine Base) - L!Hector
    if "hectorBoost" in atkSkills and atkAllyWithin3Spaces:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        defr.follow_up_denials -= 1

    if "hectorBoost" in defSkills and defAllyWithin3Spaces:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        atkr.follow_up_denials -= 1

    # Thunder Armads (Refine Eff) - L!Hector
    if "d'oho" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        atkr.DR_first_hit_NSP.append(40)

    if "d'oho" in defSkills:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        defr.DR_first_hit_NSP.append(40)

    # Maltet (Base) - B!Hector
    if "hectorFollowUp" in defSkills and defHPGreaterEqual50Percent:
        defr.follow_ups_skill += 1

    # Maltet (Refine Base) - B!Hector
    if "refHectorFollowUp" in defSkills and defHPGreaterEqual25Percent:
        defPenaltiesNeutralized = 5 * [True]
        defr.follow_ups_skill += 1

    # Maltet (Refine Eff) - B!Hector
    if "hectorDenial?" in atkSkills and defHPEqual100Percent:
        defCombatBuffs[ATK] -= 6
        defCombatBuffs[DEF] -= 6
        defr.follow_up_denials -= 1

    if "hectorDenial?" in defSkills:
        atkCombatBuffs[ATK] -= 6
        atkCombatBuffs[DEF] -= 6
        atkr.follow_up_denials -= 1

    # Conjurer Curios (Base/Refine Base) - H!Hector
    if ("curiosBoost" in atkSkills or "reduFU" in atkSkills) and (turn % 2 == 1 or not defHPEqual100Percent):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if ("curiosBoost" in defSkills or "reduFU" in defSkills) and (turn % 2 == 1 or not atkHPEqual100Percent):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Conjurer Curios (Refine Eff) - H!Hector
    if "oho dad" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defCombatBuffs[ATK] -= math.trunc(atkStats[ATK] * 0.1)
        defCombatBuffs[DEF] -= math.trunc(atkStats[ATK] * 0.1)

        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    if "oho dad" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkCombatBuffs[ATK] -= math.trunc(defStats[ATK] * 0.1)
        atkCombatBuffs[DEF] -= math.trunc(defStats[ATK] * 0.1)

        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    # Rebecca's Bow (Refine Eff) - Rebecca
    if "rebeccaBoost" in atkSkills and sum(attacker.buffs) > 0 and AtkPanicFactor == 1:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
    if "rebeccaBoost" in defSkills and sum(defender.buffs) > 0 and DefPanicFactor == 1:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Stout Tomahawk (Refine Eff) - Dorcas
    if "mutton idk" in atkSkills:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        defBonusesNeutralized = [True] * 5

    if "mutton idk" in defSkills and defAllyWithin2Spaces:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        atkBonusesNeutralized = [True] * 5

    # Deathly Dagger (Refine) - Jaffar
    if "jaffarDmg" in atkSkills: atkPostCombatEffs[2].append(("damage", 10, "foe_and_foes_allies", "within_2_spaces_foe"))
    if "jaffarDmg" in defSkills: defPostCombatEffs[2].append(("damage", 10, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Deathly Dagger (Refine +Eff) - Jaffar
    if "magicDenial" in atkSkills and defender.wpnType in TOME_WEAPONS:
        cannotCounter = True

    # Giga Excalibur (Refine Base) - P!Nino
    if "ninoDmg" in atkSkills:
        atkr.true_stat_damages.append((SPD, 20))
    if "ninoDmg" in defSkills:
        defr.true_stat_damages.append((SPD, 20))

    # Giga Excalibur (Refine Eff) - P!Nino
    if "doing her best" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "doing her best" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    # Regal Blade (Base/Refine) - LLoyd
    if "garbageSword" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs[ATK] += atkSkills["garbageSword"]
        atkCombatBuffs[SPD] += atkSkills["garbageSword"]

    if "garbageSword" in defSkills and atkHPEqual100Percent:
        defCombatBuffs[ATK] += defSkills["garbageSword"]
        defCombatBuffs[SPD] += defSkills["garbageSword"]

    # Regal Blade (Refine Eff) - Lloyd
    if "Hi Nino" in atkSkills and any(ally.wpnType in TOME_WEAPONS and ally.move == 0 for ally in atkAllyWithin2Spaces):
        atkCombatBuffs = [x + 3 for x in atkCombatBuffs]

    if "Hi Nino" in defSkills and any(ally.wpnType in TOME_WEAPONS and ally.move == 0 for ally in defAllyWithin2Spaces):
        defCombatBuffs = [x + 3 for x in defCombatBuffs]

    # Fanged Basilikos (Base) - Linus
    if "linusBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "linusBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    if "ghetsis holding a ducklett" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[SPD] += 5
        atkCombatBuffs[ATK] += 5
        atkr.stat_scaling_DR.append((SPD, 30))

    if "ghetsis holding a ducklett" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[SPD] += 5
        atkCombatBuffs[ATK] += 5
        defr.stat_scaling_DR.append((SPD, 30))

    # Vassal's Blade (Refine Base) - Karla
    if "vassalBlade" in atkSkills:
        atkCombatBuffs[SPD] += 5
        atkr.true_stat_damages.append((SPD, 15))

    if "vassalBlade" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[SPD] += 5
        defr.true_stat_damages.append((SPD, 15))

    if "Barry B. Benson" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.defensive_NFU, atkr.offensive_NFU = True

    if "Barry B. Benson" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.defensive_NFU, defr.offensive_NFU = True

    if "canasBoost" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5

    if "canasBoost" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[RES] += 5

    if "canasPulse" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5

    if "canasPulse" in atkSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[RES] += 5

    # Sieglinde (Refine Eff) - Eirika
    if "bonusInheritor" in atkSkills:  # eirika, should be highest bonus for each given stat on allies within 2 spaces
        highest_stats = [0, 0, 0, 0, 0]
        for ally in atkAllyWithin2Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            i = 1
            while i < 5:
                cur_buff = ally.buffs[i]
                highest_stats[i] = max(highest_stats[i], cur_buff)
                i += 1

        i = 1
        while i < 5:
            atkCombatBuffs[i] += highest_stats[i]
            i += 1

    if "bonusInheritor" in defSkills:
        highest_stats = [0, 0, 0, 0, 0]
        for ally in defAllyWithin2Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            i = 1
            while i < 5:
                cur_buff = ally.buffs[i]
                highest_stats[i] = max(highest_stats[i], cur_buff)

                i += 1

        i = 1
        while i < 5:
            defCombatBuffs[i] += highest_stats[i]
            i += 1

    if "eirikaBook" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs[ATK] += atkSkills["eirikaBook"]
        atkCombatBuffs[SPD] += atkSkills["eirikaBook"]

    if "eirikaBook" in defSkills and atkHPEqual100Percent:
        defCombatBuffs[ATK] += defSkills["eirikaBook"]
        defCombatBuffs[SPD] += defSkills["eirikaBook"]

    if "yup she has a book" in atkSkills and defHPEqual100Percent:
        defCombatBuffs = [x - 4 for x in defCombatBuffs]
        atkPenaltiesNeutralized = [True] * 5

    if "yup she has a book" in defSkills and atkHPEqual100Percent:
        atkCombatBuffs = [x - 4 for x in atkCombatBuffs]
        defPenaltiesNeutralized = [True] * 5

    if "stormSieglinde" in atkSkills and len(atkFoeWithin2Spaces) - 1 >= len(atkAllyWithin2Spaces):
        atkCombatBuffs[DEF] += 3
        atkCombatBuffs[RES] += 3
        atkr.spGainOnAtk += 1

    if "stormSieglinde" in defSkills and len(defFoeWithin2Spaces) - 1 >= len(defAllyWithin2Spaces):
        defCombatBuffs[DEF] += 3
        defCombatBuffs[RES] += 3
        defr.spGainOnAtk += 1

    if "stormSieglinde2" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

    if "stormSieglinde2" in defSkills and not defAdjacentToAlly:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

    if "Just Lean" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.stat_scaling_DR.append((SPD, 40))

    if "Just Lean" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.stat_scaling_DR.append((SPD, 40))

    if "renaisTwins" in atkSkills:
        map(lambda x: x + 4, atkCombatBuffs)

    if "renaisTwins" in defSkills and defAllyWithin2Spaces:
        map(lambda x: x + 4, defCombatBuffs)

    # Sisterly Axe (X!Eirika)
    if "sisterlyBoost" in atkSkills and atkAllyWithin3Spaces:

        num_ally_3_row_3_col = 0

        tiles_within_3_col = attacker.attacking_tile.tilesWithinNCols(3)
        tiles_within_3_row = attacker.attacking_tile.tilesWithinNRows(3)
        tiles_within_3_row_or_column = list(set(tiles_within_3_col) | set(tiles_within_3_row))

        for tile in tiles_within_3_row_or_column:
            if tile.hero_on != None and tile.hero_on.isAllyOf(attacker):
                num_ally_3_row_3_col += 1

        boost = min(5 + num_ally_3_row_3_col * 3, 14)

        atkCombatBuffs = [x + boost for x in atkCombatBuffs]

        atkr.damage_reduction_reduction.append(50)

    # Siegmund (+Eff) - Ephraim
    if "FollowUpEph" in atkSkills and atkHPCur / atkStats[0] > 0.90:
        atkr.follow_ups_skill += 1

    # Flame Siegmund (Base) - Ephraim, L!Ephraim
    if "flameEphFollowUp" in atkSkills and len(atkFoeWithin2Spaces) - 1 >= len(atkAllyWithin2Spaces):
        atkr.follow_ups_skill += 1

    if "flameEphFollowUp" in defSkills and len(defFoeWithin2Spaces) - 1 >= len(defAllyWithin2Spaces):
        defr.follow_ups_skill += 1

    # Flame Siegmund (Refine Base) - Ephraim, L!Ephraim
    if "refEphFU" in atkSkills:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[DEF] += 4
        atkr.follow_ups_skill += 1

    if "refEphFU" in defSkills and not defAdjacentToAlly:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[DEF] += 4
        defr.follow_ups_skill += 1

    # Flame Siegmund (Refine Eff) - Ephraim, L!Ephraim
    if "ephRefineSuper" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

    if "ephRefineSuper" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

    # Solar Brace II - L!Ephraim
    if "solarBraceII" in atkSkills:
        atkr.offensive_tempo = True
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 10, "self", "one"))

    if "solarBraceII" in defSkills:
        defr.offensive_tempo = True
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 10, "self", "one"))

    # Garm (Refine Eff) - B!Ephraim
    if "bEphBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkr.all_hits_heal += 7

    if "bEphBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]
        defr.all_hits_heal += 7

    # Festive Siegmund (Refine Base) - WI!Ephraim
    if "festEph" in atkSkills and (not atkAdjacentToAlly or defHPGreaterEqual75Percent):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    if "festEph" in defSkills and (not defAdjacentToAlly or atkHPGreaterEqual75Percent):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    # Festive Siegmund (Refine Eff) - WI!Ephraim
    if "twoTurtleDoves" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5

    if "twoTurtleDoves" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5

    # Nidhogg (Refine Eff) - Innes
    if "innesDenial" in atkSkills and defender.wpnType in MAGICAL_WEAPONS + DRAGON_WEAPONS:
        cannotCounter = True

    # Vidofnir (Base) - Tana
    if "meleeStance" in defSkills and defender.wpnType in ["Sword", "Lance", "Axe"]:
        defCombatBuffs[DEF] += 7

    # Vidofnir (Refine Eff) - Tana
    if "tanaBoost" in atkSkills and (atkInfAlliesWithin2Spaces or atkArmAlliesWithin2Spaces):
        atkCombatBuffs[ATK] += 7
        atkCombatBuffs[SPD] += 7

    if "tanaBoost" in defSkills and (defInfAlliesWithin2Spaces or defArmAlliesWithin2Spaces):
        defCombatBuffs[ATK] += 7
        defCombatBuffs[SPD] += 7

    # Fruit of Iðunn (Refine Base) - SU!Tana
    if "SUTanaBoost" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "SUTanaBoost" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Ivaldi (Refine Base) - L'Arachel
    if "laBoost" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 3
        atkCombatBuffs[SPD] += 3
        atkCombatBuffs[RES] += 3

    if "laBoost" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 3
        defCombatBuffs[SPD] += 3
        defCombatBuffs[RES] += 3

    if "holyWomanBeatsYouSenseless" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[RES] -= 5
        atkPostCombatEffs[0].append(("heal", 7, "self", "one"))

    if "holyWomanBeatsYouSenseless" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[RES] -= 5
        defPostCombatEffs[0].append(("heal", 7, "self", "one"))

    # Great Flame (Refine Eff) - Myrrh
    if "myrrhBoost" in atkSkills and atkHPGreaterEqual25Percent and atkAllyWithin2Spaces:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkr.defensive_NFU = True

    if "myrrhBoost" in defSkills and defHPGreaterEqual25Percent and defAllyWithin2Spaces:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]
        defr.defensive_NFU = True

    # Spirit Breath (Refine Base) - H!Myrrh
    if "HMyrrhBoost" in atkSkills and (atkStats[DEF] + atkPhantomStats[DEF] > defStats[DEF] + defPhantomStats[DEF] or defHPGreaterEqual75Percent):
        atkr.follow_ups_skill += 1
        atkCombatBuffs[ATK] += 5
        defCombatBuffs[ATK] -= 5

    if "HMyrrhBoost" in defSkills and (defStats[DEF] + defPhantomStats[DEF] > atkStats[DEF] + atkPhantomStats[DEF] or atkHPGreaterEqual75Percent):
        defr.follow_ups_skill += 1
        defCombatBuffs[ATK] += 5
        atkCombatBuffs[ATK] -= 5

    # Spirit Breath (Refine Eff) - H!Myrrh
    if "pls gimme candy" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5
        defCombatBuffs[ATK] -= 5

    if "pls gimme candy" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5
        atkCombatBuffs[ATK] -= 5
        defr.DR_second_strikes_NSP.append(70)

    # Audhulma (Base) - Joshua
    if "audBoost" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "audBoost" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkr.spLossWhenAtkd -= 1
        atkr.spLossOnAtk -= 1

    # Shamshir (Refine Eff) - Marisa
    if "hey all scott here" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "hey all scott here" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Pupil's Tome (Base) - Ewan
    if "ewanBoost" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_first_hit_NSP.append(30)
        atkPenaltiesNeutralized[ATK] = True
        atkPenaltiesNeutralized[RES] = True

    if "ewanBoost" in defSkills and defender.wpnType in RANGED_WEAPONS:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_first_hit_NSP.append(30)
        defPenaltiesNeutralized[ATK] = True
        defPenaltiesNeutralized[RES] = True

    # Pupil's Tome (Refine Eff) - Ewan
    if "ewanStuff" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defCombatBuffs[ATK] -= trunc(0.20 * atkStats[RES])
        defCombatBuffs[RES] -= trunc(0.20 * atkStats[RES])
        atkr.follow_ups_skill += 1

    if "ewanStuff" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkCombatBuffs[ATK] -= trunc(0.20 * defStats[RES])
        atkCombatBuffs[RES] -= trunc(0.20 * defStats[RES])
        defr.follow_ups_skill += 1

    # Desert-Tiger Axe (Base) - Gerik
    if "gerikBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "gerikBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Flashing Carrot/Beguiling Bow
    if "easterSpectrum" in atkSkills and defHPEqual100Percent:
        atkCombatBuffs = [x + 2 for x in atkCombatBuffs]

    if "easterSpectrum" in defSkills and atkHPEqual100Percent:
        defCombatBuffs = [x + 2 for x in defCombatBuffs]

    # Naglfar (Refine Eff) - Lyon
    if "lyonBoost" in atkSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[ATK] -= 4
        defCombatBuffs[RES] -= 4

    if "lyonBoost" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[ATK] -= 4
        defCombatBuffs[RES] -= 4

        if defHPCur / defStats[HP] >= 0.70:
            atkr.follow_ups_skill += 1

    # Ragnell/Alondite (Refine Eff) - Ike, L!Ike/Black Knight, Zelgius
    if ("I fight for my friends" in atkSkills or "WILLYOUSURVIVE?" in atkSkills) and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if ("I fight for my friends" in defSkills or "WILLYOUSURVIVE?" in defSkills) and defHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    # Urvan (Base) - B!Ike
    if "bikeDR" in atkSkills:
        atkr.DR_consec_strikes_NSP.append(80)

    if "bikeDR" in defSkills:
        defr.DR_consec_strikes_NSP.append(80)

    # Urvan (Refine Eff) - B!Ike
    if "bikeDesp" in atkSkills:
        atkr.DR_first_hit_NSP.append(40)

    if "bikeDesp" in defSkills:
        defr.DR_first_hit_NSP.append(40)
        defr.other_desperation = True

    # Valentine's 2019 Weapons
    if "telliusBond" in atkSkills and atkAdjacentToAlly: atkCombatBuffs = [x + 3 for x in atkCombatBuffs]
    if "telliusBond" in defSkills and defAdjacentToAlly: defCombatBuffs = [x + 3 for x in defCombatBuffs]

    # CH!Ike - Sturdy War Sword - Base
    if "sturdyWarrr" in atkSkills and atkHPGreaterEqual25Percent:
        map(lambda x: x + 5, atkCombatBuffs)
        if attacker.getSpecialType() == "Offense":
            if atkAllyWithin4Spaces >= 1:
                atkr.sp_charge_first += math.trunc(attacker.getMaxSpecialCooldown() / 2)
            if atkAllyWithin4Spaces >= 2:
                atkr.DR_first_hit_NSP.append(10 * defender.getMaxSpecialCooldown())
            if atkAllyWithin4Spaces >= 3:
                atkr.defensive_NFU, atkr.offensive_NFU = True

    if "sturdyWarrr" in defSkills and defHPGreaterEqual25Percent:
        map(lambda x: x + 5, defCombatBuffs)
        if defender.getSpecialType() == "Offense":
            if defAllyWithin4Spaces >= 1:
                defr.sp_charge_first += math.trunc(defender.getMaxSpecialCooldown() / 2)
            if defAllyWithin4Spaces >= 2:
                defr.DR_first_hit_NSP.append(10 * defender.getMaxSpecialCooldown())
            if defAllyWithin4Spaces >= 3:
                defr.defensive_NFU, defr.offensive_NFU = True

    # Emblem Ragnell (Base) - E!Ike
    if "BIGIKEFAN" in atkSkills and atkHPGreaterEqual25Percent:
        X = min(max(trunc(defStats[ATK] * 0.2) - 2, 6), 16)
        atkCombatBuffs[ATK] += X
        defCombatBuffs[ATK] -= X
        atkPenaltiesNeutralized = [True] * 5
        disableCannotCounter = True
        atkr.offensive_tempo = True

    if "BIGIKEFAN" in defSkills and defHPGreaterEqual25Percent:
        X = min(max(trunc(atkStats[ATK] * 0.2) - 2, 6), 16)
        defCombatBuffs[ATK] += X
        atkCombatBuffs[ATK] -= X
        defPenaltiesNeutralized = [True] * 5
        defr.offensive_tempo = True

    # Great Aether
    if "AETHER_GREAT" in atkSkills:
        atkr.vantage = True
        atkr.other_desperation = True
        atkr.DR_great_aether_SP = True

    if "AETHER_GREAT" in defSkills:
        defr.other_desperation = True
        defr.DR_great_aether_SP = True

    # Elena's Staff (Base) - Mist
    if "mistDebuff" in atkSkills:
        atkPostCombatEffs[2].append(("debuff_atk", 7, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("debuff_spd", 7, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "mistDebuff" in defSkills:
        defPostCombatEffs[2].append(("debuff_atk", 7, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("debuff_spd", 7, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Elena's Staff (Refine Eff) - Mist
    if "mistPanic" in atkSkills:
        atkPostCombatEffs[2].append(("status", Status.Panic, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "mistPanic" in defSkills:
        defPostCombatEffs[2].append(("status", Status.Panic, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "pointySword" in atkSkills: map(lambda x: x + 5, atkCombatBuffs)
    if "pointySword" in defSkills and defAllyWithin2Spaces: map(lambda x: x + 5, atkCombatBuffs)

    # Loyal Greatlance (Refine Eff) - Oscar
    if "oscarDrive" in atkSkills and (atkInfAlliesWithin2Spaces or atkCavAlliesWithin2Spaces):
        atkCombatBuffs[ATK] += 3
        atkCombatBuffs[SPD] += 3

    if "oscarDrive" in defSkills and (defInfAlliesWithin2Spaces or defCavAlliesWithin2Spaces):
        defCombatBuffs[ATK] += 3
        defCombatBuffs[SPD] += 3

    if "oscarDrive_f" in atkSkills:
        atkCombatBuffs[ATK] += atkSkills["oscarDrive_f"]
        atkCombatBuffs[SPD] += atkSkills["oscarDrive_f"]

    if "oscarDrive_f" in defSkills:
        defCombatBuffs[ATK] += defSkills["oscarDrive_f"]
        defCombatBuffs[SPD] += defSkills["oscarDrive_f"]

    # Sanaki
    if "sanakiBoost" in atkSkills and atkFlyAlliesWithin2Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5

    if "sanakiBoost" in defSkills and defFlyAlliesWithin2Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[RES] += 5

    # Nifl Frostflowers/Múspell Fireposy
    if "bridalFlowers" in atkSkills:
        atkCombatBuffs[ATK] += 2 * min(len(atkAllyWithin2Spaces), 3)
        atkCombatBuffs[SPD] += 2 * min(len(atkAllyWithin2Spaces), 3)

    if "bridalFlowers" in defSkills:
        defCombatBuffs[ATK] += 2 * min(len(defAllyWithin2Spaces), 3)
        defCombatBuffs[SPD] += 2 * min(len(defAllyWithin2Spaces), 3)

    # Nifl Frostflowers (Refine Base) - BR!Sanaki
    if "BRSanakiBoost" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5 + min(2 * len(atkAllyWithin3Spaces), 4)
        atkCombatBuffs[RES] += 5

    if "BRSanakiBoost" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5 + min(2 * len(defAllyWithin3Spaces), 4)
        defCombatBuffs[RES] += 5

    # Nifl Frostflowers (Refine Eff) - BR!Sanaki
    if "Adam Sandler's Click" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5

        highest_atk = 0
        for ally in atkAllyWithin2Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            highest_atk = max(ally.buffs[ATK], highest_atk)

        atkCombatBuffs[ATK] += highest_atk

    if "Adam Sandler's Click" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[RES] += 5

        highest_atk = 0
        for ally in defAllyWithin2Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            highest_atk = max(ally.buffs[ATK], highest_atk)

        defCombatBuffs[ATK] += highest_atk

    # Ragnell·Alondite (Refine Eff) - Altina/WI!Altina
    if "TWO?" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1
        defBonusesNeutralized[ATK] = True
        defBonusesNeutralized[DEF] = True

    if "TWO?" in defSkills:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[RES] += 5
        defr.spGainWhenAtkd += 1
        defr.spGainOnAtk += 1
        atkBonusesNeutralized[ATK] = True
        atkBonusesNeutralized[DEF] = True

    if "chosen" in atkSkills and all([ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS for ally in atkAdjacentToAlly]):
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[DEF] += 6

    if "chosen" in defSkills and all([ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS for ally in defAdjacentToAlly]):
        defCombatBuffs[ATK] += 6
        defCombatBuffs[DEF] += 6

    if "newChosen" in atkSkills and (all([ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS for ally in atkAdjacentToAlly]) or defHPGreaterEqual75Percent):
        atkCombatBuffs[ATK] += 9
        atkCombatBuffs[DEF] += 9
        atkCombatBuffs[RES] += 9
        atkr.stat_scaling_DR.append((RES, 40))

    if "newChosen" in defSkills and (all([ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS for ally in defAdjacentToAlly]) or atkHPGreaterEqual75Percent):
        defCombatBuffs[ATK] += 9
        defCombatBuffs[DEF] += 9
        defCombatBuffs[RES] += 9
        defr.stat_scaling_DR.append((RES, 40))

    # yeah we'll be here for a while
    if "You get NOTHING" in atkSkills:
        atkr.defensive_NFU, atkr.offensive_NFU = True
        defr.defensive_NFU, defr.offensive_NFU = True
        atkr.special_disabled = True
        defr.special_disabled = True
        atkDefensiveTerrain = False
        defDefensiveTerrain = False
        atkr.hardy_bearing = True
        defr.hardy_bearing = True
        if atkHPGreaterEqual25Percent: map(lambda x: x + 5, atkCombatBuffs)

    if "You get NOTHING" in defSkills:
        atkr.defensive_NFU, atkr.offensive_NFU = True
        defr.defensive_NFU, defr.offensive_NFU = True
        atkr.special_disabled = True
        defr.special_disabled = True
        atkDefensiveTerrain = False
        defDefensiveTerrain = False
        atkr.hardy_bearing = True
        defr.hardy_bearing = True
        if defHPGreaterEqual25Percent: map(lambda x: x + 5, defCombatBuffs)

    # Command Lance (Base) - Sigrun
    if "Maybe it's the way you're dressed" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_first_hit_NSP.append(40)

    if "Maybe it's the way you're dressed" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_first_hit_NSP.append(40)

    # Command Lance (Refine Eff) - Sigrun
    if "y=mx+b" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + min(len(atkAllyWithin3Spaces) * 2 + 4, 10) for x in atkCombatBuffs]
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    if "y=mx+b" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + min(len(defAllyWithin3Spaces) * 2 + 4, 10) for x in defAllyWithin3Spaces]
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    # Thani (Base) - Micaiah
    if "micaiahRedu" in atkSkills and (defender.move == 1 or defender.move == 3) and defender.wpnType in RANGED_WEAPONS:
        atkr.DR_first_hit_NSP.append(30)
    if "micaiahRedu" in defSkills and (attacker.move == 1 or attacker.move == 3) and attacker.wpnType in RANGED_WEAPONS:
        defr.DR_first_hit_NSP.append(30)

    # Thani (Refine Base) - Micaiah
    if "refMicaiahRedu" in atkSkills and defender.wpnType in RANGED_WEAPONS: atkr.DR_first_hit_NSP.append(30)
    if "refMicaiahRedu" in defSkills and attacker.wpnType in RANGED_WEAPONS: defr.DR_first_hit_NSP.append(30)

    # Thani (Refine Eff) - Micaiah
    if "micaiahBoost" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5
        atkr.follow_ups_skill += 1

    if "micaiahBoost" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[RES] += 5
        defr.follow_ups_skill += 1

    # Peshkatz (Base) - Sothe
    if "sotheDagger" in atkSkills:
        val = atkSkills["sotheDagger"]

        atkPostCombatEffs[2].append(("debuff_atk", val, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("debuff_spd", val, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("debuff_def", val, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("debuff_res", val, "foe_and_foes_allies", "within_2_spaces_foe"))

        atkPostCombatEffs[2].append(("buff_atk", val, "self_and_allies", "within_2_spaces_self"))
        atkPostCombatEffs[2].append(("buff_spd", val, "self_and_allies", "within_2_spaces_self"))
        atkPostCombatEffs[2].append(("buff_def", val, "self_and_allies", "within_2_spaces_self"))
        atkPostCombatEffs[2].append(("buff_res", val, "self_and_allies", "within_2_spaces_self"))

    if "sotheDagger" in defSkills:
        val = defSkills["sotheDagger"]

        defPostCombatEffs[2].append(("debuff_atk", val, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("debuff_spd", val, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("debuff_def", val, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("debuff_res", val, "foe_and_foes_allies", "within_2_spaces_foe"))

        defPostCombatEffs[2].append(("buff_atk", val, "self_and_allies", "within_2_spaces_self"))
        defPostCombatEffs[2].append(("buff_spd", val, "self_and_allies", "within_2_spaces_self"))
        defPostCombatEffs[2].append(("buff_def", val, "self_and_allies", "within_2_spaces_self"))
        defPostCombatEffs[2].append(("buff_res", val, "self_and_allies", "within_2_spaces_self"))

    if "sotheBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

        atkPostCombatEffs[2].append(("sp_charge", 1, "self_and_allies", "within_2_spaces_self"))
        atkPostCombatEffs[2].append(("sp_charge", -1, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "sotheBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

        defPostCombatEffs[2].append(("sp_charge", 1, "self_and_allies", "within_2_spaces_self"))
        defPostCombatEffs[2].append(("sp_charge", -1, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Tome of Favors (Base) - Oliver
    if "oliverBoost" in atkSkills and defender.wpnType not in BEAST_WEAPONS:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5

        atkPostCombatEffs[0].append(("heal", 7, "self", "one"))

    if "oliverBoost" in defSkills and attacker.wpnType not in BEAST_WEAPONS:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[RES] += 5

        defPostCombatEffs[0].append(("heal", 7, "self", "one"))

    if "I cannot blame you for wanting to touch something so alluring as myself." in atkSkills and any([ally.wpnType in BEAST_WEAPONS for ally in atkAllyWithin3Spaces]):
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5

    if "I cannot blame you for wanting to touch something so alluring as myself." in defSkills and any([ally.wpnType in BEAST_WEAPONS for ally in defAllyWithin3Spaces]):
        defCombatBuffs[ATK] += 5
        defCombatBuffs[RES] += 5

    # Hawk King Claw (Base) - Tibarn
    if "tibarnFU" in atkSkills and defHPEqual100Percent:
        atkr.follow_ups_skill += 1

    # Hawk King Claw (Refine Base) - Tibarn
    if "tibarnBoost" in atkSkills and (attacker.transformed or defHPGreaterEqual75Percent):
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkr.follow_ups_skill += 1

    if "tibarnBoost" in defSkills and (defender.transformed or atkHPGreaterEqual75Percent):
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        defr.follow_ups_skill += 1

    # Hawk King Claw (Refine Eff) - Tibarn
    if "tibarnThatsIt?" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

    if "tibarnThatsIt?" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

    # Wolf Queen Fang (Base) - Nailah
    if "nailahBoost" in atkSkills:
        atkCombatBuffs[ATK] += min(len(atkAllyWithin2Spaces) * 2, 6)
        atkCombatBuffs[SPD] += min(len(atkAllyWithin2Spaces) * 2, 6)

    if "nailahBoost" in defSkills:
        defCombatBuffs[ATK] += min(len(defAllyWithin2Spaces) * 2, 6)
        defCombatBuffs[SPD] += min(len(defAllyWithin2Spaces) * 2, 6)

    if "nailahRefineBoost" in atkSkills and (defHPGreaterEqual75Percent or atkAllyWithin3Spaces):
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

        if defHPGreaterEqual75Percent and atkAllyWithin3Spaces:
            defCombatBuffs[ATK] -= 5
            defCombatBuffs[DEF] -= 5

    if "nailahRefineBoost" in defSkills and (atkHPGreaterEqual75Percent or defAllyWithin3Spaces):
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

        if atkHPGreaterEqual75Percent and defAllyWithin3Spaces:
            atkCombatBuffs[ATK] -= 5
            atkCombatBuffs[DEF] -= 5

    if "nailahCanto" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.all_hits_heal += 7

    if "nailahCanto" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.all_hits_heal += 7

    if "glare" in atkSkills:
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("status", Status.Gravity, "foe_and_foes_allies", "within_1_spaces_foe"))

    if "glare" in defSkills:
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("status", Status.Gravity, "foe_and_foes_allies", "within_1_spaces_foe"))

    # Raven King Beak (Refine Base) - Naesala
    if "naesalaBoost" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.true_stat_damages.append((SPD, 15))

    if "naesalaBoost" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.true_stat_damages.append((SPD, 15))

    if "naesalaStuff" in atkSkills and (attacker.transformed or defHPGreaterEqual75Percent):
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "naesalaStuff" in defSkills and (defender.transformed or atkHPGreaterEqual75Percent):
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Covert Cat Fang (Base) - Ranulf
    if "ranulfField" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 3
        atkCombatBuffs[DEF] += 3

    if "ranulfField" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 3
        defCombatBuffs[DEF] += 3

    # Covert Cat Fang (Refine Base) - Ranulf
    if "ranulfField" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "ranulfField" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Covert Cat Fang (Refine Eff) - Ranulf
    if "ranulfDmg" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.offensive_NFU = True
        atkr.true_all_hits += min(len(atkAllyWithin3Spaces) * 3, 15)

    if "ranulfDmg" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.offensive_NFU = True
        defr.true_all_hits += min(len(defAllyWithin3Spaces) * 3, 15)

    # Brazen Cat Fang (Refine Base) - Lethe
    if "letheBoost" in atkSkills and not atkAdjacentToAlly:
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[SPD] += 6
        atkr.offensive_NFU = True
        atkr.true_sp += 10

    if "letheBoost" in defSkills and not defAdjacentToAlly:
        defCombatBuffs[ATK] += 6
        defCombatBuffs[SPD] += 6
        defr.offensive_NFU = True
        defr.true_sp += 10

    # Brazen Cat Fang (Refine Eff) - Lethe
    if "letheSpCharge" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

        if attacker.transformed:
            defr.spLossOnAtk -= 1
            defr.spLossWhenAtkd -= 1

    if "letheSpCharge" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

        if attacker.transformed:
            atkr.spLossOnAtk -= 1
            atkr.spLossWhenAtkd -= 1

    # Sabertooth Fang (Refine Base) - Mordecai
    if "mordecaiRefineLink" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5

    if "mordecaiRefineLink" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5

    # Sabertooth Fang (Refine Eff) - Mordecai
    if "mordecaiSPJump" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5

    if "mordecaiSPJump" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5

    # Lion King Fang (Refine Base) - Caineghis
    if "cainDR" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "cainDR" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_second_strikes_NSP.append(70)

    # Lion King Fang (Refine Eff) - Caineghis
    if "The Lion King 1 1/2" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        atkr.follow_ups_skill += 1

        if attacker.transformed:
            atkCombatBuffs[ATK] += max(0, min(trunc(0.25 * defStats[ATK]) - 8, 10))
            atkCombatBuffs[DEF] += max(0, min(trunc(0.25 * defStats[ATK]) - 8, 10))
            atkCombatBuffs[RES] += max(0, min(trunc(0.25 * defStats[ATK]) - 8, 10))

    if "The Lion King 1 1/2" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        defr.follow_ups_skill += 1

        if defender.transformed:
            defCombatBuffs[ATK] += max(0, min(trunc(0.25 * atkStats[ATK]) - 8, 10))
            defCombatBuffs[DEF] += max(0, min(trunc(0.25 * atkStats[ATK]) - 8, 10))
            defCombatBuffs[RES] += max(0, min(trunc(0.25 * atkStats[ATK]) - 8, 10))

    # Tempest's Claw (Refine EfF) - Haar
    if "haarBoost" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkr.TDR_stats.append((DEF, 15))
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "haarBoost" in defSkills:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        defr.TDR_stats.append((DEF, 15))
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Sealed Falchion (Base) - Awakening Falchion users + P!Chrom
    if "sealedFalchion" in atkSkills and not atkHPEqual100Percent:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

    if "sealedFalchion" in defSkills and not atkHPEqual100Percent:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]

    # Sealed Falchion (Refine Eff) - Awakening Falchion users + P!Chrom
    if "I CANT STOP THIS THING" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkCombatBuffs[DEF] += 5
        defr.follow_up_denials -= 1

    if "I CANT STOP THIS THING" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defCombatBuffs[DEF] += 5
        atkr.follow_up_denials -= 1

    # Carrot Lance/Axe+ and Blue/Green Egg+ (Refine)
    if "easterHealB" in atkSkills:
        atkPostCombatEffs[2].append(("heal", 4, "self", "one"))
    if "easterHealB" in defSkills:
        defPostCombatEffs[2].append(("heal", 4, "self", "one"))

    if "summerPush" in atkSkills and atkHPEqual100Percent:
        atkCombatBuffs = [x + 2 for x in atkCombatBuffs]
        atkPostCombatEffs[2].append(("damage", 2, "self", "one"))

    if "summerPush" in defSkills and defHPEqual100Percent:
        defCombatBuffs = [x + 2 for x in defCombatBuffs]
        defPostCombatEffs[2].append(("damage", 2, "self", "one"))

    # Expiration (Refine Eff) - M!Grima/F!Grima
    if "evilRobinBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defr.spLossWhenAtkd -= 1
        defr.spLossWhenAtkd -= 1

    if "evilRobinBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkr.spLossWhenAtkd -= 1
        atkr.spLossWhenAtkd -= 1

    # Dragonskin II (F!Grima)
    if "dragonskin" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs = [x + 6 for x in atkCombatBuffs]
        defBonusesNeutralized = [True] * 5

    if "dragonskin" in defSkills:
        defCombatBuffs = [x + 6 for x in defCombatBuffs]
        atkBonusesNeutralized = [True] * 5

    # Grima's Truth (Base) - M!Morgan
    if "morganCombatDebuff" in atkSkills:
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_atk", 5, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_spd", 5, "foe_and_foes_allies", "within_2_spaces_foe"))

        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_atk", 5, "self_and_allies", "within_2_spaces_self"))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_spd", 5, "self_and_allies", "within_2_spaces_self"))

    if "morganCombatDebuff" in defSkills:
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_atk", 5, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_spd", 5, "foe_and_foes_allies", "within_2_spaces_foe"))

        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_atk", 5, "self_and_allies", "within_2_spaces_self"))
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_spd", 5, "self_and_allies", "within_2_spaces_self"))

    # Father's Tactics (Refine Eff) - F!Morgan
    if "morganJointDrive" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 3
        atkCombatBuffs[SPD] += 3

    if "morganJointDrive" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 3
        defCombatBuffs[SPD] += 3

    # Geirskögul (Base) - B!Lucina
    if "lucinaDrive_f" in atkSkills:
        atkCombatBuffs[ATK] += atkSkills["lucinaDrive_f"]
        atkCombatBuffs[SPD] += atkSkills["lucinaDrive_f"]

    if "lucinaDrive_f" in defSkills:
        defCombatBuffs[ATK] += defSkills["lucinaDrive_f"]
        defCombatBuffs[SPD] += defSkills["lucinaDrive_f"]

    # Geirskögul (Refine Eff) - B!Lucina
    if "refinedLucinaDrive_f" in atkSkills:
        atkCombatBuffs[DEF] += atkSkills["refinedLucinaDrive_f"]
        atkCombatBuffs[RES] += atkSkills["refinedLucinaDrive_f"]
        atkr.spGainWhenAtkd += 1
        atkr.spGainOnAtk += 1

    if "refinedLucinaDrive_f" in defSkills:
        defCombatBuffs[DEF] += defSkills["refinedLucinaDrive_f"]
        defCombatBuffs[RES] += defSkills["refinedLucinaDrive_f"]
        defr.spGainWhenAtkd += 1
        defr.spGainOnAtk += 1

    # Thögn (Base) - L!Lucina
    if "legendLucinaBoost" in atkSkills and defender.wpnType in MELEE_WEAPONS:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "legendLucinaBoost" in defSkills and attacker.wpnType in MELEE_WEAPONS:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Thögn (Refine Base) - L!Lucina
    if "peppaPigAdversary" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "peppaPigAdversary" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Missiletainn (Owain)
    if "BY MISSILETAINN!!!" in atkSkills:
        atkr.spGainWhenAtkd += 1

    if "BY MISSILETAINN!!!" in defSkills:
        defr.spGainWhenAtkd += 1

    if "average_owain" in atkSkills and defHPGreaterEqual50Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "average_owain" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Owain
    if "Sacred Stones Strike!" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkSpEffects.update({"spMissiletainn": 0})

    if "Sacred Stones Strike!" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defSpEffects.update({"spMissiletainn": 0})

    # Cordelia's Lance
    if "cordeliaLance" in atkSkills and atkHPCur / atkStats[HP] >= 0.70:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    # Flower Lance (Base) - Sumia
    if "sumiaBoost" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "sumiaBoost" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    if "sumiaMovement" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "sumiaMovement" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Lance of Heroics (Base) - Cynthia
    if "weMovingPlenty" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 + min(spaces_moved_by_atkr * 2, 8) for x in atkCombatBuffs]

    if "weMovingPlenty" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 + min(spaces_moved_by_atkr * 2, 8) for x in defCombatBuffs]

    # Blessed Bouquet/First Bite/Cupid Arrow (Refine)
    if "bridalBuffsB" in atkSkills:
        atkPostCombatEffs[2].append(("buff_def", 5, "self_and_allies", "within_2_spaces_self"))
        atkPostCombatEffs[2].append(("buff_res", 5, "self_and_allies", "within_2_spaces_self"))

    if "bridalBuffsB" in defSkills:
        defPostCombatEffs[2].append(("buff_def", 5, "self_and_allies", "within_2_spaces_self"))
        defPostCombatEffs[2].append(("buff_res", 5, "self_and_allies", "within_2_spaces_self"))

    # Hewn Lance - Donnel
    if "donnelBoost" in atkSkills:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[DEF] += 4
        defr.follow_up_denials -= 1

    # Candied Dagger - Gaius
    if "gaius_candy" in atkSkills:
        atkCombatBuffs[SPD] += 4
        atkr.true_stat_damages.append((SPD, 10))

    if "gaius_damage_ref" in atkSkills and defHPEqual100Percent:
        atkr.true_all_hits += 7

    # Corvus Tome (Refine Eff) - Henry
    if "henryLowAtkBoost" in atkSkills and defStats[ATK] + defPhantomStats[ATK] >= atkStats[ATK] + atkPhantomStats[
        ATK] + 3:
        defCombatBuffs[ATK] -= 6
        defCombatBuffs[RES] -= 6
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "henryLowAtkBoost" in defSkills and atkStats[ATK] + atkPhantomStats[ATK] >= defStats[ATK] + defPhantomStats[
        ATK] + 3:
        atkCombatBuffs[ATK] -= 6
        atkCombatBuffs[RES] -= 6
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Inviolable Axe (Base) - Libra
    if "libraDebuff" in atkSkills:
        defCombatBuffs[ATK] -= 4
        defCombatBuffs[SPD] -= 4
        defCombatBuffs[DEF] -= 4
        atkr.true_all_hits += 7

    if "libraDebuff" in defSkills and defAllyWithin2Spaces:
        atkCombatBuffs[ATK] -= 4
        atkCombatBuffs[SPD] -= 4
        atkCombatBuffs[DEF] -= 4
        defr.true_all_hits += 7

    if "libraHealing" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 4
        defCombatBuffs[SPD] -= 4
        defCombatBuffs[DEF] -= 4
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self_and_allies", "within_2_spaces"))

    if "libraHealing" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 4
        atkCombatBuffs[SPD] -= 4
        atkCombatBuffs[DEF] -= 4
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self_and_allies", "within_2_spaces"))

    # Spectral Tome+/Monstrous Bow+
    if "halloweenPanic" in atkSkills: atkPostCombatEffs[2].append(
        ("status", Status.Panic, "foes_allies", "within_2_spaces_foe"))
    if "halloweenPanic" in defSkills: defPostCombatEffs[2].append(
        ("status", Status.Panic, "foes_allies", "within_2_spaces_foe"))

    # Purifying Breath - Nowi
    if "nowiBoost" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkPenaltiesNeutralized = [True] * 5

    if "nowiBoost" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defPenaltiesNeutralized = [True] * 5

    # Grimoire (Refine) - Nowi
    if "nowiSchmovement" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "nowiSchmovement" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    # Grimoire (Refine Eff) - H!Nowi
    if "nowiField_f" in atkSkills:
        atkCombatBuffs[ATK] -= atkSkills["nowiField"]
        atkCombatBuffs[SPD] -= atkSkills["nowiField"]
        atkCombatBuffs[RES] -= atkSkills["nowiField"]

    if "nowiField_f" in defSkills:
        defCombatBuffs[ATK] -= defSkills["nowiField"]
        defCombatBuffs[SPD] -= defSkills["nowiField"]
        defCombatBuffs[RES] -= defSkills["nowiField"]

    # Múspell Fireposy (Refine Base) - BR!Tharja
    if "BRTharjaBoost" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5 + min(2 * len(atkAllyWithin3Spaces), 4)
        atkCombatBuffs[SPD] += 5

    if "BRTharjaBoost" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5 + min(2 * len(defAllyWithin3Spaces), 4)
        defCombatBuffs[SPD] += 5

    # Múspell Fireposy (Refine Eff) - BR!Tharja
    if "complexRein1_f" in atkSkills:
        atkCombatBuffs[SPD] -= atkSkills["complexRein1_f"]
        atkCombatBuffs[RES] -= atkSkills["complexRein1_f"]

    if "complexRein2_f" in atkSkills:
        atkCombatBuffs[SPD] -= atkSkills["complexRein2_f"]
        atkCombatBuffs[RES] -= atkSkills["complexRein2_f"]

    if "complexRein3_f" in atkSkills:
        atkCombatBuffs[SPD] -= atkSkills["complexRein3_f"]
        atkCombatBuffs[RES] -= atkSkills["complexRein3_f"]

    if "complexRein1_f" in defSkills:
        defCombatBuffs[SPD] -= defSkills["complexRein1_f"]
        defCombatBuffs[RES] -= defSkills["complexRein1_f"]

    if "complexRein2_f" in defSkills:
        defCombatBuffs[SPD] -= defSkills["complexRein2_f"]
        defCombatBuffs[RES] -= defSkills["complexRein2_f"]

    if "complexRein3_f" in defSkills:
        defCombatBuffs[SPD] -= defSkills["complexRein3_f"]
        defCombatBuffs[RES] -= defSkills["complexRein3_f"]

    # Masking Axe (Base) - Gerome
    if "geromeBoost" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5

    if "geromeBoost" in defSkills:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5

    # Masking Axe (Refine Eff) - Gerome
    if "geromeBuff" in atkSkills and not atkAdjacentToAlly:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5

    if "geromeBuff" in defSkills and not defAdjacentToAlly:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5

    # Flavia
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

    # Hearbeat Lance (Base) - Kjelle
    if "MR KRABS I WANNA GO TO BED" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        defr.follow_up_denials -= 1

    if "MR KRABS I WANNA GO TO BED" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        atkr.follow_up_denials -= 1

    if "kjelleDeboost" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5

        X = 0

        if atkHPCur > defHPCur: X += 1

        for i in range(1, 5):
            if atkStats[i] + atkPhantomStats[i] > defStats[i] + defPhantomStats[i]:
                X += 1

        defCombatBuffs[ATK] -= trunc((0.05 * X + 0.10) * defStats[ATK])

    if "kjelleDeboost" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5

        X = 0

        if defHPCur > atkHPCur: X += 1

        for i in range(1, 5):
            if defStats[i] + defPhantomStats[i] > atkStats[i] + atkPhantomStats[i]:
                X += 1

        atkCombatBuffs[ATK] -= trunc((0.05 * X + 0.10) * atkStats[ATK])


    if "walhartBoost" in atkSkills and len(atkFoeWithin2Spaces) - 1 <= len(atkAllyWithin2Spaces):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "walhartBoost" in defSkills and len(defFoeWithin2Spaces) - 1 <= len(defAllyWithin2Spaces):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    if "walhartBolster" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "walhartBolster" in defSkills and not defAdjacentToAlly:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    if "as I type this I have a 102 fever lol" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5

    if "as I type this I have a 102 fever lol" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5

    # Aversa's Night (Base Refine) - Aversa
    if "aversaSabotage" in atkSkills and atkSkills["aversaSabotage"] == 4:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[SPD] -= 5
        defCombatBuffs[RES] -= 5

    if "aversaSabotage" in defSkills and defSkills["aversaSabotage"] == 4:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[SPD] -= 5
        atkCombatBuffs[RES] -= 5

    # Taguel Fang (Base) - Panne
    if "panneBoost" in atkSkills or "panneBoost2" in atkSkills:
        cond = True

        for ally in atkAdjacentToAlly:
            if ally.wpnType not in BEAST_WEAPONS:
                cond = False
                break

        if cond and "panneBoost" in atkSkills:
            atkCombatBuffs = [x + 3 for x in atkCombatBuffs]
        elif cond and "panneBoost2" in atkSkills:
            atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
            defr.spGainOnAtk -= 1
            defr.spGainWhenAtkd -= 1

    if "panneBoost" in defSkills or "panneBoost2" in defSkills:
        cond = True

        for ally in defAdjacentToAlly:
            if ally.wpnType not in BEAST_WEAPONS:
                cond = False
                break

        if cond and "panneBoost" in defSkills:
            defCombatBuffs = [x + 3 for x in defCombatBuffs]
        elif cond and "panneBoost2" in defSkills:
            defCombatBuffs = [x + 4 for x in defCombatBuffs]
            atkr.spGainOnAtk -= 1
            atkr.spGainWhenAtkd -= 1

    if "panneStuff" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "panneStuff" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    if "yarneRefinePulse" in atkSkills and (atkHPCur / atkStats[HP] <= 0.90 or not atkAdjacentToAlly):
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "yarneRefinePulse" in defSkills and (defHPCur / defStats[HP] <= 0.90 or not defAdjacentToAlly):
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    if "yarneBoost" in atkSkills and defHPGreaterEqual50Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.true_stat_damages.append((SPD, 10))

        if attacker.transformed:
            atkr.follow_ups_skill += 1

    if "yarneBoost" in defSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.true_stat_damages.append((SPD, 10))

        if defender.transformed:
            defr.follow_ups_skill += 1

    # Yato (Refine Eff) - M!Corrin
    if "corrinField_f" in atkSkills: atkCombatBuffs = [x + atkSkills["corrinField_f"] for x in atkCombatBuffs]
    if "corrinField_f" in defSkills: defCombatBuffs = [x + atkSkills["corrinField_f"] for x in defCombatBuffs]

    if "oldDarkBreath" in atkSkills:
        atkPostCombatEffs[0].append(("debuff_atk", 5, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[0].append(("debuff_spd", 5, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "refDarkBreath" in atkSkills:
        atkPostCombatEffs[2].append(("debuff_atk", 7, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("debuff_spd", 7, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "refDarkBreath" in defSkills:
        defPostCombatEffs[2].append(("debuff_atk", 7, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("debuff_spd", 7, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Draconic Rage (Base) - AD!Corrins
    if "corrinRage" in atkSkills and len(atkAdjacentToAlly) > len(atkFoeWithin2Spaces) - 1:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "corrinRage" in defSkills and len(defAdjacentToAlly) > len(defFoeWithin2Spaces) - 1:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    if "adriftBoost" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_first_hit_NSP.append(40)

    if "adriftBoost" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_first_hit_NSP.append(40)

    if "adriftBlast" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.spGainWhenAtkd += 1
        atkr.spGainOnAtk += 1

    if "adriftBlast" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.spGainWhenAtkd += 1
        defr.spGainOnAtk += 1

    # Savage Breath (Base) - FA!F!Corrin
    if "corrinSavage" in atkSkills:
        atkCombatBuffs = [x + max(6 - len(atkAllyWithin2Spaces), 0) for x in atkCombatBuffs]

    if "corrinSavage" in defSkills:
        defCombatBuffs = [x + max(6 - len(defAllyWithin2Spaces), 0) for x in defCombatBuffs]

    # Savage Breath (Refine Base) - FA!F!Corrin
    if "corrinRefineSavage" in atkSkills:
        atkCombatBuffs = [x + max(7 - len(atkAllyWithin2Spaces), 0) for x in atkCombatBuffs]

        if len(atkAllyWithin2Spaces) <= 1:
            atkPenaltiesNeutralized = [True] * 5

    if "corrinRefineSavage" in defSkills:
        defCombatBuffs = [x + max(7 - len(defAllyWithin2Spaces), 0) for x in defCombatBuffs]

        if len(defAllyWithin2Spaces) <= 1:
            defPenaltiesNeutralized = [True] * 5

    # Savage Breath (Refine Eff) - FA!F!Corrin
    if "https://twitter.com/YMWyungbug/status/1887810292484374993" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_first_hit_NSP.append(max(30 - (len(atkAllyWithin2Spaces) * 10)), 0)

    if "https://twitter.com/YMWyungbug/status/1887810292484374993" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_first_hit_NSP.append(max(30 - (len(defAllyWithin2Spaces) * 10)), 0)

    # Dusk Dragonstone (Base) - M!Kana
    if "secondKanaBoost" in atkSkills and defHPGreaterEqual75Percent: atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
    if "secondKanaBoost" in defSkills: defCombatBuffs = [x + 4 for x in defCombatBuffs]

    if "secondKanaHeal" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    if "secondKanaHeal" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    # Prayer Wheel (Refine Eff) - L!Azura
    if "azuraTriangle" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    # Azure Lance (Base) - Shigure
    if "I'm Shigure" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.true_all_hits += 7

    if "I'm Shigure" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.true_all_hits += 7

    # Azure Lance (Refine Eff) - Shigure
    if "shigureLink" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "shigureLink" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Felicia's Plate (Felicia)
    if "feliciaMagicGuard" in atkSkills and defender.wpnType in ["RTome", "BTome", "GTome", "CTome"]:
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

    if "feliciaMagicGuard" in defSkills and attacker.wpnType in ["RTome", "BTome", "GTome", "CTome"]:
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

    # Eldhrímnir (Base) - SP!Felicia
    if "feliciaBoost" in atkSkills:
        diff = max(0, min((atkStats[RES] + atkPhantomStats[RES]) - (defStats[RES] + defPhantomStats[RES]), 16))

        defCombatBuffs[ATK] -= trunc(diff * 0.50)
        defCombatBuffs[SPD] -= trunc(diff * 0.50)

    if "feliciaBoost" in defSkills:
        diff = max(0, min((defStats[RES] + defPhantomStats[RES]) - (atkStats[RES] + atkPhantomStats[RES]), 16))

        atkCombatBuffs[ATK] -= trunc(diff * 0.50)
        atkCombatBuffs[SPD] -= trunc(diff * 0.50)

    # Sæhrímnir (Refine Base) - SP!Flora
    if "spFloraBoost" in atkSkills:
        diff = max(0, min((atkStats[RES] + atkPhantomStats[RES]) - (defStats[RES] + defPhantomStats[RES]), 16))

        defCombatBuffs[ATK] -= trunc(diff * 0.50)
        defCombatBuffs[DEF] -= trunc(diff * 0.50)

    if "spFloraBoost" in defSkills:
        diff = max(0, min((defStats[RES] + defPhantomStats[RES]) - (atkStats[RES] + atkPhantomStats[RES]), 16))

        atkCombatBuffs[ATK] -= trunc(diff * 0.50)
        atkCombatBuffs[SPD] -= trunc(diff * 0.50)

    # Eldhrímnir (Refine Base) - SP!Felicia / Sæhrímnir (Refine Base) - SP!Flora
    if "icePicnicRefine" in atkSkills:
        diff = max(0, min((atkStats[RES] + atkPhantomStats[RES]) - (defStats[RES] + defPhantomStats[RES]), 16))

        defCombatBuffs[ATK] -= trunc(diff * 0.80)
        defCombatBuffs[SPD] -= trunc(diff * 0.80)
        defCombatBuffs[DEF] -= trunc(diff * 0.80)

        if atkHPGreaterEqual25Percent:
            atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "icePicnicRefine" in defSkills:
        diff = max(0, min((defStats[RES] + defPhantomStats[RES]) - (atkStats[RES] + atkPhantomStats[RES]), 16))

        atkCombatBuffs[ATK] -= trunc(diff * 0.80)
        atkCombatBuffs[SPD] -= trunc(diff * 0.80)
        atkCombatBuffs[DEF] -= trunc(diff * 0.80)

        if defHPGreaterEqual25Percent:
            defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Eldhrímnir (Refine Eff) - SP!Felicia
    if "who let her cook?" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.defensive_NFU = True

    if "who let her cook?" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.defensive_NFU = True

    # Sæhrímnir (Refine Base) - SP!Flora
    if "let her cook!" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "let her cook!" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Hoarfrost Knife (Base) - Flora
    if "floraBoost" in atkSkills and defender.wpnType in MELEE_WEAPONS:
        atkCombatBuffs[DEF] += 20

    if "floraEasyBoost" in atkSkills:
        atkCombatBuffs[DEF] += 20

    if "floraGuard" in atkSkills:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "floraGuard" in defSkills and defAllyWithin2Spaces:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Jakob's Tray (Jakob)

    if "jakobDebuff" in atkSkills:
        defCombatBuffs = [x - 4 for x in defCombatBuffs]

    if "jakobAllyBoost" in atkSkills:
        ally_condition = False
        for ally in atkAllyWithin2Spaces:
            if ally.HPcur < ally.visible_stats[HP]:
                ally_condition = True

        if ally_condition:
            atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "jakobAllyBoost" in defSkills:
        ally_condition = False
        for ally in defAllyWithin2Spaces:
            if ally.HPcur < ally.visible_stats[HP]:
                ally_condition = True

        if ally_condition:
            defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Inveterate Axe (Gunter)
    if "gunterJointDrive" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[DEF] += 4

    if "gunterJointDrive" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[DEF] += 4

    if "gunterJointDrive_f" in atkSkills and (attacker.move == 0 or attacker.move == 1):
        atkCombatBuffs[ATK] += atkSkills["gunterJointDrive_f"]
        atkCombatBuffs[DEF] += atkSkills["gunterJointDrive_f"]

    if "gunterJointDrive_f" in defSkills and (defender.move == 0 or defender.move == 1):
        defCombatBuffs[ATK] += defSkills["gunterJointDrive_f"]
        defCombatBuffs[DEF] += defSkills["gunterJointDrive_f"]

    # Raijinto (Refine Eff) - Ryoma/L!Ryoma
    if "waitTurns" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.defensive_NFU = True
        atkr.offensive_NFU = True

    if "waitTurns" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.defensive_NFU = True
        defr.offensive_NFU = True

    # Bushido II - L!Ryoma
    if "bushidoII" in atkSkills:
        atkr.true_all_hits += 7
        atkr.stat_scaling_DR.append((SPD, 40))

    if "bushidoII" in defSkills:
        defr.true_all_hits += 7
        defr.stat_scaling_DR.append((SPD, 40))

    # Bright Naginata (Base) - Shiro
    if "refineNaginata" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkPenaltiesNeutralized = [True] * 5

    if "refineNaginata" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5
        defPenaltiesNeutralized = [True] * 5

    if "kageroBoost" in atkSkills and atkStats[ATK] + atkPhantomStats[ATK] > defStats[ATK] + defPhantomStats[ATK]:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "kageroBoost" in defSkills and defStats[ATK] + defPhantomStats[ATK] > atkStats[ATK] + atkPhantomStats[ATK]:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    if "kageroRedu" in atkSkills:
        atkr.DR_first_hit_NSP.append(50)

    if "kazeBoost" in atkSkills:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4
        atkCombatBuffs[RES] += 4

    if "kazeBoost" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4
        defCombatBuffs[RES] += 4

    if "he kinda sounds like Joker Persona 5" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4
        atkCombatBuffs[RES] += 4

    if "he kinda sounds like Joker Persona 5" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4
        defCombatBuffs[RES] += 4

    # Skadi (Refine Eff) - FA!Takumi
    if "skadiBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkPostCombatEffs[2].append(("damage", 7, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "skadiBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defPostCombatEffs[2].append(("damage", 7, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Hinoka's Spear
    if "hinokaBoost" in atkSkills and (atkFlyAlliesWithin2Spaces or atkInfAlliesWithin2Spaces):
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "hinokaBoost" in defSkills and (defFlyAlliesWithin2Spaces or defInfAlliesWithin2Spaces):
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    # Warrior Princes (Refine Base) - P!Hinoka
    if "hinokaJointDrive" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "hinokaJointDrive" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    if "hinokaJointDrive_f" in atkSkills:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "hinokaJointDrive_f" in defSkills:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    # Warrior Princes (Refine Eff) - P!Hinoka
    if "hinokaField_f" in atkSkills:
        atkCombatBuffs[ATK] -= atkSkills["hinokaField_f"]
        atkCombatBuffs[SPD] -= atkSkills["hinokaField_f"]
        atkCombatBuffs[DEF] -= atkSkills["hinokaField_f"]

    if "hinokaField_f" in defSkills:
        defCombatBuffs[ATK] -= defSkills["hinokaField_f"]
        defCombatBuffs[SPD] -= defSkills["hinokaField_f"]
        defCombatBuffs[DEF] -= defSkills["hinokaField_f"]

    # Setsuna's Yumi
    if "setsunaRangedBoost" in atkSkills and defender.wpnType in RANGED_WEAPONS:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "setsunaRangedBoost" in defSkills and attacker.wpnType in RANGED_WEAPONS:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Subaki
    if "subakiDamage" in atkSkills and atkHPCur / atkStats[HP] >= 0.70:
        atkr.true_all_hits += 7

    if "subakiDamage" in defSkills and defHPCur / defStats[HP] >= 0.70:
        defr.true_all_hits += 7

    # Siegfried (Refine Eff) - Xander
    if "xanderific" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[1] -= 5
        defCombatBuffs[3] -= 5
        defr.follow_up_denials -= 1

    if "xanderific" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        atkr.follow_up_denials -= 1

    # Dark Greatsword (Refine) - Siegbert
    if "Toaster" in atkSkills and not atkAdjacentToAlly:
        atkCombatBuffs[1] += 5
        atkCombatBuffs[2] += 5
        defBonusesNeutralized = [True] * 5

    if "Toaster" in defSkills and not defAdjacentToAlly:
        defCombatBuffs[1] += 5
        defCombatBuffs[2] += 5
        atkBonusesNeutralized = [True] * 5

    # Peri's Spear (Peri)
    if "periBoost" in atkSkills and not atkHPEqual100Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "periBoost" in defSkills and not defHPEqual100Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Laslow's Blade (Laslow)
    if "laslowBrave" in atkSkills:
        bonus_total_reached = 0

        for ally in atkAllyWithin3Spaces:
            panic_factor = 1
            if Status.Panic in ally.statusNeg: panic_factor = -1
            if Status.NullPanic in ally.statusPos: panic_factor = 1
            if sum(ally.buffs) * panic_factor >= 10:
                bonus_total_reached += 1

        if bonus_total_reached >= 2:
            atkCombatBuffs[1] += 3
            atkCombatBuffs[3] += 3
            atkr.brave = True

    if "laslowBrave" in defSkills:
        bonus_total_reached = 0

        for ally in defAllyWithin3Spaces:
            panic_factor = 1
            if Status.Panic in ally.statusNeg: panic_factor = -1
            if Status.NullPanic in ally.statusPos: panic_factor = 1
            if sum(ally.buffs) * panic_factor >= 10:
                bonus_total_reached += 1

        if bonus_total_reached >= 2:
            defCombatBuffs[1] += 3
            defCombatBuffs[3] += 3
            defr.brave = True

    # Brynhildr (Leo)
    if "leoGravity" in atkSkills:
        atkPostCombatEffs[0].append(("status", Status.Gravity, "foe", "one"))

    if "leoWhateverTheHellThisIs" in atkSkills and defender.wpnType in TOME_WEAPONS:
        atkr.DR_first_hit_NSP.append(30)

    if "leoWhateverTheHellThisIs" in defSkills and attacker.wpnType in TOME_WEAPONS:
        defr.DR_first_hit_NSP.append(30)

    # Spy-Song Bow (Refine Eff) - Nina
    if "YAOI" in atkSkills and len(atkAllyWithin3Spaces) >= 2:
        condition = False

        n = len(atkAllyWithin3Spaces)
        for i in range(n):
            for j in range(i + 1, n):
                if atkAllyWithin3Spaces[i].isSupportOf(atkAllyWithin3Spaces[j]):
                    condition = True
                    break

        if condition:
            atkCombatBuffs = [x + 6 for x in atkCombatBuffs]
            atkr.all_hits_heal += 5

    if "YAOI" in defSkills and len(defAllyWithin3Spaces) >= 2:
        condition = False

        n = len(defAllyWithin3Spaces)
        for i in range(n):
            for j in range(i + 1, n):
                if defAllyWithin3Spaces[i].isSupportOf(defAllyWithin3Spaces[j]):
                    condition = True
                    break

        if condition:
            defCombatBuffs = [x + 6 for x in defCombatBuffs]
            defr.all_hits_heal += 5

    # Camilla
    if "camillaBoost" in atkSkills and (atkCavAlliesWithin2Spaces or atkFlyAlliesWithin2Spaces):
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "camillaBoost" in defSkills and (defCavAlliesWithin2Spaces or defFlyAlliesWithin2Spaces):
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    if "camillaField_f" in atkSkills and (attacker.move == 1 or attacker.move == 2):
        atkCombatBuffs[ATK] += 3
        atkCombatBuffs[SPD] += 3

    if "camillaField_f" in defSkills and (defender.move == 1 or defender.move == 2):
        defCombatBuffs[ATK] += 3
        defCombatBuffs[SPD] += 3

    # Book of Dreams (Base) - Adrift Camilla
    if "camillaBond" in atkSkills and atkAdjacentToAlly:
        defCombatBuffs = [x - 4 for x in defCombatBuffs]

    if "camillaBond" in defSkills and defAdjacentToAlly:
        atkCombatBuffs = [x - 4 for x in atkCombatBuffs]

    if "camillaDebuff" in atkSkills:
        defCombatBuffs = [x - 4 for x in defCombatBuffs]

    if "camillaDebuff" in defSkills and defAllyWithin2Spaces:
        atkCombatBuffs = [x - 4 for x in atkCombatBuffs]

    if "I should be studying for my finals lol" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.true_stat_damages.append((ATK, 15))

    if "I should be studying for my finals lol" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.true_stat_damages.append((ATK, 15))

    # Beruka
    if "berukaAxe" in atkSkills and atkHPGreaterEqual50Percent:
        defCombatBuffs[ATK] -= 4
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "berukaAxe" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[ATK] -= 4
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Selena
    if "lowAtkBoost" in atkSkills and defStats[ATK] + defPhantomStats[ATK] >= atkStats[ATK] + atkPhantomStats[ATK] + 3:
        atkCombatBuffs = [x + 3 for x in atkCombatBuffs]

    if "lowAtkBoost" in defSkills and atkStats[ATK] + atkPhantomStats[ATK] >= defStats[ATK] + defPhantomStats[ATK] + 3:
        defCombatBuffs = [x + 3 for x in defCombatBuffs]

    if "eliseField_f" in defSkills:
        defCombatBuffs = [x - defSkills["eliseField_f"] for x in defCombatBuffs]

    # Effie's Lance
    if "effieAtk" in atkSkills and atkHPGreaterEqual50Percent: atkCombatBuffs[ATK] += 6
    if "effieAtk" in defSkills and defHPGreaterEqual50Percent: defCombatBuffs[ATK] += 6

    if "effieFirstCombat" in atkSkills and attacker.unitCombatInitiates == 0:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        defBonusesNeutralized[ATK] = True
        defBonusesNeutralized[DEF] = True

    if "effieFirstCombat" in defSkills and defender.unitCombatInitiates == 0:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        atkBonusesNeutralized[ATK] = True
        atkBonusesNeutralized[DEF] = True

    # Soleil
    if "ladies, whats good" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.spGainOnAtk += 1

    if "rhajatEffects" in atkSkills:
        atkPostCombatEffs[2].append(("damage", 7, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("status", Status.Flash, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "rhajatEffects" in defSkills:
        defPostCombatEffs[2].append(("damage", 7, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("status", Status.Flash, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Sworn Lance (Base) - Silas
    if "a bit of stats" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5

    if "a bit of stats" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5

    if "a fair bit more stats" in atkSkills:
        condition = False
        for ally in atkAllyWithin3Spaces:
            if ally.isSupportOf(attacker):
                condition = True

        for ally in atkAllAllies:
            if ally.isSupportOf(attacker) and ally.HPcur / ally.visible_stats[HP] <= 0.8:
                condition = True

        if condition:
            atkCombatBuffs[ATK] += 7
            atkCombatBuffs[DEF] += 7
            defr.follow_up_denials -= 1

    if "a fair bit more stats" in defSkills:
        condition = False
        for ally in defAllyWithin3Spaces:
            if ally.isSupportOf(defender):
                condition = True

        for ally in defAllAllies:
            if ally.isSupportOf(defender) and ally.HPcur / ally.visible_stats[HP] <= 0.8:
                condition = True

        if condition:
            defCombatBuffs[ATK] += 7
            defCombatBuffs[DEF] += 7
            atkr.follow_up_denials -= 1

    if "garonDevour" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        defCombatBuffs[ATK] -= 5

    if "garonDevour" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        atkCombatBuffs[ATK] -= 5

    if "(groans of increasing discomfort)" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 5
        defCombatBuffs[ATK] -= 5
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "(groans of increasing discomfort)" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        atkCombatBuffs[ATK] -= 5
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Kitsune Fang (Refine Base) - Kaden
    if "kadenField2" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "kadenField2" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Kitsune Fang (Refine Eff) - Kaden (yes it's the same thing)
    if "kadenSupport" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "kadenSupport" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    if "kadenSupport_f" in atkSkills:
        atkCombatBuffs[DEF] += 2
        atkCombatBuffs[RES] += 2
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "kadenSupport_f" in defSkills:
        defCombatBuffs[DEF] += 2
        defCombatBuffs[RES] += 2
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Foxkit Fang (Base) - Selkie
    if "selkieBoost" in atkSkills and atkStats[RES] + atkPhantomStats[RES] > defStats[RES] + defPhantomStats[RES] and defender.wpnType in MELEE_WEAPONS:
        difference = (atkStats[RES] + atkPhantomStats[RES]) - (defStats[RES] + defPhantomStats[RES])

        atkCombatBuffs = [x + min(trunc(0.5 * difference), 8) for x in atkCombatBuffs]

    if "selkieBoost" in defSkills and defStats[RES] + defPhantomStats[RES] > atkStats[RES] + atkPhantomStats[RES] and attacker.wpnType in MELEE_WEAPONS:
        difference = (defStats[RES] + defPhantomStats[RES]) - (atkStats[RES] + atkPhantomStats[RES])

        defCombatBuffs = [x + min(trunc(0.5 * difference), 8) for x in defCombatBuffs]

    # Foxkit Fang (Refine Base) - Selkie
    if "selkieBoost2" in atkSkills and atkStats[RES] + atkPhantomStats[RES] > defStats[RES] + defPhantomStats[RES]:
        difference = (atkStats[RES] + atkPhantomStats[RES]) - (defStats[RES] + defPhantomStats[RES])

        atkCombatBuffs = [x + 4 + min(trunc(0.8 * difference), 8) for x in atkCombatBuffs]

    if "selkieBoost2" in defSkills and defStats[RES] + defPhantomStats[RES] > atkStats[RES] + atkPhantomStats[RES]:
        difference = (defStats[RES] + defPhantomStats[RES]) - (atkStats[RES] + atkPhantomStats[RES])

        defCombatBuffs = [x + 4 + min(trunc(0.8 * difference), 8) for x in defCombatBuffs]

    # Foxkit Fang (Refine Eff) - Selkie
    if "selkieOutres" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "selkieOutres" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    if "keatonBoost" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        defBonusesNeutralized[ATK] = True
        defBonusesNeutralized[DEF] = True
        atkr.spGainOnAtk += 1

    if "keatonBoost" in defSkills:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        atkBonusesNeutralized[ATK] = True
        atkBonusesNeutralized[DEF] = True
        defr.spGainOnAtk += 1

    if "velouriaPulse2" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "velouriaPulse2" in defSkills:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    if "velouriaBoost" in atkSkills and (attacker.transformed or defHPGreaterEqual75Percent):
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "velouriaBoost" in defSkills and (defender.transformed or atkHPGreaterEqual75Percent):
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Sword of the Creator (Base/Refine Base) - Byleth
    if "up b side b" in atkSkills or "down throw bair" in defSkills:
        atkr.defensive_tempo = True
        atkr.offensive_tempo = True
        atkr.defensive_NFU = True
        atkr.offensive_NFU = True

        if "down throw bair" in atkSkills:
            atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "up b side b" in defSkills or "down throw bair" in defSkills:
        defr.defensive_tempo = True
        defr.offensive_tempo = True
        defr.defensive_NFU = True
        defr.offensive_NFU = True

        if "down throw bair" in defSkills and defAllyWithin2Spaces:
            defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Sword of the Creator (Refine Eff) - Byleth
    if "HERE IS SOMETHING TO BELIEVE IN" in atkSkills:
        atkr.sp_pierce_DR = True
        if atkHPGreaterEqual25Percent:
            atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
            atkr.DR_first_hit_NSP.append(30)

    if "HERE IS SOMETHING TO BELIEVE IN" in defSkills:
        defr.sp_pierce_DR = True
        if defHPGreaterEqual25Percent:
            defCombatBuffs = [x + 4 for x in defCombatBuffs]
            defr.DR_first_hit_NSP.append(30)

    # Breaker Lance (Base) - Jeralt
    if "he lives" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 6
        defCombatBuffs[DEF] -= 6
        defr.follow_up_denials -= 1

    if "he lives" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 6
        atkCombatBuffs[DEF] -= 6
        atkr.follow_up_denials -= 1

    # Victorious Axe (Base) - Edelgard
    if "edelgardFU" in atkSkills and len(atkFoeWithin2Spaces) - 1 >= len(atkAllyWithin2Spaces):
        atkr.follow_ups_skill += 1

    if "edelgardFU" in defSkills and len(defFoeWithin2Spaces) - 1 >= len(defAllyWithin2Spaces):
        defr.follow_ups_skill += 1

    # Victorious Axe (Refine Base) - Edelgard
    if "edelgardRefineFU" in atkSkills and (atkHPGreaterEqual25Percent or len(atkFoeWithin2Spaces) - 1 >= len(atkAllyWithin2Spaces)):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.follow_ups_skill += 1

    if "edelgardRefineFU" in defSkills and (defHPGreaterEqual25Percent or len(defFoeWithin2Spaces) - 1 >= len(defAllyWithin2Spaces)):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.follow_ups_skill += 1

    # Victorious Axe (Refine Eff) - Edelgard
    if "another 3 years" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.true_stat_damages.append((ATK, 10))

    if "another 3 years" in defSkills and not defAdjacentToAlly:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.true_stat_damages.append((ATK, 10))

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

    # Hunting Blade (Base) - Petra
    if "petraEff" in atkSkills:
        for i in range(1, 5):
            if atkStats[i] + atkPhantomStats[i] < min([ally.get_visible_stat(i) + ally.get_phantom_stat_boost(i) for ally in atkAllyWithin2Spaces]):
                atkCombatBuffs[i] += 5

    if "petraEff" in defSkills:
        for i in range(1, 5):
            if defStats[i] + defPhantomStats[i] < min([ally.get_visible_stat(i) + ally.get_phantom_stat_boost(i) for ally in defAllyWithin2Spaces]):
                atkCombatBuffs[i] += 5

    # Hunting Blade (Refine Base) - Petra
    if "petraEffRefine" in atkSkills:
        if atkAllyWithin3Spaces:
            atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        for i in range(1, 5):
            if atkStats[i] + atkPhantomStats[i] - 4 < min([ally.get_visible_stat(i) + ally.get_phantom_stat_boost(i) for ally in atkAllyWithin3Spaces]):
                atkCombatBuffs[i] += 6

    if "petraEffRefine" in defSkills:
        if defAllyWithin3Spaces:
            defCombatBuffs = [x + 4 for x in defCombatBuffs]

        for i in range(1, 5):
            if defStats[i] + defPhantomStats[i] - 4 < min([ally.get_visible_stat(i) + ally.get_phantom_stat_boost(i) for ally in defAllyWithin3Spaces]):
                defCombatBuffs[i] += 6

    # Hunting Blade (Refine Eff) - Petra
    if "petraBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.offensive_NFU = True

        if defHPEqual100Percent:
            atkr.offensive_tempo = True
            atkr.DR_first_hit_NSP.append(60)

    if "petraBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.offensive_NFU = True

    # Breaker Bow (SU!Petra)
    if "summerPetraBoost" in atkSkills and atkHPGreaterEqual25Percent:
        defPenaltiesNeutralized[SPD] = True
        defPenaltiesNeutralized[DEF] = True

        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

        num_ally_high_atk = 0
        num_ally_high_spd = 0

        tiles_within_3_col = attacker.attacking_tile.tilesWithinNCols(3)
        tiles_within_3_row = attacker.attacking_tile.tilesWithinNRows(3)
        tiles_within_3_row_or_column = list(set(tiles_within_3_col) | set(tiles_within_3_row))

        for tile in tiles_within_3_row_or_column:
            if tile.hero_on != None and tile.hero_on.isAllyOf(attacker):
                ally_atk = tile.hero_on.get_visible_stat(ATK)

                if ally_atk >= 55: num_ally_high_atk += 1

                ally_spd = tile.hero_on.get_visible_stat(SPD)

                if ally_spd >= 40: num_ally_high_spd += 1

        # X is capped for stats, but not cooldown gain. Currently bugged?
        # https://twitter.com/i/status/1809296394047701142
        X = num_ally_high_atk + num_ally_high_spd

        atkCombatBuffs[ATK] += 6 * min(X, 3)
        atkCombatBuffs[SPD] += 6 * min(X, 3)

        if attacker.getSpecialType() == "Offense":
            A = X + 1
            B = max(X + 1 - atkr.start_of_combat_special, 0)

            atkr.sp_charge_first += A
            atkr.sp_charge_FU += B

    if "summerPetraBoost" in defSkills and defHPGreaterEqual25Percent:
        atkPenaltiesNeutralized[SPD] = True
        atkPenaltiesNeutralized[DEF] = True

        defCombatBuffs = [x + 5 for x in defCombatBuffs]

        num_ally_high_atk = 0
        num_ally_high_spd = 0

        tiles_within_3_col = defender.tile.tilesWithinNCols(3)
        tiles_within_3_row = defender.tile.tilesWithinNRows(3)
        tiles_within_3_row_or_column = list(set(tiles_within_3_col) | set(tiles_within_3_row))

        for tile in tiles_within_3_row_or_column:
            if tile.hero_on is not None and tile.hero_on.isAllyOf(defender):
                ally_atk = tile.hero_on.get_visible_stat(ATK)

                if ally_atk >= 55: num_ally_high_atk += 1

                ally_spd = tile.hero_on.get_visible_stat(SPD)

                if ally_spd >= 40: num_ally_high_spd += 1

        X = min(num_ally_high_atk + num_ally_high_spd, 3)

        defCombatBuffs[ATK] += 6 * X
        defCombatBuffs[SPD] += 6 * X

        if defender.getSpecialType() == "Offense":
            A = X + 1
            B = max(X + 1 - defr.start_of_combat_special, 0)

            defr.sp_charge_first += A
            defr.sp_charge_FU += B

    # Noble Lance (Base) - Dimitri
    if "with this lance I protect the lesbians" in atkSkills and (atkHPEqual100Percent == defHPEqual100Percent):
        atkr.follow_ups_skill += 1

    if "with this lance I protect the lesbians" in defSkills and (atkHPEqual100Percent == defHPEqual100Percent):
        defr.follow_ups_skill += 1

    # Noble Lance (Refine Base) - Dimitri
    if "with this lance I protect trans lesbians" in atkSkills and (not atkHPEqual100Percent or defHPGreaterEqual75Percent):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.follow_ups_skill += 1

    if "with this lance I protect trans lesbians" in defSkills and (not defHPEqual100Percent or atkHPGreaterEqual75Percent):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.follow_ups_skill += 1

    # Noble Lance (Refine Eff) - Dimitri
    if "of fire emblem" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.true_stat_damages.append((ATK, 10))
        atkr.TDR_stats.append((ATK, 10))
        atkr.damage_reduction_reduction.append(50)

    if "of fire emblem" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.true_stat_damages.append((ATK, 10))
        defr.TDR_stats.append((ATK, 10))
        defr.damage_reduction_reduction.append(50)

    # Flingster Spear (SP!Sylvain)
    if "sling a thing" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkr.offensive_NFU = True
        atkr.DR_first_strikes_NSP.append(40)
        if Status.SpecialCharge in attacker.statusPos:
            atkr.offensive_tempo = True

    # Freikugel (Base) - 3H!Hilda
    if "hildaField" in atkSkills and not any([ally.get_visible_stat(DEF) + ally.get_phantom_stat(DEF) > atkStats[DEF] + atkPhantomStats[DEF] for ally in atkAllyWithin2Spaces]):
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[SPD] += 6

    if "hildaField" in defSkills and not any([ally.get_visible_stat(DEF) + ally.get_phantom_stat(DEF) > defStats[DEF] + defPhantomStats[DEF] for ally in defAllyWithin2Spaces]):
        defCombatBuffs[ATK] += 6
        defCombatBuffs[SPD] += 6

    # Freikugel (Refine Base) - 3H!Hilda
    if "allyFoeDenial_f" in atkSkills:
        defr.follow_up_denials -= atkSkills["allyFoeDenial_f"]

    if "allyFoeDenial_f" in defSkills:
        atkr.follow_up_denials -= defSkills["allyFoeDenial_f"]

    if "hildaRefineField" in atkSkills and (not any([ally.get_visible_stat(DEF) > attacker.get_visible_stat(DEF) for ally in atkAllyWithin2Spaces]) or not atkAdjacentToAlly):
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[SPD] += 6
        atkr.true_stat_damages.append((SPD, 10))

    if "hildaRefineField" in defSkills and (not any([ally.get_visible_stat(DEF) > defender.get_visible_stat(DEF) for ally in defAllyWithin2Spaces]) or not defAdjacentToAlly):
        defCombatBuffs[ATK] += 6
        defCombatBuffs[SPD] += 6
        defr.true_stat_damages.append((SPD, 10))

    # Freikugel (Refine Eff) - 3H!Hilda
    if "HILDA! HILDA!" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.DR_first_hit_NSP.append(40)

    if "HILDA! HILDA!" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.DR_first_hit_NSP.append(40)

    # Athame (Base) - Kronya
    if "kronyaVantage" in atkSkills and not defHPEqual100Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "kronyaVantage" in defSkills and not atkHPEqual100Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.vantage = True

    # Athame (Refine Base) - Kronya
    if "kronyaRefineVantage" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "kronyaRefineVantage" in defSkills and not atkHPEqual100Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.vantage = True

    # Athame (Refine Eff) - Kronya
    if "kronyaExposure" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 5, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("status", Status.Exposure, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "kronyaExposure" in defSkills and not defAdjacentToAlly:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Sublime Surge (Refine Eff) - Sothis
    if "finalsmash.png" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_first_hit_NSP.append(40)

    if "finalsmash.png" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_first_hit_NSP.append(40)

    # Sirius+ - Sothis
    if "sothisTempo" in atkSkills: atkr.offensive_tempo = True
    if "sothisTempo" in defSkills: defr.offensive_tempo = True

    # Reginn - Lyngheiðr - Base
    if "reginn :)" in atkSkills:
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[SPD] += 6
        atkr.DR_first_hit_NSP.append(30)

    # Dvergr Wayfinder (Base) - AI!Reginn
    # ok yeah 3 rows or cols is becoming a more common condition
    if "reginnAccel" in atkSkills and atkHPGreaterEqual25Percent:
        boost = min(len(atkAllyWithin3RowsCols) * 3 + 5, 14)
        atkCombatBuffs = [x + boost for x in atkCombatBuffs]

        atkr.true_stat_damages.append((SPD, 20))
        atkr.DR_first_strikes_NSP.append(40)
        atkr.sp_pierce_DR = True

    if "reginnAccel" in defSkills and defHPGreaterEqual25Percent:
        boost = min(len(defAllyWithin3RowsCols) * 3 + 5, 14)
        defCombatBuffs = [x + boost for x in defCombatBuffs]

        defr.true_stat_damages.append((SPD, 20))
        defr.DR_first_strikes_NSP.append(40)
        defr.sp_pierce_DR = True

    if "reginnField_f" in atkSkills and turn <= 4:
        atkCombatBuffs[ATK] += atkSkills["reginnField_f"]
        atkCombatBuffs[SPD] += atkSkills["reginnField_f"]
        if attacker.special is not None and attacker.special.type == "Offense":
            atkr.sp_charge_first += atkSkills["reginnField_f"] / 4

    if "reginnField_f" in defSkills and turn <= 4:
        defCombatBuffs[ATK] += defSkills["reginnField_f"]
        defCombatBuffs[SPD] += defSkills["reginnField_f"]
        if defender.special is not None and defender.special.type == "Offense":
            defr.sp_charge_first += defSkills["reginnField_f"] / 4

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
        atkCombatBuffs[1] += 2
        atkCombatBuffs[3] += 2

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
        #atkPostCombatHealing += 7

    if "Garfield You Fat Cat" in defSkills:
        defCombatBuffs[1] += max(4, 10 - 000000 * 3)  # 000000 - number of foes who have acted
        defCombatBuffs[2] += max(4, 10 - 000000 * 3)
        defCombatBuffs[3] += max(4, 10 - 000000 * 3)
        defCombatBuffs[4] += max(4, 10 - 000000 * 3)
        #defPostCombatHealing += 7

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

    # Maritime Arts (SU!F!Alear)
    if "summerAlearBoost" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

        ally_games_arr_3_spaces = []

        for ally in atkAllyWithin3Spaces:
            ally_games_arr_3_spaces.append(ally.game)

        num_dist_games = len(set(ally_games_arr_3_spaces))

        defCombatBuffs = [x - min(10, num_dist_games * 3 + 4) for x in defCombatBuffs]

        engaged_count = 0
        ally_games_arr_all = []

        for ally in atkAllAllies:
            ally_games_arr_all.append(ally.game)

            if ally.emblem != None:
                engaged_count += 1

        X = min(15, 5 * len(set(ally_games_arr_all)) + engaged_count)

        atkr.true_all_hits += X
        atkr.TDR_first_strikes += X

        atkr.offensive_tempo = True

    if "summerAlearBoost" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 5 for x in defCombatBuffs]

        ally_games_arr_3_spaces = []

        for ally in defAllyWithin3Spaces:
            ally_games_arr_3_spaces.append(ally.game)

        num_dist_games = len(set(ally_games_arr_3_spaces))

        atkCombatBuffs = [x - min(10, num_dist_games * 3 + 4) for x in atkCombatBuffs]

        engaged_count = 0
        ally_games_arr_all = []

        for ally in defAllAllies:
            ally_games_arr_all.append(ally.game)

            if ally.emblem != None:
                engaged_count += 1

        X = min(15, 5 * len(set(ally_games_arr_all)) + engaged_count)

        defr.true_all_hits += X
        defr.TDR_first_strikes += X

        defr.offensive_tempo = True

    # Bond Blast (SU!Alear)
    if "summerAlearBonds" in atkSkills:
        # Special-piercing effect

        bonded_cond = False
        for ally in atkAllAllies:
            # Support partner present
            if ally.allySupport == attacker.intName:
                bonded_cond = True
            # Ally with bonded present
            if Status.Bonded in ally.statusPos:
                bonded_cond = True

        if bonded_cond:
            atkr.sp_pierce_DR = True

        # Special DR effect
        within_3_bonded_cond = False
        for ally in atkAllyWithin3Spaces:
            if ally.allySupport == attacker.intName or Status.Bonded in ally.statusPos:
                within_3_bonded_cond = True

        if within_3_bonded_cond:
            atkr.DR_sp_trigger_by_any_special_SP.append(40)

    # Enable for all support partners
    for ally in atkAllAllies:
        if "summerAlearBonds" in ally.getSkills() and attacker.allySupport == ally.intName:
            atkr.sp_pierce_DR = True

    # Enable for all allies with [Bonded]
    if Status.Bonded in attacker.statusPos:
        for ally in atkAllAllies:

            if "summerAlearBonds" in ally.getSkills():
                atkr.sp_pierce_DR = True

    if "summerAlearBonds" in defSkills:
        bonded_cond = False
        for ally in defAllAllies:
            # Support partner present
            if ally.allySupport == defender.intName:
                bonded_cond = True
            # Ally with bonded present
            if Status.Bonded in ally.statusPos:
                bonded_cond = True

        if bonded_cond:
            defr.sp_pierce_DR = True

        within_3_bonded_cond = False
        for ally in defAllyWithin3Spaces:
            if ally.allySupport == defender.intName or Status.Bonded in ally.statusPos:
                within_3_bonded_cond = True

        if within_3_bonded_cond:
            defr.DR_sp_trigger_by_any_special_SP.append(40)

    for ally in defAllAllies:
        if "summerAlearBonds" in ally.getSkills() and defender.allySupport == ally.intName:
            defr.sp_pierce_DR = True

    if Status.Bonded in defender.statusPos:
        for ally in defAllAllies:

            if "summerAlearBonds" in ally.getSkills():
                defr.sp_pierce_DR = True

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
        ignore_range = True
        if defAllyWithin3Spaces:
            defCombatBuffs = [x + 9 for x in defCombatBuffs]
            defr.DR_first_strikes_NSP.append(40)
        if defAllyWithin3Spaces >= 3:
            defr.pseudo_miracle = True

    if "hippity-hop" in atkSkills and atkAllyWithin3Spaces:
        Y = min(atkAllyWithin3Spaces * 3 + 5, 14)
        allies = attacker.attacking_tile.unitsWithinNSpaces(3, True)
        for x in allies:
            if x.getWeaponType() in ["RDragon", "BDragon", "GDragon", "CDragon"]:
                Y = 14
        atkCombatBuffs = [x + Y for x in atkCombatBuffs]
        atkr.defensive_tempo = True
        atkr.offensive_tempo = True
        atkr.DR_first_strikes_NSP.append(min(atkHPCur, 60))

    if "hippity-hop" in defSkills and defAllyWithin3Spaces:
        Y = min(defAllyWithin3Spaces * 3 + 5, 14)
        allies = defender.tile.unitsWithinNSpaces(3, True)
        for x in allies:
            if x.getWeaponType() in ["RDragon", "BDragon", "GDragon", "CDragon"]:
                Y = 14
        defCombatBuffs = [x + Y for x in atkCombatBuffs]
        defr.defensive_tempo = True
        defr.offensive_tempo = True
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
            team = attacker.attacking_tile.unitsWithinNSpaces(n=20, lookForSameSide=True)
            for x in team:
                if Status.Charge in x.statusPos:
                    charge_count += 1

        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]
        atkCombatBuffs[ATK] += min(charge_count * 4, 8)
        atkCombatBuffs[SPD] += min(charge_count * 4, 8)
        atkr.damage_reduction_reduction.append(50)

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
        defr.damage_reduction_reduction.append(50)

    if "nullBonuses" in atkSkills: defBonusesNeutralized = [True] * 5
    if "nullBonuses" in defSkills: atkBonusesNeutralized = [True] * 5

    if Status.NullBonuses in attacker.statusPos: defBonusesNeutralized = [True] * 5
    if Status.NullBonuses in defender.statusPos: atkBonusesNeutralized = [True] * 5

    if Status.NullPenalties in attacker.statusPos: atkPenaltiesNeutralized = [True] * 5
    if Status.NullPenalties in defender.statusPos: defPenaltiesNeutralized = [True] * 5

    if "nullCavBonuses" in atkSkills and defender.move == 1: defBonusesNeutralized = [True] * 5
    if "nullCavBonuses" in defSkills and attacker.move == 1: atkBonusesNeutralized = [True] * 5

    if "nullFlyBonuses" in atkSkills and defender.move == 2: defBonusesNeutralized = [True] * 5
    if "nullFlyBonuses" in defSkills and attacker.move == 2: atkBonusesNeutralized = [True] * 5

    if "nullMagicBonuses" in atkSkills and defender.wpnType in MAGICAL_WEAPONS: defBonusesNeutralized = [True] * 5
    if "nullMagicBonuses" in defSkills and attacker.wpnType in MAGICAL_WEAPONS: atkBonusesNeutralized = [True] * 5

    if "nullRangedBonuses" in atkSkills and defender.wpnType in RANGED_WEAPONS: defBonusesNeutralized = [True] * 5
    if "nullRangedBonuses" in defSkills and attacker.wpnType in RANGED_WEAPONS: atkBonusesNeutralized = [True] * 5

    if "sharenaDualChill" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4
        atkCombatBuffs[RES] += 4

    if "sharenaDualChill" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4
        defCombatBuffs[RES] += 4

    if "sharenaHealing" in atkSkills:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4
        atkCombatBuffs[RES] += 4

    if "sharenaHealing" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4
        defCombatBuffs[RES] += 4

    if "bridal_shenanigans" in atkSkills and atkHPGreaterEqual25Percent:
        local_boost = 0
        valid_area = list(set(attacker.attacking_tile.tilesWithinNCols(3)) | set(attacker.attacking_tile.tilesWithinNRows(3)))

        for tile in valid_area:
            if tile.hero_on is not None and tile.hero_on is not attacker and tile.hero_on.side == attacker.side:
                local_boost += 1
        atkCombatBuffs = [x + min(local_boost * 3 + 5, 14) for x in atkCombatBuffs]

        atkr.offensive_NFU = True
        atkr.defensive_NFU = True

        atkr.true_stat_damages.append((SPD, 20))

        atkr.all_hits_heal += min(spaces_moved_by_atkr * 3, 12)

    if "bridal_shenanigans" in defSkills and defHPGreaterEqual25Percent:
        local_boost = 0
        valid_area = list(set(defender.tile.tilesWithinNCols(3)) | set(defender.tile.tilesWithinNRows(3)))

        for tile in valid_area:
            if tile.hero_on is not None and tile.hero_on is not defender and tile.hero_on.side == defender.side:
                local_boost += 1
        defCombatBuffs = [x + min(local_boost * 3 + 5, 14) for x in defCombatBuffs]

        defr.offensive_NFU = True
        defr.defensive_NFU = True

        defr.true_stat_damages.append((SPD, 20))

        defr.all_hits_heal += min(spaces_moved_by_atkr * 3, 12)

    if "and they were roommates" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_all_hits_NSP.append(40)
        atkr.offensive_tempo = True
        atkr.defensive_tempo = True

    if "and they were roommates" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_all_hits_NSP.append(40)
        defr.offensive_tempo = True
        defr.defensive_tempo = True

    # Valaskjálf - Bruno
    if "brunoVantage" in defSkills and defHPCur / defStats[HP] <= 0.50:
        defr.vantage = True

    # Hliðskjálf (Base) - B!Veronica
    if "veronicaBuffs" in atkSkills:
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_atk", 4, "self_and_allies", "within_2_spaces_self"))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_spd", 4, "self_and_allies", "within_2_spaces_self"))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_def", 4, "self_and_allies", "within_2_spaces_self"))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_res", 4, "self_and_allies", "within_2_spaces_self"))

        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_atk", 4, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_spd", 4, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_def", 4, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_res", 4, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "veronicaBuffs" in defSkills:
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_atk", 4, "self_and_allies", "within_2_spaces_self"))
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_spd", 4, "self_and_allies", "within_2_spaces_self"))
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_def", 4, "self_and_allies", "within_2_spaces_self"))
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("buff_res", 4, "self_and_allies", "within_2_spaces_self"))

        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_atk", 4, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_spd", 4, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_def", 4, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("debuff_res", 4, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Veðrfölnir's Egg (Base) - SP!Veronica
    if "spVeronicaBoost" in atkSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "spVeronicaBoost" in defSkills and defHPGreaterEqual75Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    if "spVeronicaAlly" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        highest_total = 0

        for ally in atkAllyWithin2Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            cur_total = 0

            i = 1
            while i < 5:
                cur_total += ally.buffs[i]
                i += 1

            highest_total = max(highest_total, cur_total)

        atkCombatBuffs[ATK] += highest_total

    if "spVeronicaAlly" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

        highest_total = 0

        for ally in defAllyWithin2Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            cur_total = 0

            i = 1
            while i < 5:
                cur_total += ally.buffs[i]
                i += 1

            highest_total = max(highest_total, cur_total)

        defCombatBuffs[ATK] += highest_total

    if "spVeronicaOrders" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "spVeronicaOrders" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    if "reFjorm" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkBonusesNeutralized = [True] * 5

    if "reFjorm" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defBonusesNeutralized = [True] * 5
        defCombatBuffs[DEF] += 4
        defCombatBuffs[RES] += 4

    # Gjallarbrú (Refine Eff) - BR!Fjorm
    if "brFjormField" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "brFjormField" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    if "gunnBoost" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[SPD] -= 4
        defCombatBuffs[RES] -= 4

    if "gunnBoost" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[SPD] -= 4
        atkCombatBuffs[RES] -= 4

    if "ylgrBoost" in atkSkills and atkStats[SPD] + atkPhantomStats[SPD] > defStats[SPD] + defPhantomStats[SPD]:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "ylgrBoost" in defSkills and defStats[SPD] + defPhantomStats[SPD] > atkStats[SPD] + atkPhantomStats[SPD]:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

    if "ylgrMoreBoost" in atkSkills and (atkStats[SPD] + atkPhantomStats[SPD] > defStats[SPD] + defPhantomStats[SPD] or defHPGreaterEqual75Percent):
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.true_stat_damages.append((SPD, 15))

    if "ylgrMoreBoost" in defSkills and (defStats[SPD] + defPhantomStats[SPD] > atkStats[SPD] + atkPhantomStats[SPD] or atkHPGreaterEqual75Percent):
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.true_stat_damages.append((SPD, 15))

    if "oh and stats" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "oh and stats" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    if "laevPartner" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5

    if "laevPartner" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5

    if "niuBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.defensive_NFU, atkr.offensive_NFU = True

    if "niuBoost" in defSkills and defHPGreaterEqual25Percent:
        defr.defensive_NFU, defr.offensive_NFU = True
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Býleistr (Base Refine) - Helbindi
    if "helbindiWave" in atkSkills and (defHPGreaterEqual75Percent or turn % 2 == 1):
        atkCombatBuffs[ATK] += 5
        defCombatBuffs[ATK] -= 5

    if "helbindiWave" in defSkills and (atkHPGreaterEqual75Percent or turn % 2 == 1):
        defCombatBuffs[ATK] += 5
        atkCombatBuffs[ATK] -= 5

    if "helbindiBoost" in atkSkills:
        atkCombatBuffs[ATK] += 5
        defCombatBuffs[ATK] -= 5
        defr.follow_up_denials -= 1

    if "helbindiBoost" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        atkCombatBuffs[ATK] -= 5
        atkr.follow_up_denials -= 1

    # Hikami (Refine Base) - NY!Gunnthrá
    if "hikamiThreaten2" in atkSkills and atkHPGreaterEqual25Percent:
        defCombatBuffs[ATK] -= 4
        defCombatBuffs[SPD] -= 4
        defCombatBuffs[DEF] -= 4

    if "hikamiThreaten2" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] -= 4
        atkCombatBuffs[SPD] -= 4
        atkCombatBuffs[DEF] -= 4

    # Lyngheiðr (Base) - Eir
    if "eirBoost" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4
        defr.follow_up_denials -= 1

        atkPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 4, "self", "one"))

    if "eirBoost" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

        defPostCombatEffs[GIVEN_UNIT_ATTACKED].append(("damage", 4, "self", "one"))

    # Lyngheiðr (Refine Base) - Eir
    if "eirRefineBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        defr.follow_up_denials -= 1
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "eirRefineBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Lyngheiðr (Refine Eff) - Eir
    if "eirRestore" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        atkCombatBuffs[ATK] += trunc(0.20 * atkHPCur)
        atkCombatBuffs[RES] += trunc(0.20 * atkHPCur)

        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self_and_allies", "within_2_spaces_self"))

    if "eirRestore" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

        defCombatBuffs[ATK] += trunc(0.20 * defHPCur)
        defCombatBuffs[RES] += trunc(0.20 * defHPCur)

        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self_and_allies", "within_2_spaces_self"))

    # Sparkling Boost+ (Eir)
    if "eirField_f" in atkSkills and atkHPGreaterEqual50Percent:
        atkCombatBuffs[RES] += atkSkills["eirField_f"]
    if "eirField_f" in defSkills and defHPGreaterEqual50Percent:
        defCombatBuffs[RES] += defSkills["eirField_f"]


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

    # Ífingr (Base) - Thrasir
    if "thrasirBoost" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.defensive_NFU = True
        atkPostCombatEffs[UNCONDITIONAL].append(("debuff_omni", 4, "allies", "nearest_self"))

    if "thrasirBoost" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.defensive_NFU = True
        defPostCombatEffs[UNCONDITIONAL].append(("debuff_omni", 4, "allies", "nearest_self"))

    # Ífingr (Refine Base) - Thrasir
    if "thrasirRefineBoost" in atkSkills and atkAllyWithin3Spaces:
        atkCombatBuffs = [x + 6 for x in atkCombatBuffs]
        atkr.defensive_NFU = True
        atkr.offensive_NFU = True
        atkPostCombatEffs[UNCONDITIONAL].append(("debuff_omni", 4, "allies", "nearest_self"))

    if "thrasirRefineBoost" in defSkills and defAllyWithin3Spaces:
        defCombatBuffs = [x + 6 for x in defCombatBuffs]
        atkr.defensive_NFU = True
        atkr.offensive_NFU = True
        defPostCombatEffs[UNCONDITIONAL].append(("debuff_omni", 4, "allies", "nearest_self"))

    # Ífingr (Refine Eff) - Thrasir
    if "You should really give her an alt, IS" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defBonusesNeutralized[SPD] = True
        defBonusesNeutralized[RES] = True

    if "You should really give her an alt, IS" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkBonusesNeutralized[SPD] = True
        atkBonusesNeutralized[RES] = True

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

    if "sleepy head" in defSkills and defHPGreaterEqual25Percent:
        atkCombatBuffs[1] -= 5
        atkCombatBuffs[3] -= 5
        defr.follow_ups_skill += 1

    if "the_dose" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.capped_foe_burn_damage = max(atkr.capped_foe_burn_damage, 8)
        X = trunc(atkStats[DEF] * 0.2) + 6
        defCombatBuffs[ATK] -= X
        defCombatBuffs[DEF] -= X
        atkr.damage_reduction_reduction.append(50)
        atkr.true_all_hits += trunc(defStats[HP] * 0.3)
        atkr.TDR_dmg_taken_cap = 20
        if defender.getSpecialType() == "Offense":
            atkr.TDR_dmg_taken_extra_stacks += 1

    if "lokiGuard" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[SPD] += 4

    if "lokiGuard" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 4
        defCombatBuffs[SPD] += 4

        # reduce damage by Y
        # Y = damage dealt to foe, max 20
        # if hit by offensive special, reduce damage by 2Y

    # Beast Weapons
    if attacker.transformed:
        if "infantryBeastA" in atkSkills:
            atkr.true_sp += 10
        elif "infantryBeastB" in atkSkills:
            atkr.true_sp += 7
            atkr.offensive_tempo = True
            atkr.defensive_tempo = True
        elif "cavalryBeastA" in atkSkills:
            defCombatBuffs[ATK] -= 4
            defCombatBuffs[DEF] -= 4
            defr.follow_up_denials -= 1
        elif "cavalryBeastB" in atkSkills:
            defCombatBuffs[ATK] -= min(spaces_moved_by_atkr + 3, 6)
            defCombatBuffs[DEF] -= min(spaces_moved_by_atkr + 3, 6)

            if min(spaces_moved_by_atkr + 3, 6) >= 5:
                atkr.DR_first_hit_NSP.append(30)

    if defender.transformed:
        if "infantryBeastA" in defSkills:
            defr.true_sp += 10
        elif "infantryBeastB" in defSkills:
            defr.true_sp += 7
            defr.offensive_tempo = True
            defr.defensive_tempo = True
        elif "cavalryBeastB" in defSkills:
            atkCombatBuffs[ATK] -= min(spaces_moved_by_atkr + 3, 6)
            atkCombatBuffs[DEF] -= min(spaces_moved_by_atkr + 3, 6)

            if min(spaces_moved_by_atkr + 3, 6) >= 5:
                defr.DR_first_hit_NSP.append(30)
        elif "armorBeastA" in defSkills:
            ignore_range = True

    if "Mario":
        "only Bros!"

    if "selfDmg" in atkSkills:  # damage to self after combat always
        atkPostCombatEffs[0].append(("damage", atkSkills["selfDmg"], "self", "one"))

    if "selfDmg" in defSkills:
        defPostCombatEffs[0].append(("damage", defSkills["selfDmg"], "self", "one"))

    # Devil Axe
    if "atkOnlySelfDmg" in atkSkills:  # damage to attacker after combat iff attacker had attacked
        atkPostCombatEffs[2].append(("damage", atkSkills["atkOnlySelfDmg"], "self", "one"))

    if "atkOnlySelfDmg" in defSkills:  # damage to attacker after combat iff attacker had attacked
        defPostCombatEffs[2].append(("damage", defSkills["atkOnlySelfDmg"], "self", "one"))

    # Pain
    if "atkOnlyOtherDmg" in atkSkills:  # damage to other unit after combat iff attacker had attacked
        atkPostCombatEffs[2].append(("damage", atkSkills["atkOnlyOtherDmg"], "foe", "one"))

    # Pain+
    if "painOther" in atkSkills:
        atkPostCombatEffs[2].append(("damage", atkSkills["painOther"], "foes_allies", "within_2_spaces_foe"))

    if "painOther" in defSkills:
        defPostCombatEffs[2].append(("damage", defSkills["painOther"], "foes_allies", "within_2_spaces_foe"))

    # Fear
    if "fear" in atkSkills: atkPostCombatEffs[2].append(("debuff_atk", atkSkills["fear"], "foe", "one"))
    if "fear" in defSkills: defPostCombatEffs[2].append(("debuff_atk", defSkills["fear"], "foe", "one"))

    # Fear+
    if "disperseFear" in atkSkills: atkPostCombatEffs[2].append(
        ("debuff_atk", atkSkills["disperseFear"], "foes_allies", "within_2_spaces_foe"))
    if "disperseFear" in defSkills: defPostCombatEffs[2].append(
        ("debuff_atk", defSkills["disperseFear"], "foes_allies", "within_2_spaces_foe"))

    # Slow
    if "slow" in atkSkills: atkPostCombatEffs[2].append(("debuff_spd", atkSkills["slow"], "foe", "one"))
    if "slow" in defSkills: defPostCombatEffs[2].append(("debuff_spd", defSkills["slow"], "foe", "one"))

    # Slow+
    if "disperseSlow" in atkSkills: atkPostCombatEffs[2].append(
        ("debuff_spd", atkSkills["disperseSlow"], "foes_allies", "within_2_spaces_foe"))
    if "disperseSlow" in defSkills: defPostCombatEffs[2].append(
        ("debuff_spd", defSkills["disperseSlow"], "foes_allies", "within_2_spaces_foe"))

    # Gravity
    if "gravity" in atkSkills: atkPostCombatEffs[2].append(("status", Status.Gravity, "foe", "one"))
    if "gravity" in defSkills: defPostCombatEffs[2].append(("status", Status.Gravity, "foe", "one"))

    if "disperseGravity" in atkSkills: atkPostCombatEffs[2].append(
        ("status", Status.Gravity, "foe_and_foes_allies", "within_1_spaces_foe"))
    if "disperseGravity" in defSkills: defPostCombatEffs[2].append(
        ("status", Status.Gravity, "foe_and_foes_allies", "within_1_spaces_foe"))

    # Panic
    if "panic" in atkSkills: atkPostCombatEffs[2].append(("status", Status.Panic, "foe", "one"))
    if "panic" in defSkills: defPostCombatEffs[2].append(("status", Status.Panic, "foe", "one"))

    if "dispersePanic" in atkSkills: atkPostCombatEffs[2].append(
        ("status", Status.Panic, "foe_and_foes_allies", "within_2_spaces_foe"))
    if "dispersePanic" in defSkills: defPostCombatEffs[2].append(
        ("status", Status.Panic, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Absorb+
    if "disperseAbsorb" in atkSkills:
        atkPostCombatEffs[2].append(("heal", atkSkills["disperseAbsorb"], "allies", "within_2_spaces_self"))
    if "disperseAbsorb" in defSkills:
        defPostCombatEffs[2].append(("heal", defSkills["disperseAbsorb"], "allies", "within_2_spaces_self"))

    # Flash/Candlelight
    if "flash" in atkSkills:
        atkPostCombatEffs[2].append(("status", Status.Flash, "foe", "one"))
    if "flash" in defSkills:
        defPostCombatEffs[2].append(("status", Status.Flash, "foe", "one"))

    if "disperseFlash" in atkSkills:
        atkPostCombatEffs[2].append(("status", Status.Flash, "foe_and_foes_allies", "within_2_spaces_foe"))
    if "disperseFlash" in defSkills:
        defPostCombatEffs[2].append(("status", Status.Flash, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Trilemma
    if "trilemma" in atkSkills:
        atkPostCombatEffs[2].append(("status", Status.TriAdept, "foe", "one"))
    if "trilemma" in defSkills:
        defPostCombatEffs[2].append(("status", Status.TriAdept, "foe", "one"))

    if "disperseTrilemma" in atkSkills:
        atkPostCombatEffs[2].append(("status", Status.TriAdept, "foe_and_foes_allies", "within_2_spaces_foe"))
    if "disperseTrilemma" in defSkills:
        defPostCombatEffs[2].append(("status", Status.TriAdept, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Witchy Wand
    if "spReset" in atkSkills:
        atkPostCombatEffs[2].append(("sp_reset", 99, "foe", "one"))
        atkPostCombatEffs[2].append(("status", Status.Guard, "foe", "one"))
    if "spReset" in defSkills:
        defPostCombatEffs[2].append(("sp_reset", 99, "foe", "one"))
        defPostCombatEffs[2].append(("status", Status.Guard, "foe", "one"))

    if "disperseSpReset" in atkSkills:
        atkPostCombatEffs[2].append(("sp_reset", 99, "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("status", Status.Guard, "foe_and_foes_allies", "within_2_spaces_foe"))
    if "disperseSpReset" in defSkills:
        defPostCombatEffs[2].append(("sp_reset", 99, "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("status", Status.Guard, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Triangle Adept
    if "triAdept" in atkSkills: atkr.triangle_adept_level = atkSkills["triAdept"] * 0.05 + 0.05
    if "triAdeptW" in atkSkills: atkr.triangle_adept_level = 0.20
    if Status.TriAdept in attacker.statusNeg: atkr.triangle_adept_level = 0.20
    if "azuraTriangle" in atkSkills and atkHPGreaterEqual25Percent: atkr.triangle_adept_level = 0.20

    if "triAdept" in defSkills: defr.triangle_adept_level = defSkills["triAdept"] * 0.05 + 0.05
    if "triAdeptW" in defSkills: defr.triangle_adept_level = 0.20
    if Status.TriAdept in defender.statusNeg: defr.triangle_adept_level = 0.20
    if "azuraTriangle" in defSkills and defHPGreaterEqual25Percent: defr.triangle_adept_level = 0.20

    # Cancel Affinity Skill
    # For all levels (not status), self TA effects are neutralized
    # For Lv1, foe TA effects are neutralized
    # For Lv2, foe TA effects are neutralized iff foe has Wpn advantage
    # For Lv3, foe TA effects are reversed iff foe has Wpn advantage
    # For Status, foe TA effects are reversef iff for has Wpn advantage
    if "cancelTA" in atkSkills: atkr.cancel_affinity_level = atkSkills["cancelTA"]
    if "cancelTA" in defSkills: defr.cancel_affinity_level = defSkills["cancelTA"]

    # Owl Tome
    if "owlBoost" in atkSkills:
        atkCombatBuffs = [x + 2 * len(atkAdjacentToAlly) for x in atkCombatBuffs]

    if "owlBoost" in defSkills:
        defCombatBuffs = [x + 2 * len(defAdjacentToAlly) for x in defCombatBuffs]

    # Fox Tome
    if "foxPenalty" in atkSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Brave, Attack Twice, the one and only
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

    if "cDaggerBreakW" in atkSkills and defender.wpnType == "CDagger":
        atkr.follow_ups_skill += 1;
        defr.follow_up_denials -= 1
    if "cDaggerBreakW" in defSkills and attacker.wpnType == "CDagger":
        defr.follow_ups_skill += 1;
        atkr.follow_up_denials -= 1

    # Dull Ranged (Skill)
    if "dullRanged" in atkSkills and defender.wpnType in RANGED_WEAPONS and atkHPCur / atkStats[0] > 1.5 - 0.5 * \
            atkSkills["dullRanged"]:
        defBonusesNeutralized = [True] * 5

    if "dullRanged" in defSkills and attacker.wpnType in RANGED_WEAPONS and defHPCur / defStats[0] > 1.5 - 0.5 * \
            defSkills["dullRanged"]:
        atkBonusesNeutralized = [True] * 5

    # Dull Ranged (In Weapons)
    if "dullRangedW" in atkSkills and defender.wpnType in RANGED_WEAPONS: defBonusesNeutralized = [True] * 5
    if "dullRangedW" in defSkills and attacker.wpnType in RANGED_WEAPONS: atkBonusesNeutralized = [True] * 5

    # Dull Close (In Weapons)
    if "dullCloseW" in atkSkills and defender.wpnType in MELEE_WEAPONS: defBonusesNeutralized = [True] * 5
    if "dullCloseW" in defSkills and attacker.wpnType in MELEE_WEAPONS: atkBonusesNeutralized = [True] * 5

    if "spDamageAdd" in atkSkills:
        atkr.true_sp += atkSkills["spDamageAdd"]

    # Null Follow-Up
    if "NFU" in atkSkills and atkHPCur/atkStats[HP] >= 1.5 - 0.5 * atkSkills["NFU"]:
        atkr.defensive_NFU = True
        atkr.offensive_NFU = True

    if "NFU" in defSkills and defHPCur/defStats[HP] >= 1.5 - 0.5 * defSkills["NFU"]:
        defr.defensive_NFU = True
        defr.offensive_NFU = True

    if "firesweep" in atkSkills or "firesweep" in defSkills:
        cannotCounter = True

    if Status.Flash in defender.statusNeg:
        cannotCounter = True

    # Iron Dagger/Steel Dagger/Silver Dagger(+)
    if "dagger_single" in atkSkills:
        atkPostCombatEffs[2].append(("debuff_def", atkSkills["dagger_single"], "foe", "one"))
        atkPostCombatEffs[2].append(("debuff_res", atkSkills["dagger_single"], "foe", "one"))

    if "dagger_single" in defSkills:
        defPostCombatEffs[2].append(("debuff_def", defSkills["dagger_single"], "foe", "one"))
        defPostCombatEffs[2].append(("debuff_res", defSkills["dagger_single"], "foe", "one"))

    # Dagger 7 (or other magnitudes)
    if "dagger" in atkSkills:
        atkPostCombatEffs[2].append(("debuff_def", atkSkills["dagger"], "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("debuff_res", atkSkills["dagger"], "foe_and_foes_allies", "within_2_spaces_foe"))

    if "dagger" in defSkills:
        defPostCombatEffs[2].append(("debuff_def", defSkills["dagger"], "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("debuff_res", defSkills["dagger"], "foe_and_foes_allies", "within_2_spaces_foe"))

    # Rogue Dagger

    if "rogue_boost_single" in atkSkills:
        atkPostCombatEffs[2].append(("buff_def", atkSkills["rogue_boost_single"], "self", "one"))
        atkPostCombatEffs[2].append(("buff_res", atkSkills["rogue_boost_single"], "self", "one"))

    if "rogue_boost_single" in defSkills:
        defPostCombatEffs[2].append(("buff_def", defSkills["rogue_boost_single"], "self", "one"))
        defPostCombatEffs[2].append(("buff_res", defSkills["rogue_boost_single"], "self", "one"))

    if "rogue_boost" in atkSkills:
        atkPostCombatEffs[2].append(("buff_def", atkSkills["rogue_boost"], "self_and_allies", "within_2_spaces_self"))
        atkPostCombatEffs[2].append(("buff_res", atkSkills["rogue_boost"], "self_and_allies", "within_2_spaces_self"))

    if "rogue_boost" in defSkills:
        defPostCombatEffs[2].append(("buff_def", defSkills["rogue_boost"], "self_and_allies", "within_2_spaces_self"))
        defPostCombatEffs[2].append(("buff_res", defSkills["rogue_boost"], "self_and_allies", "within_2_spaces_self"))

    # Poison Dagger

    if "poison_dagger" in atkSkills and defender.move == 0:
        atkPostCombatEffs[2].append(("debuff_def", atkSkills["poison_dagger"], "foe", "one"))
        atkPostCombatEffs[2].append(("debuff_res", atkSkills["poison_dagger"], "foe", "one"))

    if "poison_dagger" in defSkills and attacker.move == 0:
        defPostCombatEffs[2].append(("debuff_def", defSkills["poison_dagger"], "foe", "one"))
        defPostCombatEffs[2].append(("debuff_res", defSkills["poison_dagger"], "foe", "one"))

    # Smoke Dagger
    if "smoke_others" in atkSkills:
        atkPostCombatEffs[2].append(("debuff_def", atkSkills["smoke_others"], "foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(("debuff_res", atkSkills["smoke_others"], "foes_allies", "within_2_spaces_foe"))

    if "smoke_others" in defSkills:
        defPostCombatEffs[2].append(("debuff_def", defSkills["smoke_others"], "foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(("debuff_res", defSkills["smoke_others"], "foes_allies", "within_2_spaces_foe"))

    if "spectrum_smoke" in atkSkills:
        atkPostCombatEffs[2].append(
            ("debuff_atk", atkSkills["spectrum_smoke"], "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(
            ("debuff_spd", atkSkills["spectrum_smoke"], "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(
            ("debuff_def", atkSkills["spectrum_smoke"], "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(
            ("debuff_res", atkSkills["spectrum_smoke"], "foe_and_foes_allies", "within_2_spaces_foe"))

    if "spectrum_smoke" in defSkills:
        defPostCombatEffs[2].append(
            ("debuff_atk", defSkills["spectrum_smoke"], "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(
            ("debuff_spd", defSkills["spectrum_smoke"], "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(
            ("debuff_def", defSkills["spectrum_smoke"], "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(
            ("debuff_res", defSkills["spectrum_smoke"], "foe_and_foes_allies", "within_2_spaces_foe"))

    # Kitty Paddle
    if "dagger_magic" in atkSkills and defender.wpnType in TOME_WEAPONS:
        atkPostCombatEffs[2].append(
            ("debuff_def", atkSkills["dagger_magic"], "foe_and_foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[2].append(
            ("debuff_res", atkSkills["dagger_magic"], "foe_and_foes_allies", "within_2_spaces_foe"))

    if "dagger_magic" in defSkills and attacker.wpnType in TOME_WEAPONS:
        defPostCombatEffs[2].append(
            ("debuff_def", defSkills["dagger_magic"], "foe_and_foes_allies", "within_2_spaces_foe"))
        defPostCombatEffs[2].append(
            ("debuff_res", defSkills["dagger_magic"], "foe_and_foes_allies", "within_2_spaces_foe"))

    seals = [("seal_atk", "sealAtk"), ("seal_spd", "sealSpd"), ("seal_def", "sealDef"), ("seal_res", "sealRes"),
             ("seal_atk", "sealAtkSe"), ("seal_spd", "sealSpdSe"), ("seal_def", "sealDefSe"), ("seal_res", "sealResSe")]

    for seal_name, skill_key in seals:
        if skill_key in atkSkills: atkPostCombatEffs[0].append((seal_name, atkSkills[skill_key], "foe", "one"))
        if skill_key in defSkills: defPostCombatEffs[0].append((seal_name, defSkills[skill_key], "foe", "one"))

    if "hardyBearing" in atkSkills:
        atkr.hardy_bearing = True
        defr.hardy_bearing = atkHPCur / atkStats[0] >= 1.5 - (atkSkills["hardyBearing"] * .5)

    if "hardyBearing" in defSkills:
        defr.hardy_bearing = True
        atkr.hardy_bearing = defHPCur / defStats[0] >= 1.5 - (defSkills["hardyBearing"] * .5)

    # Wrathful Staff
    if "wrathful" in atkSkills and atkHPCur / atkStats[HP] >= 1.5 - 0.5 * atkSkills["wrathful"]:
        atkr.wrathful_staff = True

    if "wrathful" in defSkills and defHPCur / defStats[HP] >= 1.5 - 0.5 * defSkills["wrathful"]:
        defr.wrathful_staff = True

    # Dazzling Staff
    if "dazzling" in atkSkills and atkHPCur / atkStats[HP] >= 1.5 - 0.5 * atkSkills["dazzling"]:
        cannotCounter = True

    # FIGHTER SKILLS
    if "wary_fighter" in atkSkills and atkHPCur / atkStats[HP] >= 1.1 - 0.2 * atkSkills["wary_fighter"]:
        atkr.follow_up_denials -= 1
        defr.follow_up_denials -= 1

    if "wary_fighter" in defSkills and defHPCur / defStats[HP] >= 1.1 - 0.2 * defSkills["wary_fighter"]:
        atkr.follow_up_denials -= 1
        defr.follow_up_denials -= 1

    if "bold_fighter" in atkSkills and atkHPCur / atkStats[HP] >= 1.5 - 0.5 * atkSkills["bold_fighter"]:
        atkr.follow_ups_skill += 1
        atkr.spGainOnAtk += 1

    if "vengeful_fighter" in defSkills and defHPCur / defStats[HP] >= 1.1 - 0.2 * defSkills["vengeful_fighter"]:
        defr.follow_ups_skill += 1
        defr.spGainOnAtk += 1

    if "crafty_fighter" in defSkills and defHPCur / defStats[HP] >= 1.0 - 0.25 * defSkills["crafty_fighter"]:
        defr.follow_ups_skill += 1
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "slick_fighter" in defSkills and defHPCur / defStats[HP] >= 1.0 - 0.25 * defSkills["slick_fighter"]:
        defr.follow_ups_skill += 1
        defPenaltiesNeutralized = [True] * 5

    if "special_fighter" in atkSkills and atkHPCur / atkStats[HP] >= 1.1 - 0.2 * atkSkills["special_fighter"]:
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "special_fighter" in defSkills and defHPCur / defStats[HP] >= 1.1 - 0.2 * defSkills["special_fighter"]:
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1
        atkr.spLossWhenAtkd -= 1
        atkr.spLossOnAtk -= 1

    if "odd_fighter" in atkSkills and atkHPCur / atkStats[HP] >= 1.5 - 0.5 * atkSkills["odd_fighter"] and turn % 2 == 1:
        atkr.follow_ups_skill += 1
        defr.follow_up_denials -= 1

    if "odd_fighter" in defSkills and defHPCur / defStats[HP] >= 1.5 - 0.5 * defSkills["odd_fighter"] and turn % 2 == 1:
        defr.follow_ups_skill += 1
        atkr.follow_up_denials -= 1

    # FLOW SKILLS
    if "flowRefresh" in atkSkills and atkHPCur / atkStats[HP] >= 1.5 - 0.5 * atkSkills["flowRefresh"]:
        atkr.offensive_NFU = True
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 10, "self", "one"))

    # idk what he's doing here
    if "NO MORE LOSSES" in defSkills and defAllyWithin3Spaces and defHPGreaterEqual50Percent:
        defr.pseudo_miracle = True

    # Special damage tags
    for key in atkSkills:
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
        if key == "atkBoostSpArmor": atkSpEffects.update({"atkBoostArmor": atkSkills[key]})
        if key == "wrathW": atkSpEffects.update({"wrathBoostW": atkSkills[key]})
        if key == "wrathSk": atkSpEffects.update({"wrathBoostSk": atkSkills[key]})
        if key == "spurnSk": atkSpEffects.update({"spurnBoostSk": atkSkills[key]})
        if key == "retaliatoryBoost": atkSpEffects.update({"retaliatoryBoost": atkSkills[key]})
        if key == "iceMirror": atkSpEffects.update({"iceMirror": 0})
        if key == "iceMirrorII": atkSpEffects.update({"iceMirrorII": 0})
        if key == "blueFlame": atkSpEffects.update({"blueFlame": 0})

    for key in defSkills:
        if key == "healSelf": defSpEffects.update({"healSelf": defSkills[key]})
        if key == "defReduce": defSpEffects.update({"defReduce": defSkills[key]})
        if key == "dmgBoost": defSpEffects.update({"dmgBoost": defSkills[key]})
        if key == "atkBoostSp": defSpEffects.update({"atkBoost": defSkills[key]})
        if key == "spdBoostSp": defSpEffects.update({"spdBoost": defSkills[key]})
        if key == "defBoostSp": defSpEffects.update({"defBoost": defSkills[key]})
        if key == "resBoostSp": defSpEffects.update({"resBoost": defSkills[key]})
        if key == "closeShield": defSpEffects.update({"closeShield": defSkills[key]})
        if key == "distantShield": defSpEffects.update({"distantShield": defSkills[key]})
        if key == "miracleSP": defSpEffects.update({"miracleSP": defSkills[key]})
        if key == "numFoeAtkBoostSp": defSpEffects.update({"NumAtkBoost": defSkills[key]})
        if key == "atkBoostSpArmor": defSpEffects.update({"atkBoostArmor": defSkills[key]})
        if key == "wrathW": defSpEffects.update({"wrathBoostW": defSkills[key]})
        if key == "wrathSk": defSpEffects.update({"wrathBoostSk": defSkills[key]})
        if key == "spurnSk": defSpEffects.update({"spurnBoostSk": defSkills[key]})
        if key == "retaliatoryBoost": defSpEffects.update({"retaliatoryBoost": defSkills[key]})
        if key == "iceMirror": defSpEffects.update({"iceMirror": 0})
        if key == "iceMirrorII": defSpEffects.update({"iceMirrorII": 0})
        if key == "blueFlame": defSpEffects.update({"blueFlame": 0})

    # COMMON A SKILLS, ENEMY PHASE ONLY


    if "stanceGuard" in defSkills:
        atkr.spGainWhenAtkd -= 1
        atkr.spGainOnAtk -= 1

    if "breathCharge" in defSkills:
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

    # Close/Distant Def.
    if "closeDef" in defSkills and attacker.wpnType in MELEE_WEAPONS:
        defCombatBuffs[DEF] += defSkills["closeDef"]
        defCombatBuffs[RES] += defSkills["closeDef"]

    if "distDef" in defSkills and attacker.wpnType in RANGED_WEAPONS:
        defCombatBuffs[DEF] += defSkills["distDef"]
        defCombatBuffs[RES] += defSkills["distDef"]

    # Close/Distant Guard
    if "closeGuard_f" in atkSkills and defender.wpnType in MELEE_WEAPONS:
        atkCombatBuffs[DEF] += atkSkills["closeGuard_f"]
        atkCombatBuffs[RES] += atkSkills["closeGuard_f"]

    if "closeGuard_f" in defSkills and attacker.wpnType in MELEE_WEAPONS:
        defCombatBuffs[DEF] += atkSkills["closeGuard_f"]
        defCombatBuffs[RES] += atkSkills["closeGuard_f"]

    if "distGuard_f" in atkSkills and defender.wpnType in RANGED_WEAPONS:
        atkCombatBuffs[DEF] += atkSkills["distGuard_f"]
        atkCombatBuffs[RES] += atkSkills["distGuard_f"]

    if "distGuard_f" in defSkills and attacker.wpnType in RANGED_WEAPONS:
        defCombatBuffs[DEF] += atkSkills["distGuard_f"]
        defCombatBuffs[RES] += atkSkills["distGuard_f"]

    if "DDpenalty" in defSkills and attacker.wpnType in RANGED_WEAPONS:
        atkBonusesNeutralized = [True] * 5

    if "amatsuDC" in defSkills and defHPGreaterEqual50Percent:
        ignore_range = True

    if "cCounter" in defSkills or "dCounter" in defSkills: ignore_range = True

    if "closePhysCounter" in defSkills and attacker.wpnType in PHYSICAL_WEAPONS:
        ignore_range = True

    if "BraveDW" in defSkills or "BraveBW" in defSkills:
        defr.brave = True

    if "atkOnlyOtherDmg" in defSkills:
        defPostCombatEffs[2].append(("damage", defSkills["atkOnlyOtherDmg"], "foe", "one"))

    # Quick Riposte
    if "QRW" in defSkills and defHPCur / defStats[0] >= 1.0 - (defSkills["QRW"] * 0.1): defr.follow_ups_skill += 1
    if "QRS" in defSkills and defHPCur / defStats[0] >= 1.0 - (defSkills["QRS"] * 0.1): defr.follow_ups_skill += 1
    if "QRSe" in defSkills and defHPCur / defStats[0] >= 1.0 - (defSkills["QRSe"] * 0.1): defr.follow_ups_skill += 1

    # Desperation
    if "desperationW" in atkSkills and atkHPCur / atkStats[0] <= 0.25 * atkSkills["desperationW"]:
        atkr.self_desperation = True

    if "desperationSk" in atkSkills and atkHPCur / atkStats[0] <= 0.25 * atkSkills["desperationSk"]:
        atkr.self_desperation = True

    if "desperationSe" in atkSkills and atkHPCur / atkStats[0] <= 0.25 * atkSkills["desperationSe"]:
        atkr.self_desperation = True

    if "stupidDesp" in atkSkills:
        defCombatBuffs[ATK] -= 5
        if (not atkHPEqual100Percent or spaces_moved_by_atkr >= 2):
            atkr.self_desperation = True

    if "stupidDesp" in defSkills:
        atkCombatBuffs[ATK] -= 5

    # Dive-Bomb
    if "dive_bomb" in atkSkills and atkHPCur / atkStats[HP] >= 1.1 - 0.1 * atkSkills["dive_bomb"] and defHPCur / defStats[HP] >= 1.1 - 0.1 * atkSkills["dive_bomb"]:
        atkr.self_desperation = True

    # Null C-Disrupt
    if "nullCounterattack" in defSkills and defHPCur / defStats[0] <= 1.5 - 0.5 * defSkills["nullCounterattack"]:
        disableCannotCounter = True

    if "nullC4" in atkSkills:
        defCombatBuffs[ATK] -= 4
        defCombatBuffs[SPD] -= 4
        atkr.DR_first_hit_NSP.append(30)

    if "nullC4" in defSkills:
        disableCannotCounter = True
        atkCombatBuffs[ATK] -= 4
        atkCombatBuffs[DEF] -= 4
        defr.DR_first_hit_NSP.append(30)

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

    if "vantage" in defSkills and defHPCur / defStats[HP] <= 0.75 - (0.25 * (3 - defSkills["vantage"])):
        defr.vantage = True

    if "vantageW" in defSkills and defHPCur / defStats[HP] <= 0.75:
        defr.vantage = True

    if Status.Vantage in defender.statusNeg:
        defr.vantage = True

    # 5 damage reduction from Shield Pulse, etc.
    if "trueDefsvSp" in atkSkills:
        atkr.TDR_on_def_sp += 5

    if "trueDefsvSp" in defSkills:
        defr.TDR_on_def_sp += 5

    # PART 1
    if "laguz_friend" in atkSkills:
        skill_lvl = atkSkills["laguz_friend"]
        if skill_lvl == 4: defStats[ATK] -= 5

        if attacker.getMaxSpecialCooldown() >= 3 and attacker.getSpecialType() == "Offense" or attacker.getSpecialType() == "Defense":
            defr.damage_reduction_reduction.append(50)
            atkr.sp_charge_foe_first += 2

    if "laguz_friend" in defSkills:
        skill_lvl = defSkills["laguz_friend"]
        if skill_lvl == 4: atkStats[ATK] -= 5

        if defender.getMaxSpecialCooldown() >= 3 and defender.getSpecialType() == "Offense" or defender.getSpecialType() == "Defense":
            atkr.damage_reduction_reduction.append(50)
            defr.sp_charge_foe_first += 2

    if "resonance" in atkSkills:
        X = max(trunc(0.2 * (atkStats[HP] - 20)), 0)

        atkr.self_burn_damage += X

        defCombatBuffs[SPD] -= 4
        defCombatBuffs[RES] -= 4

        atkr.resonance = True

    if "resonance" in defSkills:
        X = max(trunc(0.2 * (defStats[HP] - 20)), 0)

        defr.self_burn_damage += X

        atkCombatBuffs[SPD] -= 4
        atkCombatBuffs[RES] -= 4

        defr.resonance = True

    # LITERALLY EVERYTHING THAT USES BONUS AND PENALTY VALUES GOES HERE
    # INCLUDING [Bonus] AND [Penalty] KEYWORDS
    # Basically, no neutralizing bonuses/penalties past this point

    # exact value of buffs after buff neutralization
    atkNeutrBuffsStats = [0, 0, 0, 0, 0]
    defNeutrBuffsStats = [0, 0, 0, 0, 0]

    # exact value of buffs after debuff neutralization
    atkNeutrDebuffsStats = [0, 0, 0, 0, 0]
    defNeutrDebuffsStats = [0, 0, 0, 0, 0]

    # Values of each buff/debuff after neutralization
    for i in range(5):
        if AtkPanicFactor == 1:
            atkNeutrBuffsStats[i] += attacker.buffs[i] * int(not atkBonusesNeutralized[i])
        elif AtkPanicFactor == -1:
            atkNeutrDebuffsStats[i] += attacker.buffs[i] * -1 * int(not atkPenaltiesNeutralized[i])

        if DefPanicFactor == 1:
            defNeutrBuffsStats[i] += defender.buffs[i] * int(not defBonusesNeutralized[i])
        elif DefPanicFactor == -1:
            defNeutrDebuffsStats[i] += defender.buffs[i] * -1 * int(not defPenaltiesNeutralized[i])

        atkNeutrDebuffsStats[i] += attacker.debuffs[i] * int(not atkPenaltiesNeutralized[i])
        defNeutrDebuffsStats[i] += defender.debuffs[i] * int(not defPenaltiesNeutralized[i])

    # [Bonus] and [Penalty] keywords
    atkHasBonus = sum(atkNeutrBuffsStats) > 0 or attacker.statusPos
    atkHasPenalty = sum(atkNeutrDebuffsStats) < 0 or attacker.statusNeg

    defHasBonus = sum(atkNeutrBuffsStats) > 0 or defender.statusPos
    defHasPenalty = sum(atkNeutrDebuffsStats) < 0 or defender.statusNeg

    # Broadleaf Fan
    if "dominance" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[ATK] += defNeutrDebuffsStats[i]

    if "dominance" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[ATK] += atkNeutrDebuffsStats[i]

    # Scallop Blade/Big-Catch Bow/Petal Parasol
    if "elibeSummerPenalty" in atkSkills and defHasPenalty:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

    if "elibeSummerPenalty" in defSkills and atkHasPenalty:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

    # Blade Tomes
    if "bladeTome" in atkSkills:
        for i in range(1, 5): atkCombatBuffs[ATK] += atkNeutrBuffsStats[i]
    if "bladeTome" in defSkills:
        for i in range(1, 5): defCombatBuffs[ATK] += defNeutrBuffsStats[i]

    # Exalted Falchion (Refine Base) - L!Marth
    if "ILOVEBONUSES" in atkSkills and (atkHPGreaterEqual50Percent or atkHasBonus):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "ILOVEBONUSES" in defSkills and (defHPGreaterEqual50Percent or defHasBonus):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Uhhhh idk some Marth
    if "spectrumUnityMarth" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += 4 + atkNeutrDebuffsStats[i] * -2

    if "spectrumUnityMarth" in defSkills and defAllyWithin2Spaces:
        for i in range(1, 5):
            defCombatBuffs[i] += 4 + defNeutrDebuffsStats[i] * -2

    # Rowdy Sword (Refine Eff) - Luke
    if "BEAST MODE BABY" in atkSkills and sum(defNeutrBuffsStats) == 0:
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[DEF] += 6

    if "BEAST MODE BABY" in defSkills and sum(atkNeutrBuffsStats) == 0:
        defCombatBuffs[ATK] += 6
        defCombatBuffs[DEF] += 6

    # Sneering Axe (Base) - Legion
    if "legionBonusPunisher" in atkSkills:
        for i in range(1, 5): defCombatBuffs[i] -= defNeutrBuffsStats[i] * 2

    if "legionBonusPunisher" in defSkills:
        for i in range(1, 5): atkCombatBuffs[i] -= atkNeutrBuffsStats[i] * 2

    # Divine Mist (Refine Eff) - L!Y!Tiki
    if "LTikiBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defCombatBuffs[ATK] -= trunc(0.75 * (defNeutrBuffsStats[DEF] + defNeutrBuffsStats[RES]))

    if "LTikiBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkCombatBuffs[ATK] -= trunc(0.75 * (atkNeutrBuffsStats[DEF] + atkNeutrBuffsStats[RES]))

    # With Everyone! II - L!Y!Tiki
    if "I love you, and all you guys!" in defSkills and savior_triggered:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Razing Breath - FA!Y!Tiki
    if "Madden '94" in atkSkills and atkHPGreaterEqual25Percent:
        for i in range(1, 5):
            atkCombatBuffs[i] += 4 + atkNeutrBuffsStats[i]

        if atkHasBonus:
            atkr.follow_ups_skill += 1

    if "Madden '94" in defSkills and defHPGreaterEqual25Percent:
        for i in range(1, 5):
            defCombatBuffs[i] += 4 + defNeutrBuffsStats[i]

        if defHasBonus:
            atkr.follow_up_denials -= 1

    # Wizened Breath (Base)
    if "bantuBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        for i in range(1, 5):
            if not defPenaltiesNeutralized[i]:
                defCombatBuffs[i] -= max(6 - defNeutrDebuffsStats[i], 0)

    if "bantuBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

        for i in range(1, 5):
            if not atkPenaltiesNeutralized[i]:
                atkCombatBuffs[i] -= max(6 - atkNeutrDebuffsStats[i], 0)

    # Wizened Breath (Refine Eff)
    if "bantuFUDenial" in atkSkills and defHPGreaterEqual75Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defr.follow_up_denials -= 1

    if "bantuFUDenial" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkr.follow_up_denials -= 1

    # Mercurius (Refine Eff) - Astram
    if "yahoo" in atkSkills and atkAllyWithin3Spaces:
        highest_stats = [0] * 5

        for ally in atkAllyWithin3Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            i = 1
            while i < 5:
                cur_buff = ally.buffs[i]
                highest_stats[i] = max(highest_stats[i], cur_buff)
                i += 1

        for i in range(1, 5):
            atkCombatBuffs[i] += max(atkNeutrBuffsStats[i], max(highest_stats[i]))

    if "yahoo" in defSkills and defAllyWithin3Spaces:
        highest_stats = [0] * 5

        for ally in defAllyWithin3Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            i = 1
            while i < 5:
                cur_buff = ally.buffs[i]
                highest_stats[i] = max(highest_stats[i], cur_buff)
                i += 1

        for i in range(1, 5):
            defCombatBuffs[i] += max(defNeutrBuffsStats[i], max(highest_stats[i]))

    # Snide Bow (Refine Eff) - Python
    if "pythonBonusPunisher" in atkSkills:
        for i in range(2, 4): defCombatBuffs[i] -= 5 + defNeutrBuffsStats[i] * 2

    if "pythonBonusPunisher" in defSkills and defAllyWithin2Spaces:
        for i in range(2, 4): atkCombatBuffs[i] -= 5 + atkNeutrBuffsStats[i] * 2

    # Tome of Reason (Refine Eff) - Lugh
    if "lughBonus" in atkSkills:
        defCombatBuffs[ATK] -= trunc(0.60 * (atkNeutrBuffsStats[DEF] + atkNeutrBuffsStats[RES]))
        defCombatBuffs[RES] -= trunc(0.60 * (atkNeutrBuffsStats[DEF] + atkNeutrBuffsStats[RES]))

    if "lughBonus" in defSkills and defAllyWithin2Spaces:
        atkCombatBuffs[ATK] -= trunc(0.60 * (defNeutrBuffsStats[DEF] + defNeutrBuffsStats[RES]))
        atkCombatBuffs[RES] -= trunc(0.60 * (defNeutrBuffsStats[DEF] + defNeutrBuffsStats[RES]))

    # Icy Maltet (Refine Eff) - Thea
    if "theaBonusDoubler" in atkSkills and atkAllyWithin3Spaces:
        for i in range(1, 5):
            atkCombatBuffs[i] += 4 + atkNeutrBuffsStats[i]

    if "theaBonusDoubler" in defSkills and defAllyWithin3Spaces:
        for i in range(1, 5):
            defCombatBuffs[i] += 4 + defNeutrBuffsStats[i]

    # Wildcat Dagger (Base) - Chad
    if "chadBoost" in atkSkills and atkHPGreaterEqual25Percent:
        for i in range(1, 5):
            atkCombatBuffs[i] += 4 + defNeutrBuffsStats[i]
            defCombatBuffs[i] -= defNeutrBuffsStats[i]
            atkr.offensive_tempo = True

    if "chadBoost" in defSkills and defHPGreaterEqual25Percent:
        for i in range(1, 5):
            defCombatBuffs[i] += 4 + atkNeutrBuffsStats[i]
            atkCombatBuffs[i] -= atkNeutrBuffsStats[i]
            defr.offensive_tempo = True

    # Wildcat Dagger (Refine Eff) - Chad
    if "applewhite" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.DR_first_hit_NSP.append(30)
        atkr.true_stat_damages.append((SPD, 10))

    if "applewhite" in defSkills and atkHPGreaterEqual75Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.DR_first_hit_NSP.append(30)
        defr.true_stat_damages.append((SPD, 10))

    # Western Axe (Refine Eff) - Echidna
    if "echidnaUnitySpectrum" in atkSkills and defHPGreaterEqual75Percent:
        for i in range(1, 5):
            atkCombatBuffs += 4 + (-2 * atkNeutrDebuffsStats[i])

        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

    if "echidnaUnitySpectrum" in defSkills:
        for i in range(1, 5):
            defCombatBuffs += 4 + (-2 * defNeutrDebuffsStats[i])

        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

    # Runeaxe (Refine +Eff) - Narcian
    if "runeaxeBoost" in atkSkills and defHasPenalty: atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
    if "runeaxeBoost" in defSkills and atkHasPenalty: defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Eternal Breath (Refine Eff)
    if "faeBonus" in atkSkills and atkHasBonus:
        defCombatBuffs[ATK] -= 4
        defCombatBuffs[RES] -= 4
        atkr.spGainWhenAtkd += 1

    if "faeBonus" in defSkills and defHasBonus:
        atkCombatBuffs[ATK] -= 4
        atkCombatBuffs[RES] -= 4
        defr.spGainWhenAtkd += 1

    # Spy's Dagger (Refine Eff) - Matthew, + others reuse this effect
    if "mthwDominance" in atkSkills:
        for i in range(1, 5): atkCombatBuffs[ATK] += -1 * defNeutrDebuffsStats[i]
    if "mthwDominance" in defSkills:
        for i in range(1, 5): defCombatBuffs[ATK] += -1 * atkNeutrDebuffsStats[i]

    # The Cleaner
    if "the cleanerrrr" in atkSkills:
        for i in range(1, 5): atkCombatBuffs[ATK] += defNeutrBuffsStats[i]
    if "the cleanerrrr" in defSkills:
        for i in range(1, 5): defCombatBuffs[ATK] += atkNeutrBuffsStats[i]

    # Hurricane Dagger (Base) - Legault
    if "legaultBoost" in atkSkills and (defHPGreaterEqual75Percent or defHasBonus):
        atkCombatBuffs[SPD] += 5
        atkCombatBuffs[ATK] += 5

    if "legaultBoost" in defSkills and (atkHPGreaterEqual75Percent or atkHasBonus):
        atkCombatBuffs[SPD] += 5
        atkCombatBuffs[ATK] += 5

    # Fanged Basilikos
    if "linusBonusPunisher" in atkSkills and defHPGreaterEqual75Percent:
        defCombatBuffs[SPD] -= 5 + defNeutrBuffsStats[SPD]
        defCombatBuffs[DEF] -= 5 + defNeutrBuffsStats[DEF]

    if "linusBonusPunisher" in defSkills and atkHPGreaterEqual75Percent:
        atkCombatBuffs[SPD] -= 5 + atkNeutrBuffsStats[SPD]
        atkCombatBuffs[DEF] -= 5 + atkNeutrBuffsStats[DEF]

    if "braveEphFU" in atkSkills and (sum(atkNeutrBuffsStats) or Status.MobilityUp in attacker.statusPos):
        atkr.follow_ups_skill += 1

    if "braveEphFU" in defSkills and (sum(defNeutrBuffsStats) or Status.MobilityUp in defender.statusPos):
        defr.follow_ups_skill += 1

    if "braveEphFUPlus" in atkSkills and atkHasBonus:
        atkr.follow_ups_skill += 1
        atkr.offensive_NFU = True

    if "braveEphFUPlus" in defSkills and defHasBonus:
        defr.follow_ups_skill += 1
        defr.offensive_NFU = True

    # Reginleif (Refine Base) - Duo Ephraim
    if "what, it's just an ordianary weapon descrip-" in atkSkills and (atkStats[ATK] + atkPhantomStats[ATK] > defStats[ATK] + defPhantomStats[ATK] or atkHasBonus):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "what, it's just an ordianary weapon descrip-" in defSkills and (defStats[ATK] + defPhantomStats[ATK] > atkStats[ATK] + atkPhantomStats[ATK] or defHasBonus):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Reginleif (Refine Eff) - Duo Ephraim
    if "OH MY GOODNESS" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        if atkHasBonus:
            defr.follow_up_denials -= 1

    if "OH MY GOODNESS" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

        if defHasBonus:
            atkr.follow_up_denials -= 1

    # Grado Poleax (Refine Eff) - Amelia
    if "ameliaBoost" in atkSkills and (sum(atkNeutrBuffsStats) or Status.MobilityUp in attacker.statusPos):
        atkCombatBuffs[SPD] += 6
        atkCombatBuffs[DEF] += 6

    if "ameliaBoost" in defSkills and (sum(defNeutrBuffsStats) or Status.MobilityUp in defender.statusPos):
        defCombatBuffs[SPD] += 6
        defCombatBuffs[DEF] += 6

    # Weirding Tome (Refine Eff) - Lute
    if "luteBoost" in atkSkills and defHasPenalty:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "luteBoost" in defSkills and atkHasPenalty:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Desert-Tiger Axe (Refine Base) - Gerik
    if "gerikAxe" in atkSkills and atkAllyWithin3Spaces:
        highest_stats = [0] * 5

        for ally in atkAllyWithin3Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            i = 1
            while i < 5:
                cur_buff = ally.buffs[i]
                highest_stats[i] = max(highest_stats[i], cur_buff)
                i += 1

        for i in range(1, 5):
            atkCombatBuffs[i] += 4 +  max(atkNeutrBuffsStats[i], max(highest_stats[i]))

        atkr.DR_first_hit_NSP.append(30)
        atkr.offensive_tempo = True

    if "gerikAxe" in defSkills and defAllyWithin3Spaces:
        highest_stats = [0] * 5

        for ally in defAllyWithin3Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            i = 1
            while i < 5:
                cur_buff = ally.buffs[i]
                highest_stats[i] = max(highest_stats[i], cur_buff)
                i += 1

        for i in range(1, 5):
            defCombatBuffs[i] += 4 + max(defNeutrBuffsStats[i], max(highest_stats[i]))

        defr.DR_first_hit_NSP.append(30)
        defr.offensive_tempo = True

    # Father's-Son Axe (Refine Eff) - Ross
    if "hisFathersSonsFathersSonsFathersSons" in atkSkills:
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5
        atkr.true_stat_damages.append((HP, 15))
        atkPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    if "hisFathersSonsFathersSonsFathersSons" in defSkills and defAllyWithin2Spaces:
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5
        defr.true_stat_damages.append((HP, 15))
        defPostCombatEffs[UNCONDITIONAL].append(("heal", 7, "self", "one"))

    # Revenger Lance (Base) - Cormag
    if "WHY, WHY DID YOU DO THAT?????" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        if defHPGreaterEqual75Percent:
            atkr.follow_ups_skill += 1

    if "WHY, WHY DID YOU DO THAT?????" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

        if atkHPGreaterEqual75Percent:
            defr.follow_ups_skill += 1

    # Revenger Lance (Refine Eff) - Cormag
    if "cormagBoost" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.offensive_tempo = True
        atkr.TDR_stats.append((DEF, 15))

    if "cormagBoost" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.offensive_tempo = True
        defr.TDR_stats.append((DEF, 15))

    # Cursed Lance (Refine Eff) - Valter
    if "valterBoost" in atkSkills and defHasPenalty:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkCombatBuffs[DEF] += 5
        defr.spLossOnAtk -= 1
        defr.spLossWhenAtkd -= 1

    if "valterBoost" in defSkills and atkHasPenalty:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defCombatBuffs[DEF] += 5
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Light of Dawn (Base) - B!Micaiah
    if "micaiahBrave" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += -1 * defNeutrDebuffsStats[i]

    if "micaiahBrave" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += -1 * atkNeutrDebuffsStats[i]

    # Light of Dawn (Refine Base) - B!Micaiah
    if "dawnLight" in atkSkills and (defHPGreaterEqual75Percent or defHasPenalty):
        for i in range(1, 5):
            atkCombatBuffs[i] += 4 + (-1 * defNeutrDebuffsStats[i])

    if "dawnLight" in defSkills and (atkHPGreaterEqual75Percent or atkHasPenalty):
        for i in range(1, 5):
            defCombatBuffs[i] += 4 + (-1 * atkNeutrDebuffsStats[i])

    # Light of Dawn (Refine Eff) - B!Micaiah
    if "BATHED IN RADIANT DAWN" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[RES] += 6
        atkr.follow_ups_skill += 1

    if "BATHED IN RADIANT DAWN" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 6
        defCombatBuffs[RES] += 6
        defr.follow_ups_skill += 1

    # Chaos Manifest (Base) - Yune
    if "yunePenalty" in atkSkills and defHasPenalty:
        atkCombatBuffs[ATK] += 6
        atkr.follow_ups_skill += 1

    if "yunePenalty" in defSkills and atkHasPenalty:
        defCombatBuffs[ATK] += 6
        defr.follow_ups_skill += 1

    # Chaos Manifest (Refine Eff) - Yune
    if "yuneRefinePenalty" in atkSkills and (defHPGreaterEqual75Percent or defHasPenalty):
        atkCombatBuffs[ATK] += 6
        atkCombatBuffs[RES] += 5
        atkr.follow_ups_skill += 1

        highest_penalty_total = 0

        for foe in defAllyWithin2Spaces:
            foe_panic = Status.Panic in foe.statusNeg and Status.NullPanic not in foe.statusPos

            cur_penalty_total = 0

            i = 1
            while i < 5:
                cur_debuff = foe.debuffs[i]
                if foe_panic: cur_debuff += foe.buffs[i] * -1
                cur_penalty_total += cur_debuff

                i += 1

            highest_penalty_total = min(highest_penalty_total, cur_penalty_total)

        cur_penalty_total = 0

        i = 1
        while i < 5:
            cur_debuff = defNeutrDebuffsStats[i]
            cur_penalty_total += cur_debuff
            i += 1

        highest_penalty_total = min(highest_penalty_total, cur_penalty_total)

        atkr.DR_first_hit_NSP.append(-2 * highest_penalty_total)

    if "yuneRefinePenalty" in defSkills and (atkHPGreaterEqual75Percent or atkHasPenalty):
        defCombatBuffs[ATK] += 6
        defCombatBuffs[RES] += 5
        defr.follow_ups_skill += 1

    # Chaos Manifest (Refine Eff) - Yune
    if "yuneDmg" in atkSkills:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[RES] += 5

        highest_penalty_total = 0

        for foe in defAllyWithin2Spaces:
            foe_panic = Status.Panic in foe.statusNeg and Status.NullPanic not in foe.statusPos

            cur_penalty_total = 0

            i = 1
            while i < 5:
                cur_debuff = foe.debuffs[i]
                if foe_panic: cur_debuff += foe.buffs[i] * -1
                cur_penalty_total += cur_debuff

                i += 1

            highest_penalty_total = min(highest_penalty_total, cur_penalty_total)

        cur_penalty_total = 0

        i = 1
        while i < 5:
            cur_debuff = defNeutrDebuffsStats[i]
            cur_penalty_total += cur_debuff
            i += 1

        highest_penalty_total = min(highest_penalty_total, cur_penalty_total)

        atkr.true_all_hits += highest_penalty_total * -1

    if "yuneDmg" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[RES] += 5

        highest_penalty_total = 0

        for foe in atkAllyWithin2Spaces:
            foe_panic = Status.Panic in foe.statusNeg and Status.NullPanic not in foe.statusPos

            cur_penalty_total = 0

            i = 1
            while i < 5:
                cur_debuff = foe.debuffs[i]
                if foe_panic: cur_debuff += foe.buffs[i] * -1
                cur_penalty_total += cur_debuff

                i += 1

            highest_penalty_total = min(highest_penalty_total, cur_penalty_total)

        cur_penalty_total = 0

        i = 1
        while i < 5:
            cur_debuff = atkNeutrDebuffsStats[i]
            cur_penalty_total += cur_debuff
            i += 1

        highest_penalty_total = min(highest_penalty_total, cur_penalty_total)

        defr.true_all_hits += highest_penalty_total * -1

    # Sealed Falchion (Refine) - Awakening Falchion users + P!Chrom
    if "newSealedFalchion" in atkSkills and (not atkHPEqual100Percent or atkHasBonus):
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

    if "newSealedFalchion" in defSkills and (not defHPEqual100Percent or defHasBonus):
        defCombatBuffs = [x + 5 for x in defCombatBuffs]

    # Thögn (Refine Eff) - L!Lucina
    if "lucinaPenaltyPunisher" in atkSkills and atkAllyWithin3Spaces:
        for i in range(1, 4): defCombatBuffs[i] += -4 + defNeutrDebuffsStats[i]

    if "lucinaPenaltyPunisher" in defSkills and defAllyWithin3Spaces:
        for i in range(1, 4): atkCombatBuffs[i] += -4 + atkNeutrDebuffsStats[i]

    # Blade of Favors (Base) - Gregor
    if "gregorSword!" in atkSkills:
        atkr.DR_first_hit_NSP.append(40)
        for i in range(1, 5):
            defCombatBuffs[i] -= 5 + max(defender.debuffs[i] * defPenaltiesNeutralized[i] * -1, 0) + max(
                defender.buffs[i] * DefPanicFactor * defPenaltiesNeutralized[i] * -1, 0)

    if "gregorSword!" in defSkills and defAllyWithin2Spaces:
        defr.DR_first_hit_NSP.append(40)
        for i in range(1, 5):
            atkCombatBuffs -= 5 + max(attacker.debuffs[i] * atkPenaltiesNeutralized[i] * -1, 0) + max(
                attacker.buffs[i] * AtkPanicFactor * atkPenaltiesNeutralized[i] * -1, 0)

    # Aversa's Night (Refine Eff) - Aversa
    if "aversaPenaltyPunisher" in atkSkills and (defHPGreaterEqual75Percent or defHasPenalty):
        defCombatBuffs[ATK] -= 4 + defNeutrDebuffsStats[ATK]
        defCombatBuffs[SPD] -= 4 + defNeutrDebuffsStats[SPD]
        defCombatBuffs[RES] -= 4 + defNeutrDebuffsStats[RES]

    if "aversaPenaltyPunisher" in defSkills and (atkHPGreaterEqual75Percent or atkHasPenalty):
        atkCombatBuffs[ATK] -= 4 + atkNeutrDebuffsStats[ATK]
        atkCombatBuffs[SPD] -= 4 + atkNeutrDebuffsStats[SPD]
        atkCombatBuffs[RES] -= 4 + atkNeutrDebuffsStats[RES]

    # Oracle's Breath (Base) - Nah
    if "nahFUDenial" in atkSkills and sum(atkNeutrBuffsStats):
        defr.follow_up_denials -= 1

    if "nahFUDenial" in defSkills and sum(defNeutrBuffsStats):
        atkr.follow_up_denials -= 1

    # Oracle's Breath (Refine Base) - Nah
    if "nahRefineDenial" in atkSkills and (atkHPGreaterEqual50Percent or atkHasBonus):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defr.follow_up_denials -= 1

    if "nahRefineDenial" in defSkills and (defHPGreaterEqual50Percent or defHasBonus):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkr.follow_up_denials -= 1

    # Oracle's Breath (Refine Base) - Nah
    if "nahI'dWin" in atkSkills:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

        highest_stats = [0, 0, 0, 0, 0]
        for ally in atkAllyWithin2Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            i = 1
            while i < 5:
                cur_buff = ally.buffs[i]
                highest_stats[i] = max(highest_stats[i], cur_buff)
                i += 1

        i = 1
        while i < 5:
            atkCombatBuffs[i] += highest_stats[i]
            i += 1

    if "nahI'dWin" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

        highest_stats = [0, 0, 0, 0, 0]
        for ally in defAllyWithin2Spaces:
            ally_panic = Status.Panic in ally.statusNeg and Status.NullPanic not in ally.statusPos
            if ally_panic: continue

            i = 1
            while i < 5:
                cur_buff = ally.buffs[i]
                highest_stats[i] = max(highest_stats[i], cur_buff)
                i += 1

        i = 1
        while i < 5:
            defCombatBuffs[i] += highest_stats[i]
            i += 1

    # Lance of Heroics (Refine Eff) - Cynthia
    if "cynthiaBoost" in atkSkills and atkAllyWithin3Spaces:
        for i in range(1, 5):
            atkCombatBuffs[i] += 4 + atkNeutrDebuffsStats[i] * -2

    if "cynthiaBoost" in defSkills and defAllyWithin3Spaces:
        for i in range(1, 5):
            defCombatBuffs[i] += 4 + defNeutrDebuffsStats[i] * -2

    # Ancient Ragnell - Priam
    if "ancientRagnell" in atkSkills and (atkHPGreaterEqual50Percent or atkHasBonus):
        defCombatBuffs[1] -= 6
        defCombatBuffs[3] -= 6

    if "ancientRagnell" in defSkills and (defHPGreaterEqual50Percent or defHasBonus):
        atkCombatBuffs[1] -= 6
        atkCombatBuffs[3] -= 6

    # Gloom Breath (Refine Eff) - F!Corrin
    if "corrinPenaltyTheft" in atkSkills:
        for i in range(1, 5): atkCombatBuffs[i] += defNeutrDebuffsStats[i] * -1

    if "corrinPenaltyTheft" in defSkills:
        for i in range(1, 5): defCombatBuffs[i] += atkNeutrDebuffsStats[i] * -1

    # Setsuna's Yumi
    if "setsunaBonusBoost" in atkSkills and atkHasBonus:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkPenaltiesNeutralized[ATK] = True
        atkPenaltiesNeutralized[SPD] = True

    if "setsunaBonusBoost" in atkSkills and defHasBonus:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defPenaltiesNeutralized[ATK] = True
        defPenaltiesNeutralized[SPD] = True

    # Arthur's Axe
    if "arthurDebuffer" in atkSkills and (atkHasPenalty or not atkHPEqual100Percent):
        atkCombatBuffs = [x + 5 for x in atkCombatBuffs]

    if "arthurDebuffer" in defSkills and (defHasPenalty or not defHPEqual100Percent):
        defCombatBuffs = [x + 5 for x in defCombatBuffs]

    if "arthurBonus" in atkSkills and sum(atkNeutrBuffsStats) > 0:
        atkCombatBuffs = [x + 3 for x in atkCombatBuffs]

    if "arthurBonus" in defSkills and sum(defNeutrBuffsStats) > 0:
        defCombatBuffs = [x + 3 for x in defCombatBuffs]

    # Saizo's Star (Refine Eff) - Saizo
    if "saizoBoost" in atkSkills:
        for i in range(1, 5): atkCombatBuffs[i] += -1 * defNeutrDebuffsStats[i]
    if "saizoBoost" in defSkills:
        for i in range(1, 5): defCombatBuffs[i] += -1 * atkNeutrDebuffsStats[i]

    # Sun Dragonstone (Base) - Kana
    if "kanaBoost" in atkSkills and sum(atkNeutrBuffsStats):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
    if "kanaBoost" in defSkills:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Retainer's Report (Base) - Hubert
    if "hubertBoost" in atkSkills and (defHPGreaterEqual75Percent or defHasPenalty):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.follow_ups_skill += 1

    if "hubertBoost" in defSkills and (atkHPGreaterEqual75Percent or atkHasPenalty):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.follow_ups_skill += 1

    # Retainer's Report (Refine Eff) - Hubert
    if "hubertRuse" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]

    if "hubertRuse" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]

    # Cunning Bow (Base) - Claude
    if "claudeDebuff" in atkSkills and sum(atkNeutrBuffsStats) + abs(sum(defNeutrDebuffsStats)) >= 10:
        defCombatBuffs = [x - 5 for x in defCombatBuffs]

    if "claudeDebuff" in defSkills and sum(defNeutrBuffsStats) + abs(sum(atkNeutrDebuffsStats)) >= 10:
        atkCombatBuffs = [x - 5 for x in atkCombatBuffs]

    # Cunning Bow (Refine Base) - Claude
    if "claudeRefineDebuff" in atkSkills:
        if atkHasBonus or defHasPenalty:
            defCombatBuffs = [x - 5 for x in defCombatBuffs]

        stat_total = sum(atkNeutrBuffsStats) + abs(sum(defNeutrDebuffsStats))

        atkr.DR_first_hit_NSP.append(min(stat_total * 3), 60)

        if stat_total > 10: atkr.offensive_NFU = True

    if "claudeRefineDebuff" in defSkills:
        if defHasBonus or atkHasPenalty:
            atkCombatBuffs = [x - 5 for x in atkCombatBuffs]

        stat_total = sum(defNeutrBuffsStats) + abs(sum(atkNeutrDebuffsStats))

        if stat_total > 10: defr.offensive_NFU = True

    # Cunning Bow (Refine Eff) - Claude
    if "three houses discourse" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5

        atkCombatBuffs[ATK] += atkNeutrBuffsStats[ATK]
        defCombatBuffs[DEF] += defNeutrDebuffsStats[DEF]

    if "three houses discourse" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5

        defCombatBuffs[ATK] += defNeutrBuffsStats[ATK]
        atkCombatBuffs[DEF] += atkNeutrDebuffsStats[DEF]

    # Warrior's Sword (Base) - Holst
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

    # Scythe of Sariel (Base) - Death Knight
    if "oh boy I hope there's no magic babies outside my house today" in atkSkills and (sum(defNeutrBuffsStats) or Status.MobilityUp in defender.statusPos):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defr.follow_up_denials -= 1

    if "oh boy I hope there's no magic babies outside my house today" in defSkills and (sum(atkNeutrBuffsStats) or Status.MobilityUp in attacker.statusPos):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkr.follow_up_denials -= 1

    # Scythe of Sariel (Refine Base) - Death Knight
    if "scytheRef" in atkSkills and (defHasBonus or defHPGreaterEqual75Percent):
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        defr.follow_up_denials -= 1

    if "scytheRef" in defSkills and (atkHasBonus or atkHPGreaterEqual75Percent):
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        atkr.follow_up_denials -= 1

    # Scythe of Sariel (Refine Eff) - Death Knight
    if "deathScythe" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs = [x + 4 for x in atkCombatBuffs]
        atkr.follow_ups_skill += 1

    if "deathScythe" in defSkills and defHPGreaterEqual25Percent:
        defCombatBuffs = [x + 4 for x in defCombatBuffs]
        defr.follow_ups_skill += 1

    if "gunnPenaltyPunisher" in atkSkills and atkHPGreaterEqual25Percent:
        for i in range(1, 5): defCombatBuffs[i] += -4 + defNeutrDebuffsStats[i]

    if "gunnPenaltyPunisher" in defSkills and defHPGreaterEqual25Percent:
        for i in range(1, 5): atkCombatBuffs[i] += -4 + atkNeutrDebuffsStats[i]

    if "ICE UPON YOU" in atkSkills and defHasPenalty:
        atkr.follow_ups_skill += 1
        defr.follow_up_denials -= 1

    if "ICE UPON YOU" in defSkills and atkHasPenalty:
        defr.follow_ups_skill += 1
        atkr.follow_up_denials -= 1

    if "FREEZE NOW" in atkSkills and (atkHPGreaterEqual25Percent or defHasPenalty):
        defCombatBuffs[ATK] -= 5
        defCombatBuffs[DEF] -= 5

    if "FREEZE NOW" in defSkills and (defHPGreaterEqual25Percent or atkHasPenalty):
        atkCombatBuffs[ATK] -= 5
        atkCombatBuffs[DEF] -= 5

    if "Minecraft Gaming" in atkSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += -5 + defNeutrBuffsStats[i] * -2

    if "Minecraft Gaming" in defSkills and defAllyWithin2Spaces:
        for i in range(1, 5):
            atkCombatBuffs[i] += -5 + atkNeutrBuffsStats[i] * -2

    # Sandfort Spade/Shoreline Rake
    if "heroesSummerBonusDef" in atkSkills and sum(atkBonusesNeutralized):
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[DEF] += 4

    if "heroesSummerBonusDef" in defSkills and sum(defBonusesNeutralized):
        defCombatBuffs[ATK] += 4
        defCombatBuffs[DEF] += 4

    if "heroesSummerBonusDef" in atkSkills and sum(atkBonusesNeutralized):
        atkCombatBuffs[ATK] += 4
        atkCombatBuffs[RES] += 4

    if "heroesSummerBonusDef" in defSkills and sum(defBonusesNeutralized):
        defCombatBuffs[ATK] += 4
        defCombatBuffs[RES] += 4

    # Laevatein (Refine Eff) - Laevatein
    if "laevBoost" in atkSkills and (atkHasBonus or atkHPGreaterEqual50Percent):
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5

    if "laevBoost" in defSkills and (defHasBonus or atkHPGreaterEqual50Percent):
        defCombatBuffs[ATK] += 5
        defCombatBuffs[DEF] += 5

    # Níu (Base) - Laegjarn
    if "GiveMeYourBonuses" in atkSkills:
        totalBonuses = 0

        for i in range(1, 5): totalBonuses += defNeutrBuffsStats[i]

        atkCombatBuffs = [x + totalBonuses // 2 for x in atkCombatBuffs]

    if "GiveMeYourBonuses" in defSkills:
        totalBonuses = 0

        for i in range(1, 5): totalBonuses += atkNeutrBuffsStats[i]

        defCombatBuffs = [x + totalBonuses // 2 for x in defCombatBuffs]

    # Níu (Refine Base) - Leagjarn
    if "ILoveBonusesAndWomenAndI'mAllOutOfBonuses" in atkSkills:
        tempAtkBonuses = 0
        tempDefBonuses = 0

        for i in range(1, 5): tempAtkBonuses += atkNeutrBuffsStats[i]
        for i in range(1, 5): tempDefBonuses += defNeutrBuffsStats[i]

        tempTotalBonuses = min(10, math.trunc((tempAtkBonuses + tempDefBonuses) * 0.4))
        atkCombatBuffs = [x + tempTotalBonuses for x in atkCombatBuffs]

    if "ILoveBonusesAndWomenAndI'mAllOutOfBonuses" in defSkills:
        tempAtkBonuses = 0
        tempDefBonuses = 0

        for i in range(1, 5): tempAtkBonuses += atkNeutrBuffsStats[i]
        for i in range(1, 5): tempDefBonuses += defNeutrBuffsStats[i]

        tempTotalBonuses = min(10, math.trunc((tempAtkBonuses + tempDefBonuses) * 0.4))
        defCombatBuffs = [x + tempTotalBonuses for x in defCombatBuffs]

    # Worldsea Wave (Refine Base) - SU!Laegjarn
    if "jk largjarnDesp" in atkSkills and atkHPGreaterEqual25Percent:
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[SPD] += 5
        atkr.self_desperation = True

    if "jk largjarnDesp" in atkSkills and defHPGreaterEqual25Percent:
        defCombatBuffs[ATK] += 5
        defCombatBuffs[SPD] += 5
        defr.self_desperation = True

    # Worldsea Wave (Refine Eff) - SU!Laegjarn
    if "summerLaegjarnBoost" in atkSkills:
        atkCombatBuffs[ATK] += 5 + min(trunc(0.40 * (sum(atkNeutrBuffsStats) + sum(defNeutrBuffsStats))), 10)
        atkCombatBuffs[SPD] += 5 + min(trunc(0.40 * (sum(atkNeutrBuffsStats) + sum(defNeutrBuffsStats))), 10)

    if "summerLaegjarnBoost" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5 + min(trunc(0.40 * (sum(atkNeutrBuffsStats) + sum(defNeutrBuffsStats))), 10)
        defCombatBuffs[SPD] += 5 + min(trunc(0.40 * (sum(atkNeutrBuffsStats) + sum(defNeutrBuffsStats))), 10)

    # Killing Intent(+) - Thrasir
    if "killingIntent" in atkSkills and (not defHPEqual100Percent or defHasPenalty):
        defCombatBuffs[SPD] -= 5
        defCombatBuffs[RES] -= 5
        atkr.self_desperation = True

    if "killingIntent" in defSkills and (not atkHPEqual100Percent or atkHasPenalty):
        atkCombatBuffs[SPD] -= 5
        atkCombatBuffs[RES] -= 5

    # Daydream Egg - SP!Mirabilis
    if "daydream_egg" in atkSkills and (defHPGreaterEqual75Percent or defHasPenalty):
        atkCombatBuffs[ATK] += 5
        atkCombatBuffs[DEF] += 5
        atkCombatBuffs[RES] += 5

    if "beeeg debuff" in atkSkills:
        defCombatBuffs[ATK] -= 4
        defCombatBuffs[SPD] -= 4
        defCombatBuffs[DEF] -= 4

        atkCombatBuffs[ATK] += sum(defNeutrBuffsStats[1:5]) * -1

    if "beeeg debuff" in defSkills and defAllyWithin2Spaces:
        atkCombatBuffs[ATK] -= 4
        atkCombatBuffs[SPD] -= 4
        atkCombatBuffs[DEF] -= 4

        defCombatBuffs[ATK] += sum(defNeutrBuffsStats[1:5]) * -1

    # oops! all bonus doubler
    if "bonusDoublerW" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += math.trunc(atkNeutrBuffsStats[i] * (0.25 * atkSkills["bonusDoublerW"] + 0.25))

    if "bonusDoublerSk" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += math.trunc(atkNeutrBuffsStats[i] * (0.25 * atkSkills["bonusDoublerSk"] + 0.25))

    if "bonusDoublerSe" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += math.trunc(atkNeutrBuffsStats[i] * (0.25 * atkSkills["bonusDoublerSe"] + 0.25))

    if Status.BonusDoubler in attacker.statusPos:
        for i in range(1, 5):
            atkCombatBuffs[i] += atkNeutrBuffsStats[i]

    if "bonusDoublerW" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += math.trunc(defNeutrBuffsStats[i] * (0.25 * defSkills["bonusDoublerW"] + 0.25))

    if "bonusDoublerSk" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += math.trunc(defNeutrBuffsStats[i] * (0.25 * defSkills["bonusDoublerSk"] + 0.25))

    if "bonusDoublerSe" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += math.trunc(defNeutrBuffsStats[i] * (0.25 * defSkills["bonusDoublerSe"] + 0.25))

    if Status.BonusDoubler in defender.statusPos:
        for i in range(1, 5):
            defCombatBuffs[i] += defNeutrBuffsStats[i]


    # Ylgr Combat Field
    if atkYlgrStats[0]:
        i = 0
        while i < len(atkYlgrStats[0]):
            atkCombatBuffs[ATK] -= max(atkYlgrStats[ATK - 1][i], -atkNeutrDebuffsStats[ATK])
            atkCombatBuffs[SPD] -= max(atkYlgrStats[SPD - 1][i], -atkNeutrDebuffsStats[SPD])
            atkCombatBuffs[DEF] -= max(atkYlgrStats[DEF - 1][i], -atkNeutrDebuffsStats[DEF])
            atkCombatBuffs[RES] -= max(atkYlgrStats[RES - 1][i], -atkNeutrDebuffsStats[RES])

            i += 1

    if defYlgrStats[0]:
        i = 0
        while i < len(defYlgrStats[0]):
            defCombatBuffs[ATK] -= max(defYlgrStats[ATK - 1][i], -defNeutrDebuffsStats[ATK])
            defCombatBuffs[SPD] -= max(defYlgrStats[SPD - 1][i], -defNeutrDebuffsStats[SPD])
            defCombatBuffs[DEF] -= max(defYlgrStats[DEF - 1][i], -defNeutrDebuffsStats[DEF])
            defCombatBuffs[RES] -= max(defYlgrStats[RES - 1][i], -defNeutrDebuffsStats[RES])

            i += 1

    # Kaden Combat Field
    if atkKadenStats[0]:
        i = 0
        while i < len(atkKadenStats[0]):
            atkCombatBuffs[ATK] += atkKadenStats[ATK - 1][i]
            atkCombatBuffs[SPD] += atkKadenStats[SPD - 1][i]
            atkCombatBuffs[DEF] += atkKadenStats[DEF - 1][i]
            atkCombatBuffs[RES] += atkKadenStats[RES - 1][i]

            i += 1

    if defKadenStats[0]:
        i = 0
        while i < len(defKadenStats[0]):
            defCombatBuffs[ATK] += defKadenStats[ATK - 1][i]
            defCombatBuffs[SPD] += defKadenStats[SPD - 1][i]
            defCombatBuffs[DEF] += defKadenStats[DEF - 1][i]
            defCombatBuffs[RES] += defKadenStats[RES - 1][i]

            i += 1

    # Sylgr (Refine Eff) - Ylgr
    if "stupid dumb idiot field I cant code easily" in atkSkills:
        i = 1
        while i < 5:
            defCombatBuffs[i] -= max(atkNeutrBuffsStats[i], -defNeutrDebuffsStats[i])
            i += 1

    if "stupid dumb idiot field I cant code easily" in defSkills:
        i = 1
        while i < 5:
            atkCombatBuffs[i] -= max(defNeutrBuffsStats[i], -atkNeutrDebuffsStats[i])
            i += 1


    if "unityAtkDef" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 5 + atkNeutrDebuffsStats[ATK] * -2
        atkCombatBuffs[DEF] += 5 + atkNeutrDebuffsStats[DEF] * -2

    if "unityAtkDef" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5 + defNeutrDebuffsStats[ATK] * -2
        defCombatBuffs[DEF] += 5 + defNeutrDebuffsStats[DEF] * -2

    if "unityAtkRes" in atkSkills and atkAllyWithin2Spaces:
        atkCombatBuffs[ATK] += 5 + atkNeutrDebuffsStats[ATK] * -2
        atkCombatBuffs[RES] += 5 + atkNeutrDebuffsStats[RES] * -2

    if "unityAtkRes" in defSkills and defAllyWithin2Spaces:
        defCombatBuffs[ATK] += 5 + defNeutrDebuffsStats[ATK] * -2
        defCombatBuffs[RES] += 5 + defNeutrDebuffsStats[RES] * -2

    if "penaltyReverse" in atkSkills:
        for i in range(1, 5):
            atkCombatBuffs[i] += ((min(attacker.debuffs[i], 0) * -2) + (min(AtkPanicFactor * attacker.buffs[i], 0) * -2)) * (not atkPenaltiesNeutralized[i])

    if "penaltyReverse" in defSkills:
        for i in range(1, 5):
            defCombatBuffs[i] += ((min(defender.debuffs[i], 0) * -2) + (min(DefPanicFactor * defender.buffs[i], 0) * -2)) * (not defPenaltiesNeutralized[i])

    # IDEAL
    if atkHasBonus or atkHPEqual100Percent:
        if "atkIdeal" in atkSkills: atkCombatBuffs[ATK] += atkSkills["atkIdeal"]
        if "spdIdeal" in atkSkills: atkCombatBuffs[SPD] += atkSkills["spdIdeal"]
        if "defIdeal" in atkSkills: atkCombatBuffs[DEF] += atkSkills["defIdeal"]
        if "resIdeal" in atkSkills: atkCombatBuffs[RES] += atkSkills["resIdeal"]

        if atkHasBonus and atkHPEqual100Percent:
            if "atk4Ideal" in atkSkills: atkCombatBuffs[ATK] += 2
            if "spd4Ideal" in atkSkills: atkCombatBuffs[SPD] += 2
            if "def4Ideal" in atkSkills: atkCombatBuffs[DEF] += 2
            if "res4Ideal" in atkSkills: atkCombatBuffs[RES] += 2

    if defHasBonus or defHPEqual100Percent:
        if "atkIdeal" in defSkills: defCombatBuffs[ATK] += atkSkills["atkIdeal"]
        if "spdIdeal" in defSkills: defCombatBuffs[SPD] += atkSkills["spdIdeal"]
        if "defIdeal" in defSkills: defCombatBuffs[DEF] += atkSkills["defIdeal"]
        if "resIdeal" in defSkills: defCombatBuffs[RES] += atkSkills["resIdeal"]

        if defHasBonus and defHPEqual100Percent:
            if "atk4Ideal" in defSkills: defCombatBuffs[ATK] += 2
            if "spd4Ideal" in defSkills: defCombatBuffs[SPD] += 2
            if "def4Ideal" in defSkills: defCombatBuffs[DEF] += 2
            if "res4Ideal" in defSkills: defCombatBuffs[RES] += 2


    # WHERE BONUSES AND PENALTIES ARE NEUTRALIZED
    for i in range(1, 5):
        atkCombatBuffs[i] -= atkPenaltiesNeutralized[i] * (attacker.debuffs[i] + min(attacker.buffs[i] * AtkPanicFactor, 0))
        atkCombatBuffs[i] -= atkBonusesNeutralized[i] * max(attacker.buffs[i] * AtkPanicFactor, 0)

        defCombatBuffs[i] -= defPenaltiesNeutralized[i] * (defender.debuffs[i] + min(defender.buffs[i] * DefPanicFactor, 0))
        defCombatBuffs[i] -= defBonusesNeutralized[i] * max(defender.buffs[i] * DefPanicFactor, 0)

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

    # Except Igrene because FEH worded her weapon incorrectly so they just fixed it so that it works after everyone else's effects trigger
    # https://feheroes.fandom.com/wiki/Regarding_an_Issue_with_the_Description_of_the_Guardian%27s_Bow_Skill_and_How_It_Will_Be_Addressed_(Notification)
    if "what the hell????" in atkSkills and atkPhantomStats[SPD] > defPhantomStats[SPD] and not atkIgreneTriggered:
        defStats[ATK] = max(defStats[ATK] - 5, 0)
        defStats[SPD] = max(defStats[SPD] - 5, 0)
        defStats[DEF] = max(defStats[DEF] - 5, 0)

        defPhantomStats[ATK] = max(defPhantomStats[ATK] - 5, 0)
        defPhantomStats[SPD] = max(defPhantomStats[SPD] - 5, 0)
        defPhantomStats[DEF] = max(defPhantomStats[DEF] - 5, 0)

    if "what the hell????" in defSkills and defPhantomStats[SPD] > atkPhantomStats[SPD] and not defIgreneTriggered:
        atkStats[ATK] = max(atkStats[ATK] - 5, 0)
        atkStats[SPD] = max(atkStats[SPD] - 5, 0)
        atkStats[DEF] = max(atkStats[DEF] - 5, 0)

        atkPhantomStats[ATK] = max(atkPhantomStats[ATK] - 5, 0)
        atkPhantomStats[SPD] = max(atkPhantomStats[SPD] - 5, 0)
        atkPhantomStats[DEF] = max(atkPhantomStats[DEF] - 5, 0)

    # OK FOR REAL NO MORE CHANGES TO THE STATS, I'M SURE FEH LEARNED THEIR LESSON

    if Status.SpecialCharge in attacker.statusPos:
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

    if Status.SpecialCharge in defender.statusPos:
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

    if "iBreath_f" in defSkills:
        defr.spGainOnAtk += defSkills["iBreath_f"]
        defr.spGainWhenAtkd += defSkills["iBreath_f"]

    # Heavy Blade, Skill
    if "heavyBlade" in atkSkills and atkPhantomStats[ATK] > defPhantomStats[ATK] + max(-2 * atkSkills["heavyBlade"] + 7, 1):
        atkr.spGainOnAtk += 1
    if "heavyBlade" in defSkills and defPhantomStats[ATK] > atkPhantomStats[ATK] + max(-2 * defSkills["heavyBlade"] + 7, 1):
        defr.spGainOnAtk += 1

    # Heavy Blade, Weapon
    if "heavyBladeW" in atkSkills and atkPhantomStats[ATK] > defPhantomStats[ATK] + max(-2 * atkSkills["heavyBladeW"] + 7, 1):
        atkr.spGainOnAtk += 1
    if "heavyBladeW" in defSkills and defPhantomStats[ATK] > atkPhantomStats[ATK] + max(-2 * defSkills["heavyBladeW"] + 7, 1):
        defr.spGainOnAtk += 1

    # Heavy Blade, Seal
    if "heavyBladeSe" in atkSkills and atkPhantomStats[ATK] > defPhantomStats[ATK] + max(-2 * atkSkills["heavyBladeSe"] + 7, 1):
        atkr.spGainOnAtk += 1
    if "heavyBladeSe" in defSkills and defPhantomStats[ATK] > atkPhantomStats[ATK] + max(-2 * defSkills["heavyBladeSe"] + 7, 1):
        defr.spGainOnAtk += 1

    # Flashing Blade, Skill
    if "flashingBlade" in atkSkills and atkPhantomStats[SPD] > defPhantomStats[SPD] + max(-2 * atkSkills["flashingBlade"] + 7, 1):
        atkr.spGainOnAtk += 1

        if "flashingBladeDmg" in atkSkills:
            atkr.true_all_hits += 5

    if "flashingBlade" in defSkills and defPhantomStats[SPD] > atkPhantomStats[SPD] + max(-2 * defSkills["flashingBlade"] + 7, 1):
        defr.spGainOnAtk += 1

        if "flashingBladeDmg" in defSkills:
            defr.true_all_hits += 5

    # Flashing Blade, Weapon
    if "flashingBladeW" in atkSkills and atkPhantomStats[SPD] > defPhantomStats[SPD] + max(-2 * atkSkills["flashingBladeW"] + 7, 1):
        atkr.spGainOnAtk += 1
    if "flashingBladeW" in defSkills and defPhantomStats[SPD] > atkPhantomStats[SPD] + max(-2 * defSkills["flashingBladeW"] + 7, 1):
        defr.spGainOnAtk += 1

    # Infantry Rush
    if "iRush1" in atkSkills and atkPhantomStats[ATK] >= defPhantomStats[ATK] + 5: atkr.spGainOnAtk += 1
    if "iRush2" in atkSkills and atkPhantomStats[ATK] >= defPhantomStats[ATK] + 3: atkr.spGainOnAtk += 1
    if "iRush3" in atkSkills and atkPhantomStats[ATK] >= defPhantomStats[ATK] + 1: atkr.spGainOnAtk += 1

    if "iRush1" in defSkills and defPhantomStats[ATK] >= atkPhantomStats[ATK] + 5: atkr.spGainOnAtk += 1
    if "iRush2" in defSkills and defPhantomStats[ATK] >= atkPhantomStats[ATK] + 3: atkr.spGainOnAtk += 1
    if "iRush3" in defSkills and defPhantomStats[ATK] >= atkPhantomStats[ATK] + 1: atkr.spGainOnAtk += 1

    # Infantry Flash
    if "iFlash1" in atkSkills and atkPhantomStats[SPD] >= defPhantomStats[SPD] + 5: atkr.spGainOnAtk += 1
    if "iFlash2" in atkSkills and atkPhantomStats[SPD] >= defPhantomStats[SPD] + 3: atkr.spGainOnAtk += 1
    if "iFlash3" in atkSkills and atkPhantomStats[SPD] >= defPhantomStats[SPD] + 1: atkr.spGainOnAtk += 1

    if "iFlash1" in defSkills and defPhantomStats[SPD] >= atkPhantomStats[SPD] + 5: atkr.spGainOnAtk += 1
    if "iFlash2" in defSkills and defPhantomStats[SPD] >= atkPhantomStats[SPD] + 3: atkr.spGainOnAtk += 1
    if "iFlash3" in defSkills and defPhantomStats[SPD] >= atkPhantomStats[SPD] + 1: atkr.spGainOnAtk += 1

    # Binding Shield II
    if "bindingShieldII" in atkSkills and (atkPhantomStats[SPD] >= defPhantomStats[SPD] + 5 or defender.wpnType in DRAGON_WEAPONS):
        atkr.follow_ups_skill += 1
        defr.follow_up_denials -= 1
        cannotCounter = True

    if "bindingShieldII" in defSkills and (defPhantomStats[SPD] >= atkPhantomStats[SPD] + 5 or attacker.wpnType in DRAGON_WEAPONS):
        defr.follow_ups_skill += 1
        atkr.follow_up_denials -= 1

    # Luna Arc (Refine Eff) - L!Alm
    if "legendAlmSweep" in atkSkills and atkHPGreaterEqual25Percent and (defender.wpnType in PHYSICAL_WEAPONS or atkPhantomStats[SPD] > defPhantomStats[SPD] + 5):
        cannotCounter = True

    # Dracofalchion (Refine Eff) - B!Alm
    if "sweeeeeeep" in atkSkills and atkHPGreaterEqual25Percent and defender.wpnType in PHYSICAL_WEAPONS and atkPhantomStats[SPD] > defPhantomStats[SPD]:
        atkr.offensive_NFU = True
        cannotCounter = True

    if "sweeeeeeep" in defSkills and defHPGreaterEqual25Percent:
        defr.offensive_NFU = True

    # Bow of Verdane (Refine Eff) - Jamke
    if "jamkeEffects" in atkSkills and atkHPGreaterEqual25Percent:
        if atkPhantomStats[SPD] - defPhantomStats[SPD] >= 3:
            atkr.follow_ups_skill += 1

        if atkPhantomStats[SPD] - defPhantomStats[SPD] >= 7:
            atkr.self_desperation = True

    # Lunar Brace - L!Eirika
    # Do these affect AoE specials? Test.
    # And does it stack with Bonfire's percentage like how Solar Brace stacks with Sol?
    if "foeDefSpDamage" in atkSkills: atkr.true_sp += trunc(defStats[DEF] * 0.5)
    if "foeDefSpDamage" in defSkills: defr.true_sp += trunc(atkStats[DEF] * 0.5)

    if "lunarBraceII" in atkSkills:
        atkr.defensive_NFU = True
        atkr.offensive_NFU = True
        atkr.true_stat_damages_from_foe.append((DEF, 15))

    if "lunarBraceII" in defSkills:
        defr.defensive_NFU = True
        defr.offensive_NFU = True
        defr.true_stat_damages_from_foe.append((DEF, 15))

    # Festive Siegmund (Refine Eff) - WI!Ephraim
    if "twoTurtleDoves" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[ATK] > atkPhantomStats[ATK]:
        defr.brave = True

    # Reginleif (Base) - Duo Ephraim
    if "two guys" in atkSkills and (atkPhantomStats[ATK] > defPhantomStats[ATK] or Status.MobilityUp in attacker.statusPos):
        atkr.follow_ups_skill += 1

    if "two guys" in defSkills and (defPhantomStats[ATK] > atkPhantomStats[ATK] or Status.MobilityUp in defender.statusPos):
        defr.follow_ups_skill += 1

    if "what, it's just an ordianary weapon descrip-" in atkSkills and (atkPhantomStats[ATK] > defPhantomStats[ATK] or atkHasBonus):
        atkr.follow_ups_skill += 1

    if "what, it's just an ordianary weapon descrip-" in defSkills and (defPhantomStats[ATK] > atkPhantomStats[ATK] or defHasBonus):
        defr.follow_ups_skill += 1

    # Great Flame (Base/Refine Base) - Myrrh
    if "myrrhFollow" in atkSkills and atkPhantomStats[DEF] >= defPhantomStats[DEF] + atkSkills["myrrhFollow"]:
        atkr.follow_ups_skill += 1

    if "myrrhFollow" in defSkills and defPhantomStats[DEF] >= atkPhantomStats[DEF] + defSkills["myrrhFollow"]:
        defr.follow_ups_skill += 1

    # Wanderer Blade
    if "wandererer" in atkSkills and defHPGreaterEqual75Percent and atkPhantomStats[SPD] > defPhantomStats[SPD]:
        atkr.spGainOnAtk += 1
        atkr.spGainWhenAtkd += 1

    if "wandererer" in defSkills and atkHPGreaterEqual75Percent and defPhantomStats[SPD] > atkPhantomStats[SPD]:
        defr.spGainOnAtk += 1
        defr.spGainWhenAtkd += 1

    # Raven King Claw (Refine Eff) - Naesala
    if "naesalaStuff" in atkSkills and (defHPGreaterEqual75Percent or attacker.transformed):
        if atkPhantomStats[SPD] - defPhantomStats[SPD] >= 1:
            atkr.spGainOnAtk += 1

        if atkPhantomStats[SPD] - defPhantomStats[SPD] >= 7:
            atkr.offensive_NFU = True

    if "naesalaStuff" in defSkills and (atkHPGreaterEqual75Percent or defender.transformed):
        if defPhantomStats[SPD] - atkPhantomStats[SPD] >= 1:
            defr.spGainOnAtk += 1

        if defPhantomStats[SPD] - atkPhantomStats[SPD] >= 7:
            defr.offensive_NFU = True

    # Taguel Fang (Refine Eff) - Panne
    if "panneStuff" in atkSkills and atkHPGreaterEqual25Percent:
        if atkPhantomStats[SPD] - defPhantomStats[SPD] >= 1:
            atkr.follow_ups_skill += 1

        if atkPhantomStats[SPD] - defPhantomStats[SPD] >= 5:
            atkr.true_all_hits += 7

    if "panneStuff" in defSkills and defHPGreaterEqual25Percent:
        if defPhantomStats[SPD] - atkPhantomStats[SPD] >= 1:
            defr.follow_ups_skill += 1

        if defPhantomStats[SPD] - atkPhantomStats[SPD] >= 5:
            defr.true_all_hits += 7

    # Divine Breath (Refine Eff) - Naga
    if "a bit insane" in atkSkills and atkAllyWithin3Spaces and atkStats[ATK] > defStats[RES]:
        atkr.true_first_hit += trunc((atkStats[ATK] - defStats[RES]) * 0.25)

    if "a bit insane" in defSkills and defAllyWithin3Spaces and defStats[ATK] > atkStats[RES]:
        defr.true_first_hit += trunc((defStats[ATK] - atkStats[RES]) * 0.25)

    # Savage Breath (Refine Eff) - FA!F!Corrin
    if "https://twitter.com/YMWyungbug/status/1887810292484374993" in atkSkills and atkHPGreaterEqual25Percent and atkStats[ATK] > defStats[RES]:
        atkr.true_first_hit += trunc((atkStats[ATK] - defStats[RES]) * 0.10 * (3 - len(atkAllyWithin2Spaces)))

    if "https://twitter.com/YMWyungbug/status/1887810292484374993" in defSkills and defHPGreaterEqual25Percent and defStats[ATK] > atkStats[RES]:
        defr.true_first_hit += trunc((defStats[ATK] - atkStats[RES]) * 0.10 * (3 - len(defAllyWithin2Spaces)))

    # Sæhrímnir (Refine Base) - SP!Flora
    if "let her cook!" in atkSkills and atkAllyWithin3Spaces:
        if atkPhantomStats[SPD] - defPhantomStats[SPD] >= 1:
            atkr.DR_first_hit_NSP.append(30)

        if atkPhantomStats[SPD] - defPhantomStats[SPD] >= 7:
            defr.follow_up_denials -= 1

    if "let her cook!" in defSkills and defAllyWithin3Spaces:
        if defPhantomStats[SPD] - atkPhantomStats[SPD] >= 1:
            defr.DR_first_hit_NSP.append(30)

        if defPhantomStats[SPD] - atkPhantomStats[SPD] >= 7:
            atkr.follow_up_denials -= 1

    if "selkieOutres" in atkSkills:
        if atkPhantomStats[RES] - defPhantomStats[RES] >= 1:
            defr.spLossOnAtk -= 1
            defr.spLossWhenAtkd -= 1

        if atkPhantomStats[RES] - defPhantomStats[RES] >= 5:
            atkr.offensive_NFU = True

    if "selkieOutres" in defSkills and defAllyWithin2Spaces:
        if defPhantomStats[RES] - atkPhantomStats[RES] >= 1:
            atkr.spLossOnAtk -= 1
            atkr.spLossWhenAtkd -= 1

        if defPhantomStats[RES] - atkPhantomStats[RES] >= 5:
            defr.offensive_NFU = True

    # Eldhrímnir (Refine Eff)
    if "who let her cook?" in atkSkills and defHPGreaterEqual75Percent and atkPhantomStats[RES] > defPhantomStats[RES]:
        atkr.DR_first_hit_NSP.append(30)

    if "who let her cook?" in defSkills and defPhantomStats[RES] > atkPhantomStats[RES]:
        defr.DR_first_hit_NSP.append(30)

    if "he kinda sounds like Joker Persona 5" in atkSkills and atkHPGreaterEqual25Percent and atkPhantomStats[SPD] > defPhantomStats[SPD]:
        atkr.spGainOnAtk += 1
        atkr.true_all_hits += 5

    if "he kinda sounds like Joker Persona 5" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[SPD] > atkPhantomStats[SPD]:
        defr.spGainOnAtk += 1
        atkr.true_all_hits += 5

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

    # Worldsea Wave (Refine Eff) - SU!Laegjarn
    if "summerLaegjarnBoost" in atkSkills and atkPhantomStats[SPD] >= defPhantomStats[SPD] + 10:
        atkr.offensive_NFU = True

    # Lyfjaberg (Refine Base) - Eir
    if "eirRefineBoost" in defSkills and defHPGreaterEqual25Percent and defPhantomStats[SPD] > atkPhantomStats[SPD]:
        atkr.follow_up_denials -= 1
        atkr.spLossOnAtk -= 1
        atkr.spLossWhenAtkd -= 1

    # Guard
    if "guardHP" in atkSkills and atkHPCur / atkStats[0] >= atkSkills["guardHP"] / 10:
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "guardHP" in defSkills and defHPCur / defStats[0] >= defSkills["guardHP"] / 10:
        atkr.spLossWhenAtkd -= 1
        atkr.spLossOnAtk -= 1

    if Status.Guard in attacker.statusNeg:
        atkr.spLossWhenAtkd -= 1
        atkr.spLossOnAtk -= 1

    if Status.Guard in defender.statusNeg:
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "uncondGuard" in atkSkills:
        defr.spLossWhenAtkd -= 1
        defr.spLossOnAtk -= 1

    if "uncondGuard" in defSkills:
        atkr.spLossWhenAtkd -= 1
        atkr.spLossOnAtk -= 1

    # Full %DR piercing on special activation
    if "DamageReductionPierce" in atkSkills:
        atkr.sp_pierce_DR = True

    if "DamageReductionPierce" in defSkills:
        defr.sp_pierce_DR = True

    # TEMPO WEAPONS/SKILLS

    if "tempo" in atkSkills:
        atkr.defensive_tempo = True
        atkr.offensive_tempo = True

    if "tempo" in defSkills:
        defr.defensive_tempo = True
        defr.offensive_tempo = True

    if atkr.offensive_tempo:
        atkr.spLossOnAtk = 0
        atkr.spLossWhenAtkd = 0

    if atkr.defensive_tempo:
        defr.spGainOnAtk = 0
        defr.spGainWhenAtkd = 0

    if defr.offensive_tempo:
        defr.spLossOnAtk = 0
        defr.spLossWhenAtkd = 0

    if defr.defensive_tempo:
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

    # Stat-Dependant Skills
    if "windsweep" in atkSkills:
        atkr.follow_up_denials -= 1

        if atkPhantomStats[SPD] >= defPhantomStats[SPD] + (
                -2 * atkSkills["windsweep"] + 7) and defender.wpnType in PHYSICAL_WEAPONS:
            cannotCounter = True

    if "watersweep" in atkSkills:
        atkr.follow_up_denials -= 1

        if atkPhantomStats[SPD] >= defPhantomStats[SPD] + (
                -2 * atkSkills["watersweep"] + 7) and defender.wpnType in MAGICAL_WEAPONS:
            cannotCounter = True

    # Laws of Sacae II (L!Lyn)
    if "That's a bit better" in atkSkills and atkPhantomStats[SPD] >= defPhantomStats[SPD] + 5 and attacker.wpnType in MELEE_WEAPONS:
        cannotCounter = True

    # Deep-Blue Bow (Refine Eff) - SU!Lyn
    if "summerLynSweep" in atkSkills and atkHPGreaterEqual25Percent and defender.wpnType in MELEE_WEAPONS and atkPhantomStats[SPD] >= defPhantomStats[SPD] + 5:
        cannotCounter = True

    if Status.Pursual in attacker.statusPos:
        atkr.follow_ups_skill += 1

    # Spirit Breath (Base) - H!Myrrh
    if "HMyrrhFU" in atkSkills and atkPhantomStats[DEF] >= defPhantomStats[DEF] + 5:
        atkr.follow_ups_skill += 1

    if "sueSweep" in atkSkills and atkPhantomStats[SPD] >= defPhantomStats[SPD] + 5:
        cannotCounter = True


    # This is the final variable which determines if a foe can counterattack
    cannotCounterFinal = (cannotCounter and not disableCannotCounter) or not (attacker.getRange() == defender.getRange() or ignore_range) or defender.weapon is None

    # I hate this skill up until level 4 why does it have all those conditions
    if "brashAssault" in atkSkills and not cannotCounterFinal and atkHPCur / atkStats[0] <= 0.1 * atkSkills["brashAssault"] + 0.2:
        atkr.follow_ups_skill += 1

    if "brashAssaultSe" in atkSkills and not cannotCounterFinal and atkHPCur / atkStats[0] <= 0.1 * atkSkills["brashAssaultSe"] + 0.2:
        atkr.follow_ups_skill += 1

    if "brashAssaultLyn" in atkSkills and not cannotCounterFinal and atkHPCur / atkStats[0] <= 0.75:
        atkr.follow_ups_skill += 1

    # Hoarfrost Knife - Flora
    if "floraBoost" in atkSkills and not cannotCounterFinal and defender.wpnType in MELEE_WEAPONS:
        atkr.follow_ups_skill += 1

    if "floraEasyBoost" in atkSkills and not cannotCounterFinal:
        atkr.follow_ups_skill += 1

    # Brynhildr - Refine (Leo)
    if "leoWowThisRefineIsGarbage" in atkSkills and atkPhantomStats[DEF] > defPhantomStats[DEF] and defender.wpnType in RANGED_WEAPONS:
        defr.follow_up_denials -= 1

    if "leoWowThisRefineIsGarbage" in defSkills and defPhantomStats[DEF] > atkPhantomStats[DEF] and attacker.wpnType in RANGED_WEAPONS:
        atkr.follow_up_denials -= 1

    # Null Follow-Up
    if Status.NullFollowUp in attacker.statusPos and atkPhantomStats[2] > defPhantomStats[2]:
        atkr.defensive_NFU, atkr.offensive_NFU = True

    if Status.NullFollowUp in defender.statusPos and defPhantomStats[2] > atkPhantomStats[2]:
        defr.defensive_NFU, defr.offensive_NFU = True

    if atkr.defensive_NFU: defr.follow_ups_skill = 0
    if defr.defensive_NFU: atkr.follow_ups_skill = 0
    if atkr.offensive_NFU: atkr.follow_up_denials = 0
    if defr.offensive_NFU: defr.follow_up_denials = 0

    # Scowl-based effects
    if "waveScowl" in atkSkills:
        if atkPhantomStats[RES] >= defPhantomStats[RES] + 5 and defender.getSpecialType() == "Offense":
            defr.sp_charge_first -= 1

    if "waveScowl" in defSkills:
        if defPhantomStats[RES] >= atkPhantomStats[RES] + 5 and attacker.getSpecialType() == "Offense":
            atkr.sp_charge_first -= 1

    # TRUE DAMAGE ADDITION
    for x in atkr.true_stat_damages:
        stat, percentage = x

        if stat == HP:
            atkr.true_all_hits += math.trunc(atkHPCur * (percentage / 100))
        else:
            atkr.true_all_hits += math.trunc(atkStats[stat] * (percentage / 100))

    for x in defr.true_stat_damages:
        stat, percentage = x

        if stat == HP:
            defr.true_all_hits += math.trunc(defHPCur * (percentage / 100))
        else:
            defr.true_all_hits += math.trunc(defStats[stat] * (percentage / 100))

    for x in atkr.true_stat_damages_from_foe:
        stat, percentage = x

        if stat == HP:
            atkr.true_all_hits += math.trunc(defHPCur * (percentage / 100))
        else:
            atkr.true_all_hits += math.trunc(defStats[stat] * (percentage / 100))

    for x in defr.true_stat_damages_from_foe:
        stat, percentage = x

        if stat == HP:
            defr.true_all_hits += math.trunc(atkHPCur * (percentage / 100))
        else:
            defr.true_all_hits += math.trunc(atkStats[stat] * (percentage / 100))

    if Status.Exposure in defender.statusNeg: atkr.true_all_hits += 10
    if Status.Exposure in attacker.statusNeg: defr.true_all_hits += 10

    if "SpdDmg" in atkSkills and atkPhantomStats[SPD] > defPhantomStats[SPD]:
        atkr.true_all_hits += min(math.trunc((atkPhantomStats[SPD] - defPhantomStats[SPD]) * 0.1 * atkSkills["SpdDmg"]), atkSkills["SpdDmg"])
    if "SpdDmg" in defSkills and defPhantomStats[SPD] > atkPhantomStats[SPD]:
        defr.true_all_hits += min(math.trunc((defPhantomStats[SPD] - atkPhantomStats[SPD]) * 0.1 * defSkills["SpdDmg"]), defSkills["SpdDmg"])

    # Ashera's Chosen+ - Altina
    if "newChosen" in atkSkills and (all([ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS for ally in atkAdjacentToAlly]) or defHPGreaterEqual75Percent):
        if atkPhantomStats[RES] > defPhantomStats[RES]:
            atkr.true_all_hits += min(math.trunc((atkPhantomStats[RES] - defPhantomStats[RES]) * 0.7), 7)

    if "newChosen" in defSkills and (all([ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS for ally in defAdjacentToAlly]) or atkHPGreaterEqual75Percent):
        if defPhantomStats[RES] > atkPhantomStats[RES]:
            defr.true_all_hits += min(math.trunc((defPhantomStats[RES] - atkPhantomStats[RES]) * 0.7), 7)

    if "SUTikiDamage" in atkSkills and atkAllyWithin3Spaces:
        atkr.true_sp += math.trunc(defStats[SPD] * (0.1 * attacker.specialMax + 0.2))

    if "SUTikiDamage" in defSkills and defAllyWithin3Spaces:
        defr.true_sp += math.trunc(atkStats[SPD] * (0.1 * defender.specialMax + 0.2))

    if "moreeeeta" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.true_all_hits += math.trunc(atkStats[SPD] * 0.1)
    if "moreeeeta" in defSkills and defHPGreaterEqual25Percent:
        defr.true_all_hits += math.trunc(atkStats[SPD] * 0.1)

    # Light Brand (Base) - Leif
    if "thraciaMoment" in atkSkills and defStats[DEF] >= defStats[RES] + 5:
        atkr.true_all_hits += 7
    if "thraciaMoment" in defSkills and atkStats[DEF] >= atkStats[RES] + 5:
        defr.true_all_hits += 7

    # Quick Mulagir (Refine Eff) - Sue
    if "sueScatter" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.true_first_hit += math.trunc(atkStats[SPD] * 0.15)

    if "sueScatter" in defSkills and defHPGreaterEqual25Percent:
        defr.true_first_hit += math.trunc(defStats[SPD] * 0.15)

    if "canasBoost" in atkSkills and atkAllyWithin3Spaces:
        atkr.true_all_hits += max(math.trunc(atkStats[RES] * 0.20), math.trunc(defStats[RES] * 0.20))

    if "canasBoost" in defSkills and defAllyWithin3Spaces:
        defr.true_all_hits += max(math.trunc(atkStats[RES] * 0.20), math.trunc(defStats[RES] * 0.20))

    if "LOVE PROVIIIIDES, PROTECTS US" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.true_all_hits += math.trunc(atkStats[2] * 0.15)
    if "LOVE PROVIIIIDES, PROTECTS US" in defSkills and defHPGreaterEqual25Percent:
        defr.true_all_hits += math.trunc(defStats[2] * 0.15)

    if "infiniteSpecial" in atkSkills:
        atkr.true_all_hits += math.trunc(atkStats[2] * 0.15)
    if "infiniteSpecial" in defSkills:
        defr.true_all_hits += math.trunc(defStats[2] * 0.15)

    if "newVTyrfing" in atkSkills and (not atkHPEqual100Percent or defHPGreaterEqual75Percent):
        atkr.true_all_hits += math.trunc(atkStats[ATK] * 0.15)
    if "newVTyrfing" in defSkills:
        defr.true_all_hits += math.trunc(defStats[ATK] * 0.15)

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

    # Astra Blade (Base/Refine Base) - Valentia Catria
    if "megaAstra" in atkSkills and atkPhantomStats[ATK] > defPhantomStats[DEF]:
        atkr.true_all_hits += max(trunc((atkStats[ATK] - defStats[DEF]) * 0.5), 0)

    if "megaAstra" in defSkills and defPhantomStats[ATK] > atkPhantomStats[DEF]:
        defr.true_all_hits += max(trunc((defStats[ATK] - atkStats[DEF]) * 0.5), 0)

    if "sky-hopper" in atkSkills and atkHPGreaterEqual25Percent:
        atkr.true_all_hits += trunc(0.2 * atkStats[SPD])

    if "sky-hopper" in defSkills and defHPGreaterEqual25Percent:
        defr.true_all_hits += trunc(0.2 * defStats[SPD])

    # Fell Breath (Refine Eff) - Duma
    if "Twilight of the Gods is so peak" in atkSkills and atkStats[ATK] > defStats[RES]:
        atkr.true_first_hit += trunc(0.3 * (atkStats[ATK] - defStats[RES]))

    if "Twilight of the Gods is so peak" in defSkills and defAllyWithin2Spaces and defStats[ATK] > atkStats[RES]:
        defr.true_first_hit += trunc(0.3 * (defStats[ATK] - atkStats[RES]))

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

    if "laguz_friend" in defSkills:
        skill_lvl = defSkills["laguz_friend"]

        if defender.getMaxSpecialCooldown() >= 3 and defender.getSpecialType() == "Offense" or defender.getSpecialType() == "Defense":
            defr.TDR_all_hits += trunc(0.05 * skill_lvl * max(defStats[DEF], defStats[RES]))

        if defender.getMaxSpecialCooldown() >= 3 and defender.getSpecialType() == "Offense":
            defr.true_sp += trunc(0.05 * skill_lvl * max(defStats[DEF], defStats[RES]))
            if skill_lvl == 4: defr.sp_pierce_DR = True
        if defender.getSpecialType() == "Defense":
            defr.true_sp_next += trunc(0.05 * skill_lvl * max(defStats[DEF], defStats[RES]))
            if skill_lvl == 4: defr.sp_pierce_after_DSP = True

    for x in atkr.TDR_stats:
        stat, percentage = x
        atkr.TDR_all_hits += math.trunc(atkStats[stat] * (percentage / 100))

    for x in defr.TDR_stats:
        stat, percentage = x
        defr.TDR_all_hits += math.trunc(defStats[stat] * (percentage / 100))

    # EFFECTIVENESS CHECK

    atkHasEffectiveness = False
    defHasEffectiveness = False

    # Infantry Effectiveness
    if "effInf" in atkSkills and defender.move == 0: atkHasEffectiveness = True
    if "effInf" in defSkills and attacker.move == 0: defHasEffectiveness = True

    # Cavalry Effectiveness
    if "effCav" in atkSkills and "nullEffCav" not in defSkills and defender.move == 1: atkHasEffectiveness = True
    if "effCav" in defSkills and "nullEffCav" not in atkSkills and attacker.move == 1: defHasEffectiveness = True

    # Flier Effectiveness
    if "effFly" in atkSkills and ("nullEffFly" not in defSkills and "haarEff" not in defSkills) and defender.move == 2: atkHasEffectiveness = True
    if "effFly" in defSkills and ("nullEffFly" not in atkSkills and "haarEff" not in defSkills) and attacker.move == 2: defHasEffectiveness = True

    # Bow Weapons
    if attacker.wpnType in BOW_WEAPONS and ("nullEffFly" not in defSkills and "haarEff" not in defSkills) and defender.move == 2:
        atkHasEffectiveness = True

    if defender.wpnType in BOW_WEAPONS and ("nullEffFly" not in atkSkills and "haarEff" not in defSkills) not in atkSkills and attacker.move == 2:
        defHasEffectiveness = True

    # Armor Effectiveness
    if "effArmor" in atkSkills and "nullEffArm" not in defSkills and defender.move == 3: atkHasEffectiveness = True
    if "effArmor" in defSkills and "nullEffArm" not in atkSkills and attacker.move == 3: defHasEffectiveness = True

    # Cavalry and Armor
    if "effCavArmor" in atkSkills and (defender.move == 1 and "nullEffCav" not in defSkills or defender.move == 3 and "nullEffArm" not in defSkills): atkHasEffectiveness = True
    if "effCavArmor" in defSkills and (attacker.move == 1 and "nullEffCav" not in atkSkills or attacker.move == 3 and "nullEffArm" not in defSkills): defHasEffectiveness = True

    # Dragon Effectiveness
    for dragon_str in dragon_eff_strs:
        if dragon_str in atkSkills and "nullEffDragon" not in defSkills and (defender.wpnType in DRAGON_WEAPONS or "loptous" in defSkills):
            atkHasEffectiveness = True
        if dragon_str in defSkills and "nullEffDragon" not in atkSkills and (attacker.wpnType in DRAGON_WEAPONS or "loptous" in atkSkills):
            defHasEffectiveness = True

    if Status.EffDragons in attacker.statusPos and "nullEffDragon" not in defSkills and (defender.wpnType in DRAGON_WEAPONS or "loptous" in defSkills):
        atkHasEffectiveness = True
    if Status.EffDragons in defender.statusPos and "nullEffDragon" not in atkSkills and (attacker.wpnType in DRAGON_WEAPONS or "loptous" in atkSkills):
        defHasEffectiveness = True

    # Magic Effectiveness
    if "effMagic" in atkSkills and defender.wpnType in TOME_WEAPONS: atkHasEffectiveness = True
    if "effMagic" in defSkills and attacker.wpnType in TOME_WEAPONS: defHasEffectiveness = True

    # Beast Effectiveness
    beast_eff_strs = ["effBeast", "icePicnicRefine", "petraEff", "petraEffRefine", "effDragonBeast"]

    for beast_str in beast_eff_strs:
        if beast_str in atkSkills and defender.wpnType in BEAST_WEAPONS:
            atkHasEffectiveness = True
        if beast_str in defSkills and attacker.wpnType in BEAST_WEAPONS:
            defHasEffectiveness = True

    # Caeda (Sword, Lance, Axe, CBow, Armor)
    if "effCaeda" in atkSkills and (defender.wpnType in ["Sword", "Lance", "Axe", "CBow"] or (
            defender.move == 3 and "nullEffArm" not in defSkills)):
        atkHasEffectiveness = True
    if "effCaeda" in defSkills and (attacker.wpnType in ["Sword", "Lance", "Axe", "CBow"] or (
            attacker.move == 3 and "nullEffArm" not in atkSkills)):
        defHasEffectiveness = True

    # L!F!Shez (Speed Check)
    if "effShez" in atkSkills:
        if defender.move == 0 and defender.wpnType not in DRAGON_WEAPONS + BEAST_WEAPONS:
            threshold = defPhantomStats[2] + 20
        else:
            threshold = defPhantomStats[2] + 5

        if atkPhantomStats[2] >= threshold:
            atkHasEffectiveness = True

    if defender.wpnType == "BTome" and "haarEff" in atkSkills:
        defHasEffectiveness = True
    if attacker.wpnType == "BTome" and "haarEff" in defSkills:
        atkHasEffectiveness = True

    if atkHasEffectiveness: atkStats[1] += math.trunc(atkStats[1] * 0.5)
    if defHasEffectiveness: defStats[1] += math.trunc(defStats[1] * 0.5)

    # COLOR ADVANTAGE

    atkr.preTriangleAtk = atkStats[ATK]
    defr.preTriangleAtk = defStats[ATK]

    if atkr.cancel_affinity_level > 0:
        atkr.triangle_adept_level = 0

        if atkr.cancel_affinity_level == 1:
            defr.triangle_adept_level = 0

    if defr.cancel_affinity_level > 0:
        defr.triangle_adept_level = 0

        if defr.cancel_affinity_level == 1:
            atkr.triangle_adept_level = 0

    # Attacker has advantage
    if (attacker.getColor() == "Red" and defender.getColor() == "Green") or (
            attacker.getColor() == "Green" and defender.getColor() == "Blue") or \
            (attacker.getColor() == "Blue" and defender.getColor() == "Red") or (
            defender.getColor() == "Colorless" and "colorlessAdv" in atkSkills):

        if defr.cancel_affinity_level == 2:
            atkr.triangle_adept_level = 0

        if defr.cancel_affinity_level == 3 or Status.CancelAffinity in defender.statusPos:
            atkr.triangle_adept_level = -atkr.triangle_adept_level

        triAdept = min(atkr.triangle_adept_level + defr.triangle_adept_level,
                       max(atkr.triangle_adept_level, defr.triangle_adept_level), 0.2)

        atkStats[ATK] += math.trunc(atkStats[ATK] * (0.2 + triAdept))
        defStats[ATK] -= math.trunc(defStats[ATK] * (0.2 + triAdept))

        wpnAdvHero = 0

    elif (attacker.getColor() == "Blue" and defender.getColor() == "Green") or (
            attacker.getColor() == "Red" and defender.getColor() == "Blue") or \
            (attacker.getColor() == "Green" and defender.getColor() == "Red") or (
            attacker.getColor() == "Colorless" and "colorlessAdv" in defSkills):

        if atkr.cancel_affinity_level == 2:
            defr.triangle_adept_level = 0

        if atkr.cancel_affinity_level == 3 or Status.CancelAffinity in attacker.statusPos:
            defr.triangle_adept_level = -defr.triangle_adept_level

        triAdept = min(atkr.triangle_adept_level + defr.triangle_adept_level,
                       max(atkr.triangle_adept_level, defr.triangle_adept_level), 0.2)

        atkStats[ATK] -= math.trunc(atkStats[ATK] * (0.2 + triAdept))
        defStats[ATK] += math.trunc(defStats[ATK] * (0.2 + triAdept))

        wpnAdvHero = 1

    # Weapon-triangle based effects

    # Pegasus Carrot
    if "wpnAdvNFU" in atkSkills and wpnAdvHero == 0:
        atkr.offensive_NFU = True

    if "wpnAdvNFU" in defSkills and wpnAdvHero == 1:
        defr.offensive_NFU = True

    # Unconditional Hexblade
    if "permHexblade" in atkSkills: atkr.hexblade = True
    if "permHexblade" in defSkills: defr.hexblade = True

    # Sorcery Blade
    if "sorceryBlade" in atkSkills and atkHPCur / atkStats[HP] >= 1.5 * 0.5 * atkSkills["sorceryBlade"]:
        magic_ally_cond = False
        for ally in atkAdjacentToAlly:
            if ally.wpnType in TOME_WEAPONS:
                magic_ally_cond = True

        if magic_ally_cond:
            atkTargetingDefRes = int(defStats[DEF] < defStats[RES])

    if "sorceryBlade" in defSkills and defHPCur / defStats[HP] >= 1.5 * 0.5 * defSkills["sorceryBlade"]:
        magic_ally_cond = False
        for ally in defAdjacentToAlly:
            if ally.wpnType in TOME_WEAPONS:
                magic_ally_cond = True

        if magic_ally_cond:
            defTargetingDefRes = int(defStats[DEF] < defStats[RES])

    # Infantry Hexblade
    if "adjHexblade" in atkSkills:
        atkr.hexblade = True

    if "adjHexblade" in defSkills:
        defr.hexblade = True

    # Newer dragonstones
    if attacker.getTargetedDef() == 0 and "oldDragonstone" not in atkSkills:
        atkr.hexblade = True

    if defender.getTargetedDef() == 0 and "oldDragonstone" not in defSkills:
        atkr.hexblade = False

    # WHICH DEFENSE ARE WE TARGETING?
    # 0 targets DEF, 1 targets RES

    if attacker.getTargetedDef() == -1:
        atkTargetingDefRes = 0
    else:
        atkTargetingDefRes = 1

    if atkr.hexblade and not defr.disable_foe_hexblade:
        if defStats[DEF] < defStats[RES]:
            atkTargetingDefRes = 0
        else:
            atkTargetingDefRes = 1

    if defender.getTargetedDef() == -1:
        defTargetingDefRes = 0
    else:
        defTargetingDefRes = 1

    if defr.hexblade and not atkr.disable_foe_hexblade:
        if atkStats[DEF] < atkStats[RES]:
            defTargetingDefRes = 0
        else:
            defTargetingDefRes = 1


    atkr.preDefenseTerrain = atkStats[DEF]
    defr.preDefenseTerrain = defStats[DEF]

    atkr.preResistTerrain = atkStats[RES]
    defr.preResistTerrain = defStats[RES]

    # Defensive terrain
    if atkDefensiveTerrain: atkStats[3 + defTargetingDefRes] = trunc(atkStats[3 + defTargetingDefRes] * 1.3)
    if defDefensiveTerrain: defStats[3 + atkTargetingDefRes] = trunc(defStats[3 + atkTargetingDefRes] * 1.3)

    # Amount of speed required to double the foe
    atkOutspeedFactor = 5
    defOutspeedFactor = 5

    # Which index in the attack array holds the potent attack
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

    # Potent 1-4
    if "potentStrike" in atkSkills and atkStats[SPD] >= defStats[SPD] + (atkOutspeedFactor - 25):
        atkr.potent_FU = True

    if "potentStrike" in defSkills and defStats[SPD] >= atkStats[SPD] + (defOutspeedFactor - 25):
        defr.potent_FU = True

    # Lodestar Rush - E!Marth
    if "potentFix" in atkSkills:
        atkr.potent_new_percentage = atkSkills["potentFix"]

    if "potentFix" in defSkills:
        defr.potent_new_percentage = defSkills["potentFix"]

    # Follow-Up granted via Spd stat
    if atkStats[SPD] >= defStats[SPD] + atkOutspeedFactor: atkr.follow_ups_spd += 1
    if defStats[SPD] >= atkStats[SPD] + defOutspeedFactor: defr.follow_ups_spd += 1

    atkAlive = True
    defAlive = True

    def getSpecialDamage(effs, initStats, initHP, otherStats, defOrRes, base_damage, num_foe_atks, selfModifier, otherModifier, otherMoveType, otherWpnType, initAdjAllies):
        total_special = 0.0
        total_nonspecial = 0.0

        if "atkBoost" in effs:
            total_special += selfModifier.preTriangleAtk * 0.01 * effs["atkBoost"]

        if "spdBoost" in effs:
            total_special += initStats[SPD] * 0.01 * effs["spdBoost"]

        if "defBoost" in effs:
            total_special += selfModifier.preDefenseTerrain * 0.01 * effs["defBoost"]

        if "resBoost" in effs:
            total_special += selfModifier.preResistTerrain * 0.01 * effs["resBoost"]

        if "rupturedSky" in effs:
            if otherWpnType in DRAGON_WEAPONS + BEAST_WEAPONS:
                total_special += otherModifier.preTriangleAtk * 0.02 * effs["rupturedSky"]
            else:
                total_special += otherModifier.preTriangleAtk * 0.01 * effs["rupturedSky"]

        if "staffRes" in effs:
            total_special += otherModifier.preResistTerrain * 0.01 * effs["staffRes"]

        # Vengeance/Reprisal
        if "retaliatoryBoost" in effs:
            total_special += (initStats[HP] - initHP) * 0.01 * effs["retaliatoryBoost"]

        # Glimmer/Astra
        if "dmgBoost" in effs:
            total_special += base_damage * 0.01 * effs["dmgBoost"]

        # Moonbow/Luna
        targeted_defense = otherModifier.preDefenseTerrain if defOrRes == 0 else otherModifier.preResistTerrain
        if "defReduce" in effs:
            reduced_def = targeted_defense - math.trunc(targeted_defense * 0.01 * effs["defReduce"])
            reduced_attack = initStats[ATK] - reduced_def
            total_special += reduced_attack - base_damage

        # Blue Flame
        if "blueFlame" in effs:
            if initAdjAllies:
                total_special += 25
            else:
                total_special += 10

        # No Quarter
        if "atkBoostArmor" in effs:
            if otherMoveType == 3:
                total_special += selfModifier.preTriangleAtk * 0.01 * 4
            else:
                total_special += selfModifier.preTriangleAtk * 0.01 * 3

        # Great Aether
        if "NumAtkBoost" in effs:
            total_special += (effs["NumAtkBoost"] + num_foe_atks) * 0.01 * selfModifier.preTriangleAtk

        # Wrath (Should be ignored w/ Emblem Marth Ring)
        if "wrathBoostW" in effs:
            if initHP / initStats[HP] <= effs["wrathBoostW"] * 0.25:
                total_nonspecial += 10

        if "wrathBoostSk" in effs:
            if initHP / initStats[HP] <= effs["wrathBoostSk"] * 0.25:
                total_nonspecial += 10

        if "spurnBoostSk" in effs:
            if initHP / initStats[HP] <= effs["spurnBoostSk"] * 0.25:
                total_nonspecial += 5

        # Owain (Should be ignored w/ Emblem Marth Ring)
        if "spMissiletainn" in effs:
            total_nonspecial += min(initStats[HP] - initHP, 30)

        # H!Timerra (Should be ignored w/ Emblem Marth Ring)
        if "spTimerra" in effs:
            total_nonspecial += math.trunc(initStats[SPD] * 0.01 * effs["spTimerra"])

        return trunc(total_special), trunc(total_nonspecial)

    # COMPUTE TURN ORDER

    # Follow-Up Granted if sum of allowed - denied follow-ups is > 0
    followupA = atkr.follow_ups_spd + atkr.follow_ups_skill + atkr.follow_up_denials > 0
    followupD = defr.follow_ups_spd + defr.follow_ups_skill + defr.follow_up_denials > 0

    # Hardy bearing
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

    # duplicate letters if Brave
    for c in startString:
        newString += c

        if c == 'A' and atkr.brave:
            newString += c
        if c == 'D' and defr.brave:
            newString += c


    # potent strike
    if atkr.potent_FU:
        last_a_index = newString.rfind('A')
        newString = newString[:last_a_index + 1] + 'A' + newString[last_a_index + 1:]

    if defr.potent_FU:
        last_a_index = newString.rfind('D')
        newString = newString[:last_a_index + 1] + 'D' + newString[last_a_index + 1:]

        defPotentIndex = newString.rfind('D')

    # code don't work without these
    startString = newString
    startString2 = startString

    if cannotCounterFinal: startString2 = startString.replace("D", "")

    if atkr.potent_FU:
        atkPotentIndex = startString2.rfind('A')

    # create list of attack objects
    attackList = []
    A_Count = 0
    D_Count = 0
    i = 0

    atkCanFollowUp = False
    defCanFollowUp = False

    while i < len(startString2):
        if startString2[i] == "A":
            A_Count += 1
            atkCanFollowUp = A_Count == 2 and (followupA or atkr.potent_FU) and not atkr.brave or A_Count in [3, 4, 5]
            isConsecutive = True if A_Count >= 2 and startString2[i - 1] == "A" else False

            potentRedu = 100
            if "potentStrike" in atkSkills and i == atkPotentIndex:
                potentRedu = 10 * atkSkills["potentStrike"] + 40 * int(not (atkr.brave or followupA))

            attackList.append(Attack(0, atkCanFollowUp, isConsecutive, A_Count, A_Count + D_Count, None if A_Count + D_Count == 1 else attackList[i - 1], potentRedu))
        else:
            D_Count += 1
            defCanFollowUp = D_Count == 2 and (followupD or defr.potent_FU) and not defr.brave or D_Count in [3, 4, 5]
            isConsecutive = True if D_Count >= 2 and startString2[i - 1] == "D" else False
            potentRedu = 100

            if "potentStrike" in defSkills and i == defPotentIndex:
                potentRedu = 10 * defSkills["potentStrike"] + 40 * int(not (defr.brave or followupD))

            attackList.append(Attack(1, defCanFollowUp, isConsecutive, D_Count, A_Count + D_Count,
                                     None if A_Count + D_Count == 1 else attackList[i - 1], potentRedu))
        i += 1

    # Damage reduction caused by a unit's ability to make a follow up
    if "idunnDR" in atkSkills and defHPGreaterEqual75Percent and defCanFollowUp:
        atkr.DR_first_hit_NSP.append(70)

    if "idunnDR" in defSkills and atkCanFollowUp:
        defr.DR_first_hit_NSP.append(70)

    # Conjurer Curios (Refine Base) - H!Hector
    if "reduFU" in atkSkills and (turn % 2 == 1 or not defHPEqual100Percent):
        if defCanFollowUp:
            atkr.DR_first_hit_NSP.append(60)
        else:
            atkr.DR_first_hit_NSP.append(30)

    if "reduFU" in defSkills and (turn % 2 == 1 or not atkHPEqual100Percent):
        if atkCanFollowUp:
            defr.DR_first_hit_NSP.append(60)
        else:
            defr.DR_first_hit_NSP.append(30)

    # Damage reduction calculated based on a difference between two stats (Dodge, etc.)
    for stat_type, stat_max in atkr.stat_scaling_DR:
        if atkPhantomStats[stat_type] > defPhantomStats[stat_type]:
            atkr.DR_all_hits_NSP.append(min(stat_max / 10 * (atkPhantomStats[stat_type] - defPhantomStats[stat_type]), stat_max))

    for stat_type, stat_max in defr.stat_scaling_DR:
        if defPhantomStats[stat_type] > atkPhantomStats[stat_type]:
            defr.DR_all_hits_NSP.append(min(stat_max / 10 * (defPhantomStats[stat_type] - atkPhantomStats[stat_type]), stat_max))

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

    if Status.Dodge in attacker.statusPos and atkPhantomStats[2] > defPhantomStats[2]:
        atkr.DR_all_hits_NSP.append(min(4 * (atkPhantomStats[2] - defPhantomStats[2], 40)))

    if Status.Dodge in defender.statusPos and defPhantomStats[2] > atkPhantomStats[2]:
        defr.DR_all_hits_NSP.append(min(4 * (defPhantomStats[2] - atkPhantomStats[2], 40)))

    if "dodgeSk" in atkSkills and atkPhantomStats[2] > defPhantomStats[2]:
        atkr.DR_all_hits_NSP.append(min(atkSkills["dodgeSk"] * (atkPhantomStats[2] - defPhantomStats[2], atkSkills["dodgeSk"] * 10)))

    if "dodgeSk" in defSkills and defPhantomStats[2] > atkPhantomStats[2]:
        defr.DR_all_hits_NSP.append(min(defSkills["dodgeSk"] * (defPhantomStats[2] - atkPhantomStats[2], defSkills["dodgeSk"] * 10)))

    # Emblem Marth Ring
    if "shine on" in atkSkills and atkr.brave:
        atkr.reduce_self_sp_damage += 8

    if "shine on" in defSkills and defr.brave:
        defr.reduce_self_sp_damage += 8

    # method to attack
    def attack(striker, strikee, stkSpEffects, steSpEffects, stkStats, steStats, defOrRes, curReduction,
               curSpecialReduction, stkHPCur, steHPCur, stkSpCount, steSpCount, I_stkr, I_ster, curAttack):

        dmgBoost = 0
        nsp_dmgBoost = 0

        # has special triggered due to this hit
        stkr_sp_triggered = False
        ster_sp_triggered = False

        # attack minus defense or resistance
        attack = stkStats[ATK] - steStats[3 + defOrRes]

        if attack < 0: attack = 0

        if stkSpCount == 0 and striker.getSpecialType() == "Offense" and not I_stkr.special_disabled:
            if not is_in_sim: print(striker.name + " procs " + striker.getSpName() + ".")
            num_foe_atks = curAttack.attackNumAll - curAttack.attackNumSelf

            striker_tile = attacker.attacking_tile if striker.side == 0 else defender.tile

            dmgBoost, nsp_dmgBoost = getSpecialDamage(stkSpEffects, stkStats, stkHPCur, steStats, defOrRes, attack, num_foe_atks, I_stkr, I_ster, strikee.move, strikee.wpnType, allies_within_n(striker, striker_tile, 1))

            if I_stkr.brave:  # emblem marth effect
                dmgBoost = max(dmgBoost - I_stkr.reduce_self_sp_damage, 0)

            I_stkr.special_triggered = True
            stkr_sp_triggered = True

        attack += dmgBoost  # true damage by specials

        # true damage on special activation, not counted as special damage
        attack += nsp_dmgBoost

        # true damage on all hits
        attack += I_stkr.true_all_hits

        if I_stkr.resonance:
            resonance_damage = min(max((I_stkr.start_of_combat_HP - stkHPCur) * 2, 6), 12)
            attack += resonance_damage

        attack += I_stkr.true_sp_next_CACHE
        I_stkr.true_sp_next_CACHE = 0

        if curAttack.attackNumSelf == 1:
            attack += I_stkr.true_first_hit

        if curAttack.attackNumSelf != curAttack.attackNumAll:
            attack += I_stkr.true_after_foe_first
            I_stkr.true_after_foe_first = 0

        # true damage on special activation, not counted as special damage
        if stkr_sp_triggered:
            attack += I_stkr.true_sp

        # special-enabled true damage (finish)
        if I_stkr.special_triggered or stkSpCount == 0:
            attack += I_stkr.true_finish

        attack += I_stkr.stacking_retaliatory_damage
        attack += I_stkr.nonstacking_retaliatory_damage

        for x in I_stkr.retaliatory_full_damages_CACHE:
            attack += math.trunc(I_stkr.most_recent_atk * (x / 100))

        # Half damage if staff user without wrathful staff, rounded down
        if striker.getWeaponType() == "Staff" and not I_stkr.wrathful_staff:
            attack = math.trunc(attack * 0.5)

        # potent FU reduction
        attack = trunc(attack * curAttack.potentRedu / 100)

        # the final attack in all it's glory
        full_atk = attack
        I_ster.most_recent_atk = attack # that's a surprise tool that'll help us later

        # damage reduction
        total_reduction = 1

        # DR piercing
        stkr_DRR = 1

        for pierce in I_stkr.damage_reduction_reduction:
            stkr_DRR *= 1 - (pierce/100)

        # Resonance Piercing
        if I_stkr.resonance:
            stkr_DRR *= (min(max((I_stkr.start_of_combat_HP - stkHPCur) * 10, 30), 60)) / 100

        if not (I_stkr.always_pierce_DR or
                (stkr_sp_triggered and I_stkr.sp_pierce_DR) or
                (curAttack.isFollowUp and I_stkr.pierce_DR_FU) or
                (I_stkr.sp_pierce_after_def_sp_CACHE)):
            for x in curReduction:
                total_reduction *= 1 - (x / 100 * stkr_DRR)  # change by redu factor

        I_stkr.sp_pierce_after_def_sp_CACHE = False

        for x in curSpecialReduction:
            total_reduction *= 1 - (x / 100)

        # defensive specials
        if steSpCount == 0 and strikee.getSpecialType() == "Defense" and not I_ster.special_disabled:
            if attacker.getRange() == 1 and "closeShield" in steSpEffects:
                if not is_in_sim: print(strikee.name + " procs " + strikee.getSpName() + ".")
                total_reduction *= 1 - (0.10 * steSpEffects["closeShield"])
                if I_ster.double_def_sp_charge:
                    total_reduction *= 1 - (0.10 * steSpEffects["closeShield"])

            elif attacker.getRange() == 2 and "distantShield" in steSpEffects:
                if not is_in_sim: print(strikee.name + " procs " + strikee.getSpName() + ".")
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

        # Extra true daamge only if defensive special triggered
        if ster_sp_triggered and strikee.getSpecialType() == "Defense":
            attack = max(attack - I_ster.TDR_on_def_sp, 0)

        curMiracleTriggered = False

        circlet_of_bal_cond = stkSpCount == 0 or steSpCount == 0 or I_stkr.special_triggered or I_ster.special_triggered

        # non-special Miracle
        if ((I_ster.pseudo_miracle or circlet_of_bal_cond and I_ster.circlet_miracle) and steHPCur - attack < 1 and steHPCur > 1) and not I_ster.disable_foe_miracle:
            attack = steHPCur - 1
            curMiracleTriggered = True

        # special Miracle
        if steSpCount == 0 and "miracleSP" in steSpEffects and steHPCur - attack < 1 and steHPCur > 1 and not I_ster.pseudo_miracle:
            if not is_in_sim: print(strikee.name + " procs " + strikee.getSpName() + ".")
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

        elif "iceMirrorII" in steSpEffects and ster_sp_triggered:
            I_ster.stacking_retaliatory_damage += math.trunc(steStats[RES] * 0.40)

        # divine recreation, ginnungagap (weapon)
        if I_ster.retaliatory_reduced:
            I_ster.nonstacking_retaliatory_damage = (full_atk - attack) * I_ster.retaliatory_reduced

        # brash assault 4, counter roar
        I_ster.retaliatory_full_damages_CACHE = I_ster.retaliatory_full_damages[:]

        # the attack™
        steHPCur -= attack  # goodness gracious

        if not is_in_sim: print(striker.name + " attacks " + strikee.name + " for " + str(attack) + " damage.")  # YES THEY DID

        # used for determining full attack damage
        presented_attack = attack
        # to evaluate noontime heal on hit that kills
        if steHPCur < 1: attack += steHPCur

        stkSpCount = max(stkSpCount - (1 + I_stkr.spGainOnAtk), 0)
        steSpCount = max(steSpCount - (1 + I_ster.spGainWhenAtkd), 0)

        if stkr_sp_triggered:
            stkSpCount = striker.specialMax
            if I_stkr.triggered_sp_charge != 0:
                stkSpCount -= I_stkr.triggered_sp_charge
                stkSpCount = max(stkSpCount, 0)
                I_stkr.triggered_sp_charge = 0

            I_stkr.true_sp_next_CACHE = I_stkr.true_sp_next

            for x in I_stkr.DR_sp_trigger_next_all_SP:
                I_stkr.DR_sp_trigger_next_all_SP_CACHE.append(x)

        if ster_sp_triggered:
            steSpCount = strikee.specialMax
            if I_ster.triggered_sp_charge != 0:
                steSpCount -= I_ster.triggered_sp_charge
                steSpCount = max(steSpCount, 0)
                I_ster.triggered_sp_charge = 0

            I_ster.true_sp_next_CACHE = I_ster.true_sp_next

            if I_ster.sp_pierce_after_def_sp:
                I_ster.sp_pierce_after_def_sp_CACHE = True

        # healing
        totalHealedAmount = 0

        mid_combat_skill_dmg = I_stkr.all_hits_heal + I_stkr.finish_mid_combat_heal * (stkSpCount == 0 or I_stkr.special_triggered)
        surge_heal = I_stkr.surge_heal

        # save for skills
        # += trunc(stkStats[0] * (min(striker.getMaxSpecialCooldown() * 20 + 10, 100) / 100))

        totalHealedAmount += mid_combat_skill_dmg

        if curAttack.isFollowUp:
            totalHealedAmount += I_stkr.follow_up_heal

        # Absorb staff
        if "absorb" in striker.getSkills():
            totalHealedAmount += math.trunc(attack * 0.5)

        # Surge heal
        if stkr_sp_triggered:
            totalHealedAmount += surge_heal

            # Specials that heal (Daylight, Sol, etc.)
            if "healSelf" in stkSpEffects:
                totalHealedAmount += math.trunc(attack * 0.01 * stkSpEffects["healSelf"])

        if Status.DeepWounds in striker.statusNeg or I_ster.disable_foe_healing:
            total_allowance = 1

            for allowance in I_stkr.deep_wounds_allowance:
                total_allowance *= (1 - allowance/100)

            totalHealedAmount -= trunc(totalHealedAmount * total_allowance)

        stkHPCur += totalHealedAmount
        if stkHPCur > stkStats[0]: stkHPCur = stkStats[0]

        if not is_in_sim and totalHealedAmount: print(striker.name + " heals " + str(totalHealedAmount) + " HP during combat.")

        return stkHPCur, steHPCur, stkSpCount, steSpCount, presented_attack, totalHealedAmount, stkr_sp_triggered

    # burn damage

    burn_damages = [0, 0]

    if "A" in startString2:
        defHPCur = max(defHPCur - atkr.foe_burn_damage, 1)
        atkHPCur = max(atkHPCur - atkr.self_burn_damage, 1)

        burn_damages[0] += atkr.foe_burn_damage
        burn_damages[1] += atkr.self_burn_damage

    if "D" in startString2:
        atkHPCur = max(atkHPCur - defr.foe_burn_damage, 1)
        defHPCur = max(defHPCur - defr.self_burn_damage, 1)

        burn_damages[1] += defr.foe_burn_damage
        burn_damages[0] += defr.self_burn_damage

    # PERFORM THE ATTACKS

    i = 0
    while i < len(attackList) and (atkAlive and defAlive or is_in_sim):
        curAtk = attackList[i]

        # post-combat status effects & mid-combat special charges
        if curAtk.attackOwner == 0 and curAtk.attackNumSelf == 1 and atkAlive:

            atkPostCombatEffs[0] += atkPostCombatEffs[2]
            defPostCombatEffs[0] += defPostCombatEffs[1]

            atkSpCountCur = max(0, atkSpCountCur - atkr.sp_charge_first)
            atkSpCountCur = min(atkSpCountCur, attacker.specialMax)

            defSpCountCur = max(0, defSpCountCur - defr.sp_charge_foe_first)

        # On attacker's follow-up attack
        if curAtk.attackOwner == 0 and (
                curAtk.attackNumSelf == 2 and not atkr.brave or curAtk.attackNumSelf == 3 and atkr.brave):
            atkSpCountCur = max(0, atkSpCountCur - atkr.sp_charge_FU)
            atkSpCountCur = min(atkSpCountCur, attacker.specialMax)

        if curAtk.attackOwner == 1 and curAtk.attackNumSelf == 1 and defAlive:

            defPostCombatEffs[0] += defPostCombatEffs[2]
            atkPostCombatEffs[0] += atkPostCombatEffs[1]

            defSpCountCur = max(0, defSpCountCur - defr.sp_charge_first)
            defSpCountCur = min(defSpCountCur, defender.specialMax)

            atkSpCountCur = max(0, atkSpCountCur - atkr.sp_charge_foe_first)

        # On defender's follow-up attack
        if curAtk.attackOwner == 1 and (
                curAtk.attackNumSelf == 2 and not defr.brave or curAtk.attackNumSelf == 3 and defr.brave):
            defSpCountCur = max(0, defSpCountCur - defr.sp_charge_FU)
            defSpCountCur = min(defSpCountCur, defender.specialMax)

        # If unit has a percentage that changes upon special activation, set to new percentage
        # i.e. Lodestar Rush
        if (
                atkr.special_triggered or atkSpCountCur == 0) and atkr.potent_new_percentage != -1 and i == atkPotentIndex:
            curAtk.potentRedu = 100

        if (
                defr.special_triggered or defSpCountCur == 0) and defr.potent_new_percentage != -1 and i == defPotentIndex:
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

            if atkr.special_triggered or atkSpCountCur == 0 or defr.special_triggered or defSpCountCur == 0:
                special_damage_reductions += defr.DR_sp_trigger_by_any_special_SP
                defr.DR_sp_trigger_by_any_special_SP = []

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

            if atkr.special_triggered or atkSpCountCur == 0 or defr.special_triggered or defSpCountCur == 0:
                special_damage_reductions += atkr.DR_sp_trigger_by_any_special_SP
                atkr.DR_sp_trigger_by_any_special_SP = []

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

        strikeResult = attack(roles[spongebob], roles[patrick], effects[spongebob], effects[patrick],
                              stats[spongebob],
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

        stkSpecialTriggered = strikeResult[6]

        curAtk.impl_atk(stkSpecialTriggered, damageDealt, healthHealed, (atkSpCountCur, defSpCountCur),
                        (atkHPCur, defHPCur))

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

    # Post Combat Effects (that require the user to survive)
    if "specialSpiralW" in atkSkills and atkr.special_triggered:
        spiral_charge = math.ceil(atkSkills["specialSpiralW"] / 2)
        atkPostCombatEffs[0].append(("sp_charge", spiral_charge, "self", "one"))

    if "specialSpiralW" in defSkills and defSkills["specialSpiralW"] > 1 and defr.special_triggered:
        spiral_charge = math.ceil(defSkills["specialSpiralW"] / 2)
        defPostCombatEffs[0].append(("sp_charge", spiral_charge, "self", "one"))

    if "specialSpiralS" in atkSkills and atkr.special_triggered:
        spiral_charge = math.ceil(atkSkills["specialSpiralS"] / 2)
        atkPostCombatEffs[0].append(("sp_charge", spiral_charge, "self", "one"))

    if "specialSpiralS" in defSkills and defSkills["specialSpiralS"] > 1 and defr.special_triggered:
        spiral_charge = math.ceil(defSkills["specialSpiralS"] / 2)
        defPostCombatEffs[0].append(("sp_charge", spiral_charge, "self", "one"))

    # Cymbeline (Base) - Sanaki
    # Requires her to be alive
    if "sanakiBuff" in atkSkills and atkAlive:
        atkPostCombatEffs[0].append(("buff_atk", 4, "allies", "within_1_spaces_self"))

    # Bunny Fang (Base) - Yarne
    if "yarnePulse" in atkSkills and atkHPCur / atkStats[HP] <= 0.75 and atkAlive:
        atkPostCombatEffs[UNCONDITIONAL].append(("sp_charge", 2, "self", "one"))

    if "yarnePulse" in defSkills and atkHPCur / defStats[HP] <= 0.75 and defAlive:
        atkPostCombatEffs[UNCONDITIONAL].append(("sp_charge", 2, "self", "one"))

    if "yarneRefinePulse" in atkSkills and atkHPCur / atkStats[HP] <= 0.90 and atkAlive:
        atkPostCombatEffs[UNCONDITIONAL].append(("sp_charge", 2, "self", "one"))

    if "yarneRefinePulse" in defSkills and defHPCur / defStats[HP] <= 0.90 and defAlive:
        atkPostCombatEffs[UNCONDITIONAL].append(("sp_charge", 2, "self", "one"))

    # Poison Strike
    if "poisonStrike" in atkSkills and atkAlive:
        atkPostCombatEffs[0].append(("damage", atkSkills["poisonStrike"], "foe", "one"))

    # Breath of Life
    if "breath_of_life" in atkSkills and atkAlive:
        atkPostCombatEffs[0].append(("heal", atkSkills["breath_of_life"], "allies", "within_1_spaces_self"))

    # Savage Blow
    if "savageBlow" in atkSkills and atkAlive:
        atkPostCombatEffs[0].append(("damage", atkSkills["savageBlow"], "foes_allies", "within_2_spaces_foe"))

    if "easterHealA" in atkSkills and atkAlive:
        atkPostCombatEffs[0].append(("heal", 4, "self", "one"))

    if "bridalBuffsA" in atkSkills and atkAlive:
        atkPostCombatEffs[0].append(("buff_def", 2, "allies", "within_2_spaces_self"))
        atkPostCombatEffs[0].append(("buff_res", 2, "allies", "within_2_spaces_self"))

    if "clarisseDebuffA" in atkSkills and atkAlive:
        atkPostCombatEffs[0].append(("debuff_atk", 5, "foes_allies", "within_2_spaces_foe"))
        atkPostCombatEffs[0].append(("debuff_spd", 5, "foes_allies", "within_2_spaces_foe"))

    # ARE YA SMOKING YET?
    if "atkSmoke" in atkSkills and atkAlive: atkPostCombatEffs[0].append(("debuff_atk", atkSkills["atkSmoke"], "foes_allies", "within_2_spaces_foe"))
    if "atkSmoke" in defSkills and defAlive: defPostCombatEffs[0].append(("debuff_atk", defSkills["atkSmoke"], "foes_allies", "within_2_spaces_foe"))

    if "spdSmoke" in atkSkills and atkAlive: atkPostCombatEffs[0].append(("debuff_spd", atkSkills["spdSmoke"], "foes_allies", "within_2_spaces_foe"))
    if "spdSmoke" in defSkills and defAlive: defPostCombatEffs[0].append(("debuff_spd", defSkills["spdSmoke"], "foes_allies", "within_2_spaces_foe"))

    if "defSmoke" in atkSkills and atkAlive: atkPostCombatEffs[0].append(("debuff_def", atkSkills["defSmoke"], "foes_allies", "within_2_spaces_foe"))
    if "defSmoke" in defSkills and defAlive: defPostCombatEffs[0].append(("debuff_def", defSkills["defSmoke"], "foes_allies", "within_2_spaces_foe"))

    if "resSmoke" in atkSkills and atkAlive: atkPostCombatEffs[0].append(("debuff_res", atkSkills["defSmoke"], "foes_allies", "within_2_spaces_foe"))
    if "resSmoke" in defSkills and defAlive: defPostCombatEffs[0].append(("debuff_res", defSkills["defSmoke"], "foes_allies", "within_2_spaces_foe"))

    if "pulseSmoke" in atkSkills and atkAlive:
        if atkSkills["pulseSmoke"] == 1:
            area = "within_1_spaces_foe"
        else:
            area = "within_2_spaces_foe"

        atkPostCombatEffs[UNCONDITIONAL].append(("charge_sp", -1, "foe_and_foes_allies", area))

    if "pulseSmoke" in defSkills and defAlive and defSkills["pulseSmoke"] == 3:
        defPostCombatEffs[UNCONDITIONAL].append(("charge_sp", -1, "foe_and_foes_allies", "within_2_spaces_foe"))

    if "panicSmoke" in atkSkills and atkAlive:
        if atkSkills["panicSmoke"] == 1:
            area = "within_1_spaces_foe"
        else:
            area = "within_2_spaces_foe"

        atkPostCombatEffs[UNCONDITIONAL].append(("status", Status.Panic, "foe_and_foes_allies", area))

    if "panicSmoke" in defSkills and defAlive and defSkills["panicSmoke"] == 3:
        defPostCombatEffs[UNCONDITIONAL].append(("status", Status.Panic, "foe_and_foes_allies", "within_2_spaces_foe"))

    # Wizened Breath (Base) - Bantu
    if "bantuBoost" in atkSkills and atkHPGreaterEqual25Percent and atkAlive:
        atkPostCombatEffs[0].append(("debuff_atk", 6, "foe", "one"))
        atkPostCombatEffs[0].append(("debuff_spd", 6, "foe", "one"))
        atkPostCombatEffs[0].append(("debuff_def", 6, "foe", "one"))
        atkPostCombatEffs[0].append(("debuff_res", 6, "foe", "one"))

    if "bantuBoost" in defSkills and defHPGreaterEqual25Percent and defAlive:
        defPostCombatEffs[0].append(("debuff_atk", 6, "foe", "one"))
        defPostCombatEffs[0].append(("debuff_spd", 6, "foe", "one"))
        defPostCombatEffs[0].append(("debuff_def", 6, "foe", "one"))
        defPostCombatEffs[0].append(("debuff_res", 6, "foe", "one"))

    # Élivágar (Veronica)
    if "veronicaPanic" in atkSkills and atkAlive:
        atkPostCombatEffs[0].append(("status", Status.Panic, "foes_allies", "within_2_spaces_foe"))

    if "Fire Emblem" in atkSkills and atkr.special_triggered:
        b = atkSkills["Fire Emblem"]

        atkPostCombatEffs[UNCONDITIONAL].append(("buff_atk", b, "self_and_allies", "global"))
        atkPostCombatEffs[UNCONDITIONAL].append(("buff_spd", b, "self_and_allies", "global"))
        atkPostCombatEffs[UNCONDITIONAL].append(("buff_def", b, "self_and_allies", "global"))
        atkPostCombatEffs[UNCONDITIONAL].append(("buff_res", b, "self_and_allies", "global"))

    if "Fire Emblem" in defSkills and defr.special_triggered:
        b = defSkills["Fire Emblem"]

        defPostCombatEffs[UNCONDITIONAL].append(("buff_atk", b, "self_and_allies", "global"))
        defPostCombatEffs[UNCONDITIONAL].append(("buff_spd", b, "self_and_allies", "global"))
        defPostCombatEffs[UNCONDITIONAL].append(("buff_def", b, "self_and_allies", "global"))
        defPostCombatEffs[UNCONDITIONAL].append(("buff_res", b, "self_and_allies", "global"))

    atkFehMath = min(max(atkStats[ATK] - defStats[atkTargetingDefRes + 3], 0) + atkr.true_all_hits, 99)
    defFehMath = min(max(defStats[ATK] - atkStats[defTargetingDefRes + 3], 0) + defr.true_all_hits, 99)

    if attacker.getWeaponType() == "Staff" and (not atkr.wrathful_staff or defr.disable_foe_wrathful):
        atkFehMath = atkFehMath // 2

    if defender.getWeaponType() == "Staff" and (not defr.wrathful_staff or atkr.disable_foe_wrathful):
        defFehMath = defFehMath // 2

    atkHitCount = startString2.count("A")
    defHitCount = startString2.count("D")

    return atkHPCur, defHPCur, atkCombatBuffs, defCombatBuffs, wpnAdvHero, atkHasEffectiveness, defHasEffectiveness, \
        attackList, atkFehMath, atkHitCount, defFehMath, defHitCount, atkPostCombatEffs[0], defPostCombatEffs[0], burn_damages


# Get AOE damage from attacker to foe

def get_AOE_damage(attacker, defender):
    atkSkills = attacker.getSkills()
    atkStats = attacker.getStats()

    defSkills = defender.getSkills()
    defStats = defender.getStats()

    atkPhantomStats = [0] * 5
    defPhantomStats = [0] * 5

    if "phantomSpd" in atkSkills: atkPhantomStats[SPD] += atkSkills["phantomSpd"]
    if "phantomRes" in atkSkills: atkPhantomStats[RES] += atkSkills["phantomRes"]
    if "phantomSpd" in defSkills: defPhantomStats[SPD] += defSkills["phantomSpd"]
    if "phantomRes" in defSkills: defPhantomStats[RES] += defSkills["phantomRes"]

    # Easy Method
    def allies_within_n(unit, tile, n):
        unit_list = tile.unitsWithinNSpaces(n)
        returned_list = []

        for x in unit_list:
            if unit.isAllyOf(x):
                returned_list.append(x)

        return returned_list

    # Panic Status Effect
    AtkPanicFactor = 1
    DefPanicFactor = 1

    # buffs + debuffs calculation
    # throughout combat, PanicFactor * buff produces the current buff value
    if Status.Panic in attacker.statusNeg: AtkPanicFactor *= -1
    if Status.Panic in defender.statusNeg: DefPanicFactor *= -1

    if Status.NullPanic in attacker.statusPos: AtkPanicFactor = 1
    if Status.NullPanic in defender.statusPos: DefPanicFactor = 1

    atkStats[ATK] += attacker.buffs[ATK] * AtkPanicFactor + attacker.debuffs[ATK]
    atkStats[SPD] += attacker.buffs[SPD] * AtkPanicFactor + attacker.debuffs[SPD]
    atkStats[DEF] += attacker.buffs[DEF] * AtkPanicFactor + attacker.debuffs[DEF]
    atkStats[RES] += attacker.buffs[RES] * AtkPanicFactor + attacker.debuffs[RES]

    defStats[ATK] += defender.buffs[ATK] * DefPanicFactor + defender.debuffs[ATK]
    defStats[SPD] += defender.buffs[SPD] * DefPanicFactor + defender.debuffs[SPD]
    defStats[DEF] += defender.buffs[DEF] * DefPanicFactor + defender.debuffs[DEF]
    defStats[RES] += defender.buffs[RES] * DefPanicFactor + defender.debuffs[RES]

    atkr_atk = atkStats[ATK]

    atkTargetingDefRes = int(attacker.getTargetedDef() == 1)

    def_disable_foe_hexblade = False

    if "disableFoeHexblade" in defSkills or "mysticBoost" in defSkills:
        def_disable_foe_hexblade = True

    if attacker.getTargetedDef() == 0 and not "oldDragonstone" in atkSkills and not def_disable_foe_hexblade:
        if defender.getRange() == 2 and defStats[3] > defStats[4]:
            atkTargetingDefRes += 1
        elif defender.getRange() != 2:
            atkTargetingDefRes += 1
    elif attacker.getTargetedDef() == 0:
        atkTargetingDefRes += 1

    if "permHexblade" in atkSkills and not def_disable_foe_hexblade: atkTargetingDefRes = int(defStats[3] < defStats[4])

    defensive_terrain = False

    if defender.tile and defender.tile.is_def_terrain == 1:
        defensive_terrain = True

    if defensive_terrain:
        defr_def = math.ceil(defStats[3 + atkTargetingDefRes] * 1.3)
    else:
        defr_def = defStats[3 + atkTargetingDefRes]

        power_int = atkSkills["aoe_power"]

    true_damage = 0

    if "SpdDmg" in atkSkills and atkStats[SPD] + atkPhantomStats[SPD] > defStats[SPD] + defPhantomStats[SPD]:
        difference = (atkStats[SPD] + atkPhantomStats[SPD]) - (defStats[SPD] + defPhantomStats[SPD])
        true_damage += min(math.trunc(difference * 0.1 * atkSkills["SpdDmg"]), atkSkills["SpdDmg"])

    # L!Alm
    if "lunaArcDmg" in atkSkills or "refineArcDmg" in atkSkills:
        true_damage += trunc(defStats[DEF] * 0.25)

    # Kliff
    if "kliffBoostRefine" in atkSkills and defStats[ATK] + defPhantomStats[ATK] > atkStats[ATK] + atkPhantomStats[ATK]:
        true_damage += trunc(defStats[ATK] * 0.15)

    # Python
    if "pythonBoost" in attacker.HPcur / atkStats[HP] >= 0.25:
        true_damage += 7

    # Ares
    if "DRINK" in atkSkills and defender.HPcur / defStats[HP] >= 0.75:
        true_damage += 7

    # Leif
    if "thraciaMoment" in atkSkills and defStats[DEF] >= defStats[RES] + 5:
        true_damage += 7

    # L!Leif
    if "leifWhyDoesHeHaveAOEDamageOnThis" in atkSkills:
        true_damage += trunc(defStats[ATK] * 0.10)

    # Igrene
    if "igreneBoost" in atkSkills:
        true_damage += trunc(atkStats[SPD] * 0.10)

    # L!Eliwood
    if "hamburger" in atkSkills:
        true_damage += math.trunc(defStats[DEF] * 0.15)

    # Swift Mulagir (Refine Eff) - L!Lyn
    if "i got her from my first AHR summon and foddered her immediately" in atkSkills:
        true_damage += trunc(atkStats[SPD] * 0.15)

    # Legault
    if "ghetsis holding a ducklett" in atkSkills and attacker.HPcur / atkStats[HP] >= 0.25 and atkStats[SPD] + atkPhantomStats[SPD] > defStats[SPD] + defPhantomStats[SPD]:
        true_damage += 5

    # Ross
    if "hisFathersSonsFathersSonsFathersSons" in atkSkills:
        true_damage += trunc(attacker.HPcur * 0.15)

    # Naesala
    if "naesalaBoost" in atkSkills:
        true_damage += trunc(atkStats[SPD] * 0.15)

    # Altina
    if "newChosen" in atkSkills and (all([ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS for ally in allies_within_n(attacker, attacker.attacking_tile, 1)]) or defender.HPcur / defStats[HP] >= 0.75):
        if atkStats[RES] + atkPhantomStats[RES] > defStats[RES] + defPhantomStats[RES]:
            true_damage += min(math.trunc(((atkStats[RES] + atkPhantomStats[RES]) - (defStats[RES] + defPhantomStats[RES])) * 0.7), 7)

    # Gaius
    if "gaius_damage_ref" in atkSkills and defStats[HP] == defender.HPcur:
        true_damage += 7

    # Libra
    if "libraDebuff" in atkSkills:
        true_damage += 7

    # Panne
    if "panneStuff" in atkSkills and atkSkills and attacker.HPcur / atkStats[HP] >= 0.25 and (atkStats[SPD] + atkPhantomStats[SPD]) - (defStats[SPD] + defPhantomStats[SPD]) >= 5:
        true_damage += 7

    # Yarne
    if "yarneBoost" in atkSkills and defender.HPcur / defStats[HP] >= 0.50:
        true_damage += trunc(atkStats[SPD] * 0.10)

    # You figure it out
    if "I'm Shigure" in atkSkills:
        true_damage += 7

    # L!Ryoma
    if "bushidoII" in atkSkills:
        true_damage += 7

    # AD!Camilla
    if "I should be studying for my finals lol" in atkSkills and attacker.HPcur / atkStats[HP] >= 0.25:
        true_damage += trunc(atkStats[ATK] * 0.15)

    # Kaze
    if "he kinda sounds like Joker Persona 5" in atkSkills and attacker.HPcur / atkStats[HP] >= .25 and atkStats[SPD] + atkPhantomStats[SPD] > defStats[SPD] + defPhantomStats[SPD]:
        true_damage += 5

    # Edelgard
    if "another 3 years" in atkSkills:
        true_damage += trunc(atkStats[ATK] * 0.10)

    # Dimitri
    if "of fire emblem" in atkSkills:
        true_damage += trunc(atkStats[ATK] * 0.10)

    # Ylgr
    if "ylgrMoreBoost" in atkSkills and (atkStats[SPD] + atkPhantomStats[SPD] > defStats[SPD] + defPhantomStats[SPD] or defender.HPcur / defStats[HP] >= 0.75):
        true_damage += trunc(atkStats[SPD] * 0.15)

    # General Special Damage
    if "spDamageAdd" in atkSkills:
        true_damage += atkSkills["spDamageAdd"]

    # Heavy Blade 4
    if "heavyBladeDmg" in atkSkills and atkStats[ATK] + atkPhantomStats[ATK] > defStats[ATK] + defPhantomStats[ATK]:
        true_damage += 5

    # Flashing Blade 4
    if "flashingBladeDmg" in atkSkills and atkStats[SPD] + atkPhantomStats[SPD] > defStats[SPD] + defPhantomStats[SPD]:
        true_damage += 5

    # Wrath
    if "wrathSk" in atkSkills and attacker.HPcur / atkStats[HP] <= atkSkills["wrathSk"] * 0.25:
        true_damage += 10

    if "wrathW" in atkSkills and attacker.HPcur / atkStats[HP] <= atkSkills["wrathW"] * 0.25:
        true_damage += 10

    if "sprunSk" in atkSkills and attacker.HPcur / atkStats[HP] <= atkSkills["sprunSk"] * 0.25:
        true_damage += 5

    if Status.Exposure in defender.statusNeg:
        true_damage += 10

    # AOE Damage Reduction
    aoe_damage_reduction = []
    stat_scaling_DR = []

    if Status.Dodge in attacker.statusPos: stat_scaling_DR.append((SPD, 40))

    if "dodgeSk" in defSkills and defPhantomStats[SPD] > atkPhantomStats[SPD]:
        stat_scaling_DR.append((SPD, defSkills["dodgeSk"] * 10))

    # Gharnef
    if "gharnefBoost" in defSkills and defender.HPcur / defStats[HP] >= 0.25 and attacker.wpnType not in TOME_WEAPONS:
        aoe_damage_reduction.append(30)

    # Nagi
    if "nagiAOEReduce" in defSkills or "nagiRefineBoost" in defSkills:
        aoe_damage_reduction.append(80)

    if "nagiReduction" in defSkills:
        stat_scaling_DR.append((RES, 40))

    # Conrad
    if "mmm melon collie" in defSkills and defender.HPcur / defStats[HP] >= 0.25:
        stat_scaling_DR.append((RES, 40))

    # L!Julia
    if "LJuliaRefineBoost" in atkSkills and (defStats[ATK] + defPhantomStats[ATK] > atkStats[DEF] + atkPhantomStats[DEF] or attacker.HPcur / atkStats[HP] >= 0.75):
        stat_scaling_DR.append((RES, 40))

    # Julius
    dragon_eff_strs = ["effDragon", "effDragonBeast", "nagiAOEReduce", "nagiRefineBoost"]

    if "juliusDebuffPlus" in defSkills and not (any(dragon_eff_strs == skill for skill in defSkills) or Status.EffDragons in attacker.statusPos):
        stat_scaling_DR.append((RES, 40))

    # Rutger
    if "like the university" in defSkills and defender.HPcur / defStats[HP] >= 0.25:
        stat_scaling_DR.append((SPD, 40))

    # B!Eliwood
    if "nininiRef" in defSkills and allies_within_n(defender, defender.tile, 2):
        stat_scaling_DR.append((SPD, 40))

    # Legault
    if "ghetsis holding a ducklett" in defSkills:
        stat_scaling_DR.append((SPD, 30))

    # L!Eirika
    if "Just Lean" in defSkills and defender.HPcur / defStats[HP] >= 0.25:
        stat_scaling_DR.append((SPD, 40))

    # Caineghis
    if "cainDR" in defSkills:
        aoe_damage_reduction.append(70)

    # Altina
    if "newChosen" in defSkills and (all([ally.wpnType in DRAGON_WEAPONS + BEAST_WEAPONS for ally in allies_within_n(defender, defender.tile, 1)]) or attacker.HPcur / atkStats[HP] >= 0.75):
        stat_scaling_DR.append((RES, 40))

    # L!Ryoma
    if "bushidoII" in defSkills:
        stat_scaling_DR.append((SPD, 40))

    for stat_type, stat_max in stat_scaling_DR:
        def_total = defStats[stat_type] + defPhantomStats[stat_type]
        atk_total = atkStats[stat_type] + atkPhantomStats[stat_type]

        if def_total > atk_total:
            aoe_damage_reduction.append(min(stat_max / 10 * (def_total - atk_total), stat_max))

    final_damage = 0

    if power_int == 0:
        final_damage = max(trunc(0.8 * (atkr_atk - defr_def)), 0) + true_damage
    elif power_int == 1:
        final_damage = max(atkr_atk - defr_def, 0) + true_damage
    elif power_int == 2:
        final_damage = max(trunc(1.5 * (atkr_atk - defr_def)), 0) + true_damage

    total_reduction = 1
    for x in aoe_damage_reduction:
        total_reduction *= 1 - (x / 100)

    rounded_DR = (trunc(total_reduction * 100)) / 100

    reduced_final_attack = math.ceil(final_damage * rounded_DR)

    return reduced_final_attack

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

        self.isSpecial = False
        self.damage = -1
        self.spCharges = (-1, -1)
        self.curHPs = (-1, -1)
        self.healed = -1

        self.potentRedu = potentRedu

        self.is_finisher = False

    def impl_atk(self, isSpecial, damage, healed, spCharges, curHPs):
        self.isSpecial = isSpecial
        self.damage = damage
        self.spCharges = spCharges
        self.curHPs = curHPs
        self.healed = healed

# effects distributed to allies/foes within their combats
# this is a demo, final version should be placed within the map and initialized at the start of game

# exRange1 = lambda s: lambda o: abs(s[0] - o[0]) <= 1  # within 3 columns centers on unit
# exRange2 = lambda s: lambda o: abs(s[0] - o[0]) + abs(s[1] - o[1]) <= 2  # within 2 spaces
# exCondition = lambda s: lambda o: o.hasPenalty()
# exEffect = {"atkRein": 5, "defRein": 5}
# flowerofease_base = {"atkRein": 3, "defRein": 3, "resRein": 3}
# flowerofease_ref = {"atkRein": 4, "defRein": 4, "resRein": 4}

class CombatField:
    def __init__(self, owner, range, condition, affectedSide, effect):
        self.owner = owner
        self.range = range
        self.condition = condition(owner)
        self.affectedSide = affectedSide  # False for different from owner, True otherwise
        self.effect = effect

# flowerOfEaseField = CombatField(mirabilis, exRange1, exCondition, True, flowerofease_base)

# noah = Hero("Noah", 40, 42, 45, 35, 25, "Sword", 0, marthFalchion, luna, None, None, None)
# mio = Hero("Mio", 38, 39, 47, 27, 29, "BDagger", 0, tacticalBolt, moonbow, None, None, None)

player = makeHero("Sharena")
enemy = makeHero("Alfonse")

player_weapon = makeWeapon("Silver Lance+")
enemy_weapon = makeWeapon("Silver Sword+")

# player.set_skill(makeSkill("Triangle Adept 3"), ASKILL)
# player.set_skill(makeSkill("Cancel Affinity 1"), BSKILL)
# player.inflictStatus(Status.CancelAffinity)

# enemy.set_skill(makeSkill("Triangle Adept 1"), ASKILL)
# enemy.set_skill(makeSkill("Cancel Affinity 3"), BSKILL)
# enemy.inflictStatus(Status.CancelAffinity)

# ragnell = Weapon("Emblem Ragnell", "Emblem Ragnell", "", 16, 1, "Sword", {"slaying": 1, "dCounter": 0, "BIGIKEFAN": 1018}, {})
# GREAT_AETHER = Special("Great Aether", "", {"numFoeAtkBoostSp": 4, "AETHER_GREAT": 1018}, 4, "Offense")

# ice_mirror = makeSpecial("Ice Mirror")

# lodestar_rush = Special("Lodestar Rush", "", {"spdBoostSp": 4, "tempo": 0, "potentFix": 100}, 2, "Offense")

player.set_skill(player_weapon, WEAPON)
enemy.set_skill(enemy_weapon, WEAPON)

# enemy.set_skill(ice_mirror, SPECIAL)

# enemy.chargeSpecial(2)

# player.set_skill(makeSkill("Desperation 3"), BSKILL)

# player.inflictDamage(30)
# player.inflictStat(SPD, 20)

'''
potent1 = Skill("Potent 1", "", {"potentStrike": 4})
laguz_friend4 = Skill("Laguz Friend 4", "", {"laguz_friend": 4})

player.set_skill(laguz_friend4, BSKILL)
enemy.set_skill(defStance, ASKILL)

player.chargeSpecial(1)
'''

# final_result = simulate_combat(player, enemy, False, 1, 2, [], aoe_triggered=False, savior_triggered=False)

# print(player.getStats(), enemy.getStats())
# print((final_result[0], final_result[1]))