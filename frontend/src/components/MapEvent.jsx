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

function LocateUser() {
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

export function MapEvent() {
  return (
    <>
      <MapContainer
        className="h-125 w-100"
        center={[-22.937822, -43.253794]}
        zoom={11}
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[51.505, -0.09]}>
          <Popup>
            A pretty CSS3 popup. <br /> Easily customizable.
          </Popup>
        </Marker>
        <LocateUser />
      </MapContainer>
    </>
  );
}
