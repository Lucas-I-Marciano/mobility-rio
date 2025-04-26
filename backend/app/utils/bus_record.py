from collections import defaultdict

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

    # Converte defaultdict de volta para dict para a saída final (opcional, mas comum)
    return dict(grouped_data)