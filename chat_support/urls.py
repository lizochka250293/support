from django.urls import path, include
from . import views
from .views import login_out, question, detail_dialog, admin_rating, admin_detail, password_reset, admin_delete
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('api/number_create/', views.ChatDialogCreateApiView.as_view(), name='number_api'),
    path('', views.LoginViewList.as_view(), name='title'),
    path('question/', question, name='question'),
    path('number/', views.PersonalArea.as_view(), name='index'),
    path('chat/<str:room_id>/', views.PersonalRoom.as_view(), name='room'),
    path('logout/', login_out, name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('password_reset/', password_reset, name='password_reset'),
    path('dialog_detail/<int:pk>/', detail_dialog, name='detail_dialog'),
    path('admin_rating/', admin_rating, name='admin_rating'),
    path('admin_delete/<slug:slug>/', admin_delete, name='admin_delete'),
    path('admin_detail/<slug:slug>/', admin_detail, name='admin_detail'),
]
