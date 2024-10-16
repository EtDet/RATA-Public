from math import trunc, isnan
from itertools import islice
from enum import Enum

import pandas as pd

# CONSTANTS
HP = 0
ATK = 1
SPD = 2
DEF = 3
RES = 4

WEAPON = 0
ASSIST = 1
SPECIAL = 2
ASKILL = 3
BSKILL = 4
CSKILL = 5
SSEAL = 6
XSKILL = 7

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
    def __init__(self, name, intName, epithet, game, wpnType, move, stats, growths, flower_limit, BVID, refresh_type):
        # Unit's name (Julia, Corrin, Ratatoskr, etc.)
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
        self.game: int = game

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
        self.map_stat_mods: list[int] = [0] * 5

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

        # specific unit skills
        self.weapon: Weapon = None
        self.assist: Assist = None
        self.special: Special = None
        self.askill: Skill = None
        self.bskill: Skill = None
        self.cskill: Skill = None
        self.sSeal: Skill = None
        self.xskill: Skill = None

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

        self.allySupport = None
        self.summonerSupport = None

        self.blessing = None

        self.pair_skill = None

        self.resp = False
        self.has_resp = False

        # --- The following variables are used for simulation ---

        # If unit can currently act this turn
        self.unit_can_act = True

        # Number of times this unit has entered combat in this phase
        self.unitCombatInitiates = 0

        # Number of times this unit has been targeted for assist skill usage
        self.assistTargetedSelf = 0

        # Number of times this unit has used their assist skill
        self.assistTargetedOther = 0

        # If Canto can be utilized after unit's next action (attacking, breaking, or assisting, etc.)
        self.canto_ready = False

        self.special_galeforce_triggered = False
        self.nonspecial_galeforce_triggered = False

        self.beast_trans_condition = False

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
        for i in range(0, 2 - trunc(0.5 * self.rarity)):
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

            with open("growth_vectors.bin") as file:
                my_slice = list(islice(file, required_vector % 2496, required_vector + 1))

            vector = (''.join(my_slice))[0:40]

            j = 0
            while j < level:
                self.stats[i] += int(vector[j%40]) + required_vector // 2496
                j += 1

        self.level = level
        self.set_visible_stats()

    def set_IVs(self, new_asset, new_flaw, new_asc_asset):

        self.asset = new_asset
        self.flaw = new_flaw
        self.asc_asset = new_asc_asset

        #print("END", new_asset, new_flaw, new_asc_asset)

        self.set_level(self.level)

    def set_emblem(self, emblem, emblem_merges):
        if self.intName[:2] == "E!": return # temporary disabling of engaging emblems with each other

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
        if skill == None:
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

        if "spectrumBoost" in skill.effects:
            self.skill_stat_mods[ATK] += skill.effects["spectrumBoost"]
            self.skill_stat_mods[SPD] += skill.effects["spectrumBoost"]
            self.skill_stat_mods[DEF] += skill.effects["spectrumBoost"]
            self.skill_stat_mods[RES] += skill.effects["spectrumBoost"]

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
                self.specialCount = max(self.specialCount - self.weapon.effects["slaying"], 1)
                self.specialMax = max(self.specialMax - self.weapon.effects["slaying"], 1)

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

        if "spectrumBoost" in skill.effects:
            self.skill_stat_mods[ATK] -= skill.effects["spectrumBoost"]
            self.skill_stat_mods[SPD] -= skill.effects["spectrumBoost"]
            self.skill_stat_mods[DEF] -= skill.effects["spectrumBoost"]
            self.skill_stat_mods[RES] -= skill.effects["spectrumBoost"]

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
            if self.emblem is not None and self.emblem == "Marth":
                self.specialCount = max(self.specialCount - self.weapon.effects["slaying"], 1)
                self.specialMax = max(self.specialMax - self.weapon.effects["slaying"], 1)

        # Reset stats
        self.set_visible_stats()


    def set_visible_stats(self):
        i = 0
        while i < 5:
            self.visible_stats[i] = self.stats[i] + self.skill_stat_mods[i]
            self.visible_stats[i] = max(min(self.visible_stats[i], 99), 0)
            i += 1

        self.HPcur = self.visible_stats[0]

    # Getting stat with applied buffs and debuffs
    def get_visible_stat(self, STAT):
        panic_factor = 1
        if Status.Panic in self.statusNeg: panic_factor = -1
        if Status.NullPanic in self.statusPos: panic_factor = 1
        buff_applied_stat = self.visible_stats[STAT] + self.buffs[STAT] * panic_factor + self.debuffs[STAT]
        return buff_applied_stat

    def inflictStatus(self, status):
        # Positive status
        if status.value > 100 and status not in self.statusPos:
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

        print(self.name + "'s " + statStr + " was modified by " + str(num) + ".")

    def chargeSpecial(self, charge):
        # Will only charge special if charge is >0, and if special is present (-1 represents no special equipped)
        if charge != 0 and self.specialCount != -1:
            # will decrease special count by charge
            self.specialCount = max(0, self.specialCount - charge)
            self.specialCount = min(self.specialCount, self.specialMax)

            print(self.name + "'s special was charged by " + str(charge) + ". Currently is: " + str(self.specialCount))

    def inflictDamage(self, damage):
        self.HPcur -= damage
        if self.HPcur < 1: self.HPcur = 1
        print(self.name + " takes " + str(damage) + " damage out of combat.")

    def hasBonus(self):
        return (sum(self.buffs) > 0 and Status.Panic not in self.statusNeg) or len(self.statusPos) > 0

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
        isDragon = self.wpnType == "RDragon" or self.wpnType == "BDragon" or self.wpnType == "GDragon" or self.wpnType == "CDragon"
        isBeast = self.wpnType == "RBeast" or self.wpnType == "BBeast" or self.wpnType == "GBeast" or self.wpnType == "CBeast"
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
        return self.visible_stats[:]

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

