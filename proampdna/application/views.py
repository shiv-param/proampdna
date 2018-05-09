# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import application.models as app_models
import application.serializers as app_serializers
import application.utility as app_utility
import json
import math
from rest_framework import permissions, viewsets, mixins
from rest_framework import status
from django.http import JsonResponse


class SpecieViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny, )
    queryset = app_models.Specie.objects.all()

    def load_species_data(self, request, *args, **kwargs):
        try:
            specie_id = request.GET['specie_id'].strip()
        except Exception as e:
            print str(e)
            return JsonResponse({'error': "Bad Parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            species_objects = self.queryset.filter(specie_id=specie_id)
            if len(species_objects) != 0:
                species_serializer = app_serializers.SpecieSerializer(species_objects[0])
                return JsonResponse({'found': True, 'species_data': species_serializer.data}, status=status.HTTP_200_OK)
            else:
                specied_scrapped_data = app_utility.scrap(specie_id)
                if specied_scrapped_data['found']:
                    species_object, created = app_models.Specie.objects.get_or_create(specie_id=specie_id, specie_head=specied_scrapped_data['species_data']['head'])
                    if created:
                        for each in specied_scrapped_data['species_data']['main']:
                            species_data_object = app_models.SpecieData(specie=species_object, triplet=each['triplet'], amino_acid=each['amino_acid'], fraction=each['fraction'], frequency=each['frequency'])
                            species_data_object.save()
                    species_serializer = app_serializers.SpecieSerializer(species_object)
                    return JsonResponse({'found': True, 'species_data': species_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'found': False, 'error': 'Specie not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print str(e)
            return JsonResponse({'found': False, 'error': 'Some error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def index_view(request):
    return render(request, 'application/index.html', {})


def application_view(request):
    return render(request, 'application/application.html', {})

