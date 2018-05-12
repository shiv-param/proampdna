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
from django.http import JsonResponse, HttpResponse
from django.conf import settings


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
                return JsonResponse({'species_data': species_serializer.data}, status=status.HTTP_200_OK)
            else:
                specied_scrapped_data = app_utility.scrap(specie_id)
                if specied_scrapped_data['found']:
                    species_object, created = app_models.Specie.objects.get_or_create(specie_id=specie_id, specie_head=specied_scrapped_data['species_data']['head'])
                    if created:
                        for each in specied_scrapped_data['species_data']['main']:
                            species_data_object = app_models.SpecieData(specie=species_object, triplet=each['triplet'], amino_acid=each['amino_acid'], fraction=each['fraction'], frequency=each['frequency'])
                            species_data_object.save()
                    species_serializer = app_serializers.SpecieSerializer(species_object)
                    return JsonResponse({'species_data': species_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'error': 'Specie not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print str(e)
            return JsonResponse({'error': 'Some error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def run_app(self, request, *args, **kwargs):
        try:
            speciesID = request.GET['specie_id'].strip()
            primer_len = request.GET['primer_len'].strip()
            email = request.GET['email'].strip()
            aminoAcidSeq = request.GET['amino_acid_seq'].strip()
        except Exception as e:
            print str(e)
            return JsonResponse({'error': "Bad Parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:

            ret = {}
            valSeq = settings.VALID_SEQUENCE

            validSequence = True
            validPrimerLen = True
            validSpeciesID = True
            validEmail = True

            # Code for Validation of Email

            # Species ID Validation
            SpeciesObjects = self.queryset.filter(specie_id=speciesID.strip())
            if len(SpeciesObjects) == 0:
                validSpeciesID = False

            # Primer length Validation
            if primer_len.strip() not in ['3', '6', '9', '12', '15', '18', '21', '24', '27', '30']:
                validPrimerLen = False

            # Amino Acid Sequence Validation
            if aminoAcidSeq.strip() == '':
                validSequence = False

            for eachSeq in aminoAcidSeq.strip():
                if eachSeq not in valSeq:
                    validSequence = False
                    break

            if validSequence and validEmail and validSpeciesID and validPrimerLen:

                primer_len = primer_len.strip()
                aminoAcidSeq = aminoAcidSeq.strip()

                filterValues = []

                for eachSeq in aminoAcidSeq.strip():
                    if eachSeq not in filterValues:
                        filterValues.append(eachSeq)

                specieObj = self.queryset.filter(specie_id=speciesID.strip())
                SpeciesDataObjects = app_models.SpecieData.objects.filter(specie=specieObj, amino_acid__in=filterValues).order_by('amino_acid')

                codons = {}
                for each in SpeciesDataObjects:
                    if each.amino_acid in codons.keys():
                        codons[each.amino_acid].append([each.triplet, each.frequency])
                    else:
                        codons[each.amino_acid] = [[each.triplet, each.frequency]]

                sz = int(primer_len) - 1
                si = 0
                minSum = 100000000000000
                compProd = 1

                for i in range(len(aminoAcidSeq) - sz):
                    amSub = aminoAcidSeq[i:(i + sz + 1)]
                    sumi = 0
                    prod = 1
                    for j in range(len(amSub)):
                        t = codons[amSub[j]]
                        sumi += len(t)
                        prod *= len(t)
                    if sumi <= minSum:
                        minSum = sumi
                        compProd = prod
                        si = i

                subSeq = aminoAcidSeq[si:(si + sz + 1)]
                main = []
                freq = []

                for i in range(si, (si + sz + 1)):
                    ac = aminoAcidSeq[i]
                    t = codons[ac]
                    tmp = []
                    tmpf = []
                    if i == si:
                        for s in t:
                            tmp.append(s[0])
                            tmpf.append(float(s[1]))
                    else:
                        for s in t:
                            for x2 in range(len(main)):
                                tmp.append(s[0] + "" + main[x2])
                                tmpf.append((float(s[1]) / 1000) * freq[x2])
                    main = tmp
                    freq = tmpf

                mainData = []
                for i in range(len(main)):
                    mainData.append([main[i], freq[i]])

                mainData.sort(key=lambda x: x[1], reverse=True)

                # mainData(ret), aminoAcidSeq(seq), int(primer_len)*3 (plen), subSeq
                ret['aasldc'] = subSeq
                ret['resultData'] = []
                for data in mainData:
                    pattern = data[0].replace('U', 'T')
                    freq = data[1]
                    patLen = len(pattern)
                    revSeq = ''
                    GCCount = 0
                    ATCount = 0
                    ACount = 0
                    CCount = 0
                    TCount = 0
                    GCount = 0
                    salt = float(50)
                    divalent = 0
                    DNTP = 0
                    for k in range(patLen):
                        if pattern[k] == 'A':
                            ACount += 1
                        elif pattern[k] == 'C':
                            CCount += 1
                        elif pattern[k] == 'T':
                            TCount += 1
                        elif pattern[k] == 'G':
                            GCount += 1
                        if pattern[k] == 'G' or pattern[k] == 'C':
                            GCCount += 1
                        if pattern[k] == 'A' or pattern[k] == 'T':
                            ATCount += 1
                    GCPerc = (GCCount / patLen) * 100
                    ATPerc = (ATCount / patLen) * 100
                    APerc = (ACount / patLen) * 100
                    CPerc = (CCount / patLen) * 100
                    TPerc = (TCount / patLen) * 100
                    GPerc = (GCount / patLen) * 100
                    salt += (120 * math.sqrt(divalent - DNTP))
                    r = (math.log(salt / 100) / math.log(10))
                    tm = (64.9 + 41 * ((GCount + CCount - 16.4) / (ACount + CCount + TCount + GCount)))
                    ret['resultData'].append({
                        'forwardPrimer': pattern[::-1],
                        'reversePrimer': app_utility.revCod(pattern[::-1]),
                        'frequency': freq,
                        'length': patLen,
                        'GCPerc': GCPerc,
                        'meltingPoint': tm,
                        'aasldc': ret['aasldc']
                    })
                ret['total'] = len(ret['resultData'])

                page = self.paginate_queryset(ret['resultData'])
                if page is not None:
                    serializer = app_serializers.ResultSetSerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                result_set_serializer = app_serializers.ResultSetSerializer(ret['resultData'])
                return JsonResponse({'result_set': result_set_serializer.data}, status=status.HTTP_200_OK)
            else:
                errors = []
                if not validPrimerLen:
                    errors.append('Enter Valid Length of Primer (eg. 3,6,9,12,15,18,21,24,27,30)')
                if not validSpeciesID:
                    errors.append('Enter Valid Species ID')
                if not validSequence:
                    errors.append('Enter Valid Amino Acid Sequence')
                if not validEmail:
                    errors.append('Enter Valid Email ID')
                return JsonResponse({'error': 'Validation error', 'errors': errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print str(e)
            return JsonResponse({'error': 'Some error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def export_data(self, request, *args, **kwargs):
        try:
            speciesID = request.GET['specie_id'].strip()
            primer_len = request.GET['primer_len'].strip()
            email = request.GET['email'].strip()
            aminoAcidSeq = request.GET['amino_acid_seq'].strip()
            export_as = request.GET['export_as'].strip()
        except Exception as e:
            print str(e)
            return JsonResponse({'error': "Bad Parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:

            ret = {}
            valSeq = settings.VALID_SEQUENCE

            validSequence = True
            validPrimerLen = True
            validSpeciesID = True
            validEmail = True

            # Code for Validation of Email

            # Species ID Validation
            SpeciesObjects = self.queryset.filter(specie_id=speciesID.strip())
            if len(SpeciesObjects) == 0:
                validSpeciesID = False

            # Primer length Validation
            if primer_len.strip() not in ['3', '6', '9', '12', '15', '18', '21', '24', '27', '30']:
                validPrimerLen = False

            # Amino Acid Sequence Validation
            if aminoAcidSeq.strip() == '':
                validSequence = False

            for eachSeq in aminoAcidSeq.strip():
                if eachSeq not in valSeq:
                    validSequence = False
                    break

            if validSequence and validEmail and validSpeciesID and validPrimerLen:

                primer_len = primer_len.strip()
                aminoAcidSeq = aminoAcidSeq.strip()

                filterValues = []

                for eachSeq in aminoAcidSeq.strip():
                    if eachSeq not in filterValues:
                        filterValues.append(eachSeq)

                specieObj = self.queryset.filter(specie_id=speciesID.strip())
                SpeciesDataObjects = app_models.SpecieData.objects.filter(specie=specieObj, amino_acid__in=filterValues).order_by('amino_acid')

                codons = {}
                for each in SpeciesDataObjects:
                    if each.amino_acid in codons.keys():
                        codons[each.amino_acid].append([each.triplet, each.frequency])
                    else:
                        codons[each.amino_acid] = [[each.triplet, each.frequency]]

                sz = int(primer_len) - 1
                si = 0
                minSum = 100000000000000
                compProd = 1

                for i in range(len(aminoAcidSeq) - sz):
                    amSub = aminoAcidSeq[i:(i + sz + 1)]
                    sumi = 0
                    prod = 1
                    for j in range(len(amSub)):
                        t = codons[amSub[j]]
                        sumi += len(t)
                        prod *= len(t)
                    if sumi <= minSum:
                        minSum = sumi
                        compProd = prod
                        si = i

                subSeq = aminoAcidSeq[si:(si + sz + 1)]
                main = []
                freq = []

                for i in range(si, (si + sz + 1)):
                    ac = aminoAcidSeq[i]
                    t = codons[ac]
                    tmp = []
                    tmpf = []
                    if i == si:
                        for s in t:
                            tmp.append(s[0])
                            tmpf.append(float(s[1]))
                    else:
                        for s in t:
                            for x2 in range(len(main)):
                                tmp.append(s[0] + "" + main[x2])
                                tmpf.append((float(s[1]) / 1000) * freq[x2])
                    main = tmp
                    freq = tmpf

                mainData = []
                for i in range(len(main)):
                    mainData.append([main[i], freq[i]])

                mainData.sort(key=lambda x: x[1], reverse=True)

                # mainData(ret), aminoAcidSeq(seq), int(primer_len)*3 (plen), subSeq
                ret['aasldc'] = subSeq
                ret['resultData'] = []
                for data in mainData:
                    pattern = data[0].replace('U', 'T')
                    freq = data[1]
                    patLen = len(pattern)
                    revSeq = ''
                    GCCount = 0
                    ATCount = 0
                    ACount = 0
                    CCount = 0
                    TCount = 0
                    GCount = 0
                    salt = float(50)
                    divalent = 0
                    DNTP = 0
                    for k in range(patLen):
                        if pattern[k] == 'A':
                            ACount += 1
                        elif pattern[k] == 'C':
                            CCount += 1
                        elif pattern[k] == 'T':
                            TCount += 1
                        elif pattern[k] == 'G':
                            GCount += 1
                        if pattern[k] == 'G' or pattern[k] == 'C':
                            GCCount += 1
                        if pattern[k] == 'A' or pattern[k] == 'T':
                            ATCount += 1
                    GCPerc = (GCCount / patLen) * 100
                    ATPerc = (ATCount / patLen) * 100
                    APerc = (ACount / patLen) * 100
                    CPerc = (CCount / patLen) * 100
                    TPerc = (TCount / patLen) * 100
                    GPerc = (GCount / patLen) * 100
                    salt += (120 * math.sqrt(divalent - DNTP))
                    r = (math.log(salt / 100) / math.log(10))
                    tm = (64.9 + 41 * ((GCount + CCount - 16.4) / (ACount + CCount + TCount + GCount)))
                    ret['resultData'].append({
                        'forwardPrimer': pattern[::-1],
                        'reversePrimer': app_utility.revCod(pattern[::-1]),
                        'frequency': freq,
                        'length': patLen,
                        'GCPerc': GCPerc,
                        'meltingPoint': tm,
                        'aasldc': ret['aasldc']
                    })
                ret['total'] = len(ret['resultData'])
                if export_as == 'csv':
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename=results_{sp_id}.csv'.format(sp_id=speciesID)
                    response = app_utility.export(response, export_as, ret['resultData'])
                    return response
            else:
                errors = []
                if not validPrimerLen:
                    errors.append('Enter Valid Length of Primer (eg. 3,6,9,12,15,18,21,24,27,30)')
                if not validSpeciesID:
                    errors.append('Enter Valid Species ID')
                if not validSequence:
                    errors.append('Enter Valid Amino Acid Sequence')
                if not validEmail:
                    errors.append('Enter Valid Email ID')
                return JsonResponse({'error': 'Validation error', 'errors': errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print str(e)
            return JsonResponse({'error': 'Some error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def index_view(request):
    return render(request, 'application/index.html', {})


def application_view(request):
    return render(request, 'application/application.html', {})

