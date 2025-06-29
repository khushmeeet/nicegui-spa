import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from routers import Router
from header import header
from left_drawer import left_drawer
from right_drawer import right_drawer

from nicegui import ui, app

from pages import dashboard, accounts


@ui.page("/")
@ui.page("/{_:path}")
def main():
    router = Router()


    app.storage.client["left_drawer_left_arrow_visible"] = True
    app.storage.client["left_drawer_right_arrow_visible"] = False
    app.storage.client["right_drawer_left_arrow_visible"] = True
    app.storage.client["right_drawer_right_arrow_visible"] = False
    app.storage.client["active_page"] = "dashboard"
    app.storage.client["menu_items"] ={
        "dashboard": {
            "show": dashboard,
            "object": None,
            "label": "Dashboard",
            "icon": "dashboard",
            "path": "/",
        },
        "accounts": {
            "show": accounts,
            "object": None,
            "label": "Accounts",
            "icon": "business_center",
            "path": "/accounts",
        },
    }

    ld = left_drawer(router)
    rd = right_drawer()
    header(ld, rd)

    app.storage.client["right_drawer"] = rd
    app.storage.client["right_drawer_rendered_by"] = ""


    for item in app.storage.client["menu_items"].values():
        router.add(item["path"])(item["show"])


    router.frame().classes("w-full p-5 pt-0 gap-0")


ui.run(port=8123)
