from flask import Flask, render_template, jsonify, send_from_directory
import csv
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ToHtml/<path:filename>')
def serve_tohtml_files(filename):
    """מגיש קבצים מתיקיית ToHtml"""
    tohtml_dir = os.path.join(app.root_path, 'ToHtml')
    return send_from_directory(tohtml_dir, filename)

@app.route('/api/addresses')
def get_addresses():
    """מחזיר את כל הכתובות עם קואורדינטות מהקובץ CSV"""
    addresses = []
    csv_path = os.path.join(app.root_path, 'database', 'found_addresses.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # בדיקה שיש קואורדינטות תקינות
                if row['קו רוחב'] and row['קו אורך']:
                    try:
                        lat = float(row['קו רוחב'])
                        lon = float(row['קו אורך'])
                        addresses.append({
                            'address': row['כתובת'],
                            'lat': lat,
                            'lon': lon,
                            'neighborhood': row['שכונה'],
                            'visited': row['ביקרנו'] == 'כן'
                        })
                    except ValueError:
                        # אם יש בעיה בהמרת הקואורדינטות, נדלג על הכתובת
                        continue
        
        return jsonify(addresses)
        
    except FileNotFoundError:
        return jsonify({'error': 'קובץ הכתובות לא נמצא'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

