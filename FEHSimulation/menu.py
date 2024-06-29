import hero
import pandas as pd

from csv import reader, writer
import webbrowser
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from math import isnan
from functools import partial

WEAPON = 0
ASSIST = 1
SPECIAL = 2
ASKILL = 3
BSKILL = 4
CSKILL = 5
SSEAL = 6
XSKILL = 7

STATS = {"None": -1, "HP": 0, "Atk": 1, "Spd": 2, "Def": 3, "Res": 4}
STAT_STR = ["HP", "Atk", "Spd", "Def", "Res", "None"]

class HeroProxy():
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

        apl_hero.allySupport = self.a_support
        apl_hero.summonerSupport = self.s_support

        if self.weapon is not None:
            wpn_name = self.weapon.intName
            refine_substrings = ["Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz"]

            if wpn_name[-3:] in refine_substrings:
                wpn_name = wpn_name[:-3]

            if self.refine == "None": self.refine = ""

            self.weapon = hero.makeWeapon(wpn_name + self.refine)

        apl_hero.set_skill(self.weapon, WEAPON)
        apl_hero.set_skill(self.assist, ASSIST)
        apl_hero.set_skill(self.special, SPECIAL)
        apl_hero.set_skill(self.askill, ASKILL)
        apl_hero.set_skill(self.bskill, BSKILL)
        apl_hero.set_skill(self.cskill, CSKILL)
        apl_hero.set_skill(self.sSeal, SSEAL)
        apl_hero.set_skill(self.xskill, XSKILL)




def about():
    webbrowser.open("https://github.com/EtDet/RATA-Public", new=0, autoraise=True)

def remove_elements():
    spacer.config(fg="#797282", text="W")

    for x in current_elements:
        x.pack_forget()

    edit_button.pack_forget()
    delete_button.pack_forget()

    current_elements.clear()

def generate_main():
    remove_elements()

    i = 0
    while i < len(front_page_elements):
        front_page_elements[i].pack(pady=front_page_paddings[i])
        current_elements.append(front_page_elements[i])
        i += 1

def generate_units():
    cur_unit_selected.set("")

    clear_creation_fields()

    remove_elements()

    for widget in button_frame.winfo_children():
        widget.grid_remove()

    width = 97
    height = 97

    pixel = tk.PhotoImage(width=1, height=1)
    pre_button = tk.Button(button_frame, command=generate_creation, text="Create New", image=pixel, compound=tk.TOP, height=height, width=width, font='Helvetica 8')
    pre_button.image = pixel
    pre_button.grid(row=0, column=0, padx=3, pady=3)

    row, col = 0, 1

    unit_read = pd.read_csv("my_units.csv")
    for i, hrow in enumerate(unit_read.iterrows()):

        respString = "-R" if hrow[1]['Resplendent'] == True else ""

        image2 = Image.open("TestSprites\\" + hrow[1]['IntName'] + respString + ".png")
        new_width = int(image2.width * 0.4)
        new_height = int(image2.height * 0.4)

        if new_height > 85:
            new_width = int(new_width * 0.88)
            new_height = int(new_height * 0.88)

        resized_image2 = image2.resize((new_width, new_height), Image.LANCZOS)
        curImage = ImageTk.PhotoImage(resized_image2)

        images.append(curImage)
        build_name = str(hrow[1]['Build Name'])
        tempButton = tk.Button(button_frame, command=partial(show_edit_prompt, i, build_name), image=curImage, text=build_name, compound=tk.TOP, height=height, width=width, font='Helvetica 8')
        tempButton.image = curImage
        tempButton.grid(row=row, column=col, padx=3, pady=3)

        col += 1
        if col % 7 == 0:
            row += 1
            col = 0

    # Update the unit_canvas scrolling region
    unit_subframe.update_idletasks()
    unit_canvas.configure(scrollregion=unit_canvas.bbox("all"))

    search_frame.pack(pady=10)
    select_frame.pack(pady=10)
    unit_canvas.pack(side='left', fill='both', expand=True)
    unit_scrollbar.pack(side='right', fill='y')
    button_frame.pack(side='left', padx=(1,4), pady=5)

    current_elements.append(search_frame)
    current_elements.append(unit_canvas)
    current_elements.append(button_frame)
    current_elements.append(unit_scrollbar)
    current_elements.append(select_frame)

def show_edit_prompt(num, build_name):
    spacer.config(fg="#252a33", text=f'What do you want to do with "{build_name}"?')

    edit_button.config(command=partial(generate_creation_edit, num))
    delete_button.config(command=partial(delete_unit, num))

    edit_button.pack(side='left', padx=20)
    delete_button.pack(side='left')

    print(num, build_name)

