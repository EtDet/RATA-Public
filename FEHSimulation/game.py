from combat import *
from map import Map
import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import os
import json

PLAYER = 0
ENEMY = 1

RARITY_COLORS = ["#43464f", "#859ba8", "#8a4d15", "#c7d6d6", "#ffc012"]

moves = {0: "Infantry", 1: "Cavalry", 2: "Flyer", 3: "Armored"}
weapons = {
            "Sword": (0, "Sword"), "Lance": (1, "Lance"), "Axe": (2, "Axe"),
            "Staff": (15, "Staff"),
            "RTome": (11, "Red Tome"), "BTome": (12, "Blue Tome"), "GTome": (13, "Green Tome"), "CTome": (14, "Colorless Tome"),
            "CBow": (6, "Colorless Bow"), "RBow": (3, "Red Bow"), "BBow": (4, "Blue Blow"), "GBow": (5, "Green Bow"),
            "CDagger": (10, "Colorless Dagger"), "RDagger": (7, "Red Dagger"), "BDagger": (8, "Blue Dagger"), "GDagger": (9, "Green Dagger"),
            "RDragon": (16, "Red Dragon"), "BDragon": (17, "Blue Dragon"), "GDragon": (18, "Green Dragon"), "CDragon": (19, "Colorless Dragon"),
            "RBeast": (20, "Red Beast"), "BBeast": (21, "Blue Beast"), "GBeast": (22, "Green Beast"), "CBeast": (23, "Colorless Beast")
        }

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# A possible movement action by a unit
class Move():
    def __init__(self, dest, action, target, num_moved, is_warp, trav_str):
        self.destination = dest     # tile ID
        self.action = action        # 0 - move, 1 - assist, 2 - attack, -1 - end turn (screw you divine vein this needs to be separate)
        self.target = target        # Hero/Structure targeted by assist/attack
        self.num_moved = num_moved  # num tiles between start and this tile
        self.is_warp = is_warp      # does this move use a warp space?
        self.trav_string = trav_str # traversal string, holds default optimal path



# Create blank to be played upon
map0 = Map(0)

# Read JSON data associated with loaded map
with open(__location__ + "\\Maps\\Story Maps\\Book 1\\Preface\\story0-0-1.json") as read_file: data = json.load(read_file)

# Fill in terrain, starting tiles, enemy units, etc. into map
map0.define_map(data)

# hero definitions, used just for now
bolt = Weapon("Tactical Bolt", "Tactical Bolt", "idk", 14, 2, "Sword", {"colorlessAdv": 0}, ["Robin"])
robin = Hero("Robin", "M!Robin", 0, "BTome", 0, [40,29,29,29,22], [50, 50, 50, 50, 40], 30, 67)
robin.set_skill(bolt, WEAPON)

reposition = Assist("Reposition", "", {"repo":0}, 1, AssistType.Move)
robin.set_skill(reposition, ASSIST)

robin.set_IVs(ATK,SPD,ATK)
robin.set_level(1)

ragnell = Weapon("Emblem Ragnell", "Emblem Ragnell", "", 16, 1, "Sword", {"slaying": 1, "dCounter": 0, "BIGIKEFAN": 1018}, {})
GREAT_AETHER = Special("Great Aether", "", {"numFoeAtkBoostSp": 4, "AETHER_GREAT": 17}, 4, SpecialType.Offense)

ike = makeHero("E!Ike")

ike.set_skill(ragnell, WEAPON)
ike.set_skill(GREAT_AETHER, SPECIAL)

ike.set_IVs(ATK,SPD,ATK)
ike.set_level(1)


# PLACE UNITS ONTO MAP

#robin.tile = map0.tiles[18]

player_units_all = [robin, ike]
enemy_units_all = []

player_units = [robin, ike]
enemy_units = []

i = 0

# Load enemies from JSON data
while i < len(data["enemyData"]):
    curEnemy = makeHero(data["enemyData"][i]["name"])

    curEnemy.side = 1
    curEnemy.set_rarity(data["enemyData"][i]["rarity"])
    curEnemy.set_level(data["enemyData"][i]["level"])

    if "weapon" in data["enemyData"][i]:
        curWpn = makeWeapon(data["enemyData"][i]["weapon"])
        curEnemy.set_skill(curWpn, 0)

    if "alt_stats" in data["enemyData"][i]:
        curEnemy.visible_stats = data["enemyData"][i]["alt_stats"]
        j = 0
        while j < 5:
            curEnemy.visible_stats[j] += curEnemy.skill_stat_mods[j]
            curEnemy.visible_stats[j] = max(min(curEnemy.visible_stats[j], 99), 0)
            j += 1
        curEnemy.HPcur = curEnemy.visible_stats[HP]


    curEnemy.tile = map0.enemy_start_spaces[i]
    enemy_units_all.append(curEnemy)
    enemy_units.append(curEnemy)
    i += 1

# METHODS

def allowed_movement(hero):
    move_type = hero.move

    spaces_allowed = 3 - abs(move_type - 1)

    spaces_allowed += 1 * (Status.MobilityUp in hero.statusPos)
    if Status.Gravity in hero.statusNeg or Status.MobilityUp in hero.statusPos and Status.Stall in hero.statusNeg:
        spaces_allowed = 1

    return spaces_allowed

#given a hero on a map, generate a list of tiles they can move to
def get_possible_move_tiles(hero):
    curTile = hero.tile

    spaces_allowed = allowed_movement(hero)

    visited = set()         # tiles that have already been visited
    queue = [(curTile, 0, "")]  # array of tuples of potential movement tiles, current costs, and current optimal pattern
    possible_tiles = []     # unique, possible tiles, to be returned
    optimal_moves = []

    char_arr = ['N', 'S', 'E', 'W']

    # while possibilities exist
    while queue:
        # get current tuple
        current_tile, cost, path_str = queue.pop(0)

        # not possible if too far
        if cost > spaces_allowed: break

        # add tile to possible movements & visited
        possible_tiles.append(current_tile)
        optimal_moves.append(path_str)
        visited.add(current_tile)

        # get all neighbors, including None neighbors
        current_neighbors = []
        for x in (current_tile.north, current_tile.south, current_tile.east, current_tile.west):
            current_neighbors.append(x)

        i = 0
        for x in current_neighbors:
            # if not already visited or None
            if x not in visited and x is not None:

                # get cost to visit this tile
                neighbor_cost = get_tile_cost(x, hero)

                # if tile cost within allowed cost, tile is valid, and if hero is on it, they are ally
                if cost + neighbor_cost <= spaces_allowed and neighbor_cost >= 0 and (x.hero_on is None or x.hero_on is not None and x.hero_on.side == hero.side):
                    queue.append((x, cost + neighbor_cost, path_str + char_arr[i]))
                    visited.add(x)
            i += 1

    final_possible_tiles = []
    final_optimal_moves = []

    final_possible_tiles.append(possible_tiles[0])
    final_optimal_moves.append(optimal_moves[0])

    # remove tiles with allies as valid moves
    i = 1
    while i < len(possible_tiles):
        if possible_tiles[i].hero_on is None:
            final_possible_tiles.append(possible_tiles[i])
            final_optimal_moves.append(optimal_moves[i])
        i += 1

    return (final_possible_tiles, final_optimal_moves)

# given an adjacent tile and hero, calculate the movement cost to get to it
def get_tile_cost(tile, hero):
    cost = 1
    move_type = hero.move

    # cases in which units cannot go to tile
    if tile.terrain == 1 and move_type == 1: return -1 # cavalry & forests
    if tile.terrain == 2 and move_type != 2: return -1 # nonfliers & water/mountains
    if tile.terrain == 4: return -1                    # impassible terrain for anyone
    if tile.structure_on is not None: return -1        # structure currently on

    if tile.terrain == 1 and move_type == 0: cost = 2
    if tile.terrain == 3 and move_type == 1: cost = 3
    if tile.divine_vein == 1 and tile.divine_vein_owner != hero.side and hero.getRange() == 2: cost = 2

    if Status.TraverseTerrain in hero.statusPos: cost = 1

    if tile.hero_on is not None:
        if "pathfinder" in tile.hero_on.getSkills(): cost = 0

    return cost

# ASSIST SKILL VALIDATION

def final_reposition_tile(u_tile, a_tile):
    bottom_row = range(0, 5)
    if u_tile in bottom_row and a_tile == u_tile + 6: return -1

    top_row = range(42, 47)
    if u_tile in top_row and a_tile == u_tile - 6: return -1

    left_column = (0, 6, 12, 18, 24, 30, 36, 42)
    if u_tile in left_column and a_tile == u_tile + 1: return -1

    right_column = (5, 11, 17, 23, 29, 35, 41, 47)
    if u_tile in right_column and a_tile == u_tile - 1: return -1

    final_tile = -1

    if u_tile > a_tile:
        final_tile = a_tile + 2 * (u_tile - a_tile)

    if u_tile < a_tile:
        final_tile = a_tile - 2 * (a_tile - u_tile)

    return final_tile

def can_be_on_terrain(terrain_int, move_type_int):
    if terrain_int == 0 or terrain_int == 3: return True
    if terrain_int == 4: return False

    if terrain_int == 1:
        if move_type_int == 1: return False
        else: return True

    if terrain_int == 2:
        if move_type_int == 2: return True
        else: return False


animation = False



