from libraries import *
from sqlalchemy import create_engine
from pymongo import MongoClient
from urllib.parse import quote_plus
import configparser

def load_config(section):
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    # Read configuration file
    config.read('configConnection.properties')
    # Return the configuration section as a dictionary
    return dict(config.items(section))

def mysql_conn():
    # Load MySQL configurations
    config = load_config('mysql')
    username = config['username']
    password = config['password']
    host = config['host']
    database = config['database']
    
    # Create SQLAlchemy engine using read configurations
    engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/{database}')
    return engine

def mongodb_conn():
    # Load MongoDB configurations
    config = load_config('mongodb')
    username = config['username']
    password = quote_plus(config['password'])  # URL-encode the password
    host = config['host']
    
    # Create URI and MongoClient using read configurations
    uri = f"mongodb+srv://{username}:{password}@{host}/?retryWrites=true&w=majority&appName=Cluster1"
    client = MongoClient(uri)
    return client
