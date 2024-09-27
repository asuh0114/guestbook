import json
from flask import Flask, request, jsonify, render_template, Response
from uuid import uuid4
from typing import List, Dict, Any

app = Flask(__name__)

GUESTBOOK_FILE = 'guestbook_entries.json'

def load_entries() -> List[Dict[str, Any]]:
    try:
        with open(GUESTBOOK_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_entries(entries: List[Dict[str, Any]]) -> None:
    with open(GUESTBOOK_FILE, 'w', encoding='utf-8') as file:
        json.dump(entries, file, ensure_ascii=False, indent=4)

guestbook_entries: List[Dict[str, Any]] = load_entries()

@app.route('/')
def index() -> str:
    return render_template('index.html')

@app.route('/guestbook', methods=['POST'])
def add_entry() -> Response:
    entry = request.json.get('entry')
    if entry:
        ip_address = request.remote_addr
        entry_id = str(uuid4())
        guestbook_entries.append({'id': entry_id, 'content': entry, 'ip': ip_address})
        save_entries(guestbook_entries)
        return jsonify({'message': 'Entry added successfully!'}), 201
    return jsonify({'message': 'Invalid entry!'}), 400

@app.route('/guestbook', methods=['GET'])
def get_entries() -> Response:
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 5))
    start = (page - 1) * limit
    end = start + limit
    paginated_entries = guestbook_entries[start:end]
    return jsonify({'entries': paginated_entries, 'total': len(guestbook_entries)}), 200

@app.route('/guestbook/<entry_id>', methods=['DELETE'])
def delete_entry(entry_id: str) -> Response:
    global guestbook_entries
    guestbook_entries = [entry for entry in guestbook_entries if entry.get('id') != entry_id]
    save_entries(guestbook_entries)
    return jsonify({'message': 'Entry deleted successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True)