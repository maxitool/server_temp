from email.policy import default
from database import Base
from sqlalchemy import BOOLEAN, Enum, LargeBinary, Boolean, Column, Integer, Sequence, ForeignKey, DateTime, BigInteger, SmallInteger, Text, Interval, UniqueConstraint, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

WalletTypeEnum = Enum("custodial", "tonconnect", name="wallet_type", create_type=True)
TxDirEnum      = Enum("in_project_wallet", "in_user_wallet", "out_project_wallet", "out_user_wallet", name="tx_dir", create_type=True)
TxStatusEnum   = Enum("pending", "done", "failed", "reverted", name="tx_status", create_type=True)

class accounts(Base):
    __tablename__ = 'accounts'
    __table_args__ = {"schema": "coin_app_schema"}
    telegram_id = Column(BigInteger, primary_key=True, nullable=False)
    telegram_username = Column(Text)
    number_borv = Column(Numeric, nullable=False, default=0)
    date_creation = Column(DateTime(timezone=False), nullable=False, default=datetime.now(timezone.utc))
    date_last_visit = Column(DateTime(timezone=False), nullable=False, default=datetime.now(timezone.utc))
    language = Column(Text, ForeignKey('coin_app_schema.languages.language'), nullable=False, default='Russian')
    telegram_firstname = Column(Text) 
    level_clothes = Column(SmallInteger, nullable=False, default=1)
    level_apartment = Column(SmallInteger, nullable=False, default=1)
    CheckConstraint('number_borv >= 0', name='number_borv_check')
    CheckConstraint('level_clothes > 0', name='level_clothes_check')
    CheckConstraint('level_apartment > 0', name='level_apartment_check')
    languages=relationship("languages",foreign_keys=[language])
    def __repr__(self):
        return "<State(telegram_id='{0}',telegram_username='{1}',number_borv='{2}',date_creation='{3}',date_last_visit='{4}', language='{5}', telegram_firstname='{6}', level_clothes='{7}', level_apartment='{8}')>".format(self.telegram_id, self.telegram_username,self.number_borv,self.date_creation,self.date_last_visit, self.language, self.telegram_firstname, self.level_clothes, self.level_apartment)

class wallets(Base):
    __tablename__ = "wallets"
    __table_args__ = {"schema": "coin_app_schema"}
    telegram_id = Column(BigInteger, ForeignKey('coin_app_schema.accounts.telegram_id'), primary_key=True, nullable=False)
    type        = Column(WalletTypeEnum, nullable=False)
    public_addr = Column(Text, nullable=False, unique=True)
    mnemonics = Column(LargeBinary, nullable=False)         
    date_added  = Column(DateTime, default=datetime.now(timezone.utc))
    accounts=relationship("accounts",foreign_keys=[telegram_id])

class groups(Base):
    __tablename__  = 'groups'
    __table_args__ = {"schema": "coin_app_schema"}
    id_group       = Column(BigInteger, primary_key=True, nullable=False)
    name_group     = Column(Text, nullable=False, unique=True)
    telegram_id    = Column(BigInteger, ForeignKey('coin_app_schema.accounts.telegram_id'), unique=True)
    accounts=relationship("accounts",foreign_keys=[telegram_id])
    def __repr__(self):
        return "<State(id_group='{0}',name_group='{1}',telegram_id='{2}')>".format(self.id_group, self.name_group, self.telegram_id)

class groups_members(Base):
    __tablename__  = 'groups_members'
    __table_args__ = {"schema": "coin_app_schema"}
    telegram_id    = Column(BigInteger, ForeignKey('coin_app_schema.accounts.telegram_id'), primary_key=True)
    id_group       = Column(BigInteger, ForeignKey('coin_app_schema.groups.id_group'),nullable=False)
    accounts=relationship("accounts",foreign_keys=[telegram_id])
    groups=relationship("groups",foreign_keys=[id_group])
    def __repr__(self):
        return "<State(telegram_id='{0}',id_group='{1}')>".format(self.telegram_id, self.id_group)

class transactions(Base):
    __tablename__  = "transactions"
    __table_args__ = {"schema": "coin_app_schema"}
    id_transaction = Column(BigInteger, ForeignKey('coin_app_schema.accounts.telegram_id'), primary_key=True)
    telegram_id    = Column(BigInteger, nullable=False)
    direction      = Column(TxDirEnum)
    amount_ton     = Column(Numeric(38, 9), nullable=False)
    lt             = Column(BigInteger)        
    hash           = Column(Text)
    status         = Column(TxStatusEnum, default="pending")
    created_at     = Column(DateTime, default=datetime.now(timezone.utc))
    accounts=relationship("accounts",foreign_keys=[telegram_id])

