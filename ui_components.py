import streamlit as st

def display_progress_bar(current_step, total_steps):
    progress = current_step / total_steps
    st.progress(progress)
    st.write(f"Step {current_step} of {total_steps}")

def display_chat_history(chat_history):
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def display_change_talk_score(change_talk_scores):
    if change_talk_scores:
        st.line_chart(change_talk_scores)
        st.write(f"Current Change Talk Score: {change_talk_scores[-1]:.2f}")

def display_confidence_slider():
    confidence = st.slider("How confident are you in making this change?", 0, 100, 50)
    return confidence

def display_download_button(plan_summary):
    if plan_summary:
        st.download_button(
            label="Download Your Change Plan",
            data=plan_summary,
            file_name="change_plan.txt",
            mime="text/plain"
        )
