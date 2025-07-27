import time
import psutil
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd


class MetaTrader5Client:
    def __init__(self, account, password, server, portable, path):
        self.account = account
        self.password = password
        self.server = server
        self.portable = portable
        self.path = path
        self.connected = False

    def connect(self):
        if not mt5.initialize(login=self.account, password=self.password, server=self.server, portable=self.portable, path=self.path):
            raise ConnectionError(f"MT5 initialization failed: {mt5.last_error()}")
        self.connected = True

    def shutdown(self, terminate=True, wait=True, wait_seconds=1):
        if self.connected:
            mt5.shutdown()
            if terminate:
                if wait:
                    time.sleep(wait_seconds)
                self._terminate()
            self.connected = False

    def get_account_info_mt5(self):
        acc = mt5.account_info()
        if acc is None:
            raise RuntimeError("Failed to get account info")
        return acc

    def get_all_symbols(self, groups=None):
        all_symbols = mt5.symbols_get(groups=groups)
        if all_symbols is None:
            raise RuntimeError("Failed to get symbols list")
        return all_symbols

    def get_symbol_info(self, symbol):
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            raise RuntimeError("Failed to get symbol info")
        return symbol_info

    def _terminate(self):
        # exe_path = os.path.abspath(self)
        for proc in psutil.process_iter(["pid", "name", "exe"]):
            try:
                if proc.info["name"] == "terminal64.exe" and proc.info["exe"] == self.path:
                    proc.terminate()
                    print(f"[KILL] Terminated MT5 terminal at: {self.path}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    # def ensure_symbol(self, symbol):
    #     info = mt5.symbol_info(symbol)
    #     if info is None:
    #         raise ValueError(f"Symbol '{symbol}' not found")
    #     if not info.visible:
    #         mt5.symbol_select(symbol, True)
    #     return info

    # def get_tick(self, symbol):
    #     tick = mt5.symbol_info_tick(symbol)
    #     if tick:
    #         return {"symbol": symbol, "bid": tick.bid, "ask": tick.ask, "last": tick.last, "time": datetime.fromtimestamp(tick.time)}
    #     raise RuntimeError(f"Failed to get tick for {symbol}")

    # def get_candles(self, symbol, timeframe=mt5.TIMEFRAME_M5, count=100):
    #     self.ensure_symbol(symbol)
    #     rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    #     df = pd.DataFrame(rates)
    #     df["time"] = pd.to_datetime(df["time"], unit="s")
    #     return df

    # def place_market_order(self, symbol, volume=0.1, order_type="buy", sl_points=100, tp_points=100):
    #     self.ensure_symbol(symbol)
    #     tick = mt5.symbol_info_tick(symbol)
    #     symbol_info = mt5.symbol_info(symbol)
    #     point = symbol_info.point
    #     price = tick.ask if order_type == "buy" else tick.bid
    #     sl = price - sl_points * point if order_type == "buy" else price + sl_points * point
    #     tp = price + tp_points * point if order_type == "buy" else price - tp_points * point
    #     order_type_enum = mt5.ORDER_TYPE_BUY if order_type == "buy" else mt5.ORDER_TYPE_SELL

    #     request = {
    #         "action": mt5.TRADE_ACTION_DEAL,
    #         "symbol": symbol,
    #         "volume": volume,
    #         "type": order_type_enum,
    #         "price": price,
    #         "sl": sl,
    #         "tp": tp,
    #         "deviation": 10,
    #         "magic": 123456,
    #         "comment": f"{order_type.capitalize()} Order",
    #         "type_time": mt5.ORDER_TIME_GTC,
    #         "type_filling": mt5.ORDER_FILLING_IOC,
    #     }

    #     result = mt5.order_send(request)
    #     if result.retcode != mt5.TRADE_RETCODE_DONE:
    #         raise RuntimeError(f"Order failed: {result.retcode}")
    #     print(f"[MT5] {order_type.capitalize()} order placed at {price}")
    #     return result


# Example usage
if __name__ == "__main__":
    from pprint import pprint

    # 52399047, "9UtKTv0!2MUeaT", "ICMarketsSC-Demo", "D:\\MetaTrader5\\MT_1\\terminal64.exe", True
    client = MetaTrader5Client(
        account=52399047,
        password="9UtKTv0!2MUeaT",
        server="ICMarketsSC-Demo",
        portable=True,
        path="D:\\MetaTrader5\\MT_1\\terminal64.exe",
    )
    try:
        client.connect()
        symbols = client.get_all_symbols()
        # s = symbols._asdict()
        # s_info = client.get_symbol_info("EURUSD")
        # pprint(s)
        with open("symbols.csv", "w") as f:
            f.write("Symbol,Description,Path\n")
            for symbol in symbols:
                f.write(f"{symbol.name},{symbol.description},{symbol.path}\n")

    finally:
        client.shutdown(terminate=False)
