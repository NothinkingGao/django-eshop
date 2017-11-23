#coding:utf-8
from __future__ import unicode_literals
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
from datetime import datetime,timedelta
from smart_selects.db_fields import ChainedForeignKey
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist,PermissionDenied
from decimal import Decimal
#交易类型
TYPE_OPTION_ITEMS=(
	('product','产品'),
	('category','分类'),
	('tribe','部落'),
	('rank','用户等级'),
	('limit','限时抢购'),
	('group','团购'),
	('newer','新人礼包'),
	('article','文章'),
	('speed','加速度'),
	('crowd','众筹'),
	('coupon','优惠券')
)
#用户等级
USER_RANK=(
	('PT','普通用户'),
	('HJ','黄金用户'),
	('BJ','白金用户'),
	('ZS','钻石用户')
)

class Page(models.Model):
	title=models.CharField(max_length=32,verbose_name='标题')
	showTitle=models.BooleanField(verbose_name="显示标题",default=False)
	Page_OPTION=(
		('4','单行四列'),
		('2','单行两列'),
		('1','单行单列')
	)
	type=models.CharField(
		max_length=32,
		choices=Page_OPTION,
		default='1'
	)
	orderby=models.IntegerField(verbose_name='排序')

	def __unicode__(self):
		return self.title

class Slider(models.Model):
	image=models.ImageField(upload_to='products',verbose_name='缩略图')
	name=models.CharField(max_length=32,verbose_name='标题')
	url=models.CharField(max_length=32,verbose_name='链接')
	orderby=models.IntegerField(verbose_name='排序')


	def __unicode__(self):
		return self.name

class Cell(models.Model):
	name=models.CharField(max_length=32,verbose_name='名称')
	Page=models.ForeignKey(Page)
	price=models.CharField(max_length=32,verbose_name='价格')
	thumb=models.ImageField(upload_to='products',verbose_name='缩略图')
	url=models.CharField(max_length=128,verbose_name='链接')
	orderby=models.IntegerField(verbose_name='排序')

	def __unicode__(self):
		return self.name

#产品分类
class Category(models.Model):
	name = models.CharField(max_length=32,verbose_name='分类')
	sale=models.BooleanField(verbose_name="上架",default=False)
	parent=models.ForeignKey('self',verbose_name='父分类',null=True,blank=True)
	appendtime=models.DateField(auto_now_add=True)

	class Meta:
		verbose_name='产品分类'
		verbose_name_plural='产品分类'

	def __unicode__(self):
		return self.name

#产品
class Product(models.Model):
	name = models.CharField(max_length=32,verbose_name='产品名称')
	thumb=models.ImageField(upload_to='products',verbose_name='缩略图')
	category=models.ForeignKey(Category,verbose_name='分类')
	number=models.IntegerField(verbose_name="总数")
	description=models.TextField(verbose_name="产品描述")
	body=RichTextUploadingField(config_name='awesome_ckeditor',verbose_name="产品详情")
	package = models.CharField(max_length=32,verbose_name='包装')
	service = models.CharField(max_length=32,verbose_name='售后')
	coin=models.IntegerField(verbose_name="返币")
	recommend=models.BooleanField(verbose_name="推荐",default=False)
	sale=models.BooleanField(verbose_name="上架",default=False)
	freight=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="运费")
	appendtime=models.DateField(auto_now_add=True)

	class Meta:
		verbose_name='产品'
		verbose_name_plural='产品'

	def __unicode__(self):
		return self.name
#产品图像
class ProductImage(models.Model):
	product=models.ForeignKey(Product,verbose_name='产品')
	url=models.ImageField(upload_to='product',verbose_name='产品图像',blank=True)
	isdefault=models.BooleanField(verbose_name='默认',default=False)
#规格
class Standard(models.Model):
	product=models.ForeignKey(Product)
	name = models.CharField(max_length=32,verbose_name='名称')
	value = models.CharField(max_length=32,verbose_name='值')
	istitle=models.BooleanField(default=False,verbose_name='是否作为标题')
	appendtime=models.DateField(auto_now_add=True)

	class Meta:
		verbose_name='产品规格'
		verbose_name_plural='产品规格'

	def __unicode__(self):
		return self.name
