#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
서울시 25개 자치구별 반려동물 복지사업 데이터를 Support 모델에 추가하는 스크립트입니다.
Excel 파일에서 데이터를 읽어와 Django DB에 저장합니다.
"""

import os
import sys
import pandas as pd
import datetime
from django.utils import timezone

# Django 설정 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyper_pets_backend.settings')

import django
django.setup()

from api.models import Support, Region

# 서울시 지역 코드 매핑
SEOUL_DISTRICTS = {
    '강남구': '서울특별시 강남구',
    '강동구': '서울특별시 강동구',
    '강북구': '서울특별시 강북구',
    '강서구': '서울특별시 강서구',
    '관악구': '서울특별시 관악구',
    '광진구': '서울특별시 광진구',
    '구로구': '서울특별시 구로구',
    '금천구': '서울특별시 금천구',
    '노원구': '서울특별시 노원구',
    '도봉구': '서울특별시 도봉구',
    '동대문구': '서울특별시 동대문구',
    '동작구': '서울특별시 동작구',
    '마포구': '서울특별시 마포구',
    '서대문구': '서울특별시 서대문구',
    '서초구': '서울특별시 서초구',
    '성동구': '서울특별시 성동구',
    '성북구': '서울특별시 성북구',
    '송파구': '서울특별시 송파구',
    '양천구': '서울특별시 양천구',
    '영등포구': '서울특별시 영등포구',
    '용산구': '서울특별시 용산구',
    '은평구': '서울특별시 은평구',
    '종로구': '서울특별시 종로구',
    '중구': '서울특별시 중구',
    '중랑구': '서울특별시 중랑구',
    '서울시': '서울특별시',
    '서울특별시': '서울특별시',
}

# 지원 유형 매핑
SUPPORT_TYPE_MAPPING = {
    '중성화': 'medical',
    '진료비': 'medical',
    '의료': 'medical',
    '수술': 'medical',
    '접종': 'medical',
    '예방': 'medical',
    '상담': 'education',
    '교육': 'education',
    '훈련': 'education',
    '분양': 'adoption',
    '입양': 'adoption',
    '지원금': 'financial',
    '비용': 'financial',
    '지원': 'financial',
    '등록': 'other',
    '기타': 'other',
}

# /**
#  * Excel 파일에서 데이터를 읽어 Support 모델에 저장하는 함수
#  * 
#  * @param {string} excelPath - Excel 파일 경로
#  * @param {boolean} dryRun - 테스트 실행 모드 (DB에 저장하지 않음)
#  * @returns {number} - 추가된 데이터 개수
#  * 
#  * @example
#  * // Excel 파일을 읽어서 DB에 저장
#  * const addedCount = importSeoulPetWelfareData('./data/seoul_pet_welfare.xlsx', false);
#  * console.log(`${addedCount}개의 데이터가 추가되었습니다.`);
#  */
def importSeoulPetWelfareData(excelPath, dryRun=False):
  try:
    # Excel 파일 읽기
    df = pd.read_excel(excelPath)
    
    print(f"Excel 파일 읽기 성공: {len(df)}개의 행이 있습니다.")
    
    # 컬럼명 확인
    print("컬럼명:", list(df.columns))
    
    # 데이터 추가 카운터
    addedCount = 0
    
    # 각 행 처리
    for _, row in df.iterrows():
      try:
        # 기본 데이터 가져오기 (실제 Excel 파일의 컬럼명에 맞춤)
        district = row.get('자치구', '')
        title = row.get('주제', '')
        description = row.get('내용', '')
        website_url = row.get('확인 사이트', '')
        contact = row.get('담당 부서 및 문의처', '')
        category = row.get('대분류', '')
        
        # 누락된 값 처리
        if not title or pd.isna(title):
          continue
        
        # 추가 필드 구성 (Excel에 없는 필드는 적절히 채움)
        target = "서울시 " + district + " 거주 반려동물 소유자"
        benefit = description  # 내용을 지원내용으로 사용
        requirements = "서울시 " + district + " 거주자"
        how_to_apply = website_url + " 사이트 참조 또는 담당 부서 문의" if not pd.isna(website_url) else "담당 부서 문의"
        
        # 누락된 값 처리
        if not title or pd.isna(title):
          continue
          
        # 지원 유형 결정
        supportType = 'other'  # 기본값
        for keyword, typeName in SUPPORT_TYPE_MAPPING.items():
          if (title and keyword in title) or (description and keyword in description) or (category and keyword in category):
            supportType = typeName
            break
            
        # 날짜 필드 (자치구 자료에 없을 수 있음)
        startDate = datetime.date.today()
        deadline = None
        
        # 테스트 모드가 아닌 경우 DB에 저장
        if not dryRun:
          support = Support(
            title=title,
            description=description if not pd.isna(description) else '',
            support_type=supportType,
            status='ongoing',
            requirements=requirements if not pd.isna(requirements) else '',
            target=target if not pd.isna(target) else '',
            benefit=benefit if not pd.isna(benefit) else '',
            how_to_apply=how_to_apply if not pd.isna(how_to_apply) else '',
            start_date=startDate,
            deadline=deadline,
            organization=f'서울특별시 {district}' if not pd.isna(district) else '서울특별시',
            contact=contact if not pd.isna(contact) else '',
            region=district if not pd.isna(district) else '서울특별시',
            source='manual',
            external_id=f'seoul_pet_{addedCount}',
          )
          support.save()
          
          # Region 연결 (Region 모델이 있는 경우)
          try:
            regionName = SEOUL_DISTRICTS.get(district, '서울특별시')
            regions = Region.objects.filter(name__icontains=regionName)
            if regions.exists():
              for region in regions:
                support.regions.add(region)
          except Exception as regionErr:
            print(f"지역 연결 오류: {regionErr}")
          
          addedCount += 1
          print(f"추가됨: {title} ({district})")
        else:
          # 테스트 모드: 추가될 데이터 출력
          print(f"테스트 모드 - 추가 예정: {title} ({district})")
          addedCount += 1
          
      except Exception as rowErr:
        print(f"행 처리 중 오류 발생: {rowErr}")
    
    return addedCount
    
  except Exception as e:
    print(f"데이터 가져오기 오류: {e}")
    return 0

if __name__ == "__main__":
  # 데이터 파일 경로
  dataPath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', '서울시 25개 자치구별 반려동물 복지사업 정리본 (1).xlsx')
  
  # 파일 존재 여부 확인
  if not os.path.exists(dataPath):
    print(f"오류: 파일을 찾을 수 없습니다 - {dataPath}")
    print("먼저 Excel 파일을 backend/data 디렉토리에 복사하세요.")
    sys.exit(1)
  
  # 명령행 인자 처리
  dryRun = '--dry-run' in sys.argv
  if dryRun:
    print("테스트 모드: 실제로 DB에 저장하지 않습니다.")
  
  # 데이터 가져오기 실행
  addedCount = importSeoulPetWelfareData(dataPath, dryRun)
  
  # 결과 출력
  if dryRun:
    print(f"테스트 결과: {addedCount}개의 데이터가 추가될 예정입니다.")
  else:
    print(f"완료: {addedCount}개의 데이터가 추가되었습니다.")