class languages(Base):
    __tablename__ = 'languages'
    __table_args__ = {"schema": "coin_app_schema"}
    language = Column(Text, primary_key=True, nullable=False)
    def __repr__(self):
        return "<State(language='{0}')>".format(self.language)

class streamers(Base):
    __tablename__ = 'streamers'
    __table_args__ = {"schema": "coin_app_schema"}
    id_streamer = Column(Integer, primary_key=True, nullable=False)
    name_streamer = Column(Text, nullable=False, unique=True)
    price_ton = Column(Numeric, nullable=False)
    profit_ton = Column(Numeric, nullable=False)
    profit_borv = Column(Numeric, nullable=False)
    time_interval = Column(Interval, nullable=False)
    level = Column(SmallInteger, nullable=False, default=1)
    stages_number = Column(SmallInteger, nullable=False, default=1)
    is_displayed = Column(Boolean, nullable=False, default=True)
    is_open_for_purchase = Column(Boolean, nullable=False, default=True)
    CheckConstraint('price_ton >= 0', name='price_ton_check')
    CheckConstraint('profit_ton >= 0', name='profit_ton_check')
    CheckConstraint('profit_borv >= 0', name='profit_borv_check')
    CheckConstraint('level >= 0', name='level_check')
    CheckConstraint('stages_number > 0', name='stages_number_check')
    def __repr__(self):
        return "<State(id_streamer='{0}',name_streamer='{1}',price_ton='{2}',profit_ton='{3}',profit_borv='{4}',time_interval='{5}', level='{6}', stages_number='{7}', is_displayed='{8}', is_open_for_purchase='{9}')>".format(self.id_streamer, self.name_streamer,self.price_ton,self.profit_ton,self.profit_borv,self.time_interval, self.level, self.stages_number, self.is_displayed, self.is_open_for_purchase)

class streams(Base):
    __tablename__ = 'streams'
    __table_args__ = {"schema": "coin_app_schema"}
    id_stream = Column(BigInteger, primary_key=True, nullable=False)
    telegram_id = Column(BigInteger, ForeignKey('coin_app_schema.accounts.telegram_id'), nullable=False)
    id_streamer = Column(Integer, ForeignKey('coin_app_schema.streamers.id_streamer'), nullable=False)
    date_end = Column(DateTime(timezone=False), nullable=False)
    date_start = Column(DateTime(timezone=False), nullable=False, default=datetime.now(timezone.utc))
    stages_number = Column(SmallInteger, nullable=False, default=1)
    current_stage = Column(SmallInteger, nullable=False, default=0)
    profit_ton = Column(Numeric, nullable=False)
    profit_borv = Column(Numeric, nullable=False)
    # if streams will be more than 1, delete below from here and db
    UniqueConstraint('telegram_id', 'id_streamer', name='telegram_id_and_id_streamer_unique')
    CheckConstraint('stages_number > 0', name='stages_number_check')
    CheckConstraint('current_stage >= 0 AND current_stage <= stages_number', name='current_stage_check') 
    CheckConstraint('profit_ton >= 0', name='profit_ton_check')
    CheckConstraint('profit_borv >= 0', name='profit_borv_check')
    accounts=relationship("accounts",foreign_keys=[telegram_id])
    streamers=relationship("streamers",foreign_keys=[id_streamer])
    def __repr__(self):
        return "<State(id_stream='{0}',telegram_id='{1}',id_streamer='{2}',date_end='{3}',stages_number='{4}',current_stage='{5}')>".format(self.id_stream, self.telegram_id,self.id_streamer,self.date_end, self.stages_number, self.current_stage)

class shop_product_types(Base):
    __tablename__ = 'shop_product_types'
    __table_args__ = {"schema": "coin_app_schema"}
    product_type = Column(Text, primary_key=True, nullable=False)
    def __repr__(self):
        return "<State(product_type='{0}')>".format(self.product_type)

class shop_product_bonus_types(Base):
    __tablename__ = 'shop_product_bonus_types'
    __table_args__ = {"schema": "coin_app_schema"}
    product_bonus = Column(Text, primary_key=True, nullable=False)
    def __repr__(self):
        return "<State(product_bonus='{0}')>".format(self.product_bonus)

