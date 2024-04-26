from libraries import *
from utils import *
from connections import *
from caching import *
from fetch import *
cache=SimpleFileCache()
client=mongodb_conn()
#engine=mysql_conn()
def hashtag_analysis():
    query="SELECT SCREEN_NAME,ENTITIES_HASHTAGS FROM TWEET_STORE_FINAL.USER_DETAILS;"
    df_hashtags=pd.DataFrame(fetch_with_cache(query,'mysql',cache))
    df_hashtags["ENTITIES_HASHTAGS"]=df_hashtags["ENTITIES_HASHTAGS"].apply(lambda x: ast.literal_eval(x))
    hashtags_2d=df_hashtags["ENTITIES_HASHTAGS"].values.tolist()
    hashtags=sorted(list(set([item for sublist in hashtags_2d for item in sublist])))
    selected_option = st.selectbox("Choose an option:", hashtags)
    df_filt=df_hashtags[df_hashtags['ENTITIES_HASHTAGS'].apply(lambda x: selected_option in x)]
    results = client.dbmsproject98_final.TWEETS.find({"ENTITIES_HASHTAGS": {'$regex': selected_option}})
    df=pd.DataFrame(list(results))
    df["ENTITIES_HASHTAGS"]=df["ENTITIES_HASHTAGS"].apply(lambda x: ast.literal_eval(x))
    filtered_df = df[df['ENTITIES_HASHTAGS'].apply(lambda x: selected_option in x)]
    term_counts = Counter(item for sublist in filtered_df["ENTITIES_HASHTAGS"].values.tolist() for item in sublist if item != selected_option)
    filtered_df['date'] =filtered_df["CREATED_AT"].apply(lambda x:safe_convert_dates(x))
    filtered_df['date']=pd.to_datetime(filtered_df['date'].astype(str).apply(lambda x: x.split(' ')[0]))

    # Drop rows where dates could not be converted (NaT values)
    tweets_per_day = filtered_df.groupby('date').size().reset_index(name='count')

    # Output the most common terms
    most_common_terms = term_counts.most_common()
    #print(most_common_terms)
    l1=[term for term, count in most_common_terms]
    l2=[count for term, count in most_common_terms]
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
                <h3>Hashtag Details</h3>
                <p>Hashtag: #{name}</p>
                <p>Total Times Used: {desc}</p>
                <p>Frequently Used With: {freq}</p>
                
            </div>
        """.format(name=selected_option,users_used=len(df_filt),desc=len(filtered_df),freq=str(l1[0:4])[1:-1]), unsafe_allow_html=True)
    fig = px.line(tweets_per_day, x='date', y='count', title='Number of Tweets Per Day', markers=True)

    # Display the chart in Streamlit
    st.plotly_chart(fig)
    fig_sentiment = px.pie(filtered_df, names='sentiment', title='Sentiment Distribution')

    # Generate a bar chart for the Emotion column
    fig_emotion = px.bar(filtered_df['emotion'].value_counts().reset_index(), y='count', x='emotion', 
                        labels={'_id': 'Emotion', 'emotion': 'Count'}, title='Emotion Distribution')

    # Use Streamlit to display the charts side by side
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_sentiment, use_container_width=True)
    with col2:
        st.plotly_chart(fig_emotion, use_container_width=True)    
    fig = go.Figure(data=[go.Bar(x=l1[0:10], y=l2[0:10])])

    # Update the layout
    fig.update_layout(title='Bar Graph of Labels and Values',
                    xaxis_title='Labels',
                    yaxis_title='Values')

    # Use Streamlit to display the chart
    st.plotly_chart(fig)

    fig = px.pie(filtered_df, 
                names='LANG', 
                hole=0.4,  # This creates the donut chart effect by specifying the size of the hole in the middle
                title='Language Distribution')

    # Adjust the labels for clarity if needed
    fig.update_traces(textinfo='label+percent')

    # Display the chart in Streamlit
    st.plotly_chart(fig)