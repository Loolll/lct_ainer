import { Fragment, useEffect } from 'react'
import { Circle, Polygon, Popup, useMap, useMapEvents } from 'react-leaflet'
import { BboxRequestParams } from '../interfaces/common'
import { candidatesThunk } from '../store/reducers/candidatesSlice'
import { districtsThunk, setDistricts, setDistrictsIds } from '../store/reducers/districtsSlice'
import { setCenter, setZoom } from '../store/reducers/mapSlice'
import { setAbbrevFilter, setStates, statesThunk } from '../store/reducers/statesSlice'
import { useAppDispatch, useAppSelector } from '../store/store'
import { palette } from '../utils/constants'
import { convertLngToLon, convertLonToLng } from '../utils/helpers'

const DrawingElements = () => {

  const dispatch = useAppDispatch()
  const { states } = useAppSelector(state => state.states)
  const { districts } = useAppSelector(state => state.districts)
  const { candidates } = useAppSelector(state => state.candidates)
  const { currentFilter } = useAppSelector(state => state.filters)
  const map = useMap()
  const getBboxStates = () => {
    const bounds = map.getBounds()
    const params: BboxRequestParams = {
      lb_point: convertLngToLon(bounds.getSouthWest()),
      lu_point: convertLngToLon(bounds.getNorthWest()),
      rb_point: convertLngToLon(bounds.getSouthEast()),
      ru_point: convertLngToLon(bounds.getNorthEast())
    }
    dispatch(candidatesThunk.getBbox(params))
    if (currentFilter === 'state') {
      dispatch(statesThunk.getBbox(params))
    } else if (currentFilter === 'district') {
      dispatch(districtsThunk.getBbox(params))
    } else {
      dispatch(setDistricts([]))
      dispatch(setStates([]))
      dispatch(setAbbrevFilter(''))
      dispatch(setDistrictsIds([]))
    }
  }

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
                    color: palette[index]?.color || ''
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
        districts.map((district) => {
          const polygonWithLng = district.polygon.map((item) => {
            return convertLonToLng(item)
          })
          return (
            <Fragment key={district.id}>
              <Polygon
                key={district.id}
                positions={polygonWithLng}
              >
                <Popup>
                  <div>
                    <span>{district.name_ao}</span>
                    <span>&mdash;</span>
                    <span>{district.name}</span>
                  </div>
                </Popup>
              </Polygon>
              <Circle center={convertLonToLng(district.center)} radius={100} />
            </Fragment>
          )
        })
      }
      {
        candidates.map((candidate) => (
          <Fragment key={candidate.id}>
            <Circle center={convertLonToLng(candidate.point)} radius={10}>
              <Popup>
                <div>
                  {
                    candidate.address && <div>Адрес: {candidate.address}</div>
                  }
                  <div style={{ padding: '5px 0 5px 0' }}>Радиус расчета: {candidate.calculated_radius}м</div>
                  <div>Тип: {candidate.type}</div>
                </div>
              </Popup>
            </Circle>
          </Fragment>
        ))
      }
    </>
  )
}

export default DrawingElements