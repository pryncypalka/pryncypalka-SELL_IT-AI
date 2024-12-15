from django.contrib import admin
from .models import *
# from simple_history import register
# from django.contrib.auth.models import User

# # register(User)

admin.site.register(AllegroToken)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(AllegroOffer)
admin.site.register(AllegroOrder)
admin.site.register(AllegroDefaultSettings)
admin.site.register(OpenAIRequest)
admin.site.register(AdminOpenAIConfig)
admin.site.register(OpenAIInstruction)
