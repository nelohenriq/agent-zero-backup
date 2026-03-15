"""Simple Flask UI for the shared knowledge base.
- Serves a static index.html from the `static` folder.
- Provides the knowledge‑graph JSON at `/graph`.
"""

from flask import Flask, send_from_directory, abort
import pathlib

app = Flask(__name__, static_folder='static')

# ----- Home page -----------------------------------------------------
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# ----- Graph JSON ----------------------------------------------------
@app.route('/graph')
def graph():
    # The graph file lives next to this script (same directory)
    graph_path = pathlib.Path(__file__).parent / 'graph.json'
    if not graph_path.is_file():
        abort(404, description='graph.json not found')
    return send_from_directory(str(graph_path.parent), graph_path.name)

# ----- Run -----------------------------------------------------------
if __name__ == '__main__':
    # Listen on all interfaces so it can be reached from the host.
    app.run(host='0.0.0.0', port=5560, debug=False)
