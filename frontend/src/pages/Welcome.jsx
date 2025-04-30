import React, { useState } from "react";
import { useNavigate } from "react-router";

import logo from "../assets/logo_pref_rio.png";
import { WifiIcon } from "@heroicons/react/24/solid";

export const Welcome = () => {
  const navigate = useNavigate();
  const [location, setLocation] = useState(null); // { latitude: number, longitude: number } | null
  const [error, setError] = useState(null); // string | null
  const [isLoading, setIsLoading] = useState(false); // Loading state

  const requestLocationAccess = async () => {
    if (!navigator.geolocation) {
      setError(
        "Geolocalização não é suportado por esse navegador. Tente em um dispositico diferente"
      );
      return;
    }

    setIsLoading(true);
    setError(null); // Clear previous errors
    setLocation(null); // Clear previous location

    try {
      const position = await new Promise((resolve, reject) => {
        // Added timeout for better UX in case it hangs
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          timeout: 10000, // 10 seconds timeout
        });
      });

      const coords = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      };
      setLocation(coords);
      console.log("Location obtained:", coords);
      // Optionally call a prop function passed from parent
      // if (onLocationObtained) {
      //   onLocationObtained(coords);
      // }
      // Automatically navigate after obtaining location? Or keep button?
      // navigate("/confirm", { state: { location: coords } }); // Option: auto-navigate
    } catch (err) {
      console.error("Geolocation error:", err);
      // Provide more user-friendly error messages
      if (err.code === err.PERMISSION_DENIED) {
        setError(
          "Permissão de localização negada. Por favor, habilite nas configurações do seu navegador."
        );
      } else if (err.code === err.POSITION_UNAVAILABLE) {
        setError("Informação de localização indisponível no momento.");
      } else if (err.code === err.TIMEOUT) {
        setError("Tempo esgotado ao tentar obter localização.");
      } else {
        setError("Erro ao obter localização.");
      }
    } finally {
      setIsLoading(false); // Ensure loading is set to false in both success/error cases
    }
  };

  const handleNavigate = () => {
    // Pass location state if needed by the next route
    navigate("/confirm", { state: { location: location } });
  };

  return (
    // Use min-h-screen and bg-gray-100 for basic page layout? Assumed white background for now.
    <div className="flex flex-col min-h-screen items-center bg-gray-100">
      {/* Header Section */}
      {/* Using w-full and maybe max-w-* on content is often better than w-screen */}
      <div className="w-full bg-gradient-to-b from-blue-500 to-blue-900 flex items-center justify-center gap-4 p-6 md:p-10 shadow-md">
        {/* Adjusted logo size and added alt text */}
        <img
          src={logo}
          className="w-20 md:w-24 h-auto"
          alt="Logo Prefeitura Rio"
        />
        {/* <p className="text-white text-4xl md:text-5xl font-thin mx-2">+</p> */}
        {/* Replaced inline SVG with a placeholder comment, recommend using an icon library or optimized SVG */}
        {/* Placeholder for Wifi/GPS Icon - Use Heroicons, FontAwesome, etc. */}
        <WifiIcon
          className="w-10 h-10 md:w-12 md:h-12 text-white"
          aria-hidden="true"
        />
      </div>

      {/* Content Section */}
      <div className="flex flex-col gap-5 items-center p-6 text-center max-w-2xl bg-white shadow-lg rounded-lg mt-10">
        {" "}
        {/* Added padding and max-width */}
        <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mt-6">
          Facilitador de Mobilidade do Rio de Janeiro
        </h1>
        <p className="text-gray-600">
          Bem-vindo! Para te ajudar a encontrar os ônibus próximos e calcular
          tempos de chegada, precisamos da sua localização.
        </p>
        {/* Action Button Area */}
        <div className="mt-4">
          {!location && ( // Show grant button only if location is not yet set
            <button
              onClick={requestLocationAccess}
              disabled={isLoading} // Disable while loading
              className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-base px-6 py-3 me-2 mb-2 transition duration-150 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
            // Removed dark mode classes for brevity, add back if needed
            >
              {isLoading
                ? "Obtendo Localização..."
                : "Permitir Acesso à Localização"}
            </button>
          )}

          {location && ( // Show navigate button only after success
            <button
              onClick={handleNavigate}
              className="focus:outline-none text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-base px-6 py-3 me-2 mb-2 transition duration-150 ease-in-out"
            // Removed dark mode classes for brevity
            >
              Ver Ônibus Próximos
            </button>
          )}
        </div>
        {/* Error Message Area */}
        {error && (
          <div
            className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm"
            role="alert"
            aria-live="polite"
          >
            <p>
              <strong>Erro:</strong> {error}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};