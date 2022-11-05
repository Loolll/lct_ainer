import { configureStore } from '@reduxjs/toolkit'
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '../interfaces/common'
import candidatesSlice from './reducers/candidatesSlice';
import districtsSlice from './reducers/districtsSlice';
import filterSlice from './reducers/filterSlice';
import mapSlice from './reducers/mapSlice';
import statesSlice from './reducers/statesSlice'

const store = configureStore({
  reducer: {
    states: statesSlice,
    filters: filterSlice,
    districts: districtsSlice,
    candidates: candidatesSlice,
    map: mapSlice
  },
});

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export default store;
