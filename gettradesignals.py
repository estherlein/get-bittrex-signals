import requests
import json
from src import Ichimoku
import click


@click.command()
@click.argument('interval', nargs=1)
@click.argument('base', nargs=1)
@click.argument('minvolume', nargs=1, type=int)
def cli(interval, base, minvolume):
    """
    Small routine that requests information from the bittrex API and uses Ichimoku kinko hyo. Trend signals for each market are dumped to a JSON file

    :param interval:
    The candlestick interval [“oneMin”, “fiveMin”, “thirtyMin”, “hour”, “day”]

    :param base:
    The base currency of the market pair [BTC, USD or USDT]

    :param minvolume:
    Minimum volume in base currency units
    """
    print('Running routine')
    agent = Ichimoku.Ichimoku(interval)
    market_summaries = simple_request('https://bittrex.com/api/v1.1/public/getmarketsummaries')
    li = []
    for summary in market_summaries['result']:
        if base.upper() in summary['MarketName'] and summary['BaseVolume'] >= minvolume:
            market = summary['MarketName']
            last = summary['Last']
            agent.change_market(market)
            senkouspana = agent.calculate_senkouspana()
            senkouspanb = agent.calculate_senkouspanb(agent.trim_data(52))
            senkouspanashadow = agent.calculate_senkouspanashadow()
            senkouspanbshadow = agent.calculate_senkouspanbshadow(agent.trim_shadowdata(52))
            tenkansen = agent.calculate_tenkansen(agent.trim_data(9))
            kijunsen = agent.calculate_kijunsen(agent.trim_data(26))
            tempdict = {}
            if senkouspana < senkouspanb:
                senkouspancross = 'bearish'
            else:
                senkouspancross = 'bullish'
            if tenkansen < kijunsen:
                tenkensenkijunsencross = 'bearish'
            else:
                tenkensenkijunsencross = 'bullish'
            if last > kijunsen:
                kijunsencross = 'bullish'
            else:
                kijunsencross = 'bearish'
            if last > senkouspanb and last > senkouspana:
                kumocloudbreakout = 'bullish'
            else:
                if last < senkouspanb and last < senkouspana:
                    kumocloudbreakout = 'bearish'
                else:
                    kumocloudbreakout = 'consolidation'
            if last > senkouspanbshadow and last > senkouspanashadow:
                kumoshadowbreakout = 'bullish'
            else:
                if last < senkouspanbshadow and last < senkouspanashadow:
                    kumoshadowbreakout = 'bearish'
                else:
                    kumoshadowbreakout = 'consolidation'
            tempdict['Market'] = market
            tempdict['Senkou Span Cross'] = senkouspancross
            tempdict['Tenkensen/kijunsen cross '] = tenkensenkijunsencross
            tempdict['Kijunsen Cross'] = kijunsencross
            tempdict['Kumo Cloud Breakout'] = kumocloudbreakout
            tempdict['Kumo Shadow Breakout'] = kumoshadowbreakout
            tempdict['Chikun Span Cross'] = agent.calculate_chikouspan()
            li.append(tempdict)
            print(market + ' is done')
    delete_content('data.json')
    with open('data.json', 'a') as outfile:
        json.dump(li, outfile)
    print('Routine done, lets sleep')


def delete_content(fname):
    with open(fname, "w"):
        pass


def simple_request(url):
    r = requests.get(url)
    return r.json()


def format_float(f):
    return "%.8f" % f


if __name__ == "__main__":
    cli()

