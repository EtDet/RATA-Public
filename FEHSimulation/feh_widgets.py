import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import os

import textwrap
from re import sub

import json
from csv import reader, writer
import pickle

import pandas as pd
from math import isnan

from functools import partial

from PIL import Image, ImageTk

from natsort import natsorted
from collections import Counter

from copy import deepcopy

from map import wall_crops, Map, struct_sheet, makeStruct
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
OMNI = 10

STATS = {"None": -1, "HP": 0, "Atk": 1, "Spd": 2, "Def": 3, "Res": 4}
STAT_STR = ["HP", "Atk", "Spd", "Def", "Res", "None"]

BLESSINGS_DICT = {"None": -1, "Fire": 0, "Water": 1, "Earth": 2, "Wind": 3, "Light": 4, "Dark": 5, "Astra": 6, "Anima": 7}

BLESSING_COLORS = ["#e63b10", "#0f93f2", "#9e621e", "#449e1e", "#f2ee6f", "#4b1694", "#ed4ed3", "#e2e3da"]
BLESSING_TEXTS  = ["#7a270d", "#b8e6e2", "#dec381", "#a3e89e", "#3f4036", "#e3bee6", "#4f4c44", "#261f23"]

help_text = "Drag heroes from My Units onto the colored squares. Double click to remove them.\nRight click on a placed hero to edit their build (does not affect saved build).\nLeft click an empty colored square to create a new unit for specifically this map."


ar_struct_names = []

for index, row in struct_sheet.iterrows():
    cur_name = row['Name']
    category = row['Category']
    offense_exists = row['Offense Exists']
    defense_exists = row['Defense Exists']

    if category == "AR-STRUCT" or cur_name == "Fortress":
        if offense_exists:
            ar_struct_names.append(cur_name + " (O)" if defense_exists else cur_name)
        if defense_exists:
            ar_struct_names.append(cur_name + " (D)" if offense_exists else cur_name)
    elif category != "WALL":
        ar_struct_names.append(cur_name)

# Panic Manor, Tactics Room, Heavy Trap, Hex Trap
def get_tower_hp_threshold(level):
    if 1 <= level <= 9:
        return level * 5 + 35
    else:
        return level * 2 + 62

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
    # This is a 2D array where exclusive_all[i] is a list of int names of Heroes who can use weapons[i].
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
                           "Stone", "Elstone", "Atlas", "Atlas+",
                           "Assault", "Absorb", "Absorb+", "Fear", "Fear+", "Slow", "Slow+", "Gravity", "Gravity+", "Panic", "Panic+", "Pain", "Pain+", "Trilemma", "Trilemma+",
                           "Fire Breath", "Fire Breath+", "Flametongue", "Flametongue+", "Lightning Breath", "Lightning Breath+", "Light Breath", "Light Breath+", "Water Breath", "Water Breath+",

                           "Whelp (Infantry)", "Yearling (Infantry)", "Adult (Infantry)", "Whelp (Cavalry)", "Yearling (Cavalry)", "Adult (Cavalry)",
                           "Hatchling (Flier)", "Fledgling (Flier)", "Adult (Flier)", "Whelp (Armored)", "Yearling (Armored)", "Adult (Armored)",

                           "Wo Dao", "Wo Dao+", "Harmonic Lance", "Harmonic Lance+", "Wo Gùn", "Wo Gùn+", "Short Bow", "Short Bow+",
                           "Firesweep Bow", "Firesweep Bow+", "Firesweep Lance", "Firesweep L+", "Firesweep S", "Firesweep S+", "Firesweep Axe", "Firesweep Axe+",
                           "Rauðrowl", "Rauðrowl+", "Gronnowl", "Gronnowl+", "Blárowl", "Blárowl+",
                           "Zanbato", "Zanbato+", "Ridersbane", "Ridersbane+", "Poleaxe", "Poleaxe+", "Caltrop Dagger", "Caltrop Dagger+"
                           "Slaying Edge", "Slaying Edge+", "Slaying Lance", "Slaying Lance+", "Slaying Axe", "Slaying Axe+", "Slaying Bow", "Slaying Bow+",
                           "Keen Rauðrwolf", "Keen Rauðrwolf+", "Keen Blárwolf", "Keen Blárwolf+", "Keen Gronnwolf", "Keen Gronnwolf+",
                           "Armorsmasher", "Armorsmasher+", "Slaying Spear", "Slaying Spear+", "Slaying Hammer", "Slaying Hammer+", "Guard Bow", "Guard Bow+",
                           "Respisal Lance", "Reprisal Lance+", "Reprisal Axe", "Reprisal Axe+",
                           "Safeguard", "Safeguard+", "Vanguard", "Vanguard+", "Rearguard", "Readguard+",
                           "Barrier Blade", "Barrier Blade+", "Barrier Lance", "Barrier Lance+", "Barrier Axe", "Barrier Axe+",
                           "The Cleaner", "The Cleaner+", "Shining Bow", "Shining Bow+", "Dragonslasher", "Dragonslasher+", "Spendthrift Bow", "Spendthrift Bow+",
                           "Flash", "Flash+", "Melancholy", "Melancholy+", "Respite", "Respite+",
                           "Rauðrserpent", "Rauðrserpent+", "Blárserpent", "Blárserpent+", "Gronnserpent", "Gronnserpent+",
                           "Rauðrfox", "Rauðrfox+", "Blárfox", "Blárfox+", "Gronnfox", "Gronnfox+",
                           "Spirited Sword", "Spirited Sword+", "Spirited Spear", "Spirited Spear+", "Spirited Axe", "Spirited Axe+",
                           "Instant Sword", "Instant Sword+", "Instant Lance", "Instant Lance+", "Instant Axe", "Instant Axe+", "Instant Bow", "Instant Bow+",
                           "Unbound Blade", "Unbound Blade+", "Unbound Lance", "Unbound Lance+", "Unbound Axe", "Unbound Axe+",
                           "Steadfast Sword", "Steadfast Sword+", "Steadfast Lance", "Steadfast Lance+", "Steadfast Axe", "Steadfast Axe+",
                           "Guard Sword", "Guard Sword+", "Guard Lance", "Guard Lance+", "Guard Axe", "Guard Axe+",
                           "Rein Sword", "Rein Sword+", "Rein Lance", "Rein Lance+", "Rein Axe", "Rein Axe+", "Rein Bow", "Rein Bow+",
                           "Rauðrrabbit", "Rauðrrabbit+", "Blárrabbit", "Blárrabbit+", "Gronnrabbit", "Gronnrabbit+",
                           "Rauðrlion", "Rauðrlion+", "Blárlion", "Blárlion+",
                           "Stout Lance", "Stout Lance+", "Axe Lance", "Axe Lance+",
                           "Quick Dagger", "Quick Dagger+", "Vicious Dagger", "Vicious Dagger+", "Armorpin Dagger", "Armorpin Dagger+",
                           "Rauðrvulture", "Rauðrvulture+", "Gronnvulture", "Gronnvulture+", "Hvítrvulture", "Hvítrvulture+",
                           "Allied Sword", "Allied Sword+", "Allied Lance", "Allied Lance+",
                           "Vulture Blade", "Vulture Blade+", "Vulture Lance", "Vulture Lance+", "Vulture Axe", "Vulture Axe+",
                           "Up-Front Blade", "Up-Front Blade+",
                           "Defier's Lance", "Defier's Lance+",
                           "Rauðrcrab", "Rauðrcrab+",

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
                           "Bottled Juice",  "Bottled Juice+", "Devilish Bow", "Devilish Bow+", "Witchy Wand", "Witchy Wand+", "Hack-o'-Lantern", "Hack-o'-Lantern+",
                           "Joyous Lantern", "Joyous Lantern+", "Glittering Breath", "Glittering Breath+", "Goodie Boot", "Goodie Boot+",
                           "Kabura Ya", "Kabura Ya+", "Geishun", "Geishun+", "Kumade", "Kumade+", "Wagasa", "Wagasa+",
                           "It's Curtains...", "It's Curtains...+", "Grandscratcher", "Grandscratcher+", "Red-Hot Ducks", "Red-Hot Ducks+", "Splashy Bucket", "Splashy Bucket+", "Ouch Pouch", "Ouch Pouch+",
                           "Faithful Axe", "Faithful Axe+", "Gronnblooms", "Gronnblooms+", "Blárblooms", "Blárblooms+", "Heart's Blade", "Heart's Blade+", "Loyal Wreath", "Loyal Wreath+",
                           "Ovoid Staff", "Ovoid Staff+", "Flashing Carrot", "Flashing Carrot+", "Pegasus Carrot", "Pegasus Carrot+", "Beguiling Bow", "Beguiling Bow+",
                           "Luncheon Lance", "Luncheon Lance+", "Toasty Skewer", "Toasty Skewer+", "Sandwiches!", "Sandwiches!+",
                           "Vessel of Cheer", "Vessel of Cheer+", "Cake Cutter", "Cake Cutter+", "Lofty Blossoms", "Lofty Blossoms+", "Bouquet Bow", "Bouquet Bow+",
                           "Tropical Treats", "Tropical Treats+", "Sandfort Spade", "Sandfort Spade+", "Buoyboard", "Buoyboard+", "Shoreline Rake", "Shoreline Rake+",
                           "Broadleaf Fan", "Broadleaf Fan+", "Scallop Blade", "Scallop Blade+", "Big-Catch Bow", "Big-Catch Bow+", "Petal Parasol", "Petal Parasol+",
                           "Fiddlestick Bow", "Fiddlestick Bow+", "Silver Goblet", "Silver Goblet+",
                           "Pumpkin-a-Box", "Pumpkin-a-Box+", "Spooky Censer", "Spooky Censer+", "Madness Flask", "Madness Flask+", "Candlewax Bow", "Candlewax Bow+",
                           "Tannenbit", "Tannenbit+", "Bellringer", "Bellringer+", "Minty Cane", "Minty Cane+",
                           "Fortune Bow", "Fortune Bow+", "Temari", "Temari+",
                           "Melee Bouquet", "Melee Bouquet+", "Budding Bow", "Budding Bow+", "Rapport Wand", "Rapport Wand+",
                           "Gilt Fork", "Gilt Fork+", "Carrot Cudgel", "Carrot Cudgel+",
                           "Pledged Blade", "Pledged Blade+", "Huge Fan", "Huge Fan+",
                           "Coral Bow", "Coral Bow+", "Flora Guide", "Flora Guide+", "Palm Staff", "Palm Staff+",
                           "Melon Float", "Melon Float+", "Hidden Thorns", "Hidden Thorns+", "Conch Bouquet", "Conch Bouquet+",
                           "Flowing Lance", "Flowing Lance+", "Helm Bow", "Helm Bow+", "Deck Swabber", "Deck Swabber+",
                           "Courtly Bow", "Courtly Bow+", "Courtly Mask", "Courtly Mask+", "Courtly Fan", "Courtly Fan+", "Courtly Candle", "Courtly Candle+",
                           "Blackfire Breath", "Blackfire Breath+", "Pale Breath", "Pale Breath+",
                           "Ninja Katana", "Ninja Katana+", "Ninja Yari", "Ninja Yari+", "Ninja Masakari", "Ninja Masakari+",
                           "Candy Cane", "Candy Cane+", "Tannenbaton", "Tannenbaton+", "Reindeer Bow", "Reindeer Bow+",
                           "Plegian Bow", "Plegian Bow+", "Plegian Torch", "Plegian Torch+", "Plegian Axe", "Plegian Axe+",
                           "Unity Blooms", "Unity Blooms+", "Amity Blooms", "Amity Blooms+", "Pact Blooms", "Pact Blooms+",
                           "Springy Lance", "Springy Lance+", "Springy Bow", "Springy Bow+", "Springy Axe", "Springy Axe+",
                           "Observant Staff", "Observant Staff+", "Love Bouquet", "Love Bouquet+", "Love Candelabra", "Love Candelabra+",
                           "Victorfish", "Victorfish+", "Peachy Parfait", "Peachy Parfait+", "Sunflower Bow", "Sunflower Bow+",
                           "Helmsman Axe", "Helmsman Axe+",
                           "Drifting Grace", "Drifting Grace+", "Luminous Grace", "Luminous Grace+", "Staff of Twelve", "Staff of Twelve+",
                           "Lantern Breath", "Lantern Breath+", "Spider Plush", "Spider Plush+",
                           "Ninja Yumi", "Ninja Yumi+", "Shuriken Cleaver", "Shuriken Cleaver+", "Ninja Naginata", "Ninja Naginata+",
                           "Snow Globe", "Snow Globe+", "Tannenbow", "Tannenbow+", "Winter Rapier", "Winter Rapier+",
                           "Serpentine Staff", "Serpentine Staff+", "Bone Carver", "Bone Carver+",
                           "Staff of Tribute", "Staff of Tribute+", "Piercing Tribute", "Piercing Tribute+",
                           "Carrot-Tip Spear", "Carrot-Tip Spear+", "Carrot-Tip Bow", "Carrot-Tip Bow+",
                           "Bridal Orchid", "Bridal Orchid+", "Bridal Sunflower", "Bridal Sunflower+",
                           "Whitecap Bow", "Whitecap Bow+",
                           "Coral Saber", "Coral Saber+", "Seahorse Axe", "Seahorse Axe+",
                           "Florid Cane", "Florid Cane+", "Florid Knife", "Florid Knife+",
                           "Flame Gunbai", "Flame Gunbai+",
                           "Serenity Breath", "Serenity Breath+", "Surprise Breath", "Surprise Breath+",
                           "Wyvern Yumi", "Wyvern Yumi+", "Wyvern Katana", "Wyvern Katana+",

                           "Arcane Éljúðnir",
                           "Arcane Downfall",
                           "Arcane Grima"
                           ]

    # Remove of different weapon
    i = 0
    while i < len(weapons):

        # encoding issues today?
        # print(weapons[i])

        if weapon_types[i] in cur_hero.wpnType:
            if len(exclusive_all[i]) == 0:
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

    refine_substrings = ["Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz", "Eff2", "Atk2", "Spd2", "Def2", "Res2", "Wra2", "Daz2",]

    # Remove PRF refines
    for string in prf_weapons:
        is_valid = True
        for substring in refine_substrings:
            if substring in string[-3:] or (len(string) > 3 and substring in string[-4:]):
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

    # Get next 10 rows, check for refines
    start = min(row_index + 1, len(weapon_names))
    end = min(row_index + 11, len(weapon_names))
    next_rows = weapon_names[start:end]

    # By default, all weapons can be unrefined
    refine_suffixes = ["None"]

    for row in next_rows:
        # If weapon is same as the one currently equipped, add its suffix
        if weapon_name == row[:-3]:
            refine_suffixes.append(row[-3:])
        if len(weapon_name) > 3 and weapon_name == row[:-4]:
            refine_suffixes.append(row[-4:])


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
                           "Rescue", "Rescue+", "Return", "Return+", "Nudge", "Nudge+",
                           "Rally Attack", "Rally Speed", "Rally Defence", "Rally Resistance",
                           "Rally Atk/Spd", "Rally Atk/Def", "Rally Atk/Res", "Rally Spd/Def", "Rally Spd/Res", "Rally Def/Res",
                           "Rally Atk/Spd+", "Rally Atk/Def+", "Rally Atk/Res+", "Rally Spd/Def+", "Rally Spd/Res+", "Rally Def/Res+",
                           "Rally Up Atk", "Rally Up Atk+", "Rally Up Spd", "Rally Up Spd+", "Rally Up Def", "Rally Up Def+", "Rally Up Res", "Rally Up Res+",
                           "Dance", "Sing", "Play",
                           "Harsh Command", "Harsh Command+", "Ardent Sacrifice", "Reciprocal Aid",
                           "Draw Back", "Reposition", "Swap", "Pivot", "Shove", "Smite"]

    i = 0
    while i < len(assist_names):
        if cur_hero.intName in exclusive_all[i]:
            prf_assists.append(assist_names[i])

        elif assist_names[i] in implemented_assists:
            if (len(exclusive_all[i]) == 0) and cur_hero.wpnType != "Staff":
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
                            "Daylight", "Noontime", "Sol", "Aether",
                            "Blue Flame", "Ruptured Sky", "Deadeye", "Lethality", "Vital Astra", "Godlike Reflexes",
                            "Galeforce",
                            "Rising Flame", "Blazing Flame", "Growing Flame",
                            "Rising Light", "Blazing Light", "Growing Light",
                            "Rising Thunder", "Blazing Thunder", "Growing Thunder",
                            "Rising Wind", "Blazing Wind", "Growing Wind",
                            "Buckler", "Escutcheon", "Pavise", "Holy Vestments", "Sacred Cowl", "Aegis", "Miracle",
                            "Imbue", "Heavenly Light", "Kindled-Fire Balm", "Swift-Winds Balm", "Solid-Earth Balm", "Still-Water Balm",
                            "Windfire Balm", "Windfire Balm+", "Earthfire Balm", "Earthfire Balm+", "Fireflood Balm", "Fireflood Balm+",
                            "Deluge Balm", "Deluge Balm+", "Earthwater Balm", "Earthwater Balm+"]

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
    skill_names = hero.skills_sheet["Name"]
    skill_letters = hero.skills_sheet["Letter"]

    exclusive1 = list(hero.skills_sheet['ExclusiveUser1'])
    exclusive2 = list(hero.skills_sheet['ExclusiveUser2'])
    exclusive3 = list(hero.skills_sheet['ExclusiveUser3'])

    restr_move = list(hero.skills_sheet['RestrictedMovement'])
    restr_wpn = list(hero.skills_sheet['RestrictedWeapons'])

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

            if "Colorless" in restr_wpn[i] and cur_hero.wpnType in hero.COLORLESS_WEAPONS: add_cond = False
            if "Red" in restr_wpn[i] and cur_hero.wpnType in hero.RED_WEAPONS: add_cond = False
            if "Blue" in restr_wpn[i] and cur_hero.wpnType in hero.BLUE_WEAPONS: add_cond = False
            if "Green" in restr_wpn[i] and cur_hero.wpnType in hero.GREEN_WEAPONS: add_cond = False

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
            if restr_wpn[i] == "NotSwordLanceAxe" and cur_hero.wpnType not in ["Sword", "Lance", "Axe"]: add_cond = False

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
        self.pair_up = None

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
        self.pair_up = None

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
        if apl_hero is None:
            return

        # Neutral Input
        if self.asset == -1 and self.flaw == -1:
            self.asset = 0
            self.flaw = 0

        if self.asc_asset == -1:
            self.asc_asset = self.asset

        apl_hero.emblem = self.emblem

        apl_hero.set_rarity(self.rarity)
        apl_hero.set_IVs(self.asset, self.flaw, self.asc_asset)
        apl_hero.set_merges(self.merge)
        apl_hero.set_dragonflowers(self.dflowers)

        if self.emblem != None: apl_hero.set_emblem_merges(self.emblem_merge)

        apl_hero.set_level(self.level)

        apl_hero.allySupport = _intName_dict[self.a_support]

        apl_hero.summonerSupport = int(self.s_support)
        apl_hero.resp = self.resplendent

        apl_hero.set_visible_stats()

        apl_hero.pair_up = self.pair_up

        if self.weapon is not None:
            wpn_name = self.weapon.intName

            refine_substrings = ["Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz", "Eff2", "Atk2", "Spd2", "Def2", "Res2", "Wra2", "Daz2"]

            if wpn_name[-3:] in refine_substrings:
                wpn_name = wpn_name[:-3]
            elif len(wpn_name) > 3 and wpn_name[-4:] in refine_substrings:
                wpn_name = wpn_name[:-4]

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
def _apply_battle_stats(team, bonus_arr, mode, season, ar_structs):

    if mode == hero.GameMode.Story and team[0].side == ENEMY:
        return

    element_boosts = {}

    for unit in team:
        # If unit is a legendary or mythic, and current season is of their element
        if unit.blessing and unit.blessing.boostType != 0 and unit.blessing.element in season:

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

            elif unit.blessing.element in hero.AETHER_ELEMENTS and mode == hero.GameMode.AetherRaids:

                # Initialize values in element_boosts dict
                if unit.blessing.element not in element_boosts:
                    element_boosts[unit.blessing.element] = [0, 0, 0, 0, 0]

                # HP boost
                element_boosts[unit.blessing.element][HP] += 5

                # Other stats boost
                if unit.blessing.stat == ATK:
                    element_boosts[unit.blessing.element][ATK] += 3
                elif unit.blessing.stat == SPD:
                    element_boosts[unit.blessing.element][SPD] += 4
                elif unit.blessing.stat == DEF:
                    element_boosts[unit.blessing.element][DEF] += 5
                elif unit.blessing.stat == RES:
                    element_boosts[unit.blessing.element][RES] += 5

    for unit in team:
        unit.battle_stat_mods = [0] * 5

        if unit.blessing is not None and unit.blessing.boostType == 0 and unit.blessing.element in element_boosts:
            unit.battle_stat_mods = element_boosts[unit.blessing.element]
            unit.set_visible_stats()

    ar_o_fortress = 1
    ar_d_fortress = 1

    for struct in ar_structs:
        if struct.name == "Fortress":
            if struct.struct_type == PLAYER + 1:
                ar_o_fortress = struct.level
            elif struct.struct_type == ENEMY + 1:
                ar_d_fortress = struct.level

    if team[0].side == PLAYER:
        difference = max(0, ar_o_fortress - ar_d_fortress)
    else:
        difference = max(0, ar_d_fortress - ar_o_fortress)

    i = 0
    while i < len(team):
        unit = team[i]

        if bonus_arr[i]:
            unit.battle_stat_mods[HP] += 10
            unit.battle_stat_mods[ATK] += 4
            unit.battle_stat_mods[SPD] += 4
            unit.battle_stat_mods[DEF] += 4
            unit.battle_stat_mods[RES] += 4

        if mode == hero.GameMode.AetherRaids:
            unit.battle_stat_mods[ATK] += 4 * difference
            unit.battle_stat_mods[SPD] += 4 * difference
            unit.battle_stat_mods[DEF] += 4 * difference
            unit.battle_stat_mods[RES] += 4 * difference

        if unit.pair_up_obj:
            unit.battle_stat_mods[ATK] += max(min(trunc(unit.pair_up_obj.visible_stats[ATK] - 25) / 10, 4), 0)
            unit.battle_stat_mods[SPD] += max(min(trunc(unit.pair_up_obj.visible_stats[SPD] - 10) / 10, 4), 0)
            unit.battle_stat_mods[DEF] += max(min(trunc(unit.pair_up_obj.visible_stats[DEF] - 10) / 10, 4), 0)
            unit.battle_stat_mods[RES] += max(min(trunc(unit.pair_up_obj.visible_stats[RES] - 10) / 10, 4), 0)

            unit.pair_up_obj.battle_stat_mods[ATK] += max(min(trunc(unit.visible_stats[ATK] - 25) / 10, 4), 0)
            unit.pair_up_obj.battle_stat_mods[SPD] += max(min(trunc(unit.visible_stats[SPD] - 10) / 10, 4), 0)
            unit.pair_up_obj.battle_stat_mods[DEF] += max(min(trunc(unit.visible_stats[DEF] - 10) / 10, 4), 0)
            unit.pair_up_obj.battle_stat_mods[RES] += max(min(trunc(unit.visible_stats[RES] - 10) / 10, 4), 0)

            unit.pair_up_obj.set_visible_stats()

        unit.set_visible_stats()

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

        self.active_sims = []

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

        self.list_of_build_names = []

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

        self.within_widget = False

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

        # Disable Pair Up/Duo or Harmonic Skill/Style
        for sim in self.active_sims:
            sim.button_frame.action_button.config(state='disabled', text='Action\nButton')
            CreateToolTip(sim.button_frame.action_button, text='')

    def on_drag(self, event):

        target_widget = event.widget.winfo_containing(event.x_root, event.y_root)

        if target_widget == self.target_widget and target_widget != self.default_target_widget and not self.within_widget:
            self.within_widget = True

            self.target_widget.toggle_valid_ar_start_spaces()

        elif target_widget != self.target_widget and self.within_widget:
            self.within_widget = False

            self.target_widget.toggle_valid_ar_start_spaces()


    def on_release(self, event):
        if self.within_widget:
            self.target_widget.toggle_valid_ar_start_spaces()
            self.within_widget = False

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

                    dflowers = hero_to_add.flowers
                    resp = hero_to_add.resp
                    emblem = None
                    emblem_merges = 0

                    aided = hero_to_add.aided
                    pair_up = hero_to_add.pair_up

                    cheats = False

                    data = [name, cur_build_name,
                            weapon, assist, special, askill, bskill, cskill, sSeal, xskill,
                            level, merges, rarity, asset, flaw, asc, sSupport, aSupport, blessing, dflowers, resp, emblem, emblem_merges, aided, pair_up, cheats]

                    my_units_file = "my_units.csv"
                    names = pd.read_csv(my_units_file, encoding='cp1252')['Build Name'].tolist()

                    # Ensure build name is unique
                    if cur_build_name not in names and cur_build_name != "None":
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
                        self.error_text.config(fg='#d60408', text="Error: Duplicate/Invalid Build Name")
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
            inf_icon = inf_icon.resize((24, 24))
            move_icons.append(ImageTk.PhotoImage(inf_icon))
            cav_icon = status_pic.crop((462, 414, 518, 468))
            cav_icon = cav_icon.resize((24, 24))
            move_icons.append(ImageTk.PhotoImage(cav_icon))
            fly_icon = status_pic.crop((518, 414, 572, 468))
            fly_icon = fly_icon.resize((24, 24))
            move_icons.append(ImageTk.PhotoImage(fly_icon))
            arm_icon = status_pic.crop((406, 414, 462, 468))
            arm_icon = arm_icon.resize((24, 24))
            move_icons.append(ImageTk.PhotoImage(arm_icon))

            weapon_icons = []
            i = 0
            while i < 24:
                cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
                cur_icon = cur_icon.resize((25, 25))
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

            self.list_of_build_names.clear()

            my_units = pd.read_csv("my_units.csv", encoding='cp1252')["Build Name"]
            self.list_of_build_names = list(my_units)

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

                # PAIR UP
                if row == 6:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_pairup)

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

                # RESPLENDENT
                if row == 0:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_resp)

                # LEVEL
                if row == 1:
                    combo1['textvariable'] = None
                    combo1['values'] = list(reversed(numbers[1:41]))
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_level)

                # DRAGONFLOWERS
                if row == 2:
                    combo1['textvariable'] = None
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_dflowers)

                # FLAW
                if row == 3:
                    combo1['textvariable'] = None
                    combo1['values'] = iv_strs
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_flaw)

                if row == 4:
                    combo1['textvariable'] = None
                    combo1['values'] = iv_strs
                    combo1.bind("<<ComboboxSelected>>", self.handle_selection_change_ascasset)

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
        resized_image = cur_image.resize((int(cur_image.width / 1.3), int(cur_image.height / 1.3)))
        curPhoto = ImageTk.PhotoImage(resized_image)
        self.creation_image_label.config(image=curPhoto)
        self.creation_image_label.image = curPhoto

        # Actual Hero object
        self.created_hero: hero.Hero = hero.makeHero(cur_intName)

        # Set default value in ComboBoxes upon first Hero selection
        self.creation_str_vars[1].set(min(5, self.hero_proxy.rarity))
        self.creation_str_vars[2].set(max(0, self.hero_proxy.merge))

        if self.hero_proxy.asset != self.hero_proxy.flaw:
            self.creation_str_vars[3].set(STAT_STR[self.hero_proxy.asset])
            self.creation_str_vars[16].set(STAT_STR[self.hero_proxy.flaw])
        else:
            self.creation_str_vars[3].set("None")
            self.creation_str_vars[16].set("None")

        if self.hero_proxy.asset != self.hero_proxy.asc_asset:
            self.creation_str_vars[17].set(STAT_STR[self.hero_proxy.asc_asset])
        else:
            self.creation_str_vars[17].set("None")

        # Set default Asc Asset
        # creation_str_vars[16].set(STAT_STR[curProxy.asc_asset])

        # Set default level
        self.creation_str_vars[14].set(min(40, self.hero_proxy.level))

        # Set Blessing
        if self.created_hero.blessing is None:
            self.creation_str_vars[4].set("None")
            self.creation_comboboxes[4]['values'] = ["None", "Fire", "Water", "Earth", "Wind", "Light", "Dark", "Astra", "Anima"]
        else:
            if self.created_hero.blessing.boostType != 0:
                self.creation_str_vars[4].set(self.created_hero.blessing.toString())
            self.creation_comboboxes[4]['values'] = []

        self.hero_proxy.blessing = self.created_hero.blessing

        # Resplendant status
        cur_hero_row = hero.hero_sheet.loc[hero.hero_sheet["IntName"] == cur_intName]

        if cur_hero_row.iloc[0]["HasResp"]:
            self.creation_comboboxes[13]['values'] = ['True', 'False']

            if self.hero_proxy.resplendent:
                self.creation_comboboxes[13].set('True')
            else:
                self.creation_comboboxes[13].set('False')

        else:
            self.creation_comboboxes[13]['values'] = ['False']
            self.creation_comboboxes[13].set('False')

        self.handle_selection_change_resp()

        # Set Pair Up
        if self.created_hero.blessing and self.created_hero.blessing.boostType <= 2 and self.created_hero.blessing.element < 4:
            self.creation_comboboxes[6]['values'] = ["None"] + self.list_of_build_names

            if not self.creation_str_vars[6].get():
                self.creation_str_vars[6].set("None")

        else:
            self.creation_comboboxes[6]['values'] = ["None"]
            self.creation_str_vars[6].set("None")

        # Set Dragonflowers
        if self.creation_str_vars[15].get() and int(self.creation_str_vars[15].get()) > self.created_hero.flower_limit:
            self.creation_str_vars[15].set(self.created_hero.flower_limit)
        elif not self.creation_str_vars[15].get():
            self.creation_str_vars[15].set(0)

        self.creation_comboboxes[15]['values'] = list(range(0, self.created_hero.flower_limit + 1))

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

        # Autofill kit
        if pd.notnull(cur_hero_row.iloc[0]["BaseWeapon"]):
            self.creation_str_vars[7].set(cur_hero_row.iloc[0]["BaseWeapon"])
            self.handle_selection_change_weapon(cur_hero_row.iloc[0]["BaseWeapon"])

        if pd.notnull(cur_hero_row.iloc[0]["BaseAssist"]):
            self.creation_str_vars[9].set(cur_hero_row.iloc[0]["BaseAssist"])
            self.handle_selection_change_assist(cur_hero_row.iloc[0]["BaseAssist"])

        if pd.notnull(cur_hero_row.iloc[0]["BaseSpecial"]):
            self.creation_str_vars[10].set(cur_hero_row.iloc[0]["BaseSpecial"])
            self.handle_selection_change_special(cur_hero_row.iloc[0]["BaseSpecial"])

        if pd.notnull(cur_hero_row.iloc[0]["BaseA"]):
            self.creation_str_vars[20].set(cur_hero_row.iloc[0]["BaseA"])
            self.handle_selection_change_askill(cur_hero_row.iloc[0]["BaseA"])

        if pd.notnull(cur_hero_row.iloc[0]["BaseB"]):
            self.creation_str_vars[21].set(cur_hero_row.iloc[0]["BaseB"])
            self.handle_selection_change_bskill(cur_hero_row.iloc[0]["BaseB"])

        if pd.notnull(cur_hero_row.iloc[0]["BaseC"]):
            self.creation_str_vars[22].set(cur_hero_row.iloc[0]["BaseC"])
            self.handle_selection_change_cskill(cur_hero_row.iloc[0]["BaseC"])

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

        self.hero_proxy.apply_proxy(self.created_hero)

        move_icons = []
        status_pic = Image.open("CombatSprites/Status.png")

        inf_icon = status_pic.crop((350, 414, 406, 468))
        inf_icon = inf_icon.resize((24, 24))
        move_icons.append(ImageTk.PhotoImage(inf_icon))
        cav_icon = status_pic.crop((462, 414, 518, 468))
        cav_icon = cav_icon.resize((24, 24))
        move_icons.append(ImageTk.PhotoImage(cav_icon))
        fly_icon = status_pic.crop((518, 414, 572, 468))
        fly_icon = fly_icon.resize((24, 24))
        move_icons.append(ImageTk.PhotoImage(fly_icon))
        arm_icon = status_pic.crop((406, 414, 462, 468))
        arm_icon = arm_icon.resize((24, 24))
        move_icons.append(ImageTk.PhotoImage(arm_icon))

        weapon_icons = []
        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
            cur_icon = cur_icon.resize((25, 25))
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

    def handle_selection_change_resp(self, event=None):
        selected_value = self.creation_str_vars[13].get()

        if selected_value == "True":
            self.hero_proxy.resplendent = True

            cur_image = Image.open("TestSprites/" + self.created_hero.intName + "-R.png")
            resized_image = cur_image.resize((int(cur_image.width / 1.3), int(cur_image.height / 1.3)))
            curPhoto = ImageTk.PhotoImage(resized_image)
            self.creation_image_label.config(image=curPhoto)
            self.creation_image_label.image = curPhoto

        else:
            self.hero_proxy.resplendent = False

            cur_image = Image.open("TestSprites/" + self.created_hero.intName + ".png")
            resized_image = cur_image.resize((int(cur_image.width / 1.3), int(cur_image.height / 1.3)))
            curPhoto = ImageTk.PhotoImage(resized_image)
            self.creation_image_label.config(image=curPhoto)
            self.creation_image_label.image = curPhoto

        self.hero_proxy.apply_proxy(self.created_hero)

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

    def handle_selection_change_dflowers(self, event=None):
        selected_value = self.creation_str_vars[15].get()

        self.hero_proxy.dflowers = int(selected_value)

        if self.created_hero is not None:
            merge_str = ""
            if self.hero_proxy.merge > 0:
                merge_str = "+" + str(self.hero_proxy.merge)

            self.unit_stats.set(f"Lv. {self.hero_proxy.level}{merge_str}\n+{self.hero_proxy.dflowers} Flowers")

            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

    def handle_selection_change_asset(self, event=None):
        selected_value = self.creation_str_vars[3].get()

        # Receiving -1 represents None
        # Set flaw to -1 as well
        stat_int = STATS[selected_value]

        # Maintain property of asset being the same as the asc asset if they are currently equal
        # Retains the property for having no Asc Asset
        if self.hero_proxy.asset == self.hero_proxy.asc_asset:
            self.hero_proxy.asc_asset = stat_int
            self.creation_str_vars[17].set("None")
        elif self.hero_proxy.asset != self.hero_proxy.asc_asset and stat_int == self.hero_proxy.asc_asset and self.hero_proxy.asc_asset != -1:
            self.hero_proxy.asc_asset = (stat_int + 1) % 5
            self.creation_str_vars[17].set(STAT_STR[self.hero_proxy.asc_asset])

        # Set new asset value
        self.hero_proxy.asset = stat_int

        # If this overlaps with the current flaw value
        if self.hero_proxy.flaw == self.hero_proxy.asset or self.hero_proxy.flaw == -1:
            # Move flaw to next possible stat
            self.hero_proxy.flaw = (STATS[selected_value] + 1) % 5

        # If this overlaps with the current asc asset

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
            self.hero_proxy.asc_asset = (stat_int + 2) % 5

        if self.hero_proxy.flaw == -1:
            self.hero_proxy.asset = -1

        self.creation_str_vars[3].set(STAT_STR[self.hero_proxy.asset])
        self.creation_str_vars[17].set(STAT_STR[self.hero_proxy.asc_asset])

        if self.created_hero is not None:
            self.hero_proxy.apply_proxy(self.created_hero)

            i = 0
            while i < 5:
                self.creation_stats[i].set(self.stat_strings[i] + str(self.created_hero.visible_stats[i]))
                i += 1

    def handle_selection_change_ascasset(self, event=None):
        selected_value = self.creation_str_vars[17].get()

        stat_int = STATS[selected_value]

        self.hero_proxy.asc_asset = stat_int

        if self.hero_proxy.asc_asset == self.hero_proxy.asset and self.hero_proxy.asset != -1:
            self.hero_proxy.asset = (stat_int + 1) % 5
            self.creation_str_vars[3].set(STAT_STR[self.hero_proxy.asset])

        if self.hero_proxy.asset == self.hero_proxy.flaw and self.hero_proxy.flaw != -1:
            self.hero_proxy.flaw = (stat_int + 2) % 5
            self.creation_str_vars[16].set(STAT_STR[self.hero_proxy.flaw])

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

    def handle_selection_change_pairup(self, event=None):
        selected_value = self.creation_str_vars[6].get()

        if selected_value == "None":
            self.hero_proxy.pair_up = None
        else:
            self.hero_proxy.pair_up = selected_value

        self.hero_proxy.apply_proxy(self.created_hero)

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

        # Resplendent
        resp = row["Resplendent"]
        if resp:
            self.creation_comboboxes[13].set("True")
        else:
            self.creation_comboboxes[13].set("False")
        self.handle_selection_change_resp()

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

        # Merges
        flowers = row["Dragonflowers"]
        self.creation_comboboxes[15].set(flowers)
        self.handle_selection_change_dflowers()

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

        # Pair Up
        pair_up = row["PairUp"]
        if pd.isnull(pair_up):
            pair_up = "None"

        self.creation_comboboxes[6].set(pair_up)
        if row["Build Name"] in self.creation_comboboxes[6]['values']:
            self.creation_comboboxes[6]['values'] = tuple(item for item in self.creation_comboboxes[6]['values'] if item != row["Build Name"])

        self.handle_selection_change_pairup()

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
        title_name = unit.name + ": " + unit.epithet
        self.creation_comboboxes[0].set(title_name)
        self.handle_selection_change_name()

        # Resplendent
        resp = unit.resp

        if resp:
            self.creation_comboboxes[13].set("True")
        else:
            self.creation_comboboxes[13].set("False")
        self.handle_selection_change_resp()

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

        # Dragonflowers
        flowers = unit.flowers
        self.creation_comboboxes[15].set(flowers)
        self.handle_selection_change_dflowers()

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

        # Pair Up
        pair_up = unit.pair_up
        if pair_up is None:
            pair_up = "None"

        self.creation_comboboxes[6].set(pair_up)
        self.handle_selection_change_pairup()

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
            build_name = data.loc[index, "Build Name"]
            data = data.drop(index)
            data.loc[data["PairUp"] == build_name, "PairUp"] = None
            data.to_csv("my_units.csv", index=False, encoding='cp1252')

            self.delete_inactive_pairup(build_name)

            self.selected_button.forget()
            self.selected_button = None

            self.edit_button.config(state="normal")
            self.delete_button.config(state="normal")

            self.refresh_buttons(False)

            if self.creation_menu:
                self.unit_creation_cancel()

    def update_active_pairups(self, old_build_name, new_build_name):
        for sim in self.active_sims:
            for drag_point in sim.canvas.unit_drag_points.values():
                if drag_point.hero and drag_point.hero.pair_up == old_build_name:
                    drag_point.hero.pair_up = new_build_name

    def delete_inactive_pairup(self, removed_build_name):
        for sim in self.active_sims:
            for drag_point in sim.canvas.unit_drag_points.values():
                if drag_point.hero and drag_point.hero.pair_up == removed_build_name:
                    drag_point.hero.pair_up = None

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

            dflowers = hero_to_add.flowers
            resp = hero_to_add.resp
            emblem = None
            emblem_merges = 0

            aided = False

            pair_up = hero_to_add.pair_up

            cheats = False

            data = [name, cur_build_name,
                    weapon, assist, special, askill, bskill, cskill, sSeal, xskill,
                    level, merges, rarity, asset, flaw, asc, sSupport, aSupport, blessing, dflowers, resp, emblem, emblem_merges, aided, pair_up, cheats]

            my_units_file = "my_units.csv"
            names = pd.read_csv(my_units_file, encoding='cp1252')['Build Name'].tolist()

            # Ensure build name is unique, or name is unchanged
            if (cur_build_name not in names or names[index] == cur_build_name) and cur_build_name != "None":

                try:
                    my_units_file = "my_units.csv"

                    with open(my_units_file, 'r', newline='', encoding="cp1252") as file:
                        f_reader = reader(file)
                        read_data = list(f_reader)

                    # If any Pair Up units have this unit as their cohort, modify the name in that pair-up
                    old_build_name = read_data[index + 1][1]

                    read_data[index + 1] = data

                    i = 1
                    while i < len(read_data):
                        if read_data[i][-2] == old_build_name:
                            read_data[i][-2] = cur_build_name
                        i += 1

                    with open(my_units_file, mode="w", newline='', encoding="cp1252") as file:
                        f_writer = writer(file)
                        f_writer.writerows(read_data)

                    self.update_active_pairups(old_build_name, cur_build_name)

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
                self.error_text.config(fg='#d60408', text="Error: Duplicate/Invalid Build Name")
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

