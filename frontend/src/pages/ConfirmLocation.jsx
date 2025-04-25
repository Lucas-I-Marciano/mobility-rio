import { MapEvent } from "../components/MapEvent";
import { useUserLocation } from "../context/userLocation";

export const ConfirmLocation = () => {
  const { userLocation } = useUserLocation();

  return (
    <>
      <p>Click on map for the first time to locate you!</p>
      <MapEvent />
      {userLocation == null ? null : (
        <button className="p-5 bg-gray-200">Confirm location</button>
      )}
    </>
  );
};
