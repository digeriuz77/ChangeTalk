import json
import csv
import sqlite3
from datetime import datetime
import uuid

class DataManager:
    def __init__(self, db_path='chatbot.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')

    def start_conversation(self, user_id):
        conversation_id = str(uuid.uuid4())
        with self.conn:
            self.conn.execute('INSERT INTO conversations (id, user_id, start_time) VALUES (?, ?, ?)',
                              (conversation_id, user_id, datetime.now()))
        return conversation_id

    def add_message(self, conversation_id, role, content):
        message_id = str(uuid.uuid4())
        with self.conn:
            self.conn.execute('INSERT INTO messages (id, conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?, ?)',
                              (message_id, conversation_id, role, content, datetime.now()))

    def end_conversation(self, conversation_id):
        with self.conn:
            self.conn.execute('UPDATE conversations SET end_time = ? WHERE id = ?',
                              (datetime.now(), conversation_id))

    def get_conversation_history(self, conversation_id):
        cur = self.conn.cursor()
        cur.execute('SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp', (conversation_id,))
        return [{'role': role, 'content': content} for role, content in cur.fetchall()]

    def export_conversation(self, conversation_id, format='json'):
        history = self.get_conversation_history(conversation_id)
        if format == 'json':
            return json.dumps(history, indent=2)
        elif format == 'csv':
            output = []
            for message in history:
                output.append([message['role'], message['content']])
            return output

# Usage in app.py
data_manager = DataManager()
conversation_id = data_manager.start_conversation(user_id)

# In handle_open_conversation
data_manager.add_message(conversation_id, "user", user_input)
data_manager.add_message(conversation_id, "assistant", assistant_response)

# At the end of the conversation
data_manager.end_conversation(conversation_id)