def generate_creation():
    remove_elements()

    top_frame.pack(side=tk.TOP, expand=False, fill=tk.X)
    bottom_frame.pack(side=tk.BOTTOM, expand=False, fill=tk.X)
    unit_stat_frame.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)
    dropbox_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)


    current_elements.append(unit_stat_frame)
    current_elements.append(dropbox_frame)
    current_elements.append(top_frame)
    current_elements.append(bottom_frame)

def generate_creation_edit(num):
    # Move to creation screen
    generate_creation()

    print(num)
    my_units = pd.read_csv("my_units.csv")

    row = my_units.loc[num]
    print(row)


    # Internal name from sheet
    int_name = row["IntName"]
    curHero = hero.makeHero(int_name)


    # Name
    title_name = curHero.name + ": " + curHero.epithet
    creation_comboboxes[0].set(title_name)
    handle_selection_change_name()

    # Rarity
    rarity = row["Rarity"]
    creation_comboboxes[1].set(rarity)
    handle_selection_change_rarity()

    # Level
    level = row["Level"]
    creation_comboboxes[13].set(level)
    handle_selection_change_level()

    # Merges
    merges = row["Merges"]
    creation_comboboxes[2].set(merges)
    handle_selection_change_merge()

    # Asset
    asset = STAT_STR[row["Asset"]]
    creation_comboboxes[3].set(asset)
    handle_selection_change_asset()

    # Flaw
    flaw = STAT_STR[row["Flaw"]]
    creation_comboboxes[15].set(flaw)
    handle_selection_change_flaw()

    # Weapon
    weapon = row["Weapon"]

    if pd.isnull(weapon):
        weapon = "None"

    refine_substrings = ["Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz"]
    if weapon[-3:] in refine_substrings:
        weapon = weapon[:-3]

    creation_comboboxes[6].set(weapon)
    handle_selection_change_weapon()

    # Refine
    refine = row["Weapon"]

    if pd.isnull(refine):
        refine = "None"

    if refine[-3:] in refine_substrings:
        refine = refine[-3:]
    else:
        refine = "None"

    creation_comboboxes[7].set(refine)
    handle_selection_change_refine()

    # Assist
    assist = row["Assist"]

    if pd.isnull(assist):
        assist = "None"

    creation_comboboxes[8].set(assist)
    handle_selection_change_assist()

    # Special
    special = row["Special"]

    if pd.isnull(special):
        special = "None"

    creation_comboboxes[9].set(special)
    handle_selection_change_special()

    # A Skill
    askill = row["ASkill"]

    if pd.isnull(askill):
        askill = "None"

    creation_comboboxes[18].set(askill)
    handle_selection_change_askill()

    # B Skill
    bskill = row["BSkill"]

    if pd.isnull(bskill):
        bskill = "None"

    creation_comboboxes[19].set(bskill)
    handle_selection_change_bskill()

    # C Skill
    cskill = row["CSkill"]

    if pd.isnull(cskill):
        cskill = "None"

    creation_comboboxes[20].set(cskill)
    handle_selection_change_cskill()

    # Build Name
    build_name.set(row["Build Name"])

    # TOMORROW: CHANGE THE CREATE BUTTON TO A SAVE BUTTON
    # WHEN CLICKED, REPLACE ROW
    creation_make_button.config(text="Save", command=partial(edit_unit_in_list, num))

def delete_unit(num):

    data = pd.read_csv("my_units.csv")
    data = data.drop(num)
    data.to_csv("my_units.csv", index=False)

    generate_units()

def clear_creation_fields():
    curProxy.reset()

    creation_image_label.config(image=pixel)
    creation_image_label.image = pixel

    handle_selection_change_name.created_hero = None

    unit_name.set("---\n---")

    unit_stats.set("Lv. ---\n+0 Flowers")

    unit_picked.set("No Unit Selected")

    for x in creation_str_vars:
        x.set("")

    i = 0
    while i < 5:
        creation_stats[i].set(stat_strings[i] + "---")
        i += 1

    # Reset Weapon/Assist/Special options
    creation_comboboxes[6]['values'] = []
    creation_comboboxes[7]['values'] = []
    creation_comboboxes[8]['values'] = []
    creation_comboboxes[9]['values'] = []

    creation_comboboxes[18]['values'] = []
    creation_comboboxes[19]['values'] = []
    creation_comboboxes[20]['values'] = []

    build_name.set("")
    error_text.config(fg='#292e36')

    # Reset save button to Create
    creation_make_button.config(text="Create", command=add_unit_to_list)

