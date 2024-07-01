import streamlit as st

def summarize_conversation(chat_history):
    st.subheader("Conversation Summary")
    
    st.write("Let me see if I understand so far...")
    
    # Extract change statements
    change_statements = [msg["content"] for msg in chat_history if msg["role"] == "user" and any(keyword in msg["content"].lower() for keyword in ["change", "improve", "start", "stop", "different"])]
    
    # Summarize change statements
    if change_statements:
        st.write("You've mentioned some thoughts about change:")
        for statement in change_statements:
            st.write(f"- {statement}")
    
    # Summarize ambivalence
    pros = [msg["content"] for msg in chat_history if msg["role"] == "user" and "good things about changing" in msg["content"].lower()]
    cons = [msg["content"] for msg in chat_history if msg["role"] == "user" and "not-so-good things about changing" in msg["content"].lower()]
    
    if pros and cons:
        st.write("On the one hand, you've mentioned some benefits of changing:")
        for pro in pros:
            st.write(f"- {pro}")
        st.write("On the other hand, you've also mentioned some challenges:")
        for con in cons:
            st.write(f"- {con}")
    
    # Final summary
    summary = st.text_area("Overall summary:", height=200)
    
    st.write("Is there anything you want to add or correct?")
    additions = st.text_area("Additional comments or corrections:")
    
    if st.button("Complete Summary"):
        return summary, additions
    else:
        return None, None
