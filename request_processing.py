from logging import ERROR
from typing_extensions import ReadOnly
from queries.core import shop_products
from queries.orm import QueriesORM
from models.models import *
from errors import Errors
import string
import ast
import re
import string
from typing import Final
import psutil
from data_processing.shop_products_processing import ShopProductsTypes

NAME_METHOD: Final[str] = "name_method"
TYPE_RESPONSE: Final[str] = "type_response"
DATA: Final[str] = "data"
ERROR_MESSAGE: Final[str] = "error_message"
ERROR_CODE: Final[str] = "error_code"

class RequestMethod:
    GET_ALL_INFO: Final[str] = "get_all_info"
    BUY_USER_STREAMER: Final[str] = "buy_user_streamer"
    CHECK_USER_STREAMS: Final[str] = "check_user_streams"
    CHECK_STAGE_USER_STREAM: Final[str] = "check_stage_user_stream"
    CHECK_CPU_LOAD: Final[str] = "check_cpu_load"
    BUY_SHOP_PRODUCT: Final[str] = "buy_shop_product"
    CHANGE_WEARING_SHOP_PRODUCT: Final[str] = "change_wearing_shop_product"
    CREATE_GROUP : Final[str] = "create_group"
    GET_GROUP: Final[str] = "get_group"
    GET_BALANCE: Final[str] = "get_balance"
    PAYOUT: Final[str] = "payout"

class ResponseType:
    ERROR: Final[str] = "error"
    ACCOUNT: Final[str] = "account"
    ADD_STREAM: Final[str] = "add_stream"
    CHANGE_STREAMERS: Final[str] = "change_streamers"
    CHANGE_STREAMS: Final[str] = "change_streams"
    STREAMS_IN_PROGRESS: Final[str] = "streams_in_progress"
    STREAMERS: Final[str] = "streamers"
    SHOP_PRODUCTS: Final[str] = "shop_products"
    WEARING_SHOP_PRODUCTS: Final[str] = "wearing_shop_products"
    CHANGE_SHOP_PRODUCT: Final[str] = "change_shop_product"
    CPU_LOAD: Final[str] = "cpu_load"
    SET_WALLET: Final[str] = "set_wallet"
    GROUP: Final[str] = "group"
    CHANGE_BALANCE: Final[str] = "change_balance"

class Language:
    ENGLISH: Final[str] = "English"
    RUSSIAN: Final[str] = "Russian"


