import tkinter as tk
from tkinter import ttk

from re import sub

import feh_widgets as fehw

# Light mode colors
widget_colors_light = {
    "bg": "#eee",
    "text": "#000",
    "borders": "#bbb",

    "tr": "lightgray",
    "tr_button": "#eee",
    "tr_button_ACTIVE": "#ddd",
    "tr_button_text": "#000",

    "maps_title": "#bbb",
    "maps_bg": "#ddd",
    "maps_directory": "#bcd3e8",
    "maps_item": "#d8e0e6",

    "units_title": "#bbb",
    "units_bg": "#ddd",
    "units_button": "#eee",
    "units_button_ACTIVE": "#ddd",

    "game_buttonframe_bg": "#ddd",
}

# Dark mode colors
widget_colors_dark = {
    "bg": "#333",
    "text": "#fff",
    "borders": "#222",

    "tr": "#222",
    "tr_button": "#444",
    "tr_button_ACTIVE": "#555",
    "tr_button_text": "#fff",

    "maps_title": "#202020",
    "maps_bg": "#252525",
    "maps_directory": "#2b2d40",
    "maps_item": "#283066",

    "units_title": "#202020",
    "units_bg": "#252525",
    "units_button": "#444",
    "units_button_ACTIVE": "#555",

    "game_buttonframe_bg": "#555",
}

cur_widget_colors = widget_colors_dark

ribbon_button_args = {
    "width": 8,
    "bg": cur_widget_colors["tr_button"],
    "fg": cur_widget_colors["tr_button_text"],
    "activebackground": cur_widget_colors["tr_button_ACTIVE"],
    "activeforeground": cur_widget_colors["tr_button_text"],
    "relief": "flat",
    "bd": 0
}

# Window
window = tk.Tk()
window.geometry('800x600')
window.state('zoomed')
window.title('RATA 2.7.2')

rata_icon = tk.PhotoImage(file="CombatSprites/rata.png")

window.iconphoto(True, rata_icon)
window.minsize(width=400, height=300)

# Top Ribbon
ribbon_frame = tk.Frame(window, bg=cur_widget_colors["tr"], height=50)
#ribbon_frame.pack(side="top", fill="x")



# Add buttons to the ribbon
button_labels = ["File", "Edit", "View"]
button_array = []

for label in button_labels:
    cur_button = fehw.HoverButton(ribbon_frame, text=label, **ribbon_button_args)
    cur_button.pack(side="left")



# Background frames for body area
main_frame = tk.Frame(window, bg=cur_widget_colors["bg"])
main_frame.pack(fill=tk.BOTH, expand=True)

# Three frames
left_frame = tk.Frame(main_frame)
center_frame = tk.Frame(main_frame)
right_frame = tk.Frame(main_frame)

left_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
center_frame.pack(fill=tk.Y, side=tk.LEFT, expand=False)
right_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

parition_frame_args = {
    "bg": cur_widget_colors["bg"],
    "highlightthickness": 1,
    "highlightbackground": cur_widget_colors["borders"],
    "highlightcolor": cur_widget_colors["borders"]
}

maps_frame = tk.Frame(left_frame, parition_frame_args)
units_frame = tk.Frame(left_frame, parition_frame_args)
gameplay_frame = tk.Frame(center_frame, parition_frame_args)
status_frame = tk.Frame(right_frame, parition_frame_args)
extras_frame = tk.Frame(right_frame, parition_frame_args)


maps_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
maps_frame.pack_propagate(False) # widgets remain a fixed proportion

units_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
gameplay_frame.pack(fill=tk.Y, expand=True)
status_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
status_frame.pack_propagate(False)
extras_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
extras_frame.pack_propagate(False)

# MAPS FRAME ELEMENTS

style = ttk.Style()
style.theme_use('default')

style.configure(style="Treeview",
                foreground=cur_widget_colors["text"],
                background=cur_widget_colors["maps_bg"],
                font=("Helvetica", 14),
                rowheight=25,
                borderwidth=0,
                highlightthickness=0
                )

style.configure(style="Treeview.Heading",
                font=("Helvetica", 16),
                foreground="orange",
                background="green",
                relief="flat"
                )

style.map(style="Treeview.Heading",
          background=[('active', cur_widget_colors["maps_title"]), ('!disabled', cur_widget_colors["maps_title"])],
          foreground=[('active', cur_widget_colors["text"]), ('!disabled', cur_widget_colors["text"])]
          )

