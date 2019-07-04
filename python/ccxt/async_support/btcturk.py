# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
import base64
import hashlib
import math
from ccxt.base.errors import ExchangeError


class btcturk (Exchange):

    def describe(self):
        return self.deep_extend(super(btcturk, self).describe(), {
            'id': 'btcturk',
            'name': 'BTCTurk',
            'countries': ['TR'],  # Turkey
            'rateLimit': 1000,
            'has': {
                'CORS': True,
                'fetchTickers': True,
                'fetchOHLCV': True,
            },
            'timeframes': {
                '1d': '1d',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27992709-18e15646-64a3-11e7-9fa2-b0950ec7712f.jpg',
                'api': 'https://www.btcturk.com/api',
                'www': 'https://www.btcturk.com',
                'doc': 'https://github.com/BTCTrader/broker-api-docs',
            },
            'api': {
                'public': {
                    'get': [
                        'ohlcdata',  # ?last=COUNT
                        'orderbook',
                        'ticker',
                        'trades',   # ?last=COUNT(max 50)
                    ],
                },
                'private': {
                    'get': [
                        'balance',
                        'openOrders',
                        'userTransactions',  # ?offset=0&limit=25&sort=asc
                    ],
                    'post': [
                        'exchange',
                        'cancelOrder',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.002 * 1.18,
                    'taker': 0.0035 * 1.18,
                },
            },
        })

    async def fetch_markets(self, params={}):
        response = await self.publicGetTicker(params)
        result = []
        for i in range(0, len(response)):
            market = response[i]
            id = self.safe_string(market, 'pair')
            baseId = id[0:3]
            quoteId = id[3:6]
            base = self.safeCurrencyCode(baseId)
            quote = self.safeCurrencyCode(quoteId)
            baseId = baseId.lower()
            quoteId = quoteId.lower()
            symbol = base + '/' + quote
            precision = {
                'amount': 8,
                'price': 8,
            }
            active = True
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': active,
                'info': market,
                'precision': precision,
                'limits': {
                    'amount': {
                        'min': math.pow(10, -precision['amount']),
                        'max': None,
                    },
                    'price': {
                        'min': math.pow(10, -precision['price']),
                        'max': None,
                    },
                    'cost': {
                        'min': None,
                        'max': None,
                    },
                },
            })
        return result

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privateGetBalance(params)
        result = {'info': response}
        codes = list(self.currencies.keys())
        for i in range(0, len(codes)):
            code = codes[i]
            currency = self.currencies[code]
            free = currency['id'] + '_available'
            total = currency['id'] + '_balance'
            used = currency['id'] + '_reserved'
            if free in response:
                account = self.account()
                account['free'] = self.safe_float(response, free)
                account['total'] = self.safe_float(response, total)
                account['used'] = self.safe_float(response, used)
                result[code] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'pairSymbol': market['id'],
        }
        response = await self.publicGetOrderbook(self.extend(request, params))
        timestamp = self.safe_integer(response, 'timestamp')
        if timestamp is not None:
            timestamp *= 1000
        return self.parse_order_book(response, timestamp)

    def parse_ticker(self, ticker, market=None):
        symbol = None
        if market:
            symbol = market['symbol']
        timestamp = self.safe_integer(ticker, 'timestamp')
        if timestamp is not None:
            timestamp *= 1000
        last = self.safe_float(ticker, 'last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask'),
            'askVolume': None,
            'vwap': None,
            'open': self.safe_float(ticker, 'open'),
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': self.safe_float(ticker, 'average'),
            'baseVolume': self.safe_float(ticker, 'volume'),
            'quoteVolume': None,
            'info': ticker,
        }

    async def fetch_tickers(self, symbols=None, params={}):
        await self.load_markets()
        tickers = await self.publicGetTicker(params)
        result = {}
        for i in range(0, len(tickers)):
            ticker = tickers[i]
            marketId = self.safe_string(ticker, 'pair')
            symbol = marketId
            market = None
            if marketId in self.markets_by_id:
                market = self.markets_by_id[symbol]
                symbol = market['symbol']
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        tickers = await self.fetch_tickers(params)
        return self.safe_value_2(tickers, market['id'], symbol)

    def parse_trade(self, trade, market=None):
        timestamp = self.safe_integer(trade, 'date')
        if timestamp is not None:
            timestamp *= 1000
        id = self.safe_string(trade, 'tid')
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'amount')
        cost = None
        if amount is not None:
            if price is not None:
                cost = amount * price
        symbol = None
        if market is not None:
            symbol = market['symbol']
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': None,
            'side': None,
            'order': None,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': None,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        # maxCount = 50
        request = {
            'pairSymbol': market['id'],
        }
        response = await self.publicGetTrades(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1d', since=None, limit=None):
        timestamp = self.parse8601(self.safe_string(ohlcv, 'Time'))
        return [
            timestamp,
            self.safe_float(ohlcv, 'Open'),
            self.safe_float(ohlcv, 'High'),
            self.safe_float(ohlcv, 'Low'),
            self.safe_float(ohlcv, 'Close'),
            self.safe_float(ohlcv, 'Volume'),
        ]

    async def fetch_ohlcv(self, symbol, timeframe='1d', since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {}
        if limit is not None:
            request['last'] = limit
        response = await self.publicGetOhlcdata(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        request = {
            'PairSymbol': self.market_id(symbol),
            'OrderType': 0 if (side == 'buy') else 1,
            'OrderMethod': 1 if (type == 'market') else 0,
        }
        if type == 'market':
            if not('Total' in list(params.keys())):
                raise ExchangeError(self.id + ' createOrder requires the "Total" extra parameter for market orders(amount and price are both ignored)')
        else:
            request['Price'] = price
            request['Amount'] = amount
        response = await self.privatePostExchange(self.extend(request, params))
        id = self.safe_string(response, 'id')
        return {
            'info': response,
            'id': id,
        }

    async def cancel_order(self, id, symbol=None, params={}):
        request = {
            'id': id,
        }
        return await self.privatePostCancelOrder(self.extend(request, params))

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        if self.id == 'btctrader':
            raise ExchangeError(self.id + ' is an abstract base API for BTCExchange, BTCTurk')
        url = self.urls['api'] + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            self.check_required_credentials()
            nonce = str(self.nonce())
            body = self.urlencode(params)
            secret = base64.b64decode(self.secret)
            auth = self.apiKey + nonce
            headers = {
                'X-PCK': self.apiKey,
                'X-Stamp': nonce,
                'X-Signature': base64.b64encode(self.hmac(self.encode(auth), secret, hashlib.sha256, 'binary')),
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
