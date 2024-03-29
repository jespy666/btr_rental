# Generated by Django 4.2.6 on 2024-03-19 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WorkHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('Workday', 'Working day'), ('Weekend', 'Weekend day')], max_length=7)),
                ('open', models.TimeField(verbose_name='Open hours')),
                ('close', models.TimeField(verbose_name='Close hours')),
            ],
        ),
    ]