class _ReinforcementPoint:
    def __init__(self, tile_num, start_turn, num_spawns, target_name, target_amount):
        self.hero = None
        self.side = ENEMY

        self.tile = tile_num

        # Turn that reinforcements start spawning in
        self.turn = start_turn

        # Number of times this reinforcement point can keep spawning
        self.spawns_remaining = num_spawns
        self.max_spawns = num_spawns

        # Internal name of unit to be tracked for kill/alive conditions
        # Kill condition spawners spawn when a certain number of this type of unit are killed
        # Alive condition spawners check to see if there are no more of this type of unit alive to start spawning
        self.target_name = target_name

        # Amount killed required for this reinforcement to start.
        # A value of -1 indicates this is an Alive-type spawner.
        self.target_amount = target_amount

def get_row_from_build_name(build_name):
    df = pd.read_csv("my_units.csv", encoding='cp1252')
    df = df.set_index("Build Name")
    if build_name in df.index:
        return df.loc[build_name]
    else:
        return None

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
    unit.resp = row_data["Resplendent"]

    if pd.isnull(row_data["SSupport"]):
        unit.summonerSupport = 0

    unit.set_visible_stats()

    if not pd.isnull(row_data["PairUp"]):
        unit.pair_up = row_data["PairUp"]

    if side == ENEMY:
        unit.pair_up = None

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
    image = image.resize((25,25))

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

        if unit.tile:
            self.cur_position = unit.tile.tileNum
        else:
            self.cur_position = -1

        self.cur_buffs = unit.buffs[:]
        self.cur_debuffs = unit.debuffs[:]
        self.cur_status_pos = unit.statusPos[:]
        self.cur_status_neg = unit.statusNeg[:]

        self.cur_status_other = deepcopy(unit.statusOther)

        self.sp_galeforce = unit.special_galeforce_triggered
        self.nsp_galeforce = unit.nonspecial_galeforce_triggered
        self.once_per_map_cond = unit.once_per_map_cond

        self.canto = unit.canto_ready

        self.transformed = unit.transformed

        self.num_combats = unit.unitCombatInitiates

        self.num_assists_self = unit.assistTargetedSelf
        self.num_assists_self_rally = unit.assistTargetedSelf_Rally
        self.num_assists_self_move = unit.assistTargetedSelf_Move
        self.num_assists_self_other = unit.assistTargetedSelf_Other

        self.num_assists_other = unit.assistTargetedOther
        self.num_assists_other_rally = unit.assistTargetedOther_Rally
        self.num_assists_other_move = unit.assistTargetedOther_Move
        self.num_assists_other_other = unit.assistTargetedOther_Other

        self.duo_cooldown = unit.duo_cooldown

# One state of the game
class MapState:
    def __init__(self, unit_states, struct_states, units_to_move, turn_num, reinf_points, defeated_count, dv_states, first_duo_user, duos_ind_used):
        self.unit_states = unit_states
        self.struct_states = struct_states
        self.units_to_move = units_to_move

        self.turn_num = turn_num
        self.reinf_points = reinf_points

        self.defeated_count = deepcopy(defeated_count)

        self.dv_states = dv_states

        self.first_duo_user = first_duo_user
        self.duos_ind_used = duos_ind_used

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

