from pages import dashboard, accounts


__state = {
    "left_drawer_left_arrow_visible": True,
    "left_drawer_right_arrow_visible": False,
    "right_drawer_left_arrow_visible": True,
    "right_drawer_right_arrow_visible": False,
    "active_page": "dashboard",
    "menu_items": {
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
}

def get_state():
    return __state
