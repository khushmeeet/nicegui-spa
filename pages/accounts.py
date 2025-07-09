from nicegui import ui, app
from datetime import datetime, timedelta


def filter_dates(period):
    now = datetime.now()
    if period == "1D":
        return now - timedelta(days=1)
    elif period == "1M":
        return now - timedelta(days=30)
    elif period == "1Y":
        return now - timedelta(days=365)
    elif period == "YTD":
        return datetime(now.year, 1, 1)
    elif period == "All":
        return None  # No filtering
    else:
        return None


def accounts():
    right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    accounts_df = app.storage.client["accounts_df"]
    trades_df = app.storage.client["trades_df"]

    def get_all_account_balance_series():
        all_series = []
        for _, account in accounts_df.iterrows():
            acc_name = account["Name"]
            a1_df = trades_df[trades_df["account_name"] == acc_name].copy()
            a1_df_sorted = a1_df.sort_values(by=["exit_time"])
            a1_df_sorted["cum_bal"] = account["Starting Balance"] + a1_df_sorted["actual_pnl"].cumsum()
            series = [[x.timestamp() * 1000, y] for x, y in zip(a1_df_sorted["exit_time"], a1_df_sorted["cum_bal"])]
            all_series.append({"name": acc_name, "data": series})
        return all_series

    with ui.column().classes("w-full h-full text-lg"):

        chart = (
            ui.highchart(
                type="stockChart",
                extras=["stock"],
                options={
                    "chart": {"type": "line"},
                    "title": {"text": None},
                    "series": get_all_account_balance_series(),
                    "xAxis": {"type": "datetime", "labels": {"format": "{value:%d %b %Y}"}, "title": None},
                    "yAxis": {
                        "title": None,
                    },
                    "legend": {
                        "layout": "vertical",
                        "align": "right",
                        "verticalAlign": "top",
                    },
                    "plotOptions": {
                        "series": {
                            "marker": {"enabled": False},
                            "states": {"hover": {"enabled": True}},
                        }
                    },
                    "rangeSelector": {
                        "allButtonsEnabled": True,
                        "buttons": [
                            {"type": "month", "count": 3, "text": "Day", "dataGrouping": {"forced": True, "units": [["day", [1]]]}},
                            {"type": "year", "count": 1, "text": "Week", "dataGrouping": {"forced": True, "units": [["week", [1]]]}},
                            {"type": "all", "text": "Month", "count": 1, "dataGrouping": {"forced": True, "units": [["month", [1]]]}},
                        ],
                        "buttonTheme": {"width": 60},
                        "inputStyle": {"color": "#CED5DF"},
                        "selected": 0,
                    },
                    "navigator": {"enabled": True},
                },
            )
            .classes("w-full")
            .style("height: 640px")
        )

        # update_chart(type("Event", (), {"value": toggle1.value})())

        aggrid_options = {
            "columnDefs": [
                {"headerName": "Name", "field": "Name", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Broker", "field": "Broker", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Type", "field": "Type", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Login", "field": "Login", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Platform", "field": "Platform", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Server", "field": "Server", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Currency", "field": "Currency", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Starting Balance", "field": "Starting Balance", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Current Balance", "field": "Current Balance", "filter": "agTextColumnFilter", "floatingFilter": True},
            ]
        }

        ui.separator()

        ui.button("Add Account", icon="add", on_click=lambda: right_drawer.toggle())
        ui.aggrid.from_pandas(accounts_df, options=aggrid_options).classes("max-h-128")

        ui.space()
        ui.highchart(
            {
                "title": {"text": None},
                "chart": {"type": "column"},
                "xAxis": {"categories": ["USA", "China", "Brazil", "EU", "Argentina", "India"], "crosshair": True, "accessibility": {"description": "Countries"}},
                "yAxis": {"min": 0, "title": {"text": "1000 metric tons (MT)"}},
                "series": [{"name": "Corn", "data": [387749, 280000, 129000, 64300, 54000, 34300]}],
            }
        ).classes("w-full h-64")

        if right_drawer and right_drawer_rendered_by != "accounts":
            app.storage.client["right_drawer_rendered_by"] = "accounts"
            right_drawer.clear()

            with right_drawer:
                ui.markdown("##### ➕ Add Account")
                with ui.grid().classes("w-full"):
                    ui.input(label="Name").classes("w-full")
                    ui.select(options=["Broker 1", "Broker 2", "Broker 3"], label="Broker").classes("w-full")
                    ui.input(label="Login").classes("w-full")
                    ui.input(label="Password", password=True, password_toggle_button=True).classes("w-full")
                    ui.select(label="Type", options=["Live", "Demo"]).classes("w-full")
                    ui.select(label="Platform", options=["MetaTrader 5", "cTrader 5"]).classes("w-full")
                    ui.input(label="Server").classes("w-full")
                    ui.checkbox("Is Portable", value=True).classes("w-full")
                ui.upload(label="Path", multiple=False, max_files=1).classes("w-full")
                with ui.row():
                    ui.button("Save", icon="save", on_click=lambda: ui.notify("Add Account clicked", position="bottom-right"))
                    ui.button("Cancel", icon="close", on_click=lambda: right_drawer.toggle())
                    ui.button("Clear", icon="delete_outline", on_click=lambda: ui.notify("Add Account clicked"))
