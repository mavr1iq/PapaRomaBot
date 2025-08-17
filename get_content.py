import os.path

import pyktok as pyk
import requests
import time
import instaloader
from config import INSTA_PASS, INSTA_USER


async def get_tiktok(url):
    url = requests.get(url).url.split('?')[0]
    response = {}
    if 'video' in url:
        pyk.save_tiktok(url, True)
        time.sleep(3)
        video = True
        path = f'@{url.split("@")[1].replace('/', '_')}.mp4'

        response = {
            "url": url,
            "video": video,
            "path": path
        }

    elif 'photo' in url:
        url = url.replace('photo', 'video')
        tt_json = pyk.alt_get_tiktok_json(video_url=url)
        data_slot = tt_json["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]
        urls: list[str] = [img["imageURL"]["urlList"][0] for img in data_slot["imagePost"]["images"]]
        imgs: list[bytes] = [requests.get(url).content for url in urls]
        count = len(imgs)

        for idx, img in enumerate(imgs):
            with open(f"{idx+1}.jpg", "wb") as f:
                f.write(img)
            print(f"Saved {idx+1}.jpg")

        audio_url = data_slot["music"]["playUrl"]
        if audio_url == "":
            print("No audio found!")
        else:
            audio: bytes = requests.get(audio_url).content
            with open("audio.mp3", "wb") as f:
                f.write(audio)
            print("Saved audio.mp3")


        video = False
        path = ''
        audio: bool = True
        count += 1

        response = {
            "url": url,
            "video": video,
            "path": path,
            "count": count,
            "audio": audio,
        }

    return response


async def get_instagram(url):
    path = 'reel'
    video = True
    reel_id = url.split('/')[-2]
    loader = instaloader.Instaloader(
    save_metadata=False,
    download_comments=False,
    download_video_thumbnails=False,
    post_metadata_txt_pattern="")

    try:
        loader.load_session_from_file(username=INSTA_USER, filename='profile')
    except:
        loader.login(INSTA_USER, INSTA_PASS)
        loader.save_session_to_file('profile')

    loader.filename_pattern = path
    print('Downloading reel: ', url)
    reel = instaloader.Post.from_shortcode(loader.context,reel_id)
    loader.download_post(reel, path)

    count = 1
    video = False if os.path.isfile(f"{path}/{path}.jpg") else video
    new_path = f"{path}/{path}.jpg" if os.path.isfile(f"{path}/{path}.jpg") else f"{path}/{path}.mp4"

    while os.path.isfile(f"{path}/{path}_{count}.jpg"):
        new_path = f"{path}/{path}_"
        video = False
        count += 1

    count = None if count == 1 else count

    response = {
        "url": url,
        "video": video,
        "path": new_path,
        "count": count
    }

    return response