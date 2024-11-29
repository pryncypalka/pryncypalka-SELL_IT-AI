from django.db import models
from django.utils import timezone
from django.conf import settings
from .allegro_auth import AllegroAuth
from django.db.models import JSONField

def get_allegro_client():
    return AllegroAuth(
        client_id=settings.ALLEGRO_CLIENT_ID,
        client_secret=settings.ALLEGRO_CLIENT_SECRET,
        redirect_uri=settings.ALLEGRO_REDIRECT_URI,
        sandbox=settings.ALLEGRO_SANDBOX
    )
    
class AllegroToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='allegro_token')
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def refresh_if_needed(self):
        try:
            allegro = get_allegro_client()
            token_data = allegro.refresh_access_token(self.refresh_token)
            
            self.access_token = token_data['access_token'] 
            self.refresh_token = token_data['refresh_token']
            self.expires_at = timezone.now() + timezone.timedelta(seconds=token_data['expires_in'])
            self.save()
            return True
        except Exception as e:
            print(f"Refresh failed: {str(e)}")
            return False
      

    def is_valid(self):
        try:
            if self.refresh_if_needed():
                allegro = get_allegro_client()
                allegro.make_request('/me', access_token=self.access_token)
                return True
            return False
        except Exception:
            return False
        
        
class Category(models.Model):
    allegro_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    parameters = JSONField(default=dict)

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    parameters = JSONField(default=dict)
    ai_generated_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    order = models.IntegerField(default=0)

class Listing(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('error', 'Error'),
    ]
    
    product = models.ForeignKey(Product, related_name='listings', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    allegro_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    parameters = JSONField(default=dict)
    last_sync = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ListingAnalytics(models.Model):
    listing = models.ForeignKey(Listing, related_name='analytics', on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    watches = models.IntegerField(default=0)
    sales = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class AllegroOffer(models.Model):
    UNIT_CHOICES = [('UNIT', 'Units')]
    FORMAT_CHOICES = [
        ('BUY_NOW', 'Buy Now'),
        ('AUCTION', 'Auction'),
        ('ADVERTISEMENT', 'Advertisement')
    ]
    STATUS_CHOICES = [
        ('INACTIVE', 'Inactive'),
        ('ACTIVE', 'Active'),
        ('ENDED', 'Ended')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    external_id = models.CharField(max_length=100, blank=True, null=True)
    category_id = models.CharField(max_length=255)
    
    # Product data
    product_id = models.CharField(max_length=255, blank=True, null=True)
    product_id_type = models.CharField(max_length=20, blank=True, null=True)
    parameters = JSONField(default=dict)
    images = JSONField(default=list)
    
    # Business settings
    b2b_buyable_only = models.BooleanField(default=False)
    
    # Stock
    available_stock = models.IntegerField()
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='UNIT')
    
    # Selling mode
    selling_format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    minimal_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Delivery
    handling_time = models.CharField(max_length=20, default='PT24H')
    shipping_rates_id = models.CharField(max_length=255, null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)
    shipment_date = models.DateTimeField(null=True, blank=True)
    
    # Publication
    publication_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    publication_started_at = models.DateTimeField(null=True, blank=True)
    publication_ending_at = models.DateTimeField(null=True, blank=True)
    
    # Location
    location_city = models.CharField(max_length=255)
    location_country_code = models.CharField(max_length=2, default='PL')
    location_post_code = models.CharField(max_length=10)
    location_province = models.CharField(max_length=255)
    
    # Additional data
    language = models.CharField(max_length=5, default='pl-PL')
    tax_settings = JSONField(default=dict)
    after_sales_services = JSONField(default=dict)
    additional_marketplaces = JSONField(default=dict)
    contact = JSONField(default=dict, null=True)
    compatibility_list = JSONField(default=dict, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.publication_status})"

    class Meta:
        ordering = ['-created_at']