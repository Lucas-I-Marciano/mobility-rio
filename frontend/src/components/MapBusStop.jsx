import React, { useState } from "react";
import {
  MapContainer,
  TileLayer,
  useMap,
  Polyline,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import { useLocation } from "../context/location";
import { AddMarker } from "./AddMarker";
import customMarker from "../assets/map-marker.png";
import man from "../assets/man.png";
import L from "leaflet";

export function MapBusStop({ initialCenter, busData }) {
  // Remove userLocation do context daqui se não for usar o marcador azul
  const { busStopLocation } = useLocation();

  // Usa initialCenter vindo das props para centralizar
  const centerCoords = initialCenter
    ? [initialCenter.lat, initialCenter.lng]
    : [-22.9068, -43.1729]; // Fallback para Rio

  // Função auxiliar para formatar ETA no Popup
  const formatEtaPopup = (seconds) => {
    if (seconds === null || seconds === undefined || seconds < 0) return "N/A";
    const minutes = Math.round(seconds / 60);
    return `${minutes} min`;
  };

  const busIcon = new L.Icon({
    iconUrl: customMarker, // Substitua pelo caminho do ícone de ônibus
    iconSize: [30, 30],
    iconAnchor: [15, 30],
  });
  const userIcon = new L.Icon({
    iconUrl: man, // Ícone azul padrão ou outro
    iconSize: [44, 44],
    iconAnchor: [13, 36],
  });

  // --- Estilo para as Linhas ---
  const polylineOptions = {
    color: "#0ea5e9", // Azul claro (Tailwind blue-400)
    weight: 4,
    opacity: 0.7,
    dashArray: "5, 10", // Linha tracejada
  };

  // Função auxiliar para limpar/converter coordenadas (reutilizar se já tiver)
  const parseCoords = (latStr, lngStr) => {
    let lat = null,
      lng = null;
    if (typeof latStr === "string" && typeof lngStr === "string") {
      try {
        lat = parseFloat(latStr.replace(",", "."));
        lng = parseFloat(lngStr.replace(",", "."));
      } catch (e) {
        console.error("Erro parseCoords:", e);
      }
    } else if (typeof latStr === "number" && typeof lngStr === "number") {
      lat = latStr;
      lng = lngStr;
    }
    if (lat !== null && lng !== null && !isNaN(lat) && !isNaN(lng)) {
      // Verifica se são números válidos
      return { lat, lng };
    }
    console.warn(
      `Coordenadas inválidas recebidas: lat=${latStr}, lng=${lngStr}`
    );
    return null;
  };

  return (
    <div className="h-[60vh] md:h-[70vh] w-full border rounded overflow-hidden shadow">
      {/* Estilo e Tamanho Corrigidos */}
      <MapContainer
        style={{ height: "100%", width: "100%" }}
        center={centerCoords} // Usa as coordenadas recebidas
        zoom={15} // Começa com mais zoom
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {/* Marcador Opcional para a localização confirmada do usuário (prop initialCenter) */}
        {initialCenter && (
          <Marker position={centerCoords} icon={userIcon}>
            <Popup>Sua localização confirmada</Popup>
          </Marker>
        )}
        {/* Remove o marcador antigo baseado no userLocation do contexto */}
        {/* <Marker position={userLocation}><Popup>Você está aqui</Popup></Marker> */}
        <AddMarker />

        {busStopLocation &&
          Array.isArray(busData) &&
          busData.map((bus) => {
            const busCoords = parseCoords(bus.latitude, bus.longitude);
            const stopCoords = busStopLocation; // Já deve ser {lat, lng}

            console.log(busCoords);
            console.log(stopCoords);

            // Pula este ônibus se as coordenadas dele ou do ponto forem inválidas
            if (
              !busCoords ||
              !stopCoords ||
              stopCoords.lat == null ||
              stopCoords.lng == null
            ) {
              console.warn(
                `Skipping line/marker for bus ${bus.ordem} due to invalid coords.`
              );
              return null;
            }

            // Define os pontos para a linha Polyline [ [lat,lng], [lat,lng] ]
            const linePositions = [
              [stopCoords.lat, stopCoords.lng], // Ponto selecionado
              [busCoords.lat, busCoords.lng], // Posição do ônibus
            ];

            return (
              // Usa Fragment para agrupar elementos por ônibus
              <React.Fragment key={bus.ordem}>
                {/* Marcador do Ônibus */}
                <Marker
                  position={[busCoords.lat, busCoords.lng]}
                  icon={busIcon}
                >
                  <Popup>
                    <div>
                      <p>
                        <strong>Ordem:</strong> {bus.ordem}
                      </p>
                      <p>
                        <strong>Linha:</strong> {bus.linha}
                      </p>
                      <p>
                        <strong>Aprox.?</strong>{" "}
                        {bus.approaching ? "Sim" : "Não"}
                      </p>
                      <p>
                        <strong>Dist. Reta:</strong>{" "}
                        {bus.distance_km?.toFixed(1)} km
                      </p>
                      {/* Adicione outras infos úteis como ETA */}
                    </div>
                  </Popup>
                </Marker>

                {/* Linha (Polyline) conectando ponto ao ônibus */}
                <Polyline
                  positions={linePositions}
                  pathOptions={polylineOptions} // Aplica o estilo
                />
              </React.Fragment>
            );
          })}

        {Array.isArray(busData) &&
          busData.map((bus) => {
            // Valida e converte coordenadas antes de usar
            const latStr = bus.latitude;
            const lngStr = bus.longitude;
            let lat = null;
            let lng = null;

            if (typeof latStr === "string" && typeof lngStr === "string") {
              try {
                lat = parseFloat(latStr.replace(",", "."));
                lng = parseFloat(lngStr.replace(",", "."));
              } catch (e) {
                console.error(
                  `Coordenadas inválidas para ônibus ${bus.ordem}: ${latStr}, ${lngStr}`
                );
              }
            } else if (
              typeof latStr === "number" &&
              typeof lngStr === "number"
            ) {
              lat = latStr;
              lng = lngStr;
            }

            // Só renderiza se tiver coordenadas válidas
            if (lat === null || lng === null) {
              return null;
            }

            return (
              <Marker
                key={bus.ordem} // Usa ordem como key única
                position={[lat, lng]}
                icon={busIcon} // Ícone customizado de ônibus
              >
                <Popup>
                  <div>
                    <p>
                      <strong>Ordem:</strong> {bus.ordem}
                    </p>
                    <p>
                      <strong>Linha:</strong> {bus.linha}
                    </p>
                    <p>
                      <strong>Velocidade:</strong> {bus.velocidade?.toFixed(0)}{" "}
                      km/h
                    </p>
                    <p>
                      <strong>Aprox.?</strong> {bus.approaching ? "Sim" : "Não"}
                    </p>
                    <p>
                      <strong>Distância:</strong> {bus.distance_km?.toFixed(1)}{" "}
                      km
                    </p>
                    <p>
                      <strong>ETA:</strong> {formatEtaPopup(bus.eta_seconds)}
                    </p>
                    {/* <p>Últ. Atual.: {new Date(bus.datahora_ultima).toLocaleTimeString('pt-BR')}</p> */}
                  </div>
                </Popup>
              </Marker>
            );
          })}
      </MapContainer>
    </div>
  );
}
