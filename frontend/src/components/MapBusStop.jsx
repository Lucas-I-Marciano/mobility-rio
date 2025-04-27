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

export function MapBusStop({ initialCenter }) {
  // Remove userLocation do context daqui se não for usar o marcador azul
  // const { userLocation } = useLocation();

  // Usa initialCenter vindo das props para centralizar
  const centerCoords = initialCenter
    ? [initialCenter.lat, initialCenter.lng]
    : [-22.9068, -43.1729]; // Fallback para Rio

  return (
    <div className="h-[60vh] md:h-[70vh] w-full border rounded overflow-hidden shadow">
      {" "}
      {/* Estilo e Tamanho Corrigidos */}
      <MapContainer
        style={{ height: "100%", width: "100%" }}
        center={centerCoords} // Usa as coordenadas recebidas
        zoom={16} // Começa com mais zoom
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {/* Marcador Opcional para a localização confirmada do usuário (prop initialCenter) */}
        {initialCenter && (
          <Marker position={centerCoords} /* icon={algumIconeDiferente} */>
            <Popup>Sua localização confirmada</Popup>
          </Marker>
        )}
        {/* Remove o marcador antigo baseado no userLocation do contexto */}
        {/* <Marker position={userLocation}><Popup>Você está aqui</Popup></Marker> */}
        <AddMarker />{" "}
        {/* Deixa AddMarker cuidar do marcador do ponto clicado */}
      </MapContainer>
    </div>
  );
}
