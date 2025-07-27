from enum import Enum


class SymbolType(str, Enum):
    forex = "Forex"
    crypto = "Crypto"
    index = "Index"
    commodity = "Commodity"
    metal = "Metal"
    stock = "Stock"
    future = "Future"
    bond = "Bond"
    cfd = "CFD"
