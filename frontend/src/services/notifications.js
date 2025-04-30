import { apiClient } from "../client/api";

export const sendConfirmationEmail = async (bodyForEmail) => {
  try {
    const response = await apiClient.post(
      "/notifications/send-confirmation",
      bodyForEmail
    );
    return response.data;
  } catch (error) {
    console.error("Error sending e-mail:", error);
    throw error;
  }
};
