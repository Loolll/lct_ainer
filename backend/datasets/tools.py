

def fetch_district_name(value: str) -> str:
    value = value.strip().replace('ё', 'е').lower()
    return ' '.join([x for x in value.split() if x != 'район']).strip().lower()


def fetch_metro_name(value: str) -> str:
    value = value.strip().replace('ё', 'е').lower()
    return ' '.join([x for x in value.split() if x != 'метро']).strip()


def fetch_postamat_work_hours(value: str) -> float:
    # Returns average daily work hours
    def parse_interval(s: str) -> float:
        if 'выходной' in s.lower():
            return 0

        left, right = s.split('-', 1)
        left = left.split(':')
        right = right.split('(')[0].split(':')

        if len(left) > 1:
            left = int(left[0]) + int(left[1]) / 60
        else:
            left = int(left[0])

        if len(right) > 1:
            right = int(right[0]) + int(right[1].split()[0]) / 60
        else:
            right = int(right[0].split()[0])

        right = float(right)
        left = float(left)
        if right >= left:
            return right - left
        else:
            return right + 24 - left

    def parse_day_interval(value: str) -> int:
        # Returns count of days from the interval
        map = {
            'пн': 1,
            'пн-вт': 2,
            'пн-ср': 3,
            'пн-чт': 4,
            'пн-пт': 5,
            'пн-сб': 6,
            'вт': 1,
            'вт-ср': 2,
            'вт-чт': 3,
            'вт-пт': 4,
            'вт-сб': 5,
            'вт-вс': 6,
            'ср': 1,
            'ср-чт': 2,
            'ср-пт': 3,
            'ср-сб': 4,
            'ср-вс': 5,
            'чт': 1,
            'чт-пт': 2,
            'чт-сб': 3,
            'чт-вс': 4,
            'пт': 1,
            'пт-сб': 2,
            'пт-вс': 3,
            'сб': 1,
            'сб-вс': 2,
            'вс': 1
        }
        return map[value.strip().lower()]

    value = value.strip().lower().replace('ё', 'е')

    if 'ежедневно' in value:
        interval = value.split(':', 1)[1].strip()
        return parse_interval(interval)
    elif 'круглосуточно' in value:
        return 24
    elif '$' in value:
        cnt = 0
        total = 0
        for part in value.split('$'):
            part = part.strip()
            day_i, time_i = part.split(':', 1)
            days_count = parse_day_interval(day_i)
            hours_count = parse_interval(time_i)
            cnt += days_count
            total += days_count * hours_count
        return total / cnt
    else:
        raise RuntimeError
