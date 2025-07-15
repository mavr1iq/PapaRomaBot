import pyktok as pyk
import requests
import time

def get_tiktok(url):
    if 'video' in url:
        pyk.save_tiktok(url, True)
        time.sleep(3)
        video = True
        path = '@' + url.split("@")[1].replace('/', '_')

        return url, path, video

    elif 'photo' in url:
        url = url.replace('photo', 'video')
        tt_json = pyk.alt_get_tiktok_json(video_url=url)
        data_slot = tt_json["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]
        urls: list[str] = [img["imageURL"]["urlList"][0] for img in data_slot["imagePost"]["images"]]
        imgs: list[bytes] = [requests.get(url).content for url in urls]
        count = len(imgs)

        for idx, img in enumerate(imgs):
            with open(f"{idx}.jpg", "wb") as f:
                f.write(img)
            print(f"Saved {idx}.jpg")

        audio_url = data_slot["music"]["playUrl"]
        if audio_url == "":
            print("No audio found!")
        else:
            audio: bytes = requests.get(audio_url).content
            with open("audio.mp3", "wb") as f:
                f.write(audio)
            print("Saved audio.mp3")

        video = False
        path = 'audio.mp3'

        return url, path, video, count

