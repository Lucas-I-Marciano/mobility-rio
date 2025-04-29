import { apiClient } from "../client/api";

export const fetchBusLines = async () => {
  try {
    const response = await apiClient.get("/bus/lines");
    return response.data;
  } catch (error) {
    console.error("Error fetching bus lines:", error);
    throw error;
  }
};

export const fetchBusStatusForLine = async (lineId, destLat, destLng) => {
  console.log("SERVICE fetchBusStatusForLine - Called with:", {
    lineId,
    destLat,
    destLng,
  });
  if (!lineId || destLat == null || destLng == null) {
    console.warn(
      "SERVICE fetchBusStatusForLine - Invalid parameters, returning empty array."
    );
    // Não faz sentido chamar sem linha ou destino
    return []; // Retorna vazio se faltar parâmetro
  }
  try {
    console.log(
      `SERVICE fetchBusStatusForLine - Attempting GET /bus/lines/${lineId}/status`
    );
    const response = await apiClient.get(`/bus/lines/${lineId}/status`, {
      params: {
        dest_lat: destLat,
        dest_lng: destLng,
      },
    });
    console.log("SERVICE fetchBusStatusForLine - API call success."); // Log 4: Ver se a chamada deu certo
    // Assumindo que o backend retorna diretamente a lista de BusStatus
    // Se o backend paginar, você precisará pegar response.data.items ou similar
    return response.data;
  } catch (error) {
    console.error(
      `Erro ao buscar status para linha ${lineId}:`,
      error.response || error.message
    );
    console.error(
      `SERVICE fetchBusStatusForLine - API call error for line ${lineId}:`,
      error.response || error
    );
    throw error; // Re-levanta para ser tratado no componente
  }
};
