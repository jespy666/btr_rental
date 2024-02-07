# Generated by Django 4.2.6 on 2024-01-26 07:52

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_siteuser_username'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='siteuser',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AlterField(
            model_name='siteuser',
            name='emails',
            field=models.EmailField(max_length=50, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='siteuser',
            name='first_name',
            field=models.CharField(max_length=40, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='siteuser',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True, verbose_name='Phone'),
        ),
        migrations.AlterField(
            model_name='siteuser',
            name='status',
            field=models.CharField(blank=True, choices=[('Newbie', 'Newbie'), ('Amateur', 'Amateur'), ('Professional', 'Professional'), ('Master', 'Master')], max_length=20, verbose_name='Level'),
        ),
        migrations.AlterField(
            model_name='siteuser',
            name='username',
            field=models.CharField(max_length=40, unique=True, verbose_name='Username, Phone or Email'),
        ),
    ]
