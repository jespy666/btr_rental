# Generated by Django 4.2.6 on 2024-02-02 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0006_alter_booking_options_alter_booking_bike_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='bike_count',
            field=models.IntegerField(verbose_name='bikes count'),
        ),
    ]
