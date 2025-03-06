import hero
from map import wall_crops, Map
from FEHSimulation.Unused.game import start_sim

import pandas as pd
from csv import reader, writer
import webbrowser
from math import isnan
from functools import partial
import json

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

import tkmacosx as tkm
import textwrap

import pickle

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

BLESSINGS_DICT = {"None": -1, "Fire": 0, "Water": 1, "Earth": 2, "Wind": 3, "Light": 4, "Dark": 5, "Astra": 6, "Anima": 7}

class HeroProxy:
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

        apl_hero.allySupport = intName_dict[self.a_support]

        apl_hero.summonerSupport = int(self.s_support)
        apl_hero.set_visible_stats()

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

        apl_hero.blessing = self.blessing

class SelectProxy:
    def __init__(self):
        self.team_buttons = []

        # By default, with no boxes highlighted, the value should be 0
        # Negative values correlate to the team boxes (-1, -2, -3, -4, ...)
        # Positive values correlate to the lower boxes (1, 2, 3, 4, ...)
        # 0 also correlates to the 'Undo' button, but this button is unable to be highlighted
        self.highlighted_box = 0

    def set_team_boxes(self, num_boxes):
        self.team_buttons = [0] * num_boxes
        self.highlighted_box = 0

        my_units_continue.pack_forget()

    def clear_highlighted_box(self):
        if self.highlighted_box > 0:
            map_unit_selection.my_unit_buttons[self.highlighted_box - 1].configure(bg="linen")
        if self.highlighted_box < 0:
            map_unit_selection.team_buttons[self.highlighted_box * -1 - 1].configure(bg="linen")

    def set_highlighted_box(self):
        if self.highlighted_box > 0:
            map_unit_selection.my_unit_buttons[self.highlighted_box - 1].configure(bg="RoyalBlue1")
        if self.highlighted_box < 0:
            map_unit_selection.team_buttons[self.highlighted_box * -1 - 1].configure(bg="RoyalBlue1")

    def update_button_appearance(self):
        i = 0
        while i < len(self.team_buttons):
            if self.team_buttons[i] == 0:
                map_unit_selection.team_buttons[i].configure(image=pixel, text="Empty", compound=tk.CENTER)
            else:
                img = map_unit_selection.my_unit_buttons[self.team_buttons[i] - 1].image
                txt = map_unit_selection.my_unit_buttons[self.team_buttons[i] - 1].text

                map_unit_selection.team_buttons[i].configure(image=img, text=txt, compound=tk.TOP)

            i += 1

        if sum(self.team_buttons) > 0:
            my_units_continue.pack(padx=10, side=tk.RIGHT)
        else:
            my_units_continue.pack_forget()

    def box_clicked(self, box_id):
        self.clear_highlighted_box()

        def autofill(num):
            i = 0
            while i < len(self.team_buttons):
                if self.team_buttons[i] == 0:
                    self.team_buttons[i] = num
                    break

                i += 1

        # When pressing undo button, set to
        def undo():
            # If currently highlighting a team box
            if self.highlighted_box < 0:
                self.team_buttons[self.highlighted_box * -1 - 1] = 0
            # If currently highlighting a lower box, but still in team
            elif self.highlighted_box in self.team_buttons and self.highlighted_box != 0:
                self.team_buttons = [0 if x == self.highlighted_box else x for x in self.team_buttons]
            # Else, remove first avalilable
            else:
                for i in range(len(self.team_buttons) - 1, -1, -1):
                    if self.team_buttons[i] != 0:
                        self.team_buttons[i] = 0
                        break

            self.highlighted_box = 0

        def swap(team_index, lower_num):
            index1 = team_index * -1 - 1
            index2 = self.team_buttons.index(lower_num)

            self.team_buttons[index1], self.team_buttons[index2] = self.team_buttons[index2], self.team_buttons[index1]

            self.highlighted_box = 0

        # Pressing undo button
        if box_id == 0:
            undo()

        # Now selecting a unit currently on the team
        elif box_id < 0:
            # If no box is already selected, first the first point to this box
            if self.highlighted_box == 0:
                self.highlighted_box = box_id
            # Select another box currently on the team
            elif self.highlighted_box < 0:
                if self.highlighted_box == box_id:
                    self.highlighted_box = 0
                else:
                    self.highlighted_box = box_id
            # Lower box selected
            else:
                # If lower box currently in team
                if self.highlighted_box in self.team_buttons:
                    # Swap if lower box currently in team and not currently highlighted
                    # Also happens if highlighted and selected unit are the same, no change occurs
                    swap(box_id, self.highlighted_box)
                # Else, set currently highlighted from lower with newly selected from upper boxes
                else:
                    self.team_buttons[box_id * -1 - 1] = self.highlighted_box
                    self.highlighted_box = 0

        # Now selecting a unit in lower boxes
        elif box_id > 0:
            # If no unit currently selected
            if self.highlighted_box == 0:
                # Not currently in the team and space is available
                if box_id not in self.team_buttons and 0 in self.team_buttons:
                    autofill(box_id)
                # Team currently full or already in team, just highlight this box
                else:
                    self.highlighted_box = box_id
            # If already highlighting a box in the team
            elif self.highlighted_box < 0:
                # If currently on the team, perform a swap
                if box_id in self.team_buttons:
                    swap(self.highlighted_box, box_id)
                # Else, replace unit on team with one not on team
                else:
                    self.team_buttons[self.highlighted_box * -1 - 1] = box_id
                    self.highlighted_box = 0
            # Currently highlighting another box below, just select that new box
            elif self.highlighted_box > 0:
                if self.highlighted_box == box_id:
                    self.highlighted_box = 0
                else:
                    self.highlighted_box = box_id

        self.set_highlighted_box()

        self.update_button_appearance()

        #print(self.highlighted_box)
        #print(self.team_buttons)

class SelectedOptions:

    def __init__(self):
        # Line numbers from my_units.csv
        self.player_units = []
        # Hero objects
        self.enemy_units = []

        # Json data
        self.map_data = None

        self.map_str = None

        self.season_el = ()
        self.season_ae = ()

def about():
    webbrowser.open("https://github.com/EtDet/RATA-Public", new=0, autoraise=True)

def remove_elements():
    spacer.config(fg="#797282", text="W")

    for x in current_elements:
        x.pack_forget()

    edit_button.pack_forget()
    delete_button.pack_forget()

    current_elements.clear()

    # Clear Map Canvas
    preview_canvas.delete('all')
    preview_canvas.create_text(canvas_width // 2, canvas_height // 2, text="No Map Selected", font="Arial 18 bold", fill="yellow")

    window.unbind("<MouseWheel>")

    for label in creation_labels:
        CreateToolTip(label, "")

def generate_main():
    remove_elements()

    next_button.pack_forget()

    i = 0
    while i < len(front_page_elements):
        front_page_elements[i].pack(pady=front_page_paddings[i])
        current_elements.append(front_page_elements[i])
        i += 1

def maps_on_mousewheel(event):
    map_listing_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def generate_maps():
    remove_elements()

    map_frame.pack(pady=10)
    map_listing_frame.pack(side=tk.LEFT, fill=tk.Y)
    map_preview_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    inner_frame.update_idletasks()
    map_listing_canvas.config(width=inner_frame.winfo_reqwidth())

    window.bind("<MouseWheel>", maps_on_mousewheel)

    current_elements.append(map_frame)
    current_elements.append(map_listing_frame)
    current_elements.append(map_preview_frame)

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

    #with open("my_units.csv") as f:
    #    print(f)

    unit_read = pd.read_csv("../my_units.csv", encoding='cp1252')

    for i, hrow in enumerate(unit_read.iterrows()):

        respString = "-R" if hrow[1]['Resplendent'] == True else ""

        image2 = Image.open("TestSprites/" + hrow[1]['IntName'] + respString + ".png")
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

    #print(num, build_name)

def generate_creation():
    remove_elements()

    top_frame.pack(side=tk.TOP, expand=False, fill=tk.X)
    bottom_frame.pack(side=tk.BOTTOM, expand=False, fill=tk.X)
    unit_stat_frame.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)
    dropbox_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)

    creation_build_field.pack(side=tk.RIGHT, anchor='nw', padx=10, pady=10)
    creation_make_text.pack(side=tk.RIGHT, anchor='nw', padx=10, pady=10)
    error_text.pack(side=tk.LEFT, anchor='nw', padx=10, pady=10)

    creation_labels[5].grid(row=5, column=0, padx=4, pady=10)
    creation_labels[17].grid(row=5, column=0, padx=4, pady=10)

    creation_comboboxes[5].grid(row=5, column=1, padx=4, pady=4)
    creation_comboboxes[17].grid(row=5, column=1, padx=4, pady=4)

    creation_back_button.config(command=generate_units)

    current_elements.append(unit_stat_frame)
    current_elements.append(dropbox_frame)
    current_elements.append(top_frame)
    current_elements.append(bottom_frame)

