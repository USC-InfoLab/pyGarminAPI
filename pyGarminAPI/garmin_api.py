import yaml
from loguru import logger
import pandas as pd
from sqlalchemy import create_engine
from typing import List
from urllib.parse import urlencode


from datetime import datetime, timedelta

import pytz

import oauthlib.oauth1
import requests

import sys
import os

sys.path.insert(0, os.path.abspath('..'))


config_file = '../config.yml'

def load_config(config_file) -> dict:
    """Read the YAML config file

    Args:
        config_file (str): YAML configuration file path
    """
    with open(config_file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

# load the configurations
config = load_config(config_file=config_file)
# Database connection configuration
DB_HOST = config['database']['db_host']
DB_PORT = config['database']['db_port']
DB_USER = config['database']['db_user']
DB_PASS = config['database']['db_pass']
DB_NAME = config['database']['db_name']
DB_USER_TABLE = config['database']['db_user_table']
DB_AUTH_TABLE = config['database']['db_auth_table']
# Garmin API configuration
CONSUMER_KEY = config['garmin']['consumer_key']
CONSUMER_SECRET = config['garmin']['consumer_secret']
GARMIN_API_URL = config['garmin']['api_base_url']


def convert_to_utc_seconds(date_time: str) -> int:
    """Convert the date time to UTC seconds

    Args:
        date_time (str): Date time in the format of YYYY-MM-DD HH:MM:SS

    Returns:
        int: UTC seconds
    """
    # create a timezone object for pacific time
    pacific_tz = pytz.timezone('US/Pacific')

    # convert the date time string to a datetime object in the pacific time
    date_time_obj_pacific = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pacific_tz)

    # convert the pacific datetime object to UTC datetime object
    date_time_obj_utc = date_time_obj_pacific.astimezone(pytz.utc)

    # convert the UTC datetime object to UTC seconds
    utc_seconds = int(date_time_obj_utc.timestamp())

    return utc_seconds



def get_access_token(email_pattern: str = None) -> pd.DataFrame:
    """Get the access token and secret from the database

    Args:
        email_pattern (str, optional): Email pattern to filter the database. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame containing columns for the access token and secret
    """
    # create the connection
    con_str = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    db_engine = create_engine(con_str)
    # create the SQL query
    sql = f"SELECT email, access_token, token_secret FROM {DB_AUTH_TABLE}, {DB_USER_TABLE}\
            WHERE {DB_AUTH_TABLE}.user_id = {DB_USER_TABLE}.user_id"
    params = []
    # if email pattern is specified
    if email_pattern:
        sql += f" AND email LIKE %s"
        pattern = f'%{email_pattern}%'
        params = [pattern]
    # execute the query
    results = pd.read_sql_query(sql, db_engine, params=params)
    logger.success('access tokens retrieved from database')
    return results
    


def generate_signature(email_pattern: str = None) -> List[oauthlib.oauth1.Client]:
    """Generate the signature for the API request

    Args:
        email_pattern (str, optional): Email pattern to filter the database. Defaults to None.

    Returns:
        List[oauthlib.oauth1.Client]: List of oauthlib.oauth1.Client objects to sign requests
    """
    # get the access token and secret
    sign_tokens = get_access_token(email_pattern=email_pattern)
    signatures_list = []
    for i, row in sign_tokens.iterrows():
        # create the signature
        signature = oauthlib.oauth1.Client(CONSUMER_KEY, client_secret=CONSUMER_SECRET,
                                       resource_owner_key=row['access_token'],
                                       resource_owner_secret=row['token_secret'])
            # append each signature as a pandas dataframe to the signatures_list
        df_temp = pd.DataFrame({
            'email': [row['email']],
            'signature': [signature]
        })
        signatures_list.append(df_temp)
    signatures = pd.concat(signatures_list, ignore_index=True)
    logger.success('signatures generated')
    return signatures


