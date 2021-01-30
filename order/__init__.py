from datetime import datetime
from decimal import Decimal
from enum import Enum

from company import Company
from tools import mean

from typing import Dict, List, Optional, Union


class OrderQueue:
    oq: 'OrderQueue' = None

    def __init__(self):
        if OrderQueue.oq:
            raise ValueError()

        self.queue: Dict['OrderDirection', Dict[str, Optional['OrderQueueItem']]] = {
            OrderDirection.BUY: {},
            OrderDirection.SELL: {}
        }
        OrderQueue.oq = self

    def execute(self, order: 'Order') -> None:
        if order.company.ticker not in self.queue[order.direction]:
            self.queue[order.direction][order.company.ticker] = None

        if order.company.ticker not in self.queue[order.direction.opposite()]:
            self.queue[order.direction.opposite()][order.company.ticker] = None

        self.trade(order)

        if order.executed < order.quantity:
            self.add(order)

    def trade(self, order: 'Order') -> None:
        head: OrderQueueItem = self.queue[order.direction.opposite()][order.company.ticker]
        prev: Optional[OrderQueueItem] = None
        direction: int = order.direction.int()

        while head is not None:
            trade: Optional['Trade'] = None
            prev_set = False
            if order.type is OrderType.MARKET or head.order.type is OrderType.MARKET:
                trade = Trade(order, head.order)

            else:
                if direction * order.limit <= direction * head.order.limit:
                    trade = Trade(order, head.order)

            if trade is not None:
                if head.order.executed == head.order.quantity:
                    if prev:
                        prev.next = head.next
                        prev_set = True
                    else:
                        self.set_head(head.order.direction, head.order.company, head.next)
                        prev_set = True

                if order.executed == order.quantity:
                    break

            if not prev_set:
                prev = head
            head = head.next

    def add(self, order: 'Order') -> None:
        head: OrderQueueItem = self.queue[order.direction][order.company.ticker]
        prev: Optional[OrderQueueItem] = None
        direction: int = order.direction.int()
        order_queue_item: OrderQueueItem = OrderQueueItem(order)

        if head is None:
            self.set_head(order_queue_item.order.direction, order_queue_item.order.company, order_queue_item)
            return

        while head is not None:
            if head.order.type is not OrderType.MARKET and \
                    (order.type is OrderType.MARKET or direction * order.limit < direction * head.order.limit):
                break

            prev = head
            head = head.next

        if prev:
            prev.next = order_queue_item
        else:
            self.set_head(order_queue_item.order.direction, order_queue_item.order.company, order_queue_item)
        order_queue_item.next = head

    def set_head(self,
                 direction: 'OrderDirection',
                 company: Company,
                 order_queue_item: Optional['OrderQueueItem']) -> None:
        self.queue[direction][company.ticker] = order_queue_item

        if order_queue_item is not None:
            if order_queue_item.order.type is not OrderType.MARKET and \
                    order_queue_item.order.direction is OrderDirection.BUY:
                order_queue_item.order.company.bid = order_queue_item.order.limit
            if order_queue_item.order.type is not OrderType.MARKET and \
                    order_queue_item.order.direction is OrderDirection.SELL:
                order_queue_item.order.company.ask = order_queue_item.order.limit

    @classmethod
    def queue(cls) -> 'OrderQueue':
        if not cls.oq:
            cls.oq = cls()
        return cls.oq


class OrderQueueItem:
    order: 'Order'
    next: Optional['OrderQueueItem']

    def __init__(self,
                 order: 'Order'):
        self.order = order
        self.next = None


class OrderDirection(Enum):
    BUY = -1
    SELL = 1

    def opposite(self) -> 'OrderDirection':
        return OrderDirection(-self.value)

    def int(self) -> int:
        return self.value


class OrderType(Enum):
    MARKET = 0
    LIMIT = 1


class Order:
    id: int
    time: datetime
    direction: OrderDirection
    type: OrderType
    company: Company
    quantity: int
    executed: int
    limit: Decimal
    trades: List['TradeOrder']

    current_id: int = 0
    order_list: dict = {}
    order_queue: OrderQueue = OrderQueue.queue()

    def __init__(self,
                 order_direction: OrderDirection,
                 order_type: OrderType,
                 company: Union[Company, str],
                 quantity: int,
                 limit: Optional[Union[Decimal, str]] = None):
        self.id = Order.current_id
        Order.current_id += 1
        Order.order_list[self.id] = self
        self.time = datetime.now()
        self.direction = order_direction if isinstance(order_direction, OrderDirection) else OrderDirection[
            order_direction]
        self.type = order_type if isinstance(order_type, OrderType) else OrderType[order_type]
        self.company = company if isinstance(company, Company) else Company.get(company)
        self.quantity = quantity
        self.executed = 0
        if limit is not None:
            self.limit = limit if isinstance(limit, Decimal) else Decimal(str(limit))
        self.trades = []

    def execute(self) -> None:
        Order.order_queue.execute(self)

    def remaining(self) -> int:
        return self.quantity - self.executed

    @classmethod
    def get(cls, order_id: Optional[int] = None) -> Union['Order', dict]:
        if order_id is None:
            return cls.order_list
        return cls.order_list[order_id]


class Trade:
    orders: List[int]
    quantity: int
    price: Decimal
    time: datetime

    def __init__(self,
                 order_1: Order,
                 order_2: Order):
        self.orders = [order_1.id, order_2.id]
        self.quantity = min(order_1.quantity - order_1.executed, order_2.quantity - order_2.executed)

        if order_2.type is not OrderType.MARKET:
            self.price = order_2.limit
        elif order_1.type is not OrderType.MARKET:
            self.price = order_1.limit
        else:
            self.price = order_1.company.price

        self.time = datetime.now()

        order_1.company.price = self.price
        order_1.executed += self.quantity
        order_1.trades.append(self)
        order_2.executed += self.quantity
        order_2.trades.append(self)
