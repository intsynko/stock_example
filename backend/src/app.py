from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import datetime

from src.storage import stocks_runtime, stocks_storage

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

    if range_type == 's':
        last_minute_show *= 60
    point_cnt = int(last_minute_show / range_cnt)

    assert point_cnt <= 120, "количество точек ограничено (не более 120)"

    today = datetime.datetime.now()
    step = range_cnt

    if range_type == 's':
        assert range_cnt >= 1
        assert range_cnt <= 60

        # секунды надо группировать к целым числам шага, иначе график будет постоянно дергаться,
        # тк в группы границы групп постоянно едут
        to_whole = (len(stocks_runtime[ticker_id]) - 60) % step
        if to_whole > 0:
            ranges = stocks_runtime[ticker_id][-(step * point_cnt) - to_whole:-to_whole]
            today = today - datetime.timedelta(seconds=to_whole)
        else:
            ranges = stocks_runtime[ticker_id][-(step * point_cnt):]

        def sign(index):
            stamp = today - datetime.timedelta(seconds=int(len(ranges) - index * step + step / 2))
            return stamp.strftime('%H:%M:%S')

        return jsonify([
            {
                'name': sign(i),
                'value': int(sum(ranges[step * i:step * (i + 1)]) / step),
            }
            for i in range(int(len(ranges) / step))
        ])

    if range_type == 'm':
        assert range_cnt <= 60

        ranges = stocks_storage[ticker_id][today.hour]['value']
        groups_amount = int(len(ranges) / step)
        groups_amount = point_cnt if groups_amount > point_cnt else groups_amount
        start_minute = today.minute - groups_amount * step

        def sign(i):
            stamp = today - datetime.timedelta(minutes=int(step * groups_amount - step * i))
            return stamp.strftime('%H:%M')

        return jsonify([
            {
                'name': sign(i),
                'value': int(sum([ranges[j]['avg']
                                  for j in range(start_minute + step * i,start_minute + step * (i+1))
                                  if ranges.get(j) is not None]
                                 ) / step)
            }
            for i in range(groups_amount)
        ])
