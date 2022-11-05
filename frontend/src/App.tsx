import { Autocomplete, CircularProgress, Drawer, FormControl, FormLabel, TextField, RadioGroup, Radio, FormControlLabel } from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu';
import { Fragment, useState } from 'react';
import { StateItem } from './interfaces/states';
import { useAppDispatch, useAppSelector } from './store/store';
import { setAbbrevFilter, statesThunk } from './store/reducers/statesSlice';
import Map from './components/Map'
import { setFilterState, setCurrentFilter, setFilterDistricts } from './store/reducers/filterSlice';
import { FilterState } from './interfaces/filters';
import { districtsThunk, setDistrictsIds } from './store/reducers/districtsSlice';
import { DistrictItem, SearchDistrictItem } from './interfaces/districts';

const App = () => {
  const dispatch = useAppDispatch()
  const { abbrevFilter } = useAppSelector(state => state.states)
  const { districts_ids } = useAppSelector(state => state.districts)
  const { state, currentFilter, districts } = useAppSelector(state => state.filters)
  const [activeMenu, setActiveMenu] = useState(false)
  const [open, setOpen] = useState({
    state: false,
    district: false
  })
  const [filterLoading, setFilterLoading] = useState(false)
  const [options, setOptions] = useState<{ state: Pick<StateItem, 'abbrev' | 'name'>[], district: SearchDistrictItem[] }>({
    state: [],
    district: []
  })

  const getOptions = async (query: string, option: 'state' | 'district') => {
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
  }

  const getBboxDistrict = (value: SearchDistrictItem[]) => {
    dispatch(setDistrictsIds(value.map((item) => item.id)))
    dispatch(setFilterDistricts(value))
  }

  return (
    <>
      <Map
        key={`${abbrevFilter}-${districts_ids.length}-${currentFilter}`}
      />
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
                onChange={(e) => dispatch(setCurrentFilter(e.target.value as FilterState['currentFilter']))}
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
                <FormControlLabel value="none" control={<Radio />} label="Отключить фильтрацию" />
              </RadioGroup>
            </FormControl>
          </form>
        </div>
      </Drawer>
    </>
  )
}

export default App
