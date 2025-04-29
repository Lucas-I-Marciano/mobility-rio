import { useState } from "react";
import { useLocation } from "../context/location";
import { fetchSingleBusEta } from "../services/bus";

export const BusTable = ({
  data,
  isLoading,
  error,
  selectedLine,
  destinationCoords,
}) => {
  const { userLocation } = useLocation();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({});

  // --- ESTADOS PARA ETAs INDIVIDUAIS ---
  // Guarda os ETAs buscados sob demanda { "ordemId": 123, ... }
  const [individualEtas, setIndividualEtas] = useState({});
  // Guarda quais ônibus estão carregando ETA individualmente (um Set é eficiente)
  const [loadingEtas, setLoadingEtas] = useState(new Set());
  // Guarda erros de busca individual { "ordemId": "Erro...", ... }
  const [individualEtaErrors, setIndividualEtaErrors] = useState({});

  // Formatar ETA (segundos para minutos)
  const formatEta = (seconds) => {
    if (seconds === null || seconds === undefined || seconds < 0) {
      return "N/A"; // Ou Indisponível, etc.
    }
    const minutes = Math.round(seconds / 60);
    return `${minutes} min`;
  };

  // Formatar Timestamp (exemplo simples)
  const formatTimestamp = (isoString) => {
    try {
      return new Date(isoString).toLocaleTimeString("pt-BR", {
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "Inválido";
    }
  };

  // --- FUNÇÃO PARA BUSCAR ETA INDIVIDUAL ---
  const handleVerifyEtaClick = async (ordemId) => {
    // Verifica se já está carregando para evitar cliques múltiplos
    if (loadingEtas.has(ordemId) || !destinationCoords) return;

    // Adiciona ao set de loading
    setLoadingEtas((prev) => new Set(prev).add(ordemId));
    // Limpa erro anterior para este onibus
    setIndividualEtaErrors((prev) => {
      const next = { ...prev };
      delete next[ordemId];
      return next;
    });

    try {
      const eta = await fetchSingleBusEta(
        selectedLine,
        destinationCoords.lat,
        destinationCoords.lng,
        ordemId
      );
      // Atualiza o estado com o resultado (pode ser null se API falhar)
      setIndividualEtas((prev) => ({ ...prev, [ordemId]: eta }));
    } catch (err) {
      console.error(`Falha ao buscar ETA individual para ${ordemId}`, err);
      // Guarda uma mensagem de erro para este onibus
      setIndividualEtaErrors((prev) => ({ ...prev, [ordemId]: "Erro!" }));
      // Garante que o ETA não fique preso em 'null' se busca falhou
      setIndividualEtas((prev) => ({ ...prev, [ordemId]: null }));
    } finally {
      // Remove do set de loading
      setLoadingEtas((prev) => {
        const next = new Set(prev);
        next.delete(ordemId);
        return next;
      });
    }
  };
  // --- FIM FUNÇÃO ETA INDIVIDUAL ---

  // Renderização condicional
  if (isLoading) {
    return (
      <div className="p-4 text-center text-gray-500">
        Carregando ônibus para a linha {selectedLine}...
      </div>
    );
  }

  if (error) {
    return <div className="p-4 text-center text-red-600">Erro: {error}</div>;
  }

  if (!data || data.length === 0) {
    // Só mostra "nenhum encontrado" se uma linha foi selecionada mas não retornou nada
    return selectedLine ? (
      <div className="p-4 text-center text-gray-500">
        Nenhum ônibus encontrado para a linha {selectedLine}.
      </div>
    ) : null;
  }

  const handleButtonClick = async (item) => {
    setLoading(true);
    try {
      const response = await fetch("/get/eta", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origem: { latitude: item.latitude, longitude: item.longitude },
          destino: userLocation,
        }),
      });
      const result = await response.json();
      setResults((prevResults) => ({
        ...prevResults,
        [item.ordem]: result,
      }));
    } catch (error) {
      alert(`Erro ao buscar Tempo de Chegada`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-2">
      <h3 className="text-md font-semibold text-gray-700 mb-2">
        Ônibus da Linha {selectedLine}
      </h3>
      <div className="overflow-x-auto max-h-96">
        {/* Adicionado max-h para scroll */}
        <table className="min-w-full bg-white border border-gray-200 text-xs">
          {/* Reduzido text-xs */}
          <thead className="sticky top-0 bg-gray-100">
            {/* Cabeçalho fixo */}
            <tr>
              {/* Colunas baseadas no modelo BusStatus */}
              <th className="px-2 py-2 border-b text-left">Ordem</th>
              <th className="px-2 py-2 border-b text-left">Vel.</th>
              <th className="px-2 py-2 border-b text-left">Aprox.?</th>
              <th className="px-2 py-2 border-b text-left">Dist.(km)</th>
              <th className="px-2 py-2 border-b text-left">ETA Aprox.</th>
            </tr>
          </thead>
          <tbody>
            {data.map((bus) => {
              const isLoadingIndividual = loadingEtas.has(bus.ordem);
              const individualEtaResult = individualEtas[bus.ordem];
              const individualError = individualEtaErrors[bus.ordem];
              const etaToShow =
                individualEtaResult !== undefined
                  ? individualEtaResult
                  : bus.eta_seconds;

              return (
                <tr key={bus.ordem} className="hover:bg-gray-50">
                  <td className="px-2 py-2 border-b font-mono">{bus.ordem}</td>
                  <td className="px-2 py-2 border-b">
                    {bus.velocidade?.toFixed(0)}
                  </td>
                  {/* <td className="px-2 py-2 border-b">{bus.linha}</td> */}
                  {/* --- Nova Coluna Approaching --- */}
                  <td
                    className={`px-2 py-2 border-b font-medium ${
                      bus.approaching ? "text-green-600" : "text-orange-600"
                    }`}
                  >
                    {bus.approaching ? "Sim" : "Não"}
                  </td>
                  {/* --- Nova Coluna Distance --- */}
                  <td className="px-2 py-2 border-b">
                    {bus.distance_km?.toFixed(1)}
                  </td>
                  <td className="px-2 py-2 border-b">
                    {/* --- Lógica Condicional do ETA --- */}
                    {isLoadingIndividual ? (
                      <span className="text-gray-400 text-xs italic">
                        Buscando...
                      </span>
                    ) : individualError ? (
                      <span className="text-red-500 text-xs font-semibold">
                        {individualError}
                      </span>
                    ) : etaToShow !== null && etaToShow !== undefined ? (
                      <span className="font-semibold">
                        {formatEta(etaToShow)}
                      </span>
                    ) : !bus.approaching ? ( // Só mostra botão se não estiver aproximando E não tiver ETA
                      <button
                        className="bg-blue-500 hover:bg-blue-700 text-white text-[10px] font-bold py-0.5 px-1 rounded disabled:opacity-50"
                        onClick={() => handleVerifyEtaClick(bus.ordem)}
                        disabled={isLoadingIndividual || !destinationCoords} // Desabilita se coords do destino não chegaram
                        title="Verificar tempo estimado agora"
                      >
                        Verificar
                      </button>
                    ) : (
                      <span className="text-gray-500">N/A</span> // Caso: approaching=true mas eta=null (falha backend?)
                    )}
                    {/* --- Fim Lógica ETA --- */}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-gray-500 mt-1">
        *Status de aproximação em relação ao ponto selecionado.
      </p>
      <p className="text-xs text-gray-500">** Distância em linha reta (km).</p>
      <p className="text-xs text-gray-500 mt-1">
        ETA (Tempo Estimado de Chegada) é aproximado. <br />
        Calculado assumindo a posição do ônibus em direção a sua posição
      </p>
    </div>
  );
};
