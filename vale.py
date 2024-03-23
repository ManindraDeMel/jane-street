#!/usr/bin/env python3
# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py --test prod-like; sleep 1; done

import argparse
from collections import deque
from enum import Enum
import time
import socket
import json
import csv
from datetime import datetime

# ~~~~~============== CONFIGURATION  ==============~~~~~
# Replace "REPLACEME" with your team name!
team_name = "UltraTraders"

# ~~~~~============== MAIN LOOP ==============~~~~~

# You should put your code here! We provide some starter code as an example,
# but feel free to change/remove/edit/update any of it as you'd like. If you
# have any questions about the starter code, or what to do next, please ask us!
#
# To help you get started, the sample code below tries to buy BOND for a low
# price, and it prints the current prices for VALE every second. The sample
# code is intended to be a working example, but it needs some improvement
# before it will start making good trades!

# Global dictionaries to track the best bid and ask prices
best_bid_prices = {}
best_ask_prices = {}

positions = {'VALE': 0, 'VALBZ': 0}  


def handle_fill_message(message):
    global positions
    # Assuming the message contains 'symbol', 'dir' (BUY or SELL), and 'size'
    symbol = message['symbol']
    direction = message['dir']
    size = message['size']

    if direction == Dir.BUY:
        positions[symbol] += size
    elif direction == Dir.SELL:
        positions[symbol] -= size

    print(f"Updated positions after fill: {positions}")

def limit_position_convert(exchange, order_id, from_symbol, to_symbol, quantity):
    print(f"Attempting to convert {quantity} from {from_symbol} to {to_symbol}")
    exchange.send_convert_message(order_id, from_symbol, Dir.SELL, quantity)
    order_id += 1
    time.sleep(1)  # Respect rate limits
    return order_id



def execute_conversion_strategy(exchange, order_id):
    global best_bid_prices, best_ask_prices
    message_sent = False  # Flag to indicate if a message was sent

  ## CONVERSIONS
    if (positions['VALE'] <= -5) and (positions['VALBZ'] >= 5):
        exchange.send_convert_message(order_id, "VALE", Dir.BUY, 9)
        order_id += 1
        message_sent = True
    elif (positions['VALBZ'] == 5) or (positions['VALBZ'] == -5):
        exchange.send_convert_message(order_id, "VALE", Dir.BUY, 1)
        order_id += 1
        message_sent = True
    if (positions['VALBZ'] <= -5) and (positions['VALE'] >= 5):
        exchange.send_convert_message(order_id, "VALBZ", Dir.BUY, 9)
        order_id += 1
        message_sent = True
    elif (positions['VALE'] == 5) or (positions['VALBZ'] == -5):
        exchange.send_convert_message(order_id, "VALBZ", Dir.BUY, 1)
        order_id += 1
        message_sent = True
    if message_sent:
        time.sleep(0.1)  # Adjust the sleep duration as needed to comply with the exchange's rate limits


 ## IF VALE < VALBZ ~ BUY AND SELL
    # Check if ask price for VALE is less than the best bid price for VALBZ
    if best_ask_prices.get('VALE', float('inf')) < best_bid_prices.get('VALBZ', 0):
        # Buy 20 VALE
        if (positions['VALE'] != 9) and (positions['VALBZ'] != -9):
            exchange.send_add_message(order_id, "VALE", Dir.BUY, best_ask_prices['VALE'], 1)
            order_id += 1
            message_sent = True  # Set flag to True after sending a message
            time.sleep(0.1)
        # Sell 20 VALBZ
        if (positions['VALE'] != 9) and (positions['VALBZ'] != -9):
            exchange.send_add_message(order_id, "VALBZ", Dir.SELL, best_bid_prices['VALBZ'], 1)
            order_id += 1
            message_sent = True
            time.sleep(0.1)
            # If a message was sent, introduce a delay
        # Wait for confirmation of VALBZ sale (not shown here)
     ## IF VALBZ < VAL ~ BUY AND SELL
    if best_ask_prices.get('VALBZ', float('inf')) < best_bid_prices.get('VALE', 0):
        # Buy 1 VALBZ
        if (positions['VALE'] != -9) and (positions['VALBZ']  != 9):
            exchange.send_add_message(order_id, "VALBZ", Dir.BUY, best_ask_prices['VALBZ'], 1)
            order_id += 1
            message_sent = True  # Set flag to True after sending a message
            # Wait for confirmation of VALE purchase (not shown here)
            time.sleep(0.1)
        # Wait for conversion confirmation (not shown here)
        
        # Sell 1 VALE
        if (positions['VALE'] != -9) and (positions['VALBZ']  != 9):
            exchange.send_add_message(order_id, "VALE", Dir.SELL, best_bid_prices['VALE'], 1)
            order_id += 1
            message_sent = True
            time.sleep(0.1)
            # If a message was sent, introduce a delay
        if message_sent:
            time.sleep(0.1)  # Adjust the sleep duration as needed to comply with the exchange's rate limits

        # Wait for confirmation of VALBZ sale (not shown here)  
    # print(positions) 
    return order_id

