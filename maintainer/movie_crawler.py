# 原作者 李靖
# 代码重构 宋叮咛

import pymongo
import time
import requests
import os
import re
from bs4 import BeautifulSoup


def get_response(url):
    # 多次请求请求失败的链接
    while True:
        try:
            response = requests.get(url)
            break
        except BaseException:
            pass
    return response


def pic_hunter(url, file_name, pic_type, movie_id):
    # type == 1: 电影海报, type == 2: 剧照, type == 3: 相关电影海报, type == 4: 演职人员图片

    if pic_type == 1:
        path = r'{0}\resource\movie_info\{1}\poster'.format(
            os.path.abspath('..'), movie_id)
    elif pic_type == 2:
        path = r'{0}\resource\movie_info\{1}\stills'.format(
            os.path.abspath('..'), movie_id)
    elif pic_type == 3:
        path = r'{0}\resource\movie_info\{1}\relmovpos'.format(
            os.path.abspath('..'), movie_id)
    else:
        path = r'{0}\resource\movie_info\{1}\casts'.format(
            os.path.abspath('..'), movie_id)

    if not os.path.exists(path):
        os.makedirs(path)

    if not len(url):
        return

    image = get_response(url)
    pic_type = image.headers['content-type'].split('/')[1]



    path = r'{0}\{1}.{2}'.format(path, file_name, pic_type)
    file = open(path, 'wb')
    file.write(image.content)
    file.close()

    return path


def save(data):
    client = pymongo.MongoClient()
    db = client.movie_info
    collection = db.movie_info
    collection.insert_one(data)


