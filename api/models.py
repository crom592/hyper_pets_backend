# hyper_pets_backend/api/models.py
from django.db import models
from django.contrib.auth.models import User

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
    author = models.ForeignKey(User, on_delete=models.CASCADE)
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
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
