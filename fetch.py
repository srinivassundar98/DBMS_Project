
from libraries import *
from connections import *
from caching import *
#client=mongodb_conn()
engine=mysql_conn()
def execute_mysql_query(q):
    df=pd.read_sql(q,engine)
    return df.to_dict()

def execute_mongodb_query(q,coll):
    return 0

def fetch_with_cache(query, db_type, cache):
    """
    Fetches data from cache if available, otherwise retrieves from the specified database and caches it.
    
    Args:
    - query: SQL query string or MongoDB query dictionary
    - db_type: 'mysql' for MySQL database or 'mongodb' for MongoDB
    - cache: An instance of LRUCache or SimpleFileCache
    
    Returns:
    - Data retrieved either from the database or cache
    """
    # Convert the query to a suitable format for caching
    if isinstance(query, dict):  # MongoDB query
        # Convert dictionary query to a unique string representation
        query_str = json.dumps(query, sort_keys=True)
    else:  # MySQL query
        query_str = query  # Use the SQL query string as is

    # Try to retrieve data from cache
    data = cache.get(query_str)
    if data is not None:
        print("Retrieved from cache")
        return data

    # Data not in cache, fetch from the database
    if db_type == 'mysql':
        data = execute_mysql_query(query)  # This function should be defined to execute a MySQL query
    elif db_type == 'mongodb':
        data = execute_mongodb_query(query)  # This function should be defined to execute a MongoDB query
    else:
        raise ValueError("Invalid database type specified. Use 'mysql' or 'mongodb'.")

    # Cache the retrieved data
    cache.set(query_str, data)
    print("Retrieved from DB and cached")
    
    return data

# Example usage with MySQL
# mysql_cache = LRUCache(capacity=100)  # Adjust capacity as needed
# query_mysql = "SELECT * FROM users WHERE id = 1;"
# data_mysql = fetch_with_cache(query_mysql, 'mysql', mysql_cache)

# # Example usage with MongoDB
# mongodb_cache = SimpleFileCache(filename='mongodb_cache.pkl', ttl=86400)  # 24 hours TTL
# query_mongodb = {"collection": "users", "find": {"id": 1}}
# data_mongodb = fetch_with_cache(query_mongodb, 'mongodb', mongodb_cache)
