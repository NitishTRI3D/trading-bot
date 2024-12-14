from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv
import os

load_dotenv()

trading_client = TradingClient(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    paper=True
)


# preparing orders
market_order_data = MarketOrderRequest(
                    symbol="BTC/USD",
                    # amount=2500,
                    qty=0.05,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.GTC
                    )

# Market order
market_order = trading_client.submit_order(
                order_data=market_order_data
               )

list=trading_client.get_all_positions()
orders = trading_client.get_orders()
print(list)