def generate_all_units_option():
    names = hero.hero_sheet['Name']
    int_names = hero.hero_sheet['IntName']
    epithets = hero.hero_sheet['Epithet']

    # Units currently allowed for this build of the sim, what's implemented so far
    implemented_heroes = ["Abel", "Alfonse", "Anna", "F!Arthur", "Azama", "Azura", "Barst", "Bartre", "Beruka", "Caeda",
                          "Cain", "Camilla", "Catria", "Cecilia", "Cherche", "chrom", "Clarine", "Cordelia", "M!Corrin", "F!Corrin",
                          "Donnel", "Draug", "Effie", "Elise", "Eliwood", "Est", "Fae", "Felicia", "Fir", "Florina",
                          "Frederick", "Gaius", "Gordin", "Gunter", "Gwendolyn", "Hana", "Hawkeye", "Hector", "Henry", "Hinata",
                          "Hinoka", "Jagen", "Jakob", "Jeorge", "Kagero", "Laslow", "Leo", "Lilina", "Linde", "Lissa",
                          "Lon'qu", "Lucina", "Lyn", "Maria", "Marth", "Matthew", "Merric", "Minerva", "Niles", "Nino",
                          "Nowi", "Oboro", "Odin", "Ogma", "Olivia", "Palla", "Raigh", "Raven", "Peri", "M!Robin",
                          "Roy", "Ryoma", "Saizo", "Sakura", "F!Selena", "Serra", "Setsuna", "Shanna", "Sharena", "Sheena",
                          "Sophia", "Stahl", "Subaki", "Sully", "Takumi", "Tharja", "Y!Tiki", "A!Tiki", "Virion", "Wrys"]

    options = []
    intName_dict = {}

    i = 0
    while i < len(names):
        if int_names[i] in implemented_heroes:
            cur_string = names[i] + ": " + epithets[i]
            options.append(cur_string)
            intName_dict[cur_string] = int_names[i]

        i += 1

    return options, intName_dict

def get_valid_weapons(cur_hero):
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
                           "Iron Dagger", "Steel Dagger", "Silver Dagger", "Silver Dagger+", "Smoke Dagger", "Smoke Dagger+", "Rogue Dagger", "Rogue Dagger+", "Poison Dagger", "Poison Dagger+",
                           "Fire", "Elfire", "Bolganone", "Bolganone+", "Flux", "Ruin", "Fenrir", "Fenrir+", "Rauðrblade", "Rauðrblade+", "Rauðrraven", "Rauðrraven+", "Rauðrwolf", "Rauðrwolf+",
                           "Thunder", "Elthunder", "Thoron", "Thoron+", "Blárblade", "Blárblade+", "Blárraven", "Blárraven+",
                           "Wind", "Elwind", "Rexcalibur", "Rexcalibur+", "Gronnblade", "Gronnblade+", "Gronnraven", "Gronnraven+",
                           "Assault", "Absorb", "Absorb+", "Fear", "Fear+", "Slow", "Slow+", "Gravity", "Gravity+", "Panic", "Panic+", "Pain", "Pain+",
                           "Fire Breath", "Fire Breath+", "Flametongue", "Flametongue+", "Lightning Breath", "Lightning Breath+", "Light Breath", "Light Breath+"]

    # Remove of different weapon
    i = 0
    while i < len(weapons):

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
            if substring in string:
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

def get_valid_refines(weapon_name):
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

def get_valid_assists(cur_hero):
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
                           "Dance", "Sing",
                           "Harsh Command", "Ardent Sacrifice", "Reciprocal Aid",
                           "Draw Back", "Reposition", "Swap", "Pivot", "Shove", "Smite",]

    i = 0
    while i < len(assist_names):
        if assist_names[i] in implemented_assists:
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

def get_valid_specials(cur_hero):
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
                            "Rising Flame", "Blazing Flame", "Growing Flame",
                            "Rising Light", "Blazing Light", "Growing Light",
                            "Rising Thunder", "Blazing Thunder", "Growing Thunder",
                            "Rising Wind", "Blazing Wind", "Growing Wind",
                            "Buckler", "Escutcheon", "Pavise", "Holy Vestiments", "Sacred Cowl", "Aegis", "Miracle",
                            "Imbue", "Heavenly Light", "Kindled-Fire Balm", "Swift-Winds Balm", "Solid-Earth Balm", "Still-Water Balm"]

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
            if restr_wpn[i] == "NotMagic" and cur_hero.wpnType not in hero.MAGIC_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotBow" and cur_hero.wpnType not in hero.BOW_WEAPONS: add_cond = False

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

    #standard_specials = list(set(allowed_by_move) & set(allowed_by_wpn))

    standard_specials = sorted(standard_specials)

    return ["None"] + prf_specials + standard_specials

