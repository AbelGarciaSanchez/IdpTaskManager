# Generated by Django 5.1.3 on 2024-12-16 08:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0012_alter_task_deadline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
