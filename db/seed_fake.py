import sys
import os
import math
import random as rnd
from typing import List
from datetime import datetime, timedelta


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from models import Broker, Account, PlatformType, Symbol, Instrument, Suffix, CurrencyType, Strategy
from models.enums import TradeSuccessProbabilityType, TradingMindState, TradeStatusType, DirectionType, OrderType, ExitReasonType
from db.get_session import get_session

from data.commands import add_instrument


def seed_brokers(clear_existing: bool = True):
    with get_session() as session:
        if clear_existing:
            session.query(Broker).delete()
            session.commit()

        brokers = [
            Broker(name="IC Markets"),
            Broker(name="Pepperstone"),
            Broker(name="FXCM"),
            Broker(name="FTMO"),
            Broker(name="The5ers"),
            Broker(name="E8"),
        ]

        session.add_all(brokers)
        session.commit()
        print("Brokers seeded successfully.")
        return brokers


def seed_accounts(brokers: List[Broker], clear_existing: bool = True):
    with get_session() as session:
        if clear_existing:
            session.query(Account).delete()
            session.commit()

        accounts = [
            Account(
                name="John",
                login="52399047",
                password="9UtKTv0!2MUeaT",
                type="demo",
                broker=brokers[0],
                platform=PlatformType.mt5,
                path=os.path.join("D:\\", "MetaTrader5", "MT5_MT_1", "terminal64.exe"),
                portable=True,
                server="ICMarketsSC-Demo",
                currency=CurrencyType.USD,
                balance=10000,
            ),
            Account(
                name="Jane",
                login="52399298",
                password="10Bf@C4NzJWFUF",
                type="demo",
                broker=brokers[0],
                platform=PlatformType.mt5,
                path=os.path.join("D:\\", "MetaTrader5", "MT5_MT_2", "terminal64.exe"),
                portable=True,
                server="ICMarketsSC-Demo",
                currency=CurrencyType.USD,
                balance=15000,
            ),
            Account(
                name="John Spread Betting",
                login="62081926",
                password="?afslF8rqn",
                type="demo",
                broker=brokers[1],
                platform=PlatformType.mt5,
                path=os.path.join("D:\\", "MetaTrader5", "MT5_MT_3", "terminal64.exe"),
                portable=True,
                server="PepperstoneUK-Demo",
                currency=CurrencyType.GBP,
                balance=20000,
            ),
            Account(
                name="John Main",
                login="52399047",
                password="9UtKTv0!2MUeaT",
                type="live",
                broker=brokers[0],
                platform=PlatformType.mt5,
                path=os.path.join("D:\\", "MetaTrader5", "MT5_MT_4", "terminal64.exe"),
                portable=True,
                server="ICMarketsSC-Live",
                currency=CurrencyType.USD,
                balance=25000,
            ),
            Account(
                name="Jane Main",
                login="52399298",
                password="10Bf@C4NzJWFUF",
                type="live",
                broker=brokers[0],
                platform=PlatformType.mt5,
                path=os.path.join("D:\\", "MetaTrader5", "MT5_MT_5", "terminal64.exe"),
                portable=True,
                server="ICMarketsSC-Live",
                currency=CurrencyType.USD,
                balance=30000,
            ),
            Account(
                name="John Main Spread Betting",
                login="62081926",
                password="?afslF8rqn",
                type="live",
                broker=brokers[1],
                platform=PlatformType.mt5,
                path=os.path.join("D:\\", "MetaTrader5", "MT5_MT_6", "terminal64.exe"),
                portable=True,
                server="PepperstoneUK-Live",
                currency=CurrencyType.GBP,
                balance=35000,
            ),
        ]

        session.add_all(accounts)
        session.commit()
        print("Accounts seeded successfully.")
        return accounts


def seed_symbols(clear_existing: bool = True):
    with get_session() as session:
        if clear_existing:
            session.query(Symbol).delete()
            session.commit()

        symbols = [
            # Majors
            Symbol(symbol="EURUSD", description="Euro to US Dollar"),
            Symbol(symbol="USDJPY", description="US Dollar to Japanese Yen"),
            Symbol(symbol="GBPUSD", description="British Pound to US Dollar"),
            Symbol(symbol="USDCHF", description="US Dollar to Swiss Franc"),
            Symbol(symbol="AUDUSD", description="Australian Dollar to US Dollar"),
            Symbol(symbol="NZDUSD", description="New Zealand Dollar to US Dollar"),
            Symbol(symbol="USDCAD", description="US Dollar to Canadian Dollar"),
            Symbol(symbol="EURGBP", description="Euro to British Pound"),
            Symbol(symbol="EURJPY", description="Euro to Japanese Yen"),
            Symbol(symbol="EURCHF", description="Euro to Swiss Franc"),
            Symbol(symbol="EURAUD", description="Euro to Australian Dollar"),
            Symbol(symbol="EURNZD", description="Euro to New Zealand Dollar"),
            Symbol(symbol="EURCAD", description="Euro to Canadian Dollar"),
            Symbol(symbol="GBPJPY", description="British Pound to Japanese Yen"),
            Symbol(symbol="GBPCHF", description="British Pound to Swiss Franc"),
            Symbol(symbol="GBPAUD", description="British Pound to Australian Dollar"),
            Symbol(symbol="GBPNZD", description="British Pound to New Zealand Dollar"),
            Symbol(symbol="GBPCAD", description="British Pound to Canadian Dollar"),
            Symbol(symbol="AUDJPY", description="Australian Dollar to Japanese Yen"),
            Symbol(symbol="AUDCHF", description="Australian Dollar to Swiss Franc"),
            Symbol(symbol="AUDNZD", description="Australian Dollar to New Zealand Dollar"),
            Symbol(symbol="AUDCAD", description="Australian Dollar to Canadian Dollar"),
            Symbol(symbol="NZDJPY", description="New Zealand Dollar to Japanese Yen"),
            Symbol(symbol="NZDCHF", description="New Zealand Dollar to Swiss Franc"),
            Symbol(symbol="NZDCAD", description="New Zealand Dollar to Canadian Dollar"),
            Symbol(symbol="CADJPY", description="Canadian Dollar to Japanese Yen"),
            Symbol(symbol="CADCHF", description="Canadian Dollar to Swiss Franc"),
            Symbol(symbol="CHFJPY", description="Swiss Franc to Japanese Yen"),
        ]

        session.add_all(symbols)
        session.commit()
        print("Symbols seeded successfully.")
        return symbols


