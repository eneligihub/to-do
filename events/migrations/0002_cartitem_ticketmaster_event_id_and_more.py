# Generated by Django 5.0.7 on 2024-08-21 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='ticketmaster_event_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='ticketmaster_event_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]