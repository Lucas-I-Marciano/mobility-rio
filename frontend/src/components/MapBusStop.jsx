import { useState } from "react";
import {
  MapContainer,
  TileLayer,
  useMap,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import { useLocation } from "../context/location";
import { AddMarker } from "./AddMarker";
import customMarker from "../assets/map-marker.png";
import man from "../assets/man.png";

export function MapBusStop({ initialCenter, busData }) {
  // Remove userLocation do context daqui se não for usar o marcador azul
  // const { userLocation } = useLocation();

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
