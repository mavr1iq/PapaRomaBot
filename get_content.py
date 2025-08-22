import os.path

import pyktok as pyk
import requests
import time
import instaloader
import yt_dlp
from gallery_dl import config, job

from yt_dlp.postprocessor import FFmpegPostProcessor
#FFmpegPostProcessor._ffmpeg_location.set(R'ffmpeg/ffmpeg.exe')

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
    url = url.split('?')[0]
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


async def get_twitter(url):
    url = url.split('?')[0]
    path = '1'
    ydl_opts = {
        'outtmpl': path,
        'format_sort': ['res:1080', 'ext:mp4:m4a']
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            print(info.keys())
            ext = info['ext']
            title = info['title']
            if not os.path.exists(f"{path}.{ext}"):
                os.rename(path, f'{path}.{ext}')
            path = f'{path}.{ext}'

            response = {
                "url": url,
                "title": title,
                'path': path,
                'video': True,
            }

    except yt_dlp.utils.DownloadError:
        print(url)
        config.set(("output",), "directory", [path])
        j = job.DownloadJob(url)
        j.run()

        result = None
        for result in j.extractor:
            if result:
                result = result
                break

        result = result[1]
        title = result['content']
        user = result['author']['name']

        path = f'gallery-dl/twitter/{user}/{url.split("/")[5]}'

        new_path = path

        count = 1
        while os.path.isfile(f"{path}_{count}.jpg"):
            new_path = f"{path}_"
            count += 1

        response = {
            "url": url,
            "title": title,
            "path": new_path,
            "video": False,
            "count": count,
        }

    return response


async def get_youtube(url: str):
    if "shorts" in url:
        return await get_twitter(url)

    path = '1'
    duration = 180

    ydl_opts = {
        'outtmpl': path,
        'format_sort': ['res:1080', 'ext:mp4:m4a']
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        ext = info['ext']
        title = info['title']

        if info["duration"] < duration:
            ydl.download([url])
            os.rename(path, f'path.{ext}')
            path = f'path.{ext}'

            response = {
                "url": url,
                "title": title,
                'path': path,
                'video': True,
            }
        else:
            response = {
                "url": url,
                "title": "Занадото довге(",
                'text': True,
            }

    return response
