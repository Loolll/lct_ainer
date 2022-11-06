import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit'
import { getAllStates, getStatesBbox, searchStates } from '../../api/states'
import { BboxRequestParams, RootState, SearchRequestParams } from '../../interfaces/common'
import { DrawingElementsPropsRefGetBboxStatesParams } from '../../interfaces/drawingElements'
import { StateItem, StatesState } from '../../interfaces/states'

const initialState: StatesState = {
  states: [],
  abbrevFilter: ''
}

export const statesThunk = {
  getAll: createAsyncThunk<StateItem[]>(
    'states/getAll',
    async (_, { rejectWithValue }) => {
      return await getAllStates()
      .then((response) => response.data)
      .catch((err) => rejectWithValue(err))
    }
  ),
  getBbox: createAsyncThunk<StateItem[], BboxRequestParams & DrawingElementsPropsRefGetBboxStatesParams, { state: RootState }>(
    'states/getBbox',
    async (data, { getState, rejectWithValue }) => {
      const state = getState()
      return await getStatesBbox({
        ...data,
        abbrev_ao: data.hasOwnProperty('abbrevFilter') ? data.abbrevFilter : state.states.abbrevFilter
      })
      .then((response) => response.data)
      .catch((err) => rejectWithValue(err))
    }
  ),
  search: createAsyncThunk<StateItem[], SearchRequestParams>(
    'states/search',
    async (data, { rejectWithValue }) => {
      return await searchStates(data)
      .then((response) => response.data)
      .catch((err) => rejectWithValue(err))
    }
  )
}

export const statesSlice = createSlice({
  name: 'states',
  initialState,
  reducers: {
    setAbbrevFilter (state, action: PayloadAction<string>) {
      state.abbrevFilter = action.payload
    },
    setStates (state, action) {
      state.states = action.payload
    }
  },
  extraReducers: (builder) => {
    builder.addCase(statesThunk.getAll.fulfilled, (state, action) => {
      state.states = action.payload
    })
    builder.addCase(statesThunk.getBbox.fulfilled, (state, action) => {
      state.states = action.payload
    })
  }
})


export const { setAbbrevFilter, setStates } = statesSlice.actions

export default statesSlice.reducer