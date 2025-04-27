from app.core.celery_config import celery_app
from app.services.redis import get_latest_bus_data
from app.services.bus_filtering import filter_and_paginate_buses, add_distance_to_buses
from app.utils.bus_record import analyze_vehicle_movement_distance, analyze_vehicle_proximity # Supondo que exista
from app.services.travel_time import get_travel_time_estimate
from app.services.notification import send_notification_email # Supondo que exista
from app.schemas.travel_mode import TravelMode
# --- Acesso ao DB (Exemplo - ajuste para sua configuração SQLModel/SQLAlchemy) ---
# from app.db import SessionLocal # Ou sua forma de obter uma session
from app.db import get_session, Session, engine
from app.db.user_alerts import UserAlert # Seu modelo de alerta do DB
from sqlmodel import select # Se usar SQLModel
# -----------------------------------------------------------------------------
from app.core.redis import redis_client # Cliente Redis para cooldown

from datetime import datetime, timezone, time
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.check_bus_alerts")
def check_bus_alerts(): # Async pois chama get_travel_time_estimate
    logger.info("Iniciando task check_bus_alerts...")
    session = None # Inicializa session
    try:
        now = datetime.now(ZoneInfo("America/Sao_Paulo"))
        current_time_of_day = now.time()
        logger.info(f"Hora atual para verificação: {current_time_of_day}")

        # --- 1. Buscar Alertas Ativos na Janela de Tempo ---
        active_alerts = []
        with Session(engine) as session:    
            # Ajuste a query para seu ORM/SQL
            statement = select(UserAlert).where(
                UserAlert.alert_active == True,
                UserAlert.time_window_start <= current_time_of_day,
                UserAlert.time_window_end >= current_time_of_day
            )
            results = session.exec(statement)
            active_alerts = results.all()
        logger.info(f"Encontrados {len(active_alerts)} alertas ativos na janela atual.")
        # --- Fim Busca Alertas ---

        if not active_alerts:
            return "Nenhum alerta ativo na janela."

        # --- 2. Buscar Dados dos Ônibus ---
        try:
            full_bus_list = get_latest_bus_data()
        except:
            logger.warning("Dados de ônibus não encontrados no Redis.")
            return "Dados de ônibus indisponíveis."
        # Adicione outros excepts de serviço se necessário
        # --- Fim Busca Ônibus ---

        # --- 3. Processar Cada Alerta ---
        for alert in active_alerts:
            logger.info(f"Processando Alerta ID: {alert.id} | Linha: {alert.bus_line} | Email: {alert.user_email}")

            # --- 3a. Filtrar por Linha ---
            # Usa a linha do alerta (Problema 2 resolvido)
            pagination_result = filter_and_paginate_buses(
                full_bus_list=full_bus_list, page=1, limit=len(full_bus_list)+1, lines=[alert.bus_line]
            )
            buses_for_line = pagination_result.get("items", [])
            if not buses_for_line: continue # Próximo alerta

            # --- 3b. Calcular Distâncias ---
            # Usa coords do alerta (Problema 1 resolvido)
            try:
                 dest_lat = float(alert.stop_latitude)
                 dest_lng = float(alert.stop_longitude)
            except (ValueError, TypeError):
                 logger.error(f"Coordenadas inválidas para o Alerta ID: {alert.id}. Pulando.")
                 continue # Próximo alerta

            buses_with_distance = add_distance_to_buses(buses_for_line, dest_lat, dest_lng)

            # --- 3c. Analisar Movimento ---
            # Idealmente, refatore analyze_vehicle_movement_distance para retornar:
            # [{'ordem': 'ID1', 'approaching': True, 'distance': 1.5}, ...]
            proximity_results = analyze_vehicle_proximity(buses_with_distance)

            # --- 3d. Filtrar Candidatos (< 5km e Approaching) ---
            candidate_buses_info = []
            for bus_info in proximity_results:
                if bus_info.get("approaching") is True and bus_info.get("distance", float('inf')) < 0.2: # Ou 5.0 km
                    # Encontrar dados originais para lat/lon se necessário para ETA
                    original_bus = next((b for b in buses_with_distance if b.get("ordem") == bus_info["ordem"]), None)
                    if original_bus:
                        candidate_buses_info.append({
                            "ordem": bus_info["ordem"],
                            "lat_str": original_bus["latitude"],
                            "lon_str": original_bus["longitude"],
                            # Adiciona outros dados do alert se necessário para a próxima etapa
                            "alert_id": alert.id,
                            "user_email": alert.user_email,
                            "stop_lat": dest_lat, # Já temos do loop de alertas
                            "stop_lon": dest_lng  # Já temos do loop de alertas
                        })

            logger.info(f"Alerta {alert.id}: {len(candidate_buses_info)} candidatos encontrados (<5km e aproximando).")

            # --- 3e. Verificar ETA para Candidatos ---
            for candidate in candidate_buses_info:
                bus_ordem = candidate["ordem"]
                cooldown_key = f"notified:{alert.id}:{bus_ordem}"

                # --- 3f. Verificar Cooldown ---
                if redis_client and redis_client.exists(cooldown_key):
                    logger.info(f"Cooldown ativo para alert {alert.id}, bus {bus_ordem}.")
                    continue # Próximo candidato

                # --- 3g. Calcular ETA ---
                try:
                    # Usa hora atual para departure_time (Problema 4 resolvido)
                    eta_departure_time = datetime.now(ZoneInfo("America/Sao_Paulo"))
                    origin_lat = float(candidate["lat_str"].replace(",", "."))
                    origin_lng = float(candidate["lon_str"].replace(",", "."))

                    print("Vou fazer requisição")
                    eta_result = get_travel_time_estimate(
                        origin_lat=origin_lat, origin_lng=origin_lng,
                        dest_lat=dest_lat, dest_lng=dest_lng,
                        modal=TravelMode.BUS,
                        departure_time=eta_departure_time
                    )

                    # --- 3h. Verificar Condição ETA (<= 10 min) ---
                    if eta_result and eta_result.get("total_travel_time_seconds") is not None:
                        if eta_result.get("bus") is not None :
                            eta_seconds = eta_result["bus"]
                        else :
                            eta_seconds = eta_result["total_travel_time_seconds"]
                        if eta_seconds <= 600:
                            logger.info(f"ALERTA! Bus {bus_ordem} para alert {alert.id} ({alert.user_email}) está a {eta_seconds}s.")
                            # --- 3i. Enviar Notificação ---
                            # Chame sua função de envio de email aqui
                            send_notification_email(email=alert.user_email, subject=f"Linha {alert.bus_line} em {eta_seconds/60} minutos", body=f"Ônibus{bus_ordem} da linha {alert.bus_line} chegará no ponto cadastrado em {eta_seconds/60} minutos" )

                            # --- 3j. Marcar Cooldown ---
                            if redis_client:
                                try:
                                     redis_client.set(cooldown_key, "sent", ex=1800) # 30 min TTL
                                except Exception as redis_err:
                                     logger.error(f"Falha ao setar cooldown no Redis para {cooldown_key}: {redis_err}")

                except ValueError as ve:
                    logger.error(f"Erro de conversão de coordenadas para ETA - Bus {bus_ordem}: {ve}")
                except Exception as eta_err:
                    logger.exception(f"Erro ao calcular ETA ou notificar para bus {bus_ordem}, alert {alert.id}: {eta_err}")

        # --- Fim do Loop de Alertas ---
        logger.info("Task check_bus_alerts concluída.")
        return f"Processados {len(active_alerts)} alertas."

    except Exception as e:
        logger.exception(f"Erro crítico na task check_bus_alerts: {e}")
        # Re-levanta o erro para que o Celery o marque como falha
        raise
    finally:
        # Garante que a sessão do DB seja fechada
        if session:
            session.close()