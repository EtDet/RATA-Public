from combat import *
from queue import Queue
from copy import copy

class Tile:
    def __init__(self,terrain,x,y):

        # coordinate grid system starting at top left
        self.x = x
        self.y = y

        # numbered tile system starting at bottom left, going right
        self.tileNo = 0

        self.terrain = terrain
        # 0 - normal
        # 1 - forest
        # 2 - flierOnly
        # 3 - defensive
        # 4 - trench
        # 5 - defensive trench
        # 6 - wall

        # pointer to hero currently on this tile
        self.heroOn = None
        # hero currently on this tile if using save skills
        self.saviorHeroOn = None
        # no
        self.effects = None

        # tile to each cardinal direction of each node
        self.north = None
        self.east = None
        self.south = None
        self.west = None

    def getX(self): return self.x
    def getY(self): return self.y
    def getCoords(self): return self.x,self.y

    def setTileNo(self,tileNo): self.tileNo = tileNo
    def getTileNo(self): return self.tileNo

    def getNorth(self): return self.north
    def getEast(self): return self.east
    def getSouth(self): return self.south
    def getWest(self): return self.west

    def setNorth(self,north): self.north = north
    def setEast(self,east): self.east = east
    def setSouth(self,south): self.south = south
    def setWest(self,west): self.west = west

    def getHero(self): return self.heroOn
    def setHero(self,hero): self.heroOn = hero

    def getTerrain(self): return self.terrain
    def setTerrain(self,terrain): self.terrain = terrain

    def printHero(self):
        if self.heroOn == None: print("None")
        else: print(self.heroOn.getName())

    def getTilesWithinNSpaces(self,n):
        fringe = Queue() #tiles to visit
        tilesWithin = [] #tiles visited
        fringe.put(self) #put this node in fringe
        tilesWithin.append(self)

        # Breadth First Search of local tiles within n spaces

        level = 0
        fringe.put(Tile(-1,-1,-1))

        while not fringe.empty() and level < n:

            cur = fringe.get()

            if cur.getNorth() != None and cur.getNorth() not in tilesWithin:
                fringe.put(cur.getNorth())
                tilesWithin.append(cur.getNorth())
            if cur.getEast() != None and cur.getEast() not in tilesWithin:
                fringe.put(cur.getEast())
                tilesWithin.append(cur.getEast())
            if cur.getSouth() != None and cur.getSouth() not in tilesWithin:
                fringe.put(cur.getSouth())
                tilesWithin.append(cur.getSouth())
            if cur.getWest() != None and cur.getWest() not in tilesWithin:
                fringe.put(cur.getWest())
                tilesWithin.append(cur.getWest())

            if cur.getX() == -1:
                level += 1
                fringe.put(Tile(-1,-1,-1))

        return tilesWithin

    # see if otherHero is within n spaces of unit on this tile
    def isOtherWithinNTiles(self,otherHero,n):
        tiles = self.getTilesWithinNSpaces(n)
        for tile in tiles:
            if tile.getHero() == otherHero:
                return True
        return False

# subclass of tile unit can start on
class StartingTile(Tile):
    def __init__(self,terrain,num,side,x,y):
        super().__init__(terrain,x,y)
        self.num = num
        self.side = side # false - player, true - enemy

