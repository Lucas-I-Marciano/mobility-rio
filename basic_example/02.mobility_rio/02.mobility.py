import requests

url = "https://dados.mobilidade.rio/gps/sppo?dataInicial=2025-04-22+20:13:00&dataFinal=2025-04-22+20:13:00"
response_get = requests.get(url, verify=False)
print(response_get.json())
