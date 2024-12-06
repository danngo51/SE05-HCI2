# Generated by Django 5.1.3 on 2024-12-04 17:23

import django.db.models.deletion
import pgvector.django.vector
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_recipe_minutes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Embedded_Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embedding', pgvector.django.vector.VectorField(dimensions=1536)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='embedded_ingredient', to='recipes.ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='Embedded_Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embedding', pgvector.django.vector.VectorField(dimensions=1536)),
                ('recipe', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='embedded_recipe', to='recipes.recipe')),
            ],
        ),
    ]