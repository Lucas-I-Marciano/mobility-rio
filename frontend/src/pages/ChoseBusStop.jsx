import React, { useEffect, useState } from "react"; // Removido useLocation de context se não usado direto aqui
import { MapBusStop } from "../components/MapBusStop";
import { useLocation as useReactRouterLocation } from "react-router";
import { AlertForm } from "../components/AlertForm"; // Importa o novo formulário
import { useLocation } from "../context/location"; // Para pegar busStopLocation
import { BusTable } from "../components/BusTable";
import { fetchBusStatusForLine } from "../services/bus";

export const ChoseBusStop = () => {
  const routerLocation = useReactRouterLocation();
  // Pega a localização confirmada passada pela rota anterior
  const confirmedUserLocation = routerLocation.state?.userLocation;
  // Pega o ponto de ônibus selecionado no mapa desta página
  const { busStopLocation } = useLocation();
  const [showForm, setShowForm] = useState(false);
  const [line, setLine] = useState(null);
  const [selectedLine, setSelectedLine] = useState(null); // Guarda a linha selecionada no form

  const [busStatusData, setBusStatusData] = useState([]); // Guarda os dados da API
  const [isStatusLoading, setIsStatusLoading] = useState(false);
  const [statusError, setStatusError] = useState(null);

  // Se não houver localização confirmada da página anterior, talvez redirecionar ou mostrar erro
  if (!confirmedUserLocation) {
    // TODO: Lidar com caso de usuário chegar aqui sem localização confirmada
    // Ex: return <Navigate to="/" />; ou mostrar mensagem
    return (
      <div>Erro: Localização do usuário não definida. Volte ao início.</div>
    );
  }

  const handleConfirmStop = () => {
    if (busStopLocation) {
      setShowForm(true); // Mostra o formulário ao confirmar o ponto
    }
  };

  useEffect(() => {
    console.log(
      "useEffect [selectedLine, busStopLocation] - Triggered. Current values:",
      { line: selectedLine, stop: busStopLocation }
    );
    // Só busca se tivermos uma linha selecionada E um ponto de destino selecionado
    if (selectedLine && busStopLocation) {
      console.log("useEffect - Condition PASSED (line and stop selected).");
      const getStatus = async () => {
        console.log("useEffect -> getStatus: Attempting to fetch status...");
        setIsStatusLoading(true);
        setStatusError(null);
        setBusStatusData([]); // Limpa dados anteriores
        try {
          console.log(
            "useEffect -> getStatus: Calling fetchBusStatusForLine with:",
            {
              line: selectedLine,
              lat: busStopLocation.lat,
              lng: busStopLocation.lng,
            }
          );
          const data = await fetchBusStatusForLine(
            selectedLine,
            busStopLocation.lat,
            busStopLocation.lng
          );
          console.log(
            "useEffect -> getStatus: API call successful, received data:",
            data
          ); // Log 5: Ver se a API retornou
          setBusStatusData(Array.isArray(data) ? data : []);
        } catch (error) {
          console.error("useEffect -> getStatus: API call FAILED.", error); // Log 6: Ver o erro
          setStatusError("Falha ao buscar status dos ônibus.");
          setBusStatusData([]);
        } finally {
          setIsStatusLoading(false);
        }
      };
      getStatus();
    } else {
      console.log(
        "useEffect - Condition FAILED (line or stop missing). Clearing data."
      );
      // Se linha ou ponto não estiverem selecionados, limpa os dados da tabela/mapa
      setBusStatusData([]);
      setStatusError(null);
    }
  }, [selectedLine, busStopLocation]);

  return (
    <>
      <div className="flex flex-col min-h-screen items-center bg-gray-100">
        {/* Header Section */}
        <div className="w-full bg-gradient-to-r from-blue-800 to-blue-900 flex items-center justify-center gap-4 p-1 md:p-2 shadow-md">
          <h1 className="text-2xl md:text-3xl font-bold text-white">
            Selecione o Ponto de Ônibus
          </h1>
        </div>

        {/* Content Section */}
        <div className="flex flex-col gap-5 items-center py-1 text-center px-4 bg-white shadow-lg rounded-lg mt-1">
          <p className="text-gray-600">
            O mapa está centralizado na sua localização confirmada. Clique no
            local exato do ponto de ônibus que você utiliza.
          </p>
        </div>

        {/* Layout principal: Mapa à esquerda/em cima, Formulário à direita/embaixo */}
        <div className="flex flex-col lg:flex-row gap-5 p-3 items-start justify-center ">
          <div
            className={`flex-shrink-0 w-full ${
              showForm ? "lg:w-1/2" : "lg:w-5/2"
            } transition-all duration-300 ease-in-out `}
          >
            {" "}
            {/* Ajusta largura */}
            {/* Passa a localização confirmada para centralizar o mapa */}
            <MapBusStop
              initialCenter={confirmedUserLocation}
              busData={busStatusData} // Passa os ônibus para plotar
            />
            <div className="mt-2 text-center">
              {busStopLocation &&
                !showForm && ( // Mostra botão só se ponto selecionado E form não visível
                  <button
                    onClick={handleConfirmStop}
                    className="focus:outline-none text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 transition duration-150 ease-in-out"
                  >
                    Confirmar Ponto e Preencher Dados
                  </button>
                )}
              {busStopLocation && ( // Mostra coordenadas selecionadas
                <p className="text-xs text-gray-500 mt-1">
                  Ponto selecionado: Lat {busStopLocation.lat.toFixed(5)}, Lng{" "}
                  {busStopLocation.lng.toFixed(5)}
                </p>
              )}
              {!busStopLocation && (
                <p className="text-sm text-gray-500 italic mt-1">
                  Clique no mapa para selecionar o ponto...
                </p>
              )}
            </div>
          </div>

          {/* Coluna do Formulário (condicional) */}
          {showForm && busStopLocation && (
            <div className="w-full lg:w-1/2 xl:w-1/3 space-y-5">
              {" "}
              {/* Adiciona space-y */}
              {/* Formulário */}
              <div className="p-4 border rounded-lg shadow-md bg-white">
                <h2 className="text-lg font-semibold text-gray-700 mb-4">
                  Detalhes do Alerta
                </h2>
                {/* Passa o ponto e a função para setar a linha */}
                <AlertForm
                  selectedBusStop={busStopLocation}
                  setSelectedLineCallback={setSelectedLine} // Passa a função p/ AlertForm atualizar o estado aqui
                />
              </div>
              {/* Tabela de Ônibus (renderiza se linha selecionada ou carregando) */}
            </div>
          )}
          {(selectedLine || isStatusLoading || statusError) && (
            <div className="p-1 border rounded-lg shadow-md bg-white">
              <BusTable
                data={busStatusData}
                isLoading={isStatusLoading}
                error={statusError}
                selectedLine={selectedLine} // Passa a linha selecionada
              />
            </div>
          )}
        </div>
        {/* Tabela de Dados Mocados */}
      </div>
    </>
  );
};
