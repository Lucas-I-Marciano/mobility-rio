import React from "react"; // Removido useEffect se não for usado para load inicial
import { Marker, Popup, useMapEvents } from "react-leaflet";
import { useLocation } from "../context/location";

export const LocateUser = () => {
  // Pega userLocation para o Marker e os setters/state do contexto
  const {
    userLocation,
    setUserLocation,
    setIsLoadingLocation,
    setLocationError,
  } = useLocation();

  const map = useMapEvents({
    click() {
      // Inicia o processo de localização
      setLocationError(null); // Limpa erros antigos
      setIsLoadingLocation(true);
      map.locate(); // Dispara a geolocalização do Leaflet/navegador
    },
    locationfound(e) {
      console.log("Location found:", e.latlng);
      setUserLocation(e.latlng);
      map.flyTo(e.latlng, 16); // Centraliza e dá zoom
      setIsLoadingLocation(false);
      setLocationError(null); // Limpa qualquer erro anterior
    },
    locationerror(e) {
      // Handler para erros de geolocalização
      console.error("Location error:", e);
      let message = "Erro ao obter localização.";
      if (e.code === 1) {
        // PERMISSION_DENIED
        message =
          "Permissão de localização negada. Verifique as configurações do navegador.";
      } else if (e.code === 2) {
        // POSITION_UNAVAILABLE
        message = "Localização indisponível no momento.";
      } else if (e.code === 3) {
        // TIMEOUT
        message = "Tempo esgotado ao buscar localização.";
      }
      setUserLocation(null); // Garante que não há localização definida
      setLocationError(message);
      setIsLoadingLocation(false);
    },
  });

  // Renderiza marcador apenas se a localização foi encontrada com sucesso
  return userLocation === null ? null : (
    <Marker position={userLocation}>
      <Popup>Localização Atual Encontrada</Popup>
    </Marker>
  );
};
