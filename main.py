from flask import Flask, render_template
from PYTHON.routes import register_routes

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# רישום כל הנתבים
register_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

