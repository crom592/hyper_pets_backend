# hyper_pets_backend/api/models.py
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone

class Region(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    level = models.PositiveSmallIntegerField()
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return self.name
    
    def get_full_name(self):
        names = [self.name]
        current = self
        while current.parent:
            current = current.parent
            names.append(current.name)
        return ' '.join(reversed(names))
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    gradient = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Specialty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Specialties"

    def __str__(self):
        return self.name

class Shelter(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    operating_hours = models.CharField(max_length=200, blank=True)
    capacity = models.IntegerField(default=0)
    current_occupancy = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    operating_hours = models.CharField(max_length=200, blank=True)
    is_24h = models.BooleanField(default=False)
    specialties = models.ManyToManyField(Specialty, related_name='hospitals', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Salon(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    operating_hours = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'salons'
        ordering = ['name']

    def __str__(self):
        return self.name

class Pet(models.Model):
    SPECIES_CHOICES = [
        ('dog', '강아지'),
        ('cat', '고양이'),
        ('other', '기타')
    ]
    
    STATUS_CHOICES = [
        ('available', '입양가능'),
        ('pending', '입양진행중'),
        ('adopted', '입양완료')
    ]
    
    GENDER_CHOICES = [
        ('M', '수컷'),
        ('F', '암컷')
    ]

    name = models.CharField(max_length=100)
    species = models.CharField(max_length=10, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    weight = models.FloatField()
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='pets')
    image = models.ImageField(upload_to='pets/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class MedicalRecord(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='medical_records', verbose_name='반려동물')
    date = models.DateField(verbose_name='진료일')
    diagnosis = models.TextField(verbose_name='진단')
    treatment = models.TextField(verbose_name='치료')
    notes = models.TextField(blank=True, null=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '진료기록'
        verbose_name_plural = '진료기록들'

    def __str__(self):
        return f"{self.pet.name}의 진료기록 ({self.date})"

class Vaccination(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='vaccinations', verbose_name='반려동물')
    vaccine_name = models.CharField(max_length=100, verbose_name='백신명')
    date_given = models.DateField(verbose_name='접종일')
    next_due_date = models.DateField(verbose_name='다음 접종예정일')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '예방접종'
        verbose_name_plural = '예방접종들'

    def __str__(self):
        return f"{self.pet.name}의 {self.vaccine_name} 접종"

class AdoptionStory(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='adoption_stories/', null=True, blank=True)
    author = models.ForeignKey('api.CustomUser', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Adoption stories"

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=500)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Support(models.Model):
    SUPPORT_TYPE_CHOICES = (
        ('financial', '금전적 지원'),
        ('medical', '의료 지원'),
        ('adoption', '입양 지원'),
        ('education', '교육 지원'),
        ('other', '기타'),
    )

    STATUS_CHOICES = (
        ('ongoing', '진행중'),
        ('upcoming', '예정'),
        ('ended', '종료'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    support_type = models.CharField(max_length=20, choices=SUPPORT_TYPE_CHOICES, default='other')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ongoing')
    requirements = models.TextField()
    target = models.TextField(help_text='지원 대상')
    benefit = models.TextField(help_text='지원 내용')
    how_to_apply = models.TextField(help_text='신청 방법')
    start_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    organization = models.CharField(max_length=200, help_text='주관 기관')
    contact = models.CharField(max_length=100, blank=True, help_text='담당부서 연락처')
    website_url = models.URLField(max_length=500, blank=True)
    region = models.CharField(max_length=100, blank=True, help_text='지원 가능 지역')
    # WelloPolicy 연동을 위한 필드 추가
    external_id = models.CharField(max_length=100, blank=True, null=True)
    # 크롤링 기반 데이터 출처 (내부 식별용, 사용자 비노출)
    source = models.CharField(
        max_length=20, 
        choices=[('manual', '직접입력'), ('crawling', '크롤링'), ('news', '뉴스')],
        default='manual'
    )
    expires_at = models.DateField(null=True, blank=True)
    regions = models.ManyToManyField(Region, related_name='supports', blank=True)
    agency_logo = models.URLField(max_length=200, blank=True)
    original_url = models.URLField(max_length=500, blank=True)
    summary = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '지원사업'
        verbose_name_plural = '지원사업들'

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        if not self.deadline:
            return True
        return self.deadline >= timezone.now().date()


# 펫워커 서비스 모델
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('pet_owner', '반려동물 주인'),
        ('pet_sitter', '펫시터'),
        ('admin', '관리자'),
    )
    
    # 역방향 접근자 충돌 해결을 위한 related_name 추가
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name='custom_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='user',
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='pet_owner')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, related_name='residents')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    # 소셜 로그인 관련 필드
    social_provider = models.CharField(max_length=20, blank=True, null=True, help_text='소셜 로그인 제공자 (google, kakao, naver 등)')
    social_provider_id = models.CharField(max_length=100, blank=True, null=True, help_text='소셜 로그인 제공자의 사용자 ID')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username


class PetOwnerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='pet_owner_profile')
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    preferred_service_types = models.ManyToManyField('ServiceType', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}의 프로필"


class PetSitterProfile(models.Model):
    VERIFICATION_STATUS = (
        ('pending', '심사중'),
        ('approved', '승인됨'),
        ('rejected', '거절됨'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='pet_sitter_profile')
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_STATUS, default='pending')
    id_card_image = models.ImageField(upload_to='id_cards/', blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    service_area_radius = models.PositiveIntegerField(default=5)  # km 단위
    service_types = models.ManyToManyField('ServiceType', blank=True)
    available_pet_types = models.ManyToManyField('PetType', blank=True)
    certification_images = models.ManyToManyField('CertificationImage', blank=True)
    is_available = models.BooleanField(default=True)
    average_rating = models.FloatField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    response_rate = models.FloatField(default=0)
    response_time = models.PositiveIntegerField(default=0)  # 분 단위
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}의 펫시터 프로필"


class CertificationImage(models.Model):
    image = models.ImageField(upload_to='certifications/')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class PetType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class ServiceType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class UserPet(models.Model):
    GENDER_CHOICES = (
        ('M', '수컷'),
        ('F', '암컷'),
    )
    
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    pet_type = models.ForeignKey(PetType, on_delete=models.CASCADE)
    breed = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    weight = models.FloatField()
    description = models.TextField(blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)
    behavioral_notes = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='user_pets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.owner.username}의 반려동물)"


class PetSitterService(models.Model):
    pet_sitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='services')
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()  # 원 단위
    duration = models.PositiveIntegerField()  # 분 단위
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.pet_sitter.username}의 {self.service_type.name} 서비스"


class PetSitterAvailability(models.Model):
    DAYS_OF_WEEK = (
        (0, '월요일'),
        (1, '화요일'),
        (2, '수요일'),
        (3, '목요일'),
        (4, '금요일'),
        (5, '토요일'),
        (6, '일요일'),
    )
    
    pet_sitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('pet_sitter', 'day_of_week', 'start_time', 'end_time')
    
    def __str__(self):
        return f"{self.pet_sitter.username}의 {self.get_day_of_week_display()} 가능 시간: {self.start_time}-{self.end_time}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', '대기중'),
        ('confirmed', '확정됨'),
        ('in_progress', '진행중'),
        ('completed', '완료됨'),
        ('cancelled', '취소됨'),
    )
    
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    pet_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings_as_owner')
    pet_sitter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings_as_sitter')
    service = models.ForeignKey(PetSitterService, on_delete=models.CASCADE)
    pets = models.ManyToManyField(UserPet, related_name='bookings')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    total_price = models.PositiveIntegerField()
    special_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"예약 {self.booking_id} - {self.pet_owner.username}의 {self.service.service_type.name}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('card', '신용카드'),
        ('kakao', '카카오페이'),
        ('naver', '네이버페이'),
        ('bank', '계좌이체'),
    )
    
    STATUS_CHOICES = (
        ('pending', '대기중'),
        ('completed', '완료됨'),
        ('failed', '실패'),
        ('refunded', '환불됨'),
    )
    
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"결제 {self.payment_id} - {self.booking.booking_id}"


