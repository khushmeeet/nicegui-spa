from enum import Enum


class CurrencyType(str, Enum):
    # Major currencies (most traded globally)
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"
    AUD = "AUD"
    CAD = "CAD"
    NZD = "NZD"

    # Minor currencies (frequently traded but less liquid than majors)
    CNY = "CNY"
    HKD = "HKD"
    NOK = "NOK"
    SGD = "SGD"
    KRW = "KRW"
    SEK = "SEK"
    MXN = "MXN"

    # Exotic currencies (less traded, more volatile)
    # INR = "INR"
    # IDR = "IDR"
    # MYR = "MYR"
    # PHP = "PHP"
    # THB = "THB"
    # TRY = "TRY"
    # VND = "VND"
    # ZAR = "ZAR"
    # RUB = "RUB"

    # Crypto (optional, not fiat)
    # BTC = "BTC"
    # ETH = "ETH"


class CurrencySymbol(str, Enum):
    USD = "$"  # US Dollar
    EUR = "€"  # Euro
    GBP = "£"  # British Pound
    JPY = "¥"  # Japanese Yen
    CHF = "Fr"  # Swiss Franc (also sometimes shown as "CHF")
    AUD = "A$"  # Australian Dollar
    CAD = "C$"  # Canadian Dollar
    NZD = "NZ$"  # New Zealand Dollar

    CNY = "CN¥"  # Chinese Yuan (Renminbi) — same symbol as JPY
    HKD = "HK$"  # Hong Kong Dollar
    NOK = "kr"  # Norwegian Krone
    SGD = "S$"  # Singapore Dollar
    KRW = "₩"  # South Korean Won
    SEK = "kr"  # Swedish Krona
    MXN = "MX$"  # Mexican Peso — same symbol as USD


if __name__ == "__main__":
    usd = CurrencyType.USD
    usd_symbol = CurrencySymbol[usd.value]
    print(usd_symbol.value)
