from nicegui import ui, app
import json


def trading():
    right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]

    ui.markdown("## 🏦 Trading")
    ui.label("Content One").classes("text-2xl")

    if right_drawer and right_drawer_rendered_by != "trading":
        app.storage.client["right_drawer_rendered_by"] = "trading"
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
