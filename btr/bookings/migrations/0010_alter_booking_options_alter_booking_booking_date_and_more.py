# Generated by Django 4.2.6 on 2024-02-06 07:53

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0009_alter_booking_options_alter_booking_booking_date_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='booking',
            options={'verbose_name': 'Booking', 'verbose_name_plural': 'Bookings'},
        ),
        migrations.AlterField(
            model_name='booking',
            name='booking_date',
            field=models.DateField(verbose_name='Book day'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='end_time',
            field=models.TimeField(verbose_name='Time of end'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='foreign_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name="Client's phone"),
        ),
        migrations.AlterField(
            model_name='booking',
            name='start_time',
            field=models.TimeField(verbose_name='Time of start'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('pending', 'wait to confirm'), ('confirmed', 'accepted'), ('completed', 'finished'), ('canceled', 'canceled')], max_length=40, verbose_name='Status'),
        ),
    ]
