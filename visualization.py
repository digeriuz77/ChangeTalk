import streamlit as st
import plotly.graph_objects as go

def visualize_change_talk(change_talk_scores):
    fig = go.Figure(data=go.Scatter(y=change_talk_scores, mode='lines+markers'))
    fig.update_layout(title='Change Talk Score Over Time',
                      xaxis_title='Conversation Turn',
                      yaxis_title='Change Talk Score')
    st.plotly_chart(fig)

def visualize_sentiment(sentiment_scores):
    fig = go.Figure(data=go.Scatter(y=sentiment_scores, mode='lines+markers'))
    fig.update_layout(title='Sentiment Over Time',
                      xaxis_title='Conversation Turn',
                      yaxis_title='Sentiment Score')
    st.plotly_chart(fig)

def visualize_entities(entities):
    if entities:
        entity_types = [ent['label'] for ent in entities]
        entity_counts = {label: entity_types.count(label) for label in set(entity_types)}
        
        fig = go.Figure(data=[go.Bar(x=list(entity_counts.keys()), y=list(entity_counts.values()))])
        fig.update_layout(title='Entities Mentioned',
                          xaxis_title='Entity Type',
                          yaxis_title='Count')
        st.plotly_chart(fig)
    else:
        st.write("No entities detected in the current input.")