def get_user_id(signature_client: oauthlib.oauth1.Client) -> dict:
    """Retrieve user id from the API

    Args:
        signature_client (oauthlib.oauth1.Client): oauthlib.oauth1.Client object to sign requests

    Returns:
        dict: JSON response from the API
    """    
    api_endpoint = f'{GARMIN_API_URL}/wellness-api/rest/user/id'
    
    # Construct the request headers and body
    uri, headers, body = signature_client.sign(api_endpoint)
    # Send the signed request
    response = requests.get(uri, headers=headers)
    # Check if the response was successful (HTTP status code 200)
    if response.status_code == 200:
        # Process the response data (in this case, we assume it's JSON)
        logger.success('user id retrieved')
        return response.json()
    else:
        print('Request failed with HTTP status code %d' % response.status_code)
        logger.error(f'Request failed with HTTP status code {response.status_code}')
        return
    

def get_permissions_scope(signature_client: oauthlib.oauth1.Client) -> dict:
    """Retrieve permissions scope from the API

    Args:
        signature_client (oauthlib.oauth1.Client): oauthlib.oauth1.Client object to sign requests

    Returns:
        dict: JSON response from the API
    """   
    api_endpoint = f'{GARMIN_API_URL}/userPermissions'
    
    # Construct the request headers and body
    uri, headers, body = signature_client.sign(api_endpoint)
    # Send the signed request
    response = requests.get(uri, headers=headers)
    # Check if the response was successful (HTTP status code 200)
    if response.status_code == 200:
        # Process the response data (in this case, we assume it's JSON)
        logger.success('permissions scope retrieved')
        return response.json()
    else:
        print('Request failed with HTTP status code %d' % response.status_code)
        logger.error(f'Request failed with HTTP status code {response.status_code}')
        return
    
    
def get_daily_summary_health(signature_client: oauthlib.oauth1.Client, start_time: str, end_time: str) -> dict:
    """Retrieve daily summary health data from the API
    
    Args:
        signature_client (oauthlib.oauth1.Client): oauthlib.oauth1.Client object to sign requests
        start_time (str): Start time
        end_time (str): End time

    Returns:
        dict: JSON response from the API
    """  
    api_endpoint = f'{GARMIN_API_URL}/wellness-api/rest/dailies'
    start_time_seconds = convert_to_utc_seconds(start_time)
    end_time_seconds = convert_to_utc_seconds(end_time)
    
    # add parameters
    params = {
        'uploadStartTimeInSeconds': start_time_seconds,
        'uploadEndTimeInSeconds': end_time_seconds
    }
    
    url_with_params = api_endpoint + '?' + urlencode(params)

    # Construct the request headers and body
    uri, headers, body = signature_client.sign(url_with_params)

    # Send the signed request
    response = requests.get(uri, headers=headers)
    # Check if the response was successful (HTTP status code 200)
    if response.status_code == 200:
        # Process the response data (in this case, we assume it's JSON)
        logger.success('daily summaries retrieved')
        return response.json()
    else:
        print('Request failed with HTTP status code %d' % response.status_code)
        logger.error(f'Request failed with HTTP status code {response.status_code}')
        return
    
    

def get_daily_summary_activity(signature_client: oauthlib.oauth1.Client, start_time: str, end_time: str) -> dict:
    """Retrieve daily summary activity data from the API
    
    Args:
        signature_client (oauthlib.oauth1.Client): oauthlib.oauth1.Client object to sign requests
        start_time (str): Start time
        end_time (str): End time

    Returns:
        dict: JSON response from the API
    """  
    api_endpoint = f'{GARMIN_API_URL}/wellness-api/rest/activities'
    start_time_seconds = convert_to_utc_seconds(start_time)
    end_time_seconds = convert_to_utc_seconds(end_time)
    
    # add parameters
    params = {
        'uploadStartTimeInSeconds': start_time_seconds,
        'uploadEndTimeInSeconds': end_time_seconds
    }
    
    url_with_params = api_endpoint + '?' + urlencode(params)

    # Construct the request headers and body
    uri, headers, body = signature_client.sign(url_with_params)

    # Send the signed request
    response = requests.get(uri, headers=headers)
    # Check if the response was successful (HTTP status code 200)
    if response.status_code == 200:
        # Process the response data (in this case, we assume it's JSON)
        logger.success('activity summaries retrieved')
        return response.json()
    else:
        print('Request failed with HTTP status code %d' % response.status_code)
        logger.error(f'Request failed with HTTP status code {response.status_code}')
        return