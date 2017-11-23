#encoding:utf-8
from django.shortcuts import render
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist,PermissionDenied
from django.db.models.query import EmptyQuerySet,QuerySet
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect

from .models import Active,Newer,Group,Limit,Speed,Crowd,Coupon,Activeship,Activeuser
from .models import Provice,Location,City,Country,ActiveRange,Tribe
from .models import User,CoinItem,MyCoupon,Collection,Address,UserRank
from .models import Category,Product,ProductOption,Commet,Standard,ShopCart,ShopCartItem,Order,OrderItem
from .models import Promote,PromoteDeal,Page,Cell,Slider
from ActiveInfo import *
from django import forms
from .forms import AddressForm
import os
from wechatpy import WeChatClient
from wechatpy.crypto import WeChatCrypto
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature,random_string
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.exceptions import InvalidAppIdException
from wechatpy.oauth import WeChatOAuth
from wechatpy.pay import WeChatPay
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.conf import settings
from datetime import datetime,timedelta
import time
from django.core import serializers
from decimal import Decimal
from django.utils.timezone import utc
from datetime import timedelta
# Create your views here.
#全国省分
provice=Provice.objects.all()

wechatoauth = WeChatOAuth(
    settings.WECHAT_APPID,
    settings.WECHAT_SECRET,
    settings.WECHAT_REDIRECT_URL,
    'snsapi_userinfo'
)
wechatpay=WeChatPay(
	settings.WECHAT_APPID,
	settings.WECHAT_API_KEY,
	settings.WECHAT_MCH_ID
)

#微信支付授权
def oauth(method):
    @wraps(method)
    def warpper(request,*args, **kwargs):
    	code=request.GET.get('code')
    	if code:
            try:
            	wechatoauth.fetch_access_token(code)
                user_info = wechatoauth.get_user_info()
            except Exception as e:
                print e.errmsg, e.errcode
            else:
                user=None
                try:
                	user=User.objects.get(openid=user_info['openid'])
                except ObjectDoesNotExist:
                	user=User.objects.create(name=user_info['nickname'],openid=user_info['openid'],avator_url=user_info['headimgurl'],rank='PT')

                request.session['user_id']=user.id
        else:
			return HttpResponseRedirect(wechatoauth.authorize_url)
        return method(request,*args, **kwargs)
    return warpper
#主页page
#@oauth
def index(request):
	categorys=Category.objects.all()
	slider=Slider.objects.all()
	page=Page.objects.all()
	context={
	    'categorys':categorys,
	    'slider':slider,
	    'page':page
	}
	return render(request,'index/index.html',context)


def getUser(request):
	user_id=8#request.session.get('user_id')
	if user_id is None:
		return None
	user=None
	try:
		user=User.objects.get(id=user_id)
	except ObjectDoesNotExist:
		pass
	return user

def getActiveInfo(querySet,user):
	activeinfos,iswatch=[],False
	for item in querySet.all():
		iswatch=item.activeuser_set.filter(user_id=user.id).exists()
		thumb=item.thumb.url if item.thumb.name is not None else '/static/icons/active_%s.png'%item.shoptype
		ai=ActiveInfo(name=item.name,thumb=thumb,appendtime=item.appendtime,type=item.shoptype,typename=item.get_shoptype_display(),activeid=item.id,watch=iswatch,effective=item.effective(),description=item.description)
		activeinfos.append(ai)
	
	return activeinfos

#活动page
def active(request):
	user=getUser(request)
	if user is None:
		return HttpResponseRedirect('/index')
	defaultAddress=user.defaultAddress()

	activeinfos=getActiveInfoByUser(user,defaultAddress)
	context={
		'address':defaultAddress,
		'activeinfos':activeinfos
	}		
	return render(request,'active/active.html',context)
