# backend/app/services/bus_filtering.py
import math
from typing import List, Dict, Any, Optional # Import Optional
import logging
from datetime import datetime, timezone
from decimal import Decimal # Para lidar com tipos do DB se necessário
from zoneinfo import ZoneInfo
from collections import defaultdict

from app.services.redis import get_latest_bus_data
from app.services.travel_time import get_travel_time_estimate # Função síncrona agora
from app.schemas.travel_mode import TravelMode
from app.schemas.bus_response import BusStatus # Importa o modelo de resposta

from app.utils.coordinates_distance import haversine
from app.core.exceptions import ServiceError

logger = logging.getLogger(__name__)

def safe_float_convert(value_str: Any) -> Optional[float]:
    """Converte string com vírgula para float, tratando erros."""
    if isinstance(value_str, (int, float)):
        return float(value_str)
    if isinstance(value_str, str):
        try:
            return float(value_str.replace(",", "."))
        except ValueError:
            return None
    return None

def sort_by(data, key):
    """Função auxiliar para ordenar dados por uma chave específica."""
    return sorted(data, key=lambda x: x[key])

def filter_and_paginate_buses(
    full_bus_list: List[Dict[str, Any]],
    page: int = 1,
    limit: int = 10,
    lines: Optional[List[str]] = None # Optional line filter
    ) -> Dict[str, Any]:
    """
    Filters a list of buses by line (optional) and applies pagination.

    Args:
        full_bus_list: The complete list of bus data dictionaries.
        page: The desired page number (1-indexed).
        limit: The number of items per page.
        line: The specific bus line to filter by (optional).

    Returns:
        A dictionary containing pagination metadata and the filtered/paginated list of buses.
    """

    # 1. Filter by line if provided
    if lines: # Check if the list is provided and not empty
        # Convert filter lines to a set of strings for efficient 'in' check
        # Handles potential non-string items in the input list
        line_filter_set = {str(line) for line in lines if line}
        if line_filter_set: # Proceed only if the set is not empty after conversion
            filtered_list = [
                bus for bus in full_bus_list
                if isinstance(bus, dict) and str(bus.get("linha")) in line_filter_set
            ]
        else:
             # If input list was empty or contained only falsy values
             filtered_list = full_bus_list
    else:
        # No line filter applied, use the full list
        filtered_list = full_bus_list

    # 2. Apply Pagination to the filtered list
    total_items = len(filtered_list)
    limit = max(1, limit) # Ensure limit is at least 1
    page = max(1, page)   # Ensure page is at least 1
    offset = (page - 1) * limit
    total_pages = math.ceil(total_items / limit) if limit > 0 else 0

    # Ensure page number is within valid range
    if page > total_pages and total_pages > 0:
        # Optional: Redirect to last page? Or keep it simple and return empty list?
        # Let's return empty list if page is out of bounds
         paginated_items = []
         # Or adjust page to last page: page = total_pages; offset = (page - 1) * limit
    else:
         paginated_items = filtered_list[offset : offset + limit]


    # 3. Return structured data
    return {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "items": paginated_items
    }

def add_distance_to_buses(
    bus_list: List[Dict[str, Any]],
    dest_lat: float,
    dest_lng: float
    ) -> List[Dict[str, Any]]:
    """
    Calculates the distance from each bus in the list to a destination point.

    Args:
        bus_list: The list of bus data dictionaries. Expected keys: 'latitude', 'longitude' (as strings with comma decimal sep).
        dest_lat: Destination latitude (float).
        dest_lng: Destination longitude (float).

    Returns:
        A new list of bus dictionaries, each augmented with a 'distance_km' key
        if calculation was successful. Buses with invalid coordinates are omitted/logged.
    """
    buses_with_distance = []
    if not isinstance(bus_list, list):
         logger.warning("Input bus_list is not a list.")
         return [] # Return empty if input is invalid

    for bus in bus_list:
        if not isinstance(bus, dict):
            logger.warning(f"Skipping invalid item in bus_list (not a dict): {bus}")
            continue

        bus_lat_str = bus.get("latitude")
        bus_lng_str = bus.get("longitude")
        bus_ordem = bus.get("ordem", "N/A") # Get order for logging

        if isinstance(bus_lat_str, str) and isinstance(bus_lng_str, str):
            try:
                # --- Data Cleaning: Replace comma and convert to float ---
                bus_lat_float = float(bus_lat_str.replace(",", "."))
                bus_lng_float = float(bus_lng_str.replace(",", "."))

                # --- Calculate Distance ---
                distance_km = haversine(bus_lng_float, bus_lat_float, dest_lng, dest_lat)

                # --- Augment Data ---
                # Create a copy to avoid modifying original dicts if bus_list is reused
                bus_copy = bus.copy()
                bus_copy['distance_km'] = round(distance_km, 2) # Add distance rounded
                buses_with_distance.append(bus_copy)

            except ValueError as e:
                logger.warning(f"Could not convert coordinates to float for bus {bus_ordem}. Lat: '{bus_lat_str}', Lng: '{bus_lng_str}'. Error: {e}")
            except Exception as e:
                # Catch potential errors from haversine itself, though unlikely
                logger.error(f"Error calculating distance for bus {bus_ordem}: {e}")
        else:
            logger.warning(f"Missing or invalid coordinate types for bus {bus_ordem}. Lat: {type(bus_lat_str)}, Lng: {type(bus_lng_str)}")

    return buses_with_distance

