import streamlit as st
from openai import OpenAI
from azure.storage.blob import BlobServiceClient
import json
import uuid
from datetime import datetime

# Import custom modules
from oars_analyzer import OARSAnalyzer
from change_talk_score_calculator import calculate_change_talk_score
from openai_system_message_generator import get_openai_messages
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

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "change_talk_scores" not in st.session_state:
    st.session_state.change_talk_scores = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize OARSAnalyzer
oars_analyzer = OARSAnalyzer()

def upload_chat_log_to_azure(chat_history, conversation_id):
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={st.secrets.azure.storage_account_name};AccountKey={st.secrets.azure.storage_account_key}"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=st.secrets.azure.container_name, blob=f"chat_log_{conversation_id}.json")
    
    # Convert chat history to JSON string
    chat_json = json.dumps(chat_history)
    
    # Upload JSON string as blob
    blob_client.upload_blob(chat_json, overwrite=True)

@st.cache_data
def display_chat_history():
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def main():
    st.title("Motivational Interviewing Chatbot")

    display_chat_history()

    conversation_steps = [
        set_agenda,
        describe_typical_day,
        create_decision_balance,
        build_confidence,
        explore_options,
        ask_key_question,
        create_plan,
        summarize_conversation
    ]

    if st.session_state.current_step < len(conversation_steps):
        result = conversation_steps[st.session_state.current_step]()
        if result:
            st.session_state.current_step += 1
            st.experimental_rerun()
    else:
        handle_open_conversation()

    # Display change talk score
    if st.session_state.change_talk_scores:
        st.line_chart(st.session_state.change_talk_scores)
        st.write(f"Current Change Talk Score: {st.session_state.change_talk_scores[-1]:.2f}")

    # Add a button to end conversation and upload chat log
    if st.button("End Conversation and Upload"):
        upload_chat_log_to_azure(st.session_state.chat_history, st.session_state.conversation_id)
        st.success("Chat log uploaded to Azure Storage!")
        # Reset conversation
        st.session_state.chat_history = []
        st.session_state.change_talk_scores = []
        st.session_state.current_step = 0
        st.session_state.conversation_id = str(uuid.uuid4())
        st.experimental_rerun()

def handle_open_conversation():
    user_input = st.chat_input("Type your message here...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Analyze user input
        analysis = oars_analyzer.analyze_input(user_input, st.session_state.chat_history)
        
        # Calculate change talk score
        change_talk_score = calculate_change_talk_score(analysis)
        st.session_state.change_talk_scores.append(change_talk_score)
        
        # Generate OpenAI messages
        messages = get_openai_messages(st.session_state.chat_history, change_talk_score)
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        assistant_response = response.choices[0].message.content
        
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        st.experimental_rerun()

if __name__ == "__main__":
    main()
