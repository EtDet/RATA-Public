import tkinter as tk
from tkinter import ttk

import feh_widgets as feh

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
window.title('RATA 2.0.0')
window.minsize(width=400, height=300)

# Top Ribbon
ribbon_frame = tk.Frame(window, bg=cur_widget_colors["tr"], height=50)
ribbon_frame.pack(side="top", fill="x")

# Add buttons to the ribbon
button_labels = ["File", "Edit", "View"]
button_array = []

for label in button_labels:
    cur_button = feh.HoverButton(ribbon_frame, text=label, **ribbon_button_args)
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
maps_frame.pack_propagate(False) # widgets remain a fixed size

units_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
gameplay_frame.pack(fill=tk.Y, expand=True)
status_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
extras_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

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


trv = feh.FileTree(maps_frame, selectmode='browse')
trv.start_file_population()
trv.pack(padx=10, pady=5, fill="both", expand=True, anchor=tk.NW)

trv.tag_configure('item_row', background=cur_widget_colors["maps_item"])
trv.tag_configure('directory_row', background=cur_widget_colors["maps_directory"])

# UNITS FRAME ELEMENTS

hero_listing = feh.HeroListing(units_frame, fg=cur_widget_colors["text"], buttonbg=cur_widget_colors["units_button"], bg=cur_widget_colors["units_bg"])
hero_listing.pack(fill="both", expand=True, padx=10, pady=5)
hero_listing.pack_propagate(False)

hero_listing.name_frame.config(bg=cur_widget_colors["units_title"])
hero_listing.name_label.config(bg=cur_widget_colors["units_title"])

#hero_listing.bind()

# GAMEPLAY FRAME ELEMENTS

active_gameplay_sims = []
focused_gameplay_sim = [None]

# Singular instance of a running Simulation
class Simulation:
    def __init__(self, name):
        self.tab = feh.TabButton(gameplay_tabs_frame, fg=cur_widget_colors["text"], bg=cur_widget_colors["bg"], text=name)
        self.canvas = feh.GameplayCanvas(gameplay_frame)

        self.running = False

    def delete_canvas_entry(self):
        for sim in active_gameplay_sims:
            sim.canvas.forget()

        active_gameplay_sims.remove(self)

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

        print(focused_gameplay_sim[0].canvas)

        display_focused()

# Sets the canvas on the Gameplay frame to the canvas of the currently focused Simulation
def display_focused():
    for sim in active_gameplay_sims:
        sim.canvas.forget()

    focused_sim = focused_gameplay_sim[0]

    if focused_sim:
        hero_listing.target_widget = focused_sim.canvas

        for sim in active_gameplay_sims:
            sim.tab.tab_name_button.config(bg=cur_widget_colors["bg"])

        focused_sim.tab.tab_name_button.config(bg="green")

        focused_sim.canvas.pack()
    else:
        hero_listing.target_widget = empty_gameplay_canvas



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

        sim.tab.tab_name_button.config(command=sim.set_focused)
        sim.tab.tab_close_button.config(command=sim.delete_canvas_entry)
        sim.tab.pack(side=tk.LEFT, padx=2, pady=2, anchor=tk.N)

        if len(active_gameplay_sims) == 0:
            empty_gameplay_canvas.forget()
        else:
            focused_gameplay_sim[0].canvas.forget()

        active_gameplay_sims.append(sim)

        focused_gameplay_sim.clear()
        focused_gameplay_sim.append(sim)

        display_focused()

trv.bind("<Double-1>", row_selected)

gameplay_tabs_frame = tk.Frame(gameplay_frame, height=35, bg="#282424")
gameplay_tabs_frame.pack(fill=tk.X)

#tk.Label(gameplay_tabs_frame, height=2, bg="#282424").pack(side=tk.LEFT)

empty_gameplay_canvas = feh.GameplayCanvas(gameplay_frame)
empty_gameplay_canvas.pack()

hero_listing.target_widget = empty_gameplay_canvas
hero_listing.default_target_widget = empty_gameplay_canvas

window.mainloop()