# current map with units
class Map:
    def __init__(self,stp,ste):

        # generate 8x6 map of tiles of default terrain
        self.map=[]
        rows, cols = 8,6
        i = 0
        while i < rows:
            j = 0
            col = []
            while j < cols:
                col.append(Tile(0,j,i))
                j += 1
            self.map.append(col)
            i += 1

        # list of two lists of starting tiles
        self.startingTiles = [[], []]

        i = 0
        while i < len(stp):
            self.map[stp[i][0]][stp[i][1]] = StartingTile(self.map[stp[i][0]][stp[i][1]].getTerrain(),i,False,stp[i][1],stp[i][0])
            self.startingTiles[0].append(self.map[stp[i][0]][stp[i][1]])
            #self.currentTiles[0].append(self.map[stp[i][0]][stp[i][1]])
            i += 1

        i = 0
        while i < len(ste):
            self.map[ste[i][0]][ste[i][1]] = StartingTile(self.map[ste[i][0]][ste[i][1]].getTerrain(),i,True,ste[i][1],ste[i][0])
            self.startingTiles[1].append(self.map[ste[i][0]][ste[i][1]])
            #self.currentTiles[1].append(self.map[ste[i][0]][ste[i][1]])
            i += 1

        # set cardinal directions
        i = 0
        while i < len(self.map):
            j = 0
            while j < len(self.map[0]):
                if i != 0:
                    self.map[i][j].setNorth(self.map[i-1][j])
                if j != 0:
                    self.map[i][j].setWest(self.map[i][j-1])
                if i != len(self.map) - 1:
                    self.map[i][j].setSouth(self.map[i+1][j])
                if j != len(self.map[0]) - 1:
                    self.map[i][j].setEast(self.map[i][j+1])
                j += 1
            i += 1

    # place player units on player starting tiles, same for enemy
    def placeUnits(self,playerUnits,enemyUnits):

        self.playerUnits = playerUnits
        self.enemyUnits = enemyUnits

        #place units
        i = 0
        while i < len(self.startingTiles[0]):
            self.startingTiles[0][i].setHero(playerUnits[i])
            playerUnits[i].setTile(self.startingTiles[0][i])
            i += 1

        i = 0
        while i < len(self.startingTiles[1]):
            self.startingTiles[1][i].setHero(enemyUnits[i])
            enemyUnits[i].setTile(self.startingTiles[1][i])
            i += 1

        #initialize starting stats w/ weapon might, skills
        player = self.getNextUnits(False)
        for x in player:
            plrStats = x.getStats()
            plrStats[1] += x.getWeapon().getMT()
            plrSkills = x.getSkills()
            for key in plrSkills:
                if key == "HPBoost":  plrStats[0] += plrSkills["HPBoost"]
                if key == "atkBoost": plrStats[1] += plrSkills["atkBoost"]
                if key == "spdBoost": plrStats[2] += plrSkills["spdBoost"]
                if key == "defBoost": plrStats[3] += plrSkills["defBoost"]
                if key == "resBoost": plrStats[4] += plrSkills["resBoost"]
            x.setStats(plrStats)


        enemy = self.getNextUnits(True)
        for x in enemy:
            emyStats = x.getStats()
            emyStats[1] += x.getWeapon().getMT()
            emySkills = x.getSkills()
            for key in emySkills:
                if key == "HPBoost":  emyStats[0] += emySkills["HPBoost"]
                if key == "atkBoost": emyStats[1] += emySkills["atkBoost"]
                if key == "spdBoost": emyStats[2] += emySkills["spdBoost"]
                if key == "defBoost": emyStats[3] += emySkills["defBoost"]
                if key == "resBoost": emyStats[4] += emySkills["resBoost"]
            x.setStats(emyStats)

    def getMap(self): return self.map

    # get enemy units if boolean true, player if false
    def getNextUnits(self,boolean):
        if boolean: return self.enemyUnits
        else: return self.playerUnits

# one current state, with a set map
class State:
    def __init__(self,prev,map,phase,leftToAct,turn,alivePlayers,aliveEnemies):
        self.prev = prev
        self.map = copy(map)
        self.phase = phase # false - player, true - enemy
        self.leftToAct = leftToAct[:]
        self.turn = turn

        self.alivePlayers = alivePlayers
        self.aliveEnemies = aliveEnemies


        #atkStats[1] += attacker.getWeapon().getMT()
        #defStats[1] += defender.getWeapon().getMT()

    # ifIsStartOfTurn
    # distribute bonuses, lasts until start of next turn (or if removed?)
    # distribute penalties, lasts until unit moves, or if removed
    # distribute effects

    def doMove(self,newTile,unit):
        oldTile = unit.tile
        oldTile.setHero(None)
        unit.setTile(newTile)
        newTile.setHero(unit)

        i = 0
        while i < len(self.leftToAct):
            if self.leftToAct[i] == unit:
                self.leftToAct.pop(i)
            i += 1
        next = State(self,self.map,self.phase,self.leftToAct,self.turn,self.alivePlayers,self.aliveEnemies)

        return next

    def getPhase(self):
        return self.phase

    def getLeftToAct(self):
        return self.leftToAct

    def getMap(self):
        return self.map

    def getTurn(self):
        return self.turn

    def getPossibleMoves(self,unit):
        move = unit.move
        tiles = []
        if move == 3 or Status.Gravity in unit.statusNeg:
            tiles = unit.tile.getTilesWithinNSpaces(1)
        if move == 1:
            tiles = unit.tile.getTilesWithinNSpaces(3)
        if move == 0 or move == 2:
            tiles = unit.tile.getTilesWithinNSpaces(2)
        i = 0
        while i < len(tiles):
            if tiles[i].getHero() != None:
                tiles.pop(i)
                i -= 1
            i += 1
        #print("NEXT")
        tiles.append(unit.tile)

        # 3 possible moves for each unit at a given state
        # do nothing
        # attack
        # support

        # we'll account for duo skills/pair up/canto later
        return tiles

    def enemyPhase(self,playerUnits,enemyUnits):
        mapObj = self.map

        # ok who's alive
        playerUnitsAlive = []
        enemyUnitsAlive = []
        blockList = []

        map = mapObj.getMap() #y'know maybe I shouldn't've made the 2D array AND the object both be called "map"

        for x in map:
            for y in x:
                if y.getHero() != None:
                    if y.getHero() in playerUnits:
                        playerUnitsAlive.append(y)
                    elif y.getHero() in enemyUnits:
                        enemyUnitsAlive.append(y)

        #for x in playerUnitsAlive: x.setPass(True)
        #for x in enemyUnitsAlive: x.setPass(True)






