from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import (
    Category, PetType, ServiceType, CustomUser, PetOwnerProfile, 
    PetSitterProfile, UserPet, PetSitterService, PetSitterAvailability,
    CertificationImage
)
from django.db import transaction
import random
from datetime import time, timedelta, datetime

User = get_user_model()

class Command(BaseCommand):
    help = '샘플 데이터를 생성합니다'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('샘플 데이터 생성 시작...')
        
        # 카테고리 생성
        self.create_categories()
        
        # 펫 타입 생성
        self.create_pet_types()
        
        # 서비스 타입 생성
        self.create_service_types()
        
        # 사용자 생성 (펫 주인, 펫시터)
        self.create_users()
        
        self.stdout.write(self.style.SUCCESS('샘플 데이터 생성 완료!'))
    
    def create_categories(self):
        categories = [
            {
                'name': '산책',
                'description': '반려동물과 함께하는 산책 서비스',
                'icon': 'walk',
                'gradient': 'linear-gradient(135deg, #4CAF50, #8BC34A)'
            },
            {
                'name': '돌봄',
                'description': '집에서 반려동물을 돌봐주는 서비스',
                'icon': 'home',
                'gradient': 'linear-gradient(135deg, #2196F3, #03A9F4)'
            },
            {
                'name': '훈련',
                'description': '반려동물 훈련 서비스',
                'icon': 'training',
                'gradient': 'linear-gradient(135deg, #FF9800, #FFC107)'
            },
            {
                'name': '미용',
                'description': '반려동물 미용 서비스',
                'icon': 'grooming',
                'gradient': 'linear-gradient(135deg, #E91E63, #F48FB1)'
            }
        ]
        
        for category_data in categories:
            Category.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
        
        self.stdout.write(f'카테고리 {len(categories)}개 생성 완료')
    
    def create_pet_types(self):
        pet_types = [
            {'name': '강아지', 'description': '모든 종류의 개', 'icon': 'dog'},
            {'name': '고양이', 'description': '모든 종류의 고양이', 'icon': 'cat'},
            {'name': '토끼', 'description': '토끼와 관련된 돌봄', 'icon': 'rabbit'},
            {'name': '햄스터', 'description': '햄스터 및 설치류', 'icon': 'hamster'},
            {'name': '조류', 'description': '앵무새, 카나리아 등', 'icon': 'bird'},
            {'name': '파충류', 'description': '뱀, 도마뱀, 거북이 등', 'icon': 'reptile'}
        ]
        
        for pet_type_data in pet_types:
            PetType.objects.get_or_create(
                name=pet_type_data['name'],
                defaults=pet_type_data
            )
        
        self.stdout.write(f'펫 타입 {len(pet_types)}개 생성 완료')
    
    def create_service_types(self):
        service_types = [
            {'name': '산책', 'description': '반려동물과 함께 산책하기', 'icon': 'walk'},
            {'name': '방문돌봄', 'description': '집에서 반려동물 돌보기', 'icon': 'home-visit'},
            {'name': '훈련', 'description': '반려동물 훈련 서비스', 'icon': 'training'},
            {'name': '미용', 'description': '반려동물 미용 서비스', 'icon': 'grooming'},
            {'name': '호텔링', 'description': '펫시터 집에서 돌봄', 'icon': 'hotel'},
            {'name': '데이케어', 'description': '낮 시간 동안 돌봄', 'icon': 'daycare'}
        ]
        
        for service_type_data in service_types:
            ServiceType.objects.get_or_create(
                name=service_type_data['name'],
                defaults=service_type_data
            )
        
        self.stdout.write(f'서비스 타입 {len(service_types)}개 생성 완료')
    
    def create_users(self):
        # 펫 주인 생성
        pet_owners = [
            {
                'username': 'petowner1',
                'email': 'petowner1@example.com',
                'password': 'password123',
                'first_name': '민준',
                'last_name': '김',
                'user_type': 'pet_owner',
                'phone_number': '010-1234-5678',
                'address': '서울특별시 강남구 테헤란로 123',
                'bio': '반려견 두 마리와 함께 살고 있습니다.',
                'latitude': 37.5665,
                'longitude': 126.9780
            },
            {
                'username': 'petowner2',
                'email': 'petowner2@example.com',
                'password': 'password123',
                'first_name': '서연',
                'last_name': '이',
                'user_type': 'pet_owner',
                'phone_number': '010-2345-6789',
                'address': '서울특별시 서초구 서초대로 456',
                'bio': '고양이 한 마리의 집사입니다.',
                'latitude': 37.4969,
                'longitude': 127.0278
            },
            {
                'username': 'petowner3',
                'email': 'petowner3@example.com',
                'password': 'password123',
                'first_name': '지우',
                'last_name': '박',
                'user_type': 'pet_owner',
                'phone_number': '010-3456-7890',
                'address': '서울특별시 송파구 올림픽로 789',
                'bio': '토끼와 햄스터를 키우고 있어요.',
                'latitude': 37.5140,
                'longitude': 127.1060
            }
        ]
        
        for owner_data in pet_owners:
            user, created = CustomUser.objects.get_or_create(
                username=owner_data['username'],
                defaults={
                    'email': owner_data['email'],
                    'first_name': owner_data['first_name'],
                    'last_name': owner_data['last_name'],
                    'user_type': owner_data['user_type'],
                    'phone_number': owner_data['phone_number'],
                    'address': owner_data['address'],
                    'bio': owner_data['bio'],
                    'latitude': owner_data['latitude'],
                    'longitude': owner_data['longitude']
                }
            )
            
            if created:
                user.set_password(owner_data['password'])
                user.save()
                
                # 펫 주인 프로필 생성
                profile, _ = PetOwnerProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'emergency_contact': f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}'
                    }
                )
                
                # 선호하는 서비스 타입 추가
                service_types = ServiceType.objects.all()
                profile.preferred_service_types.set(random.sample(list(service_types), random.randint(1, 3)))
                
                # 반려동물 생성
                self.create_pets_for_owner(user)
        
        self.stdout.write(f'펫 주인 {len(pet_owners)}명 생성 완료')
        
        # 펫시터 생성
        pet_sitters = [
            {
                'username': 'petsitter1',
                'email': 'petsitter1@example.com',
                'password': 'password123',
                'first_name': '현우',
                'last_name': '정',
                'user_type': 'pet_sitter',
                'phone_number': '010-4567-8901',
                'address': '서울특별시 마포구 홍대입구역 3번 출구',
                'bio': '3년 경력의 전문 펫시터입니다. 강아지와 고양이 모두 돌봄 가능합니다.',
                'latitude': 37.5585,
                'longitude': 126.9258,
                'experience_years': 3,
                'service_area_radius': 5
            },
            {
                'username': 'petsitter2',
                'email': 'petsitter2@example.com',
                'password': 'password123',
                'first_name': '지민',
                'last_name': '최',
                'user_type': 'pet_sitter',
                'phone_number': '010-5678-9012',
                'address': '서울특별시 용산구 이태원로 123',
                'bio': '동물병원에서 5년간 근무한 경험이 있습니다. 모든 종류의 반려동물을 사랑합니다.',
                'latitude': 37.5384,
                'longitude': 126.9946,
                'experience_years': 5,
                'service_area_radius': 10
            },
            {
                'username': 'petsitter3',
                'email': 'petsitter3@example.com',
                'password': 'password123',
                'first_name': '수진',
                'last_name': '강',
                'user_type': 'pet_sitter',
                'phone_number': '010-6789-0123',
                'address': '서울특별시 강동구 천호대로 456',
                'bio': '반려동물 훈련사 자격증을 보유하고 있습니다. 특히 문제행동 교정에 전문성이 있습니다.',
                'latitude': 37.5492,
                'longitude': 127.1464,
                'experience_years': 2,
                'service_area_radius': 7
            },
            {
                'username': 'petsitter4',
                'email': 'petsitter4@example.com',
                'password': 'password123',
                'first_name': '준호',
                'last_name': '윤',
                'user_type': 'pet_sitter',
                'phone_number': '010-7890-1234',
                'address': '서울특별시 종로구 인사동길 12',
                'bio': '반려견 미용사 자격증을 가지고 있으며, 집에서 미용 서비스도 제공합니다.',
                'latitude': 37.5759,
                'longitude': 126.9860,
                'experience_years': 4,
                'service_area_radius': 8
            },
            {
                'username': 'petsitter5',
                'email': 'petsitter5@example.com',
                'password': 'password123',
                'first_name': '예은',
                'last_name': '한',
                'user_type': 'pet_sitter',
                'phone_number': '010-8901-2345',
                'address': '서울특별시 성북구 성북로 789',
                'bio': '파충류와 조류 전문 펫시터입니다. 특수 동물에 대한 지식이 풍부합니다.',
                'latitude': 37.5926,
                'longitude': 127.0159,
                'experience_years': 6,
                'service_area_radius': 15
            }
        ]
        
        for sitter_data in pet_sitters:
            user, created = CustomUser.objects.get_or_create(
                username=sitter_data['username'],
                defaults={
                    'email': sitter_data['email'],
                    'first_name': sitter_data['first_name'],
                    'last_name': sitter_data['last_name'],
                    'user_type': sitter_data['user_type'],
                    'phone_number': sitter_data['phone_number'],
                    'address': sitter_data['address'],
                    'bio': sitter_data['bio'],
                    'latitude': sitter_data['latitude'],
                    'longitude': sitter_data['longitude']
                }
            )
            
            if created:
                user.set_password(sitter_data['password'])
                user.save()
                
                # 펫시터 프로필 생성
                profile, _ = PetSitterProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'verification_status': 'approved',
                        'experience_years': sitter_data['experience_years'],
                        'service_area_radius': sitter_data['service_area_radius'],
                        'is_available': True,
                        'average_rating': round(random.uniform(4.0, 5.0), 1),
                        'total_reviews': random.randint(5, 50),
                        'response_rate': round(random.uniform(0.8, 1.0), 2),
                        'response_time': random.randint(5, 60)
                    }
                )
                
                # 자격증 이미지 추가
                cert_image, _ = CertificationImage.objects.get_or_create(
                    title=f"{user.last_name}{user.first_name}의 자격증",
                    defaults={
                        'description': '펫시터 자격증'
                    }
                )
                profile.certification_images.add(cert_image)
                
                # 서비스 타입 및 가능한 펫 타입 추가
                service_types = ServiceType.objects.all()
                pet_types = PetType.objects.all()
                
                profile.service_types.set(random.sample(list(service_types), random.randint(2, 4)))
                profile.available_pet_types.set(random.sample(list(pet_types), random.randint(2, 5)))
                
                # 서비스 생성
                self.create_services_for_sitter(user)
                
                # 가용 시간 생성
                self.create_availability_for_sitter(user)
        
        self.stdout.write(f'펫시터 {len(pet_sitters)}명 생성 완료')
    
    def create_pets_for_owner(self, owner):
        pet_types = PetType.objects.all()
        
        # 각 주인당 1-3마리의 반려동물 생성
        num_pets = random.randint(1, 3)
        
        for i in range(num_pets):
            pet_type = random.choice(pet_types)
            gender = random.choice(['M', 'F'])
            
            if pet_type.name == '강아지':
                breeds = ['골든 리트리버', '비숑 프리제', '말티즈', '시바 이누', '웰시 코기', '푸들', '치와와', '불독']
                breed = random.choice(breeds)
                name = random.choice(['초코', '콩이', '몽이', '루시', '보리', '해피', '바둑이', '멍멍이'])
            elif pet_type.name == '고양이':
                breeds = ['페르시안', '샴', '러시안 블루', '스코티시 폴드', '뱅갈', '아비시니안', '노르웨이 숲']
                breed = random.choice(breeds)
                name = random.choice(['나비', '까망이', '야옹이', '치즈', '루나', '모모', '레오', '냥이'])
            elif pet_type.name == '토끼':
                breeds = ['네덜란드 드워프', '미니 렉스', '라이언 헤드', '앙고라']
                breed = random.choice(breeds)
                name = random.choice(['토토', '토순이', '바니', '당근', '눈이', '솜이'])
            else:
                breeds = ['일반종']
                breed = random.choice(breeds)
                name = random.choice(['포포', '방울이', '별이', '하늘이', '구름이'])
            
            UserPet.objects.create(
                owner=owner,
                name=name,
                pet_type=pet_type,
                breed=breed,
                age=random.randint(1, 10),
                gender=gender,
                weight=round(random.uniform(1.0, 30.0), 1),
                description=f"{name}는 {breed} {pet_type.name}입니다. {'그는' if gender == 'M' else '그녀는'} 매우 활발하고 사랑스러운 성격을 가지고 있습니다.",
                medical_conditions=random.choice(['없음', '알러지', '관절염', '치과 문제']) if random.random() < 0.3 else None,
                behavioral_notes=random.choice(['낯가림', '다른 동물과 잘 어울림', '장난기가 많음', '소심함']) if random.random() < 0.5 else None
            )
    
    def create_services_for_sitter(self, sitter):
        service_types = list(sitter.pet_sitter_profile.service_types.all())
        
        for service_type in service_types:
            if service_type.name == '산책':
                price = random.choice([15000, 20000, 25000])
                duration = 60
            elif service_type.name == '방문돌봄':
                price = random.choice([30000, 35000, 40000])
                duration = 120
            elif service_type.name == '훈련':
                price = random.choice([50000, 60000, 70000])
                duration = 90
            elif service_type.name == '미용':
                price = random.choice([40000, 50000, 60000])
                duration = 120
            elif service_type.name == '호텔링':
                price = random.choice([50000, 60000, 70000])
                duration = 1440  # 24시간
            else:  # 데이케어
                price = random.choice([35000, 40000, 45000])
                duration = 480  # 8시간
            
            PetSitterService.objects.create(
                pet_sitter=sitter,
                service_type=service_type,
                price=price,
                duration=duration,
                description=f"{service_type.name} 서비스입니다. {duration//60}시간 동안 진행됩니다.",
                is_available=True
            )
    
    def create_availability_for_sitter(self, sitter):
        # 각 요일마다 가용 시간 설정
        for day in range(7):
            # 50% 확률로 오전 시간대 추가
            if random.random() > 0.5:
                start_time = time(random.randint(8, 10), 0)
                end_time = time(random.randint(11, 13), 0)
                
                PetSitterAvailability.objects.create(
                    pet_sitter=sitter,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time
                )
            
            # 70% 확률로 오후 시간대 추가
            if random.random() > 0.3:
                start_time = time(random.randint(14, 16), 0)
                end_time = time(random.randint(17, 20), 0)
                
                PetSitterAvailability.objects.create(
                    pet_sitter=sitter,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time
                )
