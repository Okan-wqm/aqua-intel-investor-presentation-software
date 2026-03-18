from django.db import models
from django.contrib.auth.models import User


class WQSystem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wq_systems')
    name = models.CharField(max_length=100, default='System 1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # V, T, S
    volume = models.FloatField(default=1000.0)
    temperature = models.FloatField(default=25.0)
    salinity = models.FloatField(default=35.0)

    # Waypoints
    initial_ph = models.FloatField(default=7.50)
    initial_alk = models.FloatField(default=2.00)
    target_ph = models.FloatField(default=8.20)
    target_alk = models.FloatField(default=3.20)

    # Limits
    tan = models.FloatField(default=1.0)
    uia_limit = models.FloatField(default=0.02)
    co2_limit = models.FloatField(default=15.0)

    # Ca & Omega
    calcium = models.FloatField(default=412.0)

    # Reagents
    reagent1 = models.CharField(max_length=20, default='nahco3')
    reagent2 = models.CharField(max_length=20, default='naoh')

    # Display
    show_uia = models.BooleanField(default=True)
    show_co2 = models.BooleanField(default=True)
    show_omega = models.BooleanField(default=True)
    show_adjust = models.BooleanField(default=True)
    show_ph_major = models.BooleanField(default=True)
    show_ph_minor = models.BooleanField(default=True)
    dic_max = models.FloatField(default=6.0)
    alk_max = models.FloatField(default=6.0)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.name} ({self.user.username})'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'volume': self.volume,
            'temperature': self.temperature,
            'salinity': self.salinity,
            'initial_ph': self.initial_ph,
            'initial_alk': self.initial_alk,
            'target_ph': self.target_ph,
            'target_alk': self.target_alk,
            'tan': self.tan,
            'uia_limit': self.uia_limit,
            'co2_limit': self.co2_limit,
            'calcium': self.calcium,
            'reagent1': self.reagent1,
            'reagent2': self.reagent2,
            'show_uia': self.show_uia,
            'show_co2': self.show_co2,
            'show_omega': self.show_omega,
            'show_adjust': self.show_adjust,
            'show_ph_major': self.show_ph_major,
            'show_ph_minor': self.show_ph_minor,
            'dic_max': self.dic_max,
            'alk_max': self.alk_max,
        }
