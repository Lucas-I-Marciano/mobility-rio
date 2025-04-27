from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

def process_vehicle_data(data: dict) -> dict:
    """
    Agrupa os dados de veículos por 'ordem' e ordena cada grupo por 'datahora'.

    Args:
        data: Dicionário contendo a chave 'results' com uma lista de registros.

    Returns:
        Dicionário onde as chaves são 'ordem' e os valores são listas
        de dicionários {'datahora': 'distance_km'} ordenados por 'datahora'.
    """
    # Usa defaultdict para simplificar o agrupamento
    # A chave é 'ordem', o valor padrão é uma lista vazia
    grouped_data = defaultdict(list)

    # --- Parte 1: Agrupamento Otimizado ---
    for record in data.get('results', []): # Usar .get para evitar erro se 'results' não existir
        vehicle_id = record.get("ordem")
        timestamp = record.get("datahora")
        distance = record.get("distance_km")

        # Adiciona verificação se os campos existem antes de usar
        if vehicle_id and timestamp and distance is not None:
             # Anexa diretamente, defaultdict cuida da criação da lista se for a 1ª vez
            grouped_data[vehicle_id].append({timestamp: distance})

    # --- Parte 2: Ordenação (lógica mantida, nomes de variáveis melhorados) ---
    for vehicle_id in grouped_data:
        timestamp_list = grouped_data[vehicle_id]
        # Ordena a lista com base na chave (timestamp) do dicionário interno
        timestamp_list.sort(key=lambda item: int(next(iter(item))))

    all_grouped_data = data.get('results', [])
    all_grouped_data.sort(key=lambda item: item["datahora"])

    # Converte defaultdict de volta para dict para a saída final (opcional, mas comum)
    return {"only_time" : dict(grouped_data), "all_data" : all_grouped_data}

def analyze_vehicle_movement(grouped_sorted_data: dict) -> list:
    """
    Analisa se os veículos estão, de forma geral, se aproximando ou se afastando.

    Compara a primeira e a última medição de distância registrada para cada veículo.

    Args:
        grouped_sorted_data: Dicionário retornado por process_vehicle_data.
                             As chaves são 'ordem' e os valores são listas
                             de dicionários {'datahora': 'distance_km'} ordenados
                             cronologicamente.

    Returns:
        Uma lista de dicionários no formato [{"id_veiculo": eh_aproximando_boolean}, ...].
        True indica aproximação (última distância < primeira distância).
        False indica afastamento ou manutenção da distância.
    """
    movement_analysis_result = []
    for vehicle_id, timestamp_list in grouped_sorted_data.items():

        # Precisa de pelo menos um ponto para análise (comparar primeiro e último)
        # Se tiver só um, a distância será igual, resultando em False (não aproximando)
        if not timestamp_list:
            continue # Pula veículos sem dados

        try:
          to_assess = []
          for i in range(len(timestamp_list)) :
            if i == 0:
                continue
            actual_index = i * -1
            last_index = actual_index - 1
            
            actual_data_point = timestamp_list[actual_index]
            last_data_point = timestamp_list[last_index]

            actual_distance = next(iter(actual_data_point.values()))
            last_distance_test = next(iter(last_data_point.values()))

            to_assess.append(actual_distance - last_distance_test)
          movement_analysis_result.append({vehicle_id: sum(to_assess) < 0})

        except (StopIteration, IndexError) as e:
            # Adiciona um tratamento básico caso haja algo inesperado com os dados internos
            print(f"Erro ao processar dados para o veículo {vehicle_id}: {e}. Pulando.")
            continue

    return movement_analysis_result

def analyze_vehicle_movement_distance(results_with_distance):
    processed_data = process_vehicle_data({"results" : results_with_distance})["only_time"]
    vehicle_movement = analyze_vehicle_movement(processed_data)
    logger.info(f"Calculated distances for {len(results_with_distance)} buses.")
    # Using logger.debug might be better for potentially large output
    logger.debug(f"Results with distance: {results_with_distance}")

    # Itera sobre cada dicionário na lista 'results' do primeiro objeto
    for item in vehicle_movement:
        # Pega a única chave presente no dicionário atual (ex: "A29041")
        # Assumindo que cada dicionário em 'results' sempre terá apenas uma chave
        chave = list(item.keys())[0]

        # Verifica se a chave existe no segundo objeto e se a lista correspondente não está vazia
        if chave in processed_data and processed_data[chave]:
            # Pega a lista de dicionários correspondente à chave no segundo objeto
            lista_distancias = processed_data[chave]

            # Pega o último dicionário da lista
            ultimo_registro = lista_distancias[-1]

            # Pega o valor do último dicionário (a distância)
            # Assumindo que cada dicionário na lista de distâncias também tem apenas uma chave
            distancia = list(ultimo_registro.values())[0]

            # Adiciona a chave "distance" com o valor encontrado ao dicionário original em dados1
            item['distance'] = distancia
        else:
            # Opcional: Define um valor padrão caso a chave não exista em processed_data ou a lista esteja vazia
            item['distance'] = None # ou 0, ou outra indicação de que não foi encontrado
    return vehicle_movement