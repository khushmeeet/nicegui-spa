from .dashboard import dashboard
from .analytics import analytics
from .accounts import accounts
from .trading import trading
from .journal import journal
from .general import general

pages = {
    "dashboard": {
        "show": dashboard,
        "object": None,
        "label": "Dashboard",
        "icon": "dashboard",
        "path": "/",
    },
    "trading": {
        "show": trading,
        "object": None,
        "label": "Trading",
        "icon": "candlestick_chart",
        "path": "/trading",
    },
    "analytics": {
        "show": analytics,
        "object": None,
        "label": "Analytics",
        "icon": "insights",
        "path": "/analytics",
    },
    "journal": {
        "show": journal,
        "object": None,
        "label": "Journal",
        "icon": "description",
        "path": "/journal",
    },
    "accounts": {
        "show": accounts,
        "object": None,
        "label": "Accounts",
        "icon": "account_balance",
        "path": "/accounts",
    },
    "general": {
        "show": general,
        "object": None,
        "label": "General",
        "icon": "article",
        "path": "/general",
    },
}
