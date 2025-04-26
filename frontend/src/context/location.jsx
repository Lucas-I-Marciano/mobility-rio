import { createContext, useContext, useState } from "react";

export const LocationContext = createContext();

export const useLocation = () => {
  return useContext(LocationContext);
};

export const LocationProvider = ({ children }) => {
  const [userLocation, setUserLocation] = useState(null);
  const [busStopLocation, setBusStopLocation] = useState(null);

  return (
    <LocationContext.Provider value={{ userLocation, setUserLocation, busStopLocation, setBusStopLocation }}>
      {children}
    </LocationContext.Provider>
  );
};
