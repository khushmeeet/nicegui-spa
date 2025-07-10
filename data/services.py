import pandas as pd
from datetime import datetime


def get_all_account_balance_series(accounts_df: pd.DataFrame, trades_df: pd.DataFrame):
    all_series = []
    for _, account in accounts_df.iterrows():
        acc_name = account["Name"]
        a1_df = trades_df[trades_df["account_name"] == acc_name].copy()
        a1_df_sorted = a1_df.sort_values(by=["exit_time"])
        series = [[x.timestamp() * 1000, y] for x, y in zip(a1_df_sorted["exit_time"], a1_df_sorted["ending_balance"])]
        all_series.append({"name": acc_name, "data": series})
    return all_series


def get_account_monthly_gain_data(account_name: str, range_filter: str, mode: str, trades_df: pd.DataFrame):
    df = trades_df[trades_df["account_name"] == account_name].copy()
    df["month"] = df["exit_time"].dt.to_period("M").dt.to_timestamp()

    if range_filter == "YTD":
        start_date = datetime(datetime.now().year, 1, 1)
    elif range_filter == "1 Year":
        start_date = pd.Timestamp.now() - pd.DateOffset(years=1)
    else:
        try:
            year = int(range_filter)
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            df = df[(df["exit_time"] >= start_date) & (df["exit_time"] < end_date)]
        except:
            df = pd.DataFrame()
            return []

    if range_filter in ["YTD", "1 Year"]:
        df = df[df["exit_time"] >= start_date]

    if df.empty:
        return []

    # Aggregate by month
    monthly = df.groupby("month").agg({"actual_pnl": "sum", "starting_balance": "first", "ending_balance": "last"}).reset_index()

    # Fill in missing months
    all_months = pd.date_range(start=monthly["month"].min(), end=monthly["month"].max(), freq="MS")

    monthly = monthly.set_index("month").reindex(all_months, fill_value=0).rename_axis("month").reset_index()

    if mode == "Percent":
        monthly["value"] = (monthly["actual_pnl"] / (monthly["starting_balance"].replace(0, 1))) * 100
    else:
        monthly["value"] = monthly["actual_pnl"]

    return {"name": "Gain", "data": [round(v, 2) for v in monthly["value"]], "colorByPoint": True}, [m.strftime("%b %Y") for m in monthly["month"]]
