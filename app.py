import streamlit as st
import pyodbc
import pandas as pd
from ollama import Client
import time

# Initialize Ollama client
client = Client()

# SQL Server connection parameters
server = r'localhost\SQLEXPRESS'
database = 'temp_db'
trusted_connection = 'yes'

# Function to execute SQL queries
def execute_query(query):
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};TRUSTED_CONNECTION={trusted_connection};'
    conn = pyodbc.connect(conn_str)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Set page configuration
st.set_page_config(page_title="SQL Server ChatGPT Clone", page_icon="🤖", layout="wide")

# Custom CSS for better appearance
st.markdown("""
<style>
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    .stButton > button {
        width: 100%;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #2b313e;
    }
    .chat-message.bot {
        background-color: #475063;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .message {
        width: 80%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat header
st.header("🤖 SQL Server ChatGPT Clone")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("Ask a question about your SQL Server database...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Generate bot response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prepare the prompt for the AI
        prompt = f"""You are an AI assistant that helps with SQL queries and database information. 
        The user is asking about a SQL Server database. Here's the user's question: 
        {user_input}
        
        If the user is asking for data or information that requires a SQL query, 
        provide the SQL query to retrieve that information. If not, provide a helpful response.
        
        Remember:
        1. The database name is 'temp_db'.
        2. Only use SQL Server compatible syntax.
        3. If you generate a SQL query, wrap it in triple backticks with 'sql' after the opening backticks.
        """

        # Stream the response
        for response in client.chat(model='llama3.1:latest', messages=[{"role": "user", "content": prompt}], stream=True):
            full_response += response['message']['content']
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.01)
        
        message_placeholder.markdown(full_response)

        # Check if the response contains a SQL query
        if "```sql" in full_response:
            sql_query = full_response.split("```sql")[1].split("```")[0].strip()
            try:
                result_df = execute_query(sql_query)
                st.write("Query result:")
                st.dataframe(result_df)
            except Exception as e:
                st.error(f"Error executing SQL query: {str(e)}")
    
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add a button to clear chat history
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.experimental_rerun()