style.map(style="Treeview",
          background=[('selected', '#4c6cac')],
          foreground=[('selected', 'yellow')]
          )

style.layout(style="Treeview", layoutspec=[('Treeview.treearea', {'sticky': 'nswe'})])

trv = fehw.FileTree(maps_frame, selectmode='browse')
trv.start_file_population()
trv.pack(padx=10, pady=5, fill="both", expand=True, anchor=tk.NW)

trv.tag_configure('item_row', background=cur_widget_colors["maps_item"])
trv.tag_configure('directory_row', background=cur_widget_colors["maps_directory"])

# UNITS FRAME ELEMENTS

hero_listing = fehw.HeroListing(units_frame, fg=cur_widget_colors["text"], buttonbg=cur_widget_colors["units_button"], bg=cur_widget_colors["units_bg"])
hero_listing.pack(fill="both", expand=True, padx=10, pady=5)

hero_listing.pack_propagate(False)

# hero_listing.name_frame.config(bg=cur_widget_colors["units_title"])
# hero_listing.name_label.config(bg=cur_widget_colors["units_title"])

# GAMEPLAY FRAME ELEMENTS

active_gameplay_sims = []
focused_gameplay_sim = [None]
bonus_units_per_tab = []

hero_listing.active_sims = active_gameplay_sims

# Singular instance of a running Simulation
class Simulation:
    def __init__(self, name):
        self.tab = fehw.TabButton(gameplay_tabs_frame, fg=cur_widget_colors["text"], bg=cur_widget_colors["bg"], text=name)
        self.canvas = fehw.GameplayCanvas(gameplay_frame, hero_listing)
        self.button_frame = fehw.GameplayButtonFrame(gameplay_frame, fg=cur_widget_colors["text"], inner_bg=cur_widget_colors["bg"], bg=cur_widget_colors["game_buttonframe_bg"])

        self.canvas.unit_status = unit_info
        self.button_frame.unit_status = unit_info

        self.canvas.button_frame = self.button_frame

        self.canvas.extras = extras

        self.button_frame.start_button.config(command=self.canvas.start_simulation)
        self.button_frame.end_turn_button.config(command=self.canvas.end_turn_button)
        self.button_frame.undo_button.config(command=self.canvas.undo_action_button)
        self.button_frame.swap_spaces_button.config(command=self.canvas.toggle_swap)

        # 0 - Player units
        # 1 - Enemy units
        # 2 - Forecasts
        # 3 - Building
        self.cur_extras_tab = 0

        self.running = False

    def delete_canvas_entry(self):
        for sim in active_gameplay_sims:
            sim.canvas.forget()
            sim.button_frame.forget()

        index = active_gameplay_sims.index(self)

        active_gameplay_sims.remove(self)
        bonus_units_per_tab.pop(index)

        if self == focused_gameplay_sim[0]:
            if active_gameplay_sims:
                focused_gameplay_sim[0] = active_gameplay_sims[0]


            else:
                focused_gameplay_sim[0] = None
                empty_gameplay_canvas.pack()

        self.tab.close()

        display_focused()

        del self

    def set_focused(self):
        focused_gameplay_sim[0] = self

        #print(focused_gameplay_sim[0].canvas)

        display_focused()

