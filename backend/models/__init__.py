from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, validator
from ast import literal_eval

from misc.colors import get_color_grad


class Georaphy(BaseModel):
    lat: float
    lon: float

    def to_json(self) -> dict:
        return {'lat': self.lat, 'lon': self.lon}

    @classmethod
    def from_json(cls, json: dict) -> 'Georaphy':
        return cls(lat=json['lat'], lon=json['lon'])

    def distance_metres(self, another: 'Georaphy') -> float:
        geog_dist = ((self.lon - another.lon)**2 + (self.lat - another.lat)**2)**0.5
        return geog_dist * 66918.235


GeographyPolygon = list[Georaphy]


def from_postgis_poly(polygon: str) -> GeographyPolygon:
    polygon = polygon[9:-2]
    pairs = [pair.split() for pair in polygon.split(',')]
    return [Georaphy(lat=x[0], lon=x[1]) for x in pairs]


def from_postgis_polygons(polygons: str) -> list[GeographyPolygon]:
    polygons = polygons[7:].replace(' ', ',')
    parsed: tuple[tuple] = literal_eval(polygons)

    if type(parsed[0]) is float:
        parsed = (parsed, )

    return [
        [
            Georaphy(lat=pairs[x], lon=pairs[x+1])
            for x in range(0, len(pairs), 2)
        ]
        for pairs in parsed
    ]


def to_postgis_poly(polygon: GeographyPolygon) -> str:
    points = ','.join([f"{x.lat} {x.lon}" for x in polygon])
    return 'POLYGON((' + points + '))'


def to_postgis_polygons(polygons: list[GeographyPolygon]) -> str:
    temp = []
    for polygon in polygons:
        points = ','.join([f"{x.lat} {x.lon}" for x in polygon])
        temp.append('(' + points + ')')
    return 'POLYGON(' + ','.join(temp) + ')'


def to_postgis_point(point: Georaphy) -> str:
    return f'POINT({point.lat} {point.lon})'


class StateForm(BaseModel):
    abbrev: str
    name: str
    polygons: list[GeographyPolygon]
    # center: Georaphy
    reliability: float


class State(StateForm):
    pass


class DistrictForm(BaseModel):
    abbrev_ao: str
    name_ao: str
    name: str
    polygon: GeographyPolygon
    center: Georaphy
    reliability: float


class District(DistrictForm):
    id: int


class MetroForm(BaseModel):
    station: str
    entrance: int
    district_id: int
    abbrev_ao: str
    point: Georaphy
    traffic_modifier: float


class Metro(MetroForm):
    id: int


class PostamatForm(BaseModel):
    id: str
    point: Georaphy
    address: str
    company: str
    abbrev_ao: str
    district_id: int
    metro_id: Optional[int]
    hours_modifier: float
    company_modifier: float
    result_modifier: float


class Postamat(PostamatForm):
    pass


class ParkingForm(BaseModel):
    id: str
    point: Georaphy
    address: str
    abbrev_ao: str
    district_id: int
    size_modifier: float


class Parking(ParkingForm):
    pass


class BusStationForm(BaseModel):
    id: int
    address: str
    point: Georaphy
    abbrev_ao: str
    district_id: int
    modifier: float


class BusStation(BusStationForm):
    pass


class CultureHouseForm(BaseModel):
    id: int
    address: str
    point: Georaphy
    abbrev_ao: str
    district_id: int


class CultureHouse(CultureHouseForm):
    pass


class LibraryForm(BaseModel):
    id: int
    point: Georaphy
    address: str
    abbrev_ao: str
    district_id: int
    modifier: float


class Library(LibraryForm):
    pass


class MfcForm(BaseModel):
    id: int
    address: str
    point: Georaphy
    abbrev_ao: str
    district_id: int
    modifier: float


class Mfc(MfcForm):
    pass


class SportsForm(BaseModel):
    id: int
    address: str
    point: Georaphy
    abbrev_ao: str
    district_id: int
    modifier: float


class Sports(SportsForm):
    pass


class NtoPaperForm(BaseModel):
    id: int
    address: str
    point: Georaphy
    abbrev_ao: str
    district_id: int


class NtoPaper(NtoPaperForm):
    pass


class NtoNonPaperForm(BaseModel):
    id: int
    address: str
    point: Georaphy
    abbrev_ao: str
    district_id: int


class NtoNonPaper(NtoNonPaperForm):
    pass


class HouseForm(BaseModel):
    id: str
    address: str
    point: Georaphy
    abbrev_ao: str
    district_id: int
    modifier: float


