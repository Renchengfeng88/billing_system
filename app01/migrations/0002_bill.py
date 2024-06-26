# Generated by Django 4.2.11 on 2024-03-27 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
                ('income', models.IntegerField(max_length=32)),
                ('note', models.CharField(max_length=32)),
                ('number', models.FloatField()),
                ('year', models.IntegerField(max_length=4)),
                ('month', models.IntegerField(max_length=2)),
                ('day', models.IntegerField(max_length=2)),
                ('type', models.CharField(max_length=32)),
                ('UserID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.user')),
            ],
        ),
    ]
