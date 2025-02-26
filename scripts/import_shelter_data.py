import os
import sys
import django
import json
from pathlib import Path

# Set up Django environment
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyper_pets_backend.settings')
django.setup()

from api.models import Shelter

def import_shelter_data():
    # Read the JSON file
    with open('fixtures/shelter_data.json', 'r', encoding='utf-8') as f:
        shelters_data = json.load(f)
    
    # Counter for tracking
    created_count = 0
    updated_count = 0
    
    for shelter_data in shelters_data:
        # Try to find existing shelter by name and address
        shelter, created = Shelter.objects.update_or_create(
            name=shelter_data['name'],
            address=shelter_data['address'],
            defaults={
                'latitude': shelter_data['latitude'],
                'longitude': shelter_data['longitude'],
                'phone': shelter_data['phone'],
                'description': shelter_data['description'],
                'operating_hours': shelter_data['operating_hours'],
            }
        )
        
        if created:
            created_count += 1
        else:
            updated_count += 1
    
    print(f'Successfully imported shelter data:')
    print(f'Created: {created_count}')
    print(f'Updated: {updated_count}')
    print(f'Total: {created_count + updated_count}')

if __name__ == '__main__':
    import_shelter_data()
