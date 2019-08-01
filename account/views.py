import json
import hashlib
import shutil
import os
import time
import re
from django.shortcuts import render_to_response, HttpResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as remove_session
from .models import client
from .msgcode import sendcode, verifycode


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


def login(request):
    # 登录页面后端部分
    user, password = user_search(request)
    if user:
        # 若用户存在，密码校验成功，生成cookies
        if user["password"] == password:
            # 若用户已经登录，返回个人中心
            return HttpResponseRedirect("../space")

    return render_to_response('login.html')
    # 不论什么原因，只要密码校验失败，返回登录页面


def forget_password(request):
    # 忘记密码页面后端部分
    return render_to_response('get_password.html')


def register(request):
    # 注册用户页面后端部分
    return render_to_response('register.html')


def get_comment(comment_list, num=0):
    db = client.account_info
    collection = db.comment

    if comment_list:
        temp = []
        for i in comment_list[num * 10: num * 10 + 10]:
            each_comment = collection.find_one({"_id": i})
            comment = {}
            comment["time"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(each_comment["publish_date"]))
            comment["content"] = each_comment["content"]
            try:
                comment["title"] = client.movie_info.movie_info.find_one(
                    {'movie_id': int(each_comment['parent_id'])})["title"]
                comment["rating"] = str(each_comment.get("rating"))
            except TypeError:
                comment["title"] = ""
                comment["rating"] = None
            comment["like_count"] = str(each_comment['like_count'])
            temp.append(comment)
    else:
        temp = None

    return temp


@csrf_exempt
def more_comments(request):
    user, password = user_search(request)
    if user:
        if user["password"] == password:
            num = request.POST.get("num")
            comment_list = user.get("comment_id", None)
            comments = get_comment(comment_list, int(num)) if comment_list else None

            return HttpResponse(json.dumps(comments))

    return HttpResponse("0")


def space(request):
    user, password = user_search(request)
    if user:
        if user["password"] == password:
            # 密码校验成功
            doc = {}
            doc["nickname"] = user["nickname"]
            doc["phone_number"] = user["phone_number"]
            doc["avatar_url"] = '/image/avatar/?file_name={0}'.format(user["phone_number"]) if os.path.exists(
                os.path.abspath(
                    '..') + "\\clouldmovie\\resource\\avatar\\{0}.jpeg".format(
                    user["phone_number"])) else '/image/avatar/?file_name=default'
            comment_list = user.get("comment_id", None)
            # 获取用户基本信息
            doc["comments"] = get_comment(comment_list) if comment_list else None
            # 获取用户评论

            return render_to_response("space.html", {'doc': json.dumps(doc)})

    return HttpResponseRedirect("../login")
    # 只要密码校验失败，返回登录页面


@csrf_exempt
def reg_sub(request):
    # 用户注册的表单提交
    phone_number = request.POST.get('phone_number')
    password = hashlib.md5(request.POST.get(
        'password').encode("utf-8")).hexdigest()
    code = request.POST.get('code')

    code = verifycode(phone_number, code)
    if code == 200:
        # if code:
        # 如果短信验证码校验成功:
        collection = client.account_info.user
        if collection.find_one({'phone_number': phone_number}):
            return HttpResponse('204')
        # 检查手机号是否已经注册

        data = {
            'phone_number': phone_number,
            'password': password,
            'create_data': time.time(),
            'nickname': '无昵称',
            'login_history': None,
        }
        collection.insert_one(data)
        return HttpResponse('200')
    else:
        return HttpResponse(code)


@csrf_exempt
def for_sub(request):
    # 忘记密码的表单提交
    phone_number = request.POST.get("phone_number")
    password = hashlib.md5(request.POST.get(
        'password').encode("utf-8")).hexdigest()
    code = request.POST.get('code')
    # 读取请求的信息

    code = verifycode(phone_number, code)
    if not code == 200:
        # if code:
        # 如果短信验证码校验失败
        return HttpResponse(code)

    collection = client.account_info.user
    if not collection.find_one({"phone_number": phone_number}):
        return HttpResponse("203")
    # 查找用户是否存在

    collection.update_one({"phone_number": phone_number}, {
        "$set": {"password": password}})
    # 在数据库中录入新的密码

    return HttpResponse("200")


@csrf_exempt
def log_sub(request):
    # 登录的表单提交
    phone_number = request.POST.get('phone_number')
    password = hashlib.md5(request.POST.get(
        'password').encode("utf-8")).hexdigest()
    # 对密码加密

    collection = client.account_info.user
    user = collection.find_one(
        {"$and": [{"phone_number": phone_number}, {"password": password}]})
    # 校验用户信息
    if user:
        # 校验成功，生成cookies，打开个人中心页面
        response = HttpResponse('200')
        response.set_cookie(
            "user_info", {"phone_number": phone_number, "password": password})
        return response
    else:
        # 校验失败，返回错误码202——用户不存在或密码错误
        return HttpResponse('202')


@csrf_exempt
def set_nickname(request):
    # 用于设置昵称
    user, password = user_search(request)
    if user:
        if user["password"] == password:
            db = client["account_info"]
            collection = db["user"]
            collection.update_one({"phone_number": user["phone_number"]}, {
                "$set": {"nickname": request.GET.get('nickname')}})
            return HttpResponse("200")
        else:
            return HttpResponse("202")
    else:
        return HttpResponseRedirect("../login")


@csrf_exempt
def set_avatar(request):
    # 用于设置头像
    user, password = user_search(request)
    if user:
        if user["password"] == password:
            avatar = request.FILES.get("avatar")
            # 读取头像
            path = os.path.abspath(
                '..') + "\\clouldmovie\\resource\\avatar\\{0}.jpeg".format(user["phone_number"])
            file = open(path, "wb")
            file.write(avatar.read())
            file.close()
            # 保存头像
            return HttpResponse("200")
        else:
            return HttpResponse("202")
    else:
        return HttpResponseRedirect("../login")


@csrf_exempt
def reset_password(request):
    user, password = user_search(request)
    if user:
        if user["password"] == password:
            db = client["account_info"]
            collection = db["user"]
            collection.update_one({"phone_number": user["phone_number"]}, {"$set": {
                "password": hashlib.md5(request.POST.get("password").encode("utf-8")).hexdigest()}})
            return HttpResponse("200")


def logout(request):
    # 用户登出，即删除记录登录信息的cookie
    response = HttpResponseRedirect("../login")
    response.delete_cookie('user_info')
    return response


@csrf_exempt
def sendmsgcode(request):
    # 发送短信验证码
    def check_piccode():
        # 校验图形验证码
        answer = request.session.get('verify').upper()
        code = request.POST.get('picode').upper()
        # 把验证码答案和用户输入的内容都转为大写

        if code == answer:
            remove_session(request)
            return 1
        else:
            return 0

    if check_piccode():
        # 验证图形验证码
        phone_number = request.POST.get("phone_number")
        # 读取手机号
        result = sendcode(phone_number)
        # 发送验证码
        return HttpResponse(result)
        # 发送回执
    else:
        # 验证码校验失败
        return HttpResponse('412')
