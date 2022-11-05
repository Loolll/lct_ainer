import { LatLngExpression } from "leaflet";

export interface MapState {
  center: LatLngExpression,
  zoom: number
}