def get_data_movie_info_basic_info(html, url, movie_id, stills):
    data = {}
    soup = BeautifulSoup(html, 'lxml')
    info_tag = soup.find('div', id='info')
    # 电影id
    data['movie_id'] = int(movie_id)
    # 检测电影是否存在
    if soup.html.head.title.string == '页面不存在':
        print('电影不存在!', end="")
        data['title'] = None
        return data
    # 片名
    title = soup.find('div', class_='aside').find("p", class_="pl").next_element.string[2:][:-5]
    title = re.sub('[*/]', '', title)
    data['title'] = title
    print(title + " ", end="")
    # 导演
    directors = []
    for each_director in info_tag.find_all('a', rel='v:directedBy'):
        directors.append(each_director.string)
    if not len(directors):
        directors = None
    data['directors'] = directors
    # 编剧
    writers = []
    for each_child in info_tag.children:
        if '编剧' in str(each_child):
            for each_writer in each_child.find_all('a'):
                writers.append(each_writer.string)
    if not len(writers):
        writers = None
    data['writers'] = writers
    # 主演
    stars = []
    for each_child in info_tag.children:
        if '主演' in str(each_child):
            for each_star in each_child.find_all('a'):
                stars.append(each_star.string)
    if not len(stars):
        stars = None
    data['stars'] = stars
    # 制片国家地区
    coungion = None
    for each_child in info_tag.children:
        if '制片国家/地区:' in str(each_child):
            coungion = each_child.next_sibling.string
            break
    data['coungion'] = coungion
    # 语言
    language = None
    for each_child in info_tag.children:
        if '语言' in str(each_child):
            language = each_child.next_sibling.string
            break
    data['language'] = language
    # 上映日期
    release_date = ''
    for release_date_ in info_tag.find_all(
            'span', property='v:initialReleaseDate'):
        release_date = release_date + release_date_.string + '/'
    if release_date == '':
        release_date = None
    else:
        release_date = release_date[:-1]
    data['release_date'] = release_date
    # 片长
    runtime = None
    try:
        runtime = int(info_tag.find('span', property='v:runtime')['content'])
    except BaseException:
        for each_child in info_tag.children:
            if '片长' in str(each_child):
                runtime = each_child.next_sibling.string
                runtime = re.sub('[分:m]+.*', '', runtime)
                runtime = int(runtime)
                break
    data['runtime'] = runtime
    # 类型
    genres = [
        each_genre.string for each_genre in info_tag.find_all(
            'span', property='v:genre')]
    if not len(genres):
        genres = None
    data['genres'] = genres
    # 评分
    try:
        rating = float(soup.find('strong', class_='ll rating_num').string)
    except BaseException:
        rating = None
    data['rating'] = rating
    # 评分人数
    try:
        rating_count = int(soup.find('span', property='v:votes').string)
    except BaseException:
        rating_count = None
    data['rating_count'] = rating_count
    # 演职人员数量
    cast_count = None
    try:
        cast_count = int(
            soup.find(
                id='celebrities').h2.span.a.get_text().split()[1])
    except BaseException:
        cast_count = None
    data['cast_count'] = cast_count
    # 短评数量
    comment_father = soup.find('div', class_='mod-hd')
    if not comment_father:
        comment_count = None
    else:
        comment_count_str = comment_father.find('span', class_='pl').a.string
        comment_count = int(re.search(r'\d+', comment_count_str).group())
    data['comment_count'] = comment_count
    # 海报图片
    poster_path = soup.find('img', rel='v:image')['src']
    pic_hunter(poster_path, movie_id, 1, movie_id)
    # 演职人员信息
    if not cast_count:
        one_duty = None
    else:
        url = 'https://movie.douban.com' + \
            soup.find('div', id='celebrities').h2.span.a['href']
        html = get_response(url).text
        duty_list = BeautifulSoup(html, 'lxml').find_all(class_='list-wrapper')
        one_duty = {}
        for each_duty in duty_list:
            duty_total = each_duty.h2.get_text()
            temp = []
            people = each_duty.find_all('li', class_='celebrity')
            for each_people in people:
                name = each_people.a['title'].strip()
                image_path_str = each_people.a.div['style']
                image_path = re.findall(r'http.+?\)', image_path_str)[-1]
                image_path = image_path[:-1]
                pic_hunter(image_path, name, 4, movie_id)
                try:
                    duty = each_people.find(class_='role').get_text()
                except BaseException:
                    duty = None
                each_people_info = {}
                each_people_info['name'] = name
                each_people_info['duty'] = duty
                temp.append(each_people_info)
            one_duty[duty_total] = temp
    data['cast_info'] = one_duty
    # 想看的人数
    try:
        like_count = int(
            soup.find(
                class_='subject-others-interests-ft').a.get_text().split('人')[0])
    except BaseException:
        like_count = None
    data['like_count'] = like_count
    # 剧情简介
    storyline = soup.find('span', class_=['all', 'hidden'])
    if not storyline:
        storyline = soup.find('span', property='v:summary')
    if not storyline:
        storyline = None
    else:
        storyline = storyline.get_text('\\n', strip=True)
    data['storyline'] = storyline
    # 相关电影名及照片路径
    relative_movie = []
    for movie in soup.find_all('dl', class_=''):
        film_name = movie.dt.a.img['alt']
        film_name = re.sub(r'[*/\:?<>|"]', '', film_name)
        poster = movie.dt.a.img['src']
        pic_hunter(poster, film_name, 3, movie_id)
        relative_movie.append(film_name)
    if not len(relative_movie):
        relative_movie = None
    data['relative_movie'] = relative_movie
    # 剧照
    img_url = soup.find('div', id='related-pic').h2.span
    if not img_url:
        stills_filename = None
    else:
        for sibling in img_url.find_all('a'):
            if '图片' in str(sibling):
                img_url = sibling['href']
                break
        imgs_html = get_response(img_url).text
        imgs_soup = BeautifulSoup(
            imgs_html, 'lxml').find(
            'ul', class_='pic-col5')
        if not imgs_soup:
            stills_filename = None
        else:
            stills_filename = []
            for each in imgs_soup.find_all('li', class_=''):
                path = "https://img3.doubanio.com/view/photo/l/public" + \
                    each.a.img['src'].split("public")[1]
                filename = each.a.img['src'].split("public/")[1][:-4]
                stills_filename.append(filename)
                path = pic_hunter(path, filename, 2, movie_id)
                stills.insert(0, path)
            if not len(stills_filename):
                stills_filename = None
    data['stills_filename'] = stills_filename

    return data

def stills_length_check(stills):
    if len(stills) > 50:
        print("缩略图队列过长，正在等待缩略图生成器生成缩略图")
        while 1:
            if len(stills) > 50:
                time.sleep(2)
            else:
                break

def main(lack_movie, stills):
    for num, movie_id in enumerate(lack_movie, start=1):
        print('第{0}部，movie_id: {1} '.format(num, movie_id), end="")
        url = 'https://movie.douban.com/subject/{0}/'.format(movie_id)
        html = get_response(url).text
        save(get_data_movie_info_basic_info(html, url, movie_id, stills))
        print('爬取完毕')
        stills_length_check(stills)
        time.sleep(2)
