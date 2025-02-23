import network
import time
import json
import ubinascii
import dht
import urequests  
from machine import Pin, ADC
from umqtt.simple import MQTTClient
import utime 

# **WiFi Configuration**
SSID = "Y"
PASSWORD = "Isky12345678"

# **Ubidots Configuration**
TOKEN = "BBUS-MNHDM0Z7G8quIpkZ5cLn7oOpzpMnph"
MQTT_BROKER = "industrial.api.ubidots.com"
DEVICE_LABEL = "sensor_esp"
VARIABLE_LDR = "LDR"
VARIABLE_SUHU = "Suhu"
VARIABLE_KELEMBABAN = "Kelembaban"
VARIABLE_JARAK = "Jarak"
VARIABLE_PIR = "Gerakan"

# **Flask API Endpoint**
FLASK_SERVER = "http://192.168.76.222:5000/send-data"  

# **Inisialisasi Sensor**
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
dht_sensor = dht.DHT11(Pin(4))
pir_sensor = Pin(12, Pin.IN)

# **Inisialisasi Sensor Ultrasonik**
trig_pin = Pin(5, Pin.OUT)
echo_pin = Pin(18, Pin.IN)

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
        time.sleep(2)  
        dht_sensor.measure()
        suhu = dht_sensor.temperature()
        kelembaban = dht_sensor.humidity()
    except OSError:
        print("Gagal membaca sensor DHT11!")
        suhu, kelembaban = None, None 

    ldr_value = ldr.read()
    gerakan = pir_sensor.value()
    jarak = get_distance()  

    # Menambahkan timestamp dalam format tanggal dan jam
    timestamp = utime.localtime()  
    timestamp_str = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(
        timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5]
    )

    # Menyusun data dengan timestamp di bawah
    return {
        "LDR": ldr_value,
        "Suhu": suhu if suhu is not None else 0,  
        "Kelembaban": kelembaban if kelembaban is not None else 0,
        "Gerakan": gerakan,
        "Jarak": jarak,  
        "Timestamp": timestamp_str 
    }

# **Mengukur Jarak dengan Sensor Ultrasonik**
def get_distance():
    
    trig_pin.value(0)
    time.sleep_us(2)
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)

    # Mengukur durasi
    start_time = time.ticks_us()
    while echo_pin.value() == 0:
        start_time = time.ticks_us()  
    while echo_pin.value() == 1:
        end_time = time.ticks_us()  

    # Hitung durasi
    duration = time.ticks_diff(end_time, start_time)
    distance = (duration * 0.0343) / 2 
    return distance

# **Fungsi untuk mengirim data ke Ubidots via MQTT**
def send_data_to_ubidots():
    client_id = ubinascii.hexlify(network.WLAN().config('mac')).decode()
    client = MQTTClient(client_id, MQTT_BROKER, user=TOKEN, password="", port=1883)
    client.connect()

    while True:
        # Mengambil data dari sensor
        data = get_sensor_data()

        # Format payload untuk mengirim data ke Ubidots
        payload = json.dumps({
            VARIABLE_LDR: data["LDR"],
            VARIABLE_SUHU: data["Suhu"],
            VARIABLE_KELEMBABAN: data["Kelembaban"],
            VARIABLE_JARAK: data["Jarak"],
            VARIABLE_PIR: data["Gerakan"],
            "Timestamp": data["Timestamp"] 
        })

        # Mengirim data ke Ubidots
        topic = "/v1.6/devices/" + DEVICE_LABEL
        client.publish(topic, payload)

        # Menampilkan output yang lebih rapi di terminal
        print("\nData Dikirim ke Ubidots")
        print(f"LDR        : {data['LDR']} (ADC Value)")
        print(f"Suhu       : {data['Suhu']} °C")
        print(f"Kelembaban : {data['Kelembaban']} %")
        print(f"Jarak      : {data['Jarak']} cm")
        print(f"Gerakan    : {data['Gerakan']} kali")
        print(f"Timestamp  : {data['Timestamp']} (Tanggal dan Jam)\n")

        time.sleep(5)

# **Fungsi untuk mengirim data ke Flask Server**
def send_data_to_flask():
    while True:
        data = get_sensor_data()
        headers = {"Content-Type": "application/json"}
        try:
            response = urequests.post(FLASK_SERVER, json=data, headers=headers)
            print(f"Data terkirim ke Flask: {response.text}")
            response.close()
        except Exception as e:
            print(f"Gagal mengirim data ke Flask: {e}")

        time.sleep(20) 

# **Jalankan Program**
connect_wifi()

# Jalankan kedua pengiriman data (ke Ubidots dan Flask)
import _thread
_thread.start_new_thread(send_data_to_ubidots, ())
send_data_to_flask()
