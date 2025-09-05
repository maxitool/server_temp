from models import models

class StreamersAvailability:
    id_streamers: list = []
    is_available: list = []
    reasons: list = []
    reasons_info: list = []

    def __init__(self):
        self.id_streamers = []
        self.is_available = []
        self.reasons = []
        self.reasons_info = []

@staticmethod
def get_new_streamers_availability(streamers: list) -> StreamersAvailability:
    result = StreamersAvailability()
    for streamer in streamers:
        result.id_streamers.append(streamer[models.streamers.id_streamer.name])
        if streamer[models.streamers.is_open_for_purchase.name] == False:
            result.is_available.append(False)
            result.reasons.append("will_be_soon")
            result.reasons_info.append("")
            continue
        match streamer[models.streamers.level.name]:
            case 0:
                result.is_available.append(True)
                result.reasons.append("free")
                result.reasons_info.append("")
            case 1:
                result.is_available.append(True)
                result.reasons.append("available")
                result.reasons_info.append("")
            case 2:
                result.is_available.append(False)
                result.reasons.append("didnt_buy_clothes_and_apartments")
                result.reasons_info.append("2")
            case 3:
                result.is_available.append(False)
                result.reasons.append("didnt_buy_clothes_and_apartments")
                result.reasons_info.append("3")
            case 4:
                result.is_available.append(False)
                result.reasons.append("didnt_buy_clothes_and_apartments")
                result.reasons_info.append("4")
            case _:
                result.is_available.append(False)
                result.reasons.append("will_be_soon")
                result.reasons_info.append("")
    return result

@staticmethod
def change_streamer_availability(account: dict, user_streamer: dict, current_number_streams: int) -> StreamersAvailability: # user_streamer - data from streamers and streamers_availability tables
    result = StreamersAvailability()
    result.id_streamers.append(user_streamer[models.streamers.id_streamer.name])
    # if streamer not is_open_for_purchase
    if user_streamer[models.streamers.is_open_for_purchase.name] == False:
        result.is_available.append(False)
        result.reasons.append("will_be_soon")
        result.reasons_info.append("")
        return result
    # if the level is low
    if account[models.accounts.level_clothes.name] < user_streamer[models.streamers.level.name] or account[models.accounts.level_apartment.name] < user_streamer[models.streamers.level.name]:
        result.is_available.append(False)
        result.reasons_info.append(str(user_streamer[models.streamers.level.name]))
        if account[models.accounts.level_clothes.name] < user_streamer[models.streamers.level.name] and account[models.accounts.level_apartment.name] < user_streamer[models.streamers.level.name]:
            result.reasons.append("didnt_buy_clothes_and_apartments")
            return result
        if account[models.accounts.level_clothes.name] < user_streamer[models.streamers.level.name]:
            result.reasons.append("didnt_buy_clothes")
            return result
        result.reasons.append("didnt_buy_apartments")
        return result
    # if new current_number_streams more or equal than max_number_streams
    if current_number_streams >= user_streamer["max_number_streams"]:
        result.is_available.append(False)
        result.reasons.append("max_streams")
        result.reasons_info.append("")
        return result
    # if streamer is free
    if user_streamer["level"] <= 0:
        result.is_available.append(True)
        result.reasons.append("free")
        result.reasons_info.append("")
        return result
    result.is_available.append(False)
    result.reasons.append("need_buy_pass")
    result.reasons_info.append(str(user_streamer["level"]))
    return result

@staticmethod
def unlock_level_streamer_availability(streamers: list, level: int) -> StreamersAvailability:
    result = StreamersAvailability()
    for streamer in streamers:
        if streamer[models.streamers.level.name] != level:
            continue
        result.id_streamers.append(streamer["id_streamer"])
        result.is_available.append(True)
        result.reasons_info.append("")
        if level <= 0:
            result.reasons.append("free")
            continue
        result.reasons.append("available")
        
    return result