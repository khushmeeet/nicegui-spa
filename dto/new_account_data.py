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
    portable: bool = True
    server: str = None

    def get_db_account(self, session, mt5_account_info):
        broker = session.query(Broker).filter_by(name=self.broker).first()
        return Account(
            name=self.name,
            broker=broker,
            login=mt5_account_info.login,
            password=self.password,
            type=AccountType(self.type),
            platform=PlatformType(self.platform),
            path=self.path,
            currency=CurrencyType(mt5_account_info.currency),
            starting_balance=mt5_account_info.balance,
            current_balance=mt5_account_info.balance,
            portable=self.portable,
            server=mt5_account_info.server,
            mt5_name=mt5_account_info.name,
            mt5_company=mt5_account_info.company,
            leverage=mt5_account_info.leverage,
        )
