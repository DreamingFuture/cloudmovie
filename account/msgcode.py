import urllib.request
import random
import time
import hashlib
import json


def get_headers():
    Nonce = str(random.randint(0, 9999999))
    AppKey = '26eea378260c9d92fc71ba2c19cc1790'
    CurTime = str(int(time.time()))
    CheckSum = hashlib.sha1(
        ("9b01db46b57a"+Nonce+CurTime).encode("utf-8")).hexdigest()
    headers = {'Nonce': Nonce,
               'AppKey': AppKey,
               'CurTime': CurTime,
               'CheckSum': CheckSum,
               'Content-Type': 'application/x-www-form-urlencoded'}
    return headers


def sendcode(mobile):
    url = 'https://api.netease.im/sms/sendcode.action'
    data = bytes(urllib.parse.urlencode({'mobile': mobile}), encoding='utf8')

    request = urllib.request.Request(url, data=data, headers=get_headers())
    response = urllib.request.urlopen(request)
    result = json.loads(response.read().decode("utf-8"))

    return result["code"]


def verifycode(mobile, code):
    url = 'https://api.netease.im/sms/verifycode.action'
    data = bytes(urllib.parse.urlencode(
        {'mobile': mobile, 'code': code}), encoding='utf8')
    request = urllib.request.Request(url, data=data, headers=get_headers())
    response = urllib.request.urlopen(request)
    result = json.loads(response.read().decode("utf-8"))

    return result["code"]
