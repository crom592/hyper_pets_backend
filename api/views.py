# hyper_pets_backend/api/views.py
import math,os
import requests
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    Category, Shelter, Hospital, Salon, Pet, AdoptionStory, Event, Support,
    CustomUser
)

from .serializers import (
    CategorySerializer, ShelterSerializer, HospitalSerializer, SalonSerializer,
    PetSerializer, AdoptionStorySerializer, EventSerializer, SupportSerializer,
    UserSerializer
)

User = get_user_model()

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
    
    @action(detail=False, methods=['GET'])
    def nearby(self, request):
        """위치 기반으로 주변 지원 정책을 검색합니다."""
        # 위치 정보가 있는 지원 정책만 필터링
        base_queryset = self.get_queryset().filter(
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        # 바운딩 박스 파라미터 확인
        if all(param in request.query_params for param in ['startX', 'startY', 'endX', 'endY']):
            # 바운딩 박스 접근법
            start_x = float(request.query_params.get('startX'))
            start_y = float(request.query_params.get('startY'))
            end_x = float(request.query_params.get('endX'))
            end_y = float(request.query_params.get('endY'))
            
            # 바운딩 박스 내의 지원 정책 필터링
            queryset = base_queryset.filter(
                latitude__range=(min(start_y, end_y), max(start_y, end_y)),
                longitude__range=(min(start_x, end_x), max(start_x, end_x))
            )
            
            # 거리 계산을 위한 중심점
            lat = float(request.query_params.get('lat', (start_y + end_y) / 2))
            lng = float(request.query_params.get('lng', (start_x + end_x) / 2))
            
        else:
            # 반경 기반 검색 (대체 방법)
            lat = float(request.query_params.get('lat', 0))
            lng = float(request.query_params.get('lng', 0))
            radius = float(request.query_params.get('radius', 5000)) / 1000  # 미터에서 km로 변환
            
            # 위도 1도 = 약 111km, 경도 1도는 위도에 따라 달라짐
            lat_km = 111.0
            lng_km = lat_km * abs(math.cos(math.radians(lat)))
            
            lat_range = radius / lat_km
            lng_range = radius / lng_km
            
            queryset = base_queryset.filter(
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
        )[:30]  # 가까운 30개만 반환
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'login']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            
            first_name = ""
            last_name = ""
            
            # Get 'name' from validated_data, default to empty string, then strip whitespace
            provided_name = validated_data.get('name', '').strip()

            if provided_name: # If there's a non-empty name after stripping
                name_parts = provided_name.split(' ', 1)
                first_name = name_parts[0]
                if len(name_parts) > 1:
                    last_name = name_parts[1]
            else: # No name provided, or it was empty/whitespace
                # Use the part of the email before '@' as first_name
                email_username_part = validated_data.get('email').split('@')[0]
                first_name = email_username_part
                # last_name remains "" by default

            try:
                user = CustomUser.objects.create_user(
                    username=validated_data.get('email'), # Use email as the username for the system
                    email=validated_data.get('email'),
                    password=validated_data.get('password'),
                    first_name=first_name,
                    last_name=last_name,
                    user_type=validated_data.get('user_type', 'pet_owner')
                )
                # Store marketing_agree if provided (and if model field exists)
                # if 'marketing_agree' in validated_data and hasattr(user, 'marketing_agree'):
                # user.marketing_agree = validated_data['marketing_agree']
                # user.save(update_fields=['marketing_agree'])

                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        print(f"--- Login attempt ---") # Logging
        print(f"Email: {email}") # Logging
        # Avoid printing password directly in production logs for security
        print(f"Password received: {'yes' if password else 'no'}") # Logging 

        user = authenticate(request, username=email, password=password)
        print(f"Authenticate result: {'User object' if user else 'None'}") # Logging

        if user:
            refresh = RefreshToken.for_user(user)
            print(f"Login successful for: {user.email}") # Logging
            print(f"---------------------") # Logging
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        print(f"Login failed for email: {email}") # Logging
        print(f"---------------------") # Logging
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get', 'patch'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            # Exclude fields that should not be updated here (e.g., password, email/username typically)
            # For password changes, create a separate dedicated endpoint.
            # For email/username, it's often restricted or handled with extra verification.
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                # Prevent username/email from being updated directly via this endpoint if desired
                # For example, if 'username' or 'email' is in request.data, you might pop it or ignore it.
                # For now, we rely on serializer's read_only/extra_kwargs for username.
                # If email is part of UserSerializer.Meta.fields and not read_only, it could be updated.
                # Let's make email read_only for updates for safety for now.
                if 'email' in serializer.validated_data:
                    # Or handle it if you want to allow email change with verification
                    return Response({'error': 'Email cannot be changed via this endpoint.'}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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