def group_and_sort_vehicle_data(data: dict | list, data_key:str = None) -> dict:
    """
    Agrupa dados de veículos por 'ordem' e ordena cada grupo por 'datahora'.

    Esta função recebe uma lista ou um dicionário contendo registros de veículos,
    agrupa esses registros pela chave 'ordem' e ordena cada grupo pela chave 'datahora'.
    O resultado é um dicionário onde as chaves são os identificadores dos veículos ('ordem')
    e os valores são listas de dicionários contendo 'datahora' e 'distance_km', ordenados por 'datahora'.

    Args:
        data (dict | list): Dados dos veículos, podendo ser uma lista de registros ou um dicionário contendo a chave <data_key> com uma lista de registros.
        data_key (str, opcional): Chave para acessar os dados dentro do dicionário, se 'data' for um dicionário. Necessário se 'data' for um dicionário.

    Returns:
        dict: Dicionário onde as chaves são os identificadores dos veículos ('ordem') e os valores são listas de dicionários {'datahora': 'distance_km'} ordenados por 'datahora'.

    Raises:
        Exception: Se 'data_key' estiver ausente quando 'data' for um dicionário.
    """

    # Usa defaultdict para simplificar o agrupamento
    # A chave é 'ordem', o valor padrão é uma lista vazia
    grouped_data = defaultdict(list)
    if isinstance(data, dict) :
        if not data_key:
            raise Exception("data_key missing")
        ordered_data = sort_by(data.get(data_key, []), "datahora")
    else :
        ordered_data = sort_by(data, "datahora")

    # --- Parte 1: Agrupamento Otimizado ---
    for record in ordered_data: # Usar .get para evitar erro se 'results' não existir
        try :
            vehicle_id = record["ordem"]
            timestamp = record["datahora"]
            distance = record["distance_km"]
        except:
            raise Exception("Missing keys: ordem, datahora or distance_km")

        # Adiciona verificação se os campos existem antes de usar
        if vehicle_id and timestamp and distance is not None:
             # Anexa diretamente, defaultdict cuida da criação da lista se for a 1ª vez
            grouped_data[vehicle_id].append({timestamp: distance})
        
    return dict(grouped_data)