def generate_creation_edit(num):
    # Move to creation screen
    generate_creation()

    my_units = pd.read_csv("../my_units.csv", encoding='cp1252')

    row = my_units.loc[num]

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

    # Blessings
    blessing = row["Blessing"]
    if pd.isnull(blessing):
        if creation_str_vars[4].get() == "None":
            creation_comboboxes[4].set("None")
    else:
        creation_comboboxes[4].set(hero.BLESSING_NAMES[int(blessing)].capitalize())

    handle_selection_change_blessing()

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

    creation_comboboxes[5].set(s_str)
    handle_selection_change_summsupport()

    # Asset & Flaw
    asset = STAT_STR[row["Asset"]]
    flaw = STAT_STR[row["Flaw"]]

    # Neutral
    if asset == flaw:
        creation_comboboxes[3].set("None")
        handle_selection_change_asset()
    # Not Neutral
    else:
        creation_comboboxes[3].set(asset)
        handle_selection_change_asset()

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

    # Support Ally
    loaded_file = open('../supports.pkl', 'rb')
    db = pickle.load(loaded_file)

    ally_str = "None"

    for pairing in db:
        if int_name in pairing:
            ally_support = pairing[pairing.index(int_name)-1]
            ally_hero = hero.makeHero(ally_support) if ally_support is not None else None
            ally_str = ally_hero.name + ": " + ally_hero.epithet if ally_hero is not None else "None"

    creation_comboboxes[17].set(ally_str)
    handle_selection_change_allysupport()

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

    # Sacred Seal
    sseal = row["SSeal"]

    if pd.isnull(sseal):
        sseal = "None"

    creation_comboboxes[21].set(sseal)
    handle_selection_change_sseal()

    # Build Name
    build_name.set(row["Build Name"])

    # TOMORROW: CHANGE THE CREATE BUTTON TO A SAVE BUTTON
    # WHEN CLICKED, REPLACE ROW
    creation_make_button.config(text="Save", command=partial(edit_unit_in_list, num))

def generate_creation_enemy(num):
    generate_creation()

    creation_comboboxes[17].grid_forget()
    creation_comboboxes[5].grid_forget()

    creation_labels[17].grid_forget()
    creation_labels[5].grid_forget()

    clear_creation_fields()

    if selectedOptions.enemy_units[num] is not None:

        curHero = selectedOptions.enemy_units[num]

        title_name = curHero.name + ": " + curHero.epithet
        creation_comboboxes[0].set(title_name)
        handle_selection_change_name()

        rarity = curHero.rarity
        creation_comboboxes[1].set(rarity)
        handle_selection_change_rarity()

        level = curHero.level
        creation_comboboxes[13].set(level)
        handle_selection_change_level()

        merges = curHero.merges
        creation_comboboxes[2].set(merges)
        handle_selection_change_merge()

        asset = STAT_STR[curHero.asset]
        flaw = STAT_STR[curHero.flaw]

        if asset == flaw:
            creation_comboboxes[3].set("None")
            handle_selection_change_asset()
        # Not Neutral
        else:
            creation_comboboxes[3].set(asset)
            handle_selection_change_asset()

            creation_comboboxes[15].set(flaw)
            handle_selection_change_flaw()

        weapon = curHero.weapon

        # Weapon & Refine
        weapon_name = "None"
        refine_name = "None"

        if weapon is not None:
            refine_substrings = ["Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz"]
            if weapon.intName[-3:] in refine_substrings:
                weapon_name = weapon.intName[:-3]
                refine_name = weapon.intName[-3:]

        creation_comboboxes[6].set(weapon_name)
        handle_selection_change_weapon()

        creation_comboboxes[7].set(refine_name)
        handle_selection_change_refine()

        # Assist
        assist = curHero.assist
        assist_name = "None"

        if assist is not None:
            assist_name = assist.name

        creation_comboboxes[8].set(assist_name)
        handle_selection_change_assist()

        # Special
        special = curHero.special
        special_name = "None"

        if special is not None:
            special_name = special.name

        creation_comboboxes[9].set(special_name)
        handle_selection_change_special()

        # A Skill
        askill = curHero.askill
        askill_name = "None"

        if askill is not None:
            askill_name = askill.name

        creation_comboboxes[18].set(askill_name)
        handle_selection_change_askill()

        # B Skill

        bskill = curHero.bskill
        bskill_name = "None"

        if bskill is not None:
            bskill_name = bskill.name

        creation_comboboxes[19].set(bskill_name)
        handle_selection_change_bskill()

        # C Skill

        cskill = curHero.cskill
        cskill_name = "None"

        if cskill is not None:
            cskill_name = cskill.name

        creation_comboboxes[20].set(cskill_name)
        handle_selection_change_cskill()

    # We don't need these things when making enemy units
    build_name.set("ENEMY")
    creation_build_field.pack_forget()
    creation_make_text.pack_forget()

    creation_back_button.config(command=generate_enemy_building)

    creation_make_button.config(command=partial(set_enemy_unit, num))

def set_enemy_unit(num):
    selectedOptions.enemy_units[num] = handle_selection_change_name.created_hero
    selectedOptions.enemy_units[num].side = 1

    generate_enemy_building()

def delete_unit(num):

    data = pd.read_csv("../my_units.csv", encoding='cp1252')
    data = data.drop(num)
    data.to_csv("my_units.csv", index=False, encoding='cp1252')

    generate_units()

# When leaving creation menu, reset all parameters
def clear_creation_fields():
    heroProxy.reset()

    creation_image_label.config(image=pixel)
    creation_image_label.image = pixel

    handle_selection_change_name.created_hero = None

    image1_label.config(image=pixel)
    image2_label.config(image=pixel)

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
    creation_comboboxes[4]['values'] = []

    creation_comboboxes[6]['values'] = []
    creation_comboboxes[7]['values'] = []
    creation_comboboxes[8]['values'] = []
    creation_comboboxes[9]['values'] = []

    creation_comboboxes[5]['values'] = []
    creation_comboboxes[17]['values'] = []

    creation_comboboxes[18]['values'] = []
    creation_comboboxes[19]['values'] = []
    creation_comboboxes[20]['values'] = []
    creation_comboboxes[21]['values'] = []

    build_name.set("")
    error_text.config(fg='#292e36')

    # Reset save button to Create
    creation_make_button.config(text="Create", command=add_unit_to_list)

