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
                 ticker: str,
                 price: Decimal):
        self.name = name
        self.ticker = ticker.lower()
        self.price = price

        self.bid = price
        self.ask = price

        Company.companies[self.ticker] = self

    @classmethod
    def get(cls, company: str) -> 'Company':
        return cls.companies[company.lower()]

    @classmethod
    def list(cls) -> Dict[str, 'Company']:
        return cls.companies