class Blessing():
    def __init__(self, element, boostType, stat):
        # 9 - none
        # 0 - fire, 1 - water, 2 - wind, 3 - earth
        # 4 - light, 5 - dark, 6 - astra, 7 - anima
        self.element = element

        # 9 - none
        # 0 - blessing, for non-legendary/mythic unit
        # 1 - legendary effect 1 - stat boost
        #     OR mythic effect 1 - AR boost + stat boost
        # 2 - legendary effect 2 - pair up
        # 3 - legendary effect 3 - stat boost + pair up
        self.boostType = boostType

        # 9 - none
        # 1 - atk, 2 - spd, 3 - def, 4 - res
        self.stat = stat

class DuoSkill:
    def __init__(self, effect):
        # 0 - 20 non-special AOE damage to enemies within 3 columns
        # 1 - Inf & Arm allies within 2 spaces and self gain MobilityUp
        # 2 - Grants Atk/Spd/Def/Res+3 and BonusDoubler to Arm and Fly allies within 3 rows
        # 3 - Special cooldown -2 to self and Inf allies within 3 rows and columns
        # 4 - Neutralizes stat penalties and negative penalties, restores 30HP, and grants to Atk/Spd+6 on self and allies within 5 rows and columns
        # 5 - Grants Def/Res+6 and grants NullEffDragons and NullEffArmors to self and allies within 5 rows and columns
        # 6 - Grants MobilityUp to self and adjacent Fly allies
        # 7 - Grants Dominance to self and allies within 3 columns and inflicts Def/Res-7 on foes within 3 columns
        # 8 - Grants Desperation to self and allies within 2 spaces (WAIT NO THERE'S MORE THAN ONE TYPE OF REUSABLE DUO SKILL COME BACK TO THIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIISSSS)
        # 9 - Moves adjacent allies to other side of unit, if space is available for targeted unit

        effect = effect
        oncePerMap = False if effect in [8, 9] else True

class HarmonicSkill(DuoSkill):
    def __init__(self, hEffect, secondGame, effect):
        super().__init__(effect)
        hEffect = hEffect
        secondGame = secondGame

# STATUS EFFECTS

# positive status effects are removed upon the start of the next controllable phase
# negative status effects are removed upon the unit finishing that turn's action

# 🔴 - combat
# 🔵 - movement
# 🟢 - other

