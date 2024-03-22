from django import forms
from captcha.fields import CaptchaField
from app01.models import *

class create_buyerform(forms.Form):
    buyername = forms.CharField(
        required=True,
        label=u'用户名',
        error_messages={'required': u'用户名必须输入'},
        widget=forms.TextInput(),
    )
    buyer_mail = forms.EmailField(
        required=True,
        label=u'邮件地址',
        error_messages={'required': u'邮件必须输入'},
        widget=forms.TextInput(attrs={'placeholder': u'邮件地址', }),

    )
    phone_number = forms.CharField(
        required=True,
        label=u'手机号码',
        error_messages={'required': u'请输入正确手机号码'},
        widget=forms.TextInput(),
    )
    buyer_newpassword = forms.CharField(
        required=True,
        label=u'密码',
        error_messages={'required': u'请输入新的密码'},
        widget=forms.PasswordInput(),
    )



    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项目必须输入")
        elif self.cleaned_data['newpassword1'] != self.cleaned_data['newpassword2']:
            raise forms.ValidationError(u"密码不匹配.")
        elif len(self.cleaned_data['newpassword1']) < 8:
            raise forms.ValidationError(u"密码长度必须是8位")
        else:
            cleaned_data = super(create_buyerform, self).clean()
        return cleaned_data

class buyer_loginform(forms.Form):
    buyername = forms.CharField(
        required=True,
        label=u'用户名',
        error_messages={'required': u'用户名必须输入'},
        widget=forms.TextInput(),
    )
    buyerpassword = forms.CharField(
        required=True,
        label=u'密码',
        error_messages={'required': u'请输入正确的密码'},
        widget=forms.PasswordInput(),
    )
