from combat import *

from field_helpers import start_of_turn, end_of_combat, create_combat_fields, get_warp_moves, allies_within_n
from map import Map, Structure

import tkinter as tk
from PIL import Image, ImageTk
import os
import json
import random
from re import sub

print("Beginning running...")

PLAYER = 0
ENEMY = 1

RARITY_COLORS = ["#43464f", "#859ba8", "#8a4d15", "#c7d6d6", "#ffc012"]

moves = {0: "Infantry", 1: "Cavalry", 2: "Flyer", 3: "Armored"}

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# A possible movement action by a unit
class Move():
    def __init__(self, dest, action, target, num_moved, is_warp, trav_str):
        self.destination = dest  # tile ID
        self.action = action  # 0 - move, 1 - assist, 2 - attack, -1 - end turn (screw you divine vein this needs to be separate)
        self.target = target  # Hero/Structure targeted by assist/attack
        self.num_moved = num_moved  # num tiles between start and this tile
        self.is_warp = is_warp  # does this move use a warp space?
        self.trav_string = trav_str  # traversal string, holds default optimal path


# Saves the state of a singular unit
class UnitState:
    def __init__(self, unit: Hero):
        self.cur_hp = unit.HPcur
        self.cur_sp = unit.specialCount

        self.cur_position = unit.tile.tileNum

        self.cur_buffs = unit.buffs[:]
        self.cur_debuffs = unit.debuffs[:]
        self.cur_status_pos = unit.statusPos[:]
        self.cur_status_neg = unit.statusNeg[:]

        self.sp_galeforce = unit.special_galeforce_triggered
        self.nsp_galeforce = unit.nonspecial_galeforce_triggered

        self.canto = unit.canto_ready


# One state of the game
class MapState:
    def __init__(self, unit_states, struct_states, units_to_move, turn_num):
        self.unit_states = unit_states
        self.struct_states = struct_states
        self.units_to_move = units_to_move

        self.turn_num = turn_num

    def print_mapstate(self):
        print("Unit States:")
        for unit in self.unit_states.keys():
            print(unit.intName)
            print(f" Current HP: {self.unit_states[unit].cur_hp}")
            print(f" Special Count: {self.unit_states[unit].cur_sp}")
            print(f" Tile Position: {self.unit_states[unit].cur_position}")
            print(f" Buffs: {self.unit_states[unit].cur_buffs}")
            print(f" Debuffs: {self.unit_states[unit].cur_debuffs}")
            print(f" Positive Statuses: {self.unit_states[unit].cur_status_pos}")
            print(f" Negative Statuses: {self.unit_states[unit].cur_status_neg}")
            print(f" Nonspecial Galeforce Triggered: {self.unit_states[unit].nsp_galeforce}")
            print(f" Special Galeforce Triggered: {self.unit_states[unit].sp_galeforce}")
            print(f" Canto Usable: {self.unit_states[unit].canto}")

        print("\nStructure States:")
        print(self.struct_states)

        print("\nUnits to Move:")
        for unit in self.units_to_move:
            print(unit.intName)

        print("\nTurn Num: " + str(self.turn_num))


# Create blank to be played upon
map0 = Map(0)
map_num = "Map_Z0003"

# Read JSON data associated with loaded map
# with open(__location__ + "\\Maps\\Story Maps\\Book 1\\Preface\\story0-0-1.json") as read_file: data = json.load(read_file)
with open(__location__ + "/Maps/Arena Maps/" + map_num + ".json") as read_file: data = json.load(read_file)

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

# ragnell = Weapon("Emblem Ragnell", "Emblem Ragnell", "", 16, 1, "Sword", {"slaying": 1, "dCounter": 0, "BIGIKEFAN": 1018}, {})
# GREAT_AETHER = Special("Great Aether", "", {"numFoeAtkBoostSp": 4, "AETHER_GREAT": 17}, 4, SpecialType.Offense)
honeAtk1 = makeSkill("Hone Atk 1")

# ike = makeHero("E!Ike")

# ike.set_skill(ragnell, WEAPON)
# ike.set_skill(GREAT_AETHER, SPECIAL)
# ike.set_skill(honeAtk1, CSKILL)

# ike.set_IVs(ATK,SPD,ATK)
# ike.set_level(40)

caring_magic = makeWeapon("Caring Magic")
warp_ragnarok = makeSpecial("Warp Ragnarok")
verge_of_death = makeSkill("Verge of Death")
resonance_4 = makeSkill("Resonance 4")
inf_null_follow = makeSkill("Inf. Null Follow 4")

celica = makeHero("Linde")

celica.set_skill(caring_magic, WEAPON)
celica.set_skill(warp_ragnarok, SPECIAL)
celica.set_skill(verge_of_death, ASKILL)
celica.set_skill(resonance_4, BSKILL)
celica.set_skill(inf_null_follow, CSKILL)

# united_bouquet = Weapon("United Bouquet", "United Bouquet", "", 16, 1, "Lance", {"slaying": 1, "bridal_shenanigans": 2}, {})

# Forever Yours' ally-granted galeforce triggers after ally's movement skills, before their canto

# forever_yours = makeSkill("Forever Yours")
# no_quarter = makeSpecial("No Quarter")
# potent4 = makeSkill("Potent 4")

dverger_wayfinder = Weapon("Dvergr Wayfinder", "Dvergr Wayfinder", "", 16, 1, "Lance",
                           {"slaying": 1, "reginnAccel": 14}, [])
reposition = makeAssist("Reposition")
seiðr_blast = Special("Seiðr Blast", "", {"spdBoostSp": 5, "reginnBlast": 10}, 3, "Offense")
atkspd_excel = makeSkill("Atk/Spd Excel")
flow_guard_4 = Skill("Flow Guard 4", "", "B", 4, {"flow_guard4": 4}, [])
shadow_shift_4 = Skill("Shadow Shift 4", "", "C", 4, {"show_shift4": 4}, [])

sisterly_axe = makeWeapon("Sisterly Axe")
gust = makeSpecial("Gust")
d_bonus_doubler = makeSkill("D Bonus Doubler")
moonlit_bangle_q = makeSkill("Moonlit Bangle Q")
times_pulse_4 = makeSkill("Time's Pulse 4")

xander = makeHero("Roderick")
xander.set_skill(makeWeapon("Knightly LanceEff"), WEAPON)
xander.set_skill(makeAssist("Shove"), ASSIST)
xander.set_skill(makeSpecial("Moonbow"), SPECIAL)
xander.set_skill(makeSkill("Attack/Res 2"), ASKILL)
xander.set_skill(makeSkill("Seal Atk/Spd 2"), BSKILL)
xander.set_skill(makeSkill("Drive Def 2"), CSKILL)
xander.set_skill(makeSeal("Attack +3"), SSEAL)

# reginn = makeHero("AI!Reginn")
reginn = Hero("Reginn", "AI!Reginn", "Dvergr Heir", 0, "Lance", 1, [41, 46, 48, 38, 22], [50, 80, 90, 60, 40], 5, 5, 0)

reginn.set_skill(dverger_wayfinder, WEAPON)
reginn.set_skill(reposition, ASSIST)
reginn.set_skill(seiðr_blast, SPECIAL)
reginn.set_skill(atkspd_excel, ASKILL)
reginn.set_skill(flow_guard_4, BSKILL)
reginn.set_skill(shadow_shift_4, CSKILL)

# reginn.set_IVs(SPD,DEF,SPD)
# reginn.set_level(40)

tested_unit = makeHero("Faye")
tested_weapon = makeWeapon("Firesweep Bow+")
tested_assist = makeAssist("Reposition")
tested_special = makeSpecial("Iceberg")
tested_askill = makeSkill("Death Blow 3")
tested_bskill = makeSkill("Wings of Mercy 3")
tested_cskill = makeSkill("Hone Atk 3")

tested_unit.set_skill(tested_weapon, WEAPON)
tested_unit.set_skill(tested_assist, ASSIST)
tested_unit.set_skill(tested_special, SPECIAL)
tested_unit.set_skill(tested_askill, ASKILL)
tested_unit.set_skill(tested_bskill, BSKILL)
tested_unit.set_skill(tested_cskill, CSKILL)


# tested_unit.resp = True

# player_units_all = [celica, sharena, xander, tested_unit]
# enemy_units_all = []

# player_units = player_units_all[:]
# enemy_units = []

# METHODS

def allowed_movement(hero):
    move_type = hero.move

    spaces_allowed = 3 - abs(move_type - 1)

    spaces_allowed += 1 * (Status.MobilityUp in hero.statusPos)
    if Status.Gravity in hero.statusNeg or Status.MobilityUp in hero.statusPos and Status.Stall in hero.statusNeg:
        spaces_allowed = 1

    return spaces_allowed


# given a hero on a map, generate a list of tiles they can move to
def get_possible_move_tiles(hero, enemy_team, spaces_allowed=None):
    curTile = hero.tile

    if spaces_allowed is None:
        spaces_allowed = allowed_movement(hero)

    visited = set()  # tiles that have already been visited
    queue = [
        (curTile, 0, "")]  # array of tuples of potential movement tiles, current costs, and current optimal pattern
    possible_tiles = []  # unique, possible tiles, to be returned
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

                if within_allowed_cost and neighbor_cost >= 0 and (
                        x.hero_on is None or (x.hero_on is not None and x.hero_on.side == hero.side) or pass_cond):
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


