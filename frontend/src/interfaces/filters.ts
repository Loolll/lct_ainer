import { TypesCandidates } from "./candidates";
import { SearchDistrictItem } from "./districts";
import { StateItem } from "./states";

export interface FilterState {
  state: Pick<StateItem, 'abbrev' | 'name'> | null,
  districts: SearchDistrictItem[],
  rate: {
    min: number,
    max: number
  },
  types: TypesCandidates[],
  currentFilter: 'state' | 'district' | 'rate' | 'types' |'none',
  currentMode: 'sector' | 'heat_map',
  currentModifier: 'modifier_v1' | 'modifier_v2'
}