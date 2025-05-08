# hyper_pets_backend/api/pet_worker_views/ai_matching_views.py
import math
from django.db.models import Q, Avg, Count, F, Sum, Case, When, Value, FloatField
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, views
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import (CustomUser, PetOwnerProfile, PetSitterProfile, UserPet, 
                     PetSitterService, ServiceType, PetType, Review)
from ..serializers import PetSitterProfileSerializer


class AIPetSitterMatchingView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        # 사용자가 펫 주인인지 확인
        if request.user.user_type != 'pet_owner':
            return Response({'error': '펫 주인만 이용할 수 있는 서비스입니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 요청 데이터 가져오기
        pet_ids = request.data.get('pet_ids', [])
        service_type_id = request.data.get('service_type')
        location = request.data.get('location', {})
        preferred_date = request.data.get('preferred_date')
        preferred_time = request.data.get('preferred_time')
        special_requirements = request.data.get('special_requirements', '')
        
        # 필수 데이터 확인
        if not pet_ids or not service_type_id:
            return Response({'error': '반려동물과 서비스 타입은 필수 항목입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 위치 정보 확인
        lat = location.get('latitude', 0)
        lng = location.get('longitude', 0)
        
        # 반려동물 정보 가져오기
        pets = UserPet.objects.filter(id__in=pet_ids, owner=request.user)
        if not pets.exists():
            return Response({'error': '유효한 반려동물 정보가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 반려동물 타입 목록
        pet_types = list(pets.values_list('pet_type_id', flat=True).distinct())
        
        # 서비스 타입 확인
        service_type = get_object_or_404(ServiceType, id=service_type_id)
        
        # 기본 필터링 조건
        # 1. 인증된 펫시터만
        # 2. 해당 서비스 타입을 제공하는 펫시터
        # 3. 해당 반려동물 타입을 케어할 수 있는 펫시터
        pet_sitters = PetSitterProfile.objects.filter(
            verification_status='approved',
            service_types__id=service_type_id,
            available_pet_types__id__in=pet_types
        ).distinct()
        
        # 위치 기반 필터링 (반경 5km 이내)
        if lat and lng:
            radius = 5  # 5km 반경
            lat_km = 111.0
            lng_km = lat_km * abs(math.cos(math.radians(lat)))
            
            lat_range = radius / lat_km
            lng_range = radius / lng_km
            
            pet_sitters = pet_sitters.filter(
                user__latitude__range=(lat - lat_range, lat + lat_range),
                user__longitude__range=(lng - lng_range, lng + lng_range)
            )
        
        # 점수 계산을 위한 어노테이션 추가
        pet_sitters = pet_sitters.annotate(
            # 1. 평점 점수 (50%)
            rating_score=Case(
                When(average_rating__gte=4.5, then=Value(50.0)),
                When(average_rating__gte=4.0, then=Value(45.0)),
                When(average_rating__gte=3.5, then=Value(40.0)),
                When(average_rating__gte=3.0, then=Value(35.0)),
                When(average_rating__gte=2.5, then=Value(30.0)),
                When(average_rating__gte=2.0, then=Value(25.0)),
                When(average_rating__gte=1.5, then=Value(20.0)),
                When(average_rating__gte=1.0, then=Value(15.0)),
                default=Value(10.0),
                output_field=FloatField()
            ),
            
            # 2. 리뷰 수 점수 (20%)
            review_count_score=Case(
                When(total_reviews__gte=50, then=Value(20.0)),
                When(total_reviews__gte=30, then=Value(18.0)),
                When(total_reviews__gte=20, then=Value(16.0)),
                When(total_reviews__gte=10, then=Value(14.0)),
                When(total_reviews__gte=5, then=Value(12.0)),
                When(total_reviews__gte=1, then=Value(10.0)),
                default=Value(5.0),
                output_field=FloatField()
            ),
            
            # 3. 응답률 점수 (15%)
            response_score=Case(
                When(response_rate__gte=0.9, then=Value(15.0)),
                When(response_rate__gte=0.8, then=Value(13.0)),
                When(response_rate__gte=0.7, then=Value(11.0)),
                When(response_rate__gte=0.6, then=Value(9.0)),
                When(response_rate__gte=0.5, then=Value(7.0)),
                default=Value(5.0),
                output_field=FloatField()
            ),
            
            # 4. 응답 시간 점수 (15%)
            response_time_score=Case(
                When(response_time__lte=10, then=Value(15.0)),
                When(response_time__lte=30, then=Value(13.0)),
                When(response_time__lte=60, then=Value(11.0)),
                When(response_time__lte=120, then=Value(9.0)),
                When(response_time__lte=240, then=Value(7.0)),
                default=Value(5.0),
                output_field=FloatField()
            )
        )
        
        # 총점 계산 및 정렬
        pet_sitters = pet_sitters.annotate(
            total_score=F('rating_score') + F('review_count_score') + 
                       F('response_score') + F('response_time_score')
        ).order_by('-total_score')
        
        # 거리 계산 및 정렬 (위치 정보가 있는 경우)
        if lat and lng:
            pet_sitters = sorted(
                pet_sitters,
                key=lambda x: (
                    # 거리 가중치 (가까울수록 점수 높음)
                    x.total_score - (
                        ((x.user.latitude - lat) ** 2 + (x.user.longitude - lng) ** 2) ** 0.5 * 2
                    )
                ),
                reverse=True
            )
        
        # 상위 5명만 추천
        recommended_sitters = pet_sitters[:5]
        
        # 결과 직렬화
        serializer = PetSitterProfileSerializer(recommended_sitters, many=True)
        
        # 추천 이유 추가
        recommendations = []
        for i, sitter in enumerate(recommended_sitters):
            recommendation = serializer.data[i]
            
            # 추천 이유 생성
            reasons = []
            if sitter.average_rating >= 4.5:
                reasons.append("최고 평점의 펫시터")
            elif sitter.average_rating >= 4.0:
                reasons.append("높은 평점의 펫시터")
            
            if sitter.total_reviews >= 30:
                reasons.append("많은 리뷰를 받은 경험 많은 펫시터")
            
            if sitter.response_rate >= 0.9:
                reasons.append("빠른 응답률을 가진 펫시터")
            
            if sitter.response_time <= 10:
                reasons.append("빠른 응답 시간을 가진 펫시터")
            
            # 펫 타입 전문가 여부
            pet_type_names = []
            for pet in pets:
                pet_type_name = pet.pet_type.name
                if pet_type_name not in pet_type_names:
                    pet_type_names.append(pet_type_name)
            
            if len(pet_type_names) == 1:
                reasons.append(f"{pet_type_names[0]} 케어 전문가")
            else:
                reasons.append(f"{', '.join(pet_type_names)} 케어 가능한 펫시터")
            
            recommendation['reasons'] = reasons
            recommendations.append(recommendation)
        
        return Response({
            'recommendations': recommendations,
            'request_details': {
                'pets': [{'id': pet.id, 'name': pet.name, 'type': pet.pet_type.name} for pet in pets],
                'service_type': service_type.name,
                'location': location,
                'preferred_date': preferred_date,
                'preferred_time': preferred_time,
                'special_requirements': special_requirements
            }
        })


class AIServiceRecommendationView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        # 사용자가 펫 주인인지 확인
        if request.user.user_type != 'pet_owner':
            return Response({'error': '펫 주인만 이용할 수 있는 서비스입니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 요청 데이터 가져오기
        pet_ids = request.data.get('pet_ids', [])
        
        # 필수 데이터 확인
        if not pet_ids:
            return Response({'error': '반려동물 정보는 필수 항목입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 반려동물 정보 가져오기
        pets = UserPet.objects.filter(id__in=pet_ids, owner=request.user)
        if not pets.exists():
            return Response({'error': '유효한 반려동물 정보가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 반려동물 특성 분석
        pet_types = list(pets.values_list('pet_type_id', flat=True).distinct())
        pet_sizes = list(pets.values_list('size', flat=True).distinct())
        pet_ages = list(pets.values_list('age', flat=True))
        pet_has_special_needs = any(pet.special_needs for pet in pets)
        
        # 서비스 타입 추천 로직
        recommended_services = []
        all_services = ServiceType.objects.all()
        
        # 1. 산책 서비스 추천 (강아지, 중소형)
        dog_type = PetType.objects.filter(name__icontains='강아지').first()
        if dog_type and dog_type.id in pet_types and 'large' not in pet_sizes:
            walking_service = all_services.filter(name__icontains='산책').first()
            if walking_service:
                recommended_services.append({
                    'id': walking_service.id,
                    'name': walking_service.name,
                    'description': walking_service.description,
                    'reason': '반려견의 건강과 행복을 위한 정기적인 산책 서비스를 추천합니다.'
                })
        
        # 2. 방문 돌봄 서비스 추천 (모든 반려동물)
        visit_service = all_services.filter(name__icontains='방문').first()
        if visit_service:
            recommended_services.append({
                'id': visit_service.id,
                'name': visit_service.name,
                'description': visit_service.description,
                'reason': '반려동물이 익숙한 환경에서 스트레스 없이 케어받을 수 있는 방문 돌봄 서비스를 추천합니다.'
            })
        
        # 3. 특별 케어 서비스 추천 (특수 케어 필요 시)
        if pet_has_special_needs:
            special_service = all_services.filter(name__icontains='특별').first()
            if special_service:
                recommended_services.append({
                    'id': special_service.id,
                    'name': special_service.name,
                    'description': special_service.description,
                    'reason': '특별한 케어가 필요한 반려동물을 위한 맞춤형 서비스를 추천합니다.'
                })
        
        # 4. 장기 돌봄 서비스 추천
        long_term_service = all_services.filter(name__icontains='장기').first()
        if long_term_service:
            recommended_services.append({
                'id': long_term_service.id,
                'name': long_term_service.name,
                'description': long_term_service.description,
                'reason': '여행이나 출장 시 안심하고 맡길 수 있는 장기 돌봄 서비스를 추천합니다.'
            })
        
        # 5. 훈련 서비스 추천 (어린 강아지)
        young_dogs = False
        if dog_type and dog_type.id in pet_types:
            for pet in pets:
                if pet.pet_type_id == dog_type.id and pet.age <= 3:
                    young_dogs = True
                    break
        
        if young_dogs:
            training_service = all_services.filter(name__icontains='훈련').first()
            if training_service:
                recommended_services.append({
                    'id': training_service.id,
                    'name': training_service.name,
                    'description': training_service.description,
                    'reason': '어린 강아지의 사회화와 기본 훈련을 위한 훈련 서비스를 추천합니다.'
                })
        
        return Response({
            'recommendations': recommended_services,
            'pets': [{'id': pet.id, 'name': pet.name, 'type': pet.pet_type.name, 'age': pet.age} for pet in pets]
        })
