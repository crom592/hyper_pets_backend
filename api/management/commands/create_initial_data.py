# hyper_pets_backend/api/management/commands/create_initial_data.py
from django.core.management.base import BaseCommand
from api.models import Category, Shelter, Hospital
from api.models import CustomUser
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates initial data for the application'

    def handle(self, *args, **kwargs):
        # Create superuser
        if not CustomUser.objects.filter(username='admin').exists():
            CustomUser.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Superuser created'))

        # Create categories
        categories_data = [
            {
                'name': '내 주변 유기동물 보호소',
                'description': '가까운 보호소에서 새로운 가족을 만나보세요',
                'icon': 'MapPin',
                'gradient': 'from-blue-500 to-cyan-500',
            },
            {
                'name': '입양 소식',
                'description': '새로운 가족을 만난 아이들의 이야기',
                'icon': 'Heart',
                'gradient': 'from-pink-500 to-rose-500',
            },
            # ... 나머지 카테고리들
        ]

        for cat_data in categories_data:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )

        # Create sample shelters
        shelters_data = [
            {
                'name': '행복한 보호소',
                'address': '서울시 강남구 역삼동 123',
                'latitude': 37.5665,
                'longitude': 126.9780,
                'phone': '02-123-4567',
            },
            # ... 더 많은 보호소 데이터
        ]

        for shelter_data in shelters_data:
            Shelter.objects.get_or_create(
                name=shelter_data['name'],
                defaults=shelter_data
            )

        # Create sample hospitals
        hospitals_data = [
            {
                'name': '24시 동물병원',
                'address': '서울시 강남구 삼성동 456',
                'latitude': 37.5665,
                'longitude': 126.9780,
                'phone': '02-123-4567',
                'is_24h': True,
            },
            # ... 더 많은 병원 데이터
        ]

        for hospital_data in hospitals_data:
            Hospital.objects.get_or_create(
                name=hospital_data['name'],
                defaults=hospital_data
            )

        self.stdout.write(self.style.SUCCESS('Initial data created successfully'))