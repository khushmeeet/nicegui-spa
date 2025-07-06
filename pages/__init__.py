from .dashboard import dashboard
from .accounts import accounts
from .trading import trading

pages = {
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
    "trading": {
        "show": trading,
        "object": None,
        "label": "Trading",
        "icon": "candlestick_chart",
        "path": "/trading",
    },
}