def get_valid_abc_skills(cur_hero):
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
            if restr_wpn[i] == "NotMagic" and cur_hero.wpnType not in hero.MAGIC_WEAPONS: add_cond = False
            if restr_wpn[i] == "NotBow" and cur_hero.wpnType not in hero.BOW_WEAPONS: add_cond = False

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

# Upon valid unit and name options, add the unit to the CSV file
def add_unit_to_list():
    hero_to_add = handle_selection_change_name.created_hero

    print(creation_str_vars[0].get(), build_name.get())
    if creation_str_vars[0].get() != "" and build_name.get() != "":

        name = hero_to_add.intName
        weapon = hero_to_add.weapon.intName if hero_to_add.weapon is not None else None
        assist = hero_to_add.assist.name if hero_to_add.assist is not None else None
        special = hero_to_add.special.name if hero_to_add.special is not None else None
        askill = hero_to_add.askill.name if hero_to_add.askill is not None else None
        bskill = hero_to_add.bskill.name if hero_to_add.bskill is not None else None
        cskill = hero_to_add.cskill.name if hero_to_add.cskill is not None else None
        sSeal = None
        xskill = None
        level = hero_to_add.level
        merges = hero_to_add.merges
        rarity = hero_to_add.rarity
        asset = hero_to_add.asset
        flaw = hero_to_add.flaw
        asc = hero_to_add.asc_asset
        sSupport = 0
        aSupport = None
        blessing = None
        dflowers = 0
        resp = False
        emblem = None
        emblem_merges = 0
        cheats = False

        data = [name, build_name.get(),
                weapon, assist, special, askill, bskill, cskill, sSeal, xskill,
                level, merges, rarity, asset, flaw, asc, aSupport, sSupport, blessing, dflowers, resp, emblem, emblem_merges, cheats]

        try:
            my_units_file = "my_units.csv"

            with open(my_units_file, mode="a", newline='') as file:
                f_writer = writer(file)
                f_writer.writerow(data)

            # Go back to unit selection screen
            generate_units()

        except PermissionError:
            print(f"Error: Permission denied when writing to file. Please close {my_units_file} and try again.")
    else:
        error_text.config(fg='#d60408')


def edit_unit_in_list(num):
    hero_to_add = handle_selection_change_name.created_hero

    if creation_str_vars[0].get() != "" and build_name.get() != "":

        name = hero_to_add.intName
        weapon = hero_to_add.weapon.intName if hero_to_add.weapon is not None else None
        assist = hero_to_add.assist.name if hero_to_add.assist is not None else None
        special = hero_to_add.special.name if hero_to_add.special is not None else None
        askill = hero_to_add.askill.name if hero_to_add.askill is not None else None
        bskill = hero_to_add.bskill.name if hero_to_add.bskill is not None else None
        cskill = hero_to_add.cskill.name if hero_to_add.cskill is not None else None
        sSeal = None
        xskill = None
        level = hero_to_add.level
        merges = hero_to_add.merges
        rarity = hero_to_add.rarity
        asset = hero_to_add.asset
        flaw = hero_to_add.flaw
        asc = hero_to_add.asc_asset
        sSupport = 0
        aSupport = None
        blessing = None
        dflowers = 0
        resp = False
        emblem = None
        emblem_merges = 0
        cheats = False

        data = [name, build_name.get(),
                weapon, assist, special, askill, bskill, cskill, sSeal, xskill,
                level, merges, rarity, asset, flaw, asc, aSupport, sSupport, blessing, dflowers, resp, emblem, emblem_merges, cheats]

        try:
            my_units_file = "my_units.csv"

            with open(my_units_file, 'r', newline='') as file:
                f_reader = reader(file)
                read_data = list(f_reader)

            read_data[num + 1] = data

            with open(my_units_file, mode="w", newline='') as file:
                f_writer = writer(file)
                f_writer.writerows(read_data)

            # Go back to unit selection screen
            generate_units()

        except PermissionError:
            print(f"Error: Permission denied when writing to file. Please close {my_units_file} and try again.")
    else:
        error_text.config(fg='#d60408')

# Scroll list of units
def on_canvas_mousewheel(event):
    canvas = unit_canvas
    delta = -1 * int(event.delta / 100)

    # Scroll the canvas vertically
    canvas.yview_scroll(delta, "units")

    # Prevent scrolling upwards if we're already at the top
    if delta < 0:
        top, bottom = canvas.yview()
        if top <= 0:
            canvas.yview_moveto(0)

