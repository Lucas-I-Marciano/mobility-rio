import React, { useState } from "react"; // Removido useEffect se não for usado para load inicial
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

  const [initialLocateDone, setInitialLocateDone] = useState(false);

  const map = useMapEvents({
    click(e) {
      // Inicia o processo de localização
      setLocationError(null); // Limpa erros antigos
      if (!initialLocateDone) {
        // --- Primeira Interação: Tenta Geolocalização ---
        console.log("Primeiro clique: Disparando map.locate()...");
        setIsLoadingLocation(true);
        map.locate(); // Dispara a geolocalização do Leaflet/navegador
      } else {
        // --- Cliques Subsequentes: Define Manualmente ---
        const clickedPos = { lat: e.latlng.lat, lng: e.latlng.lng };
        console.log(
          "Clique subsequente: Definindo localização manualmente:",
          clickedPos
        );
        setUserLocation(clickedPos); // Atualiza a posição do marcador
        setIsLoadingLocation(false); // Garante que o loading parou
      }
    },
    locationfound(e) {
      console.log("Location found via locate():", e.latlng);
      setUserLocation(e.latlng);
      map.flyTo(e.latlng, 16); // Centraliza e dá zoom
      setIsLoadingLocation(false);
      setLocationError(null);
      setInitialLocateDone(true);
    },
    locationerror(e) {
      // Erro na geolocalização (geralmente no primeiro clique)
      console.error("Location error via locate():", e);
      let message = "Erro ao obter localização.";
      if (e.code === 1) {
        message = "Permissão de localização negada.";
      } else if (e.code === 2) {
        message = "Localização indisponível.";
      } else if (e.code === 3) {
        message = "Tempo esgotado ao buscar localização.";
      }

      setUserLocation(null); // Limpa localização
      setLocationError(message);
      setIsLoadingLocation(false);
      setInitialLocateDone(true); // Marca que a tentativa inicial foi feita (mesmo com erro)
      // para permitir o clique manual subsequente.
    },
  });

  // Renderiza marcador apenas se a localização foi encontrada com sucesso
  return userLocation === null ? null : (
    <Marker position={userLocation}>
      <Popup>Localização Atual Encontrada</Popup>
    </Marker>
  );
};