#产品种类
class ProductOption(models.Model):
	product=models.ForeignKey(Product,verbose_name='产品')
	name = models.CharField(max_length=32,verbose_name='')
	avator=models.ImageField(upload_to='product/option',verbose_name='',blank=True)
	price=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="价格")
	shoptype=models.CharField(
		max_length=32,
		choices=TYPE_OPTION_ITEMS,
		default='product',
		verbose_name='交易类型'
	)
	count=models.IntegerField(verbose_name="库存")
	effective=models.BooleanField(verbose_name='是否有效',default=True)
	isdefault=models.BooleanField(verbose_name="默认",default=False)
	

	class Meta:
		verbose_name='产品种类'
		verbose_name_plural='产品种类'

	def __unicode__(self):
		return self.name

#全国省市区乡地理位置
class Provice(models.Model):	
	name=models.CharField(max_length=32,verbose_name='省名')
	class Meta:
		verbose_name='省'
		verbose_name_plural='省'

	def __unicode__(self):
		return self.name

class City(models.Model):
	name=models.CharField(max_length=32,verbose_name='市名')
	provice=models.ForeignKey(Provice)
	code=models.CharField(max_length=12,verbose_name='邮政编码',blank=True,null=True)

	class Meta:
		verbose_name='市'
		verbose_name_plural='市'

	def __unicode__(self):
		return self.name

class Region(models.Model):
	name=models.CharField(max_length=32,verbose_name='区名')
	city=models.ForeignKey(City)
	class Meta:
		verbose_name='区'
		verbose_name_plural='区'

	def __unicode__(self):
		return self.name

class Country(models.Model):
	name=models.CharField(max_length=32,verbose_name='乡')
	region=models.ForeignKey(Region)
	class Meta:
		verbose_name='乡'
		verbose_name_plural='乡'

	def __unicode__(self):
		return self.name
class Location(models.Model):
	provice=models.ForeignKey(Provice)
	city=ChainedForeignKey(
		City,
		chained_field='provice',
		chained_model_field='provice',
		show_all=False,
		auto_choose=True,
		sort=True,
		blank=True,
		null=True
	)
	region=ChainedForeignKey(
		Region,
		chained_field='city',
		chained_model_field='city',
		show_all=False,
		auto_choose=True,
		sort=True,
		blank=True,
		null=True
	)
	country=ChainedForeignKey(
		Country,
		chained_field='region',
		chained_model_field='region',
		show_all=False,
		auto_choose=True,
		sort=True,
		blank=True,
		null=True
	)
	class Meta:
		verbose_name='地理数据'
		verbose_name_plural='地理数据'

	def name(self):
		result=''
		if self.city==None:
			result=self.provice.name
		elif self.region==None:
			result='%s%s'%(self.provice,self.city)
		elif self.country==None:
			result='%s%s%s'%(self.provice,self.city,self.region)
		else:
			result='%s%s%s%s'%(self.provice,self.city,self.region,self.country)
		return result

	def __unicode__(self):
		return self.name()

#用户等级
class UserRank(models.Model):
	name=models.CharField(max_length=32,verbose_name='姓名')
	thumb=models.ImageField(upload_to='article',verbose_name='等级标志',blank=True)

	class Meta:
		verbose_name='用户等级'
		verbose_name_plural='用户等级'

	def __unicode__(self):
		return self.name
#部落
class Tribe(models.Model):
	name=models.CharField(max_length=32,verbose_name='部落名称',default='大陆')
	location=models.ForeignKey(Location,null=True,blank=True)
	body=models.TextField(verbose_name='部落详情')
	tribeType=models.CharField(
		max_length=16,
		choices=(
			('PTBL','普通部落'),
			('DLBL','位置部落'),
		),
		verbose_name='部落类型',
		default='PTBL'
	)
	class Meta:
		verbose_name='部落'
		verbose_name_plural='部落'

	appendtime=models.DateField(auto_now_add=True)

	def __unicode__(self):
		return self.name
