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
import math
from collections import defaultdict as dd

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

positions = {"GS":0}

def handle_fill_message(message):
    global positions
    symbol = message['symbol']
    quantity = int(message['size'])  # Ensure quantity is an integer
    direction = message['dir']  # 'BUY' or 'SELL'
    
    if direction == 'BUY':
        positions[symbol] += quantity
    elif direction == 'SELL':
        positions[symbol] -= quantity

def main():
    args = parse_arguments()

    exchange = ExchangeConnection(args=args)

    # Store and print the "hello" message received from the exchange. This
    # contains useful information about your positions. Normally you start with
    # all positions at zero, but if you reconnect during a round, you might
    # have already bought/sold symbols and have non-zero positions.
    hello_message = exchange.read_message()
    print("First message from exchange:", hello_message)
        
    order_id = 1
    arb_order_id = []
    arb_order_id_s = []
    price_offset = 1
    bond_fair_value = 1000

    best_buy_prices = {
            "BOND":1000,
            "GS":-999e6,
            "MS":-999e6,
            "WFC":-999e6,
            "XLF":-999e6
            }
    
    best_sell_prices = {
        "BOND":1000,
        "GS":999e6,
        "MS":999e6,
        "WFC":999e6,
        "XLF":999e6
        }
    
    market_making = [0,0,0,0,0,0,0,0,0,0]

    last_gs_buys = [100000,0,0,0,0,0,0,0,0]+[0,0,0,0,0,0,0,0,0,0]+[0,0,0,0,0,0,0,0,0,0]+[0,0,0,0,0,0,0,0,0,0]+[0,0,0,0,0,0,0,0,0,0]
    last_gs_asks = [100000,0,0,0,0,0,0,0,0,0]+[0,0,0,0,0,0,0,0,0,0]+[0,0,0,0,0,0,0,0,0,0]+[0,0,0,0,0,0,0,0,0,0]+[0,0,0,0,0,0,0,0,0,0]

    count = 0

    while True:
        message = exchange.read_message()

        # if len(arb_order_id)>=5:
        #     if message["type"]=="fill" and message["order_id"]==arb_order_id[0]:
        #             print("hello")
        #             if message["type"]=="fill" and message["order_id"]==arb_order_id[1]:
        #                     if message["type"]=="fill" and message["order_id"]==arb_order_id[2]:
        #                             if message["type"]=="fill" and message["order_id"]==arb_order_id[3]:
        #                                     if message["type"]=="fill" and message["order_id"]==arb_order_id[4]:
        #                                         # exchange.send_convert_message(order_id, "XLF", Dir.BUY, 10)
        #                                         exchange.send_add_message(order_id, "XLF", Dir.BUY, best_sell_prices["XLF"], 10)
        #                                         arb_order_id.append(order_id)
        #                                         order_id+=1
        # if len(arb_order_id_s)>=5:
        #     if message["type"]=="fill" and message["order_id"]==arb_order_id_s[0]:
        #             print("hello")
        #             if message["type"]=="fill" and message["order_id"]==arb_order_id_s[1]:
        #                     if message["type"]=="fill" and message["order_id"]==arb_order_id_s[2]:
        #                             if message["type"]=="fill" and message["order_id"]==arb_order_id_s[3]:
        #                                     if message["type"]=="fill" and message["order_id"]==arb_order_id_s[4]:
        #                                         # exchange.send_convert_message(order_id, "XLF", Dir.BUY, 10)
        #                                         exchange.send_add_message(order_id, "XLF", Dir.BUY, best_sell_prices["XLF"], 10)
        #                                         arb_order_id_s.append(order_id)
        #                                         order_id+=1

        gs_pos = 0

        if message["type"] == "close":
            print("The round has ended")
            break
        elif message["type"] == "book":
            
            # if message["symbol"] == "BOND":
            #     # Check if there are bids and offers in the book
            #     best_bid = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
            #     best_buy_prices['BOND'] = best_bid
            #     best_ask = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else float('inf')
            #     best_sell_prices['BOND'] = best_ask
                
            #     # Adjusting strategy to buy BOND for less than $1000 and sell for more than $1000
            #     if best_bid > 0 and best_bid + price_offset < bond_fair_value:
            #         # Place a buy order just above the best bid but still below $1000
            #         buy_price = min(best_bid + price_offset, bond_fair_value - 1)
            #         exchange.send_add_message(order_id, "BOND", Dir.BUY, buy_price, 1)
            #         order_id += 1

            #     if best_ask < float('inf') and best_ask - price_offset > bond_fair_value:
            #         # Place a sell order just below the best ask but still above $1000
            #         sell_price = max(best_ask - price_offset, bond_fair_value + 1)
            #         exchange.send_add_message(order_id, "BOND", Dir.SELL, sell_price, 1)
            #         order_id += 1

            if message["symbol"] == "GS":
                best_buy_prices['GS'] = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
                best_sell_prices['GS'] = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else 999e6
                
                
                last_gs_buys.append(best_buy_prices['GS'])
                theo_buy = sum(last_gs_buys[-50:]) / len(last_gs_buys[-50:])

                last_gs_asks.append(best_sell_prices['GS'])
                theo_sell = sum(last_gs_asks[-50:]) / len(last_gs_asks[-50:])

                theo_spread = (theo_sell - theo_buy)

                theo = theo_buy + 0.5*theo_spread

                our_spread = (0.8*theo_spread)

                our_buy =  math.ceil(theo-0.5*(our_spread))
                our_ask = math.floor(theo+0.5*(our_spread))

                count += 1

                if count > 50:

                    if our_buy < our_ask:
                        print(f"Current GS Position: {positions['GS']}")

                        if positions["GS"] < 10:
                            print(f"Sending BUY order for GS at price {our_buy}")
                            exchange.send_add_message(order_id, "GS", Dir.BUY, our_buy, 1)
                            order_id += 1
                            market_making.append(order_id)  # Track the new order ID
                            print(f"Canceling oldest order: {market_making[0]}")
                            exchange.send_cancel_message(market_making[0])
                            market_making.pop(0)  # Remove the oldest order ID

                        if positions["GS"] > -10:
                            print(f"Sending SELL order for GS at price {our_ask}")
                            exchange.send_add_message(order_id, "GS", Dir.SELL, our_ask, 1)
                            order_id += 1
                            market_making.append(order_id)  # Track the new order ID
                            print(f"Canceling oldest order: {market_making[0]}")
                            exchange.send_cancel_message(market_making[0])
                            market_making.pop(0)  # Remove the oldest order ID

                    if positions["GS"] < -10 or positions["GS"] > 10:
                        print("Position limit reached. Canceling all orders.")
                        for id in market_making:
                            print(f"Canceling order: {id}")
                            exchange.send_cancel_message(id)
                        market_making = []

                    print(f"Active Orders: {market_making}")


            if message["symbol"] == "MS":
                best_buy_prices['MS'] = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
                best_sell_prices['MS'] = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else float('inf')
            if message["symbol"] == "WFC":
                best_buy_prices['WFC'] = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
                best_sell_prices['WFC'] = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else float('inf')
            if message["symbol"] == "XLF":
                best_buy_prices['XLF'] = max(message["buy"], key=lambda x: x[0], default=[0, 0])[0] if message["buy"] else 0
                best_sell_prices['XLF'] = min(message["sell"], key=lambda x: x[0], default=[float('inf'), 0])[0] if message["sell"] else float('inf')

        elif message['type'] == 'fill':
            handle_fill_message(message)

        elif message["type"] in ["error", "reject"]:
            print(message)
            # message = exchange.read_message()  # Pseudocode for receiving a message

        # market making
        
            
        # bundle_sum = 3*best_buy_prices["BOND"] + 2*best_buy_prices["GS"] + 3*best_buy_prices["MS"] + 2*best_buy_prices["WFC"]

        # if best_sell_prices['XLF'] < bundle_sum - 10 :
        #     print(best_sell_prices['XLF'])
        #     print(sum(list(best_buy_prices.values())[:-1]) - 10)
        #     exchange.send_add_message(order_id, "BOND", Dir.SELL, best_buy_prices["BOND"], 3)
        #     arb_order_id.append(order_id)
        #     order_id+=1
        #     exchange.send_add_message(order_id, "GS", Dir.SELL, best_buy_prices["GS"], 2)
        #     arb_order_id.append(order_id)
        #     order_id+=1
        #     exchange.send_add_message(order_id, "MS", Dir.SELL, best_buy_prices["MS"], 3)
        #     arb_order_id.append(order_id)
        #     order_id+=1
        #     exchange.send_add_message(order_id, "WFC", Dir.SELL, best_buy_prices["WFC"], 2)
        #     arb_order_id.append(order_id)
        #     order_id+=1
        #     exchange.send_add_message(order_id, "XLF", Dir.BUY, best_sell_prices["XLF"], 10)
        #     # exchange.send_convert_message(order_id, "XLF", Dir.S, 10)
        #     arb_order_id.append(order_id)
        #     order_id+=1

        # # print(arb_order_id)

        # # print(best_buy_prices)
        # bundle_sum = 3*best_sell_prices["BOND"] + 2*best_sell_prices["GS"] + 3*best_sell_prices["MS"] + 2*best_sell_prices["WFC"]
    
        # if best_buy_prices['XLF'] - 10 > bundle_sum:
        #     exchange.send_add_message(order_id, "BOND", Dir.BUY, best_sell_prices["BOND"], 3)
        #     arb_order_id_s.append(order_id)
        #     order_id+=1
        #     exchange.send_add_message(order_id, "GS", Dir.BUY, best_sell_prices["GS"], 2)
        #     arb_order_id_s.append(order_id)
        #     order_id+=1
        #     exchange.send_add_message(order_id, "MS", Dir.BUY, best_sell_prices["MS"], 3)
        #     arb_order_id_s.append(order_id)
        #     order_id+=1
        #     exchange.send_add_message(order_id, "WFC", Dir.BUY, best_sell_prices["WFC"], 2)
        #     arb_order_id_s.append(order_id)
        #     order_id+=1
        #     exchange.send_add_message(order_id, "XLF", Dir.SELL, best_buy_prices["XLF"], 10)
        #     arb_order_id_s.append(order_id)
        #     order_id+=1
                
        # if len(arb_order_id) > 5:
        #     for id in arb_order_id[:5]:
        #         exchange.send_cancel_message(id)
        #         arb_order_id = arb_order_id[5:]

        # if len(arb_order_id_s) > 5:
        #     for id in arb_order_id_s[:5]:
        #         exchange.send_cancel_message(id)
        #         arb_order_id_s = arb_order_id_s[5:]

        #     print(arb_order_id_s)

    



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