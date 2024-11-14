# Generated by Django 5.1.1 on 2024-11-14 05:38

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
            name='GithubPolling',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_polled', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('host', models.URLField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('follow_status', models.CharField(choices=[('OUTGOING', 'OUTGOING'), ('INCOMING', 'INCOMING')], max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('url_id', models.URLField(primary_key=True, serialize=False)),
                ('displayName', models.CharField(max_length=100)),
                ('host', models.URLField()),
                ('github', models.URLField(blank=True, null=True)),
                ('profileImage', models.URLField()),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('title', models.CharField(max_length=200)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('url_id', models.URLField()),
                ('description', models.TextField()),
                ('contentType', models.CharField(choices=[('text/commonmark', 'text/commonmark'), ('text/plain', 'text/plain'), ('application/base64', 'application/base64'), ('image/png;base64', 'image/png;base64'), ('image/jpeg;base64', 'image/jpeg;base64')], default='text/plain', max_length=50)),
                ('content', models.TextField()),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('visibility', models.CharField(choices=[('PUBLIC', 'PUBLIC'), ('FRIENDS', 'FRIENDS'), ('UNLISTED', 'UNLISTED'), ('DELETED', 'DELETED')], default='PUBLIC', max_length=20)),
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
                ('url_id', models.URLField()),
                ('comment', models.TextField()),
                ('contentType', models.CharField(choices=[('text/commonmark', 'text/commonmark'), ('text/plain', 'text/plain'), ('application/base64', 'application/base64'), ('image/png;base64', 'image/png;base64'), ('image/jpeg;base64', 'image/jpeg;base64')], default='text/markdown', max_length=50)),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chartreuse.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chartreuse.user')),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('url_id', models.URLField()),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chartreuse.comment')),
                ('post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chartreuse.post')),
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
