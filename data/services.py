import pandas as pd
from datetime import datetime


def get_all_account_balance_series(accounts_df: pd.DataFrame, trades_df: pd.DataFrame):
    all_series = []
    for _, account in accounts_df.iterrows():
        acc_name = account["Name"]
        a1_df = trades_df[trades_df["account_name"] == acc_name].copy()
        a1_df_sorted = a1_df.sort_values(by=["exit_time"])
        series = [[x.timestamp() * 1000, y] for x, y in zip(a1_df_sorted["exit_time"], a1_df_sorted["ending_balance"])]
        if len(series) > 0:
            all_series.append({"name": acc_name, "data": series})
    return all_series


def get_account_monthly_gain_dataV0(account_name: str, range_filter: str, mode: str, trades_df: pd.DataFrame):
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

    monthly = df.groupby("month").agg({"actual_pnl": "sum", "starting_balance": "first", "ending_balance": "last"}).reset_index()
    all_months = pd.date_range(start=monthly["month"].min(), end=monthly["month"].max(), freq="MS")
    monthly = monthly.set_index("month").reindex(all_months, fill_value=0).rename_axis("month").reset_index()

    if mode == "Percent":
        monthly["value"] = (monthly["actual_pnl"] / (monthly["starting_balance"].replace(0, 1))) * 100
    else:
        monthly["value"] = monthly["actual_pnl"]

    return {"name": "Gain", "data": [round(v, 2) for v in monthly["value"]], "colorByPoint": True}, [m.strftime("%b %Y") for m in monthly["month"]]


def get_pnl_for_a_year(account_name: str, year: str, df: pd.DataFrame, mode: str = "Value"):
    df_to_use = df[df["account_name"] == account_name].copy()
    df_to_use = df_to_use[df_to_use["exit_time"].dt.year == int(year)]

    df_to_use["exit_date"] = df_to_use["exit_time"].dt.date

    if mode == "Percent":
        df_to_use["percent_pnl"] = (df_to_use["actual_pnl"] / df_to_use["starting_balance"]) * 100
        daily_agg = df_to_use.groupby("exit_date")["percent_pnl"].sum()
    else:
        daily_agg = df_to_use.groupby("exit_date")["actual_pnl"].sum()

    min_val = daily_agg.min()
    max_val = daily_agg.max()

    data = [[str(date), value] for date, value in daily_agg.items()]
    return data, min_val, max_val


import pandas as pd
from datetime import datetime


def get_account_monthly_gain_data(account_name: str, range_filter: str, mode: str, trades_df: pd.DataFrame):
    df = trades_df[trades_df["account_name"] == account_name].copy()

    # Filter by range
    now = pd.Timestamp.now()
    if range_filter == "YTD":
        start_date = datetime(now.year, 1, 1)
    elif range_filter == "1 Year":
        start_date = now - pd.DateOffset(years=1)
    else:
        try:
            year = int(range_filter)
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            df = df[(df["exit_time"] >= start_date) & (df["exit_time"] < end_date)]
        except:
            return [], []

    if range_filter in ["YTD", "1 Year"]:
        df = df[df["exit_time"] >= start_date]

    if df.empty:
        return [], []

    # Create a list of all months in the date range
    all_months = pd.date_range(start=df["exit_time"].min().to_period("M").to_timestamp(), end=df["exit_time"].max().to_period("M").to_timestamp(), freq="MS")

    monthly_data = []

    for month_start in all_months:
        month_end = (month_start + pd.DateOffset(months=1)) - pd.Timedelta(seconds=1)

        # Starting balance = latest ending balance before month_start
        before_month = df[df["exit_time"] < month_start]
        month_df = df[(df["exit_time"] >= month_start) & (df["exit_time"] <= month_end)]

        if before_month.empty and month_df.empty:
            # No data at all
            monthly_data.append({"month": month_start, "value": 0})
            continue

        starting_balance = before_month.sort_values("exit_time")["ending_balance"].iloc[-1] if not before_month.empty else month_df.sort_values("exit_time")["starting_balance"].iloc[0]
        ending_balance = month_df.sort_values("exit_time")["ending_balance"].iloc[-1] if not month_df.empty else starting_balance

        absolute_gain = ending_balance - starting_balance
        percent_gain = (absolute_gain / starting_balance) * 100 if starting_balance != 0 else 0

        value = round(percent_gain if mode == "Percent" else absolute_gain, 2)

        monthly_data.append({"month": month_start, "value": value})

    return ({"name": "Gain", "data": [d["value"] for d in monthly_data], "colorByPoint": True}, [d["month"].strftime("%b %Y") for d in monthly_data])
