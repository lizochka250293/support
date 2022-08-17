from django.urls import path, include
from . import views
from .views import login_out, password_reset_request, question, passwordreset
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('api/number_create/', views.ChatDialogCreateApiView.as_view(), name='number_api'),
    # path('add-rating/', views.AddStarRating.as_view, name='add_rating'),
    path('', views.LoginViewList.as_view(), name='title'),
    path('question/', question, name='question'),
    path('number/', views.PersonalArea.as_view(), name='index'),
    path('chat/<str:room_id>/', views.PersonalRoom.as_view(), name='room'),
    path('loginout/', login_out, name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('password_reset/', passwordreset, name='password_reset'),
]
