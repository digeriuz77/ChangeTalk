import streamlit as st
from openai import OpenAI
import time
import random
import json
from azure.storage.blob import BlobServiceClient
from nltk.sentiment import SentimentIntensityAnalyzer
import os
from datetime import datetime

# Import custom modules
from oars_analyzer import OARSAnalyzer
from change_talk_score_calculator import calculate_change_talk_score
from ui_components import display_progress_bar, display_change_talk_score
from visualization import visualize_change_talk, visualize_sentiment
# from data_manager import DataManager

# Streamlit configuration
st.set_page_config(page_title="Motivational Interviewing Chatbot", layout="wide")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "change_talk_scores" not in st.session_state:
    st.session_state.change_talk_scores = []
if "sentiment_scores" not in st.session_state:
    st.session_state.sentiment_scores = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(random.randint(1000, 9999))
if "welcomed" not in st.session_state:
    st.session_state.welcomed = False

# Assistant ID
ASSISTANT_ID = "asst_RAJ5HUmKrqKXAoBDhacjvMy8"

# Initialize OARSAnalyzer
oars_analyzer = OARSAnalyzer()

# Initialize DataManager
# data_manager = DataManager()

# Welcome messages
welcome_messages = [
    "Hi there! I'm a coach specializing in motivational interviewing. What change are you considering?",
    "Hello! I'm here to guide you through the process of change. What would you like to focus on today?",
    "Welcome! As a motivational interviewing coach, I'm here to support you. What change are you thinking about making?"
]

def create_thread_if_not_exists():
    if not st.session_state.thread_id:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

def add_message_to_thread(content):
    create_thread_if_not_exists()
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=content
    )

def run_assistant():
    create_thread_if_not_exists()
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID
    )
    
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
        if run_status.status == 'completed':
            break
        elif run_status.status == 'failed':
            st.error(f"Run failed: {run_status.last_error}")
            return None
        time.sleep(1)
    
    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )
    
    return messages.data[0].content[0].text.value

def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)['compound']

def upload_chat_log_to_azure(chat_history, conversation_id):
    try:
        connection_string = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = st.secrets["AZURE_CONTAINER_NAME"]
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"chat_log_{conversation_id}.json")
        
        chat_json = json.dumps(chat_history)
        blob_client.upload_blob(chat_json, overwrite=True)
        return True
    except Exception as e:
        st.error(f"Error uploading to Azure: {str(e)}")
        return False

def save_chat():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"chat_history_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(st.session_state.chat_history, f)
    st.success(f"Chat history saved as {filename}")

def get_saved_chats():
    return [f for f in os.listdir(".") if f.startswith("chat_history_") and f.endswith(".json")]

def load_chat(filename):
    with open(filename, "r") as f:
        st.session_state.chat_history = json.load(f)
    st.session_state.welcomed = True
    st.experimental_rerun()

def reset_conversation():
    st.session_state.chat_history = []
    st.session_state.change_talk_scores = []
    st.session_state.sentiment_scores = []
    st.session_state.current_step = 0
    st.session_state.welcomed = False
    st.session_state.conversation_id = str(random.randint(1000, 9999))
    st.session_state.thread_id = None
    # data_manager.start_conversation(st.session_state.conversation_id)

def main():
    st.title("Motivational Interviewing Chatbot")

    if not st.session_state.welcomed:
        welcome_message = random.choice(welcome_messages)
        st.session_state.chat_history.append({"role": "assistant", "content": welcome_message})
        st.session_state.welcomed = True

    # Single text input for user messages
    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        # data_manager.add_message(st.session_state.conversation_id, "user", user_input)
        add_message_to_thread(user_input)
        
        # Analyze user input
        analysis = oars_analyzer.analyze_input(user_input, st.session_state.chat_history)
        change_talk_score = calculate_change_talk_score(analysis)
        st.session_state.change_talk_scores.append(change_talk_score)
        st.session_state.sentiment_scores.append(analysis['sentiment'])
        
        with st.spinner("Thinking..."):
            assistant_response = run_assistant()
        
        if assistant_response:
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
            # data_manager.add_message(st.session_state.conversation_id, "assistant", assistant_response)
        
        st.experimental_rerun()

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Display progress and scores
    display_progress_bar(st.session_state.current_step, 8)  # Assuming 8 steps in total
    display_change_talk_score(st.session_state.change_talk_scores)
    visualize_change_talk(st.session_state.change_talk_scores)
    visualize_sentiment(st.session_state.sentiment_scores)

    # Buttons for additional functionality
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Summarize"):
            summary = run_assistant()  # Implement summarization logic
            if summary:
                st.session_state.chat_history.append({"role": "assistant", "content": summary})
                st.experimental_rerun()
    with col2:
        if st.button("Save Chat"):
            save_chat()
    with col3:
        if st.button("End Conversation and Upload"):
            if upload_chat_log_to_azure(st.session_state.chat_history, st.session_state.conversation_id):
                # data_manager.end_conversation(st.session_state.conversation_id)
                st.success("Chat log uploaded to Azure Storage!")
                reset_conversation()
    with col4:
        if st.button("Download Chat"):
            chat_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
            st.download_button(
                label="Download Chat Log",
                data=chat_text,
                file_name=f"chat_log_{st.session_state.conversation_id}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
