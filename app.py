import streamlit as st
from openai import OpenAI
from azure.storage.blob import BlobServiceClient
import json
import uuid

from oars_analyzer import OARSAnalyzer

# Streamlit configuration
st.set_page_config(page_title="Motivational Interviewing Chatbot", layout="wide")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "change_talk_scores" not in st.session_state:
    st.session_state.change_talk_scores = []
if "sentiment_scores" not in st.session_state:
    st.session_state.sentiment_scores = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize OARSAnalyzer
oars_analyzer = OARSAnalyzer()

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

def get_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting AI response: {str(e)}")
        return None

def main():
    st.title("Motivational Interviewing Chatbot")

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input
    user_input = st.chat_input("Type your message here...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Analyze user input
        analysis = oars_analyzer.analyze_input(user_input, st.session_state.chat_history)
        sentiment = analysis['sentiment']
        change_talk_score = analysis['change_talk_score']
        st.session_state.change_talk_scores.append(change_talk_score)
        st.session_state.sentiment_scores.append(sentiment)
        
        # Prepare messages for AI
        messages = [
            {"role": "system", "content": "You are a motivational interviewing expert. Respond to the user's input."},
            *st.session_state.chat_history
        ]

        # Get AI response
        ai_response = get_ai_response(messages)
        if ai_response:
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.experimental_rerun()

    # Display scores
    if st.session_state.change_talk_scores:
        st.line_chart({
            "Change Talk Score": st.session_state.change_talk_scores,
            "Sentiment": st.session_state.sentiment_scores
        })
        st.write(f"Current Change Talk Score: {st.session_state.change_talk_scores[-1]:.2f}")
        st.write(f"Current Sentiment: {st.session_state.sentiment_scores[-1]:.2f}")

    # End conversation and upload chat log
    if st.button("End Conversation and Upload"):
        if upload_chat_log_to_azure(st.session_state.chat_history, st.session_state.conversation_id):
            st.success("Chat log uploaded to Azure Storage!")
            # Reset conversation
            st.session_state.chat_history = []
            st.session_state.change_talk_scores = []
            st.session_state.sentiment_scores = []
            st.session_state.conversation_id = str(uuid.uuid4())
            st.experimental_rerun()
        else:
            st.error("Failed to upload chat log. Please try again.")

if __name__ == "__main__":
    main()