#用户
class User(models.Model):
	name=models.CharField(max_length=32,verbose_name='姓名')
	openid=models.CharField(max_length=32,verbose_name='微信公众号OpenID')
	avator_url=models.URLField(verbose_name='公众号头像地址')
	rank=models.CharField(
		max_length=32,
		choices=USER_RANK,
		default='PT',
		verbose_name='用户等级'
	)
	tribes=models.ManyToManyField(Tribe,verbose_name='部落',blank=True,null=True)
	coinCount=models.IntegerField(verbose_name='果币',default=0)
	avator=models.ImageField(upload_to='article',verbose_name='头像',blank=True,null=True)
	mobile=models.CharField(max_length=32,verbose_name='手机号',null=True)
	password=models.CharField(max_length=32,verbose_name='密码',null=True)
	GENDER_CHOICES=(
		('f','女生'),
		('m','男生'),
	)
	gender=models.CharField(
		max_length=2,
		verbose_name="性别",
		choices=GENDER_CHOICES,
		default='m'
	)
	parent=models.ForeignKey('self',null=True,blank=True)
	appendtime=models.DateField(auto_now_add=True)

	#获取购物车
	def shopcart(self):
		shopcart,create=ShopCart.objects.get_or_create(user_id=self.id)
		return shopcart

	#获取默认地址
	def defaultAddress(self):
		addresses=self.address_set.all()
		defaultAddress=None
		try:
			defaultAddress=addresses.get(isdefault=True)
		except ObjectDoesNotExist:
			defaultAddress=addresses.first()
		return defaultAddress
	#使用果币
	def useCoinCount(self,money):
		coinMoney=Decimal(self.coinCount)/100
		if money>coinMoney:
			return self.coinCount
		else:
			return money*100

	class Meta:
		verbose_name='用户'
		verbose_name_plural='用户'

	def __unicode__(self):
 		return self.name
#活动范围ActiveRange
class ActiveRange(models.Model):
	name = models.CharField(max_length=32,verbose_name='活动范围名称')
	location=models.ForeignKey(Location,verbose_name='地理位置',null=True,blank=True)
	tribe=models.ForeignKey(Tribe,verbose_name='部落',null=True,blank=True)
	category=models.ForeignKey(Category,verbose_name='分类',null=True,blank=True)
	product=models.ForeignKey(Product,verbose_name='产品',null=True,blank=True)
	rank=models.CharField(
		max_length=32,
		choices=USER_RANK,
		default='PT',
		verbose_name='用户等级',
	)
	appendtime=models.DateField(auto_now_add=True)

	class Meta:
		verbose_name='活动范围'
		verbose_name_plural='活动范围'

	#根据身份判断活动是否有效
	def judgeByRank(self,user):
		result=False
		if self.rank=='PT':
			result=True
		elif self.rank=='HJ' and user.rank in ['HJ','BJ','ZS']:
			result=True
		elif self.rank=='BJ' and user.rank in ['BJ','ZS']:
			result=True
		elif range.rank=='ZS' and useRank=='ZS':
			result=True
		return result
	
	#根据社群判断活动范围是否有效
	def judgeByTribe(self,user):
		if self.tribe==None:
			return True
		if not user.tribes.all().exists():
			return False
		return self.tribe.name=='大陆' or self.tribe in user.tribes.all()
	
	#通过地理位置判断是否有效
	def judgeByAddress(self,address):
		if self.location is None:
			return True
		if address is None:
			return False
		if self.location==address.location:
			return True
		if self.location.name()==address.provice():
			return True
		if self.location.name()==address.proviceCity():
			return True
		if self.location.name()==address.proviceCityRegion():
			return True
		return False
	
	def __unicode__(self):
		return self.name

#活动
class Active(models.Model):
	name=models.CharField(max_length=64,verbose_name='活动名称')
	thumb=models.ImageField(upload_to='active',verbose_name='封面',blank=True,null=True)
	shoptype=models.CharField(
		max_length=32,
		choices=TYPE_OPTION_ITEMS,
		default='product',
		verbose_name='交易类型',
	)
	users=models.ManyToManyField('User',verbose_name='活动参与人',through='Activeuser')
	activerange=models.ManyToManyField('ActiveRange',verbose_name='参与范围',through='Activeship')
	description=models.CharField(max_length=32,verbose_name='简介')
	starttime=models.DateTimeField(verbose_name='开始时间')
	endtime=models.DateTimeField(verbose_name='结束时间')
	sale=models.BooleanField(verbose_name="上架",default=False)
	complete=models.IntegerField(verbose_name="完成数")
	count=models.IntegerField(verbose_name="总数")
	meanwhile=models.BooleanField(verbose_name="是否可同时参与其他活动",default=False)
	appendtime=models.DateField(auto_now_add=True)

	class Meta:
		verbose_name='活动'

	#是否有效
	def effective(self):
		return True if (self.endtime-datetime.utcnow().replace(tzinfo=utc)).days>-1 else False
	
	#判断某一用户是否满足活动范围
	def judgeByUser(self,user):
		satisfy=False
		for range in self.activerange.all():
			if range.judgeByRank(user) and range.judgeByAddress(user.defaultAddress()) and range.judgeByTribe(user):
				satisfy=True
				break
		return satisfy

	#数量是否已完成
	def countComplete(self):
		return self.complete>=self.count

	#判断某一地址是否满足活动范围要求
	def justifyAddress(self,address):
		for range in self.activerange.all():
			if range.judgeByAddress(address):
				return True
		return False

	def __unicode__(self):
 		return self.name

