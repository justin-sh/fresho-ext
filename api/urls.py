from django.urls import path, include
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet, basename='users')
router.register('orders', views.OrderViewSet, basename="orders")

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
]