def generate_all_units_option():
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
                            "Daylight", "Noontime", "Sol", "Aether", "Blue Flame",
                            "Rising Flame", "Blazing Flame", "Growing Flame",
                            "Rising Light", "Blazing Light", "Growing Light",
                            "Rising Thunder", "Blazing Thunder", "Growing Thunder",
                            "Rising Wind", "Blazing Wind", "Growing Wind",
                            "Buckler", "Escutcheon", "Pavise", "Holy Vestments", "Sacred Cowl", "Aegis", "Miracle",
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

def get_valid_seals(cur_hero):
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

# Upon valid unit and name options, add the unit to the CSV file
def add_unit_to_list():
    hero_to_add = handle_selection_change_name.created_hero

    cur_build_name = build_name.get()

    #print(creation_str_vars[0].get(), cur_build_name)
    if creation_str_vars[0].get() != "" and build_name.get() != "":

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

        my_units_file = "../my_units.csv"
        names = pd.read_csv(my_units_file, encoding='cp1252')['Build Name'].tolist()

        # Ensure build name is unique
        if cur_build_name not in names:

            try:
                my_units_file = "../my_units.csv"

                with open(my_units_file, mode="a", newline='', encoding="cp1252") as file:
                    f_writer = writer(file)
                    f_writer.writerow(data)

                # Go back to unit selection screen
                generate_units()

                spacer.config(fg="lime", text=f'"{cur_build_name}" created successfully.')

                ally_supports = open('../supports.pkl', 'rb')
                db = pickle.load(ally_supports)

                new_db = []
                found = False

                for pairing in db:
                    if hero_to_add.intName in pairing:
                        found = True

                        if hero_to_add.allySupport not in pairing and hero_to_add.allySupport is not None:
                            temp_pairing = (hero_to_add.intName, hero_to_add.allySupport)
                            new_db.append(temp_pairing)

                        elif hero_to_add.allySupport is not None:
                            temp_pairing = pairing
                            new_db.append(temp_pairing)

                    else:
                        new_db.append(pairing)

                if not found and hero_to_add.allySupport is not None:
                    new_db.append((hero_to_add.intName, hero_to_add.allySupport))

                open("../supports.pkl", "w").close()

                db_file = open("../supports.pkl", "ab")
                pickle.dump(new_db, db_file)
                db_file.close()


            except PermissionError:
                print(f"Error: Permission denied when writing to file. Please close {my_units_file} and try again.")

        else:
            error_text.config(fg='#d60408', text="Error: Build Name Already Exists")
    else:
        error_text.config(fg='#d60408', text='Error: No Unit Selected or Build Name Empty')



def edit_unit_in_list(num):
    hero_to_add = handle_selection_change_name.created_hero

    cur_build_name = build_name.get()

    if creation_str_vars[0].get() != "" and cur_build_name != "":

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

        my_units_file = "../my_units.csv"
        names = pd.read_csv(my_units_file, encoding='cp1252')['Build Name'].tolist()

        # Ensure build name is unique, or name is unchanged
        if cur_build_name not in names or names[num] == cur_build_name:

            try:
                my_units_file = "../my_units.csv"

                with open(my_units_file, 'r', newline='', encoding="cp1252") as file:
                    f_reader = reader(file)
                    read_data = list(f_reader)

                read_data[num + 1] = data

                with open(my_units_file, mode="w", newline='', encoding="cp1252") as file:
                    f_writer = writer(file)
                    f_writer.writerows(read_data)

                # Go back to unit selection screen
                generate_units()

                spacer.config(fg="lime", text=f'"{cur_build_name}" saved successfully.')

                ally_supports = open('../supports.pkl', 'rb')
                db = pickle.load(ally_supports)

                new_db = []
                found = False

                for pairing in db:
                    if hero_to_add.intName in pairing:
                        found = True

                        if hero_to_add.allySupport not in pairing and hero_to_add.allySupport is not None:
                            temp_pairing = (hero_to_add.intName, hero_to_add.allySupport)
                            new_db.append(temp_pairing)

                        elif hero_to_add.allySupport is not None:
                            temp_pairing = pairing
                            new_db.append(temp_pairing)

                    else:
                        new_db.append(pairing)

                if not found and hero_to_add.allySupport is not None:
                    new_db.append((hero_to_add.intName, hero_to_add.allySupport))

                open("../supports.pkl", "w").close()

                db_file = open("../supports.pkl", "ab")
                pickle.dump(new_db, db_file)
                db_file.close()

            except PermissionError:
                print(f"Error: Permission denied when writing to file. Please close {my_units_file} and try again.")

        else:
            error_text.config(fg='#d60408', text="Error: Build Name Already Exists")
    else:
        error_text.config(fg='#d60408', text='Error: No Unit Selected or Build Name Empty')

# Scroll list of units when editing
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

# Scroll list of units after map selection
def my_canvas_on_mousewheel(event):
    canvas = my_units_canvas
    delta = -1 * int(event.delta / 100)

    # Scroll the canvas vertically
    canvas.yview_scroll(delta, "units")

    # Prevent scrolling upwards if we're already at the top
    if delta < 0:
        top, bottom = canvas.yview()
        if top <= 0:
            canvas.yview_moveto(0)

# BEGIN SIMULATION HERE, WITH GIVEN OPTION VALUES
def begin_simulation():
    player_ints = selectedOptions.player_units

    # Prepare player team
    my_units_file = pd.read_csv("../my_units.csv", encoding="cp1252")

    player_units = []

    i = 0
    #print(player_ints)
    while i < len(player_ints):
        if player_ints[i] != 0:
            row = my_units_file.loc[player_ints[i] - 1]

            cur_hero = hero.makeHero(row["IntName"])

            cur_hero.set_rarity(row["Rarity"])
            cur_hero.set_IVs(row["Asset"], row["Flaw"], row["Ascended"])
            cur_hero.set_merges(row["Merges"])
            cur_hero.set_dragonflowers(row["Dragonflowers"])

            cur_hero.set_level(row["Level"])

            cur_hero.summonerSupport = int(row["SSupport"]) if not pd.isnull(row["SSupport"]) else 0

            cur_hero.set_visible_stats()

            if not pd.isnull(row["Weapon"]): cur_hero.set_skill(hero.makeWeapon(row["Weapon"]), WEAPON)
            if not pd.isnull(row["Assist"]): cur_hero.set_skill(hero.makeAssist(row["Assist"]), ASSIST)
            if not pd.isnull(row["Special"]): cur_hero.set_skill(hero.makeSpecial(row["Special"]), SPECIAL)
            if not pd.isnull(row["ASkill"]): cur_hero.set_skill(hero.makeSkill(row["ASkill"]), ASKILL)
            if not pd.isnull(row["BSkill"]): cur_hero.set_skill(hero.makeSkill(row["BSkill"]), BSKILL)
            if not pd.isnull(row["CSkill"]): cur_hero.set_skill(hero.makeSkill(row["CSkill"]), CSKILL)
            if not pd.isnull(row["SSeal"]): cur_hero.set_skill(hero.makeSeal(row["SSeal"]), CSKILL)

            if not pd.isnull(row["Blessing"]): cur_hero.blessing = hero.Blessing((int(row["Blessing"]), 0, 0))

            player_units.append(cur_hero)

        i += 1


    enemy_units = selectedOptions.enemy_units
    cleaned_enemy_units = []

    for unit in enemy_units:
        if unit is not None:
            cleaned_enemy_units.append(unit)

    map = Map(0)
    map.define_map(selectedOptions.map_data)

    season = selectedOptions.season_el + selectedOptions.season_ae

    window.destroy()

    start_sim(player_units, cleaned_enemy_units, map, selectedOptions.map_str, season)

    window.mainloop()

