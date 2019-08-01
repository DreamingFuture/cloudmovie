# 作者 张浩彬

import urllib.request
import parser
import re
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient

# 找到要爬的电影排行


def get_soup_find(soup, collection):

    soup_find = soup.find_all(attrs={'class': 'item'})
    for find in soup_find:
        data = {}
        # 爬取排名
        ranking = re.sub("<[^>]*>", "", str(find.em))
        # 爬取片名
        title = re.sub("<[^>]*>", "", str(find.find(attrs={'class': 'title'})))
        # 爬取评分
        rating = re.sub(
            "<[^>]*>", "", str(find.find(attrs={'class': 'rating_num'})))
        # 爬取链接
        url = find.a['href']
        movie_id = int(url.split('subject/')[1][:-1])

        # 将数据存入data里
        data['refresh_date'] = time.strftime("%Y-%m-%d", time.localtime())
        data['ranking'] = int(ranking)
        data['title'] = str(title)
        data['others'] = float(rating)
        data['movie_id'] = movie_id
        collection.insert_one(data)


def main():
    client = MongoClient()
    db = client['movie_info']
    collection = db['top100_list']
    i = 0
    for i in range(0, 76, 25):
        url = 'https://movie.douban.com/top250?start=%d' % i
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(response, 'lxml')

        get_soup_find(soup, collection)


if __name__ == '__main__':
    main()
