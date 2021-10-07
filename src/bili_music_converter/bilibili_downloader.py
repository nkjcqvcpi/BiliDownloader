import json
import os
import subprocess
import tempfile
import time
import logging

import cv2
import requests
from mutagen.mp4 import MP4, MP4Cover

from .parser import Parser


class BiliDownloader:
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    download_api = 'https://api.bilibili.com/x/player/playurl'
    info_api = 'https://api.bilibili.com/x/web-interface/view'

    def __init__(self, sessdata, dl_path=None):
        self.parser = Parser()
        self.params = {'cid': None, 'fnval': 16}
        self.header = {'User-Agent': self.ua,
                       'Referer': 'https://www.bilibili.com', 'Accept': '*/*', 'Origin': 'https://www.bilibili.com',
                       'Accept-Language': 'zh-cn', 'Range': None, 'Host': None, 'Accept-Encoding': 'identity',
                       'Connection': 'keep-alive'}
        self.cookie = {'SESSDATA': sessdata}
        self.dl_path = dl_path or ''

    def download(self, ids, dl_path=None):
        self.dl_path = dl_path or self.dl_path
        vids = self.parser(ids)

        logging.info('Download Pending Video:')

        for vid in vids:
            param = {v: k for k, v in vid.items()}
            v_info = json.loads(requests.get(self.info_api, params=param, cookies=self.cookie).text)['data']
            self.params.update(param)
            for p in [{'cid': p['cid'], 'name': p['part']} for p in v_info['pages']]:
                self.params['cid'] = p['cid']
                p_info = json.loads(requests.get(self.download_api, params=self.params, cookies=self.cookie).text)
                url = p_info['data']['dash']['audio'][0]['baseUrl']
                audio = requests.get(url, headers=self.header, cookies=self.cookie)

                with tempfile.TemporaryDirectory() as tmpdirname:
                    fp = os.path.join(tmpdirname, 'audio.m4s')
                    with open(fp, mode='wb') as f:
                        f.write(audio.content)
                    dl_file = self._convert(fp, v_info, p['name'], dl_path)
                    self._cover(tmpdirname, v_info['pic'], dl_file)

    @staticmethod
    def _cover(tempdir, pic_url, dl_path):
        pp = os.path.join(tempdir, 'cover.jpg')
        with open(pp, mode='wb') as cover:
            cover.write(requests.get(pic_url).content)
        cover = cv2.imread(pp)
        h, w, _ = cover.shape
        if h % 2 == 1:
            h -= 1
        if w % 2 == 1:
            w -= 1
        cv2.imwrite(pp, cover[:h, :w])

        audio = MP4(dl_path)
        with open(pp, "rb") as f:
            audio["covr"] = [MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_PNG)]
        audio.save()

    @staticmethod
    def _metadata(info, name):
        __metadata = {'description': '',
                      'title': name, 'artist': info['owner']['name'],
                      'album': info['title'], 'album_artist': info['owner']['name'],
                      'date': time.localtime(info['pubdate']).tm_year, 'comment': info['desc']}
        _metadata = []
        for k, v in __metadata.items():
            _metadata.append('-metadata')
            _metadata.append('%s=%s' % (k, v))
        return _metadata, name + '.m4a'

    def _convert(self, fp, info, p_name, dl_path):
        metadata, filename = self._metadata(info, p_name)
        dl_path = os.path.join(dl_path, filename) if dl_path else filename
        cmd = ['ffmpeg', '-i', fp, '-c', 'copy', '-y'] + metadata + [dl_path]
        subprocess.run(cmd)
        return dl_path
