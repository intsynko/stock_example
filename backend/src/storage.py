import datetime

from src.settings import SECONDS_LIFETIME

""" Быстрое хранилище стоимости последних SECONDS_LIFETIME секнунд """
stocks_runtime = {'ticker_' + f"{i}".zfill(2): [] for i in range(10)}

""" Долгое хранилище стоимости в json  в формате 
    { 12: // часы 
        {
            'value': {
                // минуты
                1: {
                 'avg': ...,
                 'max': ...,
                 'min': ...,
                }
                ...
            }
             'avg': ...,
             'max': ...,
             'min': ...,   
             
             // для пересчета среденго значения
             'sum': ...,
             'len': ...,         
        }
    }
"""
stocks_storage = {'ticker_' + f"{i}".zfill(2): {} for i in range(10)}


def init_first_level_unit(value: list):
    return {
        # 'value': value,  # тут можно хранить агрегацию по 5-10 секунд каждой минуты
        'avg': int(sum(value) / len(value)),
        'min': min(value),
        'max': max(value),
    }


def init_unit(sub_unit, key):
    return {
        'value': {
            key: sub_unit,
        },
        'avg': sub_unit['avg'],
        'max': sub_unit['max'],
        'min': sub_unit['min'],
        'sum': sub_unit['avg'],
        'len': 1,
    }


def unit_append(unit, sub_unit, key):
    unit['value'][key] = sub_unit
    if sub_unit['max'] > unit['max']:
        unit['max'] = sub_unit['max']
    if sub_unit['min'] < unit['min']:
        unit['min'] = sub_unit['min']
    unit['sum'] = unit['sum'] + sub_unit['avg']
    unit['len'] += 1
    unit['avg'] = int(unit['sum'] / unit['len'])


def move_runtime_values_to_memory():
    today = datetime.datetime.now()
    for stock_name in stocks_runtime.keys():
        minute_unit = init_first_level_unit(stocks_runtime[stock_name][-60:])
        hour_unit = stocks_storage[stock_name].get(today.hour)
        if hour_unit is None:
            stocks_storage[stock_name][today.hour] = init_unit(minute_unit, today.minute)
        else:
            unit_append(stocks_storage[stock_name][today.hour], minute_unit, today.minute)
        if len(stocks_runtime[stock_name]) > SECONDS_LIFETIME:
            stocks_runtime[stock_name] = stocks_runtime[stock_name][-SECONDS_LIFETIME:]
