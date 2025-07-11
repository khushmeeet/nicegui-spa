from nicegui import ui, app
import json


def trading():
    right_drawer = app.storage.client["right_drawer"]
    right_drawer_rendered_by = app.storage.client["right_drawer_rendered_by"]
    stratgies_df = app.storage.client["strategies_df"]

    # ui.markdown("## 🏦 Trading")
    # with ui.row().classes("h-80vh w-full"):
    #     ui.add_body_html(
    #         """
    #             <!-- TradingView Widget BEGIN -->
    #             <div class="tradingview-widget-container" style="height:100%;width:100%">
    #             <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
    #             <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a></div>
    #                 <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js">
    #                 {
    #                     "allow_symbol_change": true,
    #                     "calendar": false,
    #                     "details": false,
    #                     "hide_side_toolbar": false,
    #                     "hide_top_toolbar": false,
    #                     "hide_legend": false,
    #                     "hide_volume": false,
    #                     "hotlist": false,
    #                     "interval": "15",
    #                     "locale": "en",
    #                     "save_image": true,
    #                     "style": "1",
    #                     "symbol": "CAPITALCOM:DXY",
    #                     "theme": "light",
    #                     "timezone": "Etc/UTC",
    #                     "backgroundColor": "#ffffff",
    #                     "gridColor": "rgba(46, 46, 46, 0)",
    #                     "watchlist": [],
    #                     "withdateranges": true,
    #                     "compareSymbols": [],
    #                     "studies": [],
    #                     "autosize": true
    #                 }
    #                 </script>
    #             </div>
    #             <!-- TradingView Widget END -->
    #             """
    #     )

    with ui.column().classes("w-full"):
        with ui.row().classes("w-full"):

            with ui.select(["Option 1", "Option 2", "Option 3"], label="Strategy").props("filled").classes("w-64").add_slot("prepend"):
                ui.icon("tips_and_updates")
            with ui.number(label="Trade Risk", value=1, step=0.05, min=0.1, max=5).props("filled").classes("w-64").add_slot("prepend"):
                ui.icon("percent")
        with ui.row().classes("w-full"):
            with ui.select(["Option 1", "Option 2", "Option 3"], label="Probability").props("filled").classes("w-64").add_slot("prepend"):
                ui.icon("casino")
            with ui.select(["Option 1", "Option 2", "Option 3"], label="Mindstate").props("filled").classes("w-64").add_slot("prepend"):
                ui.icon("psychology")
        with ui.expansion("Common", icon="join_inner", value=True).classes("border"):
            with ui.row().classes("w-full"):
                with ui.number(label="Stop Loss (pips)", value=15, step=1, min=5).props("filled").classes("w-64").add_slot("prepend"):
                    ui.icon("trending_down")
                with ui.number(label="Take Profit (pips)", value=15, step=1, min=5).props("filled").classes("w-64").add_slot("prepend"):
                    ui.icon("trending_up")
                with ui.select(["Option 1", "Option 2", "Option 3"], label="Direction").props("filled").classes("w-64").add_slot("prepend"):
                    ui.icon("import_export")
                with ui.select(["Option 1", "Option 2", "Option 3"], label="Order Type").props("filled").classes("w-64").add_slot("prepend"):
                    ui.icon("shopping_cart")
                with ui.select(["Option 1", "Option 2", "Option 3"], label="Direction based on currency").props("filled").classes("w-64").add_slot("prepend"):
                    ui.icon("currency_exchange")
        with ui.select(["Option 1", "Option 2", "Option 3"], label="Instruments", multiple=True).props("use-chips").props("filled").classes("w-full mb-3").add_slot("prepend"):
            ui.icon("monetization_on")

        grid = ui.aggrid(
            theme="quartz",
            options={
                "columnDefs": [{"headerName": "Selected Currency", "field": "currency"}],
                # 'rowData': grid_rows,
            },
        ).classes("w-full")

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
