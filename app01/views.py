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
from rest_framework.parsers import JSONParser
from app01 import models

class login(APIView):
    parser_classes = (JSONParser,)
    print('99999999')
    def post(self,request,*args,**kwargs):
        print('888888888')
        context = {}
        try:
            data = JSONParser().parse(request)
            username = data['username']
            password = data['password']
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
        print(context)
        return Response(context)


class register(APIView):
    parser_classes = (JSONParser,)
    def post(self,request,*args,**kwargs):
        context = {}
        try:
            data = JSONParser().parse(request)
            username = data['username']
            password = data['password']
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
    parser_classes = (JSONParser,)
    def post(self, request, *args, **kwargs):
        context ={}
        success = True
        budget = ''
        try:
            data = JSONParser().parse(request)
            kind = data['kind']
            budget_amount = data['number']
            token = data['token']
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
    parser_classes = (JSONParser,)
    def post(self,request,*args,**kwargs):
        data = JSONParser().parse(request)
        now=datetime.now()
        wish={}
        spending={}
        token = data['token']
        if check_token(token):
            a = get_username(token)
            mb = month_budget.objects.filter(year=now.year, month=now.month)
            userid = User.objects.get(username=a)
            b = Bill.objects.filter(UserID=userid,year=now.year,month=now.month,income=0)
            for m in mb:
                wish[m.kind]=m.budget_amount
            for n in b:
                spending[n.type] = spending[n.type]+n.number
        data={
            "wish": wish,
            "spending": spending,
        }

        return Response(data)

class Clock_inView(APIView):
    parser_classes = (JSONParser,)
    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        token = data['token']
        now = datetime.now()
        if check_token(token):
            a = get_username(token)
            userid = User.objects.get(username=a)
            try:
                b = Clock_in.objects.get(UserID=userid,year=now.year,month=now.month,day=now.day)
                success = False
                msg = '今日已打卡！'
            except Clock_in.DoesNotExist:
                time = Clock_in(UserID=userid,year=now.year,month=now.month,day=now.day)
                success = True
                msg = '打卡成功！'
                time.save()
        else:
            success = False
            msg = '验证失败！'
        data = {
            'success': success,
            'msg': msg,
        }
        return Response(data)

class get_p_informationView(APIView):
    parser_classes = (JSONParser,)
    def post(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        token = data['token']
        now = datetime.now()
        if check_token(token):
            a = get_username(token)
            userid = User.objects.get(username=a)
            days = Clock_in.objects.filter(UserID=userid, year=now.year, month=now.month).count()
            billdays = Bill.objects.filter(UserID=userid, year=now.year, month=now.month).distinct().count()
            bill_number = Bill.objects.filter(UserID=userid, year=now.year, month=now.month).count()
            try:
                b = Clock_in.objects.get(UserID=userid, year=now.year, month=now.month, day=now.day)
                ifrec = True
            except Clock_in.DoesNotExist:
                ifrec = False
            data = {
                'record': days,
                'day':billdays,
                'bill':bill_number,
                'ifrec':ifrec,
            }
        return Response(data)






#袁健
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import *
from .models import Bill


class BillingListView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        period = kwargs.get('period')
        income = request.data.get('income')
        token = request.data.get('token')
        if check_token(token):
            a = get_username(token)
            user_id = User.objects.get(username=a)
            if period == 'week':
                bills = self.get_week_billing(user_id, income)
                serializer = WeekbillSerializer(instance={'bills': bills})
            elif period == 'month':
                bills = self.get_month_billing(user_id, income)
                today = timezone.localtime(timezone.now()).date()
                year = today.year
                month = today.month
                serializer = MonthbillSerializer(instance={'bills': bills, 'year': year, 'month': month})
            elif period == 'year':
                bills = self.get_year_billing(user_id, income)
                serializer = YearbillSerializer(instance={'bills': bills})
            else:
                return Response({"error": "Invalid period"}, status=status.HTTP_400_BAD_REQUEST)
            serializer_data = serializer.data
            return Response(serializer_data)
    def get_week_billing(self, user_id, income):  
        # 获取周账单  
        today = timezone.localtime(timezone.now()).date()  
        start_of_week = today - timezone.timedelta(days=today.weekday())  
        end_of_week = start_of_week + timezone.timedelta(days=6)  
        bills = Bill.objects.filter(  
            UserID=user_id,
            (Q(year=start_of_week.year, month=start_of_week.month, day__gte=start_of_week.day) |  
             (Q(year=end_of_week.year, month=end_of_week.month, day__lte=end_of_week.day) & Q(year__lt=end_of_week.year) |  
              Q(year=end_of_week.year, month__lt=end_of_week.month))) &  
            (Q(year=start_of_week.year, month=start_of_week.month, day__lte=end_of_week.day) |  
             (Q(year=end_of_week.year, month=end_of_week.month, day__gte=start_of_week.day) & Q(year__gt=start_of_week.year) |  
              Q(year=start_of_week.year, month__gt=start_of_week.month))) &  
            Q(income=income)  
        )  
        return bills  
  
    def get_month_billing(self, user_id, income):  
        # 获取月账单  
        today = timezone.localtime(timezone.now()).date()  
        bills = Bill.objects.filter(UserID=user_id, month=today.month, income=income)
        return bills  
  
    def get_year_billing(self, user_id, income):  
        # 获取年账单  
        today = timezone.localtime(timezone.now()).date()  
        bills = Bill.objects.filter(UserID=user_id, year=today.year, income=income)
        return bills


class BillDetailView(GenericAPIView):

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        period = kwargs.get('period')
        if check_token(token):
            a = get_username(token)
            user_id = User.objects.get(username=a)
            if period == 'yearly':
                year = request.data.get('year')
                bills = Bill.objects.filter(UserID=user_id, year=year)
                serializer = YearlyDetailSerializer(instance={'bills': bills})

            elif period == 'monthly':
                year = request.data.get('year')
                month = request.data.get('month')
                bills = Bill.objects.filter(UserID=user_id, year=year, month=month)
                serializer = MonthlyDetailSerializer(instance={'bills': bills})

            serializer_data = serializer.data
            return Response(serializer_data)










#the devil
# class BillView(APIView):
#     def post(self, request):
#         data = json.loads(request.body)
#         models.Bill.objects.create(name=request.data.get('name'),income=request.data.get('income'),note=request.data.get('note'),number=request.data.get('number'),year=request.data.get('year'),mouth=request.data.get('mouth'),day=request.data.get('day'),type=request.data.get('type'))
#         return JsonResponse({'code': 200, 'msg': '创建成功', 'results': request.data})
#
# class Bill1View(APIView):
#     def delete(self, request, id):
#         book_obj = models.Bill.objects.filter(id=id).exists()
#         if book_obj:
#             models.Bill.objects.filter(id=id).delete()
#             return JsonResponse({'code': 200, 'msg': '删除一条成功'})
#         else:
#             return JsonResponse({'code': 101, 'msg': '当前不存在此账单'})

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

