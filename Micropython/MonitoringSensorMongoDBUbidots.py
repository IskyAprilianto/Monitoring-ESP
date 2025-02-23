import network
import time
import json
import urequests  # Untuk HTTP request ke Flask
import dht
from machine import Pin, ADC

# **WiFi Configuration**
SSID = "Y"
PASSWORD = "Isky12345678"

# **Flask API Endpoint** (Ganti IP dengan Flask Server)
FLASK_SERVER = "http://192.168.76.222:5000/send-data"

# **Inisialisasi Sensor**
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
dht_sensor = dht.DHT11(Pin(4))  # Pastikan pin sesuai dengan wiring
pir_sensor = Pin(12, Pin.IN)

# **Inisialisasi Sensor Ultrasonik**
trig_pin = Pin(5, Pin.OUT)  # Pin untuk Trig
echo_pin = Pin(18, Pin.IN)   # Pin untuk Echo

# **Koneksi ke WiFi**
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Menghubungkan ke WiFi...")
        time.sleep(1)
    print("WiFi Connected:", wlan.ifconfig())

# **Membaca sensor DHT11 dan lainnya**
def get_sensor_data():
    try:
        time.sleep(2)  # Delay sebelum membaca sensor
        dht_sensor.measure()
        suhu = dht_sensor.temperature()
        kelembaban = dht_sensor.humidity()
    except OSError:
        print("Gagal membaca sensor DHT11!")
        suhu, kelembaban = None, None  # Beri nilai default jika gagal

    ldr_value = ldr.read()
    gerakan = pir_sensor.value()
    jarak = get_distance()  # Mengambil data jarak dari sensor ultrasonik

    return {
        "LDR": ldr_value,
        "Suhu": suhu if suhu is not None else 0,  # Jika None, beri nilai 0
        "Kelembaban": kelembaban if kelembaban is not None else 0,
        "Gerakan": gerakan,
        "Jarak": jarak  # Tambahkan data jarak
    }

# **Mengukur Jarak dengan Sensor Ultrasonik**
def get_distance():
    # Kirimkan pulsa trigger
    trig_pin.value(0)
    time.sleep_us(2)
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)

    # Mengukur durasi pulsa echo
    start_time = time.ticks_us()
    while echo_pin.value() == 0:
        start_time = time.ticks_us()  # Menunggu pulsa mulai
    while echo_pin.value() == 1:
        end_time = time.ticks_us()  # Menunggu pulsa selesai

    # Hitung durasi pulsa
    duration = time.ticks_diff(end_time, start_time)
    distance = (duration * 0.0343) / 2  # Kecepatan suara adalah 343 m/s
    return distance

# **Cek koneksi ke Flask sebelum mengirim data**
def check_flask_connection():
    try:
        response = urequests.get(FLASK_SERVER.replace("/send-data", "/"))
        print("Flask Server terhubung:", response.text)
        response.close()
        return True
    except Exception as e:
        print("Gagal terhubung ke Flask:", e)
        return False

# **Kirim data ke Flask Server**
def send_data_to_flask():
    if not check_flask_connection():
        print("Pastikan Flask Server berjalan sebelum mengirim data.")
        return

    while True:
        data = get_sensor_data()
        headers = {"Content-Type": "application/json"}
        try:
            response = urequests.post(FLASK_SERVER, json=data, headers=headers)
            print(f"Data terkirim ke Flask: {response.text}")
            response.close()
        except Exception as e:
            print(f"Gagal mengirim data ke Flask: {e}")

        time.sleep(5)  # Kirim data setiap 5 detik

# **Jalankan Program**
connect_wifi()
send_data_to_flask()
