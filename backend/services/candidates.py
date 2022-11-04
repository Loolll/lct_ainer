import asyncio
from enum import Enum
import random

from store import *
from models import Candidate, CandidateForm, Georaphy, CandidateType
from analytic.distance_rate import predict as predict_rate


MAX_EXPECTED_RADIUS = 1000


class ModifierV1AroundWeights(float, Enum):
    state = 0.3
    district = 0.4
    metro = 0.21
    postamats = -0.29
    parkings = 0.17
    bus_stations = 0.19
    houses = 0.24
    culture_houses = 0.18
    libraries = 0.20
    sports = 0.22
    mfc = 0.21
    nto_paper = 0.214
    nto_non_paper = 0.22


MODIFIER_V1_NORMALIZE = sum([[x.value for x in ModifierV1AroundWeights]])


async def get_point_candidate(
        pool: asyncpg.Pool,
        radius: float,
        point: Georaphy,
        type: CandidateType = CandidateType.any
) -> Candidate:
    candidate = await get_candidate_by_point(pool, point=point, return_none=True)
    if candidate and candidate.calculated_radius == radius:
        return candidate
    else:
        return await calc_candidate(
            pool=pool,
            radius=radius,
            point=point,
            type=type
        )


async def calc_candidate(
        pool: asyncpg.Pool,
        radius: float,
        point: Georaphy,
        type: CandidateType = CandidateType.any,
        proto = None
) -> Candidate:
    loop = asyncio.get_event_loop()
    db_tasks = []
    data = {}

    async def retrieve(coro, key: str):
        data[key] = await coro

    for task in [
        retrieve(get_point_district(pool, point), 'district'),
        retrieve(get_nearest_metro(pool, point=point, max_radius=radius), 'metro'),
        retrieve(get_nearest_postamats(pool, point=point, max_radius=radius), 'postamats'),
        retrieve(get_nearest_parkings(pool, point=point, max_radius=radius), 'parkings'),
        retrieve(get_nearest_bus_stations(pool, point=point, max_radius=radius), 'bus_stations'),
        retrieve(get_nearest_culture_houses(pool, point=point, max_radius=radius), 'culture_houses'),
        retrieve(get_nearest_libraries(pool, point=point, max_radius=radius), 'libraries'),
        retrieve(get_nearest_mfc(pool, point=point, max_radius=radius), 'mfc'),
        retrieve(get_nearest_sports(pool, point=point, max_radius=radius), 'sports'),
        retrieve(get_nearest_nto_paper(pool, point=point, max_radius=radius), 'nto_paper'),
        retrieve(get_nearest_nto_non_paper(pool, point=point, max_radius=radius), 'nto_non_paper'),
        retrieve(get_nearest_houses(pool, point=point, max_radius=radius), 'houses')
    ]:
        db_tasks.append(loop.create_task(task))

    await asyncio.wait(db_tasks)

    district: District = data['district']
    if not district:
        raise DistrictNotFoundedError

    state = data['state'] = await get_state(pool, abbrev=district.abbrev_ao)

    form = {
        'abbrev_ao': state.abbrev,
        'district_id': district.id,
        'point': point,
        'type': type,
        'calculated_radius': radius,
        'state_modifier': state.reliability,
        'district_modifier': district.reliability,
    }

    for key, value in data.items():
        if key in ['state', 'district']:
            continue

        with_modifier_stat = True
        modifier_field = 'modifier'

        if key in ['nto_paper', 'nto_non_paper', 'culture_houses']:
            with_modifier_stat = False

        if key == 'metro':
            modifier_field = 'traffic_modifier'
        elif key == 'postamats':
            modifier_field = 'result_modifier'
        elif key == 'parkings':
            modifier_field = 'size_modifier'

        calc_nearest_stat(
            save_to=form,
            keys_prefix=key,
            objects=value,
            with_modifier_stat=with_modifier_stat,
            modifier_field=modifier_field
        )

    form = CandidateForm(**form)
    form.modifier_v1 = calc_result_modifier_v1(form)
    form.modifier_v2 = calc_result_modifier_v2(form)

    if proto:
        if type is CandidateType.metro:
            form.address = "метро " + proto.station.capitalize()
        else:
            form.address = proto.address.capitalize()

    return await create_candidate(pool, form)


