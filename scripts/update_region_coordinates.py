#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Region 모델의 서울시 및 자치구 데이터에 위도/경도 정보를 업데이트하는 스크립트
"""

import os
import sys
import django

# Django 설정 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyper_pets_backend.settings')

django.setup()

from api.models import Region

# 서울시 자치구별 중심점 좌표 (위도, 경도)
DISTRICT_COORDINATES = {
    '서울특별시': (37.5665, 126.9780),  # 서울시 중심점
    '종로구': (37.5721, 126.9807),
    '중구': (37.5604, 126.9959),
    '용산구': (37.5388, 126.9650),
    '성동구': (37.5488, 127.0371),
    '광진구': (37.5485, 127.0859),
    '동대문구': (37.5743, 127.0400),
    '중랑구': (37.5953, 127.0771),
    '성북구': (37.6067, 127.0192),
    '강북구': (37.6478, 127.0257),
    '도봉구': (37.6662, 127.0468),
    '노원구': (37.6518, 127.0750),
    '은평구': (37.6176, 126.9227),
    '서대문구': (37.5816, 126.9374),
    '마포구': (37.5519, 126.9378),
    '양천구': (37.5169, 126.8687),
    '강서구': (37.5651, 126.8227),
    '구로구': (37.4954, 126.8874),
    '금천구': (37.4569, 126.8954),
    '영등포구': (37.5264, 126.8962),
    '동작구': (37.5115, 126.9395),
    '관악구': (37.4782, 126.9517),
    '서초구': (37.4837, 127.0324),
    '강남구': (37.5172, 127.0473),
    '송파구': (37.5145, 127.1060),
    '강동구': (37.5304, 127.1237)
}

def update_region_coordinates():
    """
    Region 모델의 각 지역 데이터에 위도/경도 정보를 업데이트합니다.
    """
    updated_count = 0
    
    for region in Region.objects.all():
        district_name = region.name
        
        if district_name in DISTRICT_COORDINATES:
            latitude, longitude = DISTRICT_COORDINATES[district_name]
            
            region.latitude = latitude
            region.longitude = longitude
            region.save()
            
            updated_count += 1
            print(f"업데이트: {district_name} - 위도: {latitude}, 경도: {longitude}")
    
    return updated_count

if __name__ == "__main__":
    print("Region 모델에 위도/경도 정보를 업데이트하는 작업을 시작합니다...")
    updated_count = update_region_coordinates()
    print(f"완료: {updated_count}개 지역의 위치 정보가 업데이트되었습니다.")
