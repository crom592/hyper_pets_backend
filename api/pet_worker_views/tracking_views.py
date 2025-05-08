# hyper_pets_backend/api/pet_worker_views/tracking_views.py
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import (Booking, WalkingTrack, TrackPoint, WalkingEvent, Notification)
from ..serializers import (WalkingTrackSerializer, TrackPointSerializer, WalkingEventSerializer)


class WalkingTrackViewSet(viewsets.ModelViewSet):
    queryset = WalkingTrack.objects.all()
    serializer_class = WalkingTrackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['booking', 'status']
    ordering_fields = ['start_time', 'end_time']
    
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
        
        # 펫시터만 트랙 생성 가능
        if self.request.user != booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 진행 중인 예약만 트랙 생성 가능
        if booking.status != 'in_progress':
            return Response({'error': '진행 중인 예약에만 트랙을 생성할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 이미 진행 중인 트랙이 있는지 확인
        if WalkingTrack.objects.filter(booking=booking, status='in_progress').exists():
            return Response({'error': '이미 진행 중인 트랙이 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 트랙 생성
        track = serializer.save(
            booking=booking,
            start_time=timezone.now(),
            status='in_progress'
        )
        
        # 알림 생성 (펫 주인에게)
        Notification.objects.create(
            user=booking.pet_owner,
            type='track_started',
            content='산책이 시작되었습니다. 실시간으로 위치를 확인할 수 있습니다.',
            related_id=track.id
        )
        
        # 이벤트 생성 (산책 시작)
        WalkingEvent.objects.create(
            track=track,
            event_type='start',
            timestamp=timezone.now(),
            description='산책이 시작되었습니다.',
            latitude=self.request.data.get('latitude', 0),
            longitude=self.request.data.get('longitude', 0)
        )
    
    @action(detail=True, methods=['POST'])
    def complete(self, request, pk=None):
        track = self.get_object()
        
        # 펫시터만 트랙 완료 가능
        if request.user != track.booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 진행 중인 트랙만 완료 가능
        if track.status != 'in_progress':
            return Response({'error': '진행 중인 트랙만 완료할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 트랙 완료 처리
        track.status = 'completed'
        track.end_time = timezone.now()
        track.save()
        
        # 알림 생성 (펫 주인에게)
        Notification.objects.create(
            user=track.booking.pet_owner,
            type='track_completed',
            content='산책이 완료되었습니다.',
            related_id=track.id
        )
        
        # 이벤트 생성 (산책 종료)
        WalkingEvent.objects.create(
            track=track,
            event_type='end',
            timestamp=timezone.now(),
            description='산책이 완료되었습니다.',
            latitude=request.data.get('latitude', 0),
            longitude=request.data.get('longitude', 0)
        )
        
        return Response({'status': '산책이 완료되었습니다.'})
    
    @action(detail=True, methods=['POST'])
    def pause(self, request, pk=None):
        track = self.get_object()
        
        # 펫시터만 트랙 일시정지 가능
        if request.user != track.booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 진행 중인 트랙만 일시정지 가능
        if track.status != 'in_progress':
            return Response({'error': '진행 중인 트랙만 일시정지할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 트랙 일시정지 처리
        track.status = 'paused'
        track.save()
        
        # 이벤트 생성 (산책 일시정지)
        WalkingEvent.objects.create(
            track=track,
            event_type='pause',
            timestamp=timezone.now(),
            description='산책이 일시정지되었습니다.',
            latitude=request.data.get('latitude', 0),
            longitude=request.data.get('longitude', 0)
        )
        
        return Response({'status': '산책이 일시정지되었습니다.'})
    
    @action(detail=True, methods=['POST'])
    def resume(self, request, pk=None):
        track = self.get_object()
        
        # 펫시터만 트랙 재개 가능
        if request.user != track.booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 일시정지된 트랙만 재개 가능
        if track.status != 'paused':
            return Response({'error': '일시정지된 트랙만 재개할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 트랙 재개 처리
        track.status = 'in_progress'
        track.save()
        
        # 이벤트 생성 (산책 재개)
        WalkingEvent.objects.create(
            track=track,
            event_type='resume',
            timestamp=timezone.now(),
            description='산책이 재개되었습니다.',
            latitude=request.data.get('latitude', 0),
            longitude=request.data.get('longitude', 0)
        )
        
        return Response({'status': '산책이 재개되었습니다.'})
    
    @action(detail=True, methods=['GET'])
    def statistics(self, request, pk=None):
        track = self.get_object()
        
        # 트랙 포인트 가져오기
        track_points = TrackPoint.objects.filter(track=track).order_by('timestamp')
        
        # 통계 계산
        total_distance = 0
        if track_points.count() >= 2:
            for i in range(1, track_points.count()):
                prev_point = track_points[i-1]
                curr_point = track_points[i]
                
                # 두 지점 간의 거리 계산 (하버사인 공식)
                lat1, lon1 = prev_point.latitude, prev_point.longitude
                lat2, lon2 = curr_point.latitude, curr_point.longitude
                
                R = 6371  # 지구 반경 (km)
                dLat = math.radians(lat2 - lat1)
                dLon = math.radians(lon2 - lon1)
                a = (math.sin(dLat/2) * math.sin(dLat/2) +
                     math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                     math.sin(dLon/2) * math.sin(dLon/2))
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = R * c * 1000  # 미터 단위로 변환
                
                total_distance += distance
        
        # 소요 시간 계산
        duration = 0
        if track.status == 'completed' and track.end_time and track.start_time:
            duration = (track.end_time - track.start_time).total_seconds() / 60  # 분 단위
        elif track.start_time:
            duration = (timezone.now() - track.start_time).total_seconds() / 60  # 분 단위
        
        # 이벤트 가져오기
        events = WalkingEvent.objects.filter(track=track).order_by('timestamp')
        
        return Response({
            'track_id': track.id,
            'booking_id': track.booking.id,
            'status': track.status,
            'start_time': track.start_time,
            'end_time': track.end_time,
            'total_distance': round(total_distance, 2),  # 미터
            'duration': round(duration, 2),  # 분
            'average_speed': round(total_distance / (duration * 60), 2) if duration > 0 else 0,  # 미터/초
            'points_count': track_points.count(),
            'events_count': events.count(),
            'events': WalkingEventSerializer(events, many=True).data
        })


class TrackPointViewSet(viewsets.ModelViewSet):
    queryset = TrackPoint.objects.all()
    serializer_class = TrackPointSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['track']
    ordering_fields = ['timestamp']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # 사용자 타입에 따른 필터링
        if user.user_type == 'pet_owner':
            queryset = queryset.filter(track__booking__pet_owner=user)
        elif user.user_type == 'pet_sitter':
            queryset = queryset.filter(track__booking__pet_sitter=user)
        
        # 트랙 ID로 필터링
        track_id = self.request.query_params.get('track', None)
        if track_id:
            queryset = queryset.filter(track_id=track_id)
        
        return queryset
    
    def perform_create(self, serializer):
        # 트랙 정보 가져오기
        track_id = self.request.data.get('track')
        track = get_object_or_404(WalkingTrack, id=track_id)
        
        # 펫시터만 트랙 포인트 추가 가능
        if self.request.user != track.booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 진행 중인 트랙만 포인트 추가 가능
        if track.status != 'in_progress':
            return Response({'error': '진행 중인 트랙에만 포인트를 추가할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 트랙 포인트 생성
        serializer.save(
            track=track,
            timestamp=timezone.now()
        )


class WalkingEventViewSet(viewsets.ModelViewSet):
    queryset = WalkingEvent.objects.all()
    serializer_class = WalkingEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['track', 'event_type']
    ordering_fields = ['timestamp']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # 사용자 타입에 따른 필터링
        if user.user_type == 'pet_owner':
            queryset = queryset.filter(track__booking__pet_owner=user)
        elif user.user_type == 'pet_sitter':
            queryset = queryset.filter(track__booking__pet_sitter=user)
        
        # 트랙 ID로 필터링
        track_id = self.request.query_params.get('track', None)
        if track_id:
            queryset = queryset.filter(track_id=track_id)
        
        return queryset
    
    def perform_create(self, serializer):
        # 트랙 정보 가져오기
        track_id = self.request.data.get('track')
        track = get_object_or_404(WalkingTrack, id=track_id)
        
        # 펫시터만 이벤트 추가 가능
        if self.request.user != track.booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 진행 중인 트랙만 이벤트 추가 가능
        if track.status not in ['in_progress', 'paused']:
            return Response({'error': '진행 중이거나 일시정지된 트랙에만 이벤트를 추가할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 이벤트 타입 확인
        event_type = self.request.data.get('event_type')
        if event_type not in ['photo', 'poop', 'pee', 'water', 'rest', 'play', 'emergency', 'custom']:
            return Response({'error': '유효하지 않은 이벤트 타입입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 이벤트 생성
        event = serializer.save(
            track=track,
            timestamp=timezone.now()
        )
        
        # 긴급 상황인 경우 알림 생성 (펫 주인에게)
        if event_type == 'emergency':
            Notification.objects.create(
                user=track.booking.pet_owner,
                type='emergency',
                content=f'긴급 상황 발생: {event.description}',
                related_id=event.id
            )
        
        # 일반 이벤트인 경우 알림 생성 (펫 주인에게)
        else:
            Notification.objects.create(
                user=track.booking.pet_owner,
                type='event',
                content=f'산책 중 이벤트 발생: {event.description}',
                related_id=event.id
            )


class SafetyAlertViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['POST'])
    def emergency(self, request):
        # 긴급 상황 알림
        track_id = request.data.get('track')
        description = request.data.get('description', '긴급 상황이 발생했습니다.')
        latitude = request.data.get('latitude', 0)
        longitude = request.data.get('longitude', 0)
        
        if not track_id:
            return Response({'error': '트랙 정보는 필수 항목입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        track = get_object_or_404(WalkingTrack, id=track_id)
        
        # 펫시터 또는 펫 주인만 긴급 알림 생성 가능
        if request.user != track.booking.pet_sitter and request.user != track.booking.pet_owner:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 이벤트 생성
        event = WalkingEvent.objects.create(
            track=track,
            event_type='emergency',
            timestamp=timezone.now(),
            description=description,
            latitude=latitude,
            longitude=longitude
        )
        
        # 알림 생성 (펫 주인에게)
        if request.user == track.booking.pet_sitter:
            Notification.objects.create(
                user=track.booking.pet_owner,
                type='emergency',
                content=f'긴급 상황 발생: {description}',
                related_id=event.id
            )
        
        # 알림 생성 (펫시터에게)
        if request.user == track.booking.pet_owner:
            Notification.objects.create(
                user=track.booking.pet_sitter,
                type='emergency',
                content=f'펫 주인이 긴급 상황을 알렸습니다: {description}',
                related_id=event.id
            )
        
        return Response({
            'status': '긴급 알림이 전송되었습니다.',
            'event_id': event.id
        })
    
    @action(detail=False, methods=['POST'])
    def safe_zone_alert(self, request):
        # 안전 구역 이탈 알림
        track_id = request.data.get('track')
        latitude = request.data.get('latitude', 0)
        longitude = request.data.get('longitude', 0)
        
        if not track_id:
            return Response({'error': '트랙 정보는 필수 항목입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        track = get_object_or_404(WalkingTrack, id=track_id)
        
        # 펫시터만 안전 구역 이탈 알림 생성 가능
        if request.user != track.booking.pet_sitter:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 이벤트 생성
        event = WalkingEvent.objects.create(
            track=track,
            event_type='safe_zone_exit',
            timestamp=timezone.now(),
            description='안전 구역을 벗어났습니다.',
            latitude=latitude,
            longitude=longitude
        )
        
        # 알림 생성 (펫 주인에게)
        Notification.objects.create(
            user=track.booking.pet_owner,
            type='safe_zone',
            content='펫시터가 지정된 안전 구역을 벗어났습니다.',
            related_id=event.id
        )
        
        return Response({
            'status': '안전 구역 이탈 알림이 전송되었습니다.',
            'event_id': event.id
        })
    
    @action(detail=False, methods=['POST'])
    def inactivity_alert(self, request):
        # 장시간 비활동 알림
        track_id = request.data.get('track')
        
        if not track_id:
            return Response({'error': '트랙 정보는 필수 항목입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        track = get_object_or_404(WalkingTrack, id=track_id)
        
        # 시스템 자동 알림이므로 권한 체크 없음
        
        # 마지막 트랙 포인트 확인
        last_point = TrackPoint.objects.filter(track=track).order_by('-timestamp').first()
        
        if not last_point:
            return Response({'error': '트랙 포인트가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 현재 시간과 마지막 포인트 시간 차이 계산
        time_diff = (timezone.now() - last_point.timestamp).total_seconds() / 60  # 분 단위
        
        # 15분 이상 비활동 시 알림
        if time_diff >= 15:
            # 이벤트 생성
            event = WalkingEvent.objects.create(
                track=track,
                event_type='inactivity',
                timestamp=timezone.now(),
                description=f'{int(time_diff)}분 동안 활동이 없습니다.',
                latitude=last_point.latitude,
                longitude=last_point.longitude
            )
            
            # 알림 생성 (펫 주인에게)
            Notification.objects.create(
                user=track.booking.pet_owner,
                type='inactivity',
                content=f'{int(time_diff)}분 동안 펫시터의 위치 업데이트가 없습니다.',
                related_id=event.id
            )
            
            return Response({
                'status': '비활동 알림이 전송되었습니다.',
                'event_id': event.id,
                'inactivity_minutes': int(time_diff)
            })
        
        return Response({
            'status': '비활동 시간이 충분하지 않습니다.',
            'inactivity_minutes': int(time_diff)
        })
