from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Koneksi MongoDB
uri = "mongodb+srv://StarlithMonitoring:Starlith136@monitoringesp32starlith.bmcwx.mongodb.net/?retryWrites=true&w=majority&appName=MonitoringESP32Starlith"

# **Koneksi ke MongoDB**
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["MonitoringESP32Starlith"]  
collection = db["sensor_data"]  

# **Simpan data ke MongoDB**
def save_to_mongo(data):
    try:
        collection.insert_one(data)
        print("Data berhasil disimpan ke MongoDB Atlas")
    except Exception as e:
        print(f"Error menyimpan data ke MongoDB: {e}")

# **Ambil semua data dari MongoDB**
def get_all_data():
    try:
        data = list(collection.find({}, {"_id": 0}))  
        return data
    except Exception as e:
        print(f"Error mengambil data dari MongoDB: {e}")
        return []
