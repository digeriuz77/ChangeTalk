import streamlit as st

def build_confidence():
    st.subheader("Building Confidence")
    
    # Confidence Decision Balance
    confidence = st.slider("On a scale from 0 to 10, how confident are you that, if you decided to make this change, you would be successful?", 0, 10, 5)
    
    st.write(f"You said {confidence}. Why {confidence}, and why not a lower number such as {max(0, confidence-2)} or {max(0, confidence-1)}? Why are you {'a little' if confidence <= 3 else 'somewhat' if confidence <= 7 else 'very'} confident you can make this change?")
    
    reasons_for_confidence = st.text_area("Reasons for your confidence:")
    
    st.write(f"And what would have to happen for your confidence to be higher, perhaps a {min(10, confidence+2)}?")
    
    ideas_for_higher_confidence = st.text_area("Ideas for becoming more confident:")
    
    st.write("Can I share with you some things other people find helpful when making this change?")
    
    if st.button("Yes, please share"):
        st.write("(Here, you would implement the ask-share-ask strategy)")
    
    summary = f"""
    Confidence level: {confidence}/10
    
    Reasons for confidence:
    {reasons_for_confidence}
    
    Ideas for increasing confidence:
    {ideas_for_higher_confidence}
    """
    
    st.text_area("Confidence Building Summary:", summary, height=200)
    
    if st.button("Complete Confidence Building"):
        return summary, confidence
    else:
        return None, confidence
