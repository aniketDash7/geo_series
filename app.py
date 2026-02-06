from flask import Flask, render_template, request, jsonify
import os
from processor import GeospatialProcessor

app = Flask(__name__)
processor = GeospatialProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/timeseries', methods=['POST'])
def get_timeseries():
    try:
        data = request.json
        lat = data.get('lat')
        lon = data.get('lon')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if lat is None or lon is None:
            return jsonify({'error': 'Missing coordinates'}), 400
            
        print(f"Fetching data for: {lat}, {lon} from {start_date} to {end_date}")
        result = processor.get_ndvi_data(lat, lon, start_date, end_date)
        
        if result is None:
            return jsonify({'error': 'No data found for this location'}), 404

        return jsonify({
            'status': 'success',
            'data': result['timeseries'],
            'frames': result['frames']
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Using 5002 to avoid conflict with existing app if running
    app.run(debug=True, port=5002)
