import streamlit as st
import random

def ask_key_question():
    key_questions = [
        "So, what's next for you?",
        "So, where do you go from here?",
        "So, what do you think you will do?",
        "So, what are you going to do?"
    ]
    
    selected_question = random.choice(key_questions)
    st.write(selected_question)
    
    response = st.text_area("Your response:")
    
    if st.button("Continue to Plan"):
        return selected_question, response
    else:
        return None, None
