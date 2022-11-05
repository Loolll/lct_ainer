import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit'
import { getAllDistricts, getDistrictsBbox, searchDistricts } from '../../api/districts'
import { BboxRequestParams, RootState, SearchRequestParams } from '../../interfaces/common'
import { DistrictItem, DistrictState } from '../../interfaces/districts'

const initialState: DistrictState = {
  districts: [],
  districts_ids: []
}

export const districtsThunk = {
  getAll: createAsyncThunk<DistrictItem[]>(
    'districts/getAll',
    async (_, { rejectWithValue }) => {
      return await getAllDistricts()
      .then((response) => response.data)
      .catch((err) => rejectWithValue(err))
    }
  ),
  getBbox: createAsyncThunk<DistrictItem[], BboxRequestParams, { state: RootState }>(
    'districts/getBbox',
    async (data, { getState, rejectWithValue }) => {
      const state = getState()
      return await getDistrictsBbox({
        ...data,
        districts_ids: state.districts.districts_ids
      })
      .then((response) => response.data)
      .catch((err) => rejectWithValue(err))
    }
  ),
  search: createAsyncThunk<DistrictItem[], SearchRequestParams>(
    'districts/search',
    async (data, { rejectWithValue }) => {
      return await searchDistricts(data)
      .then((response) => response.data)
      .catch((err) => rejectWithValue(err))
    }
  )
}

export const districtsSlice = createSlice({
  name: 'districts',
  initialState,
  reducers: {
    setDistrictsIds (state, action: PayloadAction<number[]>) {
      state.districts_ids = action.payload
    },
    setDistricts (state, action) {
      state.districts = action.payload
    }
  },
  extraReducers: (builder) => {
    builder.addCase(districtsThunk.getAll.fulfilled, (state, action) => {
      state.districts = action.payload
    })
    builder.addCase(districtsThunk.getBbox.fulfilled, (state, action) => {
      state.districts = action.payload
    })
  }
})


export const { setDistrictsIds, setDistricts } = districtsSlice.actions

export default districtsSlice.reducer