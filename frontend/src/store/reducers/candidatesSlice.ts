import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit'
import { getCandidatesBbox } from '../../api/candidates'
import { CandidateItem, CandidatesState } from '../../interfaces/candidates'
import { BboxRequestParams, RootState } from '../../interfaces/common'

const initialState: CandidatesState = {
  candidates: []
}

export const candidatesThunk = {
  getBbox: createAsyncThunk<CandidateItem[], BboxRequestParams, { state: RootState }>(
    'candidates/getBbox',
    async (data, { getState, rejectWithValue }) => {
      const state = getState()
      return await getCandidatesBbox({
        ...data,
        districts_ids: state.districts.districts_ids,
        abbrev_ao: state.states.abbrevFilter
      })
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