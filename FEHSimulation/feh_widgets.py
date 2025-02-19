import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import os

import textwrap
from re import sub

from math import trunc
from math import isnan

import json
from csv import reader, writer
import pickle

import pandas as pd

from functools import partial

from PIL import Image, ImageTk
from natsort import natsorted

from copy import deepcopy

from map import wall_crops, Map
import hero
from combat import *

import field_helpers as feh

# CONSTANTS
PLAYER = 0
ENEMY = 1

RARITY_COLORS = ["#43464f", "#859ba8", "#8a4d15", "#c7d6d6", "#ffc012"]

HP = 0
ATK = 1
SPD = 2
DEF = 3
RES = 4

STATS = {"None": -1, "HP": 0, "Atk": 1, "Spd": 2, "Def": 3, "Res": 4}
STAT_STR = ["HP", "Atk", "Spd", "Def", "Res", "None"]

BLESSINGS_DICT = {"None": -1, "Fire": 0, "Water": 1, "Earth": 2, "Wind": 3, "Light": 4, "Dark": 5, "Astra": 6, "Anima": 7}

BLESSING_COLORS = ["#e63b10", "#0f93f2", "#9e621e", "#449e1e", "#f2ee6f", "#4b1694", "#ed4ed3", "#e2e3da"]
BLESSING_TEXTS  = ["#7a270d", "#b8e6e2", "#dec381", "#a3e89e", "#3f4036", "#e3bee6", "#4f4c44", "#261f23"]

help_text = "Drag heroes from My Units onto the colored squares. Double click to remove them.\nRight click on a placed hero to edit their build (does not affect saved build).\nLeft click an empty colored square to create a new unit for specifically this map."

def _generate_all_units_option():
    names = hero.hero_sheet['Name']
    int_names = hero.hero_sheet['IntName']
    epithets = hero.hero_sheet['Epithet']

    # Units currently allowed for this build of the sim, what's implemented so far

    options = []
    intName_dict = {}

    intName_dict[None] = None

    i = 0
    while i < len(names):
        if int_names[i] in hero.implemented_heroes:
            cur_string = names[i] + ": " + epithets[i]
            options.append(cur_string)
            intName_dict[cur_string] = int_names[i]

        i += 1

    return options, intName_dict

_all_hero_options, _intName_dict = _generate_all_units_option()

def _get_valid_weapons(cur_hero):
    weapons = list(hero.weapon_sheet['IntName'])
    weapon_types = list(hero.weapon_sheet['Type'])

    exclusive1 = list(hero.weapon_sheet['ExclusiveUser1'])
    exclusive2 = list(hero.weapon_sheet['ExclusiveUser2'])
    exclusive3 = list(hero.weapon_sheet['ExclusiveUser3'])
    exclusive4 = list(hero.weapon_sheet['ExclusiveUser4'])

    # Zip into 2D array by row
    exclusive_all = list(zip(exclusive1, exclusive2, exclusive3, exclusive4))

    # Purge NaN values
    exclusive_all = [[value for value in sublist if not isinstance(value, float) or not isnan(value)] for sublist in exclusive_all]

    weapons_of_type = []
    prf_weapons = []

    # Implemented weapons
    implemented_weapons = ["Iron Sword", "Steel Sword", "Silver Sword", "Silver Sword+", "Armorslayer", "Armorslayer+", "Brave Sword", "Brave Sword+", "Ruby Sword", "Ruby Sword+", "Killing Edge", "Killing Edge+",
                           "Iron Lance", "Steel Lance", "Silver Lance", "Silver Lance+", "Heavy Spear", "Heavy Spear+", "Brave Lance", "Brave Lance+", "Sapphire Lance", "Sapphire Lance+", "Killer Lance", "Killer Lance+",
                           "Iron Axe", "Steel Axe", "Silver Axe", "Silver Axe+", "Hammer", "Hammer+", "Brave Axe", "Brave Axe+", "Emerald Axe", "Emerald Axe+", "Killer Axe", "Killer Axe+",
                           "Iron Bow", "Steel Bow", "Silver Bow", "Silver Bow+", "Killer Bow", "Killer Bow+", "Brave Bow", "Brave Bow+", "Assassin's Bow", "Assassin's Bow+",
                           "Iron Dagger", "Steel Dagger", "Silver Dagger", "Silver Dagger+", "Smoke Dagger", "Smoke Dagger+", "Rogue Dagger", "Rogue Dagger+", "Poison Dagger", "Poison Dagger+", "Barb Shuriken", "Barb Shuriken+",
                           "Fire", "Elfire", "Bolganone", "Bolganone+", "Flux", "Ruin", "Fenrir", "Fenrir+", "Rauðrblade", "Rauðrblade+", "Rauðrraven", "Rauðrraven+", "Rauðrwolf", "Rauðrwolf+",
                           "Thunder", "Elthunder", "Thoron", "Thoron+", "Light", "Ellight", "Shine", "Shine+", "Blárblade", "Blárblade+", "Blárraven", "Blárraven+",  "Blárwolf", "Blárwolf+",
                           "Wind", "Elwind", "Rexcalibur", "Rexcalibur+", "Gronnblade", "Gronnblade+", "Gronnraven", "Gronnraven+",  "Gronnwolf", "Gronnwolf+",
                           "Assault", "Absorb", "Absorb+", "Fear", "Fear+", "Slow", "Slow+", "Gravity", "Gravity+", "Panic", "Panic+", "Pain", "Pain+", "Trilemma", "Trilemma+",
                           "Fire Breath", "Fire Breath+", "Flametongue", "Flametongue+", "Lightning Breath", "Lightning Breath+", "Light Breath", "Light Breath+", "Water Breath", "Water Breath+",

                           "Wo Dao", "Wo Dao+", "Harmonic Lance", "Harmonic Lance+", "Wo Gùn", "Wo Gùn+",
                           "Firesweep Bow", "Firesweep Bow+", "Firesweep Lance", "Firesweep L+", "Firesweep S", "Firesweep S+",
                           "Rauðrowl", "Rauðrowl+", "Gronnowl", "Gronnowl+", "Blárowl", "Blárowl+",
                           "Zanbato", "Zanbato+", "Ridersbane", "Ridersbane+", "Poleaxe", "Poleaxe+",
                           "Slaying Edge", "Slaying Edge+", "Slaying Lance", "Slaying Lance+", "Slaying Axe", "Slaying Axe+", "Slaying Bow", "Slaying Bow+",
                           "Armorsmasher", "Armorsmasher+", "Slaying Spear", "Slaying Spear+", "Slaying Hammer", "Slaying Hammer+", "Guard Bow", "Guard Bow+",
                           "Safeguard", "Safeguard+", "Respisal Lance", "Reprisal Lance+", "Barrier Blade", "Barrier Blade+",
                           "The Cleaner", "The Cleaner+", "Shining Bow", "Shining Bow+",
                           "Flash", "Flash+",

                           "Keen Rauðrwolf", "Keen Rauðrwolf+", "Keen Blárwolf", "Keen Blárwolf+", "Keen Gronnwolf", "Keen Gronnwolf+",
                           "Blárserpent", "Blárserpent+",

                           "Legion's Axe", "Legion's Axe+", "Clarisse's Bow", "Clarisse's Bow+", "Berkut's Lance", "Berkut's Lance+",

                           "Blue Egg", "Blue Egg+", "Green Egg", "Green Egg+", "Carrot Lance", "Carrot Lance+", "Carrot Axe", "Carrot Axe+",
                           "Blessed Bouquet", "Blessed Bouquet+", "First Bite", "First Bite+", "Cupid Arrow", "Cupid Arrow+", "Candlelight", "Candlelight+",
                           "Seashell", "Seashell+", "Refreshing Bolt", "Refreshing Bolt+", "Deft Harpoon", "Deft Harpoon+", "Melon Crusher", "Melon Crusher+",
                           "Tomato Tome", "Tomato Tome+", "Sealife Tome", "Sealife Tome+", "Hibiscus Tome", "Hibiscus Tome+", "Lilith Floatie", "Lilith Floatie+",
                           "Dancer's Fan", "Dancer's Fan+", "Dancer's Ring", "Dancer's Ring+", "Dancer's Score", "Dancer's Score+",
                           "Spectral Tome", "Spectral Tome+", "Monstrous Bow", "Monstrous Bow+", "Kitty Paddle", "Kitty Paddle+",
                           "Handbell", "Handbell+", "Sack o' Gifts", "Sack o' Gifts+", "Tannenboom!", "Tannenboom!+", "Candelabra", "Candelabra+",
                           "Hagoita", "Hagoita+", "Kadomatsu", "Kadomatsu+", "Kagami Mochi", "Kagami Mochi+", "Hama Ya", "Hama Ya",
                           "Green Gift", "Green Gift+", "Blue Gift", "Blue Gift+", "Gratia", "Gratia+", "Casa Blanca", "Casa Blanca+",
                           "Giant Spoon", "Giant Spoon+", "Lethal Carrot", "Lethal Carrot+",
                           "Fresh Bouquet", "Fresh Bouquet+", "Ardent Service", "Ardent Service+",
                           "Shell Lance", "Shell Lance+", "Beach Banner", "Beach Banner+", "Cocobow", "Cocobow+",
                           "Starfish", "Starfish+", "Fishie Bow", "Fishie Bow+", "Juicy Wave", "Juicy Wave+",
                           "Cloud Maiougi", "Cloud Maiougi+", "Sky Maiougi", "Sky Maiougi+", "Dusk Uchiwa", "Dusk Uchiwa+",
                           "Bottled Juice",  "Bottled Juice+", "Devilish Bow", "Devilish Bow+", "Witchy Wand", "Witchy Wand+", "Hack-o'-Lantern", "Hack-o'-Lantern+"]

    # Remove of different weapon
    i = 0
    while i < len(weapons):

        # encoding issues today?
        # print(weapons[i])

        if weapon_types[i] in cur_hero.wpnType:
            if (len(exclusive_all[i]) == 0):
                weapons_of_type.append(weapons[i])

            elif cur_hero.intName in exclusive_all[i]:
                prf_weapons.append(weapons[i])

            # Movement-specific beast weapons
            elif "Inf" in exclusive_all[i] and cur_hero.move == 0 and cur_hero.wpnType in hero.BEAST_WEAPONS:
                weapons_of_type.append(weapons[i])

            elif "Cav" in exclusive_all[i] and cur_hero.move == 1 and cur_hero.wpnType in hero.BEAST_WEAPONS:
                weapons_of_type.append(weapons[i])

            elif "Flier" in exclusive_all[i] and cur_hero.move == 2 and cur_hero.wpnType in hero.BEAST_WEAPONS:
                weapons_of_type.append(weapons[i])

            elif "Armor" in exclusive_all[i] and cur_hero.move == 3 and cur_hero.wpnType in hero.BEAST_WEAPONS:
                weapons_of_type.append(weapons[i])

        i += 1

    unrefined_prf_weapons = []
    unrefined_weapons = []

    refine_substrings = ["Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz"]

    # Remove PRF refines
    for string in prf_weapons:
        is_valid = True
        for substring in refine_substrings:
            if substring in string[-3:]:
                is_valid = False

        if is_valid:
            unrefined_prf_weapons.append(string)

    # Remove non-PRF refines
    for string in weapons_of_type:
        is_valid = True
        for substring in refine_substrings:
            if substring in string:
                is_valid = False

        if is_valid and string in implemented_weapons:
            unrefined_weapons.append(string)

    unrefined_weapons = sorted(unrefined_weapons)

    return ["None"] + unrefined_prf_weapons + unrefined_weapons

def _get_valid_refines(weapon_name):
    weapon_names = list(hero.weapon_sheet['IntName'])

    # Find the weapon's position in the sheet
    row_index = 0
    for i, row in enumerate(weapon_names):
        if row == weapon_name:
            row_index = i
            break

    # Get next 5 rows, check for refines
    start = min(row_index + 1, len(weapon_names))
    end = min(row_index + 6, len(weapon_names))
    next_rows = weapon_names[start:end]

    # By default, all weapons can be unrefined
    refine_suffixes = ["None"]

    for row in next_rows:
        # If weapon is same as the one currently equipped, add its suffix
        if weapon_name == row[:-3]:
            refine_suffixes.append(row[-3:])

    return refine_suffixes

def _get_valid_assists(cur_hero):
    assist_names = list(hero.assist_sheet['Name'])

    exclusive1 = list(hero.assist_sheet['ExclusiveUser1'])
    exclusive2 = list(hero.assist_sheet['ExclusiveUser2'])
    exclusive3 = list(hero.assist_sheet['ExclusiveUser3'])

    # Zip into 2D array by row
    exclusive_all = list(zip(exclusive1, exclusive2, exclusive3))

    # Purge NaN values
    exclusive_all = [[value for value in sublist if not isinstance(value, float) or not isnan(value)] for sublist in exclusive_all]

    standard_assists = []
    prf_assists = []

    implemented_assists = ["Heal", "Mend", "Reconcile", "Recover", "Recover+", "Martyr", "Martyr+", "Rehabilitate", "Rehabilitate+", "Restore", "Restore+",
                           "Rally Attack", "Rally Speed", "Rally Defence", "Rally Resistance",
                           "Rally Atk/Spd", "Rally Atk/Def", "Rally Atk/Res", "Rally Spd/Def", "Rally Spd/Res", "Rally Def/Res",
                           "Rally Atk/Spd+", "Rally Spd/Def+",
                           "Rally Up Atk", "Rally Up Atk+",
                           "Dance", "Sing",
                           "Harsh Command", "Ardent Sacrifice", "Reciprocal Aid",
                           "Draw Back", "Reposition", "Swap", "Pivot", "Shove", "Smite"]

    i = 0
    while i < len(assist_names):
        if cur_hero.intName in exclusive_all[i]:
            prf_assists.append(assist_names[i])

        elif assist_names[i] in implemented_assists:
            if (len(exclusive_all[i]) == 0):
                standard_assists.append(assist_names[i])

            elif cur_hero.intName in exclusive_all[i]:
                prf_assists.append(assist_names[i])

            elif "Staff" in exclusive_all[i] and cur_hero.wpnType == "Staff":
                standard_assists.append(assist_names[i])

            elif "Dancers" in exclusive_all[i] and cur_hero.refresh_type == 2:
                prf_assists.append(assist_names[i])

            elif "Singers" in exclusive_all[i] and cur_hero.refresh_type == 1:
                prf_assists.append(assist_names[i])

        i += 1

    standard_assists = sorted(standard_assists)

    return ["None"] + prf_assists + standard_assists

def _get_valid_specials(cur_hero):
    special_names = list(hero.special_sheet['Name'])

    exclusive1 = list(hero.special_sheet['ExclusiveUser1'])
    exclusive2 = list(hero.special_sheet['ExclusiveUser2'])
    exclusive3 = list(hero.special_sheet['ExclusiveUser3'])

    restr_move = list(hero.special_sheet['RestrictedMovement'])
    restr_wpn = list(hero.special_sheet['RestrictedWeapons'])


    # Zip into 2D array by row
    exclusive_all = list(zip(exclusive1, exclusive2, exclusive3))

    # Purge NaN values
    exclusive_all = [[value for value in sublist if not isinstance(value, float) or not isnan(value)] for sublist in exclusive_all]

    standard_specials = []
    prf_specials = []

    # Implemented Specials
    implemented_specials = ["Glowing Ember", "Bonfire", "Ignis", "Chilling Wind", "Iceberg", "Glacies", "New Moon", "Moonbow", "Luna",
                            "Dragon Gaze", "Draconic Aura", "Dragon Fang", "Night Sky", "Glimmer", "Astra", "Retribution", "Reprisal", "Vengeance",
                            "Daylight", "Noontime", "Sol", "Aether", "Blue Flame",
                            "Rising Flame", "Blazing Flame", "Growing Flame",
                            "Rising Light", "Blazing Light", "Growing Light",
                            "Rising Thunder", "Blazing Thunder", "Growing Thunder",
                            "Rising Wind", "Blazing Wind", "Growing Wind",
                            "Buckler", "Escutcheon", "Pavise", "Holy Vestiments", "Sacred Cowl", "Aegis", "Miracle",
                            "Imbue", "Heavenly Light", "Kindled-Fire Balm", "Swift-Winds Balm", "Solid-Earth Balm", "Still-Water Balm",
                            "Windfire Balm", "Windfire Balm+", "Earthwater Balm", "Earthwater Balm+"]

    i = 0
    while i < len(special_names):

        if cur_hero.intName in exclusive_all[i]:
            prf_specials.append(special_names[i])

        elif (len(exclusive_all[i]) == 0) and special_names[i] in implemented_specials:

            add_cond = True

            # Weapon conditions
            if restr_wpn[i] == "Staff" and cur_hero.wpnType == "Staff": add_cond = False
            if restr_wpn[i] == "NotStaff" and cur_hero.wpnType != "Staff": add_cond = False
            if restr_wpn[i] == "NotDragon" and cur_hero.wpnType not in hero.DRAGON_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotDagger" and cur_hero.wpnType not in hero.DAGGER_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotMagic" and cur_hero.wpnType not in hero.TOME_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotBow" and cur_hero.wpnType not in hero.BOW_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotBeast" and cur_hero.wpnType not in hero.BEAST_WEAPONS: add_cond = False

            if "Dragon" in restr_wpn[i] and restr_wpn[i] != "NotDragon" and cur_hero.wpnType in hero.DRAGON_WEAPONS: add_cond = False
            elif "Beast" in restr_wpn[i] and restr_wpn[i] != "NotBeast" and cur_hero.wpnType in hero.BEAST_WEAPONS: add_cond = False
            elif "Ranged" in restr_wpn[i] and cur_hero.wpnType in hero.RANGED_WEAPONS: add_cond = False
            elif "Staff" in restr_wpn[i] and restr_wpn[i] != "NotStaff" and cur_hero.wpnType == "Staff": add_cond = False

            # Movement conditions
            if "Inf" in restr_move[i] and cur_hero.move == 0: add_cond = False
            elif "Cav" in restr_move[i] and cur_hero.move == 1: add_cond = False
            elif "Fly" in restr_move[i] and cur_hero.move == 2: add_cond = False
            elif "Armor" in restr_move[i] and cur_hero.move == 3: add_cond = False

            if add_cond:
                standard_specials.append(special_names[i])

        i += 1

    standard_specials = sorted(standard_specials)

    return ["None"] + prf_specials + standard_specials

def _get_valid_abc_skills(cur_hero):
    skill_names = hero.impl_skills_sheet["Name"]
    skill_letters = hero.impl_skills_sheet["Letter"]

    exclusive1 = list(hero.impl_skills_sheet['ExclusiveUser1'])
    exclusive2 = list(hero.impl_skills_sheet['ExclusiveUser2'])
    exclusive3 = list(hero.impl_skills_sheet['ExclusiveUser3'])

    restr_move = list(hero.impl_skills_sheet['RestrictedMovement'])
    restr_wpn = list(hero.impl_skills_sheet['RestrictedWeapons'])

    # Zip into 2D array by row
    exclusive_all = list(zip(exclusive1, exclusive2, exclusive3))

    # Purge NaN values
    exclusive_all = [[value for value in sublist if not isinstance(value, float) or not isnan(value)] for sublist in exclusive_all]

    standard_skills = []
    standard_skill_letters = []

    prf_skills = []
    prf_skill_letters = []

    i = 0
    while i < len(skill_names):

        if cur_hero.intName in exclusive_all[i]:
            prf_skills.append(skill_names[i])
            prf_skill_letters.append(skill_letters[i])

        elif (len(exclusive_all[i]) == 0):

            add_cond = True

            # Color Conditions
            if restr_wpn[i] == "Colorless" and cur_hero.wpnType in hero.COLORLESS_WEAPONS: add_cond = False
            if restr_wpn[i] == "Red" and cur_hero.wpnType in hero.RED_WEAPONS: add_cond = False
            if restr_wpn[i] == "Blue" and cur_hero.wpnType in hero.BLUE_WEAPONS: add_cond = False
            if restr_wpn[i] == "Green" and cur_hero.wpnType in hero.GREEN_WEAPONS: add_cond = False

            if restr_wpn[i] == "Staff" and cur_hero.wpnType == "Staff": add_cond = False
            if restr_wpn[i] == "NotStaff" and cur_hero.wpnType != "Staff": add_cond = False
            if restr_wpn[i] == "NotDragon" and cur_hero.wpnType not in hero.DRAGON_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotDagger" and cur_hero.wpnType not in hero.DAGGER_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotMagic" and cur_hero.wpnType not in hero.TOME_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotBow" and cur_hero.wpnType not in hero.BOW_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotBeast" and cur_hero.wpnType not in hero.BEAST_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotSword" and cur_hero.wpnType != "Sword": add_cond = False
            if restr_wpn[i] == "NotLance" and cur_hero.wpnType != "Lance": add_cond = False
            if restr_wpn[i] == "NotAxe" and cur_hero.wpnType != "Axe": add_cond = False
            if restr_wpn[i] == "NotRTome" and cur_hero.wpnType != "RTome": add_cond = False
            if restr_wpn[i] == "NotBTome" and cur_hero.wpnType != "BTome": add_cond = False
            if restr_wpn[i] == "NotGTome" and cur_hero.wpnType != "GTome": add_cond = False

            if "Dragon" in restr_wpn[i] and restr_wpn[i] != "NotDragon" and cur_hero.wpnType in hero.DRAGON_WEAPONS: add_cond = False
            elif "Beast" in restr_wpn[i] and restr_wpn[i] != "NotBeast" and cur_hero.wpnType in hero.BEAST_WEAPONS:  add_cond = False
            elif "Staff" in restr_wpn[i] and restr_wpn[i] != "NotStaff" and cur_hero.wpnType == "Staff":             add_cond = False

            if "Ranged" in restr_wpn[i] and cur_hero.wpnType in hero.RANGED_WEAPONS: add_cond = False
            if "Melee" in restr_wpn[i] and cur_hero.wpnType in hero.MELEE_WEAPONS: add_cond = False

            # Movement conditions
            if "Inf" in restr_move[i] and cur_hero.move == 0: add_cond = False
            elif "Cav" in restr_move[i] and cur_hero.move == 1: add_cond = False
            elif "Fly" in restr_move[i] and cur_hero.move == 2: add_cond = False
            elif "Armor" in restr_move[i] and cur_hero.move == 3: add_cond = False

            if add_cond:
                standard_skills.append(skill_names[i])
                standard_skill_letters.append(skill_letters[i])

        i += 1

    #all_valid_skills = prf_skills + standard_skills
    #all_valid_sk_letters = prf_skill_letters + standard_skill_letters

    # Seperate into A, B, and C skills
    prf_a = []
    prf_b = []
    prf_c = []

    i = 0
    while i < len(prf_skills):
        if prf_skill_letters[i] == 'A':
            prf_a.append(prf_skills[i])
        elif prf_skill_letters[i] == 'B':
            prf_b.append(prf_skills[i])
        elif prf_skill_letters[i] == 'C':
            prf_c.append(prf_skills[i])

        i += 1


    a_skills = []
    b_skills = []
    c_skills = []

    i = 0
    while i < len(standard_skills):
        if standard_skill_letters[i] == 'A':
            a_skills.append(standard_skills[i])
        elif standard_skill_letters[i] == 'B':
            b_skills.append(standard_skills[i])
        elif standard_skill_letters[i] == 'C':
            c_skills.append(standard_skills[i])

        i += 1

    a_skills = sorted(a_skills)
    b_skills = sorted(b_skills)
    c_skills = sorted(c_skills)

    a_skills = ["None"] + prf_a + a_skills
    b_skills = ["None"] + prf_b + b_skills
    c_skills = ["None"] + prf_c + c_skills

    return a_skills, b_skills, c_skills

def _get_valid_seals(cur_hero):
    seal_names = list(hero.seals_sheet["Name"])

    restr_move = list(hero.seals_sheet['RestrictedMovement'])
    restr_wpn = list(hero.seals_sheet['RestrictedWeapons'])
    restr_use = list(hero.seals_sheet['Selectable'])

    valid_seals = []

    i = 0
    while i < len(seal_names):
        add_cond = True

        # Color Conditions
        if restr_wpn[i] == "Colorless" and cur_hero.wpnType in hero.COLORLESS_WEAPONS: add_cond = False
        if restr_wpn[i] == "Red" and cur_hero.wpnType in hero.RED_WEAPONS: add_cond = False
        if restr_wpn[i] == "Blue" and cur_hero.wpnType in hero.BLUE_WEAPONS: add_cond = False
        if restr_wpn[i] == "Green" and cur_hero.wpnType in hero.GREEN_WEAPONS: add_cond = False

        if restr_wpn[i] == "Staff" and cur_hero.wpnType == "Staff": add_cond = False
        if restr_wpn[i] == "NotStaff" and cur_hero.wpnType != "Staff": add_cond = False
        if restr_wpn[i] == "NotDragon" and cur_hero.wpnType not in hero.DRAGON_WEAPONS: add_cond = False
        if restr_wpn[i] == "NotDagger" and cur_hero.wpnType not in hero.DAGGER_WEAPONS: add_cond = False
        if restr_wpn[i] == "NotMagic" and cur_hero.wpnType not in hero.TOME_WEAPONS: add_cond = False
        if restr_wpn[i] == "NotBow" and cur_hero.wpnType not in hero.BOW_WEAPONS: add_cond = False
        if restr_wpn[i] == "NotBeast" and cur_hero.wpnType not in hero.BEAST_WEAPONS: add_cond = False
        if restr_wpn[i] == "NotSword" and cur_hero.wpnType != "Sword": add_cond = True
        if restr_wpn[i] == "NotLance" and cur_hero.wpnType != "Lance": add_cond = True
        if restr_wpn[i] == "NotAxe" and cur_hero.wpnType != "Axe": add_cond = True
        if restr_wpn[i] == "NotRTome" and cur_hero.wpnType != "RTome": add_cond = True
        if restr_wpn[i] == "NotBTome" and cur_hero.wpnType != "BTome": add_cond = True
        if restr_wpn[i] == "NotGTome" and cur_hero.wpnType != "GTome": add_cond = True

        if "Dragon" in restr_wpn[i] and restr_wpn[i] != "NotDragon" and cur_hero.wpnType in hero.DRAGON_WEAPONS: add_cond = False
        elif "Beast" in restr_wpn[i] and restr_wpn[i] != "NotBeast" and cur_hero.wpnType in hero.BEAST_WEAPONS:  add_cond = False
        elif "Staff" in restr_wpn[i] and restr_wpn[i] != "NotStaff" and cur_hero.wpnType == "Staff":             add_cond = False

        if "Ranged" in restr_wpn[i] and cur_hero.wpnType in hero.RANGED_WEAPONS: add_cond = False
        if "Melee" in restr_wpn[i] and cur_hero.wpnType in hero.MELEE_WEAPONS: add_cond = False

        # Movement conditions
        if "Inf" in restr_move[i] and cur_hero.move == 0: add_cond = False
        elif "Cav" in restr_move[i] and cur_hero.move == 1: add_cond = False
        elif "Fly" in restr_move[i] and cur_hero.move == 2: add_cond = False
        elif "Armor" in restr_move[i] and cur_hero.move == 3: add_cond = False

        if add_cond and restr_use[i]:
            valid_seals.append(seal_names[i])

        i += 1

    return ["None"] + sorted(valid_seals)

class _HeroProxy:
    def __init__(self):
        self.full_name = ""

        self.resplendent = False
        self.rarity = 5
        self.level = 40
        self.merge = 0
        self.dflowers = 0
        self.asset = -1
        self.flaw = -1
        self.asc_asset = -1
        self.blessing = None
        self.s_support = 0
        self.a_support = None

        self.weapon = None
        self.refine = ""
        self.assist = None
        self.special = None
        self.askill = None
        self.bskill = None
        self.cskill = None
        self.sSeal = None
        self.xskill = None

        self.emblem = None
        self.emblem_merge = 0

    def reset(self):
        self.resplendent = False
        self.rarity = 5
        self.level = 40
        self.merge = 0
        self.dflowers = 0

        self.asset = -1
        self.flaw = -1
        self.asc_asset = -1

        self.blessing = None

        self.s_support = 0
        self.a_support = None

        self.weapon = None
        self.refine = ""
        self.assist = None
        self.special = None
        self.askill = None
        self.bskill = None
        self.cskill = None
        self.sSeal = None
        self.xskill = None

        self.emblem = None
        self.emblem_merge = 0

    def apply_proxy(self, apl_hero):
        if apl_hero is None: return

        # Neutral Input

        if self.asset == -1 and self.flaw == -1:
            self.asset = 0
            self.flaw = 0

        if self.asc_asset == -1:
            self.asc_asset = self.asset

        apl_hero.resp = self.resplendent

        apl_hero.emblem = self.emblem

        apl_hero.set_rarity(self.rarity)
        apl_hero.set_IVs(self.asset, self.flaw, self.asc_asset)
        apl_hero.set_merges(self.merge)
        apl_hero.set_dragonflowers(self.dflowers)

        if self.emblem != None:
            self.set_emblem_merges(self.emblem_merge)

        apl_hero.set_level(self.level)

        apl_hero.allySupport = _intName_dict[self.a_support]

        apl_hero.summonerSupport = int(self.s_support)
        apl_hero.set_visible_stats()

        if self.weapon is not None:
            wpn_name = self.weapon.intName

            refine_substrings = ["Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz"]

            if wpn_name[-3:] in refine_substrings:
                wpn_name = wpn_name[:-3]

            if self.refine == "None": self.refine = ""

            self.weapon = hero.makeWeapon(wpn_name + self.refine)

        apl_hero.set_skill(self.weapon, hero.WEAPON)
        apl_hero.set_skill(self.assist, hero.ASSIST)
        apl_hero.set_skill(self.special, hero.SPECIAL)
        apl_hero.set_skill(self.askill, hero.ASKILL)
        apl_hero.set_skill(self.bskill, hero.BSKILL)
        apl_hero.set_skill(self.cskill, hero.CSKILL)
        apl_hero.set_skill(self.sSeal, hero.SSEAL)
        apl_hero.set_skill(self.xskill, hero.XSKILL)

        apl_hero.blessing = self.blessing

# Stats that are only applied when unit is deployed in an actual battle
# Such stats include but are not limited to:
# - Stat boosts granted by a Legendary/Mythic hero
# - Bonus unit status in Arena, Tempest Trials, etc.
# - Aether Raid Fortress level boosts
def _apply_battle_stats(team, bonus_arr, mode, season):

    if mode == hero.GameMode.Story and team[0].side == ENEMY:
        return

    element_boosts = {}

    for unit in team:
        # If unit is a legendary or mythic, and current season is of their element
        if unit.blessing is not None and unit.blessing.boostType != 0 and unit.blessing.element in season:

            # If unit is a legendary
            if unit.blessing.element in hero.ARENA_ELEMENTS:

                # Initialize values in element_boosts dict
                if unit.blessing.element not in element_boosts:
                    element_boosts[unit.blessing.element] = [0, 0, 0, 0, 0]

                # HP boost
                element_boosts[unit.blessing.element][HP] += 3

                # Other stats boost
                if unit.blessing.stat == ATK:
                    element_boosts[unit.blessing.element][ATK] += 2
                elif unit.blessing.stat == SPD:
                    element_boosts[unit.blessing.element][SPD] += 3
                elif unit.blessing.stat == DEF:
                    element_boosts[unit.blessing.element][DEF] += 4
                elif unit.blessing.stat == RES:
                    element_boosts[unit.blessing.element][RES] += 4

    for unit in team:
        unit.battle_stat_mods = [0] * 5

        if unit.blessing is not None and unit.blessing.boostType == 0 and unit.blessing.element in element_boosts:
            unit.battle_stat_mods = element_boosts[unit.blessing.element]
            unit.set_visible_stats()

    i = 0
    while i < len(team):
        if bonus_arr[i]:
            unit = team[i]

            unit.battle_stat_mods[HP] += 10
            unit.battle_stat_mods[ATK] += 4
            unit.battle_stat_mods[SPD] += 4
            unit.battle_stat_mods[DEF] += 4
            unit.battle_stat_mods[RES] += 4

        i += 1


# Scrollable frame compatitble with ttk.Comboboxes
class MyScrollableFrame(ctk.CTkScrollableFrame):
    def check_if_master_is_canvas(self, widget):
        # call the original method if widget is a tkinter widget, not string
        if isinstance(widget, tk.Widget):
            return super().check_if_master_is_canvas(widget)
        return False

