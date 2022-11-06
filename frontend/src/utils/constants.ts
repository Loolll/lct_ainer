import { CandidateItemType } from "../interfaces/candidates";
import { PaletteItem } from "../interfaces/common";

export const palette: PaletteItem[] = [
  {
    color: '#800000'
  },
  {
    color: '#A52A2A'
  },
  {
    color: '#A0522D'
  },
  {
    color: '#8B4513'
  },
  {
    color: '#D2691E'
  },
  {
    color: '#B8860B'
  },
  {
    color: '#CD853F'
  },
  {
    color: '#4B0082'
  },
  {
    color: '#8B008B'
  },
  {
    color: '#FF00FF'
  },
  {
    color: '#8A2BE2'
  },
  {
    color: '#483D8B'
  },
  {
    color: '#191970'
  },
  {
    color: '#00008B'
  },
  {
    color: '#4682B4'
  },
  {
    color: '#00CED1'
  },
  {
    color: '#5F9EA0'
  },
  {
    color: '#FF4500'
  },
  {
    color: '#FF7F50'
  },
  {
    color: '#2E8B57'
  },
  {
    color: '#006400'
  },
  {
    color: '#808000'
  },
  {
    color: '#008B8B'
  },
  {
    color: '#00FF00'
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