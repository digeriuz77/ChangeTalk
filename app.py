import streamlit as st
from openai import OpenAI
from oars_analyzer import OARSAnalyzer
from change_talk_score_calculator import calculate_change_talk_score
from openai_system_message_generator import get_openai_messages

# Import custom modules
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
if "current_assistant_id" not in st.session_state:
    st.session_state.current_assistant_id = "your_assistant_id_here"
if "agenda_set" not in st.session_state:
    st.session_state.agenda_set = False
if "typical_day_described" not in st.session_state:
    st.session_state.typical_day_described = False
if "decision_balance_complete" not in st.session_state:
    st.session_state.decision_balance_complete = False
if "confidence_built" not in st.session_state:
    st.session_state.confidence_built = False
if "options_explored" not in st.session_state:
    st.session_state.options_explored = False
if "key_question_asked" not in st.session_state:
    st.session_state.key_question_asked = False
if "plan_created" not in st.session_state:
    st.session_state.plan_created = False
if "conversation_summarized" not in st.session_state:
    st.session_state.conversation_summarized = False
if "change_talk_scores" not in st.session_state:
    st.session_state.change_talk_scores = []

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize OARSAnalyzer
oars_analyzer = OARSAnalyzer()

def main():
    st.title("Motivational Interviewing Chatbot")
  # Chat interface
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
    if not st.session_state.agenda_set:
        selected_topics = set_agenda()
        if selected_topics:
            st.session_state.agenda_set = True
            st.session_state.selected_topics = selected_topics
            st.session_state.chat_history.append({"role": "assistant", "content": f"Great! We'll focus our conversation on: {', '.join(selected_topics)}. Let's explore your thoughts about these topics."})
            st.experimental_rerun()
    elif not st.session_state.typical_day_described:
        typical_day, weekend_difference = describe_typical_day(st.session_state.selected_topics)
        if typical_day:
            st.session_state.typical_day_described = True
            st.session_state.chat_history.append({"role": "user", "content": f"Typical day: {typical_day}\nWeekend differences: {weekend_difference}"})
            st.experimental_rerun()
    elif not st.session_state.decision_balance_complete:
        decision_balance_summary, completed = create_decision_balance()
        if completed:
            st.session_state.decision_balance_complete = True
            st.session_state.chat_history.append({"role": "system", "content": decision_balance_summary})
            st.experimental_rerun()
    elif not st.session_state.confidence_built:
        confidence_summary, confidence = build_confidence()
        if confidence_summary:
            st.session_state.confidence_built = True
            st.session_state.confidence = confidence
            st.session_state.chat_history.append({"role": "system", "content": confidence_summary})
            st.experimental_rerun()
    elif not st.session_state.options_explored:
        options_summary = explore_options()
        if options_summary:
            st.session_state.options_explored = True
            st.session_state.chat_history.append({"role": "system", "content": options_summary})
            st.experimental_rerun()
    elif not st.session_state.key_question_asked:
        question, response = ask_key_question()
        if question and response:
            st.session_state.key_question_asked = True
            st.session_state.chat_history.append({"role": "assistant", "content": question})
            st.session_state.chat_history.append({"role": "user", "content": response})
            st.experimental_rerun()
    elif not st.session_state.plan_created:
        plan_summary = create_plan()
        if plan_summary:
            st.session_state.plan_created = True
            st.session_state.chat_history.append({"role": "system", "content": plan_summary})
            st.experimental_rerun()
    elif not st.session_state.conversation_summarized:
        summary, additions = summarize_conversation(st.session_state.chat_history)
        if summary:
            st.session_state.conversation_summarized = True
            st.session_state.chat_history.append({"role": "assistant", "content": f"Summary: {summary}\nAdditions: {additions}"})
            st.experimental_rerun()
    else:
        # Chat interface
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # User input
        user_input = st.chat_input("Type your message here...")
        if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Analyze user input
        analysis = oars_analyzer.analyze_input(user_input, st.session_state.chat_history)
        
        # Generate response based on analysis
        response = generate_response(analysis)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.experimental_rerun()

    def generate_response(analysis):
    response = ""
    
    if analysis['change_talk']:
        response += analysis['reflection'] + " "
        response += analysis['affirmation'] + " "
    else:
        response += analysis['open_question'] + " "
    
    return response

    # Add a download button for the plan
    if st.session_state.plan_created:
        plan_summary = next((msg["content"] for msg in st.session_state.chat_history if msg["role"] == "system" and "Change Plan:" in msg["content"]), None)
        if plan_summary:
            st.download_button(
                label="Download Your Change Plan",
                data=plan_summary,
                file_name="change_plan.txt",
                mime="text/plain"
            )
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

if __name__ == "__main__":
    main()

