#!/usr/bin/env python
"""
데이터베이스에 있는 병원 전화번호를 fixtures 파일의 데이터로 업데이트하는 스크립트
병원 이름을 기준으로 매칭하여 전화번호 수정
"""
import os
import json
import sys
import django
from pprint import pprint

# Django 환경 설정
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyper_pets_backend.settings')
    django.setup()
except ImportError:
    print("Django 설정 모듈을 찾을 수 없습니다. 프로젝트 구조를 확인해주세요.")
    sys.exit(1)

from api.models import Hospital

def update_hospital_data():
    """
    fixtures 파일의 전화번호 데이터로 데이터베이스 업데이트
    병원 이름을 기준으로 매칭
    """
    # fixtures 파일 경로
    fixture_path = os.path.join('api', 'fixtures', 'hospital_data.json')
    
    # fixtures 파일 읽기
    with open(fixture_path, 'r', encoding='utf-8') as f:
        fixture_data = json.load(f)
    
    # fixture 데이터를 이름 기준으로 매핑
    fixture_map = {}
    for item in fixture_data:
        if item['model'] == 'api.hospital':
            hospital_name = item['fields']['name']
            phone = item['fields']['phone']
            fixture_map[hospital_name] = phone
    
    print(f"데이터 가져오기 성공: {len(fixture_map)}개 병원 데이터 로드")
    
    # 데이터베이스에서 모든 병원 가져오기
    hospitals = Hospital.objects.all()
    print(f"데이터베이스에서 {hospitals.count()}개 병원 로드")
    
    # 데이터베이스 업데이트
    updated_count = 0
    missing_hospitals = []
    
    for hospital in hospitals:
        hospital_name = hospital.name
        if hospital_name in fixture_map:
            fixture_phone = fixture_map[hospital_name]
            if hospital.phone != fixture_phone:
                print(f"병원 '{hospital_name}': 전화번호 수정 '{hospital.phone}' -> '{fixture_phone}'")
                hospital.phone = fixture_phone
                hospital.save(update_fields=['phone'])
                updated_count += 1
            else:
                print(f"병원 '{hospital_name}': 전화번호 이미 일치함 '{fixture_phone}'")
        else:
            missing_hospitals.append(hospital_name)
            print(f"병원 '{hospital_name}'은(는) fixture에 없음")
    
    print(f"\n총 {updated_count}개의 전화번호가 업데이트되었습니다.")
    
    if missing_hospitals:
        print(f"\nfixture에서 찾을 수 없는 병원 {len(missing_hospitals)}개:")
        for name in missing_hospitals[:10]:  # 처음 10개만 출력
            print(f" - {name}")
        if len(missing_hospitals) > 10:
            print(f" ... 그 외 {len(missing_hospitals) - 10}개")

if __name__ == "__main__":
    update_hospital_data()
