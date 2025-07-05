from nicegui import ui, app


def accounts():
    right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]

    with ui.column().classes("w-full h-full text-lg"):
        ui.markdown("## 💼 Accounts")
        ui.label("Manage your trading accounts")
        ui.space()

        with ui.row().classes("w-full"):
            ui.button("Add Account", on_click=lambda: ui.notify("Add Account clicked"))
            ui.button("Archive Account", on_click=lambda: ui.notify("Archive Account clicked")).props("disabled")
            ui.button("Edit Account", on_click=lambda: ui.notify("Edit Account clicked")).props("disabled")
        ui.space()

        ui.button("Toggle Right Drawer", on_click=lambda: right_drawer.clear()).classes("mt-4")
        ui.space()

        def raise_exception():
            raise Exception("This is an exception")

        ui.button("Raise Exception", on_click=raise_exception).classes("mt-4")

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
