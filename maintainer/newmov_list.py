# 作者 张浩彬

import urllib.request
import time
from pymongo import MongoClient
from bs4 import BeautifulSoup


def main():
    client = MongoClient()
    db = client['movie_info']
    collection = db['newmov_list']
    # doc = {}
    # doc['type'] = 'newmov_list'
    # doc['refresh_date'] = time.strftime("%Y-%m-%d", time.localtime())
    # collection.insert_one(doc)

    url = 'https://movie.douban.com/cinema/nowplaying/beijing/'
    html = urllib.request.urlopen(url).read().decode()
    soup = BeautifulSoup(html, 'lxml')
    film_list = soup.find(name='ul', class_='lists')
    film_list = film_list.find_all(name='li', recursive=False)
    for i, each_film in enumerate(film_list, 1):
        title = each_film['data-title']
        ranking = i
        others = float(each_film['data-score'])
        url = each_film.find(
            name='a', class_='ticket-btn')['href'].split('?')[0]
        movie_id = int(url.split('subject/')[1][:-1])
        doc = {}
        doc['refresh_date'] = time.strftime("%Y-%m-%d", time.localtime())
        doc['title'] = title
        doc['ranking'] = ranking
        doc['others'] = others
        doc['movie_id'] = movie_id
        collection.insert_one(doc)


if __name__ == '__main__':
    main()
