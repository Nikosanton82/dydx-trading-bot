import os
import datetime
from pytz import timezone, utc
import time
from pprint import pprint
from func_utils import format_number
# from datetime import datetime, timedelta

# Replace 'YOUR_TIME_ZONE' with your actual time zone. For example, 'America/New_York' or 'Europe/London'
os.environ['TZ'] = 'Europe/Vienna'
time_zone = timezone(os.environ['TZ'])

current_time = datetime.datetime.now(time_zone)
# print("Current time in your time zone:", current_time)

# Place Market order
def place_market_order(client, market, side, size, price, reduce_only):
    # Get Position ID
    account_response = client.private.get_account()
    position_id = account_response.data["account"]["positionId"]

    # Get expiration time
    server_time = client.public.get_time()
    server_time_utc = datetime.datetime.fromisoformat(server_time.data["iso"].rstrip("Z")).replace(tzinfo=utc)
    server_time_local = server_time_utc.astimezone(time_zone)
    expiration = server_time_local + datetime.timedelta(minutes=2, seconds=10)  # Changed to 2 minutes and 10 seconds

    # print("Server Time (UTC):", server_time_utc.isoformat())  # Debug print
    # print("Server Time (Local):", server_time_local.isoformat())  # Debug print
    # print("Expiration Time:", expiration.isoformat())  # Debug print

    # Place an order 
    placed_order = client.private.create_order(
        position_id=position_id, # required for creating the order signature
        market=market,
        side=side,
        order_type="MARKET",
        post_only=False,
        size=size,
        price=price,
        limit_fee='0.015',
        expiration_epoch_seconds=expiration.timestamp(),
        time_in_force="FOK",
        reduce_only=reduce_only
    )

    # Return results
    return placed_order.data




# Abort all positions
def abort_all_positions(client):
    
    # Cancel all orders
    client.private.cancel_all_orders()

    # Protect API
    time.sleep(0.5)

    # Get markets for reference of tick size
    markets = client.public.get_markets().data

    # Protect API
    time.sleep(0.5)

    # Get all open positions
    positions = client.private.get_positions(status="OPEN")
    all_positions = positions.data["positions"]

    # pprint(all_positions)

    # Handle open positions
    close_orders = []
    if len(all_positions) > 0:

        # Loop through each position
        for position in all_positions:

            # Determinae Market:
            market = position["market"]

            # Determine Side
            side = "BUY"
            if position["side"] == "LONG":
                side = "SELL"

            # print(market, side)
            
            # Get price
            price = float(position["entryPrice"])
            accept_price = price * 1.7 if side == "BUY" else price * 0.3
            tick_size = markets["markets"][market]["tickSize"]
            accept_price = format_number(accept_price, tick_size)

            # Place order to close
            order = place_market_order(
                client,
                market,
                side,
                position["sumOpen"],
                accept_price,
                True
            )

            # Append the result to closed orders
            close_orders.append(order)

            # Protect API
            time.sleep(0.2)

        # Return closed orders
        return close_orders




