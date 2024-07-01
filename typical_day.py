import streamlit as st

def describe_typical_day(selected_topics):
    st.subheader("Describing a Typical Day")
    
    topic = ", ".join(selected_topics)
    st.write(f"To get started, could you help me better understand how {topic} fits into your life right now? Please describe a typical day for me, starting from when you wake up, and taking me through the day letting me know how {topic} fits into your life. Would that be okay?")
    
    typical_day = st.text_area("Describe your typical day:", height=300)
    
    if typical_day:
        st.write("Is the weekend any different?")
        weekend_difference = st.text_area("Describe any differences on weekends:", height=150)
        
        if st.button("Continue"):
            return typical_day, weekend_difference
    
    return None, None
