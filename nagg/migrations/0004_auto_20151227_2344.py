# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djorm_pgfulltext.fields


class Migration(migrations.Migration):

    dependencies = [
        ('nagg', '0003_newsitem_search_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsitem',
            name='search_index',
            field=djorm_pgfulltext.fields.VectorField(),
        ),
    ]
