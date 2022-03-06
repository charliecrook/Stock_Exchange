import random
import time
import datetime
from datetime import timedelta

# function to generate a random date
def random_date(start, end):
    frmt = '%d-%m-%Y %H:%M:%S'

    stime = time.mktime(time.strptime(start, frmt))
    etime = time.mktime(time.strptime(end, frmt))

    ptime = stime + random.random() * (etime - stime)
    dt = datetime.datetime.fromtimestamp(time.mktime(time.localtime(ptime)))
    return dt

# function creates a dictionary of orders of form {reference_no: [stock_name, price, quantity, timestamp]}
def create_orders(stocks, ref):
    orders = {}
    for stock in stocks:
        orders[ref] = [stock, round(random.uniform(0.01, 100.00), 2), random.randrange(1, 100, 1), random_date("10-01-2022 09:00:00", "14-01-2022 18:00:00")]
        ref += 1
    return orders