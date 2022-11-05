import { Coords } from "./common"

export interface StateItem {
  abbrev: string,
  name: string,
  polygons: Coords[][],
  reliability: number
}

export interface StatesState {
  states: StateItem[],
  abbrevFilter: string
}