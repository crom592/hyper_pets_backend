# hyper_pets_backend/api/admin.py
from django.contrib import admin
from .models import Category, Shelter, Hospital, Pet, AdoptionStory, Event, Support

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'created_at')
    search_fields = ('name', 'address', 'phone')

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'is_24h', 'created_at')
    search_fields = ('name', 'address', 'phone')
    list_filter = ('is_24h',)

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'gender', 'status', 'shelter')
    search_fields = ('name', 'breed', 'description')
    list_filter = ('species', 'status', 'gender')

@admin.register(AdoptionStory)
class AdoptionStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'pet', 'author', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'created_at')
    search_fields = ('title', 'description', 'location')
    list_filter = ('date',)

@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline', 'created_at')
    search_fields = ('title', 'description', 'requirements')
    list_filter = ('deadline',)