class Status(Enum):
    # negative, sorted

    CantoControl = 0  # 🔵 If range = 1 Canto skill becomes Canto 1, if range = 2, turn ends when canto triggers
    Panic = 1  # 🔴 Buffs are negated & treated as penalties
    Exposure = 2  # 🔴 Foe's attacks deal +10 true damage
    Sabotage = 3  # 🔴 Reduces atk/spd/def/res by lowest debuff among unit & allies within 2 spaces during combat
    Discord = 4  # 🔴 Reduces atk/spd/def/res by 2 + number of allies within 2 spaces of unit, max 3 during combat
    HushSpectrum = 5
    ShareSpoils = 6
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
    Guard = 19  # 🔴 Special charge -1
    Frozen = 20  # 🔴 Increases/decreases speed difference needed to make follow up for unit/foe by max(2 * Δdef + 10, 10)
    TriAdept = 21  # 🔴 Triangle Adept 3, weapon tri adv/disadv affected by 20%
    CancelAction = 22  # 🟢 After start of turn skills trigger, unit's action ends immediately (cancels active units in Summoner Duels)

    # positive, unsorted
    MobilityUp = 103  # 🔵 Movement increased by 1, cancelled by Gravity
    Orders = 106  # 🔵 Unit can move to space adjacent to ally within 2 spaces
    EffDragons = 107  # 🔴 Gain effectiveness against dragons
    BonusDoubler = 109  # 🔴 Gain atk/spd/def/res boost by current bonus on stat, canceled by Panic
    NullEffDragons = 110  # 🔴 Gain immunity to "eff against dragons"
    NullEffArmors = 111  # 🔴 Gain immunity to "eff against armors"
    Dominance = 112  # 🔴 Deal true damage = number of stat penalties on foe (including Panic-reversed Bonus)
    ResonanceBlades = 113  # 🔴 Grants Atk/Spd+4 during combat
    Desperation = 114  # 🔴 If unit initiates combat and can make follow-up attack, makes follow-up attack before foe can counter
    ResonanceShields = 115  # 🔴 Grants Def/Res+4 during combat and foe cannot make a follow-up attack in unit's first combat
    Vantage = 116  # 🔴 Unit counterattacks before foe's first attack in enemy phase
    FallenStar = 118  # 🔴 Reduces damage from foe's first attack by 80% in unit's first combat in player phase and first combat in enemy phase
    DenyFollowUp = 119  # 🔴 Foe cannot make a follow-up attack
    NullEffFlyers = 120  # 🔴 Gain immunity to "eff against flyers"
    Dodge = 121  # 🔴 If unit's spd > foe's spd, reduces combat & non-Røkkr AoE damage by X%, X = (unit's spd - foe's spd) * 4, max of 40%
    MakeFollowUp = 122  # 🔴 Unit makes follow-up attack when initiating combat
    TriAttack = 123  # 🔴 If within 2 spaces of 2 allies with TriAttack and initiating combat, unit attacks twice
    NullPanic = 124  # 🔴 Nullifies Panic
    CancelAffinity = 125  # 🔴 Cancel Affinity 3, reverses weapon triangle to neutral if Triangle Adept-having unit/foe has advantage
    NullFollowUp = 127  # 🔴 Disables skills that guarantee foe's follow-ups or prevent unit's follow-ups
    Pathfinder = 128  # 🔵 Unit's space costs 0 to move to by allies
    NullBonuses = 130  # 🔴 Neutralizes foe's bonuses in combat
    GrandStrategy = 131  # 🔴 If negative penalty is present on self, grants atk/spd/def/res during combat equal to penalty * 2 for each stat
    EnGarde = 133  # 🔴 Neutralizes damage outside of combat, minus AoE damage
    SpecialCharge = 134  # 🔴 Special charge +1 per hit during combat
    Treachery = 135  # 🔴 Deal true damage = number of stat bonuses on unit (not including Panic + Bonus)
    WarpBubble = 136  # 🔵 Foes cannot warp onto spaces within 4 spaces of unit (does not affect pass skills)
    Charge = 137  # 🔵 Unit can move to any space up to 3 spaces away in cardinal direction, terrain/skills that halt (not slow) movement still apply, treated as warp movement
    Canto1 = 139  # 🔵 Can move 1 space after combat (not writing all the canto jargon here)
    FoePenaltyDoubler = 140  # 🔴 Inflicts atk/spd/def/res -X on foe equal to current penalty on each stat
    DualStrike = 143  # 🔴 If unit initiates combat and is adjacent to unit with DualStrike, unit attacks twice
    TraverseTerrain = 144  # 🔵 Ignores terrain which slows unit (bushes/trenches)
    ReduceAreaOfEffect = 145  # 🔴 Reduces non-Røkkr AoE damage taken by 80%
    NullPenalties = 146  # 🔴 Neutralizes unit's penalties in combat
    Hexblade = 147  # 🔴 Damage inflicted using lower of foe's def or res (applies to AoE skills)
    RallySpectrum = 150 # 🔴 Grants Atk/Spd/Def/Res+5 and grants special -X before unit's first hit (X = 1 if unit has brave or slaying, 2 otherwise)
    AssignDecoy = 151 # 🔴 Unit is granted Savior effect for their range, fails if unit currently has savior skill
    DeepStar = 152 # 🔴 In unit's first combat where foe initiates combat, reduces first hit(s) by 80%
    TimesGate = 156 # 🔵 Allies within 4 spaces can warp to a space adjacent to unit
    Incited = 157 # 🔴 If initiating combat, grants Atk/Spd/Def/Res = num spaces moved, max 3
    FirstReduce40 = 158 # 🔴 If initiating combat, reduces damage from first attack received by 40%
    HalfDamageReduction = 159 # 🔴 Cuts foe's damage reduction skill efficacy in half
    EssenceDrain = 163 # 🔴 If unit attacks, steals positive statuses from foes within 2 spaces of target and gives to all allies with this status. If foe defeated, restores 10HP to allies with this status.
    Bonded = 164 # 🔴 Activates different effects depending on skills present in battle
    Bulwark = 165 # 🔵 Foes cannot move through spaces within X spaces of unit, X = foe's range
    DivineNectar = 166 # 🔴 Neutralizes Deep Wounds, restores 20HP as combat begins, and reduces damage by 10
    Paranoia = 167 # 🔴 If unit's HP >= 99%, grants Atk+5, Desperation, and if either # foe negative statuses >= 3 or foe is of same range, grants Vantage


