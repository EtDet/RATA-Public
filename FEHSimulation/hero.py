import json
from math import trunc
from itertools import islice
from enum import Enum

import pandas as pd
import pickle

# CONSTANTS
HP = 0
ATK = 1
SPD = 2
DEF = 3
RES = 4

OMNI = 10

WEAPON = 0
ASSIST = 1
SPECIAL = 2
ASKILL = 3
BSKILL = 4
CSKILL = 5
SSEAL = 6
XSKILL = 7

DV_STONE: int = 1
DV_FLAME: int = 2
DV_GREEN: int = 3
DV_HAZE: int = 4
DV_WATER: int = 5
DV_ICE: int = 6


MELEE_WEAPONS = ["Sword", "Lance", "Axe",
                 "RDragon", "BDragon", "GDragon", "CDragon",
                 "RBeast", "BBeast", "GBeast", "CBeast"]

RANGED_WEAPONS = ["RTome", "BTome", "GTome", "CTome",
                  "RDagger", "BDagger", "GDagger", "CDagger",
                  "RBow", "BBow", "GBow", "CBow",
                  "Staff"]

DRAGON_WEAPONS = ["RDragon", "BDragon", "GDragon", "CDragon"]
BEAST_WEAPONS = ["RBeast", "BBeast", "GBeast", "CBeast"]
BOW_WEAPONS = ["RBow", "BBow", "GBow", "CBow"]
DAGGER_WEAPONS = ["RDagger", "BDagger", "GDagger", "CDagger"]

RED_WEAPONS = ["Sword", "RTome", "RDagger", "RBow", "RDragon", "RBeast"]
BLUE_WEAPONS = ["Lance", "BTome", "BDagger", "BBow", "BDragon", "BBeast"]
GREEN_WEAPONS = ["Axe", "GTome", "GDagger", "GBow", "GDragon", "GBeast"]
COLORLESS_WEAPONS = ["Staff", "CTome", "CDagger", "CBow", "CDragon", "CBeast"]

TOME_WEAPONS = RANGED_WEAPONS[0:4]

PHYSICAL_WEAPONS = ["Sword", "Lance", "Axe"] + BOW_WEAPONS + BEAST_WEAPONS + DRAGON_WEAPONS
MAGICAL_WEAPONS = ["Staff"] + TOME_WEAPONS + DRAGON_WEAPONS

weapons = {
    "Sword": (0, "Sword"), "Lance": (1, "Lance"), "Axe": (2, "Axe"),
    "Staff": (15, "Staff"),
    "RTome": (11, "Red Tome"), "BTome": (12, "Blue Tome"), "GTome": (13, "Green Tome"), "CTome": (14, "Colorless Tome"),
    "CBow": (6, "Colorless Bow"), "RBow": (3, "Red Bow"), "BBow": (4, "Blue Blow"), "GBow": (5, "Green Bow"),
    "CDagger": (10, "Colorless Dagger"), "RDagger": (7, "Red Dagger"), "BDagger": (8, "Blue Dagger"),
    "GDagger": (9, "Green Dagger"),
    "RDragon": (16, "Red Dragon"), "BDragon": (17, "Blue Dragon"), "GDragon": (18, "Green Dragon"),
    "CDragon": (19, "Colorless Dragon"),
    "RBeast": (20, "Red Beast"), "BBeast": (21, "Blue Beast"), "GBeast": (22, "Green Beast"),
    "CBeast": (23, "Colorless Beast")
}

MELEE_STYLES = ["WIND-SWORD"]
RANGED_STYLES = ["ASTRA-STORM", "EMBLEM-LYN", "ECHO"]

# return stat increase needed for level 1 -> 40 based on growth and rarity
def growth_to_increase(value, rarity):
    return trunc(0.39 * (trunc(value * (0.79 + (0.07 * rarity)))))

def sort_indexes(arr):
    indexes = list(range(len(arr)))
    sorted_indexes = sorted(indexes, key=lambda x: (arr[x], -x), reverse=True)
    return sorted_indexes

# adjust level 1 stats to account for adjusting to/from 2★ or 4★ stats
def change_highest_two(array, opp):
    greatest_index1 = -1
    greatest_index2 = -1
    for i in range(1, len(array)):
        if array[i] > array[greatest_index1]:
            greatest_index2 = greatest_index1
            greatest_index1 = i
        elif array[i] > array[greatest_index2]:
            greatest_index2 = i

    array[greatest_index1] += 1 * opp
    array[greatest_index2] += 1 * opp