#新人
class Newer(Active):
	newer_price=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="新人价")
	class Meta:
		verbose_name='新手礼包'
		verbose_name_plural='新手礼包'

	def __unicode__(self):
		return self.name
#团购
class Group(Active):
	market_price=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="市场价")

	class Meta:
		verbose_name='团购活动'
		verbose_name_plural='团购活动'

	def __unicode__(self):
		return self.name
#众筹
class Crowd(Active):
	market_price=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="市场价")

	class Meta:
		verbose_name='众筹'
		verbose_name_plural='众筹'

	def __unicode__(self):
		return self.name
#加速度
class Speed(Active):
	class Meta:
		verbose_name='加速度'
		verbose_name_plural='加速度'

	def __unicode__(self):
		return self.name

#限时抢购
class Limit(Active):
	market_price=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="市场价")
	class Meta:
		verbose_name='限时抢购'
		verbose_name_plural='限时抢购'

	def __unicode__(self):
		return self.name
#优惠券
class Coupon(Active):
	Shop_Option_items=(
		('YH','满减券'),
		('YF','运费券'),
		('DJQ','代金券')
	)
	couponOption=models.CharField(
		max_length=32,
		verbose_name='优惠券类别',
		choices=Shop_Option_items
	)
	over=models.IntegerField(verbose_name="购物满多少")
	reduce=models.IntegerField(verbose_name="减多少")
	mailReduce=models.IntegerField(verbose_name="减多少邮费")

	class Meta:
		verbose_name='购物券'
		verbose_name_plural='购物券'

	def __unicode__(self):
		return self.name

class Activeship(models.Model):
    active = models.ForeignKey(Active, on_delete=models.CASCADE)
    activerange = models.ForeignKey(ActiveRange, on_delete=models.CASCADE,verbose_name='活动范围')

class Activeuser(models.Model):
	active = models.ForeignKey(Active, on_delete=models.CASCADE)
	user=models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='活动参与人')
	isparticipation=models.BooleanField(verbose_name="是否已参与",default=False)
#评论
class Commet(models.Model):
	product=models.ForeignKey('Product',verbose_name='分类')
	user=models.ForeignKey('User',verbose_name='用户')
	body= models.CharField(max_length=256,verbose_name='评论内容')
	recommend=models.BooleanField(verbose_name="是否推荐",default=False)
	appendtime=models.DateField(auto_now_add=True)

	class Meta:
		verbose_name='产品评论'
		verbose_name_plural='产品评论'

	def __unicode__(self):
		return self.body
#购物车
class ShopCart(models.Model):
	user=models.ForeignKey(User,verbose_name='用户')
	useCoin=models.BooleanField(verbose_name='使用果币',default=False)
	mycoupon=models.IntegerField(default=0,verbose_name='我的可用优惠券')
	appendtime=models.DateField(auto_now_add=True)
	#加入购物车
	def add(self,shoptype,shoptypeID,product_id,productOption_id,count):
		try:
			shopcartItem=self.items().get(productOption=productOption_id)
			shopcartItem.count=shopcartItem.count+int(count)
			shopcartItem.save()
		except ObjectDoesNotExist:
			shopcartItem=self.shopcartitem_set.create(shoptype=shoptype,shoptypeID=shoptypeID,product_id=product_id,productOption_id=productOption_id,count=count)
	
	#从购物车中删除
	def deleteItem(self,shopcartitem_id):
		return self.shopcartitem_set.filter(id=shopcartitem_id).delete()

	#更新产品数
	def changeItemCount(self,shopcartitem_id,count):
		return self.shopcartitem_set.filter(id=shopcartitem_id).update(count=count)

	#购物车总产品
	def items(self):
		return self.shopcartitem_set.all()

	#产品数
	def itemsCount(self):
		count=0
		for item in self.items():
			count=count+item.count
		return count

	#购物车已选择产品
	def checkItems(self):
		return self.shopcartitem_set.filter(check=True)

	#购物车已选择产品总数
	def checkItemsCount(self):
		count=0
		for item in self.checkItems():
			count=count+item.count
		return count

	#全选
	def selectAll(self):
		affectedRow=self.items().update(check=True)
		return True if affectedRow>0 else False
	#取消全选
	def unselectAll(self):
		affectedRow=self.items().update(check=False)
		return True if affectedRow>0 else False
	#选择购物车某一项
	def selectItem(self,shopcartitem_id):
		return self.items().filter(id=shopcartitem_id).update(check=True)
	#取消购物车某一项
	def unselectItem(self,shopcartitem_id):
		return self.items().filter(id=shopcartitem_id).update(check=False)
	#购物车是否为空
	def isEmpty(self):
		return False if self.items().count()>0 else True
	
	#是否有选择产品
	def isCheck(self):
		return True if self.checkItems().count()>0 else False

	#计算产品价格
	def getMoney(self):
		totalMoney=0
		for item in self.checkItems():
			totalMoney=totalMoney+item.getMoney()
		return totalMoney
	#获取优惠券
	def getMyCoupon(self):
		try:
			return MyCoupon.objects.get(id=self.mycoupon)
		except ObjectDoesNotExist:
			return None
	#计算运费
	def getFreight(self):
		return 0

	class Meta:
		verbose_name='购物车'
		verbose_name_plural='购物车'
