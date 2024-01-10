# Generated by Django 4.2.6 on 2024-01-04 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteuser',
            name='status',
            field=models.CharField(blank=True, choices=[('Newbie', 'Newbie'), ('Amateur', 'Amateur'), ('Professional', 'Professional'), ('Master', 'Master')], max_length=20, verbose_name='Level'),
        ),
    ]