# window
window = tk.Tk()
#window.resizable(False, False)
window.geometry('800x600')
window.title('FEH Sim')
window.configure(background='#797282')
#window.iconbitmap("Sprites/Marth.ico")

# MAIN MENU ELEMENTS
title_label = tk.Label(master=window, text='RATA - An FE: Heroes Simulator', font='Helvetica 24', relief="raised")
subtitle_label = tk.Label(master=window, text='By CloudX (2024)', font='Helvetica 18', relief="raised")
version_label = tk.Label(master=window, text="Ver 1.0.8 - Year 2 Complete", font='Helvetica 12', relief="raised")

start_button = tkm.Button(window, command=generate_maps, height=40, width=255, text="Level Select", font="Helvetica 14", cursor="hand2", bg='blue', fg='white', borderless=True, takefocus=0)
units_button = tkm.Button(window, command=generate_units, height=40, width=255, text="My Units", font="Helvetica 14", cursor="hand2", bg='blue', fg='white', borderless=True)
help_button = tkm.Button(window, command=about, height=40, width=255, text="GitHub Page", font="Helvetica 14", cursor="hand2", bg='blue', fg='white', borderless=True)
quit_button = tkm.Button(window, command=window.destroy, height=40, width=255, text="Close", font="Helvetica 14", cursor="hand2", bg='red', fg='white', borderless=True)

front_page_elements = [title_label, subtitle_label, version_label, start_button, units_button, help_button, quit_button]
front_page_paddings = [(80, 5), (10, 5), (5, 5), (20, 10), (0, 10), (0, 10), (0, 10)]

# MAP SELECTION ELEMENTS

# Top frame, displays title
map_frame = tk.Frame(window, bg='#797282')

# Left frame, displays selectable maps
map_listing_frame = tk.Frame(window, bg='#770000', borderwidth=0)

# Left canvas
map_listing_canvas = tk.Canvas(map_listing_frame, bg='#004400', borderwidth=0, highlightthickness=0)
map_listing_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

map_scrollbar = tk.Scrollbar(map_listing_frame, bg="black", orient='vertical', command=map_listing_canvas.yview)
map_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

map_listing_canvas.configure(yscrollcommand=map_scrollbar.set)
map_listing_canvas.bind('<Configure>', lambda e: map_listing_canvas.configure(scrollregion=map_listing_canvas.bbox("all")))

inner_frame = tk.Frame(map_listing_canvas, bg="#10141c")

map_listing_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

# Set current map looked at in the preview canvas
def set_map_canvas(map_data, curImage, map_str):
    #print(map_data["name"])

    preview_canvas.delete('all')

    # Place liquid background
    liquid_texture = "WavePattern.png"

    if "liquid" in map_data:
        liquid_texture = map_data["liquid"]

    liquid_image = Image.open("CombatSprites/" + liquid_texture)
    liquid_photo = ImageTk.PhotoImage(liquid_image)
    preview_canvas.create_image(0, 0, anchor=tk.NW, image=liquid_photo)

    set_map_canvas.liquid = liquid_photo

    # Place map
    map_image = ImageTk.getimage(curImage)
    map_image = map_image.resize((canvas_width, canvas_height), Image.LANCZOS)
    map_photo = ImageTk.PhotoImage(map_image)
    preview_canvas.create_image(2, 2, anchor=tk.NW, image=map_photo)

    set_map_canvas.image = map_photo

    # Place walls
    set_map_canvas.walls = []

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
            cur_wall = cur_wall.resize((58, 58), Image.LANCZOS)
            cur_photo = ImageTk.PhotoImage(cur_wall)

            preview_canvas.create_image(x_comp * 58 + 2, canvas_height - (y_comp + 1) * 58 + 2, anchor=tk.NW, image=cur_photo)

            set_map_canvas.walls.append(cur_photo)

        for tile_num in map_data["struct_walls"]["twoBreak"]:

            x_comp = tile_num % 6
            y_comp = tile_num // 6

            result = [-1, -1, -1, -1]

            # Get tile num for each adjacent tile (NSEW)
            if y_comp + 1 < 8: result[0] = tile_num + 6
            if y_comp - 1 >= 0: result[1] = tile_num - 6
            if x_comp + 1 < 6: result[2] = tile_num + 1
            if x_comp - 1 >= 0: result[3] = tile_num - 1

            wall_type = 0
            iterator = 1

            # If adjacent tile has a wall, add unique value to indicate that direction
            # N - 1
            # S - 2
            # E - 4
            # W - 8
            for adj_tile in result:
                if adj_tile in all_walls:
                    wall_type += iterator

                iterator *= 2

            # Move one down on the wall crops to the variant with 2 health
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
            cur_wall = cur_wall.resize((58, 58), Image.LANCZOS)
            cur_photo = ImageTk.PhotoImage(cur_wall)

            preview_canvas.create_image(x_comp * 58 + 2, canvas_height - (y_comp + 1) * 58 + 2, anchor=tk.NW, image=cur_photo)

            set_map_canvas.walls.append(cur_photo)

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
            cur_wall = cur_wall.resize((58, 58), Image.LANCZOS)
            cur_photo = ImageTk.PhotoImage(cur_wall)

            preview_canvas.create_image(x_comp * 58 + 2, canvas_height - (y_comp + 1) * 58 + 2, anchor=tk.NW, image=cur_photo)

            set_map_canvas.walls.append(cur_photo)

        # Change continue button

    # Starting positions
    i = 1
    for tile_num in map_data["playerStart"]:
        x_comp = tile_num % 6
        y_comp = tile_num // 6

        preview_canvas.create_rectangle((x_comp * 58 + 2, canvas_height - (y_comp + 1) * 58 + 2, (x_comp + 1) * 58 + 2, canvas_height - (y_comp + 0) * 58 + 2), fill="blue")

        preview_canvas.create_text(x_comp * 58 + 27, canvas_height - (y_comp + 1) * 58 + 20, text=i, anchor=tk.NW, font="Arial 16 bold", fill="yellow")
        i += 1

    i = 1
    for tile_num in map_data["enemyStart"]:
        x_comp = tile_num % 6
        y_comp = tile_num // 6

        preview_canvas.create_rectangle((x_comp * 58 + 2, canvas_height - (y_comp + 1) * 58 + 2, (x_comp + 1) * 58 + 2, canvas_height - (y_comp + 0) * 58 + 2), fill="red")

        preview_canvas.create_text(x_comp * 58 + 27, canvas_height - (y_comp + 1) * 58 + 20, text=i, anchor=tk.NW, font="Arial 16 bold", fill="yellow")
        i += 1

    #print("I can't lose in my Fire Stingray!")

    selectedOptions.map_data = map_data

    selectedOptions.map_str = map_str

    next_button.pack()
    next_button.config(command=map_unit_selection)

# Add buttons for current arena maps, update when more maps are added
for i in range(24):
    with open("Maps/Arena Maps/Map_Z" + str(i+1).zfill(4) + ".json") as read_file: data = json.load(read_file)
    map_name = data["name"]

    button_color = "#224763"
    select_color = "#347deb"
    if "Volcano" in map_name:
        button_color = "#fcba03"
        select_color = "red"

    map_str = "Map_Z" + str(i+1).zfill(4)

    map_image = Image.open("Maps/Arena Maps/" + map_str + ".png")
    map_image = map_image.resize((300, 400), Image.LANCZOS)
    curImage = ImageTk.PhotoImage(map_image)

    button = tkm.Button(master=inner_frame,
                       command=partial(set_map_canvas, data, curImage, map_str),
                       image=curImage,
                       bg=button_color,
                       fg="#dff4f5",
                       font=("Arial 20 bold"),
                       activeforeground="#dedede",
                       activebackground=select_color,
                       height=60,
                       width=300,
                       text=map_name,
                       bordercolor="LightSteelBlue4"
                       #compound="center"
                       )
    button.image = curImage
    button.pack(padx=10, pady=5)



