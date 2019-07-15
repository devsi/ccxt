<?php

namespace ccxt;

// PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
// https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

use Exception as Exception; // a common import

class bitmart extends Exchange {

    public function describe () {
        return array_replace_recursive (parent::describe (), array (
            'id' => 'bitmart',
            'name' => 'Bitmart',
            'countries' => array ( 'US', 'CN', 'HK', 'KR' ),
            'rateLimit' => 1000,
            'version' => 'v2',
            'has' => array (
                'CORS' => true,
                'fetchMarkets' => true,
                'fetchTicker' => true,
                'fetchTickers' => 'emulated',
                'fetchCurrencies' => true,
                'fetchOrderBook' => true,
                'fetchTrades' => true,
                'fetchMyTrades' => true,
                'fetchOHLCV' => true,
                'fetchBalance' => true,
                'createOrder' => true,
                'cancelOrder' => true,
                'fetchOrders' => false,
                'fetchOpenOrders' => 'emulated',
                'fetchClosedOrders' => 'emulated',
                'fetchOrder' => true,
            ),
            'urls' => array (
                'logo' => 'https://www.bitmart.com/_nuxt/img/ed5c199.png',
                'api' => 'https://openapi.bitmart.com',
                'www' => 'https://www.bitmart.com/',
                'doc' => 'https://github.com/bitmartexchange/bitmart-official-api-docs/blob/master/REST.md',
            ),
            'requiredCredentials' => array (
                'apiKey' => true,
                'secret' => true,
                'uid' => true,
            ),
            'api' => array (
                'token' => array (
                    'post' => array (
                        'authentication',
                    ),
                ),
                'public' => array (
                    'get' => array (
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
                    ),
                ),
                'private' => array (
                    'get' => array (
                        'orders',
                        'orders/{id}',
                        'trades',
                        'wallet',
                    ),
                    'post' => array (
                        'orders',
                    ),
                    'delete' => array (
                        'orders',
                        'orders/{id}',
                    ),
                ),
            ),
            'timeframes' => array (
                '1m' => 1,
                '3m' => 3,
                '5m' => 5,
                '15m' => 15,
                '30m' => 30,
                '45m' => 45,
                '1h' => 60,
                '2h' => 120,
                '3h' => 180,
                '4h' => 240,
                '1d' => 1440,
                '1w' => 10080,
                '1M' => 43200,
            ),
            'fees' => array (
                'trading' => array (
                    'tierBased' => true,
                    'percentage' => true,
                    'taker' => 0.001,
                    'maker' => 0.001,
                    'tiers' => array (
                        'taker' => [
                            [0, 0.20 / 100],
                            [10, 0.18 / 100],
                            [50, 0.16 / 100],
                            [250, 0.14 / 100],
                            [1000, 0.12 / 100],
                            [5000, 0.10 / 100],
                            [25000, 0.08 / 100],
                            [50000, 0.06 / 100],
                        ],
                        'maker' => [
                            [0, 0.1 / 100],
                            [10, 0.09 / 100],
                            [50, 0.08 / 100],
                            [250, 0.07 / 100],
                            [1000, 0.06 / 100],
                            [5000, 0.05 / 100],
                            [25000, 0.04 / 100],
                            [50000, 0.03 / 100],
                        ],
                    ),
                ),
            ),
        ));
    }

    public function sign_in ($params = array ()) {
        $message = $this->apiKey . ':' . $this->secret . ':' . $this->uid;
        $data = array (
            'grant_type' => 'client_credentials',
            'client_id' => $this->apiKey,
            'client_secret' => $this->hmac ($this->encode ($message), $this->encode ($this->secret), 'sha256'),
        );
        $response = $this->tokenPostAuthentication (array_merge ($data, $params));
        $accessToken = $this->safe_string($response, 'access_token');
        if (!$accessToken) {
            throw new AuthenticationError($this->id . ' signIn() failed to authenticate. Access token missing from $response->');
        }
        $expiresIn = $this->safe_integer($response, 'expires_in');
        $this->options['expires'] = $this->sum ($this->nonce (), $expiresIn * 1000);
        $this->options['accessToken'] = $accessToken;
        return $response;
    }

    public function fetch_markets ($params = array ()) {
        $markets = $this->publicGetSymbolsDetails ();
        $result = array();
        for ($i = 0; $i < count ($markets); $i++) {
            $market = $markets[$i];
            $id = $market['id'];
            $base = $market['base_currency'];
            $quote = $market['quote_currency'];
            $symbol = $base . '/' . $quote;
            $precision = array (
                'amount' => 8,
                'price' => $market['price_max_precision'],
            );
            $result[] = array (
                'id' => $id,
                'symbol' => $symbol,
                'base' => $base,
                'quote' => $quote,
                'precision' => $precision,
                'info' => $market,
            );
        }
        return $result;
    }

