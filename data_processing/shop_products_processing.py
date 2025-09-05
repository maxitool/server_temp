from typing import Final

class ShopProductsTypes:
    WATCH: Final[str] = "watch"
    APARTMENT: Final[str] = "apartment"
    CLOTHES: Final[str] = "clothes"
    CLOTHES_HAT: Final[str] = "clothes_hat"

@staticmethod
def get_clothes_bonus(level_clothes: int, reason: str):
    result = 0.0
    if reason != "free":
        return result
    match(level_clothes):
        case 2:
            result += 50
        case 3:
            result += 100
        case 4:
            result += 200
        case _:
            if level_clothes > 4:
                result += 200
    return result

@staticmethod
def get_apartment_bonus(level_apartment: int, reason: str):
    result = 0.0
    if reason != "free":
        return result
    match(level_apartment):
        case 2:
            result += 200
        case 3:
            result += 500
        case 4:
            result += 1000
        case _:
            if level_apartment > 4:
                result += 1000
    return result