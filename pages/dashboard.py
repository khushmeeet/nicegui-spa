from nicegui import ui, app


WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def dashboard():
    right_drawer: ui.right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]

    with ui.row().classes("mb-5"):
        with ui.card().classes("h-32 w-64"):
            ui.label("Metric 1")
        with ui.card().classes("h-32 w-64"):
            ui.label("Metric 1")

    ui.separator().classes("mb-5")
    with ui.row().classes("w-full justify-between mb-4"):
        ui.select(options=["Option 1", "Option 2", "Option 3"], label="Account").props("outlined").classes("w-64")
        ui.toggle(["Value", "Percent"])
    with ui.row().classes("mb-2"):
        with ui.grid(columns=7, rows=1).classes("gap-2"):
            for weekday in WEEKDAYS:
                ui.label(weekday).classes("text-md w-32")
    with ui.row():
        with ui.grid(columns=7, rows=6).classes("gap-2"):
            for i in range(1, 36):
                with ui.card().classes("h-32 w-32"):
                    ui.label(f"Day {i}")

    if right_drawer and right_drawer_rendered_by != "dashboard":
        right_drawer.clear()
        app.storage.client["right_drawer_rendered_by"] = "dashboard"
        with right_drawer:
            ui.label("Right Drawer for Dashboard").classes("text-lg")
            ui.button("Close", on_click=lambda: right_drawer.toggle())
