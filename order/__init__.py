from decimal import Decimal
from enum import Enum

from company import Company
from tools import mean

from typing import Dict, Optional, Union


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
            o1, o2 = None, None
            prev_set = False
            if order.type is OrderType.MARKET:
                o1, o2 = Order.trade(order, head.order)

            if order.type is OrderType.LIMIT:
                if direction * order.limit <= direction * head.order.limit:
                    o1, o2 = Order.trade(order, head.order)

            if o1 is not None and o2 is not None:
                if o2 == head.order.quantity:
                    if prev:
                        prev.next = head.next
                        prev_set = True
                    else:
                        self.set_head(head.order.direction, head.order.company, head.next)
                        prev_set = True

                if o1 == order.quantity:
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
            if direction * order.limit < direction * head.order.limit:
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
            if order_queue_item.order.direction is OrderDirection.BUY:
                order_queue_item.order.company.bid = order_queue_item.order.limit
            if order_queue_item.order.direction is OrderDirection.SELL:
                order_queue_item.order.company.ask = order_queue_item.order.limit

    def print(self):
        for direction, queue in self.queue.items():
            for ticker, head in queue.items():
                while head is not None:
                    print([direction.name, ticker, vars(head.order)])
                    head = head.next

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
        return OrderDirection.BUY if self is OrderDirection.SELL else OrderDirection.SELL

    def int(self) -> int:
        return self.value


class OrderType(Enum):
    MARKET = 0
    LIMIT = 1


class Order:
    id: int
    direction: OrderDirection
    type: OrderType
    company: Company
    quantity: int
    executed: int
    limit: Decimal

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

        self.direction = order_direction if isinstance(order_direction, OrderDirection) else OrderDirection[
            order_direction]
        self.type = order_type if isinstance(order_type, OrderType) else OrderType[order_type]
        self.company = company if isinstance(company, Company) else Company.get(company)
        self.quantity = quantity
        self.executed = 0
        limit = limit or self.company.price
        self.limit = limit if isinstance(limit, Decimal) else Decimal(str(limit))

    def execute(self) -> None:
        Order.order_queue.execute(self)

    def remaining(self) -> int:
        return self.quantity - self.executed

    @classmethod
    def get(cls, order_id: int) -> 'Order':
        return cls.order_list[order_id]

    @staticmethod
    def trade(order_1: 'Order', order_2: 'Order') -> [int, int]:
        order_1_executed = min(order_1.executed + order_2.quantity - order_2.executed, order_1.quantity)
        order_2_executed = min(order_2.executed + order_1.quantity - order_1.executed, order_2.quantity)

        order_1.executed = order_1_executed
        order_2.executed = order_2_executed

        order_1.company.price = mean([order.limit for order in [order_1, order_2] if order.type is OrderType.LIMIT])

        return order_1_executed, order_2_executed
