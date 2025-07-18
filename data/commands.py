from dto import NewAccountData
from models import Instrument, Suffix, Symbol
from models.enums import AccountType, PlatformType, CurrencyType
from db.get_session import get_session
from utils.ticker import extract_symbol_and_suffix
import MetaTrader5 as mt5


def add_instrument(session, **kwargs) -> Instrument:
    ticker = kwargs.get("ticker")
    symbols = session.query(Symbol).all()
    symbol, suffix_name, suffix_tag = extract_symbol_and_suffix(ticker, symbols)
    suffix = session.query(Suffix).filter_by(name=suffix_name).first()
    if not suffix and suffix_name:
        suffix = Suffix(name=suffix_name, tag=suffix_tag)
        session.add(suffix)
    instrument = Instrument(**kwargs, symbol=symbol, suffix=suffix)
    return instrument


def add_account(new_account_data: NewAccountData):
    account_info = get_account_info_mt5(
        login=new_account_data.login,
        password=new_account_data.password,
        server=new_account_data.server,
        path=new_account_data.path,
        portable=new_account_data.portable,
    )
    print(account_info)
    with get_session() as session:

        new_account_db_data = new_account_data.get_db_account(session)
        session.add(new_account_db_data)
        session.commit()
        new_grid_row = {
            "id": new_account_db_data.id,
            "name": new_account_db_data.name,
            "broker": new_account_db_data.broker.name,
            "login": new_account_db_data.login,
            "type": AccountType(new_account_data.type),
            "platform": PlatformType(new_account_data.platform),
            "server": new_account_data.server,
            "currency": CurrencyType(new_account_data.currency),
            "is_portable": new_account_data.portable,
            "starting_balance": new_account_data.starting_balance,
            "current_balance": new_account_data.current_balance,
            "path": new_account_data.path,
            "instruments_count": 0,
            "archived": False,
            "selected": False,
        }
        return new_grid_row


def get_account_info_mt5(login, password, server, path, portable):
    res = mt5.initialize(login=login, password=password, server=server, path=path, portable=portable)
    if not res:
        print("Unable to login and initialize")
        return
    acc = mt5.account_info()
    print(acc)
    mt5.shutdown()
