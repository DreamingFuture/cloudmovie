# 作者 宋叮咛

from selenium import webdriver
from pymongo import MongoClient
import time


def main():
    # 连接数据库, 保存排行榜基本信息
    client = MongoClient()
    db = client['movie_info']
    collection = db['homboxoff_list']
    # doc = {}
    # doc['type'] = 'homboxoff_list'
    # doc['refresh_date'] = time.strftime("%Y-%m-%d", time.localtime())
    # collection.insert_one(doc)

    # 爬取资源
    url = r'http://www.cbooo.cn/realtime'
    driver = webdriver.Firefox()
    driver.set_page_load_timeout(20)
    try:
        driver.get(url)
    except BaseException:
        driver.execute_script('window.stop()')

    # 获取电影列表
    film_list = driver.find_element_by_id('table_content')
    film_list = film_list.find_elements_by_tag_name('tr')
    driver_copy = webdriver.Firefox()
    for each_film in film_list[:-1]:
        rankingandtitle = each_film.find_element_by_xpath(
            './td[1]/a').text.split('.\n')
        ranking = int(rankingandtitle[0])
        title = rankingandtitle[1]
        box_office = []
        box_office.append(
            int(float(each_film.find_element_by_xpath('./td[2]').text)))
        box_office.append(
            int(float(each_film.find_element_by_xpath('./td[5]').text)))
        url = 'https://movie.douban.com/subject_search?search_text={0}&cat=1002'.format(
            title)

        # 获取豆瓣详情页链接
        driver_copy.get(url)
        url = driver_copy.find_element_by_class_name(
            'sc-bZQynM').find_element_by_class_name('cover-link').get_attribute('href')
        movie_id = int(url.split('subject/')[1][:-1])

        # 保存资源
        doc = {}
        doc['refresh_date'] = time.strftime("%Y-%m-%d", time.localtime())
        doc['ranking'] = int(ranking)
        doc['title'] = title
        doc['others'] = box_office
        doc['movie_id'] = movie_id
        collection.insert_one(doc)

    driver.close()
    driver_copy.close()


if __name__ == '__main__':
    main()
