import os
import configparser

import openapi_client
_api_instance = None



#list API: https://github.com/deribit/deribit-api-clients

def read_config(config_path, section):
    """
    :param config_path: the location of configuration file
    :param section: section's name
    :return return an object contains configuration info
    """
    # Locate the configuration path
    script_dir = os.path.abspath(os.path.join('.','deribit_service/config'))
    abs_config_path = script_dir + config_path
    # Read configuration
    config = configparser.ConfigParser()
    config.read(abs_config_path)

    info = {}
    if config.has_section(section):
        params = config.items(section)
        for par in params:
            info[par[0]] = par[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, abs_config_path))

    return info


#TODO(jinsiang): Update to use request sessions
def deribit_api_client(credentials, api_type):
    """
    Take creds and return api client
    """
    global _api_instance
    if _api_instance == None:

        conf = openapi_client.Configuration()
        client = openapi_client.api_client.ApiClient(conf)
        publicApi = openapi_client.api.public_api.PublicApi(client)
        response = publicApi.public_auth_get('client_credentials', '', '', credentials['auth_key'], credentials['auth_secret'], '', '', '', scope='session:test wallet:read')
        access_token = response['result']['access_token']
        # Set up token information
        conf_authed = openapi_client.Configuration()
        conf_authed.access_token = access_token
        client_authed =  openapi_client.api_client.ApiClient(conf_authed)

        # Create an instance of the market api class
        if api_type == 'market_data_api':
            _api_instance = openapi_client.MarketDataApi(client_authed)

        if api_type == 'public_api':
            _api_instance = openapi_client.ApiClient(client_authed)

    return _api_instance




