from libraries import *
from utils import *
from connections import *
from caching import *
from fetch import *
cache=SimpleFileCache()
client=mongodb_conn()
#engine=mysql_conn()

def user_analysis(min_date,max_date,user=None):
    if user:
        print("sup")
    else:
        print(min_date)


        query="""
select DISTINCT(SCREEN_NAME) AS USER_NAME,LENGTH(ENTITIES_USER_MENTIONS) - LENGTH(REPLACE(ENTITIES_USER_MENTIONS, ',', '')) AS USERS_MENTIONED,
LENGTH(ENTITIES_HASHTAGS) - LENGTH(REPLACE(ENTITIES_HASHTAGS, ',', '')) AS HASHTAGS_MENTIONED  
FROM TWEET_STORE_FINAL.USER_DETAILS WHERE CREATED_AT>='{min_date}' AND CREATED_AT<='{max_date}' ORDER BY USERS_MENTIONED DESC, HASHTAGS_MENTIONED DESC;""".format(min_date=min_date,max_date=max_date)
        df_users=pd.DataFrame(fetch_with_cache(query,'mysql',cache))
        user_list=df_users["USER_NAME"].values.tolist()
        selected_option = st.selectbox("Choose an option:", user_list)
        logging.info(f"User Selected: {selected_option}")
        q2="SELECT * FROM TWEET_STORE_FINAL.USER_DETAILS WHERE SCREEN_NAME='"+selected_option+"';"
        df_user=pd.DataFrame(fetch_with_cache(q2,'mysql',cache))
        user_id=df_user["id_str"][0]
        count_tweet = client.dbmsproject98_final.TWEETS.count_documents({"USER_ID": user_id})
        count_retweet = client.dbmsproject98_final.RETWEETS.count_documents({"USER_ID": user_id})
        desc=df_user["description"][0]
        st.markdown("""
            <style>
                .data-card {
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    background-color: #f1f1f1;
                    padding: 10px;
                    border-radius: 10px;
                    border: 2px solid #e1e1e1;
                    margin: 10px 0px;
                }
                .data-card h3 {
                    color: #0c4191;
                }
                .data-card p {
                    color: #333;
                }
            </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
                <div class="data-card">
                    <h3>User Details</h3>
                    <p>Name: {name}</p>
                    <p>ID: {id}</p>
                    <p>Description: {desc}</p>
                </div>
            """.format(name=selected_option,id=user_id,desc=desc), unsafe_allow_html=True)

        documents1 = list(client.dbmsproject98_final.TWEETS.find({'USER_ID': user_id}, {'ENTITIES_USER_MENTIONS': 1}))
        documents2 = list(client.dbmsproject98_final.RETWEETS.find({'USER_ID': user_id}, {'ORIGINAL_TWEET_ENTITIES_USER_MENTIONS': 1}))
        cleaned_items = []
        for doc in documents1:
            # Remove brackets and split by comma
            items = doc['ENTITIES_USER_MENTIONS'].replace('[', '').replace(']', '').split(',')
            cleaned_items.extend([item.strip() for item in items])  # Strip whitespace from each item
        for doc in documents2:
            # Remove brackets and split by comma
            items = doc['ORIGINAL_TWEET_ENTITIES_USER_MENTIONS'].replace('[', '').replace(']', '').split(',')
            cleaned_items.extend([item.strip() for item in items]) 
        # Count occurrences of each item
        from collections import Counter
        counter = Counter(cleaned_items)

        # Creating a DataFrame from the results
        df11 = pd.DataFrame(list(counter.items()), columns=['element', 'occurrences'])
        df11["element"]=df11["element"].apply(lambda x: str(x))
        # Sort the DataFrame by occurrences in descending order
        df11 = df11.sort_values(by='occurrences', ascending=False)
        id_list=df11["element"].values.tolist()
        occurrences=df11["occurrences"].values.tolist()        
        xax1=["ID: "+str(x) for x in id_list]
        yax=occurrences
        fig11 = go.Figure(go.Bar(
            x=xax1[0:10],
            y=yax[0:10]
            # Using a color scale based on sales
        ))

        # Add layout customization
        fig11.update_layout(
            title='User Details By Number',
            xaxis_title='Count',
            yaxis_title='Category',
            plot_bgcolor='rgba(0,0,0,0)', # Transparent background
        )
        st.plotly_chart(fig11)

    documents1 = client.dbmsproject98_final.TWEETS.find({"USER_ID": user_id})
    df1 = pd.DataFrame(list(documents1)) 
    # Convert query results to a DataFrame
    documents2 = client.dbmsproject98_final.RETWEETS.find({"USER_ID": user_id})
    df2 = pd.DataFrame(list(documents2))
    df3=pd.concat([df1, df2])
    st.dataframe(df3)        
    pipeline = [
        { "$match": {"USER_ID": user_id} },
        { "$group": {
            "_id": "$sentiment",
            "count": { "$sum": 1 }
        }}
    ]
    results1 = list(client.dbmsproject98_final.TWEETS.aggregate(pipeline))
    print(results1)
    sentiment_counts = {
        "Positive": 0,
        "Negative": 0,
        "Neutral": 0
    }

    # Update counts from results
    for result in results1:
        if result["_id"] in sentiment_counts:
            sentiment_counts[result["_id"]] = result["count"]

    # Ensure the order: positive, negative, neutral
    ordered_counts1 = [sentiment_counts["Positive"], sentiment_counts["Negative"], sentiment_counts["Neutral"]]
    print(ordered_counts1)
    results2=list(client.dbmsproject98_final.RETWEETS.aggregate(pipeline))
    sentiment_counts = {
        "Positive": 0,
        "Negative": 0,
        "Neutral": 0
    }

    # Update counts from results
    for result in results2:
        if result["_id"] in sentiment_counts:
            sentiment_counts[result["_id"]] = result["count"]
    # Ensure the order: positive, negative, neutral
    ordered_counts2 = [sentiment_counts["Positive"], sentiment_counts["Negative"], sentiment_counts["Neutral"]]
    print(ordered_counts2)
    pie_data = {
        "Categories": ["Positive", "Negative", "Neutral"],
        "Values": [x + y for x, y in zip(ordered_counts1, ordered_counts2)]
    }
