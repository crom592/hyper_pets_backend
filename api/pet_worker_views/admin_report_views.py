from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum, F, Avg
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Booking, CustomUser, Payment, PetSitterService, UserPet, PetType, ServiceType

class AdminReportBaseView(APIView):
    permission_classes = [IsAdminUser]
    
    def get_date_range(self, period, start_date=None, end_date=None):
        today = timezone.now().date()
        
        if period == 'this-month':
            start_date = today.replace(day=1)
            next_month = today.month + 1 if today.month < 12 else 1
            next_month_year = today.year if today.month < 12 else today.year + 1
            end_date = today.replace(year=next_month_year, month=next_month, day=1) - timedelta(days=1)
        
        elif period == 'last-month':
            last_month = today.month - 1 if today.month > 1 else 12
            last_month_year = today.year if today.month > 1 else today.year - 1
            start_date = today.replace(year=last_month_year, month=last_month, day=1)
            end_date = today.replace(day=1) - timedelta(days=1)
        
        elif period == 'last-3-months':
            three_months_ago = today.month - 3
            year_offset = 0
            while three_months_ago <= 0:
                three_months_ago += 12
                year_offset -= 1
            start_date = today.replace(year=today.year + year_offset, month=three_months_ago, day=1)
            end_date = today
        
        elif period == 'last-6-months':
            six_months_ago = today.month - 6
            year_offset = 0
            while six_months_ago <= 0:
                six_months_ago += 12
                year_offset -= 1
            start_date = today.replace(year=today.year + year_offset, month=six_months_ago, day=1)
            end_date = today
        
        elif period == 'this-year':
            start_date = today.replace(month=1, day=1)
            end_date = today
        
        elif period == 'custom' and start_date and end_date:
            # 이미 문자열로 받은 날짜를 datetime 객체로 변환
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        else:
            # 기본값: 최근 30일
            start_date = today - timedelta(days=30)
            end_date = today
        
        return start_date, end_date
    
    def get_previous_period_data(self, model, date_field, start_date, end_date, filter_kwargs=None, annotate_kwargs=None):
        """이전 기간의 데이터를 가져오는 헬퍼 메서드"""
        period_length = (end_date - start_date).days
        previous_end_date = start_date - timedelta(days=1)
        previous_start_date = previous_end_date - timedelta(days=period_length)
        
        filter_kwargs = filter_kwargs or {}
        filter_kwargs.update({
            f'{date_field}__gte': previous_start_date,
            f'{date_field}__lte': previous_end_date
        })
        
        queryset = model.objects.filter(**filter_kwargs)
        
        if annotate_kwargs:
            queryset = queryset.annotate(**annotate_kwargs)
        
        return queryset

class MonthlyStatsView(AdminReportBaseView):
    def get(self, request):
        period = request.query_params.get('period', 'this-month')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        
        start_date, end_date = self.get_date_range(period, start_date, end_date)
        
        # 월별 예약 및 수익 통계
        bookings = Booking.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            booking_count=Count('id'),
            revenue=Sum('total_price')
        ).order_by('month')
        
        # 결과 포맷팅
        result = []
        for booking in bookings:
            month_str = booking['month'].strftime('%Y-%m')
            result.append({
                'month': month_str,
                'bookings': booking['booking_count'],
                'revenue': booking['revenue'] or 0
            })
        
        return Response({'data': result})

class ServiceStatsView(AdminReportBaseView):
    def get(self, request):
        period = request.query_params.get('period', 'this-month')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        
        start_date, end_date = self.get_date_range(period, start_date, end_date)
        
        # 서비스 유형별 예약 통계
        service_stats = Booking.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).values(
            'service__service_type__name'
        ).annotate(
            booking_count=Count('id'),
            revenue=Sum('total_price')
        ).order_by('-booking_count')
        
        # 결과 포맷팅
        result = []
        for stat in service_stats:
            service_name = stat['service__service_type__name'] or '기타'
            result.append({
                'name': service_name,
                'bookings': stat['booking_count'],
                'revenue': stat['revenue'] or 0
            })
        
        return Response({'data': result})

