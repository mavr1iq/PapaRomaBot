import os.path

import pyktok as pyk
import requests
import time
import instaloader
import yt_dlp
from gallery_dl import config, job
from gallery_dl.job import DataJob
from pandas.core.indexes import extension
from yt_dlp.globals import extractors

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
        paths = []
        audio: bool = True
        count += 1
        for i in range(1, count):
            paths.append(f'{i}.jpg')

        response = {
            "url": url,
            "video": video,
            "paths": paths,
            "count": count,
            "audio": audio,
        }

    return response


async def get_instagram(url):
    url = url.split('?')[0]
    path = 'reel'
    video = False
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
    video = True if os.path.isfile(f"{path}/{path}.mp4") else video
    new_path = f"{path}/{path}.jpg" if os.path.isfile(f"{path}/{path}.jpg") else f"{path}/{path}.mp4"
    paths = []

    while os.path.isfile(f"{path}/{path}_{count}.jpg"):
        new_path = f"{path}/{path}_"
        paths.append(new_path+f"{count}.jpg")
        video = False
        count += 1

    if video:
        paths = new_path

    count = None if count == 1 else count

    print(paths)

    response = {
        "url": url,
        "video": video,
        "paths": paths,
        "path": paths,
        "count": count
    }

    return response


async def get_twitter(url, quote = False):
    config.set(("extractor", "twitter"), "quoted", True)
    config.set(("extractor", "twitter"), "text-tweets", True)

    data = DataJob(url)
    data.run()
    data = data.data

    url = url.split('?')[0]
    path = f'gallery-dl/twitter/{data[0][1]['author']['name']}'
    ydl_opts = {
        'outtmpl': path,
        'format_sort': ['res:1080', 'ext:mp4:m4a']
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if not quote:
                urls = [None, None]

                for i in data:
                    print(i)
                    if i[0] == 2 and i[1]['quote_id'] != 0:
                        urls[0] = f'https://x.com/{i[1]['author']['name']}/status/{i[1]['tweet_id']}'
                        break
                    if i[0] == 2 and i[1]['quote_id'] == 0:
                        urls[1] = f'https://x.com/{i[1]['author']['name']}/status/{i[1]['tweet_id']}'

                config.set(("extractor", "twitter"), "quoted", False)
                config.set(("extractor", "twitter"), "text-tweets", False)

                if urls[0]:
                    print(quote)
                    print(urls)
                    posts = [None, None]
                    posts[0] = await get_twitter(urls[0], quote=True)
                    posts[1] = await get_twitter(urls[1], quote=True)

                    print('posts')
                    print(posts)

                    response = {
                        "quoting": True,
                        "posts": posts,
                    }
                    print(response)
                    return response

            ydl.download([url])
            info = ydl.extract_info(url, download=False)

            print(info.keys())
            ext = info['ext'] if 'ext' in info.keys() else info['entries'][0]['formats'][0]['ext']
            title = info['description']
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
        config.set(("downloader",), "filename", f"{path}.jpg")
        j = job.DownloadJob(url)
        j.run()

        result = None
        for result in j.extractor:
            if result:
                result = result
                break

        print(f'test{result}')
        if result and os.path.isdir(f'gallery-dl/twitter/{result[1]['author']['name']}'):
            result = result[1]
            title = result['content']
            user = result['author']['name']
            tweet_id = str(url.split("/")[5])

            paths = []
            for f in os.listdir(f'gallery-dl/twitter/{user}'):
                if tweet_id in f:
                    paths.append(f'gallery-dl/twitter/{user}/{f}')

            print(f'paths{paths}')

            response = {
                "url": url,
                "title": title,
                "paths": paths,
                "video": False,
                "count": len(paths),
            }
        else:
            print(data)
            title = data[0][1]['content']
            response = {
                "url": url,
                "title": title,
                "video": False,
                "text": True,
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
