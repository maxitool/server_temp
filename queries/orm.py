from decimal import Decimal
import string
from turtle import mode
from queries.core import QueriesCore
from database import async_sqlalchemy_engine
from sqlalchemy import text
import ast
import re
from models.models import *
from datetime import datetime, timedelta, timezone
from data_processing import streamers_processing, streams_processing, shop_products_processing
from data_processing.shop_products_processing import ShopProductsTypes
from ton_payments.wallet_manager import WalletManager
from typing import Final

class QueriesORM:
    
    class TRANSITION_DIRACTIONS:
        IN_PROJECT_WALLET: Final[str] = "in_project_wallet"
        IN_USER_WALLET: Final[str] = "in_user_wallet"
        OUT_PROJECT_WALLET: Final[str] = "out_project_wallet"
        OUT_USER_WALLET: Final[str] = "out_user_wallet"
    
    # orm shells of queries with accounts table
    
    @staticmethod
    async def get_account_information_with_wallet_data_orm(telegram_id: int):
        account = await QueriesORM.get_account_information_orm(telegram_id)
        if not account:
            return None
        wallet = await QueriesORM.get_wallet_orm(telegram_id)
        if wallet:
            account[0][wallets.public_addr.name] = wallet[0][wallets.public_addr.name]
            ton_balance = await WalletManager.get_wallet_balance(telegram_id, wallet[0][wallets.mnemonics.name])
            if not ton_balance is None:
                account[0]["number_ton"] = ton_balance
            return account
        address, enc_mnemonics = await WalletManager.create_wallet(telegram_id)
        if not address or not enc_mnemonics:
            return account
        wallet = await QueriesORM.add_wallet_orm(telegram_id, address.to_string(True, True, True), enc_mnemonics.decode('utf-8'))
        if not wallet:
            return None
        account[0][wallets.public_addr.name] = wallet[0][wallets.public_addr.name]
        ton_balance = await WalletManager.get_wallet_balance(telegram_id, wallet[0][wallets.mnemonics.name])
        if ton_balance:
            account[0]["number_ton"] = ton_balance
        return account

    @staticmethod
    async def get_account_information_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_account_information_query(telegram_id)))
            res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_account_information_with_rewrite_orm(telegram_id: int, telegram_username: str, telegram_firstname: str, language: str, telegram_id_group_owner: int):
         account = await QueriesORM.get_account_information_with_wallet_data_orm(telegram_id)
         if not account is None:
             return account
         async with async_sqlalchemy_engine.connect() as conn:
             try:
                 res_query = await conn.execute(text(QueriesCore.add_new_account_query(telegram_id, telegram_username, telegram_firstname, language)))
                 await conn.commit()
             except Exception as e:
                 print("Error can't add account in get_account_information_with_rewrite_orm: " + str(e))
                 return None
         if telegram_id_group_owner > 0:
             group = await QueriesORM.get_group_orm(telegram_id_group_owner)
             if not group is None:
                 await QueriesORM.add_group_member_orm(telegram_id, group[0][groups.id_group.name])
         return await QueriesORM.get_account_information_with_wallet_data_orm(telegram_id)

    @staticmethod
    async def change_telegram_user_data(telegram_id: int, telegram_username: string, telegram_firstname):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.change_telegram_username_query(telegram_id, telegram_username, telegram_firstname)))
                await conn.commit()
            except Exception:
                return None
        return True

    @staticmethod
    async def __add_borv_orm(telegram_id: int, number_borv: float):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.add_number_borv_query(telegram_id, number_borv)))
                await conn.commit()
            except Exception as e:
                # add err
                print("Can't add borv to account " + str(telegram_id) + ": " + str(e))
                return None
        return True

    @staticmethod
    async def __change_level_clothes_orm(telegram_id: int, level: int):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.update_level_clothes_query(telegram_id, level)))
                await conn.commit()
            except Exception as e:
                # add err
                print("Can't change_level_clothes " + str(telegram_id) + ": " + str(e))
                return None
        return True

    @staticmethod
    async def __change_level_apartment_orm(telegram_id: int, level: int):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.update_level_apartment_query(telegram_id, level)))
                await conn.commit()
            except Exception as e:
                # add err
                print("Can't change_level_apartment " + str(telegram_id) + ": " + str(e))
                return None
        return True

    @staticmethod
    async def get_wearing_shop_products_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_wearing_shop_products_query(telegram_id)))
            res_list = res_query.all()
        if not res_list:
            answer = await QueriesORM.__add_wearing_shop_products_orm(telegram_id)
            if not answer:
                return None
            async with async_sqlalchemy_engine.connect() as conn:
                res_query = await conn.execute(text(QueriesCore.get_wearing_shop_products_query(telegram_id)))
                res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def __add_wearing_shop_products_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.add_wearing_shop_products_query(telegram_id)))
                await conn.commit()
            except Exception as e:
                print("Can't add_wearing_shop_products " + str(telegram_id) + ": " + str(e))
                return None
        return True

    @staticmethod
    async def change_wearing_shop_product_orm(telegram_id: int, id_product: int):
        product = await QueriesORM.get_shop_product_orm(id_product)
        if product is None:
            return None
        is_having = await QueriesCore.get_shop_product_having_query(telegram_id, id_product)
        if is_having is None:
            return None
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                match product[0][shop_products.product_type.name]:
                    case ShopProductsTypes.WATCH:
                        await conn.execute(text(QueriesCore.change_id_watch_query(telegram_id, id_product)))
                    case ShopProductsTypes.APARTMENT:
                        await conn.execute(text(QueriesCore.change_id_apartment_query(telegram_id, id_product)))
                    case ShopProductsTypes.CLOTHES:
                        await conn.execute(text(QueriesCore.change_id_clothes_query(telegram_id, id_product)))
                    case ShopProductsTypes.CLOTHES_HAT:
                        await conn.execute(text(QueriesCore.change_id_clothes_query(telegram_id, id_product)))
                    case _:
                        return None
                await conn.commit()
            except Exception as e:
                return None
        return True


    # orm shells of queries with wallets table

    @staticmethod
    async def get_wallet_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_wallet_query(telegram_id)))
        res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_ton_balance_orm(telegram_id: int):
        wallet = await QueriesORM.get_wallet_orm(telegram_id)
        if wallet is None:
            return None
        return await WalletManager.get_wallet_balance(telegram_id, wallet[0][wallets.mnemonics.name])

    @staticmethod
    async def add_wallet_orm(telegram_id: int, public_addr: str, enc_privkey: str):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.add_wallet_query(telegram_id, public_addr, enc_privkey)))
                await conn.commit()
            except Exception as e:
                print("Can't add_wallet " + str(telegram_id) + ": " + str(e))
                return None
        return await QueriesORM.get_wallet_orm(telegram_id)

    @staticmethod
    async def payout_orm(telegram_id: int, to_addr: str, amount_ton: float):
        wallet = await QueriesORM.get_wallet_orm(telegram_id)
        if wallet is None:
            return None
        ton_balance = await QueriesORM.get_ton_balance_orm(telegram_id)
        if ton_balance is None or ton_balance < amount_ton:
            return None
        answer = await QueriesORM.__transfer_orm(
            wallet=wallet,
            from_project_wallet=False,
            to_addr=to_addr,
            amount_ton=amount_ton,
            diraction=QueriesORM.TRANSITION_DIRACTIONS.OUT_USER_WALLET
        )
        return answer

    @staticmethod
    async def __transfer_orm(wallet: wallets, from_project_wallet: bool, to_addr: str, amount_ton: float, diraction: str, id_transaction: int = -1):
        if wallet is None:
            return None
        # create transaction
        if id_transaction <= 0:
            new_id_transaction = await QueriesORM.__create_transaction_orm(wallet[0][wallets.telegram_id.name], amount_ton, diraction)
        else:
            new_id_transaction = id_transaction
        if new_id_transaction is None:
            return None
        # send ton to wallet
        if from_project_wallet == True:
            tx_hash, lt = await WalletManager.transfer_from_project_wallet(wallet, Decimal(amount_ton))
        else:
            tx_hash, lt = await WalletManager.transfer(wallet, to_addr, Decimal(amount_ton))
        # if the transfer was successful apply transaction
        if not tx_hash is None and not lt is None:
            await QueriesORM.__apply_transaction_orm(new_id_transaction, lt, tx_hash)
            return True
        # if first call this func try deploy wallet
        if id_transaction <= 0:
            answer = await WalletManager.deploy_wallet(wallet[0][wallets.telegram_id.name], wallet[0][wallets.mnemonics.name])
            if not answer is None:
                return await QueriesORM.__transfer_orm(
                    wallet=wallet,
                    from_project_wallet=from_project_wallet,
                    to_addr=to_addr,
                    amount_ton=amount_ton,
                    diraction=diraction,
                    id_transaction=new_id_transaction
                    )
        await QueriesORM.__fail_transaction_orm(new_id_transaction)
        return None

    @staticmethod
    async def __create_transaction_orm(telegram_id: int, amount_ton: float, diraction: str):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.create_transaction_query(telegram_id, amount_ton, diraction)))
                await conn.commit()
            except Exception as e:
                print("Can't create transaction" + ": " + str(e))
                return None
        res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res[0][transactions.id_transaction.name]

    @staticmethod
    async def __apply_transaction_orm(id_transaction: int, lt: int, tx_hash):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.apply_transaction_query(id_transaction, lt, tx_hash)))
                await conn.commit()
            except Exception as e:
                print("Can't apply transaction " + str(id_transaction) + ": " + str(e))
                return None
        return True

    @staticmethod
    async def __fail_transaction_orm(id_transaction: int):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.fail_transaction_query(id_transaction)))
                await conn.commit()
            except Exception as e:
                print("Can't fail transaction " + str(id_transaction) + ": " + str(e))
                return None
        return True


    # orm shells of queries with groups table

    @staticmethod
    async def create_group_orm(telegram_id: int, name_group: str):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.create_group_query(telegram_id, name_group)))
                await conn.commit()
            except Exception as e:
                # maybe unique constraint of name is violated
                return None
        return await QueriesORM.get_group_orm(telegram_id)

    @staticmethod
    async def add_group_member_orm(telegram_id: int, id_group: int):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.add_group_member_query(telegram_id, id_group)))
                await conn.commit()
            except Exception as e:
                return None
        return True

    @staticmethod
    async def get_group_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_group_query(telegram_id)))
        res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_group_with_count_members_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_group_with_count_members_query(telegram_id)))
        res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_group_by_member_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_group_by_member_query(telegram_id)))
        res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_group_by_name_orm(name_group: str):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_group_by_name_query(name_group)))
        res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res


    # orm shells of queries with streams table

    @staticmethod
    async def get_user_streams_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_user_streams_query(telegram_id)))
            res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_user_stream_orm(telegram_id: int, id_stream: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_user_stream_query(telegram_id, id_stream)))
            res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_stream_stage_bonus(telegram_id: int, id_stream: int):
        stream = await QueriesORM.get_user_stream_orm(telegram_id, id_stream)
        if stream is None:
            return None
        if datetime.now(timezone.utc) >= stream[0][streams.date_end.name].replace(tzinfo=timezone.utc):
            return await QueriesORM.completing_user_stream_orm(telegram_id, id_stream)
        stream_time_interval = stream[0][streams.date_end.name] - stream[0][streams.date_start.name]
        now_time_interval = stream[0][streams.date_end.name].replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)
        seconds_in_stage = stream_time_interval.total_seconds() / stream[0][streams.stages_number.name]
        remainder = int(seconds_in_stage % stream[0][streams.stages_number.name])
        seconds_in_stage = int(seconds_in_stage) + remainder
        remaining_stages = int(now_time_interval.total_seconds() / seconds_in_stage)
        current_stage = stream[0][streams.stages_number.name] - remaining_stages - 1
        if current_stage <= stream[0][streams.current_stage.name]:
            return stream
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                res_query = await conn.execute(text(QueriesCore.change_current_stage_user_stream_query(id_stream, current_stage)))
                await conn.commit()
            except Exception as e:
                return None
        add_number_borv = float(stream[0][streams.profit_borv.name]) / float(stream[0][streams.stages_number.name]) * (current_stage - stream[0][streams.current_stage.name])
        if add_number_borv > 0:
            # Add logging?
            await QueriesORM.__add_borv_orm(telegram_id, add_number_borv)
        add_number_ton = float(stream[0][streams.profit_ton.name]) / float(stream[0][streams.stages_number.name]) * (current_stage - stream[0][streams.current_stage.name])
        if add_number_ton > 0:
            wallet = await QueriesORM.get_wallet_orm(telegram_id)
            if wallet:
                # Add logging?
                await QueriesORM.__transfer_orm(
                    wallet=wallet,
                    from_project_wallet=True,
                    to_addr=None,
                    amount_ton=add_number_ton,
                    diraction=QueriesORM.TRANSITION_DIRACTIONS.OUT_PROJECT_WALLET)
        return await QueriesORM.get_user_stream_orm(telegram_id, id_stream)

    @staticmethod
    async def completing_user_stream_orm(telegram_id: int, id_stream: int):
        stream = await QueriesORM.get_user_stream_orm(telegram_id, id_stream)
        if stream[0][streams.date_end.name].replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
            return stream
        account = await QueriesORM.get_account_information_orm(telegram_id)
        if account is None:
            return None
        user_streamer = await QueriesORM.get_user_streamers_orm(telegram_id, [stream[0][streams.id_streamer.name]])
        if user_streamer is None:
            return None
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                await conn.execute(text(QueriesCore.remove_user_stream_query(id_stream)))
                await conn.commit()
            except Exception as e:
                print("Error in completing_user_stream_orm: " + str(e))
                return None
        current_number_stream = int(user_streamer[0][streamers_availability.current_number_streams.name]) - 1
        if current_number_stream < 0:
            current_number_stream = 0
        is_availability_changed = await QueriesORM.__change_user_streamer_availability_orm(account[0], user_streamer[0], current_number_stream)
        if is_availability_changed is None:
            # add err
            print("add err")
        add_number_borv = float(stream[0][streams.profit_borv.name]) / float(stream[0][streams.stages_number.name]) * (stream[0][streams.stages_number.name] - stream[0][streams.current_stage.name])
        if add_number_borv > 0:
            # Add logging?
            await QueriesORM.__add_borv_orm(telegram_id, add_number_borv)
        add_number_ton = float(stream[0][streams.profit_ton.name]) / float(stream[0][streams.stages_number.name]) * (stream[0][streams.stages_number.name] - stream[0][streams.current_stage.name])
        if add_number_ton > 0:
            wallet = await QueriesORM.get_wallet_orm(telegram_id)
            if wallet:
                # Add logging?
                await QueriesORM.__transfer_orm(
                    wallet=wallet,
                    from_project_wallet=True,
                    to_addr=None,
                    amount_ton=add_number_ton,
                    diraction=QueriesORM.TRANSITION_DIRACTIONS.OUT_PROJECT_WALLET)
        stream[0][streams.current_stage.name] = stream[0][streams.stages_number.name]
        return stream

    #With outputting unfinished streams
    @staticmethod
    async def completing_user_streams_orm(telegram_id: int):
        streams_data = await QueriesORM.get_user_streams_orm(telegram_id)
        if streams_data is None:
            return None
        result = []
        for stream_data in streams_data:
            subresult = await QueriesORM.completing_user_stream_orm(telegram_id, stream_data[streams.id_stream.name])
            if not subresult is None:
                result += subresult
        if len(result) <= 0:
            return None
        return result

    #Without outputting unfinished streams
    @staticmethod
    async def completing_user_streams_without_unfinished_streams_orm(telegram_id: int):
        streams_data = await QueriesORM.get_user_streams_orm(telegram_id)
        if streams_data is None:
            return None
        result = []
        for stream_data in streams_data:
            subresult = await QueriesORM.completing_user_stream_orm(telegram_id, stream_data[streams.id_stream.name])
            if not subresult is None and subresult[0][streams.current_stage.name] >= subresult[0][streams.stages_number.name]:
                result += subresult
        if len(result) <= 0:
            return None
        return result


    # orm shells of queries with streamers table

    @staticmethod
    async def get_streamers_orm():
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_streamers_query()))
            res_list = res_query.all()
            if not res_list:
                return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_streamer_orm(id_streamer: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_streamer_query(id_streamer)))
            res_list = res_query.all()
            if not res_list:
                return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_all_user_streamers_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_all_user_streamers_query(telegram_id)))
            res_list = res_query.all()
            if not res_list:
                return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_user_streamers_with_level_orm(telegram_id: int, level: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_user_streamers_with_level_query(telegram_id, level)))
            res_list = res_query.all()
            if not res_list:
                return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_user_streamers_orm(telegram_id: int, id_streamers: list):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_user_streamers_query(telegram_id, id_streamers)))
            res_list = res_query.all()
            if not res_list:
                return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    # return added stream data
    @staticmethod
    async def buy_user_streamer_orm(telegram_id: int, id_streamer: int):
        account = await QueriesORM.get_account_information_orm(telegram_id)
        if account is None or len(account) <= 0:
            return None
        user_streamer = await QueriesORM.get_user_streamers_orm(telegram_id, [id_streamer])
        if user_streamer is None or len(user_streamer) <= 0:
            return None
        wallet = await QueriesORM.get_wallet_orm(telegram_id)
        if wallet is None:
            return None
        ton_balance = await WalletManager.get_wallet_balance(telegram_id, wallet[0][wallets.mnemonics.name])
        if ton_balance is None or float(user_streamer[0][streamers.price_ton.name]) > ton_balance:
            return None
        current_number_streams = user_streamer[0][streamers_availability.current_number_streams.name]
        new_current_number_streams = current_number_streams + 1
        if new_current_number_streams >= user_streamer[0][streamers_availability.max_number_streams.name]:
            return None
        change_answer = await QueriesORM.__change_user_streamer_availability_orm(account[0], user_streamer[0], new_current_number_streams)
        if change_answer is None:
            return None
        answer = await QueriesORM.__transfer_orm(
            wallet=wallet,
            from_project_wallet=False,
            to_addr=WalletManager.PROJECT_WALLET_ADDR,
            amount_ton=float(user_streamer[0][streamers.price_ton.name]),
            diraction=QueriesORM.TRANSITION_DIRACTIONS.IN_PROJECT_WALLET)
        if answer is None:
            return None
        profit_ton = streams_processing.get_ton_profit(account[0], user_streamer[0])
        profit_borv = streams_processing.get_borv_profit(account[0], user_streamer[0])
        time_interval = user_streamer[0][streamers.time_interval.name]
        now = datetime.now(timezone.utc)
        date_end = now + time_interval
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                stream_data_query = await conn.execute(text(QueriesCore.add_user_stream_query(telegram_id, id_streamer, now, date_end, user_streamer[0][streamers.stages_number.name], profit_ton, profit_borv)))
                await conn.commit()
                id_stream = stream_data_query.scalar()
                if id_stream is None or type(id_stream) != int:
                    return None
            except Exception as e:
                # Add err
                print("Error can't add stream in buy_user_stream_orm: " + str(e))
                return None
        await QueriesORM.__add_to_history_number_streams_orm(telegram_id, id_streamer, 1)
        stream = await QueriesORM.get_user_stream_orm(telegram_id, id_stream)
        return stream


    # orm shells of queries with shop_products table

    @staticmethod
    async def get_shop_products_orm():
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_shop_products_query()))
            res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_shop_product_orm(id_product: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_shop_product_query(id_product)))
            res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_shop_products_with_having_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_shop_products_with_having_query(telegram_id)))
            res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_shop_product_with_having_orm(telegram_id: int, id_product: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_shop_product_with_having_query(telegram_id, id_product)))
            res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_all_shop_products_having_orm(telegram_id: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_all_shop_products_having_query(telegram_id)))
            res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def get_shop_product_having_orm(telegram_id: int, id_product: int):
        async with async_sqlalchemy_engine.connect() as conn:
            res_query = await conn.execute(text(QueriesCore.get_shop_product_having_query(telegram_id, id_product)))
            res_list = res_query.all()
        if not res_list:
            return None
        res = QueriesORM.__convert_select_query_result(res_query, res_list)
        return res

    @staticmethod
    async def buy_shop_product_orm(telegram_id: int, id_product: int):
        account = await QueriesORM.get_account_information_orm(telegram_id)
        if account in None:
            return None
        product = await QueriesORM.get_shop_product_with_having_orm(telegram_id, id_product)
        if product in None:
            return None
        wallet = await QueriesORM.get_wallet_orm(telegram_id)
        if wallet is None:
            return None
        ton_balance = await WalletManager.get_wallet_balance(telegram_id, wallet[0][wallets.mnemonics.name])
        if ton_balance is None:
            return None
        # check conditions for purchase
        if product[0][shop_products.level.name] <= 0 or product[0][QueriesCore.IS_BOUGHT] == True:
            return None
        streamers_data = None
        match product[0][shop_products.product_type.name]:
            case ShopProductsTypes.WATCH:
                if account[accounts.level_apartment.name] < product[0][shop_products.level.name] or account[accounts.level_clothes.name] < product[0][shop_products.level.name]:
                    return None
                streamers_data = await QueriesORM.get_user_streamers_with_level_orm(telegram_id, product[0][shop_products.level.name])
                if streamers_data is None:
                    return None
                for streamer_data in streamers_data:
                    if streamer_data[streamers_availability.current_number_streams.name] < streamer_data[streamers_availability.max_number_streams.name]:
                        return None
            case ShopProductsTypes.APARTMENT:
                if account[accounts.level_apartment.name] + 1 != product[0][shop_products.level.name]:
                    return None
            case ShopProductsTypes.CLOTHES, ShopProductsTypes.CLOTHES_HAT:
                if account[accounts.level_clothes.name] + 1 != product[0][shop_products.level.name]:
                    return None
            case _:
                print("Error in buy_shop_product_orm function, can't recognize type of shop product")
                return None
        price_borv = float(product[0][shop_products.price_borv.name])
        price_ton = float(product[0][shop_products.price_ton.name])
        if price_borv > float(account[0][accounts.number_borv.name]) or price_ton > ton_balance:
            return None
        # buy shop product
        if price_borv > 0:
            answer = await QueriesORM.__add_borv_orm(telegram_id, -price_borv)
            if answer is None:
                return None
        if price_ton > 0:
            answer = await QueriesORM.__transfer_orm(
                wallet=wallet,
                from_project_wallet=False,
                to_addr=WalletManager.PROJECT_WALLET_ADDR,
                amount_ton=float(price_ton),
                diraction=QueriesORM.TRANSITION_DIRACTIONS.IN_PROJECT_WALLET
            )
            if answer is None:
                if price_borv > 0:
                    await QueriesORM.__add_borv_orm(telegram_id, price_borv)
                return None
        answer = await QueriesORM.__add_shop_product_having_orm(telegram_id, id_product)
        if answer is None:
            return None
        # apply shop product
        match product[0][shop_products.product_type.name]:
            case ShopProductsTypes.WATCH:
                for streamer_data in streamers_data:
                    count_current_streams = streamer_data[streamers_availability.current_number_streams.name] - 1
                    if count_current_streams < 0:
                        count_current_streams = 0
                    await QueriesORM.__change_user_streamer_availability_orm(account[0], streamer_data, count_current_streams)
            case ShopProductsTypes.APARTMENT:
                await QueriesORM.__change_level_apartment_orm(telegram_id, product[0][shop_products.level.name])
            case ShopProductsTypes.CLOTHES:
                await QueriesORM.__change_level_clothes_orm(telegram_id, product[0][shop_products.level.name])
            case ShopProductsTypes.CLOTHES_HAT:
                await QueriesORM.__change_level_clothes_orm(telegram_id, product[0][shop_products.level.name])
        await QueriesORM.change_wearing_shop_product_orm(telegram_id, id_product)
        return product[0][shop_products.product_type.name]


    @staticmethod
    async def __add_shop_product_having_orm(telegram_id: int, id_product: int):
        async with async_sqlalchemy_engine.connect() as conn:
            try:
                await conn.execute(text(QueriesCore.add_shop_product_having_query(telegram_id, id_product)))
                await conn.commit()
            except Exception as e:
                # Add Err
                print("Error can't add shop product having in add_shop_product_having_orm: " + str(e))
                return None
        return True


    # orm shells of queries with streamers_availability table

    @staticmethod
    async def check_user_streamers_availability_orm(telegram_id: int):
        streamers = await QueriesORM.get_streamers_orm()
        if streamers is None:
            return None
        user_streamers = await QueriesORM.get_all_user_streamers_orm(telegram_id)
        if not user_streamers is None and len(user_streamers) == len(streamers):
            return True
        not_added_streamers = streamers.copy()
        # if don't have some streamers_availability, add them. Maybe not optimized
        if not user_streamers is None:
            not_added_streamers = []
            for streamer in streamers:
                is_found = False
                for user_streamer in user_streamers:
                    if user_streamer["id_streamer"] == streamer["id_streamer"]:
                        is_found = True
                        break
                if not is_found:
                    not_added_streamers.append(streamer)
        availability = streamers_processing.get_new_streamers_availability(not_added_streamers)
        try:
            async with async_sqlalchemy_engine.connect() as conn:
                query = QueriesCore.set_new_user_streamers_availability_query(telegram_id, availability.id_streamers, availability.is_available, availability.reasons, availability.reasons_info)
                if query == "":
                    return None
                await conn.execute(text(query))
                await conn.commit()
                return True
        except Exception as e:
            print("Error in set_new_user_streamers_availability_orm: " + str(e))
            return None

    @staticmethod
    async def __change_user_streamer_availability_orm(account: dict, user_streamer: dict, current_number_streams: int): # user_streamer - data from streamers and streamers_availability tables
        availability = streamers_processing.change_streamer_availability(account, user_streamer, current_number_streams)
        try:
            async with async_sqlalchemy_engine.connect() as conn:
                await conn.execute(text(QueriesCore.change_user_streamer_availability_query(
                    telegram_id=account["telegram_id"], id_streamer=user_streamer["id_streamer"], 
                    is_available=availability.is_available[0], current_number_streams=current_number_streams, 
                    reason=availability.reasons[0], reason_info=availability.reasons_info[0])))
                await conn.commit()
                return True
        except Exception as e:
            # add error
            print("Error in change_user_streamer_availability_orm: " + str(e))
            return None

    @staticmethod
    async def __add_to_history_number_streams_orm(telegram_id: int, id_streamer: int, add_number: int):
        try:
            async with async_sqlalchemy_engine.connect() as conn:
                await conn.execute(text(QueriesCore.add_to_history_number_streams_query(telegram_id, id_streamer, add_number)))
                await conn.commit()
                return True
        except Exception as e:
            print("Error in add_to_history_number_streams_orm: " + str(e))
            return None


    # convert func, no query
    @staticmethod
    def __convert_select_query_result(res_query, res_list):
        res_keys = res_query.keys()
        res = [dict(zip(res_keys, item)) for item in res_list]
        return res