# window
window = tk.Tk()
#window.resizable(False, False)
window.geometry('800x600')
window.title('FEH Sim')
window.configure(background='#797282')
#window.iconbitmap("Sprites\\Marth.ico")

# MAIN MENU ELEMENTS
title_label = tk.Label(master=window, text='RATA - An FE: Heroes Simulator', font='nintendoP_Skip-D_003 24')
subtitle_label = tk.Label(master=window, text='By CloudX (2024)', font='nintendoP_Skip-D_003 12')
start_button = tk.Button(window, command=remove_elements, width=30, text="Level Select", font="Helvetica", cursor="hand2", overrelief="raised", bg='blue', fg='white')
units_button = tk.Button(window, command=generate_units, width=30, text="My Units", font="Helvetica", cursor="hand2", overrelief="raised", bg='blue', fg='white')
help_button = tk.Button(window, command=about,width=30, text="User Guide", font="Helvetica", cursor="hand2", overrelief="raised", bg='blue', fg='white')
dev_button = tk.Button(window, command=about,width=30, text="Developer Guide", font="Helvetica", cursor="hand2", overrelief="raised", bg='blue', fg='white')
quit_button = tk.Button(window, command=window.destroy, width=30, text="Close", font="Helvetica", cursor="hand2", overrelief="raised", bg='red', fg='white')

front_page_elements = [title_label, subtitle_label, start_button, units_button, help_button, dev_button, quit_button]
front_page_paddings = [(100, 20), (10, 20), (20, 20), (0, 20), (0, 20), (0, 20), (0, 20)]



# UNIT SELECTION ELEMENTS

search_frame = tk.Frame(window, bg='#797282')
back_button = tk.Button(search_frame, text='<- Back', command=generate_main, width=10)
back_button.pack(side='left')

name_search_label = ttk.Label(master=search_frame, text='Name Search:')
name_search_label.pack(side='left', padx=(25, 5))

search_string = tk.StringVar()
search_bar = ttk.Entry(search_frame, textvariable=search_string, width=30)
search_bar.pack(side='left', padx=(5,20))

search_button = tk.Button(search_frame, text='Search', width=15) #, command=searchUnits)
search_button.pack(side='left')

select_frame = tk.Frame(window, bg='#797282')
edit_button = tk.Button(select_frame, text='Edit', command=generate_main, width=10)
delete_button = tk.Button(select_frame, text='Delete', command=delete_unit, width=10, bg="#e64337")

spacer = tk.Label(select_frame, text="W", font=("Arial 14"), bg='#797282', fg='#797282')
spacer.pack(side=tk.LEFT)


# Canvas
unit_canvas = tk.Canvas(window, bg="#9ea8b8")

# Scrollbar, for Canvas
unit_scrollbar = ttk.Scrollbar(window, orient='vertical', command=unit_canvas.yview)

unit_canvas.configure(yscrollcommand=unit_scrollbar.set)
unit_canvas.bind("<Configure>", lambda e: unit_canvas.configure(scrollregion=unit_canvas.bbox("all")))
unit_canvas.bind_all("<MouseWheel>", on_canvas_mousewheel)

unit_subframe = tk.Frame(unit_canvas, width=300, height=300)
unit_canvas.create_window((0, 0), window=unit_subframe, anchor='nw')
button_frame = tk.Frame(unit_subframe)

unit_elements = [search_frame, select_frame, unit_canvas, unit_scrollbar, button_frame]



# UNIT CREATION

# Four frames
top_frame = tk.Frame(window, bg='#292e36')
unit_stat_frame = tk.Frame(window, bg='#2b2a69')
dropbox_frame = tk.Frame(window, bg='#a5b7c2')
bottom_frame = tk.Frame(window, bg='#292e36')

creation_back_button = tk.Button(top_frame, text='<- Cancel', command=generate_units, width=10)
creation_back_button.pack(side=tk.LEFT, anchor='nw', padx=10, pady=10)

creation_make_button = tk.Button(bottom_frame, text='Create', command=add_unit_to_list, width=10)
creation_make_button.pack(side=tk.RIGHT, anchor='nw', padx=10, pady=10)

build_name = tk.StringVar()
creation_build_field = tk.Entry(bottom_frame, width=30, font="Helvetica", textvariable=build_name)
creation_build_field.pack(side=tk.RIGHT, anchor='nw', padx=10, pady=10)

creation_make_text = tk.Label(bottom_frame, text='Build Name: ', width=10)
creation_make_text.pack(side=tk.RIGHT, anchor='nw', padx=10, pady=10)

error_text = tk.Label(bottom_frame, text='Error: No Unit Selected or Build Name Empty', bg='#292e36', fg='#292e36', font="Helvetica 10 bold")
error_text.pack(side=tk.RIGHT, anchor='nw', padx=10, pady=10)


