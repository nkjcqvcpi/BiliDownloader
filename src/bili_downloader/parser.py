import re


class Parser:
    bv_p = re.compile('BV[0-9A-Za-z]{10}')
    av_p = re.compile('av[0-9]+')

    def __call__(self, ids: [str, list, tuple]) -> list:
        if isinstance(ids, str):
            return [self._parser(ids)]
        elif isinstance(ids, list) or isinstance(ids, tuple):
            return [self._parser(vid) for vid in ids]
        else:
            raise SyntaxWarning

    def _parser(self, vid) -> dict:
        bv = self.bv_p.search(vid)
        av = self.av_p.search(vid)
        if bv:
            return {bv.group(): 'bvid'}
        elif av:
            return {av.group(): 'avid'}
        else:
            raise SyntaxWarning


if __name__ == '__main__':
    url = 'https://www.bilibili.com/video/BV16R4y1M7XC?from=search&seid=772507573660196375&spm_id_from=333.337.0.0'
    p = Parser()
    p(url)
