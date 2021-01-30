from decimal import Decimal

from typing import Dict


class Company:
    name: str
    ticker: str

    bid: Decimal
    ask: Decimal
    price: Decimal

    companies: Dict[str, 'Company'] = {}

    def __init__(self,
                 name: str,
                 ticker: str):
        self.name = name
        self.ticker = ticker.lower()

        self.bid = Decimal(0)
        self.ask = Decimal(0)
        self.price = Decimal(0)

        Company.companies[self.ticker] = self

    @classmethod
    def get(cls, company: str) -> 'Company':
        return cls.companies[company.lower()]

    @classmethod
    def list(cls) -> Dict[str, 'Company']:
        return cls.companies
