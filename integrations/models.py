from django.db import models
from django.utils import timezone
from django.conf import settings
from .allegro_auth import AllegroAuth
from django.db.models import JSONField
from simple_history.models import HistoricalRecords

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
    # history = HistoricalRecords()

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    parameters = JSONField(default=dict)
    ai_generated_description = models.TextField(null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField(default=0)  # Aktualny stan magazynowy
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # history = HistoricalRecords()

    def update_allegro_offers(self):
        """Aktualizuje wszystkie oferty na Allegro dla tego produktu"""
        for offer in self.allegro_offers.all():
            offer.available_stock = self.stock
            if self.stock <= 0:
                offer.publication_status = 'INACTIVE'
            elif offer.publication_status == 'INACTIVE' and self.stock > 0:
                offer.publication_status = 'ACTIVE'
            offer.save()

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    order = models.IntegerField(default=0)
    # history = HistoricalRecords()
    
    
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
    product = models.ForeignKey('Product', related_name='allegro_offers', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    external_offer_id = models.CharField(max_length=100, blank=True, null=True) 
    category_id = models.CharField(max_length=255)
    
    # Product data
    allegro_product_id = models.CharField(max_length=255, blank=True, null=True)  
    allegro_product_id_type = models.CharField(max_length=20, blank=True, null=True)
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
    currency = models.CharField(max_length=3, default='PLN') 
    
    # Delivery
    handling_time = models.CharField(max_length=20, default='PT24H')
    shipping_rates_id = models.CharField(max_length=255, null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)
    shipment_date = models.DateTimeField(null=True, blank=True)
    
    # Location
    city = models.CharField(max_length=255, null=True, blank=True)  
    country_code = models.CharField(max_length=2, default='PL') 
    post_code = models.CharField(max_length=10, null=True, blank=True) 
    province = models.CharField(max_length=255, null=True, blank=True)  
    
    # Publication
    publication_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    publication_duration = models.CharField(max_length=20, null=True, blank=True) 
    publication_started_at = models.DateTimeField(null=True, blank=True)
    publication_ending_at = models.DateTimeField(null=True, blank=True)
    republish = models.BooleanField(default=False)  
    
    # Additional data
    language = models.CharField(max_length=5, default='pl-PL')
    tax_settings = JSONField(default=dict)
    after_sales_services = JSONField(default=dict)
    additional_marketplaces = JSONField(default=dict)
    contact = JSONField(default=dict, null=True)
    compatibility_list = JSONField(default=dict, null=True)
    discounts = JSONField(default=dict, null=True)  
    message_to_seller_settings = JSONField(default=dict, null=True)  
    external = JSONField(default=dict, null=True)  
    payments = JSONField(default=dict, null=True)  
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    watches = models.IntegerField(default=0)
    sales = models.IntegerField(default=0)
    # history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} ({self.publication_status})"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'external_offer_id']

    def sync_with_product(self):
        """Synchronizuje ofertę ze stanem magazynowym produktu"""
        if self.product:
            self.available_stock = self.product.stock
            if self.product.stock <= 0:
                self.publication_status = 'INACTIVE'
            self.save()
            
class AllegroDefaultSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Shipping
    shipping_rates = models.CharField(max_length=255, null=True, blank=True)
    handling_time = models.CharField(max_length=20, default='PT24H')
    
    # Payment & Returns
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    return_policy = models.CharField(max_length=255, null=True, blank=True)
    warranty_policy = models.CharField(max_length=255, null=True, blank=True)
    implied_warranty = models.CharField(max_length=255, null=True, blank=True)
    
    # Defaults
    default_category = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Allegro Default Settings"
        verbose_name_plural = "Allegro Default Settings"
       
       
class AllegroOrder(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('READY_FOR_PROCESSING', 'Ready for processing'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    allegro_order_id = models.CharField(max_length=255, unique=True) 

    offer = models.ForeignKey(AllegroOffer, on_delete=models.SET_NULL, null=True)
    
    # Podstawowe dane kupującego
    buyer_login = models.CharField(max_length=255)
    buyer_email = models.CharField(max_length=255, null=True)
    buyer_name = models.CharField(max_length=255, null=True)  # Imię i nazwisko lub nazwa firmy
    
    # Podstawowe dane zamówienia
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='PLN')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    
    # Dane dostawy
    delivery_method = models.CharField(max_length=255, null=True)
    delivery_address = JSONField(default=dict)  
    
    # Dodatkowe informacje
    message_from_buyer = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True)
    payment_status = models.CharField(max_length=50, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    allegro_created_at = models.DateTimeField(null=True) 
    # history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Order {self.allegro_order_id} - {self.buyer_login}"
    

class OpenAIRequest(models.Model):
    """Model przechowujący historię zapytań do OpenAI"""
    OFFER_MODEL_CHOICES = [
        ("gpt-4", "GPT-4"),
        ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
    ]
    
    offer = models.ForeignKey(
        'AllegroOffer', 
        on_delete=models.CASCADE,
        null=True,  
        blank=True  
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    model = models.CharField(
        max_length=50, 
        choices=OFFER_MODEL_CHOICES, 
        default="gpt-3.5-turbo"
    )
    prompt = models.TextField()
    result = models.TextField(
        blank=True, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OpenAI Request by {self.user.username}"


class OpenAIInstruction(models.Model):
    """Model przechowujący instrukcje generowania opisów ofert"""
    
    LENGTH_CHOICES = [
        ("short", "Krótki opis"),
        ("medium", "Średni opis"),
        ("long", "Długi opis"),
    ]
    preferred_length = models.CharField(
        max_length=10,
        choices=LENGTH_CHOICES,
        default="medium"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    instruction = models.TextField()
    default_model = models.CharField(
        max_length=50,
        choices=OpenAIRequest.OFFER_MODEL_CHOICES,
        default="gpt-3.5-turbo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Instruction: {self.title} by {self.user.username}"
    
class AdminOpenAIConfig(models.Model):
    """Model przechowujący globalne ustawienia OpenAI, zarządzany przez administratora"""
 
    temperature = models.FloatField(
        default=0.7
    )
    max_tokens = models.IntegerField(
        default=500
    )
    default_instruction = models.TextField(
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Admin OpenAI Config"