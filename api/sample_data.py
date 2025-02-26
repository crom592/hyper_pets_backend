from api.models import Shelter, Hospital, Category

# 서울 주요 지역의 좌표
locations = [
    # 강남역
    {'name': '강남 동물보호소', 'lat': 37.4980854, 'lng': 127.0275886},
    {'name': '강남 24시 동물병원', 'lat': 37.4990854, 'lng': 127.0285886},
    # 홍대입구역
    {'name': '홍대 유기동물 보호센터', 'lat': 37.5571607, 'lng': 126.9242595},
    {'name': '홍대 동물병원', 'lat': 37.5581607, 'lng': 126.9252595},
    # 여의도
    {'name': '여의도 동물보호소', 'lat': 37.5216729, 'lng': 126.9242595},
    {'name': '여의도 반려동물 병원', 'lat': 37.5226729, 'lng': 126.9252595},
]

# 보호소 데이터 생성
for i in range(0, len(locations), 2):
    Shelter.objects.create(
        name=locations[i]['name'],
        description=f'{locations[i]["name"]}입니다. 유기동물들에게 새로운 가족을 찾아주고 있습니다.',
        address='서울특별시 XX구 XX동 123-45',
        latitude=locations[i]['lat'],
        longitude=locations[i]['lng'],
        phone='02-1234-5678',
        operating_hours='09:00 - 18:00',
        capacity=50,
        current_occupancy=30
    )

# 병원 데이터 생성
for i in range(1, len(locations), 2):
    hospital = Hospital.objects.create(
        name=locations[i]['name'],
        description=f'{locations[i]["name"]}입니다. 24시간 응급진료가 가능합니다.',
        address='서울특별시 XX구 XX동 123-45',
        latitude=locations[i]['lat'],
        longitude=locations[i]['lng'],
        phone='02-1234-5678',
        operating_hours='00:00 - 24:00',
        is_24h=True
    )

print('Sample data created successfully!')
