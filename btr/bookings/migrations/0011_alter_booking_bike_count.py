# Generated by Django 4.2.6 on 2024-02-06 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0010_alter_booking_options_alter_booking_booking_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='bike_count',
            field=models.CharField(max_length=2, verbose_name='bikes in rent'),
        ),
    ]
