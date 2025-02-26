import json
import requests
import os
from pathlib import Path
import time

def geocode_address(address, client_id, client_secret):
    headers = {
        'X-NCP-APIGW-API-KEY-ID': client_id,
        'X-NCP-APIGW-API-KEY': client_secret,
    }
    
    endpoint = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode'
    params = {
        'query': address
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        
        if result['addresses']:
            location = result['addresses'][0]
            return float(location['y']), float(location['x'])  # lat, lng
        return None
    except Exception as e:
        print(f"Error geocoding address {address}: {str(e)}")
        return None

def process_shelter_data():
    # Get API credentials from environment
    client_id = os.getenv('NEXT_PUBLIC_NAVER_CLIENT_ID')
    client_secret = os.getenv('NEXT_PUBLIC_NAVER_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("Error: Naver Maps API credentials not found in environment variables")
        return
    
    # Read the shelter data
    input_path = Path('fixtures/shelter_data.json')
    with open(input_path, 'r', encoding='utf-8') as f:
        shelters = json.load(f)
    
    # Process each shelter
    for shelter in shelters:
        if shelter['latitude'] == 0 and shelter['longitude'] == 0:
            print(f"Geocoding {shelter['name']}...")
            result = geocode_address(shelter['address'], client_id, client_secret)
            
            if result:
                shelter['latitude'], shelter['longitude'] = result
                print(f"Success: {shelter['latitude']}, {shelter['longitude']}")
            else:
                print(f"Failed to geocode {shelter['name']}")
            
            # Add delay to respect API rate limits
            time.sleep(0.5)
    
    # Save the updated data
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(shelters, f, ensure_ascii=False, indent=2)
    
    print(f"Updated {len(shelters)} shelters")

if __name__ == '__main__':
    process_shelter_data()
