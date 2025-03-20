# hyper_pets_backend/api/pet_walker_views/notification_views.py
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Notification
from ..serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'is_read']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        # 사용자 본인의 알림만 조회 가능
        return self.queryset.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            created_at=timezone.now(),
            is_read=False
        )
    
    @action(detail=True, methods=['POST'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': '알림을 읽음으로 표시했습니다.'})
    
    @action(detail=False, methods=['POST'])
    def mark_all_as_read(self, request):
        notifications = self.get_queryset().filter(is_read=False)
        count = notifications.count()
        notifications.update(is_read=True)
        return Response({'status': f'{count}개의 알림을 읽음으로 표시했습니다.'})
    
    @action(detail=False, methods=['GET'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})
    
    @action(detail=False, methods=['GET'])
    def recent(self, request):
        # 최근 7일 이내의 알림만 조회
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        notifications = self.get_queryset().filter(created_at__gte=seven_days_ago)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
