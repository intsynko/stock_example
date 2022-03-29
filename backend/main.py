from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from random import random
from threading import Thread
import time


app = Flask(__name__)
cors = CORS(app)
START_PRICE = 15


stocks = {'ticker_' + f"{i}".zfill(2): [] for i in range(100)}


def uwsgi_task():
    while True:
        for stock in stocks.values():
            value = (stock[-1] if stock else START_PRICE) + generate_movement()
            value = value or 0  # цена акции не может быть отрицательной
            stock.append(value)
        time.sleep(1)


def generate_movement():
    movement = -1 if random() < 0.5 else 1
    return movement


@app.route('/')
@cross_origin()
def hello_world():
    range_ = int(request.args.get('range', 5))
    response = jsonify({stock: values[-range_:] for stock, values in stocks.items()})
    return response



if __name__ == "__main__":
    Thread(target=uwsgi_task).start()
    # uwsgi_task()
    app.run('127.0.0.1', 5000, debug=True)