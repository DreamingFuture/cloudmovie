from django.shortcuts import render, HttpResponse, render_to_response
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from bson.objectid import ObjectId
from .models import client
import json
import os
import time


def casts_page(request, movie_id):
    # 演员详情页后端部分
    db = client.movie_info
    collection = db.movie_info
    film = collection.find_one({'movie_id': movie_id})

    cast_info = film.get('cast_info', None)
    cast_info_copy = {}
    if cast_info:
        for key, value in cast_info.items():
            each_duty_copy = []
            for each_people in value:
                each_people['url'] = '/image/casts/?movie_id={0}&file_name={1}'.format(
                    movie_id, each_people['name'])
                each_duty_copy.append(each_people)
            cast_info_copy[key] = each_duty_copy
    else:
        cast_info_copy = None
    title = film['title']
    cast_count = film['cast_count']
    url = '/detail/%s' % movie_id

    content = {}
    content['cast_count'] = str(cast_count)
    content['cast_info'] = cast_info_copy
    content['title'] = title
    content['detail_url'] = url

    return render_to_response('casts_page.html', {'doc': json.dumps(content)})


def stills_page(request, movie_id):
    # 剧照页后端部分
    db = client.movie_info
    collection = db.movie_info

    film = collection.find_one({'movie_id': movie_id})
    stills_filename = film['stills_filename']
    relative_movie = film['relative_movie']
    title = film['title']

    content = {}
    if stills_filename:
        content['stills'] = ['/image/stills_thumbnail/?movie_id={0}&file_name={1}'.format(
            movie_id, each_still) for each_still in stills_filename]
    else:
        content['stills'] = None

    if relative_movie:
        content['relative_movie'] = [{'title': each_movie, 'poster_url': '/image/relmovpos/?movie_id={0}&file_name={1}'.format(
            movie_id, each_movie)} for each_movie in relative_movie][:9]
    else:
        content['relative_movie'] = None

    content['stills_count'] = len(content['stills'])

    content['detail_url'] = "/detail/{0}".format(movie_id)
    content["title"] = title

    return render_to_response('stills_page.html', {'doc': json.dumps(content)})


def detail_page(request, movie_id):
    # 电影详情页后端部分
    db = client.movie_info
    collection = db.movie_info
    film = collection.find_one({'movie_id': movie_id})

    def temp(x): return str(x) if x else None
    detail = {}
    detail['movie_id'] = movie_id
    detail['title'] = film.get('title', None)

    if not detail['title']:
        return render_to_response('404.html')

    detail['coungion'] = film.get('coungion', None)
    detail['language'] = film.get('language', None)
    detail['release_date'] = film.get('release_date', None)
    detail['runtime'] = temp(film.get('runtime', None))
    detail['genres'] = film.get('genres', None)
    detail['rating'] = temp(film.get('rating', None))
    detail['rating_count'] = temp(film.get('rating_count', None))
    detail['storyline'] = "<p>"+film.get('storyline', None).replace(
        r"\n", "</p><p>")+"</p>" if film.get('storyline', None) else None
    detail['poster'] = '/image/poster/?movie_id={0}&file_name={0}'.format(
        movie_id, movie_id)

    # 演职人员的图片
    cast = film.get('cast_info', None)
    if cast:
        cast_dir = cast.get('导演 Director', None)
        cast_cast = cast.get('演员 Cast', None)
    else:
        cast_dir = None
        cast_cast = None

    photo_director = None
    if cast_dir:
        photo_director = []
        for each_director in cast_dir[:5]:
            photo_director.append(
                {'name': each_director['name'], 'url': '/image/casts/?movie_id={0}&file_name={1}'.format(movie_id, each_director['name'])})

    photo_stars = None
    num = 7-len(photo_director) if photo_director else 5
    if cast_cast and num > 0:
        photo_stars = []
        for cast in cast_cast[:num]:
            photo_stars.append(
                {'name': cast['name'], 'url': '/image/casts/?movie_id={0}&file_name={1}'.format(movie_id, cast['name'])})

    detail['photo_director'] = photo_director
    detail['photo_stars'] = photo_stars

    # 将详情页所需的导演、编剧、演员列出
    detail['directors'] = film.get('directors', None)
    detail['writers'] = film.get('writers', None)
    detail['stars'] = film.get('stars', None)

    # 相关电影片名及海报
    relative_name = film.get('relative_movie', None)
    relmovpos = None
    if relative_name:
        relmovpos = []
        for name in relative_name[:9]:
            relmovpos.append(
                {'title': name, 'url': '/image/relmovpos/?movie_id={0}&file_name={1}'.format(movie_id, name)})

    detail['relmovpos'] = relmovpos

    # 剧照
    file_name = film.get('stills_filename', None)
    stills_url = None
    if file_name:
        stills_url = [
            '/image/stills_thumbnail/?movie_id={0}&file_name={1}'.format(movie_id, i) for i in file_name[:7]]

    detail['stills_url'] = stills_url
    return render_to_response("detail_page.html", {"doc": json.dumps(detail)})


