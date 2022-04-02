from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import datetime

from src.storage import stocks_runtime, stocks_storage
from src.utils import iter_property

app = Flask(__name__)
cors = CORS(app)


@app.route('/ticker/')
@cross_origin()
def get_tickers():
    return jsonify(list(stocks_runtime.keys()))


@app.route('/ticker/<ticker_id>')
@cross_origin()
def get_ticker_by_id(ticker_id: int):
    range_cnt = int(request.args.get('range_cnt', 15))
    range_type = request.args.get('range_type', 's')
    last_minute_show = int(request.args.get('last_minute_show'))
    aggregation_type = request.args.get('aggregation_type', 'avg')

    if range_type == 's':
        last_minute_show *= 60
    point_cnt = int(last_minute_show / range_cnt)

    assert range_type in ['s', 'm'], 'допустимые варианты группировки ("s", "m")'
    assert aggregation_type in ['avg', 'min', 'max'], 'допустимые варианты агрегации ("avg", "min", "max")'
    assert 0 < point_cnt <= 120, "количество точек ограничено (не более 120)"

    today = datetime.datetime.now()
    step = range_cnt

    if range_type == 's':
        assert range_cnt >= 1
        assert range_cnt <= 60

        # секунды надо группировать к целым числам шага, иначе график будет постоянно дергаться,
        # тк в группы границы групп постоянно едут
        to_whole = (len(stocks_runtime[ticker_id]) - 60) % step  # до целого значения шага
        if to_whole > 0:
            values = stocks_runtime[ticker_id][-(step * point_cnt) - to_whole:-to_whole]
            today = today - datetime.timedelta(seconds=to_whole)
        else:
            values = stocks_runtime[ticker_id][-(step * point_cnt):]

        def get_seconds_range_by_step(step_num):
            return values[step * step_num:step * (step_num + 1)]

        return jsonify([
            {
                'name': (today - datetime.timedelta(seconds=int(len(values) - step_num * step + step / 2))).strftime('%H:%M:%S'),
                'avg': int(sum(seconds)/step),
                'min': min(seconds),
                'max': max(seconds),
            }
            for step_num, seconds in iter_property(range(int(len(values) / step)), get_seconds_range_by_step)
        ])

    if range_type == 'm':
        assert range_cnt <= 60
        if stocks_storage[ticker_id].get(today.hour) is None:
            return jsonify([])
        values = stocks_storage[ticker_id][today.hour]['value']
        groups_amount = int(len(values) / step)
        groups_amount = point_cnt if groups_amount > point_cnt else groups_amount
        start_minute = max(values.keys()) + 1 - groups_amount * step

        def get_minute_range_by_step(step_num):
            return (
                values[minute]
                for minute in range(start_minute + step * step_num, start_minute + step * (step_num + 1))
                if values.get(minute) is not None
            )

        return jsonify([
            {
                'name': (today - datetime.timedelta(minutes=int(step * groups_amount - step * step_num))).strftime('%H:%M'),
                'avg': int(sum([minute['avg'] for minute in minute_aggregated_list]) / step),
                'max': max([minute['max'] for minute in minute_aggregated_list]),
                'min': min([minute['min'] for minute in minute_aggregated_list]),
            }
            for step_num, minute_aggregated_list in iter_property(range(groups_amount), get_minute_range_by_step)
        ])
