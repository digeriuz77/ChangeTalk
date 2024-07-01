import streamlit as st
from openai import OpenAI
import time
import json
from datetime import datetime
import random

# Initialize session state
def initialize_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "current_assistant_id" not in st.session_state:
        st.session_state.current_assistant_id = "asst_RAJ5HUmKrqKXAoBDhacjvMy8"
    if "welcome_message_displayed" not in st.session_state:
        st.session_state.welcome_message_displayed = False

initialize_session_state()

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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
        assistant_id=st.session_state.current_assistant_id
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

def reset_chat():
    st.session_state.chat_history = []
    st.session_state.welcome_message_displayed = False
    st.session_state.thread_id = None
    st.experimental_rerun()

def save_chat():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"chat_history_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(st.session_state.chat_history, f)
    st.success(f"Chat history saved as {filename}")

welcome_messages = [
    "Hi there! I'm a coach specializing in motivational interviewing. What change are you considering?",
    "Hello! I'm here to guide you through the process of change. What would you like to focus on today?",
    "Welcome! As a motivational interviewing coach, I'm here to support you. What change are you thinking about making?"
]

def main():
    st.title("Motivational Interviewing Chatbot")

    # Create a container for chat and controls
    chat_container = st.container()
    controls_container = st.container()

    with chat_container:
        st.subheader("Chat")

        # Display a random welcome message if chat history is empty
        if not st.session_state.get('welcome_message_displayed', False):
            welcome_message = random.choice(welcome_messages)
            st.session_state.chat_history.append({"role": "assistant", "content": welcome_message})
            st.session_state.welcome_message_displayed = True

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_input = st.chat_input("Type your message...", key="user_input")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            add_message_to_thread(user_input)

            with st.spinner("Thinking..."):
                assistant_response = run_assistant()

            if assistant_response:
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

            st.experimental_rerun()

    with controls_container:
        # Buttons for functionality in a row
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Start Over"):
                reset_chat()
        with col2:
            if st.button("Save Chat"):
                save_chat()
        with col3:
            if st.button("Summarize"):
                st.session_state.current_assistant_id = "asst_2IN1dkowoziRpYyzSdgJbPZY"
                chat_log = " ".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
                add_message_to_thread(f"Please summarize the following chat log:\n{chat_log}")
                summary = run_assistant()
                if summary:
                    st.session_state.chat_history.append({"role": "assistant", "content": summary})
                st.session_state.current_assistant_id = "asst_RAJ5HUmKrqKXAoBDhacjvMy8"  # Reset to main assistant
                st.experimental_rerun()

if __name__ == "__main__":
    main()
