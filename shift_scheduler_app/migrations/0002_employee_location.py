# Generated by Django 5.0 on 2023-12-08 18:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shift_scheduler_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='shift_scheduler_app.location'),
        ),
    ]