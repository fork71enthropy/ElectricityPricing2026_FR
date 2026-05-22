from django.db import models

class SpotPrice(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price_eur_mwh = models.FloatField()
    volume_mw = models.FloatField()

    class Meta:
        unique_together = ('start_date', 'end_date')
        ordering = ['start_date']

    def __str__(self):
        return f"{self.start_date} — {self.price_eur_mwh} €/MWh"