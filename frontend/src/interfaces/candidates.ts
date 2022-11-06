import { BboxRequestParams, Coords } from "./common";

export interface CandidateItem {
  id?: number,
  abbrev_ao?: string,
  district_id?: number,
  point: Coords,
  address?: string,
  type?: CandidateItemType,
  calculated_radius?: number,
  aggregation_radius?: number,
  modifier_v1: number,
  modifier_v2: number,
  color_v1: string,
  color_v2: string,
  count?: number
}

export enum CandidateItemType {
  HOUSE = 'house',
  BUS_STATION = 'bus_station',
  CULTURE_HOUSE = 'culture_house',
  LIBRARY = 'library',
  METRO = 'metro',
  MFC = 'mfc',
  NTO_NON_PAPER = 'nto_non_paper',
  NTO_PAPER = 'nto_paper',
  PARKING = 'parking',
  POSTAMAT = 'postamat',
  SPORTS = 'sports',
  ANY = 'any'
}

export interface CandidatesState {
  candidates: CandidateItem[]
}

export interface GetCandidatesCalc {
  data: Coords,
  params: {
    radius: string | number
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

export type GetCandidatesParams = BboxRequestParams & {
  abbrev_ao?: string,
  districts_ids?: number[]
  min_modifier_v1?: number,
  max_modifier_v1?: number,
  min_modifier_v2?: number,
  max_modifier_v2?: number
}

export interface TypesCandidates {
  id: string,
  name: string
}