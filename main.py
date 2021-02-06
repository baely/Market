from decimal import Decimal
from flask import Flask, request

import entity as e
import order as o
import portfolio as p

from tools import to_dict

app = Flask(__name__)


@app.route("/buy", methods=["POST"])
def buy_stock():
    request_body = request.json
    order = o.Order(order_direction=o.OrderDirection.BUY, **request_body)
    order.execute()
    return str(order.id)


@app.route("/sell", methods=["POST"])
def sell_stock():
    request_body = request.json
    order = o.Order(order_direction=o.OrderDirection.SELL, **request_body)
    order.execute()
    return str(order.id)


@app.route("/order", methods=["GET"])
def get_orders():
    return to_dict(o.Order.get())


@app.route("/order/<int:order_id>", methods=["GET"])
def get_order(order_id: int):
    return to_dict(o.Order.get(order_id))


@app.route("/company/<string:ticker>", methods=["GET"])
def get_company(ticker: str):
    return to_dict(e.Company.get(ticker))


if __name__ == '__main__':
    app.run()
