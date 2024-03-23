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

# ~~~~~============== CONFIGURATION  ==============~~~~~
# Replace "REPLACEME" with your team name!
team_name = "ULTRATRADERS"

# ~~~~~============== MAIN LOOP ==============~~~~~

# You should put your code here! We provide some starter code as an example,
# but feel free to change/remove/edit/update any of it as you'd like. If you
# have any questions about the starter code, or what to do next, please ask us!
#
# To help you get started, the sample code below tries to buy BOND for a low
# price, and it prints the current prices for VALE every second. The sample
# code is intended to be a working example, but it needs some improvement
# before it will start making good trades!


def main():
    args = parse_arguments()

    exchange = ExchangeConnection(args=args)

    # Store and print the "hello" message received from the exchange. This
    # contains useful information about your positions. Normally you start with
    # all positions at zero, but if you reconnect during a round, you might
    # have already bought/sold symbols and have non-zero positions.
    hello_message = exchange.read_message()
    print("First message from exchange:", hello_message)

    # Send an order for BOND at a good price, but it is low enough that it is
    # unlikely it will be traded against. Maybe there is a better price to
    # pick? Also, you will need to send more orders over time.
    # exchange.send_add_message(order_id=1, symbol="BOND", dir=Dir.BUY, price=990, size=1)
    # exchange.send_add_message(order_id=1, symbol="SELL", dir=Dir.BUY, price=1010, size=1)
    # Set up some variables to track the bid and ask price of a symbol. Right
    # now this doesn't track much information, but it's enough to get a sense
    # of the VALE market.
    # vale_bid_price, vale_ask_price = None, None
    # vale_last_print_time = time.time()

    # Here is the main loop of the program. It will continue to read and
    # process messages in a loop until a "close" message is received. You
    # should write to code handle more types of messages (and not just print
    # the message). Feel free to modify any of the starter code below.
    #
    # Note: a common mistake people make is to call write_message() at least
    # once for every read_message() response.
    #
    # Every message sent to the exchange generates at least one response
    # message. Sending a message in response to every exchange message will
    # cause a feedback loop where your bot's messages will quickly be
    # rate-limited and ignored. Please, don't do that!

    # def best_price(side):
    #     if message[side]:
    #         return message[side][0][0]
        
    order_id = 1
    price_offset = 1
    bond_fair_value = 1000

    best_buy_prices = {
            "BOND":1000,
            "VALBZ":-999,
            "VALE":-999,
            "GS":-999,
            "MS":-999,
            "WFC":-999,
            "XLF":-999
            }
    
    best_sell_prices = {
        "BOND":1000,
        "VALBZ":999,
        "VALE":999,
        "GS":999,
        "MS":999,
        "WFC":999,
        "XLF":999
        }

    while True:
        message = exchange.read_message()

        if message["type"] == "close":
            print("The round has ended")
            break
        elif message["type"] == "book":
            
            if message["symbol"] == "BOND":
                # Check if there are bids and offers in the book
                best_bid = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
                best_buy_prices['BOND'] = best_bid
                best_ask = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else float('inf')
                best_sell_prices['BOND'] = best_ask
                
                # Adjusting strategy to buy BOND for less than $1000 and sell for more than $1000
                if best_bid > 0 and best_bid + price_offset < bond_fair_value:
                    # Place a buy order just above the best bid but still below $1000
                    buy_price = min(best_bid + price_offset, bond_fair_value - 1)
                    exchange.send_add_message(order_id, "BOND", Dir.BUY, buy_price, 1)
                    order_id += 1

                if best_ask < float('inf') and best_ask - price_offset > bond_fair_value:
                    # Place a sell order just below the best ask but still above $1000
                    sell_price = max(best_ask - price_offset, bond_fair_value + 1)
                    exchange.send_add_message(order_id, "BOND", Dir.SELL, sell_price, 1)
                    order_id += 1

            if message["symbol"] == "GS":
                best_buy_prices['GS'] = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
                best_sell_prices['GS'] = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else float('inf')
            if message["symbol"] == "MS":
                best_buy_prices['MS'] = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
                best_sell_prices['MS'] = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else float('inf')
            if message["symbol"] == "WFC":
                best_buy_prices['WFC'] = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
                best_sell_prices['WFC'] = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else float('inf')
            if message["symbol"] == "XLF":
                best_buy_prices['XLF'] = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
                best_sell_prices['XLF'] = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else float('inf')

            

            if best_sell_prices['XLF'] < sum(list(best_buy_prices.values())[:-1]) - 10:
                exchange.send_add_message(order_id, "BOND", Dir.SELL, best_buy_prices["BOND"], 3)
                order_id+=1
                exchange.send_add_message(order_id, "GS", Dir.SELL, best_buy_prices["GS"], 2)
                order_id+=1
                exchange.send_add_message(order_id, "MS", Dir.SELL, best_buy_prices["MS"], 3)
                order_id+=1
                exchange.send_add_message(order_id, "WFC", Dir.SELL, best_buy_prices["WFC"], 3)
                order_id+=1
                exchange.send_add_message(order_id, "XLF", Dir.BUY, best_sell_prices["XLF"], 10)
                order_id+=1
            
        
            if best_buy_prices['XLF'] - 10 > sum(list(best_sell_prices.values())[:-1]):
                exchange.send_add_message(order_id, "BOND", Dir.SELL, best_sell_prices["BOND"], 3)
                order_id+=1
                exchange.send_add_message(order_id, "GS", Dir.SELL, best_sell_prices["GS"], 2)
                order_id+=1
                exchange.send_add_message(order_id, "MS", Dir.SELL, best_sell_prices["MS"], 3)
                order_id+=1
                exchange.send_add_message(order_id, "WFC", Dir.SELL, best_sell_prices["WFC"], 3)
                order_id+=1
                exchange.send_add_message(order_id, "XLF", Dir.BUY, best_buy_prices["XLF"], 10)
                order_id+=1
                
        elif message["type"] in ["error", "reject", "fill"]:
            print(message)
    



# ~~~~~============== PROVIDED CODEu ==============~~~~~

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