from nicegui import ui, app


def accounts():
    right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    accounts_df = app.storage.client["accounts_df"]

    with ui.column().classes("w-full h-full text-lg"):
        ui.markdown("## 💼 Accounts")
        ui.label("Your accounts summary")

        ui.highchart(
            {
                "title": False,
                "plotOptions": {
                    "series": {
                        "stickyTracking": False,
                        "dragDrop": {"draggableY": True, "dragPrecisionY": 1},
                    },
                },
                "series": [
                    {"name": "A", "data": [[20, 10], [30, 20], [40, 30]]},
                    {"name": "B", "data": [[50, 40], [60, 50], [70, 60]]},
                ],
            },
            extras=["draggable-points"],
            on_point_click=lambda e: ui.notify(f"Click: {e}"),
            on_point_drag_start=lambda e: ui.notify(f"Drag start: {e}"),
            on_point_drop=lambda e: ui.notify(f"Drop: {e}"),
        ).classes("w-full h-128")
        aggrid_options = {
            "columnDefs": [
                {"headerName": "Name", "field": "Name", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Broker", "field": "Broker", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Type", "field": "Type", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Login", "field": "Login", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Platform", "field": "Platform", "filter": "agTextColumnFilter", "floatingFilter": True},
                {"headerName": "Server", "field": "Server", "filter": "agTextColumnFilter", "floatingFilter": True},
                # {"headerName": "Currency", "field": "currency"},
                # {"headerName": "Balance", "field": "balance"},
            ]
        }

        ui.separator()

        ui.button("Add Account", icon="add", on_click=lambda: right_drawer.toggle())
        ui.aggrid.from_pandas(accounts_df, options=aggrid_options).classes("max-h-128")

        if right_drawer and right_drawer_rendered_by != "accounts":
            app.storage.client["right_drawer_rendered_by"] = "accounts"
            right_drawer.clear()

            with right_drawer:
                ui.markdown("##### ➕ Add Account")
                with ui.grid().classes("w-full"):
                    ui.input(label="Name").classes("w-full")
                    ui.select(options=["Broker 1", "Broker 2", "Broker 3"], label="Broker").classes("w-full")
                    ui.input(label="Login").classes("w-full")
                    ui.input(label="Password", password=True, password_toggle_button=True).classes("w-full")
                    ui.select(label="Type", options=["Live", "Demo"]).classes("w-full")
                    ui.select(label="Platform", options=["MetaTrader 5", "cTrader 5"]).classes("w-full")
                    ui.input(label="Server").classes("w-full")
                    ui.checkbox("Is Portable", value=True).classes("w-full")
                ui.upload(label="Path", multiple=False, max_files=1).classes("w-full")
                with ui.row():
                    ui.button("Save", icon="save", on_click=lambda: ui.notify("Add Account clicked", position="bottom-right"))
                    ui.button("Cancel", icon="close", on_click=lambda: right_drawer.toggle())
                    ui.button("Clear", icon="delete_outline", on_click=lambda: ui.notify("Add Account clicked"))
