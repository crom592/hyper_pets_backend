# hyper_pets_backend/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ShelterViewSet, HospitalViewSet, SalonViewSet,
    PetViewSet, AdoptionStoryViewSet, EventViewSet, SupportViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'shelters', ShelterViewSet)
router.register(r'hospitals', HospitalViewSet)
router.register(r'salons', SalonViewSet)
router.register(r'pets', PetViewSet)
router.register(r'adoption-stories', AdoptionStoryViewSet)
router.register(r'events', EventViewSet)
router.register(r'supports', SupportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('shelters/nearby/', ShelterViewSet.as_view({'get': 'nearby'}), name='shelter-nearby'),
    path('hospitals/nearby/', HospitalViewSet.as_view({'get': 'nearby'}), name='hospital-nearby'),
    path('salons/nearby/', SalonViewSet.as_view({'get': 'nearby'}), name='salon-nearby'),
]
