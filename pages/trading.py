import pprint
from enum import Enum
from nicegui import ui, app

from utils.tree import build_tree
from utils.case_converter import title_to_snake
from models.enums import TradeSuccessProbabilityType, TradingMindState, DirectionType, OrderType, CurrencyType, AccountType, PlatformType


MAX_SYMBOLS_PER_TRADE = 10


async def trading():
    right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    accounts_df = app.storage.client["accounts_df"]
    strategies_df = app.storage.client["strategies_df"]
    symbols_df = app.storage.client["symbols_df"]
    brokers_df = app.storage.client["brokers_df"]
    trade_direction_types = [p.value for p in DirectionType]
    trade_order_types = [p.value for p in OrderType]

    tree_enum_mapping = {
        "Type": AccountType,
        "Broker": Enum(
            "BrokerType",
            {title_to_snake(item): item for item in brokers_df["name"].tolist()},
            type=str,
        ),
        "Platform": PlatformType,
    }
    grouping_list = list(tree_enum_mapping.keys())

    state = {
        "symbols_grid_visible": False,
        "trade_items": [],
        "common_sl_pips": 15.0,
        "common_tp_pips": 15.0,
        "selected_accounts": set(),
    }

    ui.add_css(
        """
    .custom-tooltip {
        white-space: normal;
        padding: 5px;
        background-color: #f9f9f9;
        border: 1px solid #ccc;
    }
    """
    )

    ui.markdown("## 🏦 Trading")

    with ui.splitter(value=27) as splitter:
        with splitter.before:
            with ui.column().classes("w-full pr-4 pb-4"):

                def add_account_tree_to_state(e):
                    for value in e.value:
                        state["selected_accounts"].add(value)

                grouping_select = ui.select(grouping_list, multiple=True, label="Grouping", with_input=True, clearable=True, value=grouping_list[:2]).props("outlined use-chips").classes("w-full")
                with grouping_select.add_slot("prepend"):
                    ui.icon("account_tree")

                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Select Account(s)")
                    with ui.button_group().props("flat").classes("bg-grey-2 text-grey-14"):
                        tree_expand_btn = ui.button(icon="add", color="text-grey-14").props("flat dense")
                        tree_collapse_btn = ui.button(icon="remove", color="text-grey-14").props("flat dense")
                account_tree = (
                    ui.tree(
                        build_tree(accounts_df, grouping_list[:2], enum_mapping=tree_enum_mapping, ungroup_keys=grouping_list[-1]),
                        label_key="label",
                        tick_strategy="leaf",
                        on_tick=add_account_tree_to_state,
                    )
                    .classes("w-full")
                    .expand()
                )

                def on_grouping_change(e):
                    grouping_keys = e.value
                    ungrouped_keys = list(set(grouping_list) - set(grouping_keys))
                    account_tree._props["nodes"] = build_tree(accounts_df, grouping_keys, enum_mapping=tree_enum_mapping, ungroup_keys=ungrouped_keys)
                    account_tree.update()
                    account_tree.expand()

                grouping_select.on_value_change(on_grouping_change)
                tree_expand_btn.on_click(account_tree.expand)
                tree_collapse_btn.on_click(account_tree.collapse)

        with splitter.after:
            with ui.column().classes("w-full pl-4 pb-4"):
                with ui.row():
                    strategy = ui.select(strategies_df["name"].to_list(), label="Strategy", with_input=True, clearable=True).props("outlined").classes("w-64")
                    risk = ui.number(label="Trade Risk", value=1.0, step=0.01, min=0.1, max=5.0, precision=3, format="%.2f").props("outlined").classes("w-64")
                    probability = ui.select([p.value for p in TradeSuccessProbabilityType], label="Probability", with_input=True, clearable=True).props("outlined ").classes("w-64")
                    mindstate = ui.select([p.value for p in TradingMindState], label="Mindstate", with_input=True, clearable=True).props("outlined").classes("w-64")
                    with strategy.add_slot("prepend"):
                        ui.icon("tips_and_updates")
                    with risk.add_slot("prepend"):
                        ui.icon("percent")
                    with probability.add_slot("prepend"):
                        ui.icon("casino")
                    with mindstate.add_slot("prepend"):
                        ui.icon("psychology")
                with ui.expansion("Common", icon="join_inner", value=True).classes(" w-full border p-0"):
                    with ui.row().classes("w-full"):
                        sl_pips = ui.number(label="Stop Loss (pips)", value=15.0, step=0.1, min=5.0, precision=1, format="%.1f").props("outlined").classes("w-64")
                        tp_pips = ui.number(label="Take Profit (pips)", value=15.0, step=0.1, min=5.0, precision=1, format="%.1f").props("outlined").classes("w-64")
                        direction = ui.select(trade_direction_types, value=trade_direction_types[0], label="Direction", with_input=True, clearable=True).props("outlined").classes("w-64")
                        order_type = ui.select(trade_order_types, value=trade_order_types[0], label="Order Type", with_input=True, clearable=True).props("outlined").classes("w-64")
                        direction_currency = ui.select([p.value for p in CurrencyType], label="Direction based on currency", with_input=True, clearable=True).props("outlined").classes("w-64")
                        with sl_pips.add_slot("prepend"):
                            ui.icon("trending_down")
                        with tp_pips.add_slot("prepend"):
                            ui.icon("trending_up")
                        with direction.add_slot("prepend"):
                            ui.icon("import_export")
                        with order_type.add_slot("prepend"):
                            ui.icon("shopping_cart")
                        with direction_currency.add_slot("prepend"):
                            ui.icon("currency_exchange")

                symbols_select = ui.select(symbols_df["symbol"].to_list(), label="Symbols", multiple=True, with_input=True, clearable=True).props("use-chips outlined").classes("w-full ")

                with symbols_select.add_slot("prepend"):
                    ui.icon("monetization_on")

                with ui.row().classes("w-full justify-end"):
                    execute_btn = ui.button("Execute", icon="rocket_launch").bind_visibility_from(state, "symbols_grid_visible")

                symbols_grid = (
                    ui.aggrid(
                        theme="quartz",
                        options={
                            "defaultColDef": {"resizable": True, "minWidth": 70},
                            "columnDefs": [
                                {"headerName": "Symbol", "field": "symbol"},
                                {"headerName": "Risk %", "field": "risk", ":valueFormatter": "p=>p.value.toFixed(3)"},
                                {"headerName": "Direction", "field": "direction"},
                                {"headerName": "Order Type", "field": "order_type"},
                                {
                                    "headerName": "Entry Price",
                                    "field": "entry_price",
                                    ":valueFormatter": "p=>p.value.toFixed(5)",
                                    "editable": True,
                                    "hide": True,
                                    "cellClassRules": {"bg-amber-200": "x ==0.0", "bg-transparent": "x > 0.0"},
                                },
                                {
                                    "headerName": "SL/TP Factor",
                                    "field": "sl_tp_factor",
                                    ":valueFormatter": "p=>p.value.toFixed(2)",
                                    "editable": True,
                                    "cellClassRules": {
                                        "line-through": "((x * data['common_sl_pips']) != data['sl_pips']) || ((x * data['common_tp_pips']) != data['tp_pips'])",
                                        "no-underline": "((x * data['common_sl_pips']) == data['sl_pips']) && ((x * data['common_tp_pips']) == data['tp_pips'])",
                                    },
                                },
                                {"headerName": "SL pips", "field": "sl_pips", ":valueFormatter": "p=>p.value.toFixed(1)", "editable": True},
                                {"headerName": "TP pips", "field": "tp_pips", ":valueFormatter": "p=>p.value.toFixed(1)", "editable": True},
                                {"headerName": "RR", "field": "rr", ":valueFormatter": "p=>p.value.toFixed(2)", "cellClassRules": {"bg-red-200": "x < 1.0", "bg-transparent": "x >= 1.0"}},
                                {
                                    "headerName": "Total Lots",
                                    "field": "lots",
                                    ":tooltipValueGetter": "p=>p.data['lots_per_account']",
                                },
                                {"headerName": "Total Risk", "field": "net_risk", ":valueFormatter": "p=>p.value.toFixed(2)"},
                                {"headerName": "Common SL pips", "field": "common_sl_pips", ":valueFormatter": "p=>p.value.toFixed(1)", "hide": True},
                                {"headerName": "Common TP pips", "field": "common_tp_pips", ":valueFormatter": "p=>p.value.toFixed(1)", "hide": True},
                                {"headerName": "Lots per Account", "field": "lots_per_account", "hide": True},
                            ],
                            ":getRowId": "(params) => params.data.symbol",
                            "rowData": state["trade_items"],
                            "tooltipShowDelay": 500,
                            "tooltipHideDelay": 2000,
                        },
                    )
                    .bind_visibility_from(state, "symbols_grid_visible")
                    .classes("w-full")
                    .style("height: 480px")
                )

                def on_instruments_change(e):
                    selected_symbols = e.value or []
                    existing_symbols = [item["symbol"] for item in state["trade_items"]]
                    new_symbols = list(set(selected_symbols) - set(existing_symbols))

                    lots = []
                    for i, account in enumerate(state["selected_accounts"]):
                        lots.append(i / 100)

                    for symbol in new_symbols:
                        state["trade_items"].append(
                            {
                                "symbol": symbol,
                                "risk": 1,
                                "direction": direction.value,
                                "order_type": order_type.value,
                                "entry_price": 0,
                                "sl_tp_factor": 1,
                                "sl_pips": sl_pips.value,
                                "tp_pips": tp_pips.value,
                                "lots": sum(lots),
                                "net_risk": 0,
                                "rr": tp_pips.value / sl_pips.value,
                                "common_sl_pips": sl_pips.value,
                                "common_tp_pips": tp_pips.value,
                                "lots_per_account": ", ".join([f"{x}:{y}" for x, y in zip(list(state["selected_accounts"]), lots)]),
                            }
                        )

                    deleted_symbols = list(set(existing_symbols) - set(selected_symbols))

                    if deleted_symbols:
                        deleted_rows = [item for item in state["trade_items"] if item["symbol"] in deleted_symbols]
                        state["trade_items"] = [item for item in state["trade_items"] if item["symbol"] not in deleted_symbols]
                        symbols_grid.run_grid_method("applyTransaction", {"remove": deleted_rows})

                    if new_symbols:
                        new_rows = [item for item in state["trade_items"] if item["symbol"] in new_symbols]
                        symbols_grid.run_grid_method("applyTransaction", {"add": new_rows})

                    if len(state["trade_items"]) == 0:
                        symbols_grid.options["rowData"] = state["trade_items"]
                        symbols_grid.update()

                    state["symbols_grid_visible"] = True if len(state["trade_items"]) > 0 else False

                def on_sl_pips_change(e):
                    state["common_sl_pips"] = e.value
                    if len(state["trade_items"]) > 0:
                        for i, ti in enumerate(state["trade_items"]):
                            new_row_sl_pips = ti["sl_tp_factor"] * e.value
                            new_row_rr = ti["tp_pips"] / new_row_sl_pips
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "sl_pips", new_row_sl_pips)
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "common_sl_pips", e.value)
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "rr", new_row_rr)
                            state["trade_items"][i]["sl_pips"] = new_row_sl_pips
                            state["trade_items"][i]["common_sl_pips"] = e.value
                            state["trade_items"][i]["rr"] = new_row_rr
                    symbols_grid.run_grid_method("refreshCells", {"force": True, "columns": ["sl_tp_factor"]})

                def on_tp_pips_change(e):
                    state["common_tp_pips"] = e.value
                    if len(state["trade_items"]) > 0:
                        for i, ti in enumerate(state["trade_items"]):
                            new_row_tp_pips = ti["sl_tp_factor"] * e.value
                            new_row_rr = new_row_tp_pips / ti["sl_pips"]
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "tp_pips", new_row_tp_pips)
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "common_tp_pips", e.value)
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "rr", new_row_rr)
                            state["trade_items"][i]["tp_pips"] = new_row_tp_pips
                            state["trade_items"][i]["common_tp_pips"] = e.value
                            state["trade_items"][i]["rr"] = new_row_rr
                    symbols_grid.run_grid_method("refreshCells", {"force": True, "columns": ["sl_tp_factor"]})

                def order_type_change(e):
                    if len(state["trade_items"]) > 0:
                        for i, ti in enumerate(state["trade_items"]):
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "order_type", e.value)
                            state["trade_items"][i]["order_type"] = e.value
                    if e.value == OrderType.market:
                        symbols_grid.run_grid_method("setColumnsVisible", ["entry_price"], False)
                    else:
                        symbols_grid.run_grid_method("setColumnsVisible", ["entry_price"], True)
                    symbols_grid.run_grid_method("sizeColumnsToFit")

                def on_direction_change(e):
                    if len(state["trade_items"]) > 0:
                        for i, ti in enumerate(state["trade_items"]):
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "direction", e.value)
                            state["trade_items"][i]["direction"] = e.value

                def on_change_direction_currency(e):
                    if len(state["trade_items"]) > 0:
                        for i, ti in enumerate(state["trade_items"]):
                            if e.value in ["", None]:
                                symbols_grid.run_row_method(ti["symbol"], "setDataValue", "direction", direction.value)
                                state["trade_items"][i]["direction"] = direction.value
                            else:
                                base = ti["symbol"][:3]
                                quote = ti["symbol"][3:]
                                if e.value == quote:
                                    symbols_grid.run_row_method(ti["symbol"], "setDataValue", "direction", DirectionType.long if direction.value == DirectionType.short else DirectionType.short)
                                    state["trade_items"][i]["direction"] = DirectionType.long if direction.value == DirectionType.short else DirectionType.short
                                else:
                                    symbols_grid.run_row_method(ti["symbol"], "setDataValue", "direction", direction.value)
                                    state["trade_items"][i]["direction"] = direction.value

                def on_grid_cell_value_changed(e):
                    col_id = e.args["colId"]
                    row_data = e.args["data"]
                    new_value = e.args["newValue"]
                    symbol = row_data["symbol"]
                    if col_id == "sl_tp_factor":
                        new_sl_pips = sl_pips.value * new_value
                        new_tp_pips = tp_pips.value * new_value
                        symbols_grid.run_row_method(symbol, "setDataValue", "sl_pips", new_sl_pips)
                        symbols_grid.run_row_method(symbol, "setDataValue", "tp_pips", new_tp_pips)
                        symbols_grid.run_row_method(symbol, "setDataValue", "rr", new_tp_pips / new_sl_pips)
                        item = next((i for i in state["trade_items"] if i["symbol"] == symbol), None)
                        if item:
                            item["sl_tp_factor"] = new_value
                            item["sl_pips"] = new_sl_pips
                            item["tp_pips"] = new_tp_pips
                            item["rr"] = new_tp_pips / new_sl_pips

                    if col_id == "sl_pips":
                        new_rr = row_data["tp_pips"] / new_value
                        symbols_grid.run_row_method(symbol, "setDataValue", "rr", new_rr)
                        item = next((i for i in state["trade_items"] if i["symbol"] == symbol), None)
                        if item:
                            item["sl_pips"] = new_value
                            item["rr"] = new_rr

                    if col_id == "tp_pips":
                        new_rr = new_value / row_data["sl_pips"]
                        symbols_grid.run_row_method(symbol, "setDataValue", "rr", new_rr)
                        item = next((i for i in state["trade_items"] if i["symbol"] == symbol), None)
                        if item:
                            item["tp_pips"] = new_value
                            item["rr"] = new_rr

                    if col_id == "entry_price":
                        # symbols_grid.run_row_method(symbol, "setDataValue", "entry_price", new_value)
                        item = next((i for i in state["trade_items"] if i["symbol"] == symbol), None)
                        if item:
                            item["entry_price"] = new_value

                    symbols_grid.run_grid_method("refreshCells", {"force": True})

                def execute_trades():
                    pprint.pp(state["selected_accounts"])
                    pprint.pp(state["trade_items"])

                    # cleanup
                    state["trade_items"] = []
                    state["trade_items"].clear()
                    state["selected_accounts"] = set()
                    state["symbols_grid_visible"] = False
                    state["common_sl_pips"] = 15
                    state["common_tp_pips"] = 15
                    symbols_select.on_value_change(None)
                    symbols_select.set_value([])
                    symbols_select.on_value_change(on_instruments_change)
                    symbols_grid.options["rowData"] = state["trade_items"]
                    symbols_grid.update()
                    sl_pips.set_value(15)
                    tp_pips.set_value(15)
                    order_type.set_value("Market")
                    direction.set_value("Long")
                    direction_currency.set_value("")
                    strategy.set_value("")
                    probability.set_value("")
                    mindstate.set_value("")
                    risk.set_value(1)
                    account_tree.untick()

                symbols_select.on_value_change(lambda e: ui.timer(0.5, lambda: on_instruments_change(e), once=True))
                # symbols_select.on_value_change(on_instruments_change)
                sl_pips.on_value_change(on_sl_pips_change)
                tp_pips.on_value_change(on_tp_pips_change)
                order_type.on_value_change(order_type_change)
                direction.on_value_change(on_direction_change)
                direction_currency.on_value_change(on_change_direction_currency)
                symbols_grid.on("cellValueChanged", on_grid_cell_value_changed)
                execute_btn.on_click(execute_trades)

    # if right_drawer and right_drawer_rendered_by != "trading":
    #     app.storage.client["right_drawer_rendered_by"] = "trading"
    #     right_drawer.clear()
    #     with right_drawer:
    #         names = ["Alice", "Bob", "Carol"]
    #         ui.select(names, multiple=True, value=names[:2], label="with chips").classes("w-64").props("use-chips")
    #         account_tree2 = ui.tree(
    #             [
    #                 {"id": "numbers", "children": [{"id": "1"}, {"id": "2", "label": "Y"}]},
    #                 {"id": "letters", "children": [{"id": "A"}, {"id": "B"}]},
    #             ],
    #             label_key="label",
    #             tick_strategy="leaf",
    #         ).expand()
    #         with ui.row():
    #             ui.button("+ all", on_click=account_tree2.expand)
    #             ui.button("- all", on_click=account_tree2.collapse)