#### FOR EMOTIONS

    pipeline = [
        { "$match": {"USER_ID": user_id} },
        { "$group": {
            "_id": "$emotion",
            "count": { "$sum": 1 }
        }}
    ]
    results1 = list(client.dbmsproject98_final.TWEETS.aggregate(pipeline))
    print(results1)
    emo_counts = {
        "joy": 0,
        "anger": 0,
        "sadness": 0,
        "fear": 0,
        "surprise": 0,
        "love": 0
    }

    # Update counts from results
    for result in results1:
        if result["_id"] in emo_counts:
            emo_counts[result["_id"]] = result["count"]

    # Ensure the order: positive, negative, neutral
    ordered_counts1 = [emo_counts["joy"], emo_counts["anger"], emo_counts["sadness"],
                       emo_counts["fear"], emo_counts["surprise"], emo_counts["love"]]
    print(ordered_counts1)
    results2=list(client.dbmsproject98_final.RETWEETS.aggregate(pipeline))
    emo_counts = {
        "joy": 0,
        "anger": 0,
        "sadness": 0,
        "fear": 0,
        "surprise": 0,
        "love": 0
    }

    # Update counts from results
    for result in results2:
        if result["_id"] in emo_counts:
            emo_counts[result["_id"]] = result["count"]
    # Ensure the order: positive, negative, neutral
    ordered_counts2 = [emo_counts["joy"], emo_counts["anger"], emo_counts["sadness"],
                       emo_counts["fear"], emo_counts["surprise"], emo_counts["love"]]
    print(ordered_counts2)
    # pie_data = {
    #     "Categories": ["Positive", "Negative", "Neutral"],
    #     "Values": [x + y for x, y in zip(ordered_counts1, ordered_counts2)]
    # }
    
    xax=list(emo_counts.keys())
    yax=[x + y for x, y in zip(ordered_counts1, ordered_counts2)]
    fig1 = go.Figure(go.Bar(
        x=xax,
        y=yax
         # Using a color scale based on sales
    ))

    # Add layout customization
    fig1.update_layout(
        title='Tweet Emotions',
        xaxis_title='Count',
        yaxis_title='Emotion',
        plot_bgcolor='rgba(0,0,0,0)', # Transparent background
    )

    # Create pie chart
    fig_pie = px.pie(
        names=pie_data['Categories'],
        values=pie_data['Values'],
        title='Sentiment Distribution of the User'
    )

    # Layout: display plots side by side
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.plotly_chart(fig1, use_container_width=True)    
    
    yax=['Followers','Friends','Favorites','Status']
    xax=[df_user['followers_count'][0],df_user['friends_count'][0],df_user['favourites_count'][0],df_user['statuses_count'][0]]
    fig = go.Figure(go.Bar(
        x=xax,
        y=yax,
        orientation='h',
         # Using a color scale based on sales
    ))

    # Add layout customization
    fig.update_layout(
        title='User Details By Number',
        xaxis_title='Count',
        yaxis_title='Category',
        yaxis=dict(autorange="reversed"), # This line ensures the regions are displayed top to bottom
        plot_bgcolor='rgba(0,0,0,0)', # Transparent background
    )

    # Show the plot
    st.plotly_chart(fig)

    xax=['Tweets','Retweets']
    yax=[count_tweet,count_retweet]
    fig = go.Figure(go.Bar(
        x=xax,
        y=yax
         # Using a color scale based on sales
    ))

    # Add layout customization
    fig.update_layout(
        title='Tweets and Retweets',
        xaxis_title='Tweet Type',
        yaxis_title='Number of Tweets',
        yaxis=dict(autorange="reversed"), # This line ensures the regions are displayed top to bottom
        plot_bgcolor='rgba(0,0,0,0)', # Transparent background
    )

    # Show the plot
    st.plotly_chart(fig)