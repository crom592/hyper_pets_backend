# hyper_pets_backend/api/pet_walker_views/booking_views.py
import uuid
from datetime import datetime, timedelta
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import (Booking, Payment, WalkingTrack, TrackPoint, WalkingEvent, 
                     UserPet, PetSitterService, Notification)
from ..serializers import (BookingSerializer, PaymentSerializer, WalkingTrackSerializer,
                          TrackPointSerializer, WalkingEventSerializer)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'service', 'pet_sitter', 'pet_owner']
    search_fields = ['booking_id', 'pet_sitter__username', 'pet_owner__username']
    ordering_fields = ['booking_date', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # 날짜 범위 필터링
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(booking_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(booking_date__lte=end_date)
        
        # 사용자 타입에 따른 필터링
        if user.user_type == 'pet_owner':
            queryset = queryset.filter(pet_owner=user)
        elif user.user_type == 'pet_sitter':
            queryset = queryset.filter(pet_sitter=user)
        
        return queryset
    
    def perform_create(self, serializer):
        # 예약 ID 생성
        booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
        
        # 서비스 정보 가져오기
        service_id = self.request.data.get('service')
        service = get_object_or_404(PetSitterService, id=service_id)
        
        # 펫 정보 가져오기
        pet_ids = self.request.data.get('pet_ids', [])
        pets = UserPet.objects.filter(id__in=pet_ids, owner=self.request.user)
        
        # 총 가격 계산
        total_price = service.price * len(pets)
        
        # 예약 생성
        booking = serializer.save(
            booking_id=booking_id,
            pet_owner=self.request.user,
            pet_sitter=service.pet_sitter,
            service=service,
            total_price=total_price,
            status='pending'
        )
        
        # 알림 생성 (펫시터에게)
        Notification.objects.create(
            user=service.pet_sitter,
            type='booking',
            content=f'새로운 예약 요청이 있습니다. 예약 ID: {booking_id}',
            related_id=booking.id
        )
    
    @action(detail=True, methods=['POST'])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        
        # 펫시터만 예약을 확정할 수 있음
        if request.user != booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 대기 중인 예약만 확정 가능
        if booking.status != 'pending':
            return Response({'error': '대기 중인 예약만 확정할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'confirmed'
        booking.save()
        
        # 알림 생성 (펫 주인에게)
        Notification.objects.create(
            user=booking.pet_owner,
            type='booking',
            content=f'예약이 확정되었습니다. 예약 ID: {booking.booking_id}',
            related_id=booking.id
        )
        
        return Response({'status': '예약이 확정되었습니다.'})
    
    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        reason = request.data.get('reason', '')
        
        # 예약 주인이나 펫시터만 취소 가능
        if request.user != booking.pet_owner and request.user != booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 완료된 예약은 취소 불가
        if booking.status == 'completed':
            return Response({'error': '완료된 예약은 취소할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'cancelled'
        booking.save()
        
        # 알림 생성
        if request.user == booking.pet_owner:
            # 펫시터에게 알림
            Notification.objects.create(
                user=booking.pet_sitter,
                type='booking',
                content=f'예약이 취소되었습니다. 예약 ID: {booking.booking_id}, 사유: {reason}',
                related_id=booking.id
            )
        else:
            # 펫 주인에게 알림
            Notification.objects.create(
                user=booking.pet_owner,
                type='booking',
                content=f'예약이 취소되었습니다. 예약 ID: {booking.booking_id}, 사유: {reason}',
                related_id=booking.id
            )
        
        return Response({'status': '예약이 취소되었습니다.'})
    
    @action(detail=True, methods=['POST'])
    def complete(self, request, pk=None):
        booking = self.get_object()
        
        # 펫시터만 예약을 완료할 수 있음
        if request.user != booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 확정된 예약만 완료 가능
        if booking.status != 'confirmed':
            return Response({'error': '확정된 예약만 완료할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = 'completed'
        booking.save()
        
        # 알림 생성 (펫 주인에게)
        Notification.objects.create(
            user=booking.pet_owner,
            type='booking',
            content=f'예약이 완료되었습니다. 예약 ID: {booking.booking_id}',
            related_id=booking.id
        )
        
        return Response({'status': '예약이 완료되었습니다.'})


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'payment_method', 'booking']
    search_fields = ['payment_id', 'transaction_id']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # 사용자 타입에 따른 필터링
        if user.user_type == 'pet_owner':
            queryset = queryset.filter(booking__pet_owner=user)
        elif user.user_type == 'pet_sitter':
            queryset = queryset.filter(booking__pet_sitter=user)
        
        return queryset
    
    def perform_create(self, serializer):
        # 결제 ID 생성
        payment_id = f"PY{uuid.uuid4().hex[:8].upper()}"
        
        # 예약 정보 가져오기
        booking_id = self.request.data.get('booking')
        booking = get_object_or_404(Booking, id=booking_id)
        
        # 결제 생성
        payment = serializer.save(
            payment_id=payment_id,
            booking=booking,
            amount=booking.total_price,
            status='pending',
            payment_date=timezone.now()
        )
        
        # 여기서 실제 결제 처리 로직 구현 (카카오페이, 네이버페이 등)
        # 실제 구현 시에는 외부 결제 API와 연동 필요
        
        # 테스트를 위해 바로 결제 완료 처리
        payment.status = 'completed'
        payment.transaction_id = f"TX{uuid.uuid4().hex[:10].upper()}"
        payment.save()
        
        # 알림 생성
        Notification.objects.create(
            user=booking.pet_owner,
            type='payment',
            content=f'결제가 완료되었습니다. 결제 ID: {payment_id}',
            related_id=payment.id
        )
        
        Notification.objects.create(
            user=booking.pet_sitter,
            type='payment',
            content=f'새로운 결제가 완료되었습니다. 결제 ID: {payment_id}',
            related_id=payment.id
        )


class WalkingTrackViewSet(viewsets.ModelViewSet):
    queryset = WalkingTrack.objects.all()
    serializer_class = WalkingTrackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['booking', 'is_active']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # 사용자 타입에 따른 필터링
        if user.user_type == 'pet_owner':
            queryset = queryset.filter(booking__pet_owner=user)
        elif user.user_type == 'pet_sitter':
            queryset = queryset.filter(booking__pet_sitter=user)
        
        return queryset
    
    def perform_create(self, serializer):
        # 예약 정보 가져오기
        booking_id = self.request.data.get('booking')
        booking = get_object_or_404(Booking, id=booking_id)
        
        # 펫시터만 트랙을 생성할 수 있음
        if self.request.user != booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 트랙 생성
        serializer.save(
            booking=booking,
            start_time=timezone.now(),
            is_active=True
        )
    
    @action(detail=True, methods=['POST'])
    def end_walk(self, request, pk=None):
        track = self.get_object()
        
        # 펫시터만 산책을 종료할 수 있음
        if request.user != track.booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 이미 종료된 트랙은 다시 종료할 수 없음
        if not track.is_active:
            return Response({'error': '이미 종료된 산책입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        track.is_active = False
        track.end_time = timezone.now()
        track.save()
        
        # 알림 생성 (펫 주인에게)
        Notification.objects.create(
            user=track.booking.pet_owner,
            type='walking',
            content='산책이 종료되었습니다.',
            related_id=track.id
        )
        
        return Response({'status': '산책이 종료되었습니다.'})


class TrackPointViewSet(viewsets.ModelViewSet):
    queryset = TrackPoint.objects.all()
    serializer_class = TrackPointSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # 트랙 ID로 필터링
        track_id = self.request.query_params.get('track', None)
        if track_id:
            queryset = queryset.filter(track_id=track_id)
        
        # 사용자 타입에 따른 필터링
        if user.user_type == 'pet_owner':
            queryset = queryset.filter(track__booking__pet_owner=user)
        elif user.user_type == 'pet_sitter':
            queryset = queryset.filter(track__booking__pet_sitter=user)
        
        return queryset
    
    def perform_create(self, serializer):
        # 트랙 정보 가져오기
        track_id = self.request.data.get('track')
        track = get_object_or_404(WalkingTrack, id=track_id)
        
        # 펫시터만 트랙 포인트를 생성할 수 있음
        if self.request.user != track.booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 활성화된 트랙에만 포인트 추가 가능
        if not track.is_active:
            return Response({'error': '종료된 산책에는 위치를 추가할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 트랙 포인트 생성
        serializer.save(
            track=track,
            timestamp=timezone.now()
        )


class WalkingEventViewSet(viewsets.ModelViewSet):
    queryset = WalkingEvent.objects.all()
    serializer_class = WalkingEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['track', 'event_type']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # 사용자 타입에 따른 필터링
        if user.user_type == 'pet_owner':
            queryset = queryset.filter(track__booking__pet_owner=user)
        elif user.user_type == 'pet_sitter':
            queryset = queryset.filter(track__booking__pet_sitter=user)
        
        return queryset
    
    def perform_create(self, serializer):
        # 트랙 정보 가져오기
        track_id = self.request.data.get('track')
        track = get_object_or_404(WalkingTrack, id=track_id)
        
        # 펫시터만 이벤트를 생성할 수 있음
        if self.request.user != track.booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 활성화된 트랙에만 이벤트 추가 가능
        if not track.is_active:
            return Response({'error': '종료된 산책에는 이벤트를 추가할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 이벤트 생성
        event = serializer.save(
            track=track,
            timestamp=timezone.now()
        )
        
        # 알림 생성 (펫 주인에게)
        event_type_display = event.get_event_type_display()
        Notification.objects.create(
            user=track.booking.pet_owner,
            type='walking',
            content=f'산책 중 {event_type_display} 이벤트가 발생했습니다.',
            related_id=event.id
        )