#获取某一用户的活动
def getActiveInfoByUser(user,address):
	activeinfos=[]
	#全国活动范围
	activeRanges=ActiveRange.objects.all()
	#获取活动范围,地理位置需要重写,因为活动范围可以更宽泛
	ranges=[]
	for activerange in activeRanges:
		if activerange.judgeByAddress(address) and activerange.judgeByRank(user) and activerange.judgeByTribe(user):
			ranges.append(activerange)

	for range in ranges:
		if range.active_set.exists():
			activeinfos.extend(getActiveInfo(range.active_set,user))
	#活动信息排序
	results=None
	if len(activeinfos)>0:
		results=sorted(activeinfos,key=lambda activeinfo:activeinfo.appendtime,reverse=True)
	return results
#获取未阅读的活动数
def getActiveCount(request):
	user=getUser(request)
	defaultAddress=user.defaultAddress()

	activeinfos=getActiveInfoByUser(user,defaultAddress)
	count=0
	if activeinfos is not None:
		for item in activeinfos:
			if not item.watch:
				count=count+1
	return JsonResponse({'count':count})

#分类
def category(request,category_id,page=1):
	categorys=Category.objects.all()
	productLists=Product.objects.filter(category_id=category_id)

	paginator=Paginator(productLists,15)

	#当前分类
	currentCategory=Category.objects.get(id=category_id)

	try:
	    products=paginator.page(page)
	except PageNotAnInteger:
	    products=paginator.page(1)
	except EmptyPage:
	    products=paginator.page(paginator.num_pages)
	context={
	    'products':products,
	    'categorys':categorys,
	    'category':currentCategory
	}
	return render(request,'category/category.html',context)
#产品详情
def detail(request,product_id=1):
	product=Product.objects.get(id=product_id)

	options=product.productoption_set.all()
	defaultOption=options.get(isdefault=True)

	#将库存为0的产品设置为失效
	options.filter(count__lte=0).update(effective=False)

	if defaultOption is None:
		product.productoption_set.first().isdefault=True

	backUrl='/category/%s/1'%product.category.id
	context={
		'backUrl':backUrl,
		'product':product,
		'defaultOption':defaultOption,
		'options':options.filter(shoptype='product'),
		'shoptype':'product',
		'shoptypeID':product.id
	}
	return render(request,'detail/detail.html',context)
#产品规格
def standard(request,product_id):
	product=Product.objects.get(id=product_id)
	context={
		'product':product
	}
	return render(request,'detail/standard.html',context)
#产品可选类型
def productOption(request,p0roduct_id):
	product=Product.objects.get(id=product_id)
	context={
		'product':product
	}
	return render(request,'detail/productOption.html',context)
#售后和包装
def service(request,product_id):
	product=Product.objects.get(id=product_id)
	context={
		'product':product
	}
	return render(request,'detail/service.html',context)
#评价列表
def commetList(request,product_id):
	product=Product.objects.get(id=product_id)
	context={
		'product':product
	}
	return render(request,'detail/commetList.html',context)
#团购
def group(request,group_id):
	user=getUser(request)
	if user is None:
		return HttpResponseRedirect('/index')

	group=Group.objects.get(id=group_id)

	#如果团购无范围的话,抛出异常
	if not group.activerange.all().exists():
		raise PermissionDenied
	
	#临时的写法,由第一个活动定义产品(这并不是一个好的做法,以后改吧)
	product=group.activerange.all()[0].product
	options=product.productoption_set.filter(shoptype='group')

	#如果团购无产品的话抛出异常
	if len(options)==0:
		raise PermissionDenied

	try:
		defaultOption=options.get(isdefault=True)
	except ObjectDoesNotExist:
		defaultOption=options[0]

	#如果团购活动失效的话,相应的产品选项也将失效
	if not group.effective() and defaultOption.effective==True:
		defaultOption.effective=False

	percert=float(group.complete)/float(group.count)*100

	

	#修改阅读状态
	active_id=group.active_ptr.id
	
	print '************'
	print user
	print '************'
	if not Activeuser.objects.filter(active_id=active_id,user=user).exists():
		Activeuser.objects.create(active_id=active_id,user=user)

	#结束时间
	timespan=group.endtime-datetime.utcnow().replace(tzinfo=utc)
	d=timespan.days
	m,s=divmod(timespan.seconds,60)
	h, m = divmod(m, 60)

	endtime="%01d天%01d小时%01d分钟%01d秒" % (d,h, m, s)
	context={
		'backUrl':'/active',
		'group':group,
		'product':product,
		'endtime':endtime,
		'percert':percert,
		'defaultOption':defaultOption,
		'options':options,
		'shoptype':'group',
		'shoptypeID':group.id
	}
	return render(request,'detail/group/group.html',context)
