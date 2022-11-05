import re


def calc_center(points) -> (float, float):
    x = [float(p[0]) for p in points]
    y = [float(p[1]) for p in points]
    return sum(x) / len(points), sum(y) / len(points)


def autocomplete(query: str, names: list[str], keys: list) -> set:
    resp = set()
    query = query.lower().strip()
    for name, key in zip(names, keys):
        if name.startswith(query):
            resp.add(key)
            continue

        name = name.lower().strip()
        tokens = re.split(r'[- _]', name)

        for t in tokens:
            if t.startswith(query):
                resp.add(key)
                break
    return resp
