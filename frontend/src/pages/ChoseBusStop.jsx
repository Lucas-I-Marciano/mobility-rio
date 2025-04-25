import { MapBusStop } from "../components/MapBusStop";
import { useLocation } from "../context/location";
import { LocateUser } from "../components/LocateUser"

export const ChoseBusStop = () => {
    const { userLocation, busStopLocation } = useLocation();
    return (
        <>
            <div className="flex flex-col items-center gap-1">
                <p>Clique no ponto de ônibus mais próximo de você e confirme para enviarmos te avisarmos quando o próximo ônibus passará</p>
                <p>Cada quadrado azul é um ponto de ônibus, aumente o zoom para uma precisão melhor</p>
                <MapBusStop />
                {userLocation == null ? null : (
                    <button
                        onClick={() => {
                            console.log(busStopLocation);
                        }}
                        className="focus:outline-none text-white bg-green-700 hover:bg-green-800 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800">Confirmar</button>
                )}
            </div>
        </>
    );
};
