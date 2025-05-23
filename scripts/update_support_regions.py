#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기존에 등록된 Support 모델의 데이터를 Region 모델과 연결하는 스크립트
"""

import os
import sys
import django

# Django 설정 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyper_pets_backend.settings')

django.setup()

from api.models import Support, Region

def update_support_regions():
  """
  기존 Support 모델의 데이터를 Region 모델과 연결합니다.
  region 필드(문자열)의 값을 기준으로 regions 필드(ManyToMany)에 해당 Region 객체를 추가합니다.
  """
  # 서울시 자치구 목록 가져오기
  districts = Region.objects.filter(level=1)
  
  # 자치구명 -> Region 객체 매핑
  district_map = {district.name: district for district in districts}
  
  # 서울시 전체 Region 객체
  seoul = Region.objects.filter(level=0).first()
  
  # 모든 Support 객체에 대해 처리
  total_count = Support.objects.count()
  updated_count = 0
  
  for support in Support.objects.all():
    district_name = support.region.replace('서울특별시 ', '').replace('서울시 ', '')
    
    # 이미 regions에 연결되어 있는지 확인
    if support.regions.exists():
      continue
      
    # 자치구별 처리
    if district_name in district_map:
      district = district_map[district_name]
      support.regions.add(district)
      
      # 서울시도 추가
      if seoul:
        support.regions.add(seoul)
        
      updated_count += 1
      print(f"업데이트: {support.title} - 연결된 지역: {district.name}")
    else:
      # 자치구명이 일치하지 않으면 서울시로만 연결
      if seoul:
        support.regions.add(seoul)
        updated_count += 1
        print(f"업데이트: {support.title} - 연결된 지역: 서울특별시 (자치구 매칭 실패: {district_name})")
  
  return updated_count, total_count

if __name__ == "__main__":
  print("Support 모델의 데이터를 Region 모델과 연결하는 작업을 시작합니다...")
  updated_count, total_count = update_support_regions()
  print(f"완료: 총 {total_count}개 중 {updated_count}개 Support 레코드가 업데이트되었습니다.")
