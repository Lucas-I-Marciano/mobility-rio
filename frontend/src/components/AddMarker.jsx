import { Marker, Popup, useMapEvents } from "react-leaflet";
import { useState } from "react";

export const AddMarker = () => {
    const [markerPosition, setMarkerPosition] = useState(null)
    useMapEvents({
        click(e) {
            setMarkerPosition(e.latlng);

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