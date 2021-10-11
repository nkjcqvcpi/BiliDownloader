import os
import subprocess
import tempfile
import time
import shutil
import logging

import cv2
import requests
from mutagen.mp4 import MP4, MP4Cover


class Music:
    def __init__(self, header, cookie, v_info, p_info, p, dl_path):
        self.url = p_info['dash']['audio'][0]['baseUrl']
        self.header = header
        self.cookie = cookie
        self.filename = p['name'] + '.m4a'
        self.metadata = {'description': '',
                         'title': p['name'], 'artist': v_info['owner']['name'],
                         'album': v_info['title'], 'album_artist': v_info['owner']['name'],
                         'date': time.localtime(v_info['pubdate']).tm_year, 'comment': v_info['desc']}

        with tempfile.TemporaryDirectory() as self.tmpdir:
            self.ori_path = os.path.join(self.tmpdir, 'audio.m4s')
            self.path = os.path.join(self.tmpdir, self.filename)
            self.cover_path = os.path.join(self.tmpdir, 'cover.jpg')

            self.download(header, cookie)
            self._convert()
            self._cover(v_info['pic'])
            self.save(dl_path)

    def download(self, header, cookie):
        audio = requests.get(self.url, headers=header, cookies=cookie)
        with open(self.ori_path, mode='wb') as f:
            f.write(audio.content)

    def save(self, path):
        shutil.move(self.path, os.path.join(path, self.filename))

    def _convert(self):
        metadata = []
        for k, v in self.metadata.items():
            metadata.append('-metadata')
            metadata.append('%s=%s' % (k, v))
        cmd = ['ffmpeg', '-i', self.ori_path, '-c', 'copy', '-y'] + metadata + [self.path]
        subprocess.run(cmd)

    def _cover(self, pic_url):
        pp = os.path.join(self.tmpdir, 'cover.jpg')
        with open(pp, mode='wb') as cover:
            cover.write(requests.get(pic_url).content)
        cover = cv2.imread(pp)
        h, w, _ = cover.shape
        if h % 2 == 1:
            h -= 1
        if w % 2 == 1:
            w -= 1
        cv2.imwrite(pp, cover[:h, :w])

        audio = MP4(self.path)
        with open(pp, "rb") as f:
            audio["covr"] = [MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_PNG)]
        audio.save()
