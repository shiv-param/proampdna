from bs4 import BeautifulSoup
import requests
import re
from django.conf import settings


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
