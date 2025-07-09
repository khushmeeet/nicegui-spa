import pandas as pd
from nicegui import ui, app


def accounts():
    right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    accounts_df = app.storage.client["accounts_df"]
    trades_df = app.storage.client["trades_df"]

    def get_all_account_balance_series():
        print(2)
        all_series = []
        for _, account in accounts_df.iterrows():
            acc_name = account["Name"]
            a1_df = trades_df[trades_df["account_name"] == acc_name].copy()
            a1_df_sorted = a1_df.sort_values(by=["exit_time"])
            series = [[x.timestamp() * 1000, y] for x, y in zip(a1_df_sorted["exit_time"], a1_df_sorted["ending_balance"])]
            all_series.append({"name": acc_name, "data": series})
        return all_series

    def get_monthly_gain_data():
        print(1)
        df = app.storage.client["trades_df"]
        df = trades_df.copy()
        df["exit_time"] = pd.to_datetime(df["exit_time"])

        # Filter for last 12 months
        today = pd.Timestamp.today().normalize()
        start_date = today - pd.DateOffset(months=12)
        df = df[df["exit_time"] >= start_date]

        # Add "month" column
        df["month"] = df["exit_time"].dt.to_period("M")

        # Group by month and sum actual PnL
        monthly_pnl = df.groupby("month")["actual_pnl"].sum()

        # Create cumulative starting balances for % change (approximation)
        monthly_balance = df.groupby("month")[["starting_balance", "ending_balance"]].agg("last")

        # Prepare final result
        monthly_data = []
        for month in monthly_pnl.index:
            label = month.strftime("%b-%Y")
            value = monthly_pnl[month]
            starting = monthly_balance.loc[month, "starting_balance"]
            ending = monthly_balance.loc[month, "ending_balance"]
            pct = ((ending - starting) / starting * 100) if starting else 0

            monthly_data.append({"month": label, "gain": round(value, 2), "percent": round(pct, 2)})

        return monthly_data

    with ui.column().classes("w-full h-full text-lg"):

        def on_toggle(e):
            mode = e.value
            chart.options["plotOptions"]["series"]["compare"] = mode.lower() if mode == "Percent" else None
            if mode == "Percent":
                chart.options["yAxis"]["labels"]["format"] = "{value}%"
                chart.options["tooltip"]["pointFormat"] = '<span style="color:{series.color}">{series.name}</span>: {point.change:.1f}%<br/>'
            else:
                chart.options["yAxis"]["labels"]["format"] = None
                chart.options["tooltip"]["pointFormat"] = '<span style="color:{series.color}">{series.name}</span>: {point.y:.2f}<br/>'
            chart.update()

        with ui.row().classes("w-full justify-between"):
            ui.label("Equity Curve").classes("text-2xl")
            ui.toggle(["Value", "Percent"], value="Value", on_change=on_toggle)

        chart = ui.highchart(
            type="stockChart",
            extras=["stock"],
            options={
                "chart": {"type": "line", "spacingRight": 30},
                "title": {"text": None},
                "series": get_all_account_balance_series(),
                "xAxis": {"type": "datetime", "labels": {"format": "{value:%d %b %Y}"}, "title": None},
                "yAxis": {"title": None, "labels": {"format": None, "x": 30}},
                "legend": {"enabled": True, "layout": "horizontal", "align": "center", "verticalAlign": "bottom"},
                "plotOptions": {"series": {"marker": {"enabled": False}, "states": {"hover": {"enabled": True}}}},
                "rangeSelector": {
                    "selected": 4,
                    "buttons": [
                        {"type": "month", "count": 1, "text": "1m", "title": "View 1 month"},
                        {"type": "month", "count": 2, "text": "2m", "title": "View 2 months"},
                        {"type": "month", "count": 3, "text": "3m", "title": "View 3 months"},
                        {"type": "month", "count": 6, "text": "6m", "title": "View 6 months"},
                        {"type": "ytd", "text": "YTD", "title": "View year to date"},
                        {"type": "year", "count": 1, "text": "1y", "title": "View 1 year"},
                        {"type": "year", "count": 2, "text": "2y", "title": "View 2 years"},
                        {"type": "all", "text": "All", "title": "View all"},
                    ],
                },
                "navigator": {"enabled": False},
                "tooltip": {"pointFormat": '<span style="color:{series.color}">{series.name}</span>: {point.y:.2f}<br/>'},
            },
        ).classes("w-full h-[540px]")

        # ui.timer(0.1, lambda: (chart.run_method("chart.yAxis[0].setExtremes", [None, None]), chart.run_method("chart.reflow")), once=True)

        aggrid_options = {
            "domLayout": "autoHeight",
            "suppressHorizontalScroll": False,
            "ensureDomOrder": True,
            "defaultColDef": {"resizable": True},
            "rowSelection": "single",
            "suppressRowClickSelection": False,
            "minWidth": 800,
            "columnDefs": [
                {"headerName": "", "checkboxSelection": True, "width": 40, "headerCheckboxSelection": True, "resizable": False},
                {"headerName": "Name", "field": "Name", "filter": "agTextColumnFilter", "floatingFilter": True, "width": 200, "minWidth": 100},
                {"headerName": "Broker", "field": "Broker", "filter": "agTextColumnFilter", "floatingFilter": True, "width": 150, "minWidth": 100},
                {"headerName": "Type", "field": "Type", "filter": "agTextColumnFilter", "floatingFilter": True, "width": 100, "minWidth": 100},
                {"headerName": "Login", "field": "Login", "filter": "agTextColumnFilter", "floatingFilter": True, "width": 100, "minWidth": 100},
                {"headerName": "Platform", "field": "Platform", "filter": "agTextColumnFilter", "floatingFilter": True, "width": 100, "minWidth": 100},
                {"headerName": "Server", "field": "Server", "filter": "agTextColumnFilter", "floatingFilter": True, "width": 200, "minWidth": 100},
                {"headerName": "Path", "field": "Path", "filter": "agTextColumnFilter", "floatingFilter": True, "minWidth": 100},
                {"headerName": "Currency", "field": "Currency", "filter": "agTextColumnFilter", "floatingFilter": True, "width": 100, "minWidth": 100},
                {"headerName": "Starting Balance", "field": "Starting Balance", "filter": "agTextColumnFilter", "floatingFilter": True, "minWidth": 100},
                {"headerName": "Current Balance", "field": "Current Balance", "filter": "agTextColumnFilter", "floatingFilter": True, "minWidth": 100},
            ],
        }

        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Accounts Summary").classes("text-2xl")
            ui.button("Add Account", icon="add", on_click=lambda: right_drawer.toggle())

        ui.aggrid.from_pandas(accounts_df, options=aggrid_options).classes("max-h-128")

        content = ["Monthly Growth", "Profit Heatmap", "Drawdown Curve"]
        with ui.tabs() as tabs:
            for title in content:
                ui.tab(title)
        with ui.tab_panels(tabs, value=content[0]).classes("w-full p-0") as panels:
            with ui.tab_panel(content[0]).classes("p-0"):
                monthly_data = get_monthly_gain_data()

                categories = [item["month"] for item in monthly_data]
                absolute_gains = [item["gain"] for item in monthly_data]
                percent_gains = [item["percent"] for item in monthly_data]

                with ui.row().classes("w-full items-center justify-between"):
                    with ui.row():
                        acc = ui.select(options=accounts_df["Name"].tolist(), value=accounts_df["Name"].tolist()[0], label="Account").classes("w-64")
                        data = ui.select(options=["Last 1 year", 2025, 2024], value="Last 1 year", label="Time period").classes("w-64")
                    toggle = ui.toggle(["Value", "Percent"], value="Percent")

                ui.highchart(
                    {
                        "chart": {"type": "column"},
                        "title": {"text": None},
                        "xAxis": {
                            "categories": categories,
                            "crosshair": True,
                        },
                        "yAxis": {
                            "min": 0,
                            "title": {"text": "Gain"},
                        },
                        "tooltip": {"shared": True, "headerFormat": "<b>{point.key}</b><br/>", "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y:.2f}</b><br/>'},
                        "plotOptions": {"column": {"pointPadding": 0.2, "borderWidth": 0}},
                        "series": [{"name": "Absolute Gain", "data": absolute_gains}, {"name": "Percent Gain", "data": percent_gains, "yAxis": 1}],
                        "yAxis": [{"title": {"text": "Absolute Gain"}}, {"title": {"text": "Percent Gain"}, "opposite": True, "labels": {"format": "{value}%"}}],
                    }
                ).classes("w-full h-64")
            with ui.tab_panel(content[1]).classes("p-0"):
                df_to_use = trades_df[trades_df["account_name"] == accounts_df["Name"].iloc[0]].copy()
                a1_df_sorted = df_to_use.sort_values(by=["exit_time"], ascending=True)

                ui.echart(
                    {
                        "series": {
                            "type": "heatmap",
                            "coordinateSystem": "calendar",
                            "calendarIndex": 0,
                            "data": [[str(x), y] for x, y in zip(a1_df_sorted["exit_time"], a1_df_sorted["actual_pnl"])],
                        },
                        "calendar": {
                            "top": 20,
                            "left": 30,
                            # "right": 30,
                            "cellSize": ["auto", 18],
                            "range": "2025",
                            "itemStyle": {"borderWidth": 0.5},
                            "yearLabel": {"show": False},
                        },
                        "tooltip": {"position": "top"},
                        "visualMap": {
                            "min": a1_df_sorted["actual_pnl"].min(),
                            "max": a1_df_sorted["actual_pnl"].max(),
                            "calculable": True,
                            "orient": "horizontal",
                            "left": "center",
                            "bottom": "40",
                            "itemHeight": 400,
                        },
                    }
                ).classes("w-[1024px]")

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
