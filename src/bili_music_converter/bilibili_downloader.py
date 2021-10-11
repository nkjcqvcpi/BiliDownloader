import json
import logging

import requests

from .parser import Parser
from .music import Music


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

        logging.info('\nDownload Pending Video:')

        for vid in vids:
            param = {v: k for k, v in vid.items()}
            v_info = json.loads(requests.get(self.info_api, params=param, cookies=self.cookie).text)['data']
            self.params.update(param)
            print('Downloading Videos:', v_info['title'])
            for p in [{'cid': p['cid'], 'name': p['part']} for p in v_info['pages']]:
                print('    downloading video:', p['name'])
                self.params['cid'] = p['cid']
                p_info = json.loads(requests.get(self.download_api, params=self.params, cookies=self.cookie).text)
                m = Music(self.header, self.cookie, v_info, p_info['data'], p, self.dl_path)
