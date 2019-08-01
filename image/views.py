import os
import re
from django.shortcuts import HttpResponse
from .verification_code import Code
from django.contrib.auth import logout
from PIL import Image, ImageFilter
from io import BytesIO
# Create your views here.


def movie_info_pic(request, directory):
    movie_id = request.GET.get('movie_id')
    file_name = request.GET.get('file_name')
    file_name = re.sub(r'[*/\\:?<>|"]', '', file_name)
    base_path = os.path.abspath('.') + '\\resource\\movie_info\\%s\\%s\\%s' % (movie_id, directory, file_name)
    try:
        path = base_path + '.jpeg'
        file = open(path, 'rb')
        img = file.read()
        return HttpResponse(img, 'image/jpeg')
    except FileNotFoundError:
        try:
            path = base_path + '.png'
            file = open(path, 'rb')
            img = file.read()
            return HttpResponse(img, 'image/png')
        except FileNotFoundError:
            path = base_path + '.jpg'
            file = open(path, 'rb')
            img = file.read()
            return HttpResponse(img, 'image/jpg')


def total_and_avatar(request, directory):
    file_name = request.GET.get('file_name')
    file_name = re.sub(r'[*/\\:?<>|"]', '', file_name)
    base_path = os.path.abspath('.') + '\\resource\\%s\\' % directory
    try:
        path = base_path + file_name + '.jpeg'
        file = open(path, 'rb')
        img = file.read()
        return HttpResponse(img, 'image/jpeg')
    except FileNotFoundError:
        try:
            path = base_path + file_name + '.png'
            file = open(path, 'rb')
            img = file.read()
            return HttpResponse(img, 'image/png')
        except FileNotFoundError:
            try:
                path = base_path + file_name + '.jpg'
                file = open(path, 'rb')
                img = file.read()
                return HttpResponse(img, 'image/jpg')
            except FileNotFoundError:
                path = base_path + 'default.jpeg'
                file = open(path, 'rb')
                img = file.read()
                return HttpResponse(img, 'image/jpg')

def verify_code(request):
    code = Code(4)
    string, code = code.make_code()
    request.session['verify'] = string
    print(request.session['verify'])
    # logout(request)
    # 清除本地session文件
    return HttpResponse(code.getvalue(), 'image/png')


def background(request):
    movie_id = request.GET.get('movie_id')
    base_path = os.path.abspath('.') + '\\resource\\movie_info\\%s\\poster\\%s' % (movie_id, movie_id)
    try:
        path = base_path + '.jpeg'
        img = Image.open(path)
    except FileNotFoundError:
        try:
            path = base_path + '.png'
            img = Image.open(path)
        except FileNotFoundError:
            path = base_path + '.jpg'
            img = Image.open(path)
    crop_img = img.crop((0, 117, img.width, 184))
    extend_img = crop_img.resize((1200, 300))
    darken_img = extend_img.point(lambda p: p * 0.7)
    blur_img = darken_img.filter(ImageFilter.GaussianBlur(radius=15))
    new_img = BytesIO()
    blur_img.save(new_img, 'jpeg')
    return HttpResponse(new_img.getvalue(), 'image/jpeg')
