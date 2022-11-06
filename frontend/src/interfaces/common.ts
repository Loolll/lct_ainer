import store from "../store/store"

export interface BboxRequestParams {
  lu_point: Coords,
  ru_point: Coords,
  rb_point: Coords,
  lb_point: Coords
}

export interface SearchRequestParams {
  query: string | null
}

export interface Coords {
  lat: number,
  lon: number
}

export type RootState = ReturnType<typeof store.getState>

export type AppDispatch = typeof store.dispatch;

export interface PaletteItem {
  color: string
}