from queue import Queue
from pandas import read_csv

class Tile:
    def __init__(self, tile_num, terrain, is_def_terrain, texture):
        self.tileNum = tile_num  # number between 0-47, increases by 1 going right, 6 by going up
        self.x_coord = tile_num % 6
        self.y_coord = tile_num // 6

        # terrain key
        # 0 - default
        # 1 - forest
        # 2 - flier only (mountain, water, etc.)
        # 3 - trench
        # 4 - impassible

        self.terrain = terrain
        self.is_def_terrain = is_def_terrain

        self.hero_on = None
        self.savior_hero_on = None

        self.structure_on = None

        self.north = None
        self.east = None
        self.south = None
        self.west = None

        # divine vein key
        # 0 - none
        # 1 - flame
        # 2 - stone

        self.divine_vein = -1
        self.divine_vein_side = -1

        # texture key
        # 0 - green grass / bush / water / trench / pillar
        # 1 - cobble path / tree / mountain / trench / house
        # 2 - sand / palm tree / spike pit / trench / wall
        # 3 - dark grass / flowers / x / x / castle
        # 4 - purple grass
        # 5 - wood
        self.terrain_texture = texture

    # all tiles exactly n spaces away
    def tilesNSpacesAway(self, n):
        fringe = Queue()  # tiles to visit
        visited = set()  # visited tiles to avoid duplicates
        tilesAtN = []  # tiles exactly n spaces away

        fringe.put(self)  # start with the current tile
        visited.add(self)

        # Level marker
        fringe.put(Tile(-1, -1, -1, -1))
        level = 0

        while not fringe.empty() and level <= n:
            cur = fringe.get()

            if cur.tileNum == -1:
                level += 1
                if level > n:
                    break
                if not fringe.empty():
                    fringe.put(Tile(-1, -1, -1, -1))
                continue

            # Add neighboring tiles to the queue
            for neighbor in [cur.north, cur.east, cur.south, cur.west]:
                if neighbor is not None and neighbor not in visited:
                    fringe.put(neighbor)
                    visited.add(neighbor)
                    if level == n - 1:  # Next level will be 'n'
                        tilesAtN.append(neighbor)

        return tilesAtN

    # all tiles within n spaces
    def tilesWithinNSpaces(self, n):
        fringe = Queue()  # tiles to visit
        tilesWithin = []  # tiles visited
        fringe.put(self)  # put this node in fringe
        tilesWithin.append(self)

        # Breadth First Search of local tiles within n spaces

        level = 0
        fringe.put(Tile(-1, -1, -1, -1))

        while not fringe.empty() and level < n:

            cur = fringe.get()

            if cur.north is not None and cur.north not in tilesWithin:
                fringe.put(cur.north)
                tilesWithin.append(cur.north)
            if cur.east is not None and cur.east not in tilesWithin:
                fringe.put(cur.east)
                tilesWithin.append(cur.east)
            if cur.south is not None and cur.south not in tilesWithin:
                fringe.put(cur.south)
                tilesWithin.append(cur.south)
            if cur.west is not None and cur.west not in tilesWithin:
                fringe.put(cur.west)
                tilesWithin.append(cur.west)

            if cur.tileNum == -1:
                level += 1
                fringe.put(Tile(-1, -1, -1, -1))

        return tilesWithin

    # all units within n spaces
    def unitsWithinNSpaces(self, n):
        within_n_tiles = self.tilesWithinNSpaces(n)
        arr = []
        for x in within_n_tiles:
            if x.hero_on is not None:
                arr.append(x.hero_on)

        return arr

    def unitsWithinNCols(self, n):
        within_n_tiles = self.tilesWithinNCols(n)
        arr = []
        for x in within_n_tiles:
            if x.hero_on is not None:
                arr.append(x.hero_on)

        return arr

    def unitsWithinNRows(self, n):
        within_n_tiles = self.tilesWithinNRows(n)
        arr = []
        for x in within_n_tiles:
            if x.hero_on is not None:
                arr.append(x.hero_on)

        return arr

    # all tiles within n columns
    def tilesWithinNCols(self, n):
        horizontal = [self]

        west_explorer = self
        east_explorer = self

        i = 1
        while i < n:
            if west_explorer.west is not None:
                west_explorer = west_explorer.west
                horizontal.append(west_explorer)
            if east_explorer.east is not None:
                east_explorer = east_explorer.east
                horizontal.append(east_explorer)

            i += 2

        tiles_within = horizontal[:]

        for tile in horizontal:
            cur_tile = tile
            while cur_tile.north is not None:
                cur_tile = cur_tile.north
                tiles_within.append(cur_tile)
            cur_tile = tile
            while cur_tile.south is not None:
                cur_tile = cur_tile.south
                tiles_within.append(cur_tile)

        return tiles_within

    # all tiles within n rows
    def tilesWithinNRows(self, n):
        vertical = [self]

        north_explorer = self
        south_explorer = self

        i = 1
        while i < n:
            if north_explorer.north is not None:
                north_explorer = north_explorer.north
                vertical.append(north_explorer)
            if south_explorer.south is not None:
                south_explorer = south_explorer.south
                vertical.append(south_explorer)

            i += 2

        tiles_within = vertical[:]

        for tile in vertical:
            cur_tile = tile
            while cur_tile.west is not None:
                cur_tile = cur_tile.west
                tiles_within.append(cur_tile)
            cur_tile = tile
            while cur_tile.east is not None:
                cur_tile = cur_tile.east
                tiles_within.append(cur_tile)

        return tiles_within

    def tilesWithinNRowsOrCols(self, m, n):
        if n % 2 == 0 or m % 2 == 0: return []

        return list(set(self.tilesWithinNRows(m)).union(set(self.tilesWithinNCols(n))))

    def tilesWithinNRowsAndCols(self, m, n):
        if n % 2 == 0 or m % 2 == 0: return []

        return list(set(self.tilesWithinNRows(m)).intersection(set(self.tilesWithinNCols(n))))

# Bolt Tower, Healing Tower
def get_tower_hp_change(level):
    if 1 <= level <= 9:
        return level * 5 + 5
    else:
        return level * 2 + 32

# Panic Manor, Tactics Room, Heavy Trap, Hex Trap
def get_tower_hp_threshold(level):
    if 1 <= level <= 9:
        return level * 5 + 35
    else:
        return level * 2 + 62

class Structure:
    def __init__(self, name, occupies_tile, is_targetable, struct_type, health, level):

        # structure key
        self.name = name

        # 0 - Common Wall
        # 1 - AR Structure (O)
        # 2 - AR Structure (D)
        self.struct_type = struct_type

        # How many hits needed to break structure
        # 1 or 2, structure is present
        # 0, structure is destoryed
        # -1, structure is indestructable
        self.health = health
        self.max_health = health

        self.level = level
        self.max_level = level

        self.is_targetable = is_targetable
        self.occupies_tile = occupies_tile

    def get_desc(self):
        if self.name == "Fortress":
            # DIFFERS FOR D
            if self.struct_type == 1:
                return "If structure's level > opponent's Fortress (D) level, grants Atk/Spd/Def/Res+X to all allies. (X = difference in level × 4). Note: Cannot be removed or destroyed."
            else:
                return "If structure's level > opponent's Fortress (O) level, grants Atk/Spd/Def/Res+X to all allies. (X = difference in level × 4). Note: Cannot be removed or destroyed."
        if self.name == "Bolt Tower":
            if self.struct_type == 1:
                return "At the start of turn 3, deals " + str(get_tower_hp_change(self.level)) + " damage to foes within 3 columns centered on structure."
            else:
                return "At the start of turn 3, deals " + str(get_tower_hp_change(self.level)) + " damage to foes within 7 rows and 3 columns centered on structure."
        if self.name == "Tactics Room":
            if self.struct_type == 1:
                return "At start of turn, if any foes are within the same column as structure and their HP ≤ " + str(get_tower_hp_threshold(self.level)) + " and they use a ranged weapon, inflicts [Gravity] on those foes."
            else:
                return "At start of turn, if any foes are within 7 rows and 3 columns centered on structure and their HP ≤ " + str(get_tower_hp_threshold(self.level)) + " and they use a ranged weapon, inflicts [Gravity] on those foes."
        if self.name == "Healing Tower":
            if self.struct_type == 1:
                return "At start of turn, restores " + str(get_tower_hp_change(self.level)) + " HP to allies within 3 rows and 5 columns centered on structure."
            else:
                return "At start of turn, restores " + str(get_tower_hp_change(self.level)) + " HP to allies within 5 rows and 5 columns centered on structure."
        if self.name == "Panic Manor":
            if self.struct_type == 1:
                return "At start of turn, if any foes are within 3 columns centered on structure and their HP ≤ " + str(get_tower_hp_threshold(self.level)) + ", inflicts [Panic] on those foes."
            else:
                return "At start of turn, if any foes are within 7 rows and 3 columns centered on structure and their HP ≤ " + str(get_tower_hp_threshold(self.level)) + ", inflicts [Panic] on those foes."
        if self.name == "Catapult":
            if self.struct_type == 1:
                return "At start of turn, destroys defensive structures within the same column as this structure if their level ≤ this structure's level. Note: Fortress (D), traps, resources, and ornaments cannot be destroyed."
            else:
                return "At start of turn, destroys offensive structures within the same column as this structure if their level ≤ this structure's level. Note: Fortress (O) cannot be destroyed."

        if self.name == "Infantry School":
            return "At start of turn, inflicts Atk/Spd/Def/Res-" + str(self.level + 1) + " on infantry foes within 3 columns centered on structure through their next actions."
        if self.name == "Cavalry School":
            return "At start of turn, inflicts Atk/Spd/Def/Res-" + str(self.level + 1) + " on cavalry foes within 3 columns centered on structure through their next actions."
        if self.name == "Flier School":
            return "At start of turn, inflicts Atk/Spd/Def/Res-" + str(self.level + 1) + " on flying foes within 3 columns centered on structure through their next actions."
        if self.name == "Armor School":
            return "At start of turn, inflicts Atk/Spd/Def/Res-" + str(self.level + 1) + " on armored foes within 3 columns centered on structure through their next actions."

        if self.name == "Bright Shrine":
            return "At start of turn, inflicts Atk/Spd-" + str(self.level + 1) + " on foe on the enemy team with the highest Atk+Spd total through its next action."
        if self.name == "Dark Shrine":
            return "At start of turn, inflicts Def/Res-" + str(self.level + 1) + " on foe on the enemy team with the highest Def+Res total through its next action."

        if self.name == "Duo's Indulgence":
            return "The first Duo or Harmonized Skill used between turn 1 and turn " + str(self.level + 2) + " can be used a second time. (Max of two uses. Only one use per turn.)"
        if self.name == "Duo's Hindrance":
            return "While a Duo or Harmonized Hero is on the defensive team, foe cannot use Duo or Harmonized Skills between turn 1 and turn " + str(self.level + 2) + "."
        if self.name == "Escape Ladder":
            return "A lost battle's Aether cost will be returned. May be used up to " + str(self.level) + " times per season. Cannot be destroyed."
        if self.name == "Safety Fence":
            return "Until turn " + str(self.level) + ", after skill activation at start of defensive turn, if raiding party is outside the defensive team's range or is within 2 rows and 7 columns centered on a structure, defensive turn ends immediately."
        if self.name == "Calling Circle":
            return "A reinforcement appears on turn 3 and gets an extra action once per turn if a Mythic Hero with Raiding Party Call is in your raiding party."

        if self.name == "Bolt Trap":
            return "If foe ends movement on this structure's space, deals " + str(self.level * 10) + " damage to target and units within 3 spaces. (Cancels foe's attack, Assist skill, etc.)"
        if self.name == "Heavy Trap":
            return "If foe ends movement on this structure's space, restricts movement of target and units within 2 spaces with HP ≤ " + str(self.level * 5 + 35) + " to 1 space through their next actions. (Cancels foe's attack, Assist skills, etc.)"
        if self.name == "Hex Trap":
            return "If foe ends movement on this structure's space and foe's HP ≤ " + str(self.level * 5 + 35) + ", cancels foe's attack, Assist skill, etc. and ends that foe's action. (Magic traps cannot be disarmed by Disarm Trap skills.)"

        if "False" in self.name:
            return "This looks like a " + self.name.replace("False ", "") + ", but it's just a fake."

        if self.name == "Aether Amphorae":
            return "Stores up to " + str(self.level * 50 + 50) + " Aether. If destroyed in an attack, they restore Aether to the raiding party (if they win). Note: Cannot be removed. Can be destroyed."
        if self.name == "Aether Fountain":
            return "Restores " + str(self.level * 10 + 40) + " Aether to the Aether Keep each day. If destroyed in an attack, it restores Aether to the raiding party (if they win). Note: Cannot be removed. Can be destroyed."

        if self.name == "Accessory Shop":
            return "A structure where Heroes can sample various accessories to find new looks that catch their fancy!"
        if self.name == "Armory":
            return "A structure that contains a collection of replica weapons for Heroes to sample. The stock is updated periodically too!"
        if self.name == "Concert Hall":
            return "A structure fit for all kinds of song. Famous for its impressive acoustics!"
        if self.name == "Dining Hall":
            return "A structure where dishes can be prepared with the ingredients harvested from your field."
        if self.name == "Field":
            return "A place where Dragonflowers and food-crop ingredients for the Dining Hall are grown and harvested."
        if self.name == "Hot Spring":
            return "A structure where Heroes can relax in a nice hot spring. Apparently it is a natural spring too, which is especially incredible considering it is located within a flying island in the sky."
        if self.name == "Inn":
            return "A structure where Heroes can rest. Sometimes Heroes will even dream as they slumber..."

struct_sheet = read_csv('Spreadsheets/FEHStructures.csv')

def makeStruct(name, struct_type):
    row = struct_sheet.loc[struct_sheet['Name'] == name]
    n = row.index.values[0]

    name = row.loc[n, 'Name']
    occupies_tile = row.loc[n, 'Occupies Tile']
    targetable = row.loc[n, 'Is Targetable']
    max_level = row.loc[n, 'Max Level']
    health = row.loc[n, 'Health']

    result_struct = Structure(name, occupies_tile, targetable, struct_type, health, max_level)

    return result_struct



# class AR_Structure: SUBCLASS
# level
# struct owner

# class MW_Structure: SUBCLASS
# level
# triggered

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


class Map:
    def __init__(self, size_type):

        # Standard 6x8
        if size_type == 0:
            self.tiles = [0] * 48
            for i in range(0, 48):
                self.tiles[i] = Tile(i, 0, 0, 0)
            for i in range(0, 48):
                if i // 6 != 0: self.tiles[i].south = self.tiles[i - 6]
                if i // 6 != 7: self.tiles[i].north = self.tiles[i + 6]
                if i % 6 != 0: self.tiles[i].west = self.tiles[i-1]
                if i % 6 != 5: self.tiles[i].east = self.tiles[i+1]


        self.player_start_spaces = []
        self.enemy_start_spaces = []

        self.liquid_texture = "WavePattern.png"
        self.wall_texture = "Wallpattern.png"

    def add_start_space(self, tile_no, side):
        if not side: self.player_start_spaces.append(tile_no)
        else: self.enemy_start_spaces.append(tile_no)

    def define_map(self, map_json):
        if "liquid" in map_json:
            self.liquid_texture = map_json["liquid"]
        if "wall" in map_json:
            self.wall_texture = map_json["wall"]

        i = 0
        j = len(self.tiles)-1
        while i < len(map_json["terrain"]):
            ii = len(map_json["terrain"][0])-1
            while ii >= 0:
                self.tiles[j].terrain = map_json["terrain"][i][ii]
                ii -= 1
                j -= 1
            i += 1

        if "defensiveTiles" in map_json:
            for x in map_json["defensiveTiles"]:
                self.tiles[x].is_def_terrain = 1

        for x in map_json["playerStart"]:
            self.player_start_spaces.append(x)
        for x in map_json["enemyStart"]:
            self.enemy_start_spaces.append(x)

        # Structures
        if "struct_walls" in map_json:
            walls = map_json["struct_walls"]

            for x in walls["static"]:
                temp_struct = Structure("Obstacle", True, False, 0, -1, 1)
                self.tiles[x].structure_on = temp_struct

            for x in walls["twoBreak"]:
                temp_struct = Structure("Obstacle", True, True,0, 2, 1)
                self.tiles[x].structure_on = temp_struct

            for x in walls["oneBreak"]:
                temp_struct = Structure("Obstacle", True, True,0, 1, 1)
                self.tiles[x].structure_on = temp_struct

        if "mode" in map_json and map_json["mode"] == "aether":
            fortress_O = makeStruct("Fortress", 1)
            self.tiles[2].structure_on = fortress_O

            fortress_D = makeStruct("Fortress", 2)

            if not self.tiles[27].structure_on and self.tiles[27].terrain == 0:
                self.tiles[27].structure_on = fortress_D
            else:
                self.tiles[28].structure_on = fortress_D

            fountain = makeStruct("Aether Fountain", 2)
            self.tiles[42].structure_on = fountain

            amphorae = makeStruct("Aether Amphorae", 2)
            self.tiles[47].structure_on = amphorae

    def get_heroes_present(self):
        heroes = []

        for tile in self.tiles:
            if tile.hero_on:
                heroes.append(tile.hero_on)

        return heroes

    def get_heroes_present_by_side(self):
        player_side_heroes = []
        enemy_side_heroes = []

        for tile in self.tiles:
            if tile.hero_on:
                if tile.hero_on.side == 0:
                    player_side_heroes.append(tile.hero_on)
                else:
                    enemy_side_heroes.append(tile.hero_on)

        return player_side_heroes, enemy_side_heroes