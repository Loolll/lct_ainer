import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { CandidateItemType, TypesCandidates } from '../../interfaces/candidates'
import { SearchDistrictItem } from '../../interfaces/districts'
import { FilterState } from '../../interfaces/filters'
import { StateItem } from '../../interfaces/states'

const initialState: FilterState = {
  state: null,
  districts: [],
  rate: {
    min: 0,
    max: 1
  },
  types: [],
  currentFilter: 'state',
  currentMode: 'sector',
  currentModifier: 'modifier_v1'
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
    setFilterRate (state, action: PayloadAction<FilterState['rate']>) {
      state.rate = action.payload
    },
    setFilterType (state, action: PayloadAction<TypesCandidates[]>) {
      state.types = action.payload
    },
    setCurrentFilter (state, action: PayloadAction<FilterState['currentFilter']>) {
      state.currentFilter = action.payload
    },
    setCurrentMode (state, action: PayloadAction<FilterState['currentMode']>) {
      state.currentMode = action.payload
    },
    setCurrentModifier (state, action: PayloadAction<FilterState['currentModifier']>) {
      state.currentModifier = action.payload
    }
  }
})


export const { setFilterState, setFilterDistricts, setFilterRate, setFilterType, setCurrentFilter, setCurrentMode, setCurrentModifier } = filterSlice.actions

export default filterSlice.reducer