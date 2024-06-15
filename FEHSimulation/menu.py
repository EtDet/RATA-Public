import hero
import pandas as pd

import webbrowser
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

WEAPON = 0
ASSIST = 1
SPECIAL = 2
ASKILL = 3
BSKILL = 4
CSKILL = 5
SSEAL = 6
XSKILL = 7

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

        self.asset = 0
        self.flaw = 1
        self.asc_asset = 0

        self.s_support = 0
        self.a_support = None

        self.weapon = None
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
    for x in current_elements:
        x.pack_forget()
        #x.place_forget()

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

    width = 100
    height = 100

    pixel = tk.PhotoImage(width=1, height=1)
    pre_button = tk.Button(button_frame, command=generate_creation, text="Create New", image=pixel, compound=tk.TOP, height=height, width=width, font='Helvetica 8')
    pre_button.image = pixel
    pre_button.grid(row=0, column=0, padx=3, pady=3)

    row, col = 0, 1

    for i, hrow in enumerate(unit_read.iterrows()):
        #curHero = hero.makeHero(hrow[1]['IntName'])

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
        tempButton = tk.Button(button_frame, image=curImage, text=str(hrow[1]['Build Name']), compound=tk.TOP, height=height, width=width, font='Helvetica 8')
        tempButton.image = curImage  # Store the reference to prevent garbage collection
        tempButton.grid(row=row, column=col, padx=3, pady=3)

        col += 1
        if col % 7 == 0:
            row += 1
            col = 0

    # Update the unit_canvas scrolling region
    unit_subframe.update_idletasks()
    unit_canvas.configure(scrollregion=unit_canvas.bbox("all"))

    search_frame.pack(pady=10)
    unit_canvas.pack(side='left', fill='both', expand=True)
    unit_scrollbar.pack(side='right', fill='y')
    button_frame.pack(side='left', pady=10)

    current_elements.append(search_frame)
    current_elements.append(unit_canvas)
    current_elements.append(button_frame)
    current_elements.append(unit_scrollbar)


def generate_creation():
    remove_elements()

    top_frame.pack(side=tk.TOP, expand=False, fill=tk.X)
    unit_stat_frame.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)
    dropbox_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)

    current_elements.append(unit_stat_frame)
    current_elements.append(dropbox_frame)
    current_elements.append(top_frame)

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

def generate_all_units_option():
    names = hero.hero_sheet['Name']
    int_names = hero.hero_sheet['IntName']
    epithets = hero.hero_sheet['Epithet']

    options = []
    intName_dict = {}

    i = 0
    while i < len(names):
        cur_string = names[i] + ": " + epithets[i]
        options.append(cur_string)
        intName_dict[cur_string] = int_names[i]
        i += 1

    return options, intName_dict

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
window.iconbitmap("Sprites\\Marth.ico")



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

search_frame = ttk.Frame(window)
back_button = tk.Button(search_frame, text='<- Back', command=generate_main, width=10)
back_button.pack(side='left')

output_label = ttk.Label(master=search_frame, text='Name Search:')
output_label.pack(side='left', padx=(25, 5))

search_string = tk.StringVar()
search_bar = ttk.Entry(search_frame, textvariable=search_string, width=30)
search_bar.pack(side='left', padx=(5,20))

search_button = tk.Button(search_frame, text='Search', width=15) #, command=searchUnits)
search_button.pack(side='left')

# Canvas
unit_canvas = tk.Canvas(window)

# Scrollbar, for Canvas
unit_scrollbar = ttk.Scrollbar(window, orient='vertical', command=unit_canvas.yview)

unit_canvas.configure(yscrollcommand=unit_scrollbar.set)
unit_canvas.bind("<Configure>", lambda e: unit_canvas.configure(scrollregion=unit_canvas.bbox("all")))
unit_canvas.bind_all("<MouseWheel>", on_canvas_mousewheel)

unit_subframe = tk.Frame(unit_canvas, bg='red', width=300, height=300)
unit_canvas.create_window((0, 0), window=unit_subframe, anchor='nw')
button_frame = tk.Frame(unit_subframe)

unit_elements = [search_frame, unit_canvas, unit_scrollbar, button_frame]

unit_read = pd.read_csv("feh_user_units.csv")

# UNIT CREATION

# Three frames
top_frame = tk.Frame(window, bg='gray')
unit_stat_frame = tk.Frame(window, bg='#2b2a69')
dropbox_frame = tk.Frame(window, bg='#a5b7c2')

creation_back_button = tk.Button(top_frame, text='<- Cancel', command=generate_units, width=10)
creation_back_button.pack(side=tk.LEFT, anchor='nw', padx=10, pady=10)

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

numbers = list(range(31))

left_dropbox_frame = tk.Frame(dropbox_frame, bg="#a5b7c2")
right_dropbox_frame = tk.Frame(dropbox_frame, bg="#a5b7c2")

left_dropbox_frame.pack(padx=8, pady=7, side=tk.LEFT, anchor='nw')
right_dropbox_frame.pack(padx=8, pady=7, side=tk.RIGHT, anchor='ne')

def handle_selection_change_name(event):
    selected_value = event.widget.get()
    print(f"You selected: {selected_value}")

    cur_intName = intName_dict[selected_value]

    curProxy.full_name = selected_value


    cur_image = Image.open("TestSprites\\" + cur_intName + ".png")

    resized_image = cur_image.resize((int(cur_image.width / 1.3), int(cur_image.height / 1.3)), Image.LANCZOS)

    curPhoto = ImageTk.PhotoImage(resized_image)

    creation_image_label.config(image=curPhoto)
    creation_image_label.image = curPhoto

    madeHero: hero.Hero = hero.makeHero(cur_intName)

    handle_selection_change_name.created_hero = madeHero
    curProxy.apply_proxy(madeHero)

    unit_picked.set("")

    star_var = "✰" * curProxy.rarity
    unit_name.set(f"{selected_value}\n{star_var}")
    unit_stats.set("Lv. 40\n+0 Flowers")

    i = 0
    while i < 5:
        creation_stats[i].set(stat_strings[i] + str(madeHero.visible_stats[i]))
        i += 1

def handle_selection_change_rarity(event):
    selected_value = event.widget.get()
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


creation_str_vars = []

for row in range(12):

    cur_str_var = tk.StringVar()

    tk.Label(left_dropbox_frame, text=names[row], width=12).grid(row=row, column=0, padx=10, pady=5)
    combo1 = ttk.Combobox(left_dropbox_frame, textvariable=cur_str_var)
    combo1.grid(row=row, column=1, padx=10, pady=12)

    creation_str_vars.append(cur_str_var)



    if row == 0:
        combo1['textvariable'] = None
        combo1['values'] = all_hero_options
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_name)

    if row == 1:
        combo1['textvariable'] = None
        combo1['values'] = numbers[1:6]
        combo1.bind("<<ComboboxSelected>>", handle_selection_change_rarity)


for row in range(11):

    tk.Label(right_dropbox_frame, text=names2[row], width=12).grid(row=row, column=0, padx=10, pady=5)
    combo1 = ttk.Combobox(right_dropbox_frame, textvariable=cur_str_var)
    combo1.grid(row=row, column=1, padx=10, pady=12)

    creation_str_vars.append(cur_str_var)

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