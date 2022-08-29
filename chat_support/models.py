from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models

from chat_support.validator import username_validator


class StarChoises(models.IntegerChoices):
    ONE = 1, 'одна звезда'
    TWO = 2, 'две звезды'
    THREE = 3, 'три звезды'
    FOUR = 4, 'четыре звезды'
    FIFE = 5, 'пять звезд'


class RatingStar(models.Model):
    value = models.PositiveSmallIntegerField('значение', default=StarChoises.ONE, choices=StarChoises.choices)

    def __str__(self):
        return f'{self.value}'

    class Meta:
        verbose_name = 'Звезда'
        verbose_name_plural = 'Звезды'


class User(AbstractUser):

    username = models.CharField('табельный номер', validators=[username_validator], max_length=13, unique=True)

    def __str__(self):
        return self.username

    def get_rating(self):
        chat_messages = self.user_messages.all()
        dialogs = set()
        [dialogs.add(m.dialog) for m in chat_messages]
        stars_1 = []
        stars_2 = []
        for dialog in dialogs:
            for rating in dialog.ratings.all():
                stars_1.append(rating.star_1.value)
                stars_2.append(rating.star_2.value)
        if len(stars_1) and len(stars_2):
            star_1_total = str(Decimal(str(sum(stars_1))) / Decimal(str(len(stars_1))))

            star_2_total = str(Decimal(str(sum(stars_2))) / Decimal(str(len(stars_2))))
            return f'{star_1_total}, {star_2_total}'
        return 'Нет рейтинга'


class ChatDialog(models.Model):
    start_date = models.DateTimeField('Дата создания', auto_now=True)
    is_active = models.BooleanField('Активность', default=True)

    def __str__(self):
        return f'{self.start_date}'

    def check_active(self):
        return self.ratings.count()

    class Meta:
        verbose_name = 'Диалог'
        verbose_name_plural = 'Диалоги'


class ChatMessage(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь',
                               related_name='user_messages')
    dialog = models.ForeignKey(ChatDialog, on_delete=models.CASCADE, verbose_name='диалог',
                               related_name='dialog_messages')
    create_at = models.DateTimeField('Дата', auto_now=True)
    body = models.TextField('Текст обращения')

    def __str__(self):
        return f'{self.author} - {self.body} - {self.dialog}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Rating(models.Model):
    dialog = models.ForeignKey(ChatDialog, on_delete=models.CASCADE, verbose_name='диалог, который оцениваем',
                               related_name='ratings')
    star_1 = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name='звезда_1', related_name='star_1',
                               default='1')
    star_2 = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name='звезда_2', related_name='star_2',
                               default='1')
    star_3 = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name='звезда_3', related_name='star_3',
                               default='1')
    rated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='кем поизведена оценка',
                                 related_name="user_rating")
    comment = models.TextField('комментарии', max_length=200, blank=True)

    is_actives = models.BooleanField('Активность', default=True)

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
        unique_together = ('star_1', 'star_2', 'dialog')

    def __str__(self):
        return f'{self.star_1} - {self.star_2}'
