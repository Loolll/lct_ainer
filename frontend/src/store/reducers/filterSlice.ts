import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { SearchDistrictItem } from '../../interfaces/districts'
import { FilterState } from '../../interfaces/filters'
import { StateItem } from '../../interfaces/states'

const initialState: FilterState = {
  state: null,
  districts: [],
  currentFilter: 'state'
}

export const filterSlice = createSlice({
  name: 'filter',
  initialState,
  reducers: {
    setFilterState (state, action: PayloadAction<Pick<StateItem, 'abbrev' | 'name'> | null>) {
      state.state = action.payload
    },
    setFilterDistricts (state, action: PayloadAction<SearchDistrictItem[]>) {
      state.districts = action.payload
    },
    setCurrentFilter (state, action: PayloadAction<FilterState['currentFilter']>) {
      state.currentFilter = action.payload
    }
  }
})


export const { setFilterState, setFilterDistricts, setCurrentFilter } = filterSlice.actions

export default filterSlice.reducer