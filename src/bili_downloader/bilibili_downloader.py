import json
import os
import time
import logging
import tempfile
import shutil
from tqdm.auto import tqdm

import subprocess
from pathlib import Path

import requests
import cv2 as cv
from mutagen.mp4 import MP4, MP4Cover

from .parser import Parser


class BiliDownloader:
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    download_api = 'https://api.bilibili.com/x/player/playurl'
    info_api = 'https://api.bilibili.com/x/web-interface/view'

    def __init__(self, sessdata: str, dl_path:str = None):
        """

        :param sessdata: Bilibili Login Cookie
        :param dl_path:
        """
        self.parser = Parser()
        self.params = {'cid': None, 'fnval': 16}
        self.header = {'User-Agent': self.ua, 'Referer': 'https://www.bilibili.com'}
        """, 'Accept': '*/*', 'Origin': 'https://www.bilibili.com',
                       'Accept-Language': 'zh-cn', 'Range': None, 'Host': None, 'Accept-Encoding': 'identity',
                       'Connection': 'keep-alive'}"""
        self.cookie = {'SESSDATA': sessdata}
        self.dl_path = Path.cwd() if not dl_path else Path(dl_path)

    def __call__(self, ids, dl_path:str = None, video=True, apple_music=True):
        self.dl_path = self.dl_path if not dl_path else Path(dl_path)
        vids = self.parser(ids)

        logging.info('\nDownload Pending Video:')

        for vid in vids:
            with tempfile.TemporaryDirectory() as tmpdir:
                param = {v: k for k, v in vid.items()}
                v_info = json.loads(requests.get(self.info_api, params=param, cookies=self.cookie).text)['data']
                self.params.update(param)
                print('\nDownloading Videos:', v_info['title'])

                self.cover_path = os.path.join(tmpdir, 'cover.jpg')
                self.cover(v_info['pic'])

                for p in [{'cid': p['cid'], 'name': p['part']} for p in v_info['pages']]:
                    print('    downloading video:', p['name'])
                    if video:
                        self.video_path = os.path.join(self.dl_path, p['name'] + '.mov')
                    if apple_music:
                        self.music_path = os.path.join(self.dl_path, p['name'] + '.m4a')
                    self.params['cid'] = p['cid']
                    p_info = json.loads(requests.get(self.download_api, params=self.params, cookies=self.cookie).text)
                    self.download(p_info['data'], tmpdir)

                    self.save(tmpdir, p, v_info, apple_music=True, video=True)

    def cover(self, url):
        with open(self.cover_path, mode='wb') as cover:
            cover.write(requests.get(url).content)
        cover = cv.imread(self.cover_path)
        h, w, _ = cover.shape
        if h % 2 == 1:
            h -= 1
        if w % 2 == 1:
            w -= 1
        cv.imwrite(self.cover_path, cover[:h, :w])

    def apple_music(self, tmpdir, p, v_info):
        metadata = {'description': '',
                    'title': p['name'], 'artist': v_info['owner']['name'],
                    'album': v_info['title'], 'album_artist': v_info['owner']['name'],
                    'date': time.localtime(v_info['pubdate']).tm_year, 'comment': v_info['desc']}
        md = []
        for k, v in metadata.items():
            md.append('-metadata')
            md.append('%s=%s' % (k, v))

        cmd = ['ffmpeg', '-i', os.path.join(tmpdir, 'audio.m4s'), '-c', 'copy', '-y'] + md + [self.music_path]
        subprocess.run(cmd)

        audio = MP4(self.music_path)
        with open(self.cover_path, "rb") as f:
            audio["covr"] = [MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_PNG)]
        audio.save()

    def download(self, p_info, tmpdir, audio=True, video=True):
        _ = []
        if audio:
            _ += ['audio']
        if video:
            _ += ['video']
        for i in _:
            url = p_info['dash'][i][0]['baseUrl']
            with requests.get(url, headers=self.header, cookies=self.cookie, stream=True) as r:
                total_length = int(r.headers.get("Content-Length"))
                with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
                    with open(os.path.join(tmpdir, i + '.m4s'), mode='wb') as f:
                        shutil.copyfileobj(raw, f)

    def save(self, tmpdir, p, v_info, apple_music=True, video=True):
        if apple_music:
            self.apple_music(tmpdir, p, v_info)
        if video:
            cmd = ['ffmpeg', '-i', os.path.join(tmpdir, 'video.m4s'), '-i', os.path.join(tmpdir, 'audio.m4s'),
                   '-c', 'copy', '-y', self.video_path]
            subprocess.run(cmd)
