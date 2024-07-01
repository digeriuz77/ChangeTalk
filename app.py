import streamlit as st
from openai import OpenAI
import time
import json
import joblib
from datetime import datetime
import random
import os
from data_manager import DataManager
from oars_analyzer import OARSAnalyzer
from visualization import visualize_change_talk, visualize_sentiment

# Import stage-specific functions
from agenda import set_agenda
from typical_day import describe_typical_day
from decision_balance import create_decision_balance
from build_confidence import build_confidence
from explore_options import explore_options
from key_question import ask_key_question
from plan_agreement import create_plan
from summarize import summarize_conversation

# Stage functions dictionary
stage_functions = {
    1: set_agenda,
    2: describe_typical_day,
    3: create_decision_balance,
    4: build_confidence,
    5: explore_options,
    6: ask_key_question,
    7: create_plan,
    8: summarize_conversation
}

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
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = f'chat_{int(time.time())}'
    if "change_talk_scores" not in st.session_state:
        st.session_state.change_talk_scores = []
    if "sentiment_scores" not in st.session_state:
        st.session_state.sentiment_scores = []
    if "show_analysis" not in st.session_state:
        st.session_state.show_analysis = False
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = 1

initialize_session_state()

# Initialize OpenAI client, DataManager, and OARSAnalyzer
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
data_manager = DataManager()
oars_analyzer = OARSAnalyzer()

def create_thread_if_not_exists():
    if not st.session_state.thread_id:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

def add_message_to_thread(content):
    create_thread_if_not_exists()
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=f"Current stage: {st.session_state.current_stage}\n\n{content}"
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
    st.session_state.change_talk_scores = []
    st.session_state.sentiment_scores = []
    st.session_state.conversation_id = f'chat_{int(time.time())}'
    st.session_state.current_stage = 1
    data_manager.start_conversation(st.session_state.conversation_id)
    st.experimental_rerun()

def save_chat():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"chat_history_{timestamp}.joblib"
    data = {
        "chat_history": st.session_state.chat_history,
        "change_talk_scores": st.session_state.change_talk_scores,
        "sentiment_scores": st.session_state.sentiment_scores,
        "conversation_id": st.session_state.conversation_id,
        "current_stage": st.session_state.current_stage
    }
    joblib.dump(data, filename)
    st.success(f"Chat history saved as {filename}")

def load_chat(filename):
    data = joblib.load(filename)
    st.session_state.chat_history = data["chat_history"]
    st.session_state.change_talk_scores = data["change_talk_scores"]
    st.session_state.sentiment_scores = data["sentiment_scores"]
    st.session_state.conversation_id = data["conversation_id"]
    st.session_state.current_stage = data.get("current_stage", 1)
    st.session_state.welcome_message_displayed = True
    st.experimental_rerun()

def get_saved_chats():
    return [f for f in os.listdir(".") if f.startswith("chat_history_") and f.endswith(".joblib")]

def export_chat():
    chat_data = {
        "conversation_id": st.session_state.conversation_id,
        "messages": st.session_state.chat_history,
        "change_talk_scores": st.session_state.change_talk_scores,
        "sentiment_scores": st.session_state.sentiment_scores,
        "current_stage": st.session_state.current_stage
    }
    return json.dumps(chat_data, indent=2)

def calculate_change_talk_score(analysis):
    return (analysis['change_talk_score'] + analysis['sentiment']) / 2

def update_assistant_prompt():
    system_message = """
    You are an expert motivational interviewing (MI) coach. Guide users through exploring and resolving their ambivalence about behavior change. Use OARS techniques and maintain a compassionate, non-judgmental tone.

    Use these signals to communicate with the app:
    🔄 : Move to the next conversation step
    📊 : Request the current change talk score
    📝 : Request a conversation summary
    🏁 : End the conversation

    Guide the conversation through these stages:
    1. Setting the agenda
    2. Exploring a typical day
    3. Creating a decision balance
    4. Building confidence
    5. Exploring options
    6. Asking key questions
    7. Creating a change plan
    8. Summarizing the conversation

    Use the 🔄 signal when you're ready to move to the next stage. Adapt your approach based on the user's readiness for change, which you can gauge by requesting the change talk score with 📊.

    Remember, your goal is to help the user explore their own motivations for change, not to persuade or convince them.
    """
    client.beta.assistants.update(
        assistant_id=st.session_state.current_assistant_id,
        instructions=system_message
    )

