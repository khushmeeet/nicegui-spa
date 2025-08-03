import calendar
from datetime import datetime
import pandas as pd
from nicegui import ui, app

from utils.tree import build_tree, get_mapping_and_grouping_list
from utils.mock_event import MockEvent
from data.queries import get_all_items_from_trade

WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def dashboard():
    right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    brokers_df = app.storage.client["brokers_df"]
    accounts_df = app.storage.client["accounts_df"]

    trades_df = get_all_items_from_trade()
    trades_df["exit_time"] = pd.to_datetime(trades_df["exit_time"])
    trades_df["open_time"] = pd.to_datetime(trades_df["open_time"])

    state = {
        "selected_accounts": list(accounts_df["name"]),
    }

    def update_state(**kwargs):
        for k, v in kwargs.items():
            state[k] = v

    tree_enum_mapping, grouping_list = get_mapping_and_grouping_list(brokers_df)

    with ui.row().classes("w-full justify-between mb-4"):
        with ui.dropdown_button("Select Accounts(s)", icon="business_center"):
            with ui.column().classes("w-full p-4"):
                grouping_select = ui.select(grouping_list, multiple=True, label="Grouping", with_input=True, clearable=True, value=grouping_list[0]).props("outlined use-chips").classes("w-full")
                with grouping_select.add_slot("prepend"):
                    ui.icon("account_tree")
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label("Select Account(s)")
                    with ui.button_group().props("flat").classes("bg-grey-2 text-grey-14"):
                        tree_select_all_btn = ui.button(icon="select_all", color="text-grey-14").props("flat dense")
                        tree_deselect_all_btn = ui.button(icon="deselect", color="text-grey-14").props("flat dense")
                        tree_expand_btn = ui.button(icon="add", color="text-grey-14").props("flat dense")
                        tree_collapse_btn = ui.button(icon="remove", color="text-grey-14").props("flat dense")

                account_tree = (
                    ui.tree(
                        build_tree(accounts_df, grouping_list[:1], enum_mapping=tree_enum_mapping, ungroup_keys=grouping_list[1:]),
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

                def on_account_selection_change(e):
                    selected_account_names = []
                    if e.value:
                        for node_id in e.value:
                            try:
                                account_id = int(node_id)
                                account_name = accounts_df[accounts_df["id"] == account_id]["name"].iloc[0]
                                selected_account_names.append(account_name)
                            except (ValueError, IndexError):
                                pass

                    if not selected_account_names:
                        selected_account_names = list(accounts_df["name"])

                    update_state(selected_accounts=selected_account_names)
                    update_calendar_data()

                account_tree.on_tick(on_account_selection_change)

                def on_select_all():
                    account_tree.tick()
                    all_account_ids = [str(acc_id) for acc_id in accounts_df["id"].tolist()]
                    mock_event = MockEvent(all_account_ids)
                    on_account_selection_change(mock_event)

                def on_deselect_all():
                    account_tree.untick()
                    mock_event = MockEvent([])
                    on_account_selection_change(mock_event)

                tree_select_all_btn.on_click(on_select_all)
                tree_deselect_all_btn.on_click(on_deselect_all)

        ui.toggle(["Value", "Percent"])

    calendar_container = ui.column().classes("w-full")

    YEAR, MONTH = 2025, 7
    DAYS_IN_MONTH = calendar.monthrange(YEAR, MONTH)[1]
    FIRST_WEEKDAY = calendar.monthrange(YEAR, MONTH)[0]  # 0=Monday, 6=Sunday

    # Adjust weekday order to start from Sunday
    WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    FIRST_WEEKDAY = (FIRST_WEEKDAY + 1) % 7

    def get_daily_pnl_from_df(year: int, month: int, selected_accounts: list = None) -> dict:
        filtered_df = trades_df.copy()

        if selected_accounts:
            filtered_df = filtered_df[filtered_df["account_name"].isin(selected_accounts)]

        filtered_df = filtered_df[(filtered_df["exit_time"].dt.year == year) & (filtered_df["exit_time"].dt.month == month) & (filtered_df["actual_pnl"].notna())]
        daily_pnl = filtered_df.groupby(filtered_df["exit_time"].dt.day)["actual_pnl"].sum()
        return daily_pnl.to_dict()

    def get_daily_trade_counts_from_df(year: int, month: int, selected_accounts: list = None) -> dict:
        filtered_df = trades_df.copy()

        if selected_accounts:
            filtered_df = filtered_df[filtered_df["account_name"].isin(selected_accounts)]

        filtered_df = filtered_df[(filtered_df["open_time"].dt.year == year) & (filtered_df["open_time"].dt.month == month)]
        daily_counts = filtered_df.groupby(filtered_df["open_time"].dt.day).size()
        return daily_counts.to_dict()

    def update_calendar_data():
        daily_pnl = get_daily_pnl_from_df(YEAR, MONTH, state["selected_accounts"])
        trade_counts = get_daily_trade_counts_from_df(YEAR, MONTH, state["selected_accounts"])

        calendar_container.clear()
        build_calendar(daily_pnl, trade_counts)

    def build_calendar(daily_pnl, trade_counts):
        with calendar_container:
            with ui.grid(columns=8).classes("w-full gap-3 mb-5 mt-5"):
                for day in WEEKDAYS:
                    with ui.card().classes("p-2 flex flex-col justify-between items-stretch relative").props("flat bordered"):
                        ui.label(day).classes("text-md text-center font-semibold")
                with ui.card().classes("p-2 flex flex-col justify-between items-stretch relative ml-2").props("flat bordered"):
                    ui.label("Week").classes("text-md text-center font-semibold")

            with ui.grid(columns=8).classes("w-full gap-3"):
                day_counter = 1
                week_counter = 0
                while day_counter <= DAYS_IN_MONTH:
                    week_counter += 1
                    week_pnl = 0
                    week_trades_count = 0

                    for weekday in range(7):
                        if (week_counter == 1 and weekday < FIRST_WEEKDAY) or day_counter > DAYS_IN_MONTH:
                            ui.card().classes("bg-gray-100").props("flat bordered")
                        else:
                            pnl = daily_pnl.get(day_counter, 0)
                            color = "text-emerald-600" if pnl > 0 else "text-rose-600" if pnl < 0 else "text-gray-600"
                            date_str = datetime(YEAR, MONTH, day_counter).strftime("%b %d")
                            trades = trade_counts.get(day_counter, 0)
                            with ui.card().classes("p-2 flex flex-col justify-between items-stretch relative").props("flat bordered"):
                                ui.label(date_str).classes("text-xs text-gray-500")
                                with ui.column().classes("items-end"):
                                    ui.label(f"{pnl:.2f}").classes(f"md:text-md font-bold {color}")
                                    with ui.row().classes("gap-1"):
                                        ui.label(f"{trades}").classes("text-xs text-gray-500")
                                        ui.label("trades").classes("text-xs text-gray-500 max-md:hidden")

                            week_pnl += pnl
                            day_counter += 1
                            week_trades_count += trades

                    week_color = "text-green-700" if week_pnl > 0 else "text-red-700" if week_pnl < 0 else "text-gray-700"
                    with ui.card().classes("p-2 flex flex-col justify-between items-stretch relative ml-2").props("flat bordered"):
                        ui.label(f"Week {week_counter}").classes("text-xs text-gray-500")
                        with ui.column().classes("items-end"):
                            ui.label(f"{week_pnl:.2f}").classes(f"md:text-md font-bold {week_color}")
                            with ui.row().classes("gap-1"):
                                ui.label(f"{week_trades_count}").classes("text-xs text-gray-500")
                                ui.label("trades").classes("text-xs text-gray-500 max-md:hidden")

    DAILY_PNL = get_daily_pnl_from_df(YEAR, MONTH, state["selected_accounts"])
    TRADE_COUNTS = get_daily_trade_counts_from_df(YEAR, MONTH, state["selected_accounts"])
    build_calendar(DAILY_PNL, TRADE_COUNTS)

    if right_drawer and right_drawer_rendered_by != "dashboard":
        right_drawer.clear()
        app.storage.client["right_drawer_rendered_by"] = "dashboard"
        with right_drawer:
            ui.label("Right Drawer for Dashboard").classes("text-lg")
            ui.button("Close", on_click=lambda: right_drawer.toggle())