# Hero object
class Hero:
    def __init__(self, name, intName, epithet, primary_game, secondary_game, wpnType, move, stats, growths, flower_limit, BVID, refresh_type):
        # Unit's displayed name (Julia, Corrin, Ratatoskr, etc.)
        self.name: str = name

        # Unit's unique name (M!Shez, A!Mareeta, HA!F!Grima, etc.)
        self.intName: str = intName

        # Title for this version of a hero, mainly used for retrieving images
        self.epithet: str = epithet

        # Unit's side on the map
        # 0 - player, 1 - enemy
        self.side: int = 0

        # FE Game of Origin
        # 0 - Heroes
        # 1 - Shadow Dragon/(New) Mystery
        # 15 - Gaiden/Echoes
        # 4 - Genealogy of the Holy War
        # 5 - Thracia 776
        # 6 - Binding Blade
        # 7 - Blazing Blade
        # 8 - Sacred Stones
        # 9 - Path of Radiance
        # 10 - Radiant Dawn
        # 13 - Awakening
        # 14 - Fates
        # 16 - Three Houses/Three Hopes
        # 17 - Engage
        # 69 - Tokyo Mirage Sessions ♯FE
        # 99 - Other
        self.primary_game: int = primary_game
        self.secondary_game: int = secondary_game

        # Rarity of hero, 1-5 Stars. Affects base stats.
        self.rarity: int = 5

        # Level of hero, 1-40. Increases stats per level up.
        self.level: int = 40

        # 8-bit integer used for determining level-ups.
        self.BVID: int = BVID

        # Internal stats
        self.stats: list[int] = stats[:]

        # Stats changed by skills
        self.skill_stat_mods: list[int] = [0] * 5

        # Stats changed by:
        # - Legendary/Mythic Blessings
        # - Bonus unit stats (Arena, TT, etc.)
        # Usually not present until unit enters map
        self.battle_stat_mods: list[int] = [0] * 5

        # Visible stats, what is shown in-game
        self.visible_stats: list[int] = stats[:]

        # Current health
        self.HPcur: int = self.visible_stats[HP]

        # Percentage growths for each stat, constant
        self.growths: list[int] = growths

        # level 1 5★ base stats, constant
        self.BASE_STATS: list[int] = stats[:]

        for i in range(0, 5):
            self.BASE_STATS[i] -= growth_to_increase(self.growths[i], self.rarity)

        # field buffs for different stats
        # will not change if hero has Panic effect
        self.buffs: list[int] = [0, 0, 0, 0, 0]

        # field debuffs for different stats, can only be negative
        # Harsh Command converts into buff, removes debuff values from units
        self.debuffs: list[int] = [0, 0, 0, 0, 0]

        # Additional stats that are granted by a skill.
        # They can build over time and are capped by whatever skill is present granting them.
        self.great_talent: list[int] = [0, 0, 0, 0, 0]

        # dictionary of skill strings held by this unit with the skills they have currently equipped
        self.skill_effects: dict[str:int] = {}

        self.statusPos: list[Status] = []  # array of positive status effects currently held, cleared upon start of unit's turn
        self.statusNeg: list[Status] = []  # array of negative status effects currently held, cleared upon end of unit's next action

        self.statusOther = {} # array of other status effects (disable assist effects for certain number of turns, etc.)

        # "disableWeapon"
        # "disableAssist"
        # "disableSpecial"
        # "disableASkill"
        # "disableBSkill"
        # "disableCSkill"
        # "disableEmblem"
        # "callingCircle"

        # specific unit skills
        self.weapon = None
        self.assist = None
        self.special = None
        self.askill = None
        self.bskill = None
        self.cskill = None
        self.sSeal = None
        self.xskill = None

        self.wpnType = wpnType
        self.color = self.getColor()

        # Move type
        # 0 - Infantry, 2 tiles, slowed by forests
        # 1 - Cavalry, 3 tiles, cannot pass forests, slowed by trenches
        # 2 - Flying, 2 tiles, can traverse mountains and water
        # 3 - Armored, 1 tile
        self.move = int(move)

        # Number of tiles allowed to move by move type
        self.moveTiles = -(abs(int(move) - 1)) + 3

        # 0 - No refresh moves
        # 1 - Sing
        # 2 - Dance
        # 3 - Play
        self.refresh_type: int = refresh_type

        # Current special count
        self.specialCount: int = -1

        # Max special count, includes Slaying effects
        self.specialMax: int = -1

        # IV Guide
        # A A A, neutral, no asc asset
        # A A B, neutral, asc asset B
        # A B A, asset A, flaw B, no asc asset
        # A B B, asset A, flaw and asc asset cancel out
        # A B C, asset A, flaw B, asc asset C
        self.asset: int = ATK
        self.flaw: int = ATK
        self.asc_asset: int = ATK

        self.merges: int = 0
        self.flowers: int = 0
        self.flower_limit: int = flower_limit
        self.flower_order = []

        self.emblem = None
        self.emblem_merges: int = 0

        # Ally/Summoner Support
        # 0 - No Rank
        # 1 - C
        # 2 - B
        # 3 - A
        # 4 - S

        self.allySupport = None
        self.allySupportLevel = 4

        self.summonerSupport: int = 0

        self.blessing = None

        self.pair_up = None
        self.pair_up_obj = None

        self.duo_skill = None
        self.duo_cooldown = 0

        self.resp: bool = False
        self.has_resp: bool = False

        self.aided: bool = False

        # --- The following variables are used for simulation ---

        # If unit can currently act this turn
        self.unit_can_act = True

        # Number of times this unit has entered combat in this phase
        self.unitCombatInitiates = 0

        # Number of foes defeated during this turn
        self.num_foes_defeated = 0

        # Number of times this unit has been targeted for assist skill usage
        self.assistTargetedSelf = 0

        # Breakdown by assist type
        self.assistTargetedSelf_Rally = 0
        self.assistTargetedSelf_Move = 0
        self.assistTargetedSelf_Other = 0

        # Number of times this unit has used their assist skill
        self.assistTargetedOther = 0

        # Breakdown by assist type
        self.assistTargetedOther_Rally = 0
        self.assistTargetedOther_Move = 0
        self.assistTargetedOther_Other = 0

        self.specialTriggeredThisTurn = False

        # Number of times other actions have been taken (moving, destorying walls, not counting canto moves)
        self.moveOrDestroyActions = 0

        # Style ready for use
        self.style_ready = True

        # If Canto can be utilized after unit's next action (attacking, breaking, or assisting, etc.)
        self.canto_ready = True

        # Galeforce triggered of each type

        # 1) Share Spoils
        # 2) Priority Specials (Time and Light, Time is Light)
        # 3) Nonspecial Effs w/o priority (Lone Wolf, Override)
        # 4) Special Effs w/o priority (Galeforce)

        self.priority_galeforce_triggered = False
        self.nonspecial_galeforce_triggered = False
        self.special_galeforce_triggered = False
        self.assist_galeforce_triggered = False
        self.move_galeforce_triggered = False
        self.canto_galeforce_triggered = False

        self.once_per_map_cond = False
        self.once_per_turn_cond = False

        self.transformed = False

        self.tile = None # current tile unit is standing on
        self.attacking_tile = None # used for forecasts

    # set unit to level 1, at the assigned rarity
    def set_rarity(self, new_rarity):

        # reset back to 5★, level 1
        self.stats = self.BASE_STATS[:]
        self.level = 1
        self.rarity = 5

        # apply base rarity changes
        self.rarity = new_rarity
        for i in range(0, 2 - trunc(0.5 * (self.rarity - 1))):
            j = 0
            while j < 5:
                self.stats[j] -= 1
                j += 1

        if self.rarity % 2 == 0: change_highest_two(self.stats, +1)

        self.stats[self.asset] += 1
        self.stats[self.flaw] -= 1
        if self.asset != self.asc_asset:
            self.stats[self.asc_asset] += 1

        self.set_visible_stats()

    def set_merges(self, merges):

        self.set_rarity(self.rarity)

        temp_stats = self.stats[:]
        if self.asset != self.asc_asset and self.asset == self.flaw and merges > 0:
            temp_stats[self.asc_asset] = -1

        temp_stats_2 = self.stats[:]
        if self.asset != self.asc_asset and self.asset == self.flaw:
            temp_stats_2[self.asc_asset] -= 1

        first_merge_sort_i = sort_indexes(temp_stats)
        sort_i = sort_indexes(temp_stats_2)

        i = 1
        while i < merges + 1:
            if i == 1:
                if self.asset == self.flaw:
                    self.stats[first_merge_sort_i[0]] += 1
                    self.stats[first_merge_sort_i[1]] += 1
                    self.stats[first_merge_sort_i[2]] += 1
                else:
                    self.stats[self.flaw] += 1

            if i % 5 == 1:
                self.stats[sort_i[0]] += 1
                self.stats[sort_i[1]] += 1
            if i % 5 == 2:
                self.stats[sort_i[2]] += 1
                self.stats[sort_i[3]] += 1
            if i % 5 == 3:
                self.stats[sort_i[4]] += 1
                self.stats[sort_i[0]] += 1
            if i % 5 == 4:
                self.stats[sort_i[1]] += 1
                self.stats[sort_i[2]] += 1
            if i % 5 == 0:
                self.stats[sort_i[3]] += 1
                self.stats[sort_i[4]] += 1

            i += 1

        self.merges = merges



        self.set_visible_stats()

    def set_dragonflowers(self, flowers):
        # set to level 1
        self.set_rarity(self.rarity)
        self.set_merges(self.merges)

        tempHP = self.stats[HP]
        self.stats[HP] = 100
        sort_i = sort_indexes(self.stats[:])
        self.stats[HP] = tempHP

        self.flower_order = sort_i[:]

        i = 1
        while i < flowers + 1:
            self.stats[sort_i[(i-1) % 5]] += 1
            i += 1

        self.flowers = flowers
        self.set_visible_stats()

    def set_emblem_merges(self, merges):
        # set to level 1
        self.set_rarity(self.rarity)
        self.set_merges(self.merges)
        self.set_dragonflowers(self.flowers)

        sort_i = self.flower_order

        i = 1
        while i < merges + 1:
            self.stats[sort_i[(i - 1) % 5]] += 1
            i += 1

        self.emblem_merges = merges
        self.set_visible_stats()

    def set_level(self, level):

        # set to level 1
        self.set_rarity(self.rarity)
        self.set_merges(self.merges)
        self.set_dragonflowers(self.flowers)
        self.set_emblem_merges(self.emblem_merges)

        for i in range(0,5):
            cur_modifier = 0
            if i == self.asset and not (self.merges != 0 and self.asset == self.flaw): cur_modifier += 1
            if i == self.asc_asset and self.asset != self.asc_asset: cur_modifier += 1
            if i == self.flaw and self.merges == 0: cur_modifier -= 1
            cur_modifier = min(cur_modifier, 1)

            stat_growth = growth_to_increase(self.growths[i] + 5 * cur_modifier, self.rarity)
            level_1_base = self.BASE_STATS[i]

            growth = self.growths[i] + 5 * cur_modifier
            applied_growth = trunc(growth * (self.rarity * 0.07 + 0.79))

            offset = -35 + (i * 7)

            vector_offset = (3 * level_1_base + offset + applied_growth + self.BVID) % 64

            required_vector = (stat_growth - 1) * 64 + vector_offset
            required_vector -= 64 * (required_vector//2496)

            required_vector = int(required_vector)

            with open("Spreadsheets/growth_vectors.bin") as file:
                my_slice = list(islice(file, required_vector % 2496, required_vector + 1))

            vector = (''.join(my_slice))[0:40]

            j = 0
            while j < level:
                self.stats[i] += int(vector[j%40]) + required_vector // 2496
                j += 1

        self.level = level
        self.set_visible_stats()

    # Sets enemy stat values, doesn't work currently
    def set_level_enemy(self, old_level, new_level, difficulty):
        # set to level 1
        self.set_rarity(self.rarity)
        self.set_merges(self.merges)
        self.set_dragonflowers(self.flowers)
        self.set_emblem_merges(self.emblem_merges)

        #print(self.rarity)

        for i in range(0,5):
            growth = self.growths[i] #+ 5 * cur_modifier

            # +0.10 for normal?
            # -0.05 for hard?
            # +0.00 for lunatic?
            if difficulty == 0:
                boost = 0.115
            if difficulty == 1:
                boost = -0.05
            if difficulty == 2:
                boost = 0.0

            applied_growth = trunc(growth * 1.115 * (self.rarity * 0.07 + 0.79))

            self.stats[i] += trunc((new_level - old_level) * (applied_growth/100))

        self.level = new_level
        self.set_visible_stats()

    def set_IVs(self, new_asset, new_flaw, new_asc_asset):

        self.asset = new_asset
        self.flaw = new_flaw
        self.asc_asset = new_asc_asset

        #print("END", new_asset, new_flaw, new_asc_asset)

        self.set_level(self.level)

    def set_emblem(self, emblem, emblem_merges):

        self.emblem = emblem
        self.emblem_merges = emblem_merges

        self.set_level(self.level)
        self.set_skill(-1, -1)

    def getColor(self):
        if self.wpnType == "Sword" or self.wpnType == "RBow" or self.wpnType == "RDagger" or self.wpnType == "RTome" or self.wpnType == "RDragon" or self.wpnType == "RBeast":
            return "Red"
        if self.wpnType == "Axe" or self.wpnType == "GBow" or self.wpnType == "GDagger" or self.wpnType == "GTome" or self.wpnType == "GDragon" or self.wpnType == "GBeast":
            return "Green"
        if self.wpnType == "Lance" or self.wpnType == "BBow" or self.wpnType == "BDagger" or self.wpnType == "BTome" or self.wpnType == "BDragon" or self.wpnType == "BBeast":
            return "Blue"
        else:
            return "Colorless"

    def set_skill(self, skill, slot):

        self.remove_skill(slot)

        # If skill is none, undo any changes imposed by the skill instead
        if skill is None:
            return

        # Weapon Skill Add
        if slot == 0:
            self.weapon = skill
            self.skill_stat_mods[ATK] += skill.mt

        # Assist Skill
        if slot == 1:
            self.assist = skill

        # Special Skill
        if slot == 2:
            self.special = skill

        # A Skill
        if slot == 3:
            self.askill = skill

        # B Skill
        if slot == 4:
            self.bskill = skill

        # C Skill
        if slot == 5:
            self.cskill = skill

        # Sacred Seal
        if slot == 6:
            self.sSeal = skill

        # X Skill
        if slot == 7:
            self.xskill = skill

        if "HPBoost" in skill.effects: self.skill_stat_mods[HP] += skill.effects["HPBoost"]
        if "atkBoost" in skill.effects: self.skill_stat_mods[ATK] += skill.effects["atkBoost"]
        if "spdBoost" in skill.effects: self.skill_stat_mods[SPD] += skill.effects["spdBoost"]
        if "defBoost" in skill.effects: self.skill_stat_mods[DEF] += skill.effects["defBoost"]
        if "resBoost" in skill.effects: self.skill_stat_mods[RES] += skill.effects["resBoost"]

        if "atkspdBoost" in skill.effects:
            self.skill_stat_mods[ATK] += skill.effects["atkspdBoost"]
            self.skill_stat_mods[SPD] += skill.effects["atkspdBoost"]

        if "spddefBoost" in skill.effects:
            self.skill_stat_mods[SPD] += skill.effects["spddefBoost"]
            self.skill_stat_mods[DEF] += skill.effects["spddefBoost"]

        if "spdresBoost" in skill.effects:
            self.skill_stat_mods[SPD] += skill.effects["spdresBoost"]
            self.skill_stat_mods[RES] += skill.effects["spdresBoost"]

        if "defresBoost" in skill.effects:
            self.skill_stat_mods[DEF] += skill.effects["defresBoost"]
            self.skill_stat_mods[RES] += skill.effects["defresBoost"]

        if "spectrumBoost" in skill.effects:
            self.skill_stat_mods[ATK] += skill.effects["spectrumBoost"]
            self.skill_stat_mods[SPD] += skill.effects["spectrumBoost"]
            self.skill_stat_mods[DEF] += skill.effects["spectrumBoost"]
            self.skill_stat_mods[RES] += skill.effects["spectrumBoost"]

        if "ninjalynBoost" in skill.effects:
            self.skill_stat_mods[SPD] += skill.effects["ninjalynBoost"]
            self.skill_stat_mods[DEF] -= skill.effects["ninjalynBoost"]
            self.skill_stat_mods[RES] -= skill.effects["ninjalynBoost"]

        if "ninjalynrefineBoost" in skill.effects:
            self.skill_stat_mods[ATK] += 6
            self.skill_stat_mods[SPD] += 6
            self.skill_stat_mods[DEF] -= 4
            self.skill_stat_mods[RES] -= 4

        if "lexBoost" in skill.effects:
            self.skill_stat_mods[HP] += 5
            self.skill_stat_mods[ATK] += 6
            self.skill_stat_mods[SPD] -= 5
            self.skill_stat_mods[DEF] += 6
            self.skill_stat_mods[RES] -= 5

        if self.special is not None:
            self.specialCount = self.special.cooldown
            self.specialMax = self.special.cooldown

            # Slaying effect in weapons
            if self.weapon is not None and "slaying" in self.weapon.effects:
                self.specialCount = max(self.specialCount - self.weapon.effects["slaying"], 1)
                self.specialMax = max(self.specialMax - self.weapon.effects["slaying"], 1)

            # Reverse slaying effect in older staff assists
            if self.assist is not None and "slaying" in self.assist.effects:
                self.specialCount = max(self.specialCount - self.assist.effects["slaying"], 1)
                self.specialMax = max(self.specialMax - self.assist.effects["slaying"], 1)

            # Emblem Marth's slaying effect
            if self.emblem is not None and self.emblem == "Marth":
                self.specialCount = max(self.specialCount - 1, 1)
                self.specialMax = max(self.specialMax - 1, 1)

        else:
            self.specialCount = -1
            self.specialMax = -1

        self.set_visible_stats()

    def remove_skill(self, slot):
        skill = None

        if slot == WEAPON: skill = self.weapon
        if slot == ASSIST: skill = self.assist
        if slot == SPECIAL: skill = self.special
        if slot == ASKILL: skill = self.askill
        if slot == BSKILL: skill = self.bskill
        if slot == CSKILL: skill = self.cskill
        if slot == SSEAL: skill = self.sSeal
        if slot == XSKILL: skill = self.xskill

        # If skill at slot is already None, nothing else to do
        if skill == None:
            return

        # Remove stats granted by current skill
        if "HPBoost" in skill.effects: self.skill_stat_mods[HP] -= skill.effects["HPBoost"]
        if "atkBoost" in skill.effects: self.skill_stat_mods[ATK] -= skill.effects["atkBoost"]
        if "spdBoost" in skill.effects: self.skill_stat_mods[SPD] -= skill.effects["spdBoost"]
        if "defBoost" in skill.effects: self.skill_stat_mods[DEF] -= skill.effects["defBoost"]
        if "resBoost" in skill.effects: self.skill_stat_mods[RES] -= skill.effects["resBoost"]

        if "atkspdBoost" in skill.effects:
            self.skill_stat_mods[ATK] -= skill.effects["atkspdBoost"]
            self.skill_stat_mods[SPD] -= skill.effects["atkspdBoost"]

        if "spddefBoost" in skill.effects:
            self.skill_stat_mods[SPD] -= skill.effects["spddefBoost"]
            self.skill_stat_mods[DEF] -= skill.effects["spddefBoost"]

        if "spdresBoost" in skill.effects:
            self.skill_stat_mods[SPD] -= skill.effects["spdresBoost"]
            self.skill_stat_mods[RES] -= skill.effects["spdresBoost"]

        if "defresBoost" in skill.effects:
            self.skill_stat_mods[DEF] -= skill.effects["defresBoost"]
            self.skill_stat_mods[RES] -= skill.effects["defresBoost"]

        if "spectrumBoost" in skill.effects:
            self.skill_stat_mods[ATK] -= skill.effects["spectrumBoost"]
            self.skill_stat_mods[SPD] -= skill.effects["spectrumBoost"]
            self.skill_stat_mods[DEF] -= skill.effects["spectrumBoost"]
            self.skill_stat_mods[RES] -= skill.effects["spectrumBoost"]

        if "ninjalynBoost" in skill.effects:
            self.skill_stat_mods[SPD] -= skill.effects["ninjalynBoost"]
            self.skill_stat_mods[DEF] += skill.effects["ninjalynBoost"]
            self.skill_stat_mods[RES] += skill.effects["ninjalynBoost"]

        if "ninjalynrefineBoost" in skill.effects:
            self.skill_stat_mods[ATK] -= 6
            self.skill_stat_mods[SPD] -= 6
            self.skill_stat_mods[DEF] += 4
            self.skill_stat_mods[RES] += 4

        if "lexBoost" in skill.effects:
            self.skill_stat_mods[HP] -= 5
            self.skill_stat_mods[ATK] -= 6
            self.skill_stat_mods[SPD] += 5
            self.skill_stat_mods[DEF] -= 6
            self.skill_stat_mods[RES] += 5

        # Remove the skill from the correct slot
        if slot == WEAPON and skill is not None:
            self.skill_stat_mods[ATK] -= skill.mt
            self.weapon = None

        if slot == ASSIST:
            self.assist = None

        if slot == SPECIAL:
            self.specialCount = -1
            self.specialMax = -1
            self.special = None

        if slot == ASKILL: self.askill = None
        if slot == BSKILL: self.bskill = None
        if slot == CSKILL: self.cskill = None
        if slot == SSEAL: self.sSeal = None
        if slot == XSKILL: self.xskill = None

        # Reset special count
        if self.special is not None:
            self.specialCount = self.special.cooldown
            self.specialMax = self.special.cooldown

            # Slaying effect in weapons
            if self.weapon is not None and "slaying" in self.weapon.effects:
                self.specialCount = max(self.specialCount - self.weapon.effects["slaying"], 1)
                self.specialMax = max(self.specialMax - self.weapon.effects["slaying"], 1)

            # Reverse slaying effect in older staff assists
            if self.assist is not None and "slaying" in self.assist.effects:
                self.specialCount = max(self.specialCount - self.assist.effects["slaying"], 1)
                self.specialMax = max(self.specialMax - self.assist.effects["slaying"], 1)

            # Emblem Marth's slaying effect
            if self.emblem and self.emblem == "Marth" and self.weapon:
                self.specialCount = max(self.specialCount - 1, 1)
                self.specialMax = max(self.specialMax - 1, 1)

        # Reset stats
        self.set_visible_stats()

    def set_visible_stats(self):
        i = 0

        # Summoner Support Stats
        while i < 5:
            sum_sup_stat = 0
            if i == 0:
                if self.summonerSupport == 1:
                    sum_sup_stat = 3
                if self.summonerSupport == 2 or self.summonerSupport == 3:
                    sum_sup_stat = 4
                if self.summonerSupport == 4:
                    sum_sup_stat = 5
            else:
                sum_sup_stat = 2 * int(5 - i <= self.summonerSupport)

            self.visible_stats[i] = self.stats[i] + self.skill_stat_mods[i] + sum_sup_stat + self.battle_stat_mods[i]
            self.visible_stats[i] = max(min(self.visible_stats[i], 99), 0)
            i += 1

        # Resplendent Stats
        if self.resp:
            self.visible_stats = [x + 2 for x in self.visible_stats]

        # Aided Stats
        if self.aided:
            self.visible_stats = [x + 1 for x in self.visible_stats]

        self.visible_stats = [int(x) for x in self.visible_stats]
        self.HPcur = self.visible_stats[0]

    # Getting stat with applied buffs and debuffs, not neutralized
    def get_visible_stat(self, STAT):
        panic_factor = 1
        if Status.Panic in self.statusNeg: panic_factor = -1
        if Status.NullPanic in self.statusPos: panic_factor = 1

        buff_applied_stat = self.visible_stats[STAT] + (self.buffs[STAT] * panic_factor) + self.debuffs[STAT] + self.great_talent[STAT]

        if self.transformed and STAT == ATK:
            buff_applied_stat += 2

        return min(max(buff_applied_stat, 0), 99)

    def get_phantom_stat(self, STAT):
        if STAT == ATK: return self.getSkills().get('phantomAtk', 0)
        elif STAT == SPD: return self.getSkills().get('phantomSpd', 0)
        elif STAT == DEF: return self.getSkills().get('phantomDef', 0)
        elif STAT == RES: return self.getSkills().get('phantomRes', 0)

        else:
            return 0

    def get_total_buff(self, STAT):
        self_panic = Status.Panic in self.statusNeg and Status.NullPanic not in self.statusPos

        if self_panic:
            return 0
        else:
            return self.buffs[STAT]

    def get_bonus_total(self):
        self_panic = Status.Panic in self.statusNeg and Status.NullPanic not in self.statusPos

        if self_panic:
            return 0
        else:
            return sum(self.buffs)

    def get_total_debuff(self, STAT):
        self_panic = Status.Panic in self.statusNeg and Status.NullPanic not in self.statusPos

        if self_panic:
            return self.debuffs[STAT] - self.buffs[STAT]
        else:
            return self.debuffs[STAT]

    def get_penalty_total(self):
        self_panic = Status.Panic in self.statusNeg and Status.NullPanic not in self.statusPos

        if self_panic:
            return sum(self.debuffs) - sum(self.buffs)
        else:
            return sum(self.debuffs)

    def inflictStatus(self, status):
        # Positive status
        if status.value >= 100 and status not in self.statusPos:
            self.statusPos.append(status)
            print(self.name + " receives " + status.name + " (+).")

        # Negative status
        elif status.value < 100 and status not in self.statusNeg:
            self.statusNeg.append(status)
            print(self.name + " receives " + status.name + " (-).")

    def clearPosStatus(self):  # called once enemy turn ends
        self.statusPos.clear()

    def clearNegStatus(self):  # called once unit acts
        self.statusNeg.clear()

    def inflictStat(self, stat, num):
        if stat == ATK: statStr = "Atk"
        elif stat == SPD: statStr = "Spd"
        elif stat == DEF: statStr = "Def"
        elif stat == RES: statStr = "Res"
        else: print("Invalid stat change! No changes made."); return

        if num > 0: self.buffs[stat] = max(self.buffs[stat], num)
        if num < 0: self.debuffs[stat] = min(self.debuffs[stat], num)

        if num != 0:
            print(self.name + "'s " + statStr + " was modified by " + str(num) + ".")

    def inflictGreatTalent(self, stat, num, cap):
        num = int(num)
        cap = int(cap)

        if stat == ATK: statStr = "Atk"
        elif stat == SPD: statStr = "Spd"
        elif stat == DEF: statStr = "Def"
        elif stat == RES: statStr = "Res"
        else: print("Invalid stat change! No changes made."); return

        self.great_talent[stat] = min(self.great_talent[stat] + num, cap)

        increase = max(0, min(cap - self.great_talent[stat], num))

        if increase != 0:
            print(self.name + " was given +" + str(increase) + " Great Talent " + statStr + ".")

    def chargeSpecial(self, charge):
        # Will only charge special if charge is >0, and if special is present (-1 represents no special equipped)
        if charge != 0 and self.specialCount != -1:
            # will decrease special count by charge
            self.specialCount = max(0, self.specialCount - charge)
            self.specialCount = min(self.specialCount, self.specialMax)

            if charge < -6:
                print(self.name + "'s special count was reset. Currently is: " + str(self.specialCount))
            else:
                print(self.name + "'s special was charged by " + str(charge) + ". Currently is: " + str(self.specialCount))

    def inflictDamage(self, damage):
        self.HPcur -= damage
        if self.HPcur < 1: self.HPcur = 1
        print(self.name + " takes " + str(damage) + " damage out of combat.")

    def hasBonus(self):
        return (sum(self.buffs) > 0 and Status.Panic not in self.statusNeg) or self.statusPos

    def hasPenalty(self):
        return sum(self.debuffs) < 0 or self.statusNeg

    # Determine which defense stat should be targeted when attacking
    def getTargetedDef(self):
        isTome = self.wpnType == "RTome" or self.wpnType == "BTome" or self.wpnType == "GTome" or self.wpnType == "CTome" or self.wpnType == "Staff"
        isDragon = self.wpnType == "RDragon" or self.wpnType == "BDragon" or self.wpnType == "GDragon" or self.wpnType == "CDragon"

        if isTome: return 1
        elif isDragon: return 0
        else: return -1

    def getRange(self):
        isDragon = self.wpnType in DRAGON_WEAPONS
        isBeast = self.wpnType in BEAST_WEAPONS
        isMeleeWpn = self.wpnType == "Sword" or self.wpnType == "Lance" or self.wpnType == "Axe"
        if isDragon or isBeast or isMeleeWpn: return 1
        else: return 2

    def getWeaponType(self):
        return self.wpnType

    def getWeapon(self):
        if self.weapon is None: return NIL_WEAPON
        return self.weapon

    def getAssist(self):
        return self.assist

    def getSkills(self):
        heroSkills = {}

        if self.weapon is not None:
            heroSkills = {x: heroSkills.get(x, 0) + self.weapon.effects.get(x, 0) for x in set(heroSkills).union(self.weapon.effects)}
        if self.assist is not None:
            heroSkills = {x: heroSkills.get(x, 0) + self.assist.effects.get(x, 0) for x in set(heroSkills).union(self.assist.effects)}
        if self.special is not None:
            heroSkills = {x: heroSkills.get(x, 0) + self.special.effects.get(x, 0) for x in set(heroSkills).union(self.special.effects)}
        if self.askill is not None:
            heroSkills = {x: heroSkills.get(x, 0) + self.askill.effects.get(x, 0) for x in set(heroSkills).union(self.askill.effects)}
        if self.bskill is not None:
            heroSkills = {x: heroSkills.get(x, 0) + self.bskill.effects.get(x, 0) for x in set(heroSkills).union(self.bskill.effects)}
        if self.cskill is not None:
            heroSkills = {x: heroSkills.get(x, 0) + self.cskill.effects.get(x, 0) for x in set(heroSkills).union(self.cskill.effects)}
        if self.sSeal is not None:
            heroSkills = {x: heroSkills.get(x, 0) + self.sSeal.effects.get(x, 0) for x in set(heroSkills).union(self.sSeal.effects)}
        if self.xskill is not None:
            heroSkills = {x: heroSkills.get(x, 0) + self.xskill.effects.get(x, 0) for x in set(heroSkills).union(self.xskill.effects)}

        if self.emblem is not None:
            heroSkills = {x: heroSkills.get(x, 0) + self.getEmblemEffects().get(x, 0) for x in set(heroSkills).union(self.getEmblemEffects())}

        return heroSkills

    def getEmblemEffects(self):
        if self.emblem is None: return {}
        if self.emblem == "Marth": return {"shine on": 1, "slaying": 1}
        if self.emblem == "Celica": return {"care for us": 2}
        if self.emblem == "Sigurd": return {"provide for us": 4}
        if self.emblem == "Leif": return {"free us": 5}
        if self.emblem == "Roy": return {"rise up": 6}
        if self.emblem == "Lyn": return {"sweep across": 7}
        if self.emblem == "Eirika": return {"restore calm": 8}
        if self.emblem == "Ike": return {"fight on": 9}
        if self.emblem == "Micaiah": return {"heal us": 10}
        if self.emblem == "Lucina": return {"reignite us": 13}
        if self.emblem == "Corrin": return {"bare your fangs": 14}
        if self.emblem == "Byleth": return {"teach us": 16}

    def getStats(self):

        stats = self.visible_stats[:]

        if self.transformed:
            stats[ATK] = min(max(0, stats[ATK] + 2), 99)

        for i in range(1, 5):
            stats[i] = min(stats[i] + self.great_talent[i], 99)

        return stats

    def getSpName(self):
        if self.special is None: return "Nil Special"
        return self.special.getName()

    def getSpecialType(self):
        if self.special is not None: return self.special.type
        else: return ""

    def getMaxSpecialCooldown(self):
        if self.special is not None: return self.special.cooldown
        else: return 0

    def isAllyOf(self, other):
        if other is None: return False
        return other.side == self.side and other is not self

    def isEnemyOf(self, other):
        if other is None: return False
        return other.side != self.side

    def isSupportOf(self, other):
        if other is None: return False
        return other.allySupport == self.intName

    def isSameGameAs(self, other):
        if self.primary_game == other.primary_game:
            return True
        elif self.primary_game == other.secondary_game:
            return True
        elif self.secondary_game == other.primary_game:
            return True
        elif self.secondary_game == other.secondary_game and self.secondary_game != -1:
            return True
        else:
            return False

    def get_transform_conditions(self):
        if self.wpnType not in BEAST_WEAPONS or not self.weapon:
            return []

        conditions_arr = ["DEFAULT-BEAST"]

        skill_dict = self.getSkills()

        if "faMuarimBoost" in skill_dict:
            conditions_arr = ["MUARIM-TURNS"]

        if "uncondBeast" in skill_dict:
            conditions_arr.append("NO-CONDITIONS")

        if "uncondBeast100" in skill_dict:
            conditions_arr.append("NO-CONDITIONS-100")

        if "uncondBeast50" in skill_dict:
            conditions_arr.append("NO-CONDITIONS-50")

        if "connectedWorld" in skill_dict:
            conditions_arr.append("ASKR-OTHERWORLD")
            conditions_arr.append("AR-TRANSFORM")

        if "fortuneCond" in skill_dict:
            conditions_arr.append("FORTUNE-BEAST")
            conditions_arr.append("AR-TRANSFORM")

        if "divineBrawn" in skill_dict:
            conditions_arr.append("NO-CONDITIONS")
            conditions_arr.append("AR-TRANSFORM")

        if "severancePlus" in skill_dict:
            conditions_arr.append("EMBLA-SEVERANCE")
            conditions_arr.append("AR-TRANSFORM")

        return conditions_arr

    def get_style_conditions(self, turn):
        present = 0

        styles = []

        unitSkills = self.getSkills()

        # Astra Storm Style
        if "astraStorm" in unitSkills:
            present += 1

            styles.append("ASTRA-STORM")

        # Emblem Lyn Style
        if "sweep across" in unitSkills:
            present += 1

            if "disableEmblem" not in self.statusOther and self.wpnType in RANGED_WEAPONS and turn >= 2:
                styles.append("EMBLEM-LYN")

        # Wind Sword Style
        if "eEirikaBoost" in unitSkills:
            present += 1

            styles.append("WIND-SWORD")

        # Echo Style
        if "suCelicaBoost" in unitSkills:
            present += 1

            styles.append("ECHO")

        if present != 1:
            present = False
            styles = []

        return present, styles

    def __str__(self):
        return self.intName

class Skill:
    def __init__(self, name, desc, letter, tier, effects, exc_users):
        self.name = name
        self.desc = desc
        self.letter = letter
        self.tier = tier
        self.effects = effects
        self.exc_users = exc_users

    def __str__(self):
        return self.name + "\n" + self.desc

class Weapon:
    def __init__(self, name, intName, desc, mt, range, type, effects, exc_users):
        self.name = name
        self.intName = intName
        self.desc = desc
        self.mt = int(mt)
        self.range = int(range)
        self.type = type
        self.effects = effects
        self.exc_users = exc_users

    def __str__(self): print(self.name + " \nMt: " + str(self.mt) + " Rng: " + str(self.range) + "\n" + self.desc)

NIL_WEAPON = Weapon("Nil", "Nil Weapon", "", 0, 1, "Sword", {}, [])

class Assist:
    def __init__(self, name, desc, effects, range, type, users):
        self.name = name
        self.desc = desc
        self.effects = effects
        self.range = range
        self.type = type
        self.users = users

class Special:
    def __init__(self, name, desc, effects, cooldown, type):
        self.name = name
        self.desc = desc
        self.effects = effects
        self.cooldown = cooldown
        self.type = type

    def getName(self): return self.name

FIRE: int = 0
WATER: int = 1
EARTH: int = 2
WIND: int = 3
LIGHT: int = 4
DARK: int = 5
ASTRA: int = 6
ANIMA: int = 7

ARENA_ELEMENTS = [FIRE, WATER, EARTH, WIND]
AETHER_ELEMENTS = [LIGHT, DARK, ASTRA, ANIMA]
BLESSING_NAMES = ["FIRE", "WATER", "EARTH", "WIND", "LIGHT", "DARK", "ASTRA", "ANIMA"]

class Blessing:
    def __init__(self, args):
        # 0 - fire, 1 - water, 2 - earth, 3 - wind
        # 4 - light, 5 - dark, 6 - astra, 7 - anima
        self.element = args[0]

        # 0 - blessing, for non-legendary/mythic unit
        # 1 - legendary effect 1 - stat boost
        #     OR mythic effect 1 - stat boost
        # 2 - legendary effect 2 - pair up
        #     OR mythic effect 2 - stat boost + extra slot
        # 3 - legendary effect 3 - stat boost + pair up
        #     OR mythic effect 3 - stat boost + extra slot + reinforcement
        self.boostType = args[1]

        # 0 - none
        # 1 - atk, 2 - spd, 3 - def, 4 - res
        self.stat = args[2]

    def toString(self):
        elem_str = BLESSING_NAMES[self.element].capitalize()
        type_str = " Legend, " if self.element < 4 else " Mythic, "

        boost_str = ""

        if self.element < 4:
            if self.boostType == 1:
                if self.stat == ATK:
                    boost_str = "Atk"
                if self.stat == SPD:
                    boost_str = "Spd"
                if self.stat == DEF:
                    boost_str = "Def"
                if self.stat == RES:
                    boost_str = "Res"
            elif self.boostType == 2:
                boost_str = "Pair Up"
            elif self.boostType == 3:
                if self.stat == ATK:
                    boost_str = "A/Pair"
                if self.stat == SPD:
                    boost_str = "S/Pair"
                if self.stat == DEF:
                    boost_str = "D/Pair"
                if self.stat == RES:
                    boost_str = "R/Pair"
        else:
            if self.boostType == 1:
                if self.stat == ATK:
                    boost_str = "Atk"
                if self.stat == SPD:
                    boost_str = "Spd"
                if self.stat == DEF:
                    boost_str = "Def"
                if self.stat == RES:
                    boost_str = "Res"
            elif self.boostType == 2:
                if self.stat == ATK:
                    boost_str = "A/Slot"
                if self.stat == SPD:
                    boost_str = "S/Slot"
                if self.stat == DEF:
                    boost_str = "D/Slot"
                if self.stat == RES:
                    boost_str = "R/Slot"
            elif self.boostType == 3:
                if self.stat == ATK:
                    boost_str = "A/Reinf."
                if self.stat == SPD:
                    boost_str = "S/Reinf."
                if self.stat == DEF:
                    boost_str = "D/Reinf."
                if self.stat == RES:
                    boost_str = "R/Reinf."

        return elem_str + type_str + boost_str

blessing_dict = {
    "Fjorm":          (WATER, 1, SPD),
    "Gunnthrá":       (WIND,  1, RES),
    "L!Ike":          (EARTH, 1, ATK),
    "L!Ephraim":      (FIRE,  1, DEF),
    "F!Grima":        (EARTH, 1, SPD),
    "L!Lyn":          (WIND,  1, ATK),
    "L!Ryoma":        (WATER, 1, DEF),
    "L!Hector":       (FIRE,  1, ATK),
    "L!Lucina":       (WIND,  1, SPD),
    "L!Marth":        (FIRE,  1, RES),
    "L!Y!Tiki":       (EARTH, 1, DEF),
    "L!Eirika":       (WATER, 1, ATK),
    "Hríd":           (WIND,  1, DEF),
    "L!Azura":        (WATER, 1, RES),
    "L!Roy":          (FIRE,  2, 0),
    "L!Alm":          (EARTH, 2, 0),
    "L!Eliwood":      (WIND,  2, 0),
    "L!Julia":        (EARTH, 2, 0),
    "L!Leif":         (WATER, 2, 0),
    "L!Celica":       (FIRE,  2, 0),
    "L!Chrom":        (WATER, 2, 0),
    "L!Edelgard":     (FIRE,  2, 0),
    "L!Seliph":       (EARTH, 2, 0),
    "L!F!Corrin":     (WIND,  2, 0),
    "L!Dimitri":      (WATER, 2, 0),
    "L!Lilina":       (FIRE,  2, 0),
    "L!Claude":       (EARTH, 2, 0),
    "L!Sigurd":       (WIND,  2, 0),
    "L!M!Byleth":     (WATER, 2, 0),
    "L!Micaiah":      (WIND,  2, 0),
    "L!Fae":          (EARTH, 2, 0),
    "Eitri":          (FIRE,  2, 0),
    "L!F!Byleth":     (WIND,  2, 0),
    "L!Caeda":        (WATER, 3, SPD),
    "L!Nanna":        (EARTH, 3, RES),
    "L!Myrrh":        (WIND,  3, DEF),
    "L!Xander":       (FIRE,  3, ATK),
    "L!Deirdre":      (EARTH, 3, ATK),
    "L!Ninian":       (WATER, 3, RES),
    "L!Veronica":     (WIND,  3, SPD),
    "L!F!Shez":       (FIRE,  3, SPD),
    "L!M!Robin":      (EARTH, 3, DEF),
    "L!Yuri":         (WIND,  3, ATK),
    "L!Hinoka":       (FIRE,  3, RES),
    "L!Guinivere":    (WATER, 3, DEF),
    "L!F!Alear":      (FIRE,  3, DEF),
    "L!Elincia":      (WIND,  3, RES),
    "L!Camilla":      (WATER, 3, ATK),
    "L!M!Alear":      (EARTH, 3, SPD),
    "L!M!Corrin":     (FIRE,  3, SPD),
    "L!M!Shez":       (WIND,  3, DEF),
    "L!Ayra":         (WATER, 3, SPD),
    "L!Sakura":       (EARTH, 3, RES),
    "L!Black Knight": (FIRE,  3, ATK),

    "Eir":            (LIGHT, 1, RES),
    "Duma":           (ANIMA, 1, ATK),
    "Yune":           (DARK,  1, SPD),
    "Naga":           (ASTRA, 1, DEF),
    "Sothis":         (DARK,  1, RES),
    "Thrasir":        (ANIMA, 1, DEF),
    "Altina":         (ASTRA, 1, ATK),
    "Peony":          (LIGHT, 1, SPD),
    "Líf":            (ANIMA, 1, SPD),
    "Bramimond":      (DARK,  1, ATK),
    "Mila":           (LIGHT, 1, DEF),
    "Mirabilis":      (ANIMA, 1, RES),
    "Hel":            (DARK,  1, DEF),
    "Plumeria":       (ASTRA, 1, SPD),
    "Triandra":       (DARK,  1, SPD),
    "Freyja":         (LIGHT, 1, ATK),
    "Reginn":         (ASTRA, 2, ATK),
    "Seiros":         (ANIMA, 2, ATK),
    "Dagr":           (LIGHT, 2, RES),
    "Nótt":           (DARK,  2, DEF),
    "Ashera":         (ASTRA, 2, RES),
    "Ullr":           (LIGHT, 2, SPD),
    "Ótr":            (ANIMA, 2, DEF),
    "Thórr":          (ASTRA, 2, DEF),
    "Elimine":        (ASTRA, 2, SPD),
    "Medeus":         (DARK,  2, ATK),
    "Askr":           (LIGHT, 2, DEF),
    "Arval":          (ANIMA, 2, RES),
    "Embla":          (DARK,  2, RES),
    "Seiðr":          (ASTRA, 2, ATK),
    "Fomortiis":      (ANIMA, 2, SPD),
    "Gotoh":          (LIGHT, 2, RES),
    "Nerþuz":         (LIGHT, 2, SPD),
    "Heiðr":          (ASTRA, 2, RES),
    "Freyr":          (ANIMA, 2, ATK),
    "Veyle":          (ASTRA, 2, DEF),
    "Kvasir":         (DARK,  2, SPD),
    "Gullveig":       (ANIMA, 2, SPD),
    "Ratatoskr":      (ASTRA, 2, SPD),
    "MY!Lumera":      (LIGHT, 2, DEF),
    "Loki":           (DARK,  2, ATK),
    "Heiðrún":        (ANIMA, 2, RES),
    "Eikþyrnir":      (ASTRA, 2, DEF),
    "Hræsvelgr":      (LIGHT, 2, ATK),
    "Níðhöggr":       (ASTRA, 2, RES),
    "Læraðr":         (DARK,  2, DEF),
    "Rune":           (LIGHT, 3, SPD),
    "Athos":          (ANIMA, 3, DEF),
    "Elm":            (ASTRA, 3, SPD)
}

def create_specialized_blessing(int_name):
    if int_name not in blessing_dict:
        return None
    else:
        return Blessing(blessing_dict[int_name])

class DuoSkill:
    def __init__(self, name, desc, skill_type, skill_refresh, effects):
        self.user_name = name
        self.desc = desc
        self.type = skill_type
        self.skill_refresh = skill_refresh
        self.effects = effects

# STATUS EFFECTS

# positive status effects are removed upon the start of the next controllable phase
# negative status effects are removed upon the unit finishing that turn's action

# 🔴 - combat
# 🔵 - movement
# 🟢 - other

# Use this down the line
# Enum(name, {member: i for i, member in enumerate(members, start=start)})

class Status(Enum):
    # negative, sorted
    Panic = 1  # 🔴 Buffs are negated & treated as penalties
    Exposure = 2  # 🔴 Foe's attacks deal +10 true damage
    Sabotage = 3  # 🔴 Reduces atk/spd/def/res by lowest debuff among unit & allies within 2 spaces during combat
    Discord = 4  # 🔴 Reduces atk/spd/def/res by 2 + number of allies within 2 spaces of unit, max 3 during combat
    HushSpectrum = 5 # 🔴 Atk/Spd/Def/Res-5 and sp halt +1 on self before unit's first attack
    ShareSpoils = 6 # 🔴 Atk/Spd/Def/Res-5, nullify percentage damage reduction of self, and grants another action to foe if this unit is defeated
    ShareSpoilsPlus = 6.5 # 🔴 Atk/Spd/Def/Res-5, nullify percentage damage reduction of self, and grants another action to foe if this unit is defeated (once per turn)
    FalseStart = 7  # 🟢 Disables "at start of turn" skills, does not neutralize beast transformations or reusable duo/harmonized skills, cancelled by Odd/Even Recovery Skills
    Flash = 8  # 🔴 Unable to counterattack
    Isolation = 9  # 🟢 Cannot use or receive assist skills
    DeepWounds = 10  # 🟢 Cannot recover HP
    NullMiracle = 11  # 🔴 Disables skills which allow unit to survive with 1HP (besides special Miracle)
    Undefended = 12  # 🔴 Cannot be protected by savior
    Feud = 13  # 🔴 Disables all allies' skills (excluding self) in combat, does not include savior, but you get undefended if you get this because Embla
    Ploy = 14 # 🔴 Nullifies Bonus Doubler, Treachery, and Grand Strategy on unit
    Schism = 15 # 🔴 Nullifies DualStrike, TriangleAttack, and Pathfinder, unit does not count towards allies w/ TriangleAttack or DualStrike. If neutralized, those bonuses are neutralized as well
    TimesGrip = 16  # 🔴 Inflicts Atk/Spd/Def/Res-4 during next combat, neutralizes skills during allies' combats
    Gravity = 17  # 🔵 Movement reduced to 1
    Stall = 18  # 🔵 Converts MobilityUp to Gravity
    CantoControl = 19  # 🔵 If range = 1 Canto skill becomes Canto 1, if range = 2, turn ends when canto triggers
    Guard = 20  # 🔴 Special charge -1
    Frozen = 21  # 🔴 Increases/decreases speed difference needed to make follow up for unit/foe by max(2 * Δdef + 10, 10)
    TriangleAdept = 22  # 🔴 Triangle Adept 3, weapon tri adv/disadv affected by 20%
    CancelAction = 23  # 🟢 After start of turn skills trigger, unit's action ends immediately (cancels active units in Summoner Duels)

    # positive, sorted
    ResonanceBlades = 100  # 🔴 Grants Atk/Spd+4 during combat
    ResonanceShields = 101  # 🔴 Grants Def/Res+4 during combat and foe cannot make a follow-up attack in unit's first combat
    RallySpectrum = 102  # 🔴 Grants Atk/Spd/Def/Res+5 and grants special -X before unit's first hit (X = 1 if unit has brave or slaying, 2 otherwise)
    Incited = 103  # 🔴 If initiating combat, grants Atk/Spd/Def/Res = num spaces moved, max 3
    BonusDoubler = 104  # 🔴 Gain atk/spd/def/res boost by current bonus on stat, canceled by Panic
    FoePenaltyDoubler = 105  # 🔴 Inflicts atk/spd/def/res -X on foe equal to current penalty on each stat
    GrandStrategy = 106  # 🔴 If negative penalty is present on self, grants atk/spd/def/res during combat equal to penalty * 2 for each stat
    FutureWitness = 107  # 🔴 Canto 2, Atk/Spd/Def/Res+5, reduce first attacks by 7, and sp halt +1 on foe before foe's first attack
    Dosage = 108  # 🔴 Atk/Spd/Def/Res+5, 10HP healed after combat, disables effects that steal bonuses, and clears all bonuses from foes that attempt to steal bonuses
    Empathy = 109  # 🔴 Grants Atk/Spd/Def/Res = num unique Bonus effects and Penalty effects currently on map (max 7)
    DivinelyInspiring = 110  # 🔴 Grants Atk/Spd/Def/Res = X * 3, grants -X sp jump to self before foe's first attack, and heals X * 4 HP per hit (X = num allies with this status in 3 spaces, max 2)
    Salvage = 111  # 🔵 Can move 2 spaces after combat with Canto. If Canto Control applied, base Canto movement is instead set to 2 for Melee units, 1 for Ranged units.
    Anathema = 112  # 🔴 Inflicts Spd/Def/Res-4 on foes within 3 spaces
    DraconicHex = 113 # 🔴 Inflicts Atk/Spd/Def/Res-5 on foe, and an additional Atk/Spd/Def/Res-5 minus current debuff of each stat.
    FireEmblem = 113.25  # 🔴 Nulls "Eff against move types", grants Atk/Spd/Def/Res = highest bonus on foes within 2 spaces, and reduces damage from first strikes by 10.
    FellSpirit = 113.5 # 🔴 Inflicts Atk/Spd/Def/Res-4 on foe, disables cannot counter skills, any special DR can be triggered twice, and if any unit in combat is engaged, inflicts additional Atk/Spd/Def/Res-2 on foe
    Treachery = 114  # 🔴 Deal true damage = number of stat bonuses on unit (not including Panic + Bonus)
    Dominance = 115  # 🔴 Deal true damage = number of stat penalties on foe (including Panic-reversed Bonus)
    AOEReduce80Percent = 116  # 🔴 Reduces non-Røkkr AoE damage taken by 80%
    Dodge = 117  # 🔴 If unit's spd > foe's spd, reduces combat & non-Røkkr AoE damage by X%, X = (unit's spd - foe's spd) * 4, max of 40%
    FirstReduce40 = 118  # 🔴 If initiating combat, reduces damage from first attack received by 40%
    FallenStar = 119  # 🔴 Reduces damage from foe's first attack by 80% in unit's first combat in player phase and first combat in enemy phase
    DeepStar = 120  # 🔴 In unit's first combat where foe initiates combat, reduces first hit(s) by 80%
    Reflex = 120.5 # 🔴 Reduces damage from first strikes by 7, deals damage on next hit by damage reduced on first hit
    NullBonuses = 121  # 🔴 Neutralizes foe's bonuses in combat
    NullPenalties = 122  # 🔴 Neutralizes unit's penalties in combat
    EnGarde = 123  # 🔴 Neutralizes damage outside of combat, minus AoE damage
    NullPanic = 124  # 🔴 Nullifies Panic
    NullFollowUp = 125  # 🔴 Disables skills that guarantee foe's follow-ups or prevent unit's follow-ups
    DamageReductionPierce50 = 126  # 🔴 Cuts foe's non-special damage reduction skill efficacy in half
    WarpBubble = 127  # 🔵 Foes cannot warp onto spaces within 4 spaces of unit (does not affect pass skills)
    DivineNectar = 128  # 🔴 Neutralizes Deep Wounds, restores 20HP as combat begins, and reduces damage by 10
    Imbue = 128.5 # 🔴 Restores HP = 40% of max HP as combat begins, and reduces Deep Wounds by 50%
    EffDragons = 129  # 🔴 Gain effectiveness against dragons
    NullEffDragons = 130  # 🔴 Gain immunity to "eff against dragons"
    NullEffArmors = 131  # 🔴 Gain immunity to "eff against armors"
    NullEffFliers = 132  # 🔴 Gain immunity to "eff against flyers"
    MobilityUp = 133  # 🔵 Movement increased by 1, cancelled by Gravity
    Gallop = 134  # 🔵 Movement increased by 2, cancelled by Gravity, does not stack with MobilityUp
    Charge = 135  # 🔵 Unit can move to any space up to 3 spaces away in cardinal direction, terrain/skills that halt (not slow) movement still apply, treated as warp movement
    Pathfinder = 136  # 🔵 Unit's space costs 0 to move to by allies
    Canto1 = 137  # 🔵 Can move 1 space after combat with Canto
    TraverseTerrain = 138  # 🔵 Ignores terrain which slows unit (bushes/trenches)
    Orders = 139  # 🔵 Unit can move to space adjacent to ally within 2 spaces
    TimesGate = 140  # 🔵 Allies within 4 spaces can warp to a space adjacent to unit
    Hexblade = 141  # 🔴 Damage inflicted using lower of foe's def or res (applies to AoE skills)
    SpecialCharge = 142  # 🔴 Special charge +1 per hit during combat
    PreemptPulse = 143  # 🔴 Grants -1 sp jump before unit's first attack
    Pursual = 144  # 🔴 Unit makes follow-up attack when initiating combat
    MakeFollowUp = 144.5 # 🔴 Unit makes follow-up attack
    DenyFollowUp = 145  # 🔴 Foe cannot make a follow-up attack
    Outspeeding = 146  # Increases Spd difference needed for foe to make follow-up by 10
    PotentFollow = 147 # 🔴 If being outsped by 20 or less, grants 80/40 Potent hit
    Desperation = 148  # 🔴 If unit initiates combat and can make follow-up attack, makes follow-up attack before foe can counter
    Vantage = 149  # 🔴 Unit counterattacks before foe's first attack in enemy phase
    Paranoia = 150  # 🔴 If unit's HP >= 99%, grants Atk+5, Desperation, and if either # foe negative statuses >= 3 or foe is of same range, grants Vantage
    Bulwark = 151  # 🔵 Foes cannot move through spaces within X spaces of unit, X = foe's range
    AssignDecoy = 152  # 🔴 Unit is granted Savior effect for their range, fails if unit currently has savior skill
    CancelAffinity = 153  # 🔴 Cancel Affinity 3, reverses weapon triangle to neutral if Triangle Adept-having unit/foe has advantage
    TriangleAttack = 154  # 🔴 If within 2 spaces of 2 allies with TriAttack and initiating combat, unit attacks twice
    DualStrike = 155  # 🔴 If unit initiates combat and is adjacent to unit with DualStrike, unit attacks twice
    EssenceDrain = 156 # 🔴 If unit attacks, steals positive bonuses from foes within 2 spaces of target and gives to self and all allies with this status. If foe defeated, heals 10HP to self and allies with this status.
    Bonded = 157 # 🔴 Activates different effects depending on skills present in battle
    ForesightSnare = 158 # 🟢 If unit initiated with this status is the first combat of the phase, cancel that combat and remove this status from all of team.

class GameMode(Enum):
    # PVE
    Story = 0
    HeroBattle = 1

    # PVP
    Arena = 2
    AetherRaids = 3
    Allegiance = 4

    # Special
    Special = 5

    # Event
    Rokkr = 11
    Mjolnir = 12
    Resonant = 13

    # Large Map
    RivalDomains = 100
    RelayDefense = 101
    SummonerDuels = 102


print("Reading Unit & Skill Data...")
hero_sheet = pd.read_excel('Spreadsheets/FEHstats.xlsx')
weapon_sheet = pd.read_excel('Spreadsheets/FEHWeapons.xlsx')
assist_sheet = pd.read_excel('Spreadsheets/FEHAssists.xlsx')
special_sheet = pd.read_excel('Spreadsheets/FEHSpecials.xlsx')
skills_sheet = pd.read_excel('Spreadsheets/FEHABCXSkills.xlsx')
seals_sheet = pd.read_excel("Spreadsheets/FEHSeals.xlsx")
with open('Spreadsheets/FEHDuoSkills.json', encoding="utf-8") as read_file: duoskills_sheet = json.load(read_file)

# Skills currently present for use
# Yeah this was not properly thought out
#impl_skills_sheet = pd.read_csv("Spreadsheets/FEHImplABCXSkills.csv")

print("Unit & Skill Data Loaded.")

# Support partners
# If intName in the supports.pkl array, returns their support partner
def get_ally_support(int_name):
    loaded_file = open('supports.pkl', 'rb')
    supports = pickle.load(loaded_file)

    for pairing in supports:
        if int_name in pairing:
            return pairing[pairing.index(int_name) - 1]

    return None

def makeHero(name):
    row = hero_sheet.loc[hero_sheet['IntName'] == name]
    n = row.index.values[0]

    name = row.loc[n, 'Name']
    int_name = row.loc[n, 'IntName']
    epithet = row.loc[n, 'Epithet']
    game = row.loc[n, 'Game']
    secondary_game = row.loc[n, 'Secondary Game']
    wpnType = row.loc[n, 'Weapon Type']
    moveType = row.loc[n, 'Movement']
    u_hp = row.loc[n, 'HP']
    u_atk = row.loc[n, 'Atk']
    u_spd = row.loc[n, 'Spd']
    u_def = row.loc[n, 'Def']
    u_res = row.loc[n, 'Res']
    g_hp = row.loc[n, 'HP Grow']
    g_atk = row.loc[n, 'Atk Grow']
    g_spd = row.loc[n, 'Spd Grow']
    g_def = row.loc[n, 'Def Grow']
    g_res = row.loc[n, 'Res Grow']
    dfl = row.loc[n, 'DFlowerLimit']
    bvid = row.loc[n, 'BVID']
    refreshType = row.loc[n, 'RefreshType']

    result_hero = Hero(name, int_name, epithet, game, secondary_game, wpnType, moveType, [u_hp, u_atk, u_spd, u_def, u_res], [g_hp, g_atk, g_spd, g_def, g_res], dfl, bvid, refreshType)

    # Set ally support from supports.pkl
    result_hero.allySupport = get_ally_support(int_name)

    # Assign specialized blessing type if unit is Legendary/Mythic
    result_hero.blessing = create_specialized_blessing(int_name)

    result_hero.duo_skill = makeDuoSkill(int_name)

    return result_hero

def get_generic_weapon(name):
    if "Sword" in name: return "Sword"
    if "Lance" in name: return "Lance"
    if "Axe" in name: return "Axe"

    if "Red" in name: return "RTome"
    if "Blue" in name: return "BTome"
    if "Green" in name: return "GTome"

    if "Bow" in name: return "CBow"
    if name == "Thief": return "CDagger"

    return "Staff"

def get_generic_move(name):
    if "Fighter" in name: return 0
    if "Cavalier" in name or name == "Troubadour": return 1
    if "Flier" in name: return 2
    if "Knight" in name: return 3

    return 0

def makeGeneric(name):
    result_hero = Hero(name, name, "Generic", 0, 0, get_generic_weapon(name), get_generic_move(name), [20, 20, 20, 20, 20], [40, 40, 40, 40, 40], 0, 0, 0)
    return result_hero

def makeWeapon(name):
    # ﻿
    # I found this cool thing in the spreadsheet what is this

    row = weapon_sheet.loc[weapon_sheet['IntName'] == name]

    n = row.index.values[0]

    name = row.loc[n, 'Name']
    int_name = row.loc[n, 'IntName']
    desc = row.loc[n, 'Description']
    might = row.loc[n, 'Might']
    wpnType = row.loc[n, 'Type']
    rng = row.loc[n, 'Range']
    effects = {}
    users = []

    if not pd.isna(row.loc[n, 'Effect1']) and not pd.isna(row.loc[n, 'Level1']): effects.update({row.loc[n, 'Effect1']: int(row.loc[n, 'Level1'])})
    if not pd.isna(row.loc[n, 'Effect2']) and not pd.isna(row.loc[n, 'Level2']): effects.update({row.loc[n, 'Effect2']: int(row.loc[n, 'Level2'])})
    if not pd.isna(row.loc[n, 'Effect3']) and not pd.isna(row.loc[n, 'Level3']): effects.update({row.loc[n, 'Effect3']: int(row.loc[n, 'Level3'])})
    if not pd.isna(row.loc[n, 'Effect4']) and not pd.isna(row.loc[n, 'Level4']): effects.update({row.loc[n, 'Effect4']: int(row.loc[n, 'Level4'])})
    if not pd.isna(row.loc[n, 'Effect5']) and not pd.isna(row.loc[n, 'Level5']): effects.update({row.loc[n, 'Effect5']: int(row.loc[n, 'Level5'])})

    if not pd.isna(row.loc[n, 'ExclusiveUser1']): users.append(row.loc[n, 'ExclusiveUser1'])
    if not pd.isna(row.loc[n, 'ExclusiveUser2']): users.append(row.loc[n, 'ExclusiveUser2'])
    if not pd.isna(row.loc[n, 'ExclusiveUser3']): users.append(row.loc[n, 'ExclusiveUser3'])
    if not pd.isna(row.loc[n, 'ExclusiveUser4']): users.append(row.loc[n, 'ExclusiveUser4'])

    return Weapon(name, int_name, desc, might, rng, wpnType, effects, users)

def makeAssist(name):
    row = assist_sheet.loc[assist_sheet['Name'] == name]
    n = row.index.values[0]

    name = row.loc[n, 'Name']
    desc = row.loc[n, 'Description']
    rng = row.loc[n, 'Range']
    type = row.loc[n, 'Type']

    effects = {}
    users = []

    if not pd.isna(row.loc[n, 'Effect1']) and not pd.isna(row.loc[n, 'Level1']): effects.update({row.loc[n, 'Effect1']: int(row.loc[n, 'Level1'])})
    if not pd.isna(row.loc[n, 'Effect2']) and not pd.isna(row.loc[n, 'Level2']): effects.update({row.loc[n, 'Effect2']: int(row.loc[n, 'Level2'])})

    if not pd.isna(row.loc[n, 'ExclusiveUser1']): users.append(row.loc[n, 'ExclusiveUser1'])
    if not pd.isna(row.loc[n, 'ExclusiveUser2']): users.append(row.loc[n, 'ExclusiveUser2'])
    if not pd.isna(row.loc[n, 'ExclusiveUser3']): users.append(row.loc[n, 'ExclusiveUser3'])

    return Assist(name, desc, effects, rng, type, users)

def makeSpecial(name):
    row = special_sheet.loc[special_sheet['Name'] == name]
    n = row.index.values[0]

    name = row.loc[n, 'Name']
    desc = row.loc[n, 'Description']
    cooldown = row.loc[n, 'Cooldown']
    spType = row.loc[n, 'Type']
    effects = {}
    users = []

    if not pd.isna(row.loc[n, 'Effect1']) and not pd.isna(row.loc[n, 'Level1']): effects.update({row.loc[n, 'Effect1']: int(row.loc[n, 'Level1'])})
    if not pd.isna(row.loc[n, 'Effect2']) and not pd.isna(row.loc[n, 'Level2']): effects.update({row.loc[n, 'Effect2']: int(row.loc[n, 'Level2'])})
    if not pd.isna(row.loc[n, 'Effect3']) and not pd.isna(row.loc[n, 'Level3']): effects.update({row.loc[n, 'Effect3']: int(row.loc[n, 'Level3'])})
    if not pd.isna(row.loc[n, 'Effect4']) and not pd.isna(row.loc[n, 'Level4']): effects.update({row.loc[n, 'Effect4']: int(row.loc[n, 'Level4'])})

    if not pd.isna(row.loc[n, 'ExclusiveUser1']): users.append(row.loc[n, 'ExclusiveUser1'])
    if not pd.isna(row.loc[n, 'ExclusiveUser2']): users.append(row.loc[n, 'ExclusiveUser2'])
    if not pd.isna(row.loc[n, 'ExclusiveUser3']): users.append(row.loc[n, 'ExclusiveUser3'])

    return Special(name, desc, effects, cooldown, spType)

def makeSkill(name):
    row = skills_sheet.loc[skills_sheet['Name'] == name]
    n = row.index.values[0]

    name = row.loc[n, 'Name']
    desc = row.loc[n, 'Description']
    letter = row.loc[n, 'Letter']
    tier = row.loc[n, 'Tier']
    effects = {}
    users = []

    if not pd.isna(row.loc[n, 'Effect1']) and not pd.isna(row.loc[n, 'Level1']): effects.update({row.loc[n, 'Effect1']: int(row.loc[n, 'Level1'])})
    if not pd.isna(row.loc[n, 'Effect2']) and not pd.isna(row.loc[n, 'Level2']): effects.update({row.loc[n, 'Effect2']: int(row.loc[n, 'Level2'])})
    if not pd.isna(row.loc[n, 'Effect3']) and not pd.isna(row.loc[n, 'Level3']): effects.update({row.loc[n, 'Effect3']: int(row.loc[n, 'Level3'])})
    if not pd.isna(row.loc[n, 'Effect4']) and not pd.isna(row.loc[n, 'Level4']): effects.update({row.loc[n, 'Effect4']: int(row.loc[n, 'Level4'])})
    if not pd.isna(row.loc[n, 'Effect5']) and not pd.isna(row.loc[n, 'Level5']): effects.update({row.loc[n, 'Effect5']: int(row.loc[n, 'Level5'])})

    if not pd.isna(row.loc[n, 'ExclusiveUser1']): users.append(row.loc[n, 'ExclusiveUser1'])
    if not pd.isna(row.loc[n, 'ExclusiveUser2']): users.append(row.loc[n, 'ExclusiveUser2'])
    if not pd.isna(row.loc[n, 'ExclusiveUser3']): users.append(row.loc[n, 'ExclusiveUser3'])

    return Skill(name, desc, letter, tier, effects, users)

def makeSeal(name):
    row = seals_sheet.loc[seals_sheet['Name'] == name]
    n = row.index.values[0]

    name = row.loc[n, 'Name']
    desc = row.loc[n, 'Description']
    letter = row.loc[n, 'Letter']
    tier = row.loc[n, 'Tier']
    effects = {}
    users = []

    if not pd.isna(row.loc[n, 'Effect1']) and not pd.isna(row.loc[n, 'Level1']): effects.update({row.loc[n, 'Effect1']: int(row.loc[n, 'Level1'])})
    if not pd.isna(row.loc[n, 'Effect2']) and not pd.isna(row.loc[n, 'Level2']): effects.update({row.loc[n, 'Effect2']: int(row.loc[n, 'Level2'])})
    if not pd.isna(row.loc[n, 'Effect3']) and not pd.isna(row.loc[n, 'Level3']): effects.update({row.loc[n, 'Effect3']: int(row.loc[n, 'Level3'])})
    if not pd.isna(row.loc[n, 'Effect4']) and not pd.isna(row.loc[n, 'Level4']): effects.update({row.loc[n, 'Effect4']: int(row.loc[n, 'Level4'])})
    if not pd.isna(row.loc[n, 'Effect5']) and not pd.isna(row.loc[n, 'Level5']): effects.update({row.loc[n, 'Effect5']: int(row.loc[n, 'Level5'])})

    return Skill(name, desc, letter, tier, effects, users)

def makeDuoSkill(name):
    if name not in duoskills_sheet:
        return None

    desc = duoskills_sheet[name]['desc']
    skill_type = duoskills_sheet[name]['type']
    skill_refresh = duoskills_sheet[name]['skill_refresh']
    effects = duoskills_sheet[name]['skills']

    return DuoSkill(name, desc, skill_type, skill_refresh, effects)

#veyle = makeHero("Veyle")
#obscurité = Weapon("Obscurité", "idk", 14, 2, {"stuff":10})

#print(veyle.stats)

#veyle.set_IVs(ATK, DEF, SPD)

#print(veyle.level)
#print(veyle.visible_stats)

#veyle.set_merges(10)
#veyle.set_dragonflowers(5)
#veyle.set_level(40)

#print(veyle.visible_stats)

# reset visible stats after each step of the process

#veyle.set_skill(obscurité, 0)

#print(veyle.visible_stats)

#a = makeHero("Dimitri")

aided_heroes = ["AI!Reginn", "AI!Dagr", "Yunaka"]

# Generics
generics = ["Sword Fighter", "Lance Fighter", "Axe Fighter",
            "Sword Cavalier", "Lance Cavalier", "Axe Cavalier",
            "Sword Flier", "Lance Flier", "Axe Flier",
            "Sword Knight", "Lance Knight", "Axe Knight",
            "Red Mage", "Blue Mage", "Green Mage",
            "Red Cavalier", "Blue Cavalier", "Green Cavalier",
            "Bow Fighter", "Bow Cavalier", "Thief", "Troubadour", "Cleric"
            ]

emblem_descriptions = {
    "Marth": "Accelerates Special trigger (cooldown count-1; max cooldown count cannot be reduced below 1). If unit triggers the \"unit attacks twice\" effect, reduces Special damage by 8.",
    "Ike": "If foe's Range = 2 and unit's or foe's Special is ready or triggered before or during this combat, reduces damage from foe's next attack by 40% (once per combat; excluding area-of-effect Specials).",
    "Celica": '''Boosts Special damage by unit's max Special cooldown count value × 4 (excluding area-of-effect Specials).

For each foe within 5 spaces of unit, unit can move to the nearest spaces that are within unit's range from that foe (unless space is impassable terrain).''',
    "Sigurd": '''Boosts Special damage by number of spaces from start position to end position of whoever initiated combat (max 4) × 2.

Enables [Canto (X)].
If unit's Range = 1, X = 3; otherwise, X = 2.

At start of turn, grants "unit can move 1 extra space" to unit for 1 turn (does not stack; excludes cavalry with Range = 2).''',
    "Lyn": '''When Special triggers, boosts damage by unit's max Special cooldown count value × 4 (excluding area-of-effect Specials).

Unit can use the following [Style]:
――――― Emblem Lyn Style ―――――
Unit can attack foes within 5 spaces of unit and 3 rows or 3 columns centered on unit regardless of unit's range. Unit suffers a counterattack if any of the following conditions are met: foe is armored with Range = 2, foe can counterattack regardless of unit's range, foe's Range is the same as the distance between unit and the foe.

Unit cannot move or attack structures, after-combat movement effects do not occur, unit's area-of-effect Specials cannot be triggered, and remaining movement granted from Canto is treated as 0. Skill effect's Range is treated as 2, including by skill effects determined by attack Range, like Pavise and Aegis. This Style can be used only when unit's Range = 2, cannot be used on the first turn, and once used, cannot be used for two turns.
――――――――――――――――――――''',
    "Eirika": '''When Special triggers, boosts damage by unit's max Special cooldown count value × 4 (excluding area-of-effect Specials).

If it is unit's first combat initiated by unit or first combat initiated by foe that turn, inflicts Atk-4 on unit and unit attacks twice during combat (triggers only when unit's Range = 1; does not trigger when equipped with an area-of-effect Special).''',
    "Micaiah": '''When Special triggers, boosts damage by unit's max Special cooldown count value × 4 (excluding area-of-effect Specials).

If a Rally of movement Assist skill is used by unit, restores 20 HP to target ally and neutralizes any [Penalty] on that ally, and grants another action to unit and inflicts [Isolation] on unit and Pair Up cohort through their next action, and also, if unit's or Pair Up Cohort's Range = 2, inflicts "restricts movement to 1 space" on unit and Pair Up cohort, respectively, through their next action ("grants another action" effect and onward is once per turn; if another effect that grants additional action to unit has been triggered at the same time, this effect is also considered to have been triggered).'''

}