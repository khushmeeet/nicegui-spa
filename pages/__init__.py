from .dashboard import dashboard
from .accounts import accounts

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
}