units = HeroDirectory().getHeroes()
playerUnits = [marth,nino,takumi,ephraim]
enemyUnits = [alm,nowi,hector,bartre]
startingTilesPlayer = [(7,1),(7,2),(7,3),(7,4)]
startingTilesEnemy = [(0,1),(0,2),(0,3),(0,4)]
map = Map(startingTilesPlayer,startingTilesEnemy)
map.placeUnits(playerUnits,enemyUnits)
#print(map.getMap()[0][2].getHero().getStats())

def simulate(playerUnits,enemyUnits,map):
    turn = 1
    startState = State(-1, map, False, playerUnits, turn, playerUnits, enemyUnits)
    stack = []
    stack.append(startState)

    while stack:  # while stack has states
        #print(len(stack))
        cur = stack.pop() # get top of stack
        curRem = cur.getLeftToAct() # get units that can act at this state
        i = len(curRem) - 1 # start at end of remaining units list
        if i == -1: # enemy phase case
            #print("AAAAA")
            eMap = copy(cur.getMap())
            eState = State(cur, eMap, True, enemyUnits, cur.getTurn(), playerUnits, enemyUnits)
            eState.enemyPhase(playerUnits,enemyUnits)
            pMap = copy(eState.getMap())
            #pState = State(eState, pMap, False, playerUnits, eState.getTurn() + 1)
            stack = []
        else:
            while i >= 0: # loops through deleting each unit in rem units list
                tempRem = curRem[:] # create copy of remaining units
                r = tempRem.pop(i) # this guyyyyyy
                moves = cur.getPossibleMoves(r) # what is this guyyyyyy gonna do
                for m in moves: # for each of this guyyyyyyy's moves
                    newMap = copy(cur.getMap()) # copy map
                    newState = State(cur, newMap, False, tempRem, cur.getTurn,playerUnits,enemyUnits) # make state
                    newState.doMove(m, r) # do the move the current unit is doing
                    stack.append(newState)  # add modified state to stack
                i -= 1


    return False

simulate(playerUnits,enemyUnits,map)

daMap = map.getMap()

for x in daMap:
    for y in x:
        if y.getHero() != None: print(y.getHero().getName(),end='')
        else: print(None,end='')
        #print(y.getCoords()," ",end='')
    print()
print()

def printMoves(moves):
    for x in moves:
        print(x.getX(),x.getY())

startState = State(-1,map,False,playerUnits,1,playerUnits,enemyUnits)
print("Ephraim,Nino,Takumi,Marth")

#moves = startState.getPossibleMoves(ephraim)
#printMoves(moves)
#print()
#nextState = startState.doMove(ephraim,moves[2])
#moves = nextState.getPossibleMoves(nino)
#printMoves(moves)
#print()
#nextNextState = nextState.doMove(nino,moves[3])
#moves = nextNextState.getPossibleMoves(takumi)
#printMoves(moves)
#print()
#nextNextNextState = nextNextState.doMove(takumi,moves[3])
#moves = nextNextNextState.getPossibleMoves(marth)
#printMoves(moves)
#print()
#finalState = nextNextNextState.doMove(marth,moves[4])

#print(finalState.getPhase())
#print(finalState.getLeftToAct()[0].getName())

