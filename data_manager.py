import streamlit as st
from datetime import datetime

class DataManager:
    @staticmethod
    def start_conversation(conversation_id):
        if 'conversations' not in st.session_state:
            st.session_state.conversations = {}
        st.session_state.conversations[conversation_id] = {
            'start_time': datetime.now(),
            'messages': []
        }

    @staticmethod
    def add_message(conversation_id, role, content):
        if conversation_id in st.session_state.conversations:
            st.session_state.conversations[conversation_id]['messages'].append({
                'role': role,
                'content': content,
                'timestamp': datetime.now()
            })

    @staticmethod
    def end_conversation(conversation_id):
        if conversation_id in st.session_state.conversations:
            st.session_state.conversations[conversation_id]['end_time'] = datetime.now()

    @staticmethod
    def get_conversation_history(conversation_id):
        if conversation_id in st.session_state.conversations:
            return st.session_state.conversations[conversation_id]['messages']
        return []