# Right frame, displays preview of currently selected map
map_preview_frame = tk.Frame(window, bg='#293240')

pixel = tk.PhotoImage(width=1, height=1)

canvas_width = 345
canvas_height = 460

preview_canvas = tk.Canvas(map_preview_frame, width=canvas_width, height=canvas_height, bg="#334455", highlightbackground="#111122")
preview_canvas.pack(pady=10)

preview_canvas.create_text(canvas_width//2, canvas_height//2, text="No Map Selected", font="Arial 18 bold", fill="yellow")

next_button = tk.Button(map_preview_frame, text="Continue", command=remove_elements)

map_top_label = tk.Label(map_frame, text='Arena Maps', font='Arial 18 bold')
map_top_label.pack(side='top')

map_back_button = tk.Button(map_frame, text='<- Back', command=generate_main, width=10)
map_back_button.pack(side='left', padx=(0, 700))

# UNIT SELECTION (AFTER MAP SELECTED)

unit_select_top_frame = tk.Frame(window, bg="#797282")

unit_select_label = tk.Label(unit_select_top_frame, text='Unit Selection', font='Arial 18 bold')
unit_select_label.pack(side='top')

unit_select_back_button = tk.Button(unit_select_top_frame, text='<- Back', command=generate_maps, width=10)
unit_select_back_button.pack(side='left', padx=(10, 200))

unit_select_chosen_frame = tk.Frame(window, bg="#686171")

def map_unit_selection():

    map_data = selectedOptions.map_data

    #print("Continuing with: " + map_data["name"])

    # Remove whatever's currently placed
    remove_elements()
    next_button.pack_forget()

    # Create buttons for unit_select_chosen_frame
    i = 0
    num_players = len(map_data["playerStart"])

    selectProxy.set_team_boxes(num_players)

    map_unit_selection.team_buttons = []
    map_unit_selection.my_unit_buttons = []

    while i < num_players:
        cur_button = tkm.Button(master=unit_select_chosen_frame,
                               bg="linen",
                               image=pixel,
                               text="Empty",
                               width=110,
                               height=110,
                               command=partial(selectProxy.box_clicked, i * -1 - 1),
                               #anchor=tk.S,
                               font = 'Helvetica 10',
                               borderless=True
                               )
        cur_button.pack(side='left', pady=10, padx=10)

        current_elements.append(cur_button)

        map_unit_selection.team_buttons.append(cur_button)

        i += 1

    # Create buttons for my_units_inner_frame

    for widget in my_units_inner_frame.winfo_children():
        widget.grid_remove()

    width = 87
    height = 87

    pre_button = tk.Button(master=my_units_inner_frame,
                           bg="linen",
                           command=partial(selectProxy.box_clicked, 0),
                           text="Undo",
                           image=pixel,
                           compound=tk.TOP,
                           height=height,
                           width=width,
                           font='Helvetica 8')
    pre_button.image = pixel
    pre_button.grid(row=0, column=0, padx=4, pady=4)

    row, col = 0, 1
    unit_read = pd.read_csv("../my_units.csv", encoding='cp1252')
    for i, hrow, in enumerate(unit_read.iterrows()):
        respString = "-R" if hrow[1]['Resplendent'] == True else ""

        cur_image = Image.open("TestSprites/" + hrow[1]['IntName'] + respString + ".png")
        new_width = int(cur_image.width * 0.35)
        new_height = int(cur_image.height * 0.35)

        cur_image = cur_image.resize((new_width, new_height), Image.LANCZOS)
        cur_photo = ImageTk.PhotoImage(cur_image)

        build_name = str(hrow[1]['Build Name'])

        tempButton = tk.Button(master=my_units_inner_frame,
                               bg="linen",
                               command=partial(selectProxy.box_clicked, i + 1),
                               image=cur_photo,
                               text=build_name,
                               compound=tk.TOP,
                               height=height,
                               width=width,
                               font='Helvetica 8')
        tempButton.image = cur_photo
        tempButton.text = build_name
        tempButton.grid(row=row, column=col, padx=4, pady=4)

        map_unit_selection.my_unit_buttons.append(tempButton)

        col += 1
        if col % 7 == 0:
            row += 1
            col = 0

    my_units_frame.update_idletasks()
    my_units_canvas.configure(scrollregion=my_units_canvas.bbox("all"))
    window.bind_all("<MouseWheel>", my_canvas_on_mousewheel)

    unit_select_top_frame.pack(pady=10, fill=tk.X)
    unit_select_chosen_frame.pack(pady=5)
    my_units_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=(5, 15))

    current_elements.append(unit_select_top_frame)
    current_elements.append(unit_select_chosen_frame)
    current_elements.append(my_units_frame)

    # I remember...

    if sum(selectedOptions.player_units) > 0:
        selectProxy.team_buttons = selectedOptions.player_units[:]

        selectProxy.update_button_appearance()


map_unit_selection.team_buttons = []
map_unit_selection.my_unit_buttons = []

my_units_frame = tk.Frame(window, bg="#796171")

my_units_canvas = tk.Canvas(my_units_frame, bg="#686171", borderwidth=0, highlightthickness=0)
my_units_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

my_units_scrollbar = tk.Scrollbar(my_units_frame, bg="black", orient='vertical', command=my_units_canvas.yview)
my_units_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

my_units_canvas.configure(yscrollcommand=my_units_scrollbar.set)
my_units_canvas.bind('<Configure>', lambda e: my_units_canvas.configure(scrollregion=my_units_canvas.bbox("all")))

my_units_inner_frame = tk.Frame(my_units_canvas, bg="#687271")
my_units_canvas.create_window((0, 0), window=my_units_inner_frame, anchor="nw")

# Build the individual enemy units from here
def generate_enemy_building():
    remove_elements()

    #print("Selected Units: ", selectProxy.team_buttons)

    #print(selectedOptions.enemy_units)

    selectedOptions.player_units = selectProxy.team_buttons[:]

    # If enemy team is ready, allow for the simulation to begin
    if any(value is not None for value in selectedOptions.enemy_units):
        proceed_button.pack(side='right', padx=10)
    else:
        proceed_button.pack_forget()

    enemy_top.pack(pady=10, fill=tk.X)
    enemy_main_frame.pack(pady=(150, 10))
    enemy_remove_frame.pack(pady=(0, 0))

    season_frame.pack(pady=(10,0))

    current_elements.append(season_frame)
    current_elements.append(enemy_top)
    current_elements.append(enemy_main_frame)
    current_elements.append(enemy_remove_frame)

    i = 0
    num_enemies = len(selectedOptions.map_data["playerStart"])

    # Get enemy unit slots prepared
    enemy_units = []
    while i < num_enemies:
        # Move over whatever can fit within the length
        if i < len(selectedOptions.enemy_units):
            enemy_units.append(selectedOptions.enemy_units[i])
        else:
            enemy_units.append(None)
        i += 1

    selectedOptions.enemy_units = enemy_units

    i = 0
    while i < num_enemies:
        if selectedOptions.enemy_units[i] is not None:
            respString = "-R" if selectedOptions.enemy_units[i].resp else ""

            cur_image = Image.open("TestSprites/" + selectedOptions.enemy_units[i].intName + respString + ".png")
            new_width = int(cur_image.width * 0.35)
            new_height = int(cur_image.height * 0.35)

            cur_image = cur_image.resize((new_width, new_height), Image.LANCZOS)
            cur_photo = ImageTk.PhotoImage(cur_image)

            cur_name = selectedOptions.enemy_units[i].name
        else:
            cur_photo = pixel
            cur_name = "Empty"

        temp_button = tk.Button(enemy_main_frame,
                                command=partial(generate_creation_enemy, i),
                                image=cur_photo,
                                width=85,
                                height=85,
                                text=cur_name,
                                compound=tk.TOP)
        temp_button.image = cur_photo
        temp_button.pack(padx=7, pady=7, side=tk.LEFT)

        current_elements.append(temp_button)

        i += 1

    i = 0
    while i < num_enemies:
        temp_button = tk.Button(enemy_remove_frame,
                                command=partial(remove_enemy, i),
                                image=pixel,
                                width=85,
                                height=40,
                                text="Remove",
                                compound=tk.TOP)
        temp_button.pack(padx=7, pady=7, side=tk.LEFT)

        current_elements.append(temp_button)

        i += 1

