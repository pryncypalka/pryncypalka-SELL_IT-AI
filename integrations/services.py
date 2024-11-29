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
        response = requests.get(url, headers=headers)
        
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
        response = requests.get(f"{self.base_url}/sale/offers", headers=headers, params=params)
        return response.json()
    
    def get_offer_events(self, params=None):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.allegro.public.v1+json'
        }
        response = requests.get(
            f"{self.base_url}/sale/offer-events",
            headers=headers,
            params=params
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
            f"{self.base_url}/sale/categories/{category_id}/parameters",
            headers=self._get_headers()
        )
        return response.json()