import pandas as pd
from nicegui import ui, app

from component import local_file_picker
from models import Broker, Account
from models.enums import AccountType, PlatformType, CurrencyType
from data.services import get_all_account_balance_series, get_account_monthly_gain_data, get_pnl_for_a_year
from db.get_session import get_session


class NewAccountData:
    name: str = None
    broker: str = None
    login: str = None
    password: str = None
    type: str = None
    platform: str = None
    path: str = None
    currency: str = None
    starting_balance: float = 0
    current_balance: float = 0
    portable: bool = True
    server: str = None

    def get_db_account(self, session):
        broker = session.query(Broker).filter_by(name=self.broker).first()
        return Account(
            name=self.name,
            broker=broker,
            login=self.login,
            password=self.password,
            type=AccountType(self.type),
            platform=PlatformType(self.platform),
            path=self.path,
            currency=CurrencyType(self.currency),
            starting_balance=self.starting_balance,
            current_balance=self.current_balance,
            portable=self.portable,
            server=self.server,
        )


new_account_data = NewAccountData()


async def accounts():
    right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    brokers_df = app.storage.client["brokers_df"]
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
            update_account_charts(None)

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
            ui.label("📈 Equity Curve").classes("text-2xl")
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
        dialog = ui.dialog()
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("📊 Accounts Summary").classes("text-2xl")
            # ui.button("Add Account", icon="add", on_click=lambda: right_drawer.toggle())
            ui.button("Add Account", icon="add", on_click=dialog.open)
        with ui.row().classes("w-full"):
            accounts_grid = ui.aggrid(
                theme="quartz",
                options={
                    "suppressHorizontalScroll": False,
                    # "ensureDomOrder": True,
                    "defaultColDef": {"resizable": True},
                    "rowSelection": "single",
                    "suppressRowClickSelection": False,
                    "minWidth": 800,
                    "columnDefs": [
                        {"headerName": "Name", "field": "Name", "checkboxSelection": True, "filter": "agTextColumnFilter", "width": 200, "minWidth": 100},
                        {"headerName": "Broker", "field": "Broker", "filter": "agTextColumnFilter", "width": 150, "minWidth": 100},
                        {"headerName": "Type", "field": "Type", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                        {"headerName": "Login", "field": "Login", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                        {"headerName": "Platform", "field": "Platform", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                        {"headerName": "Server", "field": "Server", "filter": "agTextColumnFilter", "width": 200, "minWidth": 100},
                        {"headerName": "Path", "field": "Path", "filter": "agTextColumnFilter", "minWidth": 100},
                        {"headerName": "Currency", "field": "Currency", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                        {"headerName": "Starting Balance", "field": "Starting Balance", "filter": "agNumberColumnFilter", "minWidth": 100},
                        {"headerName": "Current Balance", "field": "Current Balance", "filter": "agNumberColumnFilter", "minWidth": 100},
                    ],
                    "initialState": {"rowSelection": ["0"]},
                    "rowData": accounts_df.to_dict("records"),
                },
            ).on("cellClicked", lambda e: on_account_selected(e))

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
                ).classes("w-full h-[295px]")

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
                                "top": 80,
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
                    ).classes("w-[1024px] pt-2")
                    # .style("height: 400px;")
                )

        # if right_drawer and right_drawer_rendered_by != "accounts":
        #     app.storage.client["right_drawer_rendered_by"] = "accounts"
        #     right_drawer.clear()

        with dialog, ui.card():
            ui.markdown("##### ➕ Add Account")

            async def pick_file() -> None:
                result = await local_file_picker("~", multiple=False)
                new_account_data.path = result[0]

            with ui.grid().classes("w-full"):
                n = ui.input(label="Name", value="test").classes("w-full").bind_value_to(new_account_data, "name")
                b = ui.select(options=brokers_df["name"].tolist(), label="Broker", value=brokers_df["name"].tolist()[-1]).classes("w-full").bind_value_to(new_account_data, "broker")
                l = ui.input(label="Login", value=12345).classes("w-full").bind_value_to(new_account_data, "login")
                p = ui.input(label="Password", value="test", password=True, password_toggle_button=True).classes("w-full").bind_value_to(new_account_data, "password")
                t = (
                    ui.select(label="Type", options=[p.value for p in AccountType], value="Live")
                    .classes("w-full")
                    .bind_value_to(new_account_data, "type", lambda x: AccountType(x) if x is not None else None)
                )
                pf = (
                    ui.select(label="Platform", options=[p.value for p in PlatformType], value="MT4")
                    .classes("w-full")
                    .bind_value_to(new_account_data, "platform", lambda x: PlatformType(x) if x is not None else None)
                )
                s = ui.input(label="Server", value="test-server").classes("w-full").bind_value_to(new_account_data, "server")
                c = (
                    ui.select([p.value for p in CurrencyType], label="Currency", value="USD")
                    .classes("w-full")
                    .bind_value_to(new_account_data, "currency", lambda x: CurrencyType(x) if x is not None else None)
                )
                ip = ui.checkbox("Is Portable", value=True).classes("w-full").bind_value_to(new_account_data, "portable")
            with ui.row():
                ui.button("Choose file", on_click=pick_file, icon="folder")
                fpl = ui.label().classes("w-full").bind_text_from(new_account_data, "path")
            with ui.row():

                def clear_form():
                    # new_account_data = Account()
                    new_account_data.name = None
                    n.value = None
                    n.update()
                    new_account_data.broker = None
                    b.value = None
                    b.update()
                    new_account_data.login = None
                    l.value = None
                    l.update()
                    new_account_data.password = None
                    p.value = None
                    p.update()
                    new_account_data.type = None
                    t.value = None
                    t.update()
                    new_account_data.platform = None
                    pf.value = None
                    pf.update()
                    new_account_data.server = None
                    s.value = None
                    s.update()
                    new_account_data.currency = None
                    c.value = None
                    c.update()
                    new_account_data.portable = True
                    ip.value = True
                    ip.update()
                    new_account_data.path = None
                    fpl.text = None
                    fpl.update()

                def add_account():
                    with get_session() as session:
                        new_account_db_data = new_account_data.get_db_account(session)
                        session.add(new_account_db_data)
                        session.commit()
                        dialog.close()
                        ui.notify("Account added successfully", type="positive", position="top-right", duration=3000)

                    new_grid_row = {
                        # "ID": new_account_data.id,
                        "Name": new_account_data.name,
                        "Broker": new_account_data.broker,
                        "Login": new_account_data.login,
                        "Type": AccountType(new_account_data.type),
                        "Platform": PlatformType(new_account_data.platform),
                        "Server": new_account_data.server,
                        "Currency": CurrencyType(new_account_data.currency),
                        "Is Portable": new_account_data.portable,
                        "Starting Balance": new_account_data.starting_balance,
                        "Current Balance": new_account_data.current_balance,
                        "Path": new_account_data.path,
                        "Instruments #": 0,
                        "Archived": False,
                        "selected": False,
                    }
                    accounts_grid.options["rowData"].append(new_grid_row)
                    accounts_grid.update()
                    clear_form()

                ui.button("Save", icon="save", on_click=add_account)
                ui.button("Cancel", icon="close", on_click=dialog.close)
                ui.button("Clear", icon="delete_outline", on_click=clear_form)
