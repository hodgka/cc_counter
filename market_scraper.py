import asyncio
import asyncio.streams as stream
import csv
import os
from collections import namedtuple

import aiofiles
import aiohttp
import async_timeout
import pandas

Tick = namedtuple('Tick', ['MarketName', 'TimeStamp', 'Quantity', 'Price', 'Total', 'OrderType'])
tick_keys = ["MarketName", "TimeStamp", "Quantity", "Price", "Total", "OrderType"]
Order = namedtuple("Order", ["Type", "Quantity", "Rate"])
order_keys = ["Type", "Quantity", "Rate"]


async def get_market_history(sess, market):
    request_url = f"https://bittrex.com/api/v1.1/public/getmarkethistory?market={market}"
    market_history = await fetch(sess, request_url)
    market_history = market_history["result"]
    prepped_data = []
    for result in market_history:
        # print(result)
        result = {k: v for k, v in result.items() if k in tick_keys}
        result["MarketName"] = market
        # print(result)``
        prepped_data.append(Tick(**result))

    return prepped_data


async def get_order_book(sess, market, type_="both", depth=50):
    request_url = f"https://bittrex.com/api/v1.1/public/getorderbook?market={market}&type={type_}&depth={depth}"
    order_book = await fetch(sess, request_url)
    order_book = order_book["result"]
    prepped_data = []
    buys = order_book["buy"]
    sells = order_book["sell"]
    for buy in buys:
        prepped_data.append(Order("buy", **buy))
    for sell in sells:
        prepped_data.append(Order("sell", **sell))
    return prepped_data


async def get_markets(sess):
    request_url = 'http://bittrex.com/api/v1.1/public/getmarkets'
    markets_dict = await fetch(sess, request_url)
    results = markets_dict["result"]
    markets = [results[i]["MarketName"] for i in range(len(results))]
    return markets


async def fetch(sess, url):
    with async_timeout.timeout(10):
        async with sess.get(url) as r:
            return await r.json()


async def main():
    histories = []
    async with aiohttp.ClientSession() as sess:
        markets = ["BTC-ANS"]
        # markets = await get_markets(sess)

        while True:
            histories = {market: await get_market_history(sess, market) for market in markets}
            print("DONE")
            dataframes = [pandas.DataFrame.from_records(histories[history], columns=tick_keys) for history in histories]
            # write_to_files(histories)

            print(histories)
        # print(dataframes)


if __name__ == "__main__":

    ioloop = asyncio.get_event_loop()
    # ioloop.run_forever(main())
    ioloop.run_until_complete(main())
    ioloop.close()
