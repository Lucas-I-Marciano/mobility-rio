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

export const fetchSingleBusEta = async (lineId, destLat, destLng, ordemId) => {
  if (!lineId || destLat == null || destLng == null || !ordemId) {
    console.warn("fetchSingleBusEta chamada com parâmetros inválidos.");
    return null; // Retorna null se faltar algo
  }
  try {
    // Chama o MESMO endpoint, mas adiciona o ordem_id
    const response = await apiClient.get(`/bus/lines/${lineId}/status`, {
      params: {
        dest_lat: destLat,
        dest_lng: destLng,
        ordem_id: ordemId, // <<< Adiciona o ID do ônibus específico
      },
    });
    // O backend retorna uma lista, mesmo filtrando por um ônibus.
    // Pegamos o primeiro resultado (se existir) e retornamos apenas o ETA.
    if (
      response.data &&
      Array.isArray(response.data) &&
      response.data.length > 0
    ) {
      return response.data[0].eta_seconds; // Retorna apenas os segundos do ETA ou null
    } else {
      return null; // Ônibus não encontrado ou sem ETA na resposta
    }
  } catch (error) {
    console.error(
      `Erro ao buscar ETA para ônibus ${ordemId} da linha ${lineId}:`,
      error.response || error.message
    );
    throw error; // Re-levanta para ser tratado no componente
  }
};
