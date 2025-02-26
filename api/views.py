# hyper_pets_backend/api/views.py
import math
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Category, Shelter, Hospital, Salon, Pet, AdoptionStory, Event, Support
from .serializers import (
    CategorySerializer, ShelterSerializer, HospitalSerializer, SalonSerializer,
    PetSerializer, AdoptionStorySerializer, EventSerializer, SupportSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ShelterViewSet(viewsets.ModelViewSet):
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer

    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        lat = float(request.query_params.get('lat', 0))
        lng = float(request.query_params.get('lng', 0))
        radius = float(request.query_params.get('radius', 5))  # km
        
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
        )[:20]  # 가까운 20개만 반환
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        lat = float(request.query_params.get('lat', 0))
        lng = float(request.query_params.get('lng', 0))
        radius = float(request.query_params.get('radius', 5))  # km
        
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
        )[:20]  # 가까운 20개만 반환
        
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
    queryset = Support.objects.all().order_by('-created_at')
    serializer_class = SupportSerializer

    def get_queryset(self):
        queryset = Support.objects.all()
        active = self.request.query_params.get('active', None)
        
        if active:
            from django.utils import timezone
            queryset = queryset.filter(
                Q(deadline__isnull=True) | Q(deadline__gte=timezone.now())
            )
        
        return queryset


class SalonViewSet(viewsets.ModelViewSet):
    queryset = Salon.objects.all()
    serializer_class = SalonSerializer

    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        lat = float(request.query_params.get('lat', 0))
        lng = float(request.query_params.get('lng', 0))
        radius = float(request.query_params.get('radius', 5))  # km
        
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
        )[:20]  # 가까운 20개만 반환
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
