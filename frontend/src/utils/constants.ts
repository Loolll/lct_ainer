import { CandidateItemType } from "../interfaces/candidates";
import { PaletteItem } from "../interfaces/common";

export const palette: PaletteItem[] = [
  {
    color: '#FF00FF'
  },
  {
    color: '#800080'
  },
  {
    color: '#FF0000'
  },
  {
    color: '#800000'
  },
  {
    color: '#FFFF00'
  },
  {
    color: '#808000'
  },
  {
    color: '#00FF00'
  },
  {
    color: '#008000'
  },
  {
    color: '#00FFFF'
  },
  {
    color: '#008080'
  },
  {
    color: '#0000FF'
  },
  {
    color: '#000080'
  },
  {
    color: '#7B68EE'
  },
  {
    color: '#4169E1'
  },
  {
    color: '#BA55D3'
  },
  {
    color: '#9370DB'
  },
  {
    color: '#8A2BE2'
  }
]

export const typesCandidates = [
  {
    id: CandidateItemType.ANY,
    name: 'Любой'
  },
  {
    id: CandidateItemType.BUS_STATION,
    name: 'Автобусная остановка'
  },
  {
    id: CandidateItemType.CULTURE_HOUSE,
    name: 'Дом культуры'
  },
  {
    id: CandidateItemType.HOUSE,
    name: 'Дом'
  },
  {
    id: CandidateItemType.LIBRARY,
    name: 'Библиотека'
  },
  {
    id: CandidateItemType.METRO,
    name: 'Метро'
  },
  {
    id: CandidateItemType.MFC,
    name: 'МФЦ'
  },
  {
    id: CandidateItemType.NTO_NON_PAPER,
    name: 'НТО остальные'
  },
  {
    id: CandidateItemType.NTO_PAPER,
    name: 'НТО бумажные'
  },
  {
    id: CandidateItemType.PARKING,
    name: 'Парковка'
  },
  {
    id: CandidateItemType.POSTAMAT,
    name: 'Постамат'
  },
  {
    id: CandidateItemType.SPORTS,
    name: 'Спорт'
  },

]