#众筹
def crowd(request,crowd_id):
	user=getUser(request)
	if user is None:
		return HttpResponseRedirect('/index')

	crowd=Crowd.objects.get(id=crowd_id)

	#如果众筹无范围的话,抛出异常
	if not crowd.activerange.all().exists():
		raise PermissionDenied
	
	#临时的写法,由第一个活动定义产品(这并不是一个好的做法,以后改吧)
	product=crowd.activerange.all()[0].product
	options=product.productoption_set.filter(shoptype='crowd')

	#如果众筹无产品的话抛出异常
	if len(options)==0:
		raise PermissionDenied

	try:
		defaultOption=options.get(isdefault=True)
	except ObjectDoesNotExist:
		defaultOption=options[0]

	#如果众筹活动失效的话,相应的产品选项也将失效
	if not crowd.effective() and defaultOption.effective==True:
		defaultOption.effective=False

	percert=float(crowd.complete)/float(crowd.count)*100

	#修改阅读状态
	active_id=crowd.active_ptr.id
	if not Activeuser.objects.filter(active_id=active_id,user=user).exists():
		Activeuser.objects.create(active_id=active_id,user=user)

	#结束时间
	timespan=crowd.endtime-datetime.utcnow().replace(tzinfo=utc)
	d=timespan.days
	m,s=divmod(timespan.seconds,60)
	h, m = divmod(m, 60)

	endtime="%01d天%01d小时%01d分钟%01d秒" % (d,h, m, s)
	context={
		'backUrl':'/active',
		'crowd':crowd,
		'product':product,
		'endtime':endtime,
		'percert':percert,
		'defaultOption':defaultOption,
		'options':options,
		'shoptype':'crowd',
		'shoptypeID':crowd.id
	}
	return render(request,'detail/crowd/crowd.html',context)
#限时购
def limit(request,limit_id):
	user=getUser(request)
	if user is None:
		return HttpResponseRedirect('/index')
	limit=Limit.objects.get(id=limit_id)

	#如果团购无范围的话,抛出异常
	if not limit.activerange.all().exists():
		raise PermissionDenied

	product=limit.activerange.all()[0].product
	options=product.productoption_set.filter(shoptype='limit')

	#如果限时抢购无产品的话抛出异常
	if len(options)==0:
		raise PermissionDenied

	try:
		defaultOption=options.get(isdefault=True)
	except ObjectDoesNotExist:
		defaultOption=options[0]

	#如果限时抢购活动失效的话,相应的产品选项也将失效
	if not limit.effective() and defaultOption.effective==True:
		defaultOption.effective=False

	#修改阅读状态
	active_id=limit.active_ptr.id
	if not Activeuser.objects.filter(active_id=active_id,user=user).exists():
		Activeuser.objects.create(active_id=active_id,user=user)
	#结束时间
	timespan=limit.endtime-datetime.utcnow().replace(tzinfo=utc)
	d=timespan.days
	m,s=divmod(timespan.seconds,60)
	h, m = divmod(m, 60)

	endtime="%01d天%01d小时%01d分钟%01d秒" % (d,h, m, s)
	context={
		'backUrl':'/active',
		'limit':limit,
		'endtime':endtime,
		'product':product,
		'defaultOption':defaultOption,
		'options':options,
		'shoptype':'limit',
		'shoptypeID':limit.id
	}
	return render(request,'detail/limit/limit.html',context)
#新手礼包
def newer(request,newer_id):
	newer=Newer.objects.get(id=newer_id)
	context={
		'newer':newer
	}
	return render(request,'active/news.html',context)
