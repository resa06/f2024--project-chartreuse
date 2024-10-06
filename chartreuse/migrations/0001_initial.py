# Generated by Django 5.1.1 on 2024-10-04 14:22

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
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('displayName', models.CharField(max_length=100)),
                ('host', models.URLField()),
                ('github', models.URLField()),
                ('profileImage', models.URLField()),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('title', models.CharField(max_length=200)),
                ('id', models.URLField(primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('contentType', models.CharField(choices=[('text/markdown', 'text/markdown'), ('text/plain', 'text/plain'), ('application/base64', 'application/base64'), ('image/png;base64', 'image/png;base64'), ('image/jpeg;base64', 'image/jpeg;base64')], default='text/plain', max_length=50)),
                ('content', models.TextField()),
                ('published', models.DateTimeField()),
                ('visibility', models.CharField(choices=[('PUBLIC', 'PUBLIC'), ('FRIENDS', 'FRIENDS'), ('PRIVATE', 'PRIVATE'), ('UNLISTED', 'UNLISTED')], default='PUBLIC', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chartreuse.user')),
            ],
        ),
        migrations.CreateModel(
            name='FollowRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('approved', models.BooleanField(default=False)),
                ('requestee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_requests_received', to='chartreuse.user')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow_requests_sent', to='chartreuse.user')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('comment', models.TextField()),
                ('commentType', models.CharField(choices=[('text/markdown', 'text/markdown'), ('text/plain', 'text/plain'), ('application/base64', 'application/base64'), ('image/png;base64', 'image/png;base64'), ('image/jpeg;base64', 'image/jpeg;base64')], default='text/markdown', max_length=50)),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chartreuse.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chartreuse.user')),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.CharField(default='text/plain', max_length=300)),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chartreuse.user')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('user', 'post'), name='unique_user_post_like')],
            },
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('followed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='chartreuse.user')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to='chartreuse.user')),
            ],
            options={
                'unique_together': {('follower', 'followed')},
            },
        ),
    ]