class WalkingTrack(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='walking_track')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_distance = models.FloatField(default=0)  # 미터 단위
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"산책 기록 - {self.booking.booking_id}"


class TrackPoint(models.Model):
    walking_track = models.ForeignKey(WalkingTrack, on_delete=models.CASCADE, related_name='track_points')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"위치 포인트 - {self.walking_track.booking.booking_id} ({self.timestamp})"


class WalkingEvent(models.Model):
    EVENT_TYPE_CHOICES = (
        ('pee', '소변'),
        ('poo', '대변'),
        ('eat', '간식'),
        ('drink', '물'),
        ('play', '놀이'),
        ('rest', '휴식'),
        ('other', '기타'),
    )
    
    walking_track = models.ForeignKey(WalkingTrack, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    timestamp = models.DateTimeField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='walking_events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.walking_track.booking.booking_id} ({self.timestamp})"


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"리뷰 - {self.booking.booking_id} (평점: {self.rating})"


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"메시지: {self.sender.username} -> {self.receiver.username} ({self.created_at})"


class CommunityPost(models.Model):
    CATEGORY_CHOICES = (
        ('review', '돌봄후기'),
        ('question', 'Q&A'),
        ('event', '이벤트'),
        ('local', '우리동네모임'),
        ('free', '자유게시판'),
    )
    
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    images = models.ManyToManyField('PostImage', blank=True)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class PostImage(models.Model):
    image = models.ImageField(upload_to='community_posts/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"게시글 이미지 {self.id}"


class Comment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author.username}의 댓글 - {self.post.title}"


class PostLike(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f"{self.user.username}의 좋아요 - {self.post.title}"


class Notification(models.Model):
    TYPE_CHOICES = (
        ('booking', '예약 관련'),
        ('message', '메시지'),
        ('review', '리뷰'),
        ('system', '시스템'),
        ('community', '커뮤니티'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    related_booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    related_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    related_post = models.ForeignKey(CommunityPost, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}의 알림: {self.title}"

class LegalCode(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    parent_code = models.CharField(max_length=10, null=True, blank=True)
    rank = models.PositiveSmallIntegerField(null=True, blank=True)
    created_date = models.DateField(null=True, blank=True)
    abolished_date = models.DateField(null=True, blank=True)
    last_updated_date = models.DateField(null=True, blank=True)
    is_lowest_level = models.BooleanField(default=False)
    resident_code = models.CharField(max_length=10, null=True, blank=True)
    cadastral_code = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        ordering = ['code']
        
    def __str__(self):
        return self.name

class WelloPolicy(models.Model):
    policy_id = models.CharField(max_length=100, unique=True)
    meta_policy_id_idx = models.CharField(max_length=100, blank=True)
    agency_logo = models.URLField(max_length=200, blank=True)
    policy_name = models.CharField(max_length=200, blank=True)
    agency = models.CharField(max_length=100)
    support_target = models.CharField(max_length=255, blank=True)
    application_period = models.CharField(max_length=100, blank=True)
    responsible_agency = models.CharField(max_length=100, blank=True)
    support_benefit = models.CharField(max_length=100, blank=True)
    like_count = models.IntegerField(default=0)
    like_yn = models.BooleanField(default=False)
    comment_count = models.IntegerField(default=0)
    wishlist_yn = models.BooleanField(default=False)
    expiration_date = models.CharField(max_length=50)
    dday = models.CharField(max_length=20, blank=True)
    regions = models.ManyToManyField(Region, related_name='policies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wello_policies'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.policy_name

class WelloPolicyDetail(models.Model):
    policy = models.OneToOneField(WelloPolicy, on_delete=models.CASCADE, related_name='detail')
    summary = models.JSONField(null=True)
    website_url = models.URLField(max_length=500, null=True)
    contact_number = models.CharField(max_length=50, null=True)
    target = models.TextField()
    content = models.TextField()
    related_info = models.TextField(null=True)
    how_to_apply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wello_policy_details'
    
    def __str__(self):
        return f"{self.policy.policy_name} 상세정보"

class News(models.Model):
    title = models.CharField(max_length=500)
    link = models.URLField(max_length=1000)
    snippet = models.TextField()
    published_date = models.DateTimeField()
    source = models.CharField(max_length=200)
    image_url = models.URLField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "News"
        ordering = ['-published_date']
        
    def __str__(self):
        return self.title