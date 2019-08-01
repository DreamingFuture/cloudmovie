# 作者 罗晴祯

from pymongo import MongoClient
from selenium import webdriver
import re
import time

# 分类排行榜


def classify_list(db, driver):
    classify = [
        'dra_list',
        'com_list',
        'act_list',
        'rom_list',
        'sci_list',
        'ani_list',
        'mys_list',
        'thr_list',
        'hor_list',
        'doc_list',
        'sho_list',
        'adu_list',
        'lov_list',
        'mus_list',
        'rev_list',
        'hom_list',
        'kid_list',
        'bio_list',
        'his_list',
        'war_list',
        'cri_list',
        'wes_list',
        'fan_list',
        'adv_list',
        'dis_list',
        'sow_list',
        'cos_list',
        'spo_list',
        'noi_list']
    list_name = [
        '剧情',
        '喜剧',
        '动作',
        '爱情',
        '科幻',
        '动画',
        '悬疑',
        '惊悚',
        '恐怖',
        '纪录片',
        '短片',
        '情色',
        '同性',
        '音乐',
        '歌舞',
        '家庭',
        '儿童',
        '传记',
        '历史',
        '战争',
        '犯罪',
        '西部',
        '奇幻',
        '冒险',
        '灾难',
        '武侠',
        '古装',
        '运动',
        '黑色电影']
    film_list = driver.find_element_by_class_name('types')
    film_list = film_list.find_elements_by_xpath('.//a')
    film_list = [i.get_attribute("href") for i in film_list]
    film_list = {classify[i]: film_list[i] for i in range(0, len(classify))}
    n = -1
    for i, j in film_list.items():
        n = n + 1
        collection = db[i]
        driver.get(j)
        time.sleep(2)
        for k in range(1, 21):
            try:
                dict = {}
                title_and_url = driver.find_element_by_xpath(
                    '//*[@id="content"]/div/div[1]/div[6]/div[{}]/div/div/div[1]/span[1]/a'.format(str(k)))  # 片名和链接的元素
                title = title_and_url.text  # 片名
                url = title_and_url.get_attribute('href')  # 详情页链接
                movie_id = int(url.split('subject/')[1][:-1])
                ranking = k  # 排名
                others = driver.find_element_by_xpath(
                    '//*[@id="content"]/div/div[1]/div[6]/div[{}]'.format(str(k)))
                others = others.find_element_by_class_name(
                    'rating_num').text  # 评分
                dict['refresh_date'] = time.strftime("%Y-%m-%d", time.localtime())   # 字典添加元素
                dict['list_name'] = list_name[n]
                dict['title'] = title
                dict['ranking'] = int(ranking)
                dict['others'] = float(others)
                dict['movie_id'] = movie_id
                collection.insert_one(dict)
            except BaseException:
                break


# 北美票房榜


def ameboxoff_list(db, driver):
    collection = db.ameboxoff_list  # 获取集合
    for k in range(1, 11):
        dict = {}
        title = driver.find_element_by_xpath(
            '''//*[@id="listCont1"]/li[{}]/div[2]/a'''.format(str(k))).text  # 片名
        url = driver.find_element_by_xpath(
            '''//*[@id="listCont1"]/li[{}]/div[2]/a'''.format(str(k))).get_attribute("href")  # 电影详情页链接
        movie_id = int(url.split('subject/')[1][:-1])
        ranking = k  # 排名
        others = driver.find_element_by_xpath(
            '''//*[@id="listCont1"]/li[{}]/span'''.format(str(k))).text  # 票房
        dict['refresh_date'] = time.strftime("%Y-%m-%d", time.localtime())  # 字典添加元素
        dict['title'] = title
        dict['ranking'] = ranking
        dict['others'] = int(others.split('万')[0])
        dict['movie_id'] = movie_id
        collection.insert_one(dict)

# 一周口碑榜


def pubpra_list(db, driver):
    collection = db.pubpra_list  # 获取集合
    for j in range(1, 11):
        dict = {}
        title = driver.find_element_by_xpath(
            '''//*[@id="listCont2"]/li[{}]/div[2]/a'''.format(str(j))).text  # 片名
        url = driver.find_element_by_xpath(
            '''//*[@id="listCont2"]/li[{}]/div[2]/a'''.format(str(j))).get_attribute("href")  # 电影详情页链接
        movie_id = int(url.split('subject/')[1][:-1])
        ranking = j  # 排名
        up_down = driver.find_element_by_xpath(
            '''//*[@id="listCont2"]/li[{}]/span/div'''.format(str(j))).get_attribute("class")
        if up_down == 'up':
            others = '+' + driver.find_element_by_xpath(
                '''//*[@id="listCont2"]/li[{}]/span/div'''.format(str(j))).text  # 评分
        else:
            others = '-' + driver.find_element_by_xpath(
                '''//*[@id="listCont2"]/li[{}]/span/div'''.format(str(j))).text  # 评分
        dict['refresh_date'] = time.strftime("%Y-%m-%d", time.localtime())  # 字典添加元素
        dict['title'] = title
        dict['ranking'] = ranking
        dict['others'] = str(others)
        dict['movie_id'] = movie_id
        collection.insert_one(dict)


def main():
    driver = webdriver.Firefox()
    url = "https://movie.douban.com/chart"
    driver.get(url)
    driver.maximize_window()
    client = MongoClient()  # 建立连接
    db = client.movie_info  # 获取数据库
    ameboxoff_list(db, driver)
    pubpra_list(db, driver)
    classify_list(db, driver)
    driver.close()


if __name__ == '__main__':
    main()
