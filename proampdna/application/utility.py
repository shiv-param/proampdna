from bs4 import BeautifulSoup
import requests
import re
from django.conf import settings
import csv
from django.utils.encoding import smart_str


def build_url_for_scrap(specie_id):
    return settings.SCRAP_URL.format(specie_id=specie_id)


def scrap(specie_id):

    ret = {}
    page = requests.get(build_url_for_scrap(specie_id))

    if page.status_code != 200:
        ret['found'] = False
        ret['species_data'] = {}

    else:

        soup = BeautifulSoup(page.content, 'html.parser')
        speciesHead = soup.find_all('strong')[0].get_text()

        if speciesHead.find('Not found:') != -1:
            ret['found'] = False
            ret['species_data'] = {}
        else:
            speciesDataContent = soup.find_all('pre')[0].get_text()
            speciesDataContent = re.sub(r'\(([^)]+)\)', ";", speciesDataContent)
            speciesDataContent = speciesDataContent.split(';')
            speciesMainData = []
            for eachSet in speciesDataContent:
                if len(eachSet.strip()) != 0:
                    speciesData = eachSet.strip().replace(' ', ';').replace(';;', ';').replace(';;;', ';').replace(
                        ';;;;', ';').split(';')
                    speciesMainData.append({
                        'triplet': speciesData[0],
                        'amino_acid': speciesData[1],
                        'fraction': float(speciesData[2]),
                        'frequency': float(speciesData[3])
                    })
            ret['found'] = True
            ret['species_data'] = {
                'head': speciesHead,
                'main': speciesMainData
            }

    return ret


def revCod(stri):
   ret = "";
   for i in range(len(stri)):
       if stri[i] == 'A':
           ret += 'T'
       elif stri[i] == 'T':
           ret += 'A'
       elif stri[i] == 'G':
           ret += 'C'
       elif stri[i] == 'C':
           ret += 'G'
   return ret[::-1]


def export(response, export_as, data):

    if export_as == 'csv':

        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)

        writer.writerow([
            smart_str(u"Forword Primer"),
            smart_str(u"Reverse Primer"),
            smart_str(u"Frequency"),
            smart_str(u"Length"),
            smart_str(u"% GC"),
            smart_str(u"Melting Point"),
        ])

        for obj in data:
            writer.writerow([
                smart_str(obj['forwardPrimer']),
                smart_str(obj['reversePrimer']),
                smart_str(obj['frequency']),
                smart_str(obj['length']),
                smart_str(obj['GCPerc']),
                smart_str(obj['meltingPoint']),
            ])

        return response