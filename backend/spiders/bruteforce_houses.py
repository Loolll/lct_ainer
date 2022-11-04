import asyncio
import asyncpg
from dadata import DadataAsync
import json
import logging

from models import District, State, Georaphy
from store.district import get_all_districts
# from store.state import get_all_states

logging.basicConfig(encoding='utf-8', level=logging.INFO)


DELTA_CORD = 0.002  # ~ 220m
RADIUS = 500
MAX_QUERY_GROUP = 7000


TOKENS = [
    "8c584245d6dc17a05f7dab49d399009e7df42cdb",
    "4d99bd21f4c10bb64a53264ea245347f9d79cdcf",
    "412d5fc686f98cf5bcad12238700fb3de4470535",
    "9c35e3a6bd9ca0632801261f61078ef8c43b47b6",
    "bca575408a3fe900ffab99f09e40c682b11a739a",
    "9af1206557c056085ee03457fee11ab93fce57bb",
    "94feb2b01e11cd148408728c97dc2e77b2072c46",
    "1fda11c8ebb3e55629f2592431bb3059c9458a33",
    "779630600ce2b5246587cf6ee888a6539242005c"
]

SECRETS = [
    "d192db6bfa1e01219576fad062ea86dc289af579",
    "e059e45f2aeef646cd41d3309e18b1a16fb27355",
    "b49316b19c38ba6aa982ec1c3e9a278f6a069a6c",
    "2717da552ecf742dba7fa01522e2fc26f526d02f",
    "939ee1769bee24d851a848271ecc6656a2d7d92d",
    "8482861b413bc95872036d4e1554127ea0f2cd86",
    "11f21a3b300bacb9797a8e3c8de62a3a302329c6",
    "36f8262700356f064b9f613d1e145163e901e4ef",
    "898e0cdd95e632d72d4fe99def0e8db238be4d9a"
]

banned = set()
rest = {x: MAX_QUERY_GROUP for x in TOKENS}
busy = {x: False for x in TOKENS}


async def bruteforce(pool: asyncpg.Pool):
    districts = await get_all_districts(pool)

    loop = asyncio.get_event_loop()

    total_iters = 0

    tasks = []
    queue = []

    for obj in districts:


        if obj.name.lower().strip() not in [
            'гольяново',
            'кунцево',
            'люблино',
            'метрогородок',
            'можайский',
            'очаково-матвеевское',
            'печатники',
            'раменки',
            'хорошево-мневники',
            'южное бутово',
            'ясенево',
            'строгино',
            'молжаниновский',
            'косино-ухтомский',
            'бирюлево восточное',
            'западное дегунино',
            'покровское-стрешнево',
            'выхино-жулебино',
            'тропарево-никулино',
            'москворечье-сабурово',
            'солнцево',
            'филевский парк',
            'крылатское',
            'ярославский',
            'внуково',
            'пресненский',
            'хамовники',
            'северный',
            'перово',
            'останкинский',
            'орехово-борисово южное',
            'нагатинский затон',
            'митино',
            'богородское',
            'вешняки',
            'головинский',
            'даниловский',
            'куркино',
            'лефортово',
            'марьино',
            'некрасовка',
            'академический',
            'алексеевский',
            'аэропорт',
            'бабушкинский',
            'басманный',
            'беговой',
            'бескудниковский',
            'бибирево',
            'бирюлево западное',
            'братеево',
            'бутырский',
            'войковский',
            'восточное дегунино',
            'восточный',
            'гагаринский',
            'дмитровский',
            'донской',
            'дорогомилово',
            'замоскворечье',
            'зюзино',
            'зябликово',
            'ивановское',
            'измайлово',
            'капотня',
            'коньково',
            'коптево',
            'котловка',
            'красносельский',
            'кузьминки',
            'левобережный',
            'лианозово',
            'ломоносовский',
            'лосиноостровский',
            'марфино',
            'марьина роща',
            'мещанский',
            'нагатино-садовники',
            'нагорный',
            'нижегородский',
            'ново-переделкино',
            'новогиреево',
            'новокосино',
            'обручевский',
            'обручевский',
            'орехово-борисово северное',
            'отрадное',
            'преображенское',
            'проспект вернадского',
            'рязанский',
            'свиблово',
            'северное бутово',
            'северное измайлово',
            'северное медведково',
            'северное тушино',
            'соколиная гора',
            'сокольники',
            'таганский',
            'тверской',
            'текстильщики',
            'теплый стан',
            'фили-давыдково',
            'ховрино',
            'хорошевский',
            'царицыно',
            'черемушки',
            'чертаново северное',
            'чертаново центральное',
            'чертаново южное',
            'щукино',
            'южное медведково',
            'южное тушино',
            'южнопортовый',
            'якиманка',
            'алтуфьевский',
            'арбат',
            'восточное измайлово',
            'ростокино',
            'савеловский',
            'тимирязевский',
        ]:  # SKIP already done
            lu, rb = get_square(obj)
            expected_iters = calc_expected(lu, rb)
            total_iters += expected_iters
            queue.append((expected_iters, obj))

    queue.sort(key=lambda x: x[0])

    logging.info(f"TOTAL ESTIMATION QUERIES {total_iters}")

    while len(queue):
        iters, obj = queue.pop()
        send = False

        for i, t in enumerate(TOKENS):
            if rest[t] > iters and not busy[t] and t not in banned:
                task = loop.create_task(dump_obj(obj, TOKENS[i], SECRETS[i]))
                tasks.append(task)
                rest[t] -= iters
                send = True
                break

        if not send:
            queue.append((iters, obj))

        await asyncio.sleep(1)

    await asyncio.wait(tasks)

    logging.info(f'DONE {len(tasks)} OBJECTS')


