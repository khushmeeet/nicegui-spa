from enum import Enum
from typing import List
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

    state = {"symbols_grid_visible": False, "trade_items": []}

    ui.markdown("## 🏦 Trading")

    with ui.splitter(value=27) as splitter:
        with splitter.before:
            with ui.column().classes("w-full pr-4 pb-4"):

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
                    ui.button("Execute", icon="rocket_launch").bind_visibility_from(state, "symbols_grid_visible")

                symbols_grid = (
                    ui.aggrid(
                        theme="quartz",
                        options={
                            "columnDefs": [
                                {"headerName": "Symbol", "field": "symbol"},
                                {"headerName": "Risk %", "field": "risk", ":valueFormatter": "p=>p.value.toFixed(3)"},
                                {"headerName": "Direction", "field": "direction"},
                                {"headerName": "Order Type", "field": "order_type"},
                                {"headerName": "Entry Price", "field": "entry_price", ":valueFormatter": "p=>p.value.toFixed(5)"},
                                {"headerName": "SL/TP Factor", "field": "sl_tp_factor", ":valueFormatter": "p=>p.value.toFixed(2)", "editable": True},
                                {"headerName": "SL pips", "field": "sl_pips", ":valueFormatter": "p=>p.value.toFixed(1)", "editable": True},
                                {"headerName": "TP pips", "field": "tp_pips", ":valueFormatter": "p=>p.value.toFixed(1)", "editable": True},
                                {"headerName": "RR", "field": "rr", ":valueFormatter": "p=>p.value.toFixed(2)", "cellClassRules": {"bg-red-200": "x < 1.0", "bg-green-200": "x >= 1.0"}},
                                {"headerName": "Lots(~)", "field": "lots", ":valueFormatter": "p=>p.value.toFixed(2)"},
                                {"headerName": "Net Risk", "field": "net_risk", ":valueFormatter": "p=>p.value.toFixed(2)"},
                            ],
                            ":getRowId": "(params) => params.data.symbol",
                        },
                    )
                    .bind_visibility_from(state, "symbols_grid_visible")
                    .classes("w-full")
                    .style("height: calc(100vh - 650px);")
                )

                def on_instruments_change(e):
                    if len(e.value) > 0:
                        per_symbol_risk = risk.value / len(e.value)
                    if len(e.value) > len(state["trade_items"]):
                        new_symbol = list(set(e.value) - set([item["symbol"] for item in state["trade_items"]]))
                        rowData = state["trade_items"] + [
                            {
                                "symbol": new_symbol[0],
                                "risk": per_symbol_risk,
                                "direction": direction.value,
                                "order_type": order_type.value,
                                "entry_price": 0,
                                "sl_tp_factor": 1,
                                "sl_pips": sl_pips.value,
                                "tp_pips": tp_pips.value,
                                "lots": 0.25,
                                "net_risk": 0,
                                "rr": tp_pips.value / sl_pips.value,
                            }
                            # for symbol in e.value
                        ]
                        symbols_grid.options["rowData"] = rowData
                        # symbols_grid.style(f"height: {51+42*len(rowData)}px;")
                        symbols_grid.update()
                    else:
                        deleted_symbol = list(set([item["symbol"] for item in state["trade_items"]]) - set(e.value))
                        symbol_rowData = list(filter(lambda item: item["symbol"] in deleted_symbol, state["trade_items"]))
                        symbols_grid.run_grid_method("applyTransaction", {"remove": symbol_rowData})
                        rowData = list(filter(lambda item: item["symbol"] not in e.value, state["trade_items"]))
                    if len(e.value) > 0:
                        for i in range(len(rowData)):
                            rowData[i]["risk"] = per_symbol_risk

                    state["trade_items"] = rowData
                    state["symbols_grid_visible"] = True if len(rowData) > 0 else False
                    # symbols_grid.options["rowData"] = rowData
                    # symbols_grid.style(f"height: {51+42*len(rowData)}px;")
                    # symbols_grid.update()

                symbols_select.on_value_change(on_instruments_change)

                def on_sl_pips_change(e):
                    tis = state["trade_items"]
                    if len(tis) > 0:
                        for ti in tis:
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "sl_pips", ti["sl_tp_factor"] * e.value)
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "rr", ti["tp_pips"] / (ti["sl_tp_factor"] * e.value))

                def on_tp_pips_change(e):
                    tis = state["trade_items"]
                    if len(tis) > 0:
                        for ti in tis:
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "tp_pips", ti["sl_tp_factor"] * e.value)
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "rr", ti["sl_tp_factor"] * e.value / ti["sl_pips"])

                def order_type_change(e):
                    tis = state["trade_items"]
                    if len(tis) > 0:
                        for ti in tis:
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "order_type", e.value)

                def on_direction_change(e):
                    tis = state["trade_items"]
                    if len(tis) > 0:
                        for ti in tis:
                            symbols_grid.run_row_method(ti["symbol"], "setDataValue", "direction", e.value)

                def on_change_direction_currency(e):
                    tis = state["trade_items"]
                    if len(tis) > 0:
                        for ti in tis:
                            if e.value in ["", None]:
                                symbols_grid.run_row_method(ti["symbol"], "setDataValue", "direction", direction.value)
                            else:
                                base = ti["symbol"][:3]
                                quote = ti["symbol"][3:]
                                if e.value == quote:
                                    symbols_grid.run_row_method(ti["symbol"], "setDataValue", "direction", DirectionType.long if direction.value == DirectionType.short else DirectionType.short)
                                else:
                                    symbols_grid.run_row_method(ti["symbol"], "setDataValue", "direction", direction.value)

                sl_pips.on_value_change(on_sl_pips_change)
                tp_pips.on_value_change(on_tp_pips_change)
                order_type.on_value_change(order_type_change)
                direction.on_value_change(on_direction_change)
                direction_currency.on_value_change(on_change_direction_currency)

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