def remove_enemy(num):
    selectedOptions.enemy_units[num] = None

    generate_enemy_building()
    # update buttons

my_units_continue = tk.Button(unit_select_top_frame, command=generate_enemy_building, text="Continue ->", width=10)

# ENEMY SETTING

enemy_top = tk.Frame(window, bg="#797282")

enemy_select_label = tk.Label(enemy_top, text='Enemy Building', font='Arial 18 bold')
enemy_select_label.pack(side='top')

enemy_back_button = tk.Button(enemy_top, text='<- Back', command=map_unit_selection, width=10)
enemy_back_button.pack(side='left', padx=10)

enemy_main_frame = tk.Frame(window, bg="#686171")

enemy_remove_frame = tk.Frame(window, bg="firebrick3")


def handle_season_elemental(event=None):
    selected_value = elemental_str_var.get()

    el_season = ()

    if selected_value == "Fire/Water":
        el_season = (0, 1)
    elif selected_value == "Fire/Earth":
        el_season = (0, 2)
    elif selected_value == "Fire/Wind":
        el_season = (0, 3)
    elif selected_value == "Water/Earth":
        el_season = (1, 2)
    elif selected_value == "Water/Wind":
        el_season = (1, 3)
    elif selected_value == "Earth/Wind":
        el_season = (2, 3)

    selectedOptions.season_el = el_season

    return

def handle_season_aether(event=None):
    selected_value = aether_str_var.get()

    ae_season = ()

    if selected_value == "Light/Dark":
        ae_season = (4, 5)
    if selected_value == "Astra/Anima":
        ae_season = (6, 7)

    selectedOptions.season_ae = ae_season

    return

season_frame = tk.Frame(window, bg="#797282")

elemental_label = tk.Label(season_frame, text="Elemental Season:")
elemental_label.pack(side='left', pady=10)

elemental_str_var = tk.StringVar()
elemental_season_combobox = ttk.Combobox(season_frame, textvariable=elemental_str_var)
elemental_season_combobox.pack(side='left', padx=(10,20))
elemental_season_combobox['values'] = ["None", "Fire/Water", "Fire/Earth", "Fire/Wind", "Water/Earth", "Water/Wind", "Earth/Wind"]
elemental_season_combobox.bind("<<ComboboxSelected>>", handle_season_elemental)

aether_label = tk.Label(season_frame, text="Aether Season:")
aether_label.pack(side='left', padx=(20,10))

aether_str_var = tk.StringVar()
aether_season_combobox = ttk.Combobox(season_frame, textvariable=aether_str_var)
aether_season_combobox.pack(side='left')
aether_season_combobox['values'] = ["None", "Light/Dark", "Astra/Anima"]
aether_season_combobox.bind("<<ComboboxSelected>>", handle_season_aether)




proceed_button = tk.Button(enemy_top, command=begin_simulation, text='Proceed', bg='chartreuse2', width=10)

# UNIT CREATION/EDITING ELEMENTS

search_frame = tk.Frame(window, bg='#797282')
back_button = tk.Button(search_frame, text='<- Back', command=generate_main, width=10)
back_button.pack(side='left')

# RE-ADD ONCE READY

#name_search_label = ttk.Label(master=search_frame, text='Name Search:')
#name_search_label.pack(side='left', padx=(25, 5))

#search_string = tk.StringVar()
#search_bar = tk.Entry(search_frame, textvariable=search_string, width=30)
#search_bar.pack(side='left', padx=(5,20))

#search_button = tk.Button(search_frame, text='Search', width=15)
#search_button.pack(side='left')

select_frame = tk.Frame(window, bg='#797282')
edit_button = tk.Button(select_frame, text='Edit', command=generate_main, width=10)
delete_button = tk.Button(select_frame, text='Delete', command=delete_unit, width=10, bg="#e64337")

spacer = tk.Label(select_frame, text="W", font=("Arial 14"), bg='#797282', fg='#797282')
spacer.pack(side=tk.LEFT)


# Canvas
unit_canvas = tk.Canvas(window, bg="#9ea8b8")

# Scrollbar, for Canvas
unit_scrollbar = tk.Scrollbar(window, orient='vertical', command=unit_canvas.yview)

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
creation_make_text = tk.Label(bottom_frame, text='Build Name: ', width=10)


error_text = tk.Label(bottom_frame, text='Error: No Unit Selected or Build Name Empty', bg='#292e36', fg='#292e36', font="Helvetica 10 bold")


unit_picked = tk.StringVar()
unit_picked.set("No Hero Selected")

creation_image_label = tk.Label(unit_stat_frame, image=pixel, textvariable=unit_picked, font= "Helvetica 13", compound=tk.TOP, height=200, width=200, bg='#728275', relief=tk.RAISED)
creation_image_label.pack(padx=10, pady=10)

creation_icon_window = tk.Frame(unit_stat_frame, bg='#070708', relief=tk.RAISED)

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


image1_label = tk.Label(creation_icon_window, image=pixel, height=20, width=20, bg='#070708')
image1_label.pack(side=tk.LEFT, padx=5, pady=5)

image2_label = tk.Label(creation_icon_window, image=pixel, height=20, width=20, bg='#070708')
image2_label.pack(side=tk.LEFT, padx=5, pady=5)


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


names = ["Unit",         "Rarity", "Merge",    "Asset", "Blessing",   "S-Support", "Weapon",  "Refine",  "Assist",  "Special",     "Emblem",  "Emblem Merge"]
names2 = ["Resplendent", "Level",  "DFlowers", "Flaw",  "Asc. Asset", "A-Support", "A Skill", "B Skill", "C Skill", "Sacred Seal", "X Skill", "Aided"]

creation_str_vars = []

all_hero_options, intName_dict = generate_all_units_option()

numbers = list(range(41))
iv_strs = ["None", "HP", "Atk", "Spd", "Def", "Res"]

left_dropbox_frame = tk.Frame(dropbox_frame, bg="#a5b7c2")
right_dropbox_frame = tk.Frame(dropbox_frame, bg="#a5b7c2")

left_dropbox_frame.pack(padx=8, pady=7, side=tk.LEFT, anchor='nw')
right_dropbox_frame.pack(padx=8, pady=7, side=tk.RIGHT, anchor='ne')

