from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
import json
from datetime import datetime
from app01.models import *
from app01.serializers import *
from rest_framework.views import APIView
from django.http import JsonResponse
from django_redis import get_redis_connection
from rest_framework.generics import ListCreateAPIView,ListAPIView
from rest_framework.response import Response
from app01.serializers import *

class login(APIView):
    def post(self,request,*args,**kwargs):
        context = {}
        try:
            username = request.POST['username']
            password = request.POST['password']
            user = User.objects.get(username=username,password=password)
            context={
                'code':200,
                'success':True,
                'token':create_token(username),
            }
        except User.DoesNotExist:
            context = {
                'code':500,
                'success':False,
            }
        return Response(context)


class register(APIView):
    def post(self,request,*args,**kwargs):
        context = {}
        try:
            username = request.POST['username']
            password = request.POST['password']
            try:
                user = User.objects.get(username=username)
                context = {'code': 500,
                           'success': False,
                           'msg': '用戶已存在！',
                           }
            except User.DoesNotExist:
                a = User(username=username, password=password)
                a.save()
                context = {'code': 200,
                           'success': True,
                           }
        except Exception as Ex:
            context = {'code': 500,
                       'success': False,
                       'msg':"参数错误！"
                       }

        return Response(context)


class month_budgetView(APIView):
    def post(self, request, *args, **kwargs):
        context ={}
        success = True
        budget = ''
        try:
            kind = request.POST['kind']
            budget_amount = request.POST['number']
            token = request.POST['token']
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
        except Exception as Ex:
            print(Ex)
            success = False
        context = {
                   'success': success,
                   }
        return Response(context)

class getbudget(APIView):
    def post(self,request,*args,**kwargs):
        now=datetime.now()
        wish={}
        spending={}
        mb=month_budget.objects.filter(year=now.year,month=now.month)
        for m in mb:
            wish[m.kind]=m.budget_amount


        spending={
            "clothes": 0,
            "eating": 0,
            "living": 0,
            "going": 0,
            "other": 0
        }
        data={
            "wish": wish,
            "spending": spending
        }
        context={
            "code":200,
            "data":data

        }

        return Response(data)

class BillView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        models.Bill.objects.create(name=request.data.get('name'),income=request.data.get('income'),note=request.data.get('note'),number=request.data.get('number'),year=request.data.get('year'),mouth=request.data.get('mouth'),day=request.data.get('day'),type=request.data.get('type'))
        return JsonResponse({'code': 200, 'msg': '创建成功', 'results': request.data})

class Bill1View(APIView):
    def delete(self, request, id):
        book_obj = models.Bill.objects.filter(id=id).exists()
        if book_obj:
            models.Bill.objects.filter(id=id).delete()
            return JsonResponse({'code': 200, 'msg': '删除一条成功'})
        else:
            return JsonResponse({'code': 101, 'msg': '当前不存在此账单'})

# from django.shortcuts import render
# from django.views.generic import View
# from captcha.models import CaptchaStore
# from captcha.helpers import captcha_image_url
# from django.http import HttpResponse
# import json
#
#
# # 创建验证码
# def captcha():
#     hashkey = CaptchaStore.generate_key()  # 验证码答案
#     image_url = captcha_image_url(hashkey)  # 验证码地址
#     captcha = {'hashkey': hashkey, 'image_url': image_url}
#     return captcha
#
# #刷新验证码
# def refresh_captcha(request):
#     return HttpResponse(json.dumps(captcha()), content_type='application/json')
#
# # 验证验证码
# def jarge_captcha(captchaStr, captchaHashkey):
#     if captchaStr and captchaHashkey:
#         try:
#             # 获取根据hashkey获取数据库中的response值
#             get_captcha = CaptchaStore.objects.get(hashkey=captchaHashkey)
#             if get_captcha.response == captchaStr.lower():  # 如果验证码匹配
#                 return True
#         except:
#             return False
#     else:
#         return False
#
#
# class IndexView(View):
#     def get(self, request):
#         hashkey = CaptchaStore.generate_key()  # 验证码答案
#         image_url = captcha_image_url(hashkey)  # 验证码地址
#         print(hashkey,image_url)
#         captcha = {'hashkey': hashkey, 'image_url': image_url}
#         return render(request, locals())
#
#     def post(self, request):
#         capt = request.POST.get("captcha", None)  # 用户提交的验证码
#         key = request.POST.get("hashkey", None)  # 验证码答案
#         if jarge_captcha(capt, key):
#             return HttpResponse("验证码正确")
#         else:
#             return HttpResponse("验证码错误")



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

