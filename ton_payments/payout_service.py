from datetime import datetime, timedelta
from decimal import Decimal

import asyncio
import models
from sqlalchemy import update  
from database import async_sqlalchemy_engine
from models.models import *
from ton_payments.wallet_manager import WalletManager


async def send_payout(telegram_id: int, to_addr: str, fee_ton: Decimal) -> str:
    async with async_sqlalchemy_engine.connect() as conn:
        acc = await conn.get(accounts, telegram_id)
        amount = Decimal(acc.number_ton)
        if amount < fee_ton:
            print("Balance too small " + str(telegram_id))
            return None
        current_balance = amount - fee_ton
        if current_balance < 0:
            return None
        await conn.execute(
            update(accounts)
            .where(accounts.telegram_id == telegram_id)
            .values(number_ton=Decimal(current_balance))
        )
        await conn.commit()

    project_wallet = await _get_project_wallet(telegram_id)
    tx_hash = await transfer(project_wallet, to_addr, fee_ton)
    return tx_hash

async def _get_project_wallet(telegram_id: int) -> wallets:

    async with async_sqlalchemy_engine.connect() as conn:
        w = await conn.scalar(
            wallets.__table__.select().where(wallets.telegram_id == telegram_id)
        )
        if not w:
            print("Project wallet not found in DB")
            return None
        return w
