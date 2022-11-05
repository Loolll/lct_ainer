import { FC, memo } from 'react'
import { MapContainer, TileLayer } from 'react-leaflet'
import { useAppSelector } from '../store/store'
import DrawingElements from './DrawingElements'
import HeatLayer from './HeatLayer'

const Map: FC = () => {

  const { center, zoom } = useAppSelector(state => state.map)

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      minZoom={13}
      scrollWheelZoom={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <DrawingElements />
      <HeatLayer />
    </MapContainer>
  )
}

export default memo(Map)