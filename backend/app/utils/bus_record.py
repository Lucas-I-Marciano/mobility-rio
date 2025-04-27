from collections import defaultdict
import logging
from typing import List, Dict, Any

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

def _placeholder_process_vehicle_data(buses_with_distance: List[Dict[str, Any]]) -> Any:
    # Esta função pode ser necessária ou não, dependendo do que
    # analyze_vehicle_movement REALMENTE precisa como entrada.
    # Se for só para agrupar por 'ordem', talvez seja feito dentro da análise.
    # Por enquanto, retorna algo que a análise possa usar.
    logger.debug(f"Placeholder: process_vehicle_data recebeu {len(buses_with_distance)} registros.")
    # Exemplo: agrupar por ordem para análise de histórico (se for o caso)
    grouped_data = {}
    for bus in buses_with_distance:
        ordem = bus.get("ordem")
        if ordem:
            if ordem not in grouped_data:
                grouped_data[ordem] = []
            grouped_data[ordem].append(bus) # Adiciona o registro completo
    return grouped_data

def _placeholder_analyze_vehicle_movement(processed_data_grouped_by_ordem: Dict[str, List[Dict[str, Any]]]) -> Dict[str, bool]:
    # *** PONTO CRÍTICO DA REFATORAÇÃO ***
    # Esta função precisa ser ajustada para retornar um dicionário:
    # {'ordem1': True, 'ordem2': False, ...} (True = approaching)
    # A lógica exata para determinar 'approaching' está aqui dentro.
    # Talvez compare a penúltima distância com a última para cada 'ordem'?
    logger.debug("Placeholder: analyze_vehicle_movement sendo executado...")
    approaching_map = {}
    for ordem, records in processed_data_grouped_by_ordem.items():
        if len(records) >= 2:
            # Lógica de exemplo: se a distância mais recente for menor que a anterior, está aproximando
            last_distance = records[-1].get('distance_km')
            previous_distance = records[-2].get('distance_km')
            if last_distance is not None and previous_distance is not None:
                approaching_map[ordem] = last_distance < previous_distance
            else:
                approaching_map[ordem] = False # Não é possível determinar
        else:
             approaching_map[ordem] = False # Não há histórico suficiente

    # Simular o resultado que você mencionou antes para alguns IDs
    # approaching_map["B71033"] = True
    # approaching_map["B71058"] = False
    # approaching_map["B71063"] = False
    # approaching_map["A29052"] = True # Adicionando do exemplo de entrada

    logger.debug(f"Placeholder: Movement analysis map gerado: {approaching_map}")
    return approaching_map

# --- Função Principal Refatorada ---

def analyze_vehicle_proximity(
    buses_with_distance: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Analisa uma lista de ônibus (com distância já calculada) para determinar
    se estão se aproximando de um destino e retorna uma lista estruturada.

    Args:
        buses_with_distance: Lista de dicionários de ônibus, cada um DEVE
                             conter 'ordem' (str) e 'distance_km' (float).

    Returns:
        Uma lista de dicionários no formato:
        [{'ordem': str, 'approaching': bool, 'distance': float}, ...],
        ou uma lista vazia em caso de erro ou entrada inválida.
    """
    if not isinstance(buses_with_distance, list) or not buses_with_distance:
        logger.warning("analyze_vehicle_proximity recebeu entrada inválida ou vazia.")
        return []

    logger.info(f"Iniciando análise de proximidade para {len(buses_with_distance)} ônibus.")

    try:
        # Passo 1: Determinar status de aproximação para cada ônibus
        # (Estas chamadas dependem da implementação real das funções placeholder)
        processed_data = _placeholder_process_vehicle_data(buses_with_distance)
        approaching_status_map = _placeholder_analyze_vehicle_movement(processed_data)

    except Exception as e:
        logger.exception(f"Erro durante a análise interna de movimento: {e}")
        return [] # Retorna vazio se a análise falhar

    # Passo 2: Combinar resultados no formato desejado
    final_results = []
    processed_ordens = set() # Para lidar com possíveis duplicatas na entrada original

    # Iteramos pela lista original para manter a ordem e pegar a distância mais recente
    for bus in reversed(buses_with_distance): # Iterar de trás pra frente pega o último registro primeiro
        if not isinstance(bus, dict): continue

        ordem = bus.get("ordem")
        distance = bus.get("distance_km")

        # Processa cada 'ordem' apenas uma vez (o último registro dela)
        if ordem and ordem not in processed_ordens and isinstance(distance, (int, float)):
            processed_ordens.add(ordem) # Marca como processado

            # Pega o status de aproximação do mapa, default False se não encontrado
            is_approaching = approaching_status_map.get(ordem, False)

            final_results.append({
                "ordem": ordem,
                "approaching": is_approaching,
                "distance": distance # Usa a distância já calculada e arredondada
            })
        elif ordem and ordem not in processed_ordens:
             logger.warning(f"Ônibus {ordem} sem distance_km válida no último registro: {bus}")


    # Reverte a lista para manter a ordem original aproximada (opcional)
    final_results.reverse()

    logger.info(f"Análise de proximidade gerou {len(final_results)} resultados estruturados.")
    return final_results