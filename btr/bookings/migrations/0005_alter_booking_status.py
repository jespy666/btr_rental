# Generated by Django 4.2.6 on 2024-01-24 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_alter_booking_bike_count_alter_booking_booking_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('ожидает подтверждения', 'ожидает подтверждения'), ('подтверждено', 'принят'), ('завершен', 'завершен'), ('отменен', 'отменен')], max_length=40, verbose_name='Статус'),
        ),
    ]
