from nicegui import ui, app


def journal():
    right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    trades_df = app.storage.client["trades_df"]

    ui.label("📖 Journal").classes("text-2xl mb-3")

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
            "minWidth": 800,
            # "columnDefs": [
            #     {"headerName": "Name", "field": "Name", "checkboxSelection": True, "filter": "agTextColumnFilter", "width": 200, "minWidth": 100},
            #     {"headerName": "Broker", "field": "Broker", "filter": "agTextColumnFilter", "width": 150, "minWidth": 100},
            #     {"headerName": "Type", "field": "Type", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
            #     {"headerName": "Login", "field": "Login", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
            #     {"headerName": "Platform", "field": "Platform", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
            #     {"headerName": "Server", "field": "Server", "filter": "agTextColumnFilter", "width": 200, "minWidth": 100},
            #     {"headerName": "Path", "field": "Path", "filter": "agTextColumnFilter", "minWidth": 100},
            #     {"headerName": "Currency", "field": "Currency", "filter": "agTextColumnFilter", "width": 100, "minWidth": 100},
            #     {"headerName": "Starting Balance", "field": "Starting Balance", "filter": "agTextColumnFilter", "minWidth": 100},
            #     {"headerName": "Current Balance", "field": "Current Balance", "filter": "agTextColumnFilter", "minWidth": 100},
            # ],
            "initialState": {"rowSelection": ["0"]},
            "pagination": True,
            "paginationAutoPageSize": True,
        },
    ).classes("w-full").style("height: calc(100vh - 160px);")

    if right_drawer and right_drawer_rendered_by != "journal":
        app.storage.client["right_drawer_rendered_by"] = "journal"
        right_drawer.clear()
        with right_drawer:
            names = ["Alice", "Bob", "Carol"]
            ui.select(names, multiple=True, value=names[:2], label="with chips").classes("w-64").props("use-chips")
            t = ui.tree(
                [
                    {"id": "numbers", "children": [{"id": "1"}, {"id": "2", "label": "Y"}]},
                    {"id": "letters", "children": [{"id": "A"}, {"id": "B"}]},
                ],
                label_key="label",
                tick_strategy="leaf",
            ).expand()
            with ui.row():
                ui.button("+ all", on_click=t.expand)
                ui.button("- all", on_click=t.collapse)
