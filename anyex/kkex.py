# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/anyex/anyex/blob/master/CONTRIBUTING.md#how-to-contribute-code

from anyex.base.exchange import Exchange
import base64
import hashlib
import json
from anyex.base.errors import ExchangeError
from anyex.base.errors import NotSupported
from anyex.base.errors import AuthenticationError
from anyex.base.errors import InsufficientFunds
from anyex.base.errors import InvalidOrder
from anyex.base.errors import OrderNotFound


class kkex (Exchange):

    def describe(self):
        return self.deep_extend(super(kkex, self).describe(), {
            'id': 'kkex',
            'name': 'KKEX',
            'countries': 'CN',
            'rateLimit': 240,
            # 'userAgent': self.userAgents['chrome'],
            'has': {
                'CORS': True,
                'fetchOHLCV': True,
                'deposit': True,
                'withdraw': True,
                'fetchOrder': True,
                'fetchOrders': True,
                'fetchOpenOrders': True,
                'fetchClosedOrders': True,
                'fetchMyTrades': True,
            },
            'timeframes': {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '1h': 3600,
                '6h': 21600,
                '1d': 86400,
            },
            'urls': {
                'api': 'https://kkex.com/api',
                'www': 'https://www.kkex.com',
                'doc': 'https://kkex.com/api_wiki/',
                'fees': [
                    'https://intercom.help/kkex/fee',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'v1/chart_feed/config',
                        'v1/chart_feed/time',
                        'v1/chart_feed/symbols',
                        'v1/chart_feed/history',
                        'v1/products',
                        'v1/assets',
                        'v1/exchange_rate',
                        'v1/ticker',
                        'v1/tickers',
                        'v1/depth',
                        'v1/trades',
                        'v1/kline',
                        'v1/orderbook',
                    ],
                },
                'private': {
                    'post': [
                        'v2/profile',
                        'v2/userinfo',

                        'v2/trade',
                        'v2/batch_trade',
                        'v2/cancel_order',
                        'v2/cancel_all_orders',
                        'v2/order_info',
                        'v2/orders_info',
                        'v2/order_history',
                        'v2/download_orders',

                        'v2/withdraw',
                        'v2/withdraw_info',

                        'v2/process_strategy',
                        'v2/cancel_strategy',
                        'v2/batch_cancel_strategy',
                        'v2/history_strategy',
                        'v2/strategy_param',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'taker': 0.002,
                    'maker': 0.002,
                },
            }
        })

    def fetch_markets(self):
        response = self.publicGetV1Products()
        markets = response['all_products']
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['symbol']
            # kkex use base/quote in the wrong way
            base = self.common_currency_code(market['mark_asset'])
            quote = self.common_currency_code(market['base_asset'])
            symbol = base + '/' + quote
            precision = {
                'amount': 8,
                'price': 8,
            }
            limits = {
                # kkex has both bid_amount and bid_size limits
                'amount': {
                    'min': self.safe_float(market, 'max_bid_amount'),
                    'max': self.safe_float(market, 'min_bid_amount'),
                },
                'price': {
                    'min': self.safe_float(market, 'min_price'),
                    'max': self.safe_float(market, 'max_price'),
                }
            }
            limits['cost'] = {
                'min': limits['amount']['min'] * limits['price']['min'],
                'max': None,
            }
            taker = self.fees['trading']['taker']
            maker = self.fees['trading']['maker']
            active = market['status'] == 'OPEN'
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'precision': precision,
                'limits': limits,
                'taker': taker,
                'maker': maker,
                'active': active,
                'info': market,
            })
        return result

    # def fetch_balance(self, params={}):
    #     self.load_markets()
    #     balances = self.privateGetAccounts()
    #     result = {'info': balances}
    #     for b in range(0, len(balances)):
    #         balance = balances[b]
    #         currency = balance['currency']
    #         account = {
    #             'free': self.safe_float(balance, 'available'),
    #             'used': self.safe_float(balance, 'hold'),
    #             'total': self.safe_float(balance, 'balance'),
    #         }
    #         result[currency] = account
    #     return self.parse_balance(result)

    # def fetch_order_book(self, symbol, limit=None, params={}):
    #     self.load_markets()
    #     orderbook = self.publicGetProductsIdBook(self.extend({
    #         'id': self.market_id(symbol),
    #         'level': 2,  # 1 best bidask, 2 aggregated, 3 full
    #     }, params))
    #     return self.parse_order_book(orderbook)

    # def fetch_ticker(self, symbol, params={}):
    #     self.load_markets()
    #     market = self.market(symbol)
    #     request = self.extend({
    #         'id': market['id'],
    #     }, params)
    #     ticker = self.publicGetProductsIdTicker(request)
    #     timestamp = self.parse8601(ticker['time'])
    #     bid = None
    #     ask = None
    #     if 'bid' in ticker:
    #         bid = self.safe_float(ticker, 'bid')
    #     if 'ask' in ticker:
    #         ask = self.safe_float(ticker, 'ask')
    #     last = self.safe_float(ticker, 'price')
    #     return {
    #         'symbol': symbol,
    #         'timestamp': timestamp,
    #         'datetime': self.iso8601(timestamp),
    #         'high': None,
    #         'low': None,
    #         'bid': bid,
    #         'bidVolume': None,
    #         'ask': ask,
    #         'askVolume': None,
    #         'vwap': None,
    #         'open': None,
    #         'close': last,
    #         'last': last,
    #         'previousClose': None,
    #         'change': None,
    #         'percentage': None,
    #         'average': None,
    #         'baseVolume': self.safe_float(ticker, 'volume'),
    #         'quoteVolume': None,
    #         'info': ticker,
    #     }

    # def parse_trade(self, trade, market=None):
    #     timestamp = None
    #     if 'time' in trade:
    #         timestamp = self.parse8601(trade['time'])
    #     elif 'created_at' in trade:
    #         timestamp = self.parse8601(trade['created_at'])
    #     iso8601 = None
    #     if timestamp is not None:
    #         iso8601 = self.iso8601(timestamp)
    #     symbol = None
    #     if not market:
    #         if 'product_id' in trade:
    #             marketId = trade['product_id']
    #             if marketId in self.markets_by_id:
    #                 market = self.markets_by_id[marketId]
    #     if market:
    #         symbol = market['symbol']
    #     feeRate = None
    #     feeCurrency = None
    #     if market:
    #         feeCurrency = market['quote']
    #         if 'liquidity' in trade:
    #             rateType = 'taker' if (trade['liquidity'] == 'T') else 'maker'
    #             feeRate = market[rateType]
    #     feeCost = self.safe_float(trade, 'fill_fees')
    #     if feeCost is None:
    #         feeCost = self.safe_float(trade, 'fee')
    #     fee = {
    #         'cost': feeCost,
    #         'currency': feeCurrency,
    #         'rate': feeRate,
    #     }
    #     type = None
    #     id = self.safe_string(trade, 'trade_id')
    #     side = 'sell' if (trade['side'] == 'buy') else 'buy'
    #     orderId = self.safe_string(trade, 'order_id')
    #     # GDAX returns inverted side to fetchMyTrades vs fetchTrades
    #     if orderId is not None:
    #         side = 'buy' if (trade['side'] == 'buy') else 'sell'
    #     return {
    #         'id': id,
    #         'order': orderId,
    #         'info': trade,
    #         'timestamp': timestamp,
    #         'datetime': iso8601,
    #         'symbol': symbol,
    #         'type': type,
    #         'side': side,
    #         'price': self.safe_float(trade, 'price'),
    #         'amount': self.safe_float(trade, 'size'),
    #         'fee': fee,
    #     }

    # def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
    #     self.load_markets()
    #     market = None
    #     request = {}
    #     if symbol is not None:
    #         market = self.market(symbol)
    #         request['product_id'] = market['id']
    #     if limit is not None:
    #         request['limit'] = limit
    #     response = self.privateGetFills(self.extend(request, params))
    #     return self.parse_trades(response, market, since, limit)

    # def fetch_trades(self, symbol, since=None, limit=None, params={}):
    #     self.load_markets()
    #     market = self.market(symbol)
    #     response = self.publicGetProductsIdTrades(self.extend({
    #         'id': market['id'],  # fixes issue  #2
    #     }, params))
    #     return self.parse_trades(response, market, since, limit)

    # def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
    #     return [
    #         ohlcv[0] * 1000,
    #         ohlcv[3],
    #         ohlcv[2],
    #         ohlcv[1],
    #         ohlcv[4],
    #         ohlcv[5],
    #     ]

    # def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
    #     self.load_markets()
    #     market = self.market(symbol)
    #     granularity = self.timeframes[timeframe]
    #     request = {
    #         'id': market['id'],
    #         'granularity': granularity,
    #     }
    #     if since is not None:
    #         request['start'] = self.ymdhms(since)
    #         if limit is None:
    #             # https://docs.gdax.com/#get-historic-rates
    #             limit = 300  # max = 300
    #         request['end'] = self.ymdhms(self.sum(limit * granularity * 1000, since))
    #     response = self.publicGetProductsIdCandles(self.extend(request, params))
    #     return self.parse_ohlcvs(response, market, timeframe, since, limit)

    # def fetch_time(self):
    #     response = self.publicGetTime()
    #     return self.parse8601(response['iso'])

    # def parse_order_status(self, status):
    #     statuses = {
    #         'pending': 'open',
    #         'active': 'open',
    #         'open': 'open',
    #         'done': 'closed',
    #         'canceled': 'canceled',
    #     }
    #     return self.safe_string(statuses, status, status)

    # def parse_order(self, order, market=None):
    #     timestamp = self.parse8601(order['created_at'])
    #     symbol = None
    #     if not market:
    #         if order['product_id'] in self.markets_by_id:
    #             market = self.markets_by_id[order['product_id']]
    #     status = self.parse_order_status(order['status'])
    #     price = self.safe_float(order, 'price')
    #     amount = self.safe_float(order, 'size')
    #     if amount is None:
    #         amount = self.safe_float(order, 'funds')
    #     if amount is None:
    #         amount = self.safe_float(order, 'specified_funds')
    #     filled = self.safe_float(order, 'filled_size')
    #     remaining = None
    #     if amount is not None:
    #         if filled is not None:
    #             remaining = amount - filled
    #     cost = self.safe_float(order, 'executed_value')
    #     fee = {
    #         'cost': self.safe_float(order, 'fill_fees'),
    #         'currency': None,
    #         'rate': None,
    #     }
    #     if market:
    #         symbol = market['symbol']
    #     return {
    #         'id': order['id'],
    #         'info': order,
    #         'timestamp': timestamp,
    #         'datetime': self.iso8601(timestamp),
    #         'lastTradeTimestamp': None,
    #         'status': status,
    #         'symbol': symbol,
    #         'type': order['type'],
    #         'side': order['side'],
    #         'price': price,
    #         'cost': cost,
    #         'amount': amount,
    #         'filled': filled,
    #         'remaining': remaining,
    #         'fee': fee,
    #     }

    # def fetch_order(self, id, symbol=None, params={}):
    #     self.load_markets()
    #     response = self.privateGetOrdersId(self.extend({
    #         'id': id,
    #     }, params))
    #     return self.parse_order(response)

    # def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
    #     self.load_markets()
    #     request = {
    #         'status': 'all',
    #     }
    #     market = None
    #     if symbol:
    #         market = self.market(symbol)
    #         request['product_id'] = market['id']
    #     response = self.privateGetOrders(self.extend(request, params))
    #     return self.parse_orders(response, market, since, limit)

    # def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
    #     self.load_markets()
    #     request = {}
    #     market = None
    #     if symbol:
    #         market = self.market(symbol)
    #         request['product_id'] = market['id']
    #     response = self.privateGetOrders(self.extend(request, params))
    #     return self.parse_orders(response, market, since, limit)

    # def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
    #     self.load_markets()
    #     request = {
    #         'status': 'done',
    #     }
    #     market = None
    #     if symbol:
    #         market = self.market(symbol)
    #         request['product_id'] = market['id']
    #     response = self.privateGetOrders(self.extend(request, params))
    #     return self.parse_orders(response, market, since, limit)

    # def create_order(self, symbol, type, side, amount, price=None, params={}):
    #     self.load_markets()
    #     # oid = str(self.nonce())
    #     order = {
    #         'product_id': self.market_id(symbol),
    #         'side': side,
    #         'size': amount,
    #         'type': type,
    #     }
    #     if type == 'limit':
    #         order['price'] = price
    #     response = self.privatePostOrders(self.extend(order, params))
    #     return {
    #         'info': response,
    #         'id': response['id'],
    #     }

    # def cancel_order(self, id, symbol=None, params={}):
    #     self.load_markets()
    #     return self.privateDeleteOrdersId({'id': id})

    # def fee_to_precision(self, currency, fee):
    #     cost = float(fee)
    #     return('{:.' + str(self.currencies[currency].precision) + 'f}').format(cost)

    # def calculate_fee(self, symbol, type, side, amount, price, takerOrMaker='taker', params={}):
    #     market = self.markets[symbol]
    #     rate = market[takerOrMaker]
    #     cost = amount * price
    #     currency = market['quote']
    #     return {
    #         'type': takerOrMaker,
    #         'currency': currency,
    #         'rate': rate,
    #         'cost': float(self.fee_to_precision(currency, rate * cost)),
    #     }

    # def get_payment_methods(self):
    #     response = self.privateGetPaymentMethods()
    #     return response

    # def deposit(self, currency, amount, address, params={}):
    #     self.load_markets()
    #     request = {
    #         'currency': currency,
    #         'amount': amount,
    #     }
    #     method = 'privatePostDeposits'
    #     if 'payment_method_id' in params:
    #         # deposit from a payment_method, like a bank account
    #         method += 'PaymentMethod'
    #     elif 'coinbase_account_id' in params:
    #         # deposit into GDAX account from a Coinbase account
    #         method += 'CoinbaseAccount'
    #     else:
    #         # deposit methodotherwise we did not receive a supported deposit location
    #         # relevant docs link for the Googlers
    #         # https://docs.gdax.com/#deposits
    #         raise NotSupported(self.id + ' deposit() requires one of `coinbase_account_id` or `payment_method_id` extra params')
    #     response = getattr(self, method)(self.extend(request, params))
    #     if not response:
    #         raise ExchangeError(self.id + ' deposit() error: ' + self.json(response))
    #     return {
    #         'info': response,
    #         'id': response['id'],
    #     }

    # def withdraw(self, currency, amount, address, tag=None, params={}):
    #     self.check_address(address)
    #     self.load_markets()
    #     request = {
    #         'currency': currency,
    #         'amount': amount,
    #     }
    #     method = 'privatePostWithdrawals'
    #     if 'payment_method_id' in params:
    #         method += 'PaymentMethod'
    #     elif 'coinbase_account_id' in params:
    #         method += 'CoinbaseAccount'
    #     else:
    #         method += 'Crypto'
    #         request['crypto_address'] = address
    #     response = getattr(self, method)(self.extend(request, params))
    #     if not response:
    #         raise ExchangeError(self.id + ' withdraw() error: ' + self.json(response))
    #     return {
    #         'info': response,
    #         'id': response['id'],
    #     }

    # def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
    #     request = '/' + self.implode_params(path, params)
    #     query = self.omit(params, self.extract_params(path))
    #     if method == 'GET':
    #         if query:
    #             request += '?' + self.urlencode(query)
    #     url = self.urls['api'] + request
    #     if api == 'private':
    #         self.check_required_credentials()
    #         nonce = str(self.nonce())
    #         payload = ''
    #         if method != 'GET':
    #             if query:
    #                 body = self.json(query)
    #                 payload = body
    #         # payload = body if (body) else ''
    #         what = nonce + method + request + payload
    #         secret = base64.b64decode(self.secret)
    #         signature = self.hmac(self.encode(what), secret, hashlib.sha256, 'base64')
    #         headers = {
    #             'CB-ACCESS-KEY': self.apiKey,
    #             'CB-ACCESS-SIGN': self.decode(signature),
    #             'CB-ACCESS-TIMESTAMP': nonce,
    #             'CB-ACCESS-PASSPHRASE': self.password,
    #             'Content-Type': 'application/json',
    #         }
    #     return {'url': url, 'method': method, 'body': body, 'headers': headers}

    # def handle_errors(self, code, reason, url, method, headers, body):
    #     if (code == 400) or (code == 404):
    #         if body[0] == '{':
    #             response = json.loads(body)
    #             message = response['message']
    #             error = self.id + ' ' + message
    #             if message.find('price too small') >= 0:
    #                 raise InvalidOrder(error)
    #             elif message.find('price too precise') >= 0:
    #                 raise InvalidOrder(error)
    #             elif message == 'Insufficient funds':
    #                 raise InsufficientFunds(error)
    #             elif message == 'NotFound':
    #                 raise OrderNotFound(error)
    #             elif message == 'Invalid API Key':
    #                 raise AuthenticationError(error)
    #             raise ExchangeError(self.id + ' ' + message)
    #         raise ExchangeError(self.id + ' ' + body)

    # def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
    #     response = self.fetch2(path, api, method, params, headers, body)
    #     if 'message' in response:
    #         raise ExchangeError(self.id + ' ' + self.json(response))
    #     return response