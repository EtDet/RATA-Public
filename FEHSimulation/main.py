from tkinter import *
from PIL import Image, ImageTk

class Tile:

    def __init__(self,terrain):
        self.terrain = terrain
        self.heroOn = None

        self.unitBuffs = []
        self.enemyBuffs = []
        self.unitEffects = []
        self.enemyEffects = []

        self.north = None
        self.east = None
        self.south = None
        self.west = None

    def setHero(self,hero):
        self.heroOn = hero

class Map:
    def __init__(self):
        self.map = []
        i = 0
        while i < 8:
            self.map.append([Tile(0),Tile(0),Tile(0),Tile(0),Tile(0),Tile(0)])
            i+=1

    def placeHero(self,hero,row,col):
        self.map[row][col].setHero(hero)

class Hero:
    def __init__(self,hp,at,sp,df,rs,weapon,movement):
        self.hp=hp
        self.at=at
        self.sp=sp
        self.df=df
        self.rs=rs
        self.wpnType = weapon
        self.move = movement  # 0 - inf, 1 - cav, 2 - fly, 3 - arm

class Skill:
    def __init__(self, name):
        self.name = name

    #def atkIncreaseStat(self,unit,level):
    #    unit.atk += level

def draw():
    root = Tk()
    root.title('FEH Simulation Window')
    root.iconbitmap("C:\\Users\\eman5\\PycharmProjects\\FEHSimulation\\Sprites\\Marth.ico")
    root.geometry("480x740")

    cWidth = 480
    cHeight = 640

    myCanvas = Canvas(root, width=cWidth, height=cHeight, bg='white')
    myCanvas.pack(pady=50)
    i = 0

    while i < 6:
        j = 0
        while j < 8:
            myCanvas.create_rectangle(i * (cWidth / 6), j * (cHeight / 8), (i + 1) * (cWidth / 6),
                                      (j + 1) * (cHeight / 8), fill="#4b9431")
            j += 1
        i += 1

    marthSprite = Image.open('C:\\Users\\eman5\\PycharmProjects\\FEHSimulation\\Sprites\\marth.png')
    resize = marthSprite.resize((cWidth // 6, cHeight // 8))
    img = ImageTk.PhotoImage(resize)

    myCanvas.create_image(0,0,anchor=NW,image=img)

    root.mainloop()

    return root

marth = Hero(41,31,34,29,23,"Sword",0)
map = Map()
map.placeHero(marth,7,2)

draw()




