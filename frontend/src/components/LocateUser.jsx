import { Marker, Popup, useMapEvents } from "react-leaflet";
import { useUserLocation } from "../context/userLocation";

export const LocateUser = () => {
    const { userLocation, setUserLocation } = useUserLocation();
    const map = useMapEvents({
        click() {
            map.locate();
        },
        locationfound(e) {
            setUserLocation(e.latlng);
            map.flyTo(e.latlng, 16);
        },
    });

    return userLocation === null ? null : (
        <Marker position={userLocation}>
            <Popup>You are here</Popup>
        </Marker>
    );
}