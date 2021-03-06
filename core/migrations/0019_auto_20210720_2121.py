# Generated by Django 3.1.3 on 2021-07-20 21:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0018_auto_20210720_1933'),
    ]

    operations = [
        migrations.CreateModel(
            name='passenger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='passenger/avatars/')),
                ('phone_number', models.CharField(blank=True, max_length=50)),
                ('stripe_passenger_id', models.CharField(blank=True, max_length=255)),
                ('stripe_payment_method_id', models.CharField(blank=True, max_length=255)),
                ('stripe_card_last4', models.CharField(blank=True, max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='spot',
            name='tenant',
        ),
        migrations.DeleteModel(
            name='Tenant',
        ),
        migrations.AddField(
            model_name='spot',
            name='passenger',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.passenger'),
        ),
    ]
