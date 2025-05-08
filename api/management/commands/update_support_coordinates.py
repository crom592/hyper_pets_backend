"""
위치 정보가 없는 Support 데이터의 region 정보를 기반으로 
위도/경도 값을 업데이트하는 명령어
"""
from django.core.management.base import BaseCommand
from api.models import Support

class Command(BaseCommand):
    help = '지원 정책 데이터에 위치 정보 추가'

    # 지역별 좌표 정보 (프론트엔드와 동일한 데이터)
    REGION_COORDINATES = {
        '서울': [37.5665, 126.9780],
        '강남구': [37.5172, 127.0473],
        '강서구': [37.5509, 126.8495],
        '강동구': [37.5300, 127.1236],
        '강북구': [37.6396, 127.0257],
        '관악구': [37.4784, 126.9516],
        '광진구': [37.5385, 127.0825],
        '구로구': [37.4957, 126.8878],
        '금천구': [37.4566, 126.8954],
        '노원구': [37.6552, 127.0571],
        '도봉구': [37.6688, 127.0471],
        '동대문구': [37.5744, 127.0395],
        '동작구': [37.5124, 126.9560],
        '마포구': [37.5637, 126.9086],
        '서대문구': [37.5791, 126.9368],
        '서초구': [37.4835, 127.0319],
        '성동구': [37.5636, 127.0371],
        '성북구': [37.5894, 127.0162],
        '송파구': [37.5145, 127.1058],
        '양천구': [37.5169, 126.8664],
        '영등포구': [37.5264, 126.8965],
        '용산구': [37.5320, 126.9900],
        '은평구': [37.6026, 126.9291],
        '종로구': [37.5730, 126.9794],
        '중구': [37.5640, 126.9975],
        '중랑구': [37.6066, 127.0927],
        '부산': [35.1796, 129.0756],
        '대구': [35.8714, 128.6014],
        '인천': [37.4563, 126.7052],
        '광주': [35.1595, 126.8526],
        '대전': [36.3504, 127.3845],
        '울산': [35.5384, 129.3114],
        '세종': [36.4800, 127.2890],
        '경기': [37.4138, 127.5183],
        '강원': [37.8228, 128.1555],
        '충북': [36.6357, 127.4913],
        '충남': [36.6588, 126.6728],
        '전북': [35.8202, 127.1089],
        '전남': [34.8679, 126.9910],
        '경북': [36.4919, 128.8889],
        '경남': [35.4606, 128.2132],
        '제주': [33.4996, 126.5312]
    }

    def extract_coordinates_from_region(self, region_str):
        """지역 문자열에서 좌표를 추출하는 함수"""
        if not region_str:
            return None, None
        
        # 지역 문자열을 공백, 쉼표 등으로 분리하여 처리
        parts = region_str.split(',')
        parts = [p.strip() for p in parts if p.strip()]
        if not parts:
            parts = region_str.split()
            parts = [p.strip() for p in parts if p.strip()]
        
        # 각 부분에 대해 좌표 정보가 있는지 확인
        for part in parts:
            for region, coords in self.REGION_COORDINATES.items():
                if region in part:
                    return coords[0], coords[1]
        
        # 지역명에 '전국'이 포함되어 있으면 서울 좌표 사용
        if '전국' in region_str:
            return self.REGION_COORDINATES['서울']
        
        # 기본값으로 서울 좌표 반환
        return self.REGION_COORDINATES['서울']

    def extract_coordinates_from_organization(self, organization, region_str):
        """구청, 시청, 도청 등 organization 주소에서 좌표 추출"""
        if not organization:
            return self.extract_coordinates_from_region(region_str)
        
        # 주요 기관 키워드
        org_keywords = [
            '구청', '시청', '도청', '군청',
            '서울시', '경기도', '경상북도', '경상남도', '전라북도', '전라남도', '제주도',
            '인천시', '부산시', '대구시', '광주시', '대전시', '울산시', '세종시', '강원도',
            '충청북도', '충청남도'
        ]
        
        # 기관명 파싱
        parts = organization.split(',')
        parts = [p.strip() for p in parts if p.strip()]
        if not parts:
            parts = organization.split()
            parts = [p.strip() for p in parts if p.strip()]
        
        # 기관명에서 지역 키워드 찾기
        for part in parts:
            # 1. 지역 관선 키워드 확인
            for keyword in org_keywords:
                if keyword in part:
                    # 2. 지역명 확인
                    for region, coords in self.REGION_COORDINATES.items():
                        if region in part:
                            return coords[0], coords[1]
        
        # 기관명에서 추출 실패시 region에서 시도
        return self.extract_coordinates_from_region(region_str)

    def handle(self, *args, **options):
        # 모든 지원 정책 가져오기 - 강제 업데이트 실행
        supports = Support.objects.all()
        
        updated_count = 0
        skipped_count = 0
        
        for support in supports:
            # 기관 정보와 지역 정보를 모두 활용하여 좌표 추출
            lat, lng = self.extract_coordinates_from_organization(support.organization, support.region)
            
            if lat and lng:
                support.latitude = lat
                support.longitude = lng
                support.save()
                updated_count += 1
                self.stdout.write(f"Updated: {support.title} -> ({lat}, {lng})")
            else:
                skipped_count += 1
                self.stdout.write(f"Skipped: {support.title} (No coordinates found for organization: {support.organization}, region: {support.region})")
        
        self.stdout.write(self.style.SUCCESS(
            f'완료: {updated_count}개 업데이트, {skipped_count}개 건너뜀'
        ))