class shop_products(Base):
    __tablename__ = 'shop_products'
    __table_args__ = {"schema": "coin_app_schema"}
    id_product = Column(SmallInteger, primary_key=True, nullable=False)
    name_product = Column(Text, nullable=False, unique=True)
    product_type = Column(Text,  ForeignKey('coin_app_schema.shop_product_types.product_type'), nullable=False)
    product_bonus = Column(Text,  ForeignKey('coin_app_schema.shop_product_bonus_types.product_bonus'), nullable=False)
    data_bonus_product = Column(Text, nullable=True)
    price_ton = Column(Numeric, nullable=False)
    price_borv = Column(Numeric, nullable=False)
    level = Column(SmallInteger, nullable=False)
    CheckConstraint('price_ton >= 0', name='price_ton_check')
    CheckConstraint('price_borv >= 0', name='price_borv_check')
    CheckConstraint('level >= 0', name='level_check')
    shop_product_types=relationship("shop_product_types",foreign_keys=[product_type])
    shop_product_bonus_types=relationship("shop_product_bonus_types",foreign_keys=[product_bonus])
    def __repr__(self):
        return "<State(id_product='{0}',name_product='{1}',product_type='{2}',product_bonus='{3}', data_bonus_product='{4}', price_ton='{5}', price_borv='{6}')>".format(self.id_product, self.name_product,self.product_type,self.product_bonus, self.data_bonus_product, self.price_ton, self.price_borv)

class wearing_shop_products(Base):
    __tablename__ = 'wearing_shop_products'
    __table_args__ = {"schema": "coin_app_schema"}
    telegram_id = Column(BigInteger, ForeignKey('coin_app_schema.accounts.telegram_id'), primary_key=True, nullable=False)
    id_clothes = Column(Integer, nullable=False, default=-1)
    id_apartment = Column(Integer, nullable=False, default=-1)
    id_watch = Column(Integer, nullable=False, default=-1)
    accounts=relationship("accounts",foreign_keys=[telegram_id])
    def __repr__(self):
        return "<State(telegram_id='{0}', id_clothes='{1}', id_apartment='{2}', id_watch='{3}')>".format(self.telegram_id, self.id_clothes, self.id_apartment, self.id_watch)

class shop_products_having(Base):
    __tablename__ = 'shop_products_having'
    __table_args__ = {"schema": "coin_app_schema"}
    id_having = Column(BigInteger, primary_key=True, nullable=False)
    telegram_id = Column(BigInteger, ForeignKey('coin_app_schema.accounts.telegram_id'), nullable=False)
    id_product = Column(SmallInteger, ForeignKey('coin_app_schema.shop_products.id_product'), nullable=False)
    accounts=relationship("accounts",foreign_keys=[telegram_id])
    shop_products=relationship("shop_products",foreign_keys=[id_product])
    UniqueConstraint('telegram_id', 'id_product', name='telegram_id_id_product_unique')
    def __repr__(self):
        return "<State(id_having='{0}', telegram_id='{1}', id_product='{2}')>".format(self.id_having, self.telegram_id, self.id_product)

class streamers_availability_reasons(Base):
    __tablename__ = 'streams_availability_reasons'
    __table_args__ = {"schema": "coin_app_schema"}
    reason = Column(Text, primary_key=True, nullable=False)
    def __repr__(self):
        return "<State(reason='{0}')>".format(self.reason)

class streamers_availability(Base):
    __tablename__ = 'streams_availability'
    __table_args__ = {"schema": "coin_app_schema"}
    id_availability = Column(BigInteger, primary_key=True, nullable=False)
    telegram_id = Column(BigInteger, ForeignKey('coin_app_schema.accounts.telegram_id'), nullable=False)
    id_streamer = Column(Integer, ForeignKey('coin_app_schema.streamers.id_streamer'), nullable=False)
    is_available = Column(Boolean, nullable=False, default=False)
    reason = Column(Text, ForeignKey('coin_app_schema.streams_availability_reasons.reason'), nullable=False, default='not_unlocked')
    max_number_streams = Column(SmallInteger, nullable=False, default=1)
    current_number_streams = Column(SmallInteger, nullable=False, default=0)
    reason_info = Column(Text)
    history_number_streams = Column(Integer, nullable=False, default=0)
    UniqueConstraint('telegram_id', 'id_streamer', name='streamers_availability__telegram_id_and_id_streamer_unique')
    CheckConstraint('current_number_streams >= 0 AND current_number_streams <= max_number_streams', name='current_number_streams_check')
    CheckConstraint('max_number_streams > 0', name='max_number_streams_check')
    CheckConstraint('history_number_streams >= 0', name='history_number_streams_check')
    accounts=relationship("accounts",foreign_keys=[telegram_id])
    streamers=relationship("streamers",foreign_keys=[id_streamer])
    streams_availability_reasons=relationship("streams_availability_reasons",foreign_keys=[reason])
    def __repr__(self):
        return "<State(id_availability='{0}', telegram_id='{1}', id_streamer='{2}', is_available='{3}', reason='{4}', max_number_streams='{5}', current_number_streams='{6}', reason_info='{7}', history_number_streams='{8}')>".format(self.id_availability, self.telegram_id, self.id_streamer, self.is_available, self.reason, self.max_number_streams, self.current_number_streams, self.reason_info, self.history_number_streams)