import os

from reportlab.pdfgen.canvas import Canvas
from threading import Thread

import order as o


class Report:
    generated: bool
    order: 'o.Order'

    def __init__(self, order: 'o.Order'):
        self.generated = False
        self.order = order

    def generate(self):
        Thread(target=self.generate_pdf).start()

    def generate_pdf(self):
        print(os.getcwd())
        canvas = Canvas(os.path.join("report", "reports", f"{self.order.id}.pdf"))
        canvas.drawString(72, 72, "Hello, World")
        canvas.save()

        self.generated = True
