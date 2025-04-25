import { useState } from "react";
import {
    MapContainer,
    TileLayer,
    useMap,
    Marker,
    Popup,
    useMapEvents,
} from "react-leaflet";
import { useUserLocation } from "../context/userLocation";
import { AddMarker } from "./AddMarker"

export function MapBusStop() {
    const { userLocation, setUserLocation } = useUserLocation();
    console.log(userLocation);

    return (
        <>
            <MapContainer
                className="h-125 w-100"
                center={[userLocation.lat, userLocation.lng]}
                zoom={16}
                scrollWheelZoom={false}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker position={userLocation}>
                    <Popup>You are here!</Popup>
                </Marker>
                <AddMarker />
            </MapContainer>
        </>
    );
}
