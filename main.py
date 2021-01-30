from flask import Flask, request

from company import Company
from order import Order, OrderDirection

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
    return Order.get(order_id)


if __name__ == '__main__':
    Company(name="Bailey's company", ticker="BAI")
    Company(name="AAA", ticker="AAA")

    app.run()
