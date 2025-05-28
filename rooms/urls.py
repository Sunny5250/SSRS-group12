from django.urls import path
from . import views

# 应用命名空间，用于在模板中引用URL，如 {% url 'rooms:room_list' %}
app_name = 'rooms'

urlpatterns = [
    # 自习室列表页面的URL，对应RoomListView
    # 访问路径：/rooms/
    path('', views.RoomListView.as_view(), name='room_list'),
    
    # 自习室详情页面的URL，对应RoomDetailView
    # 访问路径：/rooms/<room_id>/
    # <int:pk> 表示捕获整数类型的主键参数
    path('<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
]
