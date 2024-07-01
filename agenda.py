import streamlit as st

def set_agenda():
    st.subheader("Setting the Agenda")
    
    st.write("Now there is a range of things that we could talk about today, but I am wondering, what would you most like to talk about with me today? What would make this conversation most worthwhile from your perspective?")
    
    user_topic = st.text_input("Your preferred topic (if any):")
    
    st.write("Here are some topics that other people often choose to discuss during these sessions:")
    
    topics = [
        "Physical Activity", "Healthy Eating", "Weight Management",
        "Nutrition", "Exercise Routine", "Meal Planning",
        "Portion Control", "Hydration", "Sleep and Exercise",
        "Stress and Diet", "Mindful Eating", "Balancing Diet and Exercise"
    ]
    
    selected_topics = []
    cols = st.columns(3)
    for i, topic in enumerate(topics):
        if cols[i % 3].button(topic, key=f"topic_{i}"):
            selected_topics.append(topic)
    
    st.write("You can select multiple topics if you'd like.")
    
    other_topic = st.text_input("Is there another topic you'd like to discuss that's not listed?")
    if other_topic:
        selected_topics.append(other_topic)
    
    if selected_topics or user_topic:
        st.write("You've selected the following topics:")
        for topic in selected_topics:
            st.write(f"- {topic}")
        if user_topic:
            st.write(f"- {user_topic}")
        
        st.write("Is there anything else you'd like to add? (in case there is something important that you're hesitant to bring up)")
        additional_topic = st.text_input("Additional topic (if any):")
        if additional_topic:
            selected_topics.append(additional_topic)
    
    if st.button("Confirm Agenda"):
        return selected_topics + ([user_topic] if user_topic else [])
    
    return None
