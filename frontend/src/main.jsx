import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { UserLocationProvider } from "./context/userLocation.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <UserLocationProvider>
      <App />
    </UserLocationProvider>
  </StrictMode>
);
