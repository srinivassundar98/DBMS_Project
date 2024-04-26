from libraries import *
from connections import *
client=mongodb_conn()
engine=mysql_conn()
def parse_date(date_str):
    date_format = "%a %b %d %H:%M:%S %z %Y"
    parsed_date = datetime.strptime(date_str, date_format)
    return parsed_date
def safe_convert_dates(date_str):
    try:
        return pd.to_datetime(date_str, format='%a %b %d %H:%M:%S %z %Y', errors='coerce')
    except ValueError:
        return pd.NaT
def fetch_date_range_tweet():
    # Query to get the minimum and maximum created_at dates
    collection=client.dbmsproject98_final.TWEETS
    aggregation = collection.aggregate([
        {
            "$group": {
                "_id": None,
                "min_date": {"$min": "$CREATED_AT"},
                "max_date": {"$max": "$CREATED_AT"}
            }
        }
    ])
    result = list(aggregation)
    if result:
        # Parse the string dates into datetime objects
        min_date = parse_date(result[0]['min_date'])
        max_date = parse_date(result[0]['max_date'])
        min_date2=result[0]['min_date']
        max_date2=result[0]['max_date']
        return min_date, max_date,min_date2,max_date2
    else:
        # Return today's date as both min and max if no data
        today = datetime.now(pytz.utc)
        return today, today

def fetch_date_range_user():
    # Query to get the minimum and maximum created_at dates
    query="SELECT MIN(CREATED_AT) AS MIN, MAX(CREATED_AT) AS MAX FROM TWEET_STORE_FINAL.USER_DETAILS;"
    df=pd.read_sql(query,engine)
    
    
    min_date2=df["MIN"][0]
    max_date2=df["MAX"][0]
    min_date=parse_date(df["MIN"][0])
    max_date=parse_date(df["MAX"][0])
    return min_date,max_date,min_date2,max_date2

def get_date(user=None):
    if user:
        min_date,max_date,min_date2,max_date2=fetch_date_range_user()
    else:
        min_date, max_date,min_date2,max_date2 = fetch_date_range_tweet()
    
    # Create a date range slider in Streamlit

    return min_date,max_date,min_date2,max_date2