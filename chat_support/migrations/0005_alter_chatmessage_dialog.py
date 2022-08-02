# Generated by Django 4.0.6 on 2022-08-01 20:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat_support', '0004_chatdialog_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='dialog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat_support.chatdialog', verbose_name='диалог'),
        ),
    ]
