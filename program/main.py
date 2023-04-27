from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED, PLACE_TRADES
from func_connections import connect_dydx
from func_private import abort_all_positions
from func_public import construct_market_prices
from func_cointegration import store_cointegration_results
from func_entry_pairs import open_positions


if __name__ == "__main__":
    # Connect to client
    try:
        print("Connecting to Client...")
        client = connect_dydx()
    except Exception as e:
        print(e)
        print("Error connections to client: ", e)
        exit(1)

    # # Add the code here to print local time, server time, and time difference
    # from datetime import datetime
    # import pytz
    # import os

    # # Set the 'TZ' environment variable
    # os.environ['TZ'] = 'Europe/Vienna'
    # # Get local time
    # local_time = datetime.now(pytz.timezone(os.environ['TZ']))
    # print("Local time:", local_time)

    # # Get server time
    # server_time_response = client.public.get_time()
    # server_time_str = server_time_response.data["iso"].rstrip("Z")
    # server_time = datetime.fromisoformat(server_time_str).replace(tzinfo=pytz.UTC)
    # print("Server time:", server_time)

    # # Calculate the difference
    # time_difference = local_time - server_time
    # print("Time difference:", time_difference)

    # Abort all open positions
    if ABORT_ALL_POSITIONS:
        try:
            print("Closing all positions...")
            close_orders= abort_all_positions(client)
        except Exception as e:
            print("Error closing all postions: ", e)
            exit(1)


    # Find Cointegrated Pairs
    if FIND_COINTEGRATED:

        # Construct Market Prices
        try:
            print("Fetching market prices, please allow 3 minutes...")
            df_market_prices = construct_market_prices(client)
        except Exception as e:
            print("Error constructing market prices: ", e)
            exit(1)

        # Store Cointegrated Pairs
        try:
            print("Storing cointegrated pairs...")
            stores_result = store_cointegration_results(df_market_prices)
            if stores_result != "saved":
                print("Error saving cointegrating pairs")
                exit(1)
        except Exception as e:
            print("Error saving cointegrating pairs: ", e)
            exit(1)





    # Place trades for opening positions
    if PLACE_TRADES:
        try:
            print("Finding trading opportunities...")
            open_positions(client)
        except Exception as e:
            print("Error trading pairs: ", e)
            exit(1)