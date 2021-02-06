import os

from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from threading import Thread

import order as o


class Report:
    PAGE_SIZE = A4

    generated: bool
    order: 'o.Order'

    def __init__(self, order: 'o.Order'):
        self.generated = False
        self.order = order

        self.path = os.path.join("report", "reports", f"{self.order.id}.pdf")

    def generate(self):
        Thread(target=self.generate_pdf).start()

    def generate_pdf(self):
        canvas = Canvas(self.path, Report.PAGE_SIZE)
        canvas.setTitle(f"Report of Order Execution - {self.order.id}")

        lines = [
            ["Report of Order Execution", f"{datetime.now()}"],
            ["Order:", f"{self.order.id}"],
            ["Company:", f"{self.order.company.name} ({self.order.company.ticker.upper()})"],
            ["Order time:", f"{self.order.time}"],
            ["Execution completion time:", f"{self.order.trades[-1].time}"],
            ["Direction:", f"{self.order.direction.name}"],
            ["Quantity:", f"{self.order.quantity}"],
            ["Limit:", f"${self.order.limit}" if self.order.limit else self.order.type.name],
            ["Average Price:", f"${round(self.order.value / self.order.quantity, 4)}"],
            ["Total Value:", f"${self.order.value}"],
            ["Trades:", ""]
        ]

        lines.extend([["", f"{trade.quantity} @ ${trade.price}"] for trade in self.order.trades])

        line_height = 277*mm

        for line in lines:
            canvas.drawString(15*mm, line_height, line[0])
            canvas.drawString(75*mm, line_height, line[1])
            line_height -= 10*mm

        canvas.save()

        self.generated = True
