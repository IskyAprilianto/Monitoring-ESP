from flask import Flask, request, jsonify
from mongo import save_to_mongo, get_all_data  # Import fungsi dari mongo.py

app = Flask(__name__)

# **Endpoint untuk menerima data dari ESP32**
@app.route('/send-data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        print(f"Data diterima: {data}")
        save_to_mongo(data)  # Simpan ke MongoDB
        return jsonify({"message": "Data berhasil disimpan ke MongoDB Atlas"}), 200
    except Exception as e:
        print(f"Error menerima data: {e}")
        return jsonify({"message": "Terjadi kesalahan"}), 500

# **Endpoint untuk mengambil semua data dari MongoDB**
@app.route('/get-data', methods=['GET'])
def get_data():
    try:
        data = get_all_data()
        return jsonify({"data": data}), 200
    except Exception as e:
        print(f"Error mengambil data: {e}")
        return jsonify({"message": "Terjadi kesalahan"}), 500

# **Jalankan Flask Server**
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