# Sets the canvas on the Gameplay frame to the canvas of the currently focused Simulation
def display_focused():
    for sim in active_gameplay_sims:
        sim.canvas.forget()
        sim.button_frame.forget()

    focused_sim = focused_gameplay_sim[0]

    # If tabs exist
    if focused_sim:
        hero_listing.target_widget = focused_sim.canvas

        # Other tabs have their button changed to no color
        for sim in active_gameplay_sims:
            sim.tab.tab_name_button.config(bg=cur_widget_colors["bg"])

        # Change tab color to green (currently selected)
        focused_sim.tab.tab_name_button.config(bg="green")

        # Place current canvas
        focused_sim.canvas.pack()
        focused_sim.button_frame.pack(fill=tk.BOTH, expand=True)

        # Disable Pair Up/Duo or Harmonic Skill/Style
        focused_sim.button_frame.action_button.config(state='disabled', text='Action\nButton')

        extras.player_team_button.config(state="normal")
        extras.enemy_team_button.config(state="normal")

        # Allow forecasts tab to be shown if running
        if sim.canvas.running:
            extras.forecasts_button.config(state="normal")

        if not sim.canvas.running and sim.canvas.game_mode == fehw.hero.GameMode.AetherRaids:
            extras.building_button.config(state="normal")
        else:
            extras.building_button.config(state="disabled")

        index = active_gameplay_sims.index(focused_sim)
        cur_bonus_units = bonus_units_per_tab[index]

        extras.setup_tabs(focused_sim.canvas.unit_drag_points, cur_bonus_units, focused_sim.canvas.game_mode, focused_sim.canvas.running, focused_sim.canvas.get_struct_levels())

        if not focused_sim.canvas.running:
            extras.show_player_team()
        else:
            extras.show_forecasts()

        '''
        if focused_sim.cur_extras_tab == 1:
            extras.show_enemy_team()
        if focused_sim.cur_extras_tab == 2:
            extras.show_forecasts()
        if focused_sim.cur_extras_tab == 3:
            extras.show_building()
        '''
    else:
        hero_listing.target_widget = empty_gameplay_canvas

        extras.reset_tab_buttons()

        extras.player_team_button.config(state="disabled")
        extras.enemy_team_button.config(state="disabled")
        extras.forecasts_button.config(state="disabled")
        extras.building_button.config(state="disabled")

        extras.active_tab.forget()
        extras.active_tab = None

    unit_info.clear()


# When an item in the map TreeView is double-clicked, add its tab if there are less than 5
def row_selected(event):
    item = trv.identify_row(event.y)

    try:
        file_path = trv.item(item)['tags'][1]
    except IndexError:
        return

    if trv.hover_timer:
        trv.after_cancel(trv.hover_timer)
        trv.hover_timer = None

    tw = trv.preview_window
    trv.preview_window = None
    if tw:
        tw.destroy()

    if len(active_gameplay_sims) < 5:

        sim = Simulation(trv.item(item)['text'])
        sim.canvas.setup_with_file(file_path)

        # Setup bonus units
        bonus_units_per_tab.append([False] * len([drag_point for drag_point in sim.canvas.unit_drag_points.values()]))

        # Change button frame to display respective gamemode
        gamemode_name = sim.canvas.game_mode.name
        spaced_name = sub(r'([A-Z])', r' \1', gamemode_name)
        spaced_name = spaced_name.strip()

        sim.button_frame.gamemode_info.config(text="Gamemode: " + spaced_name)

        sim.tab.tab_name_button.config(command=sim.set_focused)
        sim.tab.tab_close_button.config(command=sim.delete_canvas_entry)
        sim.tab.pack(side=tk.LEFT, padx=2, pady=2, anchor=tk.N)

        if len(active_gameplay_sims) == 0:
            empty_gameplay_canvas.forget()
        else:
            focused_gameplay_sim[0].canvas.forget()
            focused_gameplay_sim[0].button_frame.forget()

        active_gameplay_sims.append(sim)

        focused_gameplay_sim.clear()
        focused_gameplay_sim.append(sim)

        display_focused()

        sim.canvas.refresh_units_prep()

trv.bind("<Double-1>", row_selected)

gameplay_tabs_frame = tk.Frame(gameplay_frame, height=35, bg="#282424")
gameplay_tabs_frame.pack(fill=tk.X)

#tk.Label(gameplay_tabs_frame, height=2, bg="#282424").pack(side=tk.LEFT)

empty_gameplay_canvas = fehw.GameplayCanvas(gameplay_frame, hero_listing)
empty_gameplay_canvas.pack()

hero_listing.target_widget = empty_gameplay_canvas
hero_listing.default_target_widget = empty_gameplay_canvas

# UNIT INFO FRAME
unit_info = fehw.UnitInfoDisplay(status_frame, bg=cur_widget_colors["units_title"], bg_color=cur_widget_colors["maps_bg"], fg=cur_widget_colors["text"])
unit_info.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

hero_listing.unit_status = unit_info

# EXTRAS FRAME
extras = fehw.ExtrasFrame(extras_frame, bg=cur_widget_colors["units_title"], bg_color=cur_widget_colors["maps_bg"], fg=cur_widget_colors["text"])
extras.cur_sim = focused_gameplay_sim

extras.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

window.mainloop()