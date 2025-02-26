from django.core.management.base import BaseCommand
from api.models import Hospital, Shelter
import requests
import time
from django.conf import settings
import json

class Command(BaseCommand):
    help = '네이버 지도 API를 사용하여 병원과 보호소의 좌표를 업데이트합니다.'

    def geocode_address(self, address):
        url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode'
        headers = {
            'X-NCP-APIGW-API-KEY-ID': settings.NAVER_CLIENT_ID,
            'X-NCP-APIGW-API-KEY': settings.NAVER_CLIENT_SECRET,
        }
        params = {
            'query': address
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            if response.status_code == 200 and data.get('addresses'):
                result = data['addresses'][0]
                return float(result['y']), float(result['x'])  # latitude, longitude
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error geocoding address {address}: {str(e)}'))
            return None

    def update_locations(self, model):
        updated_count = 0
        failed_count = 0
        locations = model.objects.all()
        total = locations.count()

        # 좌표 업데이트 결과를 저장할 리스트
        results = []

        for idx, location in enumerate(locations, 1):
            self.stdout.write(f'Processing {idx}/{total}: {location.name}')
            
            # 주소로 좌표 조회
            coordinates = self.geocode_address(location.address)
            
            if coordinates:
                old_coords = {
                    'latitude': location.latitude,
                    'longitude': location.longitude
                }
                
                location.latitude, location.longitude = coordinates
                location.save()
                
                results.append({
                    'name': location.name,
                    'address': location.address,
                    'old_coordinates': old_coords,
                    'new_coordinates': {
                        'latitude': location.latitude,
                        'longitude': location.longitude
                    }
                })
                
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Updated coordinates for {location.name}: '
                    f'({location.latitude}, {location.longitude})'
                ))
            else:
                failed_count += 1
                self.stdout.write(self.style.WARNING(
                    f'Failed to geocode address for {location.name}'
                ))
            
            # 네이버 API 호출 제한을 고려한 딜레이
            time.sleep(0.1)

        # 결과를 JSON 파일로 저장
        model_name = model.__name__.lower()
        with open(f'{model_name}_coordinate_updates.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return updated_count, failed_count

    def handle(self, *args, **options):
        self.stdout.write('Starting coordinate update process...')

        # 병원 좌표 업데이트
        hospital_updated, hospital_failed = self.update_locations(Hospital)
        self.stdout.write(self.style.SUCCESS(
            f'Hospitals - Updated: {hospital_updated}, Failed: {hospital_failed}'
        ))

        # 보호소 좌표 업데이트
        shelter_updated, shelter_failed = self.update_locations(Shelter)
        self.stdout.write(self.style.SUCCESS(
            f'Shelters - Updated: {shelter_updated}, Failed: {shelter_failed}'
        ))

        self.stdout.write(self.style.SUCCESS('Coordinate update process completed!'))
