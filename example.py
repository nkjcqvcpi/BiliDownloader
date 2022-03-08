from src.bili_downloader import BiliDownloader

if __name__ == '__main__':
    d = BiliDownloader('b4f0af61%2C1659237450%2C8f896*21', dl_path='/Users/houtonglei/Downloads')
    d(['https://www.bilibili.com/video/BV15m4y1S7mD?from=search&seid=17188264315147612371&spm_id_from=333.337.0.0',
       'https://www.bilibili.com/video/BV1QL4y147wM?from=search&seid=1314050971745667139&spm_id_from=333.337.0.0'])

