import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { addCalcCandidates, exportCandidates, getCandidatesBbox } from '../../api/candidates'
import { CandidateItem, CandidatesState, GetCandidatesCalc, GetCandidatesParams } from '../../interfaces/candidates'
import { BboxRequestParams, RootState } from '../../interfaces/common'
import { DrawingElementsPropsRefGetBboxStatesParams } from '../../interfaces/drawingElements'

const initialState: CandidatesState = {
  candidates: []
}

export const candidatesThunk = {
  getBbox: createAsyncThunk<CandidateItem[], BboxRequestParams & DrawingElementsPropsRefGetBboxStatesParams, { state: RootState }>(
    'candidates/getBbox',
    async (data, { getState, rejectWithValue }) => {
      const state = getState()
      const params: GetCandidatesParams = {
        ...data,
        districts_ids: data.hasOwnProperty('districts_ids') ? data.districts_ids : state.districts.districts_ids,
        abbrev_ao: data.hasOwnProperty('abbrevFilter') ? data.abbrevFilter : state.states.abbrevFilter,
      }
      if ((data.modifier || state.filters.currentModifier) === 'modifier_v1') {
        params.min_modifier_v1 = data.hasOwnProperty('rate') ? data.rate?.min : state.filters.rate.min
        params.max_modifier_v1 = data.hasOwnProperty('rate') ? data.rate?.max : state.filters.rate.max
      } else if ((data.modifier || state.filters.currentModifier) === 'modifier_v2') {
        params.min_modifier_v2 = data.hasOwnProperty('rate') ? data.rate?.min : state.filters.rate.min
        params.max_modifier_v2 = data.hasOwnProperty('rate') ? data.rate?.max : state.filters.rate.max
      }
      return await getCandidatesBbox(params)
      .then((response) => response.data)
      .catch((err) => rejectWithValue(err))
    }
  ),
  export: createAsyncThunk<{ link: string }, BboxRequestParams & DrawingElementsPropsRefGetBboxStatesParams>(
    'candidates/export',
    async (data, { rejectWithValue }) => {
      return await exportCandidates(data)
      .then((response) => {
        window.open(response.data.link, '_blank')
        return response.data
      })
      .catch((err) => rejectWithValue(err))
    }
  ),
  addNew: createAsyncThunk<CandidateItem, GetCandidatesCalc>(
    'candidates/addNew',
    async (data, { rejectWithValue }) => {
      return await addCalcCandidates(data)
      .then((response) => response.data)
      .catch((err) => rejectWithValue(err))
    }
  )
}

export const candidatesSlice = createSlice({
  name: 'candidates',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(candidatesThunk.getBbox.fulfilled, (state, action) => {
      state.candidates = action.payload
    })
  }
})


// export const {  } = candidatesSlice.actions

export default candidatesSlice.reducer