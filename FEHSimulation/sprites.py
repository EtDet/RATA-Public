# https://feheroes.fandom.com/wiki/Special:Redirect/file/Alfonse_Prince_of_Askr_Mini_Unit_Ok.png

import requests
from hero import hero_sheet, Hero
from PIL import Image
from io import BytesIO
import unicodedata


def download_and_save_image(url, save_path):
    response = requests.get(url)

    if response.status_code == 200:

        image = Image.open(BytesIO(response.content))

        final_save_path = 'TestSprites\\' + save_path + ".png"

        image.save(final_save_path)

        print(f"Image successfully saved to {final_save_path}")
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
while i < len(names):
    name = normalize_string(names[i])
    int_name = int_names[i]
    epithet = normalize_string(epithets[i])
    has_resp = has_resps[i]
    weapon = weapons[i]

    #print(name + "_" + epithet)

    image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + name + "_" + epithet + "_Mini_Unit_Ok.png"

    #download_and_save_image(image_url, int_name)

    if has_resp == True:
        resp_image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + name + "_" + epithet + "_Resplendent_Mini_Unit_Ok.png"
        save_name = int_name + "-R"
        #download_and_save_image(resp_image_url, save_name)

    if weapon in ["RBeast", "BBeast", "GBeast", "CBeast"]:
        beast_image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + name + "_" + epithet + "_TransformMap_Mini_Unit_Idle.png"
        beast_name = int_name + "-Tr"
        #download_and_save_image(beast_image_url, beast_name)

    i += 1

i = 1
while i < 96:
    image_url = "https://feheroes.fandom.com/wiki/Special:Redirect/file/" + "Map_Z" + str(i).zfill(4) + ".png"

    print(image_url)

    response = requests.get(image_url)

    if response.status_code == 200:

        image = Image.open(BytesIO(response.content))

        final_save_path = 'Maps\\Arena Maps\\' + "Map_Z" + str(i).zfill(4) + ".png"

        image.save(final_save_path)

        print(f"Image successfully saved to {final_save_path}")
    else:
        print(f"Failed to retrieve image. Status code: {response.status_code}")
        break

    i += 1

# 'https://feheroes.fandom.com/wiki/Special:Redirect/file/Seidr_Goddess_of_Hope_Mini_Unit_Ok.png'

#image_url = 'https://feheroes.fandom.com/wiki/Special:Redirect/file/Alfonse_Prince_of_Askr_Mini_Unit_Ok.png'
#sample_save_path = 'TestSprites\\downloaded_image.png'
#download_and_save_image(image_url, save_path)

# Importing maps
# 'https://feheroes.fandom.com/wiki/Special:Redirect/file/Map_Z0095.png'