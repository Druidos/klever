# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-15 01:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reports', '0001_initial'),
        ('jobs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentMarkUnknownProblem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(default=0)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='reports.Component')),
            ],
            options={
                'db_table': 'cache_report_component_mark_unknown_problem',
            },
        ),
        migrations.CreateModel(
            name='ConvertedTraces',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash_sum', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='Error-traces')),
            ],
            options={
                'db_table': 'file',
            },
        ),
        migrations.CreateModel(
            name='ErrorTraceConvertionCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('converted', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marks.ConvertedTraces')),
            ],
            options={
                'db_table': 'cache_error_trace_converted',
            },
        ),
        migrations.CreateModel(
            name='MarkAssociationsChanges',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('table_data', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cache_mark_associations_changes',
            },
        ),
        migrations.CreateModel(
            name='MarkSafe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('format', models.PositiveSmallIntegerField(default=1)),
                ('version', models.PositiveSmallIntegerField(default=1)),
                ('status', models.CharField(choices=[('0', 'Unreported'), ('1', 'Reported'), ('2', 'Fixed'), ('3', 'Rejected')], default='0', max_length=1)),
                ('is_modifiable', models.BooleanField(default=True)),
                ('change_date', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(default='')),
                ('type', models.CharField(choices=[('0', 'Created'), ('1', 'Preset'), ('2', 'Uploaded')], default='0', max_length=1)),
                ('verdict', models.CharField(choices=[('0', 'Unknown'), ('1', 'Incorrect proof'), ('2', 'Missed target bug')], default='0', max_length=1)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='marksafe', to=settings.AUTH_USER_MODEL)),
                ('job', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='marksafe', to='jobs.Job')),
                ('prime', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prime_marks', to='reports.ReportSafe')),
            ],
            options={
                'db_table': 'mark_safe',
            },
        ),
        migrations.CreateModel(
            name='MarkSafeAttr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_compare', models.BooleanField(default=True)),
                ('attr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Attr')),
            ],
            options={
                'db_table': 'mark_safe_attr',
            },
        ),
        migrations.CreateModel(
            name='MarkSafeHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveSmallIntegerField()),
                ('status', models.CharField(choices=[('0', 'Unreported'), ('1', 'Reported'), ('2', 'Fixed'), ('3', 'Rejected')], default='0', max_length=1)),
                ('change_date', models.DateTimeField()),
                ('comment', models.TextField()),
                ('description', models.TextField()),
                ('verdict', models.CharField(choices=[('0', 'Unknown'), ('1', 'Incorrect proof'), ('2', 'Missed target bug')], max_length=1)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='marksafehistory', to=settings.AUTH_USER_MODEL)),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='marks.MarkSafe')),
            ],
            options={
                'db_table': 'mark_safe_history',
            },
        ),
        migrations.CreateModel(
            name='MarkSafeReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='markreport_set', to='marks.MarkSafe')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='markreport_set', to='reports.ReportSafe')),
            ],
            options={
                'db_table': 'cache_mark_safe_report',
            },
        ),
        migrations.CreateModel(
            name='MarkSafeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark_version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='marks.MarkSafeHistory')),
            ],
            options={
                'db_table': 'cache_mark_safe_tag',
            },
        ),
        migrations.CreateModel(
            name='MarkUnknown',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('format', models.PositiveSmallIntegerField(default=1)),
                ('version', models.PositiveSmallIntegerField(default=1)),
                ('status', models.CharField(choices=[('0', 'Unreported'), ('1', 'Reported'), ('2', 'Fixed'), ('3', 'Rejected')], default='0', max_length=1)),
                ('is_modifiable', models.BooleanField(default=True)),
                ('change_date', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(default='')),
                ('type', models.CharField(choices=[('0', 'Created'), ('1', 'Preset'), ('2', 'Uploaded')], default='0', max_length=1)),
                ('function', models.TextField()),
                ('problem_pattern', models.CharField(max_length=15)),
                ('link', models.URLField(null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='markunknown', to=settings.AUTH_USER_MODEL)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Component')),
                ('job', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='markunknown', to='jobs.Job')),
                ('prime', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prime_marks', to='reports.ReportUnknown')),
            ],
            options={
                'db_table': 'mark_unknown',
            },
        ),
        migrations.CreateModel(
            name='MarkUnknownHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveSmallIntegerField()),
                ('status', models.CharField(choices=[('0', 'Unreported'), ('1', 'Reported'), ('2', 'Fixed'), ('3', 'Rejected')], default='0', max_length=1)),
                ('change_date', models.DateTimeField()),
                ('comment', models.TextField()),
                ('description', models.TextField()),
                ('function', models.TextField()),
                ('problem_pattern', models.CharField(max_length=100)),
                ('link', models.URLField(null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='markunknownhistory', to=settings.AUTH_USER_MODEL)),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='marks.MarkUnknown')),
            ],
            options={
                'db_table': 'mark_unknown_history',
            },
        ),
        migrations.CreateModel(
            name='MarkUnknownReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='markreport_set', to='marks.MarkUnknown')),
            ],
            options={
                'db_table': 'cache_mark_unknown_report',
            },
        ),
        migrations.CreateModel(
            name='MarkUnsafe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True)),
                ('format', models.PositiveSmallIntegerField(default=1)),
                ('version', models.PositiveSmallIntegerField(default=1)),
                ('status', models.CharField(choices=[('0', 'Unreported'), ('1', 'Reported'), ('2', 'Fixed'), ('3', 'Rejected')], default='0', max_length=1)),
                ('is_modifiable', models.BooleanField(default=True)),
                ('change_date', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(default='')),
                ('type', models.CharField(choices=[('0', 'Created'), ('1', 'Preset'), ('2', 'Uploaded')], default='0', max_length=1)),
                ('verdict', models.CharField(choices=[('0', 'Unknown'), ('1', 'Bug'), ('2', 'Target bug'), ('3', 'False positive')], default='0', max_length=1)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='markunsafe', to=settings.AUTH_USER_MODEL)),
                ('error_trace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marks.ConvertedTraces')),
            ],
            options={
                'db_table': 'mark_unsafe',
            },
        ),
        migrations.CreateModel(
            name='MarkUnsafeAttr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_compare', models.BooleanField(default=True)),
                ('attr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Attr')),
            ],
            options={
                'db_table': 'mark_unsafe_attr',
            },
        ),
        migrations.CreateModel(
            name='MarkUnsafeCompare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(default='', max_length=1000)),
            ],
            options={
                'db_table': 'mark_unsafe_compare',
            },
        ),
        migrations.CreateModel(
            name='MarkUnsafeConvert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(default='', max_length=1000)),
            ],
            options={
                'db_table': 'mark_unsafe_convert',
            },
        ),
        migrations.CreateModel(
            name='MarkUnsafeHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.PositiveSmallIntegerField()),
                ('status', models.CharField(choices=[('0', 'Unreported'), ('1', 'Reported'), ('2', 'Fixed'), ('3', 'Rejected')], default='0', max_length=1)),
                ('change_date', models.DateTimeField()),
                ('comment', models.TextField()),
                ('description', models.TextField()),
                ('verdict', models.CharField(choices=[('0', 'Unknown'), ('1', 'Bug'), ('2', 'Target bug'), ('3', 'False positive')], max_length=1)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='markunsafehistory', to=settings.AUTH_USER_MODEL)),
                ('function', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marks.MarkUnsafeCompare')),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='marks.MarkUnsafe')),
            ],
            options={
                'db_table': 'mark_unsafe_history',
            },
        ),
        migrations.CreateModel(
            name='MarkUnsafeReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.FloatField()),
                ('broken', models.BooleanField(default=False)),
                ('error', models.TextField(null=True)),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='markreport_set', to='marks.MarkUnsafe')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='markreport_set', to='reports.ReportUnsafe')),
            ],
            options={
                'db_table': 'cache_mark_unsafe_report',
            },
        ),
        migrations.CreateModel(
            name='MarkUnsafeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark_version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='marks.MarkUnsafeHistory')),
            ],
            options={
                'db_table': 'cache_mark_unsafe_tag',
            },
        ),
        migrations.CreateModel(
            name='ReportSafeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(default=0)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='safe_tags', to='reports.ReportComponent')),
            ],
            options={
                'db_table': 'cache_report_safe_tag',
            },
        ),
        migrations.CreateModel(
            name='ReportUnsafeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(default=0)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unsafe_tags', to='reports.ReportComponent')),
            ],
            options={
                'db_table': 'cache_report_unsafe_tag',
            },
        ),
        migrations.CreateModel(
            name='SafeReportTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(default=0)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='reports.ReportSafe')),
            ],
            options={
                'db_table': 'cache_safe_report_safe_tag',
            },
        ),
        migrations.CreateModel(
            name='SafeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=32)),
                ('description', models.TextField(default='')),
                ('populated', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='marks.SafeTag')),
            ],
            options={
                'db_table': 'mark_safe_tag',
            },
        ),
        migrations.CreateModel(
            name='UnknownProblem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15)),
            ],
            options={
                'db_table': 'cache_mark_unknown_problem',
            },
        ),
        migrations.CreateModel(
            name='UnsafeReportTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(default=0)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='reports.ReportUnsafe')),
            ],
            options={
                'db_table': 'cache_unsafe_report_unsafe_tag',
            },
        ),
        migrations.CreateModel(
            name='UnsafeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=32)),
                ('description', models.TextField(default='')),
                ('populated', models.BooleanField(default=False)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='marks.UnsafeTag')),
            ],
            options={
                'db_table': 'mark_unsafe_tag',
            },
        ),
        migrations.AddField(
            model_name='unsafereporttag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marks.UnsafeTag'),
        ),
        migrations.AddField(
            model_name='safereporttag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marks.SafeTag'),
        ),
        migrations.AddField(
            model_name='reportunsafetag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='marks.UnsafeTag'),
        ),
        migrations.AddField(
            model_name='reportsafetag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='marks.SafeTag'),
        ),
        migrations.AddField(
            model_name='markunsafetag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='marks.UnsafeTag'),
        ),
        migrations.AddField(
            model_name='markunsafeattr',
            name='mark',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attrs', to='marks.MarkUnsafeHistory'),
        ),
        migrations.AddField(
            model_name='markunsafe',
            name='function',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marks.MarkUnsafeCompare'),
        ),
        migrations.AddField(
            model_name='markunsafe',
            name='job',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='markunsafe', to='jobs.Job'),
        ),
        migrations.AddField(
            model_name='markunsafe',
            name='prime',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prime_marks', to='reports.ReportUnsafe'),
        ),
        migrations.AddField(
            model_name='markunknownreport',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marks.UnknownProblem'),
        ),
        migrations.AddField(
            model_name='markunknownreport',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='markreport_set', to='reports.ReportUnknown'),
        ),
        migrations.AddField(
            model_name='marksafetag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='marks.SafeTag'),
        ),
        migrations.AddField(
            model_name='marksafeattr',
            name='mark',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attrs', to='marks.MarkSafeHistory'),
        ),
        migrations.AddField(
            model_name='errortraceconvertioncache',
            name='function',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marks.MarkUnsafeConvert'),
        ),
        migrations.AddField(
            model_name='errortraceconvertioncache',
            name='unsafe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.ReportUnsafe'),
        ),
        migrations.AddField(
            model_name='componentmarkunknownproblem',
            name='problem',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='marks.UnknownProblem'),
        ),
        migrations.AddField(
            model_name='componentmarkunknownproblem',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mark_unknowns_cache', to='reports.ReportComponent'),
        ),
    ]
