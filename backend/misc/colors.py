from .consts import COLOR_LOWER, COLOR_HIGH


def get_color_grad(rate: float) -> list:
    if rate > 1:
        raise RuntimeError

    L = COLOR_LOWER
    H = COLOR_HIGH

    return [
        int(min(L[i], H[i]) + (max(L[i], H[i]) - min(L[i], H[i])) * rate)
        for i in range(3)
    ]
