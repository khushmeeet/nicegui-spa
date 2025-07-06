from enum import Enum


class ExitReasonType(str, Enum):
    take_profit = "Take Profit"
    stop_loss = "Stop Loss"
    cancelled = "Cancelled"
    manual = "Manual"
