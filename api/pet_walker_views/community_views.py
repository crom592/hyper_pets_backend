# hyper_pets_backend/api/pet_walker_views/community_views.py
from django.db.models import Q, Count, F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from ..models import (Review, Message, CommunityPost, PostImage, Comment, PostLike, Notification)
from ..serializers import (ReviewSerializer, MessageSerializer, CommunityPostSerializer,
                          PostImageSerializer, CommentSerializer, PostLikeSerializer)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['booking__pet_sitter', 'booking__pet_owner', 'rating']
    ordering_fields = ['created_at', 'rating']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # 사용자 타입에 따른 필터링
        if user.user_type == 'pet_owner':
            queryset = queryset.filter(booking__pet_owner=user)
        elif user.user_type == 'pet_sitter':
            queryset = queryset.filter(booking__pet_sitter=user)
        
        # 평점 필터링
        min_rating = self.request.query_params.get('min_rating', None)
        max_rating = self.request.query_params.get('max_rating', None)
        if min_rating:
            queryset = queryset.filter(rating__gte=int(min_rating))
        if max_rating:
            queryset = queryset.filter(rating__lte=int(max_rating))
        
        return queryset
    
    def perform_create(self, serializer):
        # 예약 정보 가져오기
        booking_id = self.request.data.get('booking')
        booking = get_object_or_404(Booking, id=booking_id)
        
        # 펫 주인만 리뷰를 작성할 수 있음
        if self.request.user != booking.pet_owner:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 완료된 예약에만 리뷰 작성 가능
        if booking.status != 'completed':
            return Response({'error': '완료된 예약에만 리뷰를 작성할 수 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 이미 리뷰가 있는지 확인
        if Review.objects.filter(booking=booking).exists():
            return Response({'error': '이미 리뷰를 작성했습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 리뷰 생성
        review = serializer.save(
            booking=booking,
            created_at=timezone.now()
        )
        
        # 펫시터 평점 업데이트
        pet_sitter = booking.pet_sitter
        pet_sitter_profile = pet_sitter.petsitterprofile
        
        # 평균 평점 및 리뷰 수 업데이트
        reviews = Review.objects.filter(booking__pet_sitter=pet_sitter)
        pet_sitter_profile.total_reviews = reviews.count()
        pet_sitter_profile.average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        pet_sitter_profile.save()
        
        # 알림 생성 (펫시터에게)
        Notification.objects.create(
            user=booking.pet_sitter,
            type='review',
            content=f'새로운 리뷰가 작성되었습니다. 평점: {review.rating}',
            related_id=review.id
        )


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sender', 'receiver', 'booking', 'is_read']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(Q(sender=user) | Q(receiver=user))
        
        # 대화 상대 필터링
        other_user_id = self.request.query_params.get('other_user', None)
        if other_user_id:
            queryset = queryset.filter(
                Q(sender_id=other_user_id, receiver=user) | 
                Q(sender=user, receiver_id=other_user_id)
            )
        
        # 예약 관련 메시지 필터링
        booking_id = self.request.query_params.get('booking', None)
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        
        return queryset
    
    def perform_create(self, serializer):
        # 수신자 정보 가져오기
        receiver_id = self.request.data.get('receiver')
        receiver = get_object_or_404(CustomUser, id=receiver_id)
        
        # 예약 정보 가져오기 (선택적)
        booking_id = self.request.data.get('booking', None)
        booking = None
        if booking_id:
            booking = get_object_or_404(Booking, id=booking_id)
        
        # 메시지 생성
        message = serializer.save(
            sender=self.request.user,
            receiver=receiver,
            booking=booking,
            created_at=timezone.now(),
            is_read=False
        )
        
        # 알림 생성 (수신자에게)
        Notification.objects.create(
            user=receiver,
            type='message',
            content=f'새로운 메시지가 도착했습니다: {message.content[:30]}{"..." if len(message.content) > 30 else ""}',
            related_id=message.id
        )
    
    @action(detail=True, methods=['POST'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        
        # 수신자만 읽음 표시 가능
        if request.user != message.receiver:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        message.is_read = True
        message.save()
        
        return Response({'status': '메시지를 읽음으로 표시했습니다.'})
    
    @action(detail=False, methods=['POST'])
    def mark_all_as_read(self, request):
        # 특정 발신자의 모든 메시지 읽음 표시
        sender_id = request.data.get('sender', None)
        if sender_id:
            messages = self.get_queryset().filter(sender_id=sender_id, receiver=request.user, is_read=False)
            messages.update(is_read=True)
            return Response({'status': f'{messages.count()}개의 메시지를 읽음으로 표시했습니다.'})
        
        # 모든 메시지 읽음 표시
        messages = self.get_queryset().filter(receiver=request.user, is_read=False)
        messages.update(is_read=True)
        
        return Response({'status': f'{messages.count()}개의 메시지를 읽음으로 표시했습니다.'})


class CommunityPostViewSet(viewsets.ModelViewSet):
    queryset = CommunityPost.objects.all()
    serializer_class = CommunityPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count', 'like_count']
    
    def get_queryset(self):
        queryset = self.queryset
        
        # 카테고리 필터링
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # 검색어 필터링
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        post = serializer.save(
            author=self.request.user,
            created_at=timezone.now(),
            view_count=0,
            like_count=0
        )
        
        # 이미지 처리 (다중 이미지 업로드)
        images = self.request.data.getlist('images', [])
        for image in images:
            PostImage.objects.create(post=post, image=image)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # 조회수 증가
        instance.view_count = F('view_count') + 1
        instance.save()
        instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PostImageViewSet(viewsets.ModelViewSet):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = self.queryset
        
        # 게시글 ID로 필터링
        post_id = self.request.query_params.get('post', None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        return queryset
    
    def perform_create(self, serializer):
        # 게시글 정보 가져오기
        post_id = self.request.data.get('post')
        post = get_object_or_404(CommunityPost, id=post_id)
        
        # 게시글 작성자만 이미지 추가 가능
        if self.request.user != post.author:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer.save(post=post)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'author', 'parent']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        queryset = self.queryset
        
        # 게시글 ID로 필터링
        post_id = self.request.query_params.get('post', None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        # 최상위 댓글만 필터링 (대댓글 제외)
        if self.request.query_params.get('top_level', False):
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset
    
    def perform_create(self, serializer):
        # 게시글 정보 가져오기
        post_id = self.request.data.get('post')
        post = get_object_or_404(CommunityPost, id=post_id)
        
        # 부모 댓글 정보 가져오기 (대댓글인 경우)
        parent_id = self.request.data.get('parent', None)
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)
        
        comment = serializer.save(
            post=post,
            author=self.request.user,
            parent=parent,
            created_at=timezone.now()
        )
        
        # 알림 생성
        if parent:
            # 부모 댓글 작성자에게 알림
            if parent.author != self.request.user:
                Notification.objects.create(
                    user=parent.author,
                    type='comment',
                    content=f'회원님의 댓글에 답글이 달렸습니다: {comment.content[:30]}{"..." if len(comment.content) > 30 else ""}',
                    related_id=comment.id
                )
        else:
            # 게시글 작성자에게 알림
            if post.author != self.request.user:
                Notification.objects.create(
                    user=post.author,
                    type='comment',
                    content=f'회원님의 게시글에 댓글이 달렸습니다: {comment.content[:30]}{"..." if len(comment.content) > 30 else ""}',
                    related_id=comment.id
                )


class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(user=user)
        
        # 게시글 ID로 필터링
        post_id = self.request.query_params.get('post', None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        # 게시글 정보 가져오기
        post_id = request.data.get('post')
        post = get_object_or_404(CommunityPost, id=post_id)
        
        # 이미 좋아요를 눌렀는지 확인
        if PostLike.objects.filter(post=post, user=request.user).exists():
            return Response({'error': '이미 좋아요를 눌렀습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 좋아요 생성
        like = PostLike.objects.create(
            post=post,
            user=request.user
        )
        
        # 게시글 좋아요 수 증가
        post.like_count = F('like_count') + 1
        post.save()
        
        # 알림 생성 (게시글 작성자에게)
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                type='like',
                content='회원님의 게시글에 좋아요가 추가되었습니다.',
                related_id=post.id
            )
        
        serializer = self.get_serializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        post = instance.post
        
        # 좋아요 삭제
        self.perform_destroy(instance)
        
        # 게시글 좋아요 수 감소
        post.like_count = F('like_count') - 1
        post.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
