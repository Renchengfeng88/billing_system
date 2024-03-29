from rest_framework import serializers
from app01.models import *

class User_serializers(serializers.Serializer):
    # UserID=serializers.IntegerField(primary_key=True)
    # username=serializers.CharField(max_length=250)
    # password=serializers.CharField(max_length=250)
    class Meta:
        model = User
        fields = ('url', 'UserID', 'username', 'password')



class month_budget_serializers(serializers.Serializer):
    budget_id = serializers.IntegerField()
    UserID = serializers.IntegerField(source='UserID.UserID')
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    kind = serializers.CharField(max_length=10)
    budget_amount = serializers.DecimalField(max_digits=10,decimal_places=2)



import calendar
from collections import defaultdict
import datetime
from rest_framework import serializers


class WeekbillSerializer(serializers.Serializer):
    def to_representation(self, instance):
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        number_per_day = [0] * 7
        total_amount = 0
        bill_names_total = {}

        for bill in instance['bills']:
            bill_date = datetime.date(bill.year, bill.month, bill.day)
            weekday_index = bill_date.weekday()
            number_per_day[weekday_index] += bill.number
            total_amount += bill.number
            name = bill.name
            bill_names_total[name] = bill_names_total.get(name, 0) + bill.number
        bill_names_rate = {}
        for name, total in bill_names_total.items():
            if total_amount > 0:
                bill_names_rate[name] = "{:.2%}".format(total / total_amount)
            else:
                bill_names_rate[name] = "0.00%"

        order_list = []
        for name, rate in bill_names_rate.items():
            order_list.append({
                'name': name,
                'rate': rate
            })

        order_list_sorted = sorted(order_list, key=lambda item: float(item['rate'][:-2]), reverse=True)

        return {
            'data': {
                'date': weekdays,
                'number': number_per_day,
            },
            'order': order_list_sorted
        }

#袁健
class MonthbillSerializer(serializers.Serializer):
    def to_representation(self, instance):
        year = instance['year']
        month = instance['month']
        _, days_in_month = calendar.monthrange(year, month)
        number_per_day = [0] * days_in_month
        total_amount = 0
        bill_names_total = {}

        for bill in instance['bills']:
            bill_date = datetime.date(bill.year, bill.month, bill.day)
            bill_day = bill_date.day
            number_per_day[bill_day - 1] += bill.number
            total_amount += bill.number
            name = bill.name
            bill_names_total[name] = bill_names_total.get(name, 0) + bill.number

        bill_names_rate = {}
        for name, total in bill_names_total.items():
            if total_amount > 0:
                bill_names_rate[name] = "{:.2%}".format(total / total_amount)
            else:
                bill_names_rate[name] = "0.00%"

        order_list = []
        for name, total in bill_names_total.items():
            order_list.append({
                'name': name,
                'rate': bill_names_rate[name]
            })

        order_list_sorted = sorted(order_list, key=lambda item: float(item['rate'][:-2]), reverse=True)

        return {
            'data': {
                'day': days_in_month,
                'number': number_per_day,
            },
            'order': order_list_sorted
        }


class YearbillSerializer(serializers.Serializer):
    def to_representation(self, instance):
        monthly_totals = defaultdict(int)
        bill_names_total = defaultdict(int)
        total_amount = 0

        for bill in instance['bills']:
            bill_date = datetime.date(bill.year, bill.month, bill.day)
            bill_year, bill_month = bill_date.year, bill_date.month
            monthly_totals[bill_month] += bill.number
            bill_names_total[bill.name] += bill.number
            total_amount += bill.number

        number = [monthly_totals.get(month, 0) for month in range(1, 13)]
        bill_names_rate = {}
        for name, total in bill_names_total.items():
            if total_amount > 0:
                bill_names_rate[name] = "{:.2%}".format(total / total_amount)
            else:
                bill_names_rate[name] = "0.00%"

        order_list = []
        for name, total in bill_names_total.items():
            order_list.append({
                'name': name,
                'rate': bill_names_rate[name]
            })

        order_list_sorted = sorted(order_list, key=lambda item: float(item['rate'][:-2]), reverse=True)

        return {
            'data': {
                'number': number,
            },
            'order': order_list_sorted
        }


class YearlyDetailSerializer(serializers.Serializer):
    def to_representation(self, instance):
        monthly_in = defaultdict(int)
        monthly_out = defaultdict(int)

        for bill in instance['bills']:
            bill_date = datetime.date(bill.year, bill.month, bill.day)
            bill_month = bill_date.month
            if bill.income == 1:
                monthly_in[bill_month] += bill.number
            else:
                monthly_out[bill_month] += bill.number

        monthly_summary = []
        for month in range(1, 13):
            summary = {
                'month': month,
                'in': monthly_in.get(month, 0),
                'out': monthly_out.get(month, 0)
            }
            monthly_summary.append(summary)

        return monthly_summary


class MonthlyDetailSerializer(serializers.Serializer):
    def to_representation(self, instance):
        bills_by_date = defaultdict(list)
        day_in = defaultdict(int)
        day_out = defaultdict(int)

        for bill in instance['bills']:
            bill_date = datetime.date(bill.year, bill.month, bill.day)
            bills_by_date[bill_date].append({
                'name': bill.name,
                'note': bill.note,
                'number': bill.number,
                'id': bill.id,
            })
            if bill.income == 1:
                day_in[bill_date] += bill['number']
            else:
                day_out[bill_date] += bill['number']

        monthly_details = []
        for date, bills in bills_by_date.items():
            monthly_details.append({
                'time': date.strftime('%Y-%m-%d'),
                'bill': bills,
                'in': day_in[date],
                'out': day_out[date],
            })

        return monthly_details


class searchTimeSerializer(serializers.Serializer):
    def to_representation(self, instance):
        bills_by_date = defaultdict(list)
        for bill in instance['bill']:
            bill_date = datetime.date(bill.year, bill.month, bill.day)
            print(bill_date)
            bills_by_date[bill_date].append({
                'name': bill.name,
                'note': bill.note,
                'number': bill.number,
            })
        bill_time = []
        for date, bills in bills_by_date.items():
            bill_time.append({
                'time': date.strftime('%Y-%m-%d'),
                'bill': bills,
            })
        print(bill_time)
        return bill_time


class searchNumberSerializer(serializers.Serializer):
    def to_representation(self, instance):
        bill_number = []
        for bill in instance['bill']:
            bill_date = datetime.date(bill.year, bill.month, bill.day)
            bill_data = {
                'name': bill.name,
                'note': bill.note,
                'number': bill.number,
            }
            bill_number.append({
                'time': bill_date.strftime('%Y-%m-%d'),
                'bill': bill_data,
            })
        return bill_number