from data_processing import shop_products_processing
from models import models

@staticmethod
def get_ton_profit(account: dict, user_streamer: dict) -> float:
    return float(user_streamer[models.streamers.profit_ton.name])

@staticmethod
def get_borv_profit(account: dict, user_streamer: dict) -> float:
    result = float(user_streamer[models.streamers.profit_borv.name])
    if user_streamer[models.streamers_availability.reason.name] != "free" or user_streamer[models.streamers_availability.is_available.name] != True:
        return result
    result += shop_products_processing.get_clothes_bonus(float(account[models.accounts.level_clothes.name]), user_streamer[models.streamers_availability.reason.name])
    result += shop_products_processing.get_apartment_bonus(float(account[models.accounts.level_apartment.name]), user_streamer[models.streamers_availability.reason.name])
    return result

