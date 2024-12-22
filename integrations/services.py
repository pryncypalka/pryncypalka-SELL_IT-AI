import requests
from django.http import Http404
from django.conf import settings

class AllegroOfferService:
    def __init__(self, user):
        self.user = user
        if not hasattr(user, 'allegro_token'):
            raise Exception("User not connected to Allegro")
        self.token = user.allegro_token.access_token
        self.base_url = settings.ALLEGRO_API_URL
        
    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.allegro.public.v1+json',
            'Content-Type': 'application/vnd.allegro.public.v1+json'
        }

    def get_offer(self, offer_id: str) -> dict:
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.allegro.public.v1+json'
        }
        
        offer_id = offer_id.lstrip('/')
        
        url = f"{self.base_url}/sale/product-offers/{offer_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            raise Http404("Offer not found")
        response.raise_for_status()
        return response.json()
    
    def get_offers(self, filters=None):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.allegro.public.v1+json'
        }
        params = filters or {}
        response = requests.get(f"{self.base_url}/sale/offers", headers=headers, params=params, timeout=10)
        return response.json()
    
    def get_offer_events(self, params=None):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.allegro.public.v1+json'
        }
        response = requests.get(
            f"{self.base_url}/sale/offer-events",
            headers=headers,
            params=params,
            timeout=10
        )
        return response.json()

    def create_offer(self, data: dict) -> dict:
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.allegro.public.v1+json',
            'Content-Type': 'application/vnd.allegro.public.v1+json'
        }
        response = requests.post(
            f"{self.base_url}/sale/product-offers",
            headers=headers,
            json=data
        )
        if response.status_code in [201, 202]:
            return response.json()
        response.raise_for_status()
        
    def edit_offer(self, offer_id: str, offer_data: dict) -> dict:
        """
        Edits an existing offer.
        
        Args:
            offer_id (str): ID of offer to edit
            offer_data (dict): Updated offer data including fields to modify:
                - productSet: Product details
                - parameters: Offer parameters
                - description: Offer description
                - images: Offer images
                - price: Price information
                - quantity: Stock quantity
                etc.
                
        Returns:
            dict: Edited offer data or status for async processing

        Raises:
            HTTPError: For validation/authorization errors
        """
        response = requests.patch(
            f"{self.base_url}/sale/product-offers/{offer_id}",
            headers=self._get_headers(),
            json=offer_data
        )
        
        if response.status_code in [200, 202]:
            return response.json()
            
        response.raise_for_status()
        
    def check_operation_status(self, offer_id: str, operation_id: str) -> dict:
        """
        Checks status of async offer operations (POST/PATCH).
        
        Args:
            offer_id (str): Offer ID
            operation_id (str): Operation ID from Location header
            
        Returns:
            dict: Operation status containing:
                - offer: Offer details
                - operation: Status info (IN_PROGRESS etc.)
                
        Notes:
            - Returns 202 if still processing
            - Returns 303 with Location header when complete
        """
        response = requests.get(
            f"{self.base_url}/sale/product-offers/{offer_id}/operations/{operation_id}",
            headers=self._get_headers(), 
            allow_redirects=False,
            timeout=10
        )
        
        if response.status_code == 303:
            # Operation complete - return location
            return {'location': response.headers['Location']}
            
        response.raise_for_status()
        return response.json()
        
    def delete_draft_offer(self, offer_id: str):
        """
        Deletes a draft offer.
        
        Args:
            offer_id (str): Offer ID to delete
        """
        response = requests.delete(
            f"{self.base_url}/sale/offers/{offer_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()

    def modify_buy_now_price(self, offer_id: str, command_id: str, price: float, currency: str = 'PLN') -> dict:
        """
        Modifies Buy Now price for an offer.
        
        Args:
            offer_id (str): Offer ID
            command_id (str): Unique UUID for command
            price (float): New price amount
            currency (str): Currency code, default PLN
            
        Returns:
            dict: Command status response
        """
        payload = {
            "id": command_id,
            "input": {
                "buyNowPrice": {
                    "amount": str(price),
                    "currency": currency
                }
            }
        }
        response = requests.put(
            f"{self.base_url}/offers/{offer_id}/change-price-commands/{command_id}",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_publication_command_status(self, command_id: str) -> dict:
        """
        Gets offer publication command summary.
        Limited to 270k offer changes per minute.
        
        Args:
            command_id (str): Command ID
            
        Returns:
            dict: Command status summary with success/failure counts
        """
        response = requests.get(
            f"{self.base_url}/sale/offer-publication-commands/{command_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
                
                
        
    def get_categories(self, parent_id=None):
        params = {'parent.id': parent_id} if parent_id else {}
        response = requests.get(
            f"{self.base_url}/sale/categories",
            headers=self._get_headers(),
            params=params
        )
        return response.json()

    def get_category_parameters(self, category_id):
        response = requests.get(
            f"{self.base_url}/sale/categories/{category_id}/product-parameters",
            headers=self._get_headers()
        )
        return response.json()
    
    def get_category(self, category_id):
        response = requests.get(
            f"{self.base_url}/sale/categories/{category_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_matching_categories(self, name: str):
        response = requests.get(
            f"{self.base_url}/sale/matching-categories",
            headers=self._get_headers(),
            params={'name': name}
        )
        response.raise_for_status()
        return response.json()
    
    def upload_image(self, image_url=None, image_data=None):
        upload_url = settings.ALLEGRO_UPLOAD_URL + '/sale/images'
        headers = self._get_headers()
        
        if image_url:
            response = requests.post(
                upload_url,
                headers=headers,
                json={'url': image_url}
            )
        elif image_data:
            headers['Content-Type'] = 'image/jpeg'  # lub inny odpowiedni typ
            response = requests.post(
                upload_url,
                headers=headers,
                data=image_data
            )
            
        response.raise_for_status()
        return response.json()

    def upload_multiple_images(self, image_urls=None, image_files=None):
        uploaded_images = []
        
        if image_urls:
            for url in image_urls:
                result = self.upload_image(image_url=url)
                uploaded_images.append(result['location'])
                
        if image_files:
            for image in image_files:
                result = self.upload_image(image_data=image.read())
                uploaded_images.append(result['location'])
                
        return uploaded_images
    
    # need to create new product in Allegro
    def get_product_parameters(self, category_id):
        response = requests.get(
            f"{self.base_url}/sale/categories/{category_id}/product-parameters",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # Use this resource to get a list of products according to provided parameters. At least ean or phrase parameter is required.
    def search_products(self, phrase=None, mode=None, category_id=None, language='pl-PL', filters=None):
        params = {
            'language': language
        }
        
        if phrase:
            params['phrase'] = phrase
        if mode:
            params['mode'] = mode
        if category_id:
            params['category_id'] = category_id
        if filters:
            params.update(filters)
            
        response = requests.get(
            f"{self.base_url}/sale/products",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    
    def get_product_details(self, product_id, category_id=None, language='pl-PL', include_drafts=False):
        """
        Pobiera szczegółowe dane produktu.
        
        Args:
            product_id (str): ID produktu
            category_id (str, optional): ID kategorii podobnej
            language (str): Język danych (pl-PL, cs-CZ, en-US, uk-UA)
            include_drafts (bool): Czy uwzględniać produkty w stanie roboczym
        """
        params = {
            'language': language,
            'includeDrafts': include_drafts
        }
        if category_id:
            params['category_id'] = category_id
            
        response = requests.get(
            f"{self.base_url}/sale/products/{product_id}",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_automatic_pricing_rules(self):
        """
        Gets automatic pricing rules for offers.
        Returns rules with default property indicating if they were created by Allegro.
        Rate limited to 5 requests per second.
        
        Returns:
            dict: List of pricing rules containing:
                - id: Rule identifier
                - type: Type of rule (e.g. FOLLOW_BY_ALLEGRO_MIN_PRICE)
                - name: Rule name
                - default: If true, rule was created by Allegro
                - configuration: Rule configuration including pricing adjustments
                - updatedAt: Last update timestamp
        """
        response = requests.get(
            f"{self.base_url}/sale/price-automation/rules",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
            
    def create_automatic_pricing_rule(self, name: str, rule_type: str, configuration: dict) -> dict:
        """
        Creates automatic pricing rule for offers.
        Rate limited to 5 requests per second.
        
        Args:
            name (str): Rule name (max 33 chars)
            rule_type (str): Type of rule:
                - EXCHANGE_RATE: Uses exchange rates for additional marketplaces
                - FOLLOW_BY_ALLEGRO_MIN_PRICE: Follows lowest price on Allegro
                - FOLLOW_BY_MARKET_MIN_PRICE: Follows lowest market price
            configuration (dict): Rule configuration for pricing calculations
        
        Returns:
            dict: Created rule details including id, type, name, status and configuration
            
        Raises:
            HTTPError: If rule with same name exists (409) or other errors
        """
        payload = {
            "name": name,
            "type": rule_type,
            "configuration": configuration
        }
        
        response = requests.post(
            f"{self.base_url}/sale/price-automation/rules",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_pricing_rule(self, rule_id: str) -> dict:
        """
        Gets automatic pricing rule by ID.
        Rate limited to 5 requests per second.
        
        Args:
            rule_id (str): ID of the pricing rule
            
        Returns:
            dict: Rule details including type, name, configuration and status
        """
        response = requests.get(
            f"{self.base_url}/sale/price-automation/rules/{rule_id}", 
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def update_pricing_rule(self, rule_id: str, name: str, configuration: dict) -> dict:
        """
        Updates existing automatic pricing rule.
        Rate limited to 5 requests per second.
        
        Args:
            rule_id (str): ID of rule to update
            name (str): New rule name (max 33 chars)
            configuration (dict): New rule configuration
            
        Returns:
            dict: Updated rule details
        """
        payload = {
            "name": name,
            "configuration": configuration
        }
        response = requests.put(
            f"{self.base_url}/sale/price-automation/rules/{rule_id}",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status() 
        return response.json()

    def delete_pricing_rule(self, rule_id: str):
        """
        Deletes automatic pricing rule.
        Rate limited to 5 requests per second.
        
        Args:
            rule_id (str): ID of rule to delete
        """
        response = requests.delete(
            f"{self.base_url}/sale/price-automation/rules/{rule_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()

    def get_offer_pricing_rules(self, offer_id: str) -> dict:
        """
        Gets pricing rules assigned to specific offer.
        Rate limited to 5 requests per second.
        
        Args:
            offer_id (str): ID of the offer
            
        Returns:
            dict: List of pricing rules assigned to offer with marketplace details
        """
        response = requests.get(
            f"{self.base_url}/sale/price-automation/offers/{offer_id}/rules",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_tax_settings(self, category_id: str, country_codes: list = None) -> dict:
        """
        Gets tax settings for category.
        
        Args:
            category_id (str): Category ID to get tax settings for
            country_codes (list): Optional list of country codes (PL, CZ, SK, HU)
            
        Returns:
            dict: Tax settings including rates, subjects, exemptions
        """
        params = {'category_id': category_id}
        if country_codes:
            params['countryCode'] = country_codes
            
        response = requests.get(
            f"{self.base_url}/sale/tax-settings",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_offer_rating(self, offer_id: str) -> dict:
        """
        Gets rating details for an offer.
        
        Args:
            offer_id (str): Offer ID
            
        Returns:
            dict: Rating details including score distribution and size feedback
        """
        response = requests.get(
            f"{self.base_url}/sale/offers/{offer_id}/rating",
            headers=self._get_headers(),
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def calculate_offer_fee(self, offer_data: dict, marketplace_id: str = None) -> dict:
        """
        Calculates fees and commission for an offer.
        Limited to 25 requests/second per user.
        
        Args:
            offer_data (dict): Offer details including price, category etc
            marketplace_id (str): Optional marketplace ID for preview
            
        Returns:
            dict: Fee calculation results
        """
        payload = {
            "offer": offer_data, 
            "marketplaceId": marketplace_id
        }
        response = requests.post(
            f"{self.base_url}/pricing/offer-fee-preview",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_order_events(self, from_id=None, event_types=None, limit=100):
        """
        Gets order events (purchases, checkouts, payments etc).
        
        Args:
            from_id (str): Event ID to get subsequent events from
            event_types (list): Filter events by type (BOUGHT, FILLED_IN etc)
            limit (int): Max events to return (1-1000)
        
        Returns:
            dict: Order events data
        """
        params = {'limit': limit}
        if from_id:
            params['from'] = from_id
        if event_types:
            params['type'] = event_types
            
        response = requests.get(
            f"{self.base_url}/order/events",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_order_details(self, order_id: str) -> dict:
        """
        Gets detailed information about an order.
        
        Args:
            order_id (str): UUID of the order/checkout form
            
        Returns:
            dict: Complete order details including:
                - Buyer info
                - Payment details  
                - Delivery info
                - Line items
                - Invoice requirements
                - Summary and status
        """
        response = requests.get(
            f"{self.base_url}/order/checkout-forms/{order_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_warranties(self, limit=60, offset=0) -> dict:
        """Gets seller's warranties."""
        params = {'limit': limit, 'offset': offset}
        response = requests.get(
            f"{self.base_url}/after-sales-service-conditions/warranties",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()
            
    def get_return_policies(self, limit=60, offset=0) -> dict:
        """
        Gets seller's return policies.
        
        Args:
            limit (int): Results per page (1-60)
            offset (int): Page offset (0-59)
        Returns:
            dict: List of return policies with IDs and names
        """
        params = {'limit': limit, 'offset': offset}
        response = requests.get(
            f"{self.base_url}/after-sales-service-conditions/return-policies",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_implied_warranties(self, limit=60, offset=0) -> dict:
        """
        Gets seller's implied warranties.
        
        Args:
            limit (int): Results per page (1-60)
            offset (int): Page offset (0-59) 
        Returns:
            dict: List of warranties with IDs and names
        """
        params = {'limit': limit, 'offset': offset}
        response = requests.get(
            f"{self.base_url}/after-sales-service-conditions/implied-warranties", 
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_shipping_rates(self, marketplace=None) -> dict:
        """
        Gets seller's shipping rates.
        
        Args:
            marketplace (str): Filter by marketplace (e.g. 'allegro-cz')
        Returns:
            dict: List of shipping rates with IDs, names and marketplaces
        """
        params = {}
        if marketplace:
            params['marketplace'] = marketplace
            
        response = requests.get(
            f"{self.base_url}/sale/shipping-rates",
            headers=self._get_headers(),
            params=params 
        )
        response.raise_for_status()
        return response.json()
    
    
    def get_sender_details(self, shipment_id: str) -> dict:
        """
        Gets shipment details including sender address.
        """
        response = requests.get(
            f"{self.base_url}/shipment-management/shipments/{shipment_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        data = response.json()
        print(data)
        return data.get('sender', {})

        
    def get_checkout_forms(self, status=None, fulfillment_status=None, limit=100, offset=0) -> dict:
        """
        Gets list of orders.
        
        Args:
            status (list): Filter by order status (BOUGHT, FILLED_IN etc)
            fulfillment_status (list): Filter by fulfillment status
            limit (int): Results per page (1-100)
            offset (int): Page offset
        Returns:
            dict: List of orders with details
        """
        params = {
            'limit': limit,
            'offset': offset
        }
        if status:
            params['status'] = status
        if fulfillment_status:
            params['fulfillment.status'] = fulfillment_status
            
        response = requests.get(
            f"{self.base_url}/order/checkout-forms",
            headers=self._get_headers(),
            params=params
        )
        response.raise_for_status()
        return response.json()         