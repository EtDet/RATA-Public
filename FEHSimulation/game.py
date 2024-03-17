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
with open(__location__ + "\\Maps\\story0-0-0.json") as read_file: data = json.load(read_file)

# Fill in terrain, starting tiles, enemy units, etc. into map
map0.define_map(data)

# hero definitions, used just for now
#bolt = Weapon("Tactical Bolt", "Tactical Bolt", "idk", 14, 2, "Sword", {"colorlessAdv": 0}, ["Robin"])
bolt = Weapon("Dosing Fang", "Dosing Fang", "idk", 1, 1, "RBeast", {"slaying": 1, "the_dose": 20}, ["Níðhöggr"])
#robin = Hero("Robin", "M!Robin", 0, "BTome", 0, [40,29,29,29,22], [50, 50, 50, 50, 40], 30, 67)
robin = Hero("Níðhöggr", "Níðhöggr", 0, "RBeast", 3, [48, 47, 17, 47, 42], [60, 70, 30, 90, 75], 5, 20)
robin.set_skill(bolt, 0)

robin.set_IVs(DEF,SPD,DEF)
robin.set_level(1)



# PLACE UNITS ONTO MAP

#robin.tile = map0.tiles[18]

player_units_all = [robin]
enemy_units_all = []

player_units = [robin]
enemy_units = []

i = 0
while i < len(data["enemyData"]):
    curEnemy = makeHero(data["enemyData"][i]["name"])

    curEnemy.side = 1
    curEnemy.set_rarity(data["enemyData"][i]["rarity"])
    curEnemy.set_level(data["enemyData"][i]["level"])

    if "weapon" in data["enemyData"][i]:
        curWpn = makeWeapon("Iron Sword")
        curEnemy.set_skill(curWpn, 0)

    if "alt_stats" in data["enemyData"][i]:
        curEnemy.visible_stats = data["enemyData"][i]["alt_stats"]
        j = 0
        while j < 5:
            curEnemy.visible_stats[j] += curEnemy.skill_stat_mods[j]
            curEnemy.visible_stats[j] = max(min(curEnemy.visible_stats[j], 99), 0)
            j += 1


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
    # queue = [(curTile, 0)]  # array of tuples of potential movement tiles, current costs, and current optimal pattern
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

                # if tile cost within allowed cost and
                if cost + neighbor_cost <= spaces_allowed and neighbor_cost >= 0 and x.hero_on is None:
                    queue.append((x, cost + neighbor_cost, path_str + char_arr[i]))
                    visited.add(x)
            i += 1

    return (possible_tiles, optimal_moves)

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


turn_count = 0
TURN_LIMIT = 50
phase = ENEMY

animation = False


