import order as o

from typing import Dict, List


class Portfolio:
    id: int
    orders: List[o.Order]

    current_id: int = 0
    portfolio_list: Dict[int, 'Portfolio'] = {}

    def __init__(self):
        self.id = Portfolio.current_id
        Portfolio.current_id += 1
        self.order = []

    def add_order(self, order: o.Order) -> None:
        self.orders.append(order)
