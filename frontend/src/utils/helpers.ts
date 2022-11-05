import { LatLngLiteral } from "leaflet";
import { Coords, PaletteItem } from "../interfaces/common";

export function convertLngToLon (bounds: LatLngLiteral) {
  return {
    lat: bounds.lat,
    lon: bounds.lng
  }
}

export function convertLonToLng (bounds: Coords) {
  return {
    lat: bounds.lat,
    lng: bounds.lon
  }
}

export function getRandomElemFromArray (arr: (PaletteItem)[]) {
  return arr[Math.floor(Math.random()*arr.length)]
}