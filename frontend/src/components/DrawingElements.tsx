import { forwardRef, Fragment, memo, useEffect, useImperativeHandle } from 'react'
import { Circle, Polygon, Popup, Tooltip, useMap, useMapEvents } from 'react-leaflet'
import { BboxRequestParams } from '../interfaces/common'
import { DrawingElementsPropsRefGetBboxStatesParams, DrawingElementsProps, DrawingElementsPropsRef } from '../interfaces/drawingElements'
import { candidatesThunk } from '../store/reducers/candidatesSlice'
import { districtsThunk, setDistricts, setDistrictsIds } from '../store/reducers/districtsSlice'
import { setFilterRate, setFilterType } from '../store/reducers/filterSlice'
import { setBounds, setCenter, setZoom } from '../store/reducers/mapSlice'
import { setAbbrevFilter, setStates, statesThunk } from '../store/reducers/statesSlice'
import { useAppDispatch, useAppSelector } from '../store/store'
import { palette } from '../utils/constants'
import { convertLngToLon, convertLonToLng } from '../utils/helpers'

const DrawingElements = forwardRef<DrawingElementsPropsRef, DrawingElementsProps>((_, ref) => {

  const dispatch = useAppDispatch()
  const { states } = useAppSelector(state => state.states)
  const { districts } = useAppSelector(state => state.districts)
  const { candidates } = useAppSelector(state => state.candidates)
  const { currentFilter, currentMode, currentModifier } = useAppSelector(state => state.filters)
  const map = useMap()

  const getBboxStates = (data?: DrawingElementsPropsRefGetBboxStatesParams) => {
    const bounds = map.getBounds()
    const params: BboxRequestParams = {
      ...data,
      lb_point: convertLngToLon(bounds.getSouthWest()),
      lu_point: convertLngToLon(bounds.getNorthWest()),
      rb_point: convertLngToLon(bounds.getSouthEast()),
      ru_point: convertLngToLon(bounds.getNorthEast())
    }
    dispatch(setBounds(params))
    dispatch(candidatesThunk.getBbox(params))
    if ((data?.currentFilter || currentFilter) === 'state') {
      dispatch(statesThunk.getBbox(params))
    } else if ((data?.currentFilter || currentFilter) === 'district') {
      dispatch(districtsThunk.getBbox(params))
    } else if ((data?.currentFilter || currentFilter) === 'none') {
      dispatch(setDistricts([]))
      dispatch(setStates([]))
      dispatch(setAbbrevFilter(''))
      dispatch(setDistrictsIds([]))
      dispatch(setFilterType([]))
      dispatch(setFilterRate({
        min: 0,
        max: 1
      }))
    }
  }

  useImperativeHandle(ref, () => ({
    getBboxStates
  }))

  useMapEvents({
    moveend: (e) => {
      getBboxStates()
      const center = e.target.getCenter()
      const zoom = e.target.getZoom()
      dispatch(setCenter([center.lat, center.lng]))
      dispatch(setZoom(zoom))
    }
  })

  useEffect(() => {
    getBboxStates()
  }, [])

  return (
    <>
      {
        currentFilter === 'state' &&
        states.map((state, index) => (
          <Fragment key={index}>
            {
              state.polygons.map((polygon, polygonIndex) => {
                const polygonWithLng = polygon.map((item) => {
                  return convertLonToLng(item)
                })
                return <Polygon
                  key={`polygon-${index}-${polygonIndex}`}
                  positions={polygonWithLng}
                  pathOptions={{
                    color: palette.at(index)?.color || ''
                  }}
                >
                  <Popup>
                    <div>
                      <span>{state.abbrev}</span>
                      <span>&mdash;</span>
                      <span>{state.name}</span>
                    </div>
                  </Popup>
                </Polygon>
              })
            }
          </Fragment>
        ))
      }
      {
        currentFilter === 'district' &&
        districts.map((district, index) => {
          const polygonWithLng = district.polygon.map((item) => {
            return convertLonToLng(item)
          })
          return (
            <Fragment key={district.id}>
              <Polygon
                key={district.id}
                positions={polygonWithLng}
                pathOptions={{
                  color: palette.at(index)?.color || ''
                }}
              >
                <Popup>
                  <div>
                    <span>{district.name_ao}</span>
                    <span>&mdash;</span>
                    <span>{district.name}</span>
                  </div>
                </Popup>
              </Polygon>
            </Fragment>
          )
        })
      }
      {
        candidates.map((candidate) => (
          <Fragment key={candidate.id || `${candidate.modifier_v1}${candidate.modifier_v2}`}>
            {
              currentMode === 'sector' && (
                <Circle
                  center={convertLonToLng(candidate.point)}
                  radius={candidate.id ? 10 : candidate.aggregation_radius}
                  pathOptions={{
                    fillColor: currentModifier === 'modifier_v1' ? candidate.color_v1 : candidate.color_v2,
                    color: currentModifier === 'modifier_v1' ? candidate.color_v1 : candidate.color_v2
                  }}
                >
                  <>
                    {
                      candidate.id && (
                        <Popup>
                          <div>
                            {
                              candidate.address && <div>Адрес: {candidate.address}</div>
                            }
                            <div style={{ padding: '5px 0 5px 0' }}>Радиус расчета: {candidate.calculated_radius}м</div>
                            <div>Тип: {candidate.type}</div>
                            <div style={{ padding: '5px 0 5px 0' }}>Модификатор 1: {candidate.modifier_v1}</div>
                            <div>Модификатор 2: {candidate.modifier_v2}</div>
                          </div>
                        </Popup>
                      )
                    }
                    {
                      !candidate.id && (
                        <Tooltip>
                          { candidate.count } шт
                        </Tooltip>
                      )
                    }
                  </>
                </Circle>
              )
            }
            {
              currentMode === 'heat_map' && (
                <Circle
                  center={convertLonToLng(candidate.point)}
                  radius={candidate.id ? 40 : candidate.aggregation_radius}
                  pathOptions={{
                    fillColor: currentModifier === 'modifier_v1' ? candidate.color_v1 : candidate.color_v2,
                    fillOpacity: .5,
                    color: currentModifier === 'modifier_v1' ? candidate.color_v1 : candidate.color_v2
                  }}
                >
                  <Popup>
                    {
                      candidate.id && (
                        <div>
                          {
                            candidate.address && <div>Адрес: {candidate.address}</div>
                          }
                          <div style={{ padding: '5px 0 5px 0' }}>Радиус расчета: {candidate.calculated_radius}м</div>
                          <div>Тип: {candidate.type}</div>
                          <div style={{ padding: '5px 0 5px 0' }}>Модификатор 1: {candidate.modifier_v1}</div>
                          <div>Модификатор 2: {candidate.modifier_v2}</div>
                        </div>
                      )
                    }
                    {
                      !candidate.id && (
                        <div>
                          { candidate.count }
                        </div>
                      )
                    }
                  </Popup>
                </Circle>
              )
            }
          </Fragment>
        ))
      }
    </>
  )
})

export default memo(DrawingElements)