import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nicegui import ui, app

from routers import Router
from header import header
from left_drawer import left_drawer
from right_drawer import right_drawer
from pages import pages


@ui.page("/")
@ui.page("/{path:path}")
def main(path: str = None):
    router = Router()

    app.storage.client["left_drawer_left_arrow_visible"] = True
    app.storage.client["left_drawer_right_arrow_visible"] = False
    app.storage.client["right_drawer_width"] = 400
    app.storage.client["right_drawer_visible"] = True
    app.storage.client["active_page"] = "dashboard"

    app.storage.client["active_page"] = path.strip("/") if path.strip("/") else "dashboard"

    ld = left_drawer(router)
    rd = right_drawer()
    header(ld, rd)

    app.storage.client["right_drawer"] = rd
    app.storage.client["right_drawer_rendered_by"] = ""

    for page in pages.values():
        router.add(page["path"])(page["show"])

    router.frame().classes("w-full p-5 pt-0 gap-0").on("open", lambda e: router.open(e.args))


ui.run(port=8123)
