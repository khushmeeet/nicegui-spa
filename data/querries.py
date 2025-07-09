import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pandas as pd
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import Account, Broker, Instrument, Trade
from db.get_session import get_session
from utils.case_converter import snake_to_title


def get_all_items_from_trade() -> pd.DataFrame:
    with get_session() as session:
        stmt = select(Trade).options(joinedload(Trade.account), joinedload(Trade.symbol), joinedload(Trade.instrument), joinedload(Trade.strategy))
        result = session.execute(stmt)
        trades = result.scalars().all()
        trade_dicts = []
        for t in trades:
            trade_dicts.append(
                {
                    "id": t.id,
                    "trade_id": t.trade_id,
                    "status": t.status.name,
                    "risk": t.risk,
                    "direction": t.direction.name,
                    "order_type": t.order_type.name,
                    "lots": t.lots,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "open_time": t.open_time,
                    "exit_time": t.exit_time,
                    "duration": t.duration.total_seconds() if t.duration else None,
                    "actual_pnl": t.actual_pnl,
                    "account_name": t.account.name if t.account else None,
                    "account_broker": t.account.broker if t.account else None,
                    "symbol": t.symbol.id,
                    "instrument": t.instrument.id,
                    "strategy": t.strategy.name if t.strategy else None,
                    "starting_balance": t.starting_balance,
                    "ending_balance": t.ending_balance,
                }
            )

        df = pd.DataFrame(trade_dicts)
        df.set_index("id", inplace=True)
        return df


def get_all_items_from_account() -> pd.DataFrame:
    with get_session() as session:
        data = []
        query = (
            session.query(
                Account.id,
                Account.name,
                Account.login,
                Account.type,
                Account.platform,
                Account.path,
                Account.portable,
                Account.server,
                Account.currency,
                Account.starting_balance,
                Account.current_balance,
                Account.archived,
                Broker.name.label("broker"),
                func.count(Instrument.id).label("instrument_count"),
            )
            .outerjoin(Broker, Account.broker_id == Broker.id)
            .outerjoin(Instrument, Instrument.account_id == Account.id)
            .group_by(Account.id, Broker.name)
        )
        accounts = query.all()
        for acc in accounts:
            data.append(
                {
                    "ID": acc.id,
                    "Name": acc.name,
                    "Broker": acc.broker,
                    "Currency": acc.currency,
                    "Login": acc.login,
                    "Type": acc.type,
                    "Platform": acc.platform,
                    "Server": acc.server,
                    "Path": acc.path,
                    "Instruments #": acc.instrument_count,
                    "Starting Balance": acc.starting_balance,
                    "Current Balance": acc.current_balance,
                    "Archived": acc.archived,
                }
            )
        df = pd.DataFrame(data)
        try:
            df.set_index(
                "ID",
                inplace=True,
            )
        except KeyError:
            pass
        return df


def get_all_items_from_table(table, fields) -> pd.DataFrame:
    with get_session() as session:
        items = session.query(table).all()
        data = []
        for item in items:
            data.append({**{snake_to_title(field): getattr(item, field) for field in fields}})
        df = pd.DataFrame(data)
        try:
            df.set_index(
                "ID",
                inplace=True,
            )
        except KeyError:
            pass
        return df


if __name__ == "__main__":
    df = get_all_items_from_account()
    print(df.head())