pixel = tk.PhotoImage(width=1, height=1)

unit_picked = tk.StringVar()
unit_picked.set("No Hero Selected")

creation_image_label = tk.Label(unit_stat_frame, image=pixel, textvariable=unit_picked, font= "Helvetica 13", compound=tk.TOP, height=200, width=200, bg='#728275', relief=tk.RAISED)
creation_image_label.pack(padx=10, pady=10)

unit_name = tk.StringVar()
unit_name.set("---\n---")

creation_unit_label = tk.Label(unit_stat_frame, textvariable=unit_name, compound=tk.TOP, height=2, width=25, bg='#070708', fg="#e0e86b")
creation_unit_label.pack(padx=10, pady=10)

unit_stats = tk.StringVar()
unit_stats.set("Lv. ---\n+0 Flowers")

creation_merge_label = tk.Label(unit_stat_frame, textvariable=unit_stats, compound=tk.TOP, height=2, width=18, bg='#070708', fg="#e0e86b")
creation_merge_label.pack(padx=10, pady=(10, 20))

creation_stats = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()]
stat_strings = ["HP: ", "Atk: ", "Spd: ", "Def: ", "Res: "]

creation_stat_labels = []


i = 0
while i < 5:
    creation_stats[i].set(stat_strings[i] + "---")
    cur_label = tk.Label(unit_stat_frame, textvariable=creation_stats[i], compound=tk.TOP, height=1, width=18, bg='#070708', fg="#e0e86b", relief="solid")
    cur_label.pack(padx=10)
    creation_stat_labels.append(cur_label)

    i += 1


names = ["Unit", "Rarity", "Merge", "Asset", "Blessing", "S-Support", "Weapon", "Refine", "Assist", "Special", "Emblem", "Emblem Merge"]
names2 = ["Resplendent?", "Level", "DFlowers", "Flaw", "Asc. Asset", "A-Support", "A Skill", "B Skill", "C Skill", "Sacred Seal", "X Skill"]

creation_str_vars = []

all_hero_options, intName_dict = generate_all_units_option()

numbers = list(range(41))
iv_strs = ["None", "HP", "Atk", "Spd", "Def", "Res"]

left_dropbox_frame = tk.Frame(dropbox_frame, bg="#a5b7c2")
right_dropbox_frame = tk.Frame(dropbox_frame, bg="#a5b7c2")

left_dropbox_frame.pack(padx=8, pady=7, side=tk.LEFT, anchor='nw')
right_dropbox_frame.pack(padx=8, pady=7, side=tk.RIGHT, anchor='ne')

def handle_selection_change_name(event=None):
    selected_value = creation_str_vars[0].get()
    print(f"You selected: {selected_value}")

    cur_intName = intName_dict[selected_value]

    curProxy.full_name = selected_value


    cur_image = Image.open("TestSprites\\" + cur_intName + ".png")

    resized_image = cur_image.resize((int(cur_image.width / 1.3), int(cur_image.height / 1.3)), Image.LANCZOS)

    curPhoto = ImageTk.PhotoImage(resized_image)

    creation_image_label.config(image=curPhoto)
    creation_image_label.image = curPhoto

    madeHero: hero.Hero = hero.makeHero(cur_intName)

    # Set default value in ComboBoxes upon first Hero selection
    if handle_selection_change_name.created_hero is None:
        # Set default rarity
        creation_str_vars[1].set(min(5, curProxy.rarity))

        # Set default merge
        creation_str_vars[2].set(max(0, curProxy.merge))

        # Set default Asset
        creation_str_vars[3].set(STAT_STR[curProxy.asset])

        # Set default Flaw
        creation_str_vars[15].set(STAT_STR[curProxy.flaw])

        # Set default Asc Asset
        #creation_str_vars[16].set(STAT_STR[curProxy.asc_asset])

        # Set default level
        creation_str_vars[13].set(min(40, curProxy.level))


    # Generate all possible weapons for selected Hero
    weapons = get_valid_weapons(madeHero)

    # If newly selected character can't wield what's currently in the box, remove it
    if creation_str_vars[6].get() not in weapons:
        # This should be no weapon by default
        curProxy.weapon = None
        creation_str_vars[6].set("None")

        # Reset what refines should be available too
        creation_str_vars[7].set("None")
        creation_comboboxes[7]['values'] = []

    # Set allowed weapons
    creation_comboboxes[6]['values'] = weapons

    # Generate all possible assist skills
    assists = get_valid_assists(madeHero)

    if creation_str_vars[8].get() not in assists:
        curProxy.assist = None
        creation_str_vars[8].set("None")

    # Set allowed assists
    creation_comboboxes[8]['values'] = assists

    # Generate all possible special skills
    specials = get_valid_specials(madeHero)

    if creation_str_vars[9].get() not in specials:
        curProxy.special = None
        creation_str_vars[9].set("None")

    # Set allowed assists
    creation_comboboxes[9]['values'] = specials

    # ABC Skills
    a_sk, b_sk, c_sk = get_valid_abc_skills(madeHero)

    if creation_str_vars[18].get() not in a_sk:
        curProxy.askill = None
        creation_str_vars[18].set("None")

    # Set allowed assists
    creation_comboboxes[18]['values'] = a_sk

    if creation_str_vars[19].get() not in b_sk:
        curProxy.bskill = None
        creation_str_vars[19].set("None")

    # Set allowed assists
    creation_comboboxes[19]['values'] = b_sk

    if creation_str_vars[20].get() not in c_sk:
        curProxy.cskill = None
        creation_str_vars[20].set("None")

    # Set allowed assists
    creation_comboboxes[20]['values'] = c_sk
    #print(a_sk, b_sk, c_sk)


    handle_selection_change_name.created_hero = madeHero
    curProxy.apply_proxy(madeHero)

    unit_picked.set("")

    star_var = "✰" * curProxy.rarity
    unit_name.set(f"{selected_value}\n{star_var}")

    merge_str = ""
    if curProxy.merge > 0:
        merge_str = "+" + str(curProxy.merge)

    unit_stats.set(f"Lv. {curProxy.level}{merge_str}\n+0 Flowers")

    #unit_stats.set(f"Lv. {curProxy.level}\n+0 Flowers")

    i = 0
    while i < 5:
        creation_stats[i].set(stat_strings[i] + str(madeHero.visible_stats[i]))
        i += 1

