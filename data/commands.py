import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from dto import NewAccountData, NewSymbolData
from models import Instrument, Suffix, Symbol
from models.enums import AccountType, PlatformType, CurrencySymbol, SymbolType
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
        new_account_db_data = new_account_data.get_db_account(session, mt5_account_info)
        session.add(new_account_db_data)
        session.commit()
        new_grid_row = {
            "id": new_account_db_data.id,
            "name": new_account_db_data.name,
            "broker": new_account_db_data.broker.name,
            "login": new_account_db_data.login,
            "type": AccountType(new_account_db_data.type),
            "platform": PlatformType(new_account_db_data.platform),
            "server": new_account_db_data.server,
            "currency": new_account_db_data.currency,
            "is_portable": new_account_db_data.portable,
            "starting_balance": new_account_db_data.starting_balance,
            "current_balance": new_account_db_data.current_balance,
            "path": new_account_db_data.path,
            "instruments_count": 0,
            "archived": False,
            "selected": False,
            "leverage": new_account_db_data.leverage,
            "mt5_name": new_account_db_data.mt5_name,
            "mt5_company": new_account_db_data.mt5_company,
            "is_valid": True,
            "portable": new_account_db_data.portable,
            "currency_symbol": CurrencySymbol[new_account_db_data.currency].value,
        }
        return new_grid_row


def add_symbol(new_symbol_data: NewSymbolData):
    with get_session() as session:
        new_symbol_db_data = new_symbol_data.get_db_symbol()
        session.add(new_symbol_db_data)
        session.commit()
        new_grid_row = {
            "id": new_symbol_db_data.id,
            "symbol": new_symbol_db_data.symbol,
            "description": new_symbol_db_data.description,
            "type": SymbolType(new_symbol_db_data.type),
        }
        # print(mt5_account_info.currency, CurrencyType[mt5_account_info.currency])
        return new_grid_row


def delete_symbols(ids):
    with get_session() as session:
        session.query(Symbol).filter(Symbol.id.in_(ids)).delete()
        session.commit()


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


def add_array_of_dicts(model, data):
    if not data:
        raise ValueError("No data provided")

    columns_info = {col.name: col for col in model.__table__.columns}
    required_columns = {name for name, col in columns_info.items() if not col.primary_key}
    cleaned_data = []

    for i, row in enumerate(data):
        missing = required_columns - {key.lower() for key in row.keys()}
        if missing:
            raise ValueError(f"Row {i} is missing required non-nullable keys: {missing}")

        cleaned_row = {k.lower(): v for k, v in row.items() if k.lower() in required_columns}
        cleaned_data.append(cleaned_row)
        print(f"Row {i} cleaned: {cleaned_row}")
        break

    # with get_session as session:
    #     session.bulk_insert_mappings(model, cleaned_data)
    #     session.commit()


if __name__ == "__main__":
    get_account_info_mt5(52399047, "9UtKTv0!2MUeaT", "ICMarketsSC-Demo", "D:\\MetaTrader5\\MT_1\\terminal64.exe", True)
