import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { UserLocationProvider } from "./context/userLocation.jsx";
import { BrowserRouter } from "react-router";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <UserLocationProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </UserLocationProvider>
  </StrictMode>
);