    public function parse_ticker ($ticker, $market = null) {
        $timestamp = $this->milliseconds ();
        $symbol = $ticker['symbol_id'];
        $last = $this->safe_float($ticker, 'current_price');
        $percentage = $this->safe_float($ticker, 'fluctuation');
        return array (
            'symbol' => $symbol,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601 ($timestamp),
            'high' => $this->safe_float($ticker, 'highest_price'),
            'low' => $this->safe_float($ticker, 'lowest_price'),
            'bid' => $this->safe_float($ticker, 'bid_1'),
            'bidVolume' => $this->safe_float($ticker, 'bid_1_amount'),
            'ask' => $this->safe_float($ticker, 'ask_1'),
            'askVolume' => $this->safe_float($ticker, 'ask_1_amount'),
            'vwap' => null,
            'open' => null,
            'close' => $last,
            'last' => $last,
            'previousClose' => null,
            'change' => null,
            'percentage' => $percentage * 100,
            'average' => null,
            'baseVolume' => $this->safe_float($ticker, 'base_volume'),
            'quoteVolume' => $this->safe_float($ticker, 'volume'),
            'info' => $ticker,
        );
    }

    public function fetch_ticker ($symbol, $params = array ()) {
        $this->load_markets();
        $ticker = $this->publicGetTicker (array_merge (array (
            'symbol' => $this->market_id($symbol),
        ), $params));
        return $this->parse_ticker($ticker);
    }

    public function fetch_tickers ($symbols = null, $params = array ()) {
        $this->load_markets();
        $tickers = $this->publicGetTicker ($params);
        $result = array();
        for ($i = 0; $i < count ($tickers); $i++) {
            $ticker = $this->parse_ticker($tickers[$i]);
            $symbol = $ticker['symbol'];
            $result[$symbol] = $ticker;
        }
        return $result;
    }

    public function fetch_currencies ($params = array ()) {
        $currencies = $this->publicGetCurrencies ($params);
        $result = array();
        for ($i = 0; $i < count ($currencies); $i++) {
            $currency = $currencies[$i];
            $id = $currency['id'];
            $result[$id] = array (
                'id' => $id,
                'code' => $id,
                'name' => $currency['name'],
                'info' => $currency, // the original payload
                'active' => true,
            );
        }
        return $result;
    }

    public function fetch_order_book ($symbol, $limit = null, $params = array ()) {
        $this->load_markets();
        //
        // order query parameters:
        //    precision : price precision whose range is defined in $symbol details : [optional]
        //
        $response = $this->publicGetSymbolsSymbolOrders (array_merge (array (
            'symbol' => $this->market_id($symbol),
        ), $params));
        return $this->parse_order_book($response, null, 'buys', 'sells', 'price', 'amount');
    }

    public function parse_trade ($trade, $market) {
        $timestamp = $this->safe_integer($trade, 'timestamp');
        if ($timestamp === null) {
            $timestamp = $this->safe_integer($trade, 'order_time');
        }
        $side = $this->safe_string($trade, 'type');
        if ($side !== null) {
            $side = strtolower($side);
        }
        $price = $this->safe_float($trade, 'price');
        $amount = $this->safe_float($trade, 'amount');
        return array (
            'info' => $trade,
            'id' => $this->safe_string($trade, 'trade_id'),
            'order' => $this->safe_integer($trade, 'entrust_id'),
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601 ($timestamp),
            'symbol' => $market['symbol'],
            'type' => 'limit',
            'side' => $side,
            'price' => $price,
            'amount' => $amount,
            'takerOrMaker' => null,
            'cost' => $price * $amount,
            'fee' => null,
        );
    }

    public function fetch_trades ($symbol, $since = null, $limit = null, $params = array ()) {
        $this->load_markets();
        $market = $this->market ($symbol);
        $response = $this->publicGetSymbolsSymbolTrades (array_merge (array (
            'symbol' => $this->market_id($symbol),
        ), $params));
        return $this->parse_trades($response, $market, $since, $limit);
    }

    public function fetch_my_trades ($symbol = null, $since = null, $limit = null, $params = array ()) {
        if ($symbol === null) {
            throw new ArgumentsRequired($this->id . ' fetchMyTrades requires a $symbol argument');
        }
        $this->load_markets();
        $market = $this->market ($symbol);
        $request = array (
            'symbol' => $this->market_id($symbol),
        );
        if ($limit === null) {
            $limit = 500;
        }
        $request['limit'] = $limit;
        if ($this->safe_integer($params, 'offset') === null) {
            $request['offset'] = 0;
        }
        $response = $this->privateGetTrades (array_merge ($request, $params));
        $trades = $this->safe_value($response, 'trades');
        return $this->parse_trades($trades, $market, $since, $limit);
    }

