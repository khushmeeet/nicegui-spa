from nicegui import ui, app


from left_drawer import left_drawer_open, left_drawer_collapse


def header(left_drawer: ui.left_drawer = None, right_drawer: ui.right_drawer = None):
    with ui.header().props("bordered").classes("items-center justify-between bg-transparent") as header:
        with ui.element("div").classes("flex items-center gap-2"):
            ui.button(on_click=lambda: left_drawer_collapse(left_drawer), icon="keyboard_double_arrow_left").props("flat").classes("text-grey-6 max-lg:hidden").bind_visibility_from(
                app.storage.client, "left_drawer_left_arrow_visible"
            )
            ui.button(on_click=lambda: left_drawer_open(left_drawer), icon="keyboard_double_arrow_right").props("flat").classes("text-grey-6 max-lg:hidden").bind_visibility_from(
                app.storage.client, "left_drawer_right_arrow_visible"
            )
            ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").classes("text-grey-6 lg:hidden").props("flat")

        with ui.element("div").classes("flex items-center gap-2"):
            ui.button(on_click=lambda: right_drawer.toggle(), icon="menu").props("flat").classes("text-grey-6").bind_visibility_from(app.storage.client, "right_drawer_left_arrow_visible")

        return header
