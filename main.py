import json
import time

from decimal import Decimal
from enum import Enum
from flask import Flask, request
from json import JSONEncoder

from company import Company
from order import Order, OrderDirection, OrderType
from tools import to_dict

app = Flask(__name__)


@app.route("/buy", methods=["POST"])
def buy_stock():
    request_body = request.json
    order = Order(OrderDirection.BUY, **request_body)
    order.execute()
    return str(order.id)


@app.route("/sell", methods=["POST"])
def sell_stock():
    request_body = request.json
    order = Order(OrderDirection.SELL, **request_body)
    order.execute()
    return str(order.id)


@app.route("/order/<int:order_id>", methods=["GET"])
def get_order(order_id: int):
    return to_dict(Order.get(order_id))


if __name__ == '__main__':
    Company(name="Bailey's company", ticker="BAI", price=Decimal(15.00))
    Company(name="AAA", ticker="AAA", price=Decimal(100.00))

    Order(OrderDirection.BUY, order_type=OrderType.MARKET, company=Company.get("BAI"), quantity=10).execute()
    Order(OrderDirection.BUY, order_type=OrderType.MARKET, company=Company.get("BAI"), quantity=10).execute()
    Order(OrderDirection.BUY, order_type=OrderType.MARKET, company=Company.get("BAI"), quantity=10).execute()
    Order(OrderDirection.SELL, order_type=OrderType.MARKET, company=Company.get("BAI"), quantity=31).execute()

    app.run()
