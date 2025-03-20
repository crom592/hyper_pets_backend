# hyper_pets_backend/api/pet_walker_views/user_views.py
import math
from django.db.models import Q, Avg, Count, F, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from ..models import (CustomUser, PetOwnerProfile, PetSitterProfile, CertificationImage, 
                     PetType, ServiceType, Notification)
from ..serializers import (UserSerializer, PetOwnerProfileSerializer, PetSitterProfileSerializer,
                          CertificationImageSerializer)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_type', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['GET'])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def pet_owners(self, request):
        queryset = self.get_queryset().filter(user_type='pet_owner')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def pet_sitters(self, request):
        queryset = self.get_queryset().filter(user_type='pet_sitter')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PetOwnerProfileViewSet(viewsets.ModelViewSet):
    queryset = PetOwnerProfile.objects.all()
    serializer_class = PetOwnerProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CertificationImageViewSet(viewsets.ModelViewSet):
    queryset = CertificationImage.objects.all()
    serializer_class = CertificationImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(pet_sitter_profile__user=user)
    
    def perform_create(self, serializer):
        pet_sitter_profile = get_object_or_404(PetSitterProfile, user=self.request.user)
        serializer.save(pet_sitter_profile=pet_sitter_profile)


class PetSitterProfileViewSet(viewsets.ModelViewSet):
    queryset = PetSitterProfile.objects.all()
    serializer_class = PetSitterProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['verification_status', 'service_types', 'available_pet_types']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'introduction']
    ordering_fields = ['average_rating', 'total_reviews', 'response_rate']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # 필터링 옵션 처리
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            queryset = queryset.filter(average_rating__gte=float(min_rating))
        
        service_type_id = self.request.query_params.get('service_type', None)
        if service_type_id:
            queryset = queryset.filter(service_types__id=service_type_id)
        
        pet_type_id = self.request.query_params.get('pet_type', None)
        if pet_type_id:
            queryset = queryset.filter(available_pet_types__id=pet_type_id)
        
        # 일반 사용자는 인증된 펫시터만 볼 수 있음
        if not user.is_staff and user.user_type != 'pet_sitter':
            queryset = queryset.filter(verification_status='approved')
        
        # 자신의 프로필만 볼 수 있는 경우
        if user.user_type == 'pet_sitter' and not self.request.query_params.get('all', False):
            queryset = queryset.filter(user=user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, verification_status='pending')
    
    @action(detail=True, methods=['POST'], permission_classes=[IsAdminUser])
    def verify(self, request, pk=None):
        profile = self.get_object()
        status_value = request.data.get('status', 'approved')
        if status_value not in ['approved', 'rejected']:
            return Response({'error': '유효하지 않은 상태입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        profile.verification_status = status_value
        profile.save()
        
        # 알림 생성
        Notification.objects.create(
            user=profile.user,
            type='verification',
            content=f'펫시터 인증이 {"승인" if status_value == "approved" else "거부"}되었습니다.',
            related_id=profile.id
        )
        
        return Response({'status': '인증 상태가 업데이트되었습니다.'})
    
    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        # 위치 기반 검색
        lat = float(request.query_params.get('lat', 0))
        lng = float(request.query_params.get('lng', 0))
        radius = float(request.query_params.get('radius', 5000)) / 1000  # 미터를 킬로미터로 변환
        
        # 위도 1도 = 약 111km, 경도 1도는 위도에 따라 달라짐
        lat_km = 111.0
        lng_km = lat_km * abs(math.cos(math.radians(lat)))
        
        lat_range = radius / lat_km
        lng_range = radius / lng_km
        
        # 사용자 위치 기준으로 필터링
        queryset = self.get_queryset().filter(
            user__latitude__range=(lat - lat_range, lat + lat_range),
            user__longitude__range=(lng - lng_range, lng + lng_range)
        )
        
        # 실제 거리 계산 및 정렬
        queryset = sorted(
            queryset,
            key=lambda x: (
                (x.user.latitude - lat) ** 2 + 
                (x.user.longitude - lng) ** 2
            ) ** 0.5
        )[:30]  # 가까운 30개만 반환
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
