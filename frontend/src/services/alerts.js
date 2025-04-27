import { apiClient } from "../client/api";

export const createAlert = async (alertData) => {
  try {
    const response = await apiClient.post("/alerts", alertData);
    return response.data;
  } catch (error) {
    console.error("Error fetching bus lines:", error);
    throw error;
  }
};
