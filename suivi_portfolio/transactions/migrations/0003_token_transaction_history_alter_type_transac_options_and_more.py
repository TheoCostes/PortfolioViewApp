# Generated by Django 4.1 on 2023-07-27 09:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transactions', '0002_type_transac'),
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('symbole', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name_plural': 'token',
            },
        ),
        migrations.CreateModel(
            name='Transaction_history',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_transaction', models.CharField(default='Swap', max_length=100)),
                ('amount1', models.FloatField()),
                ('type_actif1', models.CharField(max_length=100)),
                ('token1', models.CharField(max_length=20)),
                ('description1', models.CharField(max_length=150)),
                ('amount2', models.FloatField(blank=True, default=0.0, null=True)),
                ('type_actif2', models.CharField(default=None, max_length=100)),
                ('token2', models.CharField(default=None, max_length=20)),
                ('description2', models.CharField(default=None, max_length=150)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterModelOptions(
            name='type_transac',
            options={'verbose_name_plural': 'Type Transactions'},
        ),
        migrations.DeleteModel(
            name='Transaction',
        ),
    ]