#加速度
def speed(request,speed_id):
	user=getUser(request)
	if user is None:
		return HttpResponseRedirect('/index')
	speed=Speed.objects.get(id=speed_id)

	#修改阅读状态
	active_id=speed.active_ptr.id
	if not Activeuser.objects.filter(active_id=active_id,user=user).exists():
		Activeuser.objects.create(active_id=active_id,user=user)
	#结束时间
	timespan=speed.endtime-datetime.utcnow().replace(tzinfo=utc)

	d=timespan.days
	m,s=divmod(timespan.seconds,60)
	h, m = divmod(m, 60)
	endtime="%01d天%01d小时%01d分钟%01d秒" % (d,h, m, s)
	context={
		'speed':speed,
		'endtime':endtime
	}
	return render(request,'active/speed.html',context)
#优惠券
def coupon(request,coupon_id):
	user=getUser(request)
	if user is None:
		return HttpResponseRedirect('/index')
	coupon=Coupon.objects.get(id=coupon_id)
	#查询是否已领取
	result=True if MyCoupon.objects.filter(user_id=user.id,coupon_id=coupon_id).exists() else False

	#获取参与的社群,位置,等级
	tribes,locations,ranks=[],[],[]
	for range in coupon.activerange.all():
		if range.tribe is not None:
			tribes.append(range.tribe)
		if range.location is not None:
			locations.append(range.location)
		if range.rank is not None:
			ranks.append(range.get_rank_display())
	#修改阅读状态
	active_id=coupon.active_ptr.id
	print active_id
	if not Activeuser.objects.filter(active_id=active_id,user=user).exists():
		Activeuser.objects.create(active_id=active_id,user=user)
	context={
		'coupon':coupon,
		'tribes':tribes,
		'locations':locations,
		'ranks':ranks,
		'result':result
	}
	return render(request,'active/coupon.html',context)


#领取优惠券
def getCoupon(request,coupon_id):
	user=getUser(request)
	try:
		coupon=Coupon.objects.get(id=coupon_id)
	except ObjectDoesNotExist:
		return JsonResponse({'result':False,'tip':'出错了!'})

	if coupon.complete>=coupon.count:
		return JsonResponse({'result':False,'tip':'已被抢光!'})
	
	if MyCoupon.objects.filter(user_id=user.id,coupon_id=coupon_id).exists():
		return JsonResponse({'result':False,'tip':'您已抢领过该优惠券!'})

	#满足社群,等级
	ranges=coupon.activerange.all()

	#一个活动范围等级和部落都满足才算满足
	satisfy=False
	for range in ranges:
		if range.judgeByRank(user) and range.judgeByTribe(user):
			satisfy=True
			break
	if not satisfy:
		return JsonResponse({'result':False,'tip':'您不满足领取条件!'})

	MyCoupon.objects.create(user_id=user.id,coupon=coupon,useStatus='KY')

	return JsonResponse({'result':True,'tip':'恭喜您,领取成功!'})

#加入猫氏部落
def append(request):
	return render(request,'active/append.html')

#收货地址
def address(request):
	user=getUser(request)
	try:
		addresses=Address.objects.filter(user_id=user.id)
	except ObjectDoesNotExist:
		pass
	url=request.META['HTTP_REFERER'].split('/')[-1]

	return render(request,'address.html',{'addresses':addresses,'url':url})
#新增收货地址
def newAddress(request,url):
	user=getUser(request)
	if request.method=='POST':
		form=AddressForm(request.POST)
		if form.is_valid():
			name=form.cleaned_data['name']
			mobile =form.cleaned_data['mobile']
			provice_id=form.cleaned_data['provice_id']
			city_id=form.cleaned_data['city_id']
			region_id=form.cleaned_data['region_id']
			country_id=form.cleaned_data['country_id']
			detail=form.cleaned_data['detail']
			isdefault=form.cleaned_data['isdefault']
			if isdefault:
				try:
					defaultAddress=Address.objects.get(isdefault=True)
					defaultAddress.isdefault=False
					defaultAddress.save()
				except ObjectDoesNotExist:
					pass
			location,created=Location.objects.get_or_create(provice_id=provice_id,city_id=city_id,region_id=region_id,country_id=country_id)
			address=Address(user=user,name=name,mobile=mobile,location=location,detail=detail,isdefault=isdefault)
			address.save()
			return HttpResponseRedirect('/'+url)
	else:
		form=AddressForm()
	return render(request,'newAddress.html',{'form':form,'url':url,'provice':provice})
