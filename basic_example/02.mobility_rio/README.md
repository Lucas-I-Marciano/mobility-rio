# Transporte Rodoviário: API de GPS dos ônibus (SPPO) [beta]

### Example

`GET https://dados.mobilidade.rio/gps/sppo?dataInicial=2025-04-22+20:13:00&dataFinal=2025-04-22+20:13:00`

```json
[
  {
    "ordem": "D86322",
    "latitude": "-22,96873",
    "longitude": "-43,62116",
    "datahora": "1706553599000",
    "velocidade": "7",
    "linha": "855",
    "datahoraenvio": "1706553600000",
    "datahoraservidor": "1706553617000"
  },
  {
    "ordem": "B31051",
    "latitude": "-22,80419",
    "longitude": "-43,31026",
    "datahora": "1706553586000",
    "velocidade": "0",
    "linha": "483",
    "datahoraenvio": "1706553600000",
    "datahoraservidor": "1706553620000"
  },
  ...
]
```

### Description of each column

|       Nome       |                                                                                        Descrição                                                                                         |     |     |     |
| :--------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | --- | --- | --- |
|      ordem       |                        Identificador único do veículo (escrito na carroceria) - formato: XYYZZZ, sendo X = A,B,C,D; Y = número da empresa; Z = número do veículo                         |     |     |     |
|     latitude     |                                                                              Latitude da posição do veículo                                                                              |     |     |     |
|    longitude     |                                                                             Longitude da posição do veículo                                                                              |     |     |     |
|     datahora     |                                                                          Horário da posição do GPS em Unix Time                                                                          |     |     |     |
|    velocidade    |                                                                            Velocidade instantânea do veículo                                                                             |     |     |     |
|      linha       | Serviço operado pelo veículo - formato: XXX (regular), SYXXX (variações, sendo Y = P [parcial], V [variante], N [noturno], E [especial]), LECDXX (linha experimental de coleta de dados) |     |     |     |
|  datahoraenvio   |                                                          Horário em que a posição do GPS é comunicada à central (filtro da API)                                                          |     |     |     |
| datahoraservidor |                                                              Horário em que a posição do GPS é disponibilizada no servidor                                                               |     |     |     |