def update_best_bid_ask(symbol, message):
    global best_bid_prices, best_ask_prices
    # Check if there are any buy orders and update the best bid price
    if message["buy"]:
        best_bid_prices[symbol] = max(message["buy"], key=lambda x: x[0])[0]
    else:
        # If there are no buy orders, we can't make a bid; you might choose to set this to 0 or keep the last known bid
        best_bid_prices[symbol] = 0  # or maintain the last known bid if appropriate

    # Check if there are any sell orders and update the best ask price
    if message["sell"]:
        best_ask_prices[symbol] = min(message["sell"], key=lambda x: x[0])[0]
    else:
        # If there are no sell orders, we can't make an ask; you might choose to set this to infinity or keep the last known ask
        best_ask_prices[symbol] = float('inf')  # or maintain the last known ask if appropriate


def main():
    args = parse_arguments()
    exchange = ExchangeConnection(args=args)
    hello_message = exchange.read_message()
    print("First message from exchange:", hello_message)
    order_id = 1
    price_offset = 1
    fair_value = 1000
    order_id = 1
    while True:
        message = exchange.read_message()
        if message['type'] == 'book' and message['symbol'] in ['VALE', 'VALBZ']:
            update_best_bid_ask(message['symbol'], message)

        elif message["type"] == "book" and message["symbol"] == "BOND":
            best_bid = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
            best_ask = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else float('inf')

            # Adjust buy and sell prices based on the larger price_offset
            if best_bid > 0 and best_bid + price_offset < fair_value:
                buy_price = min(best_bid + price_offset, fair_value - price_offset)  # Adjust buy price to be more competitive
                exchange.send_add_message(order_id, "BOND", Dir.BUY, buy_price, 1)
                order_id += 1

            if best_ask < float('inf') and best_ask - price_offset > fair_value:
                sell_price = max(best_ask - price_offset, fair_value + price_offset)  # Adjust sell price to be more competitive
                exchange.send_add_message(order_id, "BOND", Dir.SELL, sell_price, 1)
                order_id += 1

        elif message["type"] in ["error", "reject", "fill"]:
            print(message)
            time.sleep(0.1)
            # handle_fill_message(message)
        elif message['type'] == "reject" and message['error'] == "LIMIT:POSITION":
            print("LIMIT POSITION REACHED")
            # Determine the appropriate symbols and quantity based on your strategy and current positions
            from_symbol = "VALE"
            to_symbol = "VALBZ"
            quantity = 5  # Determine the appropriate quantity based on your positions and strategy
            order_id = limit_position_convert(exchange, order_id, from_symbol, to_symbol, quantity)

        elif message["type"] in ["error"]:
            print(message)
            time.sleep(0.1)
        order_id = execute_conversion_strategy(exchange, order_id)
            


