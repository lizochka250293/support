from django.contrib.auth.models import AbstractUser
from django.db import models


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

    def __str__(self):
        return self.username


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
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь', related_name='user')
    dialog = models.ForeignKey(ChatDialog, on_delete=models.CASCADE, verbose_name='диалог', related_name='messages')
    create_at = models.DateTimeField('Дата', auto_now=True)
    body = models.TextField('Текст обращения')

    def __str__(self):
        return f'{self.author} - {self.body} - {self.dialog}'


    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Rating(models.Model):
    dialog = models.ForeignKey(ChatDialog, on_delete=models.CASCADE, verbose_name='диалог, который оцениваем', related_name='ratings')
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
        return f'{self.star_1} \n {self.star_2} \n {self.star_3}'
