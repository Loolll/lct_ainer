import { createSlice } from '@reduxjs/toolkit'
import { MapState } from '../../interfaces/map'

// 55.752794, 37.620845
const initialState: MapState = {
  center: [55.752794, 37.620845],
  zoom: 13,
  bounds: {
    lb_point: null,
    lu_point: null,
    rb_point: null,
    ru_point: null
  }
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
    },
    setBounds (state, action) {
      state.bounds = action.payload
    }
  }
})


export const { setCenter, setZoom, setBounds } = mapSlice.actions

export default mapSlice.reducer