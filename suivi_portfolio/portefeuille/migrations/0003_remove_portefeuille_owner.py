# Generated by Django 4.1 on 2023-07-27 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portefeuille', '0002_alter_portefeuille_amount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portefeuille',
            name='owner',
        ),
    ]