import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from dto import NewAccountData
from models import Instrument, Suffix, Symbol
from models.enums import AccountType, PlatformType, CurrencyType, CurrencySymbol
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
    mt5_account_info = get_account_info_mt5(
        login=int(new_account_data.login),
        password=new_account_data.password,
        server=new_account_data.server,
        path=new_account_data.path,
        portable=new_account_data.portable,
    )

    with get_session() as session:
        new_account_db_data = new_account_data.get_db_account(session)
        session.add(new_account_db_data)
        session.commit()
        new_grid_row = {
            "id": new_account_db_data.id,
            "name": new_account_db_data.name,
            "broker": new_account_db_data.broker.name,
            "login": mt5_account_info.login,
            "type": AccountType(new_account_data.type),
            "platform": PlatformType(new_account_data.platform),
            "server": mt5_account_info.server,
            "currency": CurrencyType(mt5_account_info.currency),
            "is_portable": new_account_data.portable,
            "starting_balance": mt5_account_info.balance,
            "current_balance": mt5_account_info.balance,
            "path": new_account_data.path,
            "instruments_count": 0,
            "archived": False,
            "selected": False,
            "leverage": mt5_account_info.leverage,
            "mt5_name": mt5_account_info.name,
            "mt5_company": mt5_account_info.company,
            "is_valid": True,
            "portable": new_account_data.portable,
        }
        # print(mt5_account_info.currency, CurrencyType[mt5_account_info.currency])
        return new_grid_row


def get_account_info_mt5(login, password, server, path, portable):
    res = mt5.initialize(login=login, password=password, server=server, path=path, portable=portable)
    if not res:
        print("Unable to login and initialize")
        print("Error code:", mt5.last_error())
        return
    acc = mt5.account_info()
    print(acc)
    mt5.shutdown()
    return acc


if __name__ == "__main__":
    get_account_info_mt5(52399047, "9UtKTv0!2MUeaT", "ICMarketsSC-Demo", "D:\\MetaTrader5\\MT_1\\terminal64.exe", True)