def handle_selection_change_name(event=None):
    # Get name selected
    selected_value = creation_str_vars[0].get()

    # Get internal name from name + epithet
    cur_intName = intName_dict[selected_value]

    # Set who this unit is on the proxy
    heroProxy.full_name = selected_value

    # Get image of selected unit
    cur_image = Image.open("TestSprites/" + cur_intName + ".png")
    resized_image = cur_image.resize((int(cur_image.width / 1.3), int(cur_image.height / 1.3)), Image.LANCZOS)
    curPhoto = ImageTk.PhotoImage(resized_image)
    creation_image_label.config(image=curPhoto)
    creation_image_label.image = curPhoto

    # Actual Hero object
    madeHero: hero.Hero = hero.makeHero(cur_intName)

    # Set default value in ComboBoxes upon first Hero selection
    if handle_selection_change_name.created_hero is None:

        # Set default rarity
        creation_str_vars[1].set(min(5, heroProxy.rarity))

        # Set default merge
        creation_str_vars[2].set(max(0, heroProxy.merge))

        # Set default Asset
        creation_str_vars[3].set(STAT_STR[heroProxy.asset])

        # Set default Flaw
        creation_str_vars[15].set(STAT_STR[heroProxy.flaw])

        # Set default Asc Asset
        #creation_str_vars[16].set(STAT_STR[curProxy.asc_asset])

        # Set default level
        creation_str_vars[13].set(min(40, heroProxy.level))

    if madeHero.blessing is None:
        creation_str_vars[4].set("None")
        creation_comboboxes[4]['values'] = ["None", "Fire", "Water", "Earth", "Wind"]
    else:
        if madeHero.blessing.boostType != 0:
            creation_str_vars[4].set(madeHero.blessing.toString())
        creation_comboboxes[4]['values'] = []

    heroProxy.blessing = madeHero.blessing

    # Generate all possible weapons for selected Hero
    weapons = get_valid_weapons(madeHero)

    # If newly selected character can't wield what's currently in the box, remove it
    if creation_str_vars[6].get() not in weapons:
        # This should be no weapon by default
        heroProxy.weapon = None
        creation_str_vars[6].set("None")

        # Reset what refines should be available too
        creation_str_vars[7].set("None")
        creation_comboboxes[7]['values'] = []

    # Set allowed weapons
    creation_comboboxes[6]['values'] = weapons

    if heroProxy.weapon is not None:
        CreateToolTip(creation_labels[6], heroProxy.weapon.desc)
    else:
        CreateToolTip(creation_labels[6], "")

    # Generate all possible assist skills
    assists = get_valid_assists(madeHero)

    if creation_str_vars[8].get() not in assists:
        heroProxy.assist = None
        creation_str_vars[8].set("None")

    # Set allowed assists
    creation_comboboxes[8]['values'] = assists

    if heroProxy.assist is not None:
        CreateToolTip(creation_labels[8], heroProxy.assist.desc)
    else:
        CreateToolTip(creation_labels[8], "")

    # Generate all possible special skills
    specials = get_valid_specials(madeHero)

    if creation_str_vars[9].get() not in specials:
        heroProxy.special = None
        creation_str_vars[9].set("None")

    # Set allowed assists
    creation_comboboxes[9]['values'] = specials

    if heroProxy.special is not None:
        CreateToolTip(creation_labels[9], heroProxy.special.desc)
    else:
        CreateToolTip(creation_labels[9], "")

    # ABC Skills
    a_sk, b_sk, c_sk = get_valid_abc_skills(madeHero)

    # Reset a skills
    if creation_str_vars[18].get() not in a_sk:
        heroProxy.askill = None
        creation_str_vars[18].set("None")

    # Set allowed a skills
    creation_comboboxes[18]['values'] = a_sk

    # Reset b skills
    if creation_str_vars[19].get() not in b_sk:
        heroProxy.bskill = None
        creation_str_vars[19].set("None")

    # Set allowed b skills
    creation_comboboxes[19]['values'] = b_sk

    # Reset c skills
    if creation_str_vars[20].get() not in c_sk:
        heroProxy.cskill = None
        creation_str_vars[20].set("None")

    # Set allowed c skills
    creation_comboboxes[20]['values'] = c_sk

    if heroProxy.askill is not None:
        CreateToolTip(creation_labels[18], heroProxy.askill.desc)
    else:
        CreateToolTip(creation_labels[18], "")

    if heroProxy.bskill is not None:
        CreateToolTip(creation_labels[19], heroProxy.bskill.desc)
    else:
        CreateToolTip(creation_labels[19], "")

    if heroProxy.cskill is not None:
        CreateToolTip(creation_labels[20], heroProxy.cskill.desc)
    else:
        CreateToolTip(creation_labels[20], "")

    # Get valid sacred seals
    s_seals = get_valid_seals(madeHero)

    # Reset sacred seal
    if creation_str_vars[21].get() not in s_seals:
        heroProxy.sSeal = None
        creation_str_vars[21].set("None")

    # Set allowed sacred seals
    creation_comboboxes[21]['values'] = s_seals

    # Set Ally Support Partner
    if madeHero.allySupport is not None:
        temp_ally = hero.makeHero(madeHero.allySupport)
        temp_str = temp_ally.name + ": " + temp_ally.epithet
        heroProxy.a_support = temp_str
    else:
        temp_str = "None"

    creation_str_vars[17].set(temp_str)

    # Valid support partners for a hero should be all heroes minus themselves
    creation_comboboxes[17]['values'] = ["None"] + [support_names for support_names in all_hero_options if support_names != madeHero.name + ": "  + madeHero.epithet]

    # Set Summoner Support Rank
    creation_str_vars[5].set("None")

    creation_comboboxes[5]['values'] = ["None", "Rank C", "Rank B", "Rank A", "Rank S"]

    handle_selection_change_name.created_hero = madeHero
    heroProxy.apply_proxy(madeHero)

    image1_label.config(image=move_icons[madeHero.move])
    image2_label.config(image=weapon_icons[hero.weapons[madeHero.wpnType][0 ]])

    unit_picked.set("")

    star_var = "✰" * heroProxy.rarity
    unit_name.set(f"{selected_value}\n{star_var}")

    merge_str = ""
    if heroProxy.merge > 0:
        merge_str = "+" + str(heroProxy.merge)

    unit_stats.set(f"Lv. {heroProxy.level}{merge_str}\n+0 Flowers")

    #unit_stats.set(f"Lv. {curProxy.level}\n+0 Flowers")

    i = 0
    while i < 5:
        creation_stats[i].set(stat_strings[i] + str(madeHero.visible_stats[i]))
        i += 1

