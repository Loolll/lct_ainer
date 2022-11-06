import { LatLngExpression } from "leaflet";
import { Coords } from "./common";

export interface MapState {
  center: LatLngExpression,
  zoom: number,
  bounds: MapBounds
}

export interface MapBounds {
  lb_point: Coords | null,
  lu_point: Coords | null,
  rb_point: Coords | null,
  ru_point: Coords | null
}