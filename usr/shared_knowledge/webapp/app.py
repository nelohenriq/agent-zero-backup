from flask import Flask, send_from_directory, jsonify, render_template
import os

app = Flask(__name__, static_folder='static')
BASE = '/a0/usr/shared_knowledge'
GRAPH_PATH = os.path.join(BASE, 'graph.json')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/graph')
def graph():
    if not os.path.exists(GRAPH_PATH):
        return jsonify({'error': 'graph not generated'}), 404
    return send_from_directory(BASE, 'graph.json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5560)
