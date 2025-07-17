from nicegui import ui, app

from component import local_file_picker
from models import Broker, Account
from models.enums import AccountType, PlatformType, CurrencyType
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
    # right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    # right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    brokers_df = app.storage.client["brokers_df"]
    accounts_df = app.storage.client["accounts_df"]
    accounts_df["selected"] = False
    accounts_df.loc[1, "selected"] = True
    trades_df = app.storage.client["trades_df"]
    trades_df["year"] = trades_df["exit_time"].dt.year
    symbols_df = app.storage.client["symbols_df"]

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
                        {"headerName": "Name", "field": "name", "checkboxSelection": True, "filter": "agTextColumnFilter", "width": 200, "minWidth": 100},
                        {"headerName": "Broker", "field": "broker", "filter": "agTextColumnFilter", "width": 150, "minWidth": 100},
                        {"headerName": "Type", "field": "type", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                        {"headerName": "Login", "field": "login", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                        {"headerName": "Platform", "field": "platform", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                        {"headerName": "Server", "field": "server", "filter": "agTextColumnFilter", "width": 200, "minWidth": 100},
                        {"headerName": "Path", "field": "path", "filter": "agTextColumnFilter", "minWidth": 100},
                        {"headerName": "Currency", "field": "currency", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
                        {"headerName": "Starting Balance", "field": "starting_balance", "filter": "agNumberColumnFilter", "minWidth": 100},
                        {"headerName": "Current Balance", "field": "current_balance", "filter": "agNumberColumnFilter", "minWidth": 100},
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
                        "name": new_account_data.name,
                        "broker": new_account_data.broker,
                        "login": new_account_data.login,
                        "type": AccountType(new_account_data.type),
                        "platform": PlatformType(new_account_data.platform),
                        "server": new_account_data.server,
                        "currency": CurrencyType(new_account_data.currency),
                        "is_portable": new_account_data.portable,
                        "starting_balance": new_account_data.starting_balance,
                        "current_balance": new_account_data.current_balance,
                        "path": new_account_data.path,
                        "instruments_count": 0,
                        "archived": False,
                        "selected": False,
                    }
                    accounts_grid.options["rowData"].append(new_grid_row)
                    accounts_grid.update()
                    clear_form()

                ui.button("Save", icon="save", on_click=add_account)
                ui.button("Cancel", icon="close", on_click=dialog.close)
                ui.button("Clear", icon="delete_outline", on_click=clear_form)

        with ui.row().classes("w-full items-center justify-between mt-4"):
            ui.label("💲 All Symbols").classes("text-2xl")
            with ui.element():
                ui.button("Import From File", icon="upload", on_click=dialog.open).classes("mr-4")
                ui.button("Add New Symbol", icon="add", on_click=dialog.open)
        with ui.row().classes("w-full"):
            symbols_grid = ui.aggrid(
                options={
                    "defaultColDef": {"resizable": True},
                    "rowSelection": "single",
                    "columnDefs": [
                        {"headerName": "Symbol", "field": "symbol", "checkboxSelection": True, "filter": "agTextColumnFilter"},
                        {"headerName": "Type", "field": "broker", "filter": "agTextColumnFilter"},
                        {"headerName": "Sector", "field": "type", "filter": "agTextColumnFilter"},
                        {"headerName": "Industry", "field": "login", "filter": "agTextColumnFilter"},
                        {"headerName": "Country", "field": "platform", "filter": "agTextColumnFilter"},
                        {"headerName": "Currency", "field": "server", "filter": "agTextColumnFilter"},
                        {"headerName": "Exchange", "field": "path", "filter": "agTextColumnFilter"},
                    ],
                    "rowData": symbols_df.to_dict("records"),
                },
            )
