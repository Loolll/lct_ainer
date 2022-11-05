import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'

const HeatLayer = () => {
  const map = useMap()
   useEffect(() => {
     const points = addressPoints
     ? addressPoints.map((p) => {
       return [p[0], p[1]]; // lat lng intensity
       })
     : [];

    // @ts-ignore
     L.heatLayer(points, {
      gradient: {
        0.5: '#020633',
        // 0.1: '#9916EE',
        // 0.2: '#1D2FF1',
        // 0.4: '#00BC5C',
        // 0.6: '#FDD42E',
        // 0.8: '#DE1213',
        1: "#fd0c50"
      },
      minOpacity: .8,
     }).addTo(map);
   }, [])
  return (
    <></>
  )
}

export default HeatLayer

export const addressPoints = [
  [-37.9124889333, 175.4727737833]
];