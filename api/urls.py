# hyper_pets_backend/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ShelterViewSet, HospitalViewSet, SalonViewSet,
    PetViewSet, AdoptionStoryViewSet, EventViewSet, SupportViewSet,
    UserViewSet, # Added UserViewSet import
)
from .views import reverse_geocode
from .auth_views import social_login
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# 펫워커 서비스 관련 뷰 임포트
from .pet_worker_views.user_views import (
    CustomUserViewSet, PetOwnerProfileViewSet, PetSitterProfileViewSet
)
from .pet_worker_views.pet_service_views import (
    PetTypeViewSet, ServiceTypeViewSet, UserPetViewSet, PetSitterServiceViewSet
)
from .pet_worker_views.booking_views import (
    BookingViewSet, PaymentViewSet
)
from .pet_worker_views.tracking_views import (
    WalkingTrackViewSet, TrackPointViewSet, WalkingEventViewSet, SafetyAlertViewSet
)
from .pet_worker_views.community_views import (
    ReviewViewSet, MessageViewSet, CommunityPostViewSet, 
    PostImageViewSet, CommentViewSet, PostLikeViewSet
)
from .pet_worker_views.notification_views import NotificationViewSet
from .pet_worker_views.ai_matching_views import (
    AIPetSitterMatchingView, AIServiceRecommendationView
)
# 관리자 보고서 뷰 임포트
from .pet_worker_views.admin_report_views import (
    MonthlyStatsView, ServiceStatsView, LocationStatsView, PetTypeStatsView, SummaryStatsView
)

# 기존 라우터
main_router = DefaultRouter()
main_router.register(r'categories', CategoryViewSet)
main_router.register(r'shelters', ShelterViewSet)
main_router.register(r'hospitals', HospitalViewSet)
main_router.register(r'salons', SalonViewSet)
main_router.register(r'pets', PetViewSet)
main_router.register(r'adoption-stories', AdoptionStoryViewSet)
main_router.register(r'events', EventViewSet)
main_router.register(r'supports', SupportViewSet)
main_router.register(r'users', UserViewSet) # Added UserViewSet registration

# '내 계정' 관련 라우터 (사용자 중심적 엔드포인트)
my_account_router = DefaultRouter()
my_account_router.register(r'pets', UserPetViewSet, basename='my-pets')
my_account_router.register(r'profile/owner', PetOwnerProfileViewSet, basename='my-owner-profile')

# 펫워커 서비스 라우터
pet_worker_router = DefaultRouter()
# 사용자 관련
pet_worker_router.register(r'users', CustomUserViewSet) # pet-worker 컨텍스트 내 사용자 관리 (예: 펫시터 목록 등)
# 펫 및 서비스 관련
pet_worker_router.register(r'pet-types', PetTypeViewSet) # 펫 종류는 워커와 오너 모두에게 필요할 수 있음
pet_worker_router.register(r'service-types', ServiceTypeViewSet)
pet_worker_router.register(r'pet-sitter-services', PetSitterServiceViewSet)
# 예약 및 결제 관련
pet_worker_router.register(r'bookings', BookingViewSet)
pet_worker_router.register(r'payments', PaymentViewSet)
# 위치 추적 관련
pet_worker_router.register(r'walking-tracks', WalkingTrackViewSet)
pet_worker_router.register(r'track-points', TrackPointViewSet)
pet_worker_router.register(r'walking-events', WalkingEventViewSet)
pet_worker_router.register(r'safety-alerts', SafetyAlertViewSet, basename='safety-alerts')
# 커뮤니티 관련
pet_worker_router.register(r'reviews', ReviewViewSet)
pet_worker_router.register(r'messages', MessageViewSet)
pet_worker_router.register(r'community-posts', CommunityPostViewSet)
pet_worker_router.register(r'post-images', PostImageViewSet)
pet_worker_router.register(r'comments', CommentViewSet)
pet_worker_router.register(r'post-likes', PostLikeViewSet)
# 알림 관련
pet_worker_router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    # 기존 URL 패턴
    path('', include(main_router.urls)),
    # '내 계정' 관련 URL 패턴 추가
    path('my/', include(my_account_router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('shelters/nearby/', ShelterViewSet.as_view({'get': 'nearby'}), name='shelter-nearby'),
    path('hospitals/nearby/', HospitalViewSet.as_view({'get': 'nearby'}), name='hospital-nearby'),
    path('salons/nearby/', SalonViewSet.as_view({'get': 'nearby'}), name='salon-nearby'),
    path('supports/nearby/', SupportViewSet.as_view({'get': 'nearby'}), name='support-nearby'),
    
    # 인증 관련 URL 패턴
    path('auth/social-login/', social_login, name='social-login'),
    
    # 펫워커 서비스 URL 패턴
    path('pet-worker/', include(pet_worker_router.urls)),
    
    # AI 매칭 관련 URL 패턴
    path('pet-worker/ai-matching/pet-sitters/', AIPetSitterMatchingView.as_view(), name='ai-pet-sitter-matching'),
    path('pet-worker/ai-matching/services/', AIServiceRecommendationView.as_view(), name='ai-service-recommendation'),
    
    # 안전 알림 관련 URL 패턴
    path('pet-worker/safety-alerts/emergency/', SafetyAlertViewSet.as_view({'post': 'emergency'}), name='safety-emergency'),
    path('pet-worker/safety-alerts/safe-zone/', SafetyAlertViewSet.as_view({'post': 'safe_zone_alert'}), name='safety-safe-zone'),
    path('pet-worker/safety-alerts/inactivity/', SafetyAlertViewSet.as_view({'post': 'inactivity_alert'}), name='safety-inactivity'),
    
    # 관리자 보고서 관련 URL 패턴
    path('admin/reports/monthly-stats/', MonthlyStatsView.as_view(), name='admin-monthly-stats'),
    path('admin/reports/service-stats/', ServiceStatsView.as_view(), name='admin-service-stats'),
    path('admin/reports/location-stats/', LocationStatsView.as_view(), name='admin-location-stats'),
    path('admin/reports/pet-type-stats/', PetTypeStatsView.as_view(), name='admin-pet-type-stats'),
    path('admin/reports/summary-stats/', SummaryStatsView.as_view(), name='admin-summary-stats'),
    
    path('reverse-geocode/', reverse_geocode, name='reverse-geocode'),
]
