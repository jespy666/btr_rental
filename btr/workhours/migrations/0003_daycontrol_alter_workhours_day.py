# Generated by Django 4.2.6 on 2024-03-25 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workhours', '0002_alter_workhours_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayControl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Date')),
                ('open', models.TimeField(blank=True, verbose_name='Open hours')),
                ('close', models.TimeField(blank=True, verbose_name='Close hours')),
                ('is_closed', models.BooleanField(default=False, verbose_name='All day closed')),
            ],
            options={
                'verbose_name': 'Days setting',
                'verbose_name_plural': 'Days settings',
            },
        ),
        migrations.AlterField(
            model_name='workhours',
            name='day',
            field=models.CharField(choices=[('Workday', 'Working day'), ('Weekend', 'Weekend day')], max_length=7, verbose_name='Weekday'),
        ),
    ]