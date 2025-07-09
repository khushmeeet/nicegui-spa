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
            series = [[x.timestamp() * 1000, y] for x, y in zip(a1_df_sorted["exit_time"], a1_df_sorted["ending_balance"])]
            all_series.append({"name": acc_name, "data": series})
        return all_series

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
            chart.run_method("chart.yAxis[0].update", {"labels": chart.options["yAxis"]["labels"]})
            chart.run_method("chart.yAxis[0].setExtremes", [None, None])
            chart.run_method("chart.reflow")

        with ui.row().classes("w-full justify-between"):
            ui.label("Equity Curve").classes("text-2xl")
            ui.toggle(["Value", "Percent"], value="Value", on_change=on_toggle)

        chart = (
            ui.highchart(
                type="stockChart",
                extras=["stock"],
                options={
                    "chart": {"type": "line"},
                    "title": {"text": None},
                    "series": get_all_account_balance_series(),
                    "xAxis": {"type": "datetime", "labels": {"format": "{value:%d %b %Y}"}, "title": None},
                    "yAxis": {"title": None, "labels": {"format": None}},
                    "legend": {"enabled": True, "layout": "vertical", "align": "right", "verticalAlign": "top"},
                    "plotOptions": {
                        "series": {
                            "marker": {"enabled": False},
                            "states": {"hover": {"enabled": True}},
                        }
                    },
                    "rangeSelector": {
                        "selected": 7,
                        "buttons": [
                            {"type": "day", "count": 1, "text": "1d", "title": "View 1 day"},
                            {"type": "day", "count": 3, "text": "3d", "title": "View 3 days"},
                            {"type": "week", "count": 1, "text": "1w", "title": "View 1 week"},
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
            )
            .classes("w-full")
            .style("height: 480px")
        )

        # ui.timer(0.1, lambda: (chart.run_method("chart.yAxis[0].setExtremes", [None, None]), chart.run_method("chart.reflow")), once=True)

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

        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Accounts Summary").classes("text-2xl")
            ui.button("Add Account", icon="add", on_click=lambda: right_drawer.toggle())
        ui.aggrid.from_pandas(accounts_df, options=aggrid_options).classes("max-h-128")

        ui.space()
        content = ["Monthly Growth", "Profit Heatmap", "Drawdown Curve"]
        with ui.tabs() as tabs:
            for title in content:
                ui.tab(title)
        with ui.tab_panels(tabs, value=content[1]).classes("w-full") as panels:
            with ui.tab_panel(content[0]):
                ui.highchart(
                    {
                        "title": {"text": None},
                        "chart": {"type": "column"},
                        "xAxis": {"categories": ["USA", "China", "Brazil", "EU", "Argentina", "India"], "crosshair": True, "accessibility": {"description": "Countries"}},
                        "yAxis": {"min": 0, "title": {"text": "1000 metric tons (MT)"}},
                        "series": [{"name": "Corn", "data": [387749, 280000, 129000, 64300, 54000, 34300]}],
                    }
                ).classes("w-full h-64")
            with ui.tab_panel(content[1]):
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
                            "top": 80,
                            # "left": 30,
                            # "right": 30,
                            "cellSize": ["auto", 13],
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
                            "top": "top",
                        },
                    }
                ).style("width: 960px")

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
