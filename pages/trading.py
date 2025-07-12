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
    }

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
                    with ui.select(strategies_df["name"].to_list(), label="Strategy", with_input=True, clearable=True).props("outlined").classes("w-64").add_slot("prepend"):
                        ui.icon("tips_and_updates")
                    with ui.number(label="Trade Risk", value=1, step=0.05, min=0.1, max=5).props("outlined").classes("w-64").add_slot("prepend"):
                        ui.icon("percent")
                    with ui.select([p.value for p in TradeSuccessProbabilityType], label="Probability", with_input=True, clearable=True).props("outlined ").classes("w-64").add_slot("prepend"):
                        ui.icon("casino")
                    with ui.select([p.value for p in TradingMindState], label="Mindstate", with_input=True, clearable=True).props("outlined").classes("w-64").add_slot("prepend"):
                        ui.icon("psychology")
                with ui.expansion("Common", icon="join_inner", value=True).classes(" w-full border p-0"):
                    with ui.row().classes("w-full"):
                        with ui.number(label="Stop Loss (pips)", value=15, step=1, min=5).props("outlined").classes("w-64").add_slot("prepend"):
                            ui.icon("trending_down")
                        with ui.number(label="Take Profit (pips)", value=15, step=1, min=5).props("outlined").classes("w-64").add_slot("prepend"):
                            ui.icon("trending_up")
                        with ui.select(trade_direction_types, value=trade_direction_types[0], label="Direction", with_input=True, clearable=True).props("outlined").classes("w-64").add_slot("prepend"):
                            ui.icon("import_export")
                        with ui.select(trade_order_types, value=trade_order_types[0], label="Order Type", with_input=True, clearable=True).props("outlined").classes("w-64").add_slot("prepend"):
                            ui.icon("shopping_cart")
                        with ui.select([p.value for p in CurrencyType], label="Direction based on currency", with_input=True, clearable=True).props("outlined").classes("w-64").add_slot("prepend"):
                            ui.icon("currency_exchange")

                symbols_select = ui.select(symbols_df["symbol"].to_list(), label="Symbols", multiple=True, with_input=True, clearable=True).props("use-chips outlined").classes("w-full mb-3")

                with symbols_select.add_slot("prepend"):
                    ui.icon("monetization_on")

                symbols_grid = (
                    ui.aggrid(
                        theme="quartz",
                        options={
                            "columnDefs": [
                                {"headerName": "Symbol", "field": "symbol"},
                                {"headerName": "Risk %", "field": "risk"},
                                {"headerName": "Direction", "field": "direction"},
                                {"headerName": "Order Type", "field": "order_type"},
                                {"headerName": "Entry Price", "field": "entry_price"},
                                {"headerName": "SL/TP Factor", "field": "sl_tp_factor"},
                                {"headerName": "SL pips", "field": "sl_pips"},
                                {"headerName": "TP pips", "field": "tp_pips"},
                                {"headerName": "Lots(~)", "field": "lots"},
                                {"headerName": "Net Risk", "field": "net_risk"},
                            ],
                        },
                    )
                    .bind_visibility_from(state, "symbols_grid_visible")
                    .classes("w-full")
                )

                def on_instruments_change(e):
                    rowData = [{"symbol": symbol, "risk": 1} for symbol in e.value]
                    state["symbols_grid_visible"] = True if len(rowData) > 0 else False
                    symbols_grid.options["rowData"] = rowData
                    symbols_grid.update()

                symbols_select.on_value_change(on_instruments_change)

                ui.button("Execute", icon="rocket_launch").bind_visibility_from(state, "symbols_grid_visible")

    if right_drawer and right_drawer_rendered_by != "trading":
        app.storage.client["right_drawer_rendered_by"] = "trading"
        right_drawer.clear()
        with right_drawer:
            names = ["Alice", "Bob", "Carol"]
            ui.select(names, multiple=True, value=names[:2], label="with chips").classes("w-64").props("use-chips")
            account_tree2 = ui.tree(
                [
                    {"id": "numbers", "children": [{"id": "1"}, {"id": "2", "label": "Y"}]},
                    {"id": "letters", "children": [{"id": "A"}, {"id": "B"}]},
                ],
                label_key="label",
                tick_strategy="leaf",
            ).expand()
            with ui.row():
                ui.button("+ all", on_click=account_tree2.expand)
                ui.button("- all", on_click=account_tree2.collapse)
