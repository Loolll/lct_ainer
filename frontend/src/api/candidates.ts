import axios from "axios"
import { GetCandidatesCalc, GetCandidatesHeatmap } from "../interfaces/candidates"
import { BboxRequestParams } from "../interfaces/common"

export function getCandidatesBbox (data: BboxRequestParams & { abbrev_ao?: string, districts_ids?: number[] }) {
  return axios.post('/api/candidates/filter', data)
}

export function addCalcCandidates (data: GetCandidatesCalc) {
  return axios.post('/api/candidates/calc', {
    ...data.data,
    params: data.params
  })
}

export function exportCandidates (data: BboxRequestParams) {
  return axios.post('/api/candidates/export', data)
}