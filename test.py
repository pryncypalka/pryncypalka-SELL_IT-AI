
import requests
import json
from dotenv import load_dotenv
load_dotenv()
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CLIENT_ID = os.getenv("ALLEGRO_CLIENT_ID", None)
CLIENT_SECRET = os.getenv("ALLEGRO_CLIENT_SECRET", None)
TOKEN_URL = "https://allegro.pl.allegrosandbox.pl/auth/oauth/token"


def get_access_token():
    try:
        data = {'grant_type': 'client_credentials'}
        access_token_response = requests.post(TOKEN_URL, data=data, verify=False,
                                              allow_redirects=False, auth=(CLIENT_ID, CLIENT_SECRET))
        tokens = json.loads(access_token_response.text)
        
        access_token = tokens['access_token']
        return access_token
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    

    
def get_main_categories(token):
    try:
        url = "https://api.allegro.pl.allegrosandbox.pl/sale/categories"
        headers = {'Accept': "application/vnd.allegro.public.v1+json"}
        main_categories_result = requests.get(url, headers=headers, verify=False)
        return main_categories_result
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def find_first_leaf(parent_id, token):
    try:
        url = "https://api.allegro.pl.allegrosandbox.pl/sale/categories"
        headers = {'Authorization': 'Bearer ' + token, 'Accept': "application/vnd.allegro.public.v1+json"}
        query = {'parent.id': parent_id}
        categories_result = requests.get(url, headers=headers, params=query, verify=False)
        categories = categories_result.json()
        categories_list = categories['categories']
        first_category = categories_list[0]
        if first_category['leaf']:
            return categories
        else:
            return find_first_leaf(first_category['id'], token)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

def main():
 
    main_categories = get_main_categories('aaa')
    print(main_categories.text)
    
    


if __name__ == "__main__":
    main()