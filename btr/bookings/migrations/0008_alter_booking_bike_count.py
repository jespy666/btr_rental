# Generated by Django 4.2.6 on 2024-02-06 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0007_alter_booking_bike_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='bike_count',
            field=models.IntegerField(verbose_name='bikes in rent'),
        ),
    ]
