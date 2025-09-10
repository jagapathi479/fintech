from django.urls import path
from . import views
app_name = 'core'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('loan/request/', views.loan_request_view, name='loan_request'),
    path('loan/<int:pk>/', views.loan_detail_view, name='loan_detail'),
]
