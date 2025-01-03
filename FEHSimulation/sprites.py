# https://feheroes.fandom.com/wiki/Special:Redirect/file/Alfonse_Prince_of_Askr_Mini_Unit_Ok.png

import requests
from hero import hero_sheet, Hero, implemented_heroes
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

    # If image is currently of a character in this current build
    if int_name in implemented_heroes:

    # Only to be used for getting the most recent units for development, comment back as soon as you're done!
    #if True:
        download_and_save_image(image_url, "TestSprites/" + int_name + ".png")

        if has_resp == True:
            resp_image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + name + "_" + epithet + "_Resplendent_Mini_Unit_Ok.png"
            save_name = int_name + "-R"
            #download_and_save_image(resp_image_url, save_name)

        if weapon in ["RBeast", "BBeast", "GBeast", "CBeast"]:
            beast_image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + name + "_" + epithet + "_TransformMap_Mini_Unit_Idle.png"
            beast_name = int_name + "-Tr"
            download_and_save_image(beast_image_url, "TestSprites/" + beast_name + ".png")

    i += 1

i = 1
#i = 101
while i < 25:
    image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + "Map_Z" + str(i).zfill(4) + ".png"
    download_and_save_image(image_url, "Maps/Arena Maps/" + "Map_Z" + str(i).zfill(4) + ".png")
    i += 1

# 'https://feheroes.fandom.com/wiki/Special:Redirect/file/Seidr_Goddess_of_Hope_Mini_Unit_Ok.png'

#image_url = 'https://feheroes.fandom.com/wiki/Special:Redirect/file/Alfonse_Prince_of_Askr_Mini_Unit_Ok.png'
#sample_save_path = 'TestSprites\\downloaded_image.png'
#download_and_save_image(image_url, save_path)

# Importing maps
# 'https://feheroes.fandom.com/wiki/Special:Redirect/file/Map_Z0096.png'