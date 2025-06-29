from typing import Callable
from nicegui import ui, app

from pages import dashboard, pages

from routers import router


def open_page(key, func, router: router.Router = None):
        app.storage.client["active_page"] = key
        router.open(func)

def on_click(key):
    app.storage.client["active_page"]  = key
    for _key, data in pages.items():
        if data["object"]:
            if _key == key:
                data["object"].classes("bg-gray-300 text-black", remove="text-grey-14")
            else:
                data["object"].classes("text-grey-14", remove="bg-gray-300 text-black")


def open_dashboard(router):
    on_click("dashboard")
    open_page("dashboard", dashboard, router)


def menu_item(key: str, icon: str, label: str, action: Callable, left_drawer: ui.left_drawer = None, router: router.Router = None):
    with (
        ui.item()
        .props("clickable ripple v-ripple")
        .classes("p-3 pl-7 mb-2 text-grey-14")
        .on("click", lambda: open_page(key, action, router))
    ) as item:
        if key == app.storage.client["active_page"]:
            item.classes("bg-gray-300 text-black", remove="text-grey-14")

        item.on(
            "click",
            lambda: on_click(key),
        )
        with ui.item_section().props("avatar").style("min-width: 0;"):
            ui.icon(icon)
        ui.item_section(label).bind_visibility_from(left_drawer.props, "mini")
    return item


def left_drawer(router: router.Router = None):
    with (
            ui.left_drawer(top_corner=True, bottom_corner=True)
            .props("bordered")
            .classes("p-0 gap-3 bg-gray-100") as left_drawer
        ):
            with (
                ui.element("div")
                .classes("p-0 w-full nicegui-header mt-3")
                .style("height: 68px;")
            ):
                with (
                    ui.item()
                    .props("clickable")
                    .classes("p-5 text-3xl w-full h-full")
                    .on("click", lambda: open_dashboard(router))
                ):
                    with ui.item_section().props("avatar").style("min-width: 0;"):
                        ui.icon("analytics", size="1.5em")
                    ui.item_section("Trading App").bind_visibility_from(left_drawer, "mini")


            with ui.list().classes("text-xl").classes("w-full justify-start items-start"):
                for key, data in pages.items():
                    pages[key]["object"] = menu_item(
                        key, data["icon"], data["label"], data["show"], left_drawer, router
                    )
            return left_drawer

def left_drawer_collapse(left_drawer: ui.left_drawer = None):
    left_drawer.props("mini")
    app.storage.client["left_drawer_left_arrow_visible"] = False
    app.storage.client["left_drawer_right_arrow_visible"] = True

def left_drawer_open(left_drawer: ui.left_drawer = None):
    left_drawer.props("mini=False")
    app.storage.client["left_drawer_left_arrow_visible"] = True
    app.storage.client["left_drawer_right_arrow_visible"] = False