class House(HouseForm):
    pass


class CandidateType(str, Enum):
    house = 'house'
    bus_station = 'bus_station'
    culture_house = 'culture_house'
    library = 'library'
    metro = 'metro'
    mfc = 'mfc'
    nto_non_paper = 'nto_non_paper'
    nto_paper = 'nto_paper'
    parking = 'parking'
    postamat = 'postamat'
    sports = 'sports'
    any = 'any'


class CandidateForm(BaseModel):
    abbrev_ao: str
    district_id: int
    point: Georaphy
    address: Optional[str]
    type: CandidateType = CandidateType.any

    calculated_radius: float
    state_modifier: float
    district_modifier: float

    metro_count: int
    metro_min_dest: float
    metro_nearest_modifier: float
    metro_average_dest: float
    metro_average_modifier: float

    postamats_count: int
    postamats_min_dest: float
    postamats_nearest_modifier: float
    postamats_average_dest: float
    postamats_average_modifier: float

    parkings_count: int
    parkings_min_dest: float
    parkings_nearest_modifier: float
    parkings_average_dest: float
    parkings_average_modifier: float

    bus_stations_count: int
    bus_stations_min_dest: float
    bus_stations_nearest_modifier: float
    bus_stations_average_dest: float
    bus_stations_average_modifier: float

    culture_houses_count: int
    culture_houses_min_dest: float
    culture_houses_average_dest: float

    libraries_count: int
    libraries_min_dest: float
    libraries_nearest_modifier: float
    libraries_average_dest: float
    libraries_average_modifier: float

    mfc_count: int
    mfc_min_dest: float
    mfc_nearest_modifier: float
    mfc_average_dest: float
    mfc_average_modifier: float

    sports_count: int
    sports_min_dest: float
    sports_nearest_modifier: float
    sports_average_dest: float
    sports_average_modifier: float

    nto_paper_count: int
    nto_paper_min_dest: float
    nto_paper_average_dest: float

    nto_non_paper_count: int
    nto_non_paper_min_dest: float
    nto_non_paper_average_dest: float

    houses_count: int
    houses_min_dest: float
    houses_nearest_modifier: float
    houses_average_dest: float
    houses_average_modifier: float

    modifier_v1: Optional[float]
    modifier_v2: Optional[float]


class Candidate(CandidateForm):
    id: int


class MapCandidate(BaseModel):
    id: Optional[int]
    abbrev_ao: Optional[str]
    district_id: Optional[int]
    point: Georaphy
    address: Optional[str]
    type: Optional[CandidateType]
    calculated_radius: Optional[float]
    aggregation_radius: Optional[float]
    modifier_v1: float
    modifier_v2: float
    color_v1: str
    color_v2: str
    count: int = 1

    @staticmethod
    def get_hex_color(r: int, g: int, b: int) -> str:
        return f'#{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}'

    @validator('color_v1', 'color_v2', pre=True)
    def _validate_color(cls, value: str | list) -> str:
        if type(value) is list:
            return MapCandidate.get_hex_color(*value)
        else:
            return value

    @classmethod
    def from_full(cls, obj: Candidate) -> 'MapCandidate':
        return MapCandidate(
            **obj.dict(),
            color_v1=get_color_grad(obj.modifier_v1),
            color_v2=get_color_grad(obj.modifier_v2),
        )


class Nearest(BaseModel):
    distance: float
    obj: Any


class BboxQuery(BaseModel):
    lu_point: Georaphy
    ru_point: Georaphy
    rb_point: Georaphy
    lb_point: Georaphy

    def to_poly(self) -> GeographyPolygon:
        return [
            self.lu_point,
            self.ru_point,
            self.rb_point,
            self.lb_point,
            self.lu_point
        ]


class CandidateFilter(BboxQuery):
    abbrev_ao: Optional[str]
    districts_ids: Optional[list[int]]
    min_modifier_v1: Optional[float] = 0
    max_modifier_v1: Optional[float] = 1
    min_modifier_v2: Optional[float] = 0
    max_modifier_v2: Optional[float] = 1
    types: Optional[list[CandidateType]]


class StateFilter(BboxQuery):
    abbrev_ao: Optional[str]


class DistrictFilter(BboxQuery):
    districts_ids: Optional[list[int]]


class DistrictAutocompleteObject(BaseModel):
    id: int
    name: str


DistrictAutocompleteResponse = list[DistrictAutocompleteObject]


class StateAutocompleteObject(BaseModel):
    abbrev: str
    name: str


StateAutocompleteResponse = list[StateAutocompleteObject]