#删除收货地址
def delAddress(request,address_id):
	try:
		address=Address.objects.get(id=address_id)
		address.delete()
	except ObjectDoesNotExist:
		pass
	return JsonResponse({'result':True})
#设置默认收货地址
def setDefaultAddress(request,address_id,url):
	user=getUser(request)
	address=Address.objects.get(id=address_id)

	if url=='orderConfirm':
		#如果选择的地址与购物车中活动要求不符的话返回
		shopcart=ShopCart.objects.get(user_id=user.id)
		for item in shopcart.items():
			if not Active.objects.get(id=item.shoptypeID).justifyAddress(address):
				return JsonResponse({'result':'wrongaddress'})

	Address.objects.filter(user=user,isdefault=True).update(isdefault=False)
	address.isdefault=True
	address.save()
	return JsonResponse({'result':True})
#加入购物车
def addInCart(request):
	user=getUser(request)
	shopcart=user.shopcart()
	if request.method=='POST':
		product_id=request.POST['product_id']
		productOption_id=request.POST['option_id']
		count=request.POST['count']
		shoptype=request.POST['shoptype']
		shoptypeID=request.POST['shoptypeID']
		buytype=request.POST['buytype']

		#查询库存
		option=ProductOption.objects.get(id=productOption_id)
		if option.count<1:
			return JsonResponse({'result':'empty'})

		if shoptype=='product':
			#如果产品选项编号已存在,数量+1
			shopcart.add(shoptype,shoptypeID,product_id,productOption_id,count)
			return JsonResponse({'result':'success','buytype':buytype})

		#如果收货地址不存在的话
		if user.defaultAddress() is None:
			return JsonResponse({'result':'emptyaddress','buytype':buytype})

		
		active=Active.objects.get(id=shoptypeID)

		#查询活动是否已结束
		if not active.effective():
			return JsonResponse({'result':'over'})

		#一个活动范围等级和部落地理位置都满足才算满足
		satisfy=active.judgeByUser(user)
		if not satisfy:
			return JsonResponse({'result':'notsatisfy'})

		#如果产品选项编号已存在,数量+1
		shopcart.add(shoptype,shoptypeID,product_id,productOption_id,count)
		return JsonResponse({'result':'success','buytype':buytype})
#购物车项
def shopcart(request):
	shopcart=getUser(request).shopcart()
	#如果购物车使用了优惠券，则重置
	if shopcart.mycoupon!=0:
		shopcart.mycoupon=0
		shopcart.save()
	context={
		'shopcart':shopcart,
	}
	return render(request,'shopcart/shopcart.html',context)

#获取产品总价
def getMoney(request):
	user=getUser(request)
	shopcart=ShopCart.objects.get(user_id=user.id)

	cartMoney=shopcart.getMoney()

	myCoupon=shopcart.getMyCoupon()

	#使用果币数
	useCoins=user.useCoinCount(cartMoney) if shopcart.useCoin else 0
	#计算的运费
	freight=shopcart.getFreight()

	#需要减掉的运费
	mailReduce=myCoupon.reduceMail(freight) if myCoupon is not None else 0
	#购物券优惠额
	reduce=myCoupon.coupon.reduce if myCoupon is not None else 0

	totalMoney=cartMoney+freight-Decimal(useCoins)/100-reduce-mailReduce
	context={
		'cartMoney':cartMoney,
		'reduce':reduce,
		'freight':freight,
		'mailReduce':mailReduce,
		'useCoins':useCoins,
		'totalMoney':totalMoney
	}
	return JsonResponse(context)
