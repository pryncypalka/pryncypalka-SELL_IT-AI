from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from simple_history import register
from django.contrib.auth.models import User
from .models import *

register(User)

admin.site.register(AllegroToken)
admin.site.register(OpenAIRequest)
admin.site.register(AdminOpenAIConfig)
admin.site.register(OpenAIInstruction)




@admin.register(Category)
class CategoryAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'allegro_id', 'parent')


@admin.register(Product)
class ProductAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'category', 'base_price', 'stock', "user")


@admin.register(ProductImage)
class ProductImageAdmin(SimpleHistoryAdmin):
    list_display = ('product', 'order', 'image')


@admin.register(AllegroOffer)
class AllegroOfferAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'category_id', 'selling_format', 'price', 'publication_status')


@admin.register(AllegroOrder)
class AllegroOrderAdmin(SimpleHistoryAdmin):
    list_display = ('allegro_order_id', 'buyer_login', 'status', 'total_price', 'created_at')


@admin.register(AllegroDefaultSettings)
class AllegroDefaultSettingsAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'default_category', 'handling_time')


