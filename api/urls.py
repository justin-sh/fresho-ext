from django.urls import path, include

from api import views

urlpatterns = [
    path('auth/', include('rest_framework.urls')),
    # path('api/users/', views.UserViewSet),
    path('orders/init/', views.init_orders),
    path('orders/upload/', views.upload_orders),
    # path('snippets/', views.snippet_detail),
]
