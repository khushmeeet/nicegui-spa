from models import Symbol
from models.enums import SymbolType


class NewSymbolData:
    id: int = None
    symbol: str = None
    description: str = None
    type: str = None

    def get_db_symbol(self):
        return Symbol(
            symbol=self.symbol,
            description=self.description,
            type=SymbolType(self.type),
        )
