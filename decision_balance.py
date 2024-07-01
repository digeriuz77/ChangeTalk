import streamlit as st

def create_decision_balance():
    st.subheader("Decision Balance")

    # Importance Scale
    importance = st.slider("On a scale from 0 to 10, how important is this change to you?", 0, 10, 5)

    # Evocative questions based on importance
    if importance > 2:
        st.write(f"You rated the importance as {importance}. Why are you at {importance} and not {importance-2}?")
        reason_higher = st.text_input("Your response:")
    
    st.write("How much do you want to make this change?")
    desire = st.text_input("Your response (Desire):")

    # Pros and Cons
    st.subheader("Pros and Cons of Change")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Good things about not changing:")
        good_unchanged = st.text_area("List the good things about staying the same:")
        
        st.write("Not-so-good things about changing:")
        bad_change = st.text_area("List the drawbacks of making a change:")
    
    with col2:
        st.write("Not-so-good things about not changing:")
        bad_unchanged = st.text_area("List the drawbacks of staying the same:")
        
        st.write("Good things about changing:")
        good_change = st.text_area("List the benefits of making a change:")

    # Summary
    st.subheader("Summary")
    summary = f"""
    Importance: {importance}/10
    
    Key points:
    - Desire to change: {desire}
    
    Pros and Cons:
    - Good things about not changing: {good_unchanged}
    - Not-so-good things about not changing: {bad_unchanged}
    - Good things about changing: {good_change}
    - Not-so-good things about changing: {bad_change}
    """
    st.text_area("Decision Balance Summary:", summary, height=300)

    if st.button("Complete Decision Balance"):
        return summary, True
    else:
        return summary, False
