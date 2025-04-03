# FORMAT FOR GETTING AN IMAGE FILE FROM FANDOM WIKI
# https://feheroes.fandom.com/wiki/Special:Redirect/file/Alfonse_Prince_of_Askr_Mini_Unit_Ok.png

# 'https://feheroes.fandom.com/wiki/Special:Redirect/file/Seidr_Goddess_of_Hope_Mini_Unit_Ok.png'

#image_url = 'https://feheroes.fandom.com/wiki/Special:Redirect/file/Alfonse_Prince_of_Askr_Mini_Unit_Ok.png'
#sample_save_path = 'TestSprites\\downloaded_image.png'
#download_and_save_image(image_url, save_path)

# Importing maps
# 'https://feheroes.fandom.com/wiki/Special:Redirect/file/Map_Z0096.png'

import requests
from hero import hero_sheet, implemented_heroes, generics
from map import struct_sheet
from PIL import Image
from io import BytesIO
import os.path
import unicodedata


def download_and_save_image(url, save_path):
    if os.path.isfile(save_path):
        print(f"Image {save_path} already exists, moving on...")
        return 0

    response = requests.get(url)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image.save(save_path)
        print(f"Image successfully saved to {save_path}")
    else:
        print(f"Failed to retrieve image. Status code: {response.status_code}")
        return -1


def normalize_string(input_string):
    # Remove quotes and apostrophes
    input_string = input_string.replace('"', '').replace("'", "")

    # Replace Eth and Thorn
    input_string = input_string.replace('ð', 'd')
    input_string = input_string.replace('þ', 'th')

    # Remove accented characters, set to ASCII
    normalized_string = unicodedata.normalize('NFKD', input_string)
    ascii_string = normalized_string.encode('ASCII', 'ignore').decode('ASCII')

    # Replace spaces
    ascii_string = ascii_string.replace(' ', '_')

    return ascii_string

names = hero_sheet['Name']
int_names = hero_sheet['IntName']
epithets = hero_sheet['Epithet']
weapons = hero_sheet['Weapon Type']
has_resps = hero_sheet['HasResp']

i = 0
#i = len(names)
while i < len(names):
    name = normalize_string(names[i])
    int_name = int_names[i]
    epithet = normalize_string(epithets[i])
    has_resp = has_resps[i]
    weapon = weapons[i]

    #print(name + "_" + epithet)

    image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + name + "_" + epithet + "_Mini_Unit_Ok.png"

    # Rearmed Tana's OK Sprite has arrow in weird position, use ready sprite instead
    if int_name == "R!Tana":
        image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/Tana_Soaring_Princess_Mini_Unit_Ready.png"

    # If image is currently of a character in this current build
    if int_name in implemented_heroes and name + epithet != "BrunoMasked Knight":

    # Only to be used for getting the most recent units for development, comment back as soon as you're done!
    #if True:
        download_and_save_image(image_url, "TestSprites/" + int_name + ".png")

        if has_resp:
            resp_image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + name + "_" + epithet + "_Resplendent_Mini_Unit_Ok.png"
            save_name = int_name + "-R"

            download_and_save_image(resp_image_url, "TestSprites/" + save_name + ".png")

        if weapon in ["RBeast", "BBeast", "GBeast", "CBeast"]:
            beast_image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + name + "_" + epithet + "_TransformMap_Mini_Unit_Idle.png"
            beast_name = int_name + "-Tr"
            download_and_save_image(beast_image_url, "TestSprites/" + beast_name + ".png")

    i += 1

# Bruno: Masked Knight
# Uses name different from visible name on Wiki (??? -> Bruno)
download_and_save_image("https://feheroes.fandom.com/wiki/Special:Redirect/file/Masked_Knight_Mini_Unit_Ok.png", "TestSprites/" + "Bruno" + ".png")


for generic in generics:
    image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + generic + "_Mini_Unit_Idle.png"
    download_and_save_image(image_url, "TestSprites/" + generic + ".png")

# Arena Maps
i = 1
while i <= 50:
    image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + "Map_Z" + str(i).zfill(4) + ".png"
    download_and_save_image(image_url, "Maps/Arena Maps/" + "Map_Z" + str(i).zfill(4) + ".png")
    i += 1

# Story Maps

# Preface
i = 1
while i <= 2:
    image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + "Map_S" + str(i).zfill(4) + ".png"
    download_and_save_image(image_url, "Maps/Story Maps/Book 1/Preface/" + "Map_S" + str(i).zfill(4) + ".png")
    i += 1

# Prologue
i = 1
while i <= 3:
    image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + "Map_S01" + str(i).zfill(2) + ".png"
    download_and_save_image(image_url, "Maps/Story Maps/Book 1/Prologue/" + "Map_S01" + str(i).zfill(2) + ".png")
    i += 1

# Main Story

# BOOK 1
i = 1
while i <= 13:
    j = 1
    while j <= 5:
        image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + "Map_S" + str(i+1).zfill(2) + str(j).zfill(2) + ".png"
        download_and_save_image(image_url, "Maps/Story Maps/Book 1/Chapter " + str(i) + "/" + "Map_S" + str(i+1).zfill(2) + str(j).zfill(2) + ".png")
        j += 1
    i += 1

# Intermissions
image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + "Map_S1501.png"
download_and_save_image(image_url, "Maps/Story Maps/Book 1/Intermission/" + "Map_S1501.png")

image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + "Map_S1601.png"
download_and_save_image(image_url, "Maps/Story Maps/Book 1/Intermission/" + "Map_S1601.png")

# Aether Raids
i = 1
while i <= 18:
    image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + "Map_K" + str(i).zfill(4) + ".png"
    download_and_save_image(image_url, "Maps/Aether Raids (Templates)/" + "Map_K" + str(i).zfill(4) + ".png")
    i += 1

download_and_save_image("https://feheroes.fandom.com/wiki/Special:Redirect/file/Field_Offense.png", "Maps/Aether Raids (Templates)/Field_Offense.png")

# AR Structures
names = struct_sheet['Name']
offense_exists = struct_sheet['Offense Exists']
defense_exists = struct_sheet['Defense Exists']

i = 1
while i < len(names):
    name = normalize_string(names[i])

    if "False" in name:
        i += 1
        continue

    image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/Structure_" + name + ".png"
    download_and_save_image(image_url, "CombatSprites/AR Structures/" + name + ".png")

    if offense_exists[i] and defense_exists[i]:
        defense_image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/Structure_Enemy_" + name + ".png"
        download_and_save_image(defense_image_url, "CombatSprites/AR Structures/" + name + "_Enemy.png")

    i += 1

# Divine Veins
#vein_types = ["Stone", "Flame", "Green", "Haze", "Water", "Ice"]

# No water for now, Wiki doesn't have the image up
vein_types = ["Stone", "Flame", "Green", "Haze", "Ice"]

for vein in vein_types:
    download_and_save_image("https://feheroes.fandom.com/wiki/Special:Redirect/file/Divine_Vein_" + vein + "_Ally.png", "CombatSprites/Vein_" + vein + "_Player.png")
    download_and_save_image("https://feheroes.fandom.com/wiki/Special:Redirect/file/Divine_Vein_" + vein + "_Enemy.png", "CombatSprites/Vein_" + vein + "_Enemy.png")