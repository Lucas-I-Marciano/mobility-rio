from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Annotated
from sqlmodel import Session
import datetime

from app.schemas.user_alerts import UserAlertRead, UserAlertCreate
from app.db.user_alerts import UserAlert
from app.db import get_session
from app.schemas.travel_mode import TravelMode

from app.services.redis import get_latest_bus_data
from app.core.celery_config import celery_app
from app.services.bus_filtering import filter_and_paginate_buses, add_distance_to_buses
from app.utils.bus_record import process_vehicle_data, analyze_vehicle_movement_distance
from app.services.travel_time import get_travel_time_estimate

router = APIRouter(prefix="/alerts")

session_dependency = Annotated[Session, Depends(get_session)] # Help on database management

@router.post("/", response_model=UserAlertRead)
def create_user_alert(
    *,
    session: session_dependency,
    alert_in: UserAlertCreate
):
    # Cria uma instância do modelo de banco de dados a partir do modelo de entrada da API
    db_alert = UserAlert.model_validate(alert_in) # SQLModel v0.0.14+

    session.add(db_alert)
    session.commit()
    session.refresh(db_alert) # Recarrega o objeto para obter id, created_at, updated_at
    return db_alert

@router.get("/user-alerts/{alert_id}", response_model=UserAlertRead)
def read_user_alert(
    *,
    session: session_dependency,
    alert_id: int
):
    alert = session.get(UserAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="User Alert not found")
    return alert

@router.post("/teste")
async def teste(dest_lat_float = -22.984520, dest_lng_float = -43.217640, target_lines: Annotated[list[str], Body()] = ["457"]):
    full_bus_list = get_latest_bus_data()
    pagination_result = filter_and_paginate_buses(
            full_bus_list=full_bus_list,
            page=1,
            limit=len(full_bus_list) + 1, # Ensure limit > total items
            lines=target_lines
        )
    buses_for_line = pagination_result.get("items", [])

    results_with_distance = add_distance_to_buses(
            bus_list=buses_for_line,
            dest_lat=float(dest_lat_float),
            dest_lng=float(dest_lng_float)
        )
    
    processed_data = process_vehicle_data({"results" : results_with_distance})["all_data"]
    id_distance_list = analyze_vehicle_movement_distance(results_with_distance)

    filtered_id_distance_list = []
    for id_distance_dict in id_distance_list :
        if (list(id_distance_dict.values())[0]) & (list(id_distance_dict.values())[1] < 5):
            filtered_id_distance_list.append(id_distance_dict)

    list_to_get_time = []
    for object_id_distance_filtered in filtered_id_distance_list :
        key = list(object_id_distance_filtered.keys())[0]
        list_to_get_time.append([i for i in processed_data if i["ordem"] == key][-1])
    
    print(f"Faria a consulta para {len(list_to_get_time)} onibus")
    to_return = {}
    for count, object_to_consult_time in enumerate(list_to_get_time) :
        origin_lat = object_to_consult_time["latitude"]
        origin_lng= object_to_consult_time["longitude"]
        dest_lat=-22.984520
        dest_lng=-43.217640
        modal=TravelMode.BUS.value
        departure_time=datetime.datetime.fromisoformat("2025-04-26T20:24:00-03:00")
        print(f"Fazendo a consulta para o ônibus em lat:{origin_lat} e lng:{origin_lng}")
        response = await get_travel_time_estimate(
            origin_lat=float(origin_lat.replace(",", ".")),
            origin_lng=float(origin_lng.replace(",", ".")),
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            modal=modal,
            departure_time=departure_time
        )
        to_return[object_to_consult_time["ordem"]] = response
        if count == 2 :
            break
    return {"message" : "ok", "data": to_return}