# -*- coding:utf-8 -*-
from django import forms

class AddressForm(forms.Form):
	name=forms.CharField(max_length=8,error_messages={"required":"收货人不能为空!"})
	mobile = forms.CharField(max_length=11,error_messages={"required": "联系电话不能为空",})
	provice_id=forms.IntegerField(error_messages={"required": "请选择省份",})
	city_id=forms.IntegerField(error_messages={"required": "请选择城市",})
	region_id=forms.IntegerField(error_messages={"required": "请选择区县",})
	country_id=forms.IntegerField(error_messages={"required": "请选择乡村街道",})
	detail=forms.CharField(max_length=128,error_messages={"required":"请填写详细送货地址!"})
	isdefault=forms.BooleanField(required=False)