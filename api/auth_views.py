# hyper_pets_backend/api/auth_views.py
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.db import transaction
import jwt
import datetime
import os

from .models import CustomUser

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def social_login(request):
    """
    소셜 로그인 처리 API
    
    요청 데이터:
    {
        "provider": "google|kakao|naver",
        "providerId": "소셜 제공자의 사용자 ID",
        "email": "사용자 이메일",
        "name": "사용자 이름",
        "image": "프로필 이미지 URL (선택)"
    }
    """
    provider = request.data.get('provider')
    provider_id = request.data.get('providerId')
    email = request.data.get('email')
    name = request.data.get('name')
    image = request.data.get('image', '')
    
    if not provider or not provider_id or not email:
        return Response({
            'error': '필수 정보가 누락되었습니다. provider, providerId, email은 필수입니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 이메일로 사용자 찾기
    try:
        user = User.objects.get(email=email)
        # 소셜 로그인 정보 업데이트
        user.social_provider = provider
        user.social_provider_id = provider_id
        if image:
            user.profile_image = image
        user.save()
    except User.DoesNotExist:
        # 새 사용자 생성
        with transaction.atomic():
            # 이름을 공백으로 분리하여 first_name과 last_name 설정
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # 사용자 생성
            user = User.objects.create(
                username=email,  # 이메일을 사용자명으로 사용
                email=email,
                first_name=first_name,
                last_name=last_name,
                social_provider=provider,
                social_provider_id=provider_id,
                profile_image=image if image else '',
                user_type='pet_owner',  # 기본값으로 pet_owner 설정
                is_active=True
            )
    
    # JWT 토큰 생성
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)  # 30일 유효
    }
    
    token = jwt.encode(payload, os.getenv('DJANGO_SECRET_KEY', 'your-secret-key-here'), algorithm='HS256')
    
    return Response({
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}".strip(),
            'profile_image': user.profile_image,
            'user_type': user.user_type
        }
    })
