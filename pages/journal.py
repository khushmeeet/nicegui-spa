from enum import Enum
from nicegui import ui, app

from models.enums import AccountType, PlatformType

from utils.case_converter import title_to_snake
from utils.tree import build_tree

DATE_FORMATTER = """
(params) => {
    const date = new Date(params.value);
    const options = {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    };
    return date.toLocaleString('en-UK', options);
}
"""

DURATION_FORMATTER = """
    (p) => {
        if (p.value == null) return '';
        let seconds = Number(p.value);
        let days = Math.floor(seconds / 86400);
        seconds %= 86400;
        let hours = Math.floor(seconds / 3600);
        seconds %= 3600;
        let minutes = Math.floor(seconds / 60);

        let parts = [];
        if (days > 0) parts.push(`${days}d`);
        if (hours > 0) parts.push(`${hours}h`);
        if (minutes > 0 || parts.length === 0) parts.push(`${minutes}m`);

        return parts.join(' ');
    }
"""


def journal():
    right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    trades_df = app.storage.client["trades_df"]
    brokers_df = app.storage.client["brokers_df"]
    accounts_df = app.storage.client["accounts_df"]

    state = {
        "selected_accounts": set(),
        # "trades": trades_df.to_dict("records"),
    }

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

    with ui.row().classes("w-full mb-4 items-center"):
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

        ui.label("Live: 3/10, Demo: 2/10").classes("text-grey-14")
        journal_clear_filter_btn = ui.button("Clear All Filters", icon="filter_list_off").props("outline flat")

    journal = (
        ui.aggrid.from_pandas(
            trades_df,
            theme="quartz",
            options={
                # "domLayout": "autoHeight",
                "suppressHorizontalScroll": False,
                "ensureDomOrder": True,
                "defaultColDef": {"resizable": True, "minWidth": 40},
                "rowSelection": "single",
                "suppressRowClickSelection": False,
                "defaultColDef": {"flex": 1, "resizable": True, "sortable": True, "filter": True},
                "columnDefs": [
                    {"headerName": "", "field": "trade_id", "filter": "agNumberColumnFilter", "type": "rightAligned", "minWidth": 60, "cellDataType": "number", "hide": True},
                    {
                        "headerName": "Open Time",
                        "field": "open_time",
                        "filter": "agDateColumnFilter",
                        ":valueFormatter": DATE_FORMATTER,
                        "minWidth": 120,
                    },
                    {"headerName": "Win/Loss", "field": "win_loss_html", "filter": "agTextColumnFilter", "minWidth": 90},
                    {"headerName": "Strategy", "field": "strategy", "filter": "agTextColumnFilter", "minWidth": 100},
                    {"headerName": "Symbol", "field": "symbol", "filter": "agTextColumnFilter", "minWidth": 90},
                    {"headerName": "Direction", "field": "direction_html", "filter": "agTextColumnFilter", "minWidth": 80},
                    {"headerName": "Order Type", "field": "order_type_html", "filter": "agTextColumnFilter", "minWidth": 90},
                    {"headerName": "Entry Price", "field": "entry_price", "filter": "agNumberColumnFilter", "type": "rightAligned", "minWidth": 90},
                    {"headerName": "Exit Price", "field": "exit_price", "filter": "agNumberColumnFilter", "type": "rightAligned", "minWidth": 90},
                    {
                        "headerName": "Risk",
                        "field": "risk",
                        "filter": "agNumberColumnFilter",
                        ":valueFormatter": "p=>(p.value*100).toFixed(2)+' %'",
                        "type": "rightAligned",
                        "minWidth": 75,
                        "cellDataType": "number",
                    },
                    {
                        "headerName": "Pip Risk",
                        "field": "stop_loss_pips",
                        "filter": "agNumberColumnFilter",
                        "type": "rightAligned",
                        "minWidth": 70,
                        ":valueFormatter": "p=>p.value.toFixed(1)",
                    },
                    {"headerName": "Lots", "field": "lots", "filter": "agNumberColumnFilter", "type": "rightAligned", "minWidth": 70},
                    {
                        "headerName": "PnL",
                        "field": "actual_pnl",
                        "filter": "agNumberColumnFilter",
                        "type": "rightAligned",
                        ":valueFormatter": "p=>p.value.toFixed(2)",
                        "cellClassRules": {"font-bold text-rose-600": "x<=0", "font-bold text-emerald-600": "x>0"},
                        "minWidth": 100,
                    },
                    {"headerName": "RR", "field": "actual_rr", "filter": "agNumberColumnFilter", "type": "rightAligned", "minWidth": 75},
                    {
                        "headerName": "Duration",
                        "field": "duration",
                        "filter": "agNumberColumnFilter",
                        ":valueFormatter": DURATION_FORMATTER,
                        "minWidth": 90,
                    },
                    {
                        "headerName": "Starting Balance",
                        "field": "starting_balance",
                        "filter": "agNumberColumnFilter",
                        "minWidth": 100,
                        "type": "rightAligned",
                        ":valueFormatter": "p=>p.value.toFixed(2)",
                    },
                    {
                        "headerName": "Closing Balance",
                        "field": "ending_balance",
                        "filter": "agNumberColumnFilter",
                        "minWidth": 100,
                        "type": "rightAligned",
                        ":valueFormatter": "p=>p.value.toFixed(2)",
                    },
                    {"headerName": "Probability", "field": "probability", "filter": "agTextColumnFilter", "minWidth": 100},
                    {"headerName": "Mindstate", "field": "mindstate", "filter": "agTextColumnFilter", "minWidth": 100},
                    {"headerName": "Account Name", "field": "account_name", "filter": "agTextColumnFilter", "minWidth": 100},
                    {"headerName": "Exit Reason", "field": "account_type", "filter": "agTextColumnFilter", "minWidth": 100},
                    {"headerName": "Account ID", "field": "account_id", "hide": False, "minWidth": 50, "filter": "agTextColumnFilter"},
                ],
                "initialState": {"rowSelection": ["0"]},
                "pagination": True,
                "paginationPageSize": 50,
            },
            html_columns=[2, 5, 6],
        )
        .classes("w-full")
        .style("height: calc(100vh - 160px);")
    )

    journal_clear_filter_btn.on_click(lambda: journal.run_grid_method("setFilterModel", None))

    def on_tick_account_tree(e):
        print(e.value)
        accounts_ids = accounts_df.index.tolist()
        new_selection = set(filter(lambda x: x in accounts_ids, e.value))
        state["selected_accounts"] = new_selection
        # journal.options["filterModel"] = {"account_id": {"filterType": "set", "values": ["1", "3", "5"]}}
        # journal.update()
        # TODO: fix this
        journal.run_grid_method("setFilterModel", {"account_id": {"filterType": "text", "type": "contains", "filter": "1"}})

    account_tree.on_tick(on_tick_account_tree)

    # if right_drawer and right_drawer_rendered_by != "journal":
    #     app.storage.client["right_drawer_rendered_by"] = "journal"
    #     right_drawer.clear()
    #     with right_drawer:
    #         names = ["Alice", "Bob", "Carol"]
    #         ui.select(names, multiple=True, value=names[:2], label="with chips").classes("w-64").props("use-chips")
    #         t = ui.tree(
    #             [
    #                 {"id": "numbers", "children": [{"id": "1"}, {"id": "2", "label": "Y"}]},
    #                 {"id": "letters", "children": [{"id": "A"}, {"id": "B"}]},
    #             ],
    #             label_key="label",
    #             tick_strategy="leaf",
    #         ).expand()
    #         with ui.row():
    #             ui.button("+ all", on_click=t.expand)
    #             ui.button("- all", on_click=t.collapse)
