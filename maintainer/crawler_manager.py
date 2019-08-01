# 作者 宋叮咛

import time
from pymongo import MongoClient
import movie_crawler
import ameboxoff_pubpra_classify_list
import homboxoff_list
import newmov_list
import top100_list
import thumbnail_maker
from multiprocessing import Process
from multiprocessing import Manager

if __name__ == '__main__':
    client = MongoClient()
    db = client['movie_info']

    if input('需要更新排行榜吗？(Y/N)') in ['Y', 'y']:
        for i in [i for i in db.list_collection_names() if 'list' in i]:
            db.drop_collection(i)
        print('正在更新分类榜')
        ameboxoff_pubpra_classify_list.main()
        print('正在更新国内票房榜')
        homboxoff_list.main()
        print('正在更新热议新片榜')
        newmov_list.main()
        print('正在更新top100榜')
        top100_list.main()

    movie = set()
    for i in [i for i in db.list_collection_names() if 'list' in i]:
        collection = db[i]
        movie = movie | set([i['movie_id']
                             for i in collection.find({'movie_id': {'$exists': True}})])

    collection = db['movie_info']
    existed_movie = set([i['movie_id'] for i in collection.find()])

    lack_movie = movie - existed_movie

    print('缺少%d部电影' % len(lack_movie))

    manager = Manager()
    stills = manager.list()
    movie_crawler = Process(target=movie_crawler.main,
                            args=[lack_movie, stills])
    thumbnail_maker_1 = Process(target=thumbnail_maker.main, args=[stills])
    thumbnail_maker_2 = Process(target=thumbnail_maker.main, args=[stills])
    thumbnail_maker_3 = Process(target=thumbnail_maker.main, args=[stills])

    movie_crawler.start()
    thumbnail_maker_1.start()
    thumbnail_maker_2.start()
    thumbnail_maker_3.start()

    movie_crawler.join()
    print("正在等待缩略图生成....")

    while 1:
        if stills:
            time.sleep(2)
        else:
            thumbnail_maker_1.terminate()
            thumbnail_maker_2.terminate()
            thumbnail_maker_3.terminate()
            break
