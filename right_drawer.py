from nicegui import ui


def right_drawer():
    with ui.right_drawer(bottom_corner=True, elevated=True, bordered=True, value=False).classes("bg-gray-100").props("overlay v-touch-drawer") as right_drawer:
        return right_drawer
