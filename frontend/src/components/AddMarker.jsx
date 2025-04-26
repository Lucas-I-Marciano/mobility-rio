import { Marker, Popup, useMapEvents } from "react-leaflet";
import { useState } from "react";
import { useLocation } from "../context/location";

export const AddMarker = () => {
    const { setBusStopLocation } = useLocation()
    const [markerPosition, setMarkerPosition] = useState(null)
    useMapEvents({
        click(e) {
            setMarkerPosition(e.latlng);
            setBusStopLocation({ lat: e.latlng.lat, lng: e.latlng.lng })
        },
    });

    return (
        markerPosition === null ?
            null :
            < Marker position={markerPosition} >
                <Popup>Bus Stop</Popup>
            </Marker >
    )
}