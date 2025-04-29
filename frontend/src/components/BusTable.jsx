import { useState } from "react";
import { useLocation } from "../context/location";

export const BusTable = ({ data, isLoading, error, selectedLine }) => {
  const { userLocation } = useLocation();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({});

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
      return new Date(isoString).toLocaleTimeString("pt-BR");
    } catch {
      return "Inválido";
    }
  };

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
              <th className="px-2 py-2 border-b text-left">Vel. (km/h)</th>
              {/* Linha já está no título, talvez remover? <th className="px-2 py-2 border-b text-left">Linha</th> */}
              <th className="px-2 py-2 border-b text-left">Últ. Atualização</th>
              <th className="px-2 py-2 border-b text-left">ETA Aprox.</th>
            </tr>
          </thead>
          <tbody>
            {data.map((bus) => (
              <tr key={bus.ordem} className="hover:bg-gray-50">
                {/* Adicionado hover */}
                <td className="px-2 py-2 border-b">{bus.ordem}</td>
                <td className="px-2 py-2 border-b">
                  {bus.velocidade?.toFixed(0)}
                </td>
                {/* <td className="px-2 py-2 border-b">{bus.linha}</td> */}
                <td className="px-2 py-2 border-b">
                  {formatTimestamp(bus.datahora_ultima)}
                </td>
                <td className="px-2 py-2 border-b font-medium">
                  {/* Destaca ETA */}
                  {formatEta(bus.eta_seconds)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-gray-500 mt-1">
        ETA (Tempo Estimado de Chegada) é aproximado.
      </p>
    </div>
  );
};
