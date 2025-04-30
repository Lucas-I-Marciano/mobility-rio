import { createContext, useContext, useState } from "react";

export const LocationContext = createContext();

export const useLocation = () => {
  return useContext(LocationContext);
};

export const LocationProvider = ({ children }) => {
  const [userLocation, setUserLocation] = useState(null);
  const [busStopLocation, setBusStopLocation] = useState(null);
  const [isLoadingLocation, setIsLoadingLocation] = useState(false); // Estado de Loading
  const [locationError, setLocationError] = useState(null); // Estado de Erro
  const [isStopSelectionLocked, setIsStopSelectionLocked] = useState(false); // Inicia como não bloqueado

  return (
    <LocationContext.Provider
      value={{
        userLocation,
        setUserLocation,
        busStopLocation,
        setBusStopLocation,
        isLoadingLocation,
        setIsLoadingLocation, // Compartilha loading/error
        locationError,
        setLocationError,
        isStopSelectionLocked,
        setIsStopSelectionLocked,
      }}
    >
      {children}
    </LocationContext.Provider>
  );
};
