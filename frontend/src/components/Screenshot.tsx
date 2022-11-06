import { SimpleMapScreenshoter } from 'leaflet-simple-map-screenshoter'
import { memo } from 'react'
import { useMap } from 'react-leaflet'

const Screenshot = () => {
  const map = useMap()
  new SimpleMapScreenshoter().addTo(map)

  return <></>
}

export default memo(Screenshot)