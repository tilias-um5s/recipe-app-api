from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('create/', views.CreateUserApiView.as_view(), name='create'),
    path('auth-token/', views.CreateTokenView.as_view(), name='auth-token'),
    path('profile/', views.ManageUserView.as_view(), name='profile'),
]
