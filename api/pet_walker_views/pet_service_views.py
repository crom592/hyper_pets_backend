# hyper_pets_backend/api/pet_walker_views/pet_service_views.py
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from ..models import (PetType, ServiceType, UserPet, PetSitterService, PetSitterAvailability)
from ..serializers import (PetTypeSerializer, ServiceTypeSerializer, UserPetSerializer, 
                          PetSitterServiceSerializer, PetSitterAvailabilitySerializer)


class PetTypeViewSet(viewsets.ModelViewSet):
    queryset = PetType.objects.all()
    serializer_class = PetTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ServiceTypeViewSet(viewsets.ModelViewSet):
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class UserPetViewSet(viewsets.ModelViewSet):
    queryset = UserPet.objects.all()
    serializer_class = UserPetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['pet_type', 'size', 'age']
    search_fields = ['name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(owner=user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PetSitterServiceViewSet(viewsets.ModelViewSet):
    queryset = PetSitterService.objects.all()
    serializer_class = PetSitterServiceSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service_type', 'is_active']
    search_fields = ['description']
    ordering_fields = ['price']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # 서비스 타입 필터링
        service_type_id = self.request.query_params.get('service_type', None)
        if service_type_id:
            queryset = queryset.filter(service_type_id=service_type_id)
        
        # 가격 범위 필터링
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=float(max_price))
        
        # 일반 사용자는 활성화된 서비스만 볼 수 있음
        if not user.is_authenticated:
            # 인증되지 않은 사용자는 활성화된 서비스와 승인된 펫시터의 서비스만 볼 수 있음
            queryset = queryset.filter(is_active=True)
            queryset = queryset.filter(pet_sitter__petsitterprofile__verification_status='approved')
        elif not user.is_staff and getattr(user, 'user_type', '') != 'pet_sitter':
            queryset = queryset.filter(is_active=True)
            queryset = queryset.filter(pet_sitter__petsitterprofile__verification_status='approved')
        
        # 자신의 서비스만 볼 수 있는 경우
        if user.user_type == 'pet_sitter' and not self.request.query_params.get('all', False):
            queryset = queryset.filter(pet_sitter=user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(pet_sitter=self.request.user)


class PetSitterAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = PetSitterAvailability.objects.all()
    serializer_class = PetSitterAvailabilitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['day_of_week', 'pet_sitter']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        
        # 펫시터는 자신의 가용성만 볼 수 있음
        if user.user_type == 'pet_sitter':
            return self.queryset.filter(pet_sitter=user)
        
        # 펫 주인은 모든 펫시터의 가용성을 볼 수 있음
        return self.queryset
    
    def perform_create(self, serializer):
        serializer.save(pet_sitter=self.request.user)