print("Reading Unit & Skill Data...")
hero_sheet = pd.read_csv('FEHstats.csv')
weapon_sheet = pd.read_csv('FEHWeapons.csv')
assist_sheet = pd.read_csv('FEHAssists.csv')
special_sheet = pd.read_csv('FEHSpecials.csv')
skills_sheet = pd.read_csv('FEHABCXSkills.csv')
seals_sheet = pd.read_csv("FEHSeals.csv")

# Skills currently present for use
impl_skills_sheet = pd.read_csv("FEHImplABCXSkills.csv")
print("Unit & Skill Data Loaded.")

def makeHero(name):
    row = hero_sheet.loc[hero_sheet['IntName'] == name]
    n = row.index.values[0]

    name = row.loc[n, 'Name']
    int_name = row.loc[n, 'IntName']
    epithet = row.loc[n, 'Epithet']
    game = row.loc[n, 'Game']
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

    return Hero(name, int_name, epithet, game, wpnType, moveType, [u_hp, u_atk, u_spd, u_def, u_res], [g_hp, g_atk, g_spd, g_def, g_res], dfl, bvid, refreshType)

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

# Heroes added so far
implemented_heroes = ["Abel", "Alfonse", "Anna", "F!Arthur", "Azama", "Azura", "Barst", "Bartre", "Beruka", "Caeda",
                          "Cain", "Camilla", "Catria", "Cecilia", "Cherche", "Chrom", "Clarine", "Cordelia", "M!Corrin", "F!Corrin",
                          "Donnel", "Draug", "Effie", "Elise", "Eliwood", "Est", "Fae", "Felicia", "Fir", "Florina",
                          "Frederick", "Gaius", "Gordin", "Gunter", "Gwendolyn", "Hana", "Hawkeye", "Hector", "Henry", "Hinata",
                          "Hinoka", "Jagen", "Jakob", "Jeorge", "Kagero", "Laslow", "Leo", "Lilina", "Linde", "Lissa",
                          "Lon'qu", "Lucina", "Lyn", "Maria", "Marth", "Matthew", "Merric", "Minerva", "Niles", "Nino",
                          "Nowi", "Oboro", "Odin", "Ogma", "Olivia", "Palla", "Raigh", "Raven", "Peri", "M!Robin",
                          "Roy", "Ryoma", "Saizo", "Sakura", "F!Selena", "Serra", "Setsuna", "Shanna", "Sharena", "Sheena",
                          "Sophia", "Stahl", "Subaki", "Sully", "Takumi", "Tharja", "Y!Tiki", "A!Tiki", "Virion", "Wrys",

                          "Narcian", "F!Robin", "Ursula", "Michalis", "Navarre", "Zephiel", "Xander", "Lloyd", "Camus"

                          "Eirika", "Ephraim", "Seliph", "Julia",
                          "Eldigan", "Klein", "Lachesis", "Reinhardt", "Olwen", "Sanaki",
                          "Jaffar", "Karel", "Lucius", "Ninian", "Priscilla", "Rebecca",
                          "SP!Chrom", "SP!Lucina", "SP!Xander", "SP!Camilla",
                          "Alm", "Lukas", "Clair", "Faye",
                          "Ike", "Mist", "Soren", "Titania",
                          "Celica", "Mae", "Boey", "Genny",
                          "BR!Caeda", "BR!Charlotte", "BR!Lyn", "BR!Cordelia",
                          "!Marth",
                          "Athena", "Katarina", "Luke", "Roderick", "Legion", "Clarisse",
                          "SU!F!Robin", "SU!Gaius", "SU!Frederick", "SU!A!Tiki",
                          "Tobin", "Delthea", "Mathilda", "Gray", "Saber", "Sonya", "Leon", "Berkut", "Clive",
                          "SU!F!Corrin", "SU!Elise", "SU!Leo", "SU!Xander"
                    ]