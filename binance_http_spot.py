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

class TransferMethod(Enum):
    MAIN_C2C = "MAIN_C2C"
    #现货钱包转向C2C钱包
    MAIN_UMFUTURE = "MAIN_UMFUTURE"
    #现货钱包转向U本位合约钱包
    MAIN_CMFUTURE = "MAIN_CMFUTURE"
    #现货钱包转向币本位合约钱包
    MAIN_MARGIN = "MAIN_MARGIN"
    #现货钱包转向杠杆全仓钱包
    MAIN_MINING = "MAIN_MINING"
    #现货钱包转向矿池钱包
    C2C_MAIN = "C2C_MAIN"
    #C2C钱包转向现货钱包
    CMFUTURE_MAIN = 'CMFUTURE_MAIN'

class BinanceHttpClient(object):
    def __init__(self, base_url=None, api_key=None, api_secret=None, timeout=5):
        # if base_url:
        #     self.base_url = base_url
        # else:
        #     self.base_url = 'https://fapi.binance.com'  #  https://fapi.binance.co

        self.base_url = base_url if base_url else "https://api.binance.com"
        self.key = api_key
        self.secret = api_secret
        self.timeout = timeout

    def build_parameters(self, params:dict):
        return '&'.join([f"{key}={params[key]}" for key in params.keys()])

    def request(self, method: RequestMethod, path, params=None, verify=False):
        url = self.base_url + path

        if params:

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
        #print(res.status_code)
        #print(res)
        #return res.json()
        #data = res.json()
        #print(res.status_code)
        if res.status_code == 200:
            data = res.json()
            if 'code' in data.keys():
                print(data)
                return 0
            else:
                return data
        else:
            print("spot status_code", res.status_code)
            print(res.json())
            return 0
        #    print(data)
        #    return 0
        #else:
        #    return data

    def get_server_status(self):
        path = '/api/v3/ping'
        return self.request(RequestMethod.GET, path)
        # url = self.base_url + path
        # print(url)
        #
        # response_data = requests.get(url, timeout=self.timeout).json()
        # return response_data

    def get_exchange_timestamp(self):
        path = "/api/v3/time"
        return self.request(RequestMethod.GET, path)['serverTime']
        # url = self.base_url + path
        # response_data = requests.get(url, timeout=self.timeout).json()
        # return response_data

    def get_exchange_info(self):
        path = '/api/v3/exchangeInfo'
        return self.request(RequestMethod.GET, path)
        # url = self.base_url + path
        # response_data = requests.get(url, timeout=self.timeout).json()
        # return response_data

    def get_market_depth(self, symbol, limit=5):
        path = '/api/v3/depth'

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
        path = '/api/v3/klines'
        params = {"symbol": symbol,
                  "interval": interval.value,
                  "limit": limit
                  }
        if start_time:
            params['startTime'] = start_time

        if end_time:
            params['endTime'] = end_time

        return self.request(RequestMethod.GET, path, params=params)
        # url = self.base_url + path
        # response_data = requests.get(url, params=params, timeout=self.timeout).json()
        # return response_data

    def get_ticker_price(self, symbol=None):
        path = "/api/v1/ticker/price"
        url = self.base_url + path

        if symbol:
            url += '?symbol=' + symbol

        response_data = requests.get(url, timeout=self.timeout).json()
        return response_data

    def get_book_ticker(self, symbol=None):
        path = '/api/v1/ticker/bookTicker'
        url = self.base_url + path

        params = None
        if symbol:
            # url += '?symbol=' + symbol
            params = {'symbol': symbol}

        return self.request(RequestMethod.GET, path, params=params)

    def get_latest_price(self, symbol=None):
        path = '/api/v3/ticker/price'
        url = self.base_url + path

        params = None
        if symbol:
                # url += '?symbol=' + symbol
            params = {'symbol': symbol}

        return self.request(RequestMethod.GET, path, params=params)

    def get_24_hour_chg(self, symbol=None):
        url = 'https://api.binance.com/api/v3/ticker/24hr'
        #url = self.base_url + path

        params = None
        if symbol:
            # url += '?symbol=' + symbol
            params = {'symbol': symbol}

        return requests.get(url, params=params).json()


    ############# private api ###############

    def get_timestamp(self):
        return int(time.time() * 1000)

    def place_order(self, symbol, side: Side, type_: OrderType, timestamp, quantity=None, quoteOrderQty=None, price=None,stop_price=None, time_inforce=TimeInForce.GTC,recv_window=5000, is_test = False):
        if is_test:
        #path = '/api/v1/order'
            path = '/api/v3/order/test'
        else:
            path = '/api/v3/order'
        params = {

            "symbol": symbol,
            "side": side.value,
            "type": type_.value,
#            "quantity": quantity,
            "recvWindow": recv_window,
            "timestamp": timestamp*1000
        }
        if quantity:
            params['quantity'] = quantity

        if type_.value == OrderType.LIMIT.value:
            params["timeInForce"] = time_inforce.value

            if price > 0:
                params['price'] = price
            else:
                raise ValueError("price 不能为空")

        if type_.value == OrderType.MARKET.value:
            if quoteOrderQty:
                params['quoteOrderQty'] = quoteOrderQty

        if type_.value == OrderType.STOP.value:
            if stop_price > 0:
                params['stopPrice'] = stop_price  # 做多： 8000， 7800， 7790
            else:
                raise ValueError("stop price 不能为空")

            if price > 0:
                params['price'] = price
            else:
                raise ValueError("price 不能为空")
        #print(params)
        return self.request(RequestMethod.POST, path, params=params, verify=True)



    def get_order(self, symbol, order_id, recv_window=5000):
        path = '/api/v1/order'
        params = {'symbol': symbol,
                  "recvWindow": recv_window,
                  "timestamp": self.get_timestamp(),
                  "orderId": order_id
                  }

        return self.request(RequestMethod.GET, path, params=params, verify=True)

    def get_account_info(self,  timestamp=None, recv_window=5000):
        path = '/api/v3/account'
        if timestamp:
            params = {
                  "recvWindow": recv_window,
                  "timestamp": int(timestamp*1000),
                  }
        else:
            params = {
                "recvWindow": recv_window,
                "timestamp": self.get_timestamp(),
            }
        return self.request(RequestMethod.GET, path, params=params, verify=True)



    def cancel_order(self, symbol, order_id, recv_window=5000):
        path = '/api/v1/order'
        params = {'symbol': symbol,
                  "recvWindow": recv_window,
                  "timestamp": self.get_timestamp(),
                  "orderId": order_id
                  }

        return self.request(RequestMethod.DELETE, path, params=params, verify=True)



    def get_open_orders(self, symbol, recv_window=5000):
        path = '/api/v1/openOrders'
        params = {'symbol': symbol,
                  "recvWindow": recv_window,
                  "timestamp": self.get_timestamp()
                  }

        return self.request(RequestMethod.GET, path, params=params, verify=True)

    def transfer(self, type, asset, amount, timestamp):

        """
        MAIN_C2C
        现货钱包转向C2C钱包
        MAIN_UMFUTURE
        现货钱包转向U本位合约钱包
        MAIN_CMFUTURE
        现货钱包转向币本位合约钱包
        MAIN_MARGIN
        现货钱包转向杠杆全仓钱包
        MAIN_MINING
        现货钱包转向矿池钱包
        C2C_MAIN
        C2C钱包转向现货钱包
        C2C_UMFUTURE
        C2C钱包转向U本位合约钱包
        C2C_MINING
        C2C钱包转向矿池钱包
        UMFUTURE_MAIN
        U本位合约钱包转向现货钱包
        UMFUTURE_C2C
        U本位合约钱包转向C2C钱包
        UMFUTURE_MARGIN
        U本位合约钱包转向杠杆全仓钱包
        CMFUTURE_MAIN
        币本位合约钱包转向现货钱包
        MARGIN_MAIN
        杠杆全仓钱包转向现货钱包
        MARGIN_UMFUTURE
        杠杆全仓钱包转向U本位合约钱包
        MINING_MAIN
        矿池钱包转向现货钱包
        MINING_UMFUTURE
        矿池钱包转向U本位合约钱包
        MINING_C2C
        矿池钱包转向C2C钱包
        MARGIN_CMFUTURE
        杠杆全仓钱包转向币本位合约钱包
        CMFUTURE_MARGIN
        币本位合约钱包转向杠杆全仓钱包
        MARGIN_C2C
        杠杆全仓钱包转向C2C钱包
        C2C_MARGIN
        C2C钱包转向杠杆全仓钱包
        MARGIN_MINING
        杠杆全仓钱包转向矿池钱包
        MINING_MARGIN
        矿池钱包转向杠杆全仓钱包
        MAIN_PAY
        现货钱包转向支付钱包
        PAY_MAIN
        支付钱包转向现货钱包
        ISOLATEDMARGIN_MARGIN
        杠杆逐仓钱包转向杠杆全仓钱包
        MARGIN_ISOLATEDMARGIN
        杠杆全仓钱包转向杠杆逐仓钱包
        ISOLATEDMARGIN_ISOLATEDMARGIN
        杠杆逐仓钱包转向杠杆逐仓钱包
        """
        path = '/sapi/v1/asset/transfer'
        params = {
            "type": type.value,
            "asset": asset,
            "amount": amount,
            "timestamp": timestamp*1000
        }
        #print(params)

        return self.request(RequestMethod.POST, path, params=params, verify=True)


    def loan(self, asset, amount, timestamp, isIsolated = False, symbol = None):

        path = '/sapi/v1/margin/loan'
        params = {
            "asset": asset,
            "amount": amount,
            "timestamp": int(timestamp*1000),
            "recvWindow": 50000
        }

        if isIsolated:
            params['isIsolated'] = True
            params['symbol'] = symbol
        #print(params)


        return self.request(RequestMethod.POST, path, params=params, verify=True)



