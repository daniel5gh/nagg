# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djorm_pgfulltext.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nagg', '0002_auto_20151020_2239'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsitem',
            name='search_index',
            field=djorm_pgfulltext.fields.VectorField(null=True, serialize=False, editable=False, default='', db_index=True),
        ),
    ]