    public function parse_ohlcv ($ohlcv, $market = null, $timeframe = '1m', $since = null, $limit = null) {
        return array (
            $this->safe_integer($ohlcv, 'timestamp'),
            $this->safe_float($ohlcv, 'open_price'),
            $this->safe_float($ohlcv, 'highest_price'),
            $this->safe_float($ohlcv, 'lowest_price'),
            $this->safe_float($ohlcv, 'current_price'),
            $this->safe_float($ohlcv, 'volume'),
        );
    }

    public function fetch_ohlcv ($symbol, $timeframe = '1m', $since = null, $limit = null, $params = array ()) {
        $this->load_markets();
        $market = $this->market ($symbol);
        //
        // ohlcv query parameters:
        //    from : start time of k-line data (in milliseconds) : [required]
        //    $to : end time of k-line data (in milliseconds) : [required]
        //    $step : steps of sampling (in minutes, default 1 minute) : [optional]
        //
        if ($limit === null) {
            $limit = 1;
        }
        // convert $timeframe minutes $to milliseconds
        $step = ($this->timeframes[$timeframe] * 60 * 1000);
        $to = $this->milliseconds ();
        if ($since === null) {
            $since = $to - ($step * $limit);
        } else {
            $to = $this->sum ($since, $step * $limit);
        }
        $request = array (
            'symbol' => $this->market_id($symbol),
            'to' => $to,
            'from' => $since,
            'step' => $this->timeframes[$timeframe],
        );
        $response = $this->publicGetSymbolsSymbolKline (array_merge ($request, $params));
        return $this->parse_ohlcvs($response, $market, $timeframe, $since, $limit);
    }

    public function fetch_balance ($params = array ()) {
        $this->load_markets();
        $balances = $this->privateGetWallet ($params);
        $result = array( 'info' => $balances );
        for ($i = 0; $i < count ($balances); $i++) {
            $balance = $balances[$i];
            $id = $this->safe_string($balance, 'id');
            if (is_array($this->currencies_by_id) && array_key_exists($id, $this->currencies_by_id)) {
                $id = $this->currencies_by_id[$id]['code'];
            }
            $free = $this->safe_float($balance, 'available');
            $used = $this->safe_float($balance, 'frozen');
            $result[$id] = array (
                'free' => $free,
                'used' => $used,
                'total' => $this->sum ($free, $used),
            );
        }
        return $this->parse_balance($result);
    }

    public function parse_order ($order, $market = null) {
        $timestamp = $this->milliseconds ();
        $status = $this->parse_order_status($this->safe_string($order, 'status'));
        $symbol = $this->find_symbol($this->safe_string($order, 'symbol'), $market);
        $info = $order['info'];
        if ($info === null) {
            $info = array_merge (array(), $order);
        }
        $order = $this->map_order_response ($order, $market);
        return array (
            'id' => $this->safe_integer($order, 'id'),
            'info' => $info,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601 ($timestamp),
            'lastTradeTimestamp' => null,
            'symbol' => $symbol,
            'type' => 'limit',
            'side' => $this->safe_string($order, 'side'),
            'price' => $this->safe_float($order, 'price'),
            'amount' => $this->safe_float($order, 'amount'),
            'cost' => null,
            'average' => null,
            'filled' => $this->safe_float($order, 'executed_amount'),
            'remaining' => $this->safe_float($order, 'remaining_amount'),
            'status' => $status,
            'fee' => null,
            'trades' => null,
        );
    }

    public function map_order_response ($order, $market = null) {
        $originalAmount = $this->safe_float($order, 'original_amount');
        if ($originalAmount !== null) {
            $order['amount'] = $originalAmount;
        }
        $entrustId = $this->safe_integer($order, 'entrust_id');
        if ($entrustId !== null) {
            $order['id'] = $entrustId;
        }
        return $order;
    }

    public function parse_order_status ($status) {
        $statuses = array (
            '0' => 'all',
            '1' => 'open',
            '2' => 'open',
            '3' => 'closed',
            '4' => 'canceled',
            '5' => 'open',
            '6' => 'closed',
        );
        return (is_array($statuses) && array_key_exists($status, $statuses)) ? $statuses[$status] : $status;
    }

    public function create_order ($symbol, $type, $side, $amount, $price = null, $params = array ()) {
        $this->load_markets();
        $market = $this->market ($symbol);
        $order = array (
            'symbol' => $this->market_id($symbol),
            'side' => strtolower($side),
            'amount' => $this->amount_to_precision($symbol, $amount),
            'price' => $this->price_to_precision($symbol, $price),
        );
        $response = $this->privatePostOrders (array_merge ($order, $params));
        $order = array_merge (array (
            'status' => 'open',
            'info' => $response,
        ), $order);
        return $this->parse_order(array_merge ($order, $response), $market);
    }

