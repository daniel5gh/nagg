# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nagg', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsItemCollection',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.TextField()),
                ('metadata', django_pgjson.fields.JsonBField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='NewsItemCollectionMembership',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('data', django_pgjson.fields.JsonBField(default=dict)),
                ('newsitem', models.ForeignKey(to='nagg.NewsItem')),
                ('newsitemcollection', models.ForeignKey(to='nagg.NewsItemCollection')),
            ],
        ),
        migrations.AddField(
            model_name='newsitemcollection',
            name='items',
            field=models.ManyToManyField(through='nagg.NewsItemCollectionMembership', to='nagg.NewsItem'),
        ),
    ]
