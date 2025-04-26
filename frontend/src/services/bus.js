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