def handle_selection_change_rarity(event=None):
    selected_value = creation_str_vars[1].get()
    print(f"You selected: {selected_value}")

    curProxy.rarity = int(selected_value)

    if handle_selection_change_name.created_hero is not None:
        star_var = "✰" * int(selected_value)
        unit_name.set(f"{curProxy.full_name}\n{star_var}")

        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_level(event=None):
    selected_value = creation_str_vars[13].get()
    print(f"You selected: {selected_value}")

    curProxy.level = int(selected_value)

    if handle_selection_change_name.created_hero is not None:
        merge_str = ""
        if curProxy.merge > 0:
            merge_str = "+" + str(curProxy.merge)

        unit_stats.set(f"Lv. {selected_value}{merge_str}\n+0 Flowers")

        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_merge(event=None):
    selected_value = creation_str_vars[2].get()
    print(f"You selected: {selected_value}")

    curProxy.merge = int(selected_value)

    if handle_selection_change_name.created_hero is not None:

        unit_stats.set(f"Lv. {curProxy.level}+{selected_value}\n+{curProxy.dflowers} Flowers")

        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_asset(event=None):
    selected_value = creation_str_vars[3].get()
    print(f"You selected: {selected_value}")

    stat_int = STATS[selected_value]

    # Set asc asset to new value if not present (asset same as asc_asset)
    if curProxy.asset == curProxy.asc_asset:
        curProxy.asc_asset = stat_int

    # Set new asset value
    curProxy.asset = stat_int

    # If this overlaps with the current flaw value
    if curProxy.flaw == curProxy.asset or curProxy.flaw == -1:
        # Move flaw to next possible stat
        curProxy.flaw = (STATS[selected_value] + 1) % 5

    if curProxy.asset == -1:
        curProxy.flaw = -1

    creation_str_vars[15].set(STAT_STR[curProxy.flaw])

    if handle_selection_change_name.created_hero is not None:
        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_flaw(event=None):
    selected_value = creation_str_vars[15].get()
    print(f"You selected: {selected_value}")

    stat_int = STATS[selected_value]

    curProxy.flaw = stat_int

    if curProxy.asset == curProxy.flaw or curProxy.asset == -1:
        print("homer")

        curProxy.asset = (stat_int + 1) % 5
        curProxy.asc_asset = (stat_int + 1) % 5

    if curProxy.flaw == -1:
        curProxy.asset = -1

    creation_str_vars[3].set(STAT_STR[curProxy.asset])

    if handle_selection_change_name.created_hero is not None:
        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_weapon(event=None):
    selected_value = creation_str_vars[6].get()
    print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        curProxy.weapon = hero.makeWeapon(selected_value)
    else:
        curProxy.weapon = None

    curProxy.refine = ""

    # Set valid refines for this given weapon
    refines_arr = get_valid_refines(selected_value)
    creation_str_vars[7].set("None")
    creation_comboboxes[7]['values'] = refines_arr

    if handle_selection_change_name.created_hero is not None:
        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_refine(event=None):
    selected_value = creation_str_vars[7].get()
    print(f"You selected: {selected_value}")

    if selected_value != "None":
        curProxy.refine = selected_value
    else:
        curProxy.refine = ""

    if handle_selection_change_name.created_hero is not None:
        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_assist(event=None):
    selected_value = creation_str_vars[8].get()
    print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        curProxy.assist = hero.makeAssist(selected_value)
    else:
        curProxy.assist = None

    if handle_selection_change_name.created_hero is not None:
        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_special(event=None):
    selected_value = creation_str_vars[9].get()
    print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        curProxy.special = hero.makeSpecial(selected_value)
    else:
        curProxy.special = None

    if handle_selection_change_name.created_hero is not None:
        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_askill(event=None):
    selected_value = creation_str_vars[18].get()
    print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        curProxy.askill = hero.makeSkill(selected_value)
    else:
        curProxy.askill = None

    if handle_selection_change_name.created_hero is not None:
        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_bskill(event=None):
    selected_value = creation_str_vars[19].get()
    print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        curProxy.bskill = hero.makeSkill(selected_value)
    else:
        curProxy.bskill = None

    if handle_selection_change_name.created_hero is not None:
        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_cskill(event=None):
    selected_value = creation_str_vars[20].get()
    print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        curProxy.cskill = hero.makeSkill(selected_value)
    else:
        curProxy.cskill = None

    if handle_selection_change_name.created_hero is not None:
        curProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

