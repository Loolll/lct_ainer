import axios from "axios"
import { GetCandidatesCalc, GetCandidatesHeatmap, GetCandidatesParams } from "../interfaces/candidates"
import { BboxRequestParams } from "../interfaces/common"
import { DrawingElementsPropsRefGetBboxStatesParams } from "../interfaces/drawingElements"

export function getCandidatesBbox (data: GetCandidatesParams) {
  return axios.post('/api/candidates/filter', data)
}

export function addCalcCandidates (data: GetCandidatesCalc) {
  return axios.post('/api/candidates/calc', data.data, {
    params: data.params
  })
}

export function exportCandidates (data: BboxRequestParams & DrawingElementsPropsRefGetBboxStatesParams) {
  return axios.post('/api/candidates/export', data)
}