def user_search(request):
    # 用于查找用户
    cookie = request.COOKIES.get("user_info", None)
    if cookie:
        cookie = cookie.replace('\'', '\"')
        user_info = json.loads(cookie, strict=False)

        phone_number = user_info.get('phone_number')
        password = user_info.get('password')

        db = client.account_info
        collection = db.user

        user = collection.find_one({"phone_number": phone_number})
        return user, password
    else:
        return None, None


@csrf_exempt
def comment(request):
    # 用于登记评论
    user, password = user_search(request)
    if user:
        # 如果可以读取到用户信息
        if user["password"] == password:
            # 验证密码通过
            _id = request.POST.get("_id")
            content = request.POST.get("content")
            rating = request.POST.get("rating")
            # 读取POST请求中的内容
            if rating:
                # 如果可以读取到评分信息，则表明是对电影的评论
                db = client.movie_info
                collection = db.movie_info
                # 连接数据库等
                phone_number = user["phone_number"]
                result = collection.update_one({"movie_id": int(_id)}, {'$addToSet': {
                                               'user_phone_number': phone_number}})
                if result.modified_count == 0:
                    return HttpResponse("201")
                # 在电影信息中登记评论发出者_id
                doc = {}
                doc["publish_date"] = time.time()
                doc["rating"] = rating
                doc["content"] = content
                doc["like_count"] = 0
                doc["parent_id"] = _id
                doc["level"] = 0
                doc["user_phone_number"] = user["phone_number"]
                # 生成评论信息
                db = client.account_info
                collection = db.comment
                result = collection.insert_one(doc)
                # 保存评论
                collection = db.user
                collection.update_one({"phone_number": phone_number}, {
                                      "$push": {"comment_id": result.inserted_id}})
                # 在评论发送用户的数据中登记评论

                return HttpResponse("200")
            else:
                # 如果无法读取到评分信息，则表明是对评论的评论
                _id = ObjectId(_id)
                phone_number = user["phone_number"]
                db = client.account_info
                collection = db.comment
                # 连接数据库等
                collection.update_one(
                    {"_id": _id}, {"$push": {"children_id": _id}})
                # 在父级评论登记子评论_id

                parent_comment = collection.find_one({"_id": _id})
                level = parent_comment["level"]
                forefather_id = parent_comment.get("forefather_id", None)
                # 从父级评论读取 级数 和祖先评论_id

                doc = {}
                doc["publish_date"] = time.time()
                doc["content"] = content
                doc["like_count"] = 0
                doc["parent_id"] = _id
                doc["level"] = level + 1
                doc["forefather_id"] = forefather_id if forefather_id else _id
                doc["user_phone_number"] = phone_number
                # 祖父评论没有 forefather_id 字段
                # 生成评论信息
                result = collection.insert_one(doc)
                # 保存评论
                collection = db.user
                collection.update_one({"phone_number": phone_number}, {
                                      "$push": {"comment_id": result.inserted_id}})
                # 在评论发送用户的数据中登记评论
                return HttpResponse("200")

    return HttpResponse("205")


@csrf_exempt
def like_it(request):
    # 用于登记点赞
    _id = request.POST.get("_id")
    _id = ObjectId(_id)
    # 读取POST请求中的被点赞评论的_id
    db = client.account_info
    collection = db.comment
    # 连接数据库等

    result = collection.update_one({"_id": _id}, {"$inc": {"like_count": 1}})
    if result.modified_count:
        # 通过执行结果判断是否执行成功
        return HttpResponse("200")
    else:
        return HttpResponse("201")


def del_items(dict, keys):
    # 删除字典中指定的字段，返回删除的结果
    for each_key in keys:
        dict.pop(each_key, None)
    return dict


def add_nickname_and_avatar_url(comment_list, collection):
    # 为评论添加昵称, 头像路径，修改_id为字符串, 修正时间
    for each_comment in comment_list:
        # a = os.path.abspath('..') + "\\clouldmovie\\resource\\avatar\\{0}.jpeg".format(user["phone_number"]))
        each_comment["avatar_url"] = '/image/avatar/?file_name={0}'.format(each_comment["user_phone_number"]) if os.path.exists(os.path.abspath(
            '..') + "\\clouldmovie\\resource\\avatar\\{0}.jpeg".format(each_comment["user_phone_number"])) else '/image/avatar/?file_name=default'
        each_comment["_id"] = str(each_comment["_id"])
        each_comment["publish_date"] = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(each_comment["publish_date"]))
        each_comment["nickneme"] = collection.find_one(
            {"phone_number": each_comment["user_phone_number"]})["nickname"]
    return comment_list