#获取应付总价
def getTotalMoney(user):
	shopcart=user.shopcart()

	cartMoney=shopcart.getMoney()

	myCoupon=shopcart.getMyCoupon()

	#使用果币数
	useCoins=user.useCoinCount(cartMoney) if shopcart.useCoin else 0
	#计算的运费
	freight=shopcart.getFreight()

	#需要减掉的运费
	mailReduce=myCoupon.reduceMail(freight) if myCoupon is not None else 0
	#购物券优惠额
	reduce=myCoupon.coupon.reduce if myCoupon is not None else 0

	totalMoney=cartMoney+freight-Decimal(useCoins)/100-reduce-mailReduce
	return totalMoney

#从购物车中删除
def delShopCartItem(request,shopcartitem_id):
	shopcart=getUser(request).shopcart()
	shopcart.deleteItem(shopcartitem_id)
	return JsonResponse({'result':True,'totalMoney':shopcart.getMoney()})

#更改购物车产品数量
def changeShopCartItemCount(request,shopcartitem_id,count):
	user=getUser(request)
	shopcart=user.shopcart()
	shopcart.changeItemCount(shopcartitem_id,count)
	totalMoney=shopcart.getMoney()
	return JsonResponse({'result':True,'totalMoney':totalMoney})
#获取购物车中产品数
def getShopCartItemCount(request):
	user=getUser(request)
	count=user.shopcart().itemsCount()
	return JsonResponse({'count':count})

#结账时检测购物车状态,确认是否可结账
def getShopCartStatus(request):
	shopcart=getUser(request).shopcart()
	count=shopcart.itemsCount()
	#看是否已选择购物车中商品
	checkResult=shopcart.isCheck()
	return JsonResponse({'count':count,'check':checkResult})

#全选或取消全选
def selectAll(request,bool):
	shopcart=getUser(request).shopcart()
	check=True if bool=='1' else False
	result=True
	if check:
		result=shopcart.selectAll()
	else:
		result=shopcart.unselectAll()
	return JsonResponse({'result':result,'totalMoney':shopcart.getMoney()})
#选择购物车某一项
def selectCartItem(request,shopcartitem_id):
	shopcart=getUser(request).shopcart()
	efectCount=shopcart.selectItem(shopcartitem_id)
	return JsonResponse({'result':efectCount,'totalMoney':shopcart.getMoney()})
#取消购物车某一项
def unselectCartItem(request,shopcartitem_id):
	shopcart=getUser(request).shopcart()
	efectCount=shopcart.unselectItem(shopcartitem_id)
	return JsonResponse({'result':efectCount,'totalMoney':shopcart.getMoney()})
#确认订单
def orderConfirm(request):
	user=getUser(request)
	shopcart=user.shopcart()

	#如果购物车为空或没有选择商品的话
	if shopcart.isEmpty() or not shopcart.isCheck():
		raise PermissionDenied

	#获取默认地址
	defaultAddress=user.defaultAddress()
	
	#果币可抵用
	coin_equal=user.useCoinCount(shopcart.getMoney())/100;

	shopcartitems=shopcart.checkItems()

	#果券
	myCoupon=MyCoupon.objects.get(id=shopcart.mycoupon) if shopcart.mycoupon!=0 else None

	totalMoney=int(getTotalMoney(user)*100)

	#生成调用微信支付的参数
	result=wechatpay.order.create('JSAPI','www.fangchengku.com',totalMoney,'http://www.fangchengku.com/wepay_result',user_id=user.openid)
	jsapiparames=wechatpay.jsapi.get_jsapi_params(result['prepay_id'])

	context={
		'user':user,
		'coin_equal':coin_equal,
		'address':defaultAddress,
		'shopcart':shopcart,
		'mycoupon':myCoupon,
		'data':jsapiparames
	}
	return render(request,'shopcart/orderConfirm.html',context)

#是否使用果币
def isUseCoin(request,boolString):
	user=getUser(request)
	shopcart=user.shopcart()
	shopcart.useCoin=True if boolString=='true' else False
	shopcart.save()
	return JsonResponse({'data':True})

