import { useState } from 'react';
import { useLocation } from "../context/location";

export const BusTable = ({ data }) => {
    const { userLocation } = useLocation();
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState({});

    const handleButtonClick = async (item) => {
        setLoading(true);
        try {
            const response = await fetch('/get/eta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
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
        <div className="">
            <h3 className="text-md font-semibold text-gray-700 mb-1">
                Bus Table
            </h3>
            <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200 text-sm">
                    <thead>
                        <tr>
                            <th className="pl-1 pr-2 py-2 border-b">Ordem</th>
                            <th className="pl-1 pr-2 py-2 border-b">Vel.</th>
                            <th className="pl-1 pr-2 py-2 border-b">Linha</th>
                            <th className="pl-1 pr-2 py-2 border-b">Aprox.*</th>
                            <th className="pl-1 pr-2 py-2 border-b">Distancia**</th>
                            <th className="pl-1 pr-2 py-2 border-b">Tempo</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((item, index) => (
                            <tr key={index}>
                                <td className="pl-1 pr-2 py-2 border-b text-xs">{item.ordem}</td>
                                <td className="pl-1 pr-2 py-2 border-b text-xs">{item.velocidade}</td>
                                <td className="pl-1 pr-2 py-2 border-b text-xs">{item.linha}</td>
                                <td className="pl-1 pr-2 py-2 border-b text-xs">{item.approaching ? "Sim" : "Não"}</td>
                                <td className="pl-1 pr-2 py-2 border-b text-xs">{item.distancia} Km</td>
                                <td className="pl-1 pr-2 py-2 border-b text-xs">
                                    {results[item.ordem] ? (
                                        <span>{results[item.ordem]}</span>
                                    ) : (
                                        <button
                                            className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded ${loading ? 'bg-gray-500 cursor-not-allowed' : ''}`}
                                            onClick={() => handleButtonClick(item)}
                                            disabled={loading}
                                        >
                                            Buscar
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <p className="text-xs text-gray-700 mt-1">*Ônibus se aproximando do ponto ou indo em outra direção</p>
                <p className="text-xs text-gray-700">** Distância em linha reta</p>
            </div>
        </div>
    );
};
