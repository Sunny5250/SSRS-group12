from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    path('rooms/', api_views.RoomListAPIView.as_view(), name='room_list'),
    path('rooms/<int:pk>/', api_views.RoomDetailAPIView.as_view(), name='room_detail'),
    path('bookings/', api_views.BookingListCreateAPIView.as_view(), name='booking_list_create'),
    path('bookings/<int:pk>/', api_views.BookingDetailAPIView.as_view(), name='booking_detail'),
    path('timeslots/', api_views.TimeSlotListAPIView.as_view(), name='timeslot_list'),
    path('available-slots/<int:room_id>/<str:date>/', api_views.AvailableSlotsAPIView.as_view(), name='available_slots'),
]
