# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Specie(models.Model):
    specie_id = models.IntegerField()
    specie_head = models.CharField(max_length=250)


class SpecieData(models.Model):
    specie = models.ForeignKey(Specie, on_delete=models.CASCADE)
    triplet = models.CharField(max_length=3)
    amino_acid = models.CharField(max_length=1)
    fraction = models.FloatField()
    frequency = models.FloatField()
