"""hyper_pets_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# hyper_pets_backend/hyper_pets_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'shelters', views.ShelterViewSet)
router.register(r'hospitals', views.HospitalViewSet)
router.register(r'salons', views.SalonViewSet)
router.register(r'pets', views.PetViewSet)
router.register(r'adoption-stories', views.AdoptionStoryViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'supports', views.SupportViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)