import requests

def is_image(url):

    response = requests.get(url)

    content_type = response.headers.get('Content-Type', '').lower()

    if response.status_code == 200 and content_type == 'image/png':
        print("Valid URL: " + url)
        return 1

    else:
        #print(f"Failed to retrieve image. Status code: {response.status_code}")
        return 0

#link = "https://vote9.campaigns.fire-emblem-heroes.com/_next/static/media/btn_vote-blink.a9d7ebe1.png"
#is_image(link)

i = 10
while i <= 20:
    j = 0

    while j <= 25:
        image_url = "https://vote9.campaigns.fire-emblem-heroes.com/img/1" + str(i).zfill(2) + str(j).zfill(3) + ".png"

        is_image(image_url)

        j += 1

    i += 1
