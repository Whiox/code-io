# Generated by Django 5.1.5 on 2025-02-21 07:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('profile_id', models.AutoField(primary_key=True, serialize=False)),
                ('about', models.TextField(default='Не указано')),
                ('email', models.TextField(default='Не указано')),
                ('phone', models.TextField(default='Не указано')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