creation_str_vars = []
creation_comboboxes = []

for row in range(12):

    cur_str_var = tk.StringVar()

    tk.Label(left_dropbox_frame, text=names[row], width=12).grid(row=row, column=0, padx=10, pady=5)
    combo1 = ttk.Combobox(left_dropbox_frame, textvariable=cur_str_var)
    combo1.grid(row=row, column=1, padx=10, pady=10)

    creation_str_vars.append(cur_str_var)
    creation_comboboxes.append(combo1)

    # NAMES
    if row == 0:
        combo1['textvariable'] = None
        combo1['values'] = all_hero_options
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_name)

    # RARITY
    if row == 1:
        combo1['textvariable'] = None
        combo1['values'] = list(reversed(numbers[1:6]))
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_rarity)

    # MERGES
    if row == 2:
        combo1['textvariable'] = None
        combo1['values'] = list(numbers[0:11])
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_merge)

    # ASSET
    if row == 3:
        combo1['textvariable'] = None
        combo1['values'] = iv_strs
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_asset)

    # WEAPON
    if row == 6:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_weapon)

    # REFINE
    if row == 7:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_refine)

    # ASSIST
    if row == 8:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_assist)

    # SPECIAL
    if row == 9:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_special)


for row in range(11):
    cur_str_var = tk.StringVar()

    tk.Label(right_dropbox_frame, text=names2[row], width=12).grid(row=row, column=0, padx=10, pady=5)
    combo1 = ttk.Combobox(right_dropbox_frame, textvariable=cur_str_var)
    combo1.grid(row=row, column=1, padx=10, pady=10)

    creation_str_vars.append(cur_str_var)
    creation_comboboxes.append(combo1)

    # LEVEL
    if row == 1:
        combo1['textvariable'] = None
        combo1['values'] = list(reversed(numbers[1:41]))
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_level)

    # FLAW
    if row == 3:
        combo1['textvariable'] = None
        combo1['values'] = iv_strs
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_flaw)

    # ASC ASSET
    if row == 4:
        combo1['textvariable'] = None
        #combo1['values'] = iv_strs

    if row == 6:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_askill)

    if row == 7:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_bskill)

    if row == 8:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_cskill)

def check_input(event):
    value = event.widget.get()

    if value == '':
        unit_select['values'] = all_hero_options
    else:
        data = []
        for item in all_hero_options:
            if value.lower() in item.lower():
                data.append(item)

        unit_select['values'] = data

cur_unit_selected = tk.StringVar()

handle_selection_change_name.created_hero: hero.Hero = None

curProxy = HeroProxy()

unit_select = ttk.Combobox(window, width=25, textvariable=cur_unit_selected)

'''
unit_select['values'] = all_hero_options
unit_select.bind('<KeyRelease>', check_input)
unit_select.bind("<<ComboboxSelected>>", handle_selection_change)
'''

#creation_elements = [creation_back_button, unit_select]


current_elements = []
images = []

generate_main()
#generate_creation()

window.mainloop()