def create_mapstate(c_map, units_to_move, turn_num, reinf_points, defeated_count, first_duo_user, duos_ind_used):
    unit_states = {}

    for unit in c_map.get_heroes_present():
        cur_unit_state = UnitState(unit)
        unit_states[unit] = cur_unit_state

        if unit.pair_up_obj:
            cohort_state = UnitState(unit.pair_up_obj)
            unit_states[unit.pair_up_obj] = cohort_state

    struct_states = {}

    for tile in c_map.tiles:
        if tile.structure_on is not None:
            cur_struct = tile.structure_on

            struct_states[cur_struct] = cur_struct.health

    reinf_states = {}
    for tile in reinf_points:
        reinf_states[tile] = reinf_points[tile].spawns_remaining

    divine_vein_states = []
    for tile in c_map.tiles:
        divine_vein_states.append((tile.divine_vein, tile.divine_vein_side, tile.divine_vein_turn))

    return MapState(unit_states, struct_states, units_to_move[:], turn_num, reinf_states, defeated_count, divine_vein_states, first_duo_user, duos_ind_used)

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
        self.starting_tile = None
        self.has_unit_warped = False

        self.first_duo_skill_used = None
        self.indulgence_used = False

        # Currently placed movement spaces
        self.tile_sprites = []

        self.animation = False # true if an animation is currently playing, false otherwise
        self.canto = None # set to the current unit performing a canto action
        self.swap_mode = False # true if currently in swap mode, false otherwise

        self.all_units = [[], []] # all units ever present in a map
        self.current_units = [[], []] # units leading a cohort and if that cohort is on the map

        self.drag_point_units = [[], []]
        self.reinf_point_units = [[], []]

        self.all_cohorts = []

        self.unit_photos = [[], []]
        self.unit_sprites = [[], []]
        self.unit_photos_gs = [[], []] # grayscale
        self.unit_sprites_gs = [[], []]

        self.unit_photos_trans = [[], []] # transformed
        self.unit_sprites_trans = [[], []]
        self.unit_photos_gs_trans = [[], []] # grayscale, transformed
        self.unit_sprites_gs_trans = [[], []]

        self.unit_weapon_icon_photos = [[], []]
        self.unit_weapon_icon_sprites = [[], []]

        # Cohort Sprites
        self.cohort_photos = []
        self.cohort_sprites = []
        self.cohort_photos_gs = []
        self.cohort_sprites_gs = []

        self.cohort_photos_trans = []
        self.cohort_sprites_trans = []
        self.cohort_photos_gs_trans = []
        self.cohort_sprites_gs_trans = []

        self.cohort_weapon_icon_photos = [[], []]
        self.cohort_weapon_icon_sprites = [[], []]

        # Count Labels
        self.unit_sp_count_labels = [[], []]
        self.unit_hp_count_labels = [[], []]

        self.unit_hp_bars_fg = [[], []]
        self.unit_hp_bars_bg = [[], []]

        self.starting_tile_photos = []

        self.unit_tags = [[], []]

        self.ar_structs = []
        self.ar_struct_tiles = []
        self.ar_struct_sprites = []

        self.divine_vein_photos = []
        self.divine_vein_sprites = []

        self.game_mode = hero.GameMode.Story

        self.season = []

        # Preparation variables
        self.unit_drag_points = {}
        self.unit_reinf_points = {}

        self.enemy_defeated_count = {}

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
        blue_tile = Image.open("CombatSprites/" + "tileblue" + ".png").resize((self.TILE_SIZE, self.TILE_SIZE))
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
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260)).resize((25, 25))
            self.weapon_type_photos.append(ImageTk.PhotoImage(cur_icon))
            i += 1

        # AOE Special icon
        aoe_special_icon_image = status_pic.crop((1047, 419, 1200, 560)).resize((90, 90))
        self.aoe_icon = ImageTk.PhotoImage(aoe_special_icon_image)
        self.active_aoe_icons = []

        self.canto_tile_imgs = []

        self.structure_grayout_img = []

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
        self.starting_tile = None
        self.has_unit_warped = False

        self.first_duo_skill_used = None
        self.indulgence_used = False

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
            self.button_frame.action_button.config(state='disabled', text='Action\nButton')
            CreateToolTip(self.button_frame.action_button, text='')

            # Re-Enable Aether Raids Building Tab
            if self.game_mode == hero.GameMode.AetherRaids:
                self.extras.building_button.config(state='normal')

            self.map_states.clear()

            self.running = False
            self.swap_mode = False
            self.canto = None

            for tile in self.starting_tile_photos:
                index = self.starting_tile_photos.index(tile)

                cur_drag = list(self.unit_drag_points.keys())[index]

                if not self.map.tiles[cur_drag].structure_on:
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

            # Remove units from the tiles
            for tile in self.map.tiles:
                tile.hero_on = None

            self.refresh_units_prep()

            self.current_units[PLAYER].clear()
            self.current_units[ENEMY].clear()

            self.units_to_move.clear()

            self.all_cohorts.clear()

            # Restore structures to max helath
            for tile in self.map.tiles:
                if tile.structure_on:
                    tile.structure_on.health = tile.structure_on.max_health

            # Restore reinforcement points
            for spawn_point in self.unit_reinf_points.values():
                spawn_point.spawns_remaining = spawn_point.max_spawns

            self.refresh_walls()

            return

        # Else, start simulation

        # Change button's apperance to Stop Sim
        self.button_frame.start_button.config(text="Stop\nSim", bg="firebrick3")

        # Allow End Turn and Swap Spaces buttons to be used
        self.button_frame.end_turn_button.config(state="normal")
        self.button_frame.swap_spaces_button.config(state="normal")

        self.extras.building_button.config(state='disabled')

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
        result_bonus_units_player = []
        result_bonus_units_enemy = []

        i = 0
        while i < len(player_drag_points):
            if player_drag_points[i].hero:
                result_bonus_units_player.append(bonus_units[i])
            i += 1

        j = 0
        while i < len(player_drag_points + enemy_drag_points) and j < len(self.all_units[ENEMY]):
            result_bonus_units_enemy.append(bonus_units[i])

            i += 1
            j += 1

        season = []

        elem_str = self.button_frame.elemental_season_combobox.get()
        aether_str = self.button_frame.aether_season_combobox.get()

        for key in BLESSINGS_DICT:
            if key in elem_str + aether_str:
                season.append(BLESSINGS_DICT[key])

        pair_up_modes = [hero.GameMode.Story, hero.GameMode.Mjolnir, hero.GameMode.Rokkr, hero.GameMode.Allegiance]

        # Place player units in first available slot
        i = 0
        while i < len(self.all_units[PLAYER]):
            tile_int = player_drag_points[i].tile

            self.map.tiles[tile_int].hero_on = self.all_units[PLAYER][i]
            self.all_units[PLAYER][i].tile = self.map.tiles[tile_int]

            self.move_visuals_to_tile(PLAYER, i, tile_int)
            self.refresh_unit_visuals(PLAYER, i)

            self.current_units[PLAYER].append(self.all_units[PLAYER][i])

            # Prepare cohorts
            if self.game_mode in pair_up_modes and self.all_units[PLAYER][i].pair_up:
                build_pd_row = get_row_from_build_name(self.all_units[PLAYER][i].pair_up)
                cohort_obj = make_hero_from_pd_row(build_pd_row, PLAYER)
                self.all_cohorts.append(cohort_obj)

                # Pairing can reference each other directly
                self.all_units[PLAYER][i].pair_up_obj = cohort_obj
                cohort_obj.pair_up_obj = self.all_units[PLAYER][i]

            else:
                self.all_cohorts.append(None)

            i += 1

        # Place units in the space they are currently if Aether Raids, otherwise place in first available slot
        if self.game_mode != hero.GameMode.AetherRaids:
            i = 0
            while i < len(self.drag_point_units[ENEMY]):
                tile_int = enemy_drag_points[i].tile

                self.map.tiles[tile_int].hero_on = self.all_units[ENEMY][i]
                self.all_units[ENEMY][i].tile = self.map.tiles[tile_int]

                self.move_visuals_to_tile(ENEMY, i, tile_int)
                self.refresh_unit_visuals(ENEMY, i)

                self.current_units[ENEMY].append(self.all_units[ENEMY][i])

                i += 1
        else:
            i = 0
            for drag_point in self.unit_drag_points.values():
                if drag_point.hero and drag_point.side == ENEMY:
                    tile_int = drag_point.tile

                    self.map.tiles[tile_int].hero_on = self.all_units[ENEMY][i]
                    self.all_units[ENEMY][i].tile = self.map.tiles[tile_int]

                    self.move_visuals_to_tile(ENEMY, i, tile_int)
                    self.refresh_unit_visuals(ENEMY, i)

                    self.current_units[ENEMY].append(self.all_units[ENEMY][i])

                    i += 1

        # Apply stats present only within gameplay
        _apply_battle_stats(self.all_units[PLAYER], result_bonus_units_player, self.game_mode, season, self.ar_structs)
        _apply_battle_stats(self.all_units[ENEMY], result_bonus_units_enemy, self.game_mode, season, self.ar_structs)

        self.season = season[:]

        self.set_cohort_sprites()

        for unit in self.current_units[PLAYER]:
            self.units_to_move.append(unit)

        # Create all combat fields
        self.combat_fields = []
        self.combat_fields = feh.create_combat_fields(self.current_units[PLAYER], self.current_units[ENEMY])

        # Start enemy defeated count
        self.enemy_defeated_count = {}

        self.initial_mapstate = create_mapstate(self.map, self.units_to_move, self.turn_info[0], self.unit_reinf_points, self.enemy_defeated_count, self.first_duo_skill_used, self.indulgence_used)

        print("------------------- START OF NEW SIMULATION -------------------")
        print()
        print("---- PLAYER PHASE ----")

        # Start of turn skills
        current_player_units, current_enemy_units = self.map.get_heroes_present_by_side()

        # Just starting, no one defeated yet
        any_ally_defeated = False

        damage, heals, end_actions = feh.start_of_turn(current_player_units, current_enemy_units, 1, self.season, self.game_mode, self.map, any_ally_defeated, self.ar_struct_tiles)
        self.refresh_walls()

        for unit in self.current_units[PLAYER] + self.current_units[ENEMY]:

            # Update transformation sprites
            S = unit.side

            # Update with Beast Transformation
            self.update_unit_graphics(unit)

            # Distribute heals/damage
            heal_amount = 0
            damage_amount = 0

            if unit in heals and heals[unit] != -1 and Status.DeepWounds not in unit.statusNeg:
                heal_amount = heals[unit]

            if unit in damage and damage[unit] != -1 and Status.EnGarde not in unit.statusPos:
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

            unit.assistTargetedSelf_Rally = 0
            unit.assistTargetedSelf_Move = 0
            unit.assistTargetedSelf_Other = 0

            unit.assistTargetedOther_Rally = 0
            unit.assistTargetedOther_Move = 0
            unit.assistTargetedOther_Other = 0

        for unit in end_actions:
            self.units_to_move.remove(unit)
            self.update_unit_graphics(unit)

        if self.units_to_move:
            mapstate = create_mapstate(self.map, self.units_to_move, self.turn_info[0], self.unit_reinf_points, self.enemy_defeated_count, self.first_duo_skill_used, self.indulgence_used)
            self.map_states.append(mapstate)
        else:
            self.next_phase()

    def end_turn_button(self):
        if self.animation:
            return

        self.canto = None

        for tile in self.canto_tile_imgs:
            self.delete(tile)
        self.canto_tile_imgs.clear()

        self.next_phase()
        return

    def undo_action_button(self):
        if self.animation:
            return

        if len(self.map_states) > 1:
            if not self.canto:
                self.map_states.pop()
            self.apply_mapstate(self.map_states[-1])
        else:
            self.apply_mapstate(self.map_states[0])

        self.button_frame.action_button.config(state='disabled', text='Action\nButton')
        CreateToolTip(self.button_frame.action_button, text='')

        if len(self.map_states) == 1:
            self.button_frame.swap_spaces_button.config(state="normal")
            self.button_frame.undo_button.config(state="disabled")

    def toggle_swap(self):
        if self.animation: return

        self.swap_mode = not self.swap_mode

        if self.swap_mode:
            unit_needs_switch = []

            # Update Swap Button
            self.button_frame.swap_spaces_button.config(text="Swap\nDone", bg="green3")

            active_units = []
            for unit in self.all_units[PLAYER]:
                if unit.tile:
                    active_units.append(unit)
                else:
                    active_units.append(unit.pair_up_obj)

            for unit in active_units:
                if self.initial_mapstate.unit_states[unit].cur_position == -1:
                    unit_needs_switch.append(True)
                else:
                    unit_needs_switch.append(False)

            # Apply the initial mapstate
            self.apply_mapstate(self.initial_mapstate)

            applied_active_units = []
            for unit in self.all_units[PLAYER]:
                if unit.tile:
                    applied_active_units.append(unit)
                else:
                    applied_active_units.append(unit.pair_up_obj)

            i = 0
            while i < len(unit_needs_switch):
                if unit_needs_switch[i]:
                    self.switch_pairing(applied_active_units[i])
                i += 1

            final_active_units = []
            for unit in self.all_units[PLAYER]:
                if unit.tile:
                    final_active_units.append(unit)
                else:
                    final_active_units.append(unit.pair_up_obj)

            for unit in final_active_units:
                self.update_unit_graphics(unit)

            # Draw green spaces
            for tile in self.unit_drag_points.keys():
                if self.unit_drag_points[tile].side == PLAYER:
                    drawnTile = self.create_image(0, 0, image=self.move_tile_photos[4])
                    self.canto_tile_imgs.append(drawnTile)
                    self.move_to_tile(drawnTile, tile)

                    if self.map.tiles[tile].hero_on:
                        if self.map.tiles[tile].hero_on in self.all_units[PLAYER]:
                            index = self.all_units[PLAYER].index(self.map.tiles[tile].hero_on)
                            sprite = self.unit_sprites[PLAYER][index]
                        else:
                            index = self.all_cohorts.index(self.map.tiles[tile].hero_on)
                            sprite = self.cohort_sprites[index]

                        self.tag_lower(drawnTile, sprite)

        else:
            self.button_frame.swap_spaces_button.config(text="Swap\nSpaces", bg="#75f216")

            self.unit_status.clear()

            for tile in self.canto_tile_imgs:
                self.delete(tile)
            self.canto_tile_imgs.clear()

            self.initial_mapstate = create_mapstate(self.map, self.units_to_move, self.turn_info[0], self.unit_reinf_points, self.enemy_defeated_count, self.first_duo_skill_used, self.indulgence_used)

            print("---- PLAYER PHASE ----")

            current_player_units, current_enemy_units = self.map.get_heroes_present_by_side()

            # Just starting, no one defeated yet
            any_ally_defeated = False

            damage, heals, end_actions = feh.start_of_turn(current_player_units, current_enemy_units, 1, self.season, self.game_mode, self.map, any_ally_defeated, self.ar_struct_tiles)

            self.refresh_walls()
            self.refresh_divine_veins()

            for unit in current_player_units + current_enemy_units:
                # Update transformation sprites
                S = unit.side

                # Update with Beast Transformation
                self.update_unit_graphics(unit)

                heal_amount = 0
                damage_amount = 0
                if unit in heals and heals[unit] != -1 and Status.DeepWounds not in unit.statusNeg:
                    heal_amount = heals[unit]

                if unit in damage and damage[unit] != -1 and Status.EnGarde not in unit.statusPos:
                    damage_amount = damage[unit]

                if damage_amount >= heal_amount and (damage_amount > 0 or heal_amount > 0):
                    unit.HPcur = max(1, unit.HPcur + (heal_amount - damage_amount))
                    self.animate_damage_popup(abs(heal_amount - damage_amount), unit.tile.tileNum)
                elif damage_amount < heal_amount and (damage_amount > 0 or heal_amount > 0):
                    unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + (heal_amount - damage_amount))
                    self.animate_heal_popup(abs(heal_amount - damage_amount), unit.tile.tileNum)

                #self.set_hp_visual(unit, unit.HPcur)
                self.refresh_unit_visuals_obj(unit)

                unit.unitCombatInitiates = 0
                unit.assistTargetedOther = 0
                unit.assistTargetedSelf = 0

                unit.assistTargetedSelf_Rally = 0
                unit.assistTargetedSelf_Move = 0
                unit.assistTargetedSelf_Other = 0

                unit.assistTargetedOther_Rally = 0
                unit.assistTargetedOther_Move = 0
                unit.assistTargetedOther_Other = 0

                unit.canto_ready = True

            for unit in end_actions:
                self.units_to_move.remove(unit)
                self.update_unit_graphics(unit)

            if self.units_to_move:
                self.map_states.clear()
                self.map_states.append(create_mapstate(self.map, self.units_to_move, self.turn_info[0], self.unit_reinf_points, self.enemy_defeated_count, self.first_duo_skill_used, self.indulgence_used))
            else:
                self.next_phase()


        # Reset Action Button
        self.button_frame.action_button.config(state='disabled', text='Action\nButton')
        CreateToolTip(self.button_frame.action_button, text='')

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

        # Duo Skill usage
        self.first_duo_skill_used = mapstate.first_duo_user
        self.indulgence_used = mapstate.duos_ind_used

        # Update phase labels
        if self.turn_info[1] == PLAYER:
            self.button_frame.help_info.config(text="Turn " + str(self.turn_info[0]) + ": Player Phase", font=("Helvetica", 16), fg="DodgerBlue2")
        else:
            self.button_frame.help_info.config(text="Turn " + str(self.turn_info[0]) + ": Enemy Phase", font=("Helvetica", 16), fg="red")

        # Set units to move
        self.units_to_move.clear()
        for unit in mapstate.units_to_move:
            self.units_to_move.append(unit)

        for tile in self.map.tiles:
            if tile.hero_on:
                tile.hero_on.tile = None

            tile.hero_on = None

        # Move units to correct tile
        for unit in mapstate.unit_states.keys():
            unit.HPcur = mapstate.unit_states[unit].cur_hp

            # Revive fallen unit, placing back and retaining unit ordering
            if unit in self.all_units[unit.side]:
                obj_index = self.all_units[unit.side].index(unit)
                is_cohort = False
            else:
                obj_index = self.all_cohorts.index(unit)
                is_cohort = True

            found = False

            # If no other unit alive, can just add
            if unit.HPcur > 0 and len(self.current_units[unit.side]) == 0:
                if not is_cohort:
                    self.current_units[unit.side].append(unit)
                else:
                    self.current_units[unit.side].append(unit.pair_up_obj)

            # If other units are alive
            elif unit.HPcur > 0 and unit not in self.current_units[unit.side]:

                # Iterate over all current units (can only be non-cohort units)
                for i in range(len(self.current_units[unit.side])):
                    if self.all_units[unit.side].index(self.current_units[unit.side][i]) > obj_index:
                        if not is_cohort:
                            self.current_units[unit.side].insert(i, unit)
                        else:
                            self.current_units[unit.side].insert(i, unit.pair_up_obj)
                        found = True
                        break

                if not found:
                    self.current_units[unit.side].append(unit)

            unit.specialCount = mapstate.unit_states[unit].cur_sp

            unit.buffs = mapstate.unit_states[unit].cur_buffs[:]
            unit.debuffs = mapstate.unit_states[unit].cur_debuffs[:]
            unit.statusPos = mapstate.unit_states[unit].cur_status_pos[:]
            unit.statusNeg = mapstate.unit_states[unit].cur_status_neg[:]
            unit.statusOther = deepcopy(mapstate.unit_states[unit].cur_status_other)

            unit.special_galeforce_triggered = mapstate.unit_states[unit].sp_galeforce
            unit.nonspecial_galeforce_triggered = mapstate.unit_states[unit].nsp_galeforce
            unit.once_per_map_cond = mapstate.unit_states[unit].once_per_map_cond
            unit.canto_ready = mapstate.unit_states[unit].canto

            if unit.tile:
                unit.tile.hero_on = None

            unit.unitCombatInitiates = mapstate.unit_states[unit].num_combats
            unit.assistTargetedSelf = mapstate.unit_states[unit].num_assists_self
            unit.assistTargetedOther = mapstate.unit_states[unit].num_assists_other

            unit.assistTargetedSelf_Rally = mapstate.unit_states[unit].num_assists_self_rally
            unit.assistTargetedSelf_Move = mapstate.unit_states[unit].num_assists_self_move
            unit.assistTargetedSelf_Other = mapstate.unit_states[unit].num_assists_self_other

            unit.assistTargetedOther_Rally = mapstate.unit_states[unit].num_assists_other_rally
            unit.assistTargetedOther_Move = mapstate.unit_states[unit].num_assists_other_move
            unit.assistTargetedOther_Other = mapstate.unit_states[unit].num_assists_other_other

            unit.transformed = mapstate.unit_states[unit].transformed

            unit.duo_cooldown = mapstate.unit_states[unit].duo_cooldown

        for unit in mapstate.unit_states.keys():
            if unit.HPcur > 0 and mapstate.unit_states[unit].cur_position != -1:

                tile_num_to_move = mapstate.unit_states[unit].cur_position
                tile_Obj_to_move = self.map.tiles[tile_num_to_move]
                unit.tile = tile_Obj_to_move
                unit.tile.hero_on = unit

                self.update_unit_graphics(unit)

        for unit in self.all_units[PLAYER] + self.all_units[ENEMY]:
            if unit not in mapstate.unit_states.keys():
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

        for struct in mapstate.struct_states.keys():
            struct.health = mapstate.struct_states[struct]

        i = 0
        while i < len(mapstate.dv_states):
            self.map.tiles[i].divine_vein = mapstate.dv_states[i][0]
            self.map.tiles[i].divine_vein_side = mapstate.dv_states[i][1]
            self.map.tiles[i].divine_vein_turn = mapstate.dv_states[i][2]
            i += 1

        for spawn_tile in mapstate.reinf_points.keys():
            self.unit_reinf_points[spawn_tile].spawns_remaining = mapstate.reinf_points[spawn_tile]

        self.enemy_defeated_count = mapstate.defeated_count

        self.refresh_walls()
        self.refresh_divine_veins()

    def next_phase(self):

        # Reset Action Button
        self.after(1, partial(self.button_frame.action_button.config, state='disabled', text='Action\nButton'))
        CreateToolTip(self.button_frame.action_button, text='')

        # Disable Swap, Enable Undo
        self.button_frame.swap_spaces_button.config(state="disabled")
        self.button_frame.undo_button.config(state="normal")

        # Switch sides
        self.turn_info[1] = abs(self.turn_info[1] - 1)

        # Remove units left to move
        units_to_move_CACHE = self.units_to_move[:]

        while self.units_to_move:
            self.units_to_move.pop()

        current_player_units, current_enemy_units = self.map.get_heroes_present_by_side()

        # PLAYER PHASE
        if self.turn_info[1] == PLAYER:

            # First, spawn enemy reinforcements

            # Loop 1, points with kill/alive conditions are checked first
            n = 0
            for spawn_point in self.unit_reinf_points.values():

                reinf_unit = self.reinf_point_units[ENEMY][n]

                # Skip turn only conditions
                if spawn_point.target_name is None:
                    n += 1
                    continue

                spawn_condition = True

                # Kill condition check
                if spawn_point.target_amount != -1:
                    if spawn_point.target_name in self.enemy_defeated_count and self.enemy_defeated_count[spawn_point.target_name] < spawn_point.target_amount:
                        spawn_condition = False
                else:
                    enemy_heroes = self.map.get_heroes_present_by_side()[ENEMY]

                    # If any of the tracked unit is alive
                    if any(unit.intName == spawn_point.target_name for unit in enemy_heroes):
                        spawn_condition = False

                # Turn is too soon
                if self.turn_info[0] < spawn_point.turn - 1:
                    spawn_condition = False

                # No spawns remaining
                if spawn_point.spawns_remaining == 0:
                    spawn_condition = False

                # Find an available spawn position
                if spawn_condition:
                    spawn_tile = -1

                    if feh.can_be_on_tile(self.map.tiles[spawn_point.tile], reinf_unit.move) and self.map.tiles[spawn_point.tile].hero_on is None:
                        spawn_tile = spawn_point.tile

                    i = 1
                    while spawn_tile == -1 and i < 20:
                        cur_tiles = sorted([x.tileNum for x in self.map.tiles[spawn_point.tile].tilesNSpacesAway(i)], reverse=True)

                        j = 0
                        while spawn_tile == -1 and j < len(cur_tiles):
                            if feh.can_be_on_tile(self.map.tiles[cur_tiles[j]], reinf_unit.move) and self.map.tiles[cur_tiles[j]].hero_on is None:
                                spawn_tile = cur_tiles[j]
                            j += 1

                        i += 1

                    if spawn_tile != -1:
                        self.map.tiles[spawn_tile].hero_on = reinf_unit
                        reinf_unit.tile = self.map.tiles[spawn_tile]

                        self.current_units[ENEMY].append(reinf_unit)

                        reinf_unit.HPcur = reinf_unit.visible_stats[HP]
                        reinf_unit.specialCount = reinf_unit.specialMax
                        reinf_unit.buffs = [0, 0, 0, 0, 0]
                        reinf_unit.debuffs = [0, 0, 0, 0, 0]
                        reinf_unit.statusPos.clear()
                        reinf_unit.statusNeg.clear()
                        reinf_unit.statusOther = {}

                        self.update_unit_graphics(reinf_unit)

                        spawn_point.spawns_remaining -= 1

                n += 1

            # Loop 2, points with only turn conditions are checked second
            n = 0
            for spawn_point in self.unit_reinf_points.values():

                reinf_unit = self.reinf_point_units[ENEMY][n]

                # Skip kill/alive conditions
                if spawn_point.target_name is not None:
                    n += 1
                    continue

                spawn_condition = True

                if self.turn_info[0] < spawn_point.turn - 1:
                    spawn_condition = False

                if spawn_point.spawns_remaining == 0:
                    spawn_condition = False

                if spawn_condition:
                    spawn_tile = -1

                    if feh.can_be_on_tile(self.map.tiles[spawn_point.tile], reinf_unit.move) and self.map.tiles[spawn_point.tile].hero_on is None:
                        spawn_tile = spawn_point.tile

                    i = 1
                    while spawn_tile == -1 and i < 20:
                        cur_tiles = sorted([x.tileNum for x in self.map.tiles[spawn_point.tile].tilesNSpacesAway(i)], reverse=True)

                        j = 0
                        while spawn_tile == -1 and j < len(cur_tiles):
                            if feh.can_be_on_tile(self.map.tiles[cur_tiles[j]], reinf_unit.move) and self.map.tiles[cur_tiles[j]].hero_on is None:
                                spawn_tile = cur_tiles[j]
                            j += 1

                        i += 1

                    if spawn_tile != -1:
                        self.map.tiles[spawn_tile].hero_on = reinf_unit
                        reinf_unit.tile = self.map.tiles[spawn_tile]

                        self.current_units[ENEMY].append(reinf_unit)

                        reinf_unit.HPcur = reinf_unit.visible_stats[HP]
                        reinf_unit.specialCount = reinf_unit.specialMax

                        self.update_unit_graphics(reinf_unit)

                        spawn_point.spawns_remaining -= 1

                n += 1

            print("---- PLAYER PHASE ----")

            # EDIT BUTTON FRAME TEXT TO DISPLAY TURN NUMBER
            self.turn_info[0] += 1
            self.button_frame.help_info.config(text="Turn " + str(self.turn_info[0]) + ": Player Phase", font=("Helvetica", 16), fg="DodgerBlue2")

            # Get duo's indulgence


            # Clear buffs, refresh galeforce/canto
            for x in current_player_units:
                self.units_to_move.append(x)

                if Status.GrandStrategy in x.statusPos: x.debuffs = [0] * 5
                x.statusPos = []
                x.buffs = [0] * 5
                x.special_galeforce_triggered = False
                x.nonspecial_galeforce_triggered = False
                x.canto_ready = True

                struct_valid = self.get_struct_by_name("Duo's Indulgence") and self.get_struct_by_name("Duo's Indulgence").health != 0 and self.turn_info[0] <= self.get_struct_by_name("Duo's Indulgence").level + 3

                # Advance duo skill
                if (x.duo_cooldown > 0 and x.duo_skill.skill_refresh % self.turn_info[0] == 1) or (struct_valid and x == self.first_duo_skill_used and not self.indulgence_used):
                    x.duo_cooldown = 0

                    if x == self.first_duo_skill_used and not self.indulgence_used:
                        self.indulgence_used = True

                # Clear buffs, refresh galeforce/canto of cohort
                if x.pair_up_obj:
                    if Status.GrandStrategy in x.pair_up_obj.statusPos: x.pair_up_obj.debuffs = [0] * 5
                    x.pair_up_obj.statusPos = []
                    x.pair_up_obj.buffs = [0] * 5
                    x.pair_up_obj.special_galeforce_triggered = False
                    x.pair_up_obj.nonspecial_galeforce_triggered = False
                    x.pair_up_obj.canto_ready = True

            # Clear debuffs of any unit on opposing team yet to act
            for x in current_enemy_units:
                if x in units_to_move_CACHE:
                    x.statusNeg = []
                    if Status.GrandStrategy not in x.statusPos: x.debuffs = [0] * 5

            for tile in self.map.tiles:
                if tile.divine_vein != 0 and tile.divine_vein_side == PLAYER and tile.divine_vein_turn >= 1:
                    tile.divine_vein_turn -= 1

            any_ally_defeated = False
            for x in self.all_units[PLAYER]:
                if x.HPcur == 0:
                    any_ally_defeated = True

            damage, heals, end_actions = feh.start_of_turn(current_player_units, current_enemy_units, self.turn_info[0], self.season, self.game_mode, self.map, any_ally_defeated, self.ar_struct_tiles)

            #self.refresh_walls()
            self.refresh_divine_veins()

        # ENEMY PHASE
        else:
            print("---- ENEMY PHASE ----")

            self.button_frame.help_info.config(text="Turn " + str(self.turn_info[0]) + ": Enemy Phase", font=("Helvetica", 16), fg="red")

            # EDIT BUTTON FRAME TEXT TO DISPLAY TURN NUMBER

            for x in current_enemy_units:
                self.units_to_move.append(x)
                x.statusPos = []
                x.buffs = [0] * 5
                x.special_galeforce_triggered = False
                x.nonspecial_galeforce_triggered = False
                x.canto_ready = True

                if x.duo_cooldown > 0 and x.duo_skill.skill_refresh % self.turn_info[0] == 1:
                    x.duo_cooldown = 0

            # Clear debuffs of units yet to move, treat them as moved
            for x in current_player_units:
                if x in units_to_move_CACHE:
                    x.statusNeg = []
                    if Status.GrandStrategy not in x.statusPos: x.debuffs = [0] * 5

                    if x.pair_up_obj:
                        x.pair_up_obj.statusNeg = []
                        if Status.GrandStrategy not in x.pair_up_obj.statusPos: x.pair_up_obj.debuffs = [0] * 5

            for tile in self.map.tiles:
                if tile.divine_vein != 0 and tile.divine_vein_side == ENEMY and tile.divine_vein_turn >= 1:
                    tile.divine_vein_turn -= 1

            any_ally_defeated = any(self.enemy_defeated_count.values())
            for x in self.all_units[ENEMY]:
                if x.HPcur == 0:
                    any_ally_defeated = True

            damage, heals, end_actions = feh.start_of_turn(current_enemy_units, current_player_units, self.turn_info[0], self.season, self.game_mode, self.map, any_ally_defeated, self.ar_struct_tiles)

            #self.refresh_walls()
            self.refresh_divine_veins()

        for unit in current_player_units + current_enemy_units:
            # Update transformation sprites
            S = unit.side

            if unit in self.all_units[S]:
                unit_index = self.all_units[S].index(unit)

                unit_sprite = self.unit_sprites[S][unit_index]
                unit_sprite_gs = self.unit_sprites_gs[S][unit_index]
                unit_sprite_trans = self.unit_sprites_trans[S][unit_index]
                unit_sprite_gs_trans = self.unit_sprites_gs_trans[S][unit_index]

            else:
                unit_index = self.all_cohorts.index(unit)

                unit_sprite = self.cohort_sprites[unit_index]
                unit_sprite_gs = self.cohort_sprites_gs[unit_index]
                unit_sprite_trans = self.cohort_sprites_trans[unit_index]
                unit_sprite_gs_trans = self.cohort_sprites_gs_trans[unit_index]

            if unit.transformed:
                if unit in self.units_to_move or unit.side != self.turn_info[1]:
                    self.itemconfig(unit_sprite, state='hidden')
                    self.itemconfig(unit_sprite_gs, state='hidden')
                    self.itemconfig(unit_sprite_trans, state='normal')
                    self.itemconfig(unit_sprite_gs_trans, state='hidden')
                else:
                    self.itemconfig(unit_sprite, state='hidden')
                    self.itemconfig(unit_sprite_gs, state='hidden')
                    self.itemconfig(unit_sprite_trans, state='hidden')
                    self.itemconfig(unit_sprite_gs_trans, state='normal')
            else:
                if unit in self.units_to_move or unit.side != self.turn_info[1]:
                    self.itemconfig(unit_sprite, state='normal')
                    self.itemconfig(unit_sprite_gs, state='hidden')
                    self.itemconfig(unit_sprite_trans, state='hidden')
                    self.itemconfig(unit_sprite_gs_trans, state='hidden')
                else:
                    self.itemconfig(unit_sprite, state='hidden')
                    self.itemconfig(unit_sprite_gs, state='normal')
                    self.itemconfig(unit_sprite_trans, state='hidden')
                    self.itemconfig(unit_sprite_gs_trans, state='hidden')

            heal_amount = 0
            damage_amount = 0
            if unit in heals and heals[unit] != -1 and Status.DeepWounds not in unit.statusNeg:
                heal_amount = heals[unit]

            if unit in damage and damage[unit] != -1 and Status.EnGarde not in unit.statusPos:
                damage_amount = damage[unit]

            if damage_amount >= heal_amount and (damage_amount > 0 or heal_amount > 0):
                unit.HPcur = max(1, unit.HPcur + (heal_amount - damage_amount))
                self.animate_damage_popup(abs(heal_amount - damage_amount), unit.tile.tileNum)
            elif damage_amount < heal_amount and (damage_amount > 0 or heal_amount > 0):
                unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + (heal_amount - damage_amount))
                self.animate_heal_popup(abs(heal_amount - damage_amount), unit.tile.tileNum)

            # Visually update Special and HP bar/count
            self.refresh_unit_visuals_obj(unit)

            unit.unitCombatInitiates = 0
            unit.assistTargetedSelf = 0
            unit.assistTargetedOther = 0

            unit.assistTargetedSelf_Rally = 0
            unit.assistTargetedSelf_Move = 0
            unit.assistTargetedSelf_Other = 0

            if unit.pair_up_obj:
                unit.pair_up_obj.unitCombatInitiates = 0
                unit.pair_up_obj.assistTargetedSelf = 0
                unit.pair_up_obj.assistTargetedOther = 0

                unit.pair_up_obj.assistTargetedSelf_Rally = 0
                unit.pair_up_obj.assistTargetedSelf_Move = 0
                unit.pair_up_obj.assistTargetedSelf_Other = 0

        for unit in end_actions:
            self.units_to_move.remove(unit)
            self.update_unit_graphics(unit)

        if self.units_to_move:
            mapstate = create_mapstate(self.map, self.units_to_move, self.turn_info[0], self.unit_reinf_points, self.enemy_defeated_count, self.first_duo_skill_used, self.indulgence_used)
            self.map_states.append(mapstate)
        else:
            self.next_phase()

        return

    def create_rectangle_alpha(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs and 'fill' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.winfo_rgb(fill) + (alpha,)
            image = Image.new('RGBA', (x2 - x1, y2 - y1), fill)
            self.structure_grayout_img.append(ImageTk.PhotoImage(image))
            cur_photo = self.create_image(x1, y1, image=self.structure_grayout_img[-1], anchor='nw')
            return cur_photo
        #self.create_rectangle(x1, y1, x2, y2, **kwargs)

    def on_click(self, event):
        x_comp = event.x // self.TILE_SIZE
        y_comp = ((self.GAMEPLAY_WIDTH - event.y) // 90)
        tile = x_comp + 6 * y_comp

        if self.animation: return

        # Create menu to build unit on empty space
        if not self.running and not self.hero_listing.creation_menu:
            if tile in self.unit_drag_points and not self.unit_drag_points[tile].hero and not self.map.tiles[tile].structure_on:
                self.hero_listing.create_creation_popup()
                self.hero_listing.creation_make_button.config(command=partial(self.place_unit_object, event.x, event.y))

                self.hero_listing.creation_build_field.forget()
                self.hero_listing.creation_make_text.forget()

        # Generate unit status from drag point
        if not self.running and self.unit_status:
            if tile in self.unit_drag_points and self.unit_drag_points[tile].hero:
                self.unit_status.update_from_obj(self.unit_drag_points[tile].hero)

        # Move Units withing Drag Points
        if not self.running and tile in self.unit_drag_points and self.unit_drag_points[tile].hero:
            S = self.unit_drag_points[tile].side

            # Index of unit among drag points
            index = self.drag_point_units[S].index(self.unit_drag_points[tile].hero)

            self.drag_data = {
                            'cur_x': event.x,
                            'cur_y': event.y,
                            'start_tile': tile,
                            'prep_unit_id': self.unit_tags[S][index],
                            'side': S
                            }

            self.tag_raise(self.unit_sprites[S][index])
            self.tag_raise(self.unit_sprites_gs[S][index])
            self.tag_raise(self.unit_sprites_trans[S][index])
            self.tag_raise(self.unit_sprites_gs_trans[S][index])
            self.tag_raise(self.unit_weapon_icon_sprites[S][index])
            self.tag_raise(self.unit_hp_count_labels[S][index])
            self.tag_raise(self.unit_sp_count_labels[S][index])
            self.tag_raise(self.unit_hp_bars_bg[S][index])
            self.tag_raise(self.unit_hp_bars_fg[S][index])

            if self.game_mode == hero.GameMode.AetherRaids:
                for starting_tile in self.starting_tile_photos:
                    self.itemconfigure(starting_tile, state='hidden')

                valid_unit_moves = []

                for cur_tile in self.map.tiles:
                    x_move = 90 * (cur_tile.tileNum % 6)
                    y_move = 90 * (7 - (cur_tile.tileNum // 6))

                    # CASE 1: Moving Offense Side
                    if S == PLAYER:
                        if 5 < cur_tile.tileNum < 12:
                            swapable_img = self.create_image(x_move, y_move, anchor=tk.NW, image=self.move_tile_photos[5])
                            self.tag_lower(swapable_img, 6)
                            self.tile_sprites.append(swapable_img)
                            valid_unit_moves.append(cur_tile.tileNum)
                        else:
                            cur_dark_tile = self.create_rectangle_alpha(0, 0, 90, 90, fill='black', alpha=0.5, anchor=tk.CENTER)
                            self.tag_lower(cur_dark_tile, 6)
                            self.coords(cur_dark_tile, x_move, y_move)
                            self.tile_sprites.append(cur_dark_tile)

                    # CASE 2: Moving Defense Side
                    else:
                        if 35 < cur_tile.tileNum < 48:
                            swapable_img = self.create_image(x_move, y_move, anchor=tk.NW, image=self.move_tile_photos[5])
                            self.tag_lower(swapable_img, 6)
                            self.tile_sprites.append(swapable_img)
                            valid_unit_moves.append(cur_tile.tileNum)
                        else:
                            cur_dark_tile = self.create_rectangle_alpha(0, 0, 90, 90, fill='black', alpha=0.5, anchor=tk.CENTER)
                            self.tag_lower(cur_dark_tile, 6)
                            self.coords(cur_dark_tile, x_move, y_move)
                            self.tile_sprites.append(cur_dark_tile)
            else:
                valid_unit_moves = []

                for cur_tile in self.map.tiles:
                    if cur_tile.tileNum in self.unit_drag_points and self.unit_drag_points[cur_tile.tileNum].side == S:
                        valid_unit_moves.append(cur_tile.tileNum)

            self.drag_data['valid_moves'] = valid_unit_moves

        # Move Aether Raids structures
        if not self.running and self.map.tiles[tile].structure_on and self.map.tiles[tile].structure_on.struct_type != 0:

            for starting_tile in self.starting_tile_photos:
                self.itemconfigure(starting_tile, state='hidden')

            valid_struct_moves = []

            # CASE 1: Struct is within top 2 rows
            if tile >= 36:
                for cur_tile in self.map.tiles:
                    x_move = 90 * (cur_tile.tileNum % 6)
                    y_move = 90 * (7 - (cur_tile.tileNum // 6))

                    if cur_tile.terrain != 0 or (cur_tile.structure_on and cur_tile.structure_on.struct_type == 0):
                        cur_dark_tile = self.create_rectangle_alpha(0, 0, 90, 90, fill='black', alpha=0.5, anchor=tk.CENTER)
                        self.tag_lower(cur_dark_tile, 6)
                        self.coords(cur_dark_tile, x_move, y_move)
                        self.tile_sprites.append(cur_dark_tile)
                    elif cur_tile.tileNum > 11:
                        swapable_img = self.create_image(x_move, y_move, anchor=tk.NW, image=self.move_tile_photos[5])
                        self.tag_lower(swapable_img, 6)
                        self.tile_sprites.append(swapable_img)
                        valid_struct_moves.append(cur_tile.tileNum)
                    else:
                        cur_dark_tile = self.create_rectangle_alpha(0, 0, 90, 90, fill='black', alpha=0.5, anchor=tk.CENTER)
                        self.tag_lower(cur_dark_tile, 6)
                        self.coords(cur_dark_tile, x_move, y_move)
                        self.tile_sprites.append(cur_dark_tile)

            # CASE 2: Struct is within lower 4 rows
            elif 11 < tile < 36:
                for cur_tile in self.map.tiles:
                    x_move = 90 * (cur_tile.tileNum % 6)
                    y_move = 90 * (7 - (cur_tile.tileNum // 6))

                    if cur_tile.terrain != 0 or (cur_tile.tileNum > 35 and self.unit_drag_points[cur_tile.tileNum].hero) or (cur_tile.structure_on and cur_tile.structure_on.struct_type == 0) or cur_tile.is_def_terrain:
                        cur_dark_tile = self.create_rectangle_alpha(0, 0, 90, 90, fill='black', alpha=0.5, anchor=tk.CENTER)
                        self.tag_lower(cur_dark_tile, 6)
                        self.coords(cur_dark_tile, x_move, y_move)
                        self.tile_sprites.append(cur_dark_tile)
                    elif 11 < cur_tile.tileNum < 36 or cur_tile.tileNum >= 36 and not self.unit_drag_points[cur_tile.tileNum].hero:
                        swapable_img = self.create_image(x_move, y_move, anchor=tk.NW, image=self.move_tile_photos[5])
                        self.tag_lower(swapable_img, 6)
                        self.tile_sprites.append(swapable_img)
                        valid_struct_moves.append(cur_tile.tileNum)
                    else:
                        cur_dark_tile = self.create_rectangle_alpha(0, 0, 90, 90, fill='black', alpha=0.5, anchor=tk.CENTER)
                        self.tag_lower(cur_dark_tile, 6)
                        self.coords(cur_dark_tile, x_move, y_move)
                        self.tile_sprites.append(cur_dark_tile)

            # CASE 3: Struct is on buttom row (offense structures)
            elif tile < 6:
                for cur_tile in self.map.tiles:
                    x_move = 90 * (cur_tile.tileNum % 6)
                    y_move = 90 * (7 - (cur_tile.tileNum // 6))

                    if cur_tile.tileNum < 6:
                        swapable_img = self.create_image(x_move, y_move, anchor=tk.NW, image=self.move_tile_photos[5])
                        self.tag_lower(swapable_img, 6)
                        self.tile_sprites.append(swapable_img)
                        valid_struct_moves.append(cur_tile.tileNum)
                    else:
                        cur_dark_tile = self.create_rectangle_alpha(0, 0, 90, 90, fill='black', alpha=0.5, anchor=tk.CENTER)
                        self.tag_lower(cur_dark_tile, 6)
                        self.coords(cur_dark_tile, x_move, y_move)
                        self.tile_sprites.append(cur_dark_tile)

            self.drag_data = {
                              'cur_x': event.x,
                              'cur_y': event.y,
                              'start_tile': tile,
                              'struct_id': self.ar_structs.index(self.map.tiles[tile].structure_on),
                              'valid_moves': valid_struct_moves
                              }

            self.tag_raise(self.ar_struct_sprites[self.drag_data['struct_id']])

        cur_struct = self.map.tiles[tile].structure_on

        if cur_struct:
            self.unit_status.update_from_struct(cur_struct)

        # Nothing else if not running
        if not self.running:
            return

        cur_hero = self.map.tiles[tile].hero_on

        if not cur_hero:
            return

        S = cur_hero.side

        if cur_hero in self.all_units[S]:
            item_index = self.all_units[S].index(cur_hero)
            is_cohort = False
        else:
            item_index = self.all_cohorts.index(cur_hero)
            is_cohort = True

        # Unit Status frame set to current hero
        self.unit_status.update_from_obj(cur_hero)

        # If this movement is as a canto move and currently selecting the canto-enabled unit
        is_canto_move = self.canto == cur_hero

        # Enable Duo Skill Button
        if S == PLAYER and cur_hero.duo_skill and not self.all_cohorts[item_index]:
            if cur_hero.duo_skill.type == 'duo':
                self.button_frame.action_button.config(text='Duo\nSkill')
            else:
                self.button_frame.action_button.config(text='Harmonic\nSkill')

            # Move lower
            CreateToolTip(self.button_frame.action_button, cur_hero.duo_skill.desc)

            duos_hindr_present = self.get_struct_by_name("Duo's Hindrance") and self.get_struct_by_name("Duo's Hindrance").level + 2 >= self.turn_info[0] and self.get_struct_by_name("Duo's Hindrance").health != 0
            duo_on_foe_team = any(foe for foe in self.current_units[ENEMY] if foe.duo_skill and foe.HPcur != 0)

            if self.turn_info[1] == PLAYER and cur_hero.duo_cooldown == 0 and feh.can_use_duo_skill(cur_hero, self.units_to_move) and not self.swap_mode and not is_canto_move and not(duos_hindr_present and duo_on_foe_team):
                self.button_frame.action_button.config(state='normal', command=partial(self.use_duo_skill, cur_hero))
            else:
                self.button_frame.action_button.config(state='disabled')

        # Enable Pair Up Button
        elif S == PLAYER and self.all_cohorts[item_index]:
            self.button_frame.action_button.config(text='Swap\nCohort')
            if self.turn_info[1] == PLAYER and feh.can_be_on_tile(cur_hero.tile, self.all_cohorts[item_index].move) and not self.swap_mode and not is_canto_move:
                self.button_frame.action_button.config(state='normal', command=partial(self.switch_pairing, cur_hero))
            else:
                self.button_frame.action_button.config(state='disabled')
        else:
            self.button_frame.action_button.config(state='disabled', text='Action\nButton')
            CreateToolTip(self.button_frame.action_button, text='')

        # Not this side's phase, no movement allowed
        if cur_hero.side != self.turn_info[1]:
            return

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
                          'cohort': is_cohort,

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

        current_units = self.map.get_heroes_present_by_side()

        unit_team = current_units[S]
        other_team = current_units[S - 1]

        if is_canto_move:
            sdd['moves'], sdd['paths'], moves_obj_array = feh.get_canto_moves(cur_hero, unit_team, other_team, self.distance, self.spaces_allowed, self.chosen_action, self.turn_info[0], self.starting_tile, self.has_unit_warped)

        else:
            sdd['moves'], sdd['paths'], moves_obj_array = feh.get_regular_moves(cur_hero, unit_team, other_team)
            self.spaces_allowed = feh.allowed_movement(cur_hero)

        sdd['moves_obj_array'] = moves_obj_array

        self.tile_sprites = []

        TILE_BLUE = 0
        TILE_PALE_BLUE = 1
        TILE_RED = 2
        TILE_PALE_RED = 3
        TILE_GREEN = 4
        TILE_PALE_GREEN = 5

        # Create blue tiles for each possible movements
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
                if self.map.tiles[n].structure_on.struct_type != S + 1 and self.map.tiles[n].structure_on.health > 0 and "Trap" not in self.map.tiles[n].structure_on.name:
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
                        if self.map.tiles[n].structure_on.health > 0 and self.map.tiles[n].structure_on.struct_type != S + 1 and "Trap" not in self.map.tiles[n].structure_on.name:

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

                                # Then, check if smite is possible
                                if final_dest != -1:
                                    unit_on_dest = self.map.tiles[final_dest].hero_on is not None and self.map.tiles[final_dest].hero_on != cur_hero
                                    can_traverse_dest = feh.can_be_on_tile(self.map.tiles[final_dest], ally.move)

                                    foe_on_skip = self.map.tiles[skip_over].hero_on is not None and self.map.tiles[skip_over].hero_on.side != cur_hero.side
                                    struct_on_skip = self.map.tiles[skip_over].structure_on and "Trap" not in self.map.tiles[skip_over].structure_on.name and self.map.tiles[skip_over].structure_on.health != 0

                                    can_skip = self.map.tiles[skip_over].terrain != 4 and not foe_on_skip and not struct_on_skip

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
                            self_exceptions = ["annetteRally", "annetteBoost", "hubertRuse", "shigureLink", "merlinusRally", "astridRally"]
                            ally_exceptions = ["hubertRuse", "shigureLink"]

                            for skill in feint_skills + ruse_skills:
                                if skill in cur_hero.getSkills() or skill in ally.getSkills():
                                    valid_ally_cond = True

                            # Other skills that enable Rally attacks (Damiel Bow, Convoy Dagger,
                            for skill in self_exceptions:
                                if skill in cur_hero.getSkills():
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

                                valid_unit_cond = (player_HP_result > cur_hero.HPcur or ally_HP_result > ally.HPcur) and Status.DeepWounds not in cur_hero.statusNeg
                                valid_ally_cond = Status.DeepWounds not in ally.statusNeg

                            elif "ardent_sac" in cur_hero.assist.effects:
                                valid_unit_cond = cur_hero.HPcur > 10
                                valid_ally_cond = ally.HPcur != ally.visible_stats[HP]

                            elif "sacrifice" in cur_hero.assist.effects:
                                valid_unit_cond = cur_hero.HPcur > 1 or sum(ally.debuffs) < 0
                                valid_ally_cond = sum(ally.debuffs) < 0 or  ally.HPcur != ally.visible_stats[HP] and Status.DeepWounds not in ally.statusNeg

                            elif "maidenSolace" in cur_hero.assist.effects:
                                valid_unit_cond = cur_hero.HPcur > 1 or sum(ally.debuffs) < 0 or ally.statusNeg
                                valid_ally_cond = (ally.HPcur != ally.visible_stats[HP] and Status.DeepWounds not in ally.statusNeg) or sum(ally.debuffs) < 0 or ally.statusNeg

                            elif "harsh_comm" in cur_hero.assist.effects:
                                valid_unit_cond = True
                                valid_ally_cond = sum(ally.debuffs) < 0
                            elif "harsh_comm_plus" in cur_hero.assist.effects:
                                valid_unit_cond = True
                                valid_ally_cond = sum(ally.debuffs) < 0 or ally.statusNeg
                        else:
                            # big guy is a cheater
                            print("wonderhoy")

                        # Isolation
                        if Status.Isolation in cur_hero.statusNeg or Status.Isolation in ally.statusNeg:
                            valid_unit_cond = False

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

            if S == ENEMY:
                if self.cohort_sprites[i]: self.tag_raise(self.cohort_sprites[i])
                if self.cohort_sprites_gs[i]: self.tag_raise(self.cohort_sprites_gs[i])
                if self.cohort_sprites_trans[i]: self.tag_raise(self.cohort_sprites_trans[i])
                if self.cohort_sprites_gs_trans[i]: self.tag_raise(self.cohort_sprites_gs_trans[i])
                if self.cohort_weapon_icon_sprites[i]: self.tag_raise(self.cohort_weapon_icon_sprites[i])

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

            if S == PLAYER:
                if self.cohort_sprites[i]: self.tag_raise(self.cohort_sprites[i])
                if self.cohort_sprites_gs[i]: self.tag_raise(self.cohort_sprites_gs[i])
                if self.cohort_sprites_trans[i]: self.tag_raise(self.cohort_sprites_trans[i])
                if self.cohort_sprites_gs_trans[i]: self.tag_raise(self.cohort_sprites_gs_trans[i])
                if self.cohort_weapon_icon_sprites[i]: self.tag_raise(self.cohort_weapon_icon_sprites[i])

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

        if is_cohort:
            self.tag_raise(self.cohort_sprites[item_index])
            self.tag_raise(self.cohort_sprites_gs[item_index])
            self.tag_raise(self.cohort_sprites_trans[item_index])
            self.tag_raise(self.cohort_sprites_gs_trans[item_index])
            self.tag_raise(self.cohort_weapon_icon_sprites[item_index])

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

            self.drag_data['arrow_path'] = [first_path]

        if self.tile_sprites:
            for ar_sprite in self.ar_struct_sprites:
                self.tag_lower(ar_sprite, min(self.tile_sprites[0], min(self.divine_vein_sprites, default=self.tile_sprites[0] + 1)))

        self.refresh_divine_veins()

            #self.tag_raise(self.tile_sprites[0], ar_sprite)

        return

    def on_drag(self, event):
        if self.animation or not self.drag_data: return

        # AR Structures
        if not self.running and 'struct_id' in self.drag_data:
            delta_x = event.x - self.drag_data['cur_x']
            delta_y = event.y - self.drag_data['cur_y']

            self.move(self.ar_struct_sprites[self.drag_data['struct_id']], delta_x, delta_y)

            self.drag_data['cur_x'] = event.x
            self.drag_data['cur_y'] = event.y

            return

        if not self.running and 'prep_unit_id' in self.drag_data:
            delta_x = event.x - self.drag_data['cur_x']
            delta_y = event.y - self.drag_data['cur_y']

            self.move(self.drag_data['prep_unit_id'], delta_x, delta_y)

            self.drag_data['cur_x'] = event.x
            self.drag_data['cur_y'] = event.y

            return

        delta_x = event.x - self.drag_data['cur_x']
        delta_y = event.y - self.drag_data['cur_y']

        item_index = self.drag_data['index']
        S = self.drag_data['side']
        is_cohort = self.drag_data['cohort']

        if not is_cohort:
            cur_hero = self.all_units[S][item_index]
        else:
            cur_hero = self.all_cohorts[item_index]

        tag: str = self.unit_tags[S][item_index]

        self.move(tag, delta_x, delta_y)

        self.drag_data['cur_x'] = event.x
        self.drag_data['cur_y'] = event.y

        # tile from previous movement
        prev_tile_int = self.drag_data['cur_tile']

        x_comp = event.x // self.TILE_SIZE
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
                    if targeting_range == 1 and "nearSavior" in ally.getSkills() and (ally.getSkills()["nearSavior"] == 2 or ally in feh.allies_within_n(cur_tile_Obj.hero_on, 1)) and hero.Status.Undefended not in cur_tile_Obj.hero_on.statusNeg:
                        if savior_unit is None:
                            savior_unit = ally
                        else:
                            savior_unit = None
                            break

                    elif targeting_range == 2 and "farSavior" in ally.getSkills() and (ally.getSkills()["farSavior"] == 2 or ally in feh.allies_within_n(cur_tile_Obj.hero_on, 1)) and hero.Status.Undefended not in cur_tile_Obj.hero_on.statusNeg:
                        if savior_unit is None:
                            savior_unit = ally
                        else:
                            savior_unit = None
                            break

                if savior_unit is None:

                    self.extras.set_forecast_banner_foe(cur_hero, cur_tile_Obj.hero_on, distance, False, self.turn_info[0], self.combat_fields, self.ar_structs, self.units_to_move)
                    self.unit_status.update_from_obj(cur_tile_Obj.hero_on)
                else:
                    prev_savior_tile_Obj = savior_unit.tile

                    savior_unit.tile = cur_tile_Obj

                    self.extras.set_forecast_banner_foe(cur_hero, savior_unit, distance, True, self.turn_info[0], self.combat_fields, self.ar_structs, self.units_to_move)
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
        elif (cur_tile_Obj.structure_on and cur_tile_Obj.structure_on.health > 0 and cur_tile_Obj.structure_on.struct_type != S + 1
              and cur_tile_int in self.drag_data['attack_range'] and "Trap" not in cur_tile_Obj.structure_on.name):

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
            is_warp_move = False
            for move in sdd['moves_obj_array']:
                if move.destination == cur_tile_int and move.is_warp:
                    is_warp_move = True
                    break

            # Build from existing path

            if is_warp_move:
                sdd['cur_path'] = 'WARP'

            else:
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
        # Delete all colored movement tiles
        for tile in self.tile_sprites:
            self.delete(tile)
        self.tile_sprites.clear()

        sdd = self.drag_data

        if not self.running and sdd and 'prep_unit_id' in sdd:
            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90)
            destination_tile = x_comp + y_comp * 6
            start_tile = sdd['start_tile']

            if destination_tile in sdd['valid_moves'] and start_tile != destination_tile and 539 > event.x > 0 and 720 > event.y > 0:
                # CASE 1: destination_tile has nothing on it
                if not self.unit_drag_points[destination_tile].hero and not self.map.tiles[destination_tile].structure_on:
                    self.unit_drag_points[destination_tile].hero = self.unit_drag_points[start_tile].hero
                    self.unit_drag_points[start_tile].hero = None
                elif self.unit_drag_points[destination_tile].hero:
                    cur = self.unit_drag_points[start_tile].hero

                    self.unit_drag_points[start_tile].hero = self.unit_drag_points[destination_tile].hero
                    self.unit_drag_points[destination_tile].hero = cur
                else:
                    self.unit_drag_points[destination_tile].hero = self.unit_drag_points[start_tile].hero
                    self.unit_drag_points[start_tile].hero = None

                    self.map.tiles[start_tile].structure_on = self.map.tiles[destination_tile].structure_on
                    self.map.tiles[destination_tile].structure_on = None

            self.refresh_units_prep()
            self.refresh_walls()

            for tile in self.starting_tile_photos:
                index = self.starting_tile_photos.index(tile)
                cur_drag = list(self.unit_drag_points.keys())[index]

                if not self.map.tiles[cur_drag].structure_on:
                    self.itemconfigure(tile, state='normal')

            self.drag_data = None

        if not self.running and sdd and 'struct_id' in sdd:
            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90)
            destination_tile = x_comp + y_comp * 6
            start_tile = sdd['start_tile']

            if destination_tile in sdd['valid_moves'] and start_tile != destination_tile and 539 > event.x > 0 and 720 > event.y > 0:
                # CASE 1: destination_tile has nothing on it
                if (destination_tile not in self.unit_drag_points or not self.unit_drag_points[destination_tile].hero) and not self.map.tiles[destination_tile].structure_on:

                    self.map.tiles[destination_tile].structure_on = self.map.tiles[start_tile].structure_on
                    self.map.tiles[start_tile].structure_on = None

                # CASE 2: destination_tile has structure on it
                elif self.map.tiles[destination_tile].structure_on:
                    temp = self.map.tiles[start_tile].structure_on

                    self.map.tiles[start_tile].structure_on = self.map.tiles[destination_tile].structure_on
                    self.map.tiles[destination_tile].structure_on = temp
                # CASE 3: destination_tile has hero on it
                elif destination_tile in self.unit_drag_points and self.unit_drag_points[destination_tile].hero:
                    self.unit_drag_points[start_tile].hero = self.unit_drag_points[destination_tile].hero
                    self.unit_drag_points[destination_tile].hero = None

                    self.map.tiles[destination_tile].structure_on = self.map.tiles[start_tile].structure_on
                    self.map.tiles[start_tile].structure_on = None

                    self.refresh_units_prep()

            self.refresh_walls()

            for tile in self.starting_tile_photos:
                index = self.starting_tile_photos.index(tile)
                cur_drag = list(self.unit_drag_points.keys())[index]

                if not self.map.tiles[cur_drag].structure_on:
                    self.itemconfigure(tile, state='normal')

            self.drag_data = None

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
        is_cohort = sdd['cohort']

        if not is_cohort:
            cur_unit = self.all_units[S][item_index]
        else:
            cur_unit = self.all_cohorts[item_index]

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

        cur_unit.tile.hero_on = None
        cur_unit.tile = self.map.tiles[final_destination]
        self.map.tiles[final_destination].hero_on = cur_unit

        # Move all of this unit's graphics to the final tile
        self.move_visuals_to_tile_obj(cur_unit, final_destination)

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

                self.move_visuals_to_tile_obj(cur_unit, unit_final_position)
                self.move_visuals_to_tile_obj(ally, ally_final_position)

            else:
                unit_final_position = release_tile

                cur_unit.tile.hero_on = None

                cur_unit.tile = self.map.tiles[unit_final_position]

                self.map.tiles[unit_final_position].hero_on = cur_unit

                self.move_visuals_to_tile_obj(cur_unit, unit_final_position)

            self.drag_data = None

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

            if unit in self.all_units[U_side]:
                unit_index = self.all_units[U_side].index(unit)
                is_cohort = False
            else:
                unit_index = self.all_cohorts.index(unit)
                is_cohort = True

            if not is_cohort:
                self.itemconfig(self.unit_sprites[U_side][unit_index], state='hidden')
                self.itemconfig(self.unit_sprites_gs[U_side][unit_index], state='hidden')
                self.itemconfig(self.unit_sprites_trans[U_side][unit_index], state='hidden')
                self.itemconfig(self.unit_sprites_gs_trans[U_side][unit_index], state='hidden')
                self.itemconfig(self.unit_weapon_icon_sprites[U_side][unit_index], state='hidden')
            else:
                self.itemconfig(self.cohort_sprites[unit_index], state='hidden')
                self.itemconfig(self.cohort_sprites_gs[unit_index], state='hidden')
                self.itemconfig(self.cohort_sprites_trans[unit_index], state='hidden')
                self.itemconfig(self.cohort_sprites_gs_trans[unit_index], state='hidden')
                self.itemconfig(self.cohort_weapon_icon_sprites[unit_index], state='hidden')

            self.itemconfig(self.unit_sp_count_labels[U_side][unit_index], state='hidden')
            self.itemconfig(self.unit_hp_count_labels[U_side][unit_index], state='hidden')
            self.itemconfig(self.unit_hp_bars_bg[U_side][unit_index], state='hidden')
            self.itemconfig(self.unit_hp_bars_fg[U_side][unit_index], state='hidden')

        def set_unit_show(unit):
            U_side = unit.side
            unit_index = self.all_units[U_side].index(unit)

            if unit.transformed:
                self.itemconfig(self.unit_sprites_trans[U_side][unit_index], state='normal')
                self.itemconfig(self.unit_sprites[U_side][unit_index], state='hidden')
            else:
                self.itemconfig(self.unit_sprites_trans[U_side][unit_index], state='hidden')
                self.itemconfig(self.unit_sprites[U_side][unit_index], state='normal')

            self.itemconfig(self.unit_weapon_icon_sprites[U_side][unit_index], state='normal')
            self.itemconfig(self.unit_sp_count_labels[U_side][unit_index], state='normal')
            self.itemconfig(self.unit_hp_count_labels[U_side][unit_index], state='normal')
            self.itemconfig(self.unit_hp_bars_bg[U_side][unit_index], state='normal')
            self.itemconfig(self.unit_hp_bars_fg[U_side][unit_index], state='normal')

        # Sets a unit grayscale once their action is done
        def set_unit_actability(unit):
            U_side = unit.side
            unit_is_cohort = unit in self.all_cohorts

            if not unit_is_cohort:
                unit_index = self.all_units[U_side].index(unit)
            else:
                unit_index = self.all_cohorts.index(unit)

            if not unit_is_cohort:
                if unit.transformed:
                    self.itemconfig(self.unit_sprites_trans[U_side][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_gs_trans[U_side][unit_index], state='normal')
                else:
                    self.itemconfig(self.unit_sprites[U_side][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_gs[U_side][unit_index], state='normal')
            else:
                if unit.transformed:
                    self.itemconfig(self.cohort_sprites_trans[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_gs_trans[unit_index], state='normal')
                else:
                    self.itemconfig(self.cohort_sprites[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_gs[unit_index], state='normal')

        is_targeting_object = sdd['target_path'] != "NONE"
        is_targeting_hero = release_unit is not None
        is_targeting_struct = release_struct is not None

        # Get number of spaces between start and end position
        # Based on shortest possible line between points A and B, ignoring actual shape of path drawn
        distance = abs(destination_tile % 6 - sdd["start_x_comp"]) + abs(destination_tile // 6 - sdd["start_y_comp"])
        self.distance = distance
        self.starting_tile = self.map.tiles[sdd['start_x_comp'] + (6 * sdd["start_y_comp"])]

        # Galeforce
        galeforce_triggered = False

        # Trap triggered
        trap_triggered = False
        hex_trap_triggered_after_action = False

        final_dest_struct = self.map.tiles[final_destination].structure_on
        if final_dest_struct and "Trap" in final_dest_struct.name and destination_unit.side == PLAYER and final_dest_struct.health != 0:
            final_dest_struct.health = 0
            self.refresh_walls()

            if "False" not in final_dest_struct.name:
                if final_dest_struct.name == "Bolt Trap":
                    disarm_lvl = destination_unit.get("disarmTrap", 0)

                    if final_dest_struct.level > disarm_lvl:
                        trap_triggered = True

                        for unit in self.map.tiles[final_destination].unitsWithinNSpaces(3):
                            trap_damage = final_dest_struct.level * 10

                            if Status.EnGarde in unit.statusPos:
                                trap_damage = 0

                            unit.HPcur = max(1, unit.HPcur - trap_damage)
                            self.animate_damage_popup(trap_damage, unit.tile.tileNum)

                            self.set_hp_visual(unit, unit.HPcur)

                elif final_dest_struct.name == "Heavy Trap":
                    disarm_lvl = destination_unit.get("disarmTrap", 0)

                    if final_dest_struct.level > disarm_lvl:
                        trap_triggered = True

                        for unit in self.map.tiles[final_destination].unitsWithinNSpaces(2):
                            if unit.HPcur <= get_tower_hp_threshold(final_dest_struct.level):
                                unit.inflictStatus(Status.Gravity)

                elif final_dest_struct.name == "Hex Trap" and destination_unit.HPcur <= get_tower_hp_threshold(final_dest_struct.level):
                    trap_triggered = True

        # ATTAAAAAAAAAAAAAAAAAAAAAAACK!!!!!!!!!!!!!!!!!!
        if is_targeting_object and is_targeting_hero and destination_unit.isEnemyOf(release_unit) and not trap_triggered:

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
            if cur_unit in self.all_units[S]:
                player_index = self.all_units[S].index(cur_unit)

                player_sprite = self.unit_sprites[S][item_index] if not player.transformed else self.unit_sprites_trans[S][item_index]
            else:
                player_index = self.all_cohorts.index(cur_unit)

                player_sprite = self.cohort_sprites[item_index] if not player.transformed else self.cohort_sprites_trans[item_index]



            player_weapon_icon = self.unit_weapon_icon_sprites[S][item_index]
            player_hp_label = self.unit_hp_count_labels[S][item_index]
            player_sp_label = self.unit_sp_count_labels[S][item_index]
            player_hp_bar_fg = self.unit_hp_bars_fg[S][item_index]
            player_hp_bar_bg = self.unit_hp_bars_bg[S][item_index]

            # enemy sprites to be used for combat
            E_side = enemy.side

            if initiated_enemy in self.all_units[E_side]:
                enemy_index = self.all_units[E_side].index(initiated_enemy)

                enemy_sprite = self.unit_sprites[E_side][enemy_index] if not initiated_enemy.transformed else self.unit_sprites_trans[E_side][enemy_index]
                enemy_weapon_icon = self.unit_weapon_icon_sprites[E_side][enemy_index]
            else:
                enemy_index = self.all_cohorts.index(initiated_enemy)

                enemy_sprite = self.cohort_sprites[enemy_index] if not initiated_enemy.transformed else self.cohort_sprites_trans[enemy_index]
                enemy_weapon_icon = self.cohort_weapon_icon_sprites[enemy_index]

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

                combat_result = simulate_combat(player,
                                                savior_unit,
                                                True,
                                                self.turn_info[0],
                                                distance,
                                                self.combat_fields,
                                                aoe_present,
                                                self.units_to_move,
                                                savior_triggered=True,
                                                ar_structs=self.ar_structs)

                savior_unit.tile = prev_savior_tile_Obj

                # Hide unit being covered by Savior
                self.after(aoe_present + 100, set_unit_death, enemy)

                self.after(aoe_present + 100, self.move_to_tile, enemy_sprite, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile_wp,enemy_weapon_icon, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile_hp, enemy_hp_label, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile_sp, enemy_sp_label, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile_bar, enemy_hp_bar_fg, enemy_tile)
                self.after(aoe_present + 100, self.move_to_tile_bar,enemy_hp_bar_bg, enemy_tile)

            else:
                combat_result = simulate_combat(player,
                                                enemy,
                                                True,
                                                self.turn_info[0],
                                                distance,
                                                self.combat_fields,
                                                aoe_present,
                                                self.units_to_move,
                                                savior_triggered=False,
                                                ar_structs=self.ar_structs)

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
                    self.after(300 + aoe_present, self.set_hp_visual, initiated_enemy, initiated_enemy.HPcur)
                    self.after(300 + aoe_present, self.animate_damage_popup, burn_damages[PLAYER], enemy_tile)

                if burn_damages[ENEMY] > 0:
                    player.HPcur = max(1, player.HPcur - burn_damages[ENEMY])
                    self.after(300 + aoe_present, self.set_hp_visual, player, player.HPcur)
                    self.after(300 + aoe_present, self.animate_damage_popup, burn_damages[ENEMY], player_tile)

            # Perform BOL heals
            precombat_heals = combat_result[15]

            heals_present = 0

            if precombat_heals[PLAYER] > 0 or precombat_heals[ENEMY] > 0:
                heals_present = 400

                # Set precombat heals
                if precombat_heals[PLAYER] > 0:
                    player.HPcur = min(player.visible_stats[HP], player.HPcur + precombat_heals[PLAYER])
                    self.after(300 + aoe_present + burn_present, self.set_hp_visual, player, player.HPcur)
                    self.after(300 + aoe_present + burn_present, self.animate_heal_popup, precombat_heals[PLAYER], player_tile)

                if precombat_heals[ENEMY] > 0:
                    initiated_enemy.HPcur = min(initiated_enemy.visible_stats[HP], initiated_enemy.HPcur + precombat_heals[ENEMY])
                    self.after(300 + aoe_present + burn_present, self.set_hp_visual, initiated_enemy, initiated_enemy.HPcur)
                    self.after(300 + aoe_present + burn_present, self.animate_heal_popup, precombat_heals[ENEMY], enemy_tile)

            # Visualization of the blows trading
            i = 0

            # Iterate over the attacks
            while i < len(attacks):
                move_time = i * 500 + 200 + aoe_present + burn_present + heals_present + savior_present# when move starts per hit
                impact_time = i * 500 + 300 + aoe_present + burn_present + heals_present + savior_present # when damage numbers show per hit

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
            finish_time = 500 * (i + 1) + 200 + aoe_present + burn_present + heals_present + 2 * savior_present

            # Move savior unit back
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
            if Status.GrandStrategy not in player.statusPos: player.debuffs = [0, 0, 0, 0, 0]

            if player.pair_up_obj:
                player.pair_up_obj.statusNeg = []
                if Status.GrandStrategy not in x.pair_up_obj.statusPos: player.pair_up_obj.debuffs = [0, 0, 0, 0, 0]

            # Get exact changes to be enacted by post-combat effects
            current_player_units, current_enemy_units = self.map.get_heroes_present_by_side()
            damage_taken, heals_given, absolute_heals_given, sp_charges, divine_veins = feh.end_of_combat(atk_effects, def_effects, player, targeted_enemy, savior_unit)

            # Post combat damage/healing/sp charges across the field
            for x in current_player_units + current_enemy_units:
                hp_change = 0
                if x in damage_taken and Status.EnGarde not in x.statusPos:
                    hp_change -= damage_taken[x]
                if x in heals_given and Status.DeepWounds not in x.statusNeg:
                    hp_change += heals_given[x]
                if x in absolute_heals_given:
                    hp_change += absolute_heals_given[x]

                if hp_change != 0:
                    x.HPcur = max(1, min(x.HPcur + hp_change, x.visible_stats[HP]))

                    if hp_change > 0:
                        self.after(finish_time, self.animate_heal_popup, hp_change, x.tile.tileNum)
                    if hp_change < 0:
                        self.after(finish_time, self.animate_damage_popup, abs(hp_change), x.tile.tileNum)

                if x in sp_charges:
                    x.chargeSpecial(sp_charges[x])

                x_side = x.side

                if x in self.all_units[x_side]:
                    x_index = self.all_units[x_side].index(x)
                else:
                    x_index = self.all_cohorts.index(x)

                x_hp_label = self.unit_hp_count_labels[x_side][x_index]
                x_hp_bar = self.unit_hp_bars_fg[x_side][x_index]
                x_sp_label = self.unit_sp_count_labels[x_side][x_index]

                hp_percentage = x.HPcur / x.visible_stats[HP]

                if x.specialCount != -1:
                    self.after(finish_time, self.set_text_val, x_sp_label, x.specialCount)

                self.after(finish_time, self.set_text_val, x_hp_label, x.HPcur)
                self.after(finish_time, self.set_hp_bar_length, x_hp_bar, hp_percentage)

            # Apply divine veins

            # Remove duplicate values across multiple sets
            counter = Counter(num for arr in divine_veins.values() for num in arr)
            divine_veins = {key: [num for num in arr if counter[num] == 1] for key, arr in divine_veins.items()}

            if (player, "haze") in divine_veins:
                for tile_int in divine_veins[(player, "haze")]:
                    cur_tile_struct = self.map.tiles[tile_int].structure_on
                    if self.map.tiles[tile_int].terrain != 4 and (not cur_tile_struct or (cur_tile_struct and cur_tile_struct.health != -1)):
                        self.map.tiles[tile_int].divine_vein = DV_HAZE
                        self.map.tiles[tile_int].divine_vein_side = player.side
                        self.map.tiles[tile_int].divine_vein_turn = 1

            self.after(finish_time, self.refresh_divine_veins)

            # Movement-based skills after combat
            player_tile_number = player.tile.tileNum
            enemy_tile_number = enemy.tile.tileNum
            ally_tile_number = -1

            player_move_pos = player_tile_number
            enemy_move_pos = enemy_tile_number
            ally_move_pos = -1

            swapping_ally = None

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

            elif "leilaSwap" in player.getSkills() or "leilaRefineSwap" in player.getSkills():
                if len([potential_ally for potential_ally in feh.allies_within_n(player, 2) if potential_ally.isSupportOf(player)]) == 1:
                    swapping_ally = [potential_ally for potential_ally in feh.allies_within_n(player, 2) if potential_ally.isSupportOf(player)][0]
                    ally_tile_number = swapping_ally.tile.tileNum

                    player_move_pos = ally_tile_number
                    ally_move_pos = player_tile_number

                    enemy_move_pos = -1

            # Case 1: Movement with opponent

            # Ensure tiles do not have any heroes/structures/invalid terrain
            if player_move_pos != -1 and enemy_move_pos != -1 and player.HPcur != 0:
                if self.map.tiles[player_move_pos].hero_on is not None and (self.map.tiles[player_move_pos].hero_on != player and self.map.tiles[player_move_pos].hero_on != enemy):
                    player_move_pos = -1
                elif self.map.tiles[enemy_move_pos].hero_on is not None and (self.map.tiles[enemy_move_pos].hero_on != player and self.map.tiles[enemy_move_pos].hero_on != enemy):
                    enemy_move_pos = -1
                elif not feh.can_be_on_tile(self.map.tiles[player_move_pos], player.move):
                    player_move_pos = -1
                elif not feh.can_be_on_tile(self.map.tiles[enemy_move_pos], enemy.move):
                    enemy_move_pos = -1

            # If tiles are still valid, make moves
            if player_move_pos != -1 and enemy_move_pos != -1 and player.HPcur != 0 and not savior_unit:
                player.tile.hero_on = None
                enemy.tile.hero_on = None

                player.tile = self.map.tiles[player_move_pos]
                enemy.tile = self.map.tiles[enemy_move_pos]

                player.tile.hero_on = player
                enemy.tile.hero_on = enemy

                self.after(finish_time, self.move_visuals_to_tile_obj, player, player_move_pos)
                self.after(finish_time, self.move_visuals_to_tile_obj, enemy, enemy_move_pos)

            # Case 2: Movement with ally

            # Ensure tiles do not have any invalid terrain
            if player_move_pos != -1 and ally_move_pos != -1 and player.HPcur != 0:
                if not feh.can_be_on_tile(self.map.tiles[player_move_pos], player.move):
                    player_move_pos = -1
                elif not feh.can_be_on_tile(self.map.tiles[ally_move_pos], swapping_ally.move):
                    ally_move_pos = -1

            # If tiles are still valid, make moves
            if player_move_pos != -1 and ally_move_pos != -1 and player.HPcur != 0 and not savior_unit:
                player.tile.hero_on = None
                swapping_ally.tile.hero_on = None

                player.tile = self.map.tiles[player_move_pos]
                swapping_ally.tile = self.map.tiles[ally_move_pos]

                player.tile.hero_on = player
                swapping_ally.tile.hero_on = swapping_ally

                self.after(finish_time, self.move_visuals_to_tile_obj, player, player_move_pos)
                self.after(finish_time, self.move_visuals_to_tile_obj, swapping_ally, ally_move_pos)

            # If moving onto traps after combat
            player_struct = player.tile.structure_on
            enemy_struct = enemy.tile.structure_on

            if player_struct and "Trap" in player_struct.name and player.side == PLAYER and player_struct.health != 0 and player.HPcur != 0:
                player_struct.health = 0
                self.after(finish_time, self.refresh_walls)

                if "False" not in player_struct.name:
                    if player_struct.name == "Bolt Trap":
                        disarm_lvl = player.get("disarmTrap", 0)

                        if final_dest_struct.level > disarm_lvl:
                            for trap_unit in player.tile.unitsWithinNSpaces(3):
                                trap_damage = final_dest_struct.level * 10

                                if Status.EnGarde in trap_unit.statusPos:
                                    trap_damage = 0

                                trap_unit.HPcur = max(1, trap_unit.HPcur - trap_damage)

                                if damage_taken or heals_given:
                                    self.after(finish_time + 450, self.animate_damage_popup, trap_damage, trap_unit.tile.tileNum)
                                    self.after(finish_time + 450, self.set_hp_visual, trap_unit, trap_unit.HPcur)
                                else:
                                    self.after(finish_time, self.animate_damage_popup, trap_damage, trap_unit.tile.tileNum)
                                    self.after(finish_time, self.set_hp_visual, trap_unit, trap_unit.HPcur)

                    elif player_struct.name == "Heavy Trap":
                        disarm_lvl = player.get("disarmTrap", 0)

                        if final_dest_struct.level > disarm_lvl:
                            for trap_unit in player.tile.unitsWithinNSpaces(2):
                                if trap_unit.HPcur <= get_tower_hp_threshold(player_struct.level):
                                    trap_unit.inflictStatus(Status.Gravity)

                    elif player_struct.name == "Hex Trap" and player.HPcur <= get_tower_hp_threshold(player_struct.level):
                        hex_trap_triggered_after_action = True

            if enemy_struct and "Trap" in enemy_struct.name and enemy.side == PLAYER and enemy_struct.health != 0 and enemy.HPcur != 0:
                enemy_struct.health = 0
                self.after(finish_time, self.refresh_walls)

                if "False" not in enemy_struct.name:
                    if enemy_struct.name == "Bolt Trap":
                        disarm_lvl = enemy.get("disarmTrap", 0)

                        if final_dest_struct.level > disarm_lvl:
                            for trap_unit in enemy.tile.unitsWithinNSpaces(3):
                                trap_damage = final_dest_struct.level * 10

                                if Status.EnGarde in trap_unit.statusPos:
                                    trap_damage = 0

                                trap_unit.HPcur = max(1, trap_unit.HPcur - trap_damage)

                                if damage_taken or heals_given:
                                    self.after(finish_time + 450, self.animate_damage_popup, trap_damage, trap_unit.tile.tileNum)
                                    self.after(finish_time + 450, self.set_hp_visual, trap_unit, trap_unit.HPcur)
                                else:
                                    self.after(finish_time, self.animate_damage_popup, trap_damage, trap_unit.tile.tileNum)
                                    self.after(finish_time, self.set_hp_visual, trap_unit, trap_unit.HPcur)

                    elif enemy_struct.name == "Heavy Trap":
                        disarm_lvl = enemy.get("disarmTrap", 0)

                        if final_dest_struct.level > disarm_lvl:
                            for trap_unit in enemy.tile.unitsWithinNSpaces(2):
                                if trap_unit.HPcur <= get_tower_hp_threshold(enemy_struct.level):
                                    trap_unit.inflictStatus(Status.Gravity)


            # EXTRA ACTION FROM COMBAT
            if not hex_trap_triggered_after_action:

                # Share Spoils
                if Status.ShareSpoils in initiated_enemy.statusNeg and initiated_enemy.HPcur == 0:
                    galeforce_triggered = True

                # Time and Light goes here

                # Victorious Axe (Refine Eff) - Edelgard
                elif "another 3 years" in player.getSkills() and not feh.allies_within_n(player, 1) and not player.nonspecial_galeforce_triggered:
                    player.nonspecial_galeforce_triggered = True
                    galeforce_triggered = True

                # Raging Storm (II) - Edelgard
                elif "RagingStormSolo" in player.getSkills() and not feh.allies_within_n(player, 1) and not player.nonspecial_galeforce_triggered:
                    player.nonspecial_galeforce_triggered = True
                    galeforce_triggered = True

                elif "IT'S ME" in player.getSkills() and player.transformed and not player.nonspecial_galeforce_triggered:
                    player.nonspecial_galeforce_triggered = True
                    galeforce_triggered = True

                # Lone Wolf (Combat)
                elif "lone_wolf" in player.getSkills() and player.assistTargetedOther == 0 and player.assistTargetedSelf == 0 and not player.nonspecial_galeforce_triggered:
                    player.nonspecial_galeforce_triggered = True
                    galeforce_triggered = True

                # Override
                elif "override" in player.getSkills() and num_aoe_targets >= 2 and not player.nonspecial_galeforce_triggered:
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

                    if "galeforce_gravity" in player.getSkills():
                        player.inflictStatus(Status.Gravity)

                        if player.pair_up_obj:
                            player.pair_up_obj.inflictStatus(Status.Gravity)

                elif "requiemDance" in player.getSkills() and player.specialCount == 0 and not player.special_galeforce_triggered:
                    highest_hp = []
                    for ally in feh.allies_within_n(player, 2):
                        if not highest_hp or ally.HPcur == highest_hp[0].HPcur and ally not in self.units_to_move:
                            highest_hp.append(ally)
                        elif ally.HPcur > highest_hp[0].HPcur:
                            highest_hp = [ally]

                    if len(highest_hp) == 1:
                        highest_hp_ally = highest_hp[0]

                        player.special_galeforce_triggered = True
                        player.specialCount = player.specialMax

                        self.units_to_move.append(highest_hp_ally)
                        self.after(finish_time, self.update_unit_graphics, highest_hp_ally)

                        highest_hp_ally.inflictStatus(Status.Gravity)

                        if highest_hp_ally.pair_up_obj:
                            highest_hp_ally.pair_up_obj.inflictStatus(Status.Gravity)

                        self.after(finish_time, self.refresh_unit_visuals_obj, player)

                if galeforce_triggered:
                    self.after(finish_time, self.update_unit_graphics, player)

            # If the dragged unit dies in combat, remove them from the map
            if player.HPcur == 0:
                self.after(finish_time, set_unit_death, player)

                # If enemy unit, add to list of kills
                if player.side == ENEMY:
                    if player.intName not in self.enemy_defeated_count:
                        self.enemy_defeated_count[player.intName] = 1
                    else:
                        self.enemy_defeated_count[player.intName] += 1

                # remove from list of units
                if player in self.current_units[player.side]:
                    self.current_units[player.side].remove(player)
                else:
                    self.current_units[player.side].remove(player.pair_up_obj)

                # take unit off map
                player.tile.hero_on = None

                # self.after(finish_time, clear_banner)
                self.after(finish_time, self.unit_status.clear)

                if player.side == PLAYER:
                    self.after(finish_time, partial(self.button_frame.action_button.config, state='disabled', text='Action\nButton'))
                    CreateToolTip(self.button_frame.action_button, text='')

            else:
                self.after(finish_time, self.unit_status.update_from_obj, player)

            # If the targeted unit dies in combat, remove them from the map
            if initiated_enemy.HPcur == 0:
                self.after(finish_time, set_unit_death, initiated_enemy)

                # If enemy unit, add to list of kills
                if initiated_enemy.side == ENEMY:
                    if initiated_enemy.intName not in self.enemy_defeated_count:
                        self.enemy_defeated_count[initiated_enemy.intName] = 1
                    else:
                        self.enemy_defeated_count[initiated_enemy.intName] += 1

                # remove from list of units
                if initiated_enemy in self.current_units[initiated_enemy.side]:
                    self.current_units[initiated_enemy.side].remove(initiated_enemy)
                else:
                    self.current_units[initiated_enemy.side].remove(initiated_enemy.pair_up_obj)

                # take unit off map
                initiated_enemy.tile.hero_on = None


            # Remove forecast
            self.after(finish_time, self.extras.clear_forecast_banner)

            # After animation complete. re-enable user control
            self.after(finish_time, animation_done)

        # ASSIIIIIIIIIIIIIIIIIIIIIIST!!!!!!!!!!!!!!!!!!!!
        elif is_targeting_object and is_targeting_hero and destination_unit.isAllyOf(release_unit) and not trap_triggered:
            action = ASSIST

            player = destination_unit
            ally = release_unit



            # Determines if unit should keep their action upon using an assist
            assist_galeforce = False

            if ally in self.all_units[S]:
                ally_index = self.all_units[S].index(ally)
            else:
                ally_index = self.all_cohorts.index(ally)

            unit_final_position = -1
            ally_final_position = -1

            playerSkills = player.getSkills()

            # Staff Healing
            if "heal" in player.assist.effects:
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
                            hp_healed_other = 10 if Status.DeepWounds not in x.statusNeg else 0

                            x.HPcur = min(x.visible_stats[HP], x.HPcur + hp_healed_other)
                            self.refresh_unit_visuals_obj(x)

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

                if player.bskill and "live_to_serve" in player.bskill.effects:
                    percentage = 0.25 + 0.25 * player.bskill.effects["live_to_serve"]
                    hp_healed_self += trunc(hp_healed_ally * percentage)

                # Deep Wounds
                if Status.DeepWounds in player.statusNeg: hp_healed_self = 0
                if Status.DeepWounds in ally.statusNeg: hp_healed_ally = 0

                # Restore (+)
                if "restore" in player.assist.effects:
                    if Status.Schism in ally.statusNeg:
                        if Status.Pathfinder in ally.statusPos:
                            ally.statusPos.remove(Status.Pathfinder)
                        if Status.TriangleAttack in ally.statusPos:
                            ally.statusPos.remove(Status.TriangleAttack)
                        if Status.DualStrike in ally.statusPos:
                            ally.statusPos.remove(Status.DualStrike)

                    ally.debuffs = [0, 0, 0, 0, 0]
                    ally.statusNeg.clear()

                ally.HPcur = min(ally.visible_stats[HP], ally.HPcur + hp_healed_ally)
                player.HPcur = min(player.visible_stats[HP], player.HPcur + hp_healed_self)

                self.animate_heal_popup(hp_healed_ally, ally.tile.tileNum)

                # Get/Update HP assets
                self.refresh_unit_visuals_obj(ally)

                # Display self heal (only if amount healed > 0)
                if hp_healed_self > 0:
                    self.animate_heal_popup(hp_healed_self, player.tile.tileNum)

                    self.refresh_unit_visuals_obj(player)

                # Charge own special for Staff assist use
                if staff_special_triggered:
                    player.specialCount = player.specialMax
                    self.refresh_unit_visuals_obj(player)
                elif player.specialCount != -1:
                    player.specialCount = max(player.specialCount - 1, 0)
                    self.refresh_unit_visuals_obj(player)

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

            # Dance/Sing/Play
            elif "refresh" in player.assist.effects:
                unit_final_position = player.tile.tileNum
                ally_final_position = ally.tile.tileNum

                # Grant ally another action
                self.units_to_move.append(ally)

                if ally in self.all_units[S]:
                    ally_index = self.all_units[S].index(ally)

                    if not ally.transformed:
                        ally_sprite = self.unit_sprites[S][ally_index]
                        ally_gs_sprite = self.unit_sprites_gs[S][ally_index]
                    else:
                        ally_sprite = self.unit_sprites_trans[S][ally_index]
                        ally_gs_sprite = self.unit_sprites_gs_trans[S][ally_index]
                else:
                    ally_index = self.all_cohorts.index(ally)

                    if not ally.transformed:
                        ally_sprite = self.cohort_sprites[ally_index]
                        ally_gs_sprite = self.cohort_sprites_gs[ally_index]
                    else:
                        ally_sprite = self.cohort_sprites_trans[ally_index]
                        ally_gs_sprite = self.cohort_sprites_gs_trans[ally_index]

                self.itemconfig(ally_sprite, state='normal')
                self.itemconfig(ally_gs_sprite, state='hidden')

                if "atkRefresh" in playerSkills: ally.inflictStat(ATK, playerSkills["atkRefresh"])
                if "spdRefresh" in playerSkills: ally.inflictStat(SPD, playerSkills["spdRefresh"])
                if "defRefresh" in playerSkills: ally.inflictStat(DEF, playerSkills["defRefresh"])
                if "resRefresh" in playerSkills: ally.inflictStat(RES, playerSkills["resRefresh"])

                if "firestormDance" in playerSkills: ally.inflictStatus(Status.Desperation)

                if "spectrumRefresh" in playerSkills:
                    i = 1
                    while i <= 4:
                        ally.inflictStat(i, playerSkills["spectrumRefresh"])
                        i += 1

                if "atkCantrip" in playerSkills:
                    for foe in feh.nearest_foes_within_n(player, 4):
                        foe.inflictStats(ATK, -playerSkills["atkCantrip"])

                if "spdCantrip" in playerSkills:
                    for foe in feh.nearest_foes_within_n(player, 4):
                        foe.inflictStats(SPD, -playerSkills["spdCantrip"])

                if "defCantrip" in playerSkills:
                    for foe in feh.nearest_foes_within_n(player, 4):
                        foe.inflictStats(DEF, -playerSkills["defCantrip"])

                if "resCantrip" in playerSkills:
                    for foe in feh.nearest_foes_within_n(player, 4):
                        foe.inflictStats(RES, -playerSkills["resCantrip"])

                # Gentle Dream - Peony
                if "peonyRefresh" in playerSkills:
                    valid_allies = [ally]

                    for x in [player, ally]:
                        allies = feh.allies_within_n_cardinal(x, 1)
                        for other_ally in allies:
                            if other_ally not in valid_allies and other_ally != player:
                                valid_allies.append(other_ally)

                    for other_ally in valid_allies:
                        other_ally.inflictStat(ATK, 3)
                        other_ally.inflictStat(SPD, 3)
                        other_ally.inflictStat(DEF, 3)
                        other_ally.inflictStat(RES, 3)
                        other_ally.inflictStatus(Status.Orders)

                if "peonyRefreshII" in playerSkills:
                    valid_allies = [ally]

                    for x in [player, ally]:
                        allies = feh.allies_within_n_cardinal(x, 1)
                        for other_ally in allies:
                            if other_ally not in valid_allies and other_ally != player:
                                valid_allies.append(other_ally)

                    for other_ally in valid_allies:
                        other_ally.inflictStat(ATK, 4)
                        other_ally.inflictStat(SPD, 4)
                        other_ally.inflictStat(DEF, 4)
                        other_ally.inflictStat(RES, 4)
                        other_ally.inflictStatus(Status.Orders)
                        other_ally.inflictStatus(Status.NullPenalties)

                # Whimsical Dream - Mirabilis
                if "mirabilisRefresh" in playerSkills:
                    ally.inflictStat(ATK, 5)

                    for other_ally in feh.allies_within_n(ally, 2):
                        other_ally.inflictStat(ATK, 5)

                    for foe in feh.nearest_foes_within_n(ally, 4):
                        foe.inflictStat(ATK, -5)

                        for foe_ally in feh.allies_within_n(foe, 2):
                            foe_ally.inflictStat(ATK, -5)

                if "mirabilisRefreshII" in playerSkills:
                    ally.inflictStat(ATK, 6)
                    ally.inflictStatus(Status.NullBonuses)

                    for other_ally in feh.allies_within_n(ally, 2):
                        other_ally.inflictStat(ATK, 6)
                        other_ally.inflictStatus(Status.NullBonuses)

                    for foe in feh.nearest_foes_within_n(ally, 4):
                        foe.inflictStat(ATK, -6)

                        for foe_ally in feh.allies_within_n(foe, 2):
                            foe_ally.inflictStat(ATK, -6)

                # Sweet Dreams - Plumeria
                if "plumeriaRefresh" in playerSkills:
                    ally.inflictStat(ATK, 3)
                    ally.inflictStat(SPD, 3)
                    ally.inflictStat(DEF, 3)
                    ally.inflictStat(RES, 3)

                    for foe in feh.nearest_foes_within_n(ally, 4):
                        foe.inflictStat(ATK, -4)
                        foe.inflictStat(SPD, -4)
                        foe.inflictStat(DEF, -4)
                        foe.inflictStat(RES, -4)

                if "plumeriaRefreshII" in playerSkills:
                    ally.inflictStat(ATK, 5)
                    ally.inflictStat(SPD, 5)
                    ally.inflictStat(DEF, 5)
                    ally.inflictStat(RES, 5)
                    ally.inflictStatus(Status.Pursual)
                    ally.inflictStatus(Status.Hexblade)

                    for foe in feh.nearest_foes_within_n(ally, 4):
                        foe.inflictStat(ATK, -5)
                        foe.inflictStat(SPD, -5)
                        foe.inflictStat(DEF, -5)
                        foe.inflictStat(RES, -5)

                # Frightful Dream - Triandra
                if "triandraRefresh" in playerSkills:
                    valid_foes = []

                    for x in [player, ally]:
                        for foe in feh.foes_within_n_cardinal(x, 1):
                            if foe not in valid_foes:
                                valid_foes.append(foe)

                    for foe in valid_foes:
                        foe.inflictStat(ATK, -3)
                        foe.inflictStat(SPD, -3)
                        foe.inflictStat(DEF, -3)
                        foe.inflictStat(RES, -3)
                        foe.inflictStatus(Status.Guard)

                if "triandraRefreshII" in playerSkills:
                    valid_foes = []

                    for x in [player, ally]:
                        for foe in feh.foes_within_n_cardinal(x, 1):
                            if foe not in valid_foes:
                                valid_foes.append(foe)

                    for foe in valid_foes:
                        foe.inflictStat(ATK, -5)
                        foe.inflictStat(SPD, -5)
                        foe.inflictStat(DEF, -5)
                        foe.inflictStat(RES, -5)
                        foe.inflictStatus(Status.Guard)
                        foe.inflictStatus(Status.Discord)

                # Frost Breath - Nils
                if "nilsPlay" in playerSkills:
                    for foe in feh.nearest_foes_within_n(player, 4):
                        foe.inflictStat(ATK, -4)
                        foe.inflictStat(SPD, -4)
                        foe.inflictStat(DEF, -4)
                        foe.inflictStat(RES, -4)

                # Enveloping Breath (Base) - FA!Ninian
                if "faNinianBoost" in playerSkills:
                    valid_foes = []

                    for x in [player, ally]:
                        for foe in feh.foes_within_n_cardinal(x, 1):
                            if foe not in valid_foes:
                                valid_foes.append(foe)

                    for foe in valid_foes:
                        foe.inflictStat(ATK, -7)
                        foe.inflictStat(RES, -7)
                        foe.inflictStatus(Status.Guard)

                # Call to Flame - FA!Ninian
                if "callToFlame" in playerSkills:
                    ally.inflictStatus(Status.SpecialCharge)
                    ally.inflictStat(ATK, 6)

                    if ally.wpnType in DRAGON_WEAPONS:
                        ally.inflictStatus(Status.MobilityUp)

                # Faithful Breath (Base) - L!Ninian
                if "LNinianBoost" in playerSkills:
                    for foe in feh.nearest_foes_within_n(player, 4):
                        foe.inflictStat(DEF, -6)
                        foe.inflictStat(RES, -6)

                    for foe in feh.nearest_foes_within_n(ally, 4):
                        foe.inflictStat(DEF, -6)
                        foe.inflictStat(RES, -6)

                # Gray Waves - L!Azura
                if "azureMove" in playerSkills and (ally.move == 0 or ally.move == 2):
                    ally.inflictStatus(Status.MobilityUp)

                if "azureMoveNP" in playerSkills and (ally.move == 0 or ally.move == 2):
                    ally.inflictStatus(Status.MobilityUp)
                    ally.inflictStatus(Status.NullPanic)

                # Dancling Flames - DE!Azura
                if "deAzuraRefresh" in playerSkills:
                    for ally in feh.allies_within_n(player, 1):
                        ally.inflictStat(ATK, 6)
                        ally.inflictStat(SPD, 6)
                        ally.inflictStat(DEF, 6)
                        ally.inflictStat(RES, 6)

                # Prayer Wheel - L!Azura
                if "azuraBonusEnhance" in playerSkills:
                    highest_bonus = max(ally.buffs)

                    if highest_bonus:
                        ally.inflictStat(ATK, highest_bonus)
                        ally.inflictStat(SPD, highest_bonus)
                        ally.inflictStat(DEF, highest_bonus)
                        ally.inflictStat(RES, highest_bonus)

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

                ally_heal = 10 if Status.DeepWounds not in ally.statusNeg else 0

                ally.HPcur = min(ally.visible_stats[HP], ally.HPcur + ally_heal)
                player.HPcur = max(1, player.HPcur - 10)

                self.animate_heal_popup(ally_heal, ally.tile.tileNum)
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

                i = 1
                while i < len(ally.debuffs):
                    ally.buffs[i] = max(abs(ally.debuffs[i]), ally.buffs[i])
                    ally.debuffs[i] = 0
                    i += 1

            if "maidenSolace" in player.assist.effects:
                unit_final_position = player.tile.tileNum
                ally_final_position = ally.tile.tileNum

                if Status.Schism in ally.statusNeg:
                    if Status.Pathfinder in ally.statusPos:
                        ally.statusPos.remove(Status.Pathfinder)
                    if Status.TriangleAttack in ally.statusPos:
                        ally.statusPos.remove(Status.TriangleAttack)
                    if Status.DualStrike in ally.statusPos:
                        ally.statusPos.remove(Status.DualStrike)

                ally.statusNeg.clear()

                i = 1
                while i < len(ally.debuffs):
                    ally.buffs[i] = max(abs(ally.debuffs[i]), ally.buffs[i])
                    ally.debuffs[i] = 0
                    i += 1

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

            if "harsh_comm_plus" in player.assist.effects:
                unit_final_position = player.tile.tileNum
                ally_final_position = ally.tile.tileNum

                if Status.Schism in ally.statusNeg:
                    if Status.Pathfinder in ally.statusPos:
                        ally.statusPos.remove(Status.Pathfinder)
                    if Status.TriangleAttack in ally.statusPos:
                        ally.statusPos.remove(Status.TriangleAttack)
                    if Status.DualStrike in ally.statusPos:
                        ally.statusPos.remove(Status.DualStrike)

                ally.statusNeg.clear()

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

                self.move_visuals_to_tile_obj(player, unit_final_position)
                self.move_visuals_to_tile_obj(ally, ally_final_position)

            # Clear status effects, action taken
            player.statusNeg = []
            if Status.GrandStrategy not in player.statusPos: player.debuffs = [0, 0, 0, 0, 0]

            if player.pair_up_obj:
                player.pair_up_obj.statusNeg = []
                if Status.GrandStrategy not in player.pair_up_obj.statusPos: player.pair_up_obj.debuffs = [0, 0, 0, 0, 0]

            # Skills that grant effects when assist skills are used

            playerSkills = player.getSkills()
            allySkills = ally.getSkills()

            # Assist or Rally used
            if player.assist.type == "Rally" or player.assist.type == "Move":
                if "shigureLink" in playerSkills or "shigureLink" in allySkills:
                    hp_healed = playerSkills.get("shigureLink", 0) + allySkills.get("shigureLink", 0)

                    for x in [player, ally]:
                        cur_heal = hp_healed if Status.DeepWounds not in x.statusNeg else 0

                        x.HPcur = min(x.visible_stats[HP], ally.HPcur + cur_heal)
                        self.animate_heal_popup(cur_heal, x.tile.tileNum)

                        # Get/Update HP assets
                        self.refresh_unit_visuals_obj(x)

                if "merlinusRally" in playerSkills:
                    ally.inflictStat(ATK, 6)
                    ally.inflictStat(SPD, 6)
                    ally.inflictStatus(Status.BonusDoubler)
                    ally.inflictStatus(Status.NullPenalties)

                    for other_ally in feh.allies_within_n(ally, 2):
                        if other_ally != player:
                            other_ally.inflictStat(ATK, 6)
                            other_ally.inflictStat(SPD, 6)
                            other_ally.inflictStatus(Status.BonusDoubler)
                            other_ally.inflictStatus(Status.NullPenalties)

                if "hubertRuse" in playerSkills or "hubertRuse" in allySkills:
                    valid_foes = []

                    for x in [player, ally]:
                        foes = feh.foes_within_n_cardinal(x, 1)
                        for foe in foes:
                            if foe not in valid_foes:
                                valid_foes.append(foe)

                    for foe in valid_foes:
                        foe.inflictStat(ATK, -7)
                        foe.inflictStat(DEF, -7)
                        foe.inflictStat(RES, -7)
                        foe.inflictStatus(Status.Guard)
                        foe.inflictStatus(Status.Exposure)

                if "ymirBoost" in playerSkills or "ymirBoost" in allySkills:
                    hp_healed = playerSkills.get("ymirBoost", 0) + allySkills.get("ymirBoost", 0)

                    allied_affected = [player, ally]

                    for ally in feh.allies_within_n(player, 2) + feh.allies_within_n(ally, 2):
                        if ally not in allied_affected:
                            allied_affected.append(ally)

                    for ally in allied_affected:
                        # Heal
                        cur_heal = hp_healed if Status.DeepWounds not in ally.statusNeg else 0

                        ally.HPcur = min(ally.visible_stats[HP], ally.HPcur + cur_heal)
                        self.animate_heal_popup(cur_heal, ally.tile.tileNum)

                        # Get/Update HP assets
                        self.refresh_unit_visuals_obj(ally)

                        # Clear Penalties
                        if Status.Schism in ally.statusNeg:
                            if Status.Pathfinder in ally.statusPos:
                                ally.statusPos.remove(Status.Pathfinder)
                            if Status.TriangleAttack in ally.statusPos:
                                ally.statusPos.remove(Status.TriangleAttack)
                            if Status.DualStrike in ally.statusPos:
                                ally.statusPos.remove(Status.DualStrike)

                        ally.statusNeg.clear()
                        ally.debuffs = [0, 0, 0, 0, 0]

            # Link skills, or other effects that trigger after assist use
            if player.assist.type == "Move":
                if "atkSpdLink" in playerSkills or "atkSpdLink" in allySkills:
                    stat_boost = max(playerSkills.get("atkSpdLink", 0), allySkills.get("atkSpdLink", 0))

                    for x in [player, ally]:
                        x.inflictStat(ATK, stat_boost * 2)
                        x.inflictStat(SPD, stat_boost * 2)

                if "atkDefLink" in playerSkills or "atkDefLink" in allySkills:
                    stat_boost = max(playerSkills.get("atkDefLink", 0), allySkills.get("atkDefLink", 0))

                    for x in [player, ally]:
                        x.inflictStat(ATK, stat_boost * 2)
                        x.inflictStat(DEF, stat_boost * 2)

                if "atkResLink" in playerSkills or "atkResLink" in allySkills:
                    stat_boost = max(playerSkills.get("atkResLink", 0), allySkills.get("atkResLink", 0))

                    for x in [player, ally]:
                        x.inflictStat(ATK, stat_boost * 2)
                        x.inflictStat(RES, stat_boost * 2)

                if "spdDefLink" in playerSkills or "spdDefLink" in allySkills:
                    stat_boost = max(playerSkills.get("spdDefLink", 0), allySkills.get("spdDefLink", 0))

                    for x in [player, ally]:
                        x.inflictStat(SPD, stat_boost * 2)
                        x.inflictStat(DEF, stat_boost * 2)

                if "spdResLink" in playerSkills or "spdResLink" in allySkills:
                    stat_boost = max(playerSkills.get("spdResLink", 0), allySkills.get("spdResLink", 0))

                    for x in [player, ally]:
                        x.inflictStat(SPD, stat_boost * 2)
                        x.inflictStat(RES, stat_boost * 2)

                if "defResLink" in playerSkills or "defResLink" in allySkills:
                    stat_boost = max(playerSkills.get("defResLink", 0), allySkills.get("defResLink", 0))

                    for x in [player, ally]:
                        x.inflictStat(DEF, stat_boost * 2)
                        x.inflictStat(RES, stat_boost * 2)

                if "atkSpdLinkW" in playerSkills or "atkSpdLinkW" in allySkills:
                    for x in [player, ally]:
                        x.inflictStat(ATK, 6)
                        x.inflictStat(SPD, 6)

                if "atkSpdSnag" in playerSkills or "atkSpdSnag" in allySkills:
                    stat_penalty = max(playerSkills.get("atkSpdSnag", 0), allySkills.get("atkSpdSnag", 0))

                    affected_units = list(set(feh.nearest_foes_within_n(player, 4) + feh.nearest_foes_within_n(ally, 4)))

                    for x in affected_units:
                        x.inflictStat(ATK, -stat_penalty)
                        x.inflictStat(SPD, -stat_penalty)

                if "atkDefSnag" in playerSkills or "atkDefSnag" in allySkills:
                    stat_penalty = max(playerSkills.get("atkDefSnag", 0), allySkills.get("atkDefSnag", 0))

                    affected_units = list(set(feh.nearest_foes_within_n(player, 4) + feh.nearest_foes_within_n(ally, 4)))

                    for x in affected_units:
                        x.inflictStat(ATK, -stat_penalty)
                        x.inflictStat(DEF, -stat_penalty)

                if "atkResSnag" in playerSkills or "atkResSnag" in allySkills:
                    stat_penalty = max(playerSkills.get("atkResSnag", 0), allySkills.get("atkResSnag", 0))

                    affected_units = list(set(feh.nearest_foes_within_n(player, 4) + feh.nearest_foes_within_n(ally, 4)))

                    for x in affected_units:
                        x.inflictStat(ATK, -stat_penalty)
                        x.inflictStat(RES, -stat_penalty)

                if "spdDefSnag" in playerSkills or "spdDefSnag" in allySkills:
                    stat_penalty = max(playerSkills.get("spdDefSnag", 0), allySkills.get("spdDefSnag", 0))

                    affected_units = list(set(feh.nearest_foes_within_n(player, 4) + feh.nearest_foes_within_n(ally, 4)))

                    for x in affected_units:
                        x.inflictStat(SPD, -stat_penalty)
                        x.inflictStat(DEF, -stat_penalty)

                if "spdResSnag" in playerSkills or "spdResSnag" in allySkills:
                    stat_penalty = max(playerSkills.get("spdResSnag", 0), allySkills.get("spdResSnag", 0))

                    affected_units = list(set(feh.nearest_foes_within_n(player, 4) + feh.nearest_foes_within_n(ally, 4)))

                    for x in affected_units:
                        x.inflictStat(SPD, -stat_penalty)
                        x.inflictStat(RES, -stat_penalty)

                if "defResSnag" in playerSkills or "defResSnag" in allySkills:
                    stat_penalty = max(playerSkills.get("defResSnag", 0), allySkills.get("defResSnag", 0))

                    affected_units = list(set(feh.nearest_foes_within_n(player, 4) + feh.nearest_foes_within_n(ally, 4)))

                    for x in affected_units:
                        x.inflictStat(DEF, -stat_penalty)
                        x.inflictStat(RES, -stat_penalty)

                if "laslowShmovement" in playerSkills or "laslowShmovement" in allySkills:
                    affected_units = [player, ally]
                    affected_units += feh.allies_within_n(player, 2)
                    affected_units += feh.allies_within_n(ally, 2)

                    affected_units = list(set(affected_units))

                    for x in affected_units:
                        x.inflictStat(ATK, 4)
                        x.inflictStat(SPD, 4)
                        x.inflictStat(DEF, 4)
                        x.inflictStat(RES, 4)

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
                    for x in [player, ally]:
                        x.inflictStatus(Status.Pursual)

                # Saberooth Fang (Base) - Mordecai
                if "mordecaiLink" in playerSkills or "mordecaiLink" in allySkills:
                    affected_units = []
                    affected_units += feh.foes_within_n(player, 2)
                    affected_units += feh.foes_within_n(ally, 2)

                    affected_units = list(set(affected_units))

                    for foe in affected_units:
                        foe.inflictStat(ATK, -4)
                        foe.inflictStat(SPD, -4)
                        foe.inflictStat(DEF, -4)
                        foe.inflictStat(RES, -4)

                # Saberooth Fang (Refine Base) - Mordecai
                if "mordecaiRefineLink" in playerSkills or "mordecaiRefineLink" in allySkills:
                    affected_units = []
                    affected_units += feh.foes_within_n(player, 2)
                    affected_units += feh.foes_within_n(ally, 2)

                    affected_units = list(set(affected_units))

                    for foe in affected_units:
                        foe.inflictStat(ATK, -5)
                        foe.inflictStat(SPD, -5)
                        foe.inflictStat(DEF, -5)
                        foe.inflictStat(RES, -5)

                # Sabertooth Fang (Refine Eff) - Mordecai
                if "mordecaiSPJump" in playerSkills or "mordecaiSPJump" in allySkills:
                    total_jump = 0

                    if "mordecaiSPJump" in playerSkills: total_jump += 1
                    if "mordecaiSPJump" in allySkills: total_jump += 1

                    affected_units = []
                    affected_units += feh.foes_within_n(player, 2)
                    affected_units += feh.foes_within_n(ally, 2)

                    affected_units = list(set(affected_units))

                    for foe in affected_units:
                        foe.chargeSpecial(-total_jump)
                        self.refresh_unit_visuals_obj(foe)

                # Destiny's Bow (Base) - V!Chrom
                if "vChromBoost" in playerSkills or "vChromBoost" in allySkills and self.turn_info[0] <= 4:
                    total_jump = 0

                    if "vChromBoost" in playerSkills and player.assistTargetedSelf_Move == 0 and player.assistTargetedOther_Move == 0: total_jump += 1
                    if "vChromBoost" in allySkills and ally.assistTargetedSelf_Move == 0 and ally.assistTargetedOther_Move == 0: total_jump += 1

                    player.chargeSpecial(total_jump)
                    ally.chargeSpecial(total_jump)

                    self.refresh_unit_visuals_obj(player)
                    self.refresh_unit_visuals_obj(ally)

                # Geirdriful (Refine Eff) - B!Chrom
                if "I WILL PIERCE THE SNAKE" in playerSkills:
                    player.inflictStatus(Status.NullBonuses)
                    player.inflictStatus(Status.DamageReductionPierce50)

                if "I WILL PIERCE THE SNAKE" in allySkills:
                    ally.inflictStatus(Status.NullBonuses)
                    ally.inflictStatus(Status.DamageReductionPierce50)

                # Gerbera Axe (Base) - V!Lucina
                if "vLucinaBoost" in playerSkills or "vLucinaBoost" in allySkills:
                    player.inflictStatus(Status.NullBonuses)
                    ally.inflictStatus(Status.NullBonuses)

                player.assistTargetedOther_Move += 1
                ally.assistTargetedSelf_Move += 1

            # Feint Skills
            elif player.assist.type == "Rally":
                valid_foes = []

                for x in [player, ally]:
                    foes = feh.foes_within_n_cardinal(x, 1)
                    for foe in foes:
                        if foe not in valid_foes:
                            valid_foes.append(foe)

                if "atkFeint" in playerSkills or "atkFeint" in allySkills:
                    stat_debuff = max(playerSkills.get("atkFeint", 0), allySkills.get("atkFeint", 0))

                    for foe in valid_foes:
                        foe.inflictStat(ATK, -stat_debuff)

                if "spdFeint" in playerSkills or "spdFeint" in allySkills:
                    stat_debuff = max(playerSkills.get("spdFeint", 0), allySkills.get("spdFeint", 0))

                    for foe in valid_foes:
                        foe.inflictStat(SPD, -stat_debuff)

                if "defFeint" in playerSkills or "defFeint" in allySkills:
                    stat_debuff = max(playerSkills.get("defFeint", 0), allySkills.get("defFeint", 0))

                    for foe in valid_foes:
                        foe.inflictStat(DEF, -stat_debuff)

                if "resFeint" in playerSkills or "resFeint" in allySkills:
                    stat_debuff = max(playerSkills.get("resFeint", 0), allySkills.get("resFeint", 0))

                    for foe in valid_foes:
                        foe.inflictStat(RES, -stat_debuff)

                # Ruse skills
                skill_stat_map = {
                    "atkSpdRuse": [ATK, SPD],
                    "atkDefRuse": [ATK, DEF],
                    "atkResRuse": [ATK, RES],
                    "spdDefRuse": [SPD, DEF],
                    "spdResRuse": [SPD, RES],
                    "defResRuse": [DEF, RES],
                }

                for skill, stats in skill_stat_map.items():
                    if skill in playerSkills or skill in allySkills:
                        stat_debuff = max(playerSkills.get(skill, 0), allySkills.get(skill, 0))

                        for foe in valid_foes:
                            foe.inflictStatus(Status.Guard)
                            for stat in stats:
                                foe.inflictStat(stat, -stat_debuff)

                if "jolly!" in playerSkills:
                    player.inflictStat(ATK, 6)
                    player.inflictStat(SPD, 6)

                    if player.assistTargetedOther == 0:
                        galeforce_triggered = True

                if "annetteRally" in playerSkills and not(ally.wpnType in RANGED_WEAPONS and ally.move == 1):
                    ally.inflictStatus(Status.MobilityUp)

                if "annetteBoost" in playerSkills and not(ally.wpnType in RANGED_WEAPONS and ally.move == 1):
                    ally.inflictStatus(Status.MobilityUp)

                    if player.assistTargetedOther == 0:
                        galeforce_triggered = True

                if "astridRally" in playerSkills:
                    ally.inflictStatus(Status.BonusDoubler)

                    if not(ally.wpnType in RANGED_WEAPONS and ally.move == 1):
                        ally.inflictStatus(Status.MobilityUp)

                player.assistTargetedOther_Rally += 1
                ally.assistTargetedSelf_Rally += 1

            else:
                player.assistTargetedOther_Other += 1
                ally.assistTargetedSelf_Other += 1

            # Keep your turn after using assist

            # Future Vision - L!Lucina
            if ("selfAssistRefresh" in player.assist.effects or "lucinaRefresh" in player.assist.effects):
                galeforce_triggered = True

            # To Change Fate! - L!Chrom
            if "chromRefresh" in player.assist.effects and player.assistTargetedOther == 0:
                player.inflictStat(ATK, 6)
                player.inflictStatus(Status.Isolation)

                if player.pair_up_obj:
                    player.pair_up_obj.inflictStat(ATK, 6)
                    player.pair_up_obj.inflictStatus(Status.Isolation)

                if player.assistTargetedOther == 0:
                    galeforce_triggered = True

            if "chromRefreshII" in player.assist.effects:
                player.inflictStat(ATK, 6)
                player.inflictStat(DEF, 6)
                player.inflictStatus(Status.BonusDoubler)
                player.inflictStatus(Status.Isolation)

                if player.pair_up_obj:
                    player.pair_up_obj.inflictStat(ATK, 6)
                    player.pair_up_obj.inflictStat(DEF, 6)
                    player.pair_up_obj.inflictStatus(Status.BonusDoubler)
                    player.pair_up_obj.inflictStatus(Status.Isolation)

                if player.assistTargetedOther == 0:
                    galeforce_triggered = True

            # A Fate Changed! - B!Chrom
            if "aFateChanged" in player.assist.effects:
                for status in ally.statusPos:
                    if status not in player.statusPos:
                        player.inflictStatus(status)

                        if player.pair_up_obj and status not in player.pair_up_obj.statusPos:
                            player.pair_up_obj.inflictStatus(status)

                if Status.Panic not in ally.statusNeg:
                    for i in range(1, 5):
                        player.buffs[i] = max(player.buffs[i], ally.buffs[i])

                        if player.pair_up_obj:
                            player.pair_up_obj.buffs[i] = max(player.pair_up_obj.buffs[i], ally.buffs[i])

                if player.assistTargetedOther == 0:
                    galeforce_triggered = True

                    player.inflictStatus(Status.Isolation)

                    if player.pair_up_obj: player.pair_up_obj.inflictStatus(Status.Isolation)

            # Dragon's Dance - L!Ninian
            if "dragonsDance" in player.assist.effects and self.turn_info[0] >= 2 and "disableAssist" not in player.statusOther:
                player.inflictStat(ATK, 6)
                player.inflictStat(SPD, 6)
                player.inflictStatus(Status.Isolation)
                player.statusOther["disableAssist"] = 3

                if player.pair_up_obj:
                    player.pair_up_obj.inflictStat(ATK, 6)
                    player.pair_up_obj.inflictStat(SPD, 6)
                    player.pair_up_obj.inflictStatus(Status.Isolation)

                galeforce_triggered = True


            # Trap triggered after assist skill usage
            player_struct = player.tile.structure_on
            ally_struct = ally.tile.structure_on

            if player_struct and "Trap" in player_struct.name and player.side == PLAYER and player_struct.health != 0:
                player_struct.health = 0
                self.refresh_walls()

                if "False" not in player_struct.name:
                    if player_struct.name == "Bolt Trap":
                        disarm_lvl = player.get("disarmTrap", 0)

                        if final_dest_struct.level > disarm_lvl:
                            for trap_unit in player.tile.unitsWithinNSpaces(3):
                                trap_damage = final_dest_struct.level * 10

                                if Status.EnGarde in trap_unit.statusPos:
                                    trap_damage = 0

                                trap_unit.HPcur = max(1, trap_unit.HPcur - trap_damage)
                                self.animate_damage_popup(trap_damage, trap_unit.tile.tileNum)

                                self.set_hp_visual(trap_unit, trap_unit.HPcur)

                    elif player_struct.name == "Heavy Trap":
                        disarm_lvl = player.get("disarmTrap", 0)

                        if final_dest_struct.level > disarm_lvl:
                            for trap_unit in player.tile.unitsWithinNSpaces(2):
                                if trap_unit.HPcur <= get_tower_hp_threshold(player_struct.level):
                                    trap_unit.inflictStatus(Status.Gravity)

                    elif player_struct.name == "Hex Trap" and player.HPcur <= get_tower_hp_threshold(player_struct.level):
                        hex_trap_triggered_after_action = True

            if ally_struct and "Trap" in ally_struct.name and ally.side == PLAYER and ally_struct.health != 0:
                ally_struct.health = 0
                self.refresh_walls()

                if "False" not in ally_struct.name:
                    if ally_struct.name == "Bolt Trap":
                        disarm_lvl = ally.get("disarmTrap", 0)

                        if ally_struct.level > disarm_lvl:
                            for trap_unit in ally.tile.unitsWithinNSpaces(3):
                                trap_damage = ally_struct.level * 10

                                if Status.EnGarde in trap_unit.statusPos:
                                    trap_damage = 0

                                trap_unit.HPcur = max(1, trap_unit.HPcur - trap_damage)
                                self.animate_damage_popup(trap_damage, trap_unit.tile.tileNum)

                                self.set_hp_visual(trap_unit, trap_unit.HPcur)

                    elif ally_struct.name == "Heavy Trap":
                        disarm_lvl = ally.get("disarmTrap", 0)

                        if ally_struct.level > disarm_lvl:
                            for trap_unit in ally.tile.unitsWithinNSpaces(2):
                                if trap_unit.HPcur <= get_tower_hp_threshold(ally_struct.level):
                                    trap_unit.inflictStatus(Status.Gravity)

                    elif ally_struct.name == "Hex Trap" and ally.HPcur <= get_tower_hp_threshold(ally_struct.level):
                        if ally in self.units_to_move:
                            self.units_to_move.remove(ally)

                        set_unit_actability(ally)

            # Increment number of times an assist was used
            player.assistTargetedOther += 1
            ally.assistTargetedSelf += 1

            self.extras.clear_forecast_banner()

        # DESTROOOOOOOOOOOOOOOOYYYY!!!!!!!!!!!!!!!!!
        elif is_targeting_object and not is_targeting_hero and is_targeting_struct and release_struct.health > 0 and not trap_triggered:
            action = BREAK

            # Break selected wall
            release_struct.health -= 1

            # Refresh all walls
            self.refresh_walls()
            self.refresh_divine_veins()

            self.extras.clear_forecast_banner()

        # DO NOTHIIIIIIIIIIIIIIING!!!!!
        else:
            self.extras.clear_forecast_banner()
            action = MOVE

        # If any action was taken, manage those things here
        if action != INVALID:

            # Check if any sort of button can be used after action
            if cur_unit.HPcur != 0:
                if S == PLAYER and cur_unit.duo_skill and not self.all_cohorts[item_index]:
                    if cur_unit.duo_skill.type == 'duo':
                        self.after(finish_time, partial(self.button_frame.action_button.config, text='Duo\nSkill'))
                    else:
                        self.after(finish_time, partial(self.button_frame.action_button.config, text='Harmonic\nSkill'))

                    duos_hindr_present = self.get_struct_by_name("Duo's Hindrance") and self.get_struct_by_name("Duo's Hindrance").level + 2 >= self.turn_info[0] and self.get_struct_by_name("Duo's Hindrance").health != 0
                    duo_on_foe_team = any(foe for foe in self.current_units[ENEMY] if foe.duo_skill and foe.HPcur != 0)

                    if self.turn_info[1] == PLAYER and cur_unit.duo_cooldown == 0 and feh.can_use_duo_skill(cur_unit, self.units_to_move) and not self.swap_mode and not(duos_hindr_present and duo_on_foe_team):
                        self.after(finish_time, partial(self.button_frame.action_button.config, state='normal', command=partial(self.use_duo_skill, cur_unit)))
                    else:
                        self.after(finish_time, partial(self.button_frame.action_button.config, state='disabled'))

                # Enable Pair Up Button
                elif S == PLAYER and self.all_cohorts[item_index]:
                    self.button_frame.action_button.config(text='Swap\nCohort')
                    if self.turn_info[1] == PLAYER and feh.can_be_on_tile(cur_unit.tile, self.all_cohorts[item_index].move) and not self.swap_mode:
                        self.after(finish_time, partial(self.button_frame.action_button.config, state='normal', command=partial(self.switch_pairing, cur_unit)))
                    else:
                        self.after(finish_time, partial(self.button_frame.action_button.config, state='disabled'))
                else:
                    self.after(finish_time, partial(self.button_frame.action_button.config, state='disabled', text='Action\nButton'))

            # Clears debuffs if no action has occured, or
            if action != ATTACK and action != ASSIST:
                if not trap_triggered:
                    cur_unit.statusNeg = []

                    if Status.GrandStrategy not in cur_unit.statusPos:
                        cur_unit.debuffs = [0, 0, 0, 0, 0]

                    if cur_unit.pair_up_obj:
                        cur_unit.pair_up_obj.statusNeg = []

                        if Status.GrandStrategy not in cur_unit.pair_up_obj.statusPos:
                            cur_unit.pair_up_obj.debuffs = [0, 0, 0, 0, 0]

                self.unit_status.update_from_obj(cur_unit)

            if action == ASSIST:
                self.unit_status.update_from_obj(cur_unit)

            if action != MOVE and not galeforce_triggered and cur_unit.canto_ready and cur_unit.HPcur != 0 and not hex_trap_triggered_after_action:

                current_units = self.map.get_heroes_present_by_side()

                # Has unit used a warp movement?
                self.has_unit_warped = False
                for move in sdd['moves_obj_array']:
                    if move.destination == destination_tile and move.is_warp:
                        self.has_unit_warped = True

                canto_moves = feh.get_canto_moves(cur_unit, current_units[S], current_units[S-1], self.distance, self.spaces_allowed, action, self.turn_info[0], self.starting_tile, self.has_unit_warped)[2]

                # If there are any valid tiles to use Canto to, activate canto mode
                if canto_moves:
                    self.canto = cur_unit
                    cur_unit.canto_ready = False # Canto officially used up

                    # Disable Pair Up during Canto
                    if cur_unit.side == PLAYER:
                        self.after(finish_time, partial(self.button_frame.action_button.config, state='disabled', text='Action\nButton'))
                        CreateToolTip(self.button_frame.action_button, text='')

                    # moving again with canto removes all debuffs, because sure why not
                    for foe in current_units[S-1]:
                        if "cantoControlW" in foe.getSkills() and cur_unit in feh.foes_within_n(foe, 4):
                            cur_unit.inflictStatus(Status.CantoControl)

                        if "cantoControl" in foe.getSkills() and cur_unit in feh.foes_within_n(foe, foe.getSkills()["cantoControl"]):
                            cur_unit.inflictStatus(Status.CantoControl)

                    # Check Canto Moves after Canto Control is given out
                    moves_obj_array = feh.get_canto_moves(cur_unit, current_units[S], current_units[S-1], self.distance, self.spaces_allowed, action, self.turn_info[0], self.starting_tile, self.has_unit_warped)[2]

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

                if self.units_to_move and cur_hero.HPcur != 0: #or any(x.pair_up_obj for x in self.map.get_heroes_present_by_side()[S]) or any(x.duo_skill for x in self.map.get_heroes_present_by_side()[S])) and cur_unit.HPcur != 0 :
                    self.after(finish_time, set_unit_actability, cur_unit)

            # Capture the mapstate
            mapstate = create_mapstate(self.map, self.units_to_move, self.turn_info[0], self.unit_reinf_points, self.enemy_defeated_count, self.first_duo_skill_used, self.indulgence_used)

            #if (self.units_to_move or any(x.pair_up_obj for x in self.map.get_heroes_present_by_side()[S]) or any(x.duo_skill for x in self.map.get_heroes_present_by_side()[S])):
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

        if not self.units_to_move: #and not any(x.pair_up_obj for x in self.map.get_heroes_present_by_side()[S]) and not any(x.duo_skill for x in self.map.get_heroes_present_by_side()[S]):
            if not self.animation:
                self.next_phase()

            else:
                self.after(finish_time, partial(self.button_frame.action_button.config, state='disabled', text='Action\nButton'))
                self.after(finish_time, self.next_phase)

        self.drag_data = None

        return

    def on_double_click(self, event):
        x_comp = event.x // self.TILE_SIZE
        y_comp = ((self.GAMEPLAY_WIDTH - event.y) // self.TILE_SIZE)
        selected_tile = x_comp + 6 * y_comp

        if not self.running:
            if selected_tile in self.unit_drag_points:
                self.unit_drag_points[selected_tile].hero = None
                self.refresh_units_prep()

                self.unit_status.clear()

            return

        cur_hero = self.map.tiles[selected_tile].hero_on

        if cur_hero is not None and not self.swap_mode:

            S = cur_hero.side

            if S == self.turn_info[1]:
                item_index = self.all_units[S].index(cur_hero)
                if cur_hero in self.units_to_move:
                    self.units_to_move.remove(cur_hero)

                    cur_hero.statusNeg = []
                    if Status.GrandStrategy not in cur_hero.statusPos: cur_hero.debuffs = [0, 0, 0, 0, 0]

                    if cur_hero.pair_up_obj:
                        cur_hero.pair_up_obj.statusNeg = []
                        if Status.GrandStrategy not in cur_hero.pair_up_obj.statusPos: cur_hero.pair_up_obj.debuffs = [0, 0, 0, 0, 0]

                    if cur_hero == self.canto:
                        self.canto = None

                        for blue_tile_id in self.canto_tile_imgs:
                            self.delete(blue_tile_id)
                        self.canto_tile_imgs.clear()

                    if cur_hero.transformed:
                        self.itemconfig(self.unit_sprites_trans[S][item_index], state='hidden')
                        self.itemconfig(self.unit_sprites_gs_trans[S][item_index], state='normal')
                    else:
                        self.itemconfig(self.unit_sprites[S][item_index], state='hidden')
                        self.itemconfig(self.unit_sprites_gs[S][item_index], state='normal')

                if not self.units_to_move:
                    self.button_frame.action_button.config(state='disabled')
                    self.next_phase()

                else:
                    mapstate = create_mapstate(self.map, self.units_to_move, self.turn_info[0], self.unit_reinf_points, self.enemy_defeated_count, self.first_duo_skill_used, self.indulgence_used)
                    self.map_states.append(mapstate)

        return

    def on_right_click(self, event):
        x_comp = event.x // self.TILE_SIZE
        y_comp = ((self.GAMEPLAY_WIDTH - event.y) // 90)
        selected_tile = x_comp + 6 * y_comp

        if not self.running and not self.drag_data:
            if selected_tile in self.unit_drag_points and self.unit_drag_points[selected_tile].hero and self.unit_drag_points[selected_tile].hero.epithet != "Generic":
                self.hero_listing.create_edit_popup_from_unit(self.unit_drag_points[selected_tile].hero)
                self.hero_listing.creation_make_button.config(text="Save", command=partial(self.place_unit_object, event.x, event.y))
                self.hero_listing.creation_build_field.forget()
                self.hero_listing.creation_make_text.forget()

    def setup_with_file(self, json_path):
        with open(json_path, encoding="utf-8") as read_file: json_data = json.load(read_file)

        # Specify map terrain, structures, and starting positions with JSON file.
        self.map.define_map(json_data)

        for tile in self.map.tiles:
            if tile.structure_on and tile.structure_on.struct_type != 0:
                self.ar_structs.append(tile.structure_on)
                self.ar_struct_tiles.append(tile)

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
        self.unit_reinf_points.clear()

        for starting_space in self.map.player_start_spaces:
            cur_tile = self.create_image(0, 0, image=self.move_tile_photos[0])
            self.starting_tile_photos.append(cur_tile)
            self.move_to_tile(cur_tile, starting_space)

            self.unit_drag_points[starting_space] = _DragPoint(tile_num=starting_space, modifiable=True, side=PLAYER)

        if self.game_mode != hero.GameMode.AetherRaids:
            for starting_space in self.map.enemy_start_spaces:
                cur_tile = self.create_image(0, 0, image=self.move_tile_photos[3])
                self.starting_tile_photos.append(cur_tile)
                self.move_to_tile(cur_tile, starting_space)

                self.unit_drag_points[starting_space] = _DragPoint(tile_num=starting_space, modifiable=True, side=ENEMY)

        else:
            for starting_space in range(36, 48):
                cur_tile = self.create_image(0, 0, image=self.move_tile_photos[3])
                self.starting_tile_photos.append(cur_tile)
                self.move_to_tile(cur_tile, starting_space)

                if self.map.tiles[starting_space].structure_on:
                    self.itemconfig(cur_tile, state='hidden')

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

            if "sseal" in json_data["enemyData"][i]:
                curSSeal = makeSeal(json_data["enemyData"][i]["sseal"])
                curEnemy.set_skill(curSSeal, SSEAL)

            if "alt_stats" in json_data["enemyData"][i]:
                curEnemy.visible_stats = json_data["enemyData"][i]["alt_stats"]
                j = 0
                while j < 5:
                    curEnemy.visible_stats[j] += curEnemy.skill_stat_mods[j]
                    curEnemy.visible_stats[j] = max(min(curEnemy.visible_stats[j], 99), 0)
                    j += 1

                curEnemy.HPcur = curEnemy.visible_stats[HP]

            if i < len(self.map.enemy_start_spaces):
                self.unit_drag_points[self.map.enemy_start_spaces[i]].hero = curEnemy
            else:
                reinf_data = json_data["enemyData"][i]['reinf_info']

                tile = reinf_data.get('tile', 0)
                turn = reinf_data.get('turn', 1)
                amount = reinf_data.get('amount', 1)
                target_name = reinf_data.get('targetName', None)
                target_count = reinf_data.get('targetCount', -1)

                reinf_point = _ReinforcementPoint(tile, turn, amount, target_name, target_count)
                reinf_point.hero = curEnemy

                self.unit_reinf_points[tile] = reinf_point

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

    # AVOID USING
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

    # Move a unit's visuals to a given tile
    def move_visuals_to_tile_obj(self, unit, tile_int):
        side = unit.side
        is_cohort = unit in self.all_cohorts

        if not is_cohort:
            unit_index = self.all_units[side].index(unit)
        else:
            unit_index = self.all_cohorts.index(unit)

        if not is_cohort:
            self.move_to_tile(self.unit_sprites[side][unit_index], tile_int)
            self.move_to_tile(self.unit_sprites_gs[side][unit_index], tile_int)
            self.move_to_tile(self.unit_sprites_trans[side][unit_index], tile_int)
            self.move_to_tile(self.unit_sprites_gs_trans[side][unit_index], tile_int)
            self.move_to_tile_wp(self.unit_weapon_icon_sprites[side][unit_index], tile_int)
            self.move_to_tile_sp(self.unit_sp_count_labels[side][unit_index], tile_int)
            self.move_to_tile_hp(self.unit_hp_count_labels[side][unit_index], tile_int)
            self.move_to_tile_bar(self.unit_hp_bars_bg[side][unit_index], tile_int)
            self.move_to_tile_bar(self.unit_hp_bars_fg[side][unit_index], tile_int)
        else:
            self.move_to_tile(self.cohort_sprites[unit_index], tile_int)
            self.move_to_tile(self.cohort_sprites_gs[unit_index], tile_int)
            self.move_to_tile(self.cohort_sprites_trans[unit_index], tile_int)
            self.move_to_tile(self.cohort_sprites_gs_trans[unit_index], tile_int)
            self.move_to_tile_wp(self.cohort_weapon_icon_sprites[unit_index], tile_int)
            self.move_to_tile_sp(self.unit_sp_count_labels[side][unit_index], tile_int)
            self.move_to_tile_hp(self.unit_hp_count_labels[side][unit_index], tile_int)
            self.move_to_tile_bar(self.unit_hp_bars_bg[side][unit_index], tile_int)
            self.move_to_tile_bar(self.unit_hp_bars_fg[side][unit_index], tile_int)

    # Sets a unit's health to a given value
    def set_hp_visual(self, unit, cur_HP):
        S = unit.side

        is_cohort = unit in self.all_cohorts

        if not is_cohort:
            unit_index = self.all_units[S].index(unit)
        else:
            unit_index = self.all_cohorts.index(unit)

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

    # Sets unit's HP/Special Count to what they are currently, but cooler
    def refresh_unit_visuals_obj(self, unit):
        side = unit.side

        if unit in self.all_units[side]:
            index = self.all_units[side].index(unit)
        else:
            index = self.all_cohorts.index(unit)

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
    # Unit must be alive
    def update_unit_graphics(self, unit):
        S = unit.side
        is_cohort = unit in self.all_cohorts

        # Get leader's weapon sprite icon
        if not is_cohort:
            unit_index = self.all_units[S].index(unit)
            leader_weapon_sprite = self.unit_weapon_icon_sprites[S][unit_index]
        else:
            unit_index = self.all_cohorts.index(unit)
            leader_weapon_sprite = self.cohort_weapon_icon_sprites[unit_index]

        cur_tile_Obj = unit.tile

        # If unit is currently on map
        if cur_tile_Obj:
            cur_tile = cur_tile_Obj.tileNum

            self.move_visuals_to_tile_obj(unit, cur_tile)

            self.itemconfig(leader_weapon_sprite, state='normal')

            if unit.side == PLAYER:
                if not is_cohort and self.cohort_weapon_icon_sprites[unit_index]:
                    self.itemconfig(self.cohort_weapon_icon_sprites[unit_index], state='hidden')
                elif is_cohort:
                    self.itemconfig(self.unit_weapon_icon_sprites[unit.side][unit_index], state='hidden')

            self.itemconfig(self.unit_hp_count_labels[S][unit_index], state='normal')
            self.itemconfig(self.unit_sp_count_labels[S][unit_index], state='normal')

            self.itemconfig(self.unit_hp_bars_fg[S][unit_index], state='normal')
            self.itemconfig(self.unit_hp_bars_bg[S][unit_index], state='normal')

            # I don't know why, when hiding the HP bars, they are moved really far away
            # These lines place them back to the right place
            self.move_to_tile_bar(self.unit_hp_bars_fg[S][unit_index], cur_tile)
            self.move_to_tile_bar(self.unit_hp_bars_bg[S][unit_index], cur_tile)

        else:
            self.itemconfig(leader_weapon_sprite, state='hidden')
            self.itemconfig(self.unit_hp_count_labels[S][unit_index], state='hidden')
            self.itemconfig(self.unit_sp_count_labels[S][unit_index], state='hidden')

            self.itemconfig(self.unit_hp_bars_fg[S][unit_index], state='hidden')
            self.itemconfig(self.unit_hp_bars_bg[S][unit_index], state='hidden')

        # Set special count to its correct value
        if unit.specialCount != -1:
            self.set_text_val(self.unit_sp_count_labels[S][unit_index], unit.specialCount)

        # Set HP bar and count to its correct value
        self.set_hp_visual(unit, unit.HPcur)

        if not is_cohort:
            if unit.transformed:
                if unit in self.units_to_move or unit.side != self.turn_info[1]:
                    self.itemconfig(self.unit_sprites[S][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_gs[S][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_trans[S][unit_index], state='normal')
                    self.itemconfig(self.unit_sprites_gs_trans[S][unit_index], state='hidden')

                else:
                    self.itemconfig(self.unit_sprites[S][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_gs[S][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_trans[S][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_gs_trans[S][unit_index], state='normal')

            else:
                if unit in self.units_to_move or unit.side != self.turn_info[1]:
                    self.itemconfig(self.unit_sprites[S][unit_index], state='normal')
                    self.itemconfig(self.unit_sprites_gs[S][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_trans[S][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_gs_trans[S][unit_index], state='hidden')

                else:
                    self.itemconfig(self.unit_sprites[S][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_gs[S][unit_index], state='normal')
                    self.itemconfig(self.unit_sprites_trans[S][unit_index], state='hidden')
                    self.itemconfig(self.unit_sprites_gs_trans[S][unit_index], state='hidden')

            # Hide cohort sprites if player side only
            if unit.side == PLAYER:
                self.itemconfig(self.cohort_sprites[unit_index], state='hidden')
                self.itemconfig(self.cohort_sprites_gs[unit_index], state='hidden')
                self.itemconfig(self.cohort_sprites_trans[unit_index], state='hidden')
                self.itemconfig(self.cohort_sprites_gs_trans[unit_index], state='hidden')
        else:
            if unit.transformed:
                if unit in self.units_to_move or unit.side != self.turn_info[1]:

                    self.itemconfig(self.cohort_sprites[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_gs[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_trans[unit_index], state='normal')
                    self.itemconfig(self.cohort_sprites_gs_trans[unit_index], state='hidden')
                else:
                    self.itemconfig(self.cohort_sprites[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_gs[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_trans[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_gs_trans[unit_index], state='normal')
            else:
                if unit in self.units_to_move or unit.side != self.turn_info[1]:
                    self.itemconfig(self.cohort_sprites[unit_index], state='normal')
                    self.itemconfig(self.cohort_sprites_gs[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_trans[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_gs_trans[unit_index], state='hidden')
                else:
                    self.itemconfig(self.cohort_sprites[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_gs[unit_index], state='normal')
                    self.itemconfig(self.cohort_sprites_trans[unit_index], state='hidden')
                    self.itemconfig(self.cohort_sprites_gs_trans[unit_index], state='hidden')

            self.itemconfig(self.unit_sprites[S][unit_index], state='hidden')
            self.itemconfig(self.unit_sprites_gs[S][unit_index], state='hidden')
            self.itemconfig(self.unit_sprites_trans[S][unit_index], state='hidden')
            self.itemconfig(self.unit_sprites_gs_trans[S][unit_index], state='hidden')

    def refresh_walls(self):
        self.wall_photos.clear()
        self.wall_sprites.clear()

        self.ar_structs.clear()
        self.ar_struct_tiles.clear()
        self.ar_struct_sprites.clear()

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

                cur_wall = cur_wall.resize((90, 90))
                cur_photo = ImageTk.PhotoImage(cur_wall)

                img = self.create_image(90, 90, anchor=tk.CENTER, image=cur_photo)

                self.wall_photos.append(cur_photo)
                self.wall_sprites.append(img)

                self.move_to_tile(img, tile.tileNum)

            elif tile.structure_on and tile.structure_on.struct_type != 0:
                struct = tile.structure_on
                self.ar_structs.append(struct)
                self.ar_struct_tiles.append(tile)

                SIDE_NONEXCLUSIVE_AR_STRUCTS = ["Fortress", "Bolt Tower", "Tactics Room", "Healing Tower", "Panic Manor", "Catapult", "Bright Shrine", "Dark Shrine", "Calling Circle"]

                if struct.struct_type == PLAYER + 1:
                    image_path = "CombatSprites/AR Structures/" + struct.name.replace(" ", "_").replace("'", "") + ".png"

                else:
                    if struct.name in SIDE_NONEXCLUSIVE_AR_STRUCTS or "School" in struct.name:
                        image_path = "CombatSprites/AR Structures/" + struct.name.replace(" ", "_") + "_Enemy.png"
                    else:
                        image_path = "CombatSprites/AR Structures/" + struct.name.replace(" ", "_").replace("'", "").replace("False_", "") + ".png"

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

                self.ar_struct_sprites.append(struct_sprite)

                if self.unit_sprites[PLAYER]:
                    for sprite in self.wall_sprites:
                        self.tag_lower(sprite, self.unit_sprites[PLAYER][0])

                if self.unit_sprites[ENEMY]:
                    for sprite in self.wall_sprites:
                        self.tag_lower(sprite, self.unit_sprites[ENEMY][0])

    def refresh_divine_veins(self):
        veins = ["Stone", "Flame", "Green", "Haze", "Water", "Ice"]
        offsets = [(1, -6), (-15, -26), (-7, -3), (-4, -18), (-5, -5), (-4, 1)]

        # Initialize Divine Vein photos

        if not self.divine_vein_photos:
            for vein in veins:
                cur_vein_img = Image.open("CombatSprites/Vein_" + vein + "_Player.png")
                cur_vein_photo = ImageTk.PhotoImage(cur_vein_img)
                self.divine_vein_photos.append(cur_vein_photo)

            for vein in veins:
                cur_vein_img = Image.open("CombatSprites/Vein_" + vein + "_Enemy.png")
                cur_vein_photo = ImageTk.PhotoImage(cur_vein_img)
                self.divine_vein_photos.append(cur_vein_photo)


        for sprite in self.divine_vein_sprites:
            self.delete(sprite)

        self.divine_vein_sprites.clear()

        # Create photos
        for tile in self.map.tiles:
            if tile.divine_vein != 0 and tile.divine_vein_turn >= 1:

                local_vein_type = tile.divine_vein - 1

                enemy_offset = 0 if tile.divine_vein_side == PLAYER else len(self.divine_vein_photos) // 2

                vein_photo = self.divine_vein_photos[local_vein_type + enemy_offset]

                visual_x = tile.x_coord * 90
                visual_y = 630 - (90 * tile.y_coord)

                vein_sprite = self.create_image(visual_x + offsets[local_vein_type][0], visual_y + offsets[local_vein_type][1], anchor='nw', image=vein_photo)
                vein_text_shadow = self.create_text(visual_x + 45, visual_y + 45, anchor='center', text=str(tile.divine_vein_turn), font=("Helvetica", 25, 'bold'), fill="black")
                vein_text = self.create_text(visual_x - 2 + 45, visual_y - 3 + 45, anchor='center', text=str(tile.divine_vein_turn), font=("Helvetica", 25, 'bold'), fill="LightCyan2")

                # Place behind players (if any)
                if self.unit_sprites[PLAYER] + self.unit_sprites[ENEMY]:
                    self.tag_lower(vein_sprite, min(self.unit_sprites[PLAYER] + self.unit_sprites[ENEMY]))
                    self.tag_lower(vein_text_shadow, min(self.unit_sprites[PLAYER] + self.unit_sprites[ENEMY]))
                    self.tag_lower(vein_text, min(self.unit_sprites[PLAYER] + self.unit_sprites[ENEMY]))

                # Place above walls (if any)
                if self.wall_sprites + self.ar_struct_sprites:
                    self.tag_raise(vein_sprite, max(self.wall_sprites + self.ar_struct_sprites))

                # Layer divine vein info of itself correctly
                self.tag_raise(vein_text_shadow, vein_sprite)
                self.tag_raise(vein_text, vein_text_shadow)

                # Store sprites
                self.divine_vein_sprites.append(vein_sprite)
                self.divine_vein_sprites.append(vein_text_shadow)
                self.divine_vein_sprites.append(vein_text)


    # Refresh unit graphics and objects while in preparation mode
    def refresh_units_prep(self):
        self.all_units = [[], []]
        self.current_units = [[], []]

        self.drag_point_units = [[], []]
        self.reinf_point_units = [[], []]

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

        self.cohort_photos = []
        self.cohort_sprites = []

        self.cohort_photos_gs = []
        self.cohort_sprites_gs = []

        self.cohort_photos_trans = []
        self.cohort_sprites_trans = []

        self.cohort_photos_gs_trans = []
        self.cohort_sprites_gs_trans = []

        self.cohort_weapon_icon_photos = []
        self.cohort_weapon_icon_sprites = []

        i = 0
        j = 0
        for drag_point in list(self.unit_drag_points.values()) + list(self.unit_reinf_points.values()):
            if drag_point.hero:

                unit = deepcopy(drag_point.hero)
                unit.side = drag_point.side

                S = unit.side

                self.all_units[S].append(unit)

                if drag_point in self.unit_drag_points.values():
                    self.drag_point_units[S].append(drag_point.hero)
                else:
                    self.reinf_point_units[S].append(unit)

                respString = "-R" if unit.resp else ""
                cur_image = Image.open("TestSprites/" + unit.intName + respString + ".png")
                if S == ENEMY: cur_image = cur_image.transpose(Image.FLIP_LEFT_RIGHT)
                resized_image = cur_image.resize((int(cur_image.width / 2.1), int(cur_image.height / 2.1)))
                cur_photo = ImageTk.PhotoImage(resized_image)

                self.unit_photos[S].append(cur_photo)

                grayscale_image = resized_image.convert("L")
                transparent_image = Image.new("RGBA", resized_image.size, (0, 0, 0, 0))
                transparent_image.paste(grayscale_image, (0, 0), mask=resized_image.split()[3])
                grayscale_photo = ImageTk.PhotoImage(transparent_image)

                self.unit_photos_gs[S].append(grayscale_photo)

                if unit.wpnType in hero.BEAST_WEAPONS:
                    cur_image_tr = Image.open("TestSprites/" + unit.intName + "-Tr" + ".png")
                    if S == ENEMY: cur_image_tr = cur_image_tr.transpose(Image.FLIP_LEFT_RIGHT)
                    resized_image_tr = cur_image_tr.resize((int(cur_image_tr.width / 2.1), int(cur_image_tr.height / 2.1)))
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
                if drag_point in self.unit_reinf_points.values():self.itemconfig(item_id, state='hidden')
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
                if drag_point in self.unit_reinf_points.values(): self.itemconfig(weapon_id, state='hidden')
                self.move_to_tile_wp(weapon_id, drag_point.tile)
                self.unit_weapon_icon_sprites[S].append(weapon_id)

                # Special count
                sp_count_string = str(int(unit.specialCount))

                if unit.specialCount == -1:
                    sp_count_string = ""

                special_label = self.create_text(200, 100 * (2 + i), text=sp_count_string, fill="#e300e3", font=("Helvetica", 19, 'bold'), anchor='center', tags=tag)
                if drag_point in self.unit_reinf_points.values(): self.itemconfig(special_label, state='hidden')
                self.move_to_tile_sp(special_label, drag_point.tile)
                self.unit_sp_count_labels[S].append(special_label)

                if unit.side == PLAYER:
                    side_color = "#5af2db"
                else:
                    side_color = "#f52d22"

                hp_string = unit.HPcur
                hp_label = self.create_text(200, 100 * (2 + i), text=hp_string, fill=side_color, font=("Helvetica", 16, 'bold'), anchor='center', tags=tag)
                if drag_point in self.unit_reinf_points.values(): self.itemconfig(hp_label, state='hidden')
                self.move_to_tile_hp(hp_label, drag_point.tile)
                self.unit_hp_count_labels[S].append(hp_label)

                hp_bar_bg = self.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill='black', width=0, tags=tag)
                if drag_point in self.unit_reinf_points.values(): self.itemconfig(hp_bar_bg, state='hidden')
                self.move_to_tile_bar(hp_bar_bg, drag_point.tile)
                self.unit_hp_bars_bg[S].append(hp_bar_bg)

                hp_bar_fg = self.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill=side_color, width=0, tags=tag)
                if drag_point in self.unit_reinf_points.values(): self.itemconfig(hp_bar_fg, state='hidden')
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

        self.extras.setup_tabs(self.unit_drag_points, None, self.game_mode, self.running, self.get_struct_levels())

        for tile in self.map.tiles:
            tile.divine_vein = 0

        self.refresh_divine_veins()

    # Generate sprites for cohort units, if any
    def set_cohort_sprites(self):
        self.cohort_photos = []
        self.cohort_sprites = []

        self.cohort_photos_gs = []
        self.cohort_sprites_gs = []

        self.cohort_photos_trans = []
        self.cohort_sprites_trans = []

        self.cohort_photos_gs_trans = []
        self.cohort_sprites_gs_trans = []

        self.cohort_weapon_icon_photos = []
        self.cohort_weapon_icon_sprites = []

        i = 0
        for cohort in self.all_cohorts:
            if cohort:
                S = cohort.side

                leader = self.all_units[PLAYER][i]
                leader_tag = self.unit_tags[PLAYER][i]

                respString = "-R" if cohort.resp else ""
                cur_image = Image.open("TestSprites/" + cohort.intName + respString + ".png")
                resized_image = cur_image.resize((int(cur_image.width / 2.1), int(cur_image.height / 2.1)))
                cur_photo = ImageTk.PhotoImage(resized_image)

                self.cohort_photos.append(cur_photo)

                grayscale_image = resized_image.convert("L")
                transparent_image = Image.new("RGBA", resized_image.size, (0, 0, 0, 0))
                transparent_image.paste(grayscale_image, (0, 0), mask=resized_image.split()[3])
                grayscale_photo = ImageTk.PhotoImage(transparent_image)

                self.cohort_photos_gs.append(grayscale_photo)

                if cohort.wpnType in hero.BEAST_WEAPONS:
                    cur_image_tr = Image.open("TestSprites/" + cohort.intName + "-Tr" + ".png")
                    resized_image_tr = cur_image_tr.resize((int(cur_image_tr.width / 2.1), int(cur_image_tr.height / 2.1)))
                    cur_photo_tr = ImageTk.PhotoImage(resized_image_tr)

                    self.cohort_photos_trans.append(cur_photo_tr)

                    grayscale_image_tr = resized_image_tr.convert("L")
                    transparent_image_tr = Image.new("RGBA", resized_image_tr.size, (0, 0, 0, 0))
                    transparent_image_tr.paste(grayscale_image_tr, (0, 0), mask=resized_image_tr.split()[3])
                    grayscale_photo_tr = ImageTk.PhotoImage(transparent_image_tr)

                    self.cohort_photos_gs_trans.append(grayscale_photo_tr)

                else:
                    cur_photo_tr = cur_photo
                    grayscale_photo_tr = grayscale_photo

                    self.cohort_photos_trans.append(cur_photo_tr)
                    self.cohort_photos_gs_trans.append(grayscale_photo_tr)

                # Sprites on canvas

                # Player sprite
                item_id = self.create_image(100 * i, 200, anchor='center', image=cur_photo, tags=leader_tag)
                self.move_to_tile(item_id, leader.tile.tileNum)
                self.cohort_sprites.append(item_id)

                # Player sprite - grayscale
                gs_item_id = self.create_image(100 * i, 200, anchor='center', image=grayscale_photo, tags=leader_tag)
                self.itemconfig(gs_item_id, state='hidden')
                self.move_to_tile(gs_item_id, leader.tile.tileNum)
                self.cohort_sprites_gs.append(gs_item_id)

                # Player sprite - transformed
                item_id_tr = self.create_image(100 * i, 200, anchor='center', image=cur_photo_tr, tags=leader_tag)
                self.itemconfig(item_id_tr, state='hidden')
                self.move_to_tile(item_id_tr, leader.tile.tileNum)
                self.cohort_sprites_trans.append(item_id_tr)

                # Player sprite - grayscale & transformed
                gs_item_id_tr = self.create_image(100 * i, 200, anchor='center', image=grayscale_photo_tr, tags=leader_tag)
                self.itemconfig(gs_item_id_tr, state='hidden')
                self.move_to_tile(gs_item_id_tr, leader.tile.tileNum)
                self.cohort_sprites_gs_trans.append(gs_item_id_tr)


                # Weapon icon
                wpn_num = hero.weapons[cohort.wpnType][0]
                wp_photo = ImageTk.PhotoImage(make_weapon_sprite(wpn_num))
                self.cohort_weapon_icon_photos.append(wp_photo)

                weapon_id = self.create_image(160, 50, anchor=tk.NW, image=wp_photo, tags=leader_tag)
                self.move_to_tile_wp(weapon_id, leader.tile.tileNum)
                self.cohort_weapon_icon_sprites.append(weapon_id)

                # Hide everything
                self.itemconfig(item_id, state='hidden')
                self.itemconfig(weapon_id, state='hidden')

            else:
                self.cohort_photos.append(None)
                self.cohort_photos_gs.append(None)
                self.cohort_photos_trans.append(None)
                self.cohort_photos_gs_trans.append(None)

                self.cohort_sprites.append(None)
                self.cohort_sprites_gs.append(None)
                self.cohort_sprites_trans.append(None)
                self.cohort_sprites_gs_trans.append(None)

                self.cohort_weapon_icon_photos.append(None)
                self.cohort_weapon_icon_sprites.append(None)

            i += 1

    # Switch which unit is leading an a Pair Up
    def switch_pairing(self, leader):
        if self.animation:
            return

        tile = leader.tile
        cohort = leader.pair_up_obj

        # The Switch
        tile.hero_on = cohort
        cohort.tile = tile
        leader.tile = None

        # Update button to reflect who the leader is
        self.button_frame.action_button.config(state='normal', command=partial(self.switch_pairing, cohort))

        self.unit_status.update_from_obj(cohort)

        # Make cohort actionable
        if leader in self.units_to_move:
            self.units_to_move.remove(leader)
            self.units_to_move.append(cohort)

        self.update_unit_graphics(leader)
        self.update_unit_graphics(cohort)

    def use_duo_skill(self, unit):
        if self.animation: return

        # Set button states
        self.button_frame.action_button.config(state='disabled')

        self.button_frame.swap_spaces_button.config(state="disabled")
        self.button_frame.undo_button.config(state="normal")

        # Reset cooldown to max value
        unit.duo_cooldown = unit.duo_skill.skill_refresh

        # Mark this is the first time a duo skill has been used
        if not self.first_duo_skill_used:
            self.first_duo_skill_used = unit

        # Areas for which a duo skill can apply over
        unitAreas = {'one': [unit],
                     'within_1_spaces': unit.tile.unitsWithinNSpaces(1),
                     'within_2_spaces': unit.tile.unitsWithinNSpaces(2),
                     'within_3_spaces': unit.tile.unitsWithinNSpaces(2),
                     'within_4_spaces': unit.tile.unitsWithinNSpaces(4),
                     'nearest_self': feh.nearest_allies_within_n(unit, 16) + feh.nearest_foes_within_n(unit, 16),
                     'within_3_columns': unit.tile.unitsWithinNCols(3),
                     'within_3_rows': unit.tile.unitsWithinNRows(3),
                     'within_1_rows_or_cols': feh.allies_within_n_cardinal(unit, 1) + feh.foes_within_n_cardinal(unit, 1),
                     'within_1_rows_or_cols_or_has_penalty': feh.allies_within_n_cardinal(unit, 1) + feh.foes_within_n_cardinal(unit, 1),
                     'within_3_rows_or_cols': feh.allies_within_n_cardinal(unit, 3) + feh.foes_within_n_cardinal(unit, 3),
                     'within_5_rows_and_cols': feh.allies_within_n_box(unit, 5) + feh.foes_within_n_box(unit, 5),
                     'within_5_rows_or_cols': feh.allies_within_n_cardinal(unit, 5) + feh.foes_within_n_cardinal(unit, 5),
                     'global': unit.tile.unitsWithinNSpaces(16)
                     }

        areaMethods = {'self': feh.get_self,
                       'allies': feh.allies_in_group,
                       'self_and_allies': feh.allies_plus_unit,
                       'self_and_allies_infantry': feh.allies_infantry_plus_unit,
                       'self_and_allies_flying': feh.allies_flying_plus_unit,
                       'self_and_allies_infantry_armored': feh.allies_infantry_armored_plus_unit,
                       'self_and_allies_flying_armored': feh.allies_flying_armored_plus_unit,
                       'self_and_same_game_allies': feh.allies_same_game_plus_unit,
                       'foes': feh.foes_in_group,
                       'foes_ranged_nonflier': feh.foes_in_group_ranged_nonflier
                       }

        # APPLY DUO SKILL EFFECTS
        for effect in unit.duo_skill.effects:

            # Call methods
            units_in_area = unitAreas[effect['area']]
            unit_determine_method = areaMethods[effect['targets']]
            targeted_units = unit_determine_method(unit, None, units_in_area)

            # Thief Nina
            if effect['area'] == "within_1_rows_or_cols_or_has_penalty":
                for x in self.map.get_heroes_present():
                    if x.hasPenalty() and x.isEnemyOf(unit) and x not in targeted_units:
                        targeted_units.append(x)

            if effect['effect'] == "clear_penalties":
                for x in targeted_units:
                    if Status.Schism in x.statusNeg:
                        if Status.Pathfinder in x.statusPos:
                            x.statusPos.remove(Status.Pathfinder)
                        if Status.TriangleAttack in x.statusPos:
                            x.statusPos.remove(Status.TriangleAttack)
                        if Status.DualStrike in x.statusPos:
                            x.statusPos.remove(Status.DualStrike)

                    x.statusNeg.clear()
                    x.debuffs = [0, 0, 0, 0, 0]

            if effect['effect'] == "clear_bonuses":
                for x in targeted_units:
                    x.statusPos.clear()

                    if Status.Panic not in x.statusNeg:
                        x.buffs = [0, 0, 0, 0, 0]

            if effect['effect'] == "buff_atk":
                for x in targeted_units:
                    x.inflictStat(ATK, effect['degree'])

            if effect['effect'] == "buff_spd":
                for x in targeted_units:
                    x.inflictStat(SPD, effect['degree'])

            if effect['effect'] == "buff_def":
                for x in targeted_units:
                    x.inflictStat(DEF, effect['degree'])

            if effect['effect'] == "buff_res":
                for x in targeted_units:
                    x.inflictStat(RES, effect['degree'])

            if effect['effect'] == "buff_omni":
                for x in targeted_units:
                    x.inflictStat(ATK, effect['degree'])
                    x.inflictStat(SPD, effect['degree'])
                    x.inflictStat(DEF, effect['degree'])
                    x.inflictStat(RES, effect['degree'])

            if effect['effect'] == "debuff_atk":
                for x in targeted_units:
                    x.inflictStat(ATK, -effect['degree'])

            if effect['effect'] == "debuff_spd":
                for x in targeted_units:
                    x.inflictStat(SPD, -effect['degree'])

            if effect['effect'] == "debuff_def":
                for x in targeted_units:
                    x.inflictStat(DEF, -effect['degree'])

            if effect['effect'] == "debuff_res":
                for x in targeted_units:
                    x.inflictStat(RES, -effect['degree'])

            if effect['effect'] == "debuff_omni":
                for x in targeted_units:
                    x.inflictStat(ATK, -effect['degree'])
                    x.inflictStat(SPD, -effect['degree'])
                    x.inflictStat(DEF, -effect['degree'])
                    x.inflictStat(RES, -effect['degree'])

            if effect['effect'] == "damage":
                for x in targeted_units:
                    if x.HPcur != 0:

                        # V!Líf
                        if effect['degree'] == -1:
                            ally_damage = 0

                            for ally in feh.allies_within_n(unit, 3):
                                ally_damage += ally.visible_stats[HP] - ally.HPcur

                            total_damage = min(trunc(0.50 * ally_damage), 30) + 10

                            x.HPcur = max(x.HPcur - total_damage, 1)
                            self.animate_damage_popup(total_damage, x.tile.tileNum)
                            self.refresh_unit_visuals_obj(x)

                        # Standard damage
                        else:
                            x.HPcur = max(x.HPcur - effect['degree'], 1)
                            self.animate_damage_popup(effect['degree'], x.tile.tileNum)
                            self.refresh_unit_visuals_obj(x)

            if effect['effect'] == "heal":
                for x in targeted_units:
                    if x.HPcur != 0 and Status.DeepWounds not in x.statusNeg:
                        x.HPcur = min(x.HPcur + effect['degree'], x.visible_stats[HP])
                        self.animate_heal_popup(effect['degree'], x.tile.tileNum)
                        self.refresh_unit_visuals_obj(x)

            if effect['effect'] == "status":
                for x in targeted_units:
                    x.inflictStatus(Status[effect['degree']])

            if effect['effect'] == "sp_charge":
                for x in targeted_units:
                    x.chargeSpecial(effect['degree'])
                    self.refresh_unit_visuals_obj(x)

            if effect['effect'] == "timesPulse":
                for x in targeted_units:
                    if x.specialCount == x.specialMax:
                        x.chargeSpecial(effect['degree'])
                        self.refresh_unit_visuals_obj(x)

            if effect['effect'] == "dance":
                highest_hp_allies = []

                for x in targeted_units:
                    if x not in self.units_to_move and x != unit:
                        if not highest_hp_allies or highest_hp_allies[0].HPcur == x.HPcur:
                            highest_hp_allies.append(x)
                        elif highest_hp_allies[0].HPcur < x.HPcur:
                            highest_hp_allies = [x]

                if len(highest_hp_allies) == 1:
                    self.units_to_move.append(highest_hp_allies[0])
                    self.update_unit_graphics(highest_hp_allies[0])

                    # NY!Peony
                    if effect['degree'] == 1:
                        highest_hp_allies[0].inflictStat(ATK, 3)
                        highest_hp_allies[0].inflictStat(SPD, 3)
                        highest_hp_allies[0].inflictStat(DEF, 3)
                        highest_hp_allies[0].inflictStat(RES, 3)
                        highest_hp_allies[0].inflictStatus(Status.Orders)

            if effect['effect'] == "galeforce":
                self.units_to_move.append(unit)
                self.update_unit_graphics(unit)

            if effect['effect'] == "repo":
                vertical_allies = list(set(feh.allies_within_n(unit, 1)) & set(unit.tile.unitsWithinNCols(1)))
                if len(vertical_allies) == 1:
                    ally = vertical_allies[0]

                    unit_tile_num = unit.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    # Where each unit is moving to
                    ally_final_position = feh.final_reposition_tile(unit_tile_num, ally_tile_num)

                    if feh.can_be_on_tile(self.map.tiles[ally_final_position], ally.move) and not self.map.tiles[ally_final_position].hero_on:
                        ally.tile.hero_on = None
                        ally.tile = self.map.tiles[ally_final_position]
                        self.map.tiles[ally_final_position].hero_on = ally
                        self.move_visuals_to_tile_obj(ally, ally_final_position)

                horizontal_allies = list(set(feh.allies_within_n(unit, 1)) & set(unit.tile.unitsWithinNRows(1)))
                if len(horizontal_allies) == 1:
                    ally = horizontal_allies[0]

                    unit_tile_num = unit.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    # Where each unit is moving to
                    ally_final_position = feh.final_reposition_tile(unit_tile_num, ally_tile_num)

                    if feh.can_be_on_tile(self.map.tiles[ally_final_position], ally.move) and not self.map.tiles[ally_final_position].hero_on:
                        ally.tile.hero_on = None
                        ally.tile = self.map.tiles[ally_final_position]
                        self.map.tiles[ally_final_position].hero_on = ally
                        self.move_visuals_to_tile_obj(ally, ally_final_position)

        # Add mapstate after skill is applied
        mapstate = create_mapstate(self.map, self.units_to_move, self.turn_info[0], self.unit_reinf_points, self.enemy_defeated_count, self.first_duo_skill_used, self.indulgence_used)
        self.map_states.append(mapstate)

        # Refresh unit display
        self.unit_status.update_from_obj(unit)

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

    def refresh_valid_ar_start_spaces(self):
        for starting_space in self.unit_drag_points:
            cur_tile = self.create_image(0, 0, image=self.move_tile_photos[2])
            self.starting_tile_photos.append(cur_tile)
            self.move_to_tile(cur_tile, starting_space)

            self.unit_drag_points[starting_space] = _DragPoint(tile_num=starting_space, modifiable=True, side=ENEMY)

    def toggle_valid_ar_start_spaces(self):
        if self.game_mode != hero.GameMode.AetherRaids: return

        if not self.tile_sprites:

            for tile in self.map.tiles:
                x_move = 90 * (tile.tileNum % 6)
                y_move = 90 * (7 - (tile.tileNum // 6))

                cur_dark_tile = self.create_rectangle_alpha(0, 0, 90, 90, fill='black', alpha=0.5, anchor=tk.CENTER)
                self.tag_lower(cur_dark_tile, 6)
                self.coords(cur_dark_tile, x_move, y_move)
                self.tile_sprites.append(cur_dark_tile)

        else:
            for tile in self.tile_sprites:
                self.delete(tile)
            self.tile_sprites.clear()

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

        if self.map.tiles[tile].structure_on: return

        if tile in self.unit_drag_points and self.unit_drag_points[tile].modifiable and not self.running:

            made_hero = make_hero_from_pd_row(row_data, self.unit_drag_points[tile].side)

            self.unit_drag_points[tile].hero = made_hero

            self.refresh_units_prep()

            made_hero.side = self.unit_drag_points[tile].side

            if made_hero.side == ENEMY:
                self.unit_status.update_from_obj(made_hero)

    def get_struct_levels(self):
        result_dict = dict(zip(ar_struct_names, [1] * len(ar_struct_names)))

        SIDE_NONEXCLUSIVE_AR_STRUCTS = ["Fortress", "Bolt Tower", "Tactics Room", "Healing Tower", "Panic Manor", "Catapult", "Bright Shrine", "Dark Shrine", "Calling Circle"]

        for tile in self.map.tiles:
            if tile.structure_on and tile.structure_on.struct_type != 0:
                if tile.structure_on.name in SIDE_NONEXCLUSIVE_AR_STRUCTS or "School" in tile.structure_on.name:
                    if tile.structure_on.struct_type == PLAYER + 1:
                        cur_struct_name = tile.structure_on.name + " (O)"
                    else:
                        cur_struct_name = tile.structure_on.name + " (D)"
                else:
                    cur_struct_name = tile.structure_on.name

                result_dict[cur_struct_name] = tile.structure_on.level

        return result_dict

    def get_struct_by_name(self, struct_id):
        for tile in self.map.tiles:
            if tile.structure_on:
                if tile.structure_on.name == struct_id:
                    return tile.structure_on
                elif tile.structure_on.name in struct_id:
                    if tile.structure_on.struct_type == PLAYER + 1 and "(O)" in struct_id:
                        return tile.structure_on
                    elif tile.structure_on.struct_type == ENEMY + 1 and "(D)" in struct_id:
                        return tile.structure_on

        return None

    def get_struct_tile_by_name(self, struct_id):
        for tile in self.map.tiles:
            if tile.structure_on:
                if tile.structure_on.name == struct_id:
                    return tile
                elif tile.structure_on.name in struct_id:
                    if tile.structure_on.struct_type == PLAYER + 1 and "(O)" in struct_id:
                        return tile
                    elif tile.structure_on.struct_type == ENEMY + 1 and "(D)" in struct_id:
                        return tile

        return None

    def update_struct_status(self, struct):
        if struct == self.unit_status.cur_hero:
            self.unit_status.update_from_struct(struct)

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
                    with open(str(path + "/" + entry), encoding="utf-8") as read_file: json_data = json.load(read_file)

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

        if len(self.bbox(item)) != 4: return

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
        terrain_image = terrain_image.resize((preview_width, preview_height))
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
                cur_wall = cur_wall.resize((30, 30))
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
                cur_wall = cur_wall.resize((30, 30))
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
                cur_wall = cur_wall.resize((30, 30))
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
        y = y + cy + self.widget.winfo_rooty() + self.widget.winfo_height() + 5

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


        self.weapon_label = tk.Label(self.skills_frame, bg="#cc3f52", text="Brazen Cat Fang (+Eff2)", anchor=tk.W, width=22, font=(None, inner_font))
        self.assist_label = tk.Label(self.skills_frame, bg="#5fa370", text="Bart Simpson", anchor=tk.W, width=22, font=(None, inner_font))
        self.special_label = tk.Label(self.skills_frame, bg="#9b5fa3", text="According to all", anchor=tk.W, width=22, font=(None, inner_font))
        self.askill_label = tk.Label(self.skills_frame, bg="#e6413e", text="known laws of", anchor=tk.W, width=22, font=(None, inner_font))
        self.bskill_label = tk.Label(self.skills_frame, bg="#4c83c7", text="aviation, there", anchor=tk.W, width=22, font=(None, inner_font))
        self.cskill_label = tk.Label(self.skills_frame, bg="#579c57", text="is no way a bee", anchor=tk.W, width=22, font=(None, inner_font))
        self.sseal_label = tk.Label(self.skills_frame, bg="#e0b30d", text="should be able", anchor=tk.W, width=22, font=(None, inner_font))
        self.xskill_label = tk.Label(self.skills_frame, bg="#86ad42", text="to fly.", anchor=tk.W, width=22, font=(None, inner_font))

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


        self.cur_hero = None

        self.just_name_label = tk.Label(self.inner_menu, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1)
        self.just_desc_label = tk.Label(self.inner_menu, font=(None, inner_font), bg=bg_color, fg=fg, highlightthickness=1, width=60, wraplength=520, justify="left")

    def update_from_obj(self, unit: hero.Hero):
        if not self.cur_hero:
            self.clear()

        self.just_name_label.forget()
        self.just_desc_label.forget()

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
        inf_icon = inf_icon.resize((icon_size, icon_size))
        move_icons.append(ImageTk.PhotoImage(inf_icon))
        cav_icon = status_pic.crop((462, 414, 518, 465))
        cav_icon = cav_icon.resize((icon_size, icon_size))
        move_icons.append(ImageTk.PhotoImage(cav_icon))
        fly_icon = status_pic.crop((518, 414, 572, 465))
        fly_icon = fly_icon.resize((icon_size, icon_size))
        move_icons.append(ImageTk.PhotoImage(fly_icon))
        arm_icon = status_pic.crop((406, 414, 462, 465))
        arm_icon = arm_icon.resize((icon_size, icon_size))
        move_icons.append(ImageTk.PhotoImage(arm_icon))

        weapon_icons = []
        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
            cur_icon = cur_icon.resize((icon_size, icon_size))
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

        pairup_info = '''This hero can use Pair Up in the following modes:
        -Story
        -Paralogues
        -Allegiance Battles
        -Røkkr Sieges
        -Mjölnir's Strike'''

        # Pair Up
        if unit.blessing and unit.blessing.element < 4 and unit.blessing.boostType == 2:
            pair_up_text = "Currently paired with build: " + (unit.pair_up if unit.pair_up else "None") + "\n\n"

            if unit.pair_up_obj:
                pair_up_text += "Pair Up hero: " + unit.pair_up_obj.name + ": " + unit.pair_up_obj.epithet + "\n\n"

            pair_up_text += pairup_info

            if unit.side == ENEMY:
                pair_up_text += '\n\nThis hero is an enemy unit; Pair Up settings will not be applied in battle.'

        elif unit.pair_up_obj:
                pair_up_text = "Pair Up hero: " + unit.pair_up_obj.name + ": " + unit.pair_up_obj.epithet
        else:
            pair_up_text = "This hero does not have access to Pair Up."

        CreateToolTip(self.pairup_label, text=pair_up_text, side="right")

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

                if unit.blessing.element < 4:
                    blessing_text += " blessing conferred:\n\nHP+3, "

                    if blessing.stat == hero.ATK:
                        blessing_text += "Atk+2"
                    elif blessing.stat == hero.SPD:
                        blessing_text += "Spd+3"
                    elif blessing.stat == hero.DEF:
                        blessing_text += "Def+4"
                    elif blessing.stat == hero.RES:
                        blessing_text += "Res+4"
                else:
                    blessing_text += " blessing conferred:\n\nHP+5, "

                    if blessing.stat == hero.ATK:
                        blessing_text += "Atk+3"
                    elif blessing.stat == hero.SPD:
                        blessing_text += "Spd+4"
                    elif blessing.stat == hero.DEF:
                        blessing_text += "Def+5"
                    elif blessing.stat == hero.RES:
                        blessing_text += "Res+5"

            elif blessing.boostType == 2:
                blessing_text += "During " + elements[element].capitalize() + " season, grants the following stat boosts to deployed allies with a " + elements[element].capitalize()

                if unit.blessing.element < 4:
                    blessing_text += " blessing conferred:\n\nHP+3\n\nEnables usage of Pair Up in select modes."

                else:
                    blessing_text += " blessing conferred:\n\nHP+5, "

                    if blessing.stat == hero.ATK:
                        blessing_text += "Atk+3"
                    elif blessing.stat == hero.SPD:
                        blessing_text += "Spd+4"
                    elif blessing.stat == hero.DEF:
                        blessing_text += "Def+5"
                    elif blessing.stat == hero.RES:
                        blessing_text += "Res+5"

            elif blessing.boostType == 3:
                blessing_text += "During " + elements[element].capitalize() + " season, grants the following stat boosts to deployed allies with a " + elements[element].capitalize()

                if unit.blessing.element < 4:
                    blessing_text += " blessing conferred:\n\nHP+3, "

                    if blessing.stat == hero.ATK:
                        blessing_text += "Atk+2"
                    elif blessing.stat == hero.SPD:
                        blessing_text += "Spd+3"
                    elif blessing.stat == hero.DEF:
                        blessing_text += "Def+4"
                    elif blessing.stat == hero.RES:
                        blessing_text += "Res+4"

                    blessing_text += "\n\nEnables usage of Pair Up in select modes."

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
        stats = unit.getStats()

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

            statuses_str += "Stat Boosts: "
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

            statuses_str += "Inverted Stat Bonuses: "
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

            statuses_str += "Stat Penalties: "
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

        if unit.statusOther:
            statuses_str += "--- OTHER STATUSES --- \n"

            for status in unit.statusOther.keys():
                if status == "disableWeapon":
                    statuses_str += "Weapon Disabled: " + str(unit.statusOther[status]) + '\n'
                if status == "disableAssist":
                    statuses_str += "Assist Disabled: " + str(unit.statusOther[status]) + '\n'
                if status == "disableSpecial":
                    statuses_str += "Special Disabled: " + str(unit.statusOther[status]) + '\n'
                if status == "disableASkill":
                    statuses_str += "A Skill Disabled: " + str(unit.statusOther[status]) + '\n'
                if status == "disableBSkill":
                    statuses_str += "B Skill Disabled: " + str(unit.statusOther[status]) + '\n'
                if status == "disableCSkill":
                    statuses_str += "C Skill Disabled: " + str(unit.statusOther[status]) + '\n'
                if status == "disableEmblem":
                    statuses_str += "Emblem Disabled: " + str(unit.statusOther[status]) + '\n'

            statuses_str += '\n'

        if statuses_str and statuses_str[-1] == '\n':
            statuses_str = statuses_str[:-1]

        CreateToolTip(self.status_label, statuses_str)

        # Skills
        wpn_str = "-"
        weapon_desc = ""

        wpn_txt_color = "black"
        refine_substrings = ("Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz", "Eff2", "Atk2", "Spd2", "Def2", "Res2", "Wra2", "Daz2")

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

            if unit.special.desc:
                special_desc = "Cooldown:" + str(unit.specialMax) + "\n" + unit.special.desc
            else:
                special_desc = ""

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

    def update_from_struct(self, struct):
        self.clear()

        # If struct is a regular wall, do nothing
        if struct.struct_type == 0: return

        if not self.cur_hero:
            self.clear()

        self.cur_hero = struct

        banner_color = "#18284f" if struct.struct_type == PLAYER + 1 else "#541616"

        self.inner_menu.config(bg=banner_color)
        self.middle_frame.config(bg=banner_color)

        self.just_name_label.pack(anchor=tk.NW, padx=5, pady=5)
        self.just_desc_label.pack(anchor=tk.NW, padx=5, pady=5)

        SIDE_NONEXCLUSIVE_AR_STRUCTS = ["Fortress", "Bolt Tower", "Tactics Room", "Healing Tower", "Panic Manor", "Catapult", "Bright Shrine", "Dark Shrine", "Calling Circle"]

        name_str = struct.name
        if struct.name in SIDE_NONEXCLUSIVE_AR_STRUCTS or "School" in struct.name:
            if struct.struct_type == PLAYER + 1:
                name_str += " (O)"
            else:
                name_str += " (D)"

        self.just_name_label.config(text=name_str + "        Lv. " + str(struct.level))
        self.just_desc_label.config(text=struct.get_desc())

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
        self.building_tab = tk.Frame(self.body_frame, bg="#031e21")

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

        tk.Label(self.building_tab, text="AR Structures:", bg=bg_color, fg=fg, font=("Helvetica", 14)).pack(anchor=tk.NW, padx=10, pady=10)

        self.scrolling_frame = MyScrollableFrame(self.building_tab)
        self.scrolling_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=(0, 10))

        divider_colors = ["#ed8f13", "#13ed96", "#683e94", "#b3b533", "#68edd9"]

        offensive_frame = tk.Frame(self.scrolling_frame, bg="#ed8f13")
        defensive_frame = tk.Frame(self.scrolling_frame, bg="#13ed96")
        traps_frame = tk.Frame(self.scrolling_frame, bg="#683e94")
        ornaments_frame = tk.Frame(self.scrolling_frame, bg="#b3b533")
        resources_frame = tk.Frame(self.scrolling_frame, bg="#68edd9")

        self.divider_frames = [offensive_frame, defensive_frame, traps_frame, ornaments_frame, resources_frame]
        self.divider_labels = ["Offense Sturctures", "Defense Structures", "Traps", "Ornaments", "Resources"]

        off_structs = []
        def_structs = []
        traps = []
        ornaments = []
        resources = []

        struct_lists = [off_structs, def_structs, traps, ornaments, resources]

        for index, row in struct_sheet.iterrows():
            cur_name = row['Name']
            category = row['Category']
            offense_exists = row['Offense Exists']
            defense_exists = row['Defense Exists']

            if category == "AR-STRUCT" or cur_name == "Fortress":
                if offense_exists:
                    off_structs.append(cur_name + " (O)" if defense_exists else cur_name)
                if defense_exists:
                    def_structs.append(cur_name + " (D)" if offense_exists else cur_name)
            elif category in {"AR-TRAP", "AR-FTRAP"}:
                traps.append(cur_name)
            elif category == "AR-DECOR":
                ornaments.append(cur_name)
            elif cur_name == "Aether Fountain" or cur_name == "Aether Amphorae":
                resources.append(cur_name)

        self.struct_imgs = []

        self.struct_levels = {}
        self.struct_labels = {}
        self.struct_buttons = {}

        self.num_offense = 1
        self.num_defense = 1
        self.num_traps = 0
        self.num_false_traps = 0
        self.num_ornaments = 0
        self.num_resources = 0

        not_added_yet = ["Calling Circle (O)", "Calling Circle (D)"]

        i = 0
        for frame in self.divider_frames:
            frame.pack(pady=3, anchor=tk.W, fill=tk.X, expand=True)

            cur_label = tk.Label(frame, text=self.divider_labels[i], font=(None, 15, 'bold'), bg=divider_colors[i], fg="white")
            cur_label.pack(padx=5, side=tk.LEFT)

            for struct in struct_lists[i]:

                if struct in not_added_yet: continue

                cur_struct_frame = tk.Frame(self.scrolling_frame, bg=divider_colors[i])
                cur_struct_frame.pack(pady=3, anchor=tk.W, fill=tk.X, expand=True)

                cur_name = struct.replace(" (D)", "_Enemy").replace(" (O)", "").replace(" ", "_").replace("'", "").replace("False_", "")

                image_path = "CombatSprites/AR Structures/" + cur_name + ".png"
                struct_image = Image.open(image_path).resize((45, 45))

                struct_photo = ImageTk.PhotoImage(struct_image)

                self.struct_imgs.append(struct_photo)

                struct_pic_frame = tk.Label(cur_struct_frame, image=struct_photo, bg=divider_colors[i])
                struct_pic_frame.pack(side=tk.LEFT, padx=5)

                cur_struct_label = tk.Label(cur_struct_frame, text=struct, font=(None, 12, 'bold'), bg=divider_colors[i], fg="white")
                cur_struct_label.pack(side=tk.LEFT)

                toggle_presence_button = tk.Button(cur_struct_frame, text="Add", bg="sky blue", width=10, command=partial(self.toggle_struct, struct))
                toggle_presence_button.pack(side=tk.RIGHT, padx=5)

                if "Fortress" in struct or struct == "Aether Fountain" or struct == "Aether Amphorae":
                    toggle_presence_button.config(state="disabled", text="Remove", bg="#eb3d57")

                level = 1
                cur_level_label = tk.Label(cur_struct_frame, text="Lv. " + str(level), font=(None, 12, 'bold'), bg=divider_colors[i], fg="white", width=5)

                self.struct_levels[struct] = level
                self.struct_labels[struct] = cur_level_label
                self.struct_buttons[struct] = toggle_presence_button

                if i != 3:
                    add_level_button = tk.Button(cur_struct_frame, text="+", fg="green", width=2, command=partial(self.change_level, struct, +1))
                    add_level_button.pack(side=tk.RIGHT, padx=5)

                    cur_level_label.pack(side=tk.RIGHT)

                    subtract_level_button = tk.Button(cur_struct_frame, text="-", fg="red", width=2, command=partial(self.change_level, struct, -1))
                    subtract_level_button.pack(side=tk.RIGHT, padx=5)

            i += 1

        self.num_player_units = 0

        self.game_mode = None
        self.is_running = None

        self.cur_sim = None

    def toggle_struct(self, struct_id):
        if self.cur_sim and self.cur_sim[0].canvas.get_struct_by_name(struct_id):

            self.struct_buttons[struct_id].config(text="Add", bg="sky blue")

            if self.cur_sim[0].canvas.unit_status.cur_hero == self.cur_sim[0].canvas.get_struct_by_name(struct_id):
                self.cur_sim[0].canvas.unit_status.clear()

            tile_containing_struct = self.cur_sim[0].canvas.get_struct_tile_by_name(struct_id)
            tile_containing_struct.structure_on = None

            self.cur_sim[0].canvas.refresh_walls()

        else:
            general_id = struct_id.replace(" (O)", "").replace(" (D)", "")
            side = 1 if "(O)" in struct_id or struct_id in ["Escape Ladder", "Duo's Indulgence", "Safety Fence"] else 2

            ex_struct = makeStruct(general_id, side)
            ex_struct.level = self.struct_levels[struct_id]

            placed = False

            if side == 1:
                for tile in self.cur_sim[0].canvas.map.tiles[0:6]:
                    if not tile.structure_on:
                        tile.structure_on = ex_struct
                        placed = True
                        break
            else:
                for tile in self.cur_sim[0].canvas.map.tiles[12:48]:
                    not_occupied_drag_point = (tile.tileNum not in self.cur_sim[0].canvas.unit_drag_points or
                                               (tile.tileNum in self.cur_sim[0].canvas.unit_drag_points and not self.cur_sim[0].canvas.unit_drag_points[tile.tileNum].hero))

                    if not tile.structure_on and not_occupied_drag_point and tile.terrain == 0 and not tile.is_def_terrain:
                        tile.structure_on = ex_struct
                        placed = True
                        break

            if placed:
                self.cur_sim[0].canvas.unit_status.update_from_struct(ex_struct)
                self.struct_buttons[struct_id].config(text="Remove", bg="#eb3d57")

            self.cur_sim[0].canvas.refresh_walls()

        for tile in self.cur_sim[0].canvas.starting_tile_photos:
            index = self.cur_sim[0].canvas.starting_tile_photos.index(tile)
            cur_drag = list(self.cur_sim[0].canvas.unit_drag_points.keys())[index]

            if not self.cur_sim[0].canvas.map.tiles[cur_drag].structure_on:
                self.cur_sim[0].canvas.itemconfigure(tile, state='normal')
            else:
                self.cur_sim[0].canvas.itemconfigure(tile, state='hidden')

        # Show in preview the object added, if currently previewed object was removed, hide it

    def change_level(self, struct_id, change):
        general_id = struct_id.replace(" (O)", "").replace(" (D)", "")

        ex_struct = makeStruct(general_id, 1 if "(O)" in struct_id else 2)

        self.struct_levels[struct_id] = min(max(1, self.struct_levels[struct_id] + change), ex_struct.max_level)

        self.struct_labels[struct_id].config(text="Lv. " + str(self.struct_levels[struct_id]))

        if self.cur_sim and self.cur_sim[0].canvas.get_struct_by_name(struct_id):
            struct_on_map = self.cur_sim[0].canvas.get_struct_by_name(struct_id)

            struct_on_map.level = self.struct_levels[struct_id]

            self.cur_sim[0].canvas.update_struct_status(struct_on_map)

        # If this struct is currently being displayed, show in preview


    def reset_tab_buttons(self):
        for button in self.buttons:
            button.config(bg=self.default_bg)

    # Called when units are modified on canvas OR tabs are switched
    def setup_tabs(self, drag_points, bonus_labels, game_mode, is_running, struct_levels_dict):
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
            # If hero is present on drag point, get their sprite from file
            if drag_point.hero:

                unit = drag_point.hero
                unit.side = drag_point.side

                S = unit.side

                respString = "-R" if unit.resp else ""
                cur_image = Image.open("TestSprites/" + unit.intName + respString + ".png")
                resized_image = cur_image.resize((int(cur_image.width / 2.1), int(cur_image.height / 2.1)))
                cur_photo = ImageTk.PhotoImage(resized_image)

                if S == PLAYER:
                    self.player_sprites.append(cur_photo)
                else:
                    self.enemy_sprites.append(cur_photo)

            # Assign which frame gets the menu components
            if drag_point.side == PLAYER:
                master = self.player_label_frame
                adding_list = self.player_labels
            else:
                master = self.enemy_label_frame
                adding_list = self.enemy_labels

            # Create new frame for this unit
            cur_frame = tk.Label(master, bg="gray10")
            unit_count = i if drag_point.side == PLAYER else j

            # Place frame onto grid (If in Aether Raids, only put down enemy frames if they are present)
            if not(drag_point.side == ENEMY and game_mode == hero.GameMode.AetherRaids):
                cur_frame.grid(row=(unit_count - 1) // 4, column=(unit_count - 1) % 4, padx=10, pady=10)
                adding_list.append(cur_frame)
            elif drag_point.hero:
                cur_frame.grid(row=(unit_count - 1) // 4, column=(unit_count - 1) % 4, padx=10, pady=10)
                adding_list.append(cur_frame)

            if drag_point.hero:
                pic_label = tk.Label(cur_frame, width=100, height=100, image=cur_photo, bg="gray10")
                name_label = tk.Label(cur_frame, text=str(unit_count) + ") " + drag_point.hero.name, bg="gray74")
            else:
                pic_label = tk.Label(cur_frame, width=100, height=100, image=PIXEL, bg="gray10")
                name_label = tk.Label(cur_frame, text=str(unit_count) + ") None", bg="gray74")

            bonus_button_color = "gray35"

            if (drag_point.side == PLAYER and self.bonus_units[i-1]) or (drag_point.side == ENEMY and self.bonus_units[i + j - 2]):
                bonus_button_color = "gold"

            adding_list.append(pic_label)
            pic_label.pack()
            name_label.pack(fill=tk.X, padx=5, pady=5)

            if (drag_point.side == PLAYER and self.game_mode == hero.GameMode.Arena) or self.game_mode == hero.GameMode.AetherRaids and (drag_point.side == PLAYER or drag_point.hero):
                button_pos = i-1 if drag_point.side == PLAYER else i + j - 2

                bonus_button = tk.Button(cur_frame, text="Is Bonus", bg=bonus_button_color, bd=0, command=partial(self.toggle_unit_as_bonus, button_pos))

                if self.is_running:
                    bonus_button.config(state="disabled")
                    self.building_button.config(state='disabled')

                if (not self.is_running) and self.game_mode == hero.GameMode.AetherRaids:
                    self.building_button.config(state='normal')

                bonus_button.pack(fill=tk.X)
                self.bonus_units_buttons.append(bonus_button)

            if drag_point.side == PLAYER:
                i += 1
            else:
                if game_mode != hero.GameMode.AetherRaids or (game_mode == hero.GameMode.AetherRaids and drag_point.hero):
                    j += 1

            if j == 1:
                self.enemy_label_frame.forget()
            else:
                self.enemy_label_frame.pack(anchor=tk.NW, padx=10, pady=10)

        self.num_player_units = i
        self.struct_levels = struct_levels_dict

        not_added_yet = ["Duo's Indulgence", "Duo's Hindrance", "Safety Fence", "Calling Circle (O)", "Calling Circle (D)"]

        for key in self.struct_levels:
            if key in not_added_yet: continue

            self.struct_labels[key].config(text="Lv. " + str(self.struct_levels[key]))

            if self.cur_sim[0].canvas.get_struct_by_name(key):
                self.struct_buttons[key].config(text="Remove", bg="#eb3d57")
            else:
                self.struct_buttons[key].config(text="Add", bg="sky blue")


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

    def set_forecast_banner_foe(self, attacker, defender, distance, savior_triggered, turn_num, combat_fields, ar_structs, units_to_move):
        self.clear_forecast_banner()

        WIDTH = 500
        HEIGHT = 90

        atkHP = attacker.HPcur
        defHP = defender.HPcur

        aoe_damage: int = 0
        aoe_present: bool = False

        if attacker.special is not None and attacker.special.type == "AOE" and attacker.specialCount == 0:
            aoe_present = True

            aoe_damage = get_AOE_damage(attacker, defender)
            defHP = max(1, defHP - aoe_damage)

        result = simulate_combat(attacker,
                                 defender,
                                 True,
                                 turn_num,
                                 distance,
                                 combat_fields,
                                 aoe_present,
                                 units_to_move,
                                 savior_triggered,
                                 ar_structs,
                                 atkHPCur=atkHP,
                                 defHPCur=defHP)

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
        inf_icon = inf_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(inf_icon))
        cav_icon = status_pic.crop((462, 414, 518, 468))
        cav_icon = cav_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(cav_icon))
        fly_icon = status_pic.crop((518, 414, 572, 468))
        fly_icon = fly_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(fly_icon))
        arm_icon = status_pic.crop((406, 414, 462, 468))
        arm_icon = arm_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(arm_icon))

        weapon_icons = []
        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
            cur_icon = cur_icon.resize((25, 25))
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

            if x.healed != 0:
                canvas.create_text((cur_box_pos-10, 65-10), text=x.healed, fill="green", font=("Helvetica", 8, 'bold'), anchor='center')

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

            if player.bskill and "live_to_serve" in player.bskill.effects:
                percentage = 0.25 + 0.25 * player.bskill.effects["live_to_serve"]
                hp_healed_self += trunc(hp_healed_ally * percentage)

            # Deep Wounds
            if Status.DeepWounds in player.statusNeg: hp_healed_self = 0
            if Status.DeepWounds in ally.statusNeg: hp_healed_ally = 0

            new_ally_hp = min(ally.visible_stats[HP], ally.HPcur + hp_healed_ally)
            new_player_hp = min(player.visible_stats[HP], player.HPcur + hp_healed_self)

        if "rec_aid" in player.assist.effects:
            new_ally_hp = min(ally.visible_stats[HP], player.HPcur)
            new_player_hp = min(player.visible_stats[HP], ally.HPcur)

        if "ardent_sac" in player.assist.effects:
            hp_change = 10 if Status.DeepWounds not in ally.statusNeg else 0

            new_ally_hp = min(ally.visible_stats[HP], ally.HPcur + hp_change)
            new_player_hp = max(1, player.HPcur - hp_change)

        if "sacrifice" in player.assist.effects:
            new_ally_hp = min(ally.visible_stats[HP], ally.HPcur + (player.HPcur - 1))
            new_player_hp = max(1, player.HPcur - (ally.visible_stats[HP] - ally.HPcur))

        if "sacrifice" in player.assist.effects:
            if ally.HPcur < ally.visible_stats[HP]:
                new_ally_hp = min(ally.visible_stats[HP], ally.HPcur + (player.HPcur - 1))
                new_player_hp = max(1, player.HPcur - (ally.visible_stats[HP] - ally.HPcur))
            else:
                new_ally_hp = ally.HPcur
                new_player_hp = player.HPcur

        canvas.create_text((215, 16), text=str(player.HPcur) + "→" + str(new_player_hp), fill='yellow', font=("Helvetica", 13), anchor='center')
        canvas.create_text((WIDTH-216, 16), text=str(ally.HPcur) + "→" + str(new_ally_hp), fill="yellow", font=("Helvetica", 13), anchor='center')

        canvas.create_rectangle(250 - 65, 27, 270 + 65, 42, fill='#5a5c6b', outline='#dae6e2')
        canvas.create_text((250, 34), text=player.assist.name, fill="white", font=("Helvetica", 11), anchor='center')

        move_icons = []
        status_pic = Image.open("CombatSprites/" + "Status" + ".png")

        inf_icon = status_pic.crop((350, 414, 406, 468))
        inf_icon = inf_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(inf_icon))
        cav_icon = status_pic.crop((462, 414, 518, 468))
        cav_icon = cav_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(cav_icon))
        fly_icon = status_pic.crop((518, 414, 572, 468))
        fly_icon = fly_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(fly_icon))
        arm_icon = status_pic.crop((406, 414, 462, 468))
        arm_icon = arm_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(arm_icon))

        weapon_icons = []
        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
            cur_icon = cur_icon.resize((25, 25))
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
        inf_icon = inf_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(inf_icon))
        cav_icon = status_pic.crop((462, 414, 518, 468))
        cav_icon = cav_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(cav_icon))
        fly_icon = status_pic.crop((518, 414, 572, 468))
        fly_icon = fly_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(fly_icon))
        arm_icon = status_pic.crop((406, 414, 462, 468))
        arm_icon = arm_icon.resize((23, 23))
        move_icons.append(ImageTk.PhotoImage(arm_icon))

        weapon_icons = []
        i = 0
        while i < 24:
            cur_icon = status_pic.crop((56 * i, 206, 56 * (i + 1), 260))
            cur_icon = cur_icon.resize((25, 25))
            weapon_icons.append(ImageTk.PhotoImage(cur_icon))
            i += 1

        atkr_move_icon = move_icons[attacker.move]
        atkr_wpn_icon = weapon_icons[weapons[attacker.wpnType][0]]

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
        self.building_button.config(bg="green")

        if self.active_tab:
            self.active_tab.forget()

        self.building_tab.pack(fill=tk.BOTH, expand=True)
        self.active_tab = self.building_tab
