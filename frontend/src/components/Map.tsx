import { FC, memo, useState, Fragment, useRef, ForwardedRef, ChangeEvent } from 'react'
import { MapContainer, TileLayer } from 'react-leaflet'
import { useAppDispatch, useAppSelector } from '../store/store'
import DrawingElements from './DrawingElements'
import Screenshot from './Screenshot'
import { Autocomplete, CircularProgress, Drawer, FormControl, FormLabel, TextField, RadioGroup, Radio, FormControlLabel } from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu';
import { setFilterState, setCurrentFilter, setFilterDistricts, setCurrentMode, setCurrentModifier, setFilterRate, setFilterType } from '../store/reducers/filterSlice';
import { FilterState } from '../interfaces/filters';
import { districtsThunk, setDistrictsIds } from '../store/reducers/districtsSlice';
import { DistrictItem, SearchDistrictItem } from '../interfaces/districts';
import { StateItem } from '../interfaces/states'
import { setAbbrevFilter, statesThunk } from '../store/reducers/statesSlice'
import { DrawingElementsPropsRef, DrawingElementsPropsRefGetBboxStatesParams } from '../interfaces/drawingElements'
import { TypesCandidates } from '../interfaces/candidates'
import { typesCandidates } from '../utils/constants'
import DrawingMarker from './DrawingMarker'
import DrawingExport from './DrawingExport'

