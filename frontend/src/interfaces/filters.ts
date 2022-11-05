import { SearchDistrictItem } from "./districts";
import { StateItem } from "./states";

export interface FilterState {
  state: Pick<StateItem, 'abbrev' | 'name'> | null,
  districts: SearchDistrictItem[],
  currentFilter: 'state' | 'district' | 'none'
}