import streamlit as st
from azure.storage.blob import BlobServiceClient
from io import StringIO
import json

def upload_chat_log_to_azure(chat_history, conversation_id):
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={st.secrets.azure.storage_account_name};AccountKey={st.secrets.azure.storage_account_key}"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=st.secrets.azure.container_name, blob=f"chat_log_{conversation_id}.json")
    
    # Convert chat history to JSON string
    chat_json = json.dumps(chat_history)
    
    # Upload JSON string as blob
    blob_client.upload_blob(chat_json, overwrite=True)

# In your main app
if st.button("End Conversation and Upload"):
    upload_chat_log_to_azure(st.session_state.chat_history, st.session_state.conversation_id)
    st.success("Chat log uploaded to Azure Storage!")