def move_sprite_to_tile(my_canvas, item_ID, num):
    x_move = 45 + 90 * (num % 6)
    y_move = 135 + 90 * (7 - (num//6))

    my_canvas.coords(item_ID, x_move-40, y_move-40)

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

        #print(name, move_type, weapon_type, level, merges, stats, buffs, debuffs, blessing, weapon, assist, special, askill, bskill, cskill, sSeal, xskill)

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

        set_banner.rect_array.append(canvas.create_text((331, (25 + 38) / 2), text="🛡️", fill="green", font=("Helvetica", 12), anchor='e'))
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

    def set_forecast(attacker: Hero, defender: Hero):
        clear_banner()

        result = simulate_combat(attacker, defender, True, turn_count, 0, [])

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



    def on_click(event):

        global animation
        if animation: return

        # Get the current mouse coordinates
        x, y = event.x, event.y

        # Find all items overlapping with the mouse coordinates
        overlapping_items = canvas.find_overlapping(x, y, x, y)

        # Check if any of the overlapping items are player units
        player_units_overlapping = [item for item in overlapping_items if item in player_sprite_IDs]
        enemy_units_overlapping = [item for item in overlapping_items if item in enemy_sprite_IDs]

        if player_units_overlapping:
            # Remember the starting position of the drag and the item
            item_id = player_units_overlapping[0]
            item_index = player_sprite_IDs.index(item_id)
            start_x, start_y = canvas.coords(item_id)
            canvas.drag_data = {'x': x, 'y': y, 'item': item_id, 'start_x': start_x, 'start_y': start_y, 'index': item_index, 'target': None}

            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90) + 1
            new_tile = x_comp + 6 * y_comp
            x_pivot = x_comp * 90
            y_pivot = (7-y_comp) * 90 + 90

            pivot_cache = (x_pivot, y_pivot)

            cur_hero = player_units[canvas.drag_data['index']]
            set_banner(cur_hero)
            moves, paths = get_possible_move_tiles(cur_hero)

            canvas.drag_data['moves'] = []
            canvas.drag_data['paths'] = []
            canvas.drag_data['cur_tile'] = new_tile
            canvas.drag_data['cost'] = 0

            canvas.drag_data['targets_and_tiles'] = {}
            canvas.drag_data['targets_most_recent_tile'] = {}

            #canvas.drag_data['animation_go'] = False

            moves_obj_array = []
            a = cur_hero.tile.tileNum

            for x in enemy_sprite_IDs:
                canvas.tag_lower(x, item_id)

            for i in range(0, len(moves)):
                canvas.drag_data['moves'].append(moves[i].tileNum)
                canvas.drag_data['paths'].append(paths[i])
                b = moves[i].tileNum
                dist = abs(b // 6 - a // 6) + abs(b % 6 - a % 6)
                moves_obj_array.append(Move(b, 0, None, dist, False, paths[i]))

            canvas.drag_data['cur_path'] = paths[canvas.drag_data['moves'].index(new_tile)]
            canvas.drag_data['target_path'] = "NONE"
            canvas.drag_data['target_dest'] = -1

            #i = 0
            tile_arr = []
            canvas.drag_data['blue_tile_id_arr'] = tile_arr

            # create blue tiles for move range
            for m in moves_obj_array:
                x_comp = m.destination % 6
                y_comp = m.destination // 6
                x_pivot = x_comp * 90
                y_pivot = (7 - y_comp) * 90 + 90

                #creates new blue tile
                curTile = canvas.create_image(x_pivot, y_pivot, anchor=tk.NW, image=bt_photo)
                tile_arr.append(curTile)
                canvas.tag_lower(curTile, item_id)

            # create red tiles for attack range
            dupe_cache = []
            attack_range = []
            for m in moves_obj_array:
                atk_arr = get_attack_tiles(m.destination, cur_hero.weapon.range)
                for n in atk_arr:
                    if n not in attack_range: attack_range.append(n)
                    if n not in canvas.drag_data['moves'] and n not in dupe_cache:
                        dupe_cache.append(n)

                        x_comp = n % 6
                        y_comp = n // 6
                        x_pivot = x_comp * 90
                        y_pivot = (7 - y_comp) * 90 + 90

                        cur_red_tile = prt_photo
                        if chosen_map.tiles[n].hero_on != None:
                            if chosen_map.tiles[n].hero_on.side != cur_hero.side:
                                cur_red_tile = rt_photo

                        curTile = canvas.create_image(x_pivot, y_pivot, anchor=tk.NW, image=cur_red_tile)
                        tile_arr.append(curTile)
                        canvas.tag_lower(curTile, item_id)

                        for x in enemy_sprite_IDs:
                            canvas.tag_lower(curTile, x)


            # find all points to attack all enemies from, fill canvas.drag_data['targets_and_tiles']

            for m in moves_obj_array:
                atk_arr = get_attack_tiles(m.destination, cur_hero.weapon.range)
                for n in atk_arr:
                    if chosen_map.tiles[n].hero_on != None:
                        if chosen_map.tiles[n].hero_on.side != cur_hero.side:

                            if chosen_map.tiles[n].hero_on not in canvas.drag_data['targets_and_tiles']:
                                canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on] = [m.destination]

                            for target in canvas.drag_data['targets_and_tiles']:
                                if m.destination not in canvas.drag_data['targets_and_tiles'][target]:
                                    canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on].append(m.destination)



            # make starting path
            first_path = canvas.create_image(pivot_cache[0], pivot_cache[1], anchor=tk.NW, image=arrow_photos[14])
            canvas.tag_lower(first_path, item_id)
            canvas.drag_data['arrow_path'] = [first_path]
            canvas.drag_data['attack_range'] = attack_range

        elif enemy_units_overlapping:

            item_id = enemy_units_overlapping[0]
            item_index = enemy_sprite_IDs.index(item_id)
            cur_hero = enemy_units[item_index]
            set_banner(cur_hero)
            canvas.drag_data = None

        else:

            canvas.drag_data = None

    def on_drag(event):

        global animation

        if animation: return

        # Check if there is any drag data
        if canvas.drag_data:
            # Calculate the distance moved
            delta_x = event.x - canvas.drag_data['x']
            delta_y = event.y - canvas.drag_data['y']

            # Move the item based on the distance moved

            canvas.move(canvas.drag_data['item'], delta_x, delta_y)

            # Update the starting position for the next drag event
            canvas.drag_data['x'] = event.x
            canvas.drag_data['y'] = event.y

            cur_tile = canvas.drag_data['cur_tile']
            cur_path = canvas.drag_data['cur_path']

            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90) + 1
            new_tile = x_comp + y_comp * 6

            cur_hero = player_units[canvas.drag_data['index']]

            # different tile and within moves
            # figure out the current path

            if cur_tile != new_tile and chosen_map.tiles[new_tile].hero_on is not None and new_tile in canvas.drag_data['attack_range'] and \
                chosen_map.tiles[new_tile].hero_on != cur_hero and canvas.drag_data['target'] != chosen_map.tiles[new_tile].hero_on:


                target_tile = canvas.drag_data['targets_and_tiles'][chosen_map.tiles[new_tile].hero_on][0]

                if chosen_map.tiles[new_tile].hero_on in canvas.drag_data['targets_most_recent_tile']:
                    target_tile = canvas.drag_data['targets_most_recent_tile'][chosen_map.tiles[new_tile].hero_on]

                canvas.drag_data['target_path'] = canvas.drag_data['paths'][canvas.drag_data['moves'].index(target_tile)]
                canvas.drag_data['target_dest'] = target_tile


            elif (chosen_map.tiles[new_tile].hero_on is None or chosen_map.tiles[new_tile].hero_on == cur_hero) and canvas.drag_data['target_path'] != "NONE":

                canvas.drag_data['target'] = None
                set_banner(cur_hero)

                canvas.drag_data['target_path'] = "NONE"

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
                if len(traced_path) == 0:
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

            cur_hero = player_units[canvas.drag_data['index']]

            for x in canvas.drag_data['targets_and_tiles']:
                if cur_tile in canvas.drag_data['targets_and_tiles'][x]:
                    canvas.drag_data['targets_most_recent_tile'][x] = cur_tile

            # if there is a hero on new tile, current target isn't new tile hero, and new tile hero isn't dragged unit,
            if chosen_map.tiles[new_tile].hero_on is not None and chosen_map.tiles[new_tile].hero_on != cur_hero and chosen_map.tiles[new_tile].hero_on != canvas.drag_data['target']:

                # set new target
                canvas.drag_data['target'] = chosen_map.tiles[new_tile].hero_on

                # if new tile in attacking range
                if new_tile in canvas.drag_data['attack_range']:
                    set_forecast(cur_hero, chosen_map.tiles[new_tile].hero_on)

                # new tile isn't in attacking range
                else:
                    set_banner(chosen_map.tiles[new_tile].hero_on)


            for t in canvas.drag_data['arrow_path']:
                canvas.tag_lower(t, canvas.drag_data['item'])

    def on_release(event):
        global animation

        if canvas.drag_data is not None:
            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90) + 1
            new_tile = x_comp + y_comp * 6

            mouse_new_tile = new_tile

            if canvas.drag_data['target_path'] != "NONE":
                new_tile = canvas.drag_data['target_dest']

            #print(canvas.drag_data)

            # Set sprite to new position
            if event.y > 90 and event.y < 810 and event.x > 0 and event.x < 540 and new_tile in canvas.drag_data['moves']:


                move_sprite_to_tile(canvas, canvas.drag_data['item'], new_tile)
                player_units[canvas.drag_data['index']].tile.hero_on = None
                player_units[canvas.drag_data['index']].tile = chosen_map.tiles[new_tile]
                chosen_map.tiles[new_tile].hero_on = player_units[canvas.drag_data['index']]



            # Restore the item to the starting position, case happens if moved to invalid start position
            else:
                canvas.coords(canvas.drag_data['item'], canvas.drag_data['start_x'], canvas.drag_data['start_y'])

            for blue_tile_id in canvas.drag_data['blue_tile_id_arr']:
                canvas.delete(blue_tile_id)
            canvas.drag_data['blue_tile_id_arr'] = []

            for arrow in canvas.drag_data['arrow_path']:
                canvas.delete(arrow)
            canvas.drag_data['arrow_path'] = []

            if canvas.drag_data['target_path'] != "NONE":
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

                if player_tile / 6 < enemy_tile / 6:
                    player_atk_dir_vert = 1
                elif player_tile / 6 > enemy_tile / 6:
                    player_atk_dir_vert = -1

                player_sprite = canvas.drag_data['item']
                enemy_sprite = enemy_sprite_IDs[enemy_units.index(enemy)]

                def hide_enemy():
                    canvas.itemconfig(enemy_sprite, state = 'hidden')

                def animation_done():
                    # for future debugging: give animation an integer value,
                    # animation must currently be this integer value to be reset
                    # this function call might be called once another combat begins
                    global animation
                    animation = False

                #print(player_sprite, enemy_sprite)

                combat_result = simulate_combat(player, enemy, True, turn_count, 0, [])

                attacks = combat_result[7]

                i = 0
                while i < len(attacks):
                    if attacks[i].attackOwner == 0:
                        canvas.after(i * 500 + 200, animate_sprite_atk, canvas, player_sprite, player_atk_dir_hori, player_atk_dir_vert, attacks[i].damage, enemy_tile)

                        enemy.HPcur = max(0, enemy.HPcur - attacks[i].damage)
                        if enemy.HPcur == 0: break

                    if attacks[i].attackOwner == 1:
                        canvas.after(i * 500 + 200, animate_sprite_atk, canvas, enemy_sprite, player_atk_dir_hori * -1, player_atk_dir_vert * -1, attacks[i].damage, player_tile)

                        player.HPcur = max(0, player.HPcur - attacks[i].damage)
                        if player.HPcur == 0: break

                    i += 1

                finish_time = 500 * (i + 1) + 200

                if player.HPcur == 0:
                    canvas.itemconfig(player_sprite, state='hidden')
                    chosen_map.tiles[new_tile].hero_on = None
                else:
                    canvas.after(finish_time, set_banner, chosen_map.tiles[new_tile].hero_on)

                if enemy.HPcur == 0:
                    canvas.after(finish_time, hide_enemy)
                    chosen_map.tiles[mouse_new_tile].hero_on = None

                canvas.after(finish_time, animation_done)

            canvas.drag_data = None



        # window

    window = ttk.Window(themename='darkly')
    #window = ttk.Window()
    window.title('Fire Emblem Heroes Simulator')
    window.geometry('540x900') #tile size: 90x90
    window.iconbitmap(__location__ + "\\Sprites\\Marth.ico")

    frame = ttk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame, width=540, height=810)  # Adjust the canvas size
    canvas.pack()

    # map
    map_image = Image.open(__location__ + "\\Maps\\" + "story0_0_0" + ".png")
    map_photo = ImageTk.PhotoImage(map_image)
    canvas.create_image(0, 90, anchor=tk.NW, image=map_photo)

    # move tiles
    blue_tile = Image.open(__location__ + "\\CombatSprites\\" + "tileblue" + ".png")
    bt_photo = ImageTk.PhotoImage(blue_tile)

    red_tile = Image.open(__location__ + "\\CombatSprites\\" + "tilered" + ".png")
    rt_photo = ImageTk.PhotoImage(red_tile)

    pale_red_tile = Image.open(__location__ + "\\CombatSprites\\" + "tilepalered" + ".png")
    prt_photo = ImageTk.PhotoImage(pale_red_tile)

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

    #print(weapon_icons)


    # units
    player_sprites = []
    player_sprite_IDs = []
    enemy_sprites = []
    enemy_sprite_IDs = []
    for x in player_units:
        respString = "-R" if x.resp else ""
        curImage = Image.open(__location__ + "\\Sprites\\" + x.intName + respString + ".png")
        modifier = curImage.height/85
        resized_image = curImage.resize((int(curImage.width / modifier), 85), Image.LANCZOS)
        curPhoto = ImageTk.PhotoImage(resized_image)
        player_sprites.append(curPhoto)

    for i, player_sprite in enumerate(player_sprites):
        item_id = canvas.create_image(100 * i, 200, anchor=tk.NW, image=player_sprite)
        player_sprite_IDs.append(item_id)

    for x in enemy_units:
        respString = "-R" if x.resp else ""
        curImage = Image.open(__location__ + "\\Sprites\\" + x.intName + respString + ".png")
        curImage = curImage.transpose(Image.FLIP_LEFT_RIGHT)
        modifier = curImage.height/85
        resized_image = curImage.resize((int(curImage.width / modifier), 85), Image.LANCZOS)
        curPhoto = ImageTk.PhotoImage(resized_image)
        enemy_sprites.append(curPhoto)

    for i, enemy_sprite in enumerate(enemy_sprites):
        item_id = canvas.create_image(100 * i, 200, anchor=tk.NW, image=enemy_sprite)
        enemy_sprite_IDs.append(item_id)

    i = 0
    while i < len(player_units):
        move_sprite_to_tile(canvas, player_sprite_IDs[i], chosen_map.player_start_spaces[i]) # place sprite
        player_units[i].tile = chosen_map.tiles[chosen_map.player_start_spaces[i]]
        player_units[i].tile.hero_on = player_units[i]
        player_units[i].side = PLAYER
        i += 1

    i = 0
    while i < len(enemy_units):
        move_sprite_to_tile(canvas, enemy_sprite_IDs[i], chosen_map.enemy_start_spaces[i])
        enemy_units[i].tile = chosen_map.tiles[chosen_map.enemy_start_spaces[i]]
        enemy_units[i].tile.hero_on = enemy_units[i]
        enemy_units[i].side = ENEMY
        i += 1

    # Bind mouse events for drag-and-drop
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)


    window.mainloop()
    return 0

start_sim(player_units,enemy_units, map0)