#购物车项
class ShopCartItem(models.Model):
	shopcart=models.ForeignKey(ShopCart,verbose_name='购物车')
	shoptype=models.CharField(
		max_length=32,
		choices=TYPE_OPTION_ITEMS,
		default='product',
		verbose_name='交易类型',
	)
	shoptypeID=models.IntegerField(verbose_name='购物类型编码')
	product=models.ForeignKey('Product',verbose_name='产品')
	productOption=models.ForeignKey('ProductOption',verbose_name='产品规格')
	count=models.IntegerField(verbose_name="产品数")
	check=models.BooleanField(default=True)
	appendtime=models.DateField(auto_now_add=True)

	class Meta:
		verbose_name='购物车项'
		verbose_name_plural='购物车项'

	def getMoney(self):
		return self.productOption.price*self.count

	def __unicode__(self):
		return self.product.name

#果币详细
class CoinItem(models.Model):
	user=models.ForeignKey('User',verbose_name='用户')
	change=models.IntegerField(verbose_name="改变数")
	typename=models.CharField(
		max_length=32,
		choices=(
			('GWFH','购物返还'),
			('GWZC','购物支出'),
			('TGSD','推广所得')
		),
		verbose_name='获得方式'
	)
	detail = models.CharField(max_length=32,verbose_name='获得详情')
	changetime=models.DateField(auto_now_add=True)

	class Meta:
		verbose_name='果币详细'
		verbose_name_plural='果币详细'

	def __unicode__(self):
		return '%s%s'%(self.typename,self.change)

#我的优惠券
class MyCoupon(models.Model):
	user=models.ForeignKey('User',verbose_name='会员')
	coupon=models.ForeignKey('Coupon',verbose_name='优惠券')

	USEDSTATUS_ITEMS=(
		('KY','可用'),
		('BKY','不可用'),
		('ZZSY','正在使用'),
		('YGQ','已过期'),
		('YSY','已使用')	
	)
	useStatus=models.CharField(
		max_length=4,
		choices=USEDSTATUS_ITEMS,
		verbose_name='可用状态',
		default='KY'
	)
	appendtime=models.DateField(auto_now_add=True,verbose_name='获得时间')

	def effective(self):
		return coupon.effective()

	def reduceMail(self,freight):
		if self.coupon.mailReduce==0:
			return 0
		return freight if self.coupon.mailReduce>freight else self.coupon.mailReduce

	class Meta:
		verbose_name='我的优惠券'
		verbose_name_plural='我的优惠券'

	def __unicode__(self):
		return self.coupon.name
#收藏
class Collection(models.Model):
	user=models.ForeignKey('User',verbose_name='会员')
	product=models.ForeignKey('Product',verbose_name='产品')
	appendtime=models.DateField(auto_now_add=True,verbose_name='收藏时间')

	class Meta:
		verbose_name='收藏'
		verbose_name_plural='收藏'

	def __unicode__(self):
		return self.user.name
#送货地址
class Address(models.Model):
	user=models.ForeignKey('User',verbose_name='会员')
	name = models.CharField(max_length=32,verbose_name='收货人')
	mobile = models.CharField(max_length=32,verbose_name='手机号')
	location=models.ForeignKey('Location',verbose_name='地理位置')
	detail = models.CharField(max_length=32,verbose_name='详细收货地址')
	isdefault=models.BooleanField(default=False,verbose_name='是否默认')
	usable=models.BooleanField(default=True,verbose_name='是否可用')
	appendtime=models.DateField(auto_now_add=True,verbose_name='创建时间')

	class Meta:
		verbose_name='送货地址'
		verbose_name_plural='送货地址'

	def provice(self):
		return self.location.provice.name

	def proviceCity(self):
		return self.provice()+self.location.city.name

	def proviceCityRegion(self):
		return self.proviceCity()+self.location.region.name

	def __unicode__(self):
		return '%s%s'%(self.location,self.detail)

#订单
class Order(models.Model):
	orderNumber=models.CharField(max_length=128,verbose_name='订单编号')
	user=models.ForeignKey(User,verbose_name='用户')
	receive_name = models.CharField(max_length=32,verbose_name='收货人')
	mycoupon=models.ForeignKey(MyCoupon,verbose_name='使用优惠券',null=True,blank=True)
	coin=models.IntegerField(verbose_name='使用果币',default=0)
	mobile = models.CharField(max_length=32,verbose_name='联系电话')
	location=models.ForeignKey('Location',verbose_name='地理位置')
	detail = models.CharField(max_length=32,verbose_name='详细收货地址')
	totalMoney=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="订单金额")
	appendtime=models.DateField(auto_now_add=True)
	ORDER_STATUS_ITEMS=(
		('CANCEL','取消'),
		('WAITING','等待支付'),
		('PAYSUCCESS','支付成功'),
		('PACKAGE','正在出库'),
		('INDELIVERY','正在配送'),
		('COMPLETE','订单完成')
	)
	orderStatusOption = models.CharField(
		max_length=32,
		choices=ORDER_STATUS_ITEMS,
		verbose_name='订单状态'
	)
	class Meta:
		verbose_name='订单'
		verbose_name_plural='订单'

	def __unicode__(self):
		return '%s:%s%s'%(self.user.name,self.location,self.detail)
#订单详情
class OrderItem(models.Model):
	order=models.ForeignKey('Order')
	shoptype=models.CharField(
		max_length=32,
		choices=TYPE_OPTION_ITEMS,
		default='product',
		verbose_name='交易类型'
	)
	shoptypeID=models.IntegerField('交易类型单号')
	product=models.ForeignKey('Product',verbose_name='相关产品')
	productOption=models.ForeignKey('ProductOption',verbose_name='产品类型')
	product_name = models.CharField(max_length=32,verbose_name='产品名称')
	optionName = models.CharField(max_length=32,verbose_name='')
	thumb=models.ImageField(upload_to='article',verbose_name='产品缩略图',blank=True)
	price=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="成交价")
	count=models.IntegerField(verbose_name="交易数")
	appendtime=models.DateField(auto_now_add=True)

	class Meta:
		verbose_name='订单详情'
		verbose_name_plural='订单详情'

	def __unicode__(self):
		return self.product.name

#发起推广,如果发起推广,就记录,同一个产品推广只记录一次
PROMOTE_TYPE_ITEMS=(
	('POST','海报'),
	('FRIEND','好友'),
	('CIRCLE','朋友圈')
)
class Promote(models.Model):
	user=models.ForeignKey(User)
	shoptypeID=models.IntegerField()
	shoptype=models.CharField(
		max_length=32,
		choices=TYPE_OPTION_ITEMS,
		default='product',
		verbose_name='交易类型'
	)
	promoteType=models.CharField(
		max_length=32,
		choices=PROMOTE_TYPE_ITEMS,
		verbose_name='推广类型'
	)
	class Meta:
		verbose_name='推广'
		verbose_name_plural='推广'
	appendtime=models.DateField(auto_now_add=True)

	#推广记录
	def deals(self):
		return self.promotedeal_set.all()

	#增加推广
	def addDeal(self,customer):
		if customer.parent!=None:
			PromoteDeal.objects.create(self,customer)


	def __unicode__(self):
		return self.user.name

#推广成交,如果别人看到并点入就记录
class PromoteDeal(models.Model):
	promote=models.ForeignKey(Promote)
	customer=models.ForeignKey(User)
	order=models.ForeignKey(Order,null=True)
	dealtime=models.DateField(auto_now_add=True)

	#将新得到的客户记录为TA的子客户
	def getCustomer(self):
		if customer.parent==None:
			customer.parent=self.promote.user

	class Meta:
		verbose_name='推广成交'
		verbose_name_plural='推广成交'

	def __unicode__(self):
		return self.user.name
