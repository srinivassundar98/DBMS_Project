from libraries import *
from connections import *
from utils import *
from caching import *
from fetch import * 
client=mongodb_conn()
#engine=mysql_conn()
cache=SummaryCache(1048576)
def overview():
    query1="SELECT SCREEN_NAME,followers_count FROM TWEET_STORE_FINAL.USER_DETAILS ORDER BY followers_count DESC LIMIT 5;"
    query2="SELECT SCREEN_NAME,friends_count FROM TWEET_STORE_FINAL.USER_DETAILS ORDER BY friends_count DESC LIMIT 5;"
    query3="SELECT SCREEN_NAME,listed_count FROM TWEET_STORE_FINAL.USER_DETAILS ORDER BY listed_count DESC LIMIT 5;"
    query4="SELECT SCREEN_NAME,favourites_count FROM TWEET_STORE_FINAL.USER_DETAILS ORDER BY favourites_count DESC LIMIT 5;"
    query5="SELECT SCREEN_NAME,statuses_count FROM TWEET_STORE_FINAL.USER_DETAILS ORDER BY statuses_count DESC LIMIT 5;"
    query6="SELECT LOCATION,COUNT(LOCATION) as COUNT FROM TWEET_STORE_FINAL.USER_DETAILS GROUP BY LOCATION ORDER BY COUNT DESC LIMIT 10;"
    #df1=pd.read_sql(query1,engine)
    df1=pd.DataFrame(fetch_with_cache(query1,'mysql',cache))
    df2=pd.DataFrame(fetch_with_cache(query2,'mysql',cache))
    df3=pd.DataFrame(fetch_with_cache(query3,'mysql',cache))
    df4=pd.DataFrame(fetch_with_cache(query4,'mysql',cache))
    df5=pd.DataFrame(fetch_with_cache(query5,'mysql',cache))
    df6=pd.DataFrame(fetch_with_cache(query6,'mysql',cache))
    db = client['dbmsproject98_final']  # Change to your database name
    collection = db['RETWEETS']  # Change to your collection name

    # Define queries with sorting and limiting, including projection
    queries = {
        'favorite': [{'$sort': {'ORIGINAL_TWEET_FAVORITE_COUNT': -1}}, {'$limit': 5}, {'$project': {'_id': 0, 'translated_text': 1, 'ORIGINAL_TWEET_FAVORITE_COUNT': 1}}],
        'retweet': [{'$sort': {'ORIGINAL_TWEET_RETWEET_COUNT': -1}}, {'$limit': 5}, {'$project': {'_id': 0, 'translated_text': 1, 'ORIGINAL_TWEET_RETWEET_COUNT': 1}}],
        'reply': [{'$sort': {'ORIGINAL_TWEET_REPLY_COUNT': -1}}, {'$limit': 5}, {'$project': {'_id': 0, 'translated_text': 1, 'ORIGINAL_TWEET_REPLY_COUNT': 1}}],
        'quote': [{'$sort': {'ORIGINAL_TWEET_QUOTE_COUNT': -1}}, {'$limit': 5}, {'$project': {'_id': 0, 'translated_text': 1, 'ORIGINAL_TWEET_QUOTE_COUNT': 1}}]
    }

    dataframes = {}

    # Execute queries and store results in DataFrames
    for key, pipeline in queries.items():
        cursor = collection.aggregate(pipeline)
        dataframes[key] = pd.DataFrame(list(cursor))
        dataframes[key]['translated_text']=dataframes[key]['translated_text'].apply(lambda x: x[10:17])
    fig_favorite = px.bar(dataframes['favorite'], x='translated_text', y='ORIGINAL_TWEET_FAVORITE_COUNT', title='Top 5 Tweets by Favorite Count')
    fig_retweet = px.bar(dataframes['retweet'], x='translated_text', y='ORIGINAL_TWEET_RETWEET_COUNT', title='Top 5 Tweets by Retweet Count')
    fig_reply = px.bar(dataframes['reply'], x='translated_text', y='ORIGINAL_TWEET_REPLY_COUNT', title='Top 5 Tweets by Reply Count')
    fig_quote = px.bar(dataframes['quote'], x='translated_text', y='ORIGINAL_TWEET_QUOTE_COUNT', title='Top 5 Tweets by Quote Count')

    # Optionally, customize the layout to improve readability
    for fig in [fig_favorite, fig_retweet, fig_reply, fig_quote]:
        fig.update_layout(xaxis_title='Tweet Text', yaxis_title='Count', xaxis_tickangle=-45)
# Bar Charts
    fig1 = px.bar(df1, x='SCREEN_NAME', y='followers_count', title='Top 5 Users by Followers Count')
    fig2 = px.bar(df2, x='SCREEN_NAME', y='friends_count', title='Top 5 Users by Friends Count')

    # Pie Charts
    fig3 = px.pie(df3, names='SCREEN_NAME', values='listed_count', title='Top 5 Users by Listed Count')
    fig4 = px.pie(df4, names='SCREEN_NAME', values='favourites_count', title='Top 5 Users by Favourites Count')

    # Donut Charts
    fig5 = px.pie(df5, names='SCREEN_NAME', values='statuses_count', title='Top 5 Users by Statuses Count', hole=0.4)
    fig6 = px.pie(df6, names='LOCATION', values='COUNT', title='Top 10 Locations by User Count', hole=0.4)
    collection1 = db['TWEETS']  # Replace with your collection name

    # Aggregate to count each sentiment
    pipeline = [
        {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
    ]
    results1 = list(collection1.aggregate(pipeline))
    results2 = list(collection.aggregate(pipeline))
    pipeline2 = [
        {"$group": {"_id": "$emotion", "count": {"$sum": 1}}}
    ]
    results11 = list(collection.aggregate(pipeline2))

    # Create a DataFrame from the results
    emotion_counts1 = pd.DataFrame(results11)
    emotion_counts1.columns = ['emotion', 'count']
    results12 = list(collection1.aggregate(pipeline2))

    # Create a DataFrame from the results
    emotion_counts2 = pd.DataFrame(results12)
    emotion_counts2.columns = ['emotion', 'count']
    emotion_counts=pd.concat([emotion_counts1,emotion_counts2])
    fig_emo = px.pie(emotion_counts, values='count', names='emotion', title='Emotion Distribution', hole=0.4)

    # Customize the donut chart for better readability
    fig_emo.update_traces(textposition='inside', textinfo='percent+label')
    # Create a DataFrame from the results
    sentiment_counts1 = pd.DataFrame(results1)
    sentiment_counts1.columns = ['sentiment', 'count']
    sentiment_counts2 = pd.DataFrame(results2)
    sentiment_counts2.columns = ['sentiment', 'count']
    sentiment_counts=pd.concat([sentiment_counts1,sentiment_counts2])
    fig_sen = px.pie(sentiment_counts, values='count', names='sentiment', title='Sentiment Distribution')

    # Customize the pie chart for better readability
    fig_sen.update_traces(textposition='inside', textinfo='percent+label')
# Layout the visualizations in two columns
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)
        st.plotly_chart(fig5, use_container_width=True)
        st.plotly_chart(fig_sen, use_container_width=True)
        st.plotly_chart(fig_favorite, use_container_width=True)
        st.plotly_chart(fig_retweet, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)
        st.plotly_chart(fig6, use_container_width=True)
        st.plotly_chart(fig_emo, use_container_width=True)
        st.plotly_chart(fig_reply, use_container_width=True)
        st.plotly_chart(fig_quote, use_container_width=True)