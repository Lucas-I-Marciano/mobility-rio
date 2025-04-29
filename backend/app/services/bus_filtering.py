# backend/app/services/bus_filtering.py
import math
from typing import List, Dict, Any, Optional # Import Optional
import logging
from datetime import datetime, timezone
from decimal import Decimal # Para lidar com tipos do DB se necessário
from zoneinfo import ZoneInfo

from app.services.redis import get_latest_bus_data
from app.services.travel_time import get_travel_time_estimate # Função síncrona agora
from app.schemas.travel_mode import TravelMode
from app.schemas.bus_response import BusStatus # Importa o modelo de resposta

from app.utils.coordinates_distance import haversine

logger = logging.getLogger(__name__)

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


def get_line_status_with_eta(line_id: str, dest_lat: float, dest_lng: float) -> List[BusStatus]:
    """
    Obtém o status mais recente dos ônibus de uma linha e calcula o ETA para um destino.
    """
    logger.info(f"Buscando status para linha {line_id} com destino ({dest_lat}, {dest_lng})")

    # 1. Buscar todos os dados recentes
    # Tratar exceções que get_latest_bus_data pode levantar (DataNotFound, etc)
    full_bus_list = get_latest_bus_data()
    if not full_bus_list:
        return [] # Retorna lista vazia se não há dados base

    # 2. Filtrar pela linha desejada
    buses_on_line = [
        bus for bus in full_bus_list
        if isinstance(bus, dict) and str(bus.get("linha")) == str(line_id)
    ]
    if not buses_on_line:
        logger.info(f"Nenhum ônibus encontrado para a linha {line_id} nos dados recentes.")
        return []

    # 3. Obter o registro mais recente para cada ônibus único na linha
    latest_bus_map = get_latest_bus_records(buses_on_line)
    logger.info(f"Encontrados {len(latest_bus_map)} ônibus únicos na linha {line_id}.")

    # 4. Calcular ETA e formatar a saída
    results: List[BusStatus] = []
    departure_time_for_eta = datetime.now(ZoneInfo("America/Sao_Paulo")) # Hora atual para ETA

    for ordem, bus_data in latest_bus_map.items():
        try:
            # Limpeza e Conversão de Dados
            lat_str = bus_data.get("latitude", "0").replace(",", ".")
            lon_str = bus_data.get("longitude", "0").replace(",", ".")
            spd_str = bus_data.get("velocidade", "0").replace(",", ".")
            ts_str = bus_data.get("datahora", "0") # Timestamp em milissegundos (string)

            lat = float(lat_str)
            lon = float(lon_str)
            speed = float(spd_str)
            # Converte timestamp de milisegundos para datetime UTC e depois SP
            ts_utc = datetime.fromtimestamp(int(ts_str) / 1000, tz=timezone.utc)
            ts_local = ts_utc.astimezone(ZoneInfo("America/Sao_Paulo"))

            # Calcular ETA (chamando a função síncrona)
            eta_info = get_travel_time_estimate(
                origin_lat=lat,
                origin_lng=lon,
                dest_lat=dest_lat,
                dest_lng=dest_lng,
                modal=TravelMode.BUS, # Ou outro default
                departure_time=departure_time_for_eta
            )
            eta_seconds = eta_info.get("total_travel_time_seconds") if eta_info else None
                

            # Montar objeto de status
            status = BusStatus(
                ordem=ordem,
                latitude=lat,
                longitude=lon,
                velocidade=speed,
                linha=str(bus_data.get("linha", line_id)), # Garante string
                datahora_ultima=ts_local, # Usa o datetime local formatado
                eta_seconds=eta_seconds
            )
            results.append(status)

        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Erro processando dados para ônibus {ordem}: {e}. Dados: {bus_data}")
        except Exception as e:
            logger.exception(f"Erro inesperado processando ônibus {ordem}: {e}")

    logger.info(f"Retornando status para {len(results)} ônibus da linha {line_id}.")
    return results