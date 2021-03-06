# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
import hashlib
from ccxt.base.errors import ExchangeError


class fybse (Exchange):

    def describe(self):
        return self.deep_extend(super(fybse, self).describe(), {
            'id': 'fybse',
            'name': 'FYB-SE',
            'countries': ['SE'],  # Sweden
            'has': {
                'CORS': False,
            },
            'rateLimit': 1500,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766512-31019772-5edb-11e7-8241-2e675e6797f1.jpg',
                'api': 'https://www.fybse.se/api/SEK',
                'www': 'https://www.fybse.se',
                'doc': 'https://fyb.docs.apiary.io',
            },
            'api': {
                'public': {
                    'get': [
                        'ticker',
                        'tickerdetailed',
                        'orderbook',
                        'trades',
                    ],
                },
                'private': {
                    'post': [
                        'test',
                        'getaccinfo',
                        'getpendingorders',
                        'getorderhistory',
                        'cancelpendingorder',
                        'placeorder',
                        'withdraw',
                    ],
                },
            },
            'markets': {
                'BTC/SEK': {'id': 'SEK', 'symbol': 'BTC/SEK', 'base': 'BTC', 'quote': 'SEK'},
            },
        })

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privatePostGetaccinfo(params)
        btc = self.safe_float(response, 'btcBal')
        symbol = self.symbols[0]
        quote = self.markets[symbol]['quote']
        lowercase = quote.lower() + 'Bal'
        fiat = self.safe_float(response, lowercase)
        crypto = {
            'free': btc,
            'used': 0.0,
            'total': btc,
        }
        result = {'BTC': crypto}
        result[quote] = {
            'free': fiat,
            'used': 0.0,
            'total': fiat,
        }
        result['info'] = response
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        response = await self.publicGetOrderbook(params)
        return self.parse_order_book(response)

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        ticker = await self.publicGetTickerdetailed(params)
        timestamp = self.milliseconds()
        last = self.safe_float(ticker, 'last')
        volume = self.safe_float(ticker, 'vol')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': self.safe_float(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': volume,
            'quoteVolume': None,
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        timestamp = self.safe_integer(trade, 'date')
        if timestamp is not None:
            timestamp *= 1000
        id = self.safe_string(trade, 'tid')
        symbol = None
        if market is not None:
            symbol = market['symbol']
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'amount')
        cost = None
        if price is not None:
            if amount is not None:
                cost = price * amount
        return {
            'id': id,
            'info': trade,
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': None,
            'side': None,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': None,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetTrades(params)
        return self.parse_trades(response, market, since, limit)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        request = {
            'qty': amount,
            'price': price,
            'type': side[0].upper(),
        }
        response = await self.privatePostPlaceorder(self.extend(request, params))
        return {
            'info': response,
            'id': response['pending_oid'],
        }

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        request = {
            'orderNo': id,
        }
        return await self.privatePostCancelpendingorder(self.extend(request, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + path
        if api == 'public':
            url += '.json'
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            body = self.urlencode(self.extend({'timestamp': nonce}, params))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'key': self.apiKey,
                'sig': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha1),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    async def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = await self.fetch2(path, api, method, params, headers, body)
        if api == 'private':
            if 'error' in response:
                if response['error']:
                    raise ExchangeError(self.id + ' ' + self.json(response))
        return response
