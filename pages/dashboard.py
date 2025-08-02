import calendar
from datetime import datetime
from nicegui import ui, app

from utils.tree import build_tree, get_mapping_and_grouping_list
from data.queries import get_daily_trade_counts, get_daily_pnl

WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def dashboard():
    right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    brokers_df = app.storage.client["brokers_df"]
    accounts_df = app.storage.client["accounts_df"]

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
                tree_select_all_btn.on_click(account_tree.tick)
                tree_deselect_all_btn.on_click(account_tree.untick)

        ui.toggle(["Value", "Percent"])

    YEAR, MONTH = 2025, 7
    DAYS_IN_MONTH = calendar.monthrange(YEAR, MONTH)[1]
    FIRST_WEEKDAY = calendar.monthrange(YEAR, MONTH)[0]  # 0=Monday, 6=Sunday

    # Adjust weekday order to start from Sunday
    WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    FIRST_WEEKDAY = (FIRST_WEEKDAY + 1) % 7

    DAILY_PNL = get_daily_pnl(YEAR, MONTH)
    TRADE_COUNTS = get_daily_trade_counts(YEAR, MONTH)

    with ui.grid(columns=8).classes("gap-3 mb-5 mt-5"):
        for day in WEEKDAYS:
            with ui.card().classes("p-2 flex flex-col justify-between items-stretch relative").props("flat bordered"):
                ui.label(day).classes("text-md text-center font-semibold")
        with ui.card().classes("p-2 flex flex-col justify-between items-stretch relative ml-2").props("flat bordered"):
            ui.label("Week").classes("text-md text-center font-semibold")

    with ui.grid(columns=8).classes("gap-3"):
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
                    pnl = DAILY_PNL.get(day_counter, 0)
                    color = "text-emerald-600" if pnl > 0 else "text-rose-600" if pnl < 0 else "text-gray-600"
                    date_str = datetime(YEAR, MONTH, day_counter).strftime("%b %d")
                    trades = TRADE_COUNTS.get(day_counter, 0)
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

            # Add week total at the end
            week_color = "text-green-700" if week_pnl > 0 else "text-red-700" if week_pnl < 0 else "text-gray-700"
            with ui.card().classes("p-2 flex flex-col justify-between items-stretch relative ml-2").props("flat bordered"):
                ui.label(f"Week {week_counter}").classes("text-xs text-gray-500")
                with ui.column().classes("items-end"):
                    ui.label(f"{week_pnl:.2f}").classes(f"md:text-md font-bold {color}")
                    with ui.row().classes("gap-1"):
                        ui.label(f"{week_trades_count}").classes("text-xs text-gray-500")
                        ui.label("trades").classes("text-xs text-gray-500 max-md:hidden")

    if right_drawer and right_drawer_rendered_by != "dashboard":
        right_drawer.clear()
        app.storage.client["right_drawer_rendered_by"] = "dashboard"
        with right_drawer:
            ui.label("Right Drawer for Dashboard").classes("text-lg")
            ui.button("Close", on_click=lambda: right_drawer.toggle())
