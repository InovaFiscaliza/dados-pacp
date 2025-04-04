import json
import requests
import uuid
from pathlib import Path

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'


class MeliSearch:

    def __init__(self, output_folder=None, creds_file=None):
               
        if output_folder is not None:
            
            # convert output folder to a Path object
            if isinstance(output_folder, str):
                output_folder = Path(output_folder)
                
            # create subfolders, if it doesn't exist
            self.search_results_folder = output_folder / 'search_results'
            if not self.search_results_folder.exists():
                self.search_results_folder.mkdir(parents=True)
            
            self.item_details_folder = output_folder / 'item_details'
            if not self.item_details_folder.exists():
                self.item_details_folder.mkdir(parents=True)
            
        else:
            self.search_results_folder = None
            self.item_details_folder = None
            
        if creds_file is not None:
            # read credentials file and get new access token
            pass
        
        else:
            self.access_token = None

    # search items and save results to file
    def search_item(self, query, cellphones=False):

        headers = {'User-Agent': USER_AGENT}
        params = {'q': query}
        search_results = []

        if cellphones:
            # endpoint for search all items in cellphones category
            url = 'https://api.mercadolibre.com/sites/MLB/search?category=MLB1055'
        else:
            # endpoint for search all categories
            url = 'https://api.mercadolibre.com/sites/MLB/search?'

        # Instructions for get new access token are available in
        # https://developers.mercadolivre.com.br/pt_br/autenticacao-e-autorizacao
        if self.access_token is None:
            offset_limit = 1000
        else:
            self.offset_limit = 4000
            headers['Authorization'] = f'Bearer {self.access_token}'

        # first page of results
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            content = response.content.decode(response.encoding)
            content =  json.loads(content)
            
            if self.search_results_folder is not None:
                output_file = self.search_results_folder / f'{str(uuid.uuid4())}.json'
                with open(output_file,'w') as f:
                    json.dump(content,f,indent=2)
                
            total_results = content['paging']['total']
            results = content['results']
            if len(results) > 0:
                search_results.extend(results)

            if total_results < offset_limit:
                max_offset = total_results
            else:
                max_offset = offset_limit
        else:
            return None

        # iterate over next results pages
        for actual_offset in range(50,max_offset,50):
            params['offset'] = actual_offset
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                content = response.content.decode(response.encoding)
                content =  json.loads(content)
                
                if self.search_results_folder is not None:
                    output_file = self.search_results_folder / f'{str(uuid.uuid4())}.json'
                    with open(output_file,'w') as f:
                        json.dump(content,f,indent=2)
                
                if len(content['results']) > 0: 
                    search_results.extend(results)
        
        return search_results
    
    # search item details and save results to file
    def search_item_details(self, item_id):
    
        url = f'https://api.mercadolibre.com/items/{item_id}'
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.content.decode(response.encoding)
            content =  json.loads(content)

            if self.item_details_folder is not None:
                output_file = self.item_details_folder / f'{item_id}.json'
                with open(output_file,'w') as f:
                    json.dump(content,f,indent=2)
            
            return content
        else:
            return None
        
    def parse_item_details(self, item_details):
        
        keys_to_keep = [
            'id', 
            'title', 
            'seller_id', 
            'category_id', 
            'official_store_id', 
            'price', 
            'shipping',
            'currency_id', 
            'initial_quantity',
            'condition', 
            'permalink', 
            'warranty', 
            'catalog_product_id', 
            'date_created', 
            'last_updated', 
            'status'
        ]
        
        attributes_to_keep = [
            'ITEM_CONDITION', 
            'BRAND', 
            'MODEL', 
            'DETAILED_MODEL', 
            'ANATEL_HOMOLOGATION_NUMBER', 
            'CELLPHONES_ANATEL_HOMOLOGATION_NUMBER', 
            'GTIN', 
            'EMPTY_GTIN_REASON',
        ]

        columns_to_keep = [col.lower() for col in keys_to_keep+attributes_to_keep]

        try:
            if item_details['status']=='under review':
                return None
        except:
            return None

        if not 'attributes' in item_details.keys():
            return None
        
        parsed_item_details = {key:None for key in columns_to_keep}    
        for key in keys_to_keep:
            try:
                parsed_item_details[key] = item_details[key]
            except:
                continue
        
        for item_attribute in item_details['attributes']:
            if item_attribute['id'] in attributes_to_keep:
                attribute_key = item_attribute['id'].lower()
                parsed_item_details[attribute_key]  = item_attribute['value_name']

        parsed_item_details['warranty_type'] = None
        if 'sale_terms' in item_details.keys():
            for sale_term in item_details['sale_terms']:
                if sale_term['id'] == 'WARRANTY_TYPE':
                    parsed_item_details['warranty_type'] = sale_term['value_name']

        if parsed_item_details['anatel_homologation_number'] is not None:
            parsed_item_details['anatel_homologation_number'] = parsed_item_details['anatel_homologation_number'].zfill(12)

        if parsed_item_details['cellphones_anatel_homologation_number'] is not None:
            parsed_item_details['cellphones_anatel_homologation_number'] = parsed_item_details['cellphones_anatel_homologation_number'].zfill(12)

        return parsed_item_details
    
    def parse_item_details_file(self, item_details_file):
        
        if isinstance(item_details_file, str):
            item_details_file = Path(item_details_file)
        
        with open(item_details_file) as file:
            item_details = json.load(file)
            
        return self.parse_item_details(item_details)
                
        
        
    