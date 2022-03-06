from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register((Category,Recommendation))





class BookAdmin(admin.ModelAdmin):
       
    list_display = ('category','name','rating','price',"pre_discount_price",'stock',"on_offer")
    list_editable = ('name','price',"pre_discount_price",'stock',"on_offer")
    search_fields = ('name',)
    list_per_page = 20
    list_filter = ('category',"on_offer")

admin.site.register(Book,BookAdmin)




def make_ordered(modeladmin, request, queryset):
    queryset.update(status='Ordered')
    
def make_shipped(modeladmin, request, queryset):
    queryset.update(status='Shipped')
    

def make_out_for_delivery(modeladmin, request, queryset):
    queryset.update(status='Out for delivery')

def make_delivered(modeladmin, request, queryset):
    queryset.update(status='Delivered')
    

class OrderAdmin(admin.ModelAdmin):
       
    list_display = ('user','book','quantity',"timestamp",'status')
    list_editable = ('status',)
    list_per_page = 20
    list_filter = ('status',)
    actions = [make_ordered,make_shipped,make_out_for_delivery,make_delivered]

admin.site.register(Order,OrderAdmin)




class CartAdmin(admin.ModelAdmin):
       
    list_display = ('user','book','quantity',"timestamp")
    list_per_page = 20

admin.site.register(Cart,CartAdmin)



class FeedbackAdmin(admin.ModelAdmin):
       
    list_display = ('user','book','rating',"timestamp")
    list_per_page = 20
    list_filter = ('rating',)

admin.site.register(Feedback,FeedbackAdmin)









