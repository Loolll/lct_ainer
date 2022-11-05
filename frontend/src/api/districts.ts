import axios from "axios"
import { BboxRequestParams, SearchRequestParams } from "../interfaces/common"

export function getAllDistricts () {
  return axios.get('/api/districts/all')
}

export function getDistrictsBbox (data: BboxRequestParams & { districts_ids: number[]}) {
  return axios.post('/api/districts/bbox', data)
}

export function searchDistricts (params: SearchRequestParams) {
  return axios.get('/api/districts/autocomplete', { params })
}