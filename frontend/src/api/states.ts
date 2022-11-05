import axios from "axios"
import { BboxRequestParams, SearchRequestParams } from "../interfaces/common"

export function getAllStates () {
  return axios.get('/api/states/all')
}

export function getStatesBbox (data: BboxRequestParams & { abbrev_ao?: string }) {
  return axios.post('/api/states/bbox', data)
}

export function searchStates (params: SearchRequestParams) {
  return axios.get('/api/states/autocomplete', { params })
}