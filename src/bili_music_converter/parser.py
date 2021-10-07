import re


class Parser:
    bv_p = re.compile('BV[0-9A-Za-z]{10}')
    av_p = re.compile('av[0-9]+')

    def __call__(self, ids: [str, list]) -> list:
        if isinstance(ids, str):
            return [self._parser(ids)]
        elif isinstance(ids, list):
            return [self._parser(vid) for vid in ids]
        else:
            raise SyntaxWarning

    def _parser(self, vid) -> dict:
        bv = self.bv_p.search(vid)
        av = self.av_p.search(vid)
        if bv:
            return {bv.string: 'bvid'}
        elif av:
            return {av.string: 'avid'}
        else:
            raise SyntaxWarning