async def dump_obj(obj: District | State, token: str, secret: str):
    busy[token] = True

    lu, rb = get_square(obj)

    expected_iters = calc_expected(lu, rb)
    logging.info(f"Object: {obj.name}. Square: {lu}, {rb}. Token {token}. Expected iters ~{expected_iters}")

    dadata = DadataAsync(token, secret)

    for i, point in enumerate(coord_gen(lu, rb)):
        try:
            result = await dadata.geolocate(
                name="address",
                lat=point.lat, lon=point.lon,
                radius_meters=RADIUS
            )

            with open(f'/share/dump_{obj.name}.pson', 'a', encoding='utf-8') as file:
                file.write(json.dumps(result, ensure_ascii=False) + ',\n')
        except Exception as exc:
            if '429' in str(exc):
                logging.info("TO MANY REQUESTS!!!")
            elif '403' in str(exc):
                logging.info(f"BANNED TOKEN {token}")
                banned.add(token)
                raise RuntimeError()

            with open(f'/share/err_{obj.name}.pson', 'a') as file:
                file.write(f"{point.lat}, {point.lon}\n")

        if (not i % 25) or (i > expected_iters - 24):
            logging.info(f"DOWNLOADED {obj.name} ~{i/expected_iters:.2%}")

        await asyncio.sleep(0.35)

    busy[token] = False
    return


def coord_gen(lu_point: Georaphy, rb_point: Georaphy) -> Georaphy:
    sx, sy = lu_point.lon, lu_point.lat
    mx, my = rb_point.lon, rb_point.lat
    x, y = lu_point.lon, lu_point.lat
    while True:
        x += DELTA_CORD
        if x > mx:
            x = sx
            y -= DELTA_CORD
            if y < my:
                break
        yield Georaphy(lat=y, lon=x)


def get_square(obj: District | State) -> (Georaphy, Georaphy):
    poly = obj.polygon

    left_lon = 1000
    right_lon = 0
    top_lat = 0
    bottom_lat = 1000

    for point in poly:
        left_lon = min(left_lon, point.lon)
        right_lon = max(right_lon, point.lon)
        top_lat = max(top_lat, point.lat)
        bottom_lat = min(bottom_lat, point.lat)

    return Georaphy(lat=top_lat, lon=left_lon), Georaphy(lat=bottom_lat, lon=right_lon)


def calc_expected(lu: Georaphy, rb: Georaphy) -> float:
    return len(list(coord_gen(lu_point=lu, rb_point=rb)))
    # return ((rb.lon - lu.lon) * (lu.lat - rb.lat) / DELTA_CORD ** 2) + \
    #     (rb.lon - lu.lon) * 2 / DELTA_CORD  # Average movement
