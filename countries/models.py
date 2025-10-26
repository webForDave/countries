from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=256, null=False)
    capital = models.CharField(max_length=256, null=True)
    region = models.CharField(max_length=256, null=True)
    population = models.IntegerField(default=0, null=False)
    currency_code = models.CharField(max_length=5, null=True)
    exchange_rate = models.FloatField(null=True)
    estimated_gdp = models.FloatField(default=0, null=True)
    flag_url = models.CharField(max_length=512, null=True)
    last_refreshed_at = models.DateTimeField(null=False)