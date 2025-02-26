# hyper_pets_backend/api/serializers.py
from rest_framework import serializers
from .models import Category, Shelter, Hospital, Salon, Pet, AdoptionStory, Event, Support

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ShelterSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    operating_hours = serializers.CharField()

    class Meta:
        model = Shelter
        fields = [
            'id', 'name', 'description', 'address', 'latitude', 'longitude',
            'phone', 'operating_hours', 'type', 'capacity', 'current_occupancy'
        ]
    
    def get_type(self, obj):
        return 'shelter'

class HospitalSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    operating_hours = serializers.CharField()
    specialties = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'description', 'address', 'latitude', 'longitude',
            'phone', 'operating_hours', 'type', 'is_24h', 'specialties'
        ]
    
    def get_type(self, obj):
        return 'hospital'
    
    def get_specialties(self, obj):
        return list(obj.specialties.values_list('name', flat=True)) if obj.specialties.exists() else []

class PetSerializer(serializers.ModelSerializer):
    shelter_name = serializers.CharField(source='shelter.name', read_only=True)

    class Meta:
        model = Pet
        fields = '__all__'

class AdoptionStorySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    pet_name = serializers.CharField(source='pet.name', read_only=True)

    class Meta:
        model = AdoptionStory
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class SupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Support
        fields = '__all__'


class SalonSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    operating_hours = serializers.CharField()

    class Meta:
        model = Salon
        fields = [
            'id', 'name', 'description', 'address', 'latitude', 'longitude',
            'phone', 'operating_hours', 'type'
        ]
    
    def get_type(self, obj):
        return 'salon'