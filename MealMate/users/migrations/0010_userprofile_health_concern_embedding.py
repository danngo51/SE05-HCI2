# Generated by Django 5.1.3 on 2024-12-05 17:18

import pgvector.django.vector
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_userprofile_embedding'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='health_concern_embedding',
            field=pgvector.django.vector.VectorField(blank=True, dimensions=1536, null=True),
        ),
    ]
