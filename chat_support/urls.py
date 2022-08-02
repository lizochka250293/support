from django.urls import path, include
from . import views
from .views import login_out, password_reset_request, ResetPasswordView
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('api/number_create/', views.ChatDialogCreateApiView.as_view(), name='number_api'),
    # path('add-rating/', views.AddStarRating.as_view, name='add_rating'),
    path('', views.LoginViewList.as_view(), name='title'),
    path('number/<str:room_id>/', views.PersonalArea.as_view(), name='index'),
    path('chat/<str:room_id>/', views.PersonalRoom.as_view(), name='room'),
    path('loginout/', login_out, name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    # path('password_reset', password_reset_request, name="password_reset"),
    path('password_reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    # path('password-reset-confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('', include('django.contrib.auth.urls')),
    # path('chat/<str:room_name>/', views.PersonalRoom.as_view(), name='room')
]
