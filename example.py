from src.bili_music_converter import BiliDownloader

if __name__ == '__main__':
    d = BiliDownloader('eec47000%2C1630908984%2Cb1fe7*31')
    d.download(['https://www.bilibili.com/video/BV1Y7411W7iQ?spm_id_from=333.999.0.0',
                'https://www.bilibili.com/video/BV1u7411V7E5?spm_id_from=333.999.0.0',
                'https://www.bilibili.com/video/BV1FE411s7h1?spm_id_from=333.999.0.0',
                'https://www.bilibili.com/video/BV1Lp4y1C7Bq?spm_id_from=333.999.0.0',
                'https://www.bilibili.com/video/BV1AV411d7oJ?spm_id_from=333.999.0.0',
                'https://www.bilibili.com/video/BV1Qf4y117e7?spm_id_from=333.999.0.0',
                'https://www.bilibili.com/video/BV1Ey4y1C7Pa?spm_id_from=333.999.0.0',
                'https://www.bilibili.com/video/BV1Hh411f7Ty?spm_id_from=333.999.0.0',
                'https://www.bilibili.com/video/BV1m64y1X7qk?spm_id_from=333.999.0.0',
                'https://www.bilibili.com/video/BV1XP4y1s7Tp?spm_id_from=333.999.0.0'])
