from django.shortcuts import HttpResponse, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from pymongo import MongoClient
from .models import client
import re
import collections

def ch_join(name):
    try:
        name = '\\'.join(name)
    except TypeError:
        name = '未知'
    return name

# 模糊搜索
@csrf_exempt
def search(request):  # user_input是用户输入的查询结果
    user_input = request.POST.get("content")

    db = client.movie_info
    collection = db.movie_info

    suggestions = []
    # 索引
    get_writer = []
    get_director = []
    get_star = []
    movie_writers = list(collection.find({'writers':user_input}))
    movie_directors = list(collection.find({'directors':user_input}))
    movie_stars = list(collection.find({'stars':user_input}))
    movie_three = (movie_writers,movie_directors,movie_stars)
    movie_wds = ('writer', 'director', 'stars')
    get_threelist = (get_writer, get_director, get_star)
    
    for i in range(0,3):
        for people in movie_three[i]:
            writers = ch_join(people['writers'])
            directors = ch_join(people['directors'])
            get_threelist[i].append({movie_wds[i]:{'movie_id':people['movie_id'], 'title':people['title'], 'writers':writers, 'directors':directors,
                                  'release_date':people['release_date'], 'rating':people['rating'],'rating_count':people['rating_count'],
                                  'poster':r'/image/poster/?movie_id={}&file_name={}'.format(people['movie_id'], people['movie_id'])}})
   
    input_Hans = re.sub("[A-Za-z0-9\!\%\[\]\,\。]", "", user_input)  # 提取中文，实现中文可以颠倒的功能
    if (input_Hans != ' '):
        movie_title = []
        for single in input_Hans:  # 对每一个字进行选择
            single_re = single+ '.*?'
            regex = re.compile(single_re)  # 变成正则的形式
            movie_title.append(collection.find({'title':regex}))  # 只对电影名模糊搜索，其它搜索不采用模糊搜索,如果没有电影，他就是空的
        
        re_user_input = '.*?'.join(user_input)   #将内容变成x.* x.*的格式

        regex = re.compile(re_user_input)    
        movie_title.append(collection.find({'title':regex}))
        movie_tit = [movie for movie_er in movie_title for movie in movie_er]
        movie_mid = []
        for movie in movie_tit:
            movie_mid.append(movie['movie_id'])

        suggestions_new = []
        dic = collections.Counter(movie_mid)  # 此处已经排序过了
        try:
            for key in dic:
                if dic[key] >= 2:
                    suggestions_new.append(key)

            try:
                suggestions_new = suggestions_new[:5]
                movie_data = []
                for movie_one in suggestions_new:
                    movie_one = collection.find_one({'movie_id':movie_one})
                    writers = ch_join(movie_one['writers'])
                    directors = ch_join(movie_one['directors'])
                    movie_data.append({'title':{'movie_id':movie_one['movie_id'], 'title':movie_one['title'], 'writers':writers, 'directors':directors,
                                              'release_date':movie_one['release_date'], 'rating':movie_one['rating'],'rating_count':movie_one['rating_count'],
                                              'poster':r'/image/poster/?movie_id={}&file_name={}'.format(movie_one['movie_id'], movie_one['movie_id'])}})
                return render_to_response("search.html", {"movie_data":movie_data, "movie_writer":get_writer, "movie_director":get_director, "movie_star":get_star})
            except TypeError:
                return HttpResponse("404")
        except TypeError:
            return HttpResponse("404")
    return render_to_response("search.html", {"movie_writer":get_writer, "movie_director":get_director, "movie_star":get_star})
    # 当用户输入纯英文的时候
    '''else:
        re_user_input = '.*?'.join(user_input) # 将内容变成x.* x.*的格式
        regex = re.compile(re_user_input)    
        movie_title.append(collection.find({'title':regex}))
        movie_tit = [movie for movie_er in movie_title for movie in movie_er]
        movie_mid = []
        for movie in movie_tit:
            movie_mid.append(movie['movie_id'])

        try:
            suggestions_new = suggestions_new[:5]
            for movie_one in suggestions_new:
                movie_one = collection.find_one({'movie_id':movie_one})
                writers = ch_join(movie_one['writers'])
                directors = ch_join(movie_one['directors'])
                movie_data.append({'title':{'movie_id':movie_one['movie_id'], 'title':movie_one['title'], 'writers':writers, 'directors':directors,
                                          'release_date':movie_one['release_date'], 'rating':movie_one['rating'],'rating_count':movie_one['rating_count'],
                                          'poster':r'/image/poster/?movie_id={}&file_name={}'.format(movie_one['movie_id'], movie_one['movie_id'])}})
            return render_to_response("search.html", {"movie_data":movie_data, "movie_writer":movie_writer, "movie_director":get_director, "movie_star":get_star})
        except:
            return HttpResponse("404")  # 电影不存在
        '''