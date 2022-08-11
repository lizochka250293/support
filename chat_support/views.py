from django.db.models import Subquery, Q
from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordContextMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic import CreateView, FormView, ListView, DetailView
from django.views.generic.edit import FormMixin
from rest_framework import generics

from chat_support.forms import RegisterUserForm, Auntification, RatingForm
from chat_support.models import ChatMessage, ChatDialog, User
from chat_support.serializers import ChatMessageSerializer


def login_out(reguest):
    logout(reguest)
    return redirect('title')


# титульная страница авторизации

class LoginViewList(LoginView):
    form_class = Auntification
    template_name = 'chat/number.html'

    def get_success_url(self):
        user = self.request.POST.get('username')
        print(user)
        return reverse('question')

# класс перехода с кнопкой задать вопрос
def question(request):
    name = request.user.username
    context = {'room_id': name}
    return render(request=request, template_name='chat/question.html', context=context)


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
class PersonalArea(FormMixin, ListView):
    model = ChatMessage
    template_name = 'chat/index.html'
    context_object_name = "messages"
    form_class = RatingForm

    # формируем сообщения для оценки
    def get_queryset(self):
        return ChatMessage.objects.filter(author=self.request.user).order_by("-create_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # message = ChatMessage.objects.filter(author=self.request.user)
        dialogs = ChatDialog.objects.filter(is_active=True, messages__author=self.request.user).distinct()
        #.annotate(
           # message=Q('messages')
        #)
        context['dialogs'] = dialogs
        return context

    def get_success_url(self):
        pk = self.kwargs['room_id']
        return reverse('index', kwargs={'room_id': pk})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        return self.form_valid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        message_id = self.request.POST.get('message_1')
        message = get_object_or_404(ChatMessage, id=message_id)
        self.object.message = message
        self.object.is_active = False
        self.object.save()
        return super().form_valid(form)


# класс комнаты
class PersonalRoom(DetailView):
    model = ChatDialog
    template_name = 'chat/room.html'
    pk_url_kwarg = 'room_id'

    # получаем контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = ChatMessage.objects.filter(dialog=self.get_object())
        context['dialog'] = self.get_object().id
        context['user'] = ''
        for i in ChatMessage.objects.filter(dialog=self.get_object()):
            context['user'] = i.author
        return context

    def get_success_url(self):
        pk = self.kwargs['room_id']
        return reverse('index', kwargs={'room_id': pk})


class ChatDialogCreateApiView(generics.CreateAPIView):
    queryset = ChatDialog.objects.all()
    serializer_class = ChatMessageSerializer

    def perform_create(self, serializer):
        chat_dialog = ChatDialog.objects.create()
        serializer.save(author=self.request.user, dialog=chat_dialog)
        # body = serializer.data['body']
        # ChatMessage.objects.create(body=body, author=self.request.user, dialog=chat_dialog)
        # send_telegram(serializer.data['message'], serializer.data['number'])


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            mail = password_reset_form.cleaned_data['email']
            user = User.objects.get(email=mail)  # email в форме регистрации проверен на уникальность
            subject = 'Запрошен сброс пароля'
            email_template_name = "chat/email_password_reset.html"
            cont = {
                "email": user.email,
                'domain': '127.0.0.1:8000',  # доменное имя сайта
                'site_name': 'Website',  # название своего сайта
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),  # шифруем идентификатор
                "user": user,  # чтобы обратиться в письме по логину пользователя
                'token': default_token_generator.make_token(user),  # генерируем токен
                'protocol': 'http',
            }
            msg_html = render_to_string(email_template_name, cont)

            return redirect("/password_reset/done/")
    else:
        password_reset_form = PasswordResetForm()
    return render(request=request, template_name="chat/password_reset.html",
                  context={"password_reset_form": password_reset_form})