#支付成功跳转页面
def paySuccessPage(request):
	return render(request,'shopcart/paySuccessPage.html')

#支付结果通知
@csrf_exempt
def wepay_result(request):
	data=wechatpay.parse_payment_result(request.body)
	user=User.objects.get(openid=data['openid'])
	#如果支付成功,然后生成订单到数据库
	if data['return_code']=='SUCCESS' and data['result_code']=='SUCCESS':
		takeOrder(data,user)

	result='''
		<xml>
		  <return_code><![CDATA[%s]]></return_code>
		  <return_msg><![CDATA[OK]]></return_msg>
		</xml>
	'''%data['return_code']
	return HttpResponse(result)

#跳过支付,直接下单
def takeOrderDirect(request):
	user=getUser(request)
	data={
		'out_trade_no':'no_cash_order',
		'cash_fee':0
	}
	takeOrder(data,user)
	return render(request,'shopcart/paySuccessPage.html')
#立即下单
def takeOrder(data,user):
	shopcart=user.shopcart()
	#1.生成订单
	shopcartitems=shopcart.checkItems()

	#判断购物车是否清零,防止重复下订单
	if shopcartitems.count()>0:
		address=user.defaultAddress()

		if address is None or address is EmptyQuerySet:
			raise PermissionDenied

		order=Order(orderNumber=data['out_trade_no'],user=user,receive_name=address.name,mobile=address.mobile,location=address.location,
			detail=address.detail,totalMoney=Decimal(data['cash_fee'])/100,orderStatusOption='PAYSUCCESS')

		#如果使用优惠券
		if shopcart.mycoupon!=0:
			order.mycoupon_id=shopcart.mycoupon
			MyCoupon.objects.filter(id=shopcart.mycoupon,user=user).update(useStatus='YSY')

		#使用的果币额,更新果币额度
		if shopcart.useCoin and user.coinCount>0:
			order.coin=user.useCoinCount(totalMoney)
			user.coinCount-order.coin
			user.save()
			#记录果币状态变更
			CoinItem.objects.create(user=user,change=useCoins,typename='GWZC',detail=order.orderNumber)
		#保存订单
		order.save()
		
		for item in shopcartitems:
			OrderItem.objects.create(order=order,shoptype=item.shoptype,shoptypeID=item.shoptypeID,product=item.product,productOption=item.productOption,product_name=item.product.name,
				optionName=item.productOption.name,thumb=item.productOption.avator,price=item.productOption.price,count=item.count)
			#更新活动参与人
			addinActive(user,item.shoptypeID)
			#更新活动参与数量
			if item.shoptype!='product':
				active=Active.objects.get(id=item.shoptypeID)
				active.complete=active.complete+item.count
				active.save()
			#减少库存
			item.productOption.count=(item.productOption.count-item.count)
			item.productOption.save()
		#清空购物车中已选项
		shopcartitems.delete()
	else:
		pass
#更新某一活动的参与状态
def addinActive(user,shoptypeID):
	Activeuser.objects.update_or_create(active_id=shoptypeID,user=user,isparticipation=True)


#我的
def myself(request):
	user=getUser(request)
	return render(request,'myself/myself.html',{'user':user})
#我的售后
def myservice(request):
	return render(request,'myself/myservice.html')
#收藏
def collect(request,product_id):
	user=getUser(request)
	obj,result=Collection.objects.get_or_create(user=user,product_id=product_id)
	if result==False:
		obj.delete()
	return JsonResponse({'result':result})
#我的收藏
def collection(request):
	user=getUser(request)
	collections=Collection.objects.filter(user_id=user.id)
	context={
		'collections':collections
	}
	return render(request,'myself/collection.html',context)
#果币
def coin(request):
	user=getUser(request)
	return render(request,'myself/coin.html',{'user':user})
#果币明细
def coinDetail(request):
	user=getUser(request)
	coinitems=CoinItem.objects.filter(user_id=user.id)
	return render(request,'myself/coinDetail.html',{'coinitems':coinitems})

