import { createSlice } from '@reduxjs/toolkit'
import { MapState } from '../../interfaces/map'

const initialState: MapState = {
  center: [55.558741, 37.378847],
  zoom: 13
}

export const mapSlice = createSlice({
  name: 'map',
  initialState,
  reducers: {
    setCenter (state, action) {
      state.center = action.payload
    },
    setZoom (state, action) {
      state.zoom = action.payload
    }
  }
})


export const { setCenter, setZoom } = mapSlice.actions

export default mapSlice.reducer