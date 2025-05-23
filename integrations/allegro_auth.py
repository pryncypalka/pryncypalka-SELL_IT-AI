import base64
import hashlib
import secrets
import string
from urllib.parse import urlencode
import requests
from typing import Optional, Tuple, Dict

class AllegroAuth:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, sandbox: bool = True):
        """
        Initialize Allegro OAuth handler
        
        Args:
            client_id: Allegro application client ID
            client_secret: Allegro application client secret
            redirect_uri: Application redirect URI for OAuth flow
            sandbox: Whether to use sandbox environment (default: True)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        # Set proper URLs based on environment
        base_domain = "allegro.pl.allegrosandbox.pl" if sandbox else "allegro.pl"
        self.auth_url = f"https://{base_domain}/auth/oauth/authorize"
        self.token_url = f"https://{base_domain}/auth/oauth/token"
        self.api_url = f"https://api.{base_domain}"
        
        # Store PKCE verifier during auth flow
        self._code_verifier = None

    def generate_code_verifier(self, length: int = 100) -> str:
        """Generate a secure random string for PKCE code_verifier"""
        allowed_chars = string.ascii_letters + string.digits
        code_verifier = ''.join(secrets.choice(allowed_chars) for _ in range(length))
        self._code_verifier = code_verifier
        return code_verifier

    def generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge from verifier using S256 method"""
        m = hashlib.sha256()
        m.update(code_verifier.encode('ascii'))
        code_challenge = base64.urlsafe_b64encode(m.digest()).decode('ascii')
        return code_challenge.rstrip('=')

    def get_authorization_url(self) -> Tuple[str, str]:
        """
        Generate authorization URL for OAuth flow with PKCE
        
        Returns:
            Tuple containing (authorization_url, code_verifier)
        """
        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'code_challenge_method': 'S256',
            'code_challenge': code_challenge
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        return auth_url, code_verifier

    
    def get_access_token(self, auth_code: str, code_verifier: str) -> Dict:
        """
        Get access token using authorization code and PKCE verifier
        """
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'code_verifier': code_verifier
        }
        
        auth = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(
                self.token_url,
                data=data,
                headers=headers, 
                timeout=10,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Token exchange error: {str(e)}")  # Debug log
            raise Exception(f"Authorization error: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> Dict:
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        auth = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            # Zwiększony timeout i dodane retries
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=3)
            session.mount('https://', adapter)
            
            response = session.post(
                self.token_url,
                data=data, 
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Refresh error details: {str(e)}")  # Debug log
            raise

    def make_request(self, endpoint: str, method: str = 'GET', 
                    access_token: Optional[str] = None, **kwargs) -> requests.Response:
        """
        Make authenticated request to Allegro API
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            access_token: Access token for authentication
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Response from API
        """
        url = f"{self.api_url}{endpoint}"
        
        headers = kwargs.pop('headers', {})
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
            headers['Accept'] = 'application/vnd.allegro.public.v1+json'
            
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response
    