from nicegui import ui, app

from dto import NewAccountData
from component import local_file_picker
from models.enums import AccountType, PlatformType, CurrencyType
from data.commands import add_account


new_account_data = NewAccountData()


async def accounts():
    # right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    # right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    brokers_df = app.storage.client["brokers_df"]
    accounts_df = app.storage.client["accounts_df"]
    accounts_df["selected"] = False
    accounts_df.loc[1, "selected"] = True
    trades_df = app.storage.client["trades_df"]
    trades_df["year"] = trades_df["exit_time"].dt.year
    symbols_df = app.storage.client["symbols_df"]
    instruments_df = app.storage.client["instruments_df"]

    state = {
        "account_selected": accounts_df["name"].iloc[0],
    }

    with ui.column().classes("w-full h-full text-lg"):
        dialog = ui.dialog()
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("🏦 Accounts Summary").classes("text-2xl")
            with ui.element():
                ui.button("Archive Selected", icon="archive", on_click=dialog.open).classes("mr-4")
                ui.button("Add New Account", icon="add", on_click=dialog.open)

        with ui.row().classes("w-full"):
            accounts_grid = ui.aggrid(
                options={
                    "suppressHorizontalScroll": False,
                    "defaultColDef": {"resizable": True},
                    "rowSelection": "single",
                    "suppressRowClickSelection": False,
                    "columnDefs": [
                        {"headerName": "ID", "field": "id", "filter": "agNumberColumnFilter", "minWidth": 100, "hide": True},
                        {"headerName": "Name", "field": "name", "checkboxSelection": True, "filter": "agTextColumnFilter", "minWidth": 150},
                        {"headerName": "Broker", "field": "broker", "filter": "agTextColumnFilter", "minWidth": 100},
                        {"headerName": "Type", "field": "type", "filter": "agTextColumnFilter", "minWidth": 70},
                        {"headerName": "Login", "field": "login", "filter": "agTextColumnFilter", "minWidth": 90},
                        {"headerName": "Platform", "field": "platform", "filter": "agTextColumnFilter", "minWidth": 80},
                        {"headerName": "Server", "field": "server", "filter": "agTextColumnFilter", "minWidth": 150},
                        {"headerName": "Path", "field": "path", "filter": "agTextColumnFilter", "minWidth": 100},
                        {"headerName": "Currency", "field": "currency", "filter": "agTextColumnFilter", "minWidth": 100, "hide": True},
                        {
                            "headerName": "Starting Balance",
                            "field": "starting_balance",
                            "filter": "agNumberColumnFilter",
                            "minWidth": 100,
                            ":valueFormatter": "params => params.data.currency_symbol + ' '+ params.value.toFixed(2)",
                        },
                        {
                            "headerName": "Current Balance",
                            "field": "current_balance",
                            "filter": "agNumberColumnFilter",
                            "minWidth": 100,
                            ":valueFormatter": "params => params.data.currency_symbol + ' '+ params.value.toFixed(2)",
                        },
                        {"headerName": "Portable", "field": "portable", "filter": "agTextColumnFilter", "minWidth": 100},
                        {"headerName": "Leverage", "field": "leverage", "filter": "agNumberColumnFilter", "minWidth": 100},
                        {"headerName": "MT5 Name", "field": "mt5_name", "filter": "agTextColumnFilter", "minWidth": 100},
                        {"headerName": "Company", "field": "mt5_company", "filter": "agTextColumnFilter", "minWidth": 100},
                        {"headerName": "Profit", "field": "profit", "filter": "agNumberColumnFilter", "minWidth": 100},
                    ],
                    "initialState": {"rowSelection": ["0"]},
                    "rowData": accounts_df.to_dict("records"),
                },
            )  # .on("cellClicked", lambda e: on_account_selected(e))

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
                # c = (
                #     ui.select([p.value for p in CurrencyType], label="Currency", value="USD")
                #     .classes("w-full")
                #     .bind_value_to(new_account_data, "currency", lambda x: CurrencyType(x) if x is not None else None)
                # )
                ip = ui.checkbox("Is Portable", value=True).classes("w-full").bind_value_to(new_account_data, "portable")
            with ui.row():
                ui.button("Choose file", on_click=pick_file, icon="folder")
                fpl = ui.label().classes("w-full").bind_text_from(new_account_data, "path")
            with ui.row():

                def clear_form():
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
                    # c.value = None
                    # c.update()
                    new_account_data.portable = True
                    ip.value = True
                    ip.update()
                    new_account_data.path = None
                    fpl.text = None
                    fpl.update()

                def on_save_new_account():
                    new_grid_row = add_account(new_account_data)
                    print(new_grid_row["currency_symbol"])
                    accounts_grid.options["rowData"].append(new_grid_row)
                    accounts_grid.update()
                    dialog.close()
                    clear_form()
                    ui.notify("Account added successfully", type="positive", position="top-right", duration=3000)

                ui.button("Save", icon="save", on_click=on_save_new_account)
                ui.button("Cancel", icon="close", on_click=dialog.close)
                ui.button("Clear", icon="delete_outline", on_click=clear_form)

        with ui.row().classes("w-full items-center justify-between mt-4"):
            ui.label("💲 All Symbols").classes("text-2xl")
            with ui.element():
                ui.button("Import From File", icon="upload", on_click=dialog.open).classes("mr-4")
                ui.button("Add New Symbol", icon="add", on_click=dialog.open)
        # with ui.row().classes("w-full"):
        #     symbols_grid = ui.aggrid(
        #         options={
        #             "defaultColDef": {"resizable": True},
        #             "rowSelection": "single",
        #             "columnDefs": [
        #                 {"headerName": "Symbol", "field": "symbol", "checkboxSelection": True, "filter": "agTextColumnFilter"},
        #                 {"headerName": "Type", "field": "broker", "filter": "agTextColumnFilter"},
        #                 {"headerName": "Sector", "field": "type", "filter": "agTextColumnFilter"},
        #                 {"headerName": "Industry", "field": "login", "filter": "agTextColumnFilter"},
        #                 {"headerName": "Country", "field": "platform", "filter": "agTextColumnFilter"},
        #                 {"headerName": "Currency", "field": "server", "filter": "agTextColumnFilter"},
        #                 {"headerName": "Exchange", "field": "path", "filter": "agTextColumnFilter"},
        #             ],
        #             "rowData": symbols_df.to_dict("records"),
        #         },
        #     )

        with ui.row().classes("w-full items-center justify-between mt-4"):
            ui.label("💱 All Instruments").classes("text-2xl")

        # with ui.row().classes("w-full"):
        #     instruments_grid = ui.aggrid(
        #         options={
        #             "defaultColDef": {"resizable": True},
        #             "rowSelection": "single",
        #             "columnDefs": [
        #                 {"headerName": "Ticker", "field": "ticker", "checkboxSelection": True, "filter": "agTextColumnFilter"},
        #                 {"headerName": "Symbol", "field": "symbol", "filter": "agTextColumnFilter"},
        #                 {"headerName": "Account Name", "field": "account_name", "filter": "agTextColumnFilter"},
        #                 {"headerName": "Broker", "field": "account_broker", "filter": "agTextColumnFilter"},
        #                 # {"headerName": "Sector", "field": "type", "filter": "agTextColumnFilter"},
        #                 # {"headerName": "Industry", "field": "login", "filter": "agTextColumnFilter"},
        #                 # {"headerName": "Country", "field": "platform", "filter": "agTextColumnFilter"},
        #                 # {"headerName": "Currency", "field": "server", "filter": "agTextColumnFilter"},
        #                 # {"headerName": "Exchange", "field": "path", "filter": "agTextColumnFilter"},
        #             ],
        #             "rowData": instruments_df.to_dict("records"),
        #         },
        #     )
