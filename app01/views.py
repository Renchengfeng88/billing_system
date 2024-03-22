from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
import json
from datetime import datetime
from app01.models import *

def login(request):
    context = {}
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username,password=password)
            success= True
            token = create_token(username)
        except User.DoesNotExist:
            success = False
            token = ''
        context = {
            'success':success,
            'token': token,
        }
    return render(request, json.dumps(context))


def create(request):
    exit = ''
    context = {}
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            exit =True
        except User.DoesNotExist:
            a = User(username=username, password=password)
            a.save()
            exit = False
    context = {
        'exit': exit,
    }
    return render(request,  json.dumps(context))


def month_budget(request):
    context ={}
    success = True
    budget = ''
    if request.POST:
        kind = request.POST['kind']
        budget_amount = request.POST['number']
        token = request.POST['token']
        check_token(token)
        if check_token(token):
            a = get_username(token)
            try:
                userid = User.objects.get(username=a)
                now = datetime.now()
                try:
                    mb = month_budget.objects.get(UserID=userid,year=now.year,month=now.month,kind=kind)
                    mb.budget_amount = budget_amount
                    mb.save()
                except month_budget.DoesNotExist:
                    budget = month_budget(UserID=userid,year=now.year,month=now.month,kind=kind, budget_amount=budget_amount)
                    budget.save()
            except User.DoesNotExist:
                success = False
        context = {
            'success':success,
        }
    return render(request,json.dumps(context))



from django.shortcuts import render
from django.views.generic import View
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import HttpResponse
import json


# 创建验证码
def captcha():
    hashkey = CaptchaStore.generate_key()  # 验证码答案
    image_url = captcha_image_url(hashkey)  # 验证码地址
    captcha = {'hashkey': hashkey, 'image_url': image_url}
    return captcha

#刷新验证码
def refresh_captcha(request):
    return HttpResponse(json.dumps(captcha()), content_type='application/json')

# 验证验证码
def jarge_captcha(captchaStr, captchaHashkey):
    if captchaStr and captchaHashkey:
        try:
            # 获取根据hashkey获取数据库中的response值
            get_captcha = CaptchaStore.objects.get(hashkey=captchaHashkey)
            if get_captcha.response == captchaStr.lower():  # 如果验证码匹配
                return True
        except:
            return False
    else:
        return False


class IndexView(View):
    def get(self, request):
        hashkey = CaptchaStore.generate_key()  # 验证码答案
        image_url = captcha_image_url(hashkey)  # 验证码地址
        print(hashkey,image_url)
        captcha = {'hashkey': hashkey, 'image_url': image_url}
        return render(request, locals())

    def post(self, request):
        capt = request.POST.get("captcha", None)  # 用户提交的验证码
        key = request.POST.get("hashkey", None)  # 验证码答案
        if jarge_captcha(capt, key):
            return HttpResponse("验证码正确")
        else:
            return HttpResponse("验证码错误")



# Create your views here.

import time
from django.core import signing
import hashlib
from django.core.cache import cache

HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = 'CHEN_FENG_YAO'
SALT = 'www.lanou3g.com'
TIME_OUT = 30 * 60  # 30min


def encrypt(obj):
    """加密"""
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


def decrypt(src):
    """解密"""
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    print(type(raw))
    return raw


def create_token(username):
    """生成token信息"""
    # 1. 加密头信息
    header = encrypt(HEADER)
    # 2. 构造Payload
    payload = {"username": username, "iat": time.time()}
    payload = encrypt(payload)
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    # 存储到缓存中
    cache.set(username, token, TIME_OUT)
    return token


def get_payload(token):
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload


# 通过token获取用户名
def get_username(token):
    payload = get_payload(token)
    return payload['username']
    pass


def check_token(token):
    username = get_username(token)
    last_token = cache.get(username)
    if last_token:
        return last_token == token
    return False

