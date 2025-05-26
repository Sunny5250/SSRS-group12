from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('run/', views.run_tests_view, name='run_tests'),
    path('detail/<int:test_id>/', views.test_detail, name='test_detail'),
    path('progress/<int:test_id>/', views.test_progress, name='test_progress'),
    path('results/<int:test_id>/', views.test_results, name='test_results'),
]
