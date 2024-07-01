import json
import csv

def export_chat_history(chat_history, format='json'):
    if format == 'json':
        return json.dumps(chat_history, indent=2)
    elif format == 'csv':
        output = []
        for message in chat_history:
            output.append([message['role'], message['content']])
        return output

def save_chat_history(chat_history, filename, format='json'):
    if format == 'json':
        with open(filename, 'w') as f:
            json.dump(chat_history, f, indent=2)
    elif format == 'csv':
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Role', 'Content'])
            for message in chat_history:
                writer.writerow([message['role'], message['content']])

def load_chat_history(filename, format='json'):
    if format == 'json':
        with open(filename, 'r') as f:
            return json.load(f)
    elif format == 'csv':
        chat_history = []
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                chat_history.append({'role': row[0], 'content': row[1]})
        return chat_history