# ~~~~~============== PROVIDED CODE ==============~~~~~

# You probably don't need to edit anything below this line, but feel free to
# ask if you have any questions about what it is doing or how it works. If you
# do need to change anything below this line, please feel free to


class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExchangeConnection:
    def __init__(self, args):
        self.message_timestamps = deque(maxlen=500)
        self.exchange_hostname = args.exchange_hostname
        self.port = args.port
        exchange_socket = self._connect(add_socket_timeout=args.add_socket_timeout)
        self.reader = exchange_socket.makefile("r", 1)
        self.writer = exchange_socket

        self._write_message({"type": "hello", "team": team_name.upper()})

    def read_message(self):
        """Read a single message from the exchange"""
        message = json.loads(self.reader.readline())
        if "dir" in message:
            message["dir"] = Dir(message["dir"])
        return message

    def send_add_message(
        self, order_id: int, symbol: str, dir: Dir, price: int, size: int
    ):
        """Add a new order"""
        self._write_message(
            {
                "type": "add",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "price": price,
                "size": size,
            }
        )

    def send_convert_message(self, order_id: int, symbol: str, dir: Dir, size: int):
        """Convert between related symbols"""
        self._write_message(
            {
                "type": "convert",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "size": size,
            }
        )

    def send_cancel_message(self, order_id: int):
        """Cancel an existing order"""
        self._write_message({"type": "cancel", "order_id": order_id})

    def _connect(self, add_socket_timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if add_socket_timeout:
            # Automatically raise an exception if no data has been recieved for
            # multiple seconds. This should not be enabled on an "empty" test
            # exchange.
            s.settimeout(5)
        s.connect((self.exchange_hostname, self.port))
        return s

    def _write_message(self, message):
        what_to_write = json.dumps(message)
        if not what_to_write.endswith("\n"):
            what_to_write = what_to_write + "\n"

        length_to_send = len(what_to_write)
        total_sent = 0
        while total_sent < length_to_send:
            sent_this_time = self.writer.send(
                what_to_write[total_sent:].encode("utf-8")
            )
            if sent_this_time == 0:
                raise Exception("Unable to send data to exchange")
            total_sent += sent_this_time

        now = time.time()
        self.message_timestamps.append(now)
        if len(
            self.message_timestamps
        ) == self.message_timestamps.maxlen and self.message_timestamps[0] > (now - 1):
            print(
                "WARNING: You are sending messages too frequently. The exchange will start ignoring your messages. Make sure you are not sending a message in response to every exchange message."
            )


def parse_arguments():
    test_exchange_port_offsets = {"prod-like": 0, "slower": 1, "empty": 2}

    parser = argparse.ArgumentParser(description="Trade on an ETC exchange!")
    exchange_address_group = parser.add_mutually_exclusive_group(required=True)
    exchange_address_group.add_argument(
        "--production", action="store_true", help="Connect to the production exchange."
    )
    exchange_address_group.add_argument(
        "--test",
        type=str,
        choices=test_exchange_port_offsets.keys(),
        help="Connect to a test exchange.",
    )

    # Connect to a specific host. This is only intended to be used for debugging.
    exchange_address_group.add_argument(
        "--specific-address", type=str, metavar="HOST:PORT", help=argparse.SUPPRESS
    )

    args = parser.parse_args()
    args.add_socket_timeout = True

    if args.production:
        args.exchange_hostname = "production"
        args.port = 25000
    elif args.test:
        args.exchange_hostname = "test-exch-" + team_name
        args.port = 25000 + test_exchange_port_offsets[args.test]
        if args.test == "empty":
            args.add_socket_timeout = False
    elif args.specific_address:
        args.exchange_hostname, port = args.specific_address.split(":")
        args.port = int(port)

    return args


if __name__ == "__main__":
    # Check that [team_name] has been updated.
    assert (
        team_name != "REPLAC" + "EME"
    ), "Please put your team name in the variable [team_name]."

    main()
