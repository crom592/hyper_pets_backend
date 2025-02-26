import pandas as pd
import json
from pathlib import Path

def process_shelter_data():
    # Read the Excel file
    df = pd.read_excel('shelter_data.xls')
    print('Available columns:', df.columns.tolist())
    
    # Rename columns to match our schema
    df = df.rename(columns={
        '보호센터명': 'name',
        '주소': 'address',
        '전화번호': 'phone'
    })
    
    # Initialize geocoding results
    shelters = []
    
    for _, row in df.iterrows():
        shelter = {
            'name': row['name'],
            'address': row['address'],
            'phone': row['phone'],
            'type': 'shelter',
            'description': f'서울시 공식 동물보호센터',
            'operating_hours': '09:00-18:00',  # Default hours
            # We'll need to geocode these addresses to get lat/lng
            'latitude': 0,
            'longitude': 0
        }
        shelters.append(shelter)
    
    # Save to JSON file
    output_path = Path('fixtures/shelter_data.json')
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(shelters, f, ensure_ascii=False, indent=2)
    
    print(f'Processed {len(shelters)} shelters')
    print(f'Data saved to {output_path}')

if __name__ == '__main__':
    process_shelter_data()
