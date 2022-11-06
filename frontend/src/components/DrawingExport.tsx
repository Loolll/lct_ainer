import FileDownloadIcon from '@mui/icons-material/FileDownload';
import { memo } from 'react';
import { useMap } from 'react-leaflet';
import { GetCandidatesParams, TypesCandidates } from '../interfaces/candidates';
import { BboxRequestParams } from '../interfaces/common';
import { DrawingElementsPropsRefGetBboxStatesParams } from '../interfaces/drawingElements';
import { candidatesThunk } from '../store/reducers/candidatesSlice';
import { useAppDispatch, useAppSelector } from '../store/store';
import { convertLngToLon } from '../utils/helpers';

const DrawingExport = () => {

  const dispatch = useAppDispatch()
  const map = useMap()
  const { rate, types, currentModifier: modifier } = useAppSelector(state => state.filters)
  const { abbrevFilter: abbrev_ao } = useAppSelector(state => state.states)
  const { districts_ids } = useAppSelector(state => state.districts)

  const exportCandidates = () => {
    const bounds = map.getBounds()
    const params = {
      lb_point: convertLngToLon(bounds.getSouthWest()),
      lu_point: convertLngToLon(bounds.getNorthWest()),
      rb_point: convertLngToLon(bounds.getSouthEast()),
      ru_point: convertLngToLon(bounds.getNorthEast()),
      rate,
      types: types.map((item: TypesCandidates) => item.id),
      abbrev_ao,
      districts_ids,
      min_modifier_v1: 0,
      max_modifier_v1: 1,
      min_modifier_v2: 0,
      max_modifier_v2: 1
    }
    if (modifier === 'modifier_v1') {
      params.min_modifier_v1 = rate.min
      params.max_modifier_v1 = rate.max
    } else if (modifier === 'modifier_v2') {
      params.min_modifier_v2 = rate.min
      params.max_modifier_v2 = rate.max
    }
    dispatch(candidatesThunk.export(params))
  }

  return (
    <div className='custom-export' onClick={() => exportCandidates()}>
      <FileDownloadIcon sx={{ fontSize: 30 }} />
    </div>
  )
}

export default memo(DrawingExport)