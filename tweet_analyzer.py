from libraries import *
from connections import *
from utils import *

client=mongodb_conn()
def tweet_analysis():
    user_input = st.text_input("Search for:")
    db = client['dbmsproject98_final']  # Replace with your database name
    collection = db['TWEETS']  # Replace with your collection name
    escaped_input = re.escape(user_input)
# Function to perform the search and fetch results
    st.write(user_input)
    query = {
        'translated_text': {
            '$regex': escaped_input,
            '$options': 'i'  # Case-insensitive matching
        }
    }
    st.write(query)
    results = collection.find(query)
    df=pd.DataFrame(list(results))
    df.drop("ENTITIES_HASHTAGS",axis=1,inplace=True)
    st.write(df)

    df['date'] =df["CREATED_AT"].apply(lambda x:safe_convert_dates(x))
    df['date']=pd.to_datetime(df['date'].astype(str).apply(lambda x: x.split(' ')[0]))

    # Drop rows where dates could not be converted (NaT values)
    tweets_per_day = df.groupby('date').size().reset_index(name='count')

    fig = px.line(tweets_per_day, x='date', y='count', title='Number of Tweets Per Day', markers=True)

    # Display the chart in Streamlit
    st.plotly_chart(fig)
    fig_sentiment = px.pie(df, names='sentiment', title='Sentiment Distribution')
    st.plotly_chart(fig_sentiment)                    

    # Generate a bar chart for the Emotion column
    fig_emotion = px.bar(df['emotion'].value_counts().reset_index(), y='count', x='emotion', 
                        labels={'_id': 'Emotion', 'emotion': 'Count'}, title='Emotion Distribution')
    st.plotly_chart(fig_emotion)                    

    fig = px.pie(df, 
                names='LANG', 
                hole=0.4,  # This creates the donut chart effect by specifying the size of the hole in the middle
                title='Language Distribution')

    # Adjust the labels for clarity if needed
    fig.update_traces(textinfo='label+percent')

    # Display the chart in Streamlit
    st.plotly_chart(fig)