from models import Account, Broker
from models.enums import AccountType, PlatformType, CurrencyType


class NewAccountData:
    id: int = None
    name: str = None
    broker: str = None
    login: str = None
    password: str = None
    type: str = None
    platform: str = None
    path: str = None
    currency: str = None
    starting_balance: float = 0
    current_balance: float = 0
    portable: bool = True
    server: str = None

    def get_db_account(self, session):
        broker = session.query(Broker).filter_by(name=self.broker).first()
        return Account(
            name=self.name,
            broker=broker,
            login=self.login,
            password=self.password,
            type=AccountType(self.type),
            platform=PlatformType(self.platform),
            path=self.path,
            currency=CurrencyType(self.currency),
            starting_balance=self.starting_balance,
            current_balance=self.current_balance,
            portable=self.portable,
            server=self.server,
        )
