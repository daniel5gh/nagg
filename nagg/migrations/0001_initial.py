# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('source', models.TextField()),
                ('url', models.URLField()),
                ('text', models.TextField()),
                ('publish_date', models.DateTimeField()),
                ('retrieval_date', models.DateTimeField()),
            ],
        ),
    ]
