import pandas as pd
import datetime as dt
from pprint import pprint

from deribit_service import deribit_util
from openapi_client.rest import ApiException



def load_data(input_data):
    """
    Load data by using debrit API
    Need to put the openapi_client python in parent folder
    :param credentials: dic with key and secret information
    :return return the required data
    e.g.
    {
    'volume': 14.6,
    'underlying_price': 9548.31,
    'underlying_index': 'BTC-27DEC19',
    'quote_currency': 'USD',
    'open_interest': 83.4,
    'mid_price': 0.441,
    'mark_price': 0.44181073,
    'low': 0.3885,
    'last': 0.4295,
    'interest_rate': 0.0,
    'instrument_name': 'BTC-27DEC19-12000-P',
    'high': 0.4565,
    'estimated_delivery_price': 9484.63,
    'creation_timestamp': 1563340045235,
    'bid_price': 0.434,
    'base_currency': 'BTC',
    'ask_price': 0.448
    }
    """
    
    credentials = deribit_util.read_config('/config_prod.ini', 'deribit_credential')
    # Create an instance of the market api class
    api_instance = deribit_util.deribit_api_client(credentials, api_type = 'market_data_api')
    try:
        # Publicly available market data used to generate a TradingView candle chart.
        instrument_name = input_data['instrument_name']
        start_timestamp = input_data['start_timestamp']
        end_timestamp = input_data['end_timestamp']
        resolution = input_data['resolution']
        
        api_response = api_instance.public_get_tradingview_chart_data_get(instrument_name, start_timestamp, end_timestamp, resolution)
#        pprint(api_response)
        
    except ApiException as e:
        print('Exception when calling MarketDataApi->public_get_tradingview_chart_data_get: %s\n' % e)

    return api_response['result']


def transform_data(json_resp):
    df = pd.DataFrame(json_resp)
    df['ticks'] = df.ticks / 1000
    df['timestamp'] = [dt.datetime.fromtimestamp(date) for date in df.ticks]

    return df


#if __name__ == "__main__":
#    credentials = deribit_util.read_config('/config_prod.ini', 'deribit_credential')
#    list_option = ['BTC-PERPETUAL']
#    
#    for currency in list_option:
#        json_resp = load_data(credentials, input_data)
#        data = transform_data(json_resp)
#        #save data

# TODO: 
# 1. Add python-mongo connector to push data into mongo
# 2. Add python scheduler to forard data in a regular basis 