    public function cancel_order ($id, $symbol = null, $params = array ()) {
        if ($symbol === null) {
            throw new ArgumentsRequired($this->id . ' cancelOrder requires a $symbol argument');
        }
        $this->load_markets();
        $market = $this->market ($symbol);
        $response = $this->privateDeleteOrdersId (array_merge (array (
            'id' => $id,
            'entrust_id' => $id,
        ), $params));
        return $this->parse_order(array_merge (array (
            'symbol' => $this->market_id($symbol),
            'status' => 'canceled',
            'entrust_id' => $id,
            'info' => $response,
        ), $response), $market);
    }

    public function fetch_open_orders ($symbol = null, $since = null, $limit = null, $params = array ()) {
        if ($symbol === null) {
            throw new ArgumentsRequired($this->id . ' fetchOpenOrders requires a $symbol argument');
        }
        $this->load_markets();
        $market = $this->market ($symbol);
        $request = array (
            'symbol' => $this->market_id($symbol),
        );
        if ($limit === null) {
            $limit = 500;
        }
        $request['limit'] = $limit;
        if ($this->safe_integer($params, 'offset') === null) {
            $request['offset'] = 0;
        }
        // pending & partially filled $orders
        $request['status'] = 5;
        $response = $this->privateGetOrders (array_merge ($request, $params));
        $orders = $this->safe_value($response, 'orders');
        return $this->parse_orders($orders, $market, $since, $limit);
    }

    public function fetch_closed_orders ($symbol = null, $since = null, $limit = null, $params = array ()) {
        if ($symbol === null) {
            throw new ArgumentsRequired($this->id . ' fetchClosedOrders requires a $symbol argument');
        }
        $this->load_markets();
        $market = $this->market ($symbol);
        $request = array (
            'symbol' => $this->market_id($symbol),
        );
        if ($limit === null) {
            $limit = 500;
        }
        $request['limit'] = $limit;
        if ($this->safe_integer($params, 'offset') === null) {
            $request['offset'] = 0;
        }
        // successful and canceled $orders
        $request['status'] = 6;
        $response = $this->privateGetOrders (array_merge ($request, $params));
        $orders = $this->safe_value($response, 'orders');
        return $this->parse_orders($orders, $market, $since, $limit);
    }

    public function fetch_order ($id, $symbol = null, $params = array ()) {
        if ($symbol === null) {
            throw new ArgumentsRequired($this->id . ' fetchOrder requires a $symbol argument');
        }
        $this->load_markets();
        $market = $this->market ($symbol);
        $response = $this->privateGetOrdersId (array_merge (array (
            'id' => $id,
        ), $params));
        return $this->parse_order($response, $market);
    }

    public function nonce () {
        return $this->milliseconds ();
    }

    public function sign ($path, $api = 'public', $method = 'GET', $params = array (), $headers = null, $body = null) {
        $url = $this->urls['api'] . '/' . $this->version . '/' . $this->implode_params($path, $params);
        $query = $this->omit ($params, $this->extract_params($path));
        if ($api === 'public') {
            if ($query) {
                $url .= '?' . $this->urlencode ($query);
            }
        } else if ($api === 'token') {
            $this->check_required_credentials();
            $body = $this->urlencode ($query);
            $headers = array (
                'Content-Type' => 'application/x-www-form-urlencoded',
            );
        } else {
            $this->check_required_credentials();
            $token = $this->safe_string($this->options, 'accessToken');
            if ($token === null) {
                throw new AuthenticationError($this->id . ' ' . $path . ' endpoint requires an accessToken option or a prior call to signIn() method');
            }
            $expires = $this->safe_integer($this->options, 'expires');
            if ($expires !== null) {
                if ($this->nonce () >= $expires) {
                    throw new AuthenticationError($this->id . ' accessToken expired, supply a new accessToken or call to signIn() method');
                }
            }
            if ($query) {
                $url .= '?' . $this->urlencode ($query);
            }
            $headers = array (
                'Content-Type' => 'application/json',
                'X-BM-TIMESTAMP' => $this->nonce (),
                'X-BM-AUTHORIZATION' => 'Bearer ' . $token,
            );
            if ($method !== 'GET') {
                $query = $this->keysort ($query);
                $body = $this->json ($query);
                $message = $this->urlencode ($query);
                $headers['X-BM-SIGNATURE'] = $this->hmac ($this->encode ($message), $this->encode ($this->secret), 'sha256');
            }
        }
        return array( 'url' => $url, 'method' => $method, 'body' => $body, 'headers' => $headers );
    }
}
