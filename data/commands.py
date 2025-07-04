from models import Instrument, Suffix, Symbol
from utils.ticker import extract_symbol_and_suffix


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
