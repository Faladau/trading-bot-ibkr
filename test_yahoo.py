"""Test rapid Yahoo Finance source"""
import asyncio
from src.agents.data_collection.sources.yahoo_source import YahooDataSource

async def test():
    y = YahooDataSource()
    await y.connect()
    bars = await y.fetch_historical_data('AAPL', '1D', 5)
    print(f'Got {len(bars)} bars')
    if bars:
        print(f'First bar: {bars[0].symbol} {bars[0].close} {bars[0].timestamp}')
        print(f'Last bar: {bars[-1].symbol} {bars[-1].close} {bars[-1].timestamp}')
    await y.disconnect()

if __name__ == "__main__":
    asyncio.run(test())
