import { CandidateItemType } from "../interfaces/candidates";
import { PaletteItem } from "../interfaces/common";

export const palette: PaletteItem[] = [
  {
    color: '#00a1ff'
  },
  {
    color: '#00c3d0'
  },
  {
    color: '#93d472'
  },
  {
    color: '#ffce8d'
  },
  {
    color: '#ffccf8'
  },
  {
    color: '#a51f81'
  },
  {
    color: '#d54b65'
  },
  {
    color: '#ef9b6b'
  },
  {
    color: '#f6e2a0'
  },
  {
    color: '#f3efda'
  },
  {
    color: '#a587d1'
  },
  {
    color: '#2b9fc9'
  },
  {
    color: '#4dbfaa'
  },
  {
    color: '#e5e5b3'
  },
  {
    color: '#ededdb'
  },
  {
    color: '#e984ff'
  },
  {
    color: '#ff6cc4'
  },
  {
    color: '#ffab81'
  },
  {
    color: '#ffe884'
  },
  {
    color: '#dcffb2'
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