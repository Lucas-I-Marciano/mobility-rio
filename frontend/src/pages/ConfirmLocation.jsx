import React from "react";
import { MapLocate } from "../components/MapLocate";
import { useLocation } from "../context/location";
import { useNavigate } from "react-router";

export const ConfirmLocation = () => {
  // Pega os estados relevantes do contexto
  const { userLocation, isLoadingLocation, locationError } = useLocation();
  const navigate = useNavigate();

  const handleConfirmAndNavigate = () => {
    if (userLocation) {
      // Passa a localização confirmada para a próxima rota
      navigate("/bus", { state: { userLocation: userLocation } });
    }
  };

  return (
    <>
      <div className="flex flex-col min-h-screen items-center bg-gray-100">
        {/* Header Section */}
        <div className="w-full bg-gradient-to-b from-blue-500 to-blue-900 flex items-center justify-center gap-4 p-2 md:p-3 shadow-md">
          <h1 className="text-2xl md:text-3xl font-bold text-white">
            Confirme sua Localização
          </h1>
        </div>

        {/* Content Section */}
        <div className="flex flex-col gap-5 items-center pt-2 px-10 text-center max-w-2xl bg-white shadow-lg rounded-lg mt-2">
          <p className="text-gray-600">
            Clique uma vez no mapa para tentarmos encontrar sua localização
            atual. Se necessário, clique novamente no local exato que deseja
            usar como referência.
          </p>

          <div className="h-96 rounded-lg overflow-hidden shadow-md">
            <MapLocate />
          </div>

          {/* Área de Feedback e Ação */}
          <div className="min-h-[80px] flex flex-col justify-center items-center">
            {" "}
            {/* Adicionado min-h para evitar pulos */}
            {isLoadingLocation && (
              <p className="text-blue-600 animate-pulse">
                Buscando sua localização...
              </p>
            )}
            {locationError && !isLoadingLocation && (
              <div
                className="p-2 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm"
                role="alert"
                aria-live="polite"
              >
                <p>
                  <strong>Erro:</strong> {locationError}
                </p>
                <p className="text-xs mt-1">
                  Tente clicar no mapa novamente ou verifique as permissões.
                </p>
              </div>
            )}
            {userLocation && !isLoadingLocation && !locationError && (
              <div className="text-center">
                <p className="text-sm text-green-700 mb-1">
                  Localização encontrada! Confirme se está correto.
                </p>
                <button
                  className="focus:outline-none text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 transition duration-150 ease-in-out"
                  onClick={handleConfirmAndNavigate} // Chama a função correta
                >
                  Confirmar Localização e Avançar
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};
