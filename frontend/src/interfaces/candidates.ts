import { BboxRequestParams, Coords } from "./common";

export interface CandidateItem {
  id: number,
  abbrev_ao: string,
  district_id: number,
  point: Coords,
  address?: string,
  type: CandidateItemType,
  calculated_radius: number,
  modifier_v1: number,
  modifier_v2: number,
  color_v1: string,
  color_v2: string
}

export type CandidateItemType = 'house' | 'bus_station' | 'culture_house' | 'library' | 'metro' | 'mfc' | 'nto_non_paper' | 'nto_paper' | 'parking' | 'postamat' | 'sports' | 'any'

export interface CandidatesState {
  candidates: CandidateItem[]
}

export interface GetCandidatesCalc {
  data: Coords,
  params: {
    query: string
  }
}

export interface GetCandidatesHeatmap {
  data: BboxRequestParams,
  params: {
    modifier_type: CandidatesModifierType
  }
}

export enum CandidatesModifierType {
  v1 = 'modifier_v1',
  v2 = 'modifier_v2'
}