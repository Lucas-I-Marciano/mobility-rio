import datetime
import os
import httpx # Ou import requests

# ... (dentro da sua função utilitária no backend) ...

async def get_travel_time_estimate(origin_lat, origin_lng, dest_lat, dest_lng):
    """Calcula o tempo estimado de viagem usando a Travel Time API."""

    APP_ID = os.getenv("TRAVELTIME_APP_ID") # Use nomes claros no .env
    API_KEY = os.getenv("TRAVELTIME_API_KEY")

    if not APP_ID or not API_KEY:
        print("ERRO: Credenciais da Travel Time API não configuradas.")
        return None # Ou levante uma exceção

    # Hora atual em UTC, formato ISO 8601 exigido pela API
    # Adiciona alguns segundos para garantir que não seja no passado exato
    departure_time_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=15)
    departure_time_iso = departure_time_dt.isoformat(timespec='seconds').replace('+00:00', 'Z')

    api_url = "https://api.traveltimeapp.com/v4/routes"

    params = {
        "type": "public_transport",
        "origin_lat": str(origin_lat),
        "origin_lng": str(origin_lng),
        "destination_lat": str(dest_lat),
        "destination_lng": str(dest_lng),
        "departure_time": departure_time_iso,
        # Adicione outros parâmetros se necessário, como transport_modes, etc.
    }

    headers = {
        "X-Application-Id": APP_ID,
        "X-Api-Key": API_KEY,
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params, headers=headers, timeout=30)
            response.raise_for_status() # Levanta erro para 4xx/5xx

            results = response.json()

            try:
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

                # Sum the travel_time from each part
                total_travel_time_seconds = 0
                mode_times = {}
                for part in parts:
                    if isinstance(part, dict):
                        mode = part.get("mode")
                        travel_time = part.get("travel_time") # Get time, check type later

                        # Ensure mode is a valid string and travel_time is a valid number
                        if isinstance(mode, str) and mode and isinstance(travel_time, (int, float)) and travel_time >= 0:
                            # Convert to int just in case it's float
                            time_seconds = int(travel_time)

                            # Add to total time
                            total_travel_time_seconds += time_seconds

                            # Add to time for this specific mode
                            mode_times[mode] = mode_times.get(mode, 0) + time_seconds
                        else:
                            # Log if a part is skipped due to missing/invalid mode or time
                            part_id = part.get('id', 'N/A')
                            if not isinstance(mode, str) or not mode:
                                print(f"WARN: Skipping part {part_id} due to missing or invalid mode: {mode}")
                            if not isinstance(travel_time, (int, float)) or travel_time < 0:
                                print(f"WARN: Skipping part {part_id} due to missing or invalid travel_time: {travel_time}")

                # Check if any travel time was actually found
                if total_travel_time_seconds > 0 or len(parts) == 0:
                    response_dict = {"total_travel_time_seconds": total_travel_time_seconds}
                    # Add the time for each mode found
                    response_dict.update(mode_times)
                    return response_dict # Return the dictionary
                else:
                    # Handle cases where parts exist but have no travel time (unlikely but possible)
                    print(f"WARN: No valid travel time found in route parts. Parts: {parts}")
                    return None

            except (KeyError, IndexError, TypeError) as e:
                # Catch potential errors during parsing if checks above fail unexpectedly
                print(f"ERRO: Error parsing Travel Time response structure: {e}. Response: {results}")
                return None

    except httpx.TimeoutException:
        print("ERRO: Timeout ao chamar Travel Time API.")
        return None
    except httpx.RequestError as exc:
        print(f"ERRO: Erro na requisição para Travel Time API: {exc}")
        # Verificar se exc.response existe para logar status code/body
        if exc.response is not None:
            print(f"Travel Time Response Status: {exc.response.status_code}")
            try:
                print(f"Travel Time Response Body: {exc.response.json()}")
            except:
                print(f"Travel Time Response Body: {exc.response.text}")
        return None
    except Exception as e:
        print(f"ERRO: Erro inesperado ao processar Travel Time API: {e}")
        return None