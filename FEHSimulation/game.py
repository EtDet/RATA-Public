from combat import *
from field_helpers import start_of_turn, end_of_combat, create_combat_fields, get_warp_moves
from map import Map
import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import os
import json
from re import sub

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
#with open(__location__ + "\\Maps\\Story Maps\\Book 1\\Preface\\story0-0-1.json") as read_file: data = json.load(read_file)
with open(__location__ + "\\Maps\\Test Maps\\test1.json") as read_file: data = json.load(read_file)

# Fill in terrain, starting tiles, enemy units, etc. into map
map0.define_map(data)

# hero definitions, used just for now
'''
bolt = Weapon("Tactical Bolt", "Tactical Bolt", "idk", 14, 2, "Sword", {"colorlessAdv": 0}, ["Robin"])
robin = Hero("Robin", "M!Robin", 0, "BTome", 0, [40,29,29,29,22], [50, 50, 50, 50, 40], 30, 67)
robin.set_skill(bolt, WEAPON)

reposition = Assist("Reposition", "", {"repo":0}, 1, "Move", {})
robin.set_skill(reposition, ASSIST)

robin.set_IVs(ATK,SPD,ATK)
robin.set_level(40)

'''

ragnell = Weapon("Emblem Ragnell", "Emblem Ragnell", "", 16, 1, "Sword", {"slaying": 1, "dCounter": 0, "BIGIKEFAN": 1018}, {})
GREAT_AETHER = Special("Great Aether", "", {"numFoeAtkBoostSp": 4, "AETHER_GREAT": 17}, 4, SpecialType.Offense)
honeAtk1 = makeSkill("Hone Atk 1")

ike = makeHero("E!Ike")

ike.set_skill(ragnell, WEAPON)
ike.set_skill(GREAT_AETHER, SPECIAL)
ike.set_skill(honeAtk1, CSKILL)

ike.set_IVs(ATK,SPD,ATK)
ike.set_level(40)

united_bouquet = Weapon("United Bouquet", "United Bouquet", "", 16, 1, "Lance", {"slaying": 1, "bridal_shenanigans": 2}, {})
forever_yours = makeSkill("Forever Yours")
no_quarter = makeSpecial("No Quarter")
atkspd_excel = makeSkill("Atk/Spd Excel")
potent4 = makeSkill("Potent 4")



xander = makeHero("DA!Xander")
xander.set_skill(makeWeapon("Dusk Uchiwa+"), WEAPON)
xander.set_skill(makeAssist("Dance"), ASSIST)
xander.set_skill(makeSkill("Close Counter"), ASKILL)
xander.set_skill(makeSkill("Quick Riposte 3"), BSKILL)
xander.set_skill(makeSkill("Odd Def Wave 3"), CSKILL)

sharena = Hero("Sharena", "BR!Sharena", 0, "Lance", 1, [40, 44, 47, 32, 21], [50, 70, 90, 50, 35], 5, 24)

sharena.set_skill(united_bouquet, WEAPON)
sharena.set_skill(no_quarter, SPECIAL)
sharena.set_skill(atkspd_excel, ASKILL)
sharena.set_skill(potent4, BSKILL)
sharena.set_skill(forever_yours, CSKILL)

sharena.set_IVs(SPD,DEF,ATK)
sharena.set_level(40)


# PLACE UNITS ONTO MAP

#robin.tile = map0.tiles[18]

tested_unit = makeHero("Gaius")
tested_weapon = makeWeapon("Rogue Dagger+")
tested_assist = makeAssist("Rally Speed")
tested_special = makeSpecial("Growing Thunder")
tested_askill = makeSkill("Defiant Atk 3")
tested_bskill = makeSkill("Pass 3")
#tested_cskill = makeSkill("Fortify Def 3")

#xander.allySupport = "M!Corrin"
#tested_unit.allySupport = "DA!Xander"

tested_unit.set_skill(tested_weapon, WEAPON)
tested_unit.set_skill(tested_assist, ASSIST)
tested_unit.set_skill(tested_special, SPECIAL)
tested_unit.set_skill(tested_askill, ASKILL)
tested_unit.set_skill(tested_bskill, BSKILL)
#tested_unit.set_skill(tested_cskill, CSKILL)

player_units_all = [ike, sharena, xander, tested_unit]
enemy_units_all = []

player_units = player_units_all[:]
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
        curEnemy.set_skill(curWpn, WEAPON)

    if "assist" in data["enemyData"][i]:
        curAssist = makeAssist(data["enemyData"][i]["assist"])
        curEnemy.set_skill(curAssist, ASSIST)

    if "special" in data["enemyData"][i]:
        curSpecial = makeSpecial(data["enemyData"][i]["special"])
        curEnemy.set_skill(curSpecial, SPECIAL)

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
def get_possible_move_tiles(hero, enemy_team):
    curTile = hero.tile

    spaces_allowed = allowed_movement(hero)

    visited = set()         # tiles that have already been visited
    queue = [(curTile, 0, "")]  # array of tuples of potential movement tiles, current costs, and current optimal pattern
    possible_tiles = []     # unique, possible tiles, to be returned
    optimal_moves = []

    char_arr = ['N', 'S', 'E', 'W']

    # pass condition
    pass_cond = False
    if "passSk" in hero.getSkills():
        pass_cond = hero.HPcur >= 1 - 0.25 * hero.getSkills()["passSk"]
    if "passW" in hero.getSkills() and not pass_cond:
        pass_cond = hero.HPcur >= 1 - 0.25 * hero.getSkills()["passW"]

    # obstruct tiles created
    obstruct_tiles = get_obstruct_tiles(hero, enemy_team)
    visited_obstruct_tiles = []

    # while possibilities exist
    while queue:
        # get current tuple
        current_tile, cost, path_str = queue.pop(0)

        # not possible if too far
        if cost > spaces_allowed: break

        if current_tile in obstruct_tiles and not pass_cond and current_tile != hero.tile:
            visited_obstruct_tiles.append(current_tile)
            continue

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
                within_allowed_cost = cost + neighbor_cost <= spaces_allowed

                if within_allowed_cost and neighbor_cost >= 0 and (x.hero_on is None or (x.hero_on is not None and x.hero_on.side == hero.side) or pass_cond):
                    queue.append((x, cost + neighbor_cost, path_str + char_arr[i]))
                    visited.add(x)
            i += 1

    final_possible_tiles = []
    final_optimal_moves = []

    if possible_tiles:
        final_possible_tiles.append(possible_tiles[0])
        final_optimal_moves.append(optimal_moves[0])

    # remove tiles with other units on as valid moves
    i = 1
    while i < len(possible_tiles):
        if possible_tiles[i].hero_on is None:
            final_possible_tiles.append(possible_tiles[i])
            final_optimal_moves.append(optimal_moves[i])
        i += 1

    return (final_possible_tiles, final_optimal_moves, visited_obstruct_tiles)

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

# OBSTRUCT TILE PLACEMENTS
def get_obstruct_tiles(unit, enemy_team):
    all_obstruct_tiles = []
    for enemy in enemy_team:
        enemy_skills = enemy.getSkills()
        if "obstruct" in enemy_skills and enemy.HPcur/enemy.visible_stats[HP] >= 1.1 - enemy_skills["obstruct"] * 0.2:
            tiles = enemy.tile.tilesWithinNSpaces(1)
            for x in tiles:
                if x not in all_obstruct_tiles:
                    all_obstruct_tiles.append(x)

    return all_obstruct_tiles


# ASSIST SKILL VALIDATION

# Get tile moved to if unit at u_tile used reposition on ally at a_tile
# Used for getting exact movements after assist skills or post-combat movements
def final_reposition_tile(u_tile, a_tile):
    if u_tile == -1 or a_tile == -1:
        return -1

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

aoe_patterns = {
    1: [-2, -1, 0, 1, 2],    # Rising/Blazing Flame
    2: [-7, -5, 0, 5, 7],    # Rising/Blazing Light
    3: [-12, -6, 0, 6, 12],  # Rising/Blazing Thunder
    4: [-6, -1, 0, 1, 6],    # Rising/Blazing Wind & Gifted Magic (I & II)

    11: [-7, -5, -2, -1, 0, 1, 2, 5, 7],      # Growing Flame
    12: [-12, -7, -5, -2, 0, 2, 5, 7, 12],    # Growing Light
    13: [-18, -12, -6, -1, 0, 1, 6, 12, 18],  # Growing Thunder
    14: [-7, -6, -5, -1, 0, 1, 5, 6, 7],      # Growing Wind
}

# Under assumption of 6x8 map
# Constants to assume whether a tile is valid for AOE targeting (not off map)
tile_conditions = {
    -18: lambda x: 0 <= x <= 48,
    -12: lambda x: 0 <= x <= 48,
    -7: lambda x: 0 <= x <= 48 and (x-1) % 6 < 5,
    -6: lambda x: 0 <= x <= 48,
    -5: lambda x: 0 <= x and x <= 47 and (x+1) % 6 > 0,
    -2: lambda x: (x-2) % 6 < 4,
    -1: lambda x: (x-1) % 6 < 5,
    0: lambda x: True,
    1: lambda x: (x+1) % 6 > 0,
    2: lambda x: (x+2) % 6 > 1,
    5: lambda x: 0 <= x <= 48 and (x-1) % 6 < 5,
    6: lambda x: 0 <= x <= 48,
    7: lambda x: 0 <= x <= 48 and (x+1) % 6 > 0,
    12: lambda x: 0 <= x <= 48,
    18: lambda x: 0 <= x <= 48,
}

# Returns all tiles to be targeted by an AOE move given a certain position and tile range
def aoe_tiles(u_tile, aoe_range_num):

    pattern = aoe_patterns[aoe_range_num]

    final_tiles = []

    for tile in pattern:
        if tile_conditions[tile](u_tile) and tile + u_tile >= 0 and tile + u_tile <= 47:
            final_tiles.append(tile + u_tile)

    return final_tiles

# If the unit's move type can be on the given terrain
def can_be_on_terrain(terrain_int, move_type_int):
    if terrain_int == 0 or terrain_int == 3: return True
    if terrain_int == 4: return False

    if terrain_int == 1:
        if move_type_int == 1: return False
        else: return True

    if terrain_int == 2:
        if move_type_int == 2: return True
        else: return False

# Global animation variable
animation = False



