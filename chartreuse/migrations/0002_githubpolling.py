# Generated by Django 5.1.1 on 2024-10-28 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chartreuse', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GithubPolling',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_polled', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
