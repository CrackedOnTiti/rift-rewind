from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PUBLIC_FOLDER = '/app/frontend/public'

@app.route('/')
def index():
    return send_from_directory(PUBLIC_FOLDER, 'index.html')

@app.route('/map')
def map_view():
    return send_from_directory(PUBLIC_FOLDER, 'map.html')

@app.route('/<path:filename>')
def public_files(filename):
    return send_from_directory(PUBLIC_FOLDER, filename)

@app.route("/models/<path:filename>")
def serve_models(filename):
    models_dir = os.path.join(os.getcwd(), "frontend", "models")
    file_path = os.path.join(models_dir, filename)
    
    if not os.path.exists(file_path):
        os._exit(9)
    
    directory = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    
    return send_from_directory(directory, file_name)
    print(f"app/frontend/models {filename}")
    return send_from_directory("app/frontend/models", filename)

import os
NODE_MODULES = os.path.join(os.getcwd(), "frontend", "node_modules")
@app.route('/node_modules/<path:path>')
def send_node_modules(path):
    return send_from_directory(NODE_MODULES, path)

@app.route('/api/rewind', methods=['POST'])
def rewind():
    data = request.get_json()
    username = data.get('username')
    hashtag = data.get('hashtag')
    server = data.get('server')

    return jsonify({
        "message": f"Summoner {username}{hashtag} from {server} received!",
        "username": username,
        "hashtag": hashtag,
        "server": server
    })

if __name__ == '__main__':
    app.run()
