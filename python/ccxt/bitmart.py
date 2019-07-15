# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
import hashlib
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import ArgumentsRequired


class bitmart (Exchange):

    def describe(self):
        return self.deep_extend(super(bitmart, self).describe(), {
            'id': 'bitmart',
            'name': 'Bitmart',
            'countries': ['US', 'CN', 'HK', 'KR'],
            'rateLimit': 1000,
            'version': 'v2',
            'has': {
                'CORS': True,
                'fetchMarkets': True,
                'fetchTicker': True,
                'fetchTickers': 'emulated',
                'fetchCurrencies': True,
                'fetchOrderBook': True,
                'fetchTrades': True,
                'fetchMyTrades': True,
                'fetchOHLCV': True,
                'fetchBalance': True,
                'createOrder': True,
                'cancelOrder': True,
                'fetchOrders': False,
                'fetchOpenOrders': 'emulated',
                'fetchClosedOrders': 'emulated',
                'fetchOrder': True,
            },
            'urls': {
                'logo': 'https://www.bitmart.com/_nuxt/img/ed5c199.png',
                'api': 'https://openapi.bitmart.com',
                'www': 'https://www.bitmart.com/',
                'doc': 'https://github.com/bitmartexchange/bitmart-official-api-docs/blob/master/REST.md',
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': True,
                'uid': True,
            },
            'api': {
                'token': {
                    'post': [
                        'authentication',
                    ],
                },
                'public': {
                    'get': [
                        'currencies',
                        'ping',
                        'steps',
                        'symbols',
                        'symbols_details',
                        'symbols/{symbol}/kline',
                        'symbols/{symbol}/orders',
                        'symbols/{symbol}/trades',
                        'ticker',
                        'time',
                    ],
                },
                'private': {
                    'get': [
                        'orders',
                        'orders/{id}',
                        'trades',
                        'wallet',
                    ],
                    'post': [
                        'orders',
                    ],
                    'delete': [
                        'orders',
                        'orders/{id}',
                    ],
                },
            },
            'timeframes': {
                '1m': 1,
                '3m': 3,
                '5m': 5,
                '15m': 15,
                '30m': 30,
                '45m': 45,
                '1h': 60,
                '2h': 120,
                '3h': 180,
                '4h': 240,
                '1d': 1440,
                '1w': 10080,
                '1M': 43200,
            },
            'fees': {
                'trading': {
                    'tierBased': True,
                    'percentage': True,
                    'taker': 0.001,
                    'maker': 0.001,
                    'tiers': {
                        'taker': [
                            [0, 0.20 / 100],
                            [10, 0.18 / 100],
                            [50, 0.16 / 100],
                            [250, 0.14 / 100],
                            [1000, 0.12 / 100],
                            [5000, 0.10 / 100],
                            [25000, 0.08 / 100],
                            [50000, 0.06 / 100],
                        ],
                        'maker': [
                            [0, 0.1 / 100],
                            [10, 0.09 / 100],
                            [50, 0.08 / 100],
                            [250, 0.07 / 100],
                            [1000, 0.06 / 100],
                            [5000, 0.05 / 100],
                            [25000, 0.04 / 100],
                            [50000, 0.03 / 100],
                        ],
                    },
                },
            },
        })

    def sign_in(self, params={}):
        message = self.apiKey + ':' + self.secret + ':' + self.uid
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.apiKey,
            'client_secret': self.hmac(self.encode(message), self.encode(self.secret), hashlib.sha256),
        }
        response = self.tokenPostAuthentication(self.extend(data, params))
        accessToken = self.safe_string(response, 'access_token')
        if not accessToken:
            raise AuthenticationError(self.id + ' signIn() failed to authenticate. Access token missing from response.')
        expiresIn = self.safe_integer(response, 'expires_in')
        self.options['expires'] = self.sum(self.nonce(), expiresIn * 1000)
        self.options['accessToken'] = accessToken
        return response

    def fetch_markets(self, params={}):
        markets = self.publicGetSymbolsDetails()
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            id = market['id']
            base = market['base_currency']
            quote = market['quote_currency']
            symbol = base + '/' + quote
            precision = {
                'amount': 8,
                'price': market['price_max_precision'],
            }
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'precision': precision,
                'info': market,
            })
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = ticker['symbol_id']
        last = self.safe_float(ticker, 'current_price')
        percentage = self.safe_float(ticker, 'fluctuation')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'highest_price'),
            'low': self.safe_float(ticker, 'lowest_price'),
            'bid': self.safe_float(ticker, 'bid_1'),
            'bidVolume': self.safe_float(ticker, 'bid_1_amount'),
            'ask': self.safe_float(ticker, 'ask_1'),
            'askVolume': self.safe_float(ticker, 'ask_1_amount'),
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': percentage * 100,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'base_volume'),
            'quoteVolume': self.safe_float(ticker, 'volume'),
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        ticker = self.publicGetTicker(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        return self.parse_ticker(ticker)

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTicker(params)
        result = {}
        for i in range(0, len(tickers)):
            ticker = self.parse_ticker(tickers[i])
            symbol = ticker['symbol']
            result[symbol] = ticker
        return result

    def fetch_currencies(self, params={}):
        currencies = self.publicGetCurrencies(params)
        result = {}
        for i in range(0, len(currencies)):
            currency = currencies[i]
            id = currency['id']
            result[id] = {
                'id': id,
                'code': id,
                'name': currency['name'],
                'info': currency,  # the original payload
                'active': True,
            }
        return result

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        #
        # order query parameters:
        #    precision : price precision whose range is defined in symbol details : [optional]
        #
        response = self.publicGetSymbolsSymbolOrders(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        return self.parse_order_book(response, None, 'buys', 'sells', 'price', 'amount')

    def parse_trade(self, trade, market):
        timestamp = self.safe_integer(trade, 'timestamp')
        if timestamp is None:
            timestamp = self.safe_integer(trade, 'order_time')
        side = self.safe_string(trade, 'type')
        if side is not None:
            side = side.lower()
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'amount')
        return {
            'info': trade,
            'id': self.safe_string(trade, 'trade_id'),
            'order': self.safe_integer(trade, 'entrust_id'),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': 'limit',
            'side': side,
            'price': price,
            'amount': amount,
            'takerOrMaker': None,
            'cost': price * amount,
            'fee': None,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetSymbolsSymbolTrades(self.extend({
            'symbol': self.market_id(symbol),
        }, params))
        return self.parse_trades(response, market, since, limit)

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchMyTrades requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': self.market_id(symbol),
        }
        if limit is None:
            limit = 500
        request['limit'] = limit
        if self.safe_integer(params, 'offset') is None:
            request['offset'] = 0
        response = self.privateGetTrades(self.extend(request, params))
        trades = self.safe_value(response, 'trades')
        return self.parse_trades(trades, market, since, limit)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            self.safe_integer(ohlcv, 'timestamp'),
            self.safe_float(ohlcv, 'open_price'),
            self.safe_float(ohlcv, 'highest_price'),
            self.safe_float(ohlcv, 'lowest_price'),
            self.safe_float(ohlcv, 'current_price'),
            self.safe_float(ohlcv, 'volume'),
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        #
        # ohlcv query parameters:
        #    from : start time of k-line data(in milliseconds) : [required]
        #    to : end time of k-line data(in milliseconds) : [required]
        #    step : steps of sampling(in minutes, default 1 minute) : [optional]
        #
        if limit is None:
            limit = 1
        # convert timeframe minutes to milliseconds
        step = (self.timeframes[timeframe] * 60 * 1000)
        to = self.milliseconds()
        if since is None:
            since = to - (step * limit)
        else:
            to = self.sum(since, step * limit)
        request = {
            'symbol': self.market_id(symbol),
            'to': to,
            'from': since,
            'step': self.timeframes[timeframe],
        }
        response = self.publicGetSymbolsSymbolKline(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privateGetWallet(params)
        result = {'info': balances}
        for i in range(0, len(balances)):
            balance = balances[i]
            id = self.safe_string(balance, 'id')
            if id in self.currencies_by_id:
                id = self.currencies_by_id[id]['code']
            free = self.safe_float(balance, 'available')
            used = self.safe_float(balance, 'frozen')
            result[id] = {
                'free': free,
                'used': used,
                'total': self.sum(free, used),
            }
        return self.parse_balance(result)

    def parse_order(self, order, market=None):
        timestamp = self.milliseconds()
        status = self.parse_order_status(self.safe_string(order, 'status'))
        symbol = self.find_symbol(self.safe_string(order, 'symbol'), market)
        info = self.safe_value(order, 'info')
        if info is None:
            info = self.extend({}, order)
        order = self.map_order_response(order, market)
        return {
            'id': self.safe_integer(order, 'id'),
            'info': info,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'symbol': symbol,
            'type': 'limit',
            'side': self.safe_string(order, 'side'),
            'price': self.safe_float(order, 'price'),
            'amount': self.safe_float(order, 'amount'),
            'cost': None,
            'average': None,
            'filled': self.safe_float(order, 'executed_amount'),
            'remaining': self.safe_float(order, 'remaining_amount'),
            'status': status,
            'fee': None,
            'trades': None,
        }

    def map_order_response(self, order, market=None):
        originalAmount = self.safe_float(order, 'original_amount')
        if originalAmount is not None:
            order['amount'] = originalAmount
        entrustId = self.safe_integer(order, 'entrust_id')
        if entrustId is not None:
            order['id'] = entrustId
        return order

    def parse_order_status(self, status):
        statuses = {
            '0': 'all',
            '1': 'open',
            '2': 'open',
            '3': 'closed',
            '4': 'canceled',
            '5': 'open',
            '6': 'closed',
        }
        return statuses[status] if (status in list(statuses.keys())) else status

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        order = {
            'symbol': self.market_id(symbol),
            'side': side.lower(),
            'amount': self.amount_to_precision(symbol, amount),
            'price': self.price_to_precision(symbol, price),
        }
        response = self.privatePostOrders(self.extend(order, params))
        order = self.extend({
            'status': 'open',
            'info': response,
        }, order)
        return self.parse_order(self.extend(order, response), market)

    def cancel_order(self, id, symbol=None, params={}):
        if symbol is None:
            raise ArgumentsRequired(self.id + ' cancelOrder requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        response = self.privateDeleteOrdersId(self.extend({
            'id': id,
            'entrust_id': id,
        }, params))
        return self.parse_order(self.extend({
            'symbol': self.market_id(symbol),
            'status': 'canceled',
            'entrust_id': id,
            'info': response,
        }, response), market)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchOpenOrders requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': self.market_id(symbol),
        }
        if limit is None:
            limit = 500
        request['limit'] = limit
        if self.safe_integer(params, 'offset') is None:
            request['offset'] = 0
        # pending & partially filled orders
        request['status'] = 5
        response = self.privateGetOrders(self.extend(request, params))
        orders = self.safe_value(response, 'orders')
        return self.parse_orders(orders, market, since, limit)

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchClosedOrders requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': self.market_id(symbol),
        }
        if limit is None:
            limit = 500
        request['limit'] = limit
        if self.safe_integer(params, 'offset') is None:
            request['offset'] = 0
        # successful and canceled orders
        request['status'] = 6
        response = self.privateGetOrders(self.extend(request, params))
        orders = self.safe_value(response, 'orders')
        return self.parse_orders(orders, market, since, limit)

    def fetch_order(self, id, symbol=None, params={}):
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchOrder requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        response = self.privateGetOrdersId(self.extend({
            'id': id,
        }, params))
        return self.parse_order(response, market)

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        elif api == 'token':
            self.check_required_credentials()
            body = self.urlencode(query)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        else:
            self.check_required_credentials()
            token = self.safe_string(self.options, 'accessToken')
            if token is None:
                raise AuthenticationError(self.id + ' ' + path + ' endpoint requires an accessToken option or a prior call to signIn() method')
            expires = self.safe_integer(self.options, 'expires')
            if expires is not None:
                if self.nonce() >= expires:
                    raise AuthenticationError(self.id + ' accessToken expired, supply a new accessToken or call to signIn() method')
            if query:
                url += '?' + self.urlencode(query)
            headers = {
                'Content-Type': 'application/json',
                'X-BM-TIMESTAMP': self.nonce(),
                'X-BM-AUTHORIZATION': 'Bearer ' + token,
            }
            if method != 'GET':
                query = self.keysort(query)
                body = self.json(query)
                message = self.urlencode(query)
                headers['X-BM-SIGNATURE'] = self.hmac(self.encode(message), self.encode(self.secret), hashlib.sha256)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
