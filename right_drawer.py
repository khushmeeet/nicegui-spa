from nicegui import ui, app


def right_drawer():
    width = app.storage.client["right_drawer_width"]
    visible = app.storage.client["right_drawer_visible"]
    with (
        ui.right_drawer(bottom_corner=True, elevated=False, bordered=True, value=visible)
        .props(f"width={width}")
        .classes("bg-gray-100")
        .props("v-touch-drawer")
        .bind_value(app.storage.client, "right_drawer_visible")
    ) as right_drawer:
        return right_drawer