def seed_instruments(accounts, clear_existing: bool = True):
    with get_session() as session:
        if clear_existing:
            session.query(Suffix).delete()
            session.query(Instrument).delete()
            session.commit()
        symbols = session.query(Symbol).all()
        instruments_for_all_accounts = []
        for account in accounts:
            instruments = [add_instrument(session, ticker=symbol.symbol, account=account) for symbol in symbols]
            for instrument in instruments:
                instruments_for_all_accounts.append(instrument)

        session.add_all(instruments_for_all_accounts)
        session.commit()
        print("Instruments seeded successfully.")
        return instruments


def seed_strategies(clear_existing: bool = True):
    with get_session() as session:
        if clear_existing:
            session.query(Strategy).delete()
            session.commit()

        strategies = [
            Strategy(name="Range Breakout"),
            Strategy(name="Reversal"),
            Strategy(name="Trend Following"),
        ]

        session.add_all(strategies)
        session.commit()
        print("Strategies seeded successfully.")
        return strategies


def random_duration(min_minutes=30, max_minutes=2880):
    duration_minutes = rnd.randint(min_minutes, max_minutes)
    return timedelta(minutes=duration_minutes)


def random_entry_time(start_year=2021, end_year=2022):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = rnd.randint(0, delta.days)
    random_minutes = rnd.randint(0, 1440)
    return start + timedelta(days=random_days, minutes=random_minutes)


def seed_trades(accounts, symbols, strategies):
    account = accounts[0]
    probability = rnd.choice(list(TradeSuccessProbabilityType))
    mindstate = rnd.choice(list(TradingMindState))
    symbol_id = rnd.randint(1, len(symbols))
    symbol = symbols[symbol_id - 1]
    strategy_id = rnd.randint(1, len(strategies))
    strategy = strategies[strategy_id - 1]
    status = TradeStatusType.active
    direction = rnd.choice(list(DirectionType))
    order_type = rnd.choice(list(OrderType))
    if rnd.random() >= 0.65:
        order_type = OrderType.market

    risk = 0.005
    lots = 0.1
    if probability == TradeSuccessProbabilityType.low:
        risk = 0.005
        lots = 0.1
        win_chance = 0.52
    elif probability == TradeSuccessProbabilityType.medium:
        risk = 0.0075
        lots = 0.25
        win_chance = 0.61
    else:
        risk = 0.01
        lots = 0.5
        win_chance = 0.72

    win_loss = 1 if rnd.random() <= win_chance else 0

    pips = rnd.randint(15, 150)
    rr = rnd.choice([1.0, 1.5, 2.0])
    stop_loss_pips = pips
    take_profit_pips = rr * stop_loss_pips

    entry_price = round(1 + rnd.random(), 5)
    if direction == DirectionType.long:
        stop_loss_price = round(entry_price - stop_loss_pips * 0.0001, 5)
        take_profit_price = round(entry_price + take_profit_pips * 0.0001, 5)
    else:
        stop_loss_price = round(entry_price + stop_loss_pips * 0.0001, 5)
        take_profit_price = round(entry_price - take_profit_pips * 0.0001, 5)

    entry_time = random_entry_time(2021, 2024)
    duration = random_duration(min_minutes=30, max_minutes=2880)
    exit_time = entry_time + duration

    reward_risk = take_profit_pips / stop_loss_pips

    exit_price = None
    exit_reason = None
    if win_loss == 1:
        exit_price = take_profit_price
        exit_reason = ExitReasonType.take_profit
    else:
        exit_price = stop_loss_price
        exit_reason = ExitReasonType.stop_loss

    actual_reward_risk = reward_risk

    if rnd.random() <= 0.02 and order_type != OrderType.market and status == TradeStatusType.pending:
        exit_reason = ExitReasonType.cancelled
        exit_price = None
        actual_reward_risk = None

    if rnd.random() <= 0.05:
        exit_reason = ExitReasonType.manual
        if win_loss == 1:
            if direction == DirectionType.long:
                exit_price = entry_price + (take_profit_price - entry_price) * rnd.random()
            else:
                exit_price = entry_price - (entry_price - take_profit_price) * rnd.random()
            actual_reward_risk = math.abs(exit_price - entry_price) / stop_loss_pips
        else:
            if direction == DirectionType.long:
                exit_price = entry_price - (entry_price - stop_loss_price) * rnd.random()
            else:
                exit_price = entry_price + (stop_loss_price - entry_price) * rnd.random()
            actual_reward_risk = take_profit_pips / math.abs(entry_price - exit_price)


def seed_all():
    brokers = seed_brokers()
    accounts = seed_accounts(brokers)
    symbols = seed_symbols()
    instruments = seed_instruments(accounts)
    strategies = seed_strategies()
    seed_trades(accounts, symbols, strategies)
    return brokers, accounts, symbols, instruments, strategies


if __name__ == "__main__":
    seed_all()
