from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.sites import requests
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from django.views.generic.edit import FormMixin
from rest_framework import generics

from chat_support.forms import RegisterUserForm, RatingForm, PasswordReset, StaffForm
from chat_support.models import ChatMessage, ChatDialog, User, Rating
from chat_support.serializers import ChatMessageSerializer
from chat_support.services import send_telegram


def login_out(reguest):
    """Выход"""
    logout(reguest)
    return redirect('title')


class LoginViewList(LoginView):
    """Титульная страница аунтефикации"""
    form_class = AuthenticationForm
    template_name = 'chat/title.html'


@login_required
def question(request):
    """Кнопка задать вопрос"""
    name = request.user.username
    if request.user.is_superuser:
        return redirect('admin_rating')
    elif request.user.is_staff:
        return redirect('user_room')
    else:
        context = {'room_id': name}
        return render(request=request, template_name='chat/question.html', context=context)


class RegisterUser(CreateView):
    """Регистрация"""
    form_class = RegisterUserForm
    template_name = 'chat/register.html'
    success_url = reverse_lazy('title')


def password_reset(request):
    """Сброс пароля"""
    if request.method == 'POST':
        form = PasswordReset(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password_1 = form.cleaned_data['password_1']
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save(update_fields=["password"])
            return redirect('title')
    else:
        form = PasswordReset()
    return render(request, 'chat/password_reset.html', {'form': form})


class PersonalArea(LoginRequiredMixin, FormMixin, ListView):
    """Личный кабинет"""
    model = ChatMessage
    template_name = 'chat/user_room.html'
    context_object_name = "messages"
    form_class = RatingForm

    def get_queryset(self):
        """формируем сообщения для оценки"""
        return ChatMessage.objects.filter(author=self.request.user).order_by("-create_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dialogs_not_active = ChatDialog.objects.filter(is_active=False,
                                                       dialog_messages__author=self.request.user).distinct()
        dialogs_active = ChatDialog.objects.filter(is_active=True, dialog_messages__author=self.request.user).distinct()
        all_dialogs = ChatDialog.objects.filter(is_active=True)
        rating = Rating.objects.all()
        context['dialogs'] = dialogs_not_active
        context['dialogs_active'] = dialogs_active
        context['all_dialogs'] = all_dialogs
        context['rating'] = rating
        return context

    def get_success_url(self):
        return reverse('user_room')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        return self.form_valid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        dialod_id = self.request.POST.get('dialog')
        dialog = get_object_or_404(ChatDialog, id=dialod_id)
        self.object.dialog = dialog
        self.object.is_actives = False
        self.object.save()
        return super().form_valid(form)


class PersonalRoom(LoginRequiredMixin, DetailView):
    """Комната"""
    model = ChatDialog
    template_name = 'chat/chat_room.html'
    pk_url_kwarg = 'room_id'

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
        """Создается первое сообщение и для него диалог"""
        chat_dialog = ChatDialog.objects.create()
        message = serializer.save(author=self.request.user, dialog=chat_dialog)
        # В телегу отправляем здесь
        send_telegram(text=f'{message.body}', number=f'{chat_dialog.id}')


@login_required
def detail_dialog(request, pk):
    """Детали диалога для суперпользователя"""
    dialog_messages = ChatMessage.objects.select_related('author').filter(dialog_id=pk)
    users = User.objects.all()
    return render(request, 'chat/detail_dialog.html', {'dialog': dialog_messages, 'users': users})


@login_required
def admin_rating(request):
    """Регистрация нового администратора суперпользователем на главной странице и рейтинг всех админов"""
    rating = Rating.objects.all()
    users = User.objects.filter(is_staff=True)
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            cur_user = User.objects.filter(username=form.cleaned_data['username'])
            if len(cur_user) != 0:
                user = cur_user[0]
                User.objects.filter(username=form.cleaned_data['username']).update(is_staff=True)
                messages.add_message(request, messages.SUCCESS, 'Успешно добавлено!')
                return render(request, 'chat/admin_list.html', {'users': users, 'form': form})
            else:
                return redirect('register')
    else:
        form = StaffForm()
    return render(request, 'chat/admin_list.html', {'form': form, 'users': users})


@login_required
def admin_detail(request, slug):
    """Страница суперпользователя с рейтингом админа"""
    user = User.objects.get(username=slug)

    chat_messages = ChatMessage.objects.filter(author_id=user.id)
    dialogs = set()
    for message in chat_messages:
        dialogs.add(message.dialog)
    return render(request, 'chat/admin_detail.html', {'user': user, 'dialogs': dialogs})

@login_required
def admin_delete(request, slug):
    """Удаление администратора суперпользователем на главной странице"""
    user = User.objects.get(username=slug)
    users = User.objects.filter(is_staff=True)
    user.is_staff = False
    user.save()
    return redirect('admin_rating')



