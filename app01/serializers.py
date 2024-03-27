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



