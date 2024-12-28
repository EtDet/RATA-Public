import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

import os
import textwrap
import json
import pandas as pd
from functools import partial

from PIL import Image, ImageTk
from natsort import natsorted

from map import wall_crops, Map

# CONSTANTS
PLAYER = 0
ENEMY = 1

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

        self.search_bar = None

        self.target_widget = None
        self.default_target_widget = None

        self.drag_data = None
        self.dragging_from_text = False
        self.dragging_from_image = False
        self.label_causing_offset = None

        bg_color = "#ddd"

        if "bg" in kw:
            bg_color = kw["bg"]

        # Name frame (has name of frame)
        self.name_label = tk.Label(self.name_frame, text="My Units", bg=bg_color, fg=fg, font=(None, 16))
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
        # - can be dragged onto GameplayCanvas while in Preperation mode to add units to certain positions
        # - can also be dragged onto ExtrasFrame when in Preperation mode and on the My Team tab

        self.scrolling_frame = unit_button_listing = ctk.CTkScrollableFrame(self.button_frame)
        unit_button_listing.pack(expand=True, fill=tk.BOTH)

        '''
        for x in range(20):
            cur_button = tk.Button(unit_button_listing, text="Hey all scott here", font=("Helvetica", 14), relief="flat")
            cur_button.pack(pady=3, anchor=tk.W, fill=tk.X, expand=True)

            self.unit_buttons.append(cur_button)
        '''

        # Command frame, has buttons for adding, editing, and deleting
        # - adding should always be active
        # - editing & deleting should only be active iff a unit is selected

        create_button = tk.Button(self.command_frame, text="Create New", bg=buttonbg, fg=fg, bd=0)
        create_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = tk.Button(self.command_frame, text="Edit", state=tk.DISABLED, bg=buttonbg, fg=fg, bd=0)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        def create_popup():
            if not self.confirm_deletion_popup:
                self.confirm_deletion_popup = popup = tk.Toplevel(self)
                popup.title("Confirm deletion")

                label = tk.Label(popup, text='Are you sure you want to delete this build, "' + self.selected_button._text + '"?')
                label.pack(pady=20, padx=20)

                lower_frame = tk.Frame(popup)
                lower_frame.pack()

                cancel_button = tk.Button(lower_frame, text="Cancel", command=self.button_deletion_cancel)
                cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

                confirm_button = tk.Button(lower_frame, text="Delete", command=self.button_deletion_confirm)
                confirm_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = tk.Button(self.command_frame, text="Delete", state=tk.DISABLED, bg=buttonbg, fg=fg, bd=0, command=create_popup)
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

    def button_deletion_confirm(self):
        if self.confirm_deletion_popup:
            self.confirm_deletion_popup.destroy()
            self.confirm_deletion_popup = None

            self.selected_button.forget()

            self.selected_button = None

            self.edit_button.config(state="normal")
            self.delete_button.config(state="normal")

    def button_deletion_cancel(self):
        if self.confirm_deletion_popup:
            self.confirm_deletion_popup.destroy()
            self.confirm_deletion_popup = None

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

class GameplayCanvas(tk.Canvas):
    def __init__(self, master):
        self.TILE_SIZE = 90

        self.GAMEPLAY_LENGTH = self.TILE_SIZE * 6
        self.GAMEPLAY_WIDTH = self.TILE_SIZE * 8

        tk.Canvas.__init__(self, master=master, width=self.GAMEPLAY_LENGTH, height=self.GAMEPLAY_WIDTH, bg="#282424", highlightthickness=0)

        self.running = False

        self.map = Map(0)

        self.create_text(self.GAMEPLAY_LENGTH / 2, self.GAMEPLAY_WIDTH / 2, text="No map selected.", font="Helvetica 20", fill="white")

        # Gameplay variables
        self.turn_info = []

        # Store PhotoImages for later use to not be garbage collected.
        self.liquid = None
        self.terrain = None
        self.wall_photos = []
        self.move_tile_photos = []
        self.move_arrow_photos = []
        self.weapon_type_photos = []

        # Arrays of placed images on the Canvas
        self.wall_sprites = []

        # Set default sprites, constant for each map

        # Movement tiles
        blue_tile = Image.open("CombatSprites/" + "tileblue" + ".png").resize((self.TILE_SIZE, self.TILE_SIZE), Image.LANCZOS)
        light_blue_tile = Image.open("CombatSprites/" + "tilelightblue" + ".png")
        red_tile = Image.open("CombatSprites/" + "tilered" + ".png")
        pale_red_tile = Image.open("CombatSprites/" + "tilepalered" + ".png")
        green_tile = Image.open("CombatSprites/" + "tilegreen" + ".png")
        pale_green_tile = Image.open("CombatSprites/" + "tilepalegreen" + ".png")

        self.move_tile_photos.clear()
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

    def setup_with_file(self, json_path):
        with open(json_path) as read_file: json_data = json.load(read_file)

        # Specify map terrain, structures, and starting positions with JSON file.
        self.map.define_map(json_data)

        # Liquid
        liquid_image = Image.open("CombatSprites/" + self.map.liquid_texture)
        self.liquid = liquid_photo = ImageTk.PhotoImage(liquid_image)

        self.create_image(0, 0, anchor=tk.NW, image=liquid_photo)
        self.create_image(0, 90 * 3, anchor=tk.NW, image=liquid_photo)

        # Terrain
        map_path = json_path.replace(".json", ".png")
        map_image = Image.open(map_path)
        self.terrain = map_photo = ImageTk.PhotoImage(map_image)
        self.create_image(0, 0, anchor=tk.NW, image=map_photo)

        # Walls
        self.refresh_walls()

        # Turn info
        self.turn_info = [1, PLAYER, 50]

        # Map States
        self.map_states = []

        # TEMPORARY?
        for starting_space in self.map.player_start_spaces:
            self.move_to_tile(self.create_image(0, 0, image=self.move_tile_photos[0]), starting_space)

        for starting_space in self.map.enemy_start_spaces:
            self.move_to_tile(self.create_image(0, 0, image=self.move_tile_photos[2]), starting_space)



    def move_to_tile(self, sprite, tile_num):
        x_move = 45 + 90 * (tile_num % 6)
        y_move = 45 + 90 * (7 - (tile_num // 6))

        self.coords(sprite, x_move, y_move)

    def refresh_walls(self):
        self.wall_photos.clear()
        self.wall_sprites.clear()

        wall_texture = Image.open("CombatSprites/" + self.map.wall_texture)

        for tile in self.map.tiles:
            if tile.structure_on:
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

    def place_unit_from_frame(self, row_data, x, y):
        tile_x_coord = x // self.TILE_SIZE
        tile_y_coord = (self.GAMEPLAY_WIDTH // self.TILE_SIZE) - (y // self.TILE_SIZE) - 1

        final_tile = tile_x_coord + tile_y_coord * 6
        print(final_tile)


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
        print(self.identify_row(event.y))

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