class RequestProcessing:

    # View of data received: [{'name_method': '@name_method', 'data': '[{data}, {data}, ...]'}, 
    # {'name_method': '@name_method', 'data': '[{data}, {data}, ...]'}, ...] 
    # where {data} - {key: value}
    @staticmethod
    async def request_run(request: string):
        try:
            request_methods_and_data = ast.literal_eval(request)
        except Exception:
            return RequestProcessing.__error_construction(Errors.INCORRECT_STRUCTURE)
        if type(request_methods_and_data) != list:
            return RequestProcessing.__error_construction(Errors.INCORRECT_STRUCTURE)
        if len(request_methods_and_data) <= 0:
            return RequestProcessing.__error_construction(Errors.DID_NOT_RECEIVE_ANY_INFORMATION)
        response_list = []
        for request_method_and_data in request_methods_and_data:
            if type(request_method_and_data) != dict:
                return RequestProcessing.__error_construction(Errors.INCORRECT_STRUCTURE)
            response_list += await RequestProcessing.__method_run(request_method_and_data)
        response = str(response_list).replace("\'", "\"").replace("\"", "'")
        return response

    @staticmethod
    async def __method_run(request_method_and_data: dict):
        try:
            name_method = request_method_and_data[NAME_METHOD]
            if type(name_method) != str:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(NAME_METHOD))
            data = request_method_and_data[DATA]
            if type(data) != list:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(DATA))
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__method_run", str(e)))
        match name_method:
            case RequestMethod.GET_ALL_INFO:   
                return await RequestProcessing.__get_all_information(data)
            case RequestMethod.BUY_USER_STREAMER:
                return await RequestProcessing.__buy_user_streamer(data)
            case RequestMethod.CHECK_USER_STREAMS:
                return await RequestProcessing.__check_is_user_streams_completed()
            case RequestMethod.CHECK_STAGE_USER_STREAM:
                return await RequestProcessing.__check_current_stage_user_streams(data)
            case RequestMethod.CHECK_CPU_LOAD:
                return await RequestProcessing.__get_cpu_load()
            case RequestMethod.CREATE_WALLET:
                return await RequestProcessing.__create_wallet(data)
            case RequestMethod.BUY_SHOP_PRODUCT:
                return await RequestProcessing.__buy_shop_product(data)
            case RequestMethod.CHANGE_WEARING_SHOP_PRODUCT:
                return await RequestProcessing.__change_wearing_shop_product(data)
            case RequestMethod.CREATE_GROUP:
                return await RequestProcessing.__create_group(data)
            case RequestMethod.GET_GROUP:
                return await RequestProcessing.__get_group(data)
            case RequestMethod.GET_BALANCE:
                return await RequestProcessing.__get_balance(data)
            case RequestMethod.PAYOUT:
                return await RequestProcessing.__payout(data)
            case _: 
                return RequestProcessing.__error_construction(Errors.CANT_RECOGNIZE_METHOD(request_method_and_data[NAME_METHOD]))

    @staticmethod
    async def __get_cpu_load():
        try:
            cpu_percent = psutil.cpu_percent()
            if cpu_percent is None:
                return [{TYPE_RESPONSE: ResponseType.CPU_LOAD, DATA: [{"cpu_load": "-1"}] }]
            return [{TYPE_RESPONSE: ResponseType.CPU_LOAD, DATA: str(cpu_percent)}]
        except:
            return [{TYPE_RESPONSE: ResponseType.CPU_LOAD, DATA: str(-1)}]

    @staticmethod
    async def __get_all_information(request_data_list: list):
        # get necessary info from request
        try:
            telegram_id = request_data_list[0][accounts.telegram_id.name]
            if type(telegram_id) != int or telegram_id < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(accounts.telegram_id.name))
            telegram_username = request_data_list[0][accounts.telegram_username.name]
            telegram_firstname = request_data_list[0][accounts.telegram_firstname.name]
            language = request_data_list[0][accounts.language.name]
            if type(telegram_username) != str or type(telegram_firstname) != str or type(language) != str:
                return RequestProcessing.__error_construction(Errors.INCORRECT_DATA_TYPES)
            language = RequestProcessing.__recognize_language(language)
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__get_all_information", str(e)))
        try:
            telegram_id_owner_group = request_data_list[0]["telegram_id_owner_group"]
            if type(telegram_id_owner_group) != int:
                telegram_id_owner_group = 0
        except Exception as e:
            telegram_id_owner_group = 0
        if telegram_username == "":
            telegram_username = None
        if telegram_firstname == "":
            telegram_firstname = None
        response_list = []
        sub_response_list = []
        # get account info
        account_info = await QueriesORM.get_account_information_with_rewrite_orm(telegram_id, telegram_username, telegram_firstname, language, telegram_id_owner_group)
        if account_info is None:
            return RequestProcessing.__error_construction(Errors.DB_CANT_ADD_ROW_IN_TABLE(accounts.__name__))
        # change username, firstname, language if there are differences
        if account_info[0][accounts.telegram_username.name] != telegram_username or account_info[0][accounts.telegram_firstname.name] != telegram_firstname:
            await QueriesORM.change_telegram_user_data(telegram_id, telegram_username, telegram_firstname)
            account_info[0][accounts.telegram_username.name] = telegram_username
            account_info[0][accounts.telegram_firstname.name] = telegram_firstname
        response_list.append({TYPE_RESPONSE: ResponseType.ACCOUNT, DATA: str(account_info)})
        # get group if exist
        group_info = await QueriesORM.get_group_with_count_members_orm(telegram_id)
        if not group_info is None:
            response_list.append({TYPE_RESPONSE: ResponseType.GROUP, DATA: str(group_info)})
        # check if exist availability of user streamers, if not, then create
        await QueriesORM.check_user_streamers_availability_orm(telegram_id)
        # check if exist completed streams; Add info at the end
        completed_streams = await QueriesORM.completing_user_streams_without_unfinished_streams_orm(telegram_id)
        if not completed_streams is None:
            sub_response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_STREAMS, DATA: completed_streams})
        streamers = await QueriesORM.get_all_user_streamers_orm(telegram_id)
        if not streamers is None:
            response_list.append({TYPE_RESPONSE: ResponseType.STREAMERS, DATA: str(streamers)})
        streams_in_progress = await QueriesORM.get_user_streams_orm(telegram_id)
        if not streams_in_progress is None:
            response_list.append({TYPE_RESPONSE: ResponseType.STREAMS_IN_PROGRESS, DATA: str(streams_in_progress)})
        shop_products = await QueriesORM.get_shop_products_with_having_orm(telegram_id)
        if not shop_products is None:
            response_list.append({TYPE_RESPONSE: ResponseType.SHOP_PRODUCTS, DATA: str(shop_products)})
        wearing_products = await QueriesORM.get_wearing_shop_products_orm(telegram_id)
        if not wearing_products is None:
            response_list.append({TYPE_RESPONSE: ResponseType.WEARING_SHOP_PRODUCTS, DATA: str(wearing_products)})
        response_list += sub_response_list
        return response_list
    
    @staticmethod
    async def __get_balance(request_data_list: list):
        # get necessary info from request
        try:
            telegram_id = request_data_list[0][accounts.telegram_id.name]
            if type(telegram_id) != int or telegram_id < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(accounts.telegram_id.name))
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__get_balance", str(e)))
        response_list = []
        account_info = await QueriesORM.get_account_information_with_wallet_data_orm(telegram_id)
        if not account_info is None:
            response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_BALANCE, DATA: account_info})
        return response_list

    @staticmethod
    async def __payout(request_data_list: list):
        # get necessary info from request
        try:
            telegram_id = request_data_list[0][accounts.telegram_id.name]
            if type(telegram_id) != int or telegram_id < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(accounts.telegram_id.name))
            to_addr = request_data_list[0][wallets.public_addr.name]
            if type(to_addr) != str:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(wallets.public_addr.name))
            amount_ton = request_data_list[0]["number_ton"]
            if type(amount_ton) != float or amount_ton < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE("number_ton"))
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__payout", str(e)))
        response_list = []
        answer = await QueriesORM.payout_orm(telegram_id, to_addr, amount_ton)
        if answer is None:
            return response_list
        account_info = await QueriesORM.get_account_information_with_wallet_data_orm(telegram_id)
        if not account_info is None:
            response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_BALANCE, DATA: account_info})
        return response_list

    @staticmethod
    async def __buy_user_streamer(request_data_list: list):
        streamers_id_list = []
        try:
            telegram_id = request_data_list[0][accounts.telegram_id.name]
            if type(telegram_id) != int or telegram_id < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(accounts.telegram_id.name))
            if len(request_data_list) < 1:
                return RequestMethod.__error_construction(Errors.INCORRECT_STRUCTURE)
            for i in range(1, len(request_data_list)):
                id_streamer = request_data_list[i][streamers.id_streamer.name]
                if type(id_streamer) != int or id_streamer < 0:
                    return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(streamers.id_streamer.name))
                streamers_id_list.append(id_streamer)
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__buy_user_stream", str(e)))
        if len(streamers_id_list) <= 0:
            return RequestMethod.__error_construction(Errors.DID_NOT_RECEIVE_FIELD(streamers.id_streamer.name))
        response_list = []
        for streamer_id in streamers_id_list:
            added_stream = await QueriesORM.buy_user_streamer_orm(telegram_id, streamer_id)
            if not added_stream is None:
                response_list.append({TYPE_RESPONSE: ResponseType.ADD_STREAM, DATA: added_stream})
            changed_streamer = await QueriesORM.get_user_streamers_orm(telegram_id, [streamer_id])
            if not changed_streamer is None:
                response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_STREAMERS, DATA: changed_streamer})
        account_info = await QueriesORM.get_account_information_with_wallet_data_orm(telegram_id)
        if not account_info is None:
            response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_BALANCE, DATA: account_info})
        return response_list

    @staticmethod
    async def __check_is_user_streams_completed(request_data_list: list):
        try:
            telegram_id = request_data_list[0][accounts.telegram_id.name]
            if type(telegram_id) != int or telegram_id < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(accounts.telegram_id.name))
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__check_is_user_streams_completed", str(e)))
        response_list = []
        completed_streams = await QueriesORM.completing_user_streams_orm(telegram_id)
        if completed_streams is None:
            return response_list
        response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_STREAMS, DATA: completed_streams})
        account_info = await QueriesORM.get_account_information_with_wallet_data_orm(telegram_id)
        if not account_info is None:
            response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_BALANCE, DATA: account_info})
        return response_list

    @staticmethod
    async def __check_current_stage_user_streams(request_data_list: list):
        try:
            telegram_id = request_data_list[0][accounts.telegram_id.name]
            if type(telegram_id) != int or telegram_id < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(accounts.telegram_id.name))
            if len(request_data_list) < 1:
                return RequestMethod.__error_construction(Errors.INCORRECT_STRUCTURE)
            streams_id_list = []
            for i in range(1, len(request_data_list)):
                id_stream = request_data_list[i][streams.id_stream.name]
                if type(id_stream) != int or id_stream < 0:
                    return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(streams.id_stream.name))
                streams_id_list.append(id_stream)
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__check_is_user_streams_completed", str(e)))
        response_list = []
        change_streams = []
        for id_stream in streams_id_list:
            change_stream = await QueriesORM.get_stream_stage_bonus(telegram_id, id_stream)
            if not change_stream is None:
                change_streams += change_stream
        if len(change_streams) <= 0:
            return response_list
        response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_STREAMS, DATA: change_streams})
        account_info = await QueriesORM.get_account_information_with_wallet_data_orm(telegram_id)
        if not account_info is None:
            response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_BALANCE, DATA: account_info})
        return response_list

    @staticmethod
    async def __buy_shop_product(request_data_list: list):
        try:
            telegram_id = request_data_list[0][accounts.telegram_id.name]
            if type(telegram_id) != int or telegram_id < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(accounts.telegram_id.name))
            id_product = request_data_list[0][shop_products.id_product.name]
            if type(id_product) != int or id_product < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(shop_products.id_product.name))
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__buy_shop_product", str(e)))
        response_list = []
        answer_buy_product = await QueriesORM.buy_shop_product_orm(telegram_id, id_product)
        account_data =  await QueriesORM.get_account_information_orm(telegram_id)
        if not account_data is None:
            response_list.append({TYPE_RESPONSE: ResponseType.ACCOUNT, DATA: account_data})
        if answer_buy_product is None:
            return RequestProcessing.__error_construction(Errors.CANT_BUY_SHOP_PRODUCT)
        if answer_buy_product == ShopProductsTypes.WATCH:
            streamers_data =  await QueriesORM.get_all_user_streamers_orm(telegram_id)
            if not streamers_data is None:
                response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_STREAMERS, DATA: streamers_data})
        shop_product_data =  await QueriesORM.get_shop_product_with_having_orm(telegram_id, id_product)
        if not shop_product_data is None:
            response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_SHOP_PRODUCT, DATA: shop_product_data})
        wearing_products = await QueriesORM.get_wearing_shop_products_orm(telegram_id)
        if not wearing_products is None:
            response_list.append({TYPE_RESPONSE: ResponseType.WEARING_SHOP_PRODUCTS, DATA: str(wearing_products)})
        account_info = await QueriesORM.get_account_information_with_wallet_data_orm(telegram_id)
        if not account_info is None:
            response_list.append({TYPE_RESPONSE: ResponseType.CHANGE_BALANCE, DATA: account_info})
        return response_list

    @staticmethod
    async def __change_wearing_shop_product(request_data_list: list):
        try:
            telegram_id = request_data_list[0][accounts.telegram_id.name]
            if type(telegram_id) != int or telegram_id < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(accounts.telegram_id.name))
            id_product = request_data_list[0][shop_products.id_product.name]
            if type(id_product) != int or id_product < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(shop_products.id_product.name))
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__change_wearing_shop_product", str(e)))
        await QueriesORM.change_wearing_shop_product_orm(telegram_id, id_product)
        return []

    @staticmethod
    async def __create_group(request_data_list: list):
        try:
            telegram_id = request_data_list[0][accounts.telegram_id.name]
            if type(telegram_id) != int or telegram_id < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(accounts.telegram_id.name))
            name = request_data_list[0][groups.name.name]
            if type(name) != str:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(groups.name.name))
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__create_group", str(e)))
        response_list = []
        account = await QueriesORM.get_account_information_orm(telegram_id)
        if account is None:
            return RequestProcessing.__error_construction(Errors.CANT_GET_ACCOUNT)
        group_info = await QueriesORM.create_group_orm(telegram_id, name)
        if group_info is None:
            return RequestProcessing.__error_construction(Errors.THAT_NAME_OF_GROUP_ALREADY_EXIST)
        response_list.append({TYPE_RESPONSE: ResponseType.GROUP, DATA: str(group_info)})
        return response_list

    @staticmethod
    async def __get_group(request_data_list: list):
        try:
            telegram_id = request_data_list[0][accounts.telegram_id.name]
            if type(telegram_id) != int or telegram_id < 0:
                return RequestProcessing.__error_construction(Errors.INCORRECT_FIELD_VALUE(accounts.telegram_id.name))
        except Exception as e:
            return RequestProcessing.__error_construction(Errors.UNEXPECTED_ERROR_IN_METHOD("__create_group", str(e)))
        response_list = []
        group_info = await QueriesORM.get_group_with_count_members_orm(telegram_id)
        if group_info is None:
            return RequestProcessing.__error_construction(Errors.CANT_GET_GROUP)
        response_list.append({TYPE_RESPONSE: ResponseType.GROUP, DATA: str(group_info)})
        return response_list

    @staticmethod
    def __error_construction(error: list):
        return [{TYPE_RESPONSE: ResponseType.ERROR, DATA: [{ERROR_MESSAGE: error[0], ERROR_CODE: str(error[1])}]}]

    @staticmethod
    def __recognize_language(language: str):
        match language:
            case Language.ENGLISH:
                return Language.ENGLISH
        return Language.RUSSIAN