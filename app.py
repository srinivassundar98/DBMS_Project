from libraries import *
from utils import *
from connections import *
from summary_analysis import *
from tweet_analyzer import *
from hashtag_analyzer import *
from user_analyzer import *
from auth import *
from logging_app import *

# MySQL Connection parameters

# Check user credentials function
def main():
    # Inject custom CSS for sidebar and button aesthetics
    st.markdown("""
        <style>
            /* Custom sidebar style */
            .css-1d391kg, .css-1lcbmhc {
                background-color: #1e3d58; /* Bluish-black background */
                color: #ffffff;
            }
            /* Custom styling for the main content area */
            .css-1kyxreq {
                background-color: #ffffff;
                padding: 20px 40px;
                border-radius: 10px;
            }
            /* Input field styling */
            .stTextInput > div > div > input {
                width: 100%;
                padding: 10px;
                border: 1px solid #007BFF;
                border-radius: 5px;
            }
            /* Button styling */
            .stButton > button {
                width: 100%;
                border: none;
                color: white;
                padding: 10px 20px;
                background-color: #007BFF;
                border-radius: 5px;
            }
        </style>
        """, unsafe_allow_html=True)

    # Sidebar navigation
    with st.sidebar:
        st.image("logo.png", width=100)  # Optional: add your logo here
        if 'logged_in' in st.session_state and st.session_state['logged_in']:
            selected = st.radio("Navigation", ["Overview","User Analysis", "Hashtag Analysis", "Tweet Analysis"])
            logging.info(f"Navigation: {selected}")
        else:
            selected = "Login"

    # Handle login and page display
    if selected == "Login":
        login_user()
    elif 'logged_in' in st.session_state and st.session_state['logged_in']:
        if selected == "Overview":
            st.header("Summary of Dataset")
            start_date,end_date,min_date2,max_date2 = get_date()
            st.slider(
                "Select a date range",
                min_value=start_date,
                max_value=end_date,
                value=(start_date, end_date),
                format="YYYY-MM-DD"
            )
            overview()
            logging.info(f"Date Range Selected: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        elif selected == "User Analysis":
            st.header("User Based Analysis")
            start_date,end_date,min_date2,max_date2 = get_date("user")
            st.slider(
                "Select a date range",
                min_value=start_date,
                max_value=end_date,
                value=(start_date, end_date),
                format="YYYY-MM-DD"
            )
            #st.write(f"You selected: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            logging.info(f"Date Range Selected: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            user_analysis(min_date2,max_date2)
            st.write("Details of user-based analysis here.")
        elif selected == "Hashtag Analysis":
            st.header("Hashtag Based Analysis")
            start_date,end_date,min_date2,max_date2 = get_date()
            st.slider(
                "Select a date range",
                min_value=start_date,
                max_value=end_date,
                value=(start_date, end_date),
                format="YYYY-MM-DD"
            )
            #st.write(f"You selected: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            logging.info(f"Date Range Selected: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            hashtag_analysis()
            st.write("Details of hashtag-based analysis here.")

        elif selected == "Tweet Analysis":
            st.header("Tweet Based Analysis")
            start_date,end_date,min_date2,max_date2 = get_date()
            st.slider(
                "Select a date range",
                min_value=start_date,
                max_value=end_date,
                value=(start_date, end_date),
                format="YYYY-MM-DD"
            )
            tweet_analysis()
            logging.info(f"Date Range Selected: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            st.write("Details of tweet ID-based analysis here.")

def login_user():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if check_user(username, password):
                st.session_state['logged_in'] = True 
                st.session_state['username'] = username
                setup_logging(username)  
                logging.info(f"User Name: {username}")
                st.experimental_rerun()  
            else:
                st.error("Incorrect username or password")

if __name__ == "__main__":
    main()