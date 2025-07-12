import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nicegui import ui, app

from routers import Router
from header import header
from left_drawer import left_drawer
from right_drawer import right_drawer
from pages import pages
from models import Strategy, Symbol, Broker

from data.queries import get_all_items_from_account, get_all_items_from_trade, get_all_items_from_table


@ui.page("/")
@ui.page("/{path:path}")
def main(path: str = None):
    router = Router()

    app.storage.client["left_drawer_left_arrow_visible"] = True
    app.storage.client["left_drawer_right_arrow_visible"] = False
    app.storage.client["right_drawer_width"] = 400
    app.storage.client["right_drawer_visible"] = False
    app.storage.client["active_page"] = "dashboard"
    app.storage.client["accounts_df"] = get_all_items_from_account()
    app.storage.client["trades_df"] = get_all_items_from_trade()
    app.storage.client["strategies_df"] = get_all_items_from_table(Strategy, ["id", "name", "description", "tag"])
    app.storage.client["symbols_df"] = get_all_items_from_table(Symbol, ["id", "symbol", "description", "type", "sector", "industry", "country", "currency", "exchange"])
    app.storage.client["brokers_df"] = get_all_items_from_table(Broker, ["id", "name"])

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
