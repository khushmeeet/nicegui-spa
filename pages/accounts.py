import pandas as pd
from nicegui import ui, app

from data.services import get_all_account_balance_series, get_account_monthly_gain_data, get_pnl_for_a_year


def accounts():
    right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    accounts_df = app.storage.client["accounts_df"]
    accounts_df["selected"] = False
    accounts_df.loc[1, "selected"] = True
    trades_df = app.storage.client["trades_df"]
    trades_df["year"] = trades_df["exit_time"].dt.year
    available_years = sorted(trades_df["year"].unique(), reverse=True)
    state = {
        "account_selected": accounts_df["Name"].iloc[0],
    }

    def update_state(**kwargs):
        for k, v in kwargs.items():
            state[k] = v

    with ui.column().classes("w-full h-full text-lg"):

        def on_equity_curve_percent_value_toggle(e):
            mode = e.value
            chart.options["plotOptions"]["series"]["compare"] = mode.lower() if mode == "Percent" else None
            if mode == "Percent":
                chart.options["yAxis"]["labels"]["format"] = "{value}%"
                chart.options["tooltip"]["pointFormat"] = '<span style="color:{series.color}">{series.name}</span>: {point.change:.1f}%<br/>'
            else:
                chart.options["yAxis"]["labels"]["format"] = None
                chart.options["tooltip"]["pointFormat"] = '<span style="color:{series.color}">{series.name}</span>: {point.y:.2f}<br/>'
            chart.update()

        def update_bar_chart():
            series, categories = get_account_monthly_gain_data(state["account_selected"], range_selector_1.value, mode_selector_1.value, trades_df)
            bar_chart.options["series"] = [series] if series else []
            bar_chart.options["xAxis"]["categories"] = categories
            bar_chart.options["yAxis"]["labels"]["format"] = "{value}%" if mode_selector_1.value == "Percent" else None
            bar_chart.options["plotOptions"]["column"]["dataLabels"]["format"] = "{point.y:.2f}%" if mode_selector_1.value == "Percent" else None
            bar_chart.update()

        def on_account_selected(e):
            update_state(account_selected=e.args["data"]["Name"])
            update_bar_chart()
            update_heatmap()

        def update_account_charts(e):
            update_bar_chart()
            update_heatmap()

        def update_heatmap():
            year = range_selector_1.value if range_selector_1.value in [str(x) for x in available_years] else available_years[0]
            data, min_value, max_value = get_pnl_for_a_year(state["account_selected"], year, trades_df, mode_selector_1.value)
            heatmap.options["calendar"]["range"] = year
            heatmap.options["series"]["data"] = data
            heatmap.options["visualMap"]["min"] = min_value
            heatmap.options["visualMap"]["max"] = max_value
            if mode_selector_1.value == "Percent":
                heatmap.options["visualMap"][":formatter"] = "value => value.toFixed(2) + '%'"
                heatmap.options["tooltip"][":formatter"] = (
                    "params => `${params.marker}<b>${params.value[1].toFixed(2)}%</b> (${new Date(params.value[0]).getDate()} ${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][new Date(params.value[0]).getMonth()]} ${new Date(params.value[0]).getFullYear()})`",
                )
            else:
                heatmap.options["visualMap"][":formatter"] = "value => value.toFixed(2)"
                heatmap.options["tooltip"][":formatter"] = (
                    "params => `${params.marker}<b>${params.value[1].toFixed(2)}</b> (${new Date(params.value[0]).getDate()} ${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][new Date(params.value[0]).getMonth()]} ${new Date(params.value[0]).getFullYear()})`",
                )
            heatmap.update()

        with ui.row().classes("w-full justify-between"):
            ui.label("Equity Curve").classes("text-2xl")
            ui.toggle(["Value", "Percent"], value="Value", on_change=on_equity_curve_percent_value_toggle)

        chart = ui.highchart(
            type="stockChart",
            extras=["stock"],
            options={
                "chart": {"type": "line", "spacingRight": 30},
                "title": {"text": None},
                "series": get_all_account_balance_series(accounts_df, trades_df),
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

        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Accounts Summary").classes("text-2xl")
            ui.button("Add Account", icon="add", on_click=lambda: right_drawer.toggle())

        ui.aggrid.from_pandas(
            accounts_df,
            theme="quartz",
            options={
                "domLayout": "autoHeight",
                "suppressHorizontalScroll": False,
                "ensureDomOrder": True,
                "defaultColDef": {"resizable": True},
                "rowSelection": "single",
                "suppressRowClickSelection": False,
                "minWidth": 800,
                "columnDefs": [
                    {"headerName": "Name", "field": "Name", "filter": "agTextColumnFilter", "width": 200, "minWidth": 100},
                    {"headerName": "Broker", "field": "Broker", "filter": "agTextColumnFilter", "width": 150, "minWidth": 100},
                    {"headerName": "Type", "field": "Type", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                    {"headerName": "Login", "field": "Login", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                    {"headerName": "Platform", "field": "Platform", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                    {"headerName": "Server", "field": "Server", "filter": "agTextColumnFilter", "width": 200, "minWidth": 100},
                    {"headerName": "Path", "field": "Path", "filter": "agTextColumnFilter", "minWidth": 100},
                    {"headerName": "Currency", "field": "Currency", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                    {"headerName": "Starting Balance", "field": "Starting Balance", "filter": "agTextColumnFilter", "minWidth": 100},
                    {"headerName": "Current Balance", "field": "Current Balance", "filter": "agTextColumnFilter", "minWidth": 100},
                ],
                "initialState": {"rowSelection": ["0"]},
            },
        ).on("cellClicked", lambda e: on_account_selected(e)).classes("h-[315px]")

        with ui.row().classes("w-full items-center justify-between pr-1"):
            range_selector_1 = ui.toggle(options=["YTD", "1 Year"] + [str(year) for year in available_years], value="1 Year").on_value_change(update_account_charts)
            mode_selector_1 = ui.toggle(["Value", "Percent"], value="Percent").on_value_change(update_account_charts)

        tab_content = ["Monthly Growth", "Profit Heatmap", "Drawdown Curve"]
        with ui.tabs() as tabs:
            for title in tab_content:
                ui.tab(title)

        with ui.tab_panels(tabs, value=tab_content[0]).classes("w-full p-0 h-128 h-full"):
            with ui.tab_panel(tab_content[0]).classes("p-0 h-128 h-full"):
                series, categories = get_account_monthly_gain_data(state["account_selected"], range_selector_1.value, mode_selector_1.value, trades_df)
                bar_chart = ui.highchart(
                    {
                        "chart": {"type": "column"},
                        "title": {"text": None},
                        "xAxis": {"categories": categories},
                        "yAxis": {"title": {"text": None}, "labels": {"format": "{value}%"}},
                        "tooltip": {"enabled": False},
                        "legend": {"enabled": False},
                        "series": [series] if series else [],
                        "plotOptions": {
                            "column": {"dataLabels": {"enabled": True, "inside": False, "style": {"fontSize": "12px"}, "format": "{point.y:.2f}%"}},
                            "series": {"zones": [{"value": 0, "color": "#fa4b42"}, {"color": "#00e272"}]},
                        },
                    }
                ).classes("w-full")

            with ui.tab_panel(tab_content[1]).classes("p-0 h-128"):
                data, min_value, max_value = get_pnl_for_a_year(state["account_selected"], available_years[0], trades_df, mode_selector_1.value)
                heatmap = (
                    ui.echart(
                        {
                            "series": {
                                "type": "heatmap",
                                "coordinateSystem": "calendar",
                                "calendarIndex": 0,
                                "data": data,
                            },
                            "calendar": {
                                "top": 100,
                                "left": 80,
                                "cellSize": ["auto", 18],
                                "range": available_years[0],
                                "itemStyle": {"borderWidth": 0.5},
                                "yearLabel": {"show": True},
                            },
                            "tooltip": {
                                "position": "top",
                                ":formatter": "params => `${params.marker}<b>${params.value[1].toFixed(2)}%</b> (${new Date(params.value[0]).getDate()} ${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][new Date(params.value[0]).getMonth()]} ${new Date(params.value[0]).getFullYear()})`",
                            },
                            "visualMap": {
                                "min": min_value,
                                "max": max_value,
                                "calculable": True,
                                "orient": "horizontal",
                                "left": "center",
                                # "bottom": "40",
                                "top": "top",
                                "itemHeight": 400,
                                "inRange": {"color": ["#fa4b42", "#fe7f35", "#feef6a", "#00e272", "#2caffe", "#544fc5"]},
                                ":formatter": "value => value.toFixed(2) + '%'",
                            },
                        }
                    )
                    .classes("w-[1024px] pt-2 h-128")
                    .style("height: 400px;")
                )

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