def get_regular_moves(unit, unit_team, enemy_team):
    cur_tile = unit.tile

    dests = []
    paths = []
    move_Objs = []

    moves, temp_paths, obstruct_tiles = get_possible_move_tiles(unit, enemy_team)

    warp_tiles = get_warp_moves(unit, unit_team, enemy_team)

    for i in range(0, len(moves)):
        dests.append(moves[i].tileNum)
        paths.append(temp_paths[i])
        end = moves[i].tileNum
        distance = abs(end % 6 - cur_tile.x_coord) + abs(end // 6 - cur_tile.y_coord % 6)
        move_Objs.append(Move(end, 0, None, distance, False, paths[i]))

    for i in range(0, len(warp_tiles)):
        if warp_tiles[i].tileNum not in dests:
            dests.append(warp_tiles[i].tileNum)
            paths.append("WARP")
            end = warp_tiles[i].tileNum
            distance = abs(end % 6 - cur_tile.x_coord) + abs(end // 6 - cur_tile.y_coord % 6)
            move_Objs.append(Move(end, 0, None, distance, True, "WARP"))

    for i in range(0, len(obstruct_tiles)):
        if obstruct_tiles[i].tileNum not in dests and obstruct_tiles[i].hero_on is None:
            dests.append(obstruct_tiles[i].tileNum)
            paths.append("WARP")
            end = obstruct_tiles[i].tileNum
            distance = abs(end % 6 - cur_tile.x_coord) + abs(end // 6 - cur_tile.y_coord % 6)
            move_Objs.append(Move(end, 0, None, distance, True, "WARP"))

    return dests, paths, move_Objs


def get_canto_moves(unit, unit_team, enemy_team, distance_traveled, allowed_movement, turn):
    cur_tile = unit.tile

    canto_dests = []
    canto_paths = []
    canto_move_Objs = []

    base_move = 0

    unitSkills = unit.getSkills()

    if "reginnAccel" in unitSkills and turn <= 4:
        base_move = max(base_move, min(distance_traveled + 2, 5))

    # Canto does not trigger at all, occurs under the following conditions:
    # - Canto Dist. with 0 spaces traveled
    # - Canto Rem. with max spaces traveled
    # - Canto Ally 2 with no allies in range (unsure if ally in range but no valid
    #   warp tiles will still activate canto, please test and DM me @Cloud__Z__)
    # - Unit does not meet any conditions to activate any type of canto
    # In these cases, Canto Control is not applied by a foe, and unit can still
    # activate Canto elsewhere if given another action.
    if base_move == 0:
        return [], [], []

    moves, paths, obstruct_tiles = get_possible_move_tiles(unit, enemy_team, base_move)

    warp_tiles = get_warp_moves(unit, unit_team, enemy_team)

    for i in range(0, len(moves)):
        canto_dests.append(moves[i].tileNum)
        canto_paths.append(paths[i])

        end = moves[i].tileNum
        distance = abs(end % 6 - cur_tile.x_coord) + abs(end // 6 - cur_tile.y_coord % 6)
        canto_move_Objs.append(Move(end, 0, None, distance, False, canto_paths[i]))

    for i in range(0, len(warp_tiles)):
        if warp_tiles[i].tileNum not in canto_dests:

            end = warp_tiles[i].tileNum
            distance = abs(end % 6 - cur_tile.x_coord) + abs(end // 6 - cur_tile.y_coord % 6)

            # If warp is not within allowed number of spaces and not using warp-based canto
            if distance > base_move and base_move != -1:
                continue

            canto_dests.append(warp_tiles[i].tileNum)
            canto_paths.append("WARP")
            canto_move_Objs.append(Move(end, 0, None, distance, True, "WARP"))

    for i in range(0, len(obstruct_tiles)):
        if obstruct_tiles[i].tileNum not in canto_dests and obstruct_tiles[i].hero_on is None:
            canto_dests.append(obstruct_tiles[i].tileNum)
            canto_paths.append("WARP")
            end = obstruct_tiles[i].tileNum
            distance = abs(end % 6 - cur_tile.x_coord) + abs(end // 6 - cur_tile.y_coord % 6)
            canto_move_Objs.append(Move(end, 0, None, distance, True, "WARP"))

    return canto_dests, canto_paths, canto_move_Objs


# given an adjacent tile and hero, calculate the movement cost to get to it
def get_tile_cost(tile, hero):
    cost = 1
    move_type = hero.move

    # cases in which units cannot go to tile
    if tile.terrain == 1 and move_type == 1: return -1  # cavalry & forests
    if tile.terrain == 2 and move_type != 2: return -1  # nonfliers & water/mountains
    if tile.terrain == 4: return -1  # impassible terrain for anyone
    if tile.structure_on is not None and tile.structure_on.health != 0: return -1  # structure currently on

    if tile.terrain == 1 and move_type == 0: cost = 2
    if tile.terrain == 3 and move_type == 1: cost = 3
    if tile.divine_vein == 1 and tile.divine_vein_owner != hero.side and hero.getRange() == 2: cost = 2

    if Status.TraverseTerrain in hero.statusPos: cost = 1

    if "cannotStopTakumi" in hero.getSkills() and hero.HPcur / hero.visible_stats[HP] >= 0.50: cost = 1

    if tile.hero_on is not None:
        if "pathfinder" in tile.hero_on.getSkills(): cost = 0

    return cost


# OBSTRUCT TILE PLACEMENTS
def get_obstruct_tiles(unit, enemy_team):
    all_obstruct_tiles = []
    for enemy in enemy_team:
        enemy_skills = enemy.getSkills()

        obstruct_cond = False

        if "obstruct" in enemy_skills and enemy.HPcur / enemy.visible_stats[HP] >= 1.1 - enemy_skills["obstruct"] * 0.2:
            obstruct_cond = True
        if "obstructSe" in enemy_skills and enemy.HPcur / enemy.visible_stats[HP] >= 1.1 - enemy_skills["obstructSe"] * 0.2:
            obstruct_cond = True

        if obstruct_cond:
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

    bottom_row = (0, 1, 2, 3, 4, 5)
    if u_tile in bottom_row and a_tile == u_tile + 6: return -1

    top_row = (42, 43, 44, 45, 46, 47)
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
    1: [-2, -1, 0, 1, 2],  # Rising/Blazing Flame
    2: [-7, -5, 0, 5, 7],  # Rising/Blazing Light
    3: [-12, -6, 0, 6, 12],  # Rising/Blazing Thunder
    4: [-6, -1, 0, 1, 6],  # Rising/Blazing Wind & Gifted Magic (I & II)

    11: [-7, -5, -2, -1, 0, 1, 2, 5, 7],  # Growing Flame
    12: [-12, -7, -5, -2, 0, 2, 5, 7, 12],  # Growing Light
    13: [-18, -12, -6, -1, 0, 1, 6, 12, 18],  # Growing Thunder
    14: [-7, -6, -5, -1, 0, 1, 5, 6, 7],  # Growing Wind

    21: [5, 6, 7, 11, 12, 13, 17, 18, 19],  # Override, Facing North
}

# Under assumption of 6x8 map
# Constants to assume whether a tile is valid for AOE targeting (not off map)
tile_conditions = {
    -18: lambda x: 0 <= x <= 48,
    -12: lambda x: 0 <= x <= 48,
    -7: lambda x: 0 <= x <= 48 and (x - 1) % 6 < 5,
    -6: lambda x: 0 <= x <= 48,
    -5: lambda x: 0 <= x and x <= 47 and (x + 1) % 6 > 0,
    -2: lambda x: (x - 2) % 6 < 4,
    -1: lambda x: (x - 1) % 6 < 5,
    0: lambda x: True,
    1: lambda x: (x + 1) % 6 > 0,
    2: lambda x: (x + 2) % 6 > 1,
    5: lambda x: 0 <= x <= 48 and (x - 1) % 6 < 5,
    6: lambda x: 0 <= x <= 48,
    7: lambda x: 0 <= x <= 48 and (x + 1) % 6 > 0,
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


# If the unit's move type can be on the given terrain & structure
def can_be_on_tile(tile, move_type_int):
    # Structures
    if tile.structure_on is not None:
        # Destructable wall
        if tile.structure_on.struct_type == 0 and tile.structure_on.health != 0:
            return 0

    if tile.terrain == 0 or tile.terrain == 3: return True
    if tile.terrain == 4: return False

    if tile.terrain == 1:
        if move_type_int == 1:
            return False
        else:
            return True

    if tile.terrain == 2:
        if move_type_int == 2:
            return True
        else:
            return False


# Global animation variable
animation = False

# Global canto variable
canto = None

# Global swap variable
swap_mode = False


# Move different types of images to a set location
def move_to_tile(my_canvas, item_ID, num):
    x_move = 45 + 90 * (num % 6)
    y_move = 135 + 90 * (7 - (num // 6))

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

    displayed_text2 = canvas.create_text((x_pivot + 2, y_pivot + 2), text=str(number), fill='#111111',
                                         font=("Helvetica", 25, 'bold'), anchor='center')
    displayed_text = canvas.create_text((x_pivot, y_pivot), text=str(number), fill='#de1d1d',
                                        font=("Helvetica", 25, 'bold'), anchor='center')

    canvas.after(350, forget_text, canvas, displayed_text)
    canvas.after(350, forget_text, canvas, displayed_text2)


# Create green text number at tile num
def animate_heal_popup(canvas, number, text_tile):
    x_comp = text_tile % 6
    y_comp = text_tile // 6
    x_pivot = x_comp * 90 + 45
    y_pivot = (7 - y_comp) * 90 + 90 + 45

    displayed_text2 = canvas.create_text((x_pivot + 2, y_pivot + 2), text=str(number), fill='#111111',
                                         font=("Helvetica", 25, 'bold'), anchor='center')
    displayed_text = canvas.create_text((x_pivot, y_pivot), text=str(number), fill='#14c454',
                                        font=("Helvetica", 25, 'bold'), anchor='center')

    canvas.after(350, forget_text, canvas, displayed_text)
    canvas.after(350, forget_text, canvas, displayed_text2)


def forget_text(canvas, text):
    canvas.delete(text)


def get_attack_tiles(tile_num, range):
    if range != 1 and range != 2: return []
    x_comp = tile_num % 6
    y_comp = tile_num // 6

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
    if arrow_num == 0: return (16, 0)
    if arrow_num == 1: return (16, 1)
    if arrow_num == 3: return (-1, 0)
    if arrow_num == 4: return (16, 2)
    if arrow_num == 5: return (16, 0)
    if arrow_num == 6: return (0, 2)
    if arrow_num == 7: return (0, 1)
    if arrow_num == 9: return (0, 1)
    if arrow_num == 10: return (0, 2)
    if arrow_num == 11: return (0, 2)

    return (0, 0)


def create_mapstate(p_units, e_units, c_map, units_to_move, turn_num):
    unit_states = {}

    for unit in p_units + e_units:
        cur_unit_state = UnitState(unit)
        unit_states[unit] = cur_unit_state

    struct_states = {}

    for tile in c_map.tiles:
        if tile.structure_on is not None:
            cur_struct = tile.structure_on

            struct_states[cur_struct] = cur_struct.health

    return MapState(unit_states, struct_states, units_to_move[:], turn_num)


def start_sim(player_units, enemy_units, chosen_map, map_str):
    player_units_all = player_units[:]
    enemy_units_all = enemy_units[:]

    if not chosen_map.player_start_spaces or not chosen_map.enemy_start_spaces:
        print("Error 100: No starting tiles")
        return -1

    if not player_units or len(player_units) > len(chosen_map.player_start_spaces):
        print("Error 101: Invalid number of player units")
        return -1

    def next_phase():


        canvas.itemconfig(swap_spaces_text, fill="#282424")
        canvas.itemconfig(swap_spaces, fill="#282424")

        # alternate turns
        turn_info[1] = abs(turn_info[1] - 1)

        units_to_move_CACHE = units_to_move[:]

        while units_to_move:
            units_to_move.pop()

        clear_banner()

        # increment count if player phase
        if turn_info[1] == PLAYER:

            print("---- PLAYER PHASE ----")

            turn_info[0] += 1

            canvas.delete(next_phase.turn_txt)
            next_phase.turn_txt = canvas.create_text((540 / 2, 860),
                                                     text="Turn " + str(turn_info[0]) + "/" + str(turn_info[2]),
                                                     fill="#97a8c4", font=("Helvetica", 16), anchor='center')

            canvas.delete(next_phase.phase_txt)
            next_phase.phase_txt = canvas.create_text((540 / 2, 830), text="PLAYER PHASE", fill="#038cfc",
                                                      font=("Helvetica", 20), anchor='center')

            for x in player_units:
                units_to_move.append(x)
                x.statusPos = []
                x.buffs = [0] * 5
                x.special_galeforce_triggered = False

                x.canto_ready = True

            for x in enemy_units:
                if x in units_to_move_CACHE:
                    x.statusNeg = []
                    x.debuffs = [0] * 5

            #for i in range(0, len(enemy_units_all)):

            i = 0
            for unit in enemy_units_all:
                if unit.HPcur > 0:
                    canvas.itemconfig(grayscale_enemy_sprite_IDs[i], state='hidden')
                    canvas.itemconfig(enemy_sprite_IDs[i], state='normal')
                i += 1

            damage, heals = start_of_turn(player_units, enemy_units, turn_info[0])

        if turn_info[1] == ENEMY:
            print("---- ENEMY PHASE ----")

            canvas.delete(next_phase.phase_txt)
            next_phase.phase_txt = canvas.create_text((540 / 2, 830), text="ENEMY PHASE", fill="#e8321e",
                                                      font=("Helvetica", 20), anchor='center')

            for x in enemy_units:
                units_to_move.append(x)
                x.statusPos = []
                x.buffs = [0] * 5
                x.special_galeforce_triggered = False

                x.canto_ready = True

            for x in player_units:
                if x in units_to_move_CACHE:
                    x.statusNeg = []
                    x.debuffs = [0] * 5

            i = 0
            for unit in player_units_all:
                if unit.HPcur > 0:
                    #for i in range(0, len(player_units_all)):
                    canvas.itemconfig(grayscale_player_sprite_IDs[i], state='hidden')
                    canvas.itemconfig(player_sprite_IDs[i], state='normal')
                i += 1

            damage, heals = start_of_turn(enemy_units, player_units, turn_info[0])

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

        mapstate = create_mapstate(player_units_all, enemy_units_all, chosen_map, units_to_move, turn_info[0])
        map_states.append(mapstate)

    def toggle_swap():
        global swap_mode

        swap_mode = not swap_mode

        if swap_mode:
            canvas.itemconfig(swap_spaces_text, text="Confirm")
            canvas.itemconfig(swap_spaces, fill="green3")

            # canvas color = #282424

            canvas.itemconfig(end_turn, fill="#282424")
            canvas.itemconfig(end_turn_text, fill="#282424")

            canvas.itemconfig(undo_action, fill="#282424")
            canvas.itemconfig(undo_action_text, fill="#282424")

            apply_mapstate(canvas.initial_mapstate)

            for unit in player_units_all:
                curTile = canvas.create_image(0, 0, image=gt_photo)
                canvas.canto_tile_imgs.append(curTile)

                canvas.tag_lower(curTile, player_sprite_IDs[player_units_all.index(unit)])

                move_to_tile(canvas, curTile, unit.tile.tileNum)


        else:
            canvas.itemconfig(swap_spaces_text, text="Swap\nSpaces")
            canvas.itemconfig(swap_spaces, fill="#75f216")

            canvas.itemconfig(end_turn, fill="#f21651")
            canvas.itemconfig(end_turn_text, fill="DeepPink4")

            canvas.itemconfig(undo_action, fill="blue")
            canvas.itemconfig(undo_action_text, fill="#bfbda4")

            clear_banner()

            for green_tile_id in canvas.canto_tile_imgs:
                canvas.delete(green_tile_id)
            canvas.canto_tile_imgs.clear()

            canvas.initial_mapstate = create_mapstate(player_units_all, enemy_units_all, chosen_map, units_to_move, turn_info[0])

            print("---- PLAYER PHASE ----")
            damage, heals = start_of_turn(player_units, enemy_units, 1)

            for unit in player_units_all:
                if unit in heals:
                    unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + heals[unit])
                    animate_heal_popup(canvas, heals[unit], unit.tile.tileNum)

                    set_hp_visual(unit, unit.HPcur)

            i = 0
            while i < len(player_units):
                if player_units[i].specialCount != -1:
                    canvas.itemconfig(player_special_count_labels[i], text=player_units[i].specialCount)

                player_units[i].canto_ready = True

                i += 1

            i = 0
            while i < len(enemy_units):
                if enemy_units[i].specialCount != -1:
                    canvas.itemconfig(enemy_special_count_labels[i], text=enemy_units[i].specialCount)
                i += 1

            map_states.clear()

            map_states.append(create_mapstate(player_units_all, enemy_units_all, chosen_map, units_to_move, turn_info[0]))

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
        set_banner.banner_rectangle = canvas.create_rectangle(0, 0, 539, 90, fill=banner_color,
                                                              outline=RARITY_COLORS[hero.rarity - 1])

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

        unit_info_label = tk.Label(canvas, text=name, bg="gray14", font="Helvetica 12", fg="white", relief="raised",
                                   width=13)
        unit_info_label.place(x=10, y=5)

        set_banner.label_array.append(unit_info_label)

        move_icon = canvas.create_image(135, 6, anchor=tk.NW, image=move_icons[hero.move])
        weapon_icon = canvas.create_image(160, 4, anchor=tk.NW, image=weapon_icons[weapons[hero.wpnType][0]])

        set_banner.rect_array.append(move_icon)
        set_banner.rect_array.append(weapon_icon)

        text_var = "Level " + str(hero.level)
        merge_var = ""
        if hero.merges > 0: merge_var = " + " + str(hero.merges)

        unit_level_label = tk.Label(canvas, text=text_var + merge_var, bg="gray14", font="Helvetica 12", fg="white",
                                    relief="raised", width=11)
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

        panic_factor = 1
        if Status.Panic in hero.statusNeg: panic_factor = -1
        if Status.NullPanic in hero.statusPos: panic_factor = 1

        i = 0
        while i < 5:
            if hero.buffs[i] * panic_factor > abs(hero.debuffs[i]):
                fills[i] = 'blue'
            if abs(hero.debuffs[i]) > hero.buffs[i] * panic_factor:
                fills[i] = 'red'

            if i == HP and hero.HPcur < 10:
                fills[i] = 'red'

            i += 1

        percentage = trunc(hero.HPcur / stats[HP] * 1000) / 10
        if percentage == 100.0:
            percentage = 100

        set_banner.rect_array.append(
            canvas.create_text((185, 38), text=hero.HPcur, fill=fills[HP], font=("Helvetica", 12)))
        set_banner.rect_array.append(
            canvas.create_text((205, 38), text="/" + str(stats[HP]), fill='white', font=("Helvetica", 12)))
        set_banner.rect_array.append(
            canvas.create_text((250, 38), text=str(percentage) + "%", fill='white', font=("Helvetica", 12)))

        displayed_atk = min(max(stats[ATK] + hero.buffs[ATK] * panic_factor + hero.debuffs[ATK], 0), 99)
        displayed_spd = min(max(stats[SPD] + hero.buffs[SPD] * panic_factor + hero.debuffs[SPD], 0), 99)
        displayed_def = min(max(stats[DEF] + hero.buffs[DEF] * panic_factor + hero.debuffs[DEF], 0), 99)
        displayed_res = min(max(stats[RES] + hero.buffs[RES] * panic_factor + hero.debuffs[RES], 0), 99)

        set_banner.rect_array.append(
            canvas.create_text((185, 56), text=displayed_atk, fill=fills[ATK], font=("Helvetica", 11)))
        set_banner.rect_array.append(
            canvas.create_text((265, 56), text=displayed_spd, fill=fills[SPD], font=("Helvetica", 11)))
        set_banner.rect_array.append(
            canvas.create_text((185, 73), text=displayed_def, fill=fills[DEF], font=("Helvetica", 11)))
        set_banner.rect_array.append(
            canvas.create_text((265, 73), text=displayed_res, fill=fills[RES], font=("Helvetica", 11)))

        # SKILLS
        set_banner.rect_array.append(
            canvas.create_text((308, (5 + 22) / 2), text="⚔️", fill="red", font=("Helvetica", 9), anchor='e'))
        text_coords = ((310 + 410) / 2, (5 + 22) / 2)

        refine_suffixes = ("Eff", "Atk", "Spd", "Def", "Res", "Wra", "Daz")

        weapon_fill = "white"
        if int_name_weapon.endswith(refine_suffixes):
            weapon_fill = "#6beb34"

        ref_str = ""
        for suffix in refine_suffixes:
            if int_name_weapon.endswith(suffix):
                ref_str = " (" + suffix[0] + ")"

        set_banner.rect_array.append(
            canvas.create_text(*text_coords, text=weapon + ref_str, fill=weapon_fill, font=("Helvetica", 9),
                               anchor='center'))

        set_banner.rect_array.append(
            canvas.create_text((309, (25 + 38) / 2), text="◐", fill="green", font=("Helvetica", 23), anchor='e'))
        text_coords = ((310 + 410) / 2, (25 + 42) / 2)
        set_banner.rect_array.append(
            canvas.create_text(*text_coords, text=assist, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(
            canvas.create_text((308, (45 + 60) / 2), text="☆", fill="#ff33ff", font=("Helvetica", 10), anchor='e'))
        text_coords = ((310 + 410) / 2, (45 + 62) / 2)
        set_banner.rect_array.append(
            canvas.create_text(*text_coords, text=special, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(
            canvas.create_text((305, (65 + 80) / 2), text="S", fill="#ffdd33", font="Helvetica 10 bold", anchor='e'))
        text_coords = ((310 + 410) / 2, (65 + 82) / 2)
        set_banner.rect_array.append(
            canvas.create_text(*text_coords, text=sSeal, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(
            canvas.create_text((425, (5 + 22) / 2), text="A", fill="#e6150e", font="Helvetica 10 bold", anchor='e'))
        text_coords = ((430 + 530) / 2, (5 + 22) / 2)
        set_banner.rect_array.append(
            canvas.create_text(*text_coords, text=askill, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(
            canvas.create_text((425, (25 + 42) / 2), text="B", fill="#5d68dd", font="Helvetica 10 bold", anchor='e'))
        text_coords = ((430 + 530) / 2, (25 + 42) / 2)
        set_banner.rect_array.append(
            canvas.create_text(*text_coords, text=bskill, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(
            canvas.create_text((425, (45 + 62) / 2), text="C", fill="#38e85b", font="Helvetica 10 bold", anchor='e'))
        text_coords = ((430 + 530) / 2, (45 + 62) / 2)
        set_banner.rect_array.append(
            canvas.create_text(*text_coords, text=cskill, fill="white", font=("Helvetica", 9), anchor='center'))

        set_banner.rect_array.append(
            canvas.create_text((425, (65 + 80) / 2), text="X", fill="#a7e838", font="Helvetica 10 bold", anchor='e'))
        text_coords = ((430 + 530) / 2, (65 + 82) / 2)
        set_banner.rect_array.append(
            canvas.create_text(*text_coords, text=xskill, fill="white", font=("Helvetica", 9), anchor='center'))

        # STATUS EFFECTS DISPLAY
        status_rect = canvas.create_rectangle((75, 49, 127, 81), fill="#7388bd", width=0, tags='status')
        set_banner.rect_array.append(status_rect)
        text_coords = (101, 65)
        set_banner.rect_array.append(
            canvas.create_text(*text_coords, text="Statuses", fill="white", font=("Helvetica", 9), anchor='center',
                               tags='status'))

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
                canvas.bind("<B1-Motion>", on_drag_status)

                on_motion(event)

        def on_motion(event):

            if set_banner.base_rect is not None:

                has_stat_bonuses = sum(hero.buffs) > 0
                has_stat_penalties = sum(hero.debuffs) > 0

                num_bars = int(has_stat_bonuses) + int(has_stat_penalties) + len(positive_statuses) + len(
                    negative_statuses)

                base_length = max(25 * num_bars, 25)

                canvas.coords(set_banner.base_rect, event.x + 12, event.y + 15, event.x + 150,
                              event.y + base_length + 20)

                # no statuses/bonus/penalties, only creates "No Statuses" text
                if len(set_banner.status_rects) == 0 and len(set_banner.status_texts) == 1:
                    canvas.moveto(set_banner.status_texts[0], event.x + 20, event.y + 4 + 20)

                i = 0
                while i < len(set_banner.status_rects):
                    canvas.moveto(set_banner.status_rects[i], event.x + 15, event.y - 2 + (25 * i) + 20)
                    canvas.moveto(set_banner.status_texts[i], event.x + 20, event.y + 4 + (25 * i) + 20)
                    i += 1

        def on_drag_status(event):
            on_motion(event)

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

        canvas.bind("<B1-Motion>", on_drag)

    def set_attack_forecast(attacker: Hero, defender: Hero, distance):
        clear_banner()

        atkHP = attacker.HPcur
        defHP = defender.HPcur

        aoe_damage = 0
        aoe_present = False
        if attacker.special is not None and attacker.special.type == "AOE" and attacker.specialCount == 0:
            aoe_damage: int = get_AOE_damage(attacker, defender)

            defHP = max(1, defHP - aoe_damage)

            aoe_present = True

        result = simulate_combat(attacker, defender, True, turn_info[0], distance, combat_fields, aoe_present,
                                 atkHPCur=atkHP, defHPCur=defHP)

        atk_burn_damage_present = False
        def_burn_damage_present = False

        burn_damages = result[14]

        if burn_damages[1] > 0:
            atkHP = max(1, atkHP - burn_damages[1])
            atk_burn_damage_present = True

        if burn_damages[0] > 0:
            defHP = max(1, defHP - burn_damages[0])
            def_burn_damage_present = True

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

        set_banner.rect_array.append(
            canvas.create_rectangle(0, 0, 539 / 2, 90, fill=player_color, outline=RARITY_COLORS[attacker.rarity - 1]))
        set_banner.rect_array.append(canvas.create_rectangle(539 / 2 + 1, 0, 539, 90, fill=enemy_color,
                                                             outline=RARITY_COLORS[defender.rarity - 1]))

        # Names

        player_name_label = tk.Label(canvas, text=player_name, bg="gray14", font="Helvetica 12", fg="white",
                                     relief="raised", width=13)
        player_name_label.place(x=10, y=5)

        enemy_name_label = tk.Label(canvas, text=enemy_name, bg="gray14", font="Helvetica 12", fg="white",
                                    relief="raised", width=13)
        enemy_name_label.place(x=540 - 10 - 120, y=5)

        set_banner.label_array.append(player_name_label)
        set_banner.label_array.append(enemy_name_label)

        # Icons

        player_move_icon = canvas.create_image(135, 6, anchor=tk.NW, image=move_icons[attacker.move])
        player_weapon_icon = canvas.create_image(160, 4, anchor=tk.NW, image=weapon_icons[weapons[attacker.wpnType][0]])
        enemy_move_icon = canvas.create_image(540 - 135 - 20, 6, anchor=tk.NW, image=move_icons[int(defender.move)])
        enemy_weapon_icon = canvas.create_image(540 - 160 - 20, 4, anchor=tk.NW,
                                                image=weapon_icons[weapons[defender.wpnType][0]])

        set_banner.rect_array.append(player_move_icon)
        set_banner.rect_array.append(player_weapon_icon)
        set_banner.rect_array.append(enemy_move_icon)
        set_banner.rect_array.append(enemy_weapon_icon)

        # HP Calculation

        if aoe_present or def_burn_damage_present:
            atk_feh_math = str(aoe_damage + burn_damages[0]) + " + " + str(atk_feh_math)

        if atk_burn_damage_present:
            def_feh_math = str(burn_damages[1]) + " + " + str(def_feh_math)

        i = 0
        while i < len(attacks):
            if attacks[i].attackOwner == 0:
                defHP = max(0, defHP - attacks[i].damage)
                atkHP = min(attacker.visible_stats[HP], atkHP + attacks[i].healed)

            if attacks[i].attackOwner == 1:
                atkHP = max(0, atkHP - attacks[i].damage)
                defHP = min(defender.visible_stats[HP], defHP + attacks[i].healed)

            if atkHP == 0 or defHP == 0: break
            i += 1

        player_hp_calc = canvas.create_text((215, 16), text=str(player_HPcur) + " → " + str(atkHP), fill='yellow',
                                            font=("Helvetica", 13), anchor='center')
        enemy_hp_calc = canvas.create_text((324, 16), text=str(enemy_HPcur) + " → " + str(defHP), fill="yellow",
                                           font=("Helvetica", 13), anchor='center')

        set_banner.rect_array.append(player_hp_calc)
        set_banner.rect_array.append(enemy_hp_calc)

        # Weapon Triangle Advantage

        if wpn_adv == 0:
            adv_arrow = canvas.create_text((255, 13), text=" ⇑ ", fill='#42bf34', font=("Helvetica", 20, 'bold'),
                                           anchor='center')
            disadv_arrow = canvas.create_text((285, 13), text=" ⇓ ", fill='red', font=("Helvetica", 20, 'bold'),
                                              anchor='center')
            set_banner.rect_array.append(adv_arrow)
            set_banner.rect_array.append(disadv_arrow)
        if wpn_adv == 1:
            adv_arrow = canvas.create_text((255, 13), text=" ↓ ", fill='red', font=("Helvetica", 14), anchor='center')
            disadv_arrow = canvas.create_text((285, 13), text=" ↑ ", fill='#42bf34', font=("Helvetica", 14, 'bold'),
                                              anchor='center')
            set_banner.rect_array.append(adv_arrow)
            set_banner.rect_array.append(disadv_arrow)

        set_banner.rect_array.append(
            canvas.create_rectangle(270 - 40, 27, 270 + 40, 42, fill='#5a5c6b', outline='#dae6e2'))

        # FEH Math

        feh_math_text = canvas.create_text((270, 35), text="FEH Math", fill='#dae6e2', font=("Helvetica", 11, 'bold'),
                                           anchor='center')
        set_banner.rect_array.append(feh_math_text)

        atk_feh_math_text = canvas.create_text((270 - 85, 35), text=atk_feh_math, fill='#e8c35d',
                                               font=("Helvetica", 12), anchor='center')
        set_banner.rect_array.append(atk_feh_math_text)

        def_feh_math_text = canvas.create_text((270 + 85, 35), text=def_feh_math, fill='#e8c35d',
                                               font=("Helvetica", 12), anchor='center')
        set_banner.rect_array.append(def_feh_math_text)

        # Special Count

        if player_spCount != -1:
            atk_sp_charge = canvas.create_text((270 - 135, 35), text=player_spCount, fill='#ff33ff',
                                               font=("Helvetica", 12), anchor='center')
            set_banner.rect_array.append(atk_sp_charge)

        if enemy_spCount != -1:
            def_sp_charge = canvas.create_text((270 + 135, 35), text=enemy_spCount, fill='#ff33ff',
                                               font=("Helvetica", 12), anchor='center')
            set_banner.rect_array.append(def_sp_charge)

        player_atk_text = canvas.create_text((40, 35), text="Atk" + "+" * (player_combat_buffs[ATK] >= 0) + str(
            player_combat_buffs[ATK]), fill='#db3b25', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_atk_text)
        player_spd_text = canvas.create_text((90, 35), text="Spd" + "+" * (player_combat_buffs[SPD] >= 0) + str(
            player_combat_buffs[SPD]), fill='#17eb34', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_spd_text)
        player_def_text = canvas.create_text((60, 48), text="Def" + "+" * (player_combat_buffs[DEF] >= 0) + str(
            player_combat_buffs[DEF]), fill='#dbdb25', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_def_text)
        player_res_text = canvas.create_text((110, 48), text="Res" + "+" * (player_combat_buffs[RES] >= 0) + str(
            player_combat_buffs[RES]), fill='#25dbd2', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_res_text)

        player_atk_text = canvas.create_text((450, 35), text="Atk" + "+" * (enemy_combat_buffs[ATK] >= 0) + str(
            enemy_combat_buffs[ATK]), fill='#db3b25', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_atk_text)
        player_spd_text = canvas.create_text((500, 35), text="Spd" + "+" * (enemy_combat_buffs[SPD] >= 0) + str(
            enemy_combat_buffs[SPD]), fill='#17eb34', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_spd_text)
        player_def_text = canvas.create_text((430, 48), text="Def" + "+" * (enemy_combat_buffs[DEF] >= 0) + str(
            enemy_combat_buffs[DEF]), fill='#dbdb25', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_def_text)
        player_res_text = canvas.create_text((480, 48), text="Res" + "+" * (enemy_combat_buffs[RES] >= 0) + str(
            enemy_combat_buffs[RES]), fill='#25dbd2', font=("Helvetica", 10), anchor='center')
        set_banner.rect_array.append(player_res_text)

        box_size = 30
        gap_size = 8

        num_strikes = len(attacks) + int(aoe_present) + int(atk_burn_damage_present + def_burn_damage_present)

        cur_box_pos = int(270 - (gap_size * 0.5 * (num_strikes - 1) + box_size * 0.5 * (num_strikes - 1)))

        set_banner.rect_array.append(
            canvas.create_rectangle(cur_box_pos - 110, 54, cur_box_pos - 20, 76, fill="silver", outline='#dae6e2'))

        set_banner.rect_array.append(canvas.create_text((cur_box_pos - 65, 65), text="Attack Order", fill='black',
                                                        font=("Helvetica", 10, "bold"), anchor='center'))

        # AOE Special
        if aoe_present:
            box_color = "#6e2a9c"
            set_banner.rect_array.append(
                canvas.create_rectangle(cur_box_pos - 15, 50, cur_box_pos + 15, 80, fill=box_color, outline='#dae6e2'))

            set_banner.rect_array.append(
                canvas.create_text((cur_box_pos, 65), text=aoe_damage, fill='#e8c35d', font=("Helvetica", 12),
                                   anchor='center'))

            cur_box_pos += int(box_size + gap_size)

        if atk_burn_damage_present or def_burn_damage_present:
            atk_burn_txt = burn_damages[0] if def_burn_damage_present else "-"
            def_burn_txt = burn_damages[1] if atk_burn_damage_present else "-"

            atk_color = "#18284f" if attacker.side == 0 else "#541616"
            def_color = "#541616" if attacker.side == 0 else "#18284f"

            set_banner.rect_array.append(
                canvas.create_rectangle(cur_box_pos - 15, 50, cur_box_pos + 15, 65, fill=atk_color, outline='#c9692c'))
            set_banner.rect_array.append(
                canvas.create_text((cur_box_pos, 57), text=atk_burn_txt, fill='#e8c35d', font=("Helvetica", 12),
                                   anchor='center'))

            set_banner.rect_array.append(
                canvas.create_rectangle(cur_box_pos - 15, 65, cur_box_pos + 15, 80, fill=def_color, outline='#c9692c'))
            set_banner.rect_array.append(
                canvas.create_text((cur_box_pos, 72), text=def_burn_txt, fill='#e8c35d', font=("Helvetica", 12),
                                   anchor='center'))

            cur_box_pos += int(box_size + gap_size)

        # Attacks

        for x in attacks:
            box_color = "#18284f" if x.attackOwner == attacker.side else "#541616"
            border_color = "#dae6e2" if not x.isSpecial else "#6e2a9c"

            set_banner.rect_array.append(
                canvas.create_rectangle(cur_box_pos - 15, 50, cur_box_pos + 15, 80, fill=box_color,
                                        outline=border_color))

            dmg_fill = '#e8c35d'
            if x.attackOwner == 0 and atk_eff:
                dmg_fill = '#46eb34'
            if x.attackOwner == 1 and def_eff:
                dmg_fill = '#46eb34'

            set_banner.rect_array.append(
                canvas.create_text((cur_box_pos, 65), text=x.damage, fill=dmg_fill, font=("Helvetica", 12),
                                   anchor='center'))

            cur_box_pos += int(box_size + gap_size)

    def set_assist_forecast(attacker: Hero, ally: Hero):
        clear_banner()

        player_color = "#18284f" if attacker.side == 0 else "#541616"
        enemy_color = "#18284f" if ally.side == 0 else "#541616"

        set_banner.rect_array.append(
            canvas.create_rectangle(0, 0, 539 / 2, 90, fill=player_color, outline=RARITY_COLORS[attacker.rarity - 1]))
        set_banner.rect_array.append(
            canvas.create_rectangle(539 / 2 + 1, 0, 539, 90, fill=enemy_color, outline=RARITY_COLORS[ally.rarity - 1]))

        set_banner.rect_array.append(
            canvas.create_rectangle(0, 0, 539 / 2, 90, fill=player_color, outline=RARITY_COLORS[attacker.rarity - 1]))
        set_banner.rect_array.append(
            canvas.create_rectangle(539 / 2 + 1, 0, 539, 90, fill=enemy_color, outline=RARITY_COLORS[ally.rarity - 1]))

        player_name_label = tk.Label(canvas, text=attacker.name, bg="gray14", fg="white", font="Helvetica 12",
                                     relief="raised", width=13)
        player_name_label.place(x=10, y=5)

        ally_name_label = tk.Label(canvas, text=ally.name, bg="gray14", fg="white", font="Helvetica 12",
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
                hp_healed_self = dmg_taken // 2

            # Martyr+
            if attacker.assist.effects["heal"] == -49:
                dmg_taken = attacker.visible_stats[HP] - attacker.HPcur
                hp_healed_ally = dmg_taken + self_atk_stat // 2
                hp_healed_self = dmg_taken // 2

            # Recover+
            if attacker.assist.effects["heal"] == -10:
                hp_healed_ally = max(self_atk_stat // 2 + 10, 15)

            # Rehabilitate
            if attacker.assist.effects["heal"] == -1:
                ally_hp_max = ally.visible_stats[HP]
                ally_hp_cur = ally.HPcur

                hp_healed_ally = max(7 + ally_hp_max - (2 * ally_hp_cur), 7)

            # Rehabilitate+
            if attacker.assist.effects["heal"] == -2:
                ally_hp_max = ally.visible_stats[HP]
                ally_hp_cur = ally.HPcur

                hp_healed_ally = max(self_atk_stat // 2 - 10, 7) + max(ally_hp_max - (2 * ally_hp_cur), 0)

            # Physic+
            if attacker.assist.effects["heal"] == -50:
                hp_healed_ally = max(self_atk_stat // 2, 8)

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

        set_banner.rect_array.append(
            canvas.create_rectangle(270 - 65, 27, 270 + 65, 42, fill='#5a5c6b', outline='#dae6e2'))

        assist_name = canvas.create_text((270, 34), text=attacker.assist.name, fill="white", font=("Helvetica", 11),
                                         anchor='center')

        set_banner.rect_array.append(player_hp_calc)
        set_banner.rect_array.append(ally_hp_calc)
        set_banner.rect_array.append(assist_name)

        # Icons

        player_move_icon = canvas.create_image(135, 6, anchor=tk.NW, image=move_icons[attacker.move])
        player_weapon_icon = canvas.create_image(160, 4, anchor=tk.NW, image=weapon_icons[weapons[attacker.wpnType][0]])
        ally_move_icon = canvas.create_image(540 - 135 - 20, 6, anchor=tk.NW, image=move_icons[int(ally.move)])
        ally_weapon_icon = canvas.create_image(540 - 160 - 20, 4, anchor=tk.NW,
                                               image=weapon_icons[weapons[ally.wpnType][0]])

        set_banner.rect_array.append(player_move_icon)
        set_banner.rect_array.append(player_weapon_icon)
        set_banner.rect_array.append(ally_move_icon)
        set_banner.rect_array.append(ally_weapon_icon)

        return 0

    def set_struct_forecast(attacker: Hero, structure: Structure):
        clear_banner()

        player_color = "#18284f" if attacker.side == 0 else "#541616"
        struct_color = "#233b1e"
        struct_border = "#82d982"

        set_banner.rect_array.append(
            canvas.create_rectangle(0, 0, 539 / 2, 90, fill=player_color, outline=RARITY_COLORS[attacker.rarity - 1]))
        set_banner.rect_array.append(
            canvas.create_rectangle(539 / 2 + 1, 0, 539, 90, fill=struct_color, outline=struct_border))

        # Name Labels
        player_name_label = tk.Label(canvas, text=attacker.name, bg="gray14", fg="white", font="Helvetica 12",
                                     relief="raised", width=13)
        player_name_label.place(x=10, y=5)

        struct_name = "Obstacle"

        enemy_name_label = tk.Label(canvas, text=struct_name, bg="gray14", fg="white", font="Helvetica 12",
                                    relief="raised", width=13)
        enemy_name_label.place(x=540 - 10 - 120, y=5)

        set_banner.label_array.append(player_name_label)
        set_banner.label_array.append(enemy_name_label)

        # FEH Math
        set_banner.rect_array.append(
            canvas.create_rectangle(270 - 40, 27, 270 + 40, 42, fill='#5a5c6b', outline='#dae6e2'))

        feh_math_text = canvas.create_text((270, 35), text="Destroy", fill='#dae6e2', font=("Helvetica", 11, 'bold'),
                                           anchor='center')
        set_banner.rect_array.append(feh_math_text)

        # Damage labels
        player_hp_calc = canvas.create_text((215, 16), text=str(attacker.HPcur) + " → " + str(attacker.HPcur),
                                            fill='yellow', font=("Helvetica", 13), anchor='center')
        enemy_hp_calc = canvas.create_text((324, 16), text=str(structure.health) + " → " + str(structure.health - 1),
                                           fill="yellow", font=("Helvetica", 13), anchor='center')

        set_banner.rect_array.append(player_hp_calc)
        set_banner.rect_array.append(enemy_hp_calc)

        atk_feh_math_text = canvas.create_text((270 - 85, 35), text="1", fill='#e8c35d', font=("Helvetica", 12),
                                               anchor='center')
        set_banner.rect_array.append(atk_feh_math_text)

        def_feh_math_text = canvas.create_text((270 + 85, 35), text="-", fill='#e8c35d', font=("Helvetica", 12),
                                               anchor='center')
        set_banner.rect_array.append(def_feh_math_text)

        # Icons
        player_move_icon = canvas.create_image(135, 6, anchor=tk.NW, image=move_icons[attacker.move])
        player_weapon_icon = canvas.create_image(160, 4, anchor=tk.NW, image=weapon_icons[weapons[attacker.wpnType][0]])

        set_banner.rect_array.append(player_move_icon)
        set_banner.rect_array.append(player_weapon_icon)

        return 0

    def on_click(event):
        global animation
        global canto
        global swap_mode

        if animation: return

        # Get the current mouse coordinates
        x, y = event.x, event.y

        # End turn button
        if 380 < x < 450 and y > 820 and y < 900 and not swap_mode:
            canto = None

            for blue_tile_id in canvas.canto_tile_imgs:
                canvas.delete(blue_tile_id)
            canvas.canto_tile_imgs.clear()

            next_phase()

            return

        # Swap spaces button
        if 460 < x < 530 and 820 < y < 900 and len(map_states) == 1 and canto is None:
            toggle_swap()
            return



        # Undo button
        if 10 < x < 80 and 820 < y < 900 and not swap_mode:

            if len(map_states) > 1:
                if not canto:
                    map_states.pop()
                apply_mapstate(map_states[-1])
            else:
                apply_mapstate(map_states[0])

            if len(map_states) == 1:
                canvas.itemconfig(swap_spaces_text, fill="#5e5b03")
                canvas.itemconfig(swap_spaces, fill="#75f216")

        # Out of bounds case
        if x < 0 or x > 540 or y <= 90 or y > 810:
            num = random.randint(1, 100)
            if num == 57:
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
            pixel_offset_y = (7 - y_comp) * 90 + 90

            # Banner set to current hero
            set_banner(cur_hero)

            # Not this side's phase, no movement allowed
            if cur_hero.side != turn_info[1]:
                return

            # If this movement is as a canto move and currently selecting the canto-enabled unit
            is_canto_move = canto is not None and canto == cur_hero

            # Hero already moved, cannot be moved again
            if cur_hero not in units_to_move or (canto is not None and canto != cur_hero):
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

            canvas.canto_data = {}

            cur_hero_team = units_alive[S]
            enemy_team = units_all[S - 1]

            # More drag data fields to be defined
            canvas.drag_data['moves'] = []
            canvas.drag_data['paths'] = []
            canvas.drag_data['cost'] = 0
            canvas.drag_data['target'] = None
            canvas.drag_data['targets_and_tiles'] = {}
            canvas.drag_data['targets_most_recent_tile'] = {}

            canvas.drag_data['cur_path'] = ""
            canvas.drag_data['target_path'] = "NONE"
            canvas.drag_data['target_dest'] = -1

            # Get possible tiles to move to, shortest path to get to that tile, and objects of each move
            if is_canto_move:
                canvas.drag_data['moves'], canvas.drag_data['paths'], moves_obj_array = get_canto_moves(cur_hero,
                                                                                                        cur_hero_team,
                                                                                                        enemy_team,
                                                                                                        canvas.distance,
                                                                                                        canvas.spaces_allowed,
                                                                                                        turn_info[0])
            else:
                canvas.drag_data['moves'], canvas.drag_data['paths'], moves_obj_array = get_regular_moves(cur_hero,
                                                                                                          cur_hero_team,
                                                                                                          enemy_team)
                canvas.spaces_allowed = allowed_movement(cur_hero)

            # Keep track of all blue tiles such that they can be destroyed upon release (should be kept in an array outside of method)
            tile_arr = []
            canvas.drag_data['tile_id_arr'] = tile_arr

            # Create blue tiles for each possible movement
            if not (canto is not None and cur_hero == canto) and not swap_mode:

                for m in moves_obj_array:
                    x_comp = m.destination % 6
                    y_comp = m.destination // 6
                    cur_pixel_offset_x = x_comp * 90
                    cur_pixel_offset_y = (7 - y_comp) * 90 + 90

                    tile_photo = bt_photo
                    if m.is_warp:
                        tile_photo = lbt_photo

                    # creates new blue tile, layered under player
                    curTile = canvas.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW,
                                                  image=tile_photo)
                    tile_arr.append(curTile)
                    canvas.tag_lower(curTile, item_id)

            perimeter_attack_range = []  # red tiles on edge of moves
            attack_range = []  # all tiles that can be attacked
            assist_range = []  # all tiles that can be assisted

            # Identify all possible tiles to attack from, regardless of targets
            if cur_hero.weapon is not None and not (canto is not None and canto == cur_hero) and not swap_mode:
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

            # Draw red attack tiles within range
            for n in perimeter_attack_range:
                x_comp = n % 6
                y_comp = n // 6
                cur_pixel_offset_x = x_comp * 90
                cur_pixel_offset_y = (7 - y_comp) * 90 + 90

                # if enemy in range, use red tile instead of pale red tile
                # place this after calculating valid assist positioning?
                cur_tile_photo = prt_photo

                # Tile holds foe
                if chosen_map.tiles[n].hero_on is not None:
                    if chosen_map.tiles[n].hero_on.side != cur_hero.side:
                        cur_tile_photo = rt_photo
                    if chosen_map.tiles[n].hero_on.side == cur_hero.side and cur_hero.assist is not None:
                        cur_tile_photo = None

                # Tile holds structure that can be destroyed
                elif chosen_map.tiles[n].structure_on is not None:
                    if chosen_map.tiles[n].structure_on.struct_type == 0 and chosen_map.tiles[
                        n].structure_on.health > 0:
                        cur_tile_photo = rt_photo

                # Draw red tile
                curTile = canvas.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW,
                                              image=cur_tile_photo)
                tile_arr.append(curTile)

            # find all points to attack all enemies from, fill canvas.drag_data['targets_and_tiles']

            if cur_hero.weapon is not None:
                for m in moves_obj_array:
                    atk_arr = get_attack_tiles(m.destination, cur_hero.weapon.range)
                    for n in atk_arr:

                        # Hero in range
                        if chosen_map.tiles[n].hero_on is not None and chosen_map.tiles[
                            n].hero_on.side != cur_hero.side:

                            if chosen_map.tiles[n].hero_on not in canvas.drag_data['targets_and_tiles']:
                                canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on] = [m.destination]

                            if m.destination not in canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on]:
                                canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on].append(m.destination)

                        # Destroyable structure in range
                        elif chosen_map.tiles[n].structure_on is not None:
                            if chosen_map.tiles[n].structure_on.struct_type == 0 and chosen_map.tiles[
                                n].structure_on.health > 0:

                                if chosen_map.tiles[n].structure_on not in canvas.drag_data['targets_and_tiles']:
                                    canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].structure_on] = [
                                        m.destination]

                                if m.destination not in canvas.drag_data['targets_and_tiles'][
                                    chosen_map.tiles[n].structure_on]:
                                    canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].structure_on].append(
                                        m.destination)

            possible_assist_tile_nums = []

            confirmed_assists = []
            unconfirmed_assists = []

            if cur_hero.assist is not None and not (canto is not None and canto == cur_hero) and not swap_mode:
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

                                    no_one_on = chosen_map.tiles[move_ally_to].hero_on is None or chosen_map.tiles[
                                        move_ally_to].hero_on == cur_hero
                                    someone_on = not no_one_on

                                    ally_is_tile_accessable = can_be_on_tile(chosen_map.tiles[move_ally_to],
                                                                             chosen_map.tiles[
                                                                                 n].hero_on.move) and not someone_on
                                    valid_ally_cond = move_ally_to != -1 and ally_is_tile_accessable

                                elif "draw" in cur_hero.assist.effects:
                                    move_unit_to = final_reposition_tile(m.destination, n)
                                    move_ally_to = m.destination

                                    ally = chosen_map.tiles[n].hero_on

                                    no_one_on = chosen_map.tiles[move_unit_to].hero_on is None or chosen_map.tiles[
                                        move_unit_to].hero_on == cur_hero

                                    no_one_on_ally = chosen_map.tiles[move_ally_to].hero_on is None or chosen_map.tiles[
                                        move_ally_to].hero_on == cur_hero

                                    valid_unit_cond = can_be_on_tile(chosen_map.tiles[move_unit_to],
                                                                     cur_hero.move) and move_unit_to != -1 and no_one_on
                                    valid_ally_cond = can_be_on_tile(chosen_map.tiles[move_ally_to],
                                                                     ally.move) and move_ally_to != -1 and no_one_on_ally

                                elif "swap" in cur_hero.assist.effects:

                                    move_unit_to = n
                                    move_ally_to = m.destination

                                    valid_unit_cond = can_be_on_tile(chosen_map.tiles[move_unit_to], cur_hero.move)
                                    valid_ally_cond = can_be_on_tile(chosen_map.tiles[move_ally_to],
                                                                     chosen_map.tiles[move_unit_to].hero_on.move)

                                elif "pivot" in cur_hero.assist.effects:
                                    valid_ally_cond = True

                                    move_self_to = final_reposition_tile(n, m.destination)

                                    if move_self_to != -1:
                                        unit_on_dest = chosen_map.tiles[move_self_to].hero_on is not None and \
                                                       chosen_map.tiles[move_self_to].hero_on != cur_hero

                                        can_traverse_dest = can_be_on_tile(chosen_map.tiles[move_self_to], player.move)

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
                                        unit_on_dest = chosen_map.tiles[skip_over].hero_on is not None and \
                                                       chosen_map.tiles[skip_over].hero_on != cur_hero
                                        can_traverse_dest = can_be_on_tile(chosen_map.tiles[skip_over], ally.move)

                                        valid_shove = not unit_on_dest and can_traverse_dest

                                    if final_dest != -1:
                                        unit_on_dest = chosen_map.tiles[final_dest].hero_on is not None and \
                                                       chosen_map.tiles[final_dest].hero_on != cur_hero
                                        can_traverse_dest = can_be_on_tile(chosen_map.tiles[final_dest], ally.move)

                                        foe_on_skip = chosen_map.tiles[skip_over].hero_on is not None and \
                                                      chosen_map.tiles[skip_over].hero_on.side != cur_hero.side
                                        can_skip = chosen_map.tiles[skip_over].terrain != 4 and not foe_on_skip

                                        valid_smite = not unit_on_dest and can_traverse_dest and can_skip

                                    valid_ally_cond = valid_shove or valid_smite

                                elif "shove" in cur_hero.assist.effects:
                                    final_dest = final_reposition_tile(n, m.destination)
                                    valid_unit_cond = True

                                    ally = chosen_map.tiles[n].hero_on

                                    valid_shove = False
                                    if final_dest != -1:
                                        unit_on_dest = chosen_map.tiles[final_dest].hero_on is not None and \
                                                       chosen_map.tiles[final_dest].hero_on != cur_hero
                                        can_traverse_dest = can_be_on_tile(chosen_map.tiles[final_dest], ally.move)

                                        valid_shove = not unit_on_dest and can_traverse_dest

                                    valid_ally_cond = valid_shove

                            elif cur_hero.assist.type == "Staff":
                                if "heal" in cur_hero.assist.effects:
                                    valid_unit_cond = True

                                    ally = chosen_map.tiles[n].hero_on

                                    valid_ally_cond = ally.side == cur_hero.side and ally.HPcur != ally.visible_stats[
                                        HP]

                            elif cur_hero.assist.type == "Rally":
                                valid_unit_cond = True

                                given_stats = [0, 0, 0, 0]
                                if "rallyAtk" in cur_hero.assist.effects:
                                    given_stats[ATK - 1] += cur_hero.assist.effects["rallyAtk"]
                                if "rallySpd" in cur_hero.assist.effects:
                                    given_stats[SPD - 1] += cur_hero.assist.effects["rallySpd"]
                                if "rallyDef" in cur_hero.assist.effects:
                                    given_stats[DEF - 1] += cur_hero.assist.effects["rallyDef"]
                                if "rallyRes" in cur_hero.assist.effects:
                                    given_stats[RES - 1] += cur_hero.assist.effects["rallyRes"]

                                i = 0
                                while i < len(given_stats):
                                    ally = chosen_map.tiles[n].hero_on
                                    if given_stats[i] > ally.buffs[i + 1]:
                                        valid_ally_cond = True
                                    i += 1

                            elif cur_hero.assist.type == "Refresh":
                                valid_unit_cond = True

                                ally = chosen_map.tiles[n].hero_on
                                has_dance_cond = ally.assist is None or (
                                            ally.assist is not None and ally.assist.type != "Refresh")
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
                                elif "harsh_comm" in cur_hero.assist.effects:
                                    ally = chosen_map.tiles[n].hero_on

                                    valid_unit_cond = True
                                    valid_ally_cond = sum(ally.debuffs) < 0
                            else:
                                # big guy is a cheater
                                print("wonderhoy")

                            if valid_unit_cond and valid_ally_cond:

                                # add new target and tile
                                if chosen_map.tiles[n].hero_on not in canvas.drag_data['targets_and_tiles']:
                                    canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on] = [m.destination]

                                # give more tiles to target
                                if m.destination not in canvas.drag_data['targets_and_tiles'][
                                    chosen_map.tiles[n].hero_on]:
                                    canvas.drag_data['targets_and_tiles'][chosen_map.tiles[n].hero_on].append(
                                        m.destination)

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

            canvas.drag_data['arrow_path'] = []
            canvas.drag_data['attack_range'] = attack_range
            canvas.drag_data['assist_range'] = confirmed_assists

            # make starting path
            if not swap_mode:
                first_path = canvas.create_image(pixel_offset_x, pixel_offset_y, anchor=tk.NW, image=arrow_photos[14])
                canvas.tag_lower(first_path, item_id)

                canvas.drag_data['arrow_path'] = [first_path]

        else:
            canvas.drag_data = None

    def on_drag(event):
        global animation
        global canto
        global swap_mode

        if animation: return

        if not canvas.drag_data: return

        # Calculate the distance moved
        delta_x = event.x - canvas.drag_data['cur_x']
        delta_y = event.y - canvas.drag_data['cur_y']

        # unit's sprite
        item_index = canvas.drag_data['index']

        # unit's side
        S = canvas.drag_data['side']

        cur_hero: Hero = units_all[S][item_index]
        tag: str = tags_all[S][item_index]

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

        # Out of bounds, nothing else to do
        if event.x <= 0 or event.x >= 540 or event.y <= 90 or event.y >= 810:
            return

        # different tile and within moves
        # figure out the current path

        # sets path/final position to target a foe

        cur_tile_Obj = chosen_map.tiles[cur_tile_int]
        prev_tile_Obj = chosen_map.tiles[prev_tile_int]

        moved_to_different_tile = prev_tile_int != cur_tile_int

        # man do I want to use this
        cdd = canvas.drag_data

        # On drag, things should only update upon visiting a new tile
        if moved_to_different_tile:

            for x in aoe_special_icons_active:
                canvas.delete(x)
            aoe_special_icons_active.clear()

            # If moving onto a space with a Hero
            if cur_tile_Obj.hero_on is not None and cur_tile_Obj.hero_on != cur_hero:

                # Target is a foe within range
                if cur_tile_int in cdd['attack_range'] and cur_tile_Obj.hero_on.side != cur_hero.side:

                    # Default target
                    target_tile = cdd['targets_and_tiles'][cur_tile_Obj.hero_on][0]

                    # If a different tile has been visited that allows attack on target, set target from that tile instead
                    if cur_tile_Obj.hero_on in cdd['targets_most_recent_tile']:
                        target_tile = cdd['targets_most_recent_tile'][cur_tile_Obj.hero_on]

                    # Set the default path for visiting the target tile
                    cdd['target_path'] = cdd['paths'][cdd['moves'].index(target_tile)]
                    cdd['target_dest'] = target_tile

                    cdd['target'] = cur_tile_Obj.hero_on

                    if cur_hero.special is not None and cur_hero.special.type == "AOE" and cur_hero.specialCount == 0:
                        formation = cur_hero.special.effects["aoe_area"]
                        aoe_special_targets = aoe_tiles(cur_tile_int, formation)

                        for num in aoe_special_targets:
                            cur_special_image = canvas.create_image((0, 90), image=aoe_special_icon_photo,
                                                                    anchor="center")
                            move_to_tile(canvas, cur_special_image, num)
                            aoe_special_icons_active.append(cur_special_image)

                            player_status_img.append(cur_special_image)
                            canvas.tag_raise(tag)

                    cur_hero.attacking_tile = chosen_map.tiles[target_tile]

                    distance = abs(target_tile % 6 - cdd["start_x_comp"]) + abs(target_tile // 6 - cdd["start_y_comp"])

                    set_attack_forecast(cur_hero, cur_tile_Obj.hero_on, distance)


                # Target is an ally
                elif cur_tile_int in cdd['assist_range'] and cur_tile_Obj.hero_on.side == cur_hero.side:

                    # Default target
                    target_tile = canvas.drag_data['targets_and_tiles'][chosen_map.tiles[cur_tile_int].hero_on][0]

                    # If a different tile has been visited that allows assist on target
                    if chosen_map.tiles[cur_tile_int].hero_on in canvas.drag_data['targets_most_recent_tile']:
                        target_tile = canvas.drag_data['targets_most_recent_tile'][
                            chosen_map.tiles[cur_tile_int].hero_on]

                    # Get the default path for visiting the target tile
                    cdd['target_path'] = canvas.drag_data['paths'][canvas.drag_data['moves'].index(target_tile)]
                    cdd['target_dest'] = target_tile

                    cdd['target'] = cur_tile_Obj.hero_on

                    set_assist_forecast(cur_hero, chosen_map.tiles[cur_tile_int].hero_on)

                # Target is invalid (hero out of reach/no weapon/no assist)
                else:
                    canvas.drag_data['target_path'] = "NONE"
                    canvas.drag_data['target_dest'] = cur_tile_Obj

                    canvas.drag_data['target'] = None

                    set_banner(chosen_map.tiles[cur_tile_int].hero_on)

            # If moving onto a space with a destroyable structure
            elif cur_tile_Obj.structure_on is not None and cur_tile_Obj.structure_on.health > 0 and cur_tile_int in \
                    canvas.drag_data['attack_range']:

                target_tile = canvas.drag_data['targets_and_tiles'][chosen_map.tiles[cur_tile_int].structure_on][0]

                # If a different tile has been visited that allows assist on target
                if chosen_map.tiles[cur_tile_int].structure_on in canvas.drag_data['targets_most_recent_tile']:
                    target_tile = canvas.drag_data['targets_most_recent_tile'][
                        chosen_map.tiles[cur_tile_int].structure_on]

                # Get the default path for visiting the target tile
                canvas.drag_data['target_path'] = canvas.drag_data['paths'][
                    canvas.drag_data['moves'].index(target_tile)]
                canvas.drag_data['target_dest'] = target_tile

                canvas.drag_data['target'] = chosen_map.tiles[cur_tile_int].structure_on

                set_struct_forecast(cur_hero, chosen_map.tiles[cur_tile_int].structure_on)

            # If moving onto a space with nothing
            else:
                set_banner(cur_hero)
                canvas.drag_data['target'] = None
                canvas.drag_data['target_path'] = "NONE"

            # Create the string which represents the path

            # Valid position to valid position
            # should check if it is a warp move
            if cur_tile_int in canvas.drag_data['moves'] and prev_tile_int in canvas.drag_data['moves']:
                # Build from existing path

                new_tile_cost = get_tile_cost(chosen_map.tiles[cur_tile_int], cur_hero)
                canvas.drag_data['cost'] += new_tile_cost

                # Arrow can continue to grow only if within movement distance and if path does not contain starting point
                x_start_comp = canvas.drag_data['start_x_comp']
                y_start_comp = canvas.drag_data['start_y_comp']
                recalc_tile = int(x_start_comp + 6 * y_start_comp)

                spaces_allowed = allowed_movement(cur_hero)
                is_allowed = canvas.drag_data['cost'] <= spaces_allowed and cur_tile_int != recalc_tile

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

                # Path too long, remake with default path
                else:
                    canvas.drag_data['cur_path'] = canvas.drag_data['paths'][
                        canvas.drag_data['moves'].index(cur_tile_int)]

                    new_cost = 0
                    for c in canvas.drag_data['cur_path']:
                        if c == 'N': recalc_tile += 6
                        if c == 'S': recalc_tile -= 6
                        if c == 'E': recalc_tile += 1
                        if c == 'W': recalc_tile -= 1
                        new_cost += get_tile_cost(chosen_map.tiles[recalc_tile], cur_hero)

                    canvas.drag_data['cost'] = new_cost

            # Invalid position to valid position
            elif cur_tile_int in canvas.drag_data['moves'] and prev_tile_int not in canvas.drag_data['moves']:
                # Valid path removed, remake with default path

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

            # get the x/y components of the starting tile, start drawing path from here
            x_arrow_comp = canvas.drag_data['start_x_comp']
            y_arrow_comp = canvas.drag_data['start_y_comp']
            x_arrow_pivot = x_arrow_comp * 90
            y_arrow_pivot = (7 - y_arrow_comp) * 90 + 90

            # Clear the current arrow path
            for arrow in canvas.drag_data['arrow_path']:
                canvas.delete(arrow)
            canvas.drag_data['arrow_path'] = []

            # If currently targeting something, adjust path to go to tile to interact w/ object
            traced_path = canvas.drag_data['cur_path']
            if canvas.drag_data['target_path'] != "NONE":
                traced_path = canvas.drag_data['target_path']

            # draw the arrow path

            # recheck conditions
            if (cur_tile_int in canvas.drag_data['moves'] or canvas.drag_data['target_path'] != "NONE") and not swap_mode:
                if len(traced_path) == 0 or event.x > 539 or event.x < 0:
                    star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW,
                                               image=arrow_photos[MOVE_STAR])
                    canvas.drag_data['arrow_path'].append(star)
                    canvas.tag_lower(star, canvas.drag_data['item'])
                elif "WARP" in traced_path:
                    star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW,
                                               image=arrow_photos[MOVE_STAR])
                    canvas.drag_data['arrow_path'].append(star)
                    canvas.tag_lower(star, canvas.drag_data['item'])

                    final_tile_star_pos = cur_tile_int

                    if chosen_map.tiles[cur_tile_int].hero_on in canvas.drag_data['targets_and_tiles']:
                        final_tile_star_pos = canvas.drag_data['target_dest']

                    star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor='center',
                                               image=arrow_photos[MOVE_STAR])
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

                    first_arrow = canvas.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y,
                                                      anchor=tk.NW, image=arrow_photos[first_dir])
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
                        cur_element_2 = traced_path[i + 1]

                        if cur_element_1 == 'N' and cur_element_2 == 'N' or cur_element_1 == 'S' and cur_element_2 == 'S': cur_dir = 8
                        if cur_element_1 == 'E' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'W': cur_dir = 9

                        if cur_element_1 == 'N' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'S': cur_dir = 10
                        if cur_element_1 == 'N' and cur_element_2 == 'W' or cur_element_1 == 'E' and cur_element_2 == 'S': cur_dir = 11
                        if cur_element_1 == 'S' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'N': cur_dir = 12
                        if cur_element_1 == 'S' and cur_element_2 == 'W' or cur_element_1 == 'E' and cur_element_2 == 'N': cur_dir = 13

                        arrow_offset_x, arrow_offset_y = get_arrow_offsets(cur_dir)

                        cur_arrow = canvas.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y,
                                                        anchor=tk.NW, image=arrow_photos[cur_dir])
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

                    last_arrow = canvas.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y,
                                                     anchor=tk.NW, image=arrow_photos[last_dir])
                    canvas.drag_data['arrow_path'].append(last_arrow)
                    canvas.tag_lower(last_arrow, canvas.drag_data['item'])

            # draw move_star at start only if out of bounds
            elif cur_tile_int not in canvas.drag_data['moves'] and not swap_mode:
                if len(canvas.drag_data['arrow_path']) != 1:
                    for arrow in canvas.drag_data['arrow_path']:
                        canvas.delete(arrow)
                    canvas.drag_data['arrow_path'] = []

                star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=arrow_photos[MOVE_STAR])
                canvas.drag_data['arrow_path'].append(star)
                canvas.tag_lower(star, canvas.drag_data['item'])

            # For each potential target in range, set current tile as the most recent tile visited that the dragged unit can attack from
            for x in canvas.drag_data['targets_and_tiles']:
                if cur_tile_int in canvas.drag_data['targets_and_tiles'][x]:
                    canvas.drag_data['targets_most_recent_tile'][x] = cur_tile_int

            for t in canvas.drag_data['arrow_path']:
                canvas.tag_lower(t, cdd['item'])

            # End of function, set cur_tile stored in drag data to new tile
            canvas.drag_data['cur_tile'] = cur_tile_int

    # end of drag

    def on_release(event):
        global animation
        global canto
        global swap_mode

        if canvas.drag_data is not None:
            successful_move = False

            cdd = canvas.drag_data

            # Get tile position on release
            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90) + 1
            destination_tile = x_comp + y_comp * 6

            # Tile the unit is moved to
            release_tile = destination_tile

            # Tile unit is moved to, if targeting something
            if canvas.drag_data['target_path'] != "NONE":
                destination_tile = canvas.drag_data['target_dest']

            # Tile moved from
            x_start_comp = cdd['start_x_comp']
            y_start_comp = cdd['start_y_comp']
            recalc_tile = int(x_start_comp + 6 * y_start_comp)

            item_index = cdd['index']
            S = cdd['side']

            player = units_all[S][item_index]
            player_sprite = cdd['item']  # why do I need this
            grayscale_sprite = grayscale_IDs[S][item_index]
            weapon_icon_sprite = weapon_IDs[S][item_index]
            hp_label = hp_labels[S][item_index]
            sp_label = special_labels[S][item_index]
            hp_bar_fg = hp_bar_fgs[S][item_index]
            hp_bar_bg = hp_bar_bgs[S][item_index]

            within_bounds = 539 > event.x > 0 and 810 > event.y > 90

            # Set unit's final position
            if within_bounds and destination_tile in cdd['moves']:
                final_destination = destination_tile

                if destination_tile != recalc_tile or canvas.drag_data['target_path'] != "NONE":
                    successful_move = True

            else:
                final_destination = recalc_tile

            # Set sprite to new position
            move_to_tile(canvas, canvas.drag_data['item'], final_destination)
            move_to_tile(canvas, grayscale_sprite, final_destination)
            move_to_tile_wp(canvas, weapon_icon_sprite, final_destination)
            move_to_tile_hp(canvas, hp_label, final_destination)
            move_to_tile_sp(canvas, sp_label, final_destination)
            move_to_tile_fg_bar(canvas, hp_bar_fg, final_destination)
            move_to_tile_fg_bar(canvas, hp_bar_bg, final_destination)

            units_all[S][item_index].tile.hero_on = None
            units_all[S][item_index].tile = chosen_map.tiles[final_destination]
            chosen_map.tiles[final_destination].hero_on = units_all[S][item_index]

            # Delete all colored movement tiles
            for blue_tile_id in canvas.drag_data['tile_id_arr']:
                canvas.delete(blue_tile_id)
            canvas.drag_data['tile_id_arr'].clear()

            # Delete all arrows
            for arrow in canvas.drag_data['arrow_path']:
                canvas.delete(arrow)

            # Delete all AoE icons
            for aoe_icon in aoe_special_icons_active:
                canvas.delete(aoe_icon)
            aoe_special_icons_active.clear()

            # If off-board move, nothing else to do
            if not within_bounds: return

            # do i need this
            player_original = chosen_map.tiles[destination_tile].hero_on

            was_action_performed = False

            galeforce_triggered = False
            canto_triggered = False

            # unit_tile = chosen_map.tiles[new_tile].hero_on
            # target_tile = chosen_map.tiles[mouse_new_tile].hero_on

            destination_unit = chosen_map.tiles[destination_tile].hero_on # the unit going to the destination, usually to interact w/ dest unit
            release_unit = chosen_map.tiles[release_tile].hero_on # the unit on the tile being hovered over by the mouse

            # Swap Allies if in swap mode
            if swap_mode and player.isAllyOf(release_unit):
                ally = release_unit

                unit_final_position = ally.tile.tileNum
                ally_final_position = player.tile.tileNum

                player.tile.hero_on = None
                ally.tile.hero_on = None

                player.tile = chosen_map.tiles[unit_final_position]
                ally.tile = chosen_map.tiles[ally_final_position]

                chosen_map.tiles[unit_final_position].hero_on = player
                chosen_map.tiles[ally_final_position].hero_on = ally

                update_unit_graphics(player)
                update_unit_graphics(ally)

                canvas.drag_data = None

                return

            ATTACK = 0
            ASSIST = 1
            BREAK = 2
            MOVE = 3

            action = -1

            finish_time = 0

            def hide_player(is_alive):

                canvas.itemconfig(player_sprite, state='hidden')
                canvas.itemconfig(grayscale_sprite, state='normal')

                if not is_alive:
                    canvas.itemconfig(player_sprite, state='hidden')
                    canvas.itemconfig(grayscale_sprite, state='hidden')
                    canvas.itemconfig(weapon_icon_sprite, state='hidden')
                    canvas.itemconfig(player_sprite, state='hidden')
                    #move_to_tile(canvas, player_sprite, 100)
                    #move_to_tile(canvas, grayscale_sprite, 100)

                    canvas.itemconfig(hp_label, state='hidden')
                    canvas.itemconfig(sp_label, state='hidden')
                    canvas.itemconfig(hp_bar_bg, state='hidden')
                    canvas.itemconfig(hp_bar_fg, state='hidden')

            # ATTAAAAAAAAAAAAAAAAAAAAAAACK!!!!!!!!!!!!!!!!!!

            # make grayscale not happen if canto triggers, enable grayscale through other means?

            if cdd['target_path'] != "NONE" and release_unit is not None and destination_unit.side != release_unit.side:
                # Begin initiating an attack animation
                animation = True

                was_action_performed = True
                action = ATTACK

                player = destination_unit
                enemy = release_unit

                player_tile = destination_tile
                enemy_tile = release_tile

                # Using unit and foe's positioning, figure out which direction to shift while attacking
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

                # ew lets rewrite this
                E_side = enemy.side

                enemy_index = units_all[E_side].index(enemy)
                enemy_sprite = sprite_IDs[E_side][enemy_index]
                enemy_weapon_icon = weapon_IDs[E_side][enemy_index]
                enemy_hp_label = hp_labels[E_side][enemy_index]
                enemy_sp_label = special_labels[E_side][enemy_index]
                this_enemy_hp_bar_fg = hp_bar_fgs[E_side][enemy_index]
                this_enemy_hp_bar_bg = hp_bar_bgs[E_side][enemy_index]

                def hide_enemy(is_alive):

                    canvas.itemconfig(enemy_sprite, state='hidden')
                    canvas.itemconfig(grayscale_sprite, state='normal')

                    if not is_alive:
                        canvas.itemconfig(grayscale_sprite, state='hidden')
                        canvas.itemconfig(enemy_weapon_icon, state='hidden')
                        # move_to_tile(canvas, enemy_sprite, 100)

                        canvas.itemconfig(enemy_hp_label, state='hidden')
                        canvas.itemconfig(enemy_sp_label, state='hidden')
                        canvas.itemconfig(this_enemy_hp_bar_bg, state='hidden')
                        #canvas.itemconfig(this_enemy_hp_bar_fg, state='hidden')

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

                distance = abs(player_tile % 6 - cdd["start_x_comp"]) + abs(player_tile // 6 - cdd["start_y_comp"])
                canvas.distance = distance

                # Simulate combat
                combat_result = simulate_combat(player, enemy, True, turn_info[0], distance, combat_fields, aoe_present)
                attacks = combat_result[7]

                player.unitCombatInitiates += 1
                enemy.unitCombatInitiates += 1

                # Perform burn damage
                burn_damages = combat_result[14]

                burn_present = 0
                if burn_damages[0] > 0 or burn_damages[1] > 0:
                    burn_present = 500

                    if burn_damages[0] > 0:
                        enemy.HPcur = max(1, enemy.HPcur - burn_damages[0])
                        canvas.after(300 + aoe_present, set_hp_visual, enemy, enemy.HPcur)
                        canvas.after(300 + aoe_present, animate_damage_popup, canvas, burn_damages[0], enemy_tile)

                    if burn_damages[1] > 0:
                        player.HPcur = max(1, player.HPcur - burn_damages[1])
                        canvas.after(300 + aoe_present, set_hp_visual, player, player.HPcur)
                        canvas.after(300 + aoe_present, animate_damage_popup, canvas, burn_damages[1], player_tile)

                # Visualization of the blows trading
                i = 0
                while i < len(attacks):
                    move_time = i * 500 + 200 + aoe_present + burn_present
                    impact_time = i * 500 + 300 + aoe_present + burn_present

                    if attacks[i].attackOwner == 0:

                        # Move player sprite
                        canvas.after(move_time, animate_sprite_atk, canvas, player_sprite, player_atk_dir_hori,
                                     player_atk_dir_vert, attacks[i].damage, enemy_tile)

                        # Heal player, get to enemy side soon
                        if attacks[i].healed > 0:
                            canvas.after(impact_time, animate_heal_popup, canvas, attacks[i].healed, player_tile)

                        # Damage enemy
                        enemy.HPcur = max(0, enemy.HPcur - attacks[i].damage)
                        canvas.after(impact_time, set_text_val, enemy_hp_label, enemy.HPcur)

                        # Update each player's health visually
                        hp_percentage = enemy.HPcur / enemy.visible_stats[HP]
                        canvas.after(impact_time, set_hp_bar_length, this_enemy_hp_bar_fg, hp_percentage)

                        player.HPcur = min(player.visible_stats[HP], player.HPcur + attacks[i].healed)
                        canvas.after(impact_time, set_text_val, hp_label, player.HPcur)

                        hp_percentage = player.HPcur / player.visible_stats[HP]
                        canvas.after(impact_time, set_hp_bar_length, hp_bar_fg, hp_percentage)

                    if attacks[i].attackOwner == 1:
                        canvas.after(move_time, animate_sprite_atk, canvas, enemy_sprite, player_atk_dir_hori * -1,
                                     player_atk_dir_vert * -1, attacks[i].damage, player_tile)

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

                finish_time = 500 * (i + 1) + 200 + aoe_present + burn_present

                atk_effects = combat_result[12]
                def_effects = combat_result[13]

                # Clear debuffs before administering post combat effects
                player.statusNeg = []
                player.debuffs = [0, 0, 0, 0, 0]

                damage_taken, heals_given, sp_charges = end_of_combat(atk_effects, def_effects, player, enemy)

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

                    if x in sp_charges:
                        x.chargeSpecial(sp_charges[x])

                    x_side = x.side
                    x_index = units_all[x_side].index(x)
                    x_hp_label = hp_labels[x_side][x_index]
                    x_hp_bar = hp_bar_fgs[x_side][x_index]
                    x_sp_label = special_labels[x_side][x_index]

                    hp_percentage = x.HPcur / x.visible_stats[HP]

                    if x.specialCount != -1:
                        canvas.after(finish_time, set_text_val, x_sp_label, x.specialCount)

                    canvas.after(finish_time, set_text_val, x_hp_label, x.HPcur)
                    canvas.after(finish_time, set_hp_bar_length, x_hp_bar, hp_percentage)

                # movement-based skills after combat
                player_tile_number = player.tile.tileNum
                enemy_tile_number = enemy.tile.tileNum

                player_move_pos = player_tile_number
                enemy_move_pos = enemy_tile_number

                if "knock_back" in player.getSkills():
                    player_move_pos = player_tile_number
                    enemy_move_pos = final_reposition_tile(enemy_tile_number, player_tile_number)

                    if not (chosen_map.tiles[enemy_move_pos].hero_on is None and can_be_on_tile(
                            chosen_map.tiles[enemy_move_pos], enemy.move)):
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

                # ensure tiles do not have any heroes/structures/invalid terrain
                if player_move_pos != -1 and enemy_move_pos != -1 and player.HPcur != 0:
                    if chosen_map.tiles[player_move_pos].hero_on != None and (
                            chosen_map.tiles[player_move_pos].hero_on != player and chosen_map.tiles[
                        player_move_pos].hero_on != enemy):
                        player_move_pos = -1
                    elif chosen_map.tiles[enemy_move_pos].hero_on != None and (
                            chosen_map.tiles[enemy_move_pos].hero_on != player and chosen_map.tiles[
                        enemy_move_pos].hero_on != enemy):
                        enemy_move_pos = -1
                    elif not can_be_on_tile(chosen_map.tiles[player_move_pos], player.move):
                        player_move_pos = -1
                    elif not can_be_on_tile(chosen_map.tiles[enemy_move_pos], player.move):
                        enemy_move_pos = -1

                # tiles are still valid, make moves
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

                # If the dragged unit dies in combat, remove them from the map
                if player.HPcur == 0:
                    canvas.after(finish_time, hide_player, False)

                    # remove from list of units
                    if chosen_map.tiles[destination_tile].hero_on.side == 0: player_units.remove(
                        chosen_map.tiles[destination_tile].hero_on)
                    if chosen_map.tiles[destination_tile].hero_on.side == 1: enemy_units.remove(
                        chosen_map.tiles[destination_tile].hero_on)

                    # take unit off map
                    player.tile.hero_on = None

                    # end simulation if they were last unit alive
                    if player.side == 0 and not player_units:
                        canvas.after(finish_time + 700, window.destroy)

                    if player.side == 1 and not enemy_units:
                        canvas.after(finish_time + 700, window.destroy)

                    canvas.after(finish_time, clear_banner)
                else:
                    # Switch banner back to them
                    canvas.after(finish_time, set_banner, player)

                # If the foe dies in combat, remove them from the map
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

                # After animation complete. re-enable user control
                canvas.after(finish_time, animation_done)

                # Visuals for special galeforce triggering
                '''
                if not galeforce_triggered and not canto_triggered:
                    canvas.after(finish_time, hide_player, True) # grayscales unit
                else:
                    canvas.after(finish_time, set_text_val, sp_label, player.specialCount) # reset special count display
                '''

            # DESTROOOOOOOOOOOOOOOOYYYY!!!!!!!!!!!!!!!!!
            elif canvas.drag_data['target_path'] != "NONE" and release_unit is None and \
                    chosen_map.tiles[release_tile].structure_on is not None and chosen_map.tiles[
                release_tile].structure_on.health > 0:

                was_action_performed = True
                action = BREAK

                # Break selected wall
                chosen_map.tiles[release_tile].structure_on.health -= 1

                # Refresh all walls
                refresh_walls()

                # Record distance traveled
                player_tile = destination_tile

                distance = abs(player_tile % 6 - cdd["start_x_comp"]) + abs(player_tile // 6 - cdd["start_y_comp"])
                canvas.distance = distance

            # ASSIIIIIIIIIIIIIIIIIIIIIIST!!!!!!!!!!!!!!!!!!!!
            elif canvas.drag_data['target_path'] != "NONE" and chosen_map.tiles[release_tile].hero_on is not None and \
                    chosen_map.tiles[destination_tile].hero_on.side == chosen_map.tiles[release_tile].hero_on.side:
                was_action_performed = True
                action = ASSIST

                player = destination_unit
                ally = release_unit

                player_tile = destination_tile

                # Distance
                distance = abs(player_tile % 6 - cdd["start_x_comp"]) + abs(player_tile // 6 - cdd["start_y_comp"])
                canvas.distance = distance

                ally_index = units_all[S].index(ally)

                ally_sprite = sprite_IDs[S][ally_index]
                ally_grayscale = grayscale_IDs[S][ally_index]
                ally_weapon_icon = weapon_IDs[S][ally_index]
                ally_hp_label = hp_labels[S][ally_index]
                ally_sp_label = special_labels[S][ally_index]
                ally_hp_bar_fg = hp_bar_fgs[S][ally_index]
                ally_hp_bar_bg = hp_bar_bgs[S][ally_index]

                unit_final_position = -1
                ally_final_position = -1

                if "repo" in player.assist.effects:

                    # Tiles currently occupied by unit and ally
                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    # Where each unit is moving to
                    unit_final_position = player.tile.tileNum
                    ally_final_position = final_reposition_tile(unit_tile_num, ally_tile_num)

                elif "draw" in player.assist.effects:
                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    unit_final_position = final_reposition_tile(unit_tile_num, ally_tile_num)
                    ally_final_position = unit_tile_num

                elif "swap" in player.assist.effects:
                    unit_final_position = player.tile.tileNum
                    ally_final_position = ally.tile.tileNum

                elif "pivot" in player.assist.effects:
                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    ally_final_position = ally.tile.tileNum
                    unit_final_position = final_reposition_tile(ally_tile_num, unit_tile_num)

                elif "smite" in player.assist.effects:
                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    skip_over = final_reposition_tile(ally_tile_num, unit_tile_num)
                    final_dest = final_reposition_tile(skip_over, ally_tile_num)

                    valid_shove = False
                    valid_smite = False

                    if skip_over != -1:
                        unit_on_dest = chosen_map.tiles[skip_over].hero_on is not None and chosen_map.tiles[
                            skip_over].hero_on != player
                        can_traverse_dest = can_be_on_tile(chosen_map.tiles[skip_over], ally.move)

                        valid_shove = not unit_on_dest and can_traverse_dest

                    if final_dest != -1:
                        unit_on_dest = chosen_map.tiles[final_dest].hero_on is not None and chosen_map.tiles[
                            final_dest].hero_on != player
                        can_traverse_dest = can_be_on_tile(chosen_map.tiles[final_dest], ally.move)

                        foe_on_skip = chosen_map.tiles[skip_over].hero_on is not None and chosen_map.tiles[
                            skip_over].hero_on.side != player.side
                        can_skip = chosen_map.tiles[skip_over].terrain != 4 and not foe_on_skip

                        valid_smite = not unit_on_dest and can_traverse_dest and can_skip

                    final_pos = -1
                    if valid_shove and not valid_smite:
                        final_pos = skip_over
                    if valid_smite:
                        final_pos = final_dest

                    unit_final_position = player.tile.tileNum
                    ally_final_position = final_pos

                elif "shove" in player.assist.effects:
                    unit_tile_num = player.tile.tileNum
                    ally_tile_num = ally.tile.tileNum

                    unit_final_position = player.tile.tileNum
                    ally_final_position = final_reposition_tile(ally_tile_num, unit_tile_num)

                # Staff Healing
                elif "heal" in player.assist.effects:
                    unit_final_position = player.tile.tileNum
                    ally_final_position = ally.tile.tileNum

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
                        hp_healed_self = dmg_taken // 2

                    # Martyr+
                    if player.assist.effects["heal"] == -49:
                        dmg_taken = player.visible_stats[HP] - player.HPcur
                        hp_healed_ally = max(dmg_taken + self_atk_stat // 2, 7)
                        hp_healed_self = dmg_taken // 2

                    # Recover+
                    if player.assist.effects["heal"] == -10:
                        hp_healed_ally = max(self_atk_stat // 2 + 10, 15)

                    # Rehabilitate
                    if player.assist.effects["heal"] == -1:
                        ally_hp_max = ally.visible_stats[HP]
                        ally_hp_cur = ally.HPcur

                        hp_healed_ally = max(7 + ally_hp_max - (2 * ally_hp_cur), 7)

                    # Rehabilitate+
                    if player.assist.effects["heal"] == -2:
                        ally_hp_max = ally.visible_stats[HP]
                        ally_hp_cur = ally.HPcur

                        hp_healed_ally = max(self_atk_stat // 2 - 10, 7) + max(ally_hp_max - (2 * ally_hp_cur), 0)

                    if player.assist.effects["heal"] == -50:
                        hp_healed_ally = max(self_atk_stat // 2, 8)

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

                # Dance/Sing/Play
                elif "refresh" in player.assist.effects:
                    unit_final_position = player.tile.tileNum
                    ally_final_position = ally.tile.tileNum

                    # Grant ally another action
                    units_to_move.append(ally)

                    ally_index = units_all[S].index(ally)
                    ally_sprite = sprite_IDs[S][ally_index]
                    ally_gs_sprite = grayscale_IDs[S][ally_index]

                    canvas.itemconfig(ally_sprite, state='normal')
                    canvas.itemconfig(ally_gs_sprite, state='hidden')

                # Rally
                if "rallyAtk" in player.assist.effects:
                    ally.inflictStat(ATK, player.assist.effects["rallyAtk"])
                if "rallySpd" in player.assist.effects:
                    ally.inflictStat(SPD, player.assist.effects["rallySpd"])
                if "rallyDef" in player.assist.effects:
                    ally.inflictStat(DEF, player.assist.effects["rallyDef"])
                if "rallyRes" in player.assist.effects:
                    ally.inflictStat(RES, player.assist.effects["rallyRes"])

                # Reciprocal Aid
                if "rec_aid" in player.assist.effects:
                    unit_final_position = player.tile.tileNum
                    ally_final_position = ally.tile.tileNum

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

                # Ardent Sacrifice
                if "ardent_sac" in player.assist.effects:
                    unit_final_position = player.tile.tileNum
                    ally_final_position = ally.tile.tileNum

                    ally.HPcur = min(ally.visible_stats[HP], ally.HPcur + 10)
                    player.HPcur = max(1, player.HPcur - 10)

                    animate_heal_popup(canvas, 10, ally.tile.tileNum)
                    animate_damage_popup(canvas, 10, player.tile.tileNum)

                    set_hp_visual(player, player.HPcur)
                    set_hp_visual(ally, ally.HPcur)

                # Harsh Command
                if "harsh_comm" in player.assist.effects:
                    unit_final_position = player.tile.tileNum
                    ally_final_position = ally.tile.tileNum

                    i = 1
                    while i < len(ally.debuffs):
                        ally.buffs[i] = max(abs(ally.debuffs[i]), ally.buffs[i])
                        ally.debuffs[i] = 0
                        i += 1

                # Perform assist movements
                if unit_final_position != -1 and ally_final_position != -1:
                    player.tile.hero_on = None
                    ally.tile.hero_on = None

                    player.tile = chosen_map.tiles[unit_final_position]
                    ally.tile = chosen_map.tiles[ally_final_position]

                    chosen_map.tiles[unit_final_position].hero_on = player
                    chosen_map.tiles[ally_final_position].hero_on = ally

                    move_to_tile(canvas, player_sprite, unit_final_position)
                    move_to_tile(canvas, grayscale_sprite, unit_final_position)
                    move_to_tile_wp(canvas, weapon_icon_sprite, unit_final_position)
                    move_to_tile_hp(canvas, hp_label, unit_final_position)
                    move_to_tile_sp(canvas, sp_label, unit_final_position)
                    move_to_tile_fg_bar(canvas, hp_bar_fg, unit_final_position)
                    move_to_tile_fg_bar(canvas, hp_bar_bg, unit_final_position)

                    move_to_tile(canvas, ally_sprite, ally_final_position)
                    move_to_tile(canvas, ally_grayscale, ally_final_position)
                    move_to_tile_wp(canvas, ally_weapon_icon, ally_final_position)
                    move_to_tile_hp(canvas, ally_hp_label, ally_final_position)
                    move_to_tile_sp(canvas, ally_sp_label, ally_final_position)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_fg, ally_final_position)
                    move_to_tile_fg_bar(canvas, ally_hp_bar_bg, ally_final_position)

                # Clear status effects, action taken
                player.statusNeg = []
                player.debuffs = [0, 0, 0, 0, 0]
                set_banner(player)

                # Skills that grant effects when assist skills are used

                # Link skills
                if player.assist.type == "Move":
                    playerSkills = player.getSkills()
                    allySkills = ally.getSkills()

                    if "atkSpdLinkW" in playerSkills or "atkSpdLinkW" in allySkills:
                        affected_units = [player, ally]

                        for hero in affected_units:
                            hero.inflictStat(ATK, 6)
                            hero.inflictStat(SPD, 6)

                    if "laslowShmovement" in playerSkills or "laslowShmovement" in allySkills:
                        affected_units = [player, ally]
                        affected_units += allies_within_n(player, 2)
                        affected_units += allies_within_n(ally, 2)

                        affected_units = list(set(affected_units))

                        for hero in affected_units:
                            hero.inflictStat(ATK, 4)
                            hero.inflictStat(SPD, 4)
                            hero.inflictStat(DEF, 4)
                            hero.inflictStat(RES, 4)

            # DO NOTHIIIIIIIIIIIIIIING!!!!!
            if not was_action_performed and successful_move:
                player_tile = destination_tile

                distance = abs(player_tile % 6 - cdd["start_x_comp"]) + abs(player_tile // 6 - cdd["start_y_comp"])
                canvas.distance = distance

                action = MOVE

            # If any action was taken, manage those things here
            if action != -1:

                # Clears debuffs if no action has occured, or
                if action != ATTACK and action != ASSIST:
                    player.statusNeg = []
                    player.debuffs = [0, 0, 0, 0, 0]

                set_banner(player)

                if action != MOVE and not galeforce_triggered and player.canto_ready:

                    canto_moves = \
                    get_canto_moves(player, units_all[player.side], units_all[int(not player.side)], canvas.distance,
                                    canvas.spaces_allowed, turn_info[0])[2]

                    # If there are any valid tiles to use Canto to, activate canto mode
                    if canto_moves:
                        canto = player
                        player.canto_ready = False

                        canvas.itemconfig(swap_spaces, fill="#282424")
                        canvas.itemconfig(swap_spaces_text, fill="#282424")

                        # Canto officially burned
                        # Canto Control goes here

                        # Draw Blue Spaces

                        moves_obj_array = \
                        get_canto_moves(player, units_all[player.side], units_all[int(not player.side)],
                                        canvas.distance, canvas.spaces_allowed, turn_info[0])[2]

                        for m in moves_obj_array:
                            x_comp = m.destination % 6
                            y_comp = m.destination // 6
                            cur_pixel_offset_x = x_comp * 90
                            cur_pixel_offset_y = (7 - y_comp) * 90 + 90

                            tile_photo = bt_photo
                            if m.is_warp:
                                tile_photo = lbt_photo

                            # creates new blue tile, layered under player
                            def create_tile(x1, y1, z1):

                                curTile = canvas.create_image(x1, y1, anchor=tk.NW, image=z1)
                                canvas.canto_tile_imgs.append(curTile)
                                canvas.tag_lower(curTile, item_id)

                            x1 = cur_pixel_offset_x
                            y1 = cur_pixel_offset_y
                            z1 = tile_photo
                            canvas.after(finish_time, create_tile, x1, y1, z1)

                            '''
                            curTile = canvas.create_image(cur_pixel_offset_x, cur_pixel_offset_y, anchor=tk.NW, image=tile_photo)
                            canvas.canto_tile_imgs.append(curTile)
                            canvas.tag_lower(curTile, item_id)
                            '''

                elif not player.canto_ready:
                    canto = None

                    for blue_tile_id in canvas.canto_tile_imgs:
                        canvas.delete(blue_tile_id)
                    canvas.canto_tile_imgs.clear()

            cur_hero = player
            units_all[S][item_index].attacking_tile = None

            # Add current move to mapstate history
            # if successful_move and cur_hero in units_to_move:

            # remove player unit from units who can act
            if successful_move and cur_hero in units_to_move and not galeforce_triggered and canto is None:
                units_to_move.remove(cur_hero)

                if units_to_move:
                    canvas.after(finish_time, hide_player, True)

                    mapstate = create_mapstate(player_units_all, enemy_units_all, chosen_map, units_to_move,
                                               turn_info[0])
                    map_states.append(mapstate)

                    if len(map_states) > 1:
                        canvas.itemconfig(swap_spaces, fill="#282424")
                        canvas.itemconfig(swap_spaces_text, fill="#282424")

                '''
                if cur_hero.side == 0 and not animation:
                    canvas.itemconfig(grayscale_player_sprite_IDs[item_index], state='normal')
                    canvas.itemconfig(player_sprite_IDs[item_index], state='hidden')

                if cur_hero.side == 1 and not animation:
                    canvas.itemconfig(grayscale_enemy_sprite_IDs[item_index], state='normal')
                    canvas.itemconfig(enemy_sprite_IDs[item_index], state='hidden')
                '''

            # cause next phase to start either immediately or after combat
            if not units_to_move:
                if not animation:
                    next_phase()

                if animation:
                    canvas.after(finish_time, next_phase)

            canvas.drag_data = None

    def on_double_click(event):
        global animation
        global canto
        global swap_mode

        if animation: return

        x, y = event.x, event.y

        # End turn button
        if x > 380 and y > 820 and x < 450 and y < 900 and not swap_mode:
            next_phase()

            canto = None

            for blue_tile_id in canvas.canto_tile_imgs:
                canvas.delete(blue_tile_id)
            canvas.canto_tile_imgs.clear()

            return

        if 460 < x < 530 and 820 < y < 900 and len(map_states) == 1 and canto is None:
            toggle_swap()
            return

        # Undo button
        if 10 < x < 80 and 820 < y < 900 and not swap_mode:

            if len(map_states) > 1:
                if not canto:
                    map_states.pop()
                apply_mapstate(map_states[-1])
            else:
                apply_mapstate(map_states[0])

            if len(map_states) == 1:
                canvas.itemconfig(swap_spaces_text, fill="#5e5b03")
                canvas.itemconfig(swap_spaces, fill="#75f216")

        if x < 0 or x > 540 or y <= 90 or y > 810:
            return

        x_comp = event.x // 90
        y_comp = ((720 - event.y) // 90) + 1
        selected_tile = x_comp + 6 * y_comp
        cur_hero = chosen_map.tiles[selected_tile].hero_on

        if cur_hero is not None and not swap_mode:

            S = cur_hero.side

            if S == turn_info[1]:
                item_index = units_all[S].index(cur_hero)
                if cur_hero in units_to_move:
                    units_to_move.remove(cur_hero)

                    cur_hero.statusNeg = []
                    cur_hero.debuffs = [0, 0, 0, 0, 0]
                    set_banner(cur_hero)

                    if cur_hero == canto:
                        canto = None

                        for blue_tile_id in canvas.canto_tile_imgs:
                            canvas.delete(blue_tile_id)
                        canvas.canto_tile_imgs.clear()

                    if S == PLAYER:
                        canvas.itemconfig(grayscale_player_sprite_IDs[item_index], state='normal')
                        canvas.itemconfig(player_sprite_IDs[item_index], state='hidden')
                    if S == ENEMY:
                        canvas.itemconfig(grayscale_enemy_sprite_IDs[item_index], state='normal')
                        canvas.itemconfig(enemy_sprite_IDs[item_index], state='hidden')

                    if not units_to_move:
                        next_phase()

                    else:
                        mapstate = create_mapstate(player_units_all, enemy_units_all, chosen_map, units_to_move,
                                                   turn_info[0])

                        map_states.append(mapstate)

    def set_text_val(label, value):
        canvas.itemconfig(label, text=value)

    def set_hp_bar_length(rect, percent):
        new_length = int(60 * percent)

        if new_length == 0:
            canvas.itemconfig(rect, state='hidden')
            return

        coords = canvas.coords(rect)

        coords[2] = coords[0] + new_length

        canvas.coords(rect, coords)

    def set_hp_visual(unit, cur_HP):
        S = unit.side
        unit_index = units_all[S].index(unit)
        unit_hp_label = hp_labels[S][unit_index]
        unit_hp_bar = hp_bar_fgs[S][unit_index]

        hp_percentage = cur_HP / unit.visible_stats[HP]

        set_text_val(unit_hp_label, cur_HP)
        set_hp_bar_length(unit_hp_bar, hp_percentage)

    # Window packing

    tile_size = 90
    window_length = tile_size * 10
    window_width = tile_size * 6

    window = tk.Tk()
    window.title('FEH Sim')
    window.geometry(str(window_width) + "x" + str(window_length))  # tile size: 90x90
    # window.iconbitmap(__location__ + "\\Sprites\\Marth.ico")

    frame = tk.Frame(window, bg="#282424")
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame, width=window_width, height=window_length, bg="#282424", highlightthickness=0)

    canvas.drag_data = None
    canvas.distance = 0  # cache of movement distances
    canvas.spaces_allowed = 0
    canvas.canto_tile_imgs = []

    canvas.pack()

    # SPRITE LOADING

    # liquid
    liquid_image = Image.open(__location__ + "/CombatSprites/" + chosen_map.liquid_texture)
    liquid_photo = ImageTk.PhotoImage(liquid_image)
    canvas.create_image(0, 90, anchor=tk.NW, image=liquid_photo)
    canvas.create_image(0, 90 * 3, anchor=tk.NW, image=liquid_photo)

    # map

    map_image = Image.open("Maps/Arena Maps/" + map_str + ".png")
    map_photo = ImageTk.PhotoImage(map_image)
    canvas.create_image(0, 90, anchor=tk.NW, image=map_photo)

    # walls

    wall_texture = Image.open(__location__ + "/CombatSprites/" + chosen_map.wall_texture)
    wall_photos = []
    walls_placed = []

    wall_crops = {
        0: (1639, 1, 1818, 180),
        1: (1093, 547, 1272, 726),
        2: (1, 729, 180, 908),
        3: (547, 1, 726, 180),
        4: (547, 729, 726, 908),
        5: (547, 547, 726, 726),
        6: (547, 365, 726, 544),
        7: (547, 183, 726, 362),
        8: (1093, 729, 1272, 908),
        9: (1, 547, 180, 726),
        10: (1093, 365, 1272, 544),
        11: (1093, 183, 1272, 362),
        12: (1, 1, 180, 180),
        13: (1093, 1, 1272, 180),
        14: (1, 183, 180, 362),
        15: (1, 365, 180, 544)
    }

    def refresh_walls():
        wall_photos.clear()
        walls_placed.clear()

        for tile in chosen_map.tiles:
            if tile.structure_on is not None:

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

                img = canvas.create_image(90, 90, anchor=tk.CENTER, image=cur_photo)

                wall_photos.append(cur_photo)
                walls_placed.append(img)

                move_to_tile(canvas, img, tile.tileNum)

    refresh_walls()

    # move tiles
    blue_tile = Image.open(__location__ + "/CombatSprites/" + "tileblue" + ".png")
    bt_photo = ImageTk.PhotoImage(blue_tile)

    light_blue_tile = Image.open(__location__ + "/CombatSprites/" + "tilelightblue" + ".png")
    lbt_photo = ImageTk.PhotoImage(light_blue_tile)

    red_tile = Image.open(__location__ + "/CombatSprites/" + "tilered" + ".png")
    rt_photo = ImageTk.PhotoImage(red_tile)

    pale_red_tile = Image.open(__location__ + "/CombatSprites/" + "tilepalered" + ".png")
    prt_photo = ImageTk.PhotoImage(pale_red_tile)

    green_tile = Image.open(__location__ + "/CombatSprites/" + "tilegreen" + ".png")
    gt_photo = ImageTk.PhotoImage(green_tile)

    pale_green_tile = Image.open(__location__ + "/CombatSprites/" + "tilepalegreen" + ".png")
    pgt_photo = ImageTk.PhotoImage(pale_green_tile)

    # arrows
    arrows = Image.open(__location__ + "/CombatSprites/" + "Map" + ".png")
    arrow_photos = []

    START_NORTH = 0;
    START_SOUTH = 1;
    START_EAST = 2;
    START_WEST = 3
    END_NORTH = 4;
    END_SOUTH = 5;
    END_EAST = 6;
    END_WEST = 7
    LINE_VERT = 8;
    LINE_HORI = 9
    BEND_NE = 10;
    BEND_ES = 11;
    BEND_SE = 12;
    BEND_EN = 13
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
    skills1 = Image.open(__location__ + "/CombatSprites/" + "Skill_Passive1" + ".png")
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
    status_pic = Image.open(__location__ + "/CombatSprites/" + "Status" + ".png")

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
    # canvas.create_image((0, 90), image=aoe_special_icon_photo, anchor=tk.center)

    # turn order

    # cur turn #, cur phase, turn limit
    turn_info = [1, PLAYER, 50]
    units_to_move = player_units[:]

    # map history, memory of all moves in map states
    map_states = []

    phase_label = canvas.create_text((540 / 2, 830), text="PLAYER PHASE", fill="#038cfc", font=("Helvetica", 20),
                                     anchor='center')
    next_phase.phase_txt = phase_label

    turn_label = canvas.create_text((540 / 2, 860), text="Turn " + str(turn_info[0]) + "/" + str(turn_info[2]),
                                    fill="#97a8c4", font=("Helvetica", 16), anchor='center')
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

    i = 0
    for x in player_units_all:
        respString = "-R" if x.resp else ""
        curImage = Image.open(__location__ + "/TestSprites/" + x.intName + respString + ".png")
        # modifier = curImage.height/85
        # resized_image = curImage.resize((int(curImage.width / modifier), 85), Image.LANCZOS)
        resized_image = curImage.resize((int(curImage.width / 2.1), int(curImage.height / 2.1)), Image.LANCZOS)

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
        i += 1

    i = 0
    for x in enemy_units_all:
        respString = "-R" if x.resp else ""
        curImage = Image.open(__location__ + "/TestSprites/" + x.intName + respString + ".png")
        curImage = curImage.transpose(Image.FLIP_LEFT_RIGHT)
        # resized_image = curImage.resize((int(curImage.width / modifier), 85), Image.LANCZOS)
        resized_image = curImage.resize((int(curImage.width / 2.1), int(curImage.height / 2.1)), Image.LANCZOS)

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
        i += 1

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
        item_id = canvas.create_image(100 * i + 200, 200, anchor='center', image=grayscale_enemy_sprite,
                                      tags=enemy_tags[i])
        grayscale_enemy_sprite_IDs.append(item_id)

    for i, player in enumerate(player_units_all):

        w_image = weapon_icons[weapons[player.wpnType][0]]
        weapon_icon = canvas.create_image(160, 50 * (i + 2), anchor=tk.NW, image=w_image, tags=player_tags[i])
        player_weapon_icons.append(weapon_icon)

        count_string = player.specialCount
        if player.specialCount == -1: count_string = ""
        special_label = canvas.create_text(200, 100 * (2 + i), text=count_string, fill="#e300e3",
                                           font=("Helvetica", 19, 'bold'), anchor='center', tags=player_tags[i])
        player_special_count_labels.append(special_label)

        hp_string = player.HPcur
        hp_label = canvas.create_text(200, 100 * (2 + i), text=hp_string, fill="#3da7a8",
                                      font=("Helvetica", 16, 'bold'), anchor='center', tags=player_tags[i])
        player_hp_count_labels.append(hp_label)

        hp_bar_bg = canvas.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill='black', width=0,
                                            tags=player_tags[i])
        player_hp_bar_bg.append(hp_bar_bg)

        hp_bar_fg = canvas.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill='#3da7a8', width=0,
                                            tags=player_tags[i])
        player_hp_bar_fg.append(hp_bar_fg)

    for i, enemy in enumerate(enemy_units_all):

        w_image = weapon_icons[weapons[enemy.wpnType][0]]
        weapon_icon = canvas.create_image(160, 50 * (i + 2), anchor=tk.NW, image=w_image, tags=enemy_tags[i])
        enemy_weapon_icons.append(weapon_icon)

        count_string = enemy.specialCount
        if enemy.specialCount == -1: count_string = ""
        special_label = canvas.create_text(200, 100 * (2 + i), text=count_string, fill="#e300e3",
                                           font=("Helvetica", 19, 'bold'), anchor='center', tags=enemy_tags[i])
        enemy_special_count_labels.append(special_label)

        hp_string = enemy.HPcur
        hp_label = canvas.create_text(200, 100 * (2 + i), text=hp_string, fill="#ed1139",
                                      font=("Helvetica", 16, 'bold'), anchor='center', tags=enemy_tags[i])
        enemy_hp_count_labels.append(hp_label)

        hp_bar_bg = canvas.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill='black', width=0,
                                            tags=enemy_tags[i])
        enemy_hp_bar_bg.append(hp_bar_bg)

        hp_bar_fg = canvas.create_rectangle((100, 200 + 15 * i, 160, 212 + 15 * i), fill='#ed1139', width=0,
                                            tags=enemy_tags[i])
        enemy_hp_bar_fg.append(hp_bar_fg)

    # MOVE SPRITES TO START LOCATIONS

    i = 0
    while i < len(player_units):
        move_to_tile(canvas, player_tags[i], chosen_map.player_start_spaces[i])  # place sprite
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
    end_turn_text = canvas.create_text(415, 855, text="End\nTurn", fill="DeepPink4", justify=tk.CENTER)

    swap_spaces = canvas.create_rectangle((460, 820, 530, 900), fill='#75f216', width=0)
    swap_spaces_text = canvas.create_text(495, 855, text="Swap\nSpaces", fill="#5e5b03", justify=tk.CENTER)

    undo_action = canvas.create_rectangle((10, 820, 80, 900), fill='blue', width=0)
    undo_action_text = canvas.create_text(45, 855, text="Prev.\nAction", fill="#bfbda4", justify=tk.CENTER)

    # Map state before any start or turn effects
    canvas.initial_mapstate = create_mapstate(player_units_all, enemy_units_all, chosen_map, units_to_move, turn_info[0])

    print("---- PLAYER PHASE ----")
    damage, heals = start_of_turn(player_units, enemy_units, 1)

    for unit in player_units_all:
        if unit in heals:
            unit.HPcur = min(unit.visible_stats[HP], unit.HPcur + heals[unit])
            animate_heal_popup(canvas, heals[unit], unit.tile.tileNum)

            set_hp_visual(unit, unit.HPcur)

    i = 0
    while i < len(player_units):
        if player_units[i].specialCount != -1:
            canvas.itemconfig(player_special_count_labels[i], text=player_units[i].specialCount)

        player_units[i].canto_ready = True

        i += 1

    i = 0
    while i < len(enemy_units):
        if enemy_units[i].specialCount != -1:
            canvas.itemconfig(enemy_special_count_labels[i], text=enemy_units[i].specialCount)
        i += 1

    # Create all combat fields
    combat_fields = []
    combat_fields = create_combat_fields(player_units, enemy_units)

    # Create initial MapState, cannot be popped from history
    map_states.append(create_mapstate(player_units_all, enemy_units_all, chosen_map, units_to_move, turn_info[0]))

    def apply_mapstate(mapstate: MapState):
        global canto

        canto = None

        for blue_tile_id in canvas.canto_tile_imgs:
            canvas.delete(blue_tile_id)
        canvas.canto_tile_imgs.clear()

        clear_banner()

        # Set turn number
        turn_to_set = mapstate.turn_num
        phase_to_set = mapstate.units_to_move[0].side

        turn_info[0] = turn_to_set
        turn_info[1] = phase_to_set

        if turn_info[1] == PLAYER:
            phase_color = "#038cfc"
            phase_text = "PLAYER PHASE"
        else:
            phase_color = "#e8321e"
            phase_text = "ENEMY PHASE"

        # Update phase labels
        canvas.delete(next_phase.turn_txt)
        next_phase.turn_txt = canvas.create_text((540 / 2, 860),
                                                 text="Turn " + str(turn_info[0]) + "/" + str(turn_info[2]),
                                                 fill="#97a8c4", font=("Helvetica", 16), anchor='center')

        canvas.delete(next_phase.phase_txt)
        next_phase.phase_txt = canvas.create_text((540 / 2, 830), text=phase_text, fill=phase_color,
                                                  font=("Helvetica", 20), anchor='center')

        # Set units to move
        units_to_move.clear()
        for unit in mapstate.units_to_move:
            units_to_move.append(unit)

        # Move units to correct tile
        for unit in mapstate.unit_states.keys():
            unit.HPcur = mapstate.unit_states[unit].cur_hp
            # set_hp_visual(unit, unit.HPcur)

            # Revive fallen unit
            if unit.HPcur > 0 and unit not in units_alive[unit.side]:
                units_alive[unit.side].append(unit)

            unit.specialCount = mapstate.unit_states[unit].cur_sp

            unit.buffs = mapstate.unit_states[unit].cur_buffs[:]
            unit.debuffs = mapstate.unit_states[unit].cur_debuffs[:]
            unit.statusPos = mapstate.unit_states[unit].cur_status_pos[:]
            unit.statusNeg = mapstate.unit_states[unit].cur_status_neg[:]

            unit.special_galeforce_triggered = mapstate.unit_states[unit].sp_galeforce
            unit.nonspecial_galeforce_triggered = mapstate.unit_states[unit].nsp_galeforce
            unit.canto_ready = mapstate.unit_states[unit].canto

            unit.tile.hero_on = None

        for unit in mapstate.unit_states.keys():
            tile_num_to_move = mapstate.unit_states[unit].cur_position
            tile_Obj_to_move = chosen_map.tiles[tile_num_to_move]
            unit.tile = tile_Obj_to_move
            unit.tile.hero_on = unit

            if unit.HPcur > 0:
                update_unit_graphics(unit)

        for struct in mapstate.struct_states.keys():
            struct.health = mapstate.struct_states[struct]

        refresh_walls()

    # Update unit position graphics, when unit object has just been transferred to onto a new space
    def update_unit_graphics(unit):
        S = unit.side
        unit_index = units_all[S].index(unit)

        cur_tile = unit.tile.tileNum

        unit_sprite = sprite_IDs[S][unit_index]
        unit_gs_sprite = grayscale_IDs[S][unit_index]
        unit_wp_sprite = weapon_IDs[S][unit_index]
        unit_hp_label = hp_labels[S][unit_index]
        unit_sp_label = special_labels[S][unit_index]
        unit_hp_bar_fg = hp_bar_fgs[S][unit_index]
        unit_hp_bar_bg = hp_bar_bgs[S][unit_index]

        move_to_tile(canvas, unit_sprite, cur_tile)
        move_to_tile(canvas, unit_gs_sprite, cur_tile)
        move_to_tile_wp(canvas, unit_wp_sprite, cur_tile)
        move_to_tile_hp(canvas, unit_hp_label, cur_tile)
        move_to_tile_sp(canvas, unit_sp_label, cur_tile)
        move_to_tile_fg_bar(canvas, unit_hp_bar_fg, cur_tile)
        move_to_tile_fg_bar(canvas, unit_hp_bar_bg, cur_tile)

        canvas.itemconfig(unit_wp_sprite, state='normal')
        canvas.itemconfig(unit_hp_label, state='normal')
        canvas.itemconfig(unit_sp_label, state='normal')

        canvas.itemconfig(unit_hp_bar_fg, state='normal')
        canvas.itemconfig(unit_hp_bar_bg, state='normal')

        # I don't know why, when hiding the HP bars, they are moved really far away
        # These lines place them back to the right place
        move_to_tile_fg_bar(canvas, unit_hp_bar_fg, cur_tile)
        move_to_tile_fg_bar(canvas, unit_hp_bar_bg, cur_tile)

        set_hp_visual(unit, unit.HPcur)

        if unit in units_to_move or unit.side != turn_info[1]:
            canvas.itemconfig(unit_sprite, state='normal')
            canvas.itemconfig(unit_gs_sprite, state='hidden')
        else:
            canvas.itemconfig(unit_sprite, state='hidden')
            canvas.itemconfig(unit_gs_sprite, state='normal')

    # Function Assignment
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<Double-Button-1>", on_double_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    set_banner(player_units[0])
    clear_banner()

    window.mainloop()
    return 0


player_units = [celica, reginn, xander, tested_unit]
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

    if "askill" in data["enemyData"][i]:
        curASkill = makeSkill(data["enemyData"][i]["askill"])
        curEnemy.set_skill(curASkill, ASKILL)

    if "bskill" in data["enemyData"][i]:
        curBSkill = makeSkill(data["enemyData"][i]["bskill"])
        curEnemy.set_skill(curBSkill, BSKILL)

    if "cskill" in data["enemyData"][i]:
        curCSkill = makeSkill(data["enemyData"][i]["cskill"])
        curEnemy.set_skill(curCSkill, CSKILL)

    if "alt_stats" in data["enemyData"][i]:
        curEnemy.visible_stats = data["enemyData"][i]["alt_stats"]
        j = 0
        while j < 5:
            curEnemy.visible_stats[j] += curEnemy.skill_stat_mods[j]
            curEnemy.visible_stats[j] = max(min(curEnemy.visible_stats[j], 99), 0)
            j += 1

        curEnemy.HPcur = curEnemy.visible_stats[HP]

    curEnemy.tile = map0.enemy_start_spaces[i]
    enemy_units.append(curEnemy)
    i += 1

# tested_unit.inflictDamage(30)

# Test Map
if __name__ == "__main__":
    start_sim(player_units, enemy_units, map0, map_num)