class HeroListing(tk.Frame):
    def __init__(self, master, fg, buttonbg, **kw):
        tk.Frame.__init__(self, master=master, **kw)

        self.name_frame = tk.Frame(self, **kw)
        self.search_bar_frame = tk.Frame(self, **kw)
        self.button_frame = tk.Frame(self, **kw)
        self.command_frame = tk.Frame(self, **kw)

        self.selected_button = None
        self.unit_buttons = []
        self.unit_button_photos = []

        self.button_color = buttonbg
        self.text_color = fg

        self.confirm_deletion_popup = None
        self.creation_menu = None

        self.search_bar = None

        self.target_widget = None
        self.default_target_widget = None

        self.drag_data = None
        self.dragging_from_text = False
        self.dragging_from_image = False
        self.label_causing_offset = None

        # Used for creating heroes within the creation menu
        self.hero_proxy = None
        self.created_hero = None

        self.creation_labels = []
        self.creation_str_vars = []
        self.creation_comboboxes = []

        self.creation_image_label = None
        self.image1_label = None
        self.image2_label = None
        self.unit_picked = None
        self.unit_name = None
        self.unit_stats = None

        self.build_name = None
        self.creation_build_field = None
        self.creation_make_text = None

        self.error_text = None

        self.stat_strings = []
        self.creation_stats = []

        self.wpn_icon_img = None
        self.move_icon_img = None

        self.creation_make_button = None

        # Talking with other widgets
        self.unit_status = None

        bg_color = "#ddd"

        if "bg" in kw:
            bg_color = kw["bg"]

        # Name frame (has name of frame)
        self.name_label = tk.Label(self.name_frame, text=" My Units", bg=bg_color, fg=fg, font=(None, 16))
        self.name_label.pack(anchor=tk.NW)

        # Search bar frame (has search bar and buttons to search/clear)
        # - search will leave behind units with the same name, internal name, or build name
        # - clear will remove current prompt and display all units (searching for "" will do the same)
        def disable_new_line(event):
            self.refresh_buttons(True)
            return "break"

        clear_button = tk.Button(self.search_bar_frame, text="Clear", bg=buttonbg, fg=fg, relief="flat", bd=0, command=partial(self.refresh_buttons, False), width=12)
        clear_button.pack(side=tk.RIGHT, padx=(5, 5))

        search_button = tk.Button(self.search_bar_frame, text="Search", bg=buttonbg, fg=fg, relief="flat", bd=0, command=partial(self.refresh_buttons, True), width=12)
        search_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.search_bar = search_entry = tk.Text(self.search_bar_frame, width=50, height=1, undo=True, font=("Helvetica", 12))
        search_entry.bind("<Return>", disable_new_line)
        search_entry.pack(side=tk.RIGHT, padx=(5, 0), expand=True, fill=tk.X)

        # Button frame, has buttons for each unit in my_units.csv
        # - can be dragged onto GameplayCanvas while in Preparation mode to add units to certain positions
        # - can also be dragged onto ExtrasFrame when in Preparation mode and on the My Team tab

        self.scrolling_frame = unit_button_listing = MyScrollableFrame(self.button_frame)
        unit_button_listing.pack(expand=True, fill=tk.BOTH)

        for x in range(20):
            cur_button = tk.Button(unit_button_listing, text="Hey all scott here", font=("Helvetica", 14), relief="flat")
            cur_button.pack(pady=3, anchor=tk.W, fill=tk.X, expand=True)

            self.unit_buttons.append(cur_button)

        # Command frame, has buttons for adding, editing, and deleting
        # - adding should always be active
        # - editing & deleting should only be active iff a unit is selected

        create_button = tk.Button(self.command_frame, text="Create New", bg=buttonbg, fg=fg, bd=0, command=self.create_creation_popup)
        create_button.pack(side=tk.LEFT, padx=5)

        # Seperate method to handle things

        self.edit_button = tk.Button(self.command_frame, text="Edit", state=tk.DISABLED, bg=buttonbg, fg=fg, bd=0, command=self.create_edit_popup)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        def create_deletion_popup():
            if not self.confirm_deletion_popup:
                self.confirm_deletion_popup = popup = tk.Toplevel(self)
                popup.protocol("WM_DELETE_WINDOW", self.button_deletion_cancel)
                popup.title("Confirm Deletion")

                label = tk.Label(popup, text='Are you sure you want to delete this build, "' + self.selected_button._text + '"?')
                label.pack(pady=20, padx=20)

                lower_frame = tk.Frame(popup)
                lower_frame.pack()

                cancel_button = tk.Button(lower_frame, text="Cancel", command=self.button_deletion_cancel)
                cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

                confirm_button = tk.Button(lower_frame, text="Delete", command=self.button_deletion_confirm)
                confirm_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = tk.Button(self.command_frame, text="Delete", state=tk.DISABLED, bg=buttonbg, fg=fg, bd=0, command=create_deletion_popup)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # Populate frame with buttons corresponding to CSV
        self.refresh_buttons(False)

        self.name_frame.pack(side=tk.TOP, fill=tk.X)
        self.search_bar_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.button_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.command_frame.pack(side=tk.BOTTOM, pady=5)

    def refresh_buttons(self, use_search_str):
        self.edit_button.config(state="disabled")
        self.delete_button.config(state="disabled")

        if use_search_str:
            search_str = self.search_bar.get( '1.0', 'end-1c')
        else:
            self.search_bar.delete('1.0', 'end-1c')
            search_str = ""

        self.selected_button = None

        for button in self.unit_buttons:
            button.forget()
            button.destroy()

        self.unit_buttons.clear()
        self.unit_button_photos.clear()

        units_read = pd.read_csv("my_units.csv", encoding='cp1252')

        for i, hrow in enumerate(units_read.iterrows()):
            respString = "-R" if hrow[1]['Resplendent'] == True else ""

            cur_image = Image.open("TestSprites/" + hrow[1]['IntName'] + respString + ".png")
            width = cur_image.width
            cropped_img = cur_image.crop((width // 2 - 100, 0, width // 2 + 100, 120))

            new_width = int(cropped_img.width * 0.30)
            new_height = int(cropped_img.height * 0.30)

            cur_photo = ctk.CTkImage(cropped_img, size=(new_width, new_height))

            self.unit_button_photos.append(cur_photo)

            build_name = str(hrow[1]['Build Name'])

            if search_str.lower() in build_name.lower() or search_str.lower() in hrow[1]['IntName'].lower():

                cur_button = ctk.CTkButton(self.scrolling_frame,
                                           fg_color=self.button_color,
                                           text_color=self.text_color,
                                           image=cur_photo,
                                           text=build_name,
                                           font=("Helvetica", 14, "bold"),
                                           compound=tk.LEFT,
                                           anchor=tk.W,
                                           )

                cur_button.bind('<Button-1>', partial(self.on_click, hrow[1]))
                cur_button.bind('<ButtonRelease-1>', self.on_release)

                cur_button.configure(command=partial(self.select_button, cur_button))
                cur_button.pack(pady=3, anchor=tk.W, fill=tk.X, expand=True)

                self.unit_buttons.append(cur_button)

    def on_click(self, row_data, event):
        if isinstance(event.widget, tk.Label):
            self.label_causing_offset = event.widget
        else:
            self.label_causing_offset = None

        self.drag_data = row_data

        self.unit_status.update_from_obj(make_hero_from_pd_row(row_data, PLAYER))

    def on_release(self, event):

        target_widget = event.widget.winfo_containing(event.x_root, event.y_root)

        if self.target_widget == target_widget and target_widget != self.default_target_widget:
            x, y = event.x, event.y

            # Event uses as its starting point the top left corner of the clicked Widget
            # The CtkButtons are composed of a Canvas and two labels. If dragging from a
            # label, the coordinates will be slightly off, since the drag is in respect
            # to the label, not the button itself
            if self.label_causing_offset:
                x += self.label_causing_offset.winfo_rootx() - self.selected_button.winfo_rootx()
                y += self.label_causing_offset.winfo_rooty() - self.selected_button.winfo_rooty()

            button_root_x = self.selected_button.winfo_rootx()
            button_root_y = self.selected_button.winfo_rooty()
            widget_root_x = target_widget.winfo_rootx()
            widget_root_y = target_widget.winfo_rooty()

            # Calculate relative positions
            widget_x = x + button_root_x - widget_root_x
            widget_y = y + button_root_y - widget_root_y

            #print(widget_x, widget_y)

            target_widget.place_unit_from_frame(self.drag_data, widget_x, widget_y)

        self.drag_data = None

    def select_button(self, button):
        if self.selected_button:
            self.selected_button.configure(fg_color=self.button_color)
            self.selected_button = None

        else:
            self.edit_button.config(state="normal")
            self.delete_button.config(state="normal")

        button.configure(fg_color="#2088e3")
        self.selected_button = button

        if self.confirm_deletion_popup:
            self.confirm_deletion_popup.destroy()
            self.confirm_deletion_popup = None

    def create_creation_popup(self):
        if not self.creation_menu:
            self.creation_menu = creation = tk.Toplevel(self)
            creation.wm_attributes("-topmost", 1)
            creation.protocol("WM_DELETE_WINDOW", self.unit_creation_cancel)
            creation.title("Unit Creation")

            top_frame = tk.Frame(creation, bg='#292e36')
            bottom_frame = tk.Frame(creation, bg='#292e36')
            unit_stat_frame = tk.Frame(creation, bg='#2b2a69')
            dropbox_frame = tk.Frame(creation, bg='#a5b7c2')

            creation_back_button = tk.Button(top_frame, text='Cancel', width=10, command=self.unit_creation_cancel)
            creation_back_button.pack(side=tk.LEFT, anchor='nw', padx=10, pady=10)

            def add_unit_to_list():
                hero_to_add = self.created_hero

                cur_build_name = self.build_name.get()

                if self.creation_str_vars[0].get() != "" and self.build_name.get() != "":

                    name = hero_to_add.intName
                    weapon = hero_to_add.weapon.intName if hero_to_add.weapon is not None else None
                    assist = hero_to_add.assist.name if hero_to_add.assist is not None else None
                    special = hero_to_add.special.name if hero_to_add.special is not None else None
                    askill = hero_to_add.askill.name if hero_to_add.askill is not None else None
                    bskill = hero_to_add.bskill.name if hero_to_add.bskill is not None else None
                    cskill = hero_to_add.cskill.name if hero_to_add.cskill is not None else None
                    sSeal = hero_to_add.sSeal.name if hero_to_add.sSeal is not None else None
                    xskill = None

                    level = hero_to_add.level
                    merges = hero_to_add.merges
                    rarity = hero_to_add.rarity

                    asset = hero_to_add.asset
                    flaw = hero_to_add.flaw
                    asc = hero_to_add.asc_asset

                    blessing = hero_to_add.blessing.element if (hero_to_add.blessing is not None and hero_to_add.blessing.boostType == 0) else None

                    sSupport = int(hero_to_add.summonerSupport)
                    aSupport = None

                    dflowers = 0
                    resp = False
                    emblem = None
                    emblem_merges = 0
                    cheats = False

                    data = [name, cur_build_name,
                            weapon, assist, special, askill, bskill, cskill, sSeal, xskill,
                            level, merges, rarity, asset, flaw, asc, sSupport, aSupport, blessing, dflowers, resp, emblem, emblem_merges, cheats]

                    my_units_file = "my_units.csv"
                    names = pd.read_csv(my_units_file, encoding='cp1252')['Build Name'].tolist()

                    # Ensure build name is unique
                    if cur_build_name not in names:

                        try:
                            my_units_file = "my_units.csv"

                            with open(my_units_file, mode="a", newline='', encoding="cp1252") as file:
                                f_writer = writer(file)
                                f_writer.writerow(data)

                            # Go back to unit selection screen
                            self.unit_creation_cancel()
                            self.refresh_buttons(False)

                            ally_supports = open('supports.pkl', 'rb')
                            db = pickle.load(ally_supports)

                            new_db = []

                            for pairing in db:
                                if hero_to_add.intName not in pairing and hero_to_add.allySupport not in pairing:
                                    new_db.append(pairing)

                            if hero_to_add.allySupport is not None:
                                new_db.append((hero_to_add.intName, hero_to_add.allySupport))

                            open("supports.pkl", "w").close()

                            db_file = open("supports.pkl", "ab")
                            pickle.dump(new_db, db_file)
                            db_file.close()


                        except PermissionError:
                            print(f"Error: Permission denied when writing to file. Please close {my_units_file} and try again.")

                    else:
                        self.error_text.config(fg='#d60408', text="Error: Build Name Already Exists")
                else:
                    self.error_text.config(fg='#d60408', text='Error: No Unit Selected or Build Name Empty')

            self.creation_make_button = tk.Button(bottom_frame, text='Create', width=10, command=add_unit_to_list)
            self.creation_make_button.pack(side=tk.RIGHT, anchor='nw', padx=10, pady=10)

            self.build_name = tk.StringVar()
            self.creation_build_field = tk.Entry(bottom_frame, width=30, font="Helvetica", textvariable=self.build_name)
            self.creation_make_text = tk.Label(bottom_frame, text='Build Name: ', width=10)

            self.creation_build_field.pack(side=tk.RIGHT, anchor='nw', padx=10, pady=10)
            self.creation_make_text.pack(side=tk.RIGHT, anchor='nw', padx=10, pady=10)

            self.error_text = tk.Label(bottom_frame, text='Error: No Unit Selected or Build Name Empty', bg='#292e36', fg='#292e36', font="Helvetica 10 bold")
            self.error_text.pack(side=tk.LEFT, anchor='nw', padx=10, pady=10)

            self.unit_picked = tk.StringVar()
            self.unit_picked.set("No Hero Selected")

            PIXEL = tk.PhotoImage(width=1, height=1)

            self.creation_image_label = tk.Label(unit_stat_frame, image=PIXEL, textvariable=self.unit_picked, font="Helvetica 13", compound=tk.TOP, height=200, width=200, bg='#728275',
                                                 relief=tk.RAISED)
            self.creation_image_label.pack(padx=10, pady=10)

            creation_icon_window = tk.Frame(unit_stat_frame, bg='#070708', relief=tk.RAISED)
            creation_icon_window.pack()

            move_icons = []
            status_pic = Image.open("CombatSprites/" + "Status" + ".png")

            inf_icon = status_pic.crop((350, 414, 406, 468))
            inf_icon = inf_icon.resize((24, 24), Image.LANCZOS)
            move_icons.append(ImageTk.PhotoImage(inf_icon))
            cav_icon = status_pic.crop((462, 414, 518, 468))
            cav_icon = cav_icon.resize((24, 24), Image.LANCZOS)
            move_icons.append(ImageTk.PhotoImage(cav_icon))
            fly_icon = status_pic.crop((518, 414, 572, 468))
            fly_icon = fly_icon.resize((24, 24), Image.LANCZOS)
            move_icons.append(ImageTk.PhotoImage(fly_icon))
            arm_icon = status_pic.crop((406, 414, 462, 468))
            arm_icon = arm_icon.resize((24, 24), Image.LANCZOS)
            move_icons.append(ImageTk.PhotoImage(arm_icon))

            weapon_icons = []
            i = 0
            while i < 24:
                cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
                cur_icon = cur_icon.resize((25, 25), Image.LANCZOS)
                weapon_icons.append(ImageTk.PhotoImage(cur_icon))
                i += 1

            self.image1_label = tk.Label(creation_icon_window, image=PIXEL, height=20, width=20, bg='#070708')
            self.image1_label.pack(side=tk.LEFT, padx=5, pady=5)

            self.image2_label = tk.Label(creation_icon_window, image=PIXEL, height=20, width=20, bg='#070708')
            self.image2_label.pack(side=tk.LEFT, padx=5, pady=5)

            self.unit_name = tk.StringVar()
            self.unit_name.set("---\n---")

            creation_unit_label = tk.Label(unit_stat_frame, textvariable=self.unit_name, compound=tk.TOP, height=2, width=25, bg='#070708', fg="#e0e86b")
            creation_unit_label.pack(padx=10, pady=10)

            self.unit_stats = tk.StringVar()
            self.unit_stats.set("Lv. ---\n+0 Flowers")

            creation_merge_label = tk.Label(unit_stat_frame, textvariable=self.unit_stats, compound=tk.TOP, height=2, width=18, bg='#070708', fg="#e0e86b")
            creation_merge_label.pack(padx=10, pady=(10, 20))

            self.creation_stats = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()]
            self.stat_strings = ["HP: ", "Atk: ", "Spd: ", "Def: ", "Res: "]

            creation_stat_labels = []

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + "---")
                cur_label = tk.Label(unit_stat_frame, textvariable=self.creation_stats[i], compound=tk.TOP, height=1, width=18, bg='#070708', fg="#e0e86b", relief="solid")
                cur_label.pack(padx=10)
                creation_stat_labels.append(cur_label)

                i += 1

            names = ["Unit", "Rarity", "Merge", "Asset", "Blessing", "S-Support", "Pair Up", "Weapon", "Refine", "Assist", "Special", "Emblem", "Emblem Merge"]
            names2 = ["Resplendent", "Level", "Dragonflowers", "Flaw", "Asc. Asset", "A-Support Ally", "A-Support Level", "A Skill", "B Skill", "C Skill", "Sacred Seal", "X Skill", "Aided"]

            all_hero_options, intName_dict = _all_hero_options, _intName_dict

            numbers = list(range(41))
            iv_strs = ["None", "HP", "Atk", "Spd", "Def", "Res"]

            left_dropbox_frame = tk.Frame(dropbox_frame, bg="#a5b7c2")
            right_dropbox_frame = tk.Frame(dropbox_frame, bg="#a5b7c2")

            # Handles unit creation
            self.hero_proxy = _HeroProxy()
            self.created_hero = None

            self.creation_labels = []
            self.creation_str_vars = []
            self.creation_comboboxes = []

            def disable_scroll(event):
                return 'break'

            combo1 = ttk.Combobox(left_dropbox_frame)
            combo1.grid(row=0, column=1, padx=10, pady=10)

            for row in range(13):
                cur_str_var = tk.StringVar()

                cur_label = tk.Label(left_dropbox_frame, text=names[row], width=12)
                self.creation_labels.append(cur_label)

                cur_label.grid(row=row, column=0, padx=10, pady=5)

                combo1 = ttk.Combobox(left_dropbox_frame, textvariable=cur_str_var)
                combo1.bind('<MouseWheel>', disable_scroll)
                combo1.grid(row=row, column=1, padx=10, pady=10)

                self.creation_str_vars.append(cur_str_var)
                self.creation_comboboxes.append(combo1)

                # NAMES
                if row == 0:
                    combo1['textvariable'] = None
                    combo1['values'] = all_hero_options
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_name)

                # RARITY
                if row == 1:
                    combo1['textvariable'] = None
                    combo1['values'] = list(reversed(numbers[1:6]))
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_rarity)

                # MERGES
                if row == 2:
                    combo1['textvariable'] = None
                    combo1['values'] = list(numbers[0:11])
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_merge)

                # ASSET
                if row == 3:
                    combo1['textvariable'] = None
                    combo1['values'] = iv_strs
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_asset)

                # BLESSING
                if row == 4:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_blessing)

                # S SUPPORT
                if row == 5:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_summsupport)

                # WEAPON
                if row == 7:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_weapon)

                # REFINE
                if row == 8:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_refine)

                # ASSIST
                if row == 9:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_assist)

                # SPECIAL
                if row == 10:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_special)

            for row in range(13):
                cur_str_var = tk.StringVar()

                cur_label = tk.Label(right_dropbox_frame, text=names2[row], width=12)

                self.creation_labels.append(cur_label)

                cur_label.grid(row=row, column=0, padx=10, pady=5)

                combo1 = ttk.Combobox(right_dropbox_frame, textvariable=cur_str_var)
                combo1.bind('<MouseWheel>', disable_scroll)
                combo1.grid(row=row, column=1, padx=10, pady=10)

                self.creation_str_vars.append(cur_str_var)
                self.creation_comboboxes.append(combo1)

                # LEVEL
                if row == 1:
                    combo1['textvariable'] = None
                    combo1['values'] = list(reversed(numbers[1:41]))
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_level)

                # FLAW
                if row == 3:
                    combo1['textvariable'] = None
                    combo1['values'] = iv_strs
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_flaw)

                if row == 5:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_allysupport)

                if row == 7:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_askill)

                if row == 8:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_bskill)

                if row == 9:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_cskill)

                if row == 10:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_sseal)

            left_dropbox_frame.pack(padx=8, pady=7, side=tk.LEFT, anchor='nw')
            right_dropbox_frame.pack(padx=8, pady=7, side=tk.RIGHT, anchor='ne')

            top_frame.pack(side=tk.TOP, expand=False, fill=tk.X)
            bottom_frame.pack(side=tk.BOTTOM, expand=False, fill=tk.X)
            unit_stat_frame.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)
            dropbox_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def handle_selection_change_name(self, event=None):
        # Get name selected
        selected_value = self.creation_str_vars[0].get()

        # Get internal name from name + epithet
        cur_intName = _intName_dict[selected_value]

        # Set who this unit is on the proxy
        self.hero_proxy.full_name = selected_value

        # Get image of selected unit
        cur_image = Image.open("TestSprites/" + cur_intName + ".png")
        resized_image = cur_image.resize((int(cur_image.width / 1.3), int(cur_image.height / 1.3)), Image.LANCZOS)
        curPhoto = ImageTk.PhotoImage(resized_image)
        self.creation_image_label.config(image=curPhoto)
        self.creation_image_label.image = curPhoto

        # Actual Hero object
        self.created_hero: hero.Hero = hero.makeHero(cur_intName)

        # Set default value in ComboBoxes upon first Hero selection

        # Set default rarity
        self.creation_str_vars[1].set(min(5, self.hero_proxy.rarity))

        # Set default merge
        self.creation_str_vars[2].set(max(0, self.hero_proxy.merge))

        # Set default Asset
        self.creation_str_vars[3].set(STAT_STR[self.hero_proxy.asset])

        # Set default Flaw
        self.creation_str_vars[16].set(STAT_STR[self.hero_proxy.flaw])

        # Set default Asc Asset
        # creation_str_vars[16].set(STAT_STR[curProxy.asc_asset])

        # Set default level
        self.creation_str_vars[14].set(min(40, self.hero_proxy.level))

        if self.created_hero.blessing is None:
            self.creation_str_vars[4].set("None")
            self.creation_comboboxes[4]['values'] = ["None", "Fire", "Water", "Earth", "Wind"]
        else:
            if self.created_hero.blessing.boostType != 0:
                self.creation_str_vars[4].set(self.created_hero.blessing.toString())
            self.creation_comboboxes[4]['values'] = []

        self.hero_proxy.blessing = self.created_hero.blessing

        # Generate all possible weapons for selected Hero
        weapons = _get_valid_weapons(self.created_hero)

        # If newly selected character can't wield what's currently in the box, remove it
        if self.creation_str_vars[7].get() not in weapons:
            # This should be no weapon by default
            self.hero_proxy.weapon = None
            self.creation_str_vars[7].set("None")

            # Reset what refines should be available too
            self.creation_str_vars[8].set("None")
            self.creation_comboboxes[8]['values'] = []

        # Set allowed weapons
        self.creation_comboboxes[7]['values'] = weapons

        if self.hero_proxy.weapon is not None:
            CreateToolTip(self.creation_labels[7], self.hero_proxy.weapon.desc)
        else:
            CreateToolTip(self.creation_labels[7], "")

        # Generate all possible assist skills
        assists = _get_valid_assists(self.created_hero)

        if self.creation_str_vars[9].get() not in assists:
            self.hero_proxy.assist = None
            self.creation_str_vars[9].set("None")

        # Set allowed assists
        self.creation_comboboxes[9]['values'] = assists

        if self.hero_proxy.assist is not None:
            CreateToolTip(self.creation_labels[9], self.hero_proxy.assist.desc)
        else:
            CreateToolTip(self.creation_labels[9], "")

        # Generate all possible special skills
        specials = _get_valid_specials(self.created_hero)

        if self.creation_str_vars[10].get() not in specials:
            self.hero_proxy.special = None
            self.creation_str_vars[10].set("None")

        # Set allowed assists
        self.creation_comboboxes[10]['values'] = specials

        if self.hero_proxy.special is not None:
            CreateToolTip(self.creation_labels[9], self.hero_proxy.special.desc)
        else:
            CreateToolTip(self.creation_labels[9], "")

        # ABC Skills
        a_sk, b_sk, c_sk = _get_valid_abc_skills(self.created_hero)

        # Reset a skills
        if self.creation_str_vars[20].get() not in a_sk:
            self.hero_proxy.askill = None
            self.creation_str_vars[20].set("None")

        # Set allowed a skills
        self.creation_comboboxes[20]['values'] = a_sk

        # Reset b skills
        if self.creation_str_vars[21].get() not in b_sk:
            self.hero_proxy.bskill = None
            self.creation_str_vars[21].set("None")

        # Set allowed b skills
        self.creation_comboboxes[21]['values'] = b_sk

        # Reset c skills
        if self.creation_str_vars[22].get() not in c_sk:
            self.hero_proxy.cskill = None
            self.creation_str_vars[22].set("None")

        # Set allowed c skills
        self.creation_comboboxes[22]['values'] = c_sk

        if self.hero_proxy.askill is not None:
            CreateToolTip(self.creation_labels[20], self.hero_proxy.askill.desc)
        else:
            CreateToolTip(self.creation_labels[20], "")

        if self.hero_proxy.bskill is not None:
            CreateToolTip(self.creation_labels[21], self.hero_proxy.bskill.desc)
        else:
            CreateToolTip(self.creation_labels[21], "")

        if self.hero_proxy.cskill is not None:
            CreateToolTip(self.creation_labels[22], self.hero_proxy.cskill.desc)
        else:
            CreateToolTip(self.creation_labels[22], "")

        # Get valid sacred seals
        s_seals = _get_valid_seals(self.created_hero)

        # Reset sacred seal
        if self.creation_str_vars[23].get() not in s_seals:
            self.hero_proxy.sSeal = None
            self.creation_str_vars[23].set("None")

        # Set allowed sacred seals
        self.creation_comboboxes[23]['values'] = s_seals

        # Set Ally Support Partner
        if self.created_hero.allySupport is not None:
            temp_ally = hero.makeHero(self.created_hero.allySupport)
            temp_str = temp_ally.name + ": " + temp_ally.epithet
            self.hero_proxy.a_support = temp_str
        else:
            temp_str = "None"

        self.creation_str_vars[18].set(temp_str)

        # Valid support partners for a hero should be all heroes minus themselves
        self.creation_comboboxes[18]['values'] = ["None"] + [support_names for support_names in _all_hero_options if support_names != self.created_hero.name + ": " + self.created_hero.epithet]

        # Set Summoner Support Rank
        self.creation_str_vars[5].set("None")

        self.creation_comboboxes[5]['values'] = ["None", "Rank C", "Rank B", "Rank A", "Rank S"]

        # handle_selection_change_name.created_hero = madeHero
        self.hero_proxy.apply_proxy(self.created_hero)

        move_icons = []
        status_pic = Image.open("CombatSprites/Status.png")

        inf_icon = status_pic.crop((350, 414, 406, 468))
        inf_icon = inf_icon.resize((24, 24), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(inf_icon))
        cav_icon = status_pic.crop((462, 414, 518, 468))
        cav_icon = cav_icon.resize((24, 24), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(cav_icon))
        fly_icon = status_pic.crop((518, 414, 572, 468))
        fly_icon = fly_icon.resize((24, 24), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(fly_icon))
        arm_icon = status_pic.crop((406, 414, 462, 468))
        arm_icon = arm_icon.resize((24, 24), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(arm_icon))

        weapon_icons = []
        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
            cur_icon = cur_icon.resize((25, 25), Image.LANCZOS)
            weapon_icons.append(ImageTk.PhotoImage(cur_icon))
            i += 1

        self.move_icon_img = move_icons[self.created_hero.move]
        self.wpn_icon_img = weapon_icons[hero.weapons[self.created_hero.wpnType][0]]

        self.image1_label.config(image=self.move_icon_img)
        self.image2_label.config(image=self.wpn_icon_img)

        self.unit_picked.set("")

        star_var = "✰" * self.hero_proxy.rarity
        self.unit_name.set(f"{selected_value}\n{star_var}")

        merge_str = ""
        if self.hero_proxy.merge > 0:
            merge_str = "+" + str(self.hero_proxy.merge)

        self.unit_stats.set(f"Lv. {self.hero_proxy.level}{merge_str}\n+0 Flowers")

        # unit_stats.set(f"Lv. {curProxy.level}\n+0 Flowers")

        i = 0
        while i < 5:
            self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
            i += 1

    def handle_selection_change_rarity(self, event=None):
        selected_value = self.creation_str_vars[1].get()

        self.hero_proxy.rarity = int(selected_value)

        if self.created_hero is not None:
            star_var = "✰" * int(selected_value)
            self.unit_name.set(f"{self.hero_proxy.full_name}\n{star_var}")

            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

    def handle_selection_change_level(self, event=None):
        selected_value = self.creation_str_vars[14].get()

        self.hero_proxy.level = int(selected_value)

        if self.created_hero is not None:
            merge_str = ""
            if self.hero_proxy.merge > 0:
                merge_str = "+" + str(self.hero_proxy.merge)

            self.unit_stats.set(f"Lv. {selected_value}{merge_str}\n+0 Flowers")

            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

    def handle_selection_change_merge(self, event=None):
        selected_value = self.creation_str_vars[2].get()

        self.hero_proxy.merge = int(selected_value)

        if self.created_hero is not None:

            merge_str = ""
            if self.hero_proxy.merge > 0:
                merge_str = "+" + selected_value

            self.unit_stats.set(f"Lv. {self.hero_proxy.level}{merge_str}\n+{self.hero_proxy.dflowers} Flowers")

            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

    def handle_selection_change_asset(self, event=None):
        selected_value = self.creation_str_vars[3].get()

        stat_int = STATS[selected_value]

        # Set asc asset to new value if not present (asset same as asc_asset)
        if self.hero_proxy.asset == self.hero_proxy.asc_asset:
            self.hero_proxy.asc_asset = stat_int

        # Set new asset value
        self.hero_proxy.asset = stat_int

        # If this overlaps with the current flaw value
        if self.hero_proxy.flaw == self.hero_proxy.asset or self.hero_proxy.flaw == -1:
            # Move flaw to next possible stat
            self.hero_proxy.flaw = (STATS[selected_value] + 1) % 5

        if self.hero_proxy.asset == -1:
            self.hero_proxy.flaw = -1

        self.creation_str_vars[16].set(STAT_STR[self.hero_proxy.flaw])

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

    def handle_selection_change_flaw(self, event=None):
        selected_value = self.creation_str_vars[16].get()

        stat_int = STATS[selected_value]

        self.hero_proxy.flaw = stat_int

        if self.hero_proxy.asset == self.hero_proxy.flaw or self.hero_proxy.asset == -1:
            self.hero_proxy.asset = (stat_int + 1) % 5
            self.hero_proxy.asc_asset = (stat_int + 1) % 5

        if self.hero_proxy.flaw == -1:
            self.hero_proxy.asset = -1

        self.creation_str_vars[3].set(STAT_STR[self.hero_proxy.asset])

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

    def handle_selection_change_blessing(self, event=None):
        selected_value = self.creation_str_vars[4].get()

        if selected_value == "None":
            self.hero_proxy.blessing = None
        elif selected_value in BLESSINGS_DICT:
            self.hero_proxy.blessing = hero.Blessing((BLESSINGS_DICT[selected_value], 0, 0))

        self.hero_proxy.apply_proxy(self.created_hero)

    def handle_selection_change_allysupport(self, event=None):
        selected_value = self.creation_str_vars[18].get()

        if selected_value != "None":
            self.hero_proxy.a_support = selected_value
        else:
            self.hero_proxy.a_support = None

        self.hero_proxy.apply_proxy(self.created_hero)

    def handle_selection_change_summsupport(self, event=None):
        selected_value = self.creation_str_vars[5].get()

        if selected_value == "None":
            self.hero_proxy.s_support = 0
        if selected_value == "Rank C":
            self.hero_proxy.s_support = 1
        if selected_value == "Rank B":
            self.hero_proxy.s_support = 2
        if selected_value == "Rank A":
            self.hero_proxy.s_support = 3
        if selected_value == "Rank S":
            self.hero_proxy.s_support = 4

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

    def handle_selection_change_weapon(self, event=None):
        selected_value = self.creation_str_vars[7].get()

        # Set proxy value
        if selected_value != "None":
            self.hero_proxy.weapon = hero.makeWeapon(selected_value)
        else:
            self.hero_proxy.weapon = None

        self.hero_proxy.refine = ""

        if self.hero_proxy.weapon is not None:
            CreateToolTip(self.creation_labels[7], self.hero_proxy.weapon.desc)
        else:
            CreateToolTip(self.creation_labels[7], "")

        # Set valid refines for this given weapon
        refines_arr = _get_valid_refines(selected_value)
        self.creation_str_vars[8].set("None")
        self.creation_comboboxes[8]['values'] = refines_arr

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

    def handle_selection_change_refine(self, event=None):
        selected_value = self.creation_str_vars[8].get()

        if selected_value != "None":
            self.hero_proxy.refine = selected_value
        else:
            self.hero_proxy.refine = ""

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

        if self.hero_proxy.weapon is not None:
            CreateToolTip(self.creation_labels[7], self.hero_proxy.weapon.desc)
        else:
            CreateToolTip(self.creation_labels[7], "")

    def handle_selection_change_assist(self, event=None):
        selected_value = self.creation_str_vars[9].get()

        # Set proxy value
        if selected_value != "None":
            self.hero_proxy.assist = hero.makeAssist(selected_value)
        else:
            self.hero_proxy.assist = None

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

        if self.hero_proxy.assist is not None:
            CreateToolTip(self.creation_labels[9], self.hero_proxy.assist.desc)
        else:
            CreateToolTip(self.creation_labels[9], "")

    def handle_selection_change_special(self, event=None):
        selected_value = self.creation_str_vars[10].get()

        # Set proxy value
        if selected_value != "None":
            self.hero_proxy.special = hero.makeSpecial(selected_value)
        else:
            self.hero_proxy.special = None

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

        if self.hero_proxy.special is not None:
            CreateToolTip(self.creation_labels[10], self.hero_proxy.special.desc)
        else:
            CreateToolTip(self.creation_labels[10], "")

    def handle_selection_change_askill(self, event=None):
        selected_value = self.creation_str_vars[20].get()

        # Set proxy value
        if selected_value != "None":
            self.hero_proxy.askill = hero.makeSkill(selected_value)
        else:
            self.hero_proxy.askill = None

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

        if self.hero_proxy.askill is not None:
            CreateToolTip(self.creation_labels[20], self.hero_proxy.askill.desc)
        else:
            CreateToolTip(self.creation_labels[20], "")

    def handle_selection_change_bskill(self, event=None):
        selected_value = self.creation_str_vars[21].get()

        # Set proxy value
        if selected_value != "None":
            self.hero_proxy.bskill = hero.makeSkill(selected_value)
        else:
            self.hero_proxy.bskill = None

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

        if self.hero_proxy.bskill is not None:
            CreateToolTip(self.creation_labels[21], self.hero_proxy.bskill.desc)
        else:
            CreateToolTip(self.creation_labels[21], "")

    def handle_selection_change_cskill(self, event=None):
        selected_value = self.creation_str_vars[22].get()

        # Set proxy value
        if selected_value != "None":
            self.hero_proxy.cskill = hero.makeSkill(selected_value)
        else:
            self.hero_proxy.cskill = None

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

        if self.hero_proxy.cskill is not None:
            CreateToolTip(self.creation_labels[22], self.hero_proxy.cskill.desc)
        else:
            CreateToolTip(self.creation_labels[22], "")

    def handle_selection_change_sseal(self, event=None):
        selected_value = self.creation_str_vars[23].get()

        if selected_value != "None":
            self.hero_proxy.sSeal = hero.makeSeal(selected_value)
        else:
            self.hero_proxy.sSeal = None

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

        if self.hero_proxy.sSeal is not None:
            CreateToolTip(self.creation_labels[23], self.hero_proxy.sSeal.desc)
        else:
            CreateToolTip(self.creation_labels[23], "")

    def create_edit_popup(self):
        if self.creation_menu:
            return

        self.create_creation_popup()

        index = self.unit_buttons.index(self.selected_button)
        my_units = pd.read_csv("my_units.csv", encoding='cp1252')

        row = my_units.loc[index]

        # Internal name from sheet
        int_name = row["IntName"]
        self.created_hero = hero.makeHero(int_name)

        # Name
        title_name = self.created_hero.name + ": " + self.created_hero.epithet
        self.creation_comboboxes[0].set(title_name)
        self.handle_selection_change_name()

        # Rarity
        rarity = row["Rarity"]
        self.creation_comboboxes[1].set(rarity)
        self.handle_selection_change_rarity()

        # Level
        level = row["Level"]
        self.creation_comboboxes[14].set(level)
        self.handle_selection_change_level()

        # Merges
        merges = row["Merges"]
        self.creation_comboboxes[2].set(merges)
        self.handle_selection_change_merge()

        # Blessings
        blessing = row["Blessing"]
        if pd.isnull(blessing):
            if self.creation_str_vars[4].get() == "None":
                self.creation_comboboxes[4].set("None")
        else:
            self.creation_comboboxes[4].set(hero.BLESSING_NAMES[int(blessing)].capitalize())

        self.handle_selection_change_blessing()

        # Summ Support
        s_support = row["SSupport"]

        if pd.isnull(s_support):
            s_support = 0

        if s_support == 1:
            s_str = "Rank C"
        elif s_support == 2:
            s_str = "Rank B"
        elif s_support == 3:
            s_str = "Rank A"
        elif s_support == 4:
            s_str = "Rank S"
        else:
            s_str = "None"

        self.creation_comboboxes[5].set(s_str)
        self.handle_selection_change_summsupport()

        # Asset & Flaw
        asset = STAT_STR[row["Asset"]]
        flaw = STAT_STR[row["Flaw"]]

        # Neutral
        if asset == flaw:
            self.creation_comboboxes[3].set("None")
            self.handle_selection_change_asset()
        # Not Neutral
        else:
            self.creation_comboboxes[3].set(asset)
            self.handle_selection_change_asset()

            self.creation_comboboxes[16].set(flaw)
            self.handle_selection_change_flaw()

        # Weapon
        weapon = row["Weapon"]

        if pd.isnull(weapon):
            weapon = "None"

        refine_substrings = ["Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz"]
        if weapon[-3:] in refine_substrings:
            weapon = weapon[:-3]

        self.creation_comboboxes[7].set(weapon)
        self.handle_selection_change_weapon()

        # Refine
        refine = row["Weapon"]

        if pd.isnull(refine):
            refine = "None"

        if refine[-3:] in refine_substrings:
            refine = refine[-3:]
        else:
            refine = "None"

        self.creation_comboboxes[8].set(refine)
        self.handle_selection_change_refine()

        # Assist
        assist = row["Assist"]

        if pd.isnull(assist):
            assist = "None"

        self.creation_comboboxes[9].set(assist)
        self.handle_selection_change_assist()

        # Special
        special = row["Special"]

        if pd.isnull(special):
            special = "None"

        self.creation_comboboxes[10].set(special)
        self.handle_selection_change_special()

        # Support Ally
        loaded_file = open('supports.pkl', 'rb')
        db = pickle.load(loaded_file)

        ally_str = "None"

        for pairing in db:
            if int_name in pairing:
                ally_support = pairing[pairing.index(int_name) - 1]
                ally_hero = hero.makeHero(ally_support) if ally_support is not None else None
                ally_str = ally_hero.name + ": " + ally_hero.epithet if ally_hero is not None else "None"

        self.creation_comboboxes[18].set(ally_str)
        self.handle_selection_change_allysupport()

        # A Skill
        askill = row["ASkill"]

        if pd.isnull(askill):
            askill = "None"

        self.creation_comboboxes[20].set(askill)
        self.handle_selection_change_askill()

        # B Skill
        bskill = row["BSkill"]

        if pd.isnull(bskill):
            bskill = "None"

        self.creation_comboboxes[21].set(bskill)
        self.handle_selection_change_bskill()

        # C Skill
        cskill = row["CSkill"]

        if pd.isnull(cskill):
            cskill = "None"

        self.creation_comboboxes[22].set(cskill)
        self.handle_selection_change_cskill()

        # Sacred Seal
        sseal = row["SSeal"]

        if pd.isnull(sseal):
            sseal = "None"

        self.creation_comboboxes[23].set(sseal)
        self.handle_selection_change_sseal()

        # Build Name
        self.build_name.set(row["Build Name"])

        self.creation_make_button.config(text="Save", command=partial(self.unit_edit_confirm, index))

    def create_edit_popup_from_unit(self, unit):
        if self.creation_menu:
            return

        self.create_creation_popup()

        self.created_hero = deepcopy(unit)

        # Name
        title_name = self.created_hero.name + ": " + self.created_hero.epithet
        self.creation_comboboxes[0].set(title_name)
        self.handle_selection_change_name()

        # Rarity
        rarity = unit.rarity
        self.creation_comboboxes[1].set(rarity)
        self.handle_selection_change_rarity()

        # Level
        level = unit.level
        self.creation_comboboxes[14].set(level)
        self.handle_selection_change_level()

        # Merges
        merges = unit.merges
        self.creation_comboboxes[2].set(merges)
        self.handle_selection_change_merge()

        # Blessings
        blessing = unit.blessing
        if blessing is None:
            if self.creation_str_vars[4].get() == "None":
                self.creation_comboboxes[4].set("None")
        else:
            if blessing.boostType == 0:
                self.creation_comboboxes[4].set(hero.BLESSING_NAMES[int(blessing.element)].capitalize())
            else:
                self.creation_comboboxes[4].set(unit.blessing.toString())

        self.handle_selection_change_blessing()

        # Summ Support
        s_support = unit.summonerSupport

        if s_support == 1:
            s_str = "Rank C"
        elif s_support == 2:
            s_str = "Rank B"
        elif s_support == 3:
            s_str = "Rank A"
        elif s_support == 4:
            s_str = "Rank S"
        else:
            s_str = "None"

        self.creation_comboboxes[5].set(s_str)
        self.handle_selection_change_summsupport()

        # Asset & Flaw
        asset = STAT_STR[unit.asset]
        flaw = STAT_STR[unit.flaw]

        # Neutral
        if asset == flaw:
            self.creation_comboboxes[3].set("None")
            self.handle_selection_change_asset()
        # Not Neutral
        else:
            self.creation_comboboxes[3].set(asset)
            self.handle_selection_change_asset()

            self.creation_comboboxes[16].set(flaw)
            self.handle_selection_change_flaw()

        weapon = unit.weapon

        if weapon is None:
            weapon = "None"
        else:
            weapon = unit.weapon.intName

        refine_substrings = ["Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz"]
        if weapon[-3:] in refine_substrings:
            weapon = weapon[:-3]

        self.creation_comboboxes[7].set(weapon)
        self.handle_selection_change_weapon()

        # Refine
        refine = unit.weapon

        if refine is None:
            refine = "None"
        else:
            refine = unit.weapon.intName

        if refine[-3:] in refine_substrings:
            refine = refine[-3:]
        else:
            refine = "None"

        self.creation_comboboxes[8].set(refine)
        self.handle_selection_change_refine()

        # Assist
        assist = unit.assist

        if assist is None:
            assist = "None"
        else:
            assist = assist.name

        self.creation_comboboxes[9].set(assist)
        self.handle_selection_change_assist()

        # Special
        special = unit.special

        if special is None:
            special = "None"
        else:
            special = special.name

        self.creation_comboboxes[10].set(special)
        self.handle_selection_change_special()

        # A Skill
        askill = unit.askill

        if askill is None:
            askill = "None"
        else:
            askill = askill.name

        self.creation_comboboxes[20].set(askill)
        self.handle_selection_change_askill()

        # B Skill
        bskill = unit.bskill

        if bskill is None:
            bskill = "None"
        else:
            bskill = bskill.name

        self.creation_comboboxes[21].set(bskill)
        self.handle_selection_change_bskill()

        # C Skill
        cskill = unit.cskill

        if pd.isnull(cskill):
            cskill = "None"
        else:
            cskill = cskill.name

        self.creation_comboboxes[22].set(cskill)
        self.handle_selection_change_cskill()

        # Sacred Seal
        sseal = unit.sSeal

        if sseal is None:
            sseal = "None"
        else:
            sseal = sseal.name

        self.creation_comboboxes[23].set(sseal)
        self.handle_selection_change_sseal()

    def button_deletion_confirm(self):
        if self.confirm_deletion_popup:
            self.confirm_deletion_popup.destroy()
            self.confirm_deletion_popup = None

            index = self.unit_buttons.index(self.selected_button)

            data = pd.read_csv("my_units.csv", encoding='cp1252')
            data = data.drop(index)
            data.to_csv("my_units.csv", index=False, encoding='cp1252')

            self.selected_button.forget()

            self.selected_button = None

            self.edit_button.config(state="normal")
            self.delete_button.config(state="normal")

            if self.creation_menu:
                self.unit_creation_cancel()

    def button_deletion_cancel(self):
        if self.confirm_deletion_popup:
            self.confirm_deletion_popup.destroy()
            self.confirm_deletion_popup = None

    def unit_creation_cancel(self):
        if self.creation_menu:
            self.creation_menu.destroy()
            self.creation_menu = None

    def unit_edit_confirm(self, index):
        self.unit_status.update_from_obj(self.created_hero)

        hero_to_add = self.created_hero
        cur_build_name = self.build_name.get()

        if self.creation_str_vars[0].get() != "" and cur_build_name != "":

            name = hero_to_add.intName
            weapon = hero_to_add.weapon.intName if hero_to_add.weapon is not None else None
            assist = hero_to_add.assist.name if hero_to_add.assist is not None else None
            special = hero_to_add.special.name if hero_to_add.special is not None else None
            askill = hero_to_add.askill.name if hero_to_add.askill is not None else None
            bskill = hero_to_add.bskill.name if hero_to_add.bskill is not None else None
            cskill = hero_to_add.cskill.name if hero_to_add.cskill is not None else None
            sSeal = hero_to_add.sSeal.name if hero_to_add.sSeal is not None else None
            xskill = hero_to_add.xskill.name if hero_to_add.xskill is not None else None

            level = hero_to_add.level
            merges = hero_to_add.merges
            rarity = hero_to_add.rarity

            asset = hero_to_add.asset
            flaw = hero_to_add.flaw
            asc = hero_to_add.asc_asset

            blessing = hero_to_add.blessing.element if (hero_to_add.blessing is not None and hero_to_add.blessing.boostType == 0) else None

            sSupport = int(hero_to_add.summonerSupport)
            aSupport = None

            dflowers = 0
            resp = False
            emblem = None
            emblem_merges = 0
            cheats = False

            data = [name, cur_build_name,
                    weapon, assist, special, askill, bskill, cskill, sSeal, xskill,
                    level, merges, rarity, asset, flaw, asc, sSupport, aSupport, blessing, dflowers, resp, emblem, emblem_merges, cheats]

            my_units_file = "my_units.csv"
            names = pd.read_csv(my_units_file, encoding='cp1252')['Build Name'].tolist()

            # Ensure build name is unique, or name is unchanged
            if cur_build_name not in names or names[index] == cur_build_name:

                try:
                    my_units_file = "my_units.csv"

                    with open(my_units_file, 'r', newline='', encoding="cp1252") as file:
                        f_reader = reader(file)
                        read_data = list(f_reader)

                    read_data[index + 1] = data

                    with open(my_units_file, mode="w", newline='', encoding="cp1252") as file:
                        f_writer = writer(file)
                        f_writer.writerows(read_data)

                    # Go back to unit selection screen
                    self.unit_creation_cancel()
                    self.refresh_buttons(False)

                    ally_supports = open('supports.pkl', 'rb')
                    db = pickle.load(ally_supports)

                    new_db = []

                    for pairing in db:
                        if hero_to_add.intName not in pairing and hero_to_add.allySupport not in pairing:
                            new_db.append(pairing)

                    if hero_to_add.allySupport is not None:
                        new_db.append((hero_to_add.intName, hero_to_add.allySupport))

                    open("supports.pkl", "w").close()

                    db_file = open("supports.pkl", "ab")
                    pickle.dump(new_db, db_file)
                    db_file.close()

                except PermissionError:
                    print(f"Error: Permission denied when writing to file. Please close {my_units_file} and try again.")

            else:
                self.error_text.config(fg='#d60408', text="Error: Build Name Already Exists")
        else:
            self.error_text.config(fg='#d60408', text='Error: No Unit Selected or Build Name Empty')