def handle_selection_change_rarity(event=None):
    selected_value = creation_str_vars[1].get()
    #print(f"You selected: {selected_value}")

    heroProxy.rarity = int(selected_value)

    if handle_selection_change_name.created_hero is not None:
        star_var = "✰" * int(selected_value)
        unit_name.set(f"{heroProxy.full_name}\n{star_var}")

        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_level(event=None):
    selected_value = creation_str_vars[13].get()
    #print(f"You selected: {selected_value}")

    heroProxy.level = int(selected_value)

    if handle_selection_change_name.created_hero is not None:
        merge_str = ""
        if heroProxy.merge > 0:
            merge_str = "+" + str(heroProxy.merge)

        unit_stats.set(f"Lv. {selected_value}{merge_str}\n+0 Flowers")

        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_merge(event=None):
    selected_value = creation_str_vars[2].get()
    #print(f"You selected: {selected_value}")

    heroProxy.merge = int(selected_value)

    if handle_selection_change_name.created_hero is not None:

        merge_str = ""
        if heroProxy.merge > 0:
            merge_str = "+" + selected_value

        unit_stats.set(f"Lv. {heroProxy.level}{merge_str}\n+{heroProxy.dflowers} Flowers")

        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_asset(event=None):
    selected_value = creation_str_vars[3].get()
    #print(f"You selected: {selected_value}")

    stat_int = STATS[selected_value]

    # Set asc asset to new value if not present (asset same as asc_asset)
    if heroProxy.asset == heroProxy.asc_asset:
        heroProxy.asc_asset = stat_int

    # Set new asset value
    heroProxy.asset = stat_int

    # If this overlaps with the current flaw value
    if heroProxy.flaw == heroProxy.asset or heroProxy.flaw == -1:
        # Move flaw to next possible stat
        heroProxy.flaw = (STATS[selected_value] + 1) % 5

    if heroProxy.asset == -1:
        heroProxy.flaw = -1

    creation_str_vars[15].set(STAT_STR[heroProxy.flaw])

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_flaw(event=None):
    selected_value = creation_str_vars[15].get()
    #print(f"You selected: {selected_value}")

    stat_int = STATS[selected_value]

    heroProxy.flaw = stat_int

    if heroProxy.asset == heroProxy.flaw or heroProxy.asset == -1:
        #print("homer")

        heroProxy.asset = (stat_int + 1) % 5
        heroProxy.asc_asset = (stat_int + 1) % 5

    if heroProxy.flaw == -1:
        heroProxy.asset = -1

    creation_str_vars[3].set(STAT_STR[heroProxy.asset])

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_blessing(event=None):
    selected_value = creation_str_vars[4].get()

    if selected_value == "None":
        heroProxy.blessing = None
    elif selected_value in BLESSINGS_DICT:
        heroProxy.blessing = hero.Blessing((BLESSINGS_DICT[selected_value], 0, 0))

    heroProxy.apply_proxy(handle_selection_change_name.created_hero)

def handle_selection_change_allysupport(event=None):
    selected_value = creation_str_vars[17].get()

    if selected_value != "None":
        heroProxy.a_support = selected_value
    else:
        heroProxy.a_support = None

    heroProxy.apply_proxy(handle_selection_change_name.created_hero)

def handle_selection_change_summsupport(event=None):
    selected_value = creation_str_vars[5].get()

    if selected_value == "None":
        heroProxy.s_support = 0
    if selected_value == "Rank C":
        heroProxy.s_support = 1
    if selected_value == "Rank B":
        heroProxy.s_support = 2
    if selected_value == "Rank A":
        heroProxy.s_support = 3
    if selected_value == "Rank S":
        heroProxy.s_support = 4

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_weapon(event=None):
    selected_value = creation_str_vars[6].get()
    #print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        heroProxy.weapon = hero.makeWeapon(selected_value)
    else:
        heroProxy.weapon = None

    heroProxy.refine = ""

    if heroProxy.weapon is not None:
        CreateToolTip(creation_labels[6], heroProxy.weapon.desc)
    else:
        CreateToolTip(creation_labels[6], "")

    # Set valid refines for this given weapon
    refines_arr = get_valid_refines(selected_value)
    creation_str_vars[7].set("None")
    creation_comboboxes[7]['values'] = refines_arr

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

def handle_selection_change_refine(event=None):
    selected_value = creation_str_vars[7].get()
    #print(f"You selected: {selected_value}")

    if selected_value != "None":
        heroProxy.refine = selected_value
    else:
        heroProxy.refine = ""

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

    if heroProxy.weapon is not None:
        CreateToolTip(creation_labels[6], heroProxy.weapon.desc)
    else:
        CreateToolTip(creation_labels[6], "")

def handle_selection_change_assist(event=None):
    selected_value = creation_str_vars[8].get()
    #print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        heroProxy.assist = hero.makeAssist(selected_value)
    else:
        heroProxy.assist = None

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

    if heroProxy.assist is not None:
        CreateToolTip(creation_labels[8], heroProxy.assist.desc)
    else:
        CreateToolTip(creation_labels[8], "")

def handle_selection_change_special(event=None):
    selected_value = creation_str_vars[9].get()
    #print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        heroProxy.special = hero.makeSpecial(selected_value)
    else:
        heroProxy.special = None

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

    if heroProxy.special is not None:
        CreateToolTip(creation_labels[9], heroProxy.special.desc)
    else:
        CreateToolTip(creation_labels[9], "")

def handle_selection_change_askill(event=None):
    selected_value = creation_str_vars[18].get()
    #print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        heroProxy.askill = hero.makeSkill(selected_value)
    else:
        heroProxy.askill = None

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

    if heroProxy.askill is not None:
        CreateToolTip(creation_labels[18], heroProxy.askill.desc)
    else:
        CreateToolTip(creation_labels[18], "")

def handle_selection_change_bskill(event=None):
    selected_value = creation_str_vars[19].get()
    #print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        heroProxy.bskill = hero.makeSkill(selected_value)
    else:
        heroProxy.bskill = None

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

    if heroProxy.bskill is not None:
        CreateToolTip(creation_labels[19], heroProxy.bskill.desc)
    else:
        CreateToolTip(creation_labels[19], "")

def handle_selection_change_cskill(event=None):
    selected_value = creation_str_vars[20].get()
    #print(f"You selected: {selected_value}")

    # Set proxy value
    if selected_value != "None":
        heroProxy.cskill = hero.makeSkill(selected_value)
    else:
        heroProxy.cskill = None

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

    if heroProxy.cskill is not None:
        CreateToolTip(creation_labels[20], heroProxy.cskill.desc)
    else:
        CreateToolTip(creation_labels[20], "")

def handle_selection_change_sseal(event=None):
    selected_value = creation_str_vars[21].get()

    if selected_value != "None":
        heroProxy.sSeal = hero.makeSeal(selected_value)
    else:
        heroProxy.sSeal = None

    if handle_selection_change_name.created_hero is not None:
        heroProxy.apply_proxy(handle_selection_change_name.created_hero)

        i = 0
        while i < 5:
            creation_stats[i].set(stat_strings[i] + str(handle_selection_change_name.created_hero.visible_stats[i]))
            i += 1

    if heroProxy.sSeal is not None:
        CreateToolTip(creation_labels[21], heroProxy.sSeal.desc)
    else:
        CreateToolTip(creation_labels[21], "")

creation_labels = []
creation_str_vars = []
creation_comboboxes = []

for row in range(12):

    cur_str_var = tk.StringVar()

    cur_label = tk.Label(left_dropbox_frame, text=names[row], width=12)
    creation_labels.append(cur_label)

    cur_label.grid(row=row, column=0, padx=10, pady=5)

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

    # BLESSING
    if row == 4:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_blessing)

    # S SUPPORT
    if row == 5:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_summsupport)

    # WEAPON
    if row == 7:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_weapon)

    # REFINE
    if row == 8:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_refine)

    # ASSIST
    if row == 9:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_assist)

    # SPECIAL
    if row == 10:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_special)

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

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
        x = x + self.widget.winfo_rootx() #+ 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#110947", foreground="white", relief=tk.SOLID, borderwidth=1,
                      font=("Helvetica", "10"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

for row in range(12):
    cur_str_var = tk.StringVar()

    cur_label = tk.Label(right_dropbox_frame, text=names2[row], width=12)

    creation_labels.append(cur_label)

    cur_label.grid(row=row, column=0, padx=10, pady=5)

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

    if row == 5:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_allysupport)

    if row == 6:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_askill)

    if row == 7:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_bskill)

    if row == 8:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_cskill)

    if row == 9:
        combo1['textvariable'] = None
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_sseal)

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

# Handles unit creation
heroProxy = HeroProxy()

# Handles team creation
selectProxy = SelectProxy()

# Handles which options are chosen
selectedOptions = SelectedOptions()

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

if __name__ == "__main__":
    window.mainloop()