#我的果券
def myCoupon(request):
	user=getUser(request)
	mycoupons=MyCoupon.objects.filter(user_id=user.id)
	return render(request,'myself/mycoupon.html',{'mycoupons':mycoupons})

#可使用优惠券列表
def useCoupon(request):
	user=getUser(request)
	mycoupons=MyCoupon.objects.filter(user_id=user.id)
	myusefullCoupons=getUserfullCoupon(mycoupons,user)
	return render(request,'shopcart/usecoupon.html',{'mycoupons':myusefullCoupons})

#使用优惠券
def doUseMyCoupon(request,mycoupon_id):
	user=getUser(request)
	shopcart=user.shopcart()

	#如果优惠券不存在,抛出403
	if not MyCoupon.objects.filter(id=mycoupon_id).exists():
		raise PermissionDenied
	#设置优惠券状态
	MyCoupon.objects.filter(id=mycoupon_id).update(useStatus='ZZSY')

	#如果购物车已使用一张优惠券，重置
	# if shopcart.mycoupon!=0:
	# 	MyCoupon.objects.filter(id=shopcart.mycoupon).update(useStatus='KY')

	#选择优惠券
	shopcart.mycoupon=mycoupon_id
	shopcart.save()

	return HttpResponseRedirect('/orderConfirm')

#通过身份,部落,产品,分类获取可用优惠券
def getUserfullCoupon(mycoupons,user):
	#获得可用优惠券
	for item in mycoupons:
		if not item.coupon.effective():
			item.useStatus='YGQ'
		else:
			ranges=item.coupon.activerange.all()#获取每张优惠券的活动范围
			for range in ranges:
				if not getByRange(range,user,item.coupon):
					item.useStatus=='BKY'
	return mycoupons

#根据活动范围判断优惠券是否有效
def getByRange(range,user,coupon):
	shopcart=user.shopcart()
	defaultAddress=user.defaultAddress()

	#如果不满足地理位置
	if not range.judgeByAddress(defaultAddress):
		return False

	#如果优惠券对产品没有要求,购物车总产品价格满足优惠券要求
	if range.product==None and shopcart.getMoney()>coupon.over:
		return True
			
	#如果优惠券对产品有要求,产品价格满足优惠券要求
	for item in shopcart.checkItems():
		if range.product==item.product and item.getMoney()>coupon.over:
			return True
	return False

#获取微信jsapi签名
@csrf_exempt
def jsapi_signature(request):
    noncestr = random_string()
    timestamp = int(time.time())
    url = request.POST['url']

    client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
    ticket_response = client.jsapi.get_ticket()
    signature = client.jsapi.get_jsapi_signature(
        noncestr,
        ticket_response['ticket'],
        timestamp,
        url
    )
    ret_dict = {
        'noncestr': noncestr,
        'timestamp': timestamp,
        'url': url,
        'signature': signature,
    }
    return JsonResponse(ret_dict)
#设置
def setup(request):
	return render(request,'myself/setup.html')
#我的订单
def order(request):
	user=getUser(request)
	orders=Order.objects.filter(user_id=user.id)
	return render(request,'myself/order.html',{'orders':orders})
#评价商品
def commet(request):
	if request.method=='GET':
		return render(request,'myself/commet.html')
	else:
		commetForm=commetForm(request.POST)
		if commetForm.is_valid():
			receivename=addressForm.cleaned_data['receivename']
			mobile =addressForm.cleaned_data['mobile']
			address=addressForm.cleaned_data['address']
			return HttpResponseRedirect('myself/commetSuccess.html')
		else:
			return HttpResponse('something is wrong!')
#评价成功
def commetSuccess(request):
	return render(request,'myself/commet.html')
#订单详情
def orderDetail(request,order_id):
	order=Order.objects.get(id=order_id)
	return render(request,'myself/orderDetail.html',{'order':order})

#获取街道信息
def getCountry(request,region_id):
	countrys=Country.objects.filter(region_id=region_id)
	data=serializers.serialize("json",countrys)
	return JsonResponse({'data':data})


