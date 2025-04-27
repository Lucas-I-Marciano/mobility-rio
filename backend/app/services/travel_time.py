import datetime
import os
import httpx # Ou import requests
import logging
from zoneinfo import ZoneInfo
from datetime import timezone 
from app.schemas.travel_mode import TravelMode # Assuming Enum is here

logger = logging.getLogger(__name__)

async def get_travel_time_estimate(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    modal: TravelMode, # Use the Enum type
    departure_time: datetime
):
    """
    Calculates the estimated travel time using the Travel Time API via POST.
    Returns a dictionary with total_travel_time_seconds and mode breakdown, or None.
    """
    APP_ID = os.getenv("TRAVELTIME_APP_ID")
    API_KEY = os.getenv("TRAVELTIME_API_KEY")

    if not APP_ID or not API_KEY:
        logger.error("Credenciais da Travel Time API não configuradas.")
        return None

    # --- Calculate Departure Time (UTC ISO) ---
    try:
       if departure_time.tzinfo is None:
            # Isso não deveria acontecer se o frontend enviar offset
            logger.error("Erro: departure_time recebido sem informação de fuso horário.")
            # Você pode tentar aplicar um fuso padrão aqui ou levantar erro
            raise ValueError("departure_time deve incluir informação de fuso horário.")
       # Converte o datetime 'aware' para UTC
       departure_time_utc = departure_time.astimezone(timezone.utc)
       # Formata para ISO 8601 com 'Z' (Zulu time = UTC)
       # Removendo microssegundos se houver e adicionando Z
       departure_time_iso_z = departure_time_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    except Exception as e:
        logger.error(f"Erro ao calcular departure_time: {e}")
        return None
    # --- End Departure Time Calculation ---

    # --- Define API Endpoint and Headers ---
    # Using time-filter endpoint which often takes POST
    api_url = "https://api.traveltimeapp.com/v4/routes"
    headers = {
        "X-Application-Id": APP_ID,
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json", # Important for POST
        "Accept": "application/json"
    }
    # --- End Headers ---

    # --- Construct Request Body ---
    request_body = {
        "locations": [
            {
                "id": "origin_point", # Assign arbitrary IDs
                "coords": {"lat": origin_lat, "lng": origin_lng}
            },
            {
                "id": "destination_point",
                "coords": {"lat": dest_lat, "lng": dest_lng}
            }
        ],
        "departure_searches": [
            {
                "id": "search_eta_from_origin_to_dest", # Arbitrary search ID
                "departure_location_id": "origin_point", # Match origin ID
                "arrival_location_ids": ["destination_point"], # Match destination ID(s)
                "departure_time": departure_time_iso_z,
                # Request only travel_time, maybe distance if needed?
                "properties": ["travel_time", "route", "fares"],
                "transportation": {
                    # Use the enum value (which is a string)
                    "type": modal
                }
                # Add range or other parameters if needed
            }
        ]
    }
    # --- End Request Body ---

    logger.info(f"Enviando requisição POST para Travel Time API: {api_url} com departure_time: {departure_time_iso_z}")
    # logger.debug(f"Request Body: {request_body}") # Log body only if needed for debug

    try:
        async with httpx.Client() as client:
            # Use POST, passing headers and json body
            response = await client.post(api_url, headers=headers, json=request_body, timeout=30)
            response.raise_for_status() # Check for HTTP errors

            results = response.json()
            logger.debug(f"Travel Time API Response Body: {results}") # Log the full response for debugging parsing

            try :
                # Navigate safely to the 'parts' list
                # results -> list -> [0] -> dict
                first_result = results.get("results")
                if not first_result or not isinstance(first_result, list) or len(first_result) == 0:
                    print(f"WARN: 'results' array missing or empty in Travel Time response.")
                    return None

                # locations -> list -> [0] -> dict
                locations = first_result[0].get("locations")
                if not locations or not isinstance(locations, list) or len(locations) == 0:
                    print(f"WARN: 'locations' array missing or empty in Travel Time result.")
                    return None

                # properties -> list -> [0] -> dict
                properties = locations[0].get("properties")
                if not properties or not isinstance(properties, list) or len(properties) == 0:
                    print(f"WARN: 'properties' array missing or empty in Travel Time location.")
                    return None

                # route -> dict
                route = properties[0].get("route")
                if not route or not isinstance(route, dict):
                    print(f"WARN: 'route' object missing or invalid in Travel Time properties.")
                    return None

                # parts -> list
                parts = route.get("parts")
                if not parts or not isinstance(parts, list):
                    print(f"WARN: 'parts' array missing or invalid in Travel Time route.")
                    return None
                
                mode_times = {}
                for part in parts:
                    if isinstance(part, dict):
                        mode = part.get("mode")
                        travel_time = part.get("travel_time") # Get time, check type later

                        # Ensure mode is a valid string and travel_time is a valid number
                        if isinstance(mode, str) and mode and isinstance(travel_time, (int, float)) and travel_time >= 0:
                            # Convert to int just in case it's float
                            time_seconds = int(travel_time)

                            # Add to time for this specific mode
                            mode_times[mode] = mode_times.get(mode, 0) + time_seconds
                        else:
                            # Log if a part is skipped due to missing/invalid mode or time
                            part_id = part.get('id', 'N/A')
                            if not isinstance(mode, str) or not mode:
                                print(f"WARN: Skipping part {part_id} due to missing or invalid mode: {mode}")
                            if not isinstance(travel_time, (int, float)) or travel_time < 0:
                                print(f"WARN: Skipping part {part_id} due to missing or invalid travel_time: {travel_time}")
            except:
                pass

            # --- Parse the time-filter response ---
            if not results.get("results") or not isinstance(results["results"], list) or len(results["results"]) == 0:
                 logger.warning(f"WARN: 'results' array missing or empty in Travel Time response.")
                 return None

            search_result = results["results"][0] # Get the first search result

            # Find the destination location details within this result
            # The API returns details for arrival locations in the 'locations' list
            destination_details = None
            for loc in search_result.get("locations", []):
                 if loc.get("id") == "destination_point": # Find by the ID we assigned
                     destination_details = loc
                     break

            if not destination_details:
                logger.warning(f"WARN: Destination details ('destination_point') not found in Travel Time response locations.")
                return None

            # Extract properties (travel_time) for the destination
            # Properties list might be empty if unreachable
            properties = destination_details.get("properties")
            if not properties or not isinstance(properties, list) or len(properties) == 0:
                 # This might mean the destination is unreachable within constraints
                 logger.info(f"INFO: Destino ('destination_point') inalcançável ou sem propriedades retornadas. Pode ser normal.")
                 # Return a specific indicator for unreachable? Or just None/0? Let's return None.
                 # Could return {'total_travel_time_seconds': -1} to indicate unreachable specifically.
                 return None # Indicate failure to find time

            # Assuming travel_time is the first property if requested
            travel_time_seconds = properties[0].get("travel_time")

            if travel_time_seconds is not None and isinstance(travel_time_seconds, (int, float)) and travel_time_seconds >= 0:
                # --- Prepare the structured response (Total only, as mode breakdown isn't directly available in time-filter) ---
                # The time-filter response gives the total time, not parts breakdown by default.
                # To get parts, you'd need to request 'route' in properties and parse *that*,
                # similar to the previous GET /routes logic.
                # For now, just return the total time as requested by "properties": ["travel_time"]
                response_dict = {
                     "total_travel_time_seconds": int(travel_time_seconds),
                     # Mode breakdown is NOT directly available here. Add placeholder or remove.
                     # modal.value: int(travel_time_seconds) # Assign total time to the requested mode? Maybe misleading.
                }
                response_dict.update(mode_times)
                # Let's return a simpler dict for now, focusing on total time from time-filter
                return response_dict

            else:
                logger.warning(f"WARN: 'travel_time' não encontrado ou inválido nas propriedades do destino. Properties: {properties}")
                return None
            # --- End Parsing ---

    # Keep outer exception handling
    except httpx.TimeoutException:
        logger.error("ERRO: Timeout ao chamar Travel Time API.")
        return None
    except httpx.RequestError as exc:
        logger.error(f"ERRO: Erro na requisição para Travel Time API: {exc}")
        if exc.response is not None:
            logger.error(f"Travel Time Response Status: {exc.response.status_code}")
            try:
                logger.error(f"Travel Time Response Body: {exc.response.json()}")
            except:
                logger.error(f"Travel Time Response Body: {exc.response.text}")
        return None
    except Exception as e:
        logger.exception(f"ERRO: Erro inesperado ao processar Travel Time API POST: {e}") # Use logger.exception
        return None