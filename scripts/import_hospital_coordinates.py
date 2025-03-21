import os
import sys
import django
import json
from pathlib import Path

# Django 환경 설정
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyper_pets_backend.settings')
django.setup()

from api.models import Hospital

def import_hospital_coordinates():
    """병원 좌표 데이터를 가져옵니다."""
    try:
        with open('hospital_coordinate_updates.json', 'r', encoding='utf-8') as f:
            hospitals_data = json.load(f)
        
        updated_count = 0
        created_count = 0
        
        for hospital_data in hospitals_data:
            # 기본 전화번호 설정
            phone = "02-1234-5678"
            
            # 병원 생성 또는 업데이트
            hospital, created = Hospital.objects.update_or_create(
                name=hospital_data['name'],
                address=hospital_data['address'],
                defaults={
                    'latitude': hospital_data['new_coordinates']['latitude'],
                    'longitude': hospital_data['new_coordinates']['longitude'],
                    'phone': phone,  # 기본 전화번호 사용
                    'description': f"{hospital_data['name']}은 {hospital_data['address'].split()[2]}에 위치한 동물병원입니다.",
                    'operating_hours': "평일 09:00-19:00, 토요일 09:00-15:00",  # 기본 운영시간
                    'is_24h': False  # 기본값
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

if __name__ == '__main__':
    print('병원 좌표 데이터 가져오기 시작...')
    import_hospital_coordinates()
    print('병원 좌표 데이터 가져오기 완료!')