def calc_nearest_stat(
        save_to: dict,
        keys_prefix: str,
        objects: list[Nearest],
        with_modifier_stat: bool,
        modifier_field: str = 'modifier'
) -> None:
    count = len(objects)
    min_dest = min([x.distance for x in objects]) if count else 0
    average_dest = sum([x.distance for x in objects]) / count if count else 0

    _nearest = sorted(
        [x.obj.dict() for x in objects if x.distance == min_dest],
        key=lambda x: -x[modifier_field]
    )[0] if count else None

    nearest_modifier = (_nearest[modifier_field] if with_modifier_stat else None) if count else 0
    average_modifier = (
        sum(
            [x.obj.dict()[modifier_field] for x in objects]
        ) / count if with_modifier_stat else None
    ) if count else 0

    save_to[keys_prefix+'_count'] = count
    save_to[keys_prefix+'_min_dest'] = min_dest
    save_to[keys_prefix+'_average_dest'] = average_dest

    if with_modifier_stat:
        save_to[keys_prefix+'_nearest_modifier'] = nearest_modifier
        save_to[keys_prefix+'_average_modifier'] = average_modifier


def calc_result_modifier_v1(form: CandidateForm) -> float:
    state_value = form.state_modifier * ModifierV1AroundWeights.state
    district_value = form.district_modifier * ModifierV1AroundWeights.district

    metro_value = predict_rate(
        form.metro_count,
        form.metro_min_dest,
        form.metro_average_dest,
        form.metro_nearest_modifier,
        form.metro_average_modifier
    ) * ModifierV1AroundWeights.metro

    parking_value = predict_rate(
        form.parkings_count,
        form.parkings_min_dest,
        form.parkings_average_dest,
        form.parkings_nearest_modifier,
        form.parkings_average_modifier,
    ) * ModifierV1AroundWeights.parkings

    houses_value = predict_rate(
        form.houses_count,
        form.houses_min_dest,
        form.houses_average_dest,
        form.houses_nearest_modifier,
        form.houses_average_modifier,
    ) * ModifierV1AroundWeights.houses

    libraries_value = predict_rate(
        form.libraries_count,
        form.libraries_min_dest,
        form.libraries_average_dest,
        form.libraries_nearest_modifier,
        form.libraries_average_modifier,
    ) * ModifierV1AroundWeights.libraries

    culture_houses_value = calc_rate_only_by_dest(
        form.culture_houses_count,
        form.culture_houses_min_dest,
        form.culture_houses_average_dest
    ) * ModifierV1AroundWeights.culture_houses

    postamats_value = predict_rate(
        form.postamats_count,
        form.postamats_min_dest,
        form.postamats_average_dest,
        form.postamats_nearest_modifier,
        form.postamats_average_modifier,
    ) * ModifierV1AroundWeights.postamats

    bus_stations_value = predict_rate(
        form.bus_stations_count,
        form.bus_stations_min_dest,
        form.bus_stations_average_dest,
        form.bus_stations_nearest_modifier,
        form.bus_stations_average_modifier,
    ) * ModifierV1AroundWeights.bus_stations

    sports_value = predict_rate(
        form.sports_count,
        form.sports_min_dest,
        form.sports_average_dest,
        form.sports_nearest_modifier,
        form.sports_average_modifier,
    ) * ModifierV1AroundWeights.sports

    mfc_value = predict_rate(
        form.mfc_count,
        form.mfc_min_dest,
        form.mfc_average_dest,
        form.mfc_nearest_modifier,
        form.mfc_average_modifier,
    ) * ModifierV1AroundWeights.mfc

    nto_paper_value = calc_rate_only_by_dest(
        form.nto_paper_count,
        form.nto_paper_min_dest,
        form.nto_paper_average_dest
    ) * ModifierV1AroundWeights.nto_paper

    nto_non_paper_value = calc_rate_only_by_dest(
        form.nto_non_paper_count,
        form.nto_non_paper_min_dest,
        form.nto_non_paper_average_dest
    ) * ModifierV1AroundWeights.nto_non_paper

    return sum([
        state_value,
        district_value,
        metro_value,
        postamats_value,
        parking_value,
        bus_stations_value,
        culture_houses_value,
        libraries_value,
        mfc_value,
        sports_value,
        nto_paper_value,
        nto_non_paper_value,
        houses_value,
    ]) / MODIFIER_V1_NORMALIZE


def calc_result_modifier_v2(form: CandidateForm) -> float:
    return random.random()


def calc_rate_only_by_dest(count: int, min_dest: float, average_dest: float) -> float:
    dist_weight_average = (((count + 1) // 2) * min_dest + (count - 1) * average_dest) \
                     / \
                     (count - 1 + (count + 1) // 2)
    return MAX_EXPECTED_RADIUS / dist_weight_average
