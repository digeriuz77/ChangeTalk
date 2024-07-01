import streamlit as st
from openai import OpenAI
import random
import json
from azure.storage.blob import BlobServiceClient

# Import custom modules
from oars_analyzer import OARSAnalyzer
from change_talk_score_calculator import calculate_change_talk_score
from openai_system_message_generator import get_openai_messages
#from data_manager import DataManager
from ui_components import (
    display_progress_bar, display_chat_history, display_change_talk_score,
    display_confidence_slider, display_download_button
)
from visualization import visualize_change_talk, visualize_sentiment, visualize_entities

# Import conversation steps
from agenda import set_agenda
from typical_day import describe_typical_day
from decision_balance import create_decision_balance
from build_confidence import build_confidence
from explore_options import explore_options
from key_question import ask_key_question
from plan_agreement import create_plan
from summarize import summarize_conversation

# Streamlit configuration
st.set_page_config(page_title="Motivational Interviewing Chatbot", layout="wide")

# Welcome messages
welcome_messages = [
    "Hi there! I'm a coach specializing in motivational interviewing. What change are you considering?",
    "Hello! I'm here to guide you through the process of change. What would you like to focus on today?",
    "Welcome! As a motivational interviewing coach, I'm here to support you. What change are you thinking about making?"
]

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
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

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Initialize OARSAnalyzer
oars_analyzer = OARSAnalyzer()

# Initialize DataManager
#data_manager = DataManager()

def upload_chat_log_to_azure(chat_history, conversation_id):
    connection_string = st.secrets["AZURE_STORAGE_CONNECTION_STRING"]
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_name = st.secrets["AZURE_CONTAINER_NAME"]
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"chat_log_{conversation_id}.json")
    
    chat_json = json.dumps(chat_history)
    blob_client.upload_blob(chat_json, overwrite=True)

def main():
    st.title("Motivational Interviewing Chatbot")

    if not st.session_state.welcomed:
        welcome_message = random.choice(welcome_messages)
        st.session_state.chat_history.append({"role": "assistant", "content": welcome_message})
        st.session_state.welcomed = True

    display_progress_bar(st.session_state.current_step, 9)  # 9 steps in total
    display_chat_history(st.session_state.chat_history)

    conversation_steps = [
        set_agenda,
        describe_typical_day,
        create_decision_balance,
        build_confidence,
        explore_options,
        summarize_conversation,
        ask_key_question,
        create_plan,
        summarize_conversation
    ]

    if st.session_state.current_step < len(conversation_steps):
        result = conversation_steps[st.session_state.current_step]()
        if result:
            if isinstance(result, tuple):
                st.session_state.chat_history.extend([
                    {"role": "user", "content": result[0]},
                    {"role": "assistant", "content": result[1]}
                ])
            else:
                st.session_state.chat_history.append({"role": "user", "content": result})
            
            st.session_state.current_step += 1
            st.experimental_rerun()
    else:
        handle_open_conversation()

    display_change_talk_score(st.session_state.change_talk_scores)
    visualize_change_talk(st.session_state.change_talk_scores)
    visualize_sentiment(st.session_state.sentiment_scores)

    if st.button("End Conversation and Upload"):
        upload_chat_log_to_azure(st.session_state.chat_history, st.session_state.conversation_id)
        data_manager.end_conversation(st.session_state.conversation_id)
        st.success("Chat log uploaded to Azure Storage!")
        reset_conversation()

    if st.button("Download Conversation"):
        chat_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
        st.download_button(
            label="Download Chat Log",
            data=chat_text,
            file_name=f"chat_log_{st.session_state.conversation_id}.txt",
            mime="text/plain"
        )

def handle_open_conversation():
    user_input = st.chat_input("Type your message here...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        data_manager.add_message(st.session_state.conversation_id, "user", user_input)
        
        analysis = oars_analyzer.analyze_input(user_input, st.session_state.chat_history)
        change_talk_score = calculate_change_talk_score(analysis)
        st.session_state.change_talk_scores.append(change_talk_score)
        st.session_state.sentiment_scores.append(analysis['sentiment'])
        
        messages = get_openai_messages(st.session_state.chat_history, st.session_state.user_profile, change_talk_score)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        assistant_response = response.choices[0].message.content
        
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        data_manager.add_message(st.session_state.conversation_id, "assistant", assistant_response)

        visualize_entities(analysis.get('entities', []))
        
        st.experimental_rerun()

def reset_conversation():
    st.session_state.chat_history = []
    st.session_state.change_talk_scores = []
    st.session_state.sentiment_scores = []
    st.session_state.current_step = 0
    st.session_state.welcomed = False
    st.session_state.conversation_id = str(random.randint(1000, 9999))
    data_manager.start_conversation(st.session_state.conversation_id)

if __name__ == "__main__":
    main()
