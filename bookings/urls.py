from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('create/<int:room_id>/', views.BookingCreateView.as_view(), name='booking_create'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
    path('admin/', views.AdminBookingListView.as_view(), name='admin_booking_list'),
    path('admin/<int:pk>/approve/', views.BookingApproveView.as_view(), name='booking_approve'),
]
