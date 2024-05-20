from combat import *
import pandas as pd
import os

import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
megaSpread = pd.read_csv(__location__ + '\\FEHstats.csv')

def makeHero(name):
    row = megaSpread.loc[megaSpread['IntName'] == name]
    n = row.index.values[0]

    name = row.loc[n, 'Name']
    int_name = row.loc[n, 'IntName']
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

    return Hero(name, int_name, game, wpnType, moveType, [u_hp, u_atk, u_spd, u_def, u_res], [g_hp, g_atk, g_spd, g_def, g_res], dfl, bvid)


def singlePlayerButton():
    output_string.set("Single Player Selected")
    search_frame.pack()
    input_frame.pack_forget()

    sp_path = __location__ + '\\Maps'

    folders = [folder for folder in os.listdir(sp_path) if os.path.isdir(os.path.join(sp_path, folder))]

    for folder in folders:
        folder_button = tk.Button(sp_canvas, text=folder, width=30, height=4, command=lambda f=folder: print(f))
        folder_button.pack()


    sp_canvas.pack(side='left', fill='both', expand=False)
    sp_scrollbar.pack(side='right', fill='y')



def arenaButton():
    output_string.set("Arena Selected")
    for x in buttons: x.pack_forget()


def aetherRaidsButton():
    output_string.set("Aether Raids Selected")
    for x in buttons: x.pack_forget()


def sandboxButton():
    output_string.set("Sandbox Selected")
    for x in buttons: x.pack_forget()