welcome_messages = [
    "Hi there! I'm a coach specializing in motivational interviewing. What change are you considering?",
    "Hello! I'm here to guide you through the process of change. What would you like to focus on today?",
    "Welcome! As a motivational interviewing coach, I'm here to support you. What change are you thinking about making?"
]

def parse_assistant_response(response):
    signals = {
        "next_step": "🔄" in response,
        "request_score": "📊" in response,
        "request_summary": "📝" in response,
        "end_conversation": "🏁" in response
    }
    return signals, response

def main():
    st.title("Motivational Interviewing Chatbot")

    # Create containers for chat, controls, and analysis
    chat_container = st.container()
    controls_container = st.container()
    analysis_container = st.container()

    with chat_container:
        st.subheader("Chat")

        # Display a random welcome message if chat history is empty
        if not st.session_state.get('welcome_message_displayed', False):
            welcome_message = random.choice(welcome_messages)
            st.session_state.chat_history.append({"role": "assistant", "content": welcome_message})
            st.session_state.welcome_message_displayed = True
            data_manager.start_conversation(st.session_state.conversation_id)
            data_manager.add_message(st.session_state.conversation_id, "assistant", welcome_message)

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_input = st.chat_input("Type your message...", key="user_input")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            data_manager.add_message(st.session_state.conversation_id, "user", user_input)
            add_message_to_thread(user_input)

            # Analyze user input
            analysis = oars_analyzer.analyze_input(user_input, st.session_state.chat_history)
            st.session_state.change_talk_scores.append(analysis['change_talk_score'])
            st.session_state.sentiment_scores.append(analysis['sentiment'])

            with st.spinner("Thinking..."):
                assistant_response = run_assistant()

            if assistant_response:
                signals, cleaned_response = parse_assistant_response(assistant_response)
                st.session_state.chat_history.append({"role": "assistant", "content": cleaned_response})
                data_manager.add_message(st.session_state.conversation_id, "assistant", cleaned_response)

                if signals["next_step"] and st.session_state.current_stage <= 8:
                    try:
                        result = stage_functions[st.session_state.current_stage]()
                        if result:
                            add_message_to_thread(f"Stage {st.session_state.current_stage} result: {result}")
                            st.session_state.current_stage += 1
                    except Exception as e:
                        st.error(f"Error in stage {st.session_state.current_stage}: {str(e)}")
                        add_message_to_thread(f"Error occurred in stage {st.session_state.current_stage}. Please try again or move to the next stage.")

                if signals["request_score"]:
                    score = calculate_change_talk_score(analysis)
                    add_message_to_thread(f"Current change talk score: {score}")

                if signals["request_summary"]:
                    summary = summarize_conversation(st.session_state.chat_history)
                    add_message_to_thread(f"Conversation summary: {summary}")

                if signals["end_conversation"]:
                    st.success("Conversation ended. Thank you for participating!")
                    reset_chat()

            st.experimental_rerun()

    with controls_container:
        # Buttons for functionality in a row
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            if st.button("Start Over"):
                reset_chat()
        with col2:
            if st.button("Save Chat"):
                save_chat()
        with col3:
            saved_chats = get_saved_chats()
            if saved_chats:
                selected_chat = st.selectbox("Load Chat", saved_chats)
                if st.button("Load"):
                    load_chat(selected_chat)
        with col4:
            if st.button("Summarize"):
                st.session_state.current_assistant_id = "asst_2IN1dkowoziRpYyzSdgJbPZY"
                chat_log = " ".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
                add_message_to_thread(f"Please summarize the following chat log:\n{chat_log}")
                summary = run_assistant()
                if summary:
                    st.session_state.chat_history.append({"role": "assistant", "content": summary})
                    data_manager.add_message(st.session_state.conversation_id, "assistant", summary)
                st.session_state.current_assistant_id = "asst_RAJ5HUmKrqKXAoBDhacjvMy8"  # Reset to main assistant
                st.experimental_rerun()
        with col5:
            if st.button("Toggle Analysis"):
                st.session_state.show_analysis = not st.session_state.show_analysis
                st.experimental_rerun()
        with col6:
            chat_json = export_chat()
            st.download_button(
                label="Export Chat",
                data=chat_json,
                file_name=f"chat_export_{st.session_state.conversation_id}.json",
                mime="application/json"
            )

    with analysis_container:
        if st.session_state.show_analysis:
            st.subheader("Conversation Analysis")
            col1, col2 = st.columns(2)
            with col1:
                visualize_change_talk(st.session_state.change_talk_scores)
            with col2:
                visualize_sentiment(st.session_state.sentiment_scores)

if __name__ == "__main__":
    update_assistant_prompt()
    main()
