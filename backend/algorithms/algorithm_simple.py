# trading-bot/algorithms/algorithm_simple.py

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import json
import pathlib
from pprint import pprint

class SimpleAlgorithmLogger:
    def __init__(self, algorithm_name):
        # Create logs directory if it doesn't exist
        self.log_dir = pathlib.Path("logs") / algorithm_name
        self.log_dir.mkdir(exist_ok=True)
        
        # Create paths for both files
        self.db_file = self.log_dir / "db.json"
        self.temp_file = self.log_dir / "today.json"
        self.dump_file = self.log_dir / "dump.json"
        
        # Initialize or load existing historical data
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                self.historical_data = json.load(f)
        else:
            self.historical_data = {
                "algorithm_name": algorithm_name,
                "trades": []
            }

        # Initialize or load today's data
        today = datetime.now().date().isoformat()
        # today = (datetime.now().date() + timedelta(days=1)).isoformat()
        if self.temp_file.exists():
            with open(self.temp_file, 'r') as f:
                self.today_data = json.load(f)
                # If temp file is from a previous day, archive it and start fresh
                if self.today_data.get("date") != today:
                    self._archive_temp_data()
                    self.today_data = {
                        "date": today,
                        "trades": []
                    }
        else:
            self.today_data = {
                "date": today,
                "trades": []
            }
        

    def _archive_temp_data(self):
        """Archive temporary data to historical database and clear temp file"""
        if self.temp_file.exists():
            # Read and archive the temp data
            with open(self.temp_file, 'r') as f:
                temp_data = json.load(f)
                self.historical_data["trades"].extend(temp_data["trades"])
            
            # Save updated historical data
            with open(self.db_file, 'w') as f:
                json.dump(self.historical_data, f, indent=4)
            
            # Clear/reset the temp file by either:
            # Option 1: Delete the temp file
            self.temp_file.unlink()
            
            # Option 2: Or overwrite it with empty data for the new day
            # today = (datetime.now().date() + timedelta(days=1)).isoformat()
            # self.today_data = {
            #     "date": today,
            #     "trades": []
            # }
            # with open(self.temp_file, 'w') as f:
            #     json.dump(self.today_data, f, indent=4)

    def log_trade(self, order_type, status, details):
        trade_log = {
            "timestamp": datetime.now().isoformat(),
            "type": order_type,
            "status": status,
            "details": details
        }
        
        # Add to today's data
        self.today_data["trades"].append(trade_log)
        
        # Save to temp file
        with open(self.temp_file, 'w') as f:
            json.dump(self.today_data, f, indent=4)

    def has_traded_today(self, order_type):
        """Check if a specific type of trade has been executed today"""
        for trade in self.today_data["trades"]:
            if (trade["type"] == order_type and 
                trade["status"] == "SUCCESS"):
                return True
        return False

    def log_execution(self, notes):
        """Log this execution to the dump file"""
        timestamp = datetime.now().isoformat()
        execution_log = {
            "timestamp": timestamp,
            "current_hour": datetime.now().hour,
            "notes": notes
        }

        # Load existing dump data or create new
        if self.dump_file.exists():
            with open(self.dump_file, 'r') as f:
                dump_data = json.load(f)
        else:
            dump_data = {"executions": []}

        # Append new execution
        dump_data["executions"].append(execution_log)

        # Save updated dump file
        with open(self.dump_file, 'w') as f:
            json.dump(dump_data, f, indent=4)

def init_client():
    load_dotenv()
    return TradingClient(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        paper=True
    )

def place_order(trading_client, side, logger):
    market_order_data = MarketOrderRequest(
        symbol="BTC/USD",
        qty=0.0001,
        side=side,
        time_in_force=TimeInForce.GTC
    )
    
    try:
        market_order = trading_client.submit_order(order_data=market_order_data)
        logger.log_trade(
            order_type=side.value,
            status="SUCCESS",
            details={
                "symbol": "BTC/USD",
                "quantity": 0.0001,
                "order_id": str(market_order.id),
                "filled_price": market_order.filled_avg_price
            }
        )
        return market_order
    except Exception as e:
        logger.log_trade(
            order_type=side.value,
            status="ERROR",
            details={
                "symbol": "BTC/USD",
                "quantity": 0.0001,
                "error_message": str(e)
            }
        )
        return None

def main():
    ALGORITHM_NAME = "algorithm_simple"
    # Initialize the client and logger
    trading_client = init_client()
    logger = SimpleAlgorithmLogger(ALGORITHM_NAME)
    
    # Get current hour
    current_hour = datetime.now().hour
    notes = "No Action"
    # Buy at 18:00 (6 PM) if we haven't already bought today and have no position
    if current_hour == 10:
        if not logger.has_traded_today("buy"):
            place_order(trading_client, OrderSide.BUY, logger)
            if notes == "No Action":
                notes = "Bought"
            else:
                notes = notes + "Bought"
        
    # Sell at 21:00 (9 PM) if we haven't already sold today and have a position
    if current_hour == 15:
        if not logger.has_traded_today("sell") and logger.has_traded_today("buy"):
            place_order(trading_client, OrderSide.SELL, logger)
            if notes == "No Action":
                notes = "Sold"
            else:
                notes = notes + "Sold"
    # Log this execution
    logger.log_execution(notes)

if __name__ == "__main__":
    main()