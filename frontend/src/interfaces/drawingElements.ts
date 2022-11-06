import { ForwardedRef } from "react";
import { TypesCandidates } from "./candidates";
import { FilterState } from "./filters";

export interface DrawingElementsProps {
  ref: ForwardedRef<DrawingElementsPropsRef>
}

export interface DrawingElementsPropsRef {
  getBboxStates: (params?: DrawingElementsPropsRefGetBboxStatesParams) => void
}

export interface DrawingElementsPropsRefGetBboxStatesParams {
  currentFilter?: FilterState['currentFilter'],
  districts_ids?: number[],
  abbrevFilter?: string,
  rate?: {
    min: number,
    max: number
  },
  types?: string[]
  modifier?: FilterState['currentModifier']
}