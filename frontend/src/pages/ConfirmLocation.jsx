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
      <div className="flex flex-col items-center gap-3 p-4">
        {/* Texto atualizado */}
        <h1 className="text-xl font-semibold text-gray-700">
          Confirme sua Localização
        </h1>
        <p className="text-gray-600 text-center px-2">
          Clique no mapa para que possamos encontrar e exibir sua localização
          atual.
        </p>

        {/* Mapa (ajuste as classes em MapLocate.jsx) */}
        <MapLocate />

        {/* Área de Feedback e Ação */}
        <div className="mt-4 min-h-[80px] flex flex-col justify-center items-center">
          {" "}
          {/* Adicionado min-h para evitar pulos */}
          {isLoadingLocation && (
            <p className="text-blue-600 animate-pulse">
              Buscando sua localização...
            </p>
          )}
          {locationError && !isLoadingLocation && (
            <div
              className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-sm"
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
              <p className="text-sm text-green-700 mb-3">
                Localização encontrada! Confirme se está correto.
              </p>
              <button
                className="focus:outline-none text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 transition duration-150 ease-in-out"
                onClick={handleConfirmAndNavigate} // Chama a função correta
              >
                Confirmar Localização e Avançar
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};
