# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-15 01:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FileSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'file_system',
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('format', models.PositiveSmallIntegerField(default=1)),
                ('type', models.CharField(choices=[('0', 'Verification of Linux kernel modules'), ('3', 'Validation on commits in Linux kernel Git repositories')], default='0', max_length=1)),
                ('version', models.PositiveSmallIntegerField(default=1)),
                ('change_date', models.DateTimeField(auto_now=True)),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('status', models.CharField(choices=[('0', 'Not solved'), ('1', 'Pending'), ('2', 'Is solving'), ('3', 'Solved'), ('4', 'Failed'), ('5', 'Corrupted'), ('6', 'Cancelled')], default='0', max_length=1)),
                ('light', models.BooleanField(default=False)),
                ('change_author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='jobs.Job')),
            ],
            options={
                'db_table': 'job',
            },
        ),
        migrations.CreateModel(
            name='JobFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash_sum', models.CharField(db_index=True, max_length=255)),
                ('file', models.FileField(upload_to='Job')),
            ],
            options={
                'db_table': 'job_file',
            },
        ),
        migrations.CreateModel(
            name='JobHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('version', models.PositiveSmallIntegerField()),
                ('change_date', models.DateTimeField()),
                ('comment', models.CharField(default='', max_length=255)),
                ('global_role', models.CharField(choices=[('0', 'No access'), ('1', 'Observer'), ('2', 'Expert'), ('3', 'Observer and Operator'), ('4', 'Expert and Operator')], default='0', max_length=1)),
                ('description', models.TextField(default='')),
                ('change_author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='jobhistory', to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='jobs.Job')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='jobs.Job')),
            ],
            options={
                'db_table': 'jobhistory',
            },
        ),
        migrations.CreateModel(
            name='RunHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('status', models.CharField(choices=[('0', 'Not solved'), ('1', 'Pending'), ('2', 'Is solving'), ('3', 'Solved'), ('4', 'Failed'), ('5', 'Corrupted'), ('6', 'Cancelled')], max_length=1)),
                ('configuration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.JobFile')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.Job')),
                ('operator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'job_run_history',
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('0', 'No access'), ('1', 'Observer'), ('2', 'Expert'), ('3', 'Observer and Operator'), ('4', 'Expert and Operator')], max_length=1)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.JobHistory')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_job_role',
            },
        ),
        migrations.AddField(
            model_name='filesystem',
            name='file',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobs.JobFile'),
        ),
        migrations.AddField(
            model_name='filesystem',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.JobHistory'),
        ),
        migrations.AddField(
            model_name='filesystem',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='jobs.FileSystem'),
        ),
    ]