class HoverButton(tk.Button):
    def __init__(self, master, **kw):
        tk.Button.__init__(self,master=master, **kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self['background'] = self['activebackground']

    def on_leave(self, event):
        self['background'] = self.defaultBackground

class _DragPoint:
    def __init__(self, tile_num, modifiable, side):
        self.hero = None
        self.tile = tile_num
        self.modifiable = modifiable
        self.side = side

def make_hero_from_pd_row(row_data, side):
    unit = hero.makeHero(row_data["IntName"])

    if side == ENEMY:
        unit.allySupport = None

    unit.side = side

    unit.set_rarity(row_data["Rarity"])
    unit.set_IVs(row_data["Asset"], row_data["Flaw"], row_data["Ascended"])
    unit.set_merges(row_data["Merges"])
    unit.set_dragonflowers(row_data["Dragonflowers"])

    unit.set_level(row_data["Level"])

    if not unit.blessing and not pd.isnull(row_data["Blessing"]):
        unit.blessing = hero.Blessing((int(row_data["Blessing"]), 0, 0))

    unit.summonerSupport = row_data["SSupport"]

    if pd.isnull(row_data["SSupport"]):
        unit.summonerSupport = 0

    unit.set_visible_stats()

    if not pd.isnull(row_data["Weapon"]):
        curWpn = hero.makeWeapon(row_data["Weapon"])
        unit.set_skill(curWpn, hero.WEAPON)

    if not pd.isnull(row_data["Assist"]):
        curAssist = hero.makeAssist(row_data["Assist"])
        unit.set_skill(curAssist, hero.ASSIST)

    if not pd.isnull(row_data["Special"]):
        curSpecial = hero.makeSpecial(row_data["Special"])
        unit.set_skill(curSpecial, hero.SPECIAL)

    if not pd.isnull(row_data["ASkill"]):
        curASkill = hero.makeSkill(row_data["ASkill"])
        unit.set_skill(curASkill, hero.ASKILL)

    if not pd.isnull(row_data["BSkill"]):
        curBSkill = hero.makeSkill(row_data["BSkill"])
        unit.set_skill(curBSkill, hero.BSKILL)

    if not pd.isnull(row_data["CSkill"]):
        curCSkill = hero.makeSkill(row_data["CSkill"])
        unit.set_skill(curCSkill, hero.CSKILL)

    if not pd.isnull(row_data["SSeal"]):
        curSSeal = hero.makeSeal(row_data["SSeal"])
        unit.set_skill(curSSeal, hero.SSEAL)

    if not pd.isnull(row_data["XSkill"]):
        curXSkill = hero.makeSkill(row_data["XSkill"])
        unit.set_skill(curXSkill, hero.XSKILL)

    return unit


status_pic = Image.open("CombatSprites/" + "Status" + ".png")
def make_weapon_sprite(wpn_num):
    image = status_pic.crop((56 * wpn_num, 206, 56 * (wpn_num + 1), 260))
    image = image.resize((25,25), Image.LANCZOS)

    return image

# some arrow images are cropped unusually
# this snaps them back to correct place
def _get_arrow_offsets(arrow_num):
    if arrow_num == 0: return 16, 0
    if arrow_num == 1: return 16, 1
    if arrow_num == 3: return -1, 0
    if arrow_num == 4: return 16, 2
    if arrow_num == 5: return 16, 0
    if arrow_num == 6: return 0, 2
    if arrow_num == 7: return 0, 1
    if arrow_num == 9: return 0, 1
    if arrow_num == 10: return 0, 2
    if arrow_num == 11: return 0, 2

    return 0, 0

# Saves the state of a singular unit
class UnitState:
    def __init__(self, unit: Hero):
        self.cur_hp = unit.HPcur
        self.cur_sp = unit.specialCount

        self.cur_position = unit.tile.tileNum

        self.cur_buffs = unit.buffs[:]
        self.cur_debuffs = unit.debuffs[:]
        self.cur_status_pos = unit.statusPos[:]
        self.cur_status_neg = unit.statusNeg[:]

        self.sp_galeforce = unit.special_galeforce_triggered
        self.nsp_galeforce = unit.nonspecial_galeforce_triggered

        self.canto = unit.canto_ready

        self.num_combats = unit.unitCombatInitiates
        self.num_assists_self = unit.assistTargetedSelf
        self.num_assists_other = unit.assistTargetedOther

# One state of the game
class MapState:
    def __init__(self, unit_states, struct_states, units_to_move, turn_num):
        self.unit_states = unit_states
        self.struct_states = struct_states
        self.units_to_move = units_to_move

        self.turn_num = turn_num

    def print_mapstate(self):
        print("Unit States:")
        for unit in self.unit_states.keys():
            print(unit.intName)
            print(f" Current HP: {self.unit_states[unit].cur_hp}")
            print(f" Special Count: {self.unit_states[unit].cur_sp}")
            print(f" Tile Position: {self.unit_states[unit].cur_position}")
            print(f" Buffs: {self.unit_states[unit].cur_buffs}")
            print(f" Debuffs: {self.unit_states[unit].cur_debuffs}")
            print(f" Positive Statuses: {self.unit_states[unit].cur_status_pos}")
            print(f" Negative Statuses: {self.unit_states[unit].cur_status_neg}")
            print(f" Nonspecial Galeforce Triggered: {self.unit_states[unit].nsp_galeforce}")
            print(f" Special Galeforce Triggered: {self.unit_states[unit].sp_galeforce}")
            print(f" Canto Usable: {self.unit_states[unit].canto}")

        print("\nStructure States:")
        print(self.struct_states)

        print("\nUnits to Move:")
        for unit in self.units_to_move:
            print(unit.intName)

        print("\nTurn Num: " + str(self.turn_num))

def create_mapstate(p_units, e_units, c_map, units_to_move, turn_num):
    unit_states = {}

    for unit in p_units + e_units:
        cur_unit_state = UnitState(unit)
        unit_states[unit] = cur_unit_state

    struct_states = {}

    for tile in c_map.tiles:
        if tile.structure_on is not None:
            cur_struct = tile.structure_on

            struct_states[cur_struct] = cur_struct.health

    return MapState(unit_states, struct_states, units_to_move[:], turn_num)

class GameplayCanvas(tk.Canvas):
    def __init__(self, master, hero_listing):
        self.TILE_SIZE = 90

        self.GAMEPLAY_LENGTH = self.TILE_SIZE * 6
        self.GAMEPLAY_WIDTH = self.TILE_SIZE * 8

        tk.Canvas.__init__(self, master=master, width=self.GAMEPLAY_LENGTH, height=self.GAMEPLAY_WIDTH, bg="#282424", highlightthickness=0)

        self.running = False

        self.map = Map(0)

        self.create_text(self.GAMEPLAY_LENGTH / 2, self.GAMEPLAY_WIDTH / 2, text="No map selected.", font="Helvetica 20", fill="white")

        # Gameplay variables
        self.turn_info = []
        self.units_to_move = []
        self.combat_fields = []

        self.drag_data = None
        self.distance = 0
        self.spaces_allowed = 0
        self.chosen_action = 0

        # Currently placed movement spaces
        self.tile_sprites = []

        self.animation = False # true if an animation is currently playing, false otherwise
        self.canto = None # set to the current unit performing a canto action
        self.swap_mode = False # true if currently in swap mode, false otherwise

        self.all_units = [[], []]
        self.current_units = [[], []]

        self.unit_photos = [[], []]
        self.unit_sprites = [[], []]

        self.unit_photos_gs = [[], []]
        self.unit_sprites_gs = [[], []]

        self.unit_photos_trans = [[], []]
        self.unit_sprites_trans = [[], []]

        self.unit_photos_gs_trans = [[], []]
        self.unit_sprites_gs_trans = [[], []]

        self.unit_weapon_icon_photos = [[], []]
        self.unit_weapon_icon_sprites = [[], []]

        self.unit_sp_count_labels = [[], []]
        self.unit_hp_count_labels = [[], []]

        self.unit_hp_bars_fg = [[], []]
        self.unit_hp_bars_bg = [[], []]

        self.starting_tile_photos = []

        self.unit_tags = [[], []]

        self.game_mode = hero.GameMode.Story

        # Preparation variables
        self.unit_drag_points = {}

        # Store PhotoImages for later use to not be garbage collected.
        self.liquid = None
        self.terrain = None
        self.offense_piece = None

        self.wall_photos = []
        self.move_tile_photos = []
        self.move_arrow_photos = []
        self.weapon_type_photos = []

        # Arrays of placed images on the Canvas
        self.wall_sprites = []

        # Other widgets to talk to
        self.button_frame = None
        self.hero_listing = hero_listing
        self.unit_status = None
        self.extras = None

        # Set default sprites, constant for each map

        # Movement tiles
        blue_tile = Image.open("CombatSprites/" + "tileblue" + ".png").resize((self.TILE_SIZE, self.TILE_SIZE), Image.LANCZOS)
        light_blue_tile = Image.open("CombatSprites/" + "tilelightblue" + ".png")
        red_tile = Image.open("CombatSprites/" + "tilered" + ".png")
        pale_red_tile = Image.open("CombatSprites/" + "tilepalered" + ".png")
        green_tile = Image.open("CombatSprites/" + "tilegreen" + ".png")
        pale_green_tile = Image.open("CombatSprites/" + "tilepalegreen" + ".png")

        self.move_tile_photos.append(ImageTk.PhotoImage(blue_tile))
        self.move_tile_photos.append(ImageTk.PhotoImage(light_blue_tile))
        self.move_tile_photos.append(ImageTk.PhotoImage(red_tile))
        self.move_tile_photos.append(ImageTk.PhotoImage(pale_red_tile))
        self.move_tile_photos.append(ImageTk.PhotoImage(green_tile))
        self.move_tile_photos.append(ImageTk.PhotoImage(pale_green_tile))

        # Arrows
        arrows = Image.open("CombatSprites/" + "Map" + ".png")
        self.move_arrow_photos.clear()

        regions = [
            (182, 0, 240, 90),  # start_north
            (182, 91, 240, 180),  # start_south
            (256, 0, 346, 90),  # start_east
            (255, 90, 346, 180),  # start_west
            (182, 182, 240, 270),  # end_north
            (182, 271, 240, 345),  # end_south
            (256, 182, 346, 270),  # end_east
            (256, 271, 346, 345),  # end_west
            (346, 0, 436, 90),  # line_vert
            (346, 91, 436, 180),  # line_hori
            (346, 182, 436, 270),  # bend_NE
            (436, 182, 506, 270),  # bend_ES
            (346, 270, 436, 345),  # bend_SE
            (436, 270, 506, 345),  # bend_EN
            (436, 0, 505, 90)  # move_star
        ]

        for region in regions:
            cropped_image = arrows.crop(region)
            self.move_arrow_photos.append(ImageTk.PhotoImage(cropped_image))

        # Weapon Icons

        self.weapon_type_photos.clear()
        status_pic = Image.open("CombatSprites/" + "Status" + ".png")

        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260)).resize((25, 25), Image.LANCZOS)
            self.weapon_type_photos.append(ImageTk.PhotoImage(cur_icon))
            i += 1

        # AOE Special icon
        aoe_special_icon_image = status_pic.crop((1047, 419, 1200, 560)).resize((90, 90), Image.LANCZOS)
        self.aoe_icon = ImageTk.PhotoImage(aoe_special_icon_image)
        self.active_aoe_icons = []

        self.canto_tile_imgs = []

        self.bind("<Button-1>", self.on_click)
        self.bind("<Double-Button-1>", self.on_double_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Button-3>", self.on_right_click)

    def start_simulation(self):
        #print("We're going back in time to the first Thanksgiving to get turkeys off the menu.")

        if self.animation: return

        self.turn_info[0] = 1 # turn num
        self.turn_info[1] = PLAYER # side

        self.drag_data = None
        self.distance = 0
        self.spaces_allowed = 0
        self.chosen_action = 0

        if self.hero_listing.confirm_deletion_popup:
            self.hero_listing.confirm_deletion_popup.destroy()
            self.hero_listing.confirm_deletion_popup = None

        if self.hero_listing.creation_menu:
            self.hero_listing.creation_menu.destroy()
            self.hero_listing.creation_menu = None

        self.unit_status.clear()

        for tile in self.canto_tile_imgs:
            self.delete(tile)
        self.canto_tile_imgs.clear()

        # If currently running, stop
        if self.running:

            self.button_frame.start_button.config(text="Start\nSim", bg="dark green")

            self.button_frame.end_turn_button.config(state="disabled")
            self.button_frame.swap_spaces_button.config(state="disabled", text="Swap\nSpaces", bg="#75f216")
            self.button_frame.undo_button.config(state="disabled")

            self.map_states.clear()

            self.running = False
            self.swap_mode = False

            for tile in self.starting_tile_photos:
                self.itemconfigure(tile, state='normal')

            self.button_frame.state_info.config(text="EDITING")
            self.button_frame.help_info.config(text=help_text, font=("Helvetica", 9), fg=self.button_frame.text_color)

            self.button_frame.running_elemental_season_info.grid_forget()
            self.button_frame.running_aether_season_info.grid_forget()

            self.button_frame.elemental_season_combobox.grid(row=1, column=0)
            self.button_frame.aether_season_combobox.grid(row=1, column=1)

            for button in self.extras.bonus_units_buttons:
                button.config(state="normal")

            self.extras.forecasts_button.config(state="disabled")
            self.extras.show_player_team()

            for tile in self.map.tiles:
                tile.hero_on = None

            self.refresh_units_prep()

            self.current_units[PLAYER].clear()
            self.current_units[ENEMY].clear()

            self.units_to_move.clear()

            for tile in self.map.tiles:
                if tile.structure_on:
                    tile.structure_on.health = tile.structure_on.max_health

            self.refresh_walls()

            return

        # Else, start simulation

        # Change button's apperance to Stop Sim
        self.button_frame.start_button.config(text="Stop\nSim", bg="firebrick3")

        # Allow End Turn and Swap Spaces buttons to be used
        self.button_frame.end_turn_button.config(state="normal")
        self.button_frame.swap_spaces_button.config(state="normal")

        self.running = True

        # Switch to forecasts tab
        self.extras.show_forecasts()
        self.extras.forecasts_button.config(state="normal")

        # Hide tiles underneath each unit
        for tile in self.starting_tile_photos:
            self.itemconfigure(tile, state='hidden')

        # Update turn info
        self.button_frame.state_info.config(text="RUNNING")
        self.button_frame.help_info.config(text="Turn 1: Player Phase", font=("Helvetica", 16), fg="DodgerBlue2")

        self.button_frame.elemental_season_combobox.grid_forget()
        self.button_frame.aether_season_combobox.grid_forget()

        self.button_frame.running_elemental_season_info.grid(row=1, column=0)
        self.button_frame.running_aether_season_info.grid(row=1, column=1)

        # Lock each bonus unit button
        for button in self.extras.bonus_units_buttons:
            button.config(state="disabled")

        # Drag Points
        player_drag_points = [drag_point for drag_point in self.unit_drag_points.values() if drag_point.side == PLAYER]
        enemy_drag_points = [drag_point for drag_point in self.unit_drag_points.values() if drag_point.side == ENEMY]

        bonus_units = self.extras.bonus_units
        result_bonus_units = []

        i = 0
        while i < len(player_drag_points):
            if player_drag_points[i].hero:
                result_bonus_units.append(bonus_units[i])
            i += 1

        season = []

        elem_str = self.button_frame.elemental_season_combobox.get()
        aether_str = self.button_frame.aether_season_combobox.get()

        for key in BLESSINGS_DICT:
            if key in elem_str + aether_str:
                season.append(BLESSINGS_DICT[key])

        _apply_battle_stats(self.all_units[PLAYER], result_bonus_units, self.game_mode, season)
        _apply_battle_stats(self.all_units[ENEMY], [False] * len(self.all_units[ENEMY]), self.game_mode, season)

        i = 0
        while i < len(self.all_units[PLAYER]):
            tile_int = player_drag_points[i].tile

            self.map.tiles[tile_int].hero_on = self.all_units[PLAYER][i]
            self.all_units[PLAYER][i].tile = self.map.tiles[tile_int]

            self.move_visuals_to_tile(PLAYER, i, tile_int)
            self.refresh_unit_visuals(PLAYER, i)

            self.current_units[PLAYER].append(self.all_units[PLAYER][i])

            i += 1

        i = 0
        while i < len(self.all_units[ENEMY]):
            tile_int = enemy_drag_points[i].tile

            self.map.tiles[tile_int].hero_on = self.all_units[ENEMY][i]
            self.all_units[ENEMY][i].tile = self.map.tiles[tile_int]

            self.move_visuals_to_tile(ENEMY, i, tile_int)
            self.refresh_unit_visuals(ENEMY, i)

            self.current_units[ENEMY].append(self.all_units[ENEMY][i])

            i += 1

        for unit in self.current_units[PLAYER]:
            self.units_to_move.append(unit)

        # Create all combat fields
        self.combat_fields = []
        self.combat_fields = feh.create_combat_fields(self.current_units[PLAYER], self.current_units[ENEMY])

        self.initial_mapstate = create_mapstate(self.all_units[PLAYER], self.all_units[ENEMY], self.map, self.units_to_move, self.turn_info[0])

        print("---- PLAYER PHASE ----")

        # Start of turn skills
        damage, heals = feh.start_of_turn(self.current_units[PLAYER], self.current_units[ENEMY], 1)

        for unit in self.current_units[PLAYER] + self.current_units[ENEMY]:
            heal_amount = 0
            damage_amount = 0
            if unit in heals:
                heal_amount = heals[unit]

            if unit in damage:
                damage_amount = damage[unit]

            if damage_amount >= heal_amount and (damage_amount > 0 or heal_amount > 0):
                unit.HPcur = max(1, unit.HPcur + (heal_amount - damage_amount))
                self.animate_damage_popup(abs(heal_amount - damage_amount), unit.tile.tileNum)
            elif damage_amount < heal_amount and (damage_amount > 0 or heal_amount > 0):
                unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + (heal_amount - damage_amount))
                self.animate_heal_popup(abs(heal_amount - damage_amount), unit.tile.tileNum)

            self.refresh_unit_visuals(unit.side, self.all_units[unit.side].index(unit))

            unit.unitCombatInitiates = 0
            unit.assistTargetedSelf = 0
            unit.assistTargetedOther = 0

        mapstate = create_mapstate(self.all_units[PLAYER], self.all_units[ENEMY], self.map, self.units_to_move, self.turn_info[0])
        self.map_states.append(mapstate)

    def end_turn_button(self):
        if self.animation: return

        self.canto = None

        for tile in self.canto_tile_imgs:
            self.delete(tile)
        self.canto_tile_imgs.clear()

        self.next_phase()
        return

    def undo_action_button(self):
        if self.animation: return

        if len(self.map_states) > 1:
            if not self.canto:
                self.map_states.pop()
            self.apply_mapstate(self.map_states[-1])
        else:
            self.apply_mapstate(self.map_states[0])

        if len(self.map_states) == 1:
            self.button_frame.swap_spaces_button.config(state="normal")
            self.button_frame.undo_button.config(state="disabled")

    def toggle_swap(self):
        if self.animation: return

        self.swap_mode = not self.swap_mode

        if self.swap_mode:
            self.button_frame.swap_spaces_button.config(text="Swap\nDone", bg="green3")

            self.apply_mapstate(self.initial_mapstate)

            for unit in self.all_units[PLAYER]:
                self.update_unit_graphics(unit)

            for tile in self.unit_drag_points.keys():
                if self.unit_drag_points[tile].side == PLAYER:
                    drawnTile = self.create_image(0, 0, image=self.move_tile_photos[4])
                    self.canto_tile_imgs.append(drawnTile)
                    self.move_to_tile(drawnTile, tile)

                    if self.map.tiles[tile].hero_on:
                        self.tag_lower(drawnTile, self.unit_sprites[PLAYER][self.all_units[PLAYER].index(self.map.tiles[tile].hero_on)])

        else:
            self.button_frame.swap_spaces_button.config(text="Swap\nSpaces", bg="#75f216")

            self.unit_status.clear()

            for tile in self.canto_tile_imgs:
                self.delete(tile)
            self.canto_tile_imgs.clear()

            self.initial_mapstate = create_mapstate(self.all_units[PLAYER], self.all_units[ENEMY], self.map, self.units_to_move, self.turn_info[0])

            print("---- PLAYER PHASE ----")
            damage, heals = feh.start_of_turn(self.current_units[PLAYER], self.current_units[ENEMY], 1)

            for unit in self.current_units[PLAYER] + self.current_units[ENEMY]:
                heal_amount = 0
                damage_amount = 0
                if unit in heals:
                    heal_amount = heals[unit]

                if unit in damage:
                    damage_amount = damage[unit]

                if damage_amount >= heal_amount and (damage_amount > 0 or heal_amount > 0):
                    unit.HPcur = max(1, unit.HPcur + (heal_amount - damage_amount))
                    self.animate_damage_popup(abs(heal_amount - damage_amount), unit.tile.tileNum)
                elif damage_amount < heal_amount and (damage_amount > 0 or heal_amount > 0):
                    unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + (heal_amount - damage_amount))
                    self.animate_heal_popup(abs(heal_amount - damage_amount), unit.tile.tileNum)

                self.set_hp_visual(unit, unit.HPcur)

                unit.unitCombatInitiates = 0
                unit.assistTargetedOther = 0
                unit.assistTargetedSelf = 0

            i = 0
            while i < len(self.current_units[PLAYER]):
                if self.current_units[PLAYER][i].specialCount != -1:
                    self.itemconfig(self.unit_sp_count_labels[PLAYER][i], text=self.current_units[PLAYER][i].specialCount)

                self.current_units[PLAYER][i].canto_ready = True

                i += 1

            i = 0
            while i < len(self.current_units[ENEMY]):
                if self.current_units[ENEMY][i].specialCount != -1:
                    self.itemconfig(self.unit_sp_count_labels[ENEMY][i], text=self.current_units[ENEMY][i].specialCount)
                i += 1

            self.map_states.clear()
            self.map_states.append(create_mapstate(self.all_units[PLAYER], self.all_units[ENEMY], self.map, self.units_to_move, self.turn_info[0]))

    def apply_mapstate(self, mapstate):
        self.canto = None

        for tile in self.canto_tile_imgs:
            self.delete(tile)
        self.canto_tile_imgs.clear()

        self.unit_status.clear()

        # Set turn number
        turn_to_set = mapstate.turn_num
        phase_to_set = mapstate.units_to_move[0].side

        self.turn_info[0] = turn_to_set
        self.turn_info[1] = phase_to_set

        # Update phase labels
        if self.turn_info[1] == PLAYER:
            self.button_frame.help_info.config(text="Turn " + str(self.turn_info[0]) + ": Player Phase", font=("Helvetica", 16), fg="DodgerBlue2")
        else:
            self.button_frame.help_info.config(text="Turn " + str(self.turn_info[0]) + ": Enemy Phase", font=("Helvetica", 16), fg="red")

        # Set units to move
        self.units_to_move.clear()
        for unit in mapstate.units_to_move:
            self.units_to_move.append(unit)

        # Move units to correct tile
        for unit in mapstate.unit_states.keys():
            unit.HPcur = mapstate.unit_states[unit].cur_hp

            # Revive fallen unit, placing back and retaining unit ordering
            obj_index = self.all_units[unit.side].index(unit)
            found = False

            if len(self.current_units[unit.side]) == 0:
                self.current_units[unit.side].append(unit)

            elif unit.HPcur > 0 and unit not in self.current_units[unit.side]:
                for i in range(len(self.current_units[unit.side])):
                    if self.all_units[unit.side].index(self.current_units[unit.side][i]) > obj_index:
                        self.current_units[unit.side].insert(i, unit)
                        found = True
                        break

                if not found:
                    self.current_units[unit.side].append(unit)

            unit.specialCount = mapstate.unit_states[unit].cur_sp

            unit.buffs = mapstate.unit_states[unit].cur_buffs[:]
            unit.debuffs = mapstate.unit_states[unit].cur_debuffs[:]
            unit.statusPos = mapstate.unit_states[unit].cur_status_pos[:]
            unit.statusNeg = mapstate.unit_states[unit].cur_status_neg[:]

            unit.special_galeforce_triggered = mapstate.unit_states[unit].sp_galeforce
            unit.nonspecial_galeforce_triggered = mapstate.unit_states[unit].nsp_galeforce
            unit.canto_ready = mapstate.unit_states[unit].canto

            unit.tile.hero_on = None

            unit.unitCombatInitiates = mapstate.unit_states[unit].num_combats
            unit.assistTargetedSelf = mapstate.unit_states[unit].num_assists_self
            unit.assistTargetedOther = mapstate.unit_states[unit].num_assists_other

            #self.refresh_unit_visuals(unit)

        for unit in mapstate.unit_states.keys():
            if unit.HPcur > 0:

                tile_num_to_move = mapstate.unit_states[unit].cur_position
                tile_Obj_to_move = self.map.tiles[tile_num_to_move]
                unit.tile = tile_Obj_to_move
                unit.tile.hero_on = unit

                self.update_unit_graphics(unit)

        for struct in mapstate.struct_states.keys():
            struct.health = mapstate.struct_states[struct]

        self.refresh_walls()

    def next_phase(self):

        self.button_frame.swap_spaces_button.config(state="disabled")
        self.button_frame.undo_button.config(state="normal")

        self.turn_info[1] = abs(self.turn_info[1] - 1)

        units_to_move_CACHE = self.units_to_move[:]

        while self.units_to_move:
            self.units_to_move.pop()

        # clear banner

        if self.turn_info[1] == PLAYER:

            print("---- PLAYER PHASE ----")

            self.turn_info[0] += 1

            self.button_frame.help_info.config(text="Turn " + str(self.turn_info[0]) + ": Player Phase", font=("Helvetica", 16), fg="DodgerBlue2")

            # EDIT BUTTON FRAME TEXT TO DISPLAY TURN NUMBER

            for x in self.current_units[PLAYER]:
                self.units_to_move.append(x)
                x.statusPos = []
                x.buffs[0] * 5
                x.special_galeforce_triggered = False
                x.canto_ready = True

            for x in self.current_units[ENEMY]:
                if x in units_to_move_CACHE:
                    x.statusNeg = []
                    x.debuffs = [0] * 5

            i = 0
            for x in self.all_units[ENEMY]:
                if x.HPcur > 0:
                    self.itemconfig(self.unit_sprites_gs[ENEMY][i], state='hidden')
                    self.itemconfig(self.unit_sprites[ENEMY][i], state='normal')
                i += 1

            damage, heals = feh.start_of_turn(self.current_units[PLAYER], self.current_units[ENEMY], self.turn_info[0])

        if self.turn_info[1] == ENEMY:
            print("---- ENEMY PHASE ----")

            self.button_frame.help_info.config(text="Turn " + str(self.turn_info[0]) + ": Enemy Phase", font=("Helvetica", 16), fg="red")

            # EDIT BUTTON FRAME TEXT TO DISPLAY TURN NUMBER

            for x in self.current_units[ENEMY]:
                self.units_to_move.append(x)
                x.statusPos = []
                x.buffs = [0] * 5
                x.special_galeforce_triggered = False
                x.canto_ready = True

            for x in self.current_units[PLAYER]:
                if x in units_to_move_CACHE:
                    x.statusNeg = []
                    x.debuffs = [0] * 5

            i = 0
            for x in self.all_units[PLAYER]:
                if x.HPcur > 0:
                    self.itemconfig(self.unit_sprites_gs[PLAYER][i], state='hidden')
                    self.itemconfig(self.unit_sprites[PLAYER][i], state='normal')
                i += 1

            damage, heals = feh.start_of_turn(self.current_units[ENEMY], self.current_units[PLAYER], self.turn_info[0])

        # Reset visual sp Charges of all units
        i = 0
        while i < len(self.all_units[PLAYER]):
            if self.all_units[PLAYER][i].specialCount != -1:
                self.itemconfig(self.unit_sp_count_labels[PLAYER][i], text=str(int(self.all_units[PLAYER][i].specialCount)))
            i += 1

        i = 0
        while i < len(self.all_units[ENEMY]):
            if self.all_units[ENEMY][i].specialCount != -1:
                self.itemconfig(self.unit_sp_count_labels[ENEMY][i], text=str(int(self.all_units[ENEMY][i].specialCount)))
            i += 1

        for unit in self.current_units[PLAYER] + self.current_units[ENEMY]:
            heal_amount = 0
            damage_amount = 0
            if unit in heals:
                heal_amount = heals[unit]

            if unit in damage:
                damage_amount = damage[unit]

            if damage_amount >= heal_amount and (damage_amount > 0 or heal_amount > 0):
                unit.HPcur = max(1, unit.HPcur + (heal_amount - damage_amount))
                self.animate_damage_popup(abs(heal_amount - damage_amount), unit.tile.tileNum)
            elif damage_amount < heal_amount and (damage_amount > 0 or heal_amount > 0):
                unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + (heal_amount - damage_amount))
                self.animate_heal_popup(abs(heal_amount - damage_amount), unit.tile.tileNum)

            self.refresh_unit_visuals(unit.side, self.all_units[unit.side].index(unit))

            unit.unitCombatInitiates = 0
            unit.assistTargetedSelf = 0
            unit.assistTargetedOther = 0

        mapstate = create_mapstate(self.all_units[PLAYER], self.all_units[ENEMY], self.map, self.units_to_move, self.turn_info[0])
        self.map_states.append(mapstate)

        return

    def on_click(self, event):


        x_comp = event.x // self.TILE_SIZE
        y_comp = ((self.GAMEPLAY_WIDTH - event.y) // 90)
        tile = x_comp + 6 * y_comp

        if self.animation: return

        # Create menu to build unit on empty space
        if not self.running and not self.hero_listing.creation_menu:
            if tile in self.unit_drag_points and not self.unit_drag_points[tile].hero:
                self.hero_listing.create_creation_popup()
                self.hero_listing.creation_make_button.config(command=partial(self.place_unit_object, event.x, event.y))

                self.hero_listing.creation_build_field.forget()
                self.hero_listing.creation_make_text.forget()

        # Generate unit status from drag point
        if not self.running and self.unit_status:
            if tile in self.unit_drag_points and self.unit_drag_points[tile].hero:
                self.unit_status.update_from_obj(self.unit_drag_points[tile].hero)

        # Nothing else if not running
        if not self.running:
            return

        # YAY I GET TO COPY AND PASTE THE MAIN SIM CODE HERE!!! WEEEEEE!!!!!!

        # End Turn Button code here

        # Swap Spaces Button code here

        # Undo Action Button code here

        cur_hero = self.map.tiles[tile].hero_on

        if not cur_hero:
            return

        S = cur_hero.side
        item_index = self.all_units[S].index(cur_hero)

        # Unit Status frame set to current hero
        self.unit_status.update_from_obj(cur_hero)

        # Not this side's phase, no movement allowed
        if cur_hero.side != self.turn_info[1]:
            return

        # If this movement is as a canto move and currently selecting the canto-enabled unit
        is_canto_move = self.canto == cur_hero

        # Hero already moved, cannot be moved again
        if cur_hero not in self.units_to_move or (self.canto is not None and self.canto != cur_hero):
            return

        self.drag_data = {'cur_x': event.x,
                          'cur_y': event.y,
                          'cur_tile': tile,
                          'start_x_comp': x_comp,
                          'start_y_comp': y_comp,
                          'index': item_index,
                          'side': S,
                          'item': self.unit_sprites[S][item_index]
                          }

        # More drag data fields to be defined
        sdd = self.drag_data # easy shorthand

        self.drag_data['moves'] = []
        self.drag_data['paths'] = []
        self.drag_data['cost'] = 0
        self.drag_data['target'] = None
        self.drag_data['targets_and_tiles'] = {}
        self.drag_data['targets_most_recent_tile'] = {}

        self.drag_data['cur_path'] = ""
        self.drag_data['target_path'] = "NONE"
        self.drag_data['target_dest'] = -1

        # Get possible tiles to move to, shortest path to get to that tile, and objects of each move

        unit_team = self.current_units[S]
        other_team = self.current_units[S - 1]

        if is_canto_move:
            sdd['moves'], sdd['paths'], moves_obj_array = feh.get_canto_moves(cur_hero, unit_team, other_team, self.distance, self.spaces_allowed, self.chosen_action, self.turn_info[0])

        else:
            sdd['moves'], sdd['paths'], moves_obj_array = feh.get_regular_moves(cur_hero, unit_team, other_team)
            self.spaces_allowed = feh.allowed_movement(cur_hero)

        self.tile_sprites = []

        TILE_BLUE = 0
        TILE_PALE_BLUE = 1
        TILE_RED = 2
        TILE_PALE_RED = 3
        TILE_GREEN = 4
        TILE_PALE_GREEN = 5

        # Create blue tiles for each possible movement
        if not (self.canto is not None and cur_hero == self.canto) and not self.swap_mode:
            for move in moves_obj_array:
                x_comp = move.destination % 6
                y_comp = move.destination // 6
                cur_pixel_offset_x = x_comp * 90
                cur_pixel_offset_y = (7 - y_comp) * 90

                tile_photo = self.move_tile_photos[TILE_BLUE]
                if move.is_warp:
                    tile_photo = self.move_tile_photos[TILE_PALE_BLUE]

                curTile = self.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW, image=tile_photo)
                self.tile_sprites.append(curTile)

                # Place movement squares below this sprite
                self.tag_lower(curTile, self.unit_sprites[S][item_index])

        perimeter_attack_range = []  # red tiles on edge of moves
        attack_range = []  # all tiles that can be attacked
        assist_range = []  # all tiles that can be assisted

        # Identify all possible tiles to attack from, regardless of targets
        if cur_hero.weapon and not (self.canto is not None and self.canto == cur_hero) and not self.swap_mode:
            for move in moves_obj_array:
                #atk_arr = get_attack_tiles(move.destination, cur_hero.weapon.range)
                atk_arr = self.map.tiles[move.destination].tilesNSpacesAway(cur_hero.weapon.range)
                for atk_tile in atk_arr:
                    if atk_tile.tileNum not in attack_range:
                        attack_range.append(atk_tile.tileNum)

                    if atk_tile.tileNum not in sdd['moves'] and atk_tile.tileNum not in perimeter_attack_range:
                        perimeter_attack_range.append(atk_tile.tileNum)

        # Draw red attack tiles within range
        for n in perimeter_attack_range:
            x_comp = n % 6
            y_comp = n // 6
            cur_pixel_offset_x = x_comp * 90
            cur_pixel_offset_y = (7 - y_comp) * 90

            # if enemy in range, use red tile instead of pale red tile
            # place this after calculating valid assist positioning?
            cur_tile_photo = self.move_tile_photos[TILE_PALE_RED]

            # Tile holds foe
            if self.map.tiles[n].hero_on is not None:
                if self.map.tiles[n].hero_on.side != cur_hero.side:
                    cur_tile_photo = self.move_tile_photos[TILE_RED]
                if self.map.tiles[n].hero_on.side == cur_hero.side and cur_hero.assist is not None:
                    cur_tile_photo = None

            # Tile holds structure that can be destroyed
            elif self.map.tiles[n].structure_on is not None:
                if self.map.tiles[n].structure_on.struct_type != S + 1 and self.map.tiles[n].structure_on.health > 0:
                    cur_tile_photo = self.move_tile_photos[TILE_RED]

            curTile = self.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW, image=cur_tile_photo)
            self.tile_sprites.append(curTile)

        # find all points to attack all enemies from, fill canvas.drag_data['targets_and_tiles']

        if cur_hero.weapon is not None:
            for m in moves_obj_array:
                atk_arr = self.map.tiles[m.destination].tilesNSpacesAway(cur_hero.weapon.range)
                for atk_tile in atk_arr:
                    n = atk_tile.tileNum

                    # Hero in range
                    if self.map.tiles[n].hero_on is not None and self.map.tiles[n].hero_on.side != cur_hero.side:

                        if self.map.tiles[n].hero_on not in sdd['targets_and_tiles']:
                            sdd['targets_and_tiles'][self.map.tiles[n].hero_on] = [m.destination]

                        if m.destination not in sdd['targets_and_tiles'][self.map.tiles[n].hero_on]:
                            sdd['targets_and_tiles'][self.map.tiles[n].hero_on].append(m.destination)

                    # Destroyable structure in range
                    elif self.map.tiles[n].structure_on is not None:
                        if self.map.tiles[n].structure_on.health > 0 and self.map.tiles[n].structure_on.struct_type != S + 1:

                            if self.map.tiles[n].structure_on not in sdd['targets_and_tiles']:
                                sdd['targets_and_tiles'][self.map.tiles[n].structure_on] = [m.destination]

                            if m.destination not in self.drag_data['targets_and_tiles'][self.map.tiles[n].structure_on]:
                                sdd['targets_and_tiles'][self.map.tiles[n].structure_on].append(m.destination)

        possible_assist_tile_nums = []
        confirmed_assists = []
        unconfirmed_assists = []

        if cur_hero.assist is not None and not (self.canto is not None and self.canto == cur_hero) and not self.swap_mode:
            for m in moves_obj_array:
                ast_arr = self.map.tiles[m.destination].tilesNSpacesAway(cur_hero.assist.range)
                for atk_tile in ast_arr:
                    n = atk_tile.tileNum

                    if self.map.tiles[n].hero_on is not None and self.map.tiles[n].hero_on.side == cur_hero.side and n != tile:

                        valid_unit_cond = False
                        valid_ally_cond = False

                        ally = self.map.tiles[n].hero_on

                        if cur_hero.assist.type == "Move":
                            if "repo" in cur_hero.assist.effects:
                                valid_unit_cond = True
                                move_ally_to = feh.final_reposition_tile(m.destination, n)

                                no_one_on = self.map.tiles[move_ally_to].hero_on is None or self.map.tiles[move_ally_to].hero_on == cur_hero
                                someone_on = not no_one_on

                                ally_is_tile_accessable = feh.can_be_on_tile(self.map.tiles[move_ally_to], ally.move) and not someone_on
                                valid_ally_cond = move_ally_to != -1 and ally_is_tile_accessable

                            elif "draw" in cur_hero.assist.effects:
                                move_unit_to = feh.final_reposition_tile(m.destination, n)
                                move_ally_to = m.destination

                                no_one_on = self.map.tiles[move_unit_to].hero_on is None or self.map.tiles[move_unit_to].hero_on == cur_hero

                                no_one_on_ally = self.map.tiles[move_ally_to].hero_on is None or self.map.tiles[
                                    move_ally_to].hero_on == cur_hero

                                valid_unit_cond = feh.can_be_on_tile(self.map.tiles[move_unit_to], cur_hero.move) and move_unit_to != -1 and no_one_on
                                valid_ally_cond = feh.can_be_on_tile(self.map.tiles[move_ally_to], ally.move) and move_ally_to != -1 and no_one_on_ally

                            elif "swap" in cur_hero.assist.effects:
                                move_unit_to = n
                                move_ally_to = m.destination

                                valid_unit_cond = feh.can_be_on_tile(self.map.tiles[move_unit_to], cur_hero.move)
                                valid_ally_cond = feh.can_be_on_tile(self.map.tiles[move_ally_to], ally.move)

                            elif "pivot" in cur_hero.assist.effects:
                                valid_ally_cond = True

                                move_self_to = feh.final_reposition_tile(n, m.destination)

                                if move_self_to != -1:
                                    unit_on_dest = self.map.tiles[move_self_to].hero_on is not None and self.map.tiles[move_self_to].hero_on != cur_hero

                                    can_traverse_dest = feh.can_be_on_tile(self.map.tiles[move_self_to], cur_hero.move)

                                    if not unit_on_dest and can_traverse_dest:
                                        valid_unit_cond = True

                            elif "smite" in cur_hero.assist.effects:

                                skip_over = feh.final_reposition_tile(n, m.destination)
                                final_dest = feh.final_reposition_tile(skip_over, n)

                                valid_unit_cond = True

                                valid_shove = False
                                valid_smite = False

                                # First, check if shove is possible
                                if skip_over != -1:
                                    unit_on_dest = self.map.tiles[skip_over].hero_on is not None and self.map.tiles[skip_over].hero_on != cur_hero
                                    can_traverse_dest = feh.can_be_on_tile(self.map.tiles[skip_over], ally.move)

                                    valid_shove = not unit_on_dest and can_traverse_dest

                                if final_dest != -1:
                                    unit_on_dest = self.map.tiles[final_dest].hero_on is not None and self.map.tiles[final_dest].hero_on != cur_hero
                                    can_traverse_dest = feh.can_be_on_tile(self.map.tiles[final_dest], ally.move)

                                    foe_on_skip = self.map.tiles[skip_over].hero_on is not None and self.map.tiles[skip_over].hero_on.side != cur_hero.side
                                    can_skip = self.map.tiles[skip_over].terrain != 4 and not foe_on_skip

                                    valid_smite = not unit_on_dest and can_traverse_dest and can_skip

                                valid_ally_cond = valid_shove or valid_smite

                            elif "shove" in cur_hero.assist.effects:
                                final_dest = feh.final_reposition_tile(n, m.destination)
                                valid_unit_cond = True

                                valid_shove = False
                                if final_dest != -1:
                                    unit_on_dest = self.map.tiles[final_dest].hero_on is not None and self.map.tiles[final_dest].hero_on != cur_hero
                                    can_traverse_dest = feh.can_be_on_tile(self.map.tiles[final_dest], ally.move)

                                    valid_shove = not unit_on_dest and can_traverse_dest

                                valid_ally_cond = valid_shove

                        elif cur_hero.assist.type == "Staff":
                            if "heal" in cur_hero.assist.effects:
                                valid_unit_cond = True

                                valid_ally_cond = ally.side == cur_hero.side and ally.HPcur != ally.visible_stats[HP]

                        elif cur_hero.assist.type == "Rally":
                            valid_unit_cond = True

                            given_stats = [0, 0, 0, 0]
                            if "rallyAtk" in cur_hero.assist.effects:
                                given_stats[ATK - 1] += cur_hero.assist.effects["rallyAtk"]
                            if "rallySpd" in cur_hero.assist.effects:
                                given_stats[SPD - 1] += cur_hero.assist.effects["rallySpd"]
                            if "rallyDef" in cur_hero.assist.effects:
                                given_stats[DEF - 1] += cur_hero.assist.effects["rallyDef"]
                            if "rallyRes" in cur_hero.assist.effects:
                                given_stats[RES - 1] += cur_hero.assist.effects["rallyRes"]

                            i = 0
                            while i < len(given_stats):
                                if given_stats[i] > ally.buffs[i + 1]:
                                    valid_ally_cond = True
                                i += 1

                            feint_skills = ["atkFeint", "spdFeint", "defFeint", "resFeint"]
                            ruse_skills = ["atkSpdRuse", "atkDefRuse", "atkResRuse", "spdDefRuse", "spdResRuse", "defResRuse"]

                            for skill in feint_skills + ruse_skills:
                                if skill in cur_hero.getSkills() or skill in ally.getSkills():
                                    valid_ally_cond = True

                            for skill in ["rallyUpAtk", "rallyUpSpd", "rallyUpDef", "rallyUpRes"]:
                                if skill in cur_hero.getSkills():
                                    valid_ally_cond = True

                        elif cur_hero.assist.type == "Refresh":
                            valid_unit_cond = True

                            has_dance_cond = ally.assist is None or (ally.assist is not None and ally.assist.type != "Refresh")
                            valid_ally_cond = ally.side == cur_hero.side and ally not in self.units_to_move and has_dance_cond
                        elif cur_hero.assist.type == "Other":
                            if "rec_aid" in cur_hero.assist.effects:
                                ally_HP_result = min(ally.visible_stats[HP], cur_hero.HPcur)
                                player_HP_result = min(cur_hero.visible_stats[HP], ally.HPcur)

                                valid_unit_cond = player_HP_result > cur_hero.HPcur or ally_HP_result > ally.HPcur
                                valid_ally_cond = True

                            elif "ardent_sac" in cur_hero.assist.effects:
                                valid_unit_cond = cur_hero.HPcur > 10
                                valid_ally_cond = ally.HPcur != ally.visible_stats[HP]

                            elif "sacrifice" in cur_hero.assist.effects:
                                valid_unit_cond = cur_hero.HPcur > 1
                                valid_ally_cond = ally.HPcur != ally.visible_stats[HP] or sum(ally.debuffs) < 0

                            elif "harsh_comm" in cur_hero.assist.effects:
                                valid_unit_cond = True
                                valid_ally_cond = sum(ally.debuffs) < 0
                        else:
                            # big guy is a cheater
                            print("wonderhoy")

                        if valid_unit_cond and valid_ally_cond:

                            # add new target and tile
                            if self.map.tiles[n].hero_on not in sdd['targets_and_tiles']:
                                sdd['targets_and_tiles'][self.map.tiles[n].hero_on] = [m.destination]

                            # give more tiles to target
                            if m.destination not in sdd['targets_and_tiles'][self.map.tiles[n].hero_on]:
                                sdd['targets_and_tiles'][self.map.tiles[n].hero_on].append(m.destination)

                            possible_assist_tile_nums.append(n)
                            confirmed_assists.append(n)

                        else:
                            if n not in possible_assist_tile_nums:
                                possible_assist_tile_nums.append(n)
                                unconfirmed_assists.append(n)

        confirmed_assists = list(set(confirmed_assists))
        unconfirmed_assists = list(set(unconfirmed_assists))

        for n in confirmed_assists:
            x_comp = n % 6
            y_comp = n // 6
            cur_pixel_offset_x = x_comp * 90
            cur_pixel_offset_y = (7 - y_comp) * 90

            curTile = self.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW, image=self.move_tile_photos[TILE_GREEN])
            self.tile_sprites.append(curTile)

        for n in unconfirmed_assists:
            if n not in confirmed_assists:
                x_comp = n % 6
                y_comp = n // 6
                cur_pixel_offset_x = x_comp * 90
                cur_pixel_offset_y = (7 - y_comp) * 90

                curTile = self.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW, image=self.move_tile_photos[TILE_PALE_RED])
                self.tile_sprites.append(curTile)

        # Raise enemy team
        i = 0
        while i < len(self.all_units[S - 1]):
            self.tag_raise(self.unit_sprites[S - 1][i])
            self.tag_raise(self.unit_sprites_gs[S - 1][i])
            self.tag_raise(self.unit_sprites_trans[S - 1][i])
            self.tag_raise(self.unit_sprites_gs_trans[S - 1][i])
            self.tag_raise(self.unit_weapon_icon_sprites[S - 1][i])
            self.tag_raise(self.unit_hp_count_labels[S - 1][i])
            self.tag_raise(self.unit_sp_count_labels[S - 1][i])
            self.tag_raise(self.unit_hp_bars_bg[S - 1][i])
            self.tag_raise(self.unit_hp_bars_fg[S - 1][i])
            i += 1

        # Raise allies
        i = 0
        while i < len(self.all_units[S]):
            if i == item_index:
                i += 1
                continue

            self.tag_raise(self.unit_sprites[S][i])
            self.tag_raise(self.unit_sprites_gs[S][i])
            self.tag_raise(self.unit_sprites_trans[S][i])
            self.tag_raise(self.unit_sprites_gs_trans[S][i])
            self.tag_raise(self.unit_weapon_icon_sprites[S][i])
            self.tag_raise(self.unit_hp_count_labels[S][i])
            self.tag_raise(self.unit_sp_count_labels[S][i])
            self.tag_raise(self.unit_hp_bars_bg[S][i])
            self.tag_raise(self.unit_hp_bars_fg[S][i])
            i += 1

        # Raise self
        self.tag_raise(self.unit_sprites[S][item_index])
        self.tag_raise(self.unit_sprites_gs[S][item_index])
        self.tag_raise(self.unit_sprites_trans[S][item_index])
        self.tag_raise(self.unit_sprites_gs_trans[S][item_index])
        self.tag_raise(self.unit_weapon_icon_sprites[S][item_index])
        self.tag_raise(self.unit_hp_count_labels[S][item_index])
        self.tag_raise(self.unit_sp_count_labels[S][item_index])
        self.tag_raise(self.unit_hp_bars_bg[S][item_index])
        self.tag_raise(self.unit_hp_bars_fg[S][item_index])

        sdd['arrow_path'] = []
        sdd['attack_range'] = attack_range
        sdd['assist_range'] = confirmed_assists

        x_comp = event.x // self.TILE_SIZE
        y_comp = ((self.GAMEPLAY_WIDTH - event.y) // 90)
        pixel_offset_x = x_comp * 90
        pixel_offset_y = (7 - y_comp) * 90

        # make starting path
        if not self.swap_mode:
            first_path = self.create_image(pixel_offset_x, pixel_offset_y, anchor=tk.NW, image=self.move_arrow_photos[14])
            self.tag_lower(first_path, self.unit_sprites[S][item_index])
            #self.tag_lower(first_path, self.unit_sprites_trans[S][item_index])

            self.drag_data['arrow_path'] = [first_path]

        return

    def on_drag(self, event):
        if self.animation or not self.running or not self.drag_data: return

        delta_x = event.x - self.drag_data['cur_x']
        delta_y = event.y - self.drag_data['cur_y']

        item_index = self.drag_data['index']
        S = self.drag_data['side']

        cur_hero = self.all_units[S][item_index]
        tag: str = self.unit_tags[S][item_index]

        self.move(tag, delta_x, delta_y)

        self.drag_data['cur_x'] = event.x
        self.drag_data['cur_y'] = event.y

        # tile from previous movement
        prev_tile_int = self.drag_data['cur_tile']

        x_comp = event.x // 90
        y_comp = ((720 - event.y) // 90)
        cur_tile_int = x_comp + y_comp * 6

        # Out of bounds, nothing else to do
        if event.x <= 0 or event.x >= 540 or event.y <= 0 or event.y >= 720:
            return

        # different tile and within moves
        # figure out the current path

        # sets path/final position to target a foe

        cur_tile_Obj = self.map.tiles[cur_tile_int]
        prev_tile_Obj = self.map.tiles[prev_tile_int]

        moved_to_different_tile = prev_tile_int != cur_tile_int

        # On drag, things should only update upon visiting a new tile
        if not moved_to_different_tile:
            return

        sdd = self.drag_data

        for x in self.active_aoe_icons:
            self.delete(x)
        self.active_aoe_icons.clear()

        # If moving onto a space with another Hero
        if cur_tile_Obj.hero_on and cur_tile_Obj.hero_on != cur_hero:

            # Target is a foe within range
            if cur_tile_int in sdd['attack_range'] and cur_tile_Obj.hero_on.side != cur_hero.side:

                # Default target
                target_tile = sdd['targets_and_tiles'][cur_tile_Obj.hero_on][0]

                # If a different tile has been visited that allows attack on target, set target from that tile instead
                if cur_tile_Obj.hero_on in sdd['targets_most_recent_tile']:
                    target_tile = sdd['targets_most_recent_tile'][cur_tile_Obj.hero_on]

                # Set the default path for visiting the target tile
                sdd['target_path'] = sdd['paths'][sdd['moves'].index(target_tile)]
                sdd['target_dest'] = target_tile

                sdd['target'] = cur_tile_Obj.hero_on

                if cur_hero.special is not None and cur_hero.special.type == "AOE" and cur_hero.specialCount == 0:
                    formation = cur_hero.special.effects["aoe_area"]
                    aoe_special_targets = feh.aoe_tiles(cur_tile_int, formation)

                    for num in aoe_special_targets:
                        cur_special_image = self.create_image((0, 90), image=self.aoe_icon, anchor="center")
                        self.move_to_tile(cur_special_image, num)
                        self.active_aoe_icons.append(cur_special_image)

                        self.tag_raise(tag)

                cur_hero.attacking_tile = self.map.tiles[target_tile]

                distance = abs(target_tile % 6 - sdd["start_x_comp"]) + abs(target_tile // 6 - sdd["start_y_comp"])

                # Determine if Savior Unit should be targeted instead.
                targeting_range = cur_hero.weapon.range
                savior_unit = None

                for ally in feh.allies_within_n(cur_tile_Obj.hero_on, 2):
                    if targeting_range == 1 and "nearSavior" in ally.getSkills() and hero.Status.Undefended not in ally.statusNeg:
                        if savior_unit is None:
                            savior_unit = ally
                        else:
                            savior_unit = None
                            break

                    elif targeting_range == 2 and "farSavior" in ally.getSkills() and hero.Status.Undefended not in ally.statusNeg:
                        if savior_unit is None:
                            savior_unit = ally
                        else:
                            savior_unit = None
                            break

                if savior_unit is None:
                    self.extras.set_forecast_banner_foe(cur_hero, cur_tile_Obj.hero_on, distance, False, self.turn_info[0], self.combat_fields)
                    self.unit_status.update_from_obj(cur_tile_Obj.hero_on)
                else:
                    prev_savior_tile_Obj = savior_unit.tile

                    savior_unit.tile = cur_tile_Obj

                    self.extras.set_forecast_banner_foe(cur_hero, savior_unit, distance, True, self.turn_info[0], self.combat_fields)
                    self.unit_status.update_from_obj(savior_unit)

                    savior_unit.tile = prev_savior_tile_Obj


            # Target is an ally
            elif cur_tile_int in sdd['assist_range'] and cur_tile_Obj.hero_on.side == cur_hero.side:

                # Default target
                target_tile = sdd['targets_and_tiles'][self.map.tiles[cur_tile_int].hero_on][0]

                # If a different tile has been visited that allows assist on target
                if self.map.tiles[cur_tile_int].hero_on in sdd['targets_most_recent_tile']:
                    target_tile = sdd['targets_most_recent_tile'][
                        self.map.tiles[cur_tile_int].hero_on]

                # Get the default path for visiting the target tile
                sdd['target_path'] = sdd['paths'][sdd['moves'].index(target_tile)]
                sdd['target_dest'] = target_tile

                sdd['target'] = cur_tile_Obj.hero_on

                # set_assist_forecast(cur_hero, chosen_map.tiles[cur_tile_int].hero_on)
                self.extras.set_forecast_banner_ally(cur_hero, self.map.tiles[cur_tile_int].hero_on)


            # Target is invalid (hero out of reach/no weapon/no assist)
            else:
                self.drag_data['target_path'] = "NONE"
                self.drag_data['target_dest'] = cur_tile_Obj

                self.drag_data['target'] = None

                self.unit_status.update_from_obj(self.map.tiles[cur_tile_int].hero_on)
                self.extras.clear_forecast_banner()

        # If moving onto a space with a destroyable structure
        elif cur_tile_Obj.structure_on and cur_tile_Obj.structure_on.health > 0 and cur_tile_Obj.structure_on.struct_type != S + 1 and cur_tile_int in self.drag_data['attack_range']:

                target_tile = self.drag_data['targets_and_tiles'][self.map.tiles[cur_tile_int].structure_on][0]

                # If a different tile has been visited that allows assist on target
                if self.map.tiles[cur_tile_int].structure_on in self.drag_data['targets_most_recent_tile']:
                    target_tile = sdd['targets_most_recent_tile'][self.map.tiles[cur_tile_int].structure_on]

                # Get the default path for visiting the target tile
                sdd['target_path'] = sdd['paths'][sdd['moves'].index(target_tile)]
                sdd['target_dest'] = target_tile

                sdd['target'] = self.map.tiles[cur_tile_int].structure_on

                self.extras.set_forecast_banner_struct(cur_hero, self.map.tiles[cur_tile_int].structure_on)

        # If moving onto a space with nothing
        else:
            self.unit_status.update_from_obj(cur_hero)
            self.extras.clear_forecast_banner()

            sdd['target'] = None
            sdd['target_path'] = "NONE"



        # Create the string which represents the path

        # Valid position to valid position
        if cur_tile_int in sdd['moves'] and prev_tile_int in sdd['moves']:
            # Build from existing path

            new_tile_cost = feh.get_tile_cost(self.map.tiles[cur_tile_int], cur_hero)
            sdd['cost'] += new_tile_cost

            # Arrow can continue to grow only if within movement distance and if path does not contain starting point
            x_start_comp = sdd['start_x_comp']
            y_start_comp = sdd['start_y_comp']
            recalc_tile = int(x_start_comp + 6 * y_start_comp)

            spaces_allowed = feh.allowed_movement(cur_hero)
            is_allowed = sdd['cost'] <= spaces_allowed and cur_tile_int != recalc_tile

            # west
            if prev_tile_int - 1 == cur_tile_int and is_allowed:
                sdd['cur_path'] += 'W'
                if len(sdd['cur_path']) >= 2 and sdd['cur_path'].endswith("EW"):
                    sdd['cur_path'] = sdd['cur_path'][:-2]
                    sdd['cost'] -= new_tile_cost
                    sdd['cost'] -= feh.get_tile_cost(self.map.tiles[prev_tile_int], cur_hero)

            # east
            elif prev_tile_int + 1 == cur_tile_int and is_allowed:
                sdd['cur_path'] += 'E'
                if len(sdd['cur_path']) >= 2 and sdd['cur_path'].endswith("WE"):
                    sdd['cur_path'] = sdd['cur_path'][:-2]
                    sdd['cost'] -= new_tile_cost
                    sdd['cost'] -= feh.get_tile_cost(self.map.tiles[prev_tile_int], cur_hero)

            # south
            elif prev_tile_int - 6 == cur_tile_int and is_allowed:
                sdd['cur_path'] += 'S'
                if len(sdd['cur_path']) >= 2 and sdd['cur_path'].endswith("NS"):
                    sdd['cur_path'] = sdd['cur_path'][:-2]
                    sdd['cost'] -= new_tile_cost
                    sdd['cost'] -= feh.get_tile_cost(self.map.tiles[prev_tile_int], cur_hero)

            # north
            elif prev_tile_int + 6 == cur_tile_int and is_allowed:
                sdd['cur_path'] += 'N'
                if len(sdd['cur_path']) >= 2 and sdd['cur_path'].endswith("SN"):
                    sdd['cur_path'] = sdd['cur_path'][:-2]
                    sdd['cost'] -= new_tile_cost
                    sdd['cost'] -= feh.get_tile_cost(self.map.tiles[prev_tile_int], cur_hero)

            # Path too long, remake with default path
            else:
                sdd['cur_path'] = sdd['paths'][sdd['moves'].index(cur_tile_int)]

                new_cost = 0
                for c in sdd['cur_path']:
                    if c == 'N': recalc_tile += 6
                    if c == 'S': recalc_tile -= 6
                    if c == 'E': recalc_tile += 1
                    if c == 'W': recalc_tile -= 1
                    new_cost += feh.get_tile_cost(self.map.tiles[recalc_tile], cur_hero)

                sdd['cost'] = new_cost

        # Invalid position to valid position
        elif cur_tile_int in sdd['moves'] and prev_tile_int not in sdd['moves']:
            # Valid path removed, remake with default path

            sdd['cur_path'] = sdd['paths'][sdd['moves'].index(cur_tile_int)]

            x_start_comp = sdd['start_x_comp']
            y_start_comp = sdd['start_y_comp']
            recalc_tile = int(x_start_comp + 6 * y_start_comp)

            new_cost = 0
            for c in sdd['cur_path']:
                if c == 'N': recalc_tile += 6
                if c == 'S': recalc_tile -= 6
                if c == 'E': recalc_tile += 1
                if c == 'W': recalc_tile -= 1
                new_cost += feh.get_tile_cost(self.map.tiles[recalc_tile], cur_hero)

            sdd['cost'] = new_cost

        # get the x/y components of the starting tile, start drawing path from here
        x_arrow_comp = sdd['start_x_comp']
        y_arrow_comp = sdd['start_y_comp']
        x_arrow_pivot = x_arrow_comp * 90
        y_arrow_pivot = (7 - y_arrow_comp) * 90

        # Clear the current arrow path
        for arrow in sdd['arrow_path']:
            self.delete(arrow)
        sdd['arrow_path'] = []

        # If currently targeting something, adjust path to go to tile to interact w/ object
        traced_path = sdd['cur_path']
        if sdd['target_path'] != "NONE":
            traced_path = sdd['target_path']

        # draw the arrow path

        # recheck conditions
        if (cur_tile_int in sdd['moves'] or sdd['target_path'] != "NONE") and not self.swap_mode:

            # if dragged space is the same as starting space
            if len(traced_path) == 0 or event.x > 539 or event.x < 0:
                star = self.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=self.move_arrow_photos[14])
                sdd['arrow_path'].append(star)
                self.tag_lower(star, sdd['item'])

            # if dragged to a warp tile
            elif "WARP" in traced_path:
                star = self.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=self.move_arrow_photos[14])
                sdd['arrow_path'].append(star)
                self.tag_lower(star, sdd['item'])

                final_tile_star_pos = cur_tile_int

                if self.map.tiles[cur_tile_int].hero_on in sdd['targets_and_tiles']:
                    final_tile_star_pos = sdd['target_dest']

                star = self.create_image(x_arrow_pivot, y_arrow_pivot, anchor='center', image=self.move_arrow_photos[14])
                self.move_to_tile(star, final_tile_star_pos)
                self.move(star, -9, 0)
                sdd['arrow_path'].append(star)
                self.tag_lower(star, sdd['item'])

            # a path from one tile to the next, no warping
            else:
                first_dir = -1
                if traced_path[0] == 'N': first_dir = 0
                if traced_path[0] == 'S': first_dir = 1
                if traced_path[0] == 'E': first_dir = 2
                if traced_path[0] == 'W': first_dir = 3

                arrow_offset_x, arrow_offset_y = _get_arrow_offsets(first_dir)

                first_arrow = self.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y, anchor=tk.NW, image=self.move_arrow_photos[first_dir])
                sdd['arrow_path'].append(first_arrow)
                self.tag_lower(first_arrow, sdd['item'])

                if traced_path[0] == 'N': y_arrow_pivot -= 90
                if traced_path[0] == 'S': y_arrow_pivot += 90
                if traced_path[0] == 'E': x_arrow_pivot += 90
                if traced_path[0] == 'W': x_arrow_pivot -= 90

                i = 0
                while i < len(traced_path) - 1:
                    cur_dir = -1
                    cur_element_1 = traced_path[i]
                    cur_element_2 = traced_path[i + 1]

                    if cur_element_1 == 'N' and cur_element_2 == 'N' or cur_element_1 == 'S' and cur_element_2 == 'S': cur_dir = 8
                    if cur_element_1 == 'E' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'W': cur_dir = 9

                    if cur_element_1 == 'N' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'S': cur_dir = 10
                    if cur_element_1 == 'N' and cur_element_2 == 'W' or cur_element_1 == 'E' and cur_element_2 == 'S': cur_dir = 11
                    if cur_element_1 == 'S' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'N': cur_dir = 12
                    if cur_element_1 == 'S' and cur_element_2 == 'W' or cur_element_1 == 'E' and cur_element_2 == 'N': cur_dir = 13

                    arrow_offset_x, arrow_offset_y = _get_arrow_offsets(cur_dir)

                    cur_arrow = self.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y, anchor=tk.NW, image=self.move_arrow_photos[cur_dir])
                    sdd['arrow_path'].append(cur_arrow)
                    self.tag_lower(first_arrow, sdd['item'])

                    if cur_element_2 == 'N': y_arrow_pivot -= 90
                    if cur_element_2 == 'S': y_arrow_pivot += 90
                    if cur_element_2 == 'E': x_arrow_pivot += 90
                    if cur_element_2 == 'W': x_arrow_pivot -= 90

                    i += 1

                last_dir = -1
                if traced_path[-1] == 'N': last_dir = 4
                if traced_path[-1] == 'S': last_dir = 5
                if traced_path[-1] == 'E': last_dir = 6
                if traced_path[-1] == 'W': last_dir = 7

                arrow_offset_x, arrow_offset_y = _get_arrow_offsets(last_dir)

                last_arrow = self.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y, anchor=tk.NW, image=self.move_arrow_photos[last_dir])
                sdd['arrow_path'].append(last_arrow)
                self.tag_lower(last_arrow, sdd['item'])

        # draw move_star at start only if out of bounds
        elif cur_tile_int not in sdd['moves'] and not self.swap_mode:
            if len(sdd['arrow_path']) != 1:
                for arrow in sdd['arrow_path']:
                    self.delete(arrow)
                sdd['arrow_path'] = []

            star = self.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=self.move_arrow_photos[14])
            sdd['arrow_path'].append(star)
            self.tag_lower(star, sdd['item'])

        # For each potential target in range, set current tile as the most recent tile visited that the dragged unit can attack from
        for x in sdd['targets_and_tiles']:
            if cur_tile_int in sdd['targets_and_tiles'][x]:
                sdd['targets_most_recent_tile'][x] = cur_tile_int

        for t in sdd['arrow_path']:
            self.tag_lower(t, sdd['item'])

        # End of function, set cur_tile stored in drag data to new tile
        sdd['cur_tile'] = cur_tile_int

        return

    def on_release(self, event):
        sdd = self.drag_data

        if sdd is None or not self.running: return

        # Get tile position on release
        x_comp = event.x // 90
        y_comp = ((720 - event.y) // 90)
        destination_tile = x_comp + y_comp * 6

        # Tile the unit is moved to
        release_tile = destination_tile

        # Tile unit is moved to, if targeting something
        if sdd['target_path'] != "NONE":
            destination_tile = sdd['target_dest']

        # Tile moved from
        x_start_comp = sdd['start_x_comp']
        y_start_comp = sdd['start_y_comp']
        recalc_tile = int(x_start_comp + 6 * y_start_comp)

        item_index = sdd['index']
        S = sdd['side']
        cur_unit = self.all_units[S][item_index]

        within_bounds = 539 > event.x > 0 and 720 > event.y > 0

        # If the movement performed was onto a valid space
        # Movements are invalid if the unit cannot move to a space, they move to the same space without acting, or  swap mode is currently enabled
        successful_move = False

        # Set unit's final position
        if within_bounds and destination_tile in sdd['moves'] and not self.swap_mode:  # if moving to a tile in movement range
            final_destination = destination_tile

            if destination_tile != recalc_tile or sdd['target_path'] != "NONE":
                successful_move = True

        else:
            # not in movement range, set back to the start
            final_destination = recalc_tile

        self.all_units[S][item_index].tile.hero_on = None
        self.all_units[S][item_index].tile = self.map.tiles[final_destination]
        self.map.tiles[final_destination].hero_on = self.all_units[S][item_index]

        self.move_visuals_to_tile(S, item_index, final_destination)

        # Delete all colored movement tiles
        for tile in self.tile_sprites:
            self.delete(tile)
        self.tile_sprites.clear()

        # Delete all arrows
        for arrow in sdd['arrow_path']:
            self.delete(arrow)

        # Delete all AoE icons
        for aoe_icon in self.active_aoe_icons:
            self.delete(aoe_icon)
        self.active_aoe_icons.clear()

        # If off-board move, nothing else to do
        if not within_bounds:
            self.drag_data = None
            return

        destination_unit = self.map.tiles[destination_tile].hero_on  # the unit going to the destination, usually to interact w/ dest unit
        release_unit = self.map.tiles[release_tile].hero_on  # the unit on the tile being hovered over by the mouse
        release_struct = self.map.tiles[release_tile].structure_on

        # Swap Allies if in swap mode
        if self.swap_mode and release_tile in self.unit_drag_points.keys() and self.unit_drag_points[release_tile].side == PLAYER:  #cur_unit.isAllyOf(release_unit):
            if release_unit is not None:
                ally = release_unit

                unit_final_position = ally.tile.tileNum
                ally_final_position = cur_unit.tile.tileNum

                cur_unit.tile.hero_on = None
                ally.tile.hero_on = None

                cur_unit.tile = self.map.tiles[unit_final_position]
                ally.tile = self.map.tiles[ally_final_position]

                self.map.tiles[unit_final_position].hero_on = cur_unit
                self.map.tiles[ally_final_position].hero_on = ally

                self.move_visuals_to_tile(S, item_index, unit_final_position)
                self.move_visuals_to_tile(S, self.all_units[S].index(ally), ally_final_position)

                self.drag_data = None
            else:
                unit_final_position = release_tile

                cur_unit.tile.hero_on = None

                cur_unit.tile = self.map.tiles[unit_final_position]

                self.map.tiles[unit_final_position].hero_on = cur_unit

                self.move_visuals_to_tile(S, item_index, unit_final_position)

            return

        if not successful_move:
            self.drag_data = None
            return

        INVALID = -1
        ATTACK = 0
        ASSIST = 1
        BREAK = 2
        MOVE = 3

        finish_time = 0

        # Sets the given unit's visibility from the board to hidden, called when they die
        def set_unit_death(unit):
            U_side = unit.side
            unit_index = self.all_units[U_side].index(unit)

            self.itemconfig(self.unit_sprites[U_side][unit_index], state='hidden')
            self.itemconfig(self.unit_sprites_gs[U_side][unit_index], state='hidden')
            self.itemconfig(self.unit_sprites_trans[U_side][unit_index], state='hidden')
            self.itemconfig(self.unit_sprites_gs_trans[U_side][unit_index], state='hidden')

            self.itemconfig(self.unit_weapon_icon_sprites[U_side][unit_index], state='hidden')
            self.itemconfig(self.unit_sp_count_labels[U_side][unit_index], state='hidden')
            self.itemconfig(self.unit_hp_count_labels[U_side][unit_index], state='hidden')
            self.itemconfig(self.unit_hp_bars_bg[U_side][unit_index], state='hidden')
            self.itemconfig(self.unit_hp_bars_fg[U_side][unit_index], state='hidden')

        def set_unit_show(unit):
            U_side = unit.side
            unit_index = self.all_units[U_side].index(unit)

            self.itemconfig(self.unit_sprites[U_side][unit_index], state='normal')
            #self.itemconfig(self.unit_sprites_trans[U_side][unit_index], state='normal') --- IF TRANSFORMED

            self.itemconfig(self.unit_weapon_icon_sprites[U_side][unit_index], state='normal')
            self.itemconfig(self.unit_sp_count_labels[U_side][unit_index], state='normal')
            self.itemconfig(self.unit_hp_count_labels[U_side][unit_index], state='normal')
            self.itemconfig(self.unit_hp_bars_bg[U_side][unit_index], state='normal')
            self.itemconfig(self.unit_hp_bars_fg[U_side][unit_index], state='normal')

        # Sets a unit grayscale once their action is done
        def set_unit_actability(unit):
            U_side = unit.side
            unit_index = self.all_units[U_side].index(unit)

            #unit_sprite = self.unit_sprites[U_side][unit_index]
            #unit_sprite_gs = grayscale_IDs[U_side][unit_index]

            self.itemconfig(self.unit_sprites[U_side][unit_index], state='hidden')
            #self.itemconfig(self.unit_sprites_trans[U_side][unit_index], state='hidden') --- IF TRANSFORMED


            self.itemconfig(self.unit_sprites_gs[U_side][unit_index], state='normal')
            #self.itemconfig(self.unit_sprites_gs_trans[U_side][unit_index], state='normal') --- IF TRANSFORMED

        is_targeting_object = sdd['target_path'] != "NONE"
        is_targeting_hero = release_unit is not None
        is_targeting_struct = release_struct is not None

        # Get number of spaces between start and end position
        # Based on shortest possible line between points A and B, ignoring actual shape of path drawn
        distance = abs(destination_tile % 6 - sdd["start_x_comp"]) + abs(destination_tile // 6 - sdd["start_y_comp"])
        self.distance = distance

        # Galeforce/Canto Variables
        galeforce_triggered = False

        # ATTAAAAAAAAAAAAAAAAAAAAAAACK!!!!!!!!!!!!!!!!!!
        if is_targeting_object and is_targeting_hero and destination_unit.isEnemyOf(release_unit):

            # Begin initiating an attack animation
            self.animation = True

            # Action chosen is an Attack
            action = ATTACK

            player = destination_unit
            player_tile = destination_tile

            enemy = release_unit
            enemy_tile = release_tile

            # Determine savior variables
            targeting_range = player.weapon.range
            savior_unit = None

            for ally in feh.allies_within_n(enemy, 2):
                if targeting_range == 1 and "nearSavior" in ally.getSkills():
                    if savior_unit is None:
                        savior_unit = ally
                    else:
                        savior_unit = None
                        break

                elif targeting_range == 2 and "farSavior" in ally.getSkills():
                    if savior_unit is None:
                        savior_unit = ally
                    else:
                        savior_unit = None
                        break

            # Using unit and foe's positioning, figure out which direction to shift while attacking
            # Go back and revise, Emblem Lyn attacks differently when using Astra Storm Style
            player_atk_dir_hori = 0
            player_atk_dir_vert = 0

            if player_tile % 6 < enemy_tile % 6:
                player_atk_dir_hori = 1
            elif player_tile % 6 > enemy_tile % 6:
                player_atk_dir_hori = -1

            if player_tile // 6 < enemy_tile // 6:
                player_atk_dir_vert = 1
            elif player_tile // 6 > enemy_tile // 6:
                player_atk_dir_vert = -1

            if savior_unit:
                targeted_enemy = enemy
                initiated_enemy = savior_unit

            else:
                targeted_enemy = enemy
                initiated_enemy = enemy



            # player sprites to be used for combat
            player_index = self.all_units[S].index(cur_unit)

            player_sprite = self.unit_sprites[S][item_index]
            player_sprite_trans = self.unit_sprites[S][item_index]

            player_weapon_icon = self.unit_weapon_icon_sprites[S][item_index]
            player_hp_label = self.unit_hp_count_labels[S][item_index]
            player_sp_label = self.unit_sp_count_labels[S][item_index]
            player_hp_bar_fg = self.unit_hp_bars_fg[S][item_index]
            player_hp_bar_bg = self.unit_hp_bars_bg[S][item_index]

            # enemy sprites to be used for combat
            E_side = enemy.side

            enemy_index = self.all_units[E_side].index(initiated_enemy)

            enemy_sprite = self.unit_sprites[E_side][enemy_index]
            enemy_sprite_trans = self.unit_sprites[E_side][enemy_index]

            enemy_weapon_icon = self.unit_weapon_icon_sprites[E_side][enemy_index]
            enemy_hp_label = self.unit_hp_count_labels[E_side][enemy_index]
            enemy_sp_label = self.unit_sp_count_labels[E_side][enemy_index]
            enemy_hp_bar_fg = self.unit_hp_bars_fg[E_side][enemy_index]
            enemy_hp_bar_bg = self.unit_hp_bars_bg[E_side][enemy_index]

            def animation_done():
                self.animation = False

            # Perform AOE attack
            aoe_present = 0
            num_aoe_targets = 0

            # Will eventually need to change to account for skills that
            # Go back and revise, jump the count before the AoE goes off (Momentum, Arcane Truthfire)
            if player.special is not None and player.special.type == "AOE" and player.specialCount == 0:
                aoe_present = 500 # add 500 milliseconds to total animation time

                player.specialCount = player.specialMax
                self.after(300, self.set_text_val, self.unit_sp_count_labels[S][item_index], player.specialMax)

                formation_id = player.special.effects["aoe_area"]
                aoe_special_targets = feh.aoe_tiles(enemy_tile, formation_id)
                num_aoe_targets = len(aoe_special_targets)

                for tile in aoe_special_targets:
                    aoe_target = self.map.tiles[tile].hero_on
                    if aoe_target is not None and aoe_target.side != player.side:
                        aoe_damage: int = get_AOE_damage(player, aoe_target)

                        aoe_target.HPcur = max(1, aoe_target.HPcur - aoe_damage)
                        self.after(300, self.set_hp_visual, aoe_target, aoe_target.HPcur)
                        self.after(300, self.animate_damage_popup, aoe_damage, tile)

            # Begin savior process
            savior_present = 0

            if savior_unit:
                savior_present = 200

                prev_savior_tile_Obj = savior_unit.tile

                savior_unit.tile = enemy.tile

                combat_result = simulate_combat(player, savior_unit, True, self.turn_info[0], distance, self.combat_fields, aoe_present, savior_triggered=True)

                savior_unit.tile = prev_savior_tile_Obj

                # Hide unit being covered by Savior
                self.after(aoe_present + 100, set_unit_death, enemy)

                self.after(aoe_present + 100, self.move_to_tile, enemy_sprite, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile, enemy_sprite_trans, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile_wp,enemy_weapon_icon, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile_hp, enemy_hp_label, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile_sp, enemy_sp_label, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile_bar, enemy_hp_bar_fg, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile_bar,enemy_hp_bar_bg, enemy_tile)

            else:
                combat_result = simulate_combat(player, enemy, True, self.turn_info[0], distance, self.combat_fields, aoe_present, savior_triggered=False)

            # Perform the combat and return the results
            attacks = combat_result[7]  # Attack objects

            # Increment the number of combats each unit has partaken in during the turn
            player.unitCombatInitiates += 1
            initiated_enemy.unitCombatInitiates += 1

            # Perform burn damage
            burn_damages = combat_result[14]

            burn_present = 0
            if burn_damages[PLAYER] > 0 or burn_damages[ENEMY] > 0:
                burn_present = 500  # add 500 milliseconds to total animation time

                # Set burn damages
                if burn_damages[PLAYER] > 0:
                    initiated_enemy.HPcur = max(1, initiated_enemy.HPcur - burn_damages[PLAYER])
                    self.after(300 + aoe_present, self.set_hp_visual, enemy, initiated_enemy.HPcur)
                    self.after(300 + aoe_present, self.animate_damage_popup, burn_damages[PLAYER], enemy_tile)

                if burn_damages[ENEMY] > 0:
                    player.HPcur = max(1, player.HPcur - burn_damages[ENEMY])
                    self.after(300 + aoe_present, self.set_hp_visual, player, player.HPcur)
                    self.after(300 + aoe_present, self.animate_damage_popup, burn_damages[ENEMY], player_tile)

            # Perform BOL heals

            # ------------- INSERT HERE -------------


            # Visualization of the blows trading
            i = 0

            # Iterate over the attacks
            while i < len(attacks):
                move_time = i * 500 + 200 + aoe_present + burn_present + savior_present# when move starts per hit
                impact_time = i * 500 + 300 + aoe_present + burn_present + savior_present # when damage numbers show per hit

                # PLAYER SIDE ATTACKS
                if attacks[i].attackOwner == PLAYER:

                    # Move player sprite
                    self.after(move_time, self.animate_sprite_atk, player_sprite, player_atk_dir_hori, player_atk_dir_vert, attacks[i].damage, enemy_tile)

                    # Display popup for healing on hit
                    if attacks[i].healed > 0:
                        self.after(impact_time, self.animate_heal_popup, attacks[i].healed, player_tile)

                    # Damage enemy
                    initiated_enemy.HPcur = max(0, initiated_enemy.HPcur - attacks[i].damage)
                    self.after(impact_time, self.set_text_val, enemy_hp_label, initiated_enemy.HPcur)

                    # Update target HP bar percentage
                    hp_percentage_target = initiated_enemy.HPcur / initiated_enemy.visible_stats[HP]
                    self.after(impact_time, self.set_hp_bar_length, enemy_hp_bar_fg, hp_percentage_target)

                    # Heal atkr, update HP count
                    player.HPcur = min(player.visible_stats[HP], player.HPcur + attacks[i].healed)
                    self.after(impact_time, self.set_text_val, player_hp_label, player.HPcur)

                    # Update atkr HP bar percentage
                    hp_percentage_atkr = player.HPcur / player.visible_stats[HP]
                    self.after(impact_time, self.set_hp_bar_length, player_hp_bar_fg, hp_percentage_atkr)

                # ENEMY SIDE ATTACKS
                if attacks[i].attackOwner == ENEMY:

                    # Move player sprite
                    self.after(move_time, self.animate_sprite_atk, enemy_sprite, player_atk_dir_hori * -1, player_atk_dir_vert * -1, attacks[i].damage, player_tile)

                    # Display popup for healing on hit
                    if attacks[i].healed > 0:
                        self.after(impact_time, self.animate_heal_popup, attacks[i].healed, enemy_tile)

                    # Damage target
                    player.HPcur = max(0, player.HPcur - attacks[i].damage)
                    self.after(impact_time, self.set_text_val, player_hp_label, player.HPcur)

                    # Update target HP bar percentage
                    hp_percentage = player.HPcur / player.visible_stats[HP]
                    self.after(impact_time, self.set_hp_bar_length, player_hp_bar_fg, hp_percentage)

                    # Heal atkr, update HP count
                    initiated_enemy.HPcur = min(initiated_enemy.visible_stats[HP], initiated_enemy.HPcur + attacks[i].healed)
                    self.after(impact_time, self.set_text_val, enemy_hp_label, initiated_enemy.HPcur)

                    #Update atkr HP bar percentage
                    hp_percentage = initiated_enemy.HPcur / initiated_enemy.visible_stats[HP]
                    self.after(impact_time, self.set_hp_bar_length, enemy_hp_bar_fg, hp_percentage)

                # Update special counts
                if player.specialCount != -1:
                    player.specialCount = attacks[i].spCharges[0]
                    self.after(impact_time, self.set_text_val, player_sp_label, player.specialCount)

                if initiated_enemy.specialCount != -1:
                    initiated_enemy.specialCount = attacks[i].spCharges[1]
                    self.after(impact_time, self.set_text_val, enemy_sp_label, initiated_enemy.specialCount)

                # If any unit dies, break the loop
                if player.HPcur == 0 or initiated_enemy.HPcur == 0:
                    break

                i += 1

            # Finalized finish time, animation will end here
            finish_time = 500 * (i + 1) + 200 + aoe_present + burn_present + 2 * savior_present

            if savior_unit:
                self.after(finish_time - 100, set_unit_show, enemy)

                self.after(finish_time - 100, self.move_to_tile, enemy_sprite, initiated_enemy.tile.tileNum)
                self.after(finish_time - 100, self.move_to_tile_wp, enemy_weapon_icon, initiated_enemy.tile.tileNum)
                self.after(finish_time - 100, self.move_to_tile_hp, enemy_hp_label, initiated_enemy.tile.tileNum)
                self.after(finish_time - 100, self.move_to_tile_sp, enemy_sp_label, initiated_enemy.tile.tileNum)
                self.after(finish_time - 100, self.move_to_tile_bar, enemy_hp_bar_fg, initiated_enemy.tile.tileNum)
                self.after(finish_time - 100, self.move_to_tile_bar, enemy_hp_bar_bg, initiated_enemy.tile.tileNum)

            # Get the post combat effects
            atk_effects = combat_result[12]
            def_effects = combat_result[13]

            # Clear debuffs before administering post combat effects
            player.statusNeg = []
            player.debuffs = [0, 0, 0, 0, 0]

            # Get exact changes to be enacted by post-combat effects
            damage_taken, heals_given, sp_charges = feh.end_of_combat(atk_effects, def_effects, player, targeted_enemy, savior_unit)

            # Post combat damage/healing/sp charges across the field
            for x in self.current_units[PLAYER] + self.current_units[ENEMY]:
                hp_change = 0
                if x in damage_taken:
                    hp_change -= damage_taken[x]
                if x in heals_given:
                    hp_change += heals_given[x]

                if hp_change != 0:
                    if hp_change > 0:
                        self.after(finish_time, self.animate_heal_popup, hp_change, x.tile.tileNum)
                    if hp_change < 0:
                        self.after(finish_time, self.animate_damage_popup, abs(hp_change), x.tile.tileNum)

                if x in sp_charges:
                    x.chargeSpecial(sp_charges[x])

                x_side = x.side
                x_index = self.all_units[x_side].index(x)
                x_hp_label = self.unit_hp_count_labels[x_side][x_index]
                x_hp_bar = self.unit_hp_bars_fg[x_side][x_index]
                x_sp_label = self.unit_sp_count_labels[x_side][x_index]

                hp_percentage = x.HPcur / x.visible_stats[HP]

                if x.specialCount != -1:
                    self.after(finish_time, self.set_text_val, x_sp_label, x.specialCount)

                self.after(finish_time, self.set_text_val, x_hp_label, x.HPcur)
                self.after(finish_time, self.set_hp_bar_length, x_hp_bar, hp_percentage)

            # Movement-based skills after combat
            player_tile_number = player.tile.tileNum
            enemy_tile_number = enemy.tile.tileNum

            player_move_pos = player_tile_number
            enemy_move_pos = enemy_tile_number

            if "knock_back" in player.getSkills():
                player_move_pos = player_tile_number
                enemy_move_pos = feh.final_reposition_tile(enemy_tile_number, player_tile_number)

                if not (self.map.tiles[enemy_move_pos].hero_on is None and feh.can_be_on_tile(self.map.tiles[enemy_move_pos], enemy.move)):
                    enemy_move_pos = -1

            elif "drag_back" in player.getSkills():
                player_move_pos = feh.final_reposition_tile(player_tile_number, enemy_tile_number)
                enemy_move_pos = player_tile_number

            elif "lunge" in player.getSkills():
                player_move_pos = enemy_tile_number
                enemy_move_pos = player_tile_number

            elif "hit_and_run" in player.getSkills():
                player_move_pos = feh.final_reposition_tile(player_tile_number, enemy_tile_number)
                enemy_move_pos = enemy_tile_number

            # Ensure tiles do not have any heroes/structures/invalid terrain
            if player_move_pos != -1 and enemy_move_pos != -1 and player.HPcur != 0:
                if self.map.tiles[player_move_pos].hero_on is not None and (self.map.tiles[player_move_pos].hero_on != player and self.map.tiles[player_move_pos].hero_on != enemy):
                    player_move_pos = -1
                elif self.map.tiles[enemy_move_pos].hero_on is not None and (self.map.tiles[enemy_move_pos].hero_on != player and self.map.tiles[enemy_move_pos].hero_on != enemy):
                    enemy_move_pos = -1
                elif not feh.can_be_on_tile(self.map.tiles[player_move_pos], player.move):
                    player_move_pos = -1
                elif not feh.can_be_on_tile(self.map.tiles[enemy_move_pos], player.move):
                    enemy_move_pos = -1

            # If tiles are still valid, make moves
            if player_move_pos != -1 and enemy_move_pos != -1 and player.HPcur != 0 and not savior_unit:
                player.tile.hero_on = None
                enemy.tile.hero_on = None

                player.tile = self.map.tiles[player_move_pos]
                enemy.tile = self.map.tiles[enemy_move_pos]

                player.tile.hero_on = player
                enemy.tile.hero_on = enemy

                self.move_visuals_to_tile(S, item_index, player_move_pos)
                self.move_visuals_to_tile(E_side, enemy_index, enemy_move_pos)

            # EXTRA ACTION FROM COMBAT

            # Share Spoils
            if Status.ShareSpoils in initiated_enemy.statusNeg and initiated_enemy.HPcur == 0:
                galeforce_triggered = True

            elif "lone_wolf" in player.getSkills() and player.assistTargetedOther == 0 and player.assistTargetedSelf == 0:
                player.nonspecial_galeforce_triggered = True
                galeforce_triggered = True

            elif "override" in player.getSkills() and num_aoe_targets >= 2:
                player.nonspecial_galeforce_triggered = True
                galeforce_triggered = True

            # Calling Circle goes here...?

            # Galeforce conditions
            # Should trigger if:
            # - Hasn't already triggered
            # - Special is currently Galeforce
            # - Sp Count is at 0
            elif "galeforce" in player.getSkills() and player.specialCount == 0 and not player.special_galeforce_triggered:
                player.special_galeforce_triggered = True
                galeforce_triggered = True
                player.specialCount = player.specialMax
                self.after(finish_time, self.update_unit_graphics, player)

            # If the dragged unit dies in combat, remove them from the map
            if player.HPcur == 0:
                self.after(finish_time, set_unit_death, player)

                # remove from list of units
                if player.side == 0:
                    self.current_units[PLAYER].remove(player)
                else:
                    self.current_units[ENEMY].remove(player)

                # take unit off map
                player.tile.hero_on = None

                # self.after(finish_time, clear_banner)
                self.after(finish_time, self.unit_status.clear)

            # If the foe dies in combat, remove them from the map
            if initiated_enemy.HPcur == 0:
                self.after(finish_time, set_unit_death, initiated_enemy)

                # remove from list of units
                if initiated_enemy.side == 0:
                    self.current_units[PLAYER].remove(initiated_enemy)
                else:
                    self.current_units[ENEMY].remove(initiated_enemy)

                # take unit off map
                initiated_enemy.tile.hero_on = None

            # Remove forecast
            self.after(finish_time, self.extras.clear_forecast_banner)

            # After animation complete. re-enable user control
            self.after(finish_time, animation_done)

        # ASSIIIIIIIIIIIIIIIIIIIIIIST!!!!!!!!!!!!!!!!!!!!
        elif is_targeting_object and is_targeting_hero and destination_unit.isAllyOf(release_unit):
            action = ASSIST

            player = destination_unit
            ally = release_unit

            player.assistTargetedOther += 1
            ally.assistTargetedSelf += 1

            # Determines if unit should keep their action upon using an assist
            assist_galeforce = False

            ally_index = self.all_units[S].index(ally)

            ally_sprite = self.unit_sprites[S][ally_index]
            ally_grayscale = self.unit_sprites_gs[S][ally_index]
            ally_weapon_icon = self.unit_weapon_icon_sprites[S][ally_index]
            ally_hp_label = self.unit_hp_count_labels[S][ally_index]
            ally_sp_label = self.unit_sp_count_labels[S][ally_index]
            ally_hp_bar_fg = self.unit_hp_bars_fg[S][ally_index]
            ally_hp_bar_bg = self.unit_hp_bars_bg[S][ally_index]

            unit_final_position = -1
            ally_final_position = -1

            playerSkills = player.getSkills()

            if "repo" in player.assist.effects:

                # Tiles currently occupied by unit and ally
                unit_tile_num = player.tile.tileNum
                ally_tile_num = ally.tile.tileNum

                # Where each unit is moving to
                unit_final_position = player.tile.tileNum
                ally_final_position = feh.final_reposition_tile(unit_tile_num, ally_tile_num)

            elif "draw" in player.assist.effects:
                unit_tile_num = player.tile.tileNum
                ally_tile_num = ally.tile.tileNum

                unit_final_position = feh.final_reposition_tile(unit_tile_num, ally_tile_num)
                ally_final_position = unit_tile_num

            elif "swap" in player.assist.effects:
                unit_final_position = ally.tile.tileNum
                ally_final_position = player.tile.tileNum

            elif "pivot" in player.assist.effects:
                unit_tile_num = player.tile.tileNum
                ally_tile_num = ally.tile.tileNum

                ally_final_position = ally.tile.tileNum
                unit_final_position = feh.final_reposition_tile(ally_tile_num, unit_tile_num)

            elif "smite" in player.assist.effects:
                unit_tile_num = player.tile.tileNum
                ally_tile_num = ally.tile.tileNum

                skip_over = feh.final_reposition_tile(ally_tile_num, unit_tile_num)
                final_dest = feh.final_reposition_tile(skip_over, ally_tile_num)

                valid_shove = False
                valid_smite = False

                if skip_over != -1:
                    unit_on_dest = self.map.tiles[skip_over].hero_on is not None and self.map.tiles[skip_over].hero_on != player
                    can_traverse_dest = feh.can_be_on_tile(self.map.tiles[skip_over], ally.move)

                    valid_shove = not unit_on_dest and can_traverse_dest

                if final_dest != -1:
                    unit_on_dest = self.map.tiles[final_dest].hero_on is not None and self.map.tiles[final_dest].hero_on != player
                    can_traverse_dest = feh.can_be_on_tile(self.map.tiles[final_dest], ally.move)

                    foe_on_skip = self.map.tiles[skip_over].hero_on is not None and self.map.tiles[skip_over].hero_on.side != player.side
                    can_skip = self.map.tiles[skip_over].terrain != 4 and not foe_on_skip

                    valid_smite = not unit_on_dest and can_traverse_dest and can_skip

                final_pos = -1
                if valid_shove and not valid_smite:
                    final_pos = skip_over
                if valid_smite:
                    final_pos = final_dest

                unit_final_position = player.tile.tileNum
                ally_final_position = final_pos

            elif "shove" in player.assist.effects:
                unit_tile_num = player.tile.tileNum
                ally_tile_num = ally.tile.tileNum

                unit_final_position = player.tile.tileNum
                ally_final_position = feh.final_reposition_tile(ally_tile_num, unit_tile_num)

            # Staff Healing
            elif "heal" in player.assist.effects:
                unit_final_position = player.tile.tileNum
                ally_final_position = ally.tile.tileNum

                hp_healed_ally = player.assist.effects["heal"]
                hp_healed_self = 0

                panic_factor = 1
                if Status.Panic in player.statusNeg: panic_factor = -1
                if Status.NullPanic in player.statusPos: panic_factor = 1
                self_atk_stat = player.visible_stats[ATK] + player.buffs[ATK] * panic_factor + player.debuffs[ATK]

                # Reconcile
                if "heal_self" in player.assist.effects:
                    hp_healed_self = player.assist.effects["heal_self"]

                # Martyr
                if player.assist.effects["heal"] == -3:
                    dmg_taken = player.visible_stats[HP] - player.HPcur
                    hp_healed_ally = dmg_taken + 7
                    hp_healed_self = dmg_taken // 2

                # Martyr+
                if player.assist.effects["heal"] == -49:
                    dmg_taken = player.visible_stats[HP] - player.HPcur
                    hp_healed_ally = max(dmg_taken + self_atk_stat // 2, 7)
                    hp_healed_self = dmg_taken // 2

                # Recover+
                if player.assist.effects["heal"] == -10:
                    hp_healed_ally = max(self_atk_stat // 2 + 10, 15)

                # Rehabilitate
                if player.assist.effects["heal"] == -1:
                    ally_hp_max = ally.visible_stats[HP]
                    ally_hp_cur = ally.HPcur

                    hp_healed_ally = max(7 + ally_hp_max - (2 * ally_hp_cur), 7)

                # Rehabilitate+
                if player.assist.effects["heal"] == -2:
                    ally_hp_max = ally.visible_stats[HP]
                    ally_hp_cur = ally.HPcur

                    hp_healed_ally = max(self_atk_stat // 2 - 10, 7) + max(ally_hp_max - (2 * ally_hp_cur), 0)

                if player.assist.effects["heal"] == -50:
                    hp_healed_ally = max(self_atk_stat // 2, 8)

                staff_special_triggered = False

                if player.specialCount == 0 and player.special.type == "Healing":
                    if "boost_heal" in player.special.effects:
                        hp_healed_ally += player.special.effects["boost_heal"]

                    allies_arr = self.all_units[S]
                    for x in allies_arr:
                        if x != player and x != ally and "heal_allies" in player.special.effects:
                            x_index = allies_arr.index(x)
                            x_hp_label = self.unit_hp_count_labels[S][x_index]
                            x_hp_bar = self.unit_hp_bars_fg[S][x_index]

                            x.HPcur = min(x.visible_stats[HP], x.HPcur + 10)

                            hp_percentage = x.HPcur / x.visible_stats[HP]

                            self.set_text_val(x_hp_label, x.HPcur)
                            self.set_hp_bar_length(x_hp_bar, hp_percentage)

                        if x != player:
                            if "atkBalm" in player.special.effects:
                                x.inflictStat(ATK, player.special.effects["atkBalm"])
                            if "spdBalm" in player.special.effects:
                                x.inflictStat(SPD, player.special.effects["spdBalm"])
                            if "defBalm" in player.special.effects:
                                x.inflictStat(DEF, player.special.effects["defBalm"])
                            if "resBalm" in player.special.effects:
                                x.inflictStat(RES, player.special.effects["resBalm"])

                    staff_special_triggered = True

                if "live_to_serve" in player.bskill.effects:
                    percentage = 0.25 + 0.25 * player.bskill.effects["live_to_serve"]
                    hp_healed_self += trunc(hp_healed_ally * percentage)

                ally.HPcur = min(ally.visible_stats[HP], ally.HPcur + hp_healed_ally)
                player.HPcur = min(player.visible_stats[HP], player.HPcur + hp_healed_self)

                self.animate_heal_popup(hp_healed_ally, ally.tile.tileNum)

                # Get/Update HP assets
                ally_index = self.all_units[S].index(ally)
                ally_hp_label = self.unit_hp_count_labels[S][ally_index]
                ally_hp_bar = self.unit_hp_bars_fg[S][ally_index]

                hp_percentage = ally.HPcur / ally.visible_stats[HP]

                self.set_text_val(ally_hp_label, ally.HPcur)
                self.set_hp_bar_length(ally_hp_bar, hp_percentage)

                # Display self heal (only if amount healed > 0)
                if hp_healed_self > 0:
                    self.animate_heal_popup(hp_healed_self, player.tile.tileNum)

                    player_hp_label = self.unit_hp_count_labels[S][item_index]
                    player_hp_bar_fg = self.unit_hp_bars_fg[S][item_index]

                    # Update HP assets
                    hp_percentage = player.HPcur / player.visible_stats[HP]
                    self.set_text_val(player_hp_label, player.HPcur)
                    self.set_hp_bar_length(player_hp_bar_fg, hp_percentage)

                # Charge own special for Staff assist use
                if staff_special_triggered:
                    player.specialCount = player.specialMax
                    self.set_text_val(self.unit_sp_count_labels[S][item_index], player.specialCount)
                elif player.specialCount != -1:
                    player.specialCount = max(player.specialCount - 1, 0)
                    self.set_text_val(self.unit_sp_count_labels[S][item_index], player.specialCount)

            # Dance/Sing/Play
            elif "refresh" in player.assist.effects:
                unit_final_position = player.tile.tileNum
                ally_final_position = ally.tile.tileNum

                # Grant ally another action
                self.units_to_move.append(ally)

                ally_index = self.all_units[S].index(ally)
                ally_sprite = self.unit_sprites[S][ally_index]
                ally_gs_sprite = self.unit_sprites_gs[S][ally_index]

                self.itemconfig(ally_sprite, state='normal')
                self.itemconfig(ally_gs_sprite, state='hidden')

                if "atkRefresh" in playerSkills: ally.inflictStat(ATK, playerSkills["atkRefresh"])
                if "spdRefresh" in playerSkills: ally.inflictStat(SPD, playerSkills["spdRefresh"])
                if "defRefresh" in playerSkills: ally.inflictStat(ATK, playerSkills["defRefresh"])
                if "resRefresh" in playerSkills: ally.inflictStat(SPD, playerSkills["resRefresh"])

                if "spectrumRefresh" in playerSkills:
                    i = 1
                    while i <= 4:
                        ally.inflictStat(i, playerSkills["spectrumRefresh"])
                        i += 1

            # Rally
            if "rallyAtk" in player.assist.effects:
                ally.inflictStat(ATK, player.assist.effects["rallyAtk"])
            if "rallySpd" in player.assist.effects:
                ally.inflictStat(SPD, player.assist.effects["rallySpd"])
            if "rallyDef" in player.assist.effects:
                ally.inflictStat(DEF, player.assist.effects["rallyDef"])
            if "rallyRes" in player.assist.effects:
                ally.inflictStat(RES, player.assist.effects["rallyRes"])

            for local_ally in [ally] + feh.allies_within_n(ally, 2):
                if local_ally != cur_unit:
                    if "rallyUpAtk" in player.assist.effects:
                        local_ally.inflictStat(ATK, player.assist.effects["rallyUpAtk"])
                    if "rallyUpSpd" in player.assist.effects:
                        local_ally.inflictStat(SPD, player.assist.effects["rallyUpSpd"])
                    if "rallyUpDef" in player.assist.effects:
                        local_ally.inflictStat(DEF, player.assist.effects["rallyUpDef"])
                    if "rallyUpRes" in player.assist.effects:
                        local_ally.inflictStat(RES, player.assist.effects["rallyUpRes"])

            # Reciprocal Aid
            if "rec_aid" in player.assist.effects:
                unit_final_position = player.tile.tileNum
                ally_final_position = ally.tile.tileNum

                switch_hp = abs(player.HPcur - ally.HPcur)

                ally_HP_result = min(ally.visible_stats[HP], player.HPcur)
                player_HP_result = min(player.visible_stats[HP], ally.HPcur)

                if player_HP_result > player.HPcur:
                    self.animate_heal_popup(switch_hp, player.tile.tileNum)
                    self.animate_damage_popup(switch_hp, ally.tile.tileNum)
                else:
                    self.animate_heal_popup(switch_hp, ally.tile.tileNum)
                    self.animate_damage_popup(switch_hp, player.tile.tileNum)

                player.HPcur = player_HP_result
                ally.HPcur = ally_HP_result
                self.set_hp_visual(player, player.HPcur)
                self.set_hp_visual(ally, ally.HPcur)

            # Ardent Sacrifice
            if "ardent_sac" in player.assist.effects:
                unit_final_position = player.tile.tileNum
                ally_final_position = ally.tile.tileNum

                ally.HPcur = min(ally.visible_stats[HP], ally.HPcur + 10)
                player.HPcur = max(1, player.HPcur - 10)

                self.animate_heal_popup(10, ally.tile.tileNum)
                self.animate_damage_popup(10, player.tile.tileNum)

                self.set_hp_visual(player, player.HPcur)
                self.set_hp_visual(ally, ally.HPcur)

            # Sacrifice
            if "sacrifice" in player.assist.effects:
                unit_final_position = player.tile.tileNum
                ally_final_position = ally.tile.tileNum

                capped_hp = min(player.HPcur - 1, ally.visible_stats[HP] - ally.HPcur)

                player.HPcur -= capped_hp
                ally.HPcur += capped_hp

                self.animate_heal_popup(capped_hp, ally.tile.tileNum)
                self.animate_damage_popup(capped_hp, player.tile.tileNum)

                self.set_hp_visual(player, player.HPcur)
                self.set_hp_visual(ally, ally.HPcur)

            # Harsh Command
            if "harsh_comm" in player.assist.effects:
                unit_final_position = player.tile.tileNum
                ally_final_position = ally.tile.tileNum

                i = 1
                while i < len(ally.debuffs):
                    ally.buffs[i] = max(abs(ally.debuffs[i]), ally.buffs[i])
                    ally.debuffs[i] = 0
                    i += 1

            # Perform assist movements
            if unit_final_position != -1 and ally_final_position != -1:
                player.tile.hero_on = None
                ally.tile.hero_on = None

                player.tile = self.map.tiles[unit_final_position]
                ally.tile = self.map.tiles[ally_final_position]

                self.map.tiles[unit_final_position].hero_on = player
                self.map.tiles[ally_final_position].hero_on = ally

                self.move_visuals_to_tile(S, item_index, unit_final_position)
                self.move_visuals_to_tile(S, ally_index, ally_final_position)

            # Clear status effects, action taken
            player.statusNeg = []
            player.debuffs = [0, 0, 0, 0, 0]
            #set_banner(player)

            # Skills that grant effects when assist skills are used

            # Link skills, or other effects that trigger after assist use
            if player.assist.type == "Move":
                playerSkills = player.getSkills()
                allySkills = ally.getSkills()

                if "shigureLink" in playerSkills or "shigureLink" in allySkills:
                    for hero in [player, ally]:
                        hero.HPcur = min(hero.visible_stats[HP], ally.HPcur + 10)
                        self.animate_heal_popup(10, hero.tile.tileNum)

                        # Get/Update HP assets
                        hero_index = self.all_units[S].index(hero)
                        hero_hp_label = self.unit_hp_count_labels[S][hero_index]
                        hero_hp_bar = self.unit_hp_bars_fg[S][hero_index]

                        hp_percentage = hero.HPcur / hero.visible_stats[HP]
                        self.set_text_val(hero_hp_label, hero.HPcur)
                        self.set_hp_bar_length(hero_hp_bar, hp_percentage)

                if "atkSpdLink" in playerSkills or "atkSpdLink" in allySkills:
                    stat_boost = max(playerSkills.get("atkSpdLink", 0), allySkills.get("atkSpdLink", 0))

                    for hero in [player, ally]:
                        hero.inflictStat(ATK, stat_boost * 2)
                        hero.inflictStat(SPD, stat_boost * 2)

                if "atkDefLink" in playerSkills or "atkDefLink" in allySkills:
                    stat_boost = max(playerSkills.get("atkDefLink", 0), allySkills.get("atkDefLink", 0))

                    for hero in [player, ally]:
                        hero.inflictStat(ATK, stat_boost * 2)
                        hero.inflictStat(DEF, stat_boost * 2)

                if "atkResLink" in playerSkills or "atkResLink" in allySkills:
                    stat_boost = max(playerSkills.get("atkResLink", 0), allySkills.get("atkResLink", 0))

                    for hero in [player, ally]:
                        hero.inflictStat(ATK, stat_boost * 2)
                        hero.inflictStat(RES, stat_boost * 2)

                if "spdResLink" in playerSkills or "spdResLink" in allySkills:
                    stat_boost = max(playerSkills.get("spdResLink", 0), allySkills.get("spdResLink", 0))

                    for hero in [player, ally]:
                        hero.inflictStat(SPD, stat_boost * 2)
                        hero.inflictStat(RES, stat_boost * 2)

                if "defResLink" in playerSkills or "defResLink" in allySkills:
                    stat_boost = max(playerSkills.get("defResLink", 0), allySkills.get("defResLink", 0))

                    for hero in [player, ally]:
                        hero.inflictStat(DEF, stat_boost * 2)
                        hero.inflictStat(RES, stat_boost * 2)

                if "atkSpdLinkW" in playerSkills or "atkSpdLinkW" in allySkills:
                    affected_units = [player, ally]

                    for hero in affected_units:
                        hero.inflictStat(ATK, 6)
                        hero.inflictStat(SPD, 6)

                if "laslowShmovement" in playerSkills or "laslowShmovement" in allySkills:
                    affected_units = [player, ally]
                    affected_units += feh.allies_within_n(player, 2)
                    affected_units += feh.allies_within_n(ally, 2)

                    affected_units = list(set(affected_units))

                    for hero in affected_units:
                        hero.inflictStat(ATK, 4)
                        hero.inflictStat(SPD, 4)
                        hero.inflictStat(DEF, 4)
                        hero.inflictStat(RES, 4)

                # Future Vision II (L!Lucina)
                if "lucinaRefresh" in playerSkills:
                    i = 1
                    affected_units = []

                    while i <= 4 and not affected_units:
                        affected_units += feh.foes_within_n(player, i)
                        affected_units += feh.foes_within_n(ally, i)

                        affected_units = list(set(affected_units))

                        for foe in affected_units:
                            foe.inflictStat(ATK, -7)
                            foe.inflictStat(DEF, -7)

                        i += 1

                if "peppaPigAdversary" in playerSkills or "peppaPigAdversary" in allySkills:
                    for hero in [player, ally]:
                        hero.inflictStatus(Status.Pursual)

            # Feint Skills
            if player.assist.type == "Rally":
                playerSkills = player.getSkills()
                allySkills = ally.getSkills()

                valid_foes = []

                for hero in [player, ally]:
                    foes = feh.foes_within_n_cardinal(hero, 1)
                    for foe in foes:
                        if foe not in valid_foes:
                            valid_foes.append(foe)

                if "spdFeint" in playerSkills or "spdFeint" in allySkills:
                    stat_debuff = max(playerSkills.get("spdFeint", 0), allySkills.get("spdFeint", 0))

                    for foe in valid_foes:
                        foe.inflictStat(SPD, -stat_debuff)

                if "defFeint" in playerSkills or "defFeint" in allySkills:
                    stat_debuff = max(playerSkills.get("defFeint", 0), allySkills.get("defFeint", 0))

                    for foe in valid_foes:
                        foe.inflictStat(DEF, -stat_debuff)

            # Keep your turn after using assist
            if ("selfAssistRefresh" in player.assist.effects or "lucinaRefresh" in player.assist.effects) and player.assistTargetedOther == 1:
                galeforce_triggered = True

            self.extras.clear_forecast_banner()

        # DESTROOOOOOOOOOOOOOOOYYYY!!!!!!!!!!!!!!!!!
        elif is_targeting_object and not is_targeting_hero and is_targeting_struct and release_struct.health > 0:
            action = BREAK

            # Break selected wall
            release_struct.health -= 1

            # Refresh all walls
            self.refresh_walls()

            self.extras.clear_forecast_banner()

        # DO NOTHIIIIIIIIIIIIIIING!!!!!
        else:
            action = MOVE

        # If any action was taken, manage those things here
        if action != INVALID:

            # Clears debuffs if no action has occured, or
            if action != ATTACK and action != ASSIST:
                cur_unit.statusNeg = []
                cur_unit.debuffs = [0, 0, 0, 0, 0]

                self.unit_status.update_from_obj(cur_unit)

            if action == ASSIST:
                self.unit_status.update_from_obj(cur_unit)

            if action != MOVE and not galeforce_triggered and cur_unit.canto_ready and cur_unit.HPcur != 0:

                canto_moves = feh.get_canto_moves(cur_unit, self.current_units[S], self.current_units[S-1], self.distance, self.spaces_allowed, action, self.turn_info[0])[2]

                # If there are any valid tiles to use Canto to, activate canto mode
                if canto_moves:
                    self.canto = cur_unit
                    cur_unit.canto_ready = False # Canto officially used

                    # moving again with canto removes all debuffs, because sure why not
                    for foe in self.current_units[S-1]:
                        if "cantoControlW" in foe.getSkills() and cur_unit in feh.foes_within_n(foe, 4):
                            cur_unit.inflictStatus(Status.CantoControl)

                    # Check Canto Moves after Canto Control is given out
                    moves_obj_array = feh.get_canto_moves(cur_unit, self.current_units[S], self.current_units[S-1], self.distance, self.spaces_allowed, action, self.turn_info[0])[2]

                    if moves_obj_array:
                        # Hide Swap buttons
                        #self.itemconfig(swap_spaces, fill="#282424")
                        #self.itemconfig(swap_spaces_text, fill="#282424")

                        # Draw Blue Spaces for Canto Movement
                        for m in moves_obj_array:
                            x_comp = m.destination % 6
                            y_comp = m.destination // 6
                            cur_pixel_offset_x = x_comp * 90
                            cur_pixel_offset_y = (7 - y_comp) * 90

                            tile_photo = self.move_tile_photos[0]
                            if m.is_warp:
                                tile_photo = self.move_tile_photos[1]

                            # creates new blue tile, layered under player
                            def create_tile(x1, y1, z1):

                                curTile = self.create_image(x1, y1, anchor=tk.NW, image=z1)
                                self.canto_tile_imgs.append(curTile)
                                self.tag_lower(curTile, sdd['item'])

                            x1 = cur_pixel_offset_x
                            y1 = cur_pixel_offset_y
                            z1 = tile_photo
                            self.after(finish_time, create_tile, x1, y1, z1)
                    else:
                        self.canto = None


            elif not cur_unit.canto_ready:
                self.canto = None

                for blue_tile_id in self.canto_tile_imgs:
                    self.delete(blue_tile_id)
                self.canto_tile_imgs.clear()

        cur_hero = destination_unit

        # Add current move to mapstate history
        # Handles actions once move is complete
        if successful_move and cur_hero in self.units_to_move and self.canto is None:

            # If not galeforce, remove unit from units who can act
            if not galeforce_triggered:
                self.units_to_move.remove(cur_hero)

                if self.units_to_move and cur_unit.HPcur != 0:

                    self.after(finish_time, set_unit_actability, cur_unit)

            # Capture the mapstate
            mapstate = create_mapstate(self.all_units[PLAYER], self.all_units[ENEMY], self.map, self.units_to_move, self.turn_info[0])

            if self.units_to_move:
                self.map_states.append(mapstate)

            # If this is the first valid move, disable swap button and enable undo button

            if len(self.map_states) > 1:
                self.button_frame.swap_spaces_button.config(state="disabled")
                self.button_frame.undo_button.config(state="normal")

        # Enable undoing even after canto
        if self.canto:
            self.button_frame.swap_spaces_button.config(state="disabled")
            self.button_frame.undo_button.config(state="normal")

        # cause next phase to start either immediately or after combat

        if not self.units_to_move:
            if not self.animation:
                self.next_phase()

            if self.animation:
                self.after(finish_time, self.next_phase)

        self.drag_data = None

        return

    def on_double_click(self, event):
        x_comp = event.x // self.TILE_SIZE
        y_comp = ((self.GAMEPLAY_WIDTH - event.y) // 90)
        selected_tile = x_comp + 6 * y_comp

        if not self.running:
            if selected_tile in self.unit_drag_points:
                self.unit_drag_points[selected_tile].hero = None
                self.refresh_units_prep()

                self.unit_status.clear()

            return

        x, y = event.x, event.y

        x_comp = event.x // 90
        y_comp = ((720 - event.y) // 90)
        selected_tile = x_comp + 6 * y_comp
        cur_hero = self.map.tiles[selected_tile].hero_on

        if cur_hero is not None and not self.swap_mode:

            S = cur_hero.side

            if S == self.turn_info[1]:
                item_index = self.all_units[S].index(cur_hero)
                if cur_hero in self.units_to_move:
                    self.units_to_move.remove(cur_hero)

                    cur_hero.statusNeg = []
                    cur_hero.debuffs = [0, 0, 0, 0, 0]
                    #set_banner(cur_hero)

                    if cur_hero == self.canto:
                        self.canto = None

                        for blue_tile_id in self.canto_tile_imgs:
                            self.delete(blue_tile_id)
                        self.canto_tile_imgs.clear()

                    self.itemconfig(self.unit_sprites[S][item_index], state='hidden')
                    self.itemconfig(self.unit_sprites_gs[S][item_index], state='normal')

                    if not self.units_to_move:
                        self.next_phase()

                    else:
                        mapstate = create_mapstate(self.all_units[PLAYER], self.all_units[ENEMY], self.map, self.units_to_move, self.turn_info[0])
                        self.map_states.append(mapstate)

        return

    def on_right_click(self, event):
        x_comp = event.x // self.TILE_SIZE
        y_comp = ((self.GAMEPLAY_WIDTH - event.y) // 90)
        selected_tile = x_comp + 6 * y_comp

        if not self.running:
            if selected_tile in self.unit_drag_points and self.unit_drag_points[selected_tile].hero and self.unit_drag_points[selected_tile].hero.epithet != "Generic":
                self.hero_listing.create_edit_popup_from_unit(self.unit_drag_points[selected_tile].hero)
                self.hero_listing.creation_make_button.config(text="Save", command=partial(self.place_unit_object, event.x, event.y))
                self.hero_listing.creation_build_field.forget()
                self.hero_listing.creation_make_text.forget()

    def setup_with_file(self, json_path):
        with open(json_path, encoding="utf-8") as read_file: json_data = json.load(read_file)

        # Specify map terrain, structures, and starting positions with JSON file.
        self.map.define_map(json_data)

        if "mode" in json_data:
            if json_data["mode"] == "arena":
                self.game_mode = hero.GameMode.Arena
            if json_data["mode"] == "aether":
                self.game_mode = hero.GameMode.AetherRaids

        # Liquid
        liquid_image = Image.open("CombatSprites/" + self.map.liquid_texture)
        self.liquid = liquid_photo = ImageTk.PhotoImage(liquid_image)

        self.create_image(0, 0, anchor=tk.NW, image=liquid_photo)
        self.create_image(0, 90 * 4, anchor=tk.NW, image=liquid_photo)

        # Terrain
        map_path = json_path.replace(".json", ".png")
        map_path = map_path.replace("Normal_", "").replace("Hard_", "").replace("Lunatic_", "")

        map_image = Image.open(map_path)
        self.terrain = map_photo = ImageTk.PhotoImage(map_image)
        self.create_image(0, 0, anchor=tk.NW, image=map_photo)

        # AR Field Offense
        if self.game_mode == hero.GameMode.AetherRaids:
            offense = Image.open("Maps/Aether Raids (Templates)/Field_Offense.png")
            self.offense_piece = ImageTk.PhotoImage(offense)
            self.create_image(-70, 610, anchor=tk.NW, image=self.offense_piece)

        # Walls
        self.refresh_walls()

        # Turn info
        self.turn_info = [1, PLAYER, 50]

        # Map States
        self.map_states = []
        self.initial_mapstate = None

        self.unit_drag_points.clear()

        for starting_space in self.map.player_start_spaces:
            cur_tile = self.create_image(0, 0, image=self.move_tile_photos[0])
            self.starting_tile_photos.append(cur_tile)
            self.move_to_tile(cur_tile, starting_space)

            self.unit_drag_points[starting_space] = _DragPoint(tile_num=starting_space, modifiable=True, side=PLAYER)

        for starting_space in self.map.enemy_start_spaces:
            cur_tile = self.create_image(0, 0, image=self.move_tile_photos[2])
            self.starting_tile_photos.append(cur_tile)
            self.move_to_tile(cur_tile, starting_space)

            self.unit_drag_points[starting_space] = _DragPoint(tile_num=starting_space, modifiable=True, side=ENEMY)

        if self.game_mode == hero.GameMode.Arena or self.game_mode == hero.GameMode.AetherRaids:
            return

        # Load enemies from JSON data
        i = 0

        while i < len(json_data["enemyData"]):
            if json_data["enemyData"][i]["name"] in hero.generics:
                curEnemy = makeGeneric(json_data["enemyData"][i]["name"])
            else:
                curEnemy = makeHero(json_data["enemyData"][i]["name"])

            curEnemy.allySupport = None

            curEnemy.side = 1
            curEnemy.set_rarity(json_data["enemyData"][i]["rarity"])
            #curEnemy.set_level_enemy(1, json_data["enemyData"][i]["level"], difficulty) YOU WILL WORK ONE DAY
            curEnemy.set_level(json_data["enemyData"][i]["level"])

            if "weapon" in json_data["enemyData"][i]:
                curWpn = makeWeapon(json_data["enemyData"][i]["weapon"])
                curEnemy.set_skill(curWpn, WEAPON)

            if "assist" in json_data["enemyData"][i]:
                curAssist = makeAssist(json_data["enemyData"][i]["assist"])
                curEnemy.set_skill(curAssist, ASSIST)

            if "special" in json_data["enemyData"][i]:
                curSpecial = makeSpecial(json_data["enemyData"][i]["special"])
                curEnemy.set_skill(curSpecial, SPECIAL)

            if "askill" in json_data["enemyData"][i]:
                curASkill = makeSkill(json_data["enemyData"][i]["askill"])
                curEnemy.set_skill(curASkill, ASKILL)

            if "bskill" in json_data["enemyData"][i]:
                curBSkill = makeSkill(json_data["enemyData"][i]["bskill"])
                curEnemy.set_skill(curBSkill, BSKILL)

            if "cskill" in json_data["enemyData"][i]:
                curCSkill = makeSkill(json_data["enemyData"][i]["cskill"])
                curEnemy.set_skill(curCSkill, CSKILL)

            if "alt_stats" in json_data["enemyData"][i]:
                curEnemy.visible_stats = json_data["enemyData"][i]["alt_stats"]
                j = 0
                while j < 5:
                    curEnemy.visible_stats[j] += curEnemy.skill_stat_mods[j]
                    curEnemy.visible_stats[j] = max(min(curEnemy.visible_stats[j], 99), 0)
                    j += 1

                curEnemy.HPcur = curEnemy.visible_stats[HP]

            self.unit_drag_points[self.map.enemy_start_spaces[i]].hero = curEnemy
            i += 1


    def move_to_tile(self, sprite, tile_num):
        x_move = 45 + 90 * (tile_num % 6)
        y_move = 45 + 90 * (7 - (tile_num // 6))

        self.coords(sprite, x_move, y_move)

    def move_to_tile_wp(self, sprite, tile_num):
        x_move = 45 + 90 * (tile_num % 6)
        y_move = 45 + 90 * (7 - (tile_num // 6))

        self.coords(sprite, x_move - 45, y_move - 45)

    def move_to_tile_sp(self, sprite, tile_num):
        x_move = 45 + 90 * (tile_num % 6)
        y_move = 45 + 90 * (7 - (tile_num // 6))

        self.coords(sprite, x_move - 33, y_move - 7)

    def move_to_tile_hp(self, sprite, tile_num):
        x_move = 45 + 90 * (tile_num % 6)
        y_move = 45 + 90 * (7 - (tile_num // 6))

        self.coords(sprite, x_move - 33, y_move + 36)

    def move_to_tile_bar(self, sprite, tile_num):
        x_move = 45 + 90 * (tile_num % 6)
        y_move = 45 + 90 * (7 - (tile_num // 6))

        self.moveto(sprite, x_move - 18, y_move + 29)

    def move_visuals_to_tile(self, side, index, tile_int):
        self.move_to_tile(self.unit_sprites[side][index], tile_int)
        self.move_to_tile(self.unit_sprites_gs[side][index], tile_int)
        self.move_to_tile(self.unit_sprites_trans[side][index], tile_int)
        self.move_to_tile(self.unit_sprites_gs_trans[side][index], tile_int)
        self.move_to_tile_wp(self.unit_weapon_icon_sprites[side][index], tile_int)
        self.move_to_tile_sp(self.unit_sp_count_labels[side][index], tile_int)
        self.move_to_tile_hp(self.unit_hp_count_labels[side][index], tile_int)
        self.move_to_tile_bar(self.unit_hp_bars_bg[side][index], tile_int)
        self.move_to_tile_bar(self.unit_hp_bars_fg[side][index], tile_int)

    def set_hp_visual(self, unit, cur_HP):
        S = unit.side
        unit_index = self.all_units[S].index(unit)
        unit_hp_label = self.unit_hp_count_labels[S][unit_index]
        unit_hp_bar = self.unit_hp_bars_fg[S][unit_index]

        hp_percentage = cur_HP / unit.visible_stats[HP]

        self.set_text_val(unit_hp_label, cur_HP)
        self.set_hp_bar_length(unit_hp_bar, hp_percentage)

    # Sets unit's HP/Special Count to what they are currently
    def refresh_unit_visuals(self, side, index):
        unit = self.all_units[side][index]
        unit_hp_label = self.unit_hp_count_labels[side][index]
        unit_sp_label = self.unit_sp_count_labels[side][index]
        unit_hp_bar = self.unit_hp_bars_fg[side][index]

        # HP Count
        self.itemconfig(unit_hp_label, text=str(int(unit.HPcur)))

        # Sp Count
        if unit.specialCount != -1:
            self.itemconfig(unit_sp_label, text=str(int(unit.specialCount)))

        # HP Bar
        hp_percentage = unit.HPcur / unit.visible_stats[HP]
        new_length = int(60 * hp_percentage)

        if new_length == 0:
            self.itemconfig(unit_hp_bar, state='hidden')
            return

        coords = self.coords(unit_hp_bar)

        coords[2] = coords[0] + new_length

        self.coords(unit_hp_bar, coords)

    # Update unit position graphics, when unit object has just been transferred to onto a new space
    def update_unit_graphics(self, unit):
        S = unit.side
        unit_index = self.all_units[S].index(unit)
        cur_tile = unit.tile.tileNum

        self.move_visuals_to_tile(S, unit_index, cur_tile)

        '''
        unit_sprite = sprite_IDs[S][unit_index]
        unit_gs_sprite = grayscale_IDs[S][unit_index]
        unit_wp_sprite = weapon_IDs[S][unit_index]
        unit_hp_label = hp_labels[S][unit_index]
        unit_sp_label = special_labels[S][unit_index]
        unit_hp_bar_fg = hp_bar_fgs[S][unit_index]
        unit_hp_bar_bg = hp_bar_bgs[S][unit_index]

        move_to_tile(canvas, unit_sprite, cur_tile)
        move_to_tile(canvas, unit_gs_sprite, cur_tile)
        move_to_tile_wp(canvas, unit_wp_sprite, cur_tile)
        move_to_tile_hp(canvas, unit_hp_label, cur_tile)
        move_to_tile_sp(canvas, unit_sp_label, cur_tile)
        move_to_tile_fg_bar(canvas, unit_hp_bar_fg, cur_tile)
        move_to_tile_fg_bar(canvas, unit_hp_bar_bg, cur_tile)
        '''

        self.itemconfig(self.unit_weapon_icon_sprites[S][unit_index], state='normal')
        self.itemconfig(self.unit_hp_count_labels[S][unit_index], state='normal')
        self.itemconfig(self.unit_sp_count_labels[S][unit_index], state='normal')

        self.itemconfig(self.unit_hp_bars_fg[S][unit_index], state='normal')
        self.itemconfig(self.unit_hp_bars_bg[S][unit_index], state='normal')

        # I don't know why, when hiding the HP bars, they are moved really far away
        # These lines place them back to the right place
        self.move_to_tile_bar(self.unit_hp_bars_fg[S][unit_index], cur_tile)
        self.move_to_tile_bar(self.unit_hp_bars_bg[S][unit_index], cur_tile)

        if unit.specialCount != -1:
            self.set_text_val(self.unit_sp_count_labels[S][unit_index], unit.specialCount)
        #else:
        #    self.set_text_val(self.unit_sp_count_labels[S][unit_index], 999)

        self.set_hp_visual(unit, unit.HPcur)

        if unit in self.units_to_move or unit.side != self.turn_info[1]:
            self.itemconfig(self.unit_sprites[S][unit_index], state='normal')
            self.itemconfig(self.unit_sprites_gs[S][unit_index], state='hidden')
        else:
            self.itemconfig(self.unit_sprites[S][unit_index], state='hidden')
            self.itemconfig(self.unit_sprites_gs[S][unit_index], state='normal')

    def refresh_walls(self):
        self.wall_photos.clear()
        self.wall_sprites.clear()

        wall_texture = Image.open("CombatSprites/" + self.map.wall_texture)

        for tile in self.map.tiles:
            if tile.structure_on and tile.structure_on.struct_type == 0:
                # crop different parts of wall depending on:
                # - other wall objects in cardinal directions
                # - health of the wall
                wall_health = tile.structure_on.health
                wall_health_offset = 0
                if wall_health == 2:
                    wall_health_offset = 182
                if wall_health == 1:
                    wall_health_offset = 364

                wall_type = 0
                iterator = 1

                for adj_tile in [tile.north, tile.south, tile.east, tile.west]:

                    if adj_tile is not None and adj_tile.structure_on is not None and adj_tile.structure_on.struct_type == 0 and adj_tile.structure_on.health != 0:
                        wall_type += iterator

                    iterator *= 2

                cur_crop = list(wall_crops[wall_type])

                # Singleton wall is placed going downwards
                if wall_type == 0:
                    cur_crop[1] += wall_health_offset
                    cur_crop[3] += wall_health_offset
                else:
                    cur_crop[0] += wall_health_offset
                    cur_crop[2] += wall_health_offset

                if wall_health == 0:
                    cur_crop = (1639, 547, 1818, 726)

                cur_wall = wall_texture.crop(cur_crop)

                cur_wall = cur_wall.resize((90, 90), Image.LANCZOS)
                cur_photo = ImageTk.PhotoImage(cur_wall)

                img = self.create_image(90, 90, anchor=tk.CENTER, image=cur_photo)

                self.wall_photos.append(cur_photo)
                self.wall_sprites.append(img)

                self.move_to_tile(img, tile.tileNum)

            elif tile.structure_on and tile.structure_on.struct_type != 0:
                struct = tile.structure_on

                SIDE_NONEXCLUSIVE_AR_STRUCTS = ["Fortress", "Bolt Tower", "Tactics Room", "Healing Tower", "Panic Manor", "Catapult", "Light Shrine", "Dark Shrine", "Calling Circle"]


                if struct.struct_type == PLAYER + 1:
                    image_path = "CombatSprites/AR Structures/" + struct.name.replace(" ", "_") + ".png"

                else:
                    if struct.name in SIDE_NONEXCLUSIVE_AR_STRUCTS or "School" in struct.name:
                        image_path = "CombatSprites/AR Structures/" + struct.name.replace(" ", "_") + "_Enemy.png"
                    else:
                        image_path = "CombatSprites/AR Structures/" + struct.name.replace(" ", "_") + ".png"


                if struct.health != 0:
                    struct_image = Image.open(image_path)
                    struct_image = struct_image.resize((85, 85))
                else:
                    struct_image = wall_texture.crop((1639, 547, 1818, 726))
                    struct_image = struct_image.resize((90, 90))


                struct_photo = ImageTk.PhotoImage(struct_image)

                struct_sprite = self.create_image(85, 85, anchor=tk.CENTER, image=struct_photo)

                self.wall_photos.append(struct_photo)
                self.wall_sprites.append(struct_sprite)

                self.move_to_tile(struct_sprite, tile.tileNum)



    def refresh_units_prep(self):
        self.all_units = [[], []]
        self.current_units = [[], []]

        self.unit_photos = [[], []]
        self.unit_sprites = [[], []]

        self.unit_photos_gs = [[], []]
        self.unit_sprites_gs = [[], []]

        self.unit_photos_trans = [[], []]
        self.unit_sprites_trans = [[], []]

        self.unit_photos_gs_trans = [[], []]
        self.unit_sprites_gs_trans = [[], []]

        self.unit_weapon_icon_photos = [[], []]
        self.unit_weapon_icon_sprites = [[], []]

        for label in self.unit_sp_count_labels[0] + self.unit_sp_count_labels[1]:
            self.delete(label)

        for label in self.unit_hp_count_labels[0] + self.unit_hp_count_labels[1]:
            self.delete(label)

        for label in self.unit_hp_bars_fg[0] + self.unit_hp_bars_fg[1]:
            self.delete(label)

        for label in self.unit_hp_bars_bg[0] + self.unit_hp_bars_bg[1]:
            self.delete(label)

        self.unit_sp_count_labels = [[], []]
        self.unit_hp_count_labels = [[], []]

        self.unit_hp_bars_fg = [[], []]
        self.unit_hp_bars_bg = [[], []]

        self.unit_tags = [[], []]

        i = 0
        j = 0
        for drag_point in self.unit_drag_points.values():
            if drag_point.hero:
                unit = deepcopy(drag_point.hero)
                unit.side = drag_point.side

                S = unit.side

                self.all_units[S].append(unit)

                respString = "-R" if unit.resp else ""
                cur_image = Image.open("TestSprites/" + unit.intName + respString + ".png")
                if S == ENEMY: cur_image = cur_image.transpose(Image.FLIP_LEFT_RIGHT)
                resized_image = cur_image.resize((int(cur_image.width / 2.1), int(cur_image.height / 2.1)), Image.LANCZOS)
                cur_photo = ImageTk.PhotoImage(resized_image)

                self.unit_photos[S].append(cur_photo)

                grayscale_image = resized_image.convert("L")
                transparent_image = Image.new("RGBA", resized_image.size, (0, 0, 0, 0))
                transparent_image.paste(grayscale_image, (0, 0), mask=resized_image.split()[3])
                grayscale_photo = ImageTk.PhotoImage(transparent_image)

                self.unit_photos_gs[S].append(grayscale_photo)

                if unit.wpnType in hero.BEAST_WEAPONS:
                    cur_image_tr = Image.open("TestSprites/" + unit.intName + "-Tr" + ".png")
                    resized_image_tr = cur_image_tr.resize((int(cur_image_tr.width / 2.1), int(cur_image_tr.height / 2.1)), Image.LANCZOS)
                    cur_photo_tr = ImageTk.PhotoImage(resized_image_tr)

                    self.unit_photos_trans[S].append(cur_photo_tr)

                    grayscale_image_tr = resized_image_tr.convert("L")
                    transparent_image_tr = Image.new("RGBA", resized_image_tr.size, (0, 0, 0, 0))
                    transparent_image_tr.paste(grayscale_image_tr, (0, 0), mask=resized_image_tr.split()[3])
                    grayscale_photo_tr = ImageTk.PhotoImage(transparent_image_tr)

                    self.unit_photos_gs_trans[S].append(grayscale_photo_tr)

                else:
                    cur_photo_tr = cur_photo
                    grayscale_photo_tr = grayscale_photo

                    self.unit_photos_trans[S].append(cur_photo_tr)
                    self.unit_photos_gs_trans[S].append(grayscale_photo_tr)

                name = unit.intName.replace(' ', '')
                side = 'P' if S == PLAYER else 'E'
                num = i if S == PLAYER else j
                tag = f"tag_{name.replace('!', '_')}_{num}_{side}"
                self.unit_tags[S].append(tag)

                # Sprites on canvas

                # Player sprite
                item_id = self.create_image(100 * i, 200, anchor='center', image=cur_photo, tags=tag)
                self.move_to_tile(item_id, drag_point.tile)
                self.unit_sprites[S].append(item_id)

                # Player sprite - grayscale
                gs_item_id = self.create_image(100 * i, 200, anchor='center', image=grayscale_photo, tags=tag)
                self.itemconfig(gs_item_id, state='hidden')
                self.move_to_tile(gs_item_id, drag_point.tile)
                self.unit_sprites_gs[S].append(gs_item_id)

                # Player sprite - transformed
                item_id_tr = self.create_image(100 * i, 200, anchor='center', image=cur_photo_tr, tags=tag)
                self.itemconfig(item_id_tr, state='hidden')
                self.move_to_tile(item_id_tr, drag_point.tile)
                self.unit_sprites_trans[S].append(item_id_tr)

                # Player sprite - grayscale & transformed
                gs_item_id_tr = self.create_image(100 * i, 200, anchor='center', image=grayscale_photo_tr, tags=tag)
                self.itemconfig(gs_item_id_tr, state='hidden')
                self.move_to_tile(gs_item_id_tr, drag_point.tile)
                self.unit_sprites_gs_trans[S].append(gs_item_id_tr)

                # Weapon icon
                wpn_num = hero.weapons[unit.wpnType][0]
                wp_photo = ImageTk.PhotoImage(make_weapon_sprite(wpn_num))
                self.unit_weapon_icon_photos[S].append(wp_photo)

                weapon_id = self.create_image(160, 50 * (i + 2), anchor=tk.NW, image=wp_photo, tags=tag)
                self.move_to_tile_wp(weapon_id, drag_point.tile)
                self.unit_weapon_icon_sprites[S].append(weapon_id)

                # Special count
                sp_count_string = str(int(unit.specialCount))

                if unit.specialCount == -1:
                    sp_count_string = ""

                special_label = self.create_text(200, 100 * (2 + i), text=sp_count_string, fill="#e300e3", font=("Helvetica", 19, 'bold'), anchor='center', tags=tag)
                self.move_to_tile_sp(special_label, drag_point.tile)
                self.unit_sp_count_labels[S].append(special_label)

                if unit.side == PLAYER:
                    side_color = "#3da7a8"
                else:
                    side_color = "#ed1139"

                hp_string = unit.HPcur
                hp_label = self.create_text(200, 100 * (2 + i), text=hp_string, fill=side_color, font=("Helvetica", 16, 'bold'), anchor='center', tags=tag)
                self.move_to_tile_hp(hp_label, drag_point.tile)
                self.unit_hp_count_labels[S].append(hp_label)

                hp_bar_bg = self.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill='black', width=0, tags=tag)
                self.move_to_tile_bar(hp_bar_bg, drag_point.tile)
                self.unit_hp_bars_bg[S].append(hp_bar_bg)

                hp_bar_fg = self.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill=side_color, width=0, tags=tag)
                self.move_to_tile_bar(hp_bar_fg, drag_point.tile)
                self.unit_hp_bars_fg[S].append(hp_bar_fg)




            if drag_point.side == PLAYER: i += 1
            elif drag_point.side == ENEMY: j += 1

        # Refresh start button
        player_side_present = False
        enemy_side_present = False

        for drag_point in self.unit_drag_points.values():
            if drag_point.hero and drag_point.side == PLAYER:
                player_side_present = True
            elif drag_point.hero and drag_point.side == ENEMY:
                enemy_side_present = True

        if player_side_present and enemy_side_present:
            self.button_frame.start_button.config(state="normal")
        else:
            self.button_frame.start_button.config(state="disabled")

        self.extras.setup_tabs(self.unit_drag_points, None, None, False)

    def set_text_val(self, label, num):
        self.itemconfig(label, text=str(int(num)))

    def set_hp_bar_length(self, rect, percent):
        new_length = int(60 * percent)

        if new_length == 0:
            self.itemconfig(rect, state='hidden')
            return

        coords = self.coords(rect)
        coords[2] = coords[0] + new_length
        self.coords(rect, coords)

    # Move a sprite towards one direction, then return them to their original position
    def animate_sprite_atk(self, item_ID, move_hori, move_vert, damage, text_tile):
        # Get the current coordinates of the item
        x, y = self.coords(item_ID)
        start_x = x
        start_y = y

        # Calculate the new y-coordinate for moving up
        new_x = int(x + 40 * move_hori)
        new_y = int(y - 40 * move_vert)

        def move_to():
            if not self.animation: return

            nonlocal x
            nonlocal y

            x += 2 * move_hori
            y -= 2 * move_vert
            self.coords(item_ID, x, y)

            if x != new_x or y != new_y:
                self.after(2, move_to)
            else:
                move_fro()
                self.animate_damage_popup(damage, text_tile)

        def move_fro():
            if not self.animation: return

            nonlocal x
            nonlocal y

            x -= 2 * move_hori
            y += 2 * move_vert

            self.coords(item_ID, x, y)
            if x != start_x or y != start_y:
                self.after(2, move_fro)

        move_to()

    def animate_damage_popup(self, number, text_tile):
        x_comp = text_tile % 6
        y_comp = text_tile // 6
        x_pivot = x_comp * 90 + 45
        y_pivot = (7 - y_comp) * 90 + 45

        displayed_text2 = self.create_text((x_pivot + 2, y_pivot + 2), text=str(number), fill='#111111', font=("Helvetica", 25, 'bold'), anchor='center')
        displayed_text = self.create_text((x_pivot, y_pivot), text=str(number), fill='#de1d1d', font=("Helvetica", 25, 'bold'), anchor='center')

        self.after(350, self.delete, displayed_text)
        self.after(350, self.delete, displayed_text2)

    def animate_heal_popup(self, number, text_tile):
        x_comp = text_tile % 6
        y_comp = text_tile // 6
        x_pivot = x_comp * 90 + 45
        y_pivot = (7 - y_comp) * 90 + 45

        displayed_text2 = self.create_text((x_pivot + 2, y_pivot + 2), text=str(number), fill='#111111', font=("Helvetica", 25, 'bold'), anchor='center')
        displayed_text = self.create_text((x_pivot, y_pivot), text=str(number), fill='#14c454', font=("Helvetica", 25, 'bold'), anchor='center')

        self.after(350, self.delete, displayed_text)
        self.after(350, self.delete, displayed_text2)

    def place_unit_object(self, x, y):
        tile_x_coord = x // self.TILE_SIZE
        tile_y_coord = (self.GAMEPLAY_WIDTH // self.TILE_SIZE) - (y // self.TILE_SIZE) - 1

        tile = tile_x_coord + tile_y_coord * 6

        unit = self.hero_listing.created_hero

        if tile in self.unit_drag_points and self.unit_drag_points[tile].modifiable and not self.running and unit is not None:
            self.unit_drag_points[tile].hero = unit

            self.hero_listing.unit_creation_cancel()

            self.refresh_units_prep()

            unit.side = self.unit_drag_points[tile].side

            self.unit_status.update_from_obj(unit)

    def place_unit_from_frame(self, row_data, x, y):
        tile_x_coord = x // self.TILE_SIZE
        tile_y_coord = (self.GAMEPLAY_WIDTH // self.TILE_SIZE) - (y // self.TILE_SIZE) - 1

        tile = tile_x_coord + tile_y_coord * 6

        if tile in self.unit_drag_points and self.unit_drag_points[tile].modifiable and not self.running:

            made_hero = make_hero_from_pd_row(row_data, self.unit_drag_points[tile].side)

            self.unit_drag_points[tile].hero = made_hero

            self.refresh_units_prep()

            made_hero.side = self.unit_drag_points[tile].side

            if made_hero.side == ENEMY:
                self.unit_status.update_from_obj(made_hero)

class GameplayButtonFrame(tk.Frame):
    def __init__(self, master, fg, inner_bg, **kw):
        tk.Frame.__init__(self, master=master, **kw)

        self.button_frame = tk.Frame(self, bg=inner_bg)
        self.label_frame = tk.Frame(self, bg=inner_bg)

        self.text_color = fg

        # Button Frame
        self.end_turn_button = tk.Button(self.button_frame, text="End\nTurn", bg="#f21651", bd=0)
        self.end_turn_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.swap_spaces_button = tk.Button(self.button_frame, text="Swap\nSpaces", bg="#75f216", bd=0)
        self.swap_spaces_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.action_button = tk.Button(self.button_frame, text="Action\nButton", bg="#34ebe5", bd=0)
        self.action_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.undo_button = tk.Button(self.button_frame, text="Prev.\nAction", bg="#2344e8", fg="white", bd=0)
        self.undo_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.start_button = tk.Button(self.button_frame, text="Start\nSim", bg="dark green", bd=0, fg="white")
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.buttons = [self.end_turn_button, self.swap_spaces_button, self.action_button, self.undo_button, self.start_button]

        i = 0
        while i < 5:
            self.buttons[i].config(state="disabled")
            i += 1

        # Label Frame


        self.state_info = tk.Label(self.label_frame, text="EDITING", font=("Helvetica", 16, "bold"), fg=fg, bg=inner_bg, padx=0, pady=0)
        self.help_info = tk.Label(self.label_frame, text=help_text, font=("Helvetica", 9), fg=fg, bg=inner_bg)
        self.gamemode_info = tk.Label(self.label_frame, text="Gamemode: Story", font=("Helvetica", 13), fg=fg, bg=inner_bg)

        self.state_info.pack(padx=0, pady=0)
        self.gamemode_info.pack(padx=0, pady=0)
        self.help_info.pack(padx=0, pady=0)

        self.season_frame = tk.Frame(self.label_frame, bg=inner_bg)
        self.season_frame.pack()

        self.elemental_season_info = tk.Label(self.season_frame, text="Elemental Season:", font=("Helvetica", 13), fg=fg, bg=inner_bg)
        self.elemental_season_info.grid(row=0, column=0)

        self.aether_season_info = tk.Label(self.season_frame, text="Aether Season:", font=("Helvetica", 13), fg=fg, bg=inner_bg)
        self.aether_season_info.grid(row=0, column=1)

        self.elemental_str_var = tk.StringVar()
        self.elemental_season_combobox = ttk.Combobox(self.season_frame, textvariable=self.elemental_str_var, state="readonly")
        self.elemental_season_combobox['values'] = ["None", "Fire/Water", "Fire/Earth", "Fire/Wind", "Water/Earth", "Water/Wind", "Earth/Wind"]
        self.elemental_season_combobox.current(0)

        self.aether_str_var = tk.StringVar()
        self.aether_season_combobox = ttk.Combobox(self.season_frame, textvariable=self.aether_str_var, state="readonly")
        self.aether_season_combobox['values'] = ["None", "Light/Dark", "Astra/Anima"]
        self.aether_season_combobox.current(0)

        self.elemental_season_combobox.grid(row=1, column=0)
        self.aether_season_combobox.grid(row=1, column=1)

        self.running_elemental_season_info = tk.Label(self.season_frame, textvariable=self.elemental_str_var, font=("Helvetica", 13), fg=fg, bg=inner_bg)
        self.running_aether_season_info = tk.Label(self.season_frame, textvariable=self.aether_str_var, font=("Helvetica", 13), fg=fg, bg=inner_bg)

        self.button_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        self.label_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

class TabFrame(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master=master, **kw)

class TabButton(tk.Frame):
    def __init__(self, master, fg, text, **kw):

        tk.Frame.__init__(self, master=master, **kw, bd=1, highlightcolor="black")

        bg_color = "#ddd"
        fg_color = fg

        if "bg" in kw:
            bg_color = kw["bg"]

        MAX_LEN = 11

        if len(text) > MAX_LEN:
            text = text[:MAX_LEN] #+ "..."
            if text[-1] == " ":
                text = text[:MAX_LEN-1]

            text += "..."

        self.tab_name_button = tk.Button(master=self,
                                         text=text,
                                         relief="flat",
                                         bg=bg_color,
                                         fg=fg_color,
                                         activebackground=bg_color,
                                         activeforeground=fg_color,
                                         bd=0)

        self.tab_close_button = tk.Button(master=self,
                                          text="X",
                                          command=self.close,
                                          relief="flat",
                                          font=(None, 10, 'bold'),
                                          bg=bg_color,
                                          fg="red",
                                          activebackground=bg_color,
                                          activeforeground="red",
                                          bd=0)

        self.tab_name_button.pack(side=tk.LEFT)
        self.tab_close_button.pack(side=tk.LEFT)

    def close(self):
        self.destroy()

class FileTree(ttk.Treeview):
    def __init__(self, master, **kw):
        ttk.Treeview.__init__(self, master=master, **kw)

        self.preview_window = None

        self.heading("#0", text=" Maps Directory", anchor="w")
        self.column("#0", width=200)

        # Hovering Widgets
        self.hovered_item = None
        self.hover_timer = None

        # Preview Elements
        self.liquid = None
        self.terrain = None
        self.walls = []

        self.bind("<Motion>", self.on_mouse_move)
        self.bind("<Leave>", self.on_mouse_leave)

    def start_file_population(self):
        path = "Maps"
        root_node = self.insert(parent="", index="end", text=path, open=True)
        self.populate_treeview(self, root_node, path)

    def populate_treeview(self, tree, parent, path):
        path = path.replace("\\", "/") # For portability

        files = natsorted(os.listdir(path))

        for entry in files:

            full_path = os.path.join(path, entry)

            if os.path.isdir(full_path):
                node = tree.insert(parent, 'end', text=entry, tags=("directory_row"))
                self.populate_treeview(tree, node, full_path)
            else:
                if entry.endswith(".json"):
                    with open(str(path + "/" + entry)) as read_file: json_data = json.load(read_file)

                    tree.insert(parent, 'end', text=json_data['name'], tags=("item_row", str(path + "/" + entry)))

    def row_selected(self, event):
        tw = self.preview_window
        self.preview_window = None
        if tw:
            tw.destroy()

    def on_mouse_move(self, event):
        item = self.identify_row(event.y)

        if item != self.hovered_item:
            self.hovered_item = item

            if self.hover_timer:
                self.after_cancel(self.hover_timer)

            if 'item_row' in self.item(item)['tags']:

                with open(self.item(item)['tags'][1]) as read_file: json_data = json.load(read_file)
                self.hover_timer = self.after(500, self.on_hover_timeout, item, event, json_data)

            tw = self.preview_window
            self.preview_window = None
            if tw:
                tw.destroy()

    def on_mouse_leave(self, event):
        self.hovered_item = None
        if self.hover_timer:
            self.after_cancel(self.hover_timer)
            self.hover_timer = None

        tw = self.preview_window
        self.preview_window = None
        if tw:
            tw.destroy()


    def on_hover_timeout(self, item, event, map_data):
        if self.preview_window: return
        if not item: return

        x, y, cx, cy = self.bbox(item)
        x = x + self.winfo_rootx() + event.x
        y = y + cy + self.winfo_rooty()
        self.preview_window = tw = tk.Toplevel()
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        preview_width = 180
        preview_height = 240

        preview_canvas = tk.Canvas(tw, width=preview_width-2, height=preview_height-2, bg="#334455", highlightbackground="#111122")
        preview_canvas.pack()

        liquid_texture = "WavePattern.png"

        if "liquid" in map_data:
            liquid_texture = map_data["liquid"]

        liquid_image = Image.open("CombatSprites/" + liquid_texture)
        liquid_photo = ImageTk.PhotoImage(liquid_image)
        preview_canvas.create_image(0, 0, anchor=tk.NW, image=liquid_photo)

        self.liquid = liquid_photo

        terrain_texture = self.item(item)['tags'][1].replace(".json", ".png")
        terrain_texture = terrain_texture.replace("Normal_", "").replace("Hard_", "").replace("Lunatic_", "")

        terrain_image = Image.open(terrain_texture)
        terrain_image = terrain_image.resize((preview_width, preview_height), Image.LANCZOS)
        terrain_photo = ImageTk.PhotoImage(terrain_image)
        preview_canvas.create_image(0, 0, anchor=tk.NW, image=terrain_photo)

        self.terrain = terrain_photo

        # Place walls
        self.walls = []

        if "struct_walls" in map_data:
            # Default wall texture
            wall_texture = "Wallpattern.png"

            # Optional provided wall texture
            if "wall" in map_data:
                wall_texture = map_data["wall"]

            wall_image = Image.open("CombatSprites/" + wall_texture)

            all_walls = map_data["struct_walls"]["static"] + map_data["struct_walls"]["oneBreak"] + map_data["struct_walls"]["twoBreak"]

            for tile_num in map_data["struct_walls"]["oneBreak"]:

                x_comp = tile_num % 6
                y_comp = tile_num // 6

                result = [-1, -1, -1, -1]

                if y_comp + 1 < 8: result[0] = tile_num + 6
                if y_comp - 1 >= 0: result[1] = tile_num - 6
                if x_comp + 1 < 6: result[2] = tile_num + 1
                if x_comp - 1 >= 0: result[3] = tile_num - 1

                wall_type = 0
                iterator = 1

                for adj_tile in result:
                    if adj_tile in all_walls:
                        wall_type += iterator

                    iterator *= 2

                wall_health_offset = 364
                cur_crop = list(wall_crops[wall_type])

                # Singleton wall is placed going downwards
                if wall_type == 0:
                    cur_crop[1] += wall_health_offset
                    cur_crop[3] += wall_health_offset
                else:
                    cur_crop[0] += wall_health_offset
                    cur_crop[2] += wall_health_offset

                cur_wall = wall_image.crop(cur_crop)
                cur_wall = cur_wall.resize((30, 30), Image.LANCZOS)
                cur_photo = ImageTk.PhotoImage(cur_wall)

                preview_canvas.create_image(x_comp * 30, preview_height - (y_comp + 1) * 30, anchor=tk.NW, image=cur_photo)

                self.walls.append(cur_photo)

            for tile_num in map_data["struct_walls"]["twoBreak"]:

                x_comp = tile_num % 6
                y_comp = tile_num // 6

                result = [-1, -1, -1, -1]

                if y_comp + 1 < 8: result[0] = tile_num + 6
                if y_comp - 1 >= 0: result[1] = tile_num - 6
                if x_comp + 1 < 6: result[2] = tile_num + 1
                if x_comp - 1 >= 0: result[3] = tile_num - 1

                wall_type = 0
                iterator = 1

                for adj_tile in result:
                    if adj_tile in all_walls:
                        wall_type += iterator

                    iterator *= 2

                wall_health_offset = 182
                cur_crop = list(wall_crops[wall_type])

                # Singleton wall is placed going downwards
                if wall_type == 0:
                    cur_crop[1] += wall_health_offset
                    cur_crop[3] += wall_health_offset
                else:
                    cur_crop[0] += wall_health_offset
                    cur_crop[2] += wall_health_offset

                cur_wall = wall_image.crop(cur_crop)
                cur_wall = cur_wall.resize((30, 30), Image.LANCZOS)
                cur_photo = ImageTk.PhotoImage(cur_wall)

                preview_canvas.create_image(x_comp * 30, preview_height - (y_comp + 1) * 30, anchor=tk.NW, image=cur_photo)

                self.walls.append(cur_photo)

            for tile_num in map_data["struct_walls"]["static"]:

                x_comp = tile_num % 6
                y_comp = tile_num // 6

                result = [-1, -1, -1, -1]

                if y_comp + 1 < 8: result[0] = tile_num + 6
                if y_comp - 1 >= 0: result[1] = tile_num - 6
                if x_comp + 1 < 6: result[2] = tile_num + 1
                if x_comp - 1 >= 0: result[3] = tile_num - 1

                wall_type = 0
                iterator = 1

                for adj_tile in result:
                    if adj_tile in all_walls:
                        wall_type += iterator

                    iterator *= 2

                wall_health_offset = 0
                cur_crop = list(wall_crops[wall_type])

                # Singleton wall is placed going downwards
                if wall_type == 0:
                    cur_crop[1] += wall_health_offset
                    cur_crop[3] += wall_health_offset
                else:
                    cur_crop[0] += wall_health_offset
                    cur_crop[2] += wall_health_offset

                cur_wall = wall_image.crop(cur_crop)
                cur_wall = cur_wall.resize((30, 30), Image.LANCZOS)
                cur_photo = ImageTk.PhotoImage(cur_wall)

                preview_canvas.create_image(x_comp * 30, preview_height - (y_comp + 1) * 30, anchor=tk.NW, image=cur_photo)

                self.walls.append(cur_photo)

class ToolTip(object):

    def __init__(self, widget, side):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.side = side

    def showtip(self, text):
        try:
            lines = text.splitlines()  # Split text into lines
            wrapped_lines = [textwrap.fill(line, 60) for line in lines]
            self.text = "\n".join(wrapped_lines)

        # Weapon description is blank (or I haven't edited it yet)
        except AttributeError:
            self.text = ""

        if self.tipwindow or not self.text: return

        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx()
        y = y + cy + self.widget.winfo_rooty() + 27

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_attributes("-topmost", 1)
        #tw.update_idletasks()

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#110947", foreground="white", relief=tk.SOLID, borderwidth=1, highlightcolor="white",
                      font=("Helvetica", "10"))
        label.pack(ipadx=1)

        if self.side == "right":
            tw.update_idletasks()
            offset = tw.winfo_width() - self.widget.winfo_width()
            x = x - offset

        tw.wm_geometry("+%d+%d" % (x, y))

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text, side=None):
    if not side:
        side = "left"

    toolTip = ToolTip(widget, side)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

class UnitInfoDisplay(tk.Frame):
    def __init__(self, master, bg_color, fg, **kw):
        tk.Frame.__init__(self, master=master, **kw)

        title_frame = tk.Frame(self, **kw)
        title_frame.pack(fill=tk.X, expand=False, anchor=tk.NW)

        bg = "white"
        if "bg" in kw:
            bg = kw["bg"]

        title_label = tk.Label(title_frame, text=" Selected Hero Status", bg=bg, fg=fg, font=(None, 16))
        title_label.pack(anchor=tk.W)

        self.default_bg = bg_color
        self.text_color = fg

        self.inner_menu = tk.Frame(self, bg=self.default_bg)
        self.inner_menu.pack(fill=tk.BOTH, expand=True)

        # Inner components
        inner_font = 12

        self.name_frame = tk.Frame(self.inner_menu, bg="blue")

        self.name_label = tk.Label(self.name_frame, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.rarity_label = tk.Label(self.name_frame, width=9, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.rarity_label.pack(side=tk.LEFT)

        self.move_icon_img = None
        self.wpn_icon_img = None

        self.image1_label = tk.Label(self.name_frame, bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.image1_label.pack(side=tk.LEFT)

        self.image2_label = tk.Label(self.name_frame, bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.image2_label.pack(side=tk.LEFT)

        self.advanced_label = tk.Label(self.name_frame, text="Advanced", width=12, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.advanced_label.pack(side=tk.LEFT)

        self.level_frame = tk.Frame(self.inner_menu, bg="red")

        self.level_label = tk.Label(self.level_frame, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.level_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.dflowers_label = tk.Label(self.level_frame, width=14, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.dflowers_label.pack(side=tk.LEFT)

        self.resplendent_label = tk.Label(self.level_frame, width=14, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.resplendent_label.pack(side=tk.LEFT)

        self.aided_label = tk.Label(self.level_frame, width=8, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.aided_label.pack(side=tk.LEFT)

        self.pairup_label = tk.Label(self.level_frame, text="Pair Up", width=7, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.pairup_label.pack(side=tk.LEFT)

        self.middle_frame = tk.Frame(self.inner_menu, bg="orange")

        self.stats_frame = tk.Frame(self.middle_frame, bg="green", highlightthickness=1, highlightbackground=fg)
        self.skills_frame = tk.Frame(self.middle_frame, bg="purple", highlightthickness=1, highlightbackground=fg)
        self.stats_frame.pack(side=tk.LEFT, padx=20)
        self.skills_frame.pack(side=tk.RIGHT, fill=tk.BOTH, pady=10, padx=10)

        self.HP_frame = tk.Frame(self.stats_frame, bg="#73666c")
        self.HP_frame.pack()
        self.HP_label = tk.Label(self.HP_frame, fg="white", bg="#73666c", text="HP", font=(None, inner_font), width=2)
        self.HP_label.pack(side=tk.LEFT, padx=(1,2))
        self.HP_value_label = tk.Label(self.HP_frame, fg="white", bg="#73666c", text="99/99 100%", font=(None, inner_font), width=9)
        self.HP_value_label.pack(side=tk.LEFT)

        self.other_stats_frame = tk.Frame(self.stats_frame, bg="black")
        self.other_stats_frame.pack()

        self.atk_stat_frame = tk.Frame(self.other_stats_frame, bg="#6e4046")
        self.spd_stat_frame = tk.Frame(self.other_stats_frame, bg="#4d6e40")
        self.def_stat_frame = tk.Frame(self.other_stats_frame, bg="#87764c")
        self.res_stat_frame = tk.Frame(self.other_stats_frame, bg="#466569")

        self.atk_stat_frame.grid(row=0, column=0)
        self.spd_stat_frame.grid(row=0, column=1)
        self.def_stat_frame.grid(row=1, column=0)
        self.res_stat_frame.grid(row=1, column=1)

        self.atk_stat_label = tk.Label(self.atk_stat_frame, fg="white", bg="#6e4046", text="Atk", font=(None, inner_font), width=3)
        self.spd_stat_label = tk.Label(self.spd_stat_frame, fg="white", bg="#4d6e40", text="Spd", font=(None, inner_font), width=3)
        self.def_stat_label = tk.Label(self.def_stat_frame, fg="white", bg="#87764c", text="Def", font=(None, inner_font), width=3)
        self.res_stat_label = tk.Label(self.res_stat_frame, fg="white", bg="#466569", text="Res", font=(None, inner_font), width=3)

        self.atk_stat_label.pack(side=tk.LEFT)
        self.spd_stat_label.pack(side=tk.LEFT)
        self.def_stat_label.pack(side=tk.LEFT)
        self.res_stat_label.pack(side=tk.LEFT)

        self.atk_value_label = tk.Label(self.atk_stat_frame, fg="white", bg="#6e4046", text="99", font=(None, inner_font), width=2)
        self.spd_value_label = tk.Label(self.spd_stat_frame, fg="white", bg="#4d6e40", text="99", font=(None, inner_font), width=2)
        self.def_value_label = tk.Label(self.def_stat_frame, fg="white", bg="#87764c", text="99", font=(None, inner_font), width=2)
        self.res_value_label = tk.Label(self.res_stat_frame, fg="white", bg="#466569", text="99", font=(None, inner_font), width=2)

        self.atk_value_label.pack(side=tk.LEFT)
        self.spd_value_label.pack(side=tk.LEFT)
        self.def_value_label.pack(side=tk.LEFT)
        self.res_value_label.pack(side=tk.LEFT)

        skill_bg_colors = ["#cc3f52", "#5fa370", "#9b5fa3", "#e6413e", "#4c83c7", "#579c57", "#b59d12", "#86ad42"]
        skill_icon_colors = ["red", "green", "#ff33ff", "#e6150e", "#5d68dd", "#38e85b", "#ffdd33", "#a7e838"]
        skill_icons = "⚔◐☆ABCSX"

        self.status_label = tk.Label(self.stats_frame, text="Statuses List", width=12, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="white")
        self.status_label.pack()


        self.weapon_label = tk.Label(self.skills_frame, bg="#cc3f52", text="Brazen Cat Fang (+Eff2)", anchor=tk.W, width=20, font=(None, inner_font))
        self.assist_label = tk.Label(self.skills_frame, bg="#5fa370", text="Bart Simpson", anchor=tk.W, width=20, font=(None, inner_font))
        self.special_label = tk.Label(self.skills_frame, bg="#9b5fa3", text="According to all", anchor=tk.W, width=20, font=(None, inner_font))
        self.askill_label = tk.Label(self.skills_frame, bg="#e6413e", text="known laws of", anchor=tk.W, width=20, font=(None, inner_font))
        self.bskill_label = tk.Label(self.skills_frame, bg="#4c83c7", text="aviation, there", anchor=tk.W, width=20, font=(None, inner_font))
        self.cskill_label = tk.Label(self.skills_frame, bg="#579c57", text="is no way a bee", anchor=tk.W, width=20, font=(None, inner_font))
        self.sseal_label = tk.Label(self.skills_frame, bg="#e0b30d", text="should be able", anchor=tk.W, width=20, font=(None, inner_font))
        self.xskill_label = tk.Label(self.skills_frame, bg="#86ad42", text="to fly.", anchor=tk.W, width=20, font=(None, inner_font))

        skill_labels = [self.weapon_label, self.assist_label, self.special_label, self.askill_label, self.bskill_label, self.cskill_label, self.sseal_label, self.xskill_label]

        i = 0
        while i < len(skill_labels):
            tk.Label(self.skills_frame, bg="#282424", fg=skill_bg_colors[i], text=skill_icons[i], width=2, font=(None, inner_font)).grid(row=i, column=0)
            skill_labels[i].grid(row=i, column=1)
            i += 1


        self.everything_else = tk.Frame(self.inner_menu)
        self.blessing_label = tk.Label(self.everything_else, text="Blessing: Fire", width=17, font=(None, inner_font), bg=self.default_bg, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.blessing_label.pack(side=tk.LEFT)
        self.emblem_label = tk.Label(self.everything_else, text="Emblem: None", width=20, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.emblem_label.pack(side=tk.LEFT)
        self.ssupport_label = tk.Label(self.everything_else, text="Summoner Support: S", font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.ssupport_label.pack(side=tk.LEFT)


        self.and_you = tk.Frame(self.inner_menu)
        self.asupport_label = tk.Label(self.and_you, text="Ally Support: Flame Emperor: Bringer of War (Rank S)",
                                       width=50, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, highlightbackground="orange")
        self.asupport_label.pack(side=tk.LEFT)


        self.cur_hero = False

    def update_from_obj(self, unit: hero.Hero):
        if not self.cur_hero:
            self.clear()

        self.cur_hero = unit

        S = unit.side
        banner_color = "#18284f" if S == PLAYER else "#541616"

        self.inner_menu.config(bg=banner_color)
        self.middle_frame.config(bg=banner_color)

        self.name_frame.pack(fill=tk.X)

        name_str = unit.name + ": " + unit.epithet
        #name_str = "Flame Emperor: Bringer of War" # for testing max string length

        self.name_label.config(text=name_str)
        self.rarity_label.config(text="☆" * unit.rarity)

        move_icons = []
        icon_size = 20
        status_pic = Image.open("CombatSprites/Status.png")

        inf_icon = status_pic.crop((350, 414, 406, 465))
        inf_icon = inf_icon.resize((icon_size, icon_size), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(inf_icon))
        cav_icon = status_pic.crop((462, 414, 518, 465))
        cav_icon = cav_icon.resize((icon_size, icon_size), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(cav_icon))
        fly_icon = status_pic.crop((518, 414, 572, 465))
        fly_icon = fly_icon.resize((icon_size, icon_size), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(fly_icon))
        arm_icon = status_pic.crop((406, 414, 462, 465))
        arm_icon = arm_icon.resize((icon_size, icon_size), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(arm_icon))

        weapon_icons = []
        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
            cur_icon = cur_icon.resize((icon_size, icon_size), Image.LANCZOS)
            weapon_icons.append(ImageTk.PhotoImage(cur_icon))
            i += 1

        self.move_icon_img = move_icons[unit.move]
        self.wpn_icon_img = weapon_icons[hero.weapons[unit.wpnType][0]]

        self.image1_label.config(image=self.move_icon_img)
        self.image2_label.config(image=self.wpn_icon_img)

        refresher_types = ["None", "Sing", "Dance", "Play"]

        advanced_text = "Internal Name: " + unit.intName + "\n"
        advanced_text += "Growths: " + str(unit.growths) + "\n"
        advanced_text += "Base Vector ID: " + str(unit.BVID) + "\n"
        advanced_text += "Refresher Type: " + str(unit.refresh_type) + " (" + refresher_types[unit.refresh_type] + ")"

        CreateToolTip(self.advanced_label, text=advanced_text, side="right")

        # Level frame (contains level, merges, dragonflowers)
        self.level_frame.pack(fill=tk.X)

        level_str = "Lv. " + str(unit.level)
        if unit.merges:
            level_str += "+" + str(unit.merges)
        self.level_label.config(text=level_str)

        dflower_str = "+" + str(unit.flowers) + " Dragonflowers"
        self.dflowers_label.config(text=dflower_str)

        dflower_desc = "Unit gains stats in the order of the ranking of their Lv. 1 stats, with HP always counted first.\n\nThis unit's ordering is: "
        stat_strs = ["HP", "Atk", "Spd", "Def", "Res"]

        i = 0
        while i < 5:
            dflower_desc += stat_strs[unit.flower_order[i]]
            if i < 4:
                dflower_desc += ", "

            i += 1

        CreateToolTip(self.dflowers_label, text=dflower_desc, side="left")

        resplendent_str = "Resplendent: "
        if unit.resp:
            resplendent_str += "Yes"
        else:
            resplendent_str += "No"

        self.resplendent_label.config(text=resplendent_str)

        aided_str = "Aided: "
        if unit.aided:
            aided_str += "Yes"
        else:
            aided_str += "No"

        self.aided_label.config(text=aided_str)

        CreateToolTip(self.pairup_label, text="This hero does not have access to Pair Up.", side="right")

        elements = ["Fire", "Water", "Earth", "Wind", "Light", "Dark", "Astra", "Anima"]


        if unit.blessing:
            if unit.blessing.boostType != 0:
                if unit.blessing.element < 4:
                    blessing_str = elements[unit.blessing.element] + " Legendary"
                else:
                    blessing_str = elements[unit.blessing.element] + " Mythic"
            else:
                blessing_str = "Blessing: " + elements[unit.blessing.element]

            self.blessing_label.config(bg=BLESSING_COLORS[unit.blessing.element], fg=BLESSING_TEXTS[unit.blessing.element])
        else:
            blessing_str = "Blessing: None"
            self.blessing_label.config(bg=self.default_bg, fg=self.text_color)

        self.blessing_label.config(text=blessing_str)

        blessing_text = ""

        if unit.blessing:
            blessing = unit.blessing
            element = blessing.element

            blessing_text += elements[element]

            if blessing.boostType != 0:
                if element < 4:
                    blessing_text += " Legendary\n"
                else:
                    blessing_text += " Mythic\n"
            else:
                blessing_text += " Blessing\n"

            blessing_text += "\n"

            if blessing.boostType == 0:
                blessing_text += "During " + elements[element].capitalize() + " season, grants effects to this unit based on the " + elements[element].capitalize()
                if element < 4:
                    blessing_text += " Legendary"
                else:
                    blessing_text += " Mythic"
                blessing_text += " heroes currently deployed."

            elif blessing.boostType == 1:
                blessing_text += "During " + elements[element].capitalize() + " season, grants the following stat boosts to deployed allies with a " + elements[element].capitalize()
                blessing_text += " blessing conferred:\n\nHP+3, "

                if blessing.stat == hero.ATK:
                    blessing_text += "Atk+2"
                elif blessing.stat == hero.SPD:
                    blessing_text += "Spd+3"
                elif blessing.stat == hero.DEF:
                    blessing_text += "Def+4"
                elif blessing.stat == hero.RES:
                    blessing_text += "Res+4"

        CreateToolTip(self.blessing_label, blessing_text)

        ssupport_names = ["None", "C", "B", "A", "S"]
        self.ssupport_label.config(text="Summoner Support: " + ssupport_names[unit.summonerSupport])

        ally_str = "None"
        if unit.allySupport:
            ally = hero.makeHero(unit.allySupport)
            ally_str = ally.name + ": " + ally.epithet + " (Rank S)"
            del ally

        self.asupport_label.config(text="Ally Support: " + ally_str)

        fills = ['white'] * 5

        is_neutral_iv = unit.asset == unit.flaw
        is_asc = unit.asset != unit.asc_asset
        is_merged = unit.merges > 0

        if not is_neutral_iv:
            fills[unit.asset] = 'blue'

        if not is_merged and unit.asset != unit.flaw and unit.flaw != unit.asc_asset:
            fills[unit.flaw] = 'red'

        if is_neutral_iv and unit.asset != unit.asc_asset or \
                unit.asset != unit.flaw and unit.flaw != unit.asc_asset and is_asc or \
                not is_neutral_iv and unit.flaw == unit.asc_asset and is_merged:
            fills[unit.asc_asset] = 'blue'

        self.HP_label.config(fg=fills[HP])
        self.atk_stat_label.config(fg=fills[ATK])
        self.spd_stat_label.config(fg=fills[SPD])
        self.def_stat_label.config(fg=fills[DEF])
        self.res_stat_label.config(fg=fills[RES])

        fills = ['white'] * 5
        stats = unit.visible_stats[:]

        panic_factor = 1
        if hero.Status.Panic in unit.statusNeg: panic_factor = -1
        if hero.Status.NullPanic in unit.statusPos: panic_factor = 1

        i = 0
        while i < 5:
            if unit.buffs[i] * panic_factor > abs(unit.debuffs[i]):
                fills[i] = 'blue'
            if abs(unit.debuffs[i]) > unit.buffs[i] * panic_factor:
                fills[i] = 'red'

            if i == HP and unit.HPcur < 10:
                fills[i] = 'red'

            i += 1

        percentage = trunc(unit.HPcur / stats[HP] * 1000) / 10
        if percentage == 100.0:
            percentage = 100

        displayed_atk = min(max(stats[ATK] + unit.buffs[ATK] * panic_factor + unit.debuffs[ATK], 0), 99)
        displayed_spd = min(max(stats[SPD] + unit.buffs[SPD] * panic_factor + unit.debuffs[SPD], 0), 99)
        displayed_def = min(max(stats[DEF] + unit.buffs[DEF] * panic_factor + unit.debuffs[DEF], 0), 99)
        displayed_res = min(max(stats[RES] + unit.buffs[RES] * panic_factor + unit.debuffs[RES], 0), 99)

        self.HP_value_label.config(fg=fills[HP], text=str(unit.HPcur) + "/" + str(stats[HP]) + " " + str(percentage) + "%")
        self.atk_value_label.config(fg=fills[ATK], text=displayed_atk)
        self.spd_value_label.config(fg=fills[SPD], text=displayed_spd)
        self.def_value_label.config(fg=fills[DEF], text=displayed_def)
        self.res_value_label.config(fg=fills[RES], text=displayed_res)

        statuses_str = ""
        positive_header_used = False
        negative_header_used = False

        # Positive statuses
        if sum(unit.buffs) > 0 and panic_factor == 1:
            statuses_str += "--- POSITIVE STATUSES --- \n"
            positive_header_used = True

            statuses_str += "Stat Boosts:"
            if unit.buffs[ATK] > 0:
                statuses_str += "Atk+" + str(unit.buffs[ATK]) + "/"
            if unit.buffs[SPD] > 0:
                statuses_str += "Spd+" + str(unit.buffs[SPD]) + "/"
            if unit.buffs[DEF] > 0:
                statuses_str += "Def+" + str(unit.buffs[DEF]) + "/"
            if unit.buffs[RES] > 0:
                statuses_str += "Res+" + str(unit.buffs[RES])

            if statuses_str[-1] == '/':
                statuses_str = statuses_str[:-1]

            statuses_str += '\n'

        if unit.statusPos:
            if not positive_header_used:
                statuses_str += "--- POSITIVE STATUSES --- \n"
                positive_header_used = True

            for status in unit.statusPos:
                status_name = status.name
                spaced_name = sub(r'([A-Z])', r' \1', status_name)
                spaced_name = spaced_name.strip()

                statuses_str += spaced_name + '\n'

            statuses_str += '\n'

        if sum(unit.buffs) > 0 and panic_factor == -1:
            statuses_str += "--- NEGATIVE STATUSES --- \n"
            negative_header_used = True

            statuses_str += "Inverted Stat Bonuses:"
            if unit.buffs[ATK] > 0:
                statuses_str += "Atk-" + str(unit.buffs[ATK]) + "/"
            if unit.buffs[SPD] > 0:
                statuses_str += "Spd-" + str(unit.buffs[SPD]) + "/"
            if unit.buffs[DEF] > 0:
                statuses_str += "Def-" + str(unit.buffs[DEF]) + "/"
            if unit.buffs[RES] > 0:
                statuses_str += "Res-" + str(unit.buffs[RES])

            if statuses_str[-1] == '/':
                statuses_str = statuses_str[:-1]

            statuses_str += '\n'

        if sum(unit.debuffs) < 0:
            if not negative_header_used:
                statuses_str += "--- NEGATIVE STATUSES --- \n"
                negative_header_used = True

            statuses_str += "Stat Penalties:"
            if unit.debuffs[ATK] < 0:
                statuses_str += "Atk" + str(unit.debuffs[ATK]) + "/"
            if unit.debuffs[SPD] < 0:
                statuses_str += "Spd" + str(unit.debuffs[SPD]) + "/"
            if unit.debuffs[DEF] < 0:
                statuses_str += "Def" + str(unit.debuffs[DEF]) + "/"
            if unit.debuffs[RES] < 0:
                statuses_str += "Res" + str(unit.debuffs[RES])

            if statuses_str[-1] == '/':
                statuses_str = statuses_str[:-1]

            statuses_str += '\n'

        if unit.statusNeg:
            if not negative_header_used:
                statuses_str += "--- NEGATIVE STATUSES --- \n"
                negative_header_used = True

            for status in unit.statusNeg:
                status_name = status.name
                spaced_name = sub(r'([A-Z])', r' \1', status_name)
                spaced_name = spaced_name.strip()

                statuses_str += spaced_name + '\n'

            statuses_str += '\n'

        CreateToolTip(self.status_label, statuses_str)

        # Skills
        wpn_str = "-"
        weapon_desc = ""

        wpn_txt_color = "black"
        refine_substrings = ("Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz")

        if unit.weapon:
            wpn_str = unit.weapon.name

            ref_str = ""
            for suffix in refine_substrings:
                if unit.weapon.intName.endswith(suffix):
                    wpn_txt_color = "#6beb34"
                    ref_str = " (+" + suffix + ")"
                    break

            wpn_str += ref_str

            wpn_desc = "" if unit.weapon.desc == "nan" or (isinstance(unit.weapon.desc, float) and math.isnan(unit.weapon.desc)) else "\n" + unit.weapon.desc

            weapon_desc = "Might:" + str(unit.weapon.mt) + " Range:" + str(unit.weapon.range) + wpn_desc

        self.weapon_label.config(text=wpn_str, fg=wpn_txt_color)
        CreateToolTip(self.weapon_label, weapon_desc, side="right")


        ast_str = "-"
        assist_desc = ""
        if unit.assist:
            ast_str = unit.assist.name
            assist_desc = "Range:" + str(unit.assist.range) + "\n" + unit.assist.desc

        self.assist_label.config(text=ast_str)
        CreateToolTip(self.assist_label, assist_desc, side="right")

        sp_str = "-"
        special_desc = ""
        if unit.special:
            sp_str = unit.special.name
            special_desc = "Cooldown:" + str(unit.specialMax) + "\n" + unit.special.desc

        self.special_label.config(text=sp_str)
        CreateToolTip(self.special_label, special_desc, side="right")

        a_str = "-"
        askill_desc = ""
        if unit.askill:
            a_str = unit.askill.name
            askill_desc = unit.askill.desc

        self.askill_label.config(text=a_str)
        CreateToolTip(self.askill_label, askill_desc, side="right")

        b_str = "-"
        bskill_desc = ""
        if unit.bskill:
            b_str = unit.bskill.name
            bskill_desc = unit.bskill.desc

        self.bskill_label.config(text=b_str)
        CreateToolTip(self.bskill_label, bskill_desc, side="right")

        c_str = "-"
        cskill_desc = ""
        if unit.cskill:
            c_str = unit.cskill.name
            cskill_desc = unit.cskill.desc

        self.cskill_label.config(text=c_str)
        CreateToolTip(self.cskill_label, cskill_desc, side="right")

        s_str = "-"
        sseal_desc = ""
        if unit.sSeal:
            s_str = unit.sSeal.name
            sseal_desc = unit.sSeal.desc

        self.sseal_label.config(text=s_str)
        CreateToolTip(self.sseal_label, sseal_desc, side="right")

        x_str = "-"
        self.xskill_label.config(text=x_str)



        self.everything_else.pack(anchor=tk.NW)
        self.and_you.pack(anchor=tk.NW)
        self.middle_frame.pack()

    def clear(self):
        self.inner_menu.config(bg=self.default_bg)

        for widget in self.inner_menu.winfo_children():
            widget.forget()

class ExtrasFrame(tk.Frame):
    def __init__(self, master, bg_color, fg, **kw):
        tk.Frame.__init__(self, master=master, **kw)

        self.default_bg = bg_color
        self.text_color = fg

        self.bonus_units = []

        title_frame = tk.Frame(self, **kw)
        title_frame.pack(fill=tk.X, expand=False, anchor=tk.NW)

        bg = "white"
        if "bg" in kw:
            bg = kw["bg"]

        title_label = tk.Label(title_frame, text=" Extras", bg=bg, fg=fg, font=(None, 16))
        title_label.pack(anchor=tk.W)

        self.inner_menu = tk.Frame(self, bg=self.default_bg)
        self.inner_menu.pack(fill=tk.BOTH, expand=True)

        self.tab_frame = tk.Frame(self.inner_menu, bg=bg)
        self.tab_frame.pack(fill=tk.X)

        button_params = {
            "state": tk.DISABLED,
            "fg": self.text_color,
            "bg": bg_color,
            "bd": 1,
            "relief": "flat",
            "highlightthickness": 1,
            "highlightbackground": "red"
        }

        self.player_team_button = tk.Button(self.tab_frame, text="Player Team", **button_params, command=self.show_player_team)
        self.enemy_team_button = tk.Button(self.tab_frame, text="Enemy Team", **button_params, command=self.show_enemy_team)
        self.forecasts_button = tk.Button(self.tab_frame, text="Forecasts", **button_params, command=self.show_forecasts)
        self.building_button = tk.Button(self.tab_frame, text="Building", **button_params, command=self.show_building)

        self.buttons = [self.player_team_button, self.enemy_team_button, self.forecasts_button, self.building_button]

        self.player_team_button.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(8, 4))
        self.enemy_team_button.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=4)
        self.forecasts_button.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=4)
        self.building_button.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(4, 8))

        self.body_frame = tk.Frame(self.inner_menu, bg="gray23")
        self.body_frame.pack(fill=tk.BOTH, expand=True)

        self.player_team_tab = tk.Frame(self.body_frame, bg="#18284f")
        self.enemy_team_tab = tk.Frame(self.body_frame, bg="#541616")
        self.forecast_tab = tk.Frame(self.body_frame, bg="#1a1f26")
        self.building_tab = tk.Frame(self.body_frame, bg="mint cream")

        tk.Label(self.player_team_tab, text="Player Side Heroes Deployed:", bg=bg_color, fg=fg, font=("Helvetica", 14)).pack(anchor=tk.NW, padx=10, pady=10)
        tk.Label(self.enemy_team_tab, text="Enemy Side Heroes Deployed:", bg=bg_color, fg=fg, font=("Helvetica", 14)).pack(anchor=tk.NW, padx=10, pady=10)

        self.active_tab = None

        self.player_label_frame = tk.Frame(self.player_team_tab, bg=bg_color)
        self.enemy_label_frame = tk.Frame(self.enemy_team_tab, bg=bg_color)

        self.player_label_frame.pack(anchor=tk.NW, padx=10, pady=10)
        self.enemy_label_frame.pack(anchor=tk.NW, padx=10, pady=10)

        self.player_labels = []
        self.enemy_labels = []

        self.player_sprites = []
        self.enemy_sprites = []

        self.bonus_units = []
        self.bonus_units_buttons = []

        tk.Label(self.forecast_tab, text="Current Combat Forecast:", bg=bg_color, fg=fg, font=("Helvetica", 14)).pack(anchor=tk.NW, padx=10, pady=10)

        self.forecast_canvas = tk.Canvas(self.forecast_tab, width=500, height=90, bg="#2d333d", highlightthickness=0)
        self.forecast_canvas.pack(anchor=tk.NW, padx=10, pady=10)

        self.icons = []
        self.labels = []

        self.game_mode = None
        self.is_running = None

    def reset_tab_buttons(self):
        for button in self.buttons:
            button.config(bg=self.default_bg)

    def setup_tabs(self, drag_points, bonus_labels, game_mode, is_running):
        for label in self.player_labels + self.enemy_labels:
            label.destroy()

        if bonus_labels:
            self.bonus_units = bonus_labels

        if game_mode:
            self.game_mode = game_mode

        self.is_running = is_running

        self.player_labels.clear()
        self.enemy_labels.clear()

        self.player_sprites.clear()
        self.enemy_sprites.clear()

        self.bonus_units_buttons.clear()

        PIXEL = tk.PhotoImage(width=1, height=1)

        i = 1
        j = 1
        for drag_point in drag_points.values():
            if drag_point.hero:
                unit = drag_point.hero
                unit.side = drag_point.side

                S = unit.side

                respString = "-R" if unit.resp else ""
                cur_image = Image.open("TestSprites/" + unit.intName + respString + ".png")
                resized_image = cur_image.resize((int(cur_image.width / 2.1), int(cur_image.height / 2.1)), Image.LANCZOS)
                cur_photo = ImageTk.PhotoImage(resized_image)

                if S == PLAYER:
                    self.player_sprites.append(cur_photo)
                else:
                    self.enemy_sprites.append(cur_photo)

            if drag_point.side == PLAYER:
                master = self.player_label_frame
                adding_list = self.player_labels
            else:
                master = self.enemy_label_frame
                adding_list = self.enemy_labels

            cur_frame = tk.Label(master, bg="gray10")
            cur_frame.pack(padx=10, pady=10, side=tk.LEFT)
            adding_list.append(cur_frame)

            unit_count = i if drag_point.side == PLAYER else j

            if drag_point.hero:
                pic_label = tk.Label(cur_frame, width=100, height=100, image=cur_photo, bg="gray10")
                name_label = tk.Label(cur_frame, text=str(unit_count) + ") " + unit.name, bg="gray74")
            else:
                pic_label = tk.Label(cur_frame, width=100, height=100, image=PIXEL, bg="gray10")
                name_label = tk.Label(cur_frame, text=str(unit_count) + ") None", bg="gray74")

            bonus_button_color = "gray35"

            if drag_point.side == PLAYER and self.bonus_units[i-1]:
                bonus_button_color = "gold"

            adding_list.append(pic_label)
            pic_label.pack()
            name_label.pack(fill=tk.X, padx=5, pady=5)

            if drag_point.side == PLAYER and (self.game_mode == hero.GameMode.Arena or self.game_mode == hero.GameMode.AetherRaids):
                bonus_button = tk.Button(cur_frame, text="Is Bonus", bg=bonus_button_color, bd=0, command=partial(self.toggle_unit_as_bonus, i-1))

                if self.is_running:
                    bonus_button.config(state="disabled")

                bonus_button.pack(fill=tk.X)
                self.bonus_units_buttons.append(bonus_button)

            if drag_point.side == PLAYER:
                i += 1
            else:
                j += 1

    def toggle_unit_as_bonus(self, button_num):
        if self.bonus_units[button_num]:
            self.bonus_units_buttons[button_num].config(bg="gray35")
            self.bonus_units[button_num] = False
        else:
            self.bonus_units_buttons[button_num].config(bg="gold")
            self.bonus_units[button_num] = True

    def clear_forecast_banner(self):
        self.forecast_canvas.delete('all')

        for label in self.labels:
            label.place_forget()

    def set_forecast_banner_foe(self, attacker, defender, distance, savior_triggered, turn_num, combat_fields):
        self.clear_forecast_banner()

        WIDTH = 500
        HEIGHT = 90

        atkHP = attacker.HPcur
        defHP = defender.HPcur

        aoe_damage: int = 0
        aoe_present: bool = False

        if attacker.special is not None and attacker.special.type == "AOE" and attacker.specialCount == 0:
            aoe_present = True

            aoe_damage = hero.get_AOE_damage(attacker, defender)
            defHP = max(1, defHP - aoe_damage)

        result = simulate_combat(attacker, defender, True, turn_num, distance, combat_fields, aoe_present, savior_triggered, atkHPCur=atkHP, defHPCur=defHP)

        atk_burn_damage_present = False
        def_burn_damage_present = False

        burn_damages = result[14]

        if burn_damages[ENEMY] > 0:
            atkHP = max(1, atkHP - burn_damages[1])
            atk_burn_damage_present = True

        if burn_damages[PLAYER] > 0:
            defHP = max(1, defHP - burn_damages[0])
            def_burn_damage_present = True

        wpn_adv = result[4]
        atk_eff = result[5]
        def_eff = result[6]

        attacks = result[7]

        atk_feh_math_R = result[8]
        atk_hits_R = result[9]
        def_feh_math_R = result[10]
        def_hits_R = result[11]

        atk_multihit_symbol = " × " + str(atk_hits_R)
        if atk_hits_R == 1:
            atk_multihit_symbol = ""

        def_multihit_symbol = " × " + str(def_hits_R)
        if def_hits_R == 1:
            def_multihit_symbol = ""

        atk_feh_math = str(atk_feh_math_R) + atk_multihit_symbol
        def_feh_math = str(def_feh_math_R) + def_multihit_symbol

        if def_hits_R == 0: def_feh_math = "—"
        if atk_hits_R == 0: atk_feh_math = "—"

        # Background
        player_color = "#18284f" if attacker.side == 0 else "#541616"
        enemy_color = "#18284f" if defender.side == 0 else "#541616"

        canvas = self.forecast_canvas

        canvas.create_rectangle(0, 0, WIDTH / 2, HEIGHT-1, fill=player_color, outline=RARITY_COLORS[attacker.rarity - 1])
        canvas.create_rectangle(WIDTH / 2 + 1, 0, WIDTH-1, HEIGHT-1, fill=enemy_color, outline=RARITY_COLORS[defender.rarity - 1])

        # Names
        player_name_label = tk.Label(canvas, text=attacker.name, bg="gray14", font="Helvetica 12", fg="white", relief="raised", width=13)
        player_name_label.place(x=10, y=5)

        enemy_name_label = tk.Label(canvas, text=defender.name, bg="gray14", font="Helvetica 12", fg="white", relief="raised", width=13)
        enemy_name_label.place(x=WIDTH - 130, y=5)

        self.labels = [player_name_label, enemy_name_label]

        move_icons = []
        status_pic = Image.open("CombatSprites/" + "Status" + ".png")

        inf_icon = status_pic.crop((350, 414, 406, 468))
        inf_icon = inf_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(inf_icon))
        cav_icon = status_pic.crop((462, 414, 518, 468))
        cav_icon = cav_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(cav_icon))
        fly_icon = status_pic.crop((518, 414, 572, 468))
        fly_icon = fly_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(fly_icon))
        arm_icon = status_pic.crop((406, 414, 462, 468))
        arm_icon = arm_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(arm_icon))

        weapon_icons = []
        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
            cur_icon = cur_icon.resize((25, 25), Image.LANCZOS)
            weapon_icons.append(ImageTk.PhotoImage(cur_icon))
            i += 1

        atkr_move_icon = move_icons[attacker.move]
        atkr_wpn_icon = weapon_icons[weapons[attacker.wpnType][0]]
        defr_move_icon = move_icons[int(defender.move)]
        defr_weapon_icon = weapon_icons[weapons[defender.wpnType][0]]

        self.icons = [atkr_move_icon, atkr_wpn_icon, defr_move_icon, defr_weapon_icon]

        canvas.create_image(135, 6, anchor=tk.NW, image=atkr_move_icon)
        canvas.create_image(160, 4, anchor=tk.NW, image=weapon_icons[weapons[attacker.wpnType][0]])
        canvas.create_image(WIDTH - 155, 6, anchor=tk.NW, image=move_icons[int(defender.move)])
        canvas.create_image(WIDTH - 180, 4, anchor=tk.NW, image=weapon_icons[weapons[defender.wpnType][0]])

        # HP Calculation
        if aoe_present or def_burn_damage_present:
            atk_feh_math = str(aoe_damage + burn_damages[0]) + " + " + str(atk_feh_math)

        if atk_burn_damage_present:
            def_feh_math = str(burn_damages[1]) + " + " + str(def_feh_math)

        i = 0
        while i < len(attacks):
            if attacks[i].attackOwner == 0:
                defHP = max(0, defHP - attacks[i].damage)
                atkHP = min(attacker.visible_stats[HP], atkHP + attacks[i].healed)

            if attacks[i].attackOwner == 1:
                atkHP = max(0, atkHP - attacks[i].damage)
                defHP = min(defender.visible_stats[HP], defHP + attacks[i].healed)

            if atkHP == 0 or defHP == 0: break
            i += 1

        canvas.create_text((215, 16), text=str(attacker.HPcur) + "→" + str(atkHP), fill='yellow', font=("Helvetica", 13), anchor='center')
        canvas.create_text((WIDTH-216, 16), text=str(defender.HPcur) + "→" + str(defHP), fill="yellow", font=("Helvetica", 13), anchor='center')

        if wpn_adv == 1:
            canvas.create_text((257, 9), text=" ⇑ ", fill='#42bf34', font=("Helvetica", 14, 'bold'), anchor='center')
            canvas.create_text((WIDTH-256, 9), text=" ⇓ ", fill='red', font=("Helvetica", 14, 'bold'), anchor='center')
        if wpn_adv == 0:
            canvas.create_text((257, 9), text=" ⇓ ", fill='red', font=("Helvetica", 14, 'bold'), anchor='center')
            canvas.create_text((WIDTH-256, 9), text=" ⇑ ", fill='#42bf34', font=("Helvetica", 14, 'bold'), anchor='center')

        canvas.create_rectangle(250 - 40, 27, 250 + 40, 42, fill='#5a5c6b', outline='#dae6e2')
        canvas.create_text((250, 35), text="FEH Math", fill='#dae6e2', font=("Helvetica", 11, 'bold'), anchor='center')

        canvas.create_text((250 - 85, 35), text=atk_feh_math, fill='#e8c35d', font=("Helvetica", 12), anchor='center')
        canvas.create_text((250 + 85, 35), text=def_feh_math, fill='#e8c35d', font=("Helvetica", 12), anchor='center')

        player_spCount = attacker.specialCount
        enemy_spCount = defender.specialCount

        if player_spCount != -1:
            canvas.create_text((250 - 125, 35), text=player_spCount, fill='#ff33ff', font=("Helvetica", 12), anchor='center')

        if enemy_spCount != -1:
            canvas.create_text((250 + 125, 35), text=enemy_spCount, fill='#ff33ff', font=("Helvetica", 12), anchor='center')

        player_combat_buffs = result[2]
        enemy_combat_buffs = result[3]

        canvas.create_text((40, 35), text="Atk" + "+" * (player_combat_buffs[ATK] >= 0) + str(player_combat_buffs[ATK]), fill='#db3b25', font=("Helvetica", 10), anchor='center')
        canvas.create_text((90, 35), text="Spd" + "+" * (player_combat_buffs[SPD] >= 0) + str(player_combat_buffs[SPD]), fill='#17eb34', font=("Helvetica", 10), anchor='center')
        canvas.create_text((60, 48), text="Def" + "+" * (player_combat_buffs[DEF] >= 0) + str(player_combat_buffs[DEF]), fill='#dbdb25', font=("Helvetica", 10), anchor='center')
        canvas.create_text((110, 48), text="Res" + "+" * (player_combat_buffs[RES] >= 0) + str(player_combat_buffs[RES]), fill='#25dbd2', font=("Helvetica", 10), anchor='center')

        canvas.create_text((WIDTH-90, 35), text="Atk" + "+" * (enemy_combat_buffs[ATK] >= 0) + str(enemy_combat_buffs[ATK]), fill='#db3b25', font=("Helvetica", 10), anchor='center')
        canvas.create_text((WIDTH-40, 35), text="Spd" + "+" * (enemy_combat_buffs[SPD] >= 0) + str(enemy_combat_buffs[SPD]), fill='#17eb34', font=("Helvetica", 10), anchor='center')
        canvas.create_text((WIDTH-110, 48), text="Def" + "+" * (enemy_combat_buffs[DEF] >= 0) + str(enemy_combat_buffs[DEF]), fill='#dbdb25', font=("Helvetica", 10), anchor='center')
        canvas.create_text((WIDTH-60, 48), text="Res" + "+" * (enemy_combat_buffs[RES] >= 0) + str(enemy_combat_buffs[RES]), fill='#25dbd2', font=("Helvetica", 10), anchor='center')

        box_size = 30
        gap_size = 8

        num_strikes = len(attacks) + int(aoe_present) + int(atk_burn_damage_present + def_burn_damage_present)

        cur_box_pos = int(250 - (gap_size * 0.5 * (num_strikes - 1) + box_size * 0.5 * (num_strikes - 1)))

        canvas.create_rectangle(cur_box_pos - 110, 54, cur_box_pos - 20, 76, fill="silver", outline='#dae6e2')
        canvas.create_text((cur_box_pos - 65, 65), text="Attack Order", fill='black', font=("Helvetica", 10, "bold"), anchor='center')

        # AOE Damage
        if aoe_present:
            box_color = "#6e2a9c"
            canvas.create_rectangle(cur_box_pos - 15, 50, cur_box_pos + 15, 80, fill=box_color, outline='#dae6e2')
            canvas.create_text((cur_box_pos, 65), text=aoe_damage, fill='#e8c35d', font=("Helvetica", 12), anchor='center')

            cur_box_pos += int(box_size + gap_size)

        # Burn Damage
        if atk_burn_damage_present or def_burn_damage_present:
            atk_burn_txt = burn_damages[PLAYER] if def_burn_damage_present else "-"
            def_burn_txt = burn_damages[ENEMY] if atk_burn_damage_present else "-"

            atk_color = "#18284f" if attacker.side == 0 else "#541616"
            def_color = "#541616" if attacker.side == 0 else "#18284f"

            canvas.create_rectangle(cur_box_pos - 15, 50, cur_box_pos + 15, 65, fill=atk_color, outline='#c9692c')
            canvas.create_text((cur_box_pos, 57), text=atk_burn_txt, fill='#e8c35d', font=("Helvetica", 12), anchor='center')

            canvas.create_rectangle(cur_box_pos - 15, 65, cur_box_pos + 15, 80, fill=def_color, outline='#c9692c')
            canvas.create_text((cur_box_pos, 72), text=def_burn_txt, fill='#e8c35d', font=("Helvetica", 12), anchor='center')

            cur_box_pos += int(box_size + gap_size)

        # Attacks
        for x in attacks:
            box_color = "#18284f" if x.attackOwner == attacker.side else "#541616"
            border_color = "#dae6e2" if not x.isSpecial else "#fc03e3"

            canvas.create_rectangle(cur_box_pos - 15, 50, cur_box_pos + 15, 80, fill=box_color, outline=border_color)

            dmg_fill = '#e8c35d'
            if x.attackOwner == 0 and atk_eff:
                dmg_fill = '#46eb34'
            if x.attackOwner == 1 and def_eff:
                dmg_fill = '#46eb34'

            canvas.create_text((cur_box_pos, 65), text=x.damage, fill=dmg_fill, font=("Helvetica", 12), anchor='center')

            cur_box_pos += int(box_size + gap_size)

    def set_forecast_banner_ally(self, player, ally):
        self.clear_forecast_banner()

        bg_color = "#18284f" if player.side == 0 else "#541616"

        WIDTH = 500
        HEIGHT = 90

        canvas = self.forecast_canvas

        canvas.create_rectangle(0, 0, WIDTH / 2, HEIGHT - 1, fill=bg_color, outline=RARITY_COLORS[player.rarity - 1])
        canvas.create_rectangle(WIDTH / 2 + 1, 0, WIDTH - 1, HEIGHT - 1, fill=bg_color, outline=RARITY_COLORS[ally.rarity - 1])

        player_name_label = tk.Label(canvas, text=player.name, bg="gray14", fg="white", font="Helvetica 12", relief="raised", width=13)
        player_name_label.place(x=10, y=5)

        ally_name_label = tk.Label(canvas, text=ally.name, bg="gray14", fg="white", font="Helvetica 12", relief="raised", width=13)
        ally_name_label.place(x=500 - 130, y=5)

        self.labels.append(player_name_label)
        self.labels.append(ally_name_label)

        new_player_hp = player.HPcur
        new_ally_hp = ally.HPcur

        # Calculate HP after healing
        if "heal" in player.assist.effects:
            hp_healed_ally = player.assist.effects["heal"]
            hp_healed_self = 0

            panic_factor = 1
            if Status.Panic in player.statusNeg: panic_factor = -1
            if Status.NullPanic in player.statusPos: panic_factor = 1
            self_atk_stat = player.visible_stats[ATK] + player.buffs[ATK] * panic_factor + player.debuffs[ATK]

            # Reconcile
            if "heal_self" in player.assist.effects:
                hp_healed_self = player.assist.effects["heal_self"]

            # Martyr
            if player.assist.effects["heal"] == -3:
                dmg_taken = player.visible_stats[HP] - player.HPcur
                hp_healed_ally = dmg_taken + 7
                hp_healed_self = dmg_taken // 2

            # Martyr+
            if player.assist.effects["heal"] == -49:
                dmg_taken = player.visible_stats[HP] - player.HPcur
                hp_healed_ally = dmg_taken + self_atk_stat // 2
                hp_healed_self = dmg_taken // 2

            # Recover+
            if player.assist.effects["heal"] == -10:
                hp_healed_ally = max(self_atk_stat // 2 + 10, 15)

            # Rehabilitate
            if player.assist.effects["heal"] == -1:
                ally_hp_max = ally.visible_stats[HP]
                ally_hp_cur = ally.HPcur

                hp_healed_ally = max(7 + ally_hp_max - (2 * ally_hp_cur), 7)

            # Rehabilitate+
            if player.assist.effects["heal"] == -2:
                ally_hp_max = ally.visible_stats[HP]
                ally_hp_cur = ally.HPcur

                hp_healed_ally = max(self_atk_stat // 2 - 10, 7) + max(ally_hp_max - (2 * ally_hp_cur), 0)

            # Physic+
            if player.assist.effects["heal"] == -50:
                hp_healed_ally = max(self_atk_stat // 2, 8)

            if player.specialCount == 0 and player.special.type == "Healing":
                if "boost_heal" in player.special.effects:
                    hp_healed_ally += player.special.effects["boost_heal"]

                if "heal_allies" in player.special.effects:
                    hp_healed_ally += player.special.effects["heal_allies"]

            if "live_to_serve" in player.bskill.effects:
                percentage = 0.25 + 0.25 * player.bskill.effects["live_to_serve"]
                hp_healed_self += trunc(hp_healed_ally * percentage)

            new_ally_hp = min(ally.visible_stats[HP], ally.HPcur + hp_healed_ally)
            new_player_hp = min(player.visible_stats[HP], player.HPcur + hp_healed_self)

        if "rec_aid" in player.assist.effects:
            new_ally_hp = min(ally.visible_stats[HP], player.HPcur)
            new_player_hp = min(player.visible_stats[HP], ally.HPcur)

        if "ardent_sac" in player.assist.effects:
            new_ally_hp = min(ally.visible_stats[HP], ally.HPcur + 10)
            new_player_hp = max(1, player.HPcur - 10)

        if "sacrifice" in player.assist.effects:
            new_ally_hp = min(ally.visible_stats[HP], ally.HPcur + (player.HPcur - 1))
            new_player_hp = max(1, player.HPcur - (ally.visible_stats[HP] - ally.HPcur))

        canvas.create_text((215, 16), text=str(player.HPcur) + "→" + str(new_player_hp), fill='yellow', font=("Helvetica", 13), anchor='center')
        canvas.create_text((WIDTH-216, 16), text=str(ally.HPcur) + "→" + str(new_ally_hp), fill="yellow", font=("Helvetica", 13), anchor='center')

        canvas.create_rectangle(250 - 65, 27, 270 + 65, 42, fill='#5a5c6b', outline='#dae6e2')
        canvas.create_text((250, 34), text=player.assist.name, fill="white", font=("Helvetica", 11), anchor='center')

        move_icons = []
        status_pic = Image.open("CombatSprites/" + "Status" + ".png")

        inf_icon = status_pic.crop((350, 414, 406, 468))
        inf_icon = inf_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(inf_icon))
        cav_icon = status_pic.crop((462, 414, 518, 468))
        cav_icon = cav_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(cav_icon))
        fly_icon = status_pic.crop((518, 414, 572, 468))
        fly_icon = fly_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(fly_icon))
        arm_icon = status_pic.crop((406, 414, 462, 468))
        arm_icon = arm_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(arm_icon))

        weapon_icons = []
        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
            cur_icon = cur_icon.resize((25, 25), Image.LANCZOS)
            weapon_icons.append(ImageTk.PhotoImage(cur_icon))
            i += 1

        atkr_move_icon = move_icons[player.move]
        atkr_wpn_icon = weapon_icons[weapons[player.wpnType][0]]
        defr_move_icon = move_icons[int(ally.move)]
        defr_weapon_icon = weapon_icons[weapons[ally.wpnType][0]]

        self.icons = [atkr_move_icon, atkr_wpn_icon, defr_move_icon, defr_weapon_icon]

        canvas.create_image(135, 6, anchor=tk.NW, image=atkr_move_icon)
        canvas.create_image(160, 4, anchor=tk.NW, image=atkr_wpn_icon)
        canvas.create_image(WIDTH - 155, 6, anchor=tk.NW, image=defr_move_icon)
        canvas.create_image(WIDTH - 180, 4, anchor=tk.NW, image=defr_weapon_icon)

    def set_forecast_banner_struct(self, attacker, structure):
        self.clear_forecast_banner()

        # Background
        player_color = "#18284f" if attacker.side == 0 else "#541616"
        struct_color = "#233b1e"
        struct_border = "#82d982"

        WIDTH = 500
        HEIGHT = 90

        canvas = self.forecast_canvas

        canvas.create_rectangle(0, 0, WIDTH / 2, HEIGHT - 1, fill=player_color, outline=RARITY_COLORS[attacker.rarity - 1])
        canvas.create_rectangle(WIDTH / 2 + 1, 0, WIDTH - 1, HEIGHT - 1, fill=struct_color, outline=struct_border)

        # Name Labels
        player_name_label = tk.Label(canvas, text=attacker.name, bg="gray14", fg="white", font="Helvetica 12", relief="raised", width=13)
        player_name_label.place(x=10, y=5)

        struct_name = "Obstacle"

        enemy_name_label = tk.Label(canvas, text=struct_name, bg="gray14", fg="white", font="Helvetica 12", relief="raised", width=13)
        enemy_name_label.place(x=WIDTH - 130, y=5)

        self.labels.append(player_name_label)
        self.labels.append(enemy_name_label)

        canvas.create_rectangle(250 - 40, 27, 250 + 40, 42, fill='#5a5c6b', outline='#dae6e2')
        canvas.create_text((250, 35), text="Destroy", fill='#dae6e2', font=("Helvetica", 11, 'bold'), anchor='center')

        # Damage labels
        canvas.create_text((215, 16), text=str(attacker.HPcur) + "→" + str(attacker.HPcur), fill='yellow', font=("Helvetica", 13), anchor='center')
        canvas.create_text((WIDTH-216, 16), text=str(structure.health) + "→" + str(structure.health - 1), fill="yellow", font=("Helvetica", 13), anchor='center')

        canvas.create_text((250 - 85, 35), text="1", fill='#e8c35d', font=("Helvetica", 12), anchor='center')
        canvas.create_text((270 + 85, 35), text="-", fill='#e8c35d', font=("Helvetica", 12), anchor='center')

        move_icons = []
        status_pic = Image.open("CombatSprites/" + "Status" + ".png")

        inf_icon = status_pic.crop((350, 414, 406, 468))
        inf_icon = inf_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(inf_icon))
        cav_icon = status_pic.crop((462, 414, 518, 468))
        cav_icon = cav_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(cav_icon))
        fly_icon = status_pic.crop((518, 414, 572, 468))
        fly_icon = fly_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(fly_icon))
        arm_icon = status_pic.crop((406, 414, 462, 468))
        arm_icon = arm_icon.resize((23, 23), Image.LANCZOS)
        move_icons.append(ImageTk.PhotoImage(arm_icon))

        weapon_icons = []
        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
            cur_icon = cur_icon.resize((25, 25), Image.LANCZOS)
            weapon_icons.append(ImageTk.PhotoImage(cur_icon))
            i += 1

        atkr_move_icon = move_icons[player.move]
        atkr_wpn_icon = weapon_icons[weapons[player.wpnType][0]]

        self.icons = [atkr_move_icon, atkr_wpn_icon]

        canvas.create_image(135, 6, anchor=tk.NW, image=atkr_move_icon)
        canvas.create_image(160, 4, anchor=tk.NW, image=atkr_wpn_icon)

        #print("THE")

    def show_player_team(self):
        self.reset_tab_buttons()
        self.player_team_button.config(bg="green")

        if self.active_tab:
            self.active_tab.forget()

        #print("player team button, woohoo!")
        self.player_team_tab.pack(fill=tk.BOTH, expand=True)
        self.active_tab = self.player_team_tab

    def show_enemy_team(self):
        self.reset_tab_buttons()
        self.enemy_team_button.config(bg="green")

        #print("enemy team button, ehxcellent")

        if self.active_tab:
            self.active_tab.forget()

        self.enemy_team_tab.pack(fill=tk.BOTH, expand=True)
        self.active_tab = self.enemy_team_tab

    def show_forecasts(self):
        self.reset_tab_buttons()
        self.forecasts_button.config(bg="green")

        #print("clicked forecasts, haw haw!")

        if self.active_tab:
            self.active_tab.forget()

        self.forecast_tab.pack(fill=tk.BOTH, expand=True)
        self.active_tab = self.forecast_tab

    def show_building(self):
        self.reset_tab_buttons()

        #print("moe")

        if self.active_tab:
            self.active_tab.forget()
