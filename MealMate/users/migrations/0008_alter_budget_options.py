# Generated by Django 5.1.3 on 2024-12-04 05:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_budget_alter_userprofile_budget'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='budget',
            options={'verbose_name': 'Budget', 'verbose_name_plural': 'Budgets'},
        ),
    ]
