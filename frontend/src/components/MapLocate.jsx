import { useState } from "react";
import {
  MapContainer,
  TileLayer,
  useMap,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import { LocateUser } from "./LocateUser";

export function MapLocate() {
  return (
    <>
      <MapContainer
        className="h-125 w-100"
        center={[-22.937822, -43.253794]}
        zoom={11}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <LocateUser />
      </MapContainer>
    </>
  );
}
