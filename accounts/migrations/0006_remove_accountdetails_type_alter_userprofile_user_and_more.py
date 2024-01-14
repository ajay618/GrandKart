# Generated by Django 4.2.5 on 2024-01-01 04:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_userprofile_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountdetails',
            name='type',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='accountdetails',
            name='type',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]