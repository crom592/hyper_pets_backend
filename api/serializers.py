# hyper_pets_backend/api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (Category, Shelter, Hospital, Salon, Pet, AdoptionStory, Event, Support,
                    CustomUser, PetOwnerProfile, PetSitterProfile, CertificationImage, PetType,
                    ServiceType, UserPet, PetSitterService, PetSitterAvailability, Booking,
                    Payment, WalkingTrack, TrackPoint, WalkingEvent, Review, Message,
                    CommunityPost, PostImage, Comment, PostLike, Notification,Region)

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'
        
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
    regions = RegionSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Support
        fields = '__all__'
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # dday 계산 로직 추가
        if instance.deadline:
            from django.utils import timezone
            today = timezone.now().date()
            data['dday'] = (instance.deadline - today).days
        return data

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


# 펫워커 서비스 시리얼라이저
class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    marketing_agree = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'user_type', 
            'phone_number', 'address', 'profile_image', 'bio', 'latitude', 'longitude', 
            'date_joined', 'password', 'name', 'marketing_agree'
        ]
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False, 'allow_blank': True, 'read_only': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }


class PetOwnerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    preferred_service_types = serializers.PrimaryKeyRelatedField(many=True, queryset=ServiceType.objects.all())
    
    class Meta:
        model = PetOwnerProfile
        fields = '__all__'


class CertificationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationImage
        fields = '__all__'


class PetSitterProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    certification_images = CertificationImageSerializer(many=True, read_only=True)
    service_types = serializers.PrimaryKeyRelatedField(many=True, queryset=ServiceType.objects.all())
    available_pet_types = serializers.PrimaryKeyRelatedField(many=True, queryset=PetType.objects.all())
    price = serializers.SerializerMethodField()
    
    class Meta:
        model = PetSitterProfile
        fields = '__all__'
        read_only_fields = ['verification_status', 'average_rating', 'total_reviews', 'response_rate', 'response_time']
    
    def get_price(self, obj):
        # 펫시터의 서비스 중 가장 낮은 가격 반환
        services = obj.user.services.filter(is_available=True)
        if services.exists():
            return services.order_by('price').first().price
        return None


class PetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetType
        fields = '__all__'


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = '__all__'


class UserPetSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    pet_type = PetTypeSerializer(read_only=True)
    pet_type_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=PetType.objects.all(), source='pet_type')
    
    class Meta:
        model = UserPet
        fields = '__all__'


class PetSitterServiceSerializer(serializers.ModelSerializer):
    pet_sitter = UserSerializer(read_only=True)
    service_type = ServiceTypeSerializer(read_only=True)
    service_type_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=ServiceType.objects.all(), source='service_type')
    
    class Meta:
        model = PetSitterService
        fields = '__all__'


class PetSitterAvailabilitySerializer(serializers.ModelSerializer):
    pet_sitter = UserSerializer(read_only=True)
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = PetSitterAvailability
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    pet_owner = UserSerializer(read_only=True)
    pet_sitter = UserSerializer(read_only=True)
    service = PetSitterServiceSerializer(read_only=True)
    pets = UserPetSerializer(many=True, read_only=True)
    pet_ids = serializers.PrimaryKeyRelatedField(many=True, write_only=True, queryset=UserPet.objects.all(), source='pets')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['booking_id', 'status', 'total_price']


class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['payment_id', 'status', 'transaction_id', 'payment_date']


class TrackPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackPoint
        fields = '__all__'


class WalkingEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = WalkingEvent
        fields = '__all__'


class WalkingTrackSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    track_points = TrackPointSerializer(many=True, read_only=True)
    events = WalkingEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = WalkingTrack
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    booking = BookingSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['is_read']


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__'


class CommunityPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CommunityPost
        fields = '__all__'
        read_only_fields = ['view_count', 'like_count']
    
    def get_comment_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    post = CommunityPostSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = '__all__'
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class PostLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = CommunityPostSerializer(read_only=True)
    
    class Meta:
        model = PostLike
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['is_read']