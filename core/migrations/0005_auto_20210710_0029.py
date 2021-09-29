# Generated by Django 3.1.3 on 2021-07-10 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_category_spot'),
    ]

    operations = [
        migrations.AddField(
            model_name='spot',
            name='spot_address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='spot',
            name='spot_lat',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='spot',
            name='spot_lng',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='spot',
            name='spot_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='spot',
            name='spot_phone',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
