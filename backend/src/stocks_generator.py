from random import random
import time

from src.settings import START_PRICE
from src.storage import stocks_runtime, move_runtime_values_to_memory


def generate_movement():
    movement = -1 if random() < 0.5 else 1
    return movement


def uwsgi_task():
    while True:
        for stock_name in stocks_runtime.values():
            value = (stock_name[-1] if stock_name else START_PRICE) + generate_movement()
            value = value or 0  # цена акции не может быть отрицательной
            stock_name.append(value)
        if len(stocks_runtime['ticker_01']) % 60 == 0:
            move_runtime_values_to_memory()
        time.sleep(1)