def new_basis(movie_id, num=0):
    # 依据评论发布时间返回评论
    num *= 10
    # 请求次数乘10，从评论列表第num个评论获取10个
    db = client["movie_info"]
    collection = db["movie_info"]

    user_list = collection.find_one({"movie_id": movie_id})
    user_list = user_list.get("user_phone_number", None)
    # 从评论信息中获取发布用户的_id
    if user_list:
        db = client["account_info"]
        collection = db["comment"]
        comment = list(del_items(collection.find_one({"parent_id": str(movie_id), "user_phone_number": each_user, "rating": {
                       "$exists": "True"}}), ["parent_id", "children_id", "forefather_id"]) for each_user in user_list[num:num+10])
        comment = add_nickname_and_avatar_url(comment, db["user"])
        return HttpResponse(json.dumps(comment))
    else:
        return HttpResponse("0")


def hot_basis(movie_id, num=0):
    # 依据评论热度返回评论
    def get_like_count(x):
        return x["like_count"]

    num *= 10
    # 请求次数乘10，从评论列表第num个评论获取10个
    db = client["movie_info"]
    collection = db["movie_info"]

    user_list = collection.find_one({"movie_id": movie_id})
    user_list = user_list.get("user_phone_number", None)
    # 从movie_info里查找评论登记信息
    if user_list:
        # 若可以查询到评论

        db = client["account_info"]
        collection = db["comment"]

        comment = [del_items(collection.find_one({"parent_id": str(movie_id), "user_phone_number": each_user, "rating": {
                             "$exists": "True"}}), ["parent_id", "children_id", "forefather_id"]) for each_user in user_list]
        comment = sorted(comment, key=get_like_count,
                         reverse=True)[num: num+10]
        # 查找所有对电影的评论，选取从第num个往后10个评论
        comment = add_nickname_and_avatar_url(comment, db["user"])
        return HttpResponse(json.dumps(comment))
    else:
        return HttpResponse("0")


def level_basis(movie_id, num=0):
    # 依据评论楼层数量返回评论

    def find_by_level(comment_id):
        # 这个函数通过comment_id查找父辈级评论，并将其依据级数升序打包为列表
        nonlocal comment_list
        nonlocal collection
        # comment_list是储存评论的列表
        comment = collection.find_one({"_id": comment_id})
        # 搜索评论
        if not comment:
            # 如果已经找不到任何评论（因为顶级评论的parent_id是movie_id），则表明是顶级评论
            comment_list = [del_items(each_comment, [
                                      "parent_id", "children_id", "forefather_id"]) for each_comment in comment_list]
            # 从评论列表中过滤掉冗余信息
            return comment_list
        else:
            # 如果可以找到评论
            comment_list.insert(0, comment)
            # 将评论插入列表
            # parent_comment = collection.find_one({"_id": comment["parent_id"]})
            # 依据parent_id找到父级评论
            return find_by_level(comment["parent_id"])
            # 递归搜索父级评论

    def level_info(top_comment):
        # 这个函数用于找出某个顶级评论的所有分支评论的级数，并打包成字典
        comment_list = list(collection.find(
            {'forefather_id': top_comment['_id'], "children_id": None}))
        # 查找所有底层评论
        level_info = sorted(
            comment_list, key=lambda dict: dict["level"], reverse=True)
        # 依据级数排序
        return level_info

    db = client["movie_info"]
    collection = db["movie_info"]
    user_list = collection.find_one({"movie_id": movie_id})
    # 从movie_info里查找评论登记信息

    if user_list:
        # 如果可以找到评论
        user_list = user_list.get("user_phone_number", None)

        db = client["account_info"]
        collection = db["comment"]

        comment = [collection.find_one({"parent_id": str(movie_id), "user_phone_number": each_user, "rating": {
                                       "$exists": "True"}}) for each_user in user_list]
        # 查找顶级评论
        total_level_info = [level_info(each_comment)
                            for each_comment in comment]
        # 列出所有顶级评论的分支的级数
        total_level_info = [
            each_comment for each_comment in total_level_info if each_comment]
        temp = []
        for each_comment_list in total_level_info:
            for each_comment in each_comment_list:
                temp.append(each_comment)
        total_level_info = temp
        # 过滤空结果
        total_level_info = sorted(
            total_level_info, key=lambda dict: dict.get("level", None), reverse=True)
        # 依照级数降序排序
        comment_id = total_level_info[num]['_id']
        # 获取第num个底级评论
        comment_list = []
        # comment_list.append(total_level_info[num])
        comment_list = find_by_level(comment_id)
        # 由底级评论找到评论组，打包
        comment_list = add_nickname_and_avatar_url(comment_list, db["user"])
        # 请查看函数定义
        return HttpResponse(json.dumps(comment_list))
    else:
        return HttpResponse("0")


def get_comment(request, movie_id):
    basis = request.GET.get("basis")
    num = int(request.GET.get("num"))

    if basis == 'new':
        return new_basis(movie_id, num)
    elif basis == 'hot':
        return hot_basis(movie_id, num)
    elif basis == 'level':
        return level_basis(movie_id, num)
    else:
        return HttpResponse('0')
