import requests
import json

# Written by Zachary Zhu @ Jan 2023 for Matthew Walsh

# Which countries do you want to get data for?
countries = [
  'Bulgaria',
  'Czechia',
  'Croatia',
  'Estonia',
  'Hungary',
  'Latvia',
  'Lithuania',
  'Poland',
  'Romania',
  'Slovakia',
  'Slovenia',
]

# Name of the TSV file to write to:
tsvFile = 'kohesio-data-export.tsv'

# Request to get dict of country IDs from which to use in later API calls
res = requests.get('https://kohesio.ec.europa.eu/api/facet/eu/countries', params={'language': 'en'})
if not res.status_code == 200:
  raise Exception('RuntimeException: request failed with status code: ' + str(res.status_code))
countryIds = json.loads(res.text)
countryIds = { x['instanceLabel']:x['instance'] for x in countryIds }

# Adds relevant information for each beneficiary to a list, which will later be written into a TSV
beneficiaryInfo = []
beneficiaryInfo.append('Country\tRegion\tBeneficiary Name\tTotal Budget\tEU Contribution\tNumber of Projects\tTransliterated Name\t\n')

for country in countries:
  countryId = countryIds[country]

  res = \
    requests.get(
      'https://kohesio.ec.europa.eu/api/facet/eu/regions',
      params={
        'language' : 'en',
        'country'  : countryId,
      }
    )
  if not res.status_code == 200:
    raise Exception('RuntimeException: request failed with status code: ' + str(res.status_code))

  regionIds = json.loads(res.text)
  regionIds = { x['name']:x['region'] for x in regionIds }

  for regionName, regionId in regionIds.items():
    res = requests.get(
        'https://kohesio.ec.europa.eu/api/facet/eu/search/beneficiaries',
        params={
          'offset'   : 0,
          'country'  : countryId,
          'region'   : regionId,
          'language' : 'en',
        }
      )

    if not res.status_code == 200:
      raise Exception('RuntimeException: request failed with status code: ' + str(res.status_code))
    
    beneficiaries = json.loads(res.text)['list']

    for beneficiary in beneficiaries:
      info = [
        country,
        regionName,
        beneficiary['label'],
        beneficiary['budget'],
        beneficiary['euBudget'],
        str(beneficiary['numberProjects']),
        str(beneficiary['transliteration'] or ''),
        '\n',
      ]
      beneficiaryInfo.append('\t'.join(info))

with open(tsvFile, 'w') as f:
  f.writelines(beneficiaryInfo)

