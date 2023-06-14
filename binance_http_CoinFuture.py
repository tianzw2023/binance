"""
    第4课：这是币安交易所的http request client.
    http client优化.

"""

import requests
import json
from enum import Enum
import time
import hashlib
import hmac


class Interval(Enum):
    MINUTE_1 = '1m'
    MINUTE_3 = '3m'
    MINUTE_5 = '5m'
    MINUTE_15 = '15m'
    MINUTE_30 = '30m'
    HOUR_1 = '1h'
    HOUR_2 = '2h'
    HOUR_4 = '4h'
    HOUR_6 = '6h'

    HOUR_8 = '8h'
    HOUR_12 = '12h'
    DAY_1 = '1d'
    DAY_3 = '3d'
    WEEK_1 = '1w'
    MONTH_1 = '1M'

class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"

class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"

class PositionSide(Enum):
    DUAL = "BOTH"
    SELL = "SELL"


class TimeInForce(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTX = "GTX"

class RequestMethod(Enum):
    GET = "get"
    POST = "post"
    DELETE = "delete"
    PUT = "put"


class BinanceCoinFutureHttpClient(object):
    def __init__(self, base_url=None, api_key=None, api_secret=None, timeout=5):
        # if base_url:
        #     self.base_url = base_url
        # else:
        #     self.base_url = 'https://fapi.binance.com'  #  https://fapi.binance.co

        self.base_url = base_url if base_url else "https://dapi.binance.com"
        self.key = api_key
        self.secret = api_secret
        self.timeout = timeout

    def build_parameters(self, params:dict):

        return '&'.join([f"{key}={params[key]}" for key in params.keys()])
        # requery = ''
        # for key in params.keys():
        #     requery += f"{key}={params[key]}&"
        #
        # requery = requery[0:-1]
        # return requery

    def request(self, method: RequestMethod, path, params=None, verify=False):
        url = self.base_url + path

        if params:
            # print(self.build_parameters(params))
            # {'symbol': 'BTCUSDT', 'limit': 5} #
            # url = url + '？' 'symbol=BTCUSDT&limit=5'
            url = url + '?' + self.build_parameters(params)

        if verify:

            query_str = self.build_parameters(params)
            signature = hmac.new(self.secret.encode('utf-8'), msg=query_str.encode('utf-8'),
                                 digestmod=hashlib.sha256).hexdigest()
            url += '&signature=' + signature

            # response_data = requests.post(url, headers=headers, timeout=self.timeout).json()
            # return response_data

        headers = {"X-MBX-APIKEY": self.key}
        try:
            res = requests.request(method.value, url, headers=headers, timeout=self.timeout)

        except:
            print("no response")
            return 0
        #print(res.json())
        if res.status_code == 200:
            data = res.json()
            #print(data)
            if isinstance(data, list):
                return data
            else:
                if 'code' in data.keys():
                #print(data)
                    return 0
                else:
                    return data
        else:
            print("future status_code", res.status_code)
            print(res.json())
            return 0

    def get_server_status(self):
        path = '/dapi/v1/ping'
        return self.request(RequestMethod.GET, path)
        # url = self.base_url + path
        # print(url)
        #
        # response_data = requests.get(url, timeout=self.timeout).json()
        # return response_data

    def get_exchange_timestamp(self):
        path = "/dapi/v1/time"
        return self.request(RequestMethod.GET, path)['serverTime']
        # url = self.base_url + path
        # response_data = requests.get(url, timeout=self.timeout).json()
        # return response_data

    def get_exchange_info(self):
        path = '/dapi/v1/exchangeInfo'
        return self.request(RequestMethod.GET, path)
        # url = self.base_url + path
        # response_data = requests.get(url, timeout=self.timeout).json()
        # return response_data

    def get_market_depth(self, symbol, limit=5):
        path = '/dapi/v1/depth'

        # url = self.base_url + path

        limits = [5, 10, 20, 50, 100, 500, 1000]
        if limit not in limits:
            # raise ValueError(f"{limit} is not valid depth limit")
            limit = 5

        params = {"symbol": symbol,
                  "limit": limit
                  }

        return self.request(RequestMethod.GET, path, params=params)

        # full_url = url + '?' + "symbol=" + symbol + '&limit=' + str(limit)



        # response_data = requests.get(url, params=params, timeout=self.timeout).json()
        # return response_data

        # full_url = url + '?' + "symbol=" + symbol + '&limit=' + str(limit)
        # response_data = requests.get(full_url, timeout=self.timeout).json()
        # return response_data

    def get_klines(self, symbol, interval: Interval, start_time=None, end_time=None, limit=500):
        path = '/dapi/v1/klines'
        params = {"symbol": symbol,
                  "interval": interval.value,
                  "limit": limit
                  }
        if start_time:
            params['startTime'] = start_time

        if end_time:
            params['endTime'] = end_time

        return self.request(RequestMethod.GET, path, params=params, verify=False)



    def get_ticker_price(self, symbol=None):
        path = "/dapi/v1/ticker/price"
        url = self.base_url + path

        if symbol:
            url += '?symbol=' + symbol

        response_data = requests.get(url, timeout=self.timeout).json()
        return response_data

    def get_book_ticker(self, symbol=None):
        path = '/dapi/v1/ticker/bookTicker'
        url = self.base_url + path

        params = None
        if symbol:
            # url += '?symbol=' + symbol
            params = {'symbol': symbol}

        return self.request(RequestMethod.GET, path, params=params)

    def funding_rate(self):
        path = '/dapi/v1/premiumIndex'
        return self.request(RequestMethod.GET, path)

    def get_24_hour_chg(self, symbol=None):
        url = 'https://fapi.binance.com/fapi/v1/ticker/24hr'
        #url = self.base_url + path

        params = None
        if symbol:
            # url += '?symbol=' + symbol
            params = {'symbol': symbol}

        return requests.get(url, params=params).json()







    ############# private api ###############

    def get_timestamp(self):
        return int(time.time() * 1000)

    def place_order(self, symbol, side: Side,  type_: OrderType, quantity, timestamp, quoteOrderQty=None, price=None,stop_price=None, reduceOnly=False, is_test=False,time_inforce=TimeInForce.GTC,recv_window=5000):
        if is_test == True:
            path = '/dapi/v1/order/test'
        elif is_test == False:
            path = '/dapi/v1/order'
        params = {
            "symbol": symbol,
            #"positionSide":"LONG",
            "side": side.value,
            "type": type_.value,
            "quantity": quantity,
            "recvWindow": recv_window,
            "reduceOnly": reduceOnly,
            "timestamp": self.get_timestamp()
        }

        if type_ == OrderType.LIMIT:
            params["timeInForce"] = time_inforce.value
            if price > 0:
                params['price'] = price
            else:
                raise ValueError("price 不能为空")

        if type_ == OrderType.MARKET:
            if quoteOrderQty:
                params["quoteOrderQty"] = quoteOrderQty

        if type_ == OrderType.STOP:
            if stop_price > 0:
                params['stopPrice'] = stop_price  # 做多： 8000， 7800， 7790
            else:
                raise ValueError("stop price 不能为空")

            if price > 0:
                params['price'] = price
            else:
                raise ValueError("price 不能为空")

        return self.request(RequestMethod.POST, path, params=params, verify=True)


    def get_order(self, symbol, order_id, recv_window=5000):
        path = '/dapi/v1/order'
        params = {'symbol': symbol,
                  "recvWindow": recv_window,
                  "timestamp": self.get_timestamp(),
                  "orderId": order_id
                  }

        return self.request(RequestMethod.GET, path, params=params, verify=True)



    def cancel_order(self, symbol, order_id, recv_window=5000):
        path = '/dapi/v1/order'
        params = {'symbol': symbol,
                  "recvWindow": recv_window,
                  "timestamp": self.get_timestamp(),
                  "orderId": order_id
                  }

        return self.request(RequestMethod.DELETE, path, params=params, verify=True)



    def get_open_orders(self, symbol, recv_window=5000):
        path = '/dapi/v1/openOrders'
        params = {'symbol': symbol,
                  "recvWindow": recv_window,
                  "timestamp": self.get_timestamp()
                  }

        return self.request(RequestMethod.GET, path, params=params, verify=True)

    def adjust_leverage(self, symbol, leverage, timestamp, recv_window=5000):
        path = '/dapi/v1/leverage'

        params = {
                    "symbol": symbol,
                    "leverage": leverage,
                    "recvWindow": recv_window,
                    "timestamp": int(timestamp*1000)
                    }


        return self.request(RequestMethod.POST, path, params=params, verify=True)

    def get_account_details(self, timestamp):
        path = '/dapi/v1/account'
        params = {
                    "timestamp": int(timestamp*1000)
                    }
        return self.request(RequestMethod.GET, path, params=params, verify=True)




