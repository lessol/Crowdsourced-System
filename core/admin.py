from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.passenger)
admin.site.register(models.driver)
admin.site.register(models.VehicleType)
admin.site.register(models.Spot)
admin.site.register(models.Transaction)