import streamlit as st
from openai import OpenAI
import time
import joblib
import os
from datetime import datetime

from oars_analyzer import OARSAnalyzer
from change_talk_score_calculator import calculate_change_talk_score
from data_manager import DataManager
from ui_components import (
    display_progress_bar, display_chat_history, display_change_talk_score,
    display_confidence_slider, display_download_button
)
from visualization import visualize_change_talk, visualize_sentiment

# Streamlit configuration
st.set_page_config(page_title="Motivational Interviewing Chatbot", layout="wide")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Constants
AI_AVATAR_ICON = '✨'
ASSISTANT_ID = "asst_RAJ5HUmKrqKXAoBDhacjvMy8"

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "change_talk_scores" not in st.session_state:
    st.session_state.change_talk_scores = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = f'chat_{int(time.time())}'

# Initialize OARSAnalyzer and DataManager
oars_analyzer = OARSAnalyzer()
data_manager = DataManager()

def save_chat_history(chat_id, messages):
    os.makedirs('data', exist_ok=True)
    joblib.dump(messages, f'data/{chat_id}_messages.joblib')

def load_chat_history(chat_id):
    try:
        return joblib.load(f'data/{chat_id}_messages.joblib')
    except:
        return []

def stream_openai_response(response):
    message_placeholder = st.empty()
    full_response = ''
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            message_placeholder.markdown(full_response + '▌')
    message_placeholder.markdown(full_response)
    return full_response

def run_assistant(user_input):
    messages = [{"role": "user", "content": user_input}]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )
    return stream_openai_response(response)

def handle_assistant_response(response):
    if '🔄' in response:
        st.session_state.current_step += 1
        return response.replace('🔄', '')
    elif '📊' in response:
        score = st.session_state.change_talk_scores[-1] if st.session_state.change_talk_scores else 0
        return f"The current change talk score is {score:.2f}"
    elif '📝' in response:
        return summarize_conversation()
    elif '🏁' in response:
        end_conversation()
        return "Conversation ended. Thank you for participating."
    return response

def summarize_conversation():
    # Implement conversation summarization logic here
    return "Conversation summary..."

def end_conversation():
    data_manager.end_conversation(st.session_state.conversation_id)
    save_chat_history(st.session_state.conversation_id, st.session_state.chat_history)

def main():
    st.title("Motivational Interviewing Chatbot")

    # Sidebar for additional controls and information
    with st.sidebar:
        st.subheader("Conversation Progress")
        display_progress_bar(st.session_state.current_step, 8)
        
        st.subheader("Change Talk Score")
        display_change_talk_score(st.session_state.change_talk_scores)
        
        confidence = display_confidence_slider()
        st.write(f"Your confidence level: {confidence}")
        
        if st.button("End Conversation"):
            end_conversation()
            st.success("Conversation ended and data saved.")
            st.experimental_rerun()

    # Main chat area
    chat_container = st.container()
    with chat_container:
        display_chat_history(st.session_state.chat_history)

    # User input area
    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        data_manager.add_message(st.session_state.conversation_id, "user", user_input)
        
        analysis = oars_analyzer.analyze_input(user_input)
        change_talk_score = calculate_change_talk_score(analysis)
        st.session_state.change_talk_scores.append(change_talk_score)
        
        with st.chat_message("assistant", avatar=AI_AVATAR_ICON):
            assistant_response = run_assistant(user_input)
        
        processed_response = handle_assistant_response(assistant_response)
        
        st.session_state.chat_history.append({"role": "assistant", "content": processed_response})
        data_manager.add_message(st.session_state.conversation_id, "assistant", processed_response)
        
        save_chat_history(st.session_state.conversation_id, st.session_state.chat_history)
        
        st.experimental_rerun()

    # Visualizations and download button (below chat input)
    st.subheader("Conversation Analysis")
    col1, col2 = st.columns(2)
    with col1:
        visualize_change_talk(st.session_state.change_talk_scores)
    with col2:
        visualize_sentiment([msg.get('sentiment', 0) for msg in st.session_state.chat_history if msg['role'] == 'user'])

    plan_summary = summarize_conversation()
    display_download_button(plan_summary)

if __name__ == "__main__":
    main()