const Map: FC = () => {

  const dispatch = useAppDispatch()
  const drawingRef: ForwardedRef<DrawingElementsPropsRef> = useRef(null)
  const { center, zoom } = useAppSelector(state => state.map)
  const { state, currentFilter, currentMode, currentModifier, districts, rate, types } = useAppSelector(state => state.filters)
  const [activeMenu, setActiveMenu] = useState(false)
  const [open, setOpen] = useState({
    state: false,
    district: false,
    type: false
  })
  const [filterLoading, setFilterLoading] = useState(false)
  const [options, setOptions] = useState<{ state: Pick<StateItem, 'abbrev' | 'name'>[], district: SearchDistrictItem[], types: TypesCandidates[] }>({
    state: [],
    district: [],
    types: typesCandidates
  })

  const getOptions = async (query: string, option: 'state' | 'district' | 'type') => {
    if (option === 'type') {
      setOptions(options => {
        return {
          ...options,
          type: options.types.filter((option) => option.id === query)
        }
      })
      return
    }
    setFilterLoading(true)
    const params = {
      query: query || null
    };
    (option === 'state'
      ? dispatch(statesThunk.search(params))
      : dispatch(districtsThunk.search(params)))
    .unwrap()
    .then((response: StateItem[] | DistrictItem[]) => {
      setOptions(options => ({
        ...options,
        [option]: [...response]
      }))
    })
    .finally(() => setFilterLoading(false))
  }

  const getBboxState = (value: Pick<StateItem, "abbrev" | "name"> | null) => {
    dispatch(setAbbrevFilter(value?.abbrev || ''))
    dispatch(setFilterState(value))
    const params = {
      abbrevFilter: value?.abbrev || ''
    }
    drawingRef.current && drawingRef.current.getBboxStates(params)
  }

  const getBboxDistrict = (value: SearchDistrictItem[]) => {
    const ids = value.map((item) => item.id)
    dispatch(setDistrictsIds(ids))
    dispatch(setFilterDistricts(value))
    const params = {
      districts_ids: ids
    }
    drawingRef.current && drawingRef.current.getBboxStates(params)
  }

  const getBboxType = (value: TypesCandidates[]) => {
    dispatch(setFilterType(value))
    const params = {
      types: value.map((item) => item.id)
    }
    drawingRef.current && drawingRef.current.getBboxStates(params)
  }

  const changeRadioFilter = (e: ChangeEvent<HTMLInputElement>) => {
    dispatch(setCurrentFilter(e.target.value as FilterState['currentFilter']))
    const params: DrawingElementsPropsRefGetBboxStatesParams = {
      currentFilter: e.target.value as FilterState['currentFilter']
    }
    if (e.target.value === 'none') {
      params.abbrevFilter = ''
      params.districts_ids = []
      params.rate = {
        min: 0,
        max: 1
      }
      dispatch(setFilterState(null))
      dispatch(setFilterDistricts([]))
    }
    drawingRef.current && drawingRef.current.getBboxStates(params)
  }

  const changeFilterMode = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value as FilterState['currentMode']
    dispatch(setCurrentMode(value))
  }

  const changeFilterModifier = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value as FilterState['currentModifier']
    dispatch(setCurrentModifier(value))
    const params = {
      modifier: value
    }
    drawingRef.current && drawingRef.current.getBboxStates(params)
  }

  const changeFilterRate = (value: string | number, rateOption: keyof FilterState['rate']) => {
    const newRate = {
      ...rate,
      [rateOption]: value
    }
    dispatch(setFilterRate(newRate))
    const params = {
      rate: newRate
    }
    drawingRef.current && drawingRef.current.getBboxStates(params)
  }

  return (
    <MapContainer
      center={center}
      zoom={zoom}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <DrawingExport />
      <DrawingElements
        ref={drawingRef}
      />
      <DrawingMarker />
      <Screenshot />
      <div
        className="custom-menu-btn"
        onClick={() => setActiveMenu(true)}
      >
        <MenuIcon sx={{ fontSize: 30 }} />
      </div>
      <Drawer
        anchor="left"
        open={activeMenu}
        onClose={() => setActiveMenu(false)}
      >
        <div className='custom-menu'>
          <form>
            <FormControl>
              <FormLabel id="filters">Фильтрация</FormLabel>
              <RadioGroup
                aria-labelledby="filters"
                value={currentFilter}
                onChange={(e) => changeRadioFilter(e)}
                name="radio-filter"
              >
                <FormControlLabel value="state" control={<Radio />} label="По округам" />
                {
                  currentFilter === 'state' && (
                    <Autocomplete
                      id="state-autocomplete"
                      sx={{ width: 300 }}
                      size="small"
                      open={open.state}
                      onOpen={() => {
                        setOpen(obj => ({
                          ...obj,
                          state: true
                        }))
                      }}
                      onClose={(e) => {
                        setOpen(obj => ({
                          ...obj,
                          state: false
                        }))
                      }}
                      onInput={(e) => {
                        setTimeout(() => {
                          getOptions((e.target as HTMLInputElement).value, 'state')
                        }, 100)
                      }}
                      onFocus={(e) => {
                        getOptions((e.target as HTMLInputElement).value, 'state')
                      }}
                      onChange={(_, value) => getBboxState(value)}
                      value={state}
                      isOptionEqualToValue={(option, value) => option.abbrev === value.abbrev}
                      getOptionLabel={(option) => option.name}
                      options={options.state}
                      noOptionsText="Нет данных"
                      loading={filterLoading}
                      loadingText="Нет данных"
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Округ"
                          InputProps={{
                            ...params.InputProps,
                            endAdornment: (
                              <Fragment>
                                {filterLoading ? <CircularProgress color="inherit" size={20} /> : null}
                                {params.InputProps.endAdornment}
                              </Fragment>
                            ),
                          }}
                        />
                      )}
                    />
                  )
                }
                <FormControlLabel value="district" control={<Radio />} label="По районам" />
                {
                  currentFilter === 'district' && (
                    <Autocomplete
                      id="district-autocomplete"
                      multiple
                      sx={{ width: 300 }}
                      size="small"
                      open={open.district}
                      onOpen={() => {
                        setOpen(obj => ({
                          ...obj,
                          district: true
                        }))
                      }}
                      onClose={() => {
                        setOpen(obj => ({
                          ...obj,
                          district: false
                        }))
                      }}
                      onInput={(e) => {
                        setTimeout(() => {
                          getOptions((e.target as HTMLInputElement).value, 'district')
                        }, 100)
                      }}
                      onFocus={(e) => {
                        getOptions((e.target as HTMLInputElement).value, 'district')
                      }}
                      onChange={(_, value) => getBboxDistrict(value)}
                      value={districts}
                      isOptionEqualToValue={(option, value) => option.id === value.id}
                      filterSelectedOptions
                      getOptionLabel={(option) => option.name}
                      disableCloseOnSelect
                      options={options.district}
                      noOptionsText="Нет данных"
                      loading={filterLoading}
                      loadingText="Нет данных"
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Район"
                          InputProps={{
                            ...params.InputProps,
                            endAdornment: (
                              <Fragment>
                                {filterLoading ? <CircularProgress color="inherit" size={20} /> : null}
                                {params.InputProps.endAdornment}
                              </Fragment>
                            ),
                          }}
                        />
                      )}
                    />
                  )
                }
                <FormControlLabel value="types" control={<Radio />} label="По типу" />
                {
                  currentFilter === 'types' && (
                    <Autocomplete
                      id="types-autocomplete"
                      multiple
                      sx={{ width: 300 }}
                      size="small"
                      open={open.type}
                      onOpen={() => {
                        setOpen(obj => ({
                          ...obj,
                          type: true
                        }))
                      }}
                      onClose={() => {
                        setOpen(obj => ({
                          ...obj,
                          type: false
                        }))
                      }}
                      onInput={(e) => {
                        setTimeout(() => {
                          getOptions((e.target as HTMLInputElement).value, 'type')
                        }, 100)
                      }}
                      onFocus={(e) => {
                        getOptions((e.target as HTMLInputElement).value, 'type')
                      }}
                      onChange={(_, value) => getBboxType(value)}
                      value={types}
                      isOptionEqualToValue={(option, value) => option.id === value.id}
                      filterSelectedOptions
                      getOptionLabel={(option) => option.name}
                      disableCloseOnSelect
                      options={options.types}
                      noOptionsText="Нет данных"
                      loading={filterLoading}
                      loadingText="Нет данных"
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Типы"
                          InputProps={{
                            ...params.InputProps,
                            endAdornment: (
                              <Fragment>
                                {filterLoading ? <CircularProgress color="inherit" size={20} /> : null}
                                {params.InputProps.endAdornment}
                              </Fragment>
                            ),
                          }}
                        />
                      )}
                    />
                  )
                }
                <FormControlLabel value="rate" control={<Radio />} label="По рейтингу" />
                {
                  currentFilter === 'rate' && (
                    <>
                      <TextField
                        value={rate.min}
                        type="number"
                        size="small"
                        InputProps={{
                          inputProps: { 
                            max: rate.max < 1 ? rate.max : 1, min: 0, step: .1
                          }
                        }}
                        label="Мин"
                        sx={{ width: 300 }}
                        style={{ paddingBottom: '10px' }}
                        onChange={(e) => changeFilterRate(e.target.value, 'min')}
                      />
                      <TextField
                        value={rate.max}
                        type="number"
                        size="small"
                        InputProps={{
                          inputProps: { 
                            max: 1, min: rate.min > 0 ? rate.min : 0, step: .1
                          }
                        }}
                        label="Макс"
                        sx={{ width: 300 }}
                        onChange={(e) => changeFilterRate(e.target.value, 'max')}
                      />
                    </>
                  )
                }
                <FormControlLabel value="none" control={<Radio />} label="Отключить фильтрацию" />
              </RadioGroup>
            </FormControl>
            <FormControl style={{ paddingTop: '15px' }}>
              <FormLabel id="display-mode">Режим отображения</FormLabel>
              <RadioGroup
                aria-labelledby="display-mode"
                value={currentMode}
                onChange={(e) => changeFilterMode(e)}
                name="display-mode-radio"
              >
                <FormControlLabel value="sector" control={<Radio />} label="Сектора" />
                <FormControlLabel value="heat_map" control={<Radio />} label="Тепловая карта" />
                {
                  currentMode === 'heat_map' && (
                    <FormControl style={{ paddingLeft: '15px' }}>
                      <FormLabel id="modifier">Модификатор</FormLabel>
                      <RadioGroup
                        aria-labelledby="modifier"
                        value={currentModifier}
                        onChange={(e) => changeFilterModifier(e)}
                        name="modifier-radio"
                      >
                        <FormControlLabel value="modifier_v1" control={<Radio />} label="v1" />
                        <FormControlLabel value="modifier_v2" control={<Radio />} label="v2" />
                      </RadioGroup>
                    </FormControl>
                  )
                }
              </RadioGroup>
            </FormControl>
          </form>
        </div>
      </Drawer>
    </MapContainer>
  )
}

export default memo(Map)