def move_to_tile(my_canvas, item_ID, num):
    x_move = 45 + 90 * (num % 6)
    y_move = 135 + 90 * (7 - (num//6))

    my_canvas.coords(item_ID, x_move-40, y_move-40)

def move_to_tile_wp(my_canvas, item_ID, num):
    x_move = 45 + 90 * (num % 6)
    y_move = 135 + 90 * (7 - (num // 6))
    my_canvas.coords(item_ID, x_move - 45, y_move - 45)

def move_to_tile_sp(my_canvas, label_ID, num):
    x_move = 45 + 90 * (num % 6)
    y_move = 135 + 90 * (7 - (num // 6))

    my_canvas.coords(label_ID, x_move - 33, y_move - 7)

def move_to_tile_hp(my_canvas, label_ID, num):
    x_move = 45 + 90 * (num % 6)
    y_move = 135 + 90 * (7 - (num // 6))

    my_canvas.coords(label_ID, x_move - 33, y_move + 36)

def animate_sprite_atk(my_canvas, item_ID, move_hori, move_vert, damage, text_tile):
    # Get the current coordinates of the item
    x, y = my_canvas.coords(item_ID)
    global animation
    start_x = x
    start_y = y

    # Calculate the new y-coordinate for moving up
    new_x = int(x + 40 * move_hori)
    new_y = int(y - 40 * move_vert)

    def move_to():
        global animation
        if not animation: return

        nonlocal x
        nonlocal y

        x += 2 * move_hori
        y -= 2 * move_vert
        my_canvas.coords(item_ID, x, y)

        if x != new_x or y != new_y:
            my_canvas.after(2, move_to)
        else:
            move_fro()
            animate_damage_popup(my_canvas, damage, text_tile)


    def move_fro():
        global animation
        if not animation: return

        nonlocal x
        nonlocal y

        x -= 2 * move_hori
        y += 2 * move_vert

        my_canvas.coords(item_ID, x, y)
        if x != start_x or y != start_y:
            my_canvas.after(2, move_fro)


    move_to()

def animate_damage_popup(canvas, number, text_tile):
    x_comp = text_tile % 6
    y_comp = text_tile // 6
    x_pivot = x_comp * 90 + 45
    y_pivot = (7 - y_comp) * 90 + 90 + 45

    displayed_text2 = canvas.create_text((x_pivot+1, y_pivot+1), text=str(number), fill='#7a643c', font=("Helvetica", 25, 'bold'), anchor='center')
    displayed_text = canvas.create_text((x_pivot, y_pivot), text=str(number), fill='#de1d1d', font=("Helvetica", 25, 'bold'), anchor='center')

    canvas.after(350, forget_text, canvas, displayed_text)
    canvas.after(350, forget_text, canvas, displayed_text2)

def forget_text(canvas, text):
    canvas.delete(text)

def get_attack_tiles(tile_num, range):
    if range != 1 and range != 2: return []
    x_comp = tile_num % 6
    y_comp = tile_num//6

    result = []

    if x_comp + range < 6: result.append(tile_num + range)
    if x_comp - range >= 0: result.append(tile_num - range)
    if y_comp + range < 8: result.append(tile_num + 6 * range)
    if y_comp - range >= 0: result.append(tile_num - 6 * range)

    if range == 2:
        if x_comp + 1 < 6 and y_comp + 1 < 8: result.append(tile_num + 1 + 6)
        if x_comp + 1 < 6 and y_comp - 1 >= 0: result.append(tile_num + 1 - 6)
        if x_comp - 1 >= 0 and y_comp + 1 < 8: result.append(tile_num - 1 + 6)
        if x_comp - 1 >= 0 and y_comp - 1 >= 0: result.append(tile_num - 1 - 6)

    return result

# some arrow images are cropped unusually
# this snaps them back to correct place
def get_arrow_offsets(arrow_num):
    if arrow_num == 0: return(16, 0)
    if arrow_num == 1: return(16, 1)
    if arrow_num == 3: return(-1, 0)
    if arrow_num == 4: return(16, 2)
    if arrow_num == 5: return(16, 0)
    if arrow_num == 6: return(0, 2)
    if arrow_num == 7: return(0, 1)
    if arrow_num == 9: return (0, 1)
    if arrow_num == 10: return(0, 2)
    if arrow_num == 11: return(0, 2)

    return (0,0)


def start_sim(player_units, enemy_units, chosen_map):
    if not chosen_map.player_start_spaces or not chosen_map.enemy_start_spaces:
        print("Error 100: No starting tiles")
        return -1

    if not player_units or len(player_units) > len(chosen_map.player_start_spaces):
        print("Error 101: Invalid number of player units")
        return -1

    def next_phase():
        # alternate turns
        turn_info[1] = abs(turn_info[1] - 1)

        # increment count if player phase
        if turn_info[1] == PLAYER:
            turn_info[0] += 1

            canvas.delete(next_phase.turn_txt)
            next_phase.turn_txt = canvas.create_text((540 / 2, 860), text="Turn " + str(turn_info[0]) + "/" + str(turn_info[2]), fill="#97a8c4", font=("Helvetica", 16), anchor='center')

            canvas.delete(next_phase.phase_txt)
            next_phase.phase_txt = canvas.create_text((540 / 2, 830), text="PLAYER PHASE", fill="#038cfc", font=("Helvetica", 20), anchor='center')

            for x in player_units:
                units_to_move.append(x)

            for i in range(0, len(player_units_all)):
                canvas.itemconfig(grayscale_enemy_sprite_IDs[i], state='hidden')
                canvas.itemconfig(enemy_sprite_IDs[i], state='normal')

        if turn_info[1] == ENEMY:
            canvas.delete(next_phase.phase_txt)
            next_phase.phase_txt = canvas.create_text((540 / 2, 830), text="ENEMY PHASE", fill="#e8321e", font=("Helvetica", 20), anchor='center')

            for x in enemy_units:
                units_to_move.append(x)

            for i in range(0, len(player_units_all)):
                canvas.itemconfig(grayscale_player_sprite_IDs[i], state='hidden')
                canvas.itemconfig(player_sprite_IDs[i], state='normal')

    def clear_banner():
        if hasattr(set_banner, "banner_rectangle") and set_banner.banner_rectangle:
            canvas.delete(set_banner.banner_rectangle)

        if hasattr(set_banner, "rect_array") and set_banner.rect_array:
            for x in set_banner.rect_array:
                canvas.delete(x)

        if hasattr(set_banner, "label_array") and set_banner.label_array:
            for x in set_banner.label_array:
                x.destroy()

    def set_banner(hero: Hero):

        name = hero.name
        move_type = moves[hero.move]
        weapon_type = weapons[hero.wpnType]
        level = hero.level
        merges = hero.merges
        stats = hero.visible_stats[:]
        buffs = hero.buffs[:]
        debuffs = hero.debuffs[:]

        blessing = hero.blessing

        weapon = "-"
        assist = "-"
        special = "-"
        askill = "-"
        bskill = "-"
        cskill = "-"
        sSeal = "-"
        xskill = "-"

        if hero.weapon is not None: weapon = hero.weapon.name
        if hero.assist is not None: assist = hero.assist.name
        if hero.special is not None: special = hero.special.name
        if hero.askill is not None: askill = hero.askill.name
        if hero.bskill is not None: bskill = hero.bskill.name
        if hero.cskill is not None: cskill = hero.cskill.name
        if hero.sSeal is not None: sSeal = hero.sSeal.name
        if hero.xskill is not None: xskill = hero.xskill.name

        clear_banner()

        banner_color = "#18284f" if hero.side == 0 else "#541616"
        set_banner.banner_rectangle = canvas.create_rectangle(0, 0, 539, 90, fill=banner_color, outline=RARITY_COLORS[hero.rarity-1])

        set_banner.rect_array = []
        set_banner.rect_array.append(canvas.create_rectangle((310, 5, 410, 22), fill="#cc3f52", outline=""))
        set_banner.rect_array.append(canvas.create_rectangle((310, 25, 410, 42), fill="#5fa370", outline=""))
        set_banner.rect_array.append(canvas.create_rectangle((310, 45, 410, 62), fill="#9b5fa3", outline=""))
        set_banner.rect_array.append(canvas.create_rectangle((310, 65, 410, 82), fill="#b59d12", outline=""))

        set_banner.rect_array.append(canvas.create_rectangle((430, 5, 530, 22), fill="#e6413e", outline=""))
        set_banner.rect_array.append(canvas.create_rectangle((430, 25, 530, 42), fill="#4c83c7", outline=""))
        set_banner.rect_array.append(canvas.create_rectangle((430, 45, 530, 62), fill="#579c57", outline=""))
        set_banner.rect_array.append(canvas.create_rectangle((430, 65, 530, 82), fill="#86ad42", outline=""))

        set_banner.label_array = []

        unit_info_label = tk.Label(canvas, text=name, bg=banner_color, font="nintendoP_Skip-D_003 10", relief="raised", width=13)
        unit_info_label.place(x=10, y=5)

        set_banner.label_array.append(unit_info_label)

        move_icon = canvas.create_image(135, 6, anchor=tk.NW, image=move_icons[hero.move])
        weapon_icon = canvas.create_image(160, 4, anchor=tk.NW, image=weapon_icons[weapons[hero.wpnType][0]])

        set_banner.rect_array.append(move_icon)
        set_banner.rect_array.append(weapon_icon)

        text_var = "Level " + str(hero.level)
        merge_var = ""
        if hero.merges > 0: merge_var = " + " + str(hero.merges)

        unit_level_label = tk.Label(canvas, text=text_var + merge_var, bg=banner_color, font="nintendoP_Skip-D_003 10", relief="raised", width=11)
        unit_level_label.place(x=187, y=5)

        set_banner.label_array.append(unit_level_label)

        unit_stat_label = tk.Text(canvas, wrap=tk.WORD, height=2, width=20, font="nintendoP_Skip-D_003 10", bd=0, highlightthickness=0)
        set_banner.label_array.append(unit_stat_label)

        is_neutral_iv = hero.asset == hero.flaw
        is_asc = hero.asset != hero.asc_asset
        is_merged = hero.merges > 0

        if (HP == hero.asset and not is_neutral_iv) or \
                (HP == hero.asc_asset and is_neutral_iv and is_asc) or\
                (HP == hero.asc_asset and not is_neutral_iv and hero.flaw == hero.asc_asset and is_merged) or \
                (not is_neutral_iv and HP == hero.asc_asset and HP != hero.asset and HP != hero.flaw):
            unit_stat_label.insert(tk.END, "HP ", ("blue", "hp"))
        elif HP == hero.flaw and hero.asc_asset != hero.flaw and not is_neutral_iv and not is_merged:
            unit_stat_label.insert(tk.END, "HP ", ("red", "hp"))
        else:
            unit_stat_label.insert(tk.END, "HP ", "normal")

        unit_stat_label.insert(tk.END, str(hero.HPcur) + "/" + str(stats[0]), "hp")

        if (ATK == hero.asset and not is_neutral_iv) or \
                (ATK == hero.asc_asset and is_neutral_iv and is_asc) or\
                (ATK == hero.asc_asset and not is_neutral_iv and hero.flaw == hero.asc_asset and is_merged) or \
                (not is_neutral_iv and ATK == hero.asc_asset and ATK != hero.asset and ATK != hero.flaw):
            unit_stat_label.insert(tk.END, " Atk ", ("blue", "atk"))
        elif ATK == hero.flaw and hero.asc_asset != hero.flaw and not is_neutral_iv and not is_merged:
            unit_stat_label.insert(tk.END, " Atk ", ("red", "atk"))
        else:
            unit_stat_label.insert(tk.END, " Atk ", "normal")

        unit_stat_label.insert(tk.END, str(stats[1]), "atk")

        if (SPD == hero.asset and not is_neutral_iv) or \
                (SPD == hero.asc_asset and is_neutral_iv and is_asc) or\
                (SPD == hero.asc_asset and not is_neutral_iv and hero.flaw == hero.asc_asset and is_merged) or \
                (not is_neutral_iv and SPD == hero.asc_asset and SPD != hero.asset and SPD != hero.flaw):
            unit_stat_label.insert(tk.END, " Spd ", ("blue", "spd"))
        elif SPD == hero.flaw and hero.asc_asset != hero.flaw and not is_neutral_iv and not is_merged:
            unit_stat_label.insert(tk.END, " Spd ", ("red", "spd"))
        else:
            unit_stat_label.insert(tk.END, " Spd ", "normal")

        unit_stat_label.insert(tk.END, str(stats[2]), "spd")

        unit_stat_label.insert(tk.END, "\n      " + str(int(hero.HPcur/stats[0] * 100)) + "%", "hp")

        if (DEF == hero.asset and not is_neutral_iv) or \
                (DEF == hero.asc_asset and is_neutral_iv and is_asc) or \
                (DEF == hero.asc_asset and not is_neutral_iv and hero.flaw == hero.asc_asset and is_merged) or \
                (not is_neutral_iv and DEF == hero.asc_asset and DEF != hero.asset and DEF != hero.flaw):
            unit_stat_label.insert(tk.END, " Def ", ("blue", "def"))
        elif DEF == hero.flaw and hero.asc_asset != hero.flaw and not is_neutral_iv and not is_merged:
            unit_stat_label.insert(tk.END, " Def ", ("red", "res"))
        else:
            unit_stat_label.insert(tk.END, " Def ", "normal")

        unit_stat_label.insert(tk.END, str(stats[3]), "def")

        if (RES == hero.asset and not is_neutral_iv) or \
                (RES == hero.asc_asset and is_neutral_iv and is_asc) or \
                (RES == hero.asc_asset and not is_neutral_iv and hero.flaw == hero.asc_asset and is_merged) or \
                (not is_neutral_iv and RES == hero.asc_asset and RES != hero.asset and RES != hero.flaw):
            unit_stat_label.insert(tk.END, " Res ", ("blue", "res"))
        elif RES == hero.flaw and hero.asc_asset != hero.flaw and not is_neutral_iv and not is_merged:
            unit_stat_label.insert(tk.END, " Res ", ("red", "res"))
        else:
            unit_stat_label.insert(tk.END, " Res ", "normal")

        unit_stat_label.insert(tk.END, str(stats[4]), "res")

        unit_stat_label.tag_configure("blue", foreground="#5493bf")
        unit_stat_label.tag_configure("red", foreground="#d15047")

        unit_stat_label.place(x=100, y=34)

        # SKILLS
        set_banner.rect_array.append(canvas.create_text((308, (5 + 22) / 2), text="⚔️", fill="red", font=("Helvetica", 9), anchor='e'))
        text_coords = ((310 + 410) / 2, (5 + 22) / 2)
        set_banner.rect_array.append(canvas.create_text(*text_coords, text=weapon, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(canvas.create_text((309, (25 + 38) / 2), text="◐", fill="green", font=("Helvetica", 23), anchor='e'))
        text_coords = ((310 + 410) / 2, (25 + 42) / 2)
        set_banner.rect_array.append(canvas.create_text(*text_coords, text=assist, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(canvas.create_text((308, (45 + 60) / 2), text="☆", fill="#ff33ff", font=("Helvetica", 10), anchor='e'))
        text_coords = ((310 + 410) / 2, (45 + 62) / 2)
        set_banner.rect_array.append(canvas.create_text(*text_coords, text=special, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(canvas.create_text((305, (65 + 80) / 2), text="S", fill="#ffdd33", font=("Helvetica", 10), anchor='e'))
        text_coords = ((310 + 410) / 2, (65 + 82) / 2)
        set_banner.rect_array.append(canvas.create_text(*text_coords, text=sSeal, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(canvas.create_text((425, (5 + 22) / 2), text="A", fill="#e6150e", font=("Helvetica", 10), anchor='e'))
        text_coords = ((430 + 530) / 2, (5 + 22) / 2)
        set_banner.rect_array.append(canvas.create_text(*text_coords, text=askill, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(canvas.create_text((425, (25 + 42) / 2), text="B", fill="#0d68bd", font=("Helvetica", 10), anchor='e'))
        text_coords = ((430 + 530) / 2, (25 + 42) / 2)
        set_banner.rect_array.append(canvas.create_text(*text_coords, text=bskill, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(canvas.create_text((425, (45 + 62) / 2), text="C", fill="#38e85b", font=("Helvetica", 10), anchor='e'))
        text_coords = ((430 + 530) / 2, (45 + 62) / 2)
        set_banner.rect_array.append(canvas.create_text(*text_coords, text=cskill, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(canvas.create_text((424, (65 + 80) / 2), text="X", fill="#a7e838", font=("Helvetica", 10), anchor='e'))
        text_coords = ((430 + 530) / 2, (65 + 82) / 2)
        set_banner.rect_array.append(canvas.create_text(*text_coords, text=xskill, fill="white", font=("Helvetica", 9), anchor='center'))

    def set_attack_forecast(attacker: Hero, defender: Hero):
        clear_banner()

        result = simulate_combat(attacker, defender, True, turn_info[0], 0, [])

        player_name = attacker.name
        player_move_type = moves[attacker.move]
        player_weapon_type = weapons[attacker.wpnType]
        player_HPcur = attacker.HPcur
        player_HPresult = result[0]
        player_spCount = attacker.specialCount
        player_combat_buffs = result[2]

        enemy_name = defender.name
        enemy_move_type = moves[defender.move]
        enemy_weapon_type = weapons[defender.wpnType]
        enemy_HPcur = int(defender.HPcur)
        enemy_HPresult = int(result[1])
        enemy_spCount = defender.specialCount
        enemy_combat_buffs = result[3]

        wpn_adv = result[4]
        atk_eff = result[5]
        def_eff = result[6]

        attacks = result[7]

        atk_feh_math_R = result[8]
        atk_hits_R = result[9]
        def_feh_math_R = result[10]
        def_hits_R = result[11]

        # FEH Math Hits

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

        set_banner.rect_array.append(canvas.create_rectangle(0, 0, 539/2, 90, fill=player_color, outline=RARITY_COLORS[attacker.rarity - 1]))
        set_banner.rect_array.append(canvas.create_rectangle(539 / 2 + 1, 0, 539, 90, fill=enemy_color, outline=RARITY_COLORS[defender.rarity - 1]))

        set_banner.rect_array.append(canvas.create_rectangle(0, 0, 539 / 2, 90, fill=player_color, outline=RARITY_COLORS[attacker.rarity - 1]))
        set_banner.rect_array.append(canvas.create_rectangle(539 / 2 + 1, 0, 539, 90, fill=enemy_color, outline=RARITY_COLORS[defender.rarity - 1]))

        # Names

        player_name_label = tk.Label(canvas, text=player_name, bg='black', font="nintendoP_Skip-D_003 10", relief="raised", width=13)
        player_name_label.place(x=10, y=5)

        enemy_name_label = tk.Label(canvas, text=enemy_name, bg='black', font="nintendoP_Skip-D_003 10", relief="raised", width=13)
        enemy_name_label.place(x=540-10-120, y=5)

        set_banner.label_array.append(player_name_label)
        set_banner.label_array.append(enemy_name_label)

        # Icons

        player_move_icon = canvas.create_image(135, 6, anchor=tk.NW, image=move_icons[attacker.move])
        player_weapon_icon = canvas.create_image(160, 4, anchor=tk.NW, image=weapon_icons[weapons[attacker.wpnType][0]])
        enemy_move_icon = canvas.create_image(540-135-20, 6, anchor=tk.NW, image=move_icons[int(defender.move)])
        enemy_weapon_icon = canvas.create_image(540-160-20, 4, anchor=tk.NW, image=weapon_icons[weapons[defender.wpnType][0]])

        set_banner.rect_array.append(player_move_icon)
        set_banner.rect_array.append(player_weapon_icon)
        set_banner.rect_array.append(enemy_move_icon)
        set_banner.rect_array.append(enemy_weapon_icon)

        # HP Calculation

        player_hp_calc = canvas.create_text((215, 16), text=str(player_HPcur) + " → " + str(player_HPresult), fill='yellow',font=("Helvetica", 11), anchor='center')
        enemy_hp_calc = canvas.create_text((324, 16), text=str(enemy_HPcur) + " → " + str(enemy_HPresult), fill="yellow", font=("Helvetica", 11), anchor='center')

        set_banner.rect_array.append(player_hp_calc)
        set_banner.rect_array.append(enemy_hp_calc)

        # Weapon Triangle Advantage

        if wpn_adv == 0:
            adv_arrow = canvas.create_text((255, 16), text=" ⇑ ", fill='green',font=("Helvetica", 20, 'bold'), anchor='center')
            disadv_arrow = canvas.create_text((285, 16), text=" ⇓ ", fill='red',font=("Helvetica", 20, 'bold'), anchor='center')
            set_banner.rect_array.append(adv_arrow)
            set_banner.rect_array.append(disadv_arrow)
        if wpn_adv == 1:
            adv_arrow = canvas.create_text((255, 16), text=" ↓ ", fill='red', font=("Helvetica", 14), anchor='center')
            disadv_arrow = canvas.create_text((285, 16), text=" ↑ ", fill='green', font=("Helvetica", 14, 'bold'), anchor='center')
            set_banner.rect_array.append(adv_arrow)
            set_banner.rect_array.append(disadv_arrow)

        set_banner.rect_array.append(canvas.create_rectangle(270-40, 27, 270+40, 42, fill='#5a5c6b', outline='#dae6e2'))

        # FEH Math

        feh_math_text = canvas.create_text((270, 35), text="FEH Math", fill='#dae6e2', font=("Helvetica", 11, 'bold'), anchor='center')
        set_banner.rect_array.append(feh_math_text)

        atk_feh_math_text = canvas.create_text((270-85, 35), text=atk_feh_math, fill='#e8c35d', font=("nintendoP_Skip-D_003", 8), anchor='center')
        set_banner.rect_array.append(atk_feh_math_text)

        def_feh_math_text = canvas.create_text((270+85, 35), text=def_feh_math, fill='#e8c35d', font=("nintendoP_Skip-D_003", 8), anchor='center')
        set_banner.rect_array.append(def_feh_math_text)

        # Special Count

        if player_spCount != -1:
            atk_sp_charge = canvas.create_text((270 - 135, 35), text=player_spCount, fill='#ff33ff', font=("Helvetica", 8), anchor='center')
            set_banner.rect_array.append(atk_sp_charge)

        if enemy_spCount != -1:
            def_sp_charge = canvas.create_text((270 + 135, 35), text=enemy_spCount, fill='#ff33ff', font=("Helvetica", 8), anchor='center')
            set_banner.rect_array.append(def_sp_charge)

        box_size = 30
        gap_size = 8

        cur_box_pos = int(270 - (gap_size * 0.5 * (len(attacks)-1) + box_size * 0.5 * (len(attacks)-1)))

        set_banner.rect_array.append(canvas.create_rectangle(cur_box_pos - 110, 54, cur_box_pos - 20, 76, fill="silver", outline='#dae6e2'))

        set_banner.rect_array.append(canvas.create_text((cur_box_pos - 65, 65), text="Attack Order", fill='black', font=("Helvetica", 10, "bold"), anchor='center'))

        # Attacks

        for x in attacks:
            box_color = "#18284f" if x.attackOwner == 0 else "#541616"

            set_banner.rect_array.append(canvas.create_rectangle(cur_box_pos - 15, 50, cur_box_pos + 15, 80, fill=box_color, outline='#dae6e2'))

            set_banner.rect_array.append(canvas.create_text((cur_box_pos, 65), text=x.damage, fill='#e8c35d', font=("nintendoP_Skip-D_003", 10), anchor='center'))

            cur_box_pos += int(box_size + gap_size)

    def set_assist_forecast(attacker: Hero, ally: Hero):
        clear_banner()

        player_color = "#18284f" if attacker.side == 0 else "#541616"
        enemy_color = "#18284f" if ally.side == 0 else "#541616"

        set_banner.rect_array.append(canvas.create_rectangle(0, 0, 539 / 2, 90, fill=player_color, outline=RARITY_COLORS[attacker.rarity - 1]))
        set_banner.rect_array.append(canvas.create_rectangle(539 / 2 + 1, 0, 539, 90, fill=enemy_color, outline=RARITY_COLORS[ally.rarity - 1]))

        set_banner.rect_array.append(canvas.create_rectangle(0, 0, 539 / 2, 90, fill=player_color, outline=RARITY_COLORS[attacker.rarity - 1]))
        set_banner.rect_array.append(canvas.create_rectangle(539 / 2 + 1, 0, 539, 90, fill=enemy_color, outline=RARITY_COLORS[ally.rarity - 1]))

        player_name_label = tk.Label(canvas, text=attacker.name, bg='black', font="nintendoP_Skip-D_003 10",
                                     relief="raised", width=13)
        player_name_label.place(x=10, y=5)

        ally_name_label = tk.Label(canvas, text=ally.name, bg='black', font="nintendoP_Skip-D_003 10",
                                    relief="raised", width=13)
        ally_name_label.place(x=540 - 10 - 120, y=5)

        set_banner.label_array.append(player_name_label)
        set_banner.label_array.append(ally_name_label)

        player_hp_calc = canvas.create_text((215, 16), text=str(player.HPcur) + " → " + str(player.HPcur),
                                            fill='yellow', font=("Helvetica", 11), anchor='center')
        ally_hp_calc = canvas.create_text((324, 16), text=str(ally.HPcur) + " → " + str(ally.HPcur),
                                           fill="yellow", font=("Helvetica", 11), anchor='center')

        assist_name = canvas.create_text((270, 30), text=attacker.assist.name,
                                          fill="yellow", font=("Helvetica", 11), anchor='center')

        set_banner.rect_array.append(player_hp_calc)
        set_banner.rect_array.append(ally_hp_calc)
        set_banner.rect_array.append(assist_name)

        # Icons

        player_move_icon = canvas.create_image(135, 6, anchor=tk.NW, image=move_icons[attacker.move])
        player_weapon_icon = canvas.create_image(160, 4, anchor=tk.NW, image=weapon_icons[weapons[attacker.wpnType][0]])
        ally_move_icon = canvas.create_image(540 - 135 - 20, 6, anchor=tk.NW, image=move_icons[int(ally.move)])
        ally_weapon_icon = canvas.create_image(540 - 160 - 20, 4, anchor=tk.NW, image=weapon_icons[weapons[ally.wpnType][0]])

        set_banner.rect_array.append(player_move_icon)
        set_banner.rect_array.append(player_weapon_icon)
        set_banner.rect_array.append(ally_move_icon)
        set_banner.rect_array.append(ally_weapon_icon)

        return 0

    def set_struct_forecast(attacker: Hero, structure):
        clear_banner()
        return 0

    def on_click(event):
        global animation
        if animation: return

        # Get the current mouse coordinates
        x, y = event.x, event.y

        # Out of bounds case
        if x < 0 or x > 540 or y < 90 or y > 720: return

        # Get the tile currently hovered over
        x_comp = event.x // 90
        y_comp = ((720 - event.y) // 90) + 1
        tile = x_comp + 6 * y_comp

        cur_hero = chosen_map.tiles[tile].hero_on

        if cur_hero is not None:
            # Get current sprite and index
            S = cur_hero.side
            item_index = units_all[S].index(cur_hero)
            item_id = sprite_IDs[S][item_index]

            # Start positioning of the sprite
            start_x, start_y = canvas.coords(item_id)

            # Calculate tile num and top left corner of start tile
            x_pivot = x_comp * 90
            y_pivot = (7-y_comp) * 90 + 90
            pivot_cache = (x_pivot, y_pivot)

            # Banner set to current hero
            set_banner(cur_hero)

            # Not this side's phase, no movement allowed
            if cur_hero.side != turn_info[1]:
                return

            # Hero already moved, cannot be moved again
            if cur_hero not in units_to_move:
                return

            # Drag data to be kept during a drag
            canvas.drag_data = {'cur_x': x,
                                'cur_y': y,
                                'item': item_id,
                                'start_x': start_x,
                                'start_y': start_y,
                                'index': item_index,
                                'target': None,
                                'side': S
                                }

            # Get possible tiles to move to and a shortest path to get to that tile
            moves, paths = get_possible_move_tiles(cur_hero)

            # More drag data fields to be defined
            canvas.drag_data['moves'] = []
            canvas.drag_data['paths'] = []
            canvas.drag_data['cur_tile'] = tile
            canvas.drag_data['cost'] = 0
            canvas.drag_data['targets_and_tiles'] = {}
            canvas.drag_data['targets_most_recent_tile'] = {}

            moves_obj_array = []

            # Save moves into drag data, create Move object for each possible movement
            for i in range(0, len(moves)):
                canvas.drag_data['moves'].append(moves[i].tileNum)
                canvas.drag_data['paths'].append(paths[i])
                end = moves[i].tileNum
                distance = abs(end // 6 - tile // 6) + abs(end % 6 - tile % 6)
                moves_obj_array.append(Move(end, 0, None, distance, False, paths[i]))

            canvas.drag_data['cur_path'] = paths[canvas.drag_data['moves'].index(tile)]
            canvas.drag_data['target_path'] = "NONE"
            canvas.drag_data['target_dest'] = -1

            tile_arr = []
            canvas.drag_data['blue_tile_id_arr'] = tile_arr

            # Create blue tiles in move range
            for m in moves_obj_array:
                x_comp = m.destination % 6
                y_comp = m.destination // 6
                x_pivot = x_comp * 90
                y_pivot = (7 - y_comp) * 90 + 90

                #creates new blue tile, layered under player
                curTile = canvas.create_image(x_pivot, y_pivot, anchor=tk.NW, image=bt_photo)
                tile_arr.append(curTile)
                canvas.tag_lower(curTile, item_id)

            # TO DO: create green tiles for assist range, consider available space
            perimeter_attack_range = [] # red tiles on edge of moves
            attack_range = [] # all tiles that can be attacked
            assist_range = [] # all tiles that can be assisted

            # Create red tiles for attack range
            if cur_hero.weapon is not None:
                # for all possible movement tiles
                for m in moves_obj_array:
                    # find attack range (list of ints)
                    atk_arr = get_attack_tiles(m.destination, cur_hero.weapon.range)
                    # for each tile within attack range
                    for n in atk_arr:
                        # if not already in attack range, add
                        if n not in attack_range:
                            attack_range.append(n)

                        # if not overlapping with moves and not placed already
                        if n not in canvas.drag_data['moves'] and n not in perimeter_attack_range:
                            perimeter_attack_range.append(n)

            if cur_hero.assist is not None:
                for m in moves_obj_array:
                    ast_arr = get_attack_tiles(m.destination, cur_hero.assist.range)
                    for n in ast_arr:
                        if n not in assist_range:
                            assist_range.append(n)

            for n in perimeter_attack_range:
                x_comp = n % 6
                y_comp = n // 6
                x_pivot = x_comp * 90
                y_pivot = (7 - y_comp) * 90 + 90

                # if enemy in range, use red tile instead of pale red tile
                # place this after calculating valid assist positioning?
                cur_tile_photo = prt_photo
                if chosen_map.tiles[n].hero_on is not None:
                    if chosen_map.tiles[n].hero_on.side != cur_hero.side:
                        cur_tile_photo = rt_photo
                    if chosen_map.tiles[n].hero_on.side == cur_hero.side and cur_hero.assist is not None:
                        cur_tile_photo = None

                curTile = canvas.create_image(x_pivot, y_pivot, anchor=tk.NW, image=cur_tile_photo)
                tile_arr.append(curTile)


            # find all points to attack all enemies from, fill canvas.drag_data['targets_and_tiles']
            # TO DO: find all points to use assists on all allies, consider available space for each assist
            if cur_hero.weapon is not None:
                for m in moves_obj_array:
                    atk_arr = get_attack_tiles(m.destination, cur_hero.weapon.range)
                    for n in atk_arr:
                        if chosen_map.tiles[n].hero_on is not None and chosen_map.tiles[n].hero_on.side != cur_hero.side:

                            if chosen_map.tiles[n].hero_on not in canvas.drag_data['targets_and_tiles']:
                                canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on] = [m.destination]

                            if m.destination not in canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on]:
                                canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on].append(m.destination)

            possible_assist_tile_nums = []

            confirmed_assists = []
            unconfirmed_assists = []

            if cur_hero.assist is not None:
                for m in moves_obj_array:
                    ast_arr = get_attack_tiles(m.destination, cur_hero.assist.range)
                    for n in ast_arr:
                        if (chosen_map.tiles[n].hero_on is not None and
                                chosen_map.tiles[n].hero_on.side == cur_hero.side and n != tile):

                            valid_unit_cond = False
                            valid_ally_cond = False

                            move_unit_to = -1
                            move_ally_to = -1

                            if cur_hero.assist.type == AssistType.Move:
                                if "repo" in cur_hero.assist.effects:
                                    valid_unit_cond = True
                                    move_unit_to = m.destination
                                    move_ally_to = final_reposition_tile(m.destination, n)

                                    # CONSIDER FOR WHEN HERO ON IS UNIT
                                    someone_on = chosen_map.tiles[move_ally_to].hero_on is not None and not tile

                                    no_one_on = chosen_map.tiles[move_ally_to].hero_on is None or chosen_map.tiles[move_ally_to].hero_on == cur_hero
                                    someone_on = not no_one_on

                                    ally_is_tile_accessable = can_be_on_terrain(chosen_map.tiles[move_ally_to].terrain, chosen_map.tiles[n].hero_on.move) and not someone_on
                                    valid_ally_cond = move_ally_to != -1 and ally_is_tile_accessable

                                elif "draw" in cur_hero.assist.effects:
                                    print("DRAW")
                                elif "swap" in cur_hero.assist.effects:
                                    print("SWAP")
                                elif "pivot" in cur_hero.assist.effects:
                                    print("PIVOT")
                                elif "smite" in cur_hero.assist.effects:
                                    print("SMITE")
                                elif "shove" in cur_hero.assist.effects:
                                    print("SHOVE")
                            else:
                                # big guy is a cheater
                                print("wonderhoy")

                            if valid_unit_cond and valid_ally_cond:
                                #print("DO THE MOVE!!!!!!!!!!!!")

                                # add new target and tile
                                if chosen_map.tiles[n].hero_on not in canvas.drag_data['targets_and_tiles']:
                                    canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on] = [m.destination]

                                # give more tiles to target
                                if m.destination not in canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on]:
                                        canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on].append(m.destination)

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
                x_pivot = x_comp * 90
                y_pivot = (7 - y_comp) * 90 + 90

                curTile = canvas.create_image(x_pivot, y_pivot, anchor=tk.NW, image=gt_photo)
                tile_arr.append(curTile)

            for n in unconfirmed_assists:
                if n not in confirmed_assists:
                    x_comp = n % 6
                    y_comp = n // 6
                    x_pivot = x_comp * 90
                    y_pivot = (7 - y_comp) * 90 + 90

                    curTile = canvas.create_image(x_pivot, y_pivot, anchor=tk.NW, image=prt_photo)
                    tile_arr.append(curTile)


            i = 0
            while i < len(enemy_units_all):
                canvas.tag_raise(enemy_sprite_IDs[i])
                canvas.tag_raise(grayscale_enemy_sprite_IDs[i])
                canvas.tag_raise(enemy_weapon_icons[i])
                i += 1

            i = 0
            while i < len(player_units_all):
                canvas.tag_raise(player_sprite_IDs[i])
                canvas.tag_raise(grayscale_player_sprite_IDs[i])
                canvas.tag_raise(player_weapon_icons[i])
                i += 1

            canvas.tag_raise(item_id)
            if cur_hero.side == 0:
                canvas.tag_raise(player_weapon_icons[item_index])
            if cur_hero.side == 1:
                canvas.tag_raise(enemy_weapon_icons[item_index])

            # make starting path
            first_path = canvas.create_image(pivot_cache[0], pivot_cache[1], anchor=tk.NW, image=arrow_photos[14])
            canvas.tag_lower(first_path, item_id)
            canvas.drag_data['arrow_path'] = [first_path]
            canvas.drag_data['attack_range'] = attack_range
            canvas.drag_data['assist_range'] = assist_range

        else:
            canvas.drag_data = None

    def on_drag(event):
        global animation

        if animation: return

        # Check if there is any drag data
        if canvas.drag_data:
            # Calculate the distance moved
            delta_x = event.x - canvas.drag_data['cur_x']
            delta_y = event.y - canvas.drag_data['cur_y']

            cur_hero = -1
            item_index = canvas.drag_data['index']
            grayscale_item_index = -1
            tag = -1


            if canvas.drag_data['side'] == 0:
                cur_hero = player_units_all[item_index]
                grayscale_item_index = grayscale_player_sprite_IDs[item_index]
                tag = player_tags[item_index]
            if canvas.drag_data['side'] == 1:
                cur_hero = enemy_units_all[item_index]
                grayscale_item_index = grayscale_enemy_sprite_IDs[item_index]
                tag = enemy_tags[item_index]

            # Move the item based on the distance moved

            canvas.move(tag, delta_x, delta_y)

            # Update the starting position for the next drag event
            canvas.drag_data['cur_x'] = event.x
            canvas.drag_data['cur_y'] = event.y

            cur_tile = canvas.drag_data['cur_tile']
            cur_path = canvas.drag_data['cur_path']

            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90) + 1
            new_tile = x_comp + y_comp * 6

            # different tile and within moves
            # figure out the current path

            # IF
            # moved onto a new tile,
            # new tile has hero on it,
            # tile is in attack range,
            # new tile doesn't have dragged hero on it,
            # targeted hero isn't hero on new tile
            # and targeted hero isn't on the same side as cur_hero

            # sets path/final position to target a foe

            if event.y > 91 and event.x < 539 and cur_tile != new_tile and chosen_map.tiles[new_tile].hero_on is not None and new_tile in canvas.drag_data['attack_range'] and \
                chosen_map.tiles[new_tile].hero_on != cur_hero and canvas.drag_data['target'] != chosen_map.tiles[new_tile].hero_on\
                    and chosen_map.tiles[new_tile].hero_on.side != cur_hero.side:

                if chosen_map.tiles[new_tile].hero_on.side != cur_hero.side:
                    target_tile = canvas.drag_data['targets_and_tiles'][chosen_map.tiles[new_tile].hero_on][0]

                if chosen_map.tiles[new_tile].hero_on in canvas.drag_data['targets_most_recent_tile']:
                    target_tile = canvas.drag_data['targets_most_recent_tile'][chosen_map.tiles[new_tile].hero_on]

                canvas.drag_data['target_path'] = canvas.drag_data['paths'][canvas.drag_data['moves'].index(target_tile)]
                canvas.drag_data['target_dest'] = target_tile

            # sets path/final position to target an ally

            if event.y > 91 and event.x < 539 and cur_tile != new_tile and chosen_map.tiles[new_tile].hero_on is not None and \
                new_tile in canvas.drag_data['assist_range'] and chosen_map.tiles[new_tile].hero_on != cur_hero and \
                    canvas.drag_data['target'] != chosen_map.tiles[new_tile].hero_on and chosen_map.tiles[new_tile].hero_on in canvas.drag_data['targets_and_tiles']:

                #if chosen_map.tiles[new_tile].hero_on.side != cur_hero.side:
                target_tile = canvas.drag_data['targets_and_tiles'][chosen_map.tiles[new_tile].hero_on][0]

                if chosen_map.tiles[new_tile].hero_on in canvas.drag_data['targets_most_recent_tile']:
                    target_tile = canvas.drag_data['targets_most_recent_tile'][chosen_map.tiles[new_tile].hero_on]

                canvas.drag_data['target_path'] = canvas.drag_data['paths'][canvas.drag_data['moves'].index(target_tile)]
                canvas.drag_data['target_dest'] = target_tile

            # IF
            # new tile has no hero on it or this hero on it
            # and there existed a target on previous tile

            # calculate path from drag, not targeting someone

            if event.y > 91 and event.x < 539 and (chosen_map.tiles[new_tile].hero_on is None or chosen_map.tiles[new_tile].hero_on == cur_hero) and canvas.drag_data['target'] is not None:

                canvas.drag_data['target'] = None
                set_banner(cur_hero)

                canvas.drag_data['target_path'] = "NONE"

            # IF
            # current tile isn't new tile
            # and new tile is within posible moves
            if cur_tile != new_tile and new_tile in canvas.drag_data['moves']:

                new_tile_cost = get_tile_cost(chosen_map.tiles[new_tile], cur_hero)
                canvas.drag_data['cost'] += new_tile_cost

                spaces_allowed = allowed_movement(cur_hero)
                is_allowed = canvas.drag_data['cost'] <= spaces_allowed

                # west
                if cur_tile - 1 == new_tile and is_allowed:
                    canvas.drag_data['cur_path'] += 'W'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("EW"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[cur_tile], cur_hero)

                # east
                elif cur_tile + 1 == new_tile and is_allowed:
                    canvas.drag_data['cur_path'] += 'E'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("WE"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[cur_tile], cur_hero)

                # south
                elif cur_tile - 6 == new_tile and is_allowed:
                    canvas.drag_data['cur_path'] += 'S'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("NS"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[cur_tile], cur_hero)

                # north
                elif cur_tile + 6 == new_tile and is_allowed:
                    canvas.drag_data['cur_path'] += 'N'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("SN"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[cur_tile], cur_hero)

                else:
                    canvas.drag_data['cur_path'] = canvas.drag_data['paths'][canvas.drag_data['moves'].index(new_tile)]

                    x_start_comp = canvas.drag_data['start_x'] // 90
                    y_start_comp = ((720 - canvas.drag_data['start_y']) // 90) + 1
                    recalc_tile = int(x_start_comp + 6 * y_start_comp)

                    new_cost = 0
                    for c in canvas.drag_data['cur_path']:
                        if c == 'N': recalc_tile += 6
                        if c == 'S': recalc_tile -= 6
                        if c == 'E': recalc_tile += 1
                        if c == 'W': recalc_tile -= 1
                        new_cost += get_tile_cost(chosen_map.tiles[recalc_tile], cur_hero)

                    canvas.drag_data['cost'] = new_cost

                canvas.drag_data['cur_tile'] = new_tile


            # get the x/y components of the starting tile, start drawing path from here
            x_arrow_comp = canvas.drag_data['start_x'] // 90
            y_arrow_comp = ((720 - canvas.drag_data['start_y']) // 90) + 1
            x_arrow_pivot = x_arrow_comp * 90
            y_arrow_pivot = (7 - y_arrow_comp) * 90 + 90
            arrow_start_tile = int(x_arrow_comp + 6 * y_arrow_comp)

            for arrow in canvas.drag_data['arrow_path']:
                canvas.delete(arrow)
            canvas.drag_data['arrow_path'] = []

            traced_path = canvas.drag_data['cur_path']
            if canvas.drag_data['target_path'] != "NONE":
                traced_path = canvas.drag_data['target_path']

            # draw the arrow path
            if new_tile in canvas.drag_data['moves'] or canvas.drag_data['target_path'] != "NONE":
                if len(traced_path) == 0 or event.x > 539 or event.x < 0:
                    star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=arrow_photos[MOVE_STAR])
                    canvas.drag_data['arrow_path'].append(star)
                    canvas.tag_lower(star, canvas.drag_data['item'])
                else:
                    first_dir = -1
                    if traced_path[0] == 'N': first_dir = 0
                    if traced_path[0] == 'S': first_dir = 1
                    if traced_path[0] == 'E': first_dir = 2
                    if traced_path[0] == 'W': first_dir = 3

                    arrow_offset_x, arrow_offset_y = get_arrow_offsets(first_dir)

                    first_arrow = canvas.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y, anchor=tk.NW, image=arrow_photos[first_dir])
                    canvas.drag_data['arrow_path'].append(first_arrow)
                    canvas.tag_lower(first_arrow, canvas.drag_data['item'])

                    if traced_path[0] == 'N': y_arrow_pivot -= 90
                    if traced_path[0] == 'S': y_arrow_pivot += 90
                    if traced_path[0] == 'E': x_arrow_pivot += 90
                    if traced_path[0] == 'W': x_arrow_pivot -= 90

                    i = 0
                    while i < len(traced_path) - 1:
                        cur_dir = -1
                        cur_element_1 = traced_path[i]
                        cur_element_2 = traced_path[i+1]

                        if cur_element_1 == 'N' and cur_element_2 == 'N' or cur_element_1 == 'S' and cur_element_2 == 'S': cur_dir = 8
                        if cur_element_1 == 'E' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'W': cur_dir = 9

                        if cur_element_1 == 'N' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'S': cur_dir = 10
                        if cur_element_1 == 'N' and cur_element_2 == 'W' or cur_element_1 == 'E' and cur_element_2 == 'S': cur_dir = 11
                        if cur_element_1 == 'S' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'N': cur_dir = 12
                        if cur_element_1 == 'S' and cur_element_2 == 'W' or cur_element_1 == 'E' and cur_element_2 == 'N': cur_dir = 13

                        arrow_offset_x, arrow_offset_y = get_arrow_offsets(cur_dir)

                        cur_arrow = canvas.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y, anchor=tk.NW, image=arrow_photos[cur_dir])
                        canvas.drag_data['arrow_path'].append(cur_arrow)
                        canvas.tag_lower(first_arrow, canvas.drag_data['item'])

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

                    arrow_offset_x, arrow_offset_y = get_arrow_offsets(last_dir)

                    last_arrow = canvas.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y, anchor=tk.NW, image=arrow_photos[last_dir])
                    canvas.drag_data['arrow_path'].append(last_arrow)
                    canvas.tag_lower(last_arrow, canvas.drag_data['item'])

            # delete current path, draw move_star at start only
            elif new_tile not in canvas.drag_data['moves']:
                if len(canvas.drag_data['arrow_path']) != 1:
                    for arrow in canvas.drag_data['arrow_path']:
                        canvas.delete(arrow)
                    canvas.drag_data['arrow_path'] = []
                star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=arrow_photos[MOVE_STAR])
                canvas.drag_data['arrow_path'].append(star)
                canvas.tag_lower(star, canvas.drag_data['item'])

            if canvas.drag_data['side'] == 0: cur_hero = player_units_all[canvas.drag_data['index']]
            if canvas.drag_data['side'] == 1: cur_hero = enemy_units_all[canvas.drag_data['index']]

            for x in canvas.drag_data['targets_and_tiles']:
                if cur_tile in canvas.drag_data['targets_and_tiles'][x]:
                    canvas.drag_data['targets_most_recent_tile'][x] = cur_tile

            # if
            # there is a hero on new tile,
            # current target isn't new tile hero,
            # and new tile hero isn't dragged unit,

            if (event.y > 91 and event.x > 0 and event.x < 539 and chosen_map.tiles[new_tile].hero_on is not None and
                    chosen_map.tiles[new_tile].hero_on != cur_hero and chosen_map.tiles[new_tile].hero_on != canvas.drag_data['target']):

                # set new target
                canvas.drag_data['target'] = chosen_map.tiles[new_tile].hero_on

                # if new tile in attacking range
                if new_tile in canvas.drag_data['attack_range'] and cur_hero.side != chosen_map.tiles[new_tile].hero_on.side:
                    set_attack_forecast(cur_hero, chosen_map.tiles[new_tile].hero_on)

                elif new_tile in canvas.drag_data['assist_range'] and cur_hero.side == chosen_map.tiles[new_tile].hero_on.side\
                        and chosen_map.tiles[new_tile].hero_on in canvas.drag_data['targets_and_tiles']:
                    set_assist_forecast(cur_hero, chosen_map.tiles[new_tile].hero_on)

                # new tile isn't in attacking range
                else:
                    set_banner(chosen_map.tiles[new_tile].hero_on)


            for t in canvas.drag_data['arrow_path']:
                canvas.tag_lower(t, canvas.drag_data['item'])

    def on_release(event):
        global animation

        if canvas.drag_data is not None:
            successful_move = False

            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90) + 1
            new_tile = x_comp + y_comp * 6

            mouse_new_tile = new_tile

            if canvas.drag_data['target_path'] != "NONE":
                new_tile = canvas.drag_data['target_dest']

            x_start_comp = canvas.drag_data['start_x'] // 90
            y_start_comp = ((720 - canvas.drag_data['start_y']) // 90) + 1
            recalc_tile = int(x_start_comp + 6 * y_start_comp)


            item_index = canvas.drag_data['index']
            S = canvas.drag_data['side']
            grayscale_sprite = grayscale_IDs[S][item_index]
            weapon_icon_sprite = weapon_IDs[S][item_index]

            # Set sprite to new position
            if event.x < 539 and event.x > 0 and event.y < 810 and event.y > 90 and new_tile in canvas.drag_data['moves']:
                move_to_tile(canvas, canvas.drag_data['item'], new_tile)
                move_to_tile(canvas, grayscale_sprite, new_tile)
                move_to_tile(canvas, weapon_icon_sprite, new_tile)

                units_all[S][item_index].tile.hero_on = None
                units_all[S][item_index].tile = chosen_map.tiles[new_tile]
                chosen_map.tiles[new_tile].hero_on = units_all[S][item_index]

                # move initiated if moved to a new tile or attacking
                if new_tile != recalc_tile or canvas.drag_data['target_path'] != "NONE":
                    successful_move = True

            # Restore the item to the starting position, case happens if moved to invalid start position
            else:
                move_to_tile(canvas, canvas.drag_data['item'], recalc_tile)
                move_to_tile(canvas, grayscale_sprite, recalc_tile)
                move_to_tile(canvas, weapon_icon_sprite, recalc_tile)

            for blue_tile_id in canvas.drag_data['blue_tile_id_arr']:
                canvas.delete(blue_tile_id)

            for arrow in canvas.drag_data['arrow_path']:
                canvas.delete(arrow)

            # If off-board move, nothing else to do
            if event.x < 0 or event.x > 540 or event.y < 90 or event.y > 720: return

            # Ok it might just be a failsafe for these lines
            player_original = chosen_map.tiles[new_tile].hero_on

            # ATTAAAAAAAAAAAAAAAAAAAAAAACK!!!!!!!!!!!!!!!!!!
            if event.x < 539 and event.x > 0 and event.y < 810 and event.y > 90 and canvas.drag_data['target_path'] != "NONE" and \
                    chosen_map.tiles[new_tile].hero_on.side != chosen_map.tiles[mouse_new_tile].hero_on.side:
                animation = True

                player = chosen_map.tiles[new_tile].hero_on
                enemy = chosen_map.tiles[mouse_new_tile].hero_on

                player_tile = new_tile
                enemy_tile = mouse_new_tile

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

                player_sprite = canvas.drag_data['item']

                enemy_index = -1

                if canvas.drag_data['side'] == 0:
                    enemy_index = enemy_units.index(enemy)
                    enemy_sprite = enemy_sprite_IDs[enemy_index]
                    enemy_weapon_icon = enemy_weapon_icons[enemy_index]
                if canvas.drag_data['side'] == 1:
                    enemy_index = player_units.index(enemy)
                    enemy_sprite = player_sprite_IDs[enemy_index]
                    enemy_weapon_icon = player_weapon_icons[enemy_index]

                def hide_enemy(is_alive):
                    canvas.itemconfig(enemy_sprite, state='hidden')
                    canvas.itemconfig(grayscale_sprite, state='normal')

                    if not is_alive:
                        canvas.itemconfig(enemy_weapon_icon, state='hidden')
                        move_to_tile(canvas, enemy_sprite, 100)

                def hide_player(is_alive):
                    canvas.itemconfig(player_sprite, state='hidden')
                    canvas.itemconfig(grayscale_sprite, state='normal')

                    if not is_alive:
                        canvas.itemconfig(weapon_icon_sprite, state='hidden')
                        move_to_tile(canvas, player_sprite, 100)
                        move_to_tile(canvas, grayscale_sprite, 100)

                def animation_done():
                    global animation
                    animation = False

                combat_result = simulate_combat(player, enemy, True, turn_info[0], 0, [])
                attacks = combat_result[7]

                i = 0
                while i < len(attacks):
                    if attacks[i].attackOwner == 0:
                        canvas.after(i * 500 + 200, animate_sprite_atk, canvas, player_sprite, player_atk_dir_hori, player_atk_dir_vert, attacks[i].damage, enemy_tile)
                        enemy.HPcur = max(0, enemy.HPcur - attacks[i].damage)

                    if attacks[i].attackOwner == 1:
                        canvas.after(i * 500 + 200, animate_sprite_atk, canvas, enemy_sprite, player_atk_dir_hori * -1, player_atk_dir_vert * -1, attacks[i].damage, player_tile)
                        player.HPcur = max(0, player.HPcur - attacks[i].damage)

                    if player.specialCount != -1: player.specialCount = attacks[i].spCharges[0]
                    if enemy.specialCount != -1: enemy.specialCount = attacks[i].spCharges[1]

                    if player.HPcur == 0 or enemy.HPcur == 0: break
                    i += 1

                finish_time = 500 * (i + 1) + 200

                if player.HPcur == 0:
                    canvas.after(finish_time, hide_player, False)

                    # remove from list of units
                    if chosen_map.tiles[new_tile].hero_on.side == 0: player_units.remove(chosen_map.tiles[new_tile].hero_on)
                    if chosen_map.tiles[new_tile].hero_on.side == 1: enemy_units.remove(chosen_map.tiles[new_tile].hero_on)

                    # end simulation if they were last unit alive
                    if chosen_map.tiles[new_tile].hero_on.side == 0 and not player_units:
                        canvas.after(finish_time + 500, window.destroy)

                    if chosen_map.tiles[new_tile].hero_on.side == 1 and not enemy_units:
                        canvas.after(finish_time + 500, window.destroy)

                    # take unit off map
                    chosen_map.tiles[new_tile].hero_on = None

                    canvas.after(finish_time, clear_banner)
                else:
                    canvas.after(finish_time, set_banner, chosen_map.tiles[new_tile].hero_on)

                if enemy.HPcur == 0:
                    canvas.after(finish_time, hide_enemy, False)

                    if chosen_map.tiles[new_tile].hero_on.side == 0: enemy_units.remove(chosen_map.tiles[mouse_new_tile].hero_on)
                    if chosen_map.tiles[new_tile].hero_on.side == 1: player_units.remove(chosen_map.tiles[mouse_new_tile].hero_on)
                    chosen_map.tiles[mouse_new_tile].hero_on = None

                    if chosen_map.tiles[new_tile].hero_on.side == 0 and not enemy_units:
                        canvas.after(finish_time + 500, window.destroy)

                    if chosen_map.tiles[new_tile].hero_on.side == 1 and not player_units:
                        canvas.after(finish_time + 500, window.destroy)

                canvas.after(finish_time, animation_done)
                canvas.after(finish_time, hide_player, True)

            # SUPPOOOOOOOOOOOOOOOOOOOORT!!!!!!!!!!!!!!!!!!!!
            elif event.x < 539 and event.x > 0 and event.y < 810 and event.y > 90 and canvas.drag_data['target_path'] != "NONE" and \
                    chosen_map.tiles[new_tile].hero_on.side == chosen_map.tiles[mouse_new_tile].hero_on.side:
                player = chosen_map.tiles[new_tile].hero_on
                ally = chosen_map.tiles[mouse_new_tile].hero_on

                if "repo" in player.assist.effects:


                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    final_pos = final_reposition_tile(unit_tile_num, ally_tile_num)

                    ally.tile.hero_on = None
                    ally.tile = chosen_map.tiles[final_pos]
                    chosen_map.tiles[final_pos].hero_on = ally

                    ally_index = player_units_all.index(ally)

                    ally_sprite = player_sprite_IDs[ally_index]
                    ally_weapon_icon = player_weapon_icons[ally_index]

                    move_to_tile(canvas, ally_sprite, final_pos)
                    move_to_tile(canvas, ally_weapon_icon, final_pos)


                elif "draw" in player.assist.effects:
                    print("DRAW")
                elif "swap" in player.assist.effects:
                    print("SWAP")
                elif "pivot" in player.assist.effects:
                    print("PIVOT")
                elif "smite" in player.assist.effects:
                    print("SMITE")
                elif "shove" in player.assist.effects:
                    print("SHOVE")
                set_banner(player)

            # remove player unit from units who can act

            cur_hero = player_original

            if successful_move and cur_hero in units_to_move:
                units_to_move.remove(cur_hero)

                item_index = canvas.drag_data['index']

                if cur_hero.side == 0 and not animation:
                    canvas.itemconfig(grayscale_player_sprite_IDs[item_index], state='normal')
                    canvas.itemconfig(player_sprite_IDs[item_index], state='hidden')

                if cur_hero.side == 1 and not animation:
                    canvas.itemconfig(grayscale_enemy_sprite_IDs[item_index], state='normal')
                    canvas.itemconfig(enemy_sprite_IDs[item_index], state='hidden')

            # cause next phase to start either immediately or after combat
            if not units_to_move:
                if not animation:
                    next_phase()
                if animation:
                    canvas.after(finish_time, next_phase)

            canvas.drag_data = None

    def on_double_click(event):
        x, y = event.x, event.y

        if x < 0 or x > 540 or y < 90 or y > 720: return

        x_comp = event.x // 90
        y_comp = ((720 - event.y) // 90) + 1
        selected_tile = x_comp + 6 * y_comp
        cur_hero = chosen_map.tiles[selected_tile].hero_on

        if cur_hero is not None:
            if cur_hero.side == 0 and turn_info[1] == PLAYER:
                item_index = player_units_all.index(cur_hero)
                if cur_hero in units_to_move:
                    units_to_move.remove(cur_hero)
                    canvas.itemconfig(grayscale_player_sprite_IDs[item_index], state='normal')
                    canvas.itemconfig(player_sprite_IDs[item_index], state='hidden')
                    if not units_to_move:
                        next_phase()

            if cur_hero.side == 1 and turn_info[1] == ENEMY:
                item_index = enemy_units_all.index(cur_hero)
                if cur_hero in units_to_move:
                    units_to_move.remove(cur_hero)
                    canvas.itemconfig(grayscale_enemy_sprite_IDs[item_index], state='normal')
                    canvas.itemconfig(enemy_sprite_IDs[item_index], state='hidden')
                    if not units_to_move:
                        next_phase()


    window = ttk.Window(themename='darkly')
    window.title('Fire Emblem Heroes Simulator')
    window.geometry('540x900') #tile size: 90x90
    window.iconbitmap(__location__ + "\\Sprites\\Marth.ico")

    frame = ttk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame, width=540, height=890)  # Adjust the canvas size
    canvas.drag_data = None
    canvas.pack()

    # SPRITE LOADING

    # map
    map_image = Image.open(__location__ + "\\Maps\\Story Maps\\Book 1\\Preface\\" + "story0_0_1" + ".png")
    map_photo = ImageTk.PhotoImage(map_image)
    canvas.create_image(0, 90, anchor=tk.NW, image=map_photo)

    # move tiles
    blue_tile = Image.open(__location__ + "\\CombatSprites\\" + "tileblue" + ".png")
    bt_photo = ImageTk.PhotoImage(blue_tile)

    red_tile = Image.open(__location__ + "\\CombatSprites\\" + "tilered" + ".png")
    rt_photo = ImageTk.PhotoImage(red_tile)

    pale_red_tile = Image.open(__location__ + "\\CombatSprites\\" + "tilepalered" + ".png")
    prt_photo = ImageTk.PhotoImage(pale_red_tile)

    green_tile = Image.open(__location__ +"\\CombatSprites\\" + "tilegreen" + ".png")
    gt_photo = ImageTk.PhotoImage(green_tile)

    pale_green_tile = Image.open(__location__ + "\\CombatSprites\\" + "tilepalegreen" + ".png")
    pgt_photo = ImageTk.PhotoImage(pale_green_tile)

    # arrows
    arrows = Image.open(__location__ + "\\CombatSprites\\" + "Map" + ".png")
    arrow_photos = []

    START_NORTH = 0; START_SOUTH = 1; START_EAST = 2; START_WEST = 3
    END_NORTH = 4; END_SOUTH = 5; END_EAST = 6; END_WEST = 7
    LINE_VERT = 8; LINE_HORI = 9
    BEND_NE = 10; BEND_ES = 11; BEND_SE = 12; BEND_EN = 13
    MOVE_STAR = 14

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
        arrow_photos.append(ImageTk.PhotoImage(cropped_image))

    # hero hud
    skills1 = Image.open(__location__ + "\\CombatSprites\\" + "Skill_Passive1" + ".png")
    skill_photos = []
    i = 0
    j = 0
    while i < 13:
        while j < 13:
            cropped_image = skills1.crop((74 * j, 74 * i, 74 * (j + 1), 74 * (i + 1)))
            skill_photos.append(ImageTk.PhotoImage(cropped_image))
            j += 1
        i += 1

    move_icons = []
    status_pic = Image.open(__location__ + "\\CombatSprites\\" + "Status" + ".png")

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

    # turn order

    # cur turn #, cur phase, turn limit
    turn_info = [1, PLAYER, 50]
    units_to_move = player_units[:]

    phase_label = canvas.create_text((540 / 2, 830), text="PLAYER PHASE", fill="#038cfc", font=("Helvetica", 20), anchor='center')
    next_phase.phase_txt = phase_label

    turn_label = canvas.create_text((540 / 2, 860), text="Turn " + str(turn_info[0]) + "/" + str(turn_info[2]), fill="#97a8c4", font=("Helvetica", 16), anchor='center')
    next_phase.turn_txt = turn_label

    # GENERATE ITEMS FOR EACH DRAGGABLE PLAYER

    player_tags = []
    enemy_tags = []

    # units
    player_sprites = []
    player_sprite_IDs = []
    enemy_sprites = []
    enemy_sprite_IDs = []

    grayscale_player_sprites = []
    grayscale_enemy_sprites = []
    grayscale_player_sprite_IDs = []
    grayscale_enemy_sprite_IDs = []

    player_weapon_icons = []
    enemy_weapon_icons = []

    player_special_count_labels = []
    enemy_special_count_labels = []

    player_hp_count_labels = []
    enemy_hp_count_labels = []

    player_hp_bar_bg = []
    enemy_hp_bar_bg = []
    player_hp_bar_fg = []
    enemy_hp_bar_fg = []

    player_status_img = []
    enemy_status_img = []

    units_all = [player_units_all, enemy_units_all]
    sprite_IDs = [player_sprite_IDs, enemy_sprite_IDs]
    grayscale_IDs = [grayscale_player_sprite_IDs, grayscale_enemy_sprite_IDs]
    weapon_IDs = [player_weapon_icons, enemy_weapon_icons]
    special_labels = [player_special_count_labels, enemy_special_count_labels]
    hp_labels = [player_hp_count_labels, enemy_hp_count_labels]
    hp_bar_bgs = [player_hp_bar_bg, enemy_hp_bar_bg]
    hp_bar_fgs = [player_hp_bar_fg, enemy_hp_bar_fg]

    for x in player_units_all:
        respString = "-R" if x.resp else ""
        curImage = Image.open(__location__ + "\\Sprites\\" + x.intName + respString + ".png")
        modifier = curImage.height/85
        resized_image = curImage.resize((int(curImage.width / modifier), 85), Image.LANCZOS)

        curPhoto = ImageTk.PhotoImage(resized_image)
        player_sprites.append(curPhoto)

        grayscale_image = resized_image.convert("L")

        transparent_image = Image.new("RGBA", resized_image.size, (0, 0, 0, 0))
        transparent_image.paste(grayscale_image, (0, 0), mask=resized_image.split()[3])

        grayscale_photo = ImageTk.PhotoImage(transparent_image)
        grayscale_player_sprites.append(grayscale_photo)

    for x in enemy_units_all:
        respString = "-R" if x.resp else ""
        curImage = Image.open(__location__ + "\\Sprites\\" + x.intName + respString + ".png")
        curImage = curImage.transpose(Image.FLIP_LEFT_RIGHT)
        modifier = curImage.height/85
        resized_image = curImage.resize((int(curImage.width / modifier), 85), Image.LANCZOS)

        curPhoto = ImageTk.PhotoImage(resized_image)
        enemy_sprites.append(curPhoto)

        grayscale_image = resized_image.convert("L")

        transparent_image = Image.new("RGBA", resized_image.size, (0, 0, 0, 0))
        transparent_image.paste(grayscale_image, (0, 0), mask=resized_image.split()[3])

        grayscale_photo = ImageTk.PhotoImage(transparent_image)
        grayscale_enemy_sprites.append(grayscale_photo)

    for i,player in enumerate(player_units_all):
        name = player_units_all[i].intName
        side = 'P'
        tag = f"tag_{name.replace('!', '_')}_{i}_{side}"
        player_tags.append(tag)

    for i,enemy in enumerate(enemy_units_all):
        name = enemy_units_all[i].intName
        side = 'P'
        tag = f"tag_{name.replace('!', '_')}_{i}_{side}"
        enemy_tags.append(tag)

    # PLACE IMAGES ONTO CANVAS

    for i, player_sprite in enumerate(player_sprites):
        item_id = canvas.create_image(100 * i, 200, anchor=tk.NW, image=player_sprite, tags=(player_tags[i]))
        player_sprite_IDs.append(item_id)

    for i, grayscale_player_sprite in enumerate(grayscale_player_sprites):
        item_id = canvas.create_image(100 * i, 200, anchor=tk.NW, image=grayscale_player_sprite, tags=player_tags[i])
        grayscale_player_sprite_IDs.append(item_id)

    for i, enemy_sprite in enumerate(enemy_sprites):
        item_id = canvas.create_image(100 * i, 200, anchor=tk.NW, image=enemy_sprite, tags=enemy_tags[i])
        enemy_sprite_IDs.append(item_id)

    for i, grayscale_enemy_sprite in enumerate(grayscale_enemy_sprites):
        item_id = canvas.create_image(100 * i + 200, 200, anchor=tk.NW, image=grayscale_enemy_sprite, tags=enemy_tags[i])
        grayscale_enemy_sprite_IDs.append(item_id)

    for i, player in enumerate(player_units_all):
        w_image = weapon_icons[weapons[player.wpnType][0]]
        weapon_icon = canvas.create_image(160, 50 * (i + 2), anchor=tk.NW, image=w_image, tags=player_tags[i])
        player_weapon_icons.append(weapon_icon)

        count_string = player.specialCount
        if player.specialCount == -1: count_string = ""
        special_label = canvas.create_text(200, 100 * (2 + i), text=count_string, fill="#e300e3", font=("Helvetica", 19, 'bold'), anchor='center', tags=player_tags[i])
        player_special_count_labels.append(special_label)

        hp_string = player.HPcur
        hp_label = canvas.create_text(200, 100 * (2 + i), text=hp_string, fill="blue", font=("Helvetica", 16, 'bold'), anchor='center', tags=player_tags[i])
        player_hp_count_labels.append(hp_label)


    for i, enemy in enumerate(enemy_units_all):
        w_image = weapon_icons[weapons[enemy.wpnType][0]]
        weapon_icon = canvas.create_image(160, 50 * (i + 2), anchor=tk.NW, image=w_image, tags=enemy_tags[i])
        enemy_weapon_icons.append(weapon_icon)

    # MOVE UNITS TO TILE

    i = 0
    while i < len(player_units):
        move_to_tile(canvas, player_tags[i], chosen_map.player_start_spaces[i]) # place sprite
        player_units[i].tile = chosen_map.tiles[chosen_map.player_start_spaces[i]]
        player_units[i].tile.hero_on = player_units[i]
        player_units[i].side = PLAYER

        move_to_tile_wp(canvas, player_weapon_icons[i], chosen_map.player_start_spaces[i])
        move_to_tile_sp(canvas, player_special_count_labels[i], chosen_map.player_start_spaces[i])

        move_to_tile_hp(canvas, player_hp_count_labels[i], chosen_map.player_start_spaces[i])

        canvas.itemconfig(grayscale_player_sprite_IDs[i], state='hidden')

        i += 1

    i = 0
    while i < len(enemy_units):
        move_to_tile(canvas, enemy_tags[i], chosen_map.enemy_start_spaces[i])
        enemy_units[i].tile = chosen_map.tiles[chosen_map.enemy_start_spaces[i]]
        enemy_units[i].tile.hero_on = enemy_units[i]
        enemy_units[i].side = ENEMY

        move_to_tile(canvas, enemy_weapon_icons[i], chosen_map.enemy_start_spaces[i])

        canvas.itemconfig(grayscale_enemy_sprite_IDs[i], state='hidden')

        i += 1

    # Function Assignment
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<Double-Button-1>", on_double_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    set_banner(player_units[0])
    clear_banner()

    window.mainloop()
    return 0

start_sim(player_units,enemy_units, map0)