# Move different types of images to a set location
def move_to_tile(my_canvas, item_ID, num):
    x_move = 45 + 90 * (num % 6)
    y_move = 135 + 90 * (7 - (num//6))

    my_canvas.coords(item_ID, x_move, y_move)

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

def move_to_tile_fg_bar(my_canvas, rect_ID, num):
    x_move = 45 + 90 * (num % 6)
    y_move = 135 + 90 * (7 - (num // 6))

    my_canvas.moveto(rect_ID, x_move - 18, y_move + 29)

# Move a sprite towards one direction, then return them to their original position
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

# Create red text number at tile num
def animate_damage_popup(canvas, number, text_tile):
    x_comp = text_tile % 6
    y_comp = text_tile // 6
    x_pivot = x_comp * 90 + 45
    y_pivot = (7 - y_comp) * 90 + 90 + 45

    displayed_text2 = canvas.create_text((x_pivot+2, y_pivot+2), text=str(number), fill='#111111', font=("Helvetica", 25, 'bold'), anchor='center')
    displayed_text = canvas.create_text((x_pivot, y_pivot), text=str(number), fill='#de1d1d', font=("Helvetica", 25, 'bold'), anchor='center')

    canvas.after(350, forget_text, canvas, displayed_text)
    canvas.after(350, forget_text, canvas, displayed_text2)

# Create green text number at tile num
def animate_heal_popup(canvas, number, text_tile):
    x_comp = text_tile % 6
    y_comp = text_tile // 6
    x_pivot = x_comp * 90 + 45
    y_pivot = (7 - y_comp) * 90 + 90 + 45

    displayed_text2 = canvas.create_text((x_pivot+2, y_pivot+2), text=str(number), fill='#111111', font=("Helvetica", 25, 'bold'), anchor='center')
    displayed_text = canvas.create_text((x_pivot, y_pivot), text=str(number), fill='#14c454', font=("Helvetica", 25, 'bold'), anchor='center')

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

        while units_to_move:
            units_to_move.pop()

        # increment count if player phase
        if turn_info[1] == PLAYER:
            turn_info[0] += 1

            canvas.delete(next_phase.turn_txt)
            next_phase.turn_txt = canvas.create_text((540 / 2, 860), text="Turn " + str(turn_info[0]) + "/" + str(turn_info[2]), fill="#97a8c4", font=("Helvetica", 16), anchor='center')

            canvas.delete(next_phase.phase_txt)
            next_phase.phase_txt = canvas.create_text((540 / 2, 830), text="PLAYER PHASE", fill="#038cfc", font=("Helvetica", 20), anchor='center')


            for x in player_units:
                units_to_move.append(x)
                x.statusPos = []
                x.buffs = [0] * 5
                x.special_galeforce_triggered = False

            for i in range(0, len(enemy_units_all)):
                canvas.itemconfig(grayscale_enemy_sprite_IDs[i], state='hidden')
                canvas.itemconfig(enemy_sprite_IDs[i], state='normal')

            damage, heals = start_of_turn(player_units, turn_info[0])



        if turn_info[1] == ENEMY:
            canvas.delete(next_phase.phase_txt)
            next_phase.phase_txt = canvas.create_text((540 / 2, 830), text="ENEMY PHASE", fill="#e8321e", font=("Helvetica", 20), anchor='center')

            for x in enemy_units:
                units_to_move.append(x)
                x.statusPos = []
                x.buffs = [0] * 5
                x.special_galeforce_triggered = False

            for i in range(0, len(player_units_all)):
                canvas.itemconfig(grayscale_player_sprite_IDs[i], state='hidden')
                canvas.itemconfig(player_sprite_IDs[i], state='normal')

            damage, heals = start_of_turn(enemy_units, turn_info[0])

        i = 0
        while i < len(player_units):
            if player_units[i].specialCount != -1:
                canvas.itemconfig(player_special_count_labels[i], text=player_units[i].specialCount)
            i += 1

        i = 0
        while i < len(enemy_units):
            if enemy_units[i].specialCount != -1:
                canvas.itemconfig(enemy_special_count_labels[i], text=enemy_units[i].specialCount)
            i += 1

        for unit in player_units:
            if unit in heals:
                unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + heals[unit])
                animate_heal_popup(canvas, heals[unit], unit.tile.tileNum)
                set_hp_visual(unit, unit.HPcur)

            unit.unitCombatInitiates = 0

        for unit in enemy_units:
            if unit in heals:
                unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + heals[unit])
                animate_heal_popup(canvas, heals[unit], unit.tile.tileNum)
                set_hp_visual(unit, unit.HPcur)

            unit.unitCombatInitiates = 0

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
        int_name_weapon = '-'
        assist = "-"
        special = "-"
        askill = "-"
        bskill = "-"
        cskill = "-"
        sSeal = "-"
        xskill = "-"

        if hero.weapon is not None:
            weapon = hero.weapon.name
            int_name_weapon = hero.weapon.intName
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

        # STAT LABEL
        fills = ['white'] * 5

        is_neutral_iv = hero.asset == hero.flaw
        is_asc = hero.asset != hero.asc_asset
        is_merged = hero.merges > 0

        if not is_neutral_iv:
            fills[hero.asset] = 'blue'

        if not is_merged and hero.asset != hero.flaw and hero.flaw != hero.asc_asset:
            fills[hero.flaw] = 'red'

        if is_neutral_iv and hero.asset != hero.asc_asset or \
            hero.asset != hero.flaw and hero.flaw != hero.asc_asset and is_asc or \
            not is_neutral_iv and hero.flaw == hero.asc_asset and is_merged:

            fills[hero.asc_asset] = 'blue'

        set_banner.rect_array.append(canvas.create_rectangle((131, 30, 291, 47), fill="#73666c", width=0))

        set_banner.rect_array.append(canvas.create_rectangle((131, 49, 209, 64), fill="#6e4046", width=0))
        set_banner.rect_array.append(canvas.create_rectangle((211, 49, 291, 64), fill="#4d6e40", width=0))
        set_banner.rect_array.append(canvas.create_rectangle((131, 66, 209, 81), fill="#87764c", width=0))
        set_banner.rect_array.append(canvas.create_rectangle((211, 66, 291, 81), fill="#466569", width=0))

        set_banner.rect_array.append(canvas.create_text((155, 38), text="HP", fill=fills[HP], font=("Helvetica", 11)))

        set_banner.rect_array.append(canvas.create_text((155, 56), text="Atk", fill=fills[ATK], font=("Helvetica", 11)))
        set_banner.rect_array.append(canvas.create_text((235, 56), text="Spd", fill=fills[SPD], font=("Helvetica", 11)))
        set_banner.rect_array.append(canvas.create_text((155, 73), text="Def", fill=fills[DEF], font=("Helvetica", 11)))
        set_banner.rect_array.append(canvas.create_text((235, 73), text="Res", fill=fills[RES], font=("Helvetica", 11)))

        fills = ['white'] * 5

        i = 0
        while i < 5:
            if hero.buffs[i] > abs(hero.debuffs[i]):
                fills[i] = 'blue'
            if abs(hero.debuffs[i]) > hero.buffs[i]:
                fills[i] = 'red'

            if i == HP and hero.HPcur < 10:
                fills[i] = 'red'

            i += 1

        percentage = trunc(hero.HPcur/stats[HP] * 1000) / 10
        if percentage == 100.0:
            percentage = 100

        set_banner.rect_array.append(canvas.create_text((185, 38), text=hero.HPcur, fill=fills[HP], font=("Helvetica", 12)))
        set_banner.rect_array.append(canvas.create_text((205, 38), text="/" + str(stats[HP]), fill='white', font=("Helvetica", 12)))
        set_banner.rect_array.append(canvas.create_text((250, 38), text=str(percentage) + "%", fill='white', font=("Helvetica", 12)))

        displayed_atk = min(max(stats[ATK] + hero.buffs[ATK] + hero.debuffs[ATK], 0), 99)
        displayed_spd = min(max(stats[SPD] + hero.buffs[SPD] + hero.debuffs[SPD], 0), 99)
        displayed_def = min(max(stats[DEF] + hero.buffs[DEF] + hero.debuffs[DEF], 0), 99)
        displayed_res = min(max(stats[RES] + hero.buffs[RES] + hero.debuffs[RES], 0), 99)

        set_banner.rect_array.append(canvas.create_text((185, 56), text=displayed_atk, fill=fills[ATK], font=("Helvetica", 11)))
        set_banner.rect_array.append(canvas.create_text((265, 56), text=displayed_spd, fill=fills[SPD], font=("Helvetica", 11)))
        set_banner.rect_array.append(canvas.create_text((185, 73), text=displayed_def, fill=fills[DEF], font=("Helvetica", 11)))
        set_banner.rect_array.append(canvas.create_text((265, 73), text=displayed_res, fill=fills[RES], font=("Helvetica", 11)))

        # SKILLS
        set_banner.rect_array.append(canvas.create_text((308, (5 + 22) / 2), text="⚔️", fill="red", font=("Helvetica", 9), anchor='e'))
        text_coords = ((310 + 410) / 2, (5 + 22) / 2)

        refine_suffixes = ("Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz")

        weapon_fill = "white"
        if int_name_weapon.endswith(refine_suffixes):
            weapon_fill = "#6beb34"

        ref_str = ""
        for suffix in refine_suffixes:
            if int_name_weapon.endswith(suffix):
                ref_str = " (" + suffix[0] + ")"

        set_banner.rect_array.append(canvas.create_text(*text_coords, text=weapon + ref_str , fill=weapon_fill, font=("Helvetica", 9), anchor='center'))

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

        # STATUS EFFECTS DISPLAY
        status_rect = canvas.create_rectangle((75, 49, 127, 81), fill="#7388bd", width=0, tags='status')
        set_banner.rect_array.append(status_rect)
        text_coords = (101, 65)
        set_banner.rect_array.append(canvas.create_text(*text_coords, text="Statuses", fill="white", font=("Helvetica", 9), anchor='center', tags='status'))

        set_banner.base_rect = None

        positive_statuses = hero.statusPos
        negative_statuses = hero.statusNeg

        set_banner.status_rects = []
        set_banner.status_texts = []

        def on_enter(event):
            if set_banner.base_rect is None:
                set_banner.base_rect = canvas.create_rectangle(0, 0, 50, 50, fill="#434959")

                green_fill = '#5ebf5e'
                red_fill = '#bf5149'

                panic_factor = 1
                if Status.Panic in hero.statusNeg: panic_factor = -1
                if Status.NullPanic in hero.statusPos: panic_factor = 1

                has_stat_bonuses = sum(hero.buffs) > 0
                has_stat_penalties = sum(hero.debuffs) < 0

                if has_stat_bonuses:
                    fill = green_fill
                    operator = "+"
                    if panic_factor == -1:
                        fill = red_fill
                        operator = "-"

                    status_rect = canvas.create_rectangle(0, 0, 130, 22, tags='one_status', fill=fill)
                    set_banner.status_rects.append(status_rect)

                    buffs_string = ""
                    if hero.buffs[ATK] > 0:
                        buffs_string += "A" + operator + str(hero.buffs[ATK]) + " "
                    if hero.buffs[SPD] > 0:
                        buffs_string += "S" + operator + str(hero.buffs[SPD]) + " "
                    if hero.buffs[DEF] > 0:
                        buffs_string += "D" + operator + str(hero.buffs[DEF]) + " "
                    if hero.buffs[RES] > 0:
                        buffs_string += "R" + operator + str(hero.buffs[RES])

                    status_text = canvas.create_text(0, 0, text=buffs_string, tags='one_text', fill='white')
                    set_banner.status_texts.append(status_text)

                if has_stat_penalties:
                    status_rect = canvas.create_rectangle(0, 0, 130, 22, tags='one_status', fill=red_fill)
                    set_banner.status_rects.append(status_rect)

                    debuffs_string = ""
                    if hero.debuffs[ATK] < 0:
                        debuffs_string += "A" + str(hero.debuffs[ATK]) + " "
                    if hero.debuffs[SPD] < 0:
                        debuffs_string += "S" + str(hero.debuffs[SPD]) + " "
                    if hero.debuffs[DEF] < 0:
                        debuffs_string += "D" + str(hero.debuffs[DEF]) + " "
                    if hero.debuffs[RES] < 0:
                        debuffs_string += "R" + str(hero.debuffs[RES])

                    status_text = canvas.create_text(0, 0, text=debuffs_string, tags='one_text', fill='white')
                    set_banner.status_texts.append(status_text)

                i = 0
                while i < len(positive_statuses):
                    status_rect = canvas.create_rectangle(0, 0, 130, 22, tags='one_status', fill=green_fill)
                    set_banner.status_rects.append(status_rect)

                    status_name = positive_statuses[i].name
                    spaced_name = sub(r'([A-Z])', r' \1', status_name)
                    spaced_name = spaced_name.strip()

                    status_text = canvas.create_text(0, 0, text=spaced_name, tags='one_text', fill='white')
                    set_banner.status_texts.append(status_text)

                    i += 1

                while i < len(positive_statuses) + len(negative_statuses):
                    status_rect = canvas.create_rectangle(0, 0, 130, 22, tags='one_status', fill=red_fill)
                    set_banner.status_rects.append(status_rect)

                    status_name = negative_statuses[i - len(positive_statuses)].name
                    spaced_name = sub(r'([A-Z])', r' \1', status_name)
                    spaced_name = spaced_name.strip()

                    status_text = canvas.create_text(0, 0, text=spaced_name, tags='one_text', fill='white')
                    set_banner.status_texts.append(status_text)

                    i += 1

                if len(set_banner.status_rects) == 0:
                    status_text = canvas.create_text(0, 0, text="No Effects", tags='one_text', fill='white')
                    set_banner.status_texts.append(status_text)

                canvas.bind("<Motion>", on_motion)

        def on_motion(event):
            if set_banner.base_rect is not None:

                has_stat_bonuses = sum(hero.buffs) > 0
                has_stat_penalties = sum(hero.debuffs) > 0

                num_bars = int(has_stat_bonuses) + int(has_stat_penalties) + len(positive_statuses) + len(negative_statuses)

                base_length = max(25 * num_bars, 25)

                canvas.coords(set_banner.base_rect, event.x + 12, event.y + 15, event.x + 150, event.y + base_length + 20)

                # no statuses/bonus/penalties, only creates "No Statuses" text
                if len(set_banner.status_rects) == 0 and len(set_banner.status_texts) == 1:
                    canvas.moveto(set_banner.status_texts[0], event.x + 20, event.y + 4 + 20)

                i = 0
                while i < len(set_banner.status_rects):
                    canvas.moveto(set_banner.status_rects[i], event.x + 15, event.y - 2 + (25 * i) + 20)
                    canvas.moveto(set_banner.status_texts[i], event.x + 20, event.y + 4 + (25 * i) + 20)
                    i += 1

        def on_leave(event):
            if set_banner.base_rect is not None:
                canvas.delete(set_banner.base_rect)

                for x in set_banner.status_rects:
                    canvas.delete(x)

                for x in set_banner.status_texts:
                    canvas.delete(x)

                set_banner.base_rect = None
                set_banner.status_rects = []
                set_banner.status_texts = []
                canvas.unbind("<Motion>")

        canvas.tag_bind("status", "<Enter>", on_enter)
        canvas.tag_bind("status", "<Leave>", on_leave)



    def set_attack_forecast(attacker: Hero, defender: Hero, distance):
        clear_banner()


        result = simulate_combat(attacker, defender, True, turn_info[0], distance, combat_fields)

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

        atkHP = attacker.HPcur
        defHP = defender.HPcur

        aoe_present = False
        if attacker.special is not None and attacker.special.type == "AOE" and attacker.specialCount == 0:
            aoe_damage: int = get_AOE_damage(attacker, defender)

            defHP = max(1, defHP - aoe_damage)

            aoe_present = True

        if aoe_present:
            atk_feh_math = str(aoe_damage) + "+" + str(atk_feh_math)

        i = 0
        while i < len(attacks):
            if attacks[i].attackOwner == 0:
                defHP = max(0, defHP - attacks[i].damage)
                atkHP = min(attacker.stats[HP], atkHP + attacks[i].healed)

            if attacks[i].attackOwner == 1:
                atkHP = max(0, atkHP - attacks[i].damage)
                defHP = min(defender.stats[HP], defHP + attacks[i].healed)

            if atkHP == 0 or defHP == 0: break
            i += 1

        player_hp_calc = canvas.create_text((215, 16), text=str(player_HPcur) + " → " + str(atkHP), fill='yellow',font=("Helvetica", 13), anchor='center')
        enemy_hp_calc = canvas.create_text((324, 16), text=str(enemy_HPcur) + " → " + str(defHP), fill="yellow", font=("Helvetica", 13), anchor='center')

        set_banner.rect_array.append(player_hp_calc)
        set_banner.rect_array.append(enemy_hp_calc)

        # Weapon Triangle Advantage

        if wpn_adv == 0:
            adv_arrow = canvas.create_text((255, 13), text=" ⇑ ", fill='#42bf34',font=("Helvetica", 20, 'bold'), anchor='center')
            disadv_arrow = canvas.create_text((285, 13), text=" ⇓ ", fill='red',font=("Helvetica", 20, 'bold'), anchor='center')
            set_banner.rect_array.append(adv_arrow)
            set_banner.rect_array.append(disadv_arrow)
        if wpn_adv == 1:
            adv_arrow = canvas.create_text((255, 13), text=" ↓ ", fill='red', font=("Helvetica", 14), anchor='center')
            disadv_arrow = canvas.create_text((285, 13), text=" ↑ ", fill='#42bf34', font=("Helvetica", 14, 'bold'), anchor='center')
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
            atk_sp_charge = canvas.create_text((270 - 135, 35), text=player_spCount, fill='#ff33ff', font=("Helvetica", 12), anchor='center')
            set_banner.rect_array.append(atk_sp_charge)

        if enemy_spCount != -1:
            def_sp_charge = canvas.create_text((270 + 135, 35), text=enemy_spCount, fill='#ff33ff', font=("Helvetica", 12), anchor='center')
            set_banner.rect_array.append(def_sp_charge)

        player_atk_text = canvas.create_text((40, 35), text="Atk" + "+" * (player_combat_buffs[ATK] >= 0) + str(player_combat_buffs[ATK]), fill='#db3b25', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_atk_text)
        player_spd_text = canvas.create_text((90, 35), text="Spd" + "+" * (player_combat_buffs[SPD] >= 0) + str(player_combat_buffs[SPD]), fill='#17eb34', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_spd_text)
        player_def_text = canvas.create_text((60, 48), text="Def" + "+" * (player_combat_buffs[DEF] >= 0) + str(player_combat_buffs[DEF]), fill='#dbdb25', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_def_text)
        player_res_text = canvas.create_text((110, 48), text="Res" + "+" * (player_combat_buffs[RES] >= 0) + str(player_combat_buffs[RES]), fill='#25dbd2', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_res_text)

        player_atk_text = canvas.create_text((450, 35), text="Atk" + "+" * (enemy_combat_buffs[ATK] >= 0) + str(enemy_combat_buffs[ATK]), fill='#db3b25', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_atk_text)
        player_spd_text = canvas.create_text((500, 35), text="Spd" + "+" * (enemy_combat_buffs[SPD] >= 0) + str(enemy_combat_buffs[SPD]), fill='#17eb34', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_spd_text)
        player_def_text = canvas.create_text((430, 48), text="Def" + "+" * (enemy_combat_buffs[DEF] >= 0) + str(enemy_combat_buffs[DEF]), fill='#dbdb25', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_def_text)
        player_res_text = canvas.create_text((480, 48), text="Res" + "+" * (enemy_combat_buffs[RES] >= 0) + str(enemy_combat_buffs[RES]), fill='#25dbd2', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_res_text)

        box_size = 30
        gap_size = 8

        num_strikes = len(attacks) + int(aoe_present)

        cur_box_pos = int(270 - (gap_size * 0.5 * (num_strikes-1) + box_size * 0.5 * (num_strikes-1)))

        set_banner.rect_array.append(canvas.create_rectangle(cur_box_pos - 110, 54, cur_box_pos - 20, 76, fill="silver", outline='#dae6e2'))

        set_banner.rect_array.append(canvas.create_text((cur_box_pos - 65, 65), text="Attack Order", fill='black', font=("Helvetica", 10, "bold"), anchor='center'))

        # AOE Special
        if aoe_present:
            box_color = "#6e2a9c"
            set_banner.rect_array.append(canvas.create_rectangle(cur_box_pos - 15, 50, cur_box_pos + 15, 80, fill=box_color, outline='#dae6e2'))

            set_banner.rect_array.append(canvas.create_text((cur_box_pos, 65), text=aoe_damage, fill='#e8c35d', font=("nintendoP_Skip-D_003", 10), anchor='center'))

            cur_box_pos += int(box_size + gap_size)

        # Attacks

        for x in attacks:
            box_color = "#18284f" if x.attackOwner == attacker.side else "#541616"

            set_banner.rect_array.append(canvas.create_rectangle(cur_box_pos - 15, 50, cur_box_pos + 15, 80, fill=box_color, outline='#dae6e2'))

            dmg_fill = '#e8c35d'
            if x.attackOwner == 0 and atk_eff:
                dmg_fill = '#46eb34'
            if x.attackOwner == 1 and def_eff:
                dmg_fill = '#46eb34'

            set_banner.rect_array.append(canvas.create_text((cur_box_pos, 65), text=x.damage, fill=dmg_fill, font=("nintendoP_Skip-D_003", 10), anchor='center'))

            cur_box_pos += int(box_size + gap_size)

    def set_assist_forecast(attacker: Hero, ally: Hero):
        clear_banner()

        #print(attacker.name, ally.name)


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

        new_player_hp = attacker.HPcur
        new_ally_hp = ally.HPcur

        # Calculate HP after healing
        if "heal" in attacker.assist.effects:
            hp_healed_ally = attacker.assist.effects["heal"]
            hp_healed_self = 0

            panic_factor = 1
            if Status.Panic in attacker.statusNeg: panic_factor = -1
            if Status.NullPanic in attacker.statusPos: panic_factor = 1
            self_atk_stat = attacker.visible_stats[ATK] + attacker.buffs[ATK] * panic_factor + attacker.debuffs[ATK]

            # Reconcile
            if "heal_self" in attacker.assist.effects:
                hp_healed_self = attacker.assist.effects["heal_self"]

            # Martyr
            if attacker.assist.effects["heal"] == -3:
                dmg_taken = attacker.visible_stats[HP] - attacker.HPcur
                hp_healed_ally = dmg_taken + 7
                hp_healed_self = dmg_taken//2

            # Martyr+
            if attacker.assist.effects["heal"] == -49:
                dmg_taken = attacker.visible_stats[HP] - attacker.HPcur
                hp_healed_ally = dmg_taken + self_atk_stat//2
                hp_healed_self = dmg_taken//2

            # Recover+
            if attacker.assist.effects["heal"] == -10:
                hp_healed_ally = max(self_atk_stat//2 + 10, 15)

            if attacker.specialCount == 0 and attacker.special.type == "Healing":
                if "boost_heal" in attacker.special.effects:
                    hp_healed_ally += attacker.special.effects["boost_heal"]

                if "heal_allies" in attacker.special.effects:
                    hp_healed_ally += attacker.special.effects["heal_allies"]

            if "live_to_serve" in attacker.bskill.effects:
                percentage = 0.25 + 0.25 * attacker.bskill.effects["live_to_serve"]
                hp_healed_self += trunc(hp_healed_ally * percentage)

            new_ally_hp = min(ally.visible_stats[HP], ally.HPcur + hp_healed_ally)
            new_player_hp = min(attacker.visible_stats[HP], attacker.HPcur + hp_healed_self)

        if "rec_aid" in attacker.assist.effects:
            new_ally_hp = min(ally.visible_stats[HP], attacker.HPcur)
            new_player_hp = min(attacker.visible_stats[HP], ally.HPcur)

        if "ardent_sac" in attacker.assist.effects:
            new_ally_hp = min(ally.visible_stats[HP], ally.HPcur + 10)
            new_player_hp = max(1, player.HPcur - 10)


        player_hp_calc = canvas.create_text((215, 16), text=str(attacker.HPcur) + " → " + str(new_player_hp),
                                            fill='yellow', font=("Helvetica", 11), anchor='center')
        ally_hp_calc = canvas.create_text((324, 16), text=str(ally.HPcur) + " → " + str(new_ally_hp),
                                           fill="yellow", font=("Helvetica", 11), anchor='center')

        set_banner.rect_array.append(canvas.create_rectangle(270 - 65, 27, 270 + 65, 42, fill='#5a5c6b', outline='#dae6e2'))

        assist_name = canvas.create_text((270, 34), text=attacker.assist.name, fill="white", font=("Helvetica", 11), anchor='center')

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
        if x < 0 or x > 540 or y <= 90 or y > 810:
            print("homer simpson")
            return

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

            # Calculate tile num and top left corner of start tile
            pixel_offset_x = x_comp * 90
            pixel_offset_y = (7-y_comp) * 90 + 90

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
                                'cur_tile': tile,
                                'start_x_comp': x_comp,
                                'start_y_comp': y_comp,
                                'index': item_index,
                                'side': S
                                }

            cur_hero_team = units_alive[S]
            enemy_team = units_all[S-1]

            # Get possible tiles to move to and a shortest path to get to that tile
            moves, paths, obstruct_tiles = get_possible_move_tiles(cur_hero, enemy_team)

            # Get possible tiles to warp to
            warp_moves = get_warp_moves(cur_hero, cur_hero_team, enemy_team)

            # More drag data fields to be defined
            canvas.drag_data['moves'] = []
            canvas.drag_data['paths'] = []
            canvas.drag_data['cost'] = 0
            canvas.drag_data['target'] = None
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

            canvas.drag_data['cur_path'] = ""
            canvas.drag_data['target_path'] = "NONE"
            canvas.drag_data['target_dest'] = -1

            # Establish each possible non-obstruct-based warp movement as a Move object
            for i in range(0, len(warp_moves)):
                if warp_moves[i].tileNum not in canvas.drag_data['moves']:

                    canvas.drag_data['moves'].append(warp_moves[i].tileNum)
                    canvas.drag_data['paths'].append("WARP")
                    end = warp_moves[i].tileNum
                    distance = abs(end // 6 - tile // 6) + abs(end % 6 - tile % 6)
                    moves_obj_array.append(Move(end, 0, None, distance, True, "WARP"))

            # Establish each possible obstruct-based warp movement as a Move object
            for i in range(0, len(obstruct_tiles)):
                if obstruct_tiles[i].tileNum not in canvas.drag_data['moves'] and obstruct_tiles[i].hero_on is None:
                    canvas.drag_data['moves'].append(obstruct_tiles[i].tileNum)
                    canvas.drag_data['paths'].append("WARP")
                    end = obstruct_tiles[i].tileNum
                    distance = abs(end // 6 - tile // 6) + abs(end % 6 - tile % 6)
                    moves_obj_array.append(Move(end, 0, None, distance, True, "WARP"))

            # Keep track of all blue tiles such that they can be destroyed upon release (should be kept in an array outside of method)
            tile_arr = []
            canvas.drag_data['tile_id_arr'] = tile_arr

            # Create blue tiles for each possible movement
            for m in moves_obj_array:
                x_comp = m.destination % 6
                y_comp = m.destination // 6
                cur_pixel_offset_x = x_comp * 90
                cur_pixel_offset_y = (7 - y_comp) * 90 + 90

                tile_photo = bt_photo
                if m.is_warp:
                    tile_photo = lbt_photo

                #creates new blue tile, layered under player
                curTile = canvas.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW, image=tile_photo)
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

            # Draw red attack tiles within range
            for n in perimeter_attack_range:
                x_comp = n % 6
                y_comp = n // 6
                cur_pixel_offset_x = x_comp * 90
                cur_pixel_offset_y = (7 - y_comp) * 90 + 90

                # if enemy in range, use red tile instead of pale red tile
                # place this after calculating valid assist positioning?
                cur_tile_photo = prt_photo
                if chosen_map.tiles[n].hero_on is not None:
                    if chosen_map.tiles[n].hero_on.side != cur_hero.side:
                        cur_tile_photo = rt_photo
                    if chosen_map.tiles[n].hero_on.side == cur_hero.side and cur_hero.assist is not None:
                        cur_tile_photo = None

                curTile = canvas.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW, image=cur_tile_photo)
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

                            if cur_hero.assist.type == "Move":
                                if "repo" in cur_hero.assist.effects:
                                    valid_unit_cond = True
                                    move_ally_to = final_reposition_tile(m.destination, n)

                                    # CONSIDER FOR WHEN HERO ON IS UNIT
                                    someone_on = chosen_map.tiles[move_ally_to].hero_on is not None and not tile

                                    no_one_on = chosen_map.tiles[move_ally_to].hero_on is None or chosen_map.tiles[move_ally_to].hero_on == cur_hero
                                    someone_on = not no_one_on

                                    ally_is_tile_accessable = can_be_on_terrain(chosen_map.tiles[move_ally_to].terrain, chosen_map.tiles[n].hero_on.move) and not someone_on
                                    valid_ally_cond = move_ally_to != -1 and ally_is_tile_accessable

                                elif "draw" in cur_hero.assist.effects:
                                    move_unit_to = final_reposition_tile(m.destination, n)
                                    move_ally_to = m.destination

                                    ally = chosen_map.tiles[n].hero_on

                                    no_one_on = chosen_map.tiles[move_unit_to].hero_on is None or chosen_map.tiles[move_unit_to].hero_on == cur_hero

                                    no_one_on_ally = chosen_map.tiles[move_ally_to].hero_on is None or chosen_map.tiles[move_ally_to].hero_on == cur_hero

                                    valid_unit_cond = can_be_on_terrain(chosen_map.tiles[move_unit_to].terrain, cur_hero.move) and move_unit_to != -1 and no_one_on
                                    valid_ally_cond = can_be_on_terrain(chosen_map.tiles[move_ally_to].terrain, ally.move) and move_ally_to != -1 and no_one_on_ally

                                elif "swap" in cur_hero.assist.effects:

                                    move_unit_to = n
                                    move_ally_to = m.destination

                                    valid_unit_cond = can_be_on_terrain(chosen_map.tiles[move_unit_to].terrain, cur_hero.move)
                                    valid_ally_cond = can_be_on_terrain(chosen_map.tiles[move_ally_to].terrain, chosen_map.tiles[move_unit_to].hero_on.move)

                                elif "pivot" in cur_hero.assist.effects:
                                    valid_ally_cond = True

                                    move_self_to = final_reposition_tile(n, m.destination)

                                    if move_self_to != -1:
                                        unit_on_dest = chosen_map.tiles[move_self_to].hero_on is not None and chosen_map.tiles[move_self_to].hero_on != cur_hero
                                        can_traverse_dest = can_be_on_terrain(chosen_map.tiles[unit_on_dest].terrain, player.move)

                                        if not unit_on_dest and can_traverse_dest:
                                            valid_unit_cond = True

                                elif "smite" in cur_hero.assist.effects:

                                    skip_over = final_reposition_tile(n, m.destination)
                                    final_dest = final_reposition_tile(skip_over, n)

                                    valid_unit_cond = True

                                    ally = chosen_map.tiles[n].hero_on

                                    valid_shove = False
                                    valid_smite = False

                                    # First, check if shove is possible
                                    if skip_over != -1:
                                        unit_on_dest = chosen_map.tiles[skip_over].hero_on is not None and chosen_map.tiles[skip_over].hero_on != cur_hero
                                        can_traverse_dest = can_be_on_terrain(chosen_map.tiles[skip_over].terrain, ally.move)

                                        valid_shove = not unit_on_dest and can_traverse_dest

                                    if final_dest != -1:
                                        unit_on_dest = chosen_map.tiles[final_dest].hero_on is not None and chosen_map.tiles[final_dest].hero_on != cur_hero
                                        can_traverse_dest = can_be_on_terrain(chosen_map.tiles[final_dest].terrain, ally.move)

                                        foe_on_skip = chosen_map.tiles[skip_over].hero_on is not None and chosen_map.tiles[skip_over].hero_on.side != cur_hero.side
                                        can_skip = chosen_map.tiles[skip_over].terrain != 4 and not foe_on_skip

                                        valid_smite = not unit_on_dest and can_traverse_dest and can_skip

                                    valid_ally_cond = valid_shove or valid_smite

                                elif "shove" in cur_hero.assist.effects:
                                    final_dest = final_reposition_tile(n, m.destination)
                                    valid_unit_cond = True

                                    ally = chosen_map.tiles[n].hero_on

                                    valid_shove = False
                                    if final_dest != -1:
                                        unit_on_dest = chosen_map.tiles[final_dest].hero_on is not None and chosen_map.tiles[final_dest].hero_on != cur_hero
                                        can_traverse_dest = can_be_on_terrain(chosen_map.tiles[final_dest].terrain, ally.move)

                                        valid_shove = not unit_on_dest and can_traverse_dest

                                    valid_ally_cond = valid_shove

                            elif cur_hero.assist.type == "Staff":
                                if "heal" in cur_hero.assist.effects:
                                    valid_unit_cond = True

                                    ally = chosen_map.tiles[n].hero_on

                                    valid_ally_cond = ally.side == cur_hero.side and ally.HPcur != ally.visible_stats[HP]

                            elif cur_hero.assist.type == "Rally":
                                valid_unit_cond = True

                                given_stats = [0, 0, 0, 0]
                                if "rallyAtk" in cur_hero.assist.effects:
                                    given_stats[ATK-1] += cur_hero.assist.effects["rallyAtk"]
                                if "rallySpd" in cur_hero.assist.effects:
                                    given_stats[SPD-1] += cur_hero.assist.effects["rallySpd"]
                                if "rallyDef" in cur_hero.assist.effects:
                                    given_stats[DEF-1] += cur_hero.assist.effects["rallyDef"]
                                if "rallyRes" in cur_hero.assist.effects:
                                    given_stats[RES-1] += cur_hero.assist.effects["rallyRes"]

                                i = 0
                                while i < len(given_stats):
                                    ally = chosen_map.tiles[n].hero_on
                                    if given_stats[i] > ally.buffs[i + 1]:
                                        valid_ally_cond = True
                                    i += 1

                            elif cur_hero.assist.type == "Refresh":
                                valid_unit_cond = True

                                ally = chosen_map.tiles[n].hero_on
                                has_dance_cond = ally.assist is None or (ally.assist is not None and ally.assist.type != "Refresh")
                                valid_ally_cond = ally.side == cur_hero.side and ally not in units_to_move and has_dance_cond
                            elif cur_hero.assist.type == "Other":
                                if "rec_aid" in cur_hero.assist.effects:
                                    ally = chosen_map.tiles[n].hero_on

                                    ally_HP_result = min(ally.visible_stats[HP], player.HPcur)
                                    player_HP_result = min(player.visible_stats[HP], ally.HPcur)

                                    valid_unit_cond = player_HP_result > player.HPcur or ally_HP_result > ally.HPcur
                                    valid_ally_cond = True

                                elif "ardent_sac" in cur_hero.assist.effects:
                                    ally = chosen_map.tiles[n].hero_on

                                    valid_unit_cond = player.HPcur > 10
                                    valid_ally_cond = ally.HPcur != ally.visible_stats[HP]
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
                cur_pixel_offset_x = x_comp * 90
                cur_pixel_offset_y = (7 - y_comp) * 90 + 90

                curTile = canvas.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW, image=gt_photo)
                tile_arr.append(curTile)

            for n in unconfirmed_assists:
                if n not in confirmed_assists:
                    x_comp = n % 6
                    y_comp = n // 6
                    cur_pixel_offset_x = x_comp * 90
                    cur_pixel_offset_y = (7 - y_comp) * 90 + 90

                    curTile = canvas.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW, image=prt_photo)
                    tile_arr.append(curTile)


            i = 0
            while i < len(enemy_units_all):
                canvas.tag_raise(enemy_sprite_IDs[i])
                canvas.tag_raise(grayscale_enemy_sprite_IDs[i])
                canvas.tag_raise(enemy_weapon_icons[i])
                canvas.tag_raise(enemy_hp_count_labels[i])
                canvas.tag_raise(enemy_special_count_labels[i])
                canvas.tag_raise(enemy_hp_bar_bg[i])
                canvas.tag_raise(enemy_hp_bar_fg[i])
                i += 1

            i = 0
            while i < len(player_units_all):
                canvas.tag_raise(player_sprite_IDs[i])
                canvas.tag_raise(grayscale_player_sprite_IDs[i])
                canvas.tag_raise(player_weapon_icons[i])
                canvas.tag_raise(player_hp_count_labels[i])
                canvas.tag_raise(player_special_count_labels[i])
                canvas.tag_raise(player_hp_bar_bg[i])
                canvas.tag_raise(player_hp_bar_fg[i])
                i += 1

            canvas.tag_raise(item_id)

            if cur_hero.side == 0:
                canvas.tag_raise(player_weapon_icons[item_index])
                canvas.tag_raise(player_hp_count_labels[item_index])
                canvas.tag_raise(player_special_count_labels[item_index])
                canvas.tag_raise(player_hp_bar_bg[item_index])
                canvas.tag_raise(player_hp_bar_fg[item_index])
            if cur_hero.side == 1:
                canvas.tag_raise(enemy_weapon_icons[item_index])
                canvas.tag_raise(enemy_hp_count_labels[item_index])
                canvas.tag_raise(enemy_special_count_labels[item_index])
                canvas.tag_raise(enemy_hp_bar_bg[item_index])
                canvas.tag_raise(enemy_hp_bar_fg[item_index])

            # make starting path
            first_path = canvas.create_image(pixel_offset_x, pixel_offset_y, anchor=tk.NW, image=arrow_photos[14])
            canvas.tag_lower(first_path, item_id)

            canvas.drag_data['arrow_path'] = [first_path]
            canvas.drag_data['attack_range'] = attack_range
            canvas.drag_data['assist_range'] = confirmed_assists

        else:
            canvas.drag_data = None

    def on_drag(event):
        global animation

        if animation: return

        # Check if there is any drag data already
        if canvas.drag_data:

            # Calculate the distance moved
            delta_x = event.x - canvas.drag_data['cur_x']
            delta_y = event.y - canvas.drag_data['cur_y']

            item_index = canvas.drag_data['index']
            S = canvas.drag_data['side']

            cur_hero = units_all[S][item_index]
            tag = tags_all[S][item_index]

            # Move the item based on the distance moved
            canvas.move(tag, delta_x, delta_y)

            # Update the starting position for the next drag event
            canvas.drag_data['cur_x'] = event.x
            canvas.drag_data['cur_y'] = event.y

            # tile from previous movement
            prev_tile_int = canvas.drag_data['cur_tile']

            # tile from current movement
            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90) + 1
            cur_tile_int = x_comp + y_comp * 6

            # Out of bounds, we've done enough
            if event.x <= 0 or event.x >= 540 or event.y <= 90 or event.y >= 810:
                return

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

            cur_tile_Obj = chosen_map.tiles[cur_tile_int]
            prev_tile_Obj = chosen_map.tiles[prev_tile_int]

            within_horizontal_bounds = event.y > 91 and event.x < 539
            moved_to_different_tile = prev_tile_int != cur_tile_int

            if within_horizontal_bounds and moved_to_different_tile and cur_tile_Obj.hero_on is not None and \
                cur_tile_Obj.hero_on != cur_hero and canvas.drag_data['target'] != cur_tile_Obj.hero_on:

                # Target foe with an attack
                if cur_tile_int in canvas.drag_data['attack_range'] and cur_tile_Obj.hero_on.side != cur_hero.side:

                    if cur_tile_Obj.hero_on.side != cur_hero.side:
                        target_tile = canvas.drag_data['targets_and_tiles'][cur_tile_Obj.hero_on][0]

                    if cur_tile_Obj.hero_on in canvas.drag_data['targets_most_recent_tile']:
                        target_tile = canvas.drag_data['targets_most_recent_tile'][cur_tile_Obj.hero_on]

                    canvas.drag_data['target_path'] = canvas.drag_data['paths'][canvas.drag_data['moves'].index(target_tile)]
                    canvas.drag_data['target_dest'] = target_tile


                # Target ally with a support
                elif cur_tile_int in canvas.drag_data['assist_range'] and cur_tile_Obj.hero_on.side == cur_hero.side:
                    target_tile = canvas.drag_data['targets_and_tiles'][chosen_map.tiles[cur_tile_int].hero_on][0]

                    if chosen_map.tiles[cur_tile_int].hero_on in canvas.drag_data['targets_most_recent_tile']:
                        target_tile = canvas.drag_data['targets_most_recent_tile'][chosen_map.tiles[cur_tile_int].hero_on]

                    canvas.drag_data['target_path'] = canvas.drag_data['paths'][canvas.drag_data['moves'].index(target_tile)]
                    canvas.drag_data['target_dest'] = target_tile

                # Eh who cares
                else:
                    canvas.drag_data['target'] = None
                    set_banner(cur_hero)
                    canvas.drag_data['target_path'] = "NONE"

                    for x in aoe_special_icons_active:
                        canvas.delete(x)
                    aoe_special_icons_active.clear()

            # Edge case of hitting a foe adjacent to unit with an AOE attack
            elif within_horizontal_bounds and cur_tile_Obj.hero_on is not None and cur_tile_Obj.hero_on == cur_hero:
                for x in aoe_special_icons_active:
                    canvas.delete(x)
                aoe_special_icons_active.clear()


            # IF
            # new tile has no hero on it or this hero on it
            # and there existed a target on previous tile

            # not targeting someone

            #print((chosen_map.tiles[cur_tile_int].hero_on is None or chosen_map.tiles[cur_tile_int].hero_on == cur_hero))
            if event.y > 91 and event.x > 0 and event.x < 539 and (chosen_map.tiles[cur_tile_int].hero_on is None or chosen_map.tiles[cur_tile_int].hero_on == cur_hero) and canvas.drag_data['target'] is not None:

                canvas.drag_data['target'] = None
                set_banner(cur_hero)

                canvas.drag_data['target_path'] = "NONE"

            # IF
            # current tile isn't new tile
            # and new tile is within posible moves

            # build from existing path
            if prev_tile_int != cur_tile_int and cur_tile_int in canvas.drag_data['moves']:

                new_tile_cost = get_tile_cost(chosen_map.tiles[cur_tile_int], cur_hero)
                canvas.drag_data['cost'] += new_tile_cost

                spaces_allowed = allowed_movement(cur_hero)
                is_allowed = canvas.drag_data['cost'] <= spaces_allowed

                # west
                if prev_tile_int - 1 == cur_tile_int and is_allowed:
                    canvas.drag_data['cur_path'] += 'W'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("EW"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[prev_tile_int], cur_hero)

                # east
                elif prev_tile_int + 1 == cur_tile_int and is_allowed:
                    canvas.drag_data['cur_path'] += 'E'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("WE"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[prev_tile_int], cur_hero)

                # south
                elif prev_tile_int - 6 == cur_tile_int and is_allowed:
                    canvas.drag_data['cur_path'] += 'S'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("NS"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[prev_tile_int], cur_hero)

                # north
                elif prev_tile_int + 6 == cur_tile_int and is_allowed:
                    canvas.drag_data['cur_path'] += 'N'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("SN"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[prev_tile_int], cur_hero)

                elif event.x > 0 and event.x < 539:
                    canvas.drag_data['cur_path'] = canvas.drag_data['paths'][canvas.drag_data['moves'].index(cur_tile_int)]

                    x_start_comp = canvas.drag_data['start_x_comp']
                    y_start_comp = canvas.drag_data['start_y_comp']
                    recalc_tile = int(x_start_comp + 6 * y_start_comp)

                    new_cost = 0
                    for c in canvas.drag_data['cur_path']:
                        if c == 'N': recalc_tile += 6
                        if c == 'S': recalc_tile -= 6
                        if c == 'E': recalc_tile += 1
                        if c == 'W': recalc_tile -= 1
                        new_cost += get_tile_cost(chosen_map.tiles[recalc_tile], cur_hero)

                    canvas.drag_data['cost'] = new_cost

                canvas.drag_data['cur_tile'] = cur_tile_int


            # get the x/y components of the starting tile, start drawing path from here
            x_arrow_comp = canvas.drag_data['start_x_comp']
            y_arrow_comp = canvas.drag_data['start_y_comp']
            x_arrow_pivot = x_arrow_comp * 90
            y_arrow_pivot = (7 - y_arrow_comp) * 90 + 90

            for arrow in canvas.drag_data['arrow_path']:
                canvas.delete(arrow)
            canvas.drag_data['arrow_path'] = []

            traced_path = canvas.drag_data['cur_path']
            if canvas.drag_data['target_path'] != "NONE":
                traced_path = canvas.drag_data['target_path']

            # draw the arrow path
            if cur_tile_int in canvas.drag_data['moves'] or canvas.drag_data['target_path'] != "NONE":
                if len(traced_path) == 0 or event.x > 539 or event.x < 0:
                    star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=arrow_photos[MOVE_STAR])
                    canvas.drag_data['arrow_path'].append(star)
                    canvas.tag_lower(star, canvas.drag_data['item'])
                elif traced_path == "WARP":
                    star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=arrow_photos[MOVE_STAR])
                    canvas.drag_data['arrow_path'].append(star)
                    canvas.tag_lower(star, canvas.drag_data['item'])

                    final_tile_star_pos = cur_tile_int

                    if chosen_map.tiles[cur_tile_int].hero_on in canvas.drag_data['targets_and_tiles']:
                        final_tile_star_pos = canvas.drag_data['target_dest']

                    star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor='center', image=arrow_photos[MOVE_STAR])
                    move_to_tile(canvas, star, final_tile_star_pos)
                    canvas.move(star, -9, 0)
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



            # draw move_star at start only if out of bounds
            elif cur_tile_int not in canvas.drag_data['moves']:
                if len(canvas.drag_data['arrow_path']) != 1:
                    for arrow in canvas.drag_data['arrow_path']:
                        canvas.delete(arrow)
                    canvas.drag_data['arrow_path'] = []

                star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=arrow_photos[MOVE_STAR])
                canvas.drag_data['arrow_path'].append(star)
                canvas.tag_lower(star, canvas.drag_data['item'])

                for x in aoe_special_icons_active:
                    canvas.delete(x)
                aoe_special_icons_active.clear()

            cur_hero = units_all[canvas.drag_data['side']][canvas.drag_data['index']]

            for x in canvas.drag_data['targets_and_tiles']:
                if prev_tile_int in canvas.drag_data['targets_and_tiles'][x]:
                    canvas.drag_data['targets_most_recent_tile'][x] = prev_tile_int

            # if
            # there is a hero on new tile,
            # current target isn't new tile hero,
            # and new tile hero isn't dragged unit,

            if (event.y > 91 and event.x > 0 and event.x < 539 and chosen_map.tiles[cur_tile_int].hero_on is not None and
                    chosen_map.tiles[cur_tile_int].hero_on != cur_hero and chosen_map.tiles[cur_tile_int].hero_on != canvas.drag_data['target']):

                # set new target
                canvas.drag_data['target'] = chosen_map.tiles[cur_tile_int].hero_on

                # if new tile in attacking range
                if cur_tile_int in canvas.drag_data['attack_range'] and cur_hero.side != chosen_map.tiles[cur_tile_int].hero_on.side:
                    cur_hero.attacking_tile = chosen_map.tiles[target_tile]

                    # If moving onto a foe with an AOE special ready
                    for x in aoe_special_icons_active:
                        canvas.delete(x)
                    aoe_special_icons_active.clear()

                    if cur_hero.special is not None and cur_hero.special.type == "AOE" and cur_hero.specialCount == 0:
                        formation = cur_hero.special.effects["aoe_area"]
                        aoe_special_targets = aoe_tiles(cur_tile_int, formation)

                        for num in aoe_special_targets:
                            cur_special_image = canvas.create_image((0, 90), image=aoe_special_icon_photo, anchor="center")
                            move_to_tile(canvas, cur_special_image, num)
                            aoe_special_icons_active.append(cur_special_image)

                            player_status_img.append(cur_special_image)
                            canvas.tag_lower(item_index, cur_special_image)

                    # when warping, clash skills use euclidean distance
                    # when not warping, clash skills use manhattan distance
                    distance = len(canvas.drag_data['target_path'])
                    #if canvas.drag_data['target_path'] == "WARP":
                    #    distance =

                    set_attack_forecast(cur_hero, chosen_map.tiles[cur_tile_int].hero_on, distance)

                elif cur_tile_int in canvas.drag_data['assist_range'] and cur_hero.side == chosen_map.tiles[cur_tile_int].hero_on.side\
                        and chosen_map.tiles[cur_tile_int].hero_on in canvas.drag_data['targets_and_tiles']:

                    set_assist_forecast(cur_hero, chosen_map.tiles[cur_tile_int].hero_on)

                    for x in aoe_special_icons_active:
                        canvas.delete(x)
                    aoe_special_icons_active.clear()

                # new tile isn't in attacking range
                else:
                    cur_hero.attacking_tile = None
                    set_banner(chosen_map.tiles[cur_tile_int].hero_on)

                    for x in aoe_special_icons_active:
                        canvas.delete(x)
                    aoe_special_icons_active.clear()

            elif cur_tile_Obj.hero_on is None:
                for x in aoe_special_icons_active:
                    canvas.delete(x)
                aoe_special_icons_active.clear()

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

            x_start_comp = canvas.drag_data['start_x_comp']
            y_start_comp = canvas.drag_data['start_y_comp']
            recalc_tile = int(x_start_comp + 6 * y_start_comp)


            item_index = canvas.drag_data['index']
            S = canvas.drag_data['side']

            player = units_all[S][item_index]

            player_sprite = canvas.drag_data['item']
            grayscale_sprite = grayscale_IDs[S][item_index]
            weapon_icon_sprite = weapon_IDs[S][item_index]
            hp_label = hp_labels[S][item_index]
            sp_label = special_labels[S][item_index]
            hp_bar_fg = hp_bar_fgs[S][item_index]
            hp_bar_bg = hp_bar_bgs[S][item_index]

            # Set sprite to new position
            if event.x < 539 and event.x > 0 and event.y < 810 and event.y > 90 and new_tile in canvas.drag_data['moves']:
                move_to_tile(canvas, canvas.drag_data['item'], new_tile)
                move_to_tile(canvas, grayscale_sprite, new_tile)
                move_to_tile_wp(canvas, weapon_icon_sprite, new_tile)
                move_to_tile_hp(canvas, hp_label, new_tile)
                move_to_tile_sp(canvas, sp_label, new_tile)
                move_to_tile_fg_bar(canvas, hp_bar_fg, new_tile)
                move_to_tile_fg_bar(canvas, hp_bar_bg, new_tile)

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
                move_to_tile_wp(canvas, weapon_icon_sprite, recalc_tile)
                move_to_tile_hp(canvas, hp_label, recalc_tile)
                move_to_tile_sp(canvas, sp_label, recalc_tile)
                move_to_tile_fg_bar(canvas, hp_bar_fg, recalc_tile)
                move_to_tile_fg_bar(canvas, hp_bar_bg, recalc_tile)

            for blue_tile_id in canvas.drag_data['tile_id_arr']:
                canvas.delete(blue_tile_id)
            canvas.drag_data['tile_id_arr'].clear()

            for arrow in canvas.drag_data['arrow_path']:
                canvas.delete(arrow)

            for x in aoe_special_icons_active:
                canvas.delete(x)
            aoe_special_icons_active.clear()

            # If off-board move, nothing else to do
            if event.x < 0 or event.x > 540 or event.y < 90 or event.y > 810:
                return

            # Ok it might just be a failsafe for these lines
            player_original = chosen_map.tiles[new_tile].hero_on

            action_performed = False
            galeforce_triggered = False

            # ATTAAAAAAAAAAAAAAAAAAAAAAACK!!!!!!!!!!!!!!!!!!
            if event.x < 539 and event.x > 0 and event.y < 810 and event.y > 90 and canvas.drag_data['target_path'] != "NONE" and \
                    chosen_map.tiles[new_tile].hero_on.side != chosen_map.tiles[mouse_new_tile].hero_on.side:
                animation = True
                action_performed = True

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


                if canvas.drag_data['side'] == 0:
                    enemy_index = enemy_units_all.index(enemy)

                    enemy_sprite = enemy_sprite_IDs[enemy_index]
                    enemy_weapon_icon = enemy_weapon_icons[enemy_index]
                    enemy_hp_label = enemy_hp_count_labels[enemy_index]
                    enemy_sp_label = enemy_special_count_labels[enemy_index]

                    this_enemy_hp_bar_fg = enemy_hp_bar_fg[enemy_index]
                    this_enemy_hp_bar_bg = enemy_hp_bar_bg[enemy_index]

                if canvas.drag_data['side'] == 1:
                    enemy_index = player_units_all.index(enemy)

                    enemy_sprite = player_sprite_IDs[enemy_index]
                    enemy_weapon_icon = player_weapon_icons[enemy_index]
                    enemy_hp_label = player_hp_count_labels[enemy_index]
                    enemy_sp_label = player_special_count_labels[enemy_index]

                    this_enemy_hp_bar_fg = player_hp_bar_fg[enemy_index]
                    this_enemy_hp_bar_bg = player_hp_bar_bg[enemy_index]

                def hide_enemy(is_alive):
                    canvas.itemconfig(enemy_sprite, state='hidden')
                    canvas.itemconfig(grayscale_sprite, state='normal')

                    if not is_alive:
                        canvas.itemconfig(enemy_weapon_icon, state='hidden')
                        move_to_tile(canvas, enemy_sprite, 100)

                        canvas.itemconfig(enemy_hp_label, state='hidden')
                        canvas.itemconfig(enemy_sp_label, state='hidden')
                        canvas.itemconfig(this_enemy_hp_bar_bg, state='hidden')
                        canvas.itemconfig(this_enemy_hp_bar_fg, state='hidden')

                def hide_player(is_alive):
                    canvas.itemconfig(player_sprite, state='hidden')
                    canvas.itemconfig(grayscale_sprite, state='normal')

                    if not is_alive:
                        canvas.itemconfig(weapon_icon_sprite, state='hidden')
                        move_to_tile(canvas, player_sprite, 100)
                        move_to_tile(canvas, grayscale_sprite, 100)

                        canvas.itemconfig(hp_label, state='hidden')
                        canvas.itemconfig(sp_label, state='hidden')
                        canvas.itemconfig(hp_bar_bg, state='hidden')
                        canvas.itemconfig(hp_bar_fg, state='hidden')

                def animation_done():
                    global animation
                    animation = False




                # Perform AOE attack
                aoe_present = 0
                if player.special is not None and player.special.type == "AOE" and player.specialCount == 0:
                    aoe_present = 500

                    player.specialCount = player.specialMax
                    canvas.after(300, set_text_val, sp_label, player.specialMax)

                    formation = player.special.effects["aoe_area"]
                    aoe_special_targets = aoe_tiles(enemy_tile, formation)

                    for tile in aoe_special_targets:
                        aoe_target = chosen_map.tiles[tile].hero_on
                        if aoe_target is not None and aoe_target.side != player.side:
                            aoe_damage: int = get_AOE_damage(player, aoe_target)

                            aoe_target.HPcur = max(1, aoe_target.HPcur - aoe_damage)
                            canvas.after(300, set_hp_visual, aoe_target, aoe_target.HPcur)
                            canvas.after(300, animate_damage_popup, canvas, aoe_damage, tile)


                # get warp distance from manhattan distance
                distance = len(canvas.drag_data['target_path'])

                # Simulate combat
                combat_result = simulate_combat(player, enemy, True, turn_info[0], distance, [])
                attacks = combat_result[7]

                player.unitCombatInitiates += 1
                enemy.unitCombatInitiates += 1

                # Visualization of the blows trading
                i = 0

                while i < len(attacks):
                    move_time = i * 500 + 200 + aoe_present
                    impact_time = i * 500 + 300 + aoe_present

                    if attacks[i].attackOwner == 0:

                        # Move player sprite
                        canvas.after(move_time, animate_sprite_atk, canvas, player_sprite, player_atk_dir_hori, player_atk_dir_vert, attacks[i].damage, enemy_tile)

                        # Heal player, get to enemy side soon
                        if attacks[i].healed > 0:
                            canvas.after(impact_time, animate_heal_popup, canvas, attacks[i].healed, player_tile)

                        # Damage enemy
                        enemy.HPcur = max(0, enemy.HPcur - attacks[i].damage)
                        canvas.after(impact_time, set_text_val, enemy_hp_label, enemy.HPcur)

                        # Update each player's health visually
                        hp_percentage = enemy.HPcur/enemy.visible_stats[HP]
                        canvas.after(impact_time, set_hp_bar_length, this_enemy_hp_bar_fg, hp_percentage)

                        player.HPcur = min(player.visible_stats[HP], player.HPcur + attacks[i].healed)
                        canvas.after(impact_time, set_text_val, hp_label, player.HPcur)

                        hp_percentage = player.HPcur / player.visible_stats[HP]
                        canvas.after(impact_time, set_hp_bar_length, hp_bar_fg, hp_percentage)

                    if attacks[i].attackOwner == 1:
                        canvas.after(move_time, animate_sprite_atk, canvas, enemy_sprite, player_atk_dir_hori * -1, player_atk_dir_vert * -1, attacks[i].damage, player_tile)

                        player.HPcur = max(0, player.HPcur - attacks[i].damage)
                        canvas.after(impact_time, set_text_val, hp_label, player.HPcur)

                        hp_percentage = player.HPcur / player.visible_stats[HP]
                        canvas.after(impact_time, set_hp_bar_length, hp_bar_fg, hp_percentage)

                        enemy.HPcur = min(enemy.visible_stats[HP], enemy.HPcur + attacks[i].healed)
                        canvas.after(impact_time, set_text_val, enemy_hp_label, enemy.HPcur)

                        hp_percentage = enemy.HPcur / enemy.visible_stats[HP]
                        canvas.after(impact_time, set_hp_bar_length, this_enemy_hp_bar_fg, hp_percentage)

                    if player.specialCount != -1:
                        player.specialCount = attacks[i].spCharges[0]
                        canvas.after(impact_time, set_text_val, sp_label, player.specialCount)
                    if enemy.specialCount != -1:
                        enemy.specialCount = attacks[i].spCharges[1]
                        canvas.after(impact_time, set_text_val, enemy_sp_label, enemy.specialCount)


                    if player.HPcur == 0 or enemy.HPcur == 0: break
                    i += 1

                finish_time = 500 * (i + 1) + 200 + aoe_present

                atk_effects = combat_result[12]
                def_effects = combat_result[13]

                player.statusNeg = []
                player.debuffs = [0, 0, 0, 0, 0]

                damage_taken, heals_given = end_of_combat(atk_effects, def_effects, player, enemy)

                # Post combat special charges go here

                # Post combat damage/healing across the field
                for x in player_units + enemy_units:
                    hp_change = 0
                    if x in damage_taken:
                        hp_change -= damage_taken[x]
                    if x in heals_given:
                        hp_change += heals_given[x]

                    if hp_change != 0:
                        if hp_change > 0:
                            canvas.after(finish_time, animate_heal_popup, canvas, hp_change, x.tile.tileNum)
                        if hp_change < 0:
                            canvas.after(finish_time, animate_damage_popup, canvas, abs(hp_change), x.tile.tileNum)

                        x_side = x.side
                        x_index = units_all[x_side].index(x)
                        x_hp_label = hp_labels[x_side][x_index]
                        x_hp_bar = hp_bar_fgs[x_side][x_index]

                        hp_percentage = x.HPcur / x.visible_stats[HP]

                        canvas.after(finish_time, set_text_val, x_hp_label, x.HPcur)
                        canvas.after(finish_time, set_hp_bar_length, x_hp_bar, hp_percentage)

                # movement-based skills after combat
                player_tile_number = player.tile.tileNum
                enemy_tile_number = enemy.tile.tileNum

                player_move_pos = -1
                enemy_move_pos = -1

                if "knock_back" in player.getSkills():
                    player_move_pos = player_tile_number
                    enemy_move_pos = final_reposition_tile(enemy_tile_number, player_tile_number)

                    if not(chosen_map.tiles[enemy_move_pos].hero_on is None and can_be_on_terrain(chosen_map.tiles[enemy_move_pos].terrain, enemy.move)):
                        enemy_move_pos = -1

                elif "drag_back" in player.getSkills():
                    player_move_pos = final_reposition_tile(player_tile_number, enemy_tile_number)
                    enemy_move_pos = player_tile_number

                elif "lunge" in player.getSkills():
                    player_move_pos = enemy_tile_number
                    enemy_move_pos = player_tile_number

                elif "hit_and_run" in player.getSkills():
                    player_move_pos = final_reposition_tile(player_tile_number, enemy_tile_number)
                    enemy_move_pos = enemy_tile_number

                # movement conditions for post combat moves
                if player_move_pos != -1 and enemy_move_pos != -1 and player.HPcur != 0:
                    if chosen_map.tiles[player_move_pos].hero_on != None and (chosen_map.tiles[player_move_pos].hero_on != player and chosen_map.tiles[player_move_pos].hero_on != enemy):
                        player_move_pos = -1
                    elif chosen_map.tiles[enemy_move_pos].hero_on != None and (chosen_map.tiles[enemy_move_pos].hero_on != player and chosen_map.tiles[enemy_move_pos].hero_on != enemy):
                        enemy_move_pos = -1
                    elif not can_be_on_terrain(chosen_map.tiles[player_move_pos].terrain, player.move):
                        player_move_pos = -1
                    elif not can_be_on_terrain(chosen_map.tiles[enemy_move_pos].terrain, player.move):
                        enemy_move_pos = -1

                if player_move_pos != -1 and enemy_move_pos != -1 and player.HPcur != 0:

                    player.tile.hero_on = None
                    enemy.tile.hero_on = None

                    player.tile = chosen_map.tiles[player_move_pos]
                    enemy.tile = chosen_map.tiles[enemy_move_pos]

                    player.tile.hero_on = player
                    enemy.tile.hero_on = enemy

                    canvas.after(finish_time, move_to_tile, canvas, player_sprite, player_move_pos)
                    canvas.after(finish_time, move_to_tile, canvas, grayscale_sprite, player_move_pos)
                    canvas.after(finish_time, move_to_tile_wp, canvas, weapon_icon_sprite, player_move_pos)
                    canvas.after(finish_time, move_to_tile_hp, canvas, hp_label, player_move_pos)
                    canvas.after(finish_time, move_to_tile_sp, canvas, sp_label, player_move_pos)
                    canvas.after(finish_time, move_to_tile_fg_bar, canvas, hp_bar_fg, player_move_pos)
                    canvas.after(finish_time, move_to_tile_fg_bar, canvas, hp_bar_bg, player_move_pos)

                    enemy_grayscale = grayscale_IDs[enemy.side][enemy_index]

                    canvas.after(finish_time, move_to_tile, canvas, enemy_sprite, enemy_move_pos)
                    canvas.after(finish_time, move_to_tile, canvas, enemy_grayscale, enemy_move_pos)
                    canvas.after(finish_time, move_to_tile_wp, canvas, enemy_weapon_icon, enemy_move_pos)
                    canvas.after(finish_time, move_to_tile_hp, canvas, enemy_hp_label, enemy_move_pos)
                    canvas.after(finish_time, move_to_tile_sp, canvas, enemy_sp_label, enemy_move_pos)
                    canvas.after(finish_time, move_to_tile_fg_bar, canvas, this_enemy_hp_bar_fg, enemy_move_pos)
                    canvas.after(finish_time, move_to_tile_fg_bar, canvas, this_enemy_hp_bar_bg, enemy_move_pos)

                # galeforce goes here

                if player.special is not None and "galeforce" in player.special.effects and player.specialCount == 0 and player.special_galeforce_triggered == False:
                    player.special_galeforce_triggered = True
                    galeforce_triggered = True

                    player.specialCount = player.specialMax

                # canto goes here

                if player.HPcur == 0:
                    canvas.after(finish_time, hide_player, False)

                    # remove from list of units
                    if chosen_map.tiles[new_tile].hero_on.side == 0: player_units.remove(chosen_map.tiles[new_tile].hero_on)
                    if chosen_map.tiles[new_tile].hero_on.side == 1: enemy_units.remove(chosen_map.tiles[new_tile].hero_on)

                    # take unit off map
                    player.tile.hero_on = None

                    # end simulation if they were last unit alive
                    if player.side == 0 and not player_units:
                        canvas.after(finish_time + 700, window.destroy)

                    if player.side == 1 and not enemy_units:
                        canvas.after(finish_time + 700, window.destroy)

                    canvas.after(finish_time, clear_banner)
                else:
                    canvas.after(finish_time, set_banner, player)

                if enemy.HPcur == 0:
                    canvas.after(finish_time, hide_enemy, False)

                    # remove from list of units
                    if enemy.side == 0: player_units.remove(enemy)
                    if enemy.side == 1: enemy_units.remove(enemy)

                    # take unit off map
                    enemy.tile.hero_on = None

                    # end simulation if all enemy units are defeated
                    if enemy.side == 0 and not player_units:
                        canvas.after(finish_time + 700, window.destroy)

                    if enemy.side == 1 and not enemy_units:
                        canvas.after(finish_time + 700, window.destroy)


                canvas.after(finish_time, animation_done)

                if not galeforce_triggered:
                    canvas.after(finish_time, hide_player, True)
                else:
                    canvas.after(finish_time, set_text_val, sp_label, player.specialCount)

            # SUPPOOOOOOOOOOOOOOOOOOOORT!!!!!!!!!!!!!!!!!!!!
            elif event.x < 539 and event.x > 0 and event.y < 810 and event.y > 90 and canvas.drag_data['target_path'] != "NONE" and \
                    chosen_map.tiles[new_tile].hero_on.side == chosen_map.tiles[mouse_new_tile].hero_on.side:
                action_performed = True

                player = chosen_map.tiles[new_tile].hero_on
                ally = chosen_map.tiles[mouse_new_tile].hero_on

                ally_index = units_all[S].index(ally)

                ally_sprite = sprite_IDs[S][ally_index]
                ally_grayscale = grayscale_IDs[S][ally_index]
                ally_weapon_icon = weapon_IDs[S][ally_index]
                ally_hp_label = hp_labels[S][ally_index]
                ally_sp_label = special_labels[S][ally_index]
                ally_hp_bar_fg = hp_bar_fgs[S][ally_index]
                ally_hp_bar_bg = hp_bar_bgs[S][ally_index]

                if "repo" in player.assist.effects:

                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    final_pos = final_reposition_tile(unit_tile_num, ally_tile_num)

                    # Move ally to other tile
                    ally.tile.hero_on = None
                    ally.tile = chosen_map.tiles[final_pos]
                    chosen_map.tiles[final_pos].hero_on = ally

                    move_to_tile(canvas, ally_sprite, final_pos)
                    move_to_tile(canvas, ally_grayscale, final_pos)
                    move_to_tile_wp(canvas, ally_weapon_icon, final_pos)
                    move_to_tile_hp(canvas, ally_hp_label, final_pos)
                    move_to_tile_sp(canvas, ally_sp_label, final_pos)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_fg, final_pos)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_bg, final_pos)


                elif "draw" in player.assist.effects:
                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    final_pos_player = final_reposition_tile(unit_tile_num, ally_tile_num)
                    final_pos_ally = unit_tile_num

                    print(final_pos_player, final_pos_ally)

                    player.tile = chosen_map.tiles[final_pos_player]
                    chosen_map.tiles[final_pos_player].hero_on = player

                    ally.tile.hero_on = None
                    ally.tile = chosen_map.tiles[final_pos_ally]
                    chosen_map.tiles[final_pos_ally].hero_on = ally

                    #final_pos_player = player.tile.tileNum
                    #final_pos_ally = ally.tile.tileNum

                    move_to_tile(canvas, player_sprite, final_pos_player)
                    move_to_tile(canvas, ally_sprite, final_pos_ally)

                    move_to_tile(canvas, grayscale_sprite, final_pos_player)
                    move_to_tile(canvas, ally_grayscale, final_pos_ally)

                    move_to_tile_wp(canvas, weapon_icon_sprite, final_pos_player)
                    move_to_tile_wp(canvas, ally_weapon_icon, final_pos_ally)

                    move_to_tile_hp(canvas, hp_label, final_pos_player)
                    move_to_tile_sp(canvas, sp_label, final_pos_player)
                    move_to_tile_fg_bar(canvas, hp_bar_fg, final_pos_player)
                    move_to_tile_fg_bar(canvas, hp_bar_bg, final_pos_player)

                    move_to_tile_hp(canvas, ally_hp_label, final_pos_ally)
                    move_to_tile_sp(canvas, ally_sp_label, final_pos_ally)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_fg, final_pos_ally)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_bg, final_pos_ally)

                elif "swap" in player.assist.effects:

                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    ally.tile = chosen_map.tiles[unit_tile_num]
                    chosen_map.tiles[unit_tile_num].hero_on = ally

                    player.tile = chosen_map.tiles[ally_tile_num]
                    chosen_map.tiles[ally_tile_num].hero_on = player

                    final_pos_player = player.tile.tileNum
                    final_pos_ally = ally.tile.tileNum

                    move_to_tile(canvas, player_sprite, final_pos_player)
                    move_to_tile(canvas, ally_sprite, final_pos_ally)

                    move_to_tile(canvas, grayscale_sprite, final_pos_player)
                    move_to_tile(canvas, ally_grayscale, final_pos_ally)

                    move_to_tile_wp(canvas, weapon_icon_sprite, final_pos_player)
                    move_to_tile_wp(canvas, ally_weapon_icon, final_pos_ally)

                    move_to_tile_hp(canvas, hp_label, final_pos_player)
                    move_to_tile_sp(canvas, sp_label, final_pos_player)
                    move_to_tile_fg_bar(canvas, hp_bar_fg, final_pos_player)
                    move_to_tile_fg_bar(canvas, hp_bar_bg, final_pos_player)

                    move_to_tile_hp(canvas, ally_hp_label, final_pos_ally)
                    move_to_tile_sp(canvas, ally_sp_label, final_pos_ally)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_fg, final_pos_ally)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_bg, final_pos_ally)


                    print("SWAP")
                elif "pivot" in player.assist.effects:
                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    final_pos = final_reposition_tile(ally_tile_num, unit_tile_num)

                    # Move ally to other tile
                    player.tile.hero_on = None
                    player.tile = chosen_map.tiles[final_pos]
                    chosen_map.tiles[final_pos].hero_on = player

                    move_to_tile(canvas, player_sprite, final_pos)
                    move_to_tile(canvas, grayscale_sprite, final_pos)
                    move_to_tile_wp(canvas, weapon_icon_sprite, final_pos)
                    move_to_tile_hp(canvas, hp_label, final_pos)
                    move_to_tile_sp(canvas, sp_label, final_pos)
                    move_to_tile_fg_bar(canvas, hp_bar_fg, final_pos)
                    move_to_tile_fg_bar(canvas, hp_bar_bg, final_pos)

                elif "smite" in player.assist.effects:
                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    skip_over = final_reposition_tile(ally_tile_num, unit_tile_num)
                    final_dest = final_reposition_tile(skip_over, ally_tile_num)

                    valid_shove = False
                    valid_smite = False

                    if skip_over != -1:
                        unit_on_dest = chosen_map.tiles[skip_over].hero_on is not None and chosen_map.tiles[skip_over].hero_on != player
                        can_traverse_dest = can_be_on_terrain(chosen_map.tiles[skip_over].terrain, ally.move)

                        valid_shove = not unit_on_dest and can_traverse_dest

                    if final_dest != -1:
                        unit_on_dest = chosen_map.tiles[final_dest].hero_on is not None and chosen_map.tiles[final_dest].hero_on != player
                        can_traverse_dest = can_be_on_terrain(chosen_map.tiles[final_dest].terrain, ally.move)

                        foe_on_skip = chosen_map.tiles[skip_over].hero_on is not None and chosen_map.tiles[skip_over].hero_on.side != player.side
                        can_skip = chosen_map.tiles[skip_over].terrain != 4 and not foe_on_skip

                        valid_smite = not unit_on_dest and can_traverse_dest and can_skip

                    final_pos = -1
                    if valid_shove and not valid_smite:
                        final_pos = skip_over
                    if valid_smite:
                        final_pos = final_dest

                    ally.tile.hero_on = None
                    ally.tile = chosen_map.tiles[final_pos]
                    chosen_map.tiles[final_pos].hero_on = ally

                    move_to_tile(canvas, ally_sprite, final_pos)
                    move_to_tile(canvas, ally_grayscale, final_pos)
                    move_to_tile_wp(canvas, ally_weapon_icon, final_pos)
                    move_to_tile_hp(canvas, ally_hp_label, final_pos)
                    move_to_tile_sp(canvas, ally_sp_label, final_pos)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_fg, final_pos)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_bg, final_pos)

                elif "shove" in player.assist.effects:
                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    final_pos = final_reposition_tile(ally_tile_num, unit_tile_num)

                    ally.tile.hero_on = None
                    ally.tile = chosen_map.tiles[final_pos]
                    chosen_map.tiles[final_pos].hero_on = ally

                    move_to_tile(canvas, ally_sprite, final_pos)
                    move_to_tile(canvas, ally_grayscale, final_pos)
                    move_to_tile_wp(canvas, ally_weapon_icon, final_pos)
                    move_to_tile_hp(canvas, ally_hp_label, final_pos)
                    move_to_tile_sp(canvas, ally_sp_label, final_pos)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_fg, final_pos)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_bg, final_pos)

                # Staff Healing
                elif "heal" in player.assist.effects:
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
                        hp_healed_self = dmg_taken//2

                    # Martyr+
                    if player.assist.effects["heal"] == -49:
                        dmg_taken = player.visible_stats[HP] - player.HPcur
                        hp_healed_ally = max(dmg_taken + self_atk_stat // 2, 7)
                        hp_healed_self = dmg_taken // 2

                    # Recover+
                    if player.assist.effects["heal"] == -10:
                        hp_healed_ally = max(self_atk_stat // 2 + 10, 15)

                    staff_special_triggered = False

                    if player.specialCount == 0 and player.special.type == "Healing":
                        if "boost_heal" in player.special.effects:
                            hp_healed_ally += player.special.effects["boost_heal"]

                        allies_arr = units_all[S]
                        for x in allies_arr:
                            if x != player and x != ally and "heal_allies" in player.special.effects:

                                x_index = allies_arr.index(x)
                                x_hp_label = hp_labels[S][x_index]
                                x_hp_bar = hp_bar_fgs[S][x_index]

                                x.HPcur = min(x.visible_stats[HP], x.HPcur + 10)

                                hp_percentage = x.HPcur / x.visible_stats[HP]

                                set_text_val(x_hp_label, x.HPcur)
                                set_hp_bar_length(x_hp_bar, hp_percentage)

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

                    if "live_to_serve" in player.bskill.effects:
                        percentage = 0.25 + 0.25 * player.bskill.effects["live_to_serve"]
                        hp_healed_self += trunc(hp_healed_ally * percentage)

                    ally.HPcur = min(ally.visible_stats[HP], ally.HPcur + hp_healed_ally)
                    player.HPcur = min(player.visible_stats[HP], player.HPcur + hp_healed_self)

                    animate_heal_popup(canvas, hp_healed_ally, ally.tile.tileNum)

                    # Get/Update HP assets
                    ally_index = units_all[S].index(ally)
                    ally_hp_label = hp_labels[S][ally_index]
                    ally_hp_bar = hp_bar_fgs[S][ally_index]

                    hp_percentage = ally.HPcur / ally.visible_stats[HP]
                    set_text_val(ally_hp_label, ally.HPcur)
                    set_hp_bar_length(ally_hp_bar, hp_percentage)

                    # Display self heal (only if amount healed > 0)
                    if hp_healed_self > 0:
                        animate_heal_popup(canvas, hp_healed_self, player.tile.tileNum)

                        # Update HP assets
                        hp_percentage = player.HPcur / player.visible_stats[HP]
                        set_text_val(hp_label, player.HPcur)
                        set_hp_bar_length(hp_bar_fg, hp_percentage)

                    # Charge special for Staff assist use
                    if staff_special_triggered:
                        player.specialCount = player.specialMax
                        set_text_val(sp_label, player.specialCount)
                    elif player.specialCount != -1:
                        player.specialCount = max(player.specialCount - 1, 0)
                        set_text_val(sp_label, player.specialCount)


                elif "refresh" in player.assist.effects:
                    # Grant ally another action
                    units_to_move.append(ally)

                    ally_index = units_all[S].index(ally)
                    ally_sprite = sprite_IDs[S][ally_index]
                    ally_gs_sprite = grayscale_IDs[S][ally_index]

                    canvas.itemconfig(ally_sprite, state='normal')
                    canvas.itemconfig(ally_gs_sprite, state='hidden')

                if "rallyAtk" in player.assist.effects:
                    ally.inflictStat(ATK, player.assist.effects["rallyAtk"])
                if "rallySpd" in player.assist.effects:
                    ally.inflictStat(SPD, player.assist.effects["rallySpd"])
                if "rallyDef" in player.assist.effects:
                    ally.inflictStat(DEF, player.assist.effects["rallyDef"])
                if "rallyRes" in player.assist.effects:
                    ally.inflictStat(RES, player.assist.effects["rallyRes"])

                if "rec_aid" in player.assist.effects:
                    switch_hp = abs(player.HPcur - ally.HPcur)

                    ally_HP_result = min(ally.visible_stats[HP], player.HPcur)
                    player_HP_result = min(player.visible_stats[HP], ally.HPcur)

                    if player_HP_result > player.HPcur:
                        animate_heal_popup(canvas, switch_hp, player.tile.tileNum)
                        animate_damage_popup(canvas, switch_hp, ally.tile.tileNum)
                    else:
                        animate_heal_popup(canvas, switch_hp, ally.tile.tileNum)
                        animate_damage_popup(canvas, switch_hp, player.tile.tileNum)

                    player.HPcur = player_HP_result
                    ally.HPcur = ally_HP_result
                    set_hp_visual(player, player.HPcur)
                    set_hp_visual(ally, ally.HPcur)

                if "ardent_sac" in player.assist.effects:
                    ally.HPcur = min(ally.visible_stats[HP], ally.HPcur + 10)
                    player.HPcur = max(1, player.HPcur - 10)

                    animate_heal_popup(canvas, 10, ally.tile.tileNum)
                    animate_damage_popup(canvas, 10, player.tile.tileNum)

                    set_hp_visual(player, player.HPcur)
                    set_hp_visual(ally, ally.HPcur)

                set_banner(player)

                player.statusNeg = []
                player.debuffs = [0, 0, 0, 0, 0]

            # DO NOTHIIIIIIIIIIIIIIING!!!!!
            if not action_performed and successful_move:
                player.statusNeg = []
                player.debuffs = [0, 0, 0, 0, 0]
                set_banner(player)

            # remove player unit from units who can act
            cur_hero = player_original
            units_all[S][item_index].attacking_tile = None

            if successful_move and cur_hero in units_to_move and not galeforce_triggered:
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

        if x > 380 and y > 820 and x < 450 and y < 900:
            next_phase()

            return

        if x < 0 or x > 540 or y <= 90 or y > 810:
            print("homer simpson")
            return

        x_comp = event.x // 90
        y_comp = ((720 - event.y) // 90) + 1
        selected_tile = x_comp + 6 * y_comp
        cur_hero = chosen_map.tiles[selected_tile].hero_on

        if cur_hero is not None:
            if cur_hero.side == 0 and turn_info[1] == PLAYER:
                item_index = player_units_all.index(cur_hero)
                if cur_hero in units_to_move:
                    units_to_move.remove(cur_hero)

                    cur_hero.statusNeg = []
                    cur_hero.debuffs = [0, 0, 0, 0, 0]
                    set_banner(cur_hero)

                    canvas.itemconfig(grayscale_player_sprite_IDs[item_index], state='normal')
                    canvas.itemconfig(player_sprite_IDs[item_index], state='hidden')
                    if not units_to_move:
                        next_phase()

            if cur_hero.side == 1 and turn_info[1] == ENEMY:
                item_index = enemy_units_all.index(cur_hero)
                if cur_hero in units_to_move:
                    units_to_move.remove(cur_hero)

                    cur_hero.statusNeg = []
                    cur_hero.debuffs = [0, 0, 0, 0, 0]
                    set_banner(cur_hero)

                    canvas.itemconfig(grayscale_enemy_sprite_IDs[item_index], state='normal')
                    canvas.itemconfig(enemy_sprite_IDs[item_index], state='hidden')
                    if not units_to_move:
                        next_phase()

    def set_text_val(label, value):
        canvas.itemconfig(label, text=value)

    def set_hp_bar_length(rect, percent):
        new_length = int(60 * percent)
        if new_length == 0:
            canvas.itemconfig(rect, state='hidden')
            return
        coords = canvas.coords(rect)

        coords[2] = coords[0] + new_length

        canvas.coords(rect, *coords)

    def set_hp_visual(unit, cur_HP):
        S = unit.side
        unit_index = units_all[S].index(unit)
        unit_hp_label = hp_labels[S][unit_index]
        unit_hp_bar = hp_bar_fgs[S][unit_index]

        hp_percentage = cur_HP / unit.visible_stats[HP]

        set_text_val(unit_hp_label, cur_HP)
        set_hp_bar_length(unit_hp_bar, hp_percentage)



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
    #map_image = Image.open(__location__ + "\\Maps\\Story Maps\\Book 1\\Preface\\" + "story0_0_1" + ".png")
    map_image = Image.open(__location__ + "\\Maps\\Test Maps\\" + "test1" + ".png")
    map_photo = ImageTk.PhotoImage(map_image)
    canvas.create_image(0, 90, anchor=tk.NW, image=map_photo)

    # move tiles
    blue_tile = Image.open(__location__ + "\\CombatSprites\\" + "tileblue" + ".png")
    bt_photo = ImageTk.PhotoImage(blue_tile)

    light_blue_tile = Image.open(__location__ + "\\CombatSprites\\" + "tilelightblue" + ".png")
    lbt_photo = ImageTk.PhotoImage(light_blue_tile)

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



    aoe_special_icon_image = status_pic.crop((1047, 419, 1200, 560))
    aoe_special_icon_image = aoe_special_icon_image.resize((90, 90), Image.LANCZOS)
    aoe_special_icon_photo = ImageTk.PhotoImage(aoe_special_icon_image)
    #canvas.create_image((0, 90), image=aoe_special_icon_photo, anchor=tk.center)

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

    aoe_special_icons_active = []

    units_all = [player_units_all, enemy_units_all]
    units_alive = [player_units, enemy_units]
    tags_all = [player_tags, enemy_tags]
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
        #modifier = curImage.height/85
        #resized_image = curImage.resize((int(curImage.width / modifier), 85), Image.LANCZOS)
        resized_image = curImage.resize((int(curImage.width / 2.1), int(curImage.height/ 2.1)), Image.LANCZOS)

        curPhoto = ImageTk.PhotoImage(resized_image)
        player_sprites.append(curPhoto)

        grayscale_image = resized_image.convert("L")

        transparent_image = Image.new("RGBA", resized_image.size, (0, 0, 0, 0))
        transparent_image.paste(grayscale_image, (0, 0), mask=resized_image.split()[3])

        grayscale_photo = ImageTk.PhotoImage(transparent_image)
        grayscale_player_sprites.append(grayscale_photo)

        name = x.intName
        side = 'P'
        tag = f"tag_{name.replace('!', '_')}_{i}_{side}"
        player_tags.append(tag)

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

        name = x.intName
        side = 'E'
        tag = f"tag_{name.replace('!', '_')}_{i}_{side}"
        enemy_tags.append(tag)


    # CREATE IMAGES ON CANVAS

    for i, player_sprite in enumerate(player_sprites):
        item_id = canvas.create_image(100 * i, 200, anchor='center', image=player_sprite, tags=(player_tags[i]))
        player_sprite_IDs.append(item_id)

    for i, grayscale_player_sprite in enumerate(grayscale_player_sprites):
        item_id = canvas.create_image(100 * i, 200, anchor='center', image=grayscale_player_sprite, tags=player_tags[i])
        grayscale_player_sprite_IDs.append(item_id)

    for i, enemy_sprite in enumerate(enemy_sprites):
        item_id = canvas.create_image(100 * i, 200, anchor='center', image=enemy_sprite, tags=enemy_tags[i])
        enemy_sprite_IDs.append(item_id)

    for i, grayscale_enemy_sprite in enumerate(grayscale_enemy_sprites):
        item_id = canvas.create_image(100 * i + 200, 200, anchor='center', image=grayscale_enemy_sprite, tags=enemy_tags[i])
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
        hp_label = canvas.create_text(200, 100 * (2 + i), text=hp_string, fill="#1e33eb", font=("Helvetica", 16, 'bold'), anchor='center', tags=player_tags[i])
        player_hp_count_labels.append(hp_label)

        hp_bar_bg = canvas.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill='black', width=0, tags=player_tags[i])
        player_hp_bar_bg.append(hp_bar_bg)

        hp_bar_fg = canvas.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill='#1e33eb', width=0, tags=player_tags[i])
        player_hp_bar_fg.append(hp_bar_fg)


    for i, enemy in enumerate(enemy_units_all):
        w_image = weapon_icons[weapons[enemy.wpnType][0]]
        weapon_icon = canvas.create_image(160, 50 * (i + 2), anchor=tk.NW, image=w_image, tags=enemy_tags[i])
        enemy_weapon_icons.append(weapon_icon)

        count_string = enemy.specialCount
        if enemy.specialCount == -1: count_string = ""
        special_label = canvas.create_text(200, 100 * (2 + i), text=count_string, fill="#e300e3", font=("Helvetica", 19, 'bold'), anchor='center', tags=enemy_tags[i])
        enemy_special_count_labels.append(special_label)

        hp_string = enemy.HPcur
        hp_label = canvas.create_text(200, 100 * (2 + i), text=hp_string, fill="#941e03", font=("Helvetica", 16, 'bold'), anchor='center', tags=enemy_tags[i])
        enemy_hp_count_labels.append(hp_label)

        hp_bar_bg = canvas.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill='black', width=0, tags=enemy_tags[i])
        enemy_hp_bar_bg.append(hp_bar_bg)

        hp_bar_fg = canvas.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill='#941e03', width=0, tags=enemy_tags[i])
        enemy_hp_bar_fg.append(hp_bar_fg)

    # MOVE SPRITES TO START LOCATIONS

    i = 0
    while i < len(player_units):
        move_to_tile(canvas, player_tags[i], chosen_map.player_start_spaces[i]) # place sprite
        player_units[i].tile = chosen_map.tiles[chosen_map.player_start_spaces[i]]
        player_units[i].tile.hero_on = player_units[i]
        player_units[i].side = PLAYER

        move_to_tile_wp(canvas, player_weapon_icons[i], chosen_map.player_start_spaces[i])
        move_to_tile_sp(canvas, player_special_count_labels[i], chosen_map.player_start_spaces[i])
        move_to_tile_hp(canvas, player_hp_count_labels[i], chosen_map.player_start_spaces[i])

        move_to_tile_fg_bar(canvas, player_hp_bar_bg[i], chosen_map.player_start_spaces[i])
        move_to_tile_fg_bar(canvas, player_hp_bar_fg[i], chosen_map.player_start_spaces[i])

        canvas.itemconfig(grayscale_player_sprite_IDs[i], state='hidden')

        i += 1

    i = 0
    while i < len(enemy_units):
        start_tile = chosen_map.enemy_start_spaces[i]

        move_to_tile(canvas, enemy_tags[i], start_tile)
        enemy_units[i].tile = chosen_map.tiles[start_tile]
        enemy_units[i].tile.hero_on = enemy_units[i]
        enemy_units[i].side = ENEMY

        move_to_tile_wp(canvas, enemy_weapon_icons[i], start_tile)
        move_to_tile_sp(canvas, enemy_special_count_labels[i], start_tile)
        move_to_tile_hp(canvas, enemy_hp_count_labels[i], start_tile)

        move_to_tile_fg_bar(canvas, enemy_hp_bar_bg[i], start_tile)
        move_to_tile_fg_bar(canvas, enemy_hp_bar_fg[i], start_tile)

        canvas.itemconfig(grayscale_enemy_sprite_IDs[i], state='hidden')

        i += 1

    end_turn = canvas.create_rectangle((380, 820, 450, 900), fill='#f21651', width=0)
    end_turn_text = canvas.create_text(415, 855, text="End Turn", fill="#edb7be")
    duo_skill = canvas.create_rectangle((460, 820, 530, 900), fill='#75f216', width=0)
    end_turn_text = canvas.create_text(495, 855, text="Duo Skill", fill="#5e5b03")


    damage, heals = start_of_turn(player_units, 1)

    for unit in player_units_all:
        if unit in heals:
            unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + heals[unit])
            animate_heal_popup(canvas, heals[unit], unit.tile.tileNum)

            set_hp_visual(unit, unit.HPcur)

    i = 0
    while i < len(player_units):
        if player_units[i].specialCount != -1:
            canvas.itemconfig(player_special_count_labels[i], text=player_units[i].specialCount)
        i += 1

    i = 0
    while i < len(enemy_units):
        if enemy_units[i].specialCount != -1:
            canvas.itemconfig(enemy_special_count_labels[i], text=enemy_units[i].specialCount)
        i += 1

    combat_fields = []
    combat_fields = create_combat_fields(player_units, enemy_units)

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