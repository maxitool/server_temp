from __future__ import annotations
import os
import base64
from decimal import Decimal
from enum import Enum
from typing import Final

import aiohttp
from cryptography.fernet import Fernet # type: ignore
from tonsdk.contract.wallet import WalletContract, Wallets, WalletVersionEnum # type: ignore
from tonsdk.utils import to_nano, bytes_to_b64str, Address
from tonsdk.contract.token.ft import JettonWallet
from tonsdk.crypto import mnemonic_new

from models.models import *
from database import async_sqlalchemy_engine
from sqlalchemy import text

class WalletManager:
    PROJECT_WALLET_ADDR: Final[str] = os.environ.get("PROJECT_WALLET_ADDR")
    __FERNET = Fernet(os.environ["KEY_ENC"])
    __TONCENTER_API: Final[str] = "https://toncenter.com/api/v2"  
    __TONCENTER_KEY: Final[str] = os.environ.get("TONCENTER_KEY")  
    __PROJECT_WALLET_MNEMONICS: Final[str] = os.environ.get("PROJECT_WALLET_MNEMONICS") 

    class SESSION_METHOD(Enum):
        POST = 1
        GET = 2

    @staticmethod
    async def __post(session_method: SESSION_METHOD, method: str, parameters: dict, **params):
        async with aiohttp.ClientSession() as session:
            url = f"{WalletManager.__TONCENTER_API}/{method}"
            if parameters and len(parameters) > 0:
                url += "?"
                for key in parameters:
                    url += key + "=" + parameters[key] + "&"
                url = url[:-1]
            headers = {"X-API-Key": WalletManager.__TONCENTER_KEY}
            json_result = None
            match(session_method):
                case WalletManager.SESSION_METHOD.GET:
                    async with session.get(url, json=params, timeout=20) as response:
                        json_result = await response.json()
                        if not json_result.get("ok") or json_result.get("ok") != True:
                            return None
                case WalletManager.SESSION_METHOD.POST:
                    async with session.post(url, json=params, timeout=20) as response:
                        json_result = await response.json()
                        if not json_result.get("ok") or json_result.get("ok") != True:
                            return None
            return json_result

    @staticmethod
    def __decode_mnemonics(enc_mnemonics: bytes):
        return WalletManager.__FERNET.decrypt(enc_mnemonics).decode('utf-8').split()

    @staticmethod
    async def get_wallet_balance(telegram_id: int, enc_mnemonics: bytes) -> float:
        _mnemonics, _pub_k, _priv_k, wallet = Wallets.from_mnemonics(
            mnemonics=WalletManager.__decode_mnemonics(enc_mnemonics),
            version=WalletVersionEnum.v4r2,
            workchain=0,
            account_id=telegram_id  
        )
        result = await WalletManager.__post(
            session_method=WalletManager.SESSION_METHOD.GET,
            method="getWalletInformation",
            parameters={"address":wallet.address.to_string(True,True,True)}
        )
        balance = result.get("result").get("balance")
        balance *= 1e-9
        return balance

    @staticmethod
    async def create_wallet(telegram_id: int):
        mnemonics = mnemonic_new()
        _mnemonics, _pub_k, _priv_k, wallet = Wallets.from_mnemonics(
            mnemonics=mnemonics,
            version=WalletVersionEnum.v4r2,
            workchain=0,
            account_id=telegram_id  
        )
        mnemonics = ""
        for word in _mnemonics:
            mnemonics += word + " "
        mnemonics = mnemonics[:-1]
        enc_mnemonics = WalletManager.__FERNET.encrypt(mnemonics.encode('utf-8'))
        return wallet.address, enc_mnemonics

    @staticmethod
    async def deploy_wallet(telegram_id: int, enc_mnemonics: bytes):
        _mnemonics, _pub_k, _priv_k, wallet = Wallets.from_mnemonics(
            mnemonics=WalletManager.__decode_mnemonics(enc_mnemonics),
            version=WalletVersionEnum.v4r2,
            workchain=0,
            account_id=telegram_id  
        )
        query = wallet.create_init_external_message()
        boc = bytes_to_b64str(query["message"].to_boc(False))
        result = await WalletManager.__post(
            session_method=WalletManager.SESSION_METHOD.POST,
            method="sendBoc", 
            parameters=None,
            boc=boc
        )
        if result is None:
            return None
        return True

    @staticmethod
    async def transfer(from_wallet: wallets, to_addr: str, amount_ton: Decimal):
        if not from_wallet or from_wallet[0][wallets.type.name] != "custodial" or not to_addr:
            return None, None
        mnemonics = WalletManager.__decode_mnemonics(from_wallet[0][wallets.mnemonics.name])
        _mnemonics, _pub_k, _priv_k, wallet = Wallets.from_mnemonics(
            mnemonics=mnemonics,
            version=WalletVersionEnum.v4r2,
            workchain=0,
            account_id=from_wallet[0][wallets.telegram_id.name] 
        )
        pub_addr = wallet.address.to_string(True,True,True)
        seqno = await WalletManager.__post(
            session_method=WalletManager.SESSION_METHOD.GET,
            method="getWalletInformation",
            parameters={"address":pub_addr}
        )
        if seqno is None:
            return None, None
        try:
            seqno = int(seqno.get("result").get("seqno"))
        except Exception as e:
            print("Can't get seqno for user with id " + str(from_wallet[0][wallets.telegram_id.name]))
            return None, None
        query = wallet.create_transfer_message(
            to_addr=to_addr,
            amount=to_nano(amount_ton, "ton"),
            seqno=seqno
        )
        boc = base64.b64encode(query["message"].to_boc(False)).decode()

        result = await WalletManager.__post(
            session_method=WalletManager.SESSION_METHOD.POST,
            method="sendBocReturnHash", 
            parameters=None, 
            boc=boc
        )
        if result is None:
            return None, None
        tx_hash = result.get("result").get("hash")
        lt = result.get("result").get("lt")
        return tx_hash, lt

    @staticmethod
    async def transfer_from_project_wallet(to_wallet: wallets, amount_ton: Decimal):
        if not to_wallet or to_wallet[0][wallets.type.name] != "custodial":
            return None, None
        project_mnemonics = WalletManager.__decode_mnemonics(WalletManager.__PROJECT_WALLET_MNEMONICS.encode('utf-8'))
        _mnemonics, _pub_k, _priv_k, wallet = Wallets.from_mnemonics(
            mnemonics=project_mnemonics,
            version=WalletVersionEnum.v4r2,
            workchain=0
        )
        project_seqno = await WalletManager.__post(
            session_method=WalletManager.SESSION_METHOD.GET,
            method="getWalletInformation",
            parameters={"address":WalletManager.PROJECT_WALLET_ADDR}
        )
        if project_seqno is None:
            return None, None
        try:
            project_seqno = int(project_seqno.get("result").get("seqno"))
        except Exception as e:
            print("Can't get project seqno! \n")
            return None, None
        query = wallet.create_transfer_message(
            to_addr=to_wallet[0][wallets.public_addr.name],
            amount=to_nano(amount_ton, "ton"),
            seqno=project_seqno
        )
        boc = base64.b64encode(query["message"].to_boc(False)).decode()
        result = await WalletManager.__post(
            session_method=WalletManager.SESSION_METHOD.POST,
            method="sendBocReturnHash", 
            parameters=None, 
            boc=boc
        )
        if result is None:
            return None, None
        tx_hash = result.get("result").get("hash")
        lt = result.get("result").get("lt")
        return tx_hash, lt