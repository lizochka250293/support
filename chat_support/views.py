from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordContextMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect

from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, FormView, ListView
from django.views.generic.edit import FormMixin

from chat_support.forms import RegisterUserForm, Auntification
from chat_support.models import ChatMessage


def login_out(reguest):
    logout(reguest)
    return redirect('title')

# титульная страница авторизации

class LoginViewList(LoginView):
    form_class = Auntification
    template_name = 'chat/number.html'

    def get_success_url(self):
        room_number = self.request.POST.get('username')
        return reverse('index', kwargs={'room_name': room_number})

# регистрация
class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'chat/register.html'
    success_url = reverse_lazy('title')

# забыли свой пароль

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'chat/password_reset.html'
    success_url = 'password_reset_confirm'


class PasswordResetConfirmView(PasswordContextMixin, FormView):
    template_name = 'chat/password_reset_confirm.html'
    success_url = 'title'

# класс личного кабинета
class PersonalArea(ListView, FormMixin):
    model = ChatMessage
    template_name = 'chat/index.html'
    context_object_name = "messages"
    # form_class = RatingForm
# забираем контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room_name'] = self.kwargs['room_name']
        return context
# формируем сообщения для оценки
    def get_queryset(self):
        return ChatMessage.objects.filter(author=self.kwargs['room_name'])