class LocationStatsView(AdminReportBaseView):
    def get(self, request):
        period = request.query_params.get('period', 'this-month')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        
        start_date, end_date = self.get_date_range(period, start_date, end_date)
        
        # 지역별 예약 통계 (사용자의 주소 기반)
        location_stats = Booking.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            pet_owner__address__isnull=False
        ).values(
            'pet_owner__address'
        ).annotate(
            booking_count=Count('id'),
            latitude=Avg('pet_owner__latitude'),
            longitude=Avg('pet_owner__longitude')
        ).order_by('-booking_count')
        
        # 결과 포맷팅
        result = []
        for stat in location_stats:
            if stat['pet_owner__address'] and stat['latitude'] and stat['longitude']:
                result.append({
                    'address': stat['pet_owner__address'],
                    'bookings': stat['booking_count'],
                    'latitude': stat['latitude'],
                    'longitude': stat['longitude']
                })
        
        return Response({'data': result})

class PetTypeStatsView(AdminReportBaseView):
    def get(self, request):
        period = request.query_params.get('period', 'this-month')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        
        start_date, end_date = self.get_date_range(period, start_date, end_date)
        
        # 반려동물 유형별 통계
        # 예약에 연결된 반려동물을 통해 통계 수집
        pet_type_stats = Booking.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).values(
            'pets__pet_type__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 결과 포맷팅
        result = []
        for stat in pet_type_stats:
            pet_type = stat['pets__pet_type__name'] or '기타'
            result.append({
                'name': pet_type,
                'value': stat['count']
            })
        
        return Response({'data': result})

class SummaryStatsView(AdminReportBaseView):
    def get(self, request):
        period = request.query_params.get('period', 'this-month')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        
        start_date, end_date = self.get_date_range(period, start_date, end_date)
        
        # 현재 기간 통계
        total_bookings = Booking.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).count()
        
        total_revenue = Payment.objects.filter(
            payment_date__gte=start_date,
            payment_date__lte=end_date,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        new_users = CustomUser.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            user_type='pet_owner'
        ).count()
        
        new_sitters = CustomUser.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date,
            user_type='pet_sitter'
        ).count()
        
        # 이전 기간 통계 (비교용)
        period_length = (end_date - start_date).days
        previous_end_date = start_date - timedelta(days=1)
        previous_start_date = previous_end_date - timedelta(days=period_length)
        
        previous_bookings = Booking.objects.filter(
            created_at__gte=previous_start_date,
            created_at__lte=previous_end_date
        ).count()
        
        previous_revenue = Payment.objects.filter(
            payment_date__gte=previous_start_date,
            payment_date__lte=previous_end_date,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        previous_users = CustomUser.objects.filter(
            created_at__gte=previous_start_date,
            created_at__lte=previous_end_date,
            user_type='pet_owner'
        ).count()
        
        previous_sitters = CustomUser.objects.filter(
            created_at__gte=previous_start_date,
            created_at__lte=previous_end_date,
            user_type='pet_sitter'
        ).count()
        
        # 증감률 계산
        bookings_change = self.calculate_percentage_change(previous_bookings, total_bookings)
        revenue_change = self.calculate_percentage_change(previous_revenue, total_revenue)
        users_change = self.calculate_percentage_change(previous_users, new_users)
        sitters_change = self.calculate_percentage_change(previous_sitters, new_sitters)
        
        result = {
            'totalBookings': total_bookings,
            'totalRevenue': total_revenue,
            'newUsers': new_users,
            'newSitters': new_sitters,
            'previousPeriodComparison': {
                'bookings': bookings_change,
                'revenue': revenue_change,
                'users': users_change,
                'sitters': sitters_change
            }
        }
        
        return Response({'data': result})
    
    def calculate_percentage_change(self, previous, current):
        if previous == 0:
            return 100 if current > 0 else 0
        
        change = ((current - previous) / previous) * 100
        return round(change)
