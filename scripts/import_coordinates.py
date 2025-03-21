import os
import sys
import django
import json
from pathlib import Path

# Django 환경 설정
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyper_pets_backend.settings')
django.setup()

from api.models import Hospital, Shelter

def import_hospital_coordinates():
    """병원 좌표 데이터를 가져옵니다."""
    try:
        with open('hospital_coordinate_updates.json', 'r', encoding='utf-8') as f:
            hospitals_data = json.load(f)
        
        updated_count = 0
        created_count = 0
        
        for hospital_data in hospitals_data:
            hospital, created = Hospital.objects.update_or_create(
                name=hospital_data['name'],
                address=hospital_data['address'],
                defaults={
                    'latitude': hospital_data['new_coordinates']['latitude'],
                    'longitude': hospital_data['new_coordinates']['longitude'],
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        print(f'병원 데이터 가져오기 완료:')
        print(f'생성됨: {created_count}')
        print(f'업데이트됨: {updated_count}')
        print(f'총: {created_count + updated_count}')
        
    except Exception as e:
        print(f'병원 데이터 가져오기 오류: {str(e)}')

def import_shelter_coordinates():
    """보호소 좌표 데이터를 가져옵니다."""
    try:
        with open('shelter_coordinate_updates.json', 'r', encoding='utf-8') as f:
            shelters_data = json.load(f)
        
        updated_count = 0
        created_count = 0
        
        for shelter_data in shelters_data:
            shelter, created = Shelter.objects.update_or_create(
                name=shelter_data['name'],
                address=shelter_data['address'],
                defaults={
                    'latitude': shelter_data['new_coordinates']['latitude'],
                    'longitude': shelter_data['new_coordinates']['longitude'],
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        print(f'보호소 데이터 가져오기 완료:')
        print(f'생성됨: {created_count}')
        print(f'업데이트됨: {updated_count}')
        print(f'총: {created_count + updated_count}')
        
    except Exception as e:
        print(f'보호소 데이터 가져오기 오류: {str(e)}')

if __name__ == '__main__':
    print('좌표 데이터 가져오기 시작...')
    import_hospital_coordinates()
    import_shelter_coordinates()
    print('좌표 데이터 가져오기 완료!')
