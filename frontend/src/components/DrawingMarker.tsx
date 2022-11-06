import { Button, FormControl, FormLabel, TextField } from '@mui/material'
import { memo, useState } from 'react'
import { Marker, Popup, useMapEvents } from 'react-leaflet'
import { GetCandidatesCalc } from '../interfaces/candidates'
import { candidatesThunk } from '../store/reducers/candidatesSlice'
import { useAppDispatch, useAppSelector } from '../store/store'

const DrawingMarker = () => {

  const dispatch = useAppDispatch()
  const [position, setPosition] = useState<[number, number]>([0, 0])
  const [radius, setRadius] = useState(0)
  const { currentFilter } = useAppSelector(state => state.filters)

  useMapEvents({
    click: (e) => {
      setPosition([e.latlng.lat, e.latlng.lng])
    }
  })

  const saveCandidate = () => {
    const params: GetCandidatesCalc = {
      data: {
        lat: position[0],
        lon: position[1]
      },
      params: {
        radius
      }
    }
    dispatch(candidatesThunk.addNew(params))
  }

  return (
    <>
      {
        currentFilter === 'none' && !position.find((coord) => !coord) && (
          <Marker position={position}>
            <Popup>
              <FormControl>
                <FormLabel id="create-radius">Радиус</FormLabel>
                <TextField
                  value={radius}
                  onChange={(e) => setRadius(+e.target.value)}
                  type="number"
                  aria-labelledby="create-radius"
                  label="Радиус"
                  size="small"
                  sx={{ width: 300 }}
                  InputProps={{
                    inputProps: { 
                      min: 0, step: 1
                    }
                  }}
                  style={{ margin: '5px 0 5px 0' }}
                />
              </FormControl>
              <div style={{ textAlign: 'center' }}>
                <Button
                  size="small"
                  variant="contained"
                  onClick={() => saveCandidate()}
                >
                  Сохранить
                </Button>
              </div>
            </Popup>
          </Marker>
        )
      }
    </>
  )
}

export default memo(DrawingMarker)