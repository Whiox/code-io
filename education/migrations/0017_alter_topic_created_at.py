# Generated by Django 5.1.5 on 2025-05-02 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0016_topic_author_topic_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
