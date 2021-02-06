from decimal import Decimal

from typing import Dict, Type, TypeVar

_T = TypeVar("_T")


class Entity:
    ticker: str

    bid: Decimal
    ask: Decimal
    price: Decimal

    entities: Dict[str, 'Entity'] = {}

    def __init__(self,
                 ticker: str,
                 price: Decimal):
        self.ticker = ticker.upper()
        self.price = price

        self.bid = price
        self.ask = price

        Entity.entities[self.ticker] = self

    @classmethod
    def get(cls, ticker: str) -> 'Entity':
        return cls.entities[ticker.upper()]

    @classmethod
    def list(cls: Type[_T]) -> Dict[str, _T]:
        return {ticker: entity for ticker, entity in Entity.entities.items() if isinstance(entity, cls)}


class Company(Entity):
    name: str

    def __init__(self,
                 name: str,
                 ticker: str,
                 price: Decimal):
        super().__init__(ticker, price)
        self.name = name
