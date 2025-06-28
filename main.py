import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from routers import Router
from header import header
from left_drawer import left_drawer
from right_drawer import right_drawer
from state import get_state

from nicegui import ui, app


@ui.page("/")
@ui.page("/{_:path}")
def main():
    router = Router()

    state = get_state()

    ld = left_drawer(router)
    rd = right_drawer()
    header(ld, rd)
    app.storage.client["right_drawer"] = rd
    app.storage.client["right_drawer_rendered_by"] = ""


    for item in state["menu_items"].values():
        router.add(item["path"])(item["show"])


    router.frame().classes("w-full p-5 pt-0 gap-0")


ui.run(port=8123)
