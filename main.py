from decimal import Decimal
from flask import Flask, request

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


@app.route("/order", methods=["GET"])
def get_orders():
    return to_dict(Order.get())


@app.route("/order/<int:order_id>", methods=["GET"])
def get_order(order_id: int):
    return to_dict(Order.get(order_id))


@app.route("/company/<string:ticker>", methods=["GET"])
def get_company(ticker: str):
    return to_dict(Company.get(ticker))


if __name__ == '__main__':
    app.run()
