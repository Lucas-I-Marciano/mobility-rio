import { Marker, Popup, useMapEvents } from "react-leaflet";
// Removido useState se não for mais necessário (o marker pode vir do contexto)
// import { useState } from "react";
import { useLocation } from "../context/location";
import L from "leaflet"; // Para ícone customizado
import { useState } from "react";

// Ícone customizado para o ponto de ônibus selecionado
const busStopIcon = new L.Icon({
  /* ... configuração do ícone ... */
});

export const AddMarker = () => {
  // Pega e Seta o busStopLocation do contexto
  const { busStopLocation, setBusStopLocation, isStopSelectionLocked } =
    useLocation();
  const [markerPosition, setMarkerPosition] = useState(null); // Use local state for the marker

  useMapEvents({
    click(e) {
      console.log(isStopSelectionLocked);

      if (isStopSelectionLocked) {
        console.log("Seleção de ponto está bloqueada.");
        return; // Não faz nada se estiver bloqueado
      }
      const clickedPos = { lat: e.latlng.lat, lng: e.latlng.lng };
      setMarkerPosition(clickedPos); // Update local state for rendering THIS marker
      setBusStopLocation(clickedPos); // Update global state for other components (like the button)
    },
  });

  // Renderiza o marcador baseado diretamente no estado global busStopLocation
  return busStopLocation === null ? null : (
    <Marker position={busStopLocation} /* icon={busStopIcon} */>
      <Popup>Ponto de ônibus selecionado</Popup>
    </Marker>
  );
};
