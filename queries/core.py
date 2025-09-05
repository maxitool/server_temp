import string
from tokenize import group

from models.models import *
from settings import double_precision
from sqlalchemy import DateTime
from typing import Final
from datetime import datetime, timedelta

class QueriesCore:
    
    # Some const names
    COUNT_FIELD: Final[str] = "count_field"
    IS_BOUGHT: Final[str] = "is_bought"
    COUNT_MEMBERS: Final[str] = "count_members"


    # core queries with accounts table
    accounts_table_name = accounts.__table__.schema + "." + accounts.__name__

    @staticmethod
    def get_account_information_query(telegram_id: int):
        return "SELECT * FROM " + QueriesCore.accounts_table_name + \
            " WHERE " + accounts.telegram_id.name + " = " + str(telegram_id) + " LIMIT 1"

    @staticmethod
    def get_number_borv_query(telegram_id: int):
        return "SELECT " + accounts.number_borv.name + " FROM " + QueriesCore.accounts_table_name + \
            " WHERE " + accounts.telegram_id.name + "=" + str(telegram_id) + " LIMIT 1"

    @staticmethod
    def add_new_account_query(telegram_id: int, telegram_username: string, telegram_firstname: string, language: string):
        return "INSERT INTO " + QueriesCore.accounts_table_name + " (" + accounts.telegram_username.name + ", " +  accounts.telegram_id.name + ", " + accounts.telegram_firstname.name + ", " + accounts.language.name \
            + ") VALUES ('" + telegram_username + "', " + str(telegram_id) + ", '" + telegram_firstname + ", '" + language + "'); " + \
            "INSERT INTO " + QueriesCore.wearing_shop_products_table_name + " (" + wearing_shop_products.telegram_id.name + ") VALUES (" + str(telegram_id) + ")"

    @staticmethod
    def add_number_borv_query(telegram_id: int, number_add_borv: float):
        return "UPDATE " + QueriesCore.accounts_table_name + " SET " + accounts.number_borv.name + "=" + accounts.number_borv.name + "+" \
            + double_precision.format(number_add_borv) + " WHERE " + accounts.telegram_id.name + " = " + str(telegram_id)

    @staticmethod
    def add_number_ton_query(telegram_id: int, number_add_ton: float):
        return "UPDATE " + QueriesCore.accounts_table_name + " SET " + accounts.number_ton.name + "=" + accounts.number_ton.name + "+" \
            + double_precision.format(number_add_ton) + " WHERE " + accounts.telegram_id.name + " = " + str(telegram_id)

    @staticmethod
    def add_number_borv_and_ton_query(telegram_id: int, number_add_borv: float, number_add_ton: float):
        return "UPDATE " + QueriesCore.accounts_table_name + " SET " + \
            accounts.number_borv.name + "=" + accounts.number_borv.name + "+" + double_precision.format(number_add_borv) + ", " + \
            accounts.number_ton.name + "=" + accounts.number_ton.name + "+" + double_precision.format(number_add_ton) + \
            " WHERE " + accounts.telegram_id.name + " = " + str(telegram_id)

    @staticmethod
    def set_wallet_query(telegram_id: int, wallet_public: str, wallet_private: str):
        return "UPDATE " + QueriesCore.accounts_table_name + " SET " + accounts.wallet_public.name + "='" + wallet_public + \
           "', " + accounts.wallet_private.name + "='" + wallet_private + "' WHERE " + accounts.telegram_id.name + " = " + str(telegram_id)

    @staticmethod
    def update_date_last_visit_query(telegram_id: int):
        return "UPDATE " + QueriesCore.accounts_table_name + " SET " + accounts.date_last_visit.name + " = " + "timezone('utc'::text, now())" + \
            " WHERE " + accounts.telegram_id.name + " = " + str(telegram_id)

    @staticmethod
    def change_telegram_username_and_firstname_query(telegram_id: int, telegram_username: string, telegram_firstname: string):
        return "UPDATE " + QueriesCore.accounts_table_name + " SET " + accounts.telegram_username.name + " = '" + telegram_username + \
            "', " + accounts.telegram_firstname.name + " = '" + telegram_firstname + \
            "' WHERE " + accounts.telegram_id.name + " = " + str(telegram_id)

    @staticmethod
    def update_level_clothes_query(telegram_id: int, level: int):
        return "UPDATE " + QueriesCore.accounts_table_name + " SET " + accounts.level_clothes.name + " = " + str(level) + \
            " WHERE " + accounts.telegram_id.name + " = " + str(telegram_id) + " LIMIT 1"

    @staticmethod
    def update_level_apartment_query(telegram_id: int, level: int):
        return "UPDATE " + QueriesCore.accounts_table_name + " SET " + accounts.level_apartment.name + " = " + str(level) + \
            " WHERE " + accounts.telegram_id.name + " = " + str(telegram_id) + " LIMIT 1"


    # core queries with wallets table
    wallets_table_name = wallets.__table__.schema + "." + wallets.__name__

    @staticmethod
    def get_wallet_query(telegram_id: int):
        return "SELECT * FROM " + QueriesCore.wallets_table_name + \
            " WHERE " + wallets.telegram_id.name + "=" + str(telegram_id) + " AND " + wallets.type.name + "='custodial' LIMIT 1"

    @staticmethod
    def add_wallet_query(telegram_id: int, public_addr: str, enc_mnemonics: str):
        return "INSERT INTO " + QueriesCore.wallets_table_name + \
            " (" + wallets.telegram_id.name + ", " + wallets.type.name + ", " + wallets.public_addr.name + ", " + wallets.mnemonics.name +\
            ") VALUES (" + str(telegram_id) + ", 'custodial', '" + public_addr + "', '" + enc_mnemonics + "')"


    # core queries with transactions table
    transactions_table_name = transactions.__table__.schema + "." + transactions.__name__

    @staticmethod
    def create_transaction_query(telegram_id: int, amount_ton: float, diraction: str):
        return "INSERT INTO " + QueriesCore.transactions_table_name + \
            " (" + transactions.telegram_id.name + ", " + transactions.amount_ton.name + ", " + transactions.status.name + ", " + transactions.diraction.name +\
            ") VALUES (" + str(telegram_id) + ", " + str(amount_ton) + ", 'pending', '" + diraction + "')" +\
            " RETURNING " + transactions.id_transaction.name

    @staticmethod
    def apply_transaction_query(id_transaction: int, lt: int, tx_hash: str):
        return "UPDATE " + QueriesCore.transactions_table_name + " SET " + \
            transactions.status.name + " = 'done', " + transactions.lt.name + " = " + str(lt) + \
            ", " + transactions.hash.name + " = " + tx_hash + \
            " WHERE " + transactions.id_transaction.name + " = " + str(id_transaction) + " LIMIT 1"

    @staticmethod
    def fail_transaction_query(id_transaction: int):
        return "UPDATE " + QueriesCore.transactions_table_name + " SET " + \
            transactions.status.name + " = 'failed'" + \
            " WHERE " + transactions.id_transaction.name + " = " + str(id_transaction) + " LIMIT 1"


    # core queries with groups table
    groups_table_name = groups.__table__.schema + "." + groups.__name__
    groups_members_table_name = groups_members.__table__.schema + "." + groups_members.__name__

    @staticmethod
    def create_group_query(telegram_id: int, name: str):
        return "INSERT INTO " + QueriesCore.groups_table_name + " (" + groups.name.name + ", " + groups.telegram_id.name + \
            ") VALUES ('" + name + "', " + str(telegram_id) + ")"

    @staticmethod
    def get_group_query(telegram_id: int):
        return "SELECT * FROM " + QueriesCore.groups_table_name + " WHERE " + groups.telegram_id.name + " = " + str(telegram_id) + " LIMIT 1"

    @staticmethod
    def get_group_with_count_members_query(telegram_id: int):
        return "SELECT owners.*, COUNT(members." + groups_members.telegram_id.name + ") AS " + QueriesCore.COUNT_MEMBERS + \
            " FROM " + QueriesCore.groups_members_table_name + " members INNER JOIN " +\
            "(SELECT * FROM " + QueriesCore.groups_table_name + " WHERE " + groups.telegram_id.name + " = " + str(telegram_id) + " LIMIT 1) " +\
            "owners ON owners." + groups.id_group.name + " = members." + groups_members.id_group.name +\
            " GROUP BY owners." + groups.id_group.name + ", owners." + groups.name_group.name + ", owners." + groups.telegram_id.name + " LIMIT 1"

    @staticmethod
    def get_group_by_name_query(name: str):
        return "SELECT * FROM " + QueriesCore.groups_table_name + " WHERE " + groups.name.name + " = '" + name + "' LIMIT 1"

    @staticmethod
    def add_group_member_query(telegram_id: int, id_group: int):
        return "INSERT INTO " + QueriesCore.groups_members_table_name + " (" + groups_members.telegram_id.name + ", " + groups_members.id_group.name + \
            ") VALUES (" + str(telegram_id) + ", " + str(id_group) + ")"

    @staticmethod
    def get_group_by_member_query(telegram_id: int):
        return "SELECT owners.* FROM " + QueriesCore.groups_table_name + " owners INNER JOIN " +\
            "(SELECT * FROM " + QueriesCore.groups_members_table_name + " WHERE " + groups.telegram_id.name + " = " + str(telegram_id) + " LIMIT 1) " +\
            "members ON owners." + groups.id_group.name + " = members." + groups_members.id_group.name + " LIMIT 1"

    # core queries with wearing_shop_products table
    wearing_shop_products_table_name = wearing_shop_products.__table__.schema + "." + wearing_shop_products.__name__

    @staticmethod
    def get_wearing_shop_products_query(telegram_id: int):
        return "SELECT * FROM " + QueriesCore.wearing_shop_products_table_name + \
            " WHERE " + wearing_shop_products.telegram_id.name + " = " + str(telegram_id) + " LIMIT 1"

    @staticmethod
    def add_wearing_shop_products_query(telegram_id: int):
        return "INSERT INTO " + QueriesCore.wearing_shop_products_table_name + " (" + wearing_shop_products.telegram_id.name + ") VALUES (" + str(telegram_id) + ")"

    @staticmethod
    def change_id_clothes_query(telegram_id: int, id_clothes: int):
        return "UPDATE " + QueriesCore.wearing_shop_products_table_name + " SET " + wearing_shop_products.id_clothes.name + " = " + str(id_clothes) \
             + " WHERE " + wearing_shop_products.telegram_id.name + " = " + str(telegram_id) + " LIMIT 1"

    @staticmethod
    def change_id_apartment_query(telegram_id: int, id_apartment: int):
        return "UPDATE " + QueriesCore.wearing_shop_products_table_name + " SET " + wearing_shop_products.id_apartment.name + " = " + str(id_apartment) \
             + " WHERE " + wearing_shop_products.telegram_id.name + " = " + str(telegram_id) + " LIMIT 1"

    @staticmethod
    def change_id_watch_query(telegram_id: int, id_watch: int):
        return "UPDATE " + QueriesCore.wearing_shop_products_table_name + " SET " + wearing_shop_products.id_watch.name + " = " + str(id_watch) \
             + " WHERE " + wearing_shop_products.telegram_id.name + " = " + str(telegram_id) + " LIMIT 1"

    # core queries with streamers table
    streamers_table_name = streamers.__table__.schema + "." + streamers.__name__

    @staticmethod
    def get_streamers_query():
        return "SELECT * FROM " + QueriesCore.streamers_table_name + " WHERE " + streamers.is_displayed.name + " = true " + \
            "ORDER BY " + streamers.level.name + ", " + streamers.price_ton.name
    
    @staticmethod
    def get_streamer_query(id_streamer: int):
        return "SELECT * FROM " + QueriesCore.streamers_table_name + " WHERE " + streamers.id_streamer.name + " = " + str(id_streamer) + " AND " + \
            streamers.is_displayed.name + " = true " + "LIMIT 1"

    @staticmethod
    def get_all_user_streamers_query(telegram_id: int):
        return "SELECT streamers.*, availability.* FROM " + \
            "(SELECT * FROM " + QueriesCore.streamers_availability_table_name + " WHERE " + streamers_availability.telegram_id.name + " = " + str(telegram_id) + ")" + \
            " availability INNER JOIN " + QueriesCore.streamers_table_name + " streamers ON availability." + streamers_availability.id_streamer.name + " = streamers." + streamers.id_streamer.name + \
            " WHERE " + streamers.is_displayed.name + " = true" + " ORDER BY streamers." + streamers.level.name + ", streamers." + streamers.price_ton.name
     
    @staticmethod
    def get_user_streamers_with_level_query(telegram_id: int, level: int):
        return "SELECT streamers.*, availability.* FROM " + \
            "(SELECT * FROM " + QueriesCore.streamers_availability_table_name + " WHERE " + streamers_availability.telegram_id.name + " = " + str(telegram_id) + ")" + \
            " availability INNER JOIN " + QueriesCore.streamers_table_name + " streamers ON availability." + streamers_availability.id_streamer.name + " = streamers." + streamers.id_streamer.name + \
            " WHERE streamers." + streamers.level.name + " = " + str(level) + " AND streamers." + streamers.is_displayed.name + " = true" + " ORDER BY streamers." + streamers.price_ton.name
    

    @staticmethod
    def get_user_streamers_query(telegram_id: int, id_streamers: list):
        query = "SELECT streamers.*, availability.* FROM (SELECT * FROM " + QueriesCore.streamers_availability_table_name + \
            " WHERE " + streamers_availability.telegram_id.name + " = " + str(telegram_id) + " AND ("
        for id_streamer in id_streamers:
            query += " " + streamers_availability.id_streamer.name + " = " + str(id_streamer) + " OR"
        query = query[:len(query) - 2]
        query += ")) availability INNER JOIN " + \
            QueriesCore.streamers_table_name + " streamers ON availability." + streamers_availability.id_streamer.name + \
            " = streamers." + streamers.id_streamer.name + \
            " WHERE " + streamers.is_displayed.name + " = true" + " ORDER BY streamers." + streamers.level.name + ", streamers." + streamers.price_ton.name
        return query

    # core queries with streams table
    streams_table_name = streams.__table__.schema + "." + streams.__name__

    @staticmethod
    def get_user_streams_query(telegram_id: int):
        return "SELECT * FROM " + QueriesCore.streams_table_name + " WHERE " + streams.telegram_id.name + " = " + str(telegram_id)

    @staticmethod
    def get_count_user_streams(telegram_id: int, id_streamer: int):
        return "SELECT COUNT(" + streams.id_stream.name + ") AS " + QueriesCore.COUNT_FIELD + " FROM " + QueriesCore.streams_table_name + " WHERE " + \
            streams.telegram_id.name + " = " + str(telegram_id) + " AND " + streams.id_streamer.name + " = " + str(id_streamer)

    @staticmethod
    def get_user_stream_query(telegram_id: int, id_stream: int):
        return "SELECT * FROM " + QueriesCore.streams_table_name + " WHERE " + streams.telegram_id.name + " = " + str(telegram_id) + \
            " AND " + streams.id_stream.name + " = " + str(id_stream) + " LIMIT 1"

    @staticmethod
    def add_user_stream_query(telegram_id: int, id_streamer: int, date_start: datetime, date_end: datetime, stages_number: int, profit_ton: float, profit_borv: float):
        return "INSERT INTO " + QueriesCore.streams_table_name + \
            " (" + streams.telegram_id.name + "," + streams.id_streamer.name + "," + streams.date_start.name + "," + streams.date_end.name + "," + streams.stages_number.name + "," + streams.profit_ton.name + "," + streams.profit_borv.name + \
            ") VALUES (" + str(telegram_id) + ", " + str(id_streamer) + ", '" + date_start.strftime('%Y-%m-%d %H:%M:%S.%f') + "', '" + date_end.strftime('%Y-%m-%d %H:%M:%S.%f') + "', " + str(stages_number) + ", " + str(profit_ton) + ", " + str(profit_borv) + ")" + \
            " RETURNING " + streams.id_stream.name
    
    @staticmethod
    def remove_user_stream_query(id_stream: int):
        return "DELETE FROM " + QueriesCore.streams_table_name + " WHERE " + streams.id_stream.name + " = " + str(id_stream)

    def change_current_stage_user_stream_query(id_stream: int, current_stage: int):
        return "UPDATE " + QueriesCore.streams_table_name + " SET " + streams.current_stage.name + " = " + str(current_stage) + \
            " WHERE " + streams.id_stream.name + " = " + str(id_stream)


    # core queries with shop products
    shop_products_table_name = shop_products.__table__.schema + "." + shop_products.__name__
    shop_products_having_table_name = shop_products_having.__table__.schema + "." + shop_products_having.__name__

    @staticmethod
    def get_shop_products_query():
        return "SELECT * FROM " + QueriesCore.shop_products_table_name + " ORDER BY " + shop_products.price_ton.name + ", " + shop_products.price_borv.name
    
    @staticmethod
    def get_shop_product_query(id_product: int):
        return "SELECT * FROM " + QueriesCore.shop_products_table_name + " WHERE " + shop_products.id_product.name + " = " + str(id_product) + " LIMIT 1"

    @staticmethod
    def get_shop_products_with_having_query(telegram_id: int):
        return "SELECT products.*, CASE WHEN have." + shop_products_having.id_having.name + " IS NOT NULL THEN TRUE ELSE FALSE END AS " + QueriesCore.IS_BOUGHT + \
            " FROM " + QueriesCore.shop_products_table_name + " products " + \
            "LEFT JOIN (SELECT * FROM " + QueriesCore.shop_products_having_table_name + " WHERE " + shop_products_having.telegram_id.name + " = "  + str(telegram_id) + \
            ") have ON products." + shop_products.id_product.name + " = have." + shop_products_having.id_product.name +\
            " ORDER BY products." + shop_products.price_ton.name + ", products." + shop_products.price_borv.name

    @staticmethod
    def get_shop_product_with_having_query(telegram_id: int, id_product: int):
        return "SELECT products.*, CASE WHEN have." + shop_products_having.id_having.name + " IS NOT NULL THEN TRUE ELSE FALSE END AS " + QueriesCore.IS_BOUGHT + \
            " FROM " + QueriesCore.shop_products_table_name + " products " + \
            "LEFT JOIN (SELECT * FROM " + QueriesCore.shop_products_having_table_name + " WHERE " + shop_products_having.telegram_id.name + " = "  + str(telegram_id) + \
            ") have ON products." + shop_products.id_product.name + " = have." + shop_products_having.id_product.name + \
            " WHERE products." + shop_products.id_product.name + " = " + str(id_product) + " LIMIT 1"

    @staticmethod
    def get_all_shop_products_having_query(telegram_id: int):
        return "SELECT * FROM " + QueriesCore.shop_products_having_table_name + " WHERE " + shop_products_having.telegram_id.name + " = " + str(telegram_id)

    @staticmethod
    def get_shop_product_having_query(telegram_id: int, id_product: int):
        return "SELECT * FROM " + QueriesCore.shop_products_having_table_name + " WHERE " + shop_products_having.telegram_id.name + " = " + str(telegram_id) + \
            " AND " + shop_products_having.id_product.name + " = " + str(id_product) + " LIMIT 1"

    @staticmethod
    def add_shop_product_having_query(telegram_id: int, id_product: int):
        return "INSERT INTO " + QueriesCore.shop_products_having_table_name + " (" + shop_products_having.telegram_id.name + ", " + shop_products_having.id_product.name + \
            ") VALUES (" + str(telegram_id) + ", " + str(id_product) + ")"

    # core queries with streamers_availability table
    streamers_availability_table_name = streamers_availability.__table__.schema + "." + streamers_availability.__name__

    @staticmethod
    def set_new_user_streamers_availability_query(telegram_id: int, id_streamers: list, is_available: list, reasons: list, reasons_info: list):
        query = "INSERT INTO " + QueriesCore.streamers_availability_table_name + \
            " (" + streamers_availability.telegram_id.name + ", " + streamers_availability.id_streamer.name + ", " + streamers_availability.is_available.name + ", " + streamers_availability.reason.name + ", " + streamers_availability.reason_info.name + \
            ") VALUES "
        try:
            for i in range(len(id_streamers)):
                query += "(" + str(telegram_id) + ", " + str(id_streamers[i]) + ", " + str(is_available[i]) + ", '" + reasons[i] + "', '" + reasons_info[i] + "'),"
            query = query[:len(query) - 1]
            return query
        except Exception as e:
            print("Error in set_user_streamers_availability_query: " + e)
            return ""

    @staticmethod
    def change_user_streamer_availability_query(telegram_id: int, id_streamer: int, is_available: bool, current_number_streams: int, reason: str, reason_info: str):
        return "UPDATE " + QueriesCore.streamers_availability_table_name + " SET " + \
            streamers_availability.is_available.name + " = " + str(is_available) + ", " + \
            streamers_availability.current_number_streams.name + " = " + str(current_number_streams) + ", " + \
            streamers_availability.reason.name + " = '" + reason + "', " + \
            streamers_availability.reason_info.name + " = '" + reason_info + "'" + \
            " WHERE " + streamers_availability.telegram_id.name + " = " + str(telegram_id) + " AND " + \
            streamers_availability.id_streamer.name + " = " + str(id_streamer)

    @staticmethod
    def add_to_history_number_streams_query(telegram_id: int, id_streamer: int, add_number_streams: int):
        return "UPDATE " + QueriesCore.streamers_availability_table_name + " SET " + \
            streamers_availability.history_number_streams.name + " = " + streamers_availability.history_number_streams.name + "+" + str(add_number_streams) + \
            " WHERE " + streamers_availability.telegram_id.name + " = " + str(telegram_id) + \
            " AND " + streamers_availability.id_streamer.name + " = " + str(id_streamer)
