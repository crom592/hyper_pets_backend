# hyper_pets_backend/api/views.py
import math,os
import requests
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from .models import (Category, Shelter, Hospital, Salon, Pet, AdoptionStory, Event, Support,)

from .serializers import (
    CategorySerializer, ShelterSerializer, HospitalSerializer, SalonSerializer,
    PetSerializer, AdoptionStorySerializer, EventSerializer, SupportSerializer,
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ShelterViewSet(viewsets.ModelViewSet):
    queryset = Shelter.objects.all().order_by('name')
    serializer_class = ShelterSerializer

    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        # Check if bounding box parameters are provided
        if all(param in request.query_params for param in ['startX', 'startY', 'endX', 'endY']):
            # Bounding box approach (similar to Hogangnono)
            start_x = float(request.query_params.get('startX'))
            start_y = float(request.query_params.get('startY'))
            end_x = float(request.query_params.get('endX'))
            end_y = float(request.query_params.get('endY'))
            
            # Get locations within the bounding box
            queryset = self.get_queryset().filter(
                latitude__range=(min(start_y, end_y), max(start_y, end_y)),
                longitude__range=(min(start_x, end_x), max(start_x, end_x))
            )
            
            # Get center point for distance calculation
            lat = float(request.query_params.get('lat', (start_y + end_y) / 2))
            lng = float(request.query_params.get('lng', (start_x + end_x) / 2))
            
        else:
            # Fallback to radius-based search
            lat = float(request.query_params.get('lat', 0))
            lng = float(request.query_params.get('lng', 0))
            radius = float(request.query_params.get('radius', 5000)) / 1000  # Convert meters to km
            
            # 위도 1도 = 약 111km, 경도 1도는 위도에 따라 달라짐
            lat_km = 111.0
            lng_km = lat_km * abs(math.cos(math.radians(lat)))
            
            lat_range = radius / lat_km
            lng_range = radius / lng_km
            
            queryset = self.get_queryset().filter(
                latitude__range=(lat - lat_range, lat + lat_range),
                longitude__range=(lng - lng_range, lng + lng_range)
            )
        
        # 실제 거리 계산 및 정렬
        queryset = sorted(
            queryset,
            key=lambda x: (
                (x.latitude - lat) ** 2 + 
                (x.longitude - lng) ** 2
            ) ** 0.5
        )[:30]  # 가까운 30개만 반환 (증가)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all().order_by('name')
    serializer_class = HospitalSerializer

    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        # Check if bounding box parameters are provided
        if all(param in request.query_params for param in ['startX', 'startY', 'endX', 'endY']):
            # Bounding box approach (similar to Hogangnono)
            start_x = float(request.query_params.get('startX'))
            start_y = float(request.query_params.get('startY'))
            end_x = float(request.query_params.get('endX'))
            end_y = float(request.query_params.get('endY'))
            
            # Get locations within the bounding box
            queryset = self.get_queryset().filter(
                latitude__range=(min(start_y, end_y), max(start_y, end_y)),
                longitude__range=(min(start_x, end_x), max(start_x, end_x))
            )
            
            # Get center point for distance calculation
            lat = float(request.query_params.get('lat', (start_y + end_y) / 2))
            lng = float(request.query_params.get('lng', (start_x + end_x) / 2))
            
        else:
            # Fallback to radius-based search
            lat = float(request.query_params.get('lat', 0))
            lng = float(request.query_params.get('lng', 0))
            radius = float(request.query_params.get('radius', 5000)) / 1000  # Convert meters to km
            
            # 위도 1도 = 약 111km, 경도 1도는 위도에 따라 달라짐
            lat_km = 111.0
            lng_km = lat_km * abs(math.cos(math.radians(lat)))
            
            lat_range = radius / lat_km
            lng_range = radius / lng_km
            
            queryset = self.get_queryset().filter(
                latitude__range=(lat - lat_range, lat + lat_range),
                longitude__range=(lng - lng_range, lng + lng_range)
            )
        
        # 실제 거리 계산 및 정렬
        queryset = sorted(
            queryset,
            key=lambda x: (
                (x.latitude - lat) ** 2 + 
                (x.longitude - lng) ** 2
            ) ** 0.5
        )[:30]  # 가까운 30개만 반환 (증가)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer

    def get_queryset(self):
        queryset = Pet.objects.all()
        species = self.request.query_params.get('species', None)
        status = self.request.query_params.get('status', None)
        shelter_id = self.request.query_params.get('shelter', None)

        if species:
            queryset = queryset.filter(species=species)
        if status:
            queryset = queryset.filter(status=status)
        if shelter_id:
            queryset = queryset.filter(shelter_id=shelter_id)

        return queryset

class AdoptionStoryViewSet(viewsets.ModelViewSet):
    queryset = AdoptionStory.objects.all().order_by('-created_at')
    serializer_class = AdoptionStorySerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()
        upcoming = self.request.query_params.get('upcoming', None)
        
        if upcoming:
            from django.utils import timezone
            queryset = queryset.filter(date__gte=timezone.now())
        
        return queryset

class SupportViewSet(viewsets.ModelViewSet):
    queryset = Support.objects.all()
    serializer_class = SupportSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        region = self.request.query_params.get('region', None)
        status = self.request.query_params.get('status', None)
        support_type = self.request.query_params.get('type', None)
        
        if region:
            queryset = queryset.filter(regions__code=region)
        if status:
            queryset = queryset.filter(status=status)
        if support_type:
            queryset = queryset.filter(support_type=support_type)
            
        return queryset

class SalonViewSet(viewsets.ModelViewSet):
    queryset = Salon.objects.all().order_by('name')
    serializer_class = SalonSerializer

    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        # Check if bounding box parameters are provided
        if all(param in request.query_params for param in ['startX', 'startY', 'endX', 'endY']):
            # Bounding box approach (similar to Hogangnono)
            start_x = float(request.query_params.get('startX'))
            start_y = float(request.query_params.get('startY'))
            end_x = float(request.query_params.get('endX'))
            end_y = float(request.query_params.get('endY'))
            
            # Get locations within the bounding box
            queryset = self.get_queryset().filter(
                latitude__range=(min(start_y, end_y), max(start_y, end_y)),
                longitude__range=(min(start_x, end_x), max(start_x, end_x))
            )
            
            # Get center point for distance calculation
            lat = float(request.query_params.get('lat', (start_y + end_y) / 2))
            lng = float(request.query_params.get('lng', (start_x + end_x) / 2))
            
        else:
            # Fallback to radius-based search
            lat = float(request.query_params.get('lat', 0))
            lng = float(request.query_params.get('lng', 0))
            radius = float(request.query_params.get('radius', 5000)) / 1000  # Convert meters to km
            
            # 위도 1도 = 약 111km, 경도 1도는 위도에 따라 달라짐
            lat_km = 111.0
            lng_km = lat_km * abs(math.cos(math.radians(lat)))
            
            lat_range = radius / lat_km
            lng_range = radius / lng_km
            
            queryset = self.get_queryset().filter(
                latitude__range=(lat - lat_range, lat + lat_range),
                longitude__range=(lng - lng_range, lng + lng_range)
            )
        
        # 실제 거리 계산 및 정렬
        queryset = sorted(
            queryset,
            key=lambda x: (
                (x.latitude - lat) ** 2 + 
                (x.longitude - lng) ** 2
            ) ** 0.5
        )[:30]  # 가까운 30개만 반환 (증가)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def reverse_geocode(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    if not lat or not lng:
        return JsonResponse({'error': 'Missing lat or lng'}, status=400)

    NAVER_API_URL = 'https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc'
    headers = {
        'X-NCP-APIGW-API-KEY-ID': os.getenv('NAVER_CLIENT_ID'),
        'X-NCP-APIGW-API-KEY': os.getenv('NAVER_CLIENT_SECRET'),
    }
    params = {
        'coords': f'{lng},{lat}',
        'output': 'json',
        'orders': 'legalcode,admcode',
    }

    try:
        res = requests.get(NAVER_API_URL, headers=headers, params=params)
        return JsonResponse(res.json(), status=res.status_code)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)