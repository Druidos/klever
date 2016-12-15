# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-15 01:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import reports.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jobs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'attr',
            },
        ),
        migrations.CreateModel(
            name='AttrName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=63, unique=True)),
            ],
            options={
                'db_table': 'attr_name',
            },
        ),
        migrations.CreateModel(
            name='AttrStatistic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('safes', models.PositiveIntegerField(default=0)),
                ('unsafes', models.PositiveIntegerField(default=0)),
                ('unknowns', models.PositiveIntegerField(default=0)),
                ('attr', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='reports.Attr')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.AttrName')),
            ],
            options={
                'db_table': 'cache_report_attr_statistic',
            },
        ),
        migrations.CreateModel(
            name='CompareJobsCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attr_values', models.TextField(db_index=True)),
                ('verdict1', models.CharField(choices=[('0', 'Total safe'), ('1', 'Found all unsafes'), ('2', 'Found not all unsafes'), ('3', 'Unknown'), ('4', 'Unmatched')], max_length=1)),
                ('verdict2', models.CharField(choices=[('0', 'Total safe'), ('1', 'Found all unsafes'), ('2', 'Found not all unsafes'), ('3', 'Unknown'), ('4', 'Unmatched')], max_length=1)),
                ('reports1', models.CharField(max_length=1000)),
                ('reports2', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'cache_report_jobs_compare',
            },
        ),
        migrations.CreateModel(
            name='CompareJobsInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('files_diff', models.TextField()),
            ],
            options={
                'db_table': 'cache_report_jobs_compare_info',
            },
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, unique=True)),
            ],
            options={
                'db_table': 'component',
            },
        ),
        migrations.CreateModel(
            name='ComponentResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpu_time', models.BigIntegerField()),
                ('wall_time', models.BigIntegerField()),
                ('memory', models.BigIntegerField()),
                ('component', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='reports.Component')),
            ],
            options={
                'db_table': 'cache_report_component_resource',
            },
        ),
        migrations.CreateModel(
            name='ComponentUnknown',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(default=0)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Component')),
            ],
            options={
                'db_table': 'cache_report_component_unknown',
            },
        ),
        migrations.CreateModel(
            name='Computer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'computer',
            },
        ),
        migrations.CreateModel(
            name='LightResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpu_time', models.BigIntegerField()),
                ('wall_time', models.BigIntegerField()),
                ('memory', models.BigIntegerField()),
                ('component', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='reports.Component')),
            ],
            options={
                'db_table': 'cache_report_light_resource',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'db_table': 'report',
            },
        ),
        migrations.CreateModel(
            name='ReportAttr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Attr')),
            ],
            options={
                'db_table': 'report_attrs',
            },
        ),
        migrations.CreateModel(
            name='ReportComponentLeaf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'cache_report_component_leaf',
            },
        ),
        migrations.CreateModel(
            name='ReportRoot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('safes', models.PositiveIntegerField(default=0)),
                ('job', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='jobs.Job')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'report_root',
            },
        ),
        migrations.CreateModel(
            name='Verdict',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unsafe', models.PositiveIntegerField(default=0)),
                ('unsafe_bug', models.PositiveIntegerField(default=0)),
                ('unsafe_target_bug', models.PositiveIntegerField(default=0)),
                ('unsafe_false_positive', models.PositiveIntegerField(default=0)),
                ('unsafe_unknown', models.PositiveIntegerField(default=0)),
                ('unsafe_unassociated', models.PositiveIntegerField(default=0)),
                ('unsafe_inconclusive', models.PositiveIntegerField(default=0)),
                ('safe', models.PositiveIntegerField(default=0)),
                ('safe_missed_bug', models.PositiveIntegerField(default=0)),
                ('safe_incorrect_proof', models.PositiveIntegerField(default=0)),
                ('safe_unknown', models.PositiveIntegerField(default=0)),
                ('safe_unassociated', models.PositiveIntegerField(default=0)),
                ('safe_inconclusive', models.PositiveIntegerField(default=0)),
                ('unknown', models.PositiveIntegerField(default=0)),
            ],
            options={
                'db_table': 'cache_report_verdict',
            },
        ),
        migrations.CreateModel(
            name='ReportComponent',
            fields=[
                ('report_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='reports.Report')),
                ('cpu_time', models.BigIntegerField(null=True)),
                ('wall_time', models.BigIntegerField(null=True)),
                ('memory', models.BigIntegerField(null=True)),
                ('start_date', models.DateTimeField()),
                ('finish_date', models.DateTimeField(null=True)),
                ('log', models.CharField(max_length=128, null=True)),
                ('archive', models.FileField(null=True, upload_to=reports.models.get_component_path)),
                ('data', models.FileField(null=True, upload_to=reports.models.get_component_path)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Component')),
                ('computer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Computer')),
            ],
            options={
                'db_table': 'report_component',
            },
            bases=('reports.report',),
        ),
        migrations.CreateModel(
            name='ReportSafe',
            fields=[
                ('report_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='reports.Report')),
                ('archive', models.FileField(null=True, upload_to='Safes/%Y/%m')),
                ('proof', models.CharField(max_length=128, null=True)),
                ('verdict', models.CharField(choices=[('0', 'Unknown'), ('1', 'Incorrect proof'), ('2', 'Missed target bug'), ('3', 'Incompatible marks'), ('4', 'Without marks')], default='4', max_length=1)),
            ],
            options={
                'db_table': 'report_safe',
            },
            bases=('reports.report',),
        ),
        migrations.CreateModel(
            name='ReportUnknown',
            fields=[
                ('report_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='reports.Report')),
                ('archive', models.FileField(upload_to='Unknowns/%Y/%m')),
                ('problem_description', models.CharField(max_length=128)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Component')),
            ],
            options={
                'db_table': 'report_unknown',
            },
            bases=('reports.report',),
        ),
        migrations.CreateModel(
            name='ReportUnsafe',
            fields=[
                ('report_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='reports.Report')),
                ('archive', models.FileField(upload_to='Unsafes/%Y/%m')),
                ('error_trace', models.CharField(max_length=128)),
                ('verdict', models.CharField(choices=[('0', 'Unknown'), ('1', 'Bug'), ('2', 'Target bug'), ('3', 'False positive'), ('4', 'Incompatible marks'), ('5', 'Without marks')], default='5', max_length=1)),
            ],
            options={
                'db_table': 'report_unsafe',
            },
            bases=('reports.report',),
        ),
        migrations.AddField(
            model_name='reportattr',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attrs', to='reports.Report'),
        ),
        migrations.AddField(
            model_name='report',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='reports.Report'),
        ),
        migrations.AddField(
            model_name='report',
            name='root',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.ReportRoot'),
        ),
        migrations.AddField(
            model_name='lightresource',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.ReportRoot'),
        ),
        migrations.AddField(
            model_name='comparejobsinfo',
            name='root1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='reports.ReportRoot'),
        ),
        migrations.AddField(
            model_name='comparejobsinfo',
            name='root2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='reports.ReportRoot'),
        ),
        migrations.AddField(
            model_name='comparejobsinfo',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comparejobscache',
            name='info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.CompareJobsInfo'),
        ),
        migrations.AddField(
            model_name='attr',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.AttrName'),
        ),
        migrations.AddField(
            model_name='verdict',
            name='report',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='reports.ReportComponent'),
        ),
        migrations.AddField(
            model_name='reportcomponentleaf',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leaves', to='reports.ReportComponent'),
        ),
        migrations.AddField(
            model_name='reportcomponentleaf',
            name='safe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='leaves', to='reports.ReportSafe'),
        ),
        migrations.AddField(
            model_name='reportcomponentleaf',
            name='unknown',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='leaves', to='reports.ReportUnknown'),
        ),
        migrations.AddField(
            model_name='reportcomponentleaf',
            name='unsafe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='leaves', to='reports.ReportUnsafe'),
        ),
        migrations.AddField(
            model_name='componentunknown',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unknowns_cache', to='reports.ReportComponent'),
        ),
        migrations.AddField(
            model_name='componentresource',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources_cache', to='reports.ReportComponent'),
        ),
        migrations.AlterIndexTogether(
            name='comparejobscache',
            index_together=set([('info', 'verdict1', 'verdict2')]),
        ),
        migrations.AddField(
            model_name='attrstatistic',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.ReportComponent'),
        ),
        migrations.AlterIndexTogether(
            name='attr',
            index_together=set([('name', 'value')]),
        ),
    ]