def myUnitsButton():
    output_string.set("'My Units' Selected")

    search_frame.pack()
    input_frame.pack_forget()

    for widget in button_frame.winfo_children(): widget.destroy()

    # Create buttons for each unit
    for i, hrow in enumerate(unit_read.iterrows()):
        curHero = makeHero(hrow[1]['IntName'])

        respString = "-R" if hrow[1]['Resplendent'] == True else ""

        image2 = Image.open(__location__ + "\\Sprites\\" + hrow[1]['IntName'] + respString + ".png")
        new_width = int(image2.width * 0.4)
        new_height = int(image2.height * 0.4)

        if new_height > 85:
            new_width = int(new_width * 0.88)
            new_height = int(new_height * 0.88)

        resized_image2 = image2.resize((new_width, new_height), Image.LANCZOS)
        curImage = ImageTk.PhotoImage(resized_image2)

        images.append(curImage)
        tempButton = tk.Button(button_frame, image=curImage, text=str(hrow[1]['Build Name']), compound=tk.TOP, height=100, width=100, font='Helvetica 8')
        tempButton.image = curImage  # Store the reference to prevent garbage collection
        tempButton.grid(row=i // 7, column=i % 7, padx=3, pady=3)

    # Update the unit_canvas scrolling region
    unit_subframe.update_idletasks()
    unit_canvas.configure(scrollregion=unit_canvas.bbox("all"))

    unit_canvas.pack(side='left', fill='both', expand=True)
    unit_scrollbar.pack(side='right', fill='y')
    button_frame.pack(side='bottom', pady=10)

def searchUnits():
    curString = search_string.get()
    for item in button_frame.winfo_children():
        item.destroy()

    i = 0
    for hrow in unit_read.iterrows():

        curHero = makeHero(hrow[1]['IntName'])

        #print(curHero.intName)
        #print(hrow[1]['Build Name'])
        if curString.lower() in hrow[1]['IntName'].lower() or curString.lower() in hrow[1]['Build Name'].lower():

            respString = "-R" if hrow[1]['Resplendent'] == True else ""

            image2 = Image.open(__location__ + "\\Sprites\\" + hrow[1]['IntName'] + respString + ".png")


            new_width = int(image2.width * 0.4)
            new_height = int(image2.height * 0.4)

            if new_height > 85:
                new_width = int(new_width * 0.88)
                new_height = int(new_height * 0.88)


            resized_image2 = image2.resize((new_width, new_height), Image.LANCZOS)
            curImage = ImageTk.PhotoImage(resized_image2)

            images.append(curImage)
            images.append(curImage)
            tempButton = tk.Button(button_frame, image=curImage, text=str(hrow[1]['Build Name']), compound=tk.TOP, height=100, width=100, font='Helvetica 8')
            tempButton.image = curImage
            tempButton.grid(row=i // 7, column=i % 7, padx=3, pady=3, sticky='nswe')

            i += 1

def sp_backToMain():
    sp_canvas.pack_forget()
    sp_scrollbar.pack_forget()

    input_frame.pack(side='left', anchor='nw', padx=10, pady=10)

def myUnits_backToMain():
    unit_canvas.pack_forget()
    unit_scrollbar.pack_forget()

    sp_canvas.pack_forget()
    sp_scrollbar.pack_forget()

    button_frame.pack_forget()

    search_frame.pack_forget()

    input_frame.pack(side='left', anchor='nw', padx=10, pady=10)


def on_canvas_mousewheel(event):
    unit_canvas.yview_scroll(-1 * int(event.delta / 120), "units")


# window
window = ttk.Window(themename='darkly')
window.title('Fire Emblem Heroes Simulator')
window.geometry('800x600')
window.iconbitmap(__location__ + "\\Sprites\\Marth.ico")


#top label
title_label = ttk.Label(master=window, text='RATA', font='nintendoP_Skip-D_003 24')
title_label.pack(side='top', anchor='nw')

subtitle_label = ttk.Label(master=window, text='By CloudX (2024)', font='nintendoP_Skip-D_003 12')
subtitle_label.pack(side='top', anchor='nw')

version_level = ttk.Label(master=window, text='Ver 1.0.0', font='nintendoP_Skip-D_003 10')
version_level.pack(side='top', anchor='nw')

# main menu buttons
input_frame = ttk.Frame(master=window)

btWidth = 30
btHeight = 3

button_singe_player = tk.Button(master=input_frame, text='Single Player', command=singlePlayerButton, width=btWidth, height=btHeight)
button_arena = tk.Button(master=input_frame, text='Arena', command=arenaButton, width=btWidth, height=btHeight)
button_aether_raids = tk.Button(master=input_frame, text='Aether Raids', command=aetherRaidsButton, width=btWidth, height=btHeight)
button_sandbox = tk.Button(master=input_frame, text='Sandbox', command=sandboxButton, width=btWidth, height=btHeight)
button_my_units = tk.Button(master=input_frame, text='My Units', command=myUnitsButton, width=btWidth, height=btHeight)

buttons = [button_singe_player, button_arena, button_aether_raids, button_sandbox, button_my_units]

for b in buttons: b.pack(side='top', pady=5)

input_frame.pack(side='top', anchor='nw', padx=10, pady=10)


# single-player buttons

sp_canvas = tk.Canvas(window)
sp_scrollbar = ttk.Scrollbar(window, orient='vertical', command=sp_canvas.yview)

sp_canvas.configure(yscrollcommand=sp_scrollbar.set)
sp_canvas.bind("<Configure>", lambda e: sp_canvas.configure(scrollregion=sp_canvas.bbox("all")))
sp_canvas.bind_all("<MouseWheel>", on_canvas_mousewheel)

# unit buttons
unit_canvas = tk.Canvas(window)
unit_scrollbar = ttk.Scrollbar(window, orient='vertical', command=unit_canvas.yview)

unit_canvas.configure(yscrollcommand=unit_scrollbar.set)
unit_canvas.bind("<Configure>", lambda e: unit_canvas.configure(scrollregion=unit_canvas.bbox("all")))
unit_canvas.bind_all("<MouseWheel>", on_canvas_mousewheel)

unit_subframe = tk.Frame(unit_canvas, bg='red', width=300, height=300)
unit_canvas.create_window((0, 0), window=unit_subframe, anchor='nw')
button_frame = tk.Frame(unit_subframe)

unit_read = pd.read_csv(__location__ + '\\feh_user_units.csv')
images = []


# Top Bar
search_frame = ttk.Frame(window)

back_button = tk.Button(search_frame, text='<-', command=myUnits_backToMain)
back_button.pack(side='left', padx=5)

# Output for selecting menu
output_string = tk.StringVar()
output_label = ttk.Label(master=search_frame, text='Output', font='nintendoP_Skip-D_003 12', textvariable=output_string)
output_label.pack(side='left', padx=100)

# Search bar for My Units
search_string = tk.StringVar()
search_bar = ttk.Entry(search_frame, textvariable=search_string)
search_bar.pack(side='left')
search_button = ttk.Button(search_frame, text='Search', command=searchUnits)
search_button.pack(side='left', padx=5)

window.mainloop()
