#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
법정동 코드 CSV 파일을 사용하여 Region 모델에 서울시 자치구 데이터를 가져오는 스크립트
"""

import os
import sys
import csv
import django

# Django 설정 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyper_pets_backend.settings')

django.setup()

from api.models import Region

def import_regions_from_csv(csv_file_path, max_level=2):
    """
    CSV 파일에서 Region 모델로 지역 데이터를 가져옵니다.
    
    Args:
        csv_file_path: CSV 파일 경로
        max_level: 가져올 최대 레벨 (0: 서울시, 1: 자치구, 2: 동)
    """
    # 지역 캐시 (code -> Region 객체)
    region_cache = {}
    
    # CSV 파일 열기
    print(f"CSV 파일 읽기: {csv_file_path}")
    with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        # 헤더 확인
        print(f"CSV 헤더: {reader.fieldnames}")
        
        # CSV 행 처리
        for row in reader:
            # 코드와 상위 지역 코드 가져오기
            code = row['법정동코드'].strip()
            parent_code = row['상위지역코드'].strip()
            region_name = row['법정동명'].strip()
            
            # 코드 길이로 레벨 결정
            if code.endswith('00000000'):  # 시/도 레벨 (서울특별시)
                level = 0
            elif code.endswith('000000'):  # 구/군 레벨 (강남구 등)
                level = 1
            else:  # 동 레벨
                level = 2
                
            # 최대 레벨 체크
            if level > max_level:
                continue
                
            # 이미 추가된 지역인지 확인
            if Region.objects.filter(code=code).exists():
                region = Region.objects.get(code=code)
                region_cache[code] = region
                print(f"이미 존재하는 지역: {region_name} (코드: {code}, 레벨: {level})")
                continue
                
            # 상위 지역이 있는 경우 (서울특별시는 parent가 없음)
            parent = None
            if parent_code != '0000000000' and parent_code in region_cache:
                parent = region_cache[parent_code]
            
            # Region 모델에 저장
            region = Region(
                code=code,
                name=region_name.split()[-1],  # "서울특별시 강남구" -> "강남구"
                parent=parent,
                level=level
            )
            region.save()
            region_cache[code] = region
            
            print(f"추가됨: {region_name} (코드: {code}, 레벨: {level})")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='법정동 코드 CSV 파일에서 Region 모델로 데이터를 가져옵니다.')
    parser.add_argument('--csv', default='data/legal_codes.csv', help='CSV 파일 경로')
    parser.add_argument('--level', type=int, default=1, help='가져올 최대 레벨 (0: 서울시, 1: 자치구, 2: 동)')
    args = parser.parse_args()
    
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), args.csv)
    
    # 파일 존재 확인
    if not os.path.exists(csv_path):
        print(f"오류: CSV 파일을 찾을 수 없습니다 - {csv_path}")
        sys.exit(1)
    
    # 데이터 가져오기 실행
    import_regions_from_csv(csv_path, args.level)
    print("완료: Region 모델에 지역 데이터가 추가되었습니다.")
    
    # Region 모델 확인
    regions_count = Region.objects.count()
    print(f"Region 모델에 총 {regions_count}개의 지역이 있습니다.")
