# import json
from django.core.paginator import Paginator
# from django.http import JsonResponse
from django.shortcuts import render_to_response, HttpResponse
from .models import client


# Create your views here.

# 存在电影数据，添加到字典中
# 并进行除去None
def add_dic(info):
    try:
        info['directors'] = '\\'.join(client.movie_info.find_one({'movie_id': info['movie_id']})['directors'])
    except TypeError:
        info['directors'] = '无数据'
    try:
        info['writers'] = '\\'.join(client.movie_info.find_one({'movie_id': info['movie_id']})['writers'])
    except TypeError:
        info['writers'] = '无数据'
    info['release_date'] = client.movie_info.find_one({'movie_id': info['movie_id']})['release_date']
    info['rating_count'] = client.movie_info.find_one({'movie_id': info['movie_id']})['rating_count']
    info['poster'] = r'/image/poster/?movie_id={}&file_name={}'.format(info['movie_id'], info['movie_id'])
    if info['release_date'] is None:
        info['release_date'] = '无数据'
    if info['rating_count'] is None:
        info['rating_count'] = 0


# 不存在电影数据，添加数据为无
def add_none(info):
    info['directors'] = '无数据'
    info['writers'] = '无数据'
    info['release_date'] = '无数据'
    info['rating_count'] = 0
    info['poster'] = None


# 分页
def pages(names, page):
    paginator = Paginator(names, 10)
    names = paginator.page(page)
    return names


# 排序
def sort(sort_resource, movielist):
    count_list = sorted(sort_resource, key=lambda x: x[1], reverse=True)
    # 根据排序 写入排名
    dic = {}
    info_new = []
    for i in range(len(movielist)):
        info_new.append({})
    for i in range(len(count_list)):
        dic[count_list[i][0]] = str(i + 1)
    for info in movielist:
        info['ranking'] = dic[info['title']]
        info_new[int(info['ranking']) - 1] = info
    return info_new


# 精细化数据
def redefine(rank, movielist):
    if rank == 'newmov_list':
        for info in movielist:
            pass
    else:
        pass


# 周口碑榜5
def pubpra_list():
    info_pubpra = client.pubpra_list.find({}, {'_id': 0})
    info_pubpra = [i for i in info_pubpra]
    refresh_date = info_pubpra[0]['refresh_date']
    return info_pubpra, refresh_date


# 北美票房榜
def ameboxoff_list():
    info_ameboxoff = client.ameboxoff_list.find({}, {'_id': 0})
    return info_ameboxoff


# 分类排行榜
def sort_list(rank, page):
    collection = client[rank]
    info_list = collection.find({}, {'_id': 0})
    # 从游标格式转为列表
    info_list = [i for i in info_list]
    # 获取榜单名
    list_name = info_list[0]['list_name']
    for info in info_list:
        # 添加数据到字典中
        if client.movie_info.find_one({'movie_id': info['movie_id']})['title']:
            # 添加数据到字典中
            add_dic(info)
        else:
            add_none(info)
    # 分页
    info_list = pages(info_list, page)

    return info_list, list_name


# top100榜
def top100_list(rank, page):
    collection = client[rank]
    info_top100 = collection.find({}, {'_id': 0})
    info_top100 = [i for i in info_top100]
    for info in info_top100:
        if client.movie_info.find_one({'movie_id': info['movie_id']})['title']:
            # 添加数据到字典中
            add_dic(info)
        else:
            add_none(info)
    # 分页
    info_top100 = pages(info_top100, page)

    return info_top100


# 国内票房榜
def homboxoff_list(rank):
    collection = client[rank]
    info_homboxoff = collection.find({}, {'_id': 0})
    info_homboxoff = [i for i in info_homboxoff]
    for info in info_homboxoff:
        # 获取票房
        info['box_now'] = info['others'][0]
        info['box_total'] = info['others'][1]
        # 添加数据到字典中
        if client.movie_info.find_one({'movie_id': info['movie_id']})['title']:
            # 添加数据到字典中
            add_dic(info)
        else:
            add_none(info)
    return info_homboxoff


# 热议新片榜
def newmov_list(rank, page):
    collection = client[rank]
    info_newmovie = collection.find({}, {'_id': 0})
    info_newmovie = [i for i in info_newmovie]
    count_list = []
    for info in info_newmovie:
        # 数字改成字符串
        info['others'] = str(info['others'])
        # 添加数据到字典中
        # 电影信息是否存在
        if client.movie_info.find_one({'movie_id': info['movie_id']})['title']:
            add_dic(info)
        else:
            add_none(info)

        # 排序数据
        count_list.append((info['title'], info['rating_count']))
    # 根据 评价人数 排序
    info_newmovies = sort(count_list, info_newmovie)

    # 分页
    info_newmovies = pages(info_newmovies, page)

    return info_newmovies


# 热映新片榜
def hotmov_list(page):
    info_hotmovie = client.newmov_list.find({}, {'_id': 0})
    info_hotmovie = [i for i in info_hotmovie]
    ranking_list = []
    for info in info_hotmovie:
        # 添加数据到字典中
        if client.movie_info.find_one({'movie_id': info['movie_id']})['title']:
            # 添加数据到字典中
            add_dic(info)
        else:
            add_none(info)

        ranking_list.append((info['title'], info['others']))

    # 根据评分排序
    info_hotmovies = sort(ranking_list, info_hotmovie)

    # 分页
    info_hotmovies = pages(info_hotmovies, page)

    return info_hotmovies


# response
def rank_list(response):
    info_pubpra = pubpra_list()[0]
    refresh_date = pubpra_list()[1]
    info_ameboxoff = ameboxoff_list()
    rank = response.GET.get('ranking') if response.GET.get('ranking') else "hotmov_list"
    page = response.GET.get('page', 1)
    response_1 = HttpResponse('200')
    response_1.set_cookie('phoner_number', value='132222')
    user = response_1.cookies.get('phone_number', 'none')

    if rank == 'hotmov_list':
        info_hotmovie = hotmov_list(page)
        return render_to_response('info_hotmovie.html',
                                  {'info_hotmovie': info_hotmovie, 'info_pubpra': info_pubpra,
                                   'info_ameboxoff': info_ameboxoff, 'refresh_date': refresh_date, 'user': user,
                                   'page': page})
    elif rank == 'newmov_list':
        info_newmovie = newmov_list(rank, page)
        return render_to_response('info_newmovie.html',
                                  {'info_newmovie': info_newmovie, 'info_pubpra': info_pubpra,
                                   'info_ameboxoff': info_ameboxoff, 'refresh_date': refresh_date, 'user': user,
                                   'page': page})
    elif rank == 'homboxoff_list':
        info_homboxoff = homboxoff_list(rank)
        return render_to_response('info_homboxoff.html',
                                  {'info_homboxoff': info_homboxoff, 'info_pubpra': info_pubpra,
                                   'info_ameboxoff': info_ameboxoff, 'refresh_date': refresh_date, 'user': user})
    elif rank == 'top100_list':
        info_top100 = top100_list(rank, page)
        return render_to_response('info_top100.html',
                                  {'info_top100': info_top100, 'info_pubpra': info_pubpra,
                                   'info_ameboxoff': info_ameboxoff, 'refresh_date': refresh_date, 'user': user,
                                   'page': page})
    else:
        info_list, list_name = sort_list(rank, page)
        return render_to_response('info_list.html',
                                  {'info_list': info_list, 'info_pubpra': info_pubpra,
                                   'info_ameboxoff': info_ameboxoff, 'list_name': list_name,
                                   'refresh_date': refresh_date, 'user': user, 'page': page, 'rank': rank})
