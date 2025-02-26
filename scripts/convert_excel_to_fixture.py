import pandas as pd
import json
from datetime import datetime
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

def get_coordinates(address):
    try:
        geolocator = Nominatim(user_agent="hyper_pets")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        location = geocode(address)
        if location:
            return location.latitude, location.longitude
        return None
    except:
        return None

# 엑셀 파일 읽기
df = pd.read_excel('../hospital_data.xlsx')

# 현재 시간
current_time = datetime.utcnow().isoformat() + 'Z'

hospitals = []
pk = 1

for _, row in df.iterrows():
    # 주소에서 위도/경도 가져오기
    coords = get_coordinates(row['주소'])
    if coords:
        latitude, longitude = coords
    else:
        # 좌표를 찾지 못한 경우 서울 시청 근처로 임의 설정
        latitude = 37.5666805 + (np.random.random() - 0.5) * 0.01
        longitude = 126.9784147 + (np.random.random() - 0.5) * 0.01

    # 전화번호 정리 (하이픈 추가)
    phone = str(row['전화번호']).replace('-', '').strip()
    if not phone:
        phone = '02-1234-5678'  # 기본값
    elif len(phone) == 11:  # 02로 시작하지 않는 경우
        phone = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    elif len(phone) == 10 and phone.startswith('02'):  # 02로 시작하는 경우
        phone = f"{phone[:2]}-{phone[2:6]}-{phone[6:]}"

    hospital = {
        "model": "api.hospital",
        "pk": pk,
        "fields": {
            "name": row['업체명'],
            "address": row['주소'],
            "phone": phone,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "description": f"{row['업체명']}은 {row['주소'].split()[2]}에 위치한 동물병원입니다.",
            "operating_hours": "평일 09:00-19:00, 토요일 09:00-15:00",  # 기본값
            "is_24h": False,
            "created_at": current_time,
            "updated_at": current_time,
            "specialties": [1]  # 기본 일반진료 specialty
        }
    }
    hospitals.append(hospital)
    pk += 1
    # API 제한으로 인한 대기
    time.sleep(1)

# JSON 파일로 저장
with open('../api/fixtures/hospital_data.json', 'w', encoding='utf-8') as f:
    json.dump(hospitals, f, ensure_ascii=False, indent=2)

print(f"총 {len(hospitals)}개의 병원 데이터가 생성되었습니다.")
