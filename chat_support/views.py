from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites import requests
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

from chat_support.forms import RegisterUserForm, Auntification, RatingForm, PasswordReset, StaffForm
from chat_support.models import ChatMessage, ChatDialog, User, Rating
from chat_support.serializers import ChatMessageSerializer


def login_out(reguest):
    logout(reguest)
    return redirect('title')


# титульная страница авторизации

class LoginViewList(LoginView):
    form_class = Auntification
    template_name = 'chat/number.html'

    # def get_success_url(self):
    #     user = self.request.POST.get('username')
    #     print(user)
    #     return reverse('question')

# класс перехода с кнопкой задать вопрос
def question(request):
    name = request.user.username
    print(type(name))
    if name == '308':
        print('ok')
        return redirect('admin_rating')
    else:
        context = {'room_id': name}
        return render(request=request, template_name='chat/question.html', context=context)


# регистрация
class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'chat/register.html'
    success_url = reverse_lazy('title')




def passwordreset(request):
    if request.method == 'POST':
        form = PasswordReset(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password_1 = form.cleaned_data['password_1']
            if password != password_1:
                raise TypeError('Пароли не совпадают.')
            user = User.objects.get(username=username)
            if user is None:
                raise TypeError('Пользователь не найден. Введите кооректно табельный номер.')
            user.set_password(password)
            user.save(update_fields=["password"])
            return redirect('title')
    else:
        form = PasswordReset()
    return render(request, 'chat/password_reset.html', {'form': form})

# класс личного кабинета
class PersonalArea(LoginRequiredMixin, FormMixin, ListView):
    model = ChatMessage
    template_name = 'chat/index.html'
    context_object_name = "messages"
    form_class = RatingForm

    # формируем сообщения для оценки
    def get_queryset(self):
        """формируем сообщения для оценки"""
        return ChatMessage.objects.filter(author=self.request.user).order_by("-create_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dialogs_not_active = ChatDialog.objects.filter(is_active=False, messages__author=self.request.user).distinct()
        dialogs_active = ChatDialog.objects.filter(is_active=True, messages__author=self.request.user).distinct()
        all_dialogs = ChatDialog.objects.filter(is_active=True)
        rating = Rating.objects.all()
        context['dialogs'] = dialogs_not_active
        context['dialogs_active'] = dialogs_active
        context['all_dialogs'] = all_dialogs
        context['rating'] = rating
        return context

    def get_success_url(self):
        return reverse('index')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        return self.form_valid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        dialod_id = self.request.POST.get('dialog')
        print(dialod_id)
        dialog = get_object_or_404(ChatDialog, id=dialod_id)
        self.object.dialog = dialog
        self.object.is_actives = False
        self.object.save()
        return super().form_valid(form)


# класс комнаты
class PersonalRoom(LoginRequiredMixin, DetailView):
    model = ChatDialog
    template_name = 'chat/room.html'
    pk_url_kwarg = 'room_id'

    # получаем контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = ChatMessage.objects.filter(dialog=self.get_object())
        print(context['messages'])
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
        # send_telegram(text=f'{message.body}', number=f'{chat_dialog.id}')

def detail_dialog(request, pk):
    dialog = ChatMessage.objects.filter(dialog_id=pk)
    print(dialog)
    return render(request, 'chat/detail_dialog.html', {'dialog': dialog})
#как сделать выплывающее окно что все ок?
def admin_rating(request):
    rating = Rating.objects.all()
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            cur_user = User.objects.filter(username=form.cleaned_data['username'])
            user = cur_user[0]
            if user:
                user_is_staff = User.objects.filter(username=form.cleaned_data['username']).update(is_staff=True)
                print('ok')
                return render(request, 'chat/admin_list.html', {'rating': rating, 'form': form})
            else:
                pass
    else:
        form = StaffForm()
        staff = User.objects.filter(is_staff=True)
        dict_staff = {}
        for user_staff in staff:
            dict_staff[user_staff.id] = []
            dialog = ChatMessage.objects.filter(author_id=user_staff.id)
            for i in dialog:
                dict_staff[user_staff.id].append(i.dialog_id)
        rating = Rating.objects.all()
        dict_star = {}
        for i in rating:
            dict_star[i.dialog_id]=[i.star_1_id, i.star_2_id]
        star = {}
        for k, v in dict_staff.items():
            star[k] = []
            for i in v:
                if i in dict_star:
                    star[k].append(dict_star[i])
        total = {}
        for k, v in star.items():
            total[k] = []
            total[k].append([sum(x)/len(v) for x in zip(*v)])
        user = User.objects.all()
        dict_user = {}
        for i in user:
            dict_user[i.id]=i.username
        total_user = {}
        for k, v in total.items():
            for i, n in dict_user.items():
                if k == i:
                    total_user[dict_user[i]] = v
        print(total_user)
        return render(request, 'chat/admin_list.html', {'rating': total_user, 'form': form})

def admin_detail(request, slug):
    user = User.objects.get(username=slug)
    print(user.id)
    dialog = ChatMessage.objects.filter(author_id=user.id)
    dict_dialog = {}
    for i in dialog:
        dict_dialog[i.dialog_id]=[]
        print(i.dialog_id)
        rating = Rating.objects.get(dialog_id=i.dialog_id)
        print(rating.star_1_id)
        dict_dialog[i.dialog_id].append(rating.star_1_id)
        dict_dialog[i.dialog_id].append(rating.star_2_id)
    print(dict_dialog)
    return render(request, 'chat/admin_detail.html', {'user': user, 'dict_dialog': dict_dialog})



# def send_telegram(text: str, number: str):
#     api_token = ""
#     url = "https://api.telegram.org/bot"
#     channel_id = ""
#     url += api_token
#     method = url + "/sendMessage"
#     to_send = f'{text}, http://127.0.0.1:8000/chat/{number}/'
#     r = requests.post(method, data={
#         "chat_id": channel_id,
#         "text": to_send
#     })