def analyze_vehicle_movement(grouped_sorted_data: dict) -> list:
    """
    Analisa se os veículos estão, de forma geral, se aproximando ou se afastando.

    Compara a soma da diferença das distâncias tomadas uma a uma (atual x imediantamente anterior) registrada para cada veículo.

    Args:
        grouped_sorted_data: Dicionário retornado por process_vehicle_data.
                             As chaves são 'ordem' e os valores são listas
                             de dicionários {'datahora': 'distance_km'} ordenados
                             cronologicamente.

    Returns:
        Uma lista de dicionários no formato [{"id_veiculo": eh_aproximando_boolean}, ...].
        True indica aproximação (soma da diferença das distâncias < 0).
        False indica afastamento ou manutenção da distância.
    """
    movement_analysis_result = {}
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
            last_distance = next(iter(last_data_point.values()))

            to_assess.append(actual_distance - last_distance)
          movement_analysis_result[vehicle_id] = sum(to_assess) < 0

        except (StopIteration, IndexError) as e:
            # Adiciona um tratamento básico caso haja algo inesperado com os dados internos
            print(f"Erro ao processar dados para o veículo {vehicle_id}: {e}. Pulando.")
            continue

    return movement_analysis_result

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
        grouped_and_sorted_list = group_and_sort_vehicle_data(buses_with_distance)
        approaching_status_map =  analyze_vehicle_movement(grouped_and_sorted_list)

    except Exception as e:
        logger.exception(f"Erro durante a análise interna de movimento: {e}")
        return [] # Retorna vazio se a análise falhar

    # Passo 2: Combinar resultados no formato desejado
    final_results = []
    processed_ordens = set() # Para lidar com possíveis duplicatas na entrada original

    # Iteramos pela lista original para manter a ordem e pegar a distância mais recente
    ordered_buses_with_distance = sort_by(buses_with_distance, "datahora")
    for bus in reversed(buses_with_distance): # Iterar de trás pra frente pega o último registro primeiro
        if not isinstance(bus, dict): continue

        ordem = bus.get("ordem")
        distance = bus.get("distance_km")
        latitude = bus.get("latitude")
        longitude = bus.get("longitude")
        datahora = bus.get("datahora")
        velocidade = bus.get("velocidade")
        linha = bus.get("linha")
        datahoraenvio = bus.get("datahoraenvio")
        datahoraservidor = bus.get("datahoraservidor")

        # Processa cada 'ordem' apenas uma vez (o último registro dela)
        if ordem and ordem not in processed_ordens and isinstance(distance, (int, float)):
            processed_ordens.add(ordem) # Marca como processado

            # Pega o status de aproximação do mapa, default False se não encontrado
            is_approaching = approaching_status_map.get(ordem, False)

            final_results.append({
                "ordem": ordem,
                "latitude" : latitude,
                "longitude" : longitude,
                "datahora" : datahora,
                "velocidade" : velocidade,
                "linha" : linha,
                "datahoraenvio" : datahoraenvio,
                "datahoraservidor" : datahoraservidor,
                "distance": distance,
                "approaching": is_approaching,
            })
        elif ordem and ordem not in processed_ordens:
             logger.warning(f"Ônibus {ordem} sem distance_km válida no último registro: {bus}")

    logger.info(f"Análise de proximidade gerou {len(final_results)} resultados estruturados.")
    return final_results

