# Generated by Django 4.2.6 on 2024-01-23 08:01

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_alter_booking_foreign_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='bike_count',
            field=models.IntegerField(verbose_name='Количество байков'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='booking_date',
            field=models.DateField(verbose_name='День проката'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='end_time',
            field=models.TimeField(verbose_name='Время окончания'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='foreign_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name='Телефон клиента'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='start_time',
            field=models.TimeField(verbose_name='Время начала'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('pending', 'ожидает подтверждения'), ('подтверждено', 'принят'), ('completed', 'завершен'), ('отменен', 'отменен')], max_length=40, verbose_name='Статус'),
        ),
    ]