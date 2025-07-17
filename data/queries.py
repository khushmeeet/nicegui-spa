import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pandas as pd
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import Account, Broker, Instrument, Trade
from models.enums import DirectionType, OrderType
from db.get_session import get_session
from utils.case_converter import snake_to_title


def get_all_instruments() -> pd.DataFrame:
    with get_session() as session:
        instruments = session.query(Instrument).options(joinedload(Instrument.account).joinedload(Account.broker), joinedload(Instrument.symbol)).all()

        data = []
        for inst in instruments:
            acc = inst.account
            data.append(
                {
                    "instrument_id": inst.id,
                    "ticker": inst.ticker,
                    "description": inst.description,
                    "symbol_id": inst.symbol_id,
                    "symbol": inst.symbol.symbol,
                    "account_id": inst.account_id,
                    "lot_size": inst.lot_size,
                    "leverage": inst.leverage,
                    "min_volume": inst.min_volume,
                    "max_volume": inst.max_volume,
                    "step_volume": inst.step_volume,
                    "account_name": acc.name if acc else None,
                    "account_login": acc.login if acc else None,
                    "account_platform": acc.platform.name if acc else None,
                    "account_currency": acc.currency.name if acc and acc.currency else None,
                    "account_current_balance": acc.current_balance if acc else None,
                    "account_broker": acc.broker.name,
                }
            )

        return pd.DataFrame(data)


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
                    "trade_id": int(t.trade_id),
                    "status": t.status.name,
                    "risk": t.risk,
                    "direction": t.direction.name,
                    "order_type": t.order_type.name,
                    "lots": t.lots,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "open_time": t.open_time,
                    "exit_time": t.exit_time,
                    "duration": t.duration.total_seconds(),
                    "actual_pnl": t.actual_pnl,
                    "actual_rr": t.actual_reward_risk,
                    "account_name": t.account.name,
                    "account_broker": t.account.broker.name,
                    "symbol": t.symbol.symbol,
                    "instrument": t.instrument.id,
                    "strategy": t.strategy.name,
                    "starting_balance": t.starting_balance,
                    "ending_balance": t.ending_balance,
                    "probability": t.probability,
                    "mindstate": t.mindstate,
                    "stop_loss_pips": t.stop_loss_pips,
                    "exit_reason": t.exit_reason,
                    "backtested": t.validated_from_backtest,
                    "account_id": t.account_id,
                    "account_currency": t.account.currency,
                }
            )

        df = pd.DataFrame(trade_dicts)
        df.set_index("id", inplace=True)
        df.sort_values("exit_time", inplace=True, ascending=False)
        df["order_type"] = df["order_type"].apply(lambda x: snake_to_title(x))
        df["direction_html"] = df["direction"].apply(
            lambda x: f'<span class="bg-{'blue' if snake_to_title(x) == DirectionType.long else 'amber'}-200 rounded-full py-1 px-3">{snake_to_title(x)}</span>'
        )
        df["order_type_html"] = df["order_type"].apply(
            lambda x: f'<span class="bg-{'pink' if snake_to_title(x) == OrderType.market else 'cyan' if snake_to_title(x) == OrderType.limit else 'orange'}-200 rounded-full py-1 px-3">{snake_to_title(x)}</span>'
        )
        df["win_loss_html"] = df["actual_pnl"].apply(lambda x: f'<span class="bg-{'emerald' if x>0 else 'rose'}-300 rounded-full py-1 px-3">{"Win" if x >0 else "Loss"}</span>')
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
                    "id": acc.id,
                    "name": acc.name,
                    "broker": acc.broker,
                    "currency": acc.currency,
                    "login": acc.login,
                    "type": acc.type,
                    "platform": acc.platform,
                    "server": acc.server,
                    "path": acc.path,
                    "instruments_count": acc.instrument_count,
                    "starting_balance": round(acc.starting_balance, 2),
                    "current_balance": round(acc.current_balance, 2),
                    "archived": acc.archived,
                }
            )
        df = pd.DataFrame(data)
        # try:
        #     df.set_index(
        #         "id",
        #         inplace=True,
        #     )
        # except KeyError:
        #     pass
        return df


def get_all_items_from_table(table, fields) -> pd.DataFrame:
    with get_session() as session:
        items = session.query(table).all()
        data = []
        for item in items:
            data.append({**{field: getattr(item, field) for field in fields}})
        df = pd.DataFrame(data)
        try:
            df.set_index(
                "id",
                inplace=True,
            )
        except KeyError:
            pass
        return df


if __name__ == "__main__":
    df = get_all_items_from_account()
    print(df.head())