def get_latest_bus_records(bus_list: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Processa uma lista de registros de ônibus e retorna um dicionário
    contendo apenas o registro mais recente para cada 'ordem'.
    """
    latest_records = {}
    for bus in bus_list:
        if not isinstance(bus, dict): continue
        ordem = bus.get("ordem")
        # Usa datahoraservidor para desempate, ou datahora se preferir/confiar mais
        # Converte para inteiro para comparação segura
        timestamp_str = bus.get("datahoraservidor") or bus.get("datahora", "0")
        try:
            timestamp = int(timestamp_str)
        except (ValueError, TypeError):
            timestamp = 0 # Trata como antigo se timestamp inválido

        if ordem:
            current_latest_timestamp = int(latest_records.get(ordem, {}).get("datahoraservidor") or latest_records.get(ordem, {}).get("datahora", "0"))
            if timestamp >= current_latest_timestamp: # Pega o mais recente (ou igual)
                 latest_records[ordem] = bus
    return latest_records

def get_line_status_with_eta(line_id: str, dest_lat: float, dest_lng: float, ordem_id:str = None) -> List[BusStatus]:
    """
    Obtém o status mais recente e verificado dos ônibus de uma linha,
    calcula o ETA condicionalmente e inclui status de aproximação/distância.
    """
    logger.info(f"Buscando status otimizado para linha {line_id} / Destino ({dest_lat}, {dest_lng})")

    # --- 1. Obter Dados Base e Filtrar Linha ---
    try:
        full_bus_list = get_latest_bus_data()
        if not full_bus_list: return []

        # Usamos filter_and_paginate para pegar todos da linha (limite alto)
        # Certifique-se que filter_and_paginate_buses aceita lines como List[str]
        pagination_result = filter_and_paginate_buses(
            full_bus_list=full_bus_list, page=1, limit=len(full_bus_list) + 1, lines=[line_id]
        )
        buses_for_line = pagination_result.get("items", [])
        if not buses_for_line: return []

        if ordem_id:
            buses_for_line = [bus for bus in buses_for_line if bus["ordem"] == ordem_id]

    except Exception as e: # Captura erros dos serviços Redis/Filter
        logger.exception(f"Erro ao obter/filtrar dados base para linha {line_id}: {e}")
        # Poderia levantar uma exceção específica aqui para a API tratar
        raise ServiceError(f"Falha ao obter dados base para linha {line_id}")
    
    # --- 2. Calcular Distâncias ---
    # add_distance_to_buses já trata erros internos de conversão, etc.
    buses_with_distance = add_distance_to_buses(buses_for_line, dest_lat, dest_lng)

    # --- 3. Analisar Proximidade/Direção ---
    # analyze_vehicle_proximity retorna a lista já com 'approaching' e 'distance'
    # e apenas o último registro de cada ônibus.
    try:
        proximity_results = analyze_vehicle_proximity(buses_with_distance)
        logger.info(f"Análise de proximidade concluída para {len(proximity_results)} ônibus únicos.")
    except Exception as e:
        logger.exception(f"Erro durante a análise de proximidade para linha {line_id}: {e}")
        # Decide como tratar: retornar vazio ou levantar erro? Vamos retornar vazio.
        return []
    
    # --- 4. Calcular ETAs Condicionalmente e Montar Resposta Final ---
    final_statuses: List[BusStatus] = []
    departure_time_for_eta = datetime.now(ZoneInfo("America/Sao_Paulo")) # Hora atual para ETA

    for bus_info in proximity_results:
        if not isinstance(bus_info, dict): continue # Segurança

        eta_seconds: Optional[int] = None
        is_approaching: bool = bus_info.get("approaching", False) # Pega o status

        # Só calcula ETA se estiver se aproximando
        if is_approaching is True or ordem_id:
            logger.debug(f"Ônibus {bus_info.get('ordem')} aproximando ou Requisitado pontualmente, calculando ETA...")
            # Pega coords do ônibus atual (resultado da análise)
            lat_str = bus_info.get("latitude")
            lon_str = bus_info.get("longitude")
            bus_lat = safe_float_convert(lat_str)
            bus_lon = safe_float_convert(lon_str)

            if bus_lat is not None and bus_lon is not None:
                try:
                    # Chama a função síncrona de ETA
                    eta_info = get_travel_time_estimate(
                        origin_lat=bus_lat, origin_lng=bus_lon,
                        dest_lat=dest_lat, dest_lng=dest_lng,
                        modal=TravelMode.BUS, 
                        departure_time=departure_time_for_eta
                    )
                    if eta_info:
                        eta_seconds = eta_info.get("bus", False)
                        if not eta_seconds :
                            eta_seconds = eta_info.get("total_travel_time_seconds")
                        logger.info(f"ETA calculado para {bus_info.get('ordem')}: {eta_seconds}s | Total Trave: {eta_info.get('total_travel_time_seconds')}s")
                    else:
                         logger.warning(f"get_travel_time_estimate retornou None para {bus_info.get('ordem')}")

                except Exception as eta_err:
                    # Loga erro do cálculo de ETA mas continua o processo
                    logger.exception(f"Erro ao calcular ETA para ônibus {bus_info.get('ordem')}: {eta_err}")
            else:
                logger.warning(f"Coordenadas inválidas no resultado da análise para {bus_info.get('ordem')}, não calculando ETA.")

        # --- Montar o objeto BusStatus Final ---
        try:
            # Converte timestamp (assumindo que está em 'datahora' como string de ms)
            ts_str = bus_info.get("datahora", "0")
            ts_utc = datetime.fromtimestamp(int(ts_str) / 1000, tz=timezone.utc)
            ts_local = ts_utc.astimezone(ZoneInfo("America/Sao_Paulo"))

            status = BusStatus(
                ordem=str(bus_info.get("ordem", "N/A")),
                # Usa safe_float_convert para garantir float ou None (mas BusStatus espera float)
                # Melhor tratar None aqui ou garantir que não chegue None. Usando 0.0 como fallback.
                latitude=safe_float_convert(bus_info.get("latitude")) or 0.0,
                longitude=safe_float_convert(bus_info.get("longitude")) or 0.0,
                velocidade=safe_float_convert(bus_info.get("velocidade")) or 0.0,
                linha=str(bus_info.get("linha", line_id)),
                datahora_ultima=ts_local,
                approaching=is_approaching, # Inclui o status de aproximação
                distance_km=safe_float_convert(bus_info.get("distance")), # Pega a distância Haversine
                eta_seconds=eta_seconds # Inclui o ETA (ou None)
            )
            final_statuses.append(status)
        except Exception as format_err:
            logger.exception(f"Erro ao formatar dados finais para ônibus {bus_info.get('ordem')}: {format_err}")


    logger.info(f"Retornando status final para {len(final_statuses)} ônibus da linha {line_id}.")
    return final_statuses