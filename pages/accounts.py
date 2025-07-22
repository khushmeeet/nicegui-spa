import json
import pandas as pd
from nicegui import ui, app

from dto import NewAccountData, NewSymbolData
from component import local_file_picker
from models import Symbol
from models.enums import AccountType, PlatformType, SymbolType
from data.commands import add_account, add_symbol, delete_symbols, add_array_of_dicts


new_account_data = NewAccountData()
new_symbol_data = NewSymbolData()
file_input_id = "my_file_input"
file_input_event_handler_script = f"""
    const input = document.getElementById("{file_input_id}");
    if (!input.hasListener) {{
        input.addEventListener("change", function(evt) {{
            const file = evt.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {{
                const text = e.target.result;
                let parsedData = null;

                try {{
                    if (file.name.endsWith('.json')) {{
                        parsedData = JSON.parse(text);
                    }} else if (file.name.endsWith('.csv')) {{
                        const lines = text.trim().split('\\n');
                        const headers = lines[0].split(',');
                        parsedData = lines.slice(1).map(line => {{
                            const values = line.split(',');
                            let obj = {{}};
                            headers.forEach((header, i) => obj[header.trim()] = values[i].trim());
                            return obj;
                        }});
                    }} else {{
                        parsedData = {{error: "Unsupported file format"}};
                    }}
                }} catch(error) {{
                    console.error("Error parsing file content:", error);
                    parsedData = {{error: "Error parsing file content", details: error.message}};
                }}

                const event = new CustomEvent("file_content", {{
                    detail: JSON.stringify(parsedData),
                    bubbles: true,
                    composed: true
                }});
                input.dispatchEvent(event);
            }};
            reader.readAsText(file);
        }});
        input.hasListener = true;
    }}
"""


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
        # "account_selected": accounts_df["name"].iloc[0],
        "enable_delete_symbols_button": False,
    }
    ui.html("<style>.multi-line-notification { white-space: pre-line; }</style>")
    with ui.column().classes("w-full h-full text-lg"):
        add_new_account_dialog = ui.dialog()
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("🏦 Accounts Summary").classes("text-2xl")
            with ui.element():
                ui.button("Archive Selected", icon="archive", on_click=add_new_account_dialog.open).classes("mr-4")
                ui.button("Add New Account", icon="add", on_click=add_new_account_dialog.open)

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
                        {"headerName": "Currency", "field": "currency", "filter": "agTextColumnFilter", "minWidth": 100, "hide": True},
                        {
                            "headerName": "Starting Balance",
                            "field": "starting_balance",
                            "filter": "agNumberColumnFilter",
                            "minWidth": 100,
                            "type": "rightAligned",
                            ":valueFormatter": "params => params.data.currency_symbol + ' '+ params.value.toFixed(2)",
                            "hide": True,
                        },
                        {
                            "headerName": "Balance",
                            "field": "current_balance",
                            "filter": "agNumberColumnFilter",
                            "minWidth": 100,
                            "type": "rightAligned",
                            ":valueFormatter": "params => params.data.currency_symbol + ' '+ params.value.toFixed(2)",
                        },
                        {"headerName": "Profit", "field": "profit", "filter": "agNumberColumnFilter", "minWidth": 100, "type": "rightAligned"},
                        {"headerName": "Leverage", "field": "leverage", "filter": "agNumberColumnFilter", "minWidth": 100},
                        {"headerName": "MT5 Name", "field": "mt5_name", "filter": "agTextColumnFilter", "minWidth": 100},
                        {"headerName": "Company", "field": "mt5_company", "filter": "agTextColumnFilter", "minWidth": 100},
                        {"headerName": "Portable", "field": "portable", "filter": "agTextColumnFilter", "minWidth": 100, "editable": True},
                        {"headerName": "Path", "field": "path", "filter": "agTextColumnFilter", "minWidth": 100},
                    ],
                    "initialState": {"rowSelection": ["0"]},
                    "rowData": accounts_df[::-1].to_dict("records"),
                },
            )

        with add_new_account_dialog, ui.card():
            ui.markdown("##### ➕ Add Account")

            async def pick_file() -> None:
                result = await local_file_picker("~", multiple=False)
                new_account_data.path = result[0]

            with ui.grid().classes("w-full"):
                n = ui.input(label="Name").classes("w-full").bind_value_to(new_account_data, "name")
                b = ui.select(options=brokers_df["name"].tolist(), label="Broker").classes("w-full").bind_value_to(new_account_data, "broker")
                l = ui.input(label="Login").classes("w-full").bind_value_to(new_account_data, "login")
                p = ui.input(label="Password", password=True, password_toggle_button=True).classes("w-full").bind_value_to(new_account_data, "password")
                t = ui.select(label="Type", options=[p.value for p in AccountType]).classes("w-full").bind_value_to(new_account_data, "type", lambda x: AccountType(x) if x is not None else None)
                pf = (
                    ui.select(label="Platform", options=[p.value for p in PlatformType])
                    .classes("w-full")
                    .bind_value_to(new_account_data, "platform", lambda x: PlatformType(x) if x is not None else None)
                )
                s = ui.input(label="Server").classes("w-full").bind_value_to(new_account_data, "server")
                ip = ui.checkbox("Is Portable", value=True).classes("w-full").bind_value_to(new_account_data, "portable")
            with ui.row():
                ui.button("Choose file", on_click=pick_file, icon="folder")
                fpl = ui.label().classes("w-full").bind_text_from(new_account_data, "path")
            with ui.row():

                def clear_new_account_form():
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
                    new_account_data.portable = True
                    ip.value = True
                    ip.update()
                    new_account_data.path = None
                    fpl.text = None
                    fpl.update()

                def on_save_new_account():
                    new_grid_row = add_account(new_account_data)
                    accounts_grid.options["rowData"].append(new_grid_row)
                    accounts_grid.update()
                    add_new_account_dialog.close()
                    clear_new_account_form()
                    ui.notify("Account added successfully", type="positive", position="top-right", duration=3000)

                ui.button("Save", icon="save", on_click=on_save_new_account)
                ui.button("Cancel", icon="close", on_click=add_new_account_dialog.close)
                ui.button("Clear", icon="delete_outline", on_click=clear_new_account_form)

        with ui.row().classes("w-full items-center justify-between mt-4"):
            ui.label("💲 All Symbols").classes("text-2xl")
            add_new_symbol_dialog = ui.dialog()
            with ui.element():
                file_input = ui.html(f"""<input type="file" id="{file_input_id}" accept=".csv,.json" style="visibility:hidden; position: absolute; left: -9999px" />""")
                ui.button("Import From File", icon="upload", on_click=lambda: ui.run_javascript(f'document.getElementById("{file_input_id}").click();')).classes("mr-4")
                ui.button("Add New", icon="add", on_click=add_new_symbol_dialog.open).classes("mr-4")
                delete_symbols_button = ui.button("Delete", icon="delete_outline").bind_enabled_from(state, "enable_delete_symbols_button")
        with ui.row().classes("w-full"):
            symbols_grid = ui.aggrid(
                options={
                    "defaultColDef": {"resizable": True},
                    "rowSelection": "single",
                    "columnDefs": [
                        {"headerName": "ID", "field": "id", "filter": "agNumberColumnFilter", "minWidth": 100, "hide": True},
                        {"headerName": "Symbol", "field": "symbol", "checkboxSelection": True, "filter": "agTextColumnFilter"},
                        {"headerName": "Description", "field": "description", "filter": "agTextColumnFilter"},
                        {"headerName": "Type", "field": "type", "filter": "agTextColumnFilter"},
                    ],
                    "rowData": symbols_df[::-1].to_dict("records"),
                    "rowSelection": "multiple",
                    ":getRowId": "(params) => params.data.id.toString()",
                },
            )

            async def on_symbol_selected(e):
                rows = await symbols_grid.get_selected_rows()
                state["enable_delete_symbols_button"] = bool(rows)

            symbols_grid.on("rowSelected", on_symbol_selected)

            async def on_delete_selected_symbols(e):
                rows = await symbols_grid.get_selected_rows()
                delete_symbols([row["id"] for row in rows])
                symbols_grid.run_grid_method("applyTransaction", {"remove": rows})
                ui.notify("Symbols deleted successfully", type="positive", position="top-right", duration=3000)

            def load_symbols_from_file(e):
                content = json.loads(e.args["detail"])
                ui.run_javascript(f'document.getElementById("{file_input_id}").value = "";')
                if "error" in content:
                    error = content["error"]
                    details = content.get("details", None)
                    details = None
                    ui.notify(
                        f"Error loading symbols: {error}" + ("\n{details}" if details else ""),
                        multi_line=True,
                        type="negative",
                        position="top-right",
                        duration=3000,
                        classes="multi-line-notification",
                    )
                    return
                try:
                    add_array_of_dicts(Symbol, content)
                except Exception as e:
                    print(f"Error importing symbols: {e}")
                    ui.notify(f"Error importing symbols: \n{str(e)}", multi_line=True, type="negative", position="top-right", duration=3000, classes="multi-line-notification")
                    return

            delete_symbols_button.on_click(on_delete_selected_symbols)
            ui.run_javascript(file_input_event_handler_script)
            file_input.on("file_content", load_symbols_from_file)

        with add_new_symbol_dialog, ui.card():
            ui.markdown("##### ➕ Add Account")
            s = ui.input(label="Symbol").classes("w-full").bind_value_to(new_symbol_data, "symbol")
            d = ui.input(label="Description").classes("w-full").bind_value_to(new_symbol_data, "description")
            t = ui.select(label="Type", options=[p.value for p in SymbolType]).classes("w-full").bind_value_to(new_symbol_data, "type", lambda x: SymbolType(x) if x is not None else None)

            def clear_new_symbol_form():
                new_symbol_data.symbol = None
                s.value = None
                s.update()
                new_symbol_data.description = None
                d.value = None
                d.update()
                new_symbol_data.type = None
                t.value = None
                t.update()

            def on_save_new_symbol():
                new_grid_row = add_symbol(new_symbol_data)
                symbols_grid.run_grid_method("applyTransaction", {"add": [new_grid_row], "addIndex": 0})
                add_new_symbol_dialog.close()
                clear_new_symbol_form()
                ui.notify("Symbol added successfully", type="positive", position="top-right", duration=3000)

            with ui.row():
                ui.button("Save", icon="save", on_click=on_save_new_symbol)
                ui.button("Cancel", icon="close", on_click=add_new_symbol_dialog.close)
                ui.button("Clear", icon="delete_outline", on_click=clear_new_symbol_form)

        with ui.row().classes("w-full items-center justify-between mt-4"):
            ui.label("💱 All Instruments").classes("text-2xl")

        with ui.row().classes("w-full"):
            instruments_grid = ui.aggrid(
                options={
                    "defaultColDef": {"resizable": True},
                    "rowSelection": "single",
                    "columnDefs": [
                        {"headerName": "Ticker", "field": "ticker", "checkboxSelection": True, "filter": "agTextColumnFilter"},
                        {"headerName": "Symbol", "field": "symbol", "filter": "agTextColumnFilter"},
                        {"headerName": "Account Name", "field": "account_name", "filter": "agTextColumnFilter"},
                        {"headerName": "Broker", "field": "account_broker", "filter": "agTextColumnFilter"},
                        # {"headerName": "Sector", "field": "type", "filter": "agTextColumnFilter"},
                        # {"headerName": "Industry", "field": "login", "filter": "agTextColumnFilter"},
                        # {"headerName": "Country", "field": "platform", "filter": "agTextColumnFilter"},
                        # {"headerName": "Currency", "field": "server", "filter": "agTextColumnFilter"},
                        # {"headerName": "Exchange", "field": "path", "filter": "agTextColumnFilter"},
                    ],
                    "rowData": instruments_df.to_dict("records"),
                },
            )
