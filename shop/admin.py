#coding:utf-8
from django.contrib import admin
from .models import Active,Newer,Group,Limit,Coupon,Speed,Crowd,Activeship,Activeuser
from .models import Country,Location,ActiveRange,Tribe
from .models import User,CoinItem,MyCoupon,Collection,Address,UserRank
from .models import Category,Product,ProductOption,ProductImage,Commet,Standard,ShopCart,ShopCartItem,Order,OrderItem
from .models import Promote,PromoteDeal
from .models import Page,Cell,Slider

class ActiveshipInline(admin.TabularInline):
    model = Activeship
    extra = 1
class ActiveuserInline(admin.TabularInline):
    model = Activeuser
    extra = 1


#活动标志
class ActiveRangeAdmin(admin.ModelAdmin):
    inlines = (ActiveshipInline,)
#活动
class ActiveAdmin(admin.ModelAdmin):
	inlines = (ActiveshipInline,ActiveuserInline)
class GroupAdmin(admin.ModelAdmin):
	inlines = (ActiveshipInline,ActiveuserInline)
class LimitAdmin(admin.ModelAdmin):
	inlines = (ActiveshipInline,ActiveuserInline)
class CouponAdmin(admin.ModelAdmin):
	inlines = (ActiveshipInline,ActiveuserInline)
class SpeedAdmin(admin.ModelAdmin):
	inlines = (ActiveshipInline,ActiveuserInline)
class CrowdAdmin(admin.ModelAdmin):
	inlines = (ActiveshipInline,ActiveuserInline)
class NewerAdmin(admin.ModelAdmin):
	inlines = (ActiveshipInline,ActiveuserInline)

admin.site.register(Active,ActiveAdmin)
admin.site.register(Coupon,CouponAdmin)
admin.site.register(Limit,CouponAdmin)	
admin.site.register(Group,GroupAdmin)	
admin.site.register(Newer,NewerAdmin)
admin.site.register(Speed,SpeedAdmin)
admin.site.register(Crowd,CrowdAdmin)
admin.site.register(Location)
admin.site.register(ActiveRange,ActiveRangeAdmin)


#我的优惠券
class MyCouponInline(admin.TabularInline):
	model=MyCoupon
#收藏
class CollectionInline(admin.TabularInline):
	model=Collection
#送货地址
class AddressInline(admin.TabularInline):
	model=Address
#购物车项
class ShopCartItemInline(admin.TabularInline):
	model=ShopCartItem
#果币
class CoinItemInline(admin.TabularInline):
	model=CoinItem
#购物车	
class ShopCartAdmin(admin.ModelAdmin):
	inlines=[ShopCartItemInline]
admin.site.register(ShopCart,ShopCartAdmin)

#用户
class UserAdmin(admin.ModelAdmin):
	inlines=[
		AddressInline,
		CoinItemInline,
		MyCouponInline,
		CollectionInline,	
	]
	list_display=('name','appendtime')
admin.site.register(User,UserAdmin)

#部落
class TribeAdmin(admin.ModelAdmin):
	list_display=('name','appendtime')
#等级
class UserRankAdmin(admin.ModelAdmin):
	pass
admin.site.register(Tribe,TribeAdmin)
admin.site.register(UserRank,UserRankAdmin)

#产品目录
class CategoryAdmin(admin.ModelAdmin):
	pass
admin.site.register(Category,CategoryAdmin)

#产品选项
class ProductOptionInline(admin.TabularInline):
	model=ProductOption
#产品图像
class ProductImageInline(admin.TabularInline):
	model=ProductImage

#规格
class StandardInline(admin.TabularInline):
	model=Standard

#评论
class CommetInline(admin.TabularInline):
	model=Commet

class ProductAdmin(admin.ModelAdmin):
	inlines=[
		StandardInline,
		ProductImageInline,
		ProductOptionInline,
		CommetInline
	]
admin.site.register(Product,ProductAdmin)

#订单
class OrderItemInline(admin.TabularInline):
	model=OrderItem
class OrderAdmin(admin.ModelAdmin):
	inlines=[
		OrderItemInline
	]
admin.site.register(Order,OrderAdmin)

#推广
class PromoteDealInline(admin.TabularInline):
	model=PromoteDeal
class PromoteAdmin(admin.ModelAdmin):
	inlines=[
		PromoteDealInline,
	]
admin.site.register(Promote,PromoteAdmin)

class CellInline(admin.TabularInline):
	model=Cell
class PageAdmin(admin.ModelAdmin):
	inlines=[CellInline]
	list_display=('title','type','showTitle','orderby')

admin.site.register(Page,PageAdmin)

admin.site.register(Slider)






