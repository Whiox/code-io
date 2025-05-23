# Generated by Django 5.1.3 on 2025-05-14 20:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0022_courseprogress'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='courses',
            name='author',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='my_courses', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
