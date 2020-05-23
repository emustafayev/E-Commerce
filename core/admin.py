from django.contrib import admin

from .models import Item, OrderItem, Order, Payment, Coupon, Address



class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'shipping_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered']
    search_fields = [
        'user__username',
    ]


admin.site.register(Item)	
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Address)