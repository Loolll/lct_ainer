import { Coords } from "./common"

export interface DistrictItem {
  abbrev_ao: string,
  name_ao: string,
  name: string,
  polygon: Coords[],
  center: Coords,
  reliability: number,
  id: number
}

export type SearchDistrictItem = Pick<DistrictItem, 'id' | 'name'>

export interface DistrictState {
  districts: DistrictItem[],
  districts_ids: number[]
}