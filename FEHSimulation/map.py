from queue import Queue


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

        self.divine_vein = 0
        self.divine_vein_owner = 0

        # texture key
        # 0 - green grass / bush / water / trench / pillar
        # 1 - cobble path / tree / mountain / trench / house
        # 2 - sand / palm tree / spike pit / trench / wall
        # 3 - dark grass / flowers / x / x / castle
        # 4 - purple grass
        # 5 - wood
        self.terrain_texture = texture

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

    # all tiles within n columns
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

    def tilesWithinNRowsOrCols(self, n):
        if self.hero_on is None: return []
        if n % 2 == 0: return []

        return list(set(self.tilesWithinNCols(n)).union(set(self.tilesWithinNRows(n))))


class Structure:
    def __init__(self, struct_type, health):

        # structure key

        # 0 - Common Wall
        self.struct_type = struct_type

        # How many hits needed to break structure
        # 1 or 2, structure is present
        # 0, structure is destoryed
        # -1, structure is indestructable
        self.health = health

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
                temp_struct = Structure(0, -1)
                self.tiles[x].structure_on = temp_struct

            for x in walls["twoBreak"]:
                temp_struct = Structure(0, 2)
                self.tiles[x].structure_on = temp_struct

            for x in walls["oneBreak"]:
                temp_struct = Structure(0, 1)
                self.tiles[x].structure_on = temp_struct