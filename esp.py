import network
import time
import ubinascii
import dht
from machine import Pin
from umqtt.simple import MQTTClient

# WiFi Configuration
SSID = "Dharma 4"  
PASSWORD = "0818881210"  

# Ubidots Configuration
TOKEN = "BBUS-X22dYuktZNwot2UyXDlW0br7H6FOIF"  
MQTT_BROKER = "industrial.api.ubidots.com"
DEVICE_LABEL = "sensor_esp"
VARIABLE_SUHU = "Suhu"
VARIABLE_KELEMBABAN = "Kelembaban"
VARIABLE_JARAK = "Jarak"

# Inisialisasi Sensor DHT11
dht_sensor = dht.DHT11(Pin(4))  

# Inisialisasi Sensor Ultrasonik
TRIG = Pin(18, Pin.OUT)  
ECHO = Pin(21, Pin.IN)  

# Fungsi untuk koneksi ke WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Menghubungkan ke WiFi...")
        time.sleep(1)
    print("WiFi Connected:", wlan.ifconfig())

# Fungsi untuk membaca data dari DHT11
def get_dht_data():
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temperature, humidity
    except OSError as e:
        print("Gagal membaca sensor DHT11:", e)
        return None, None

# Fungsi untuk membaca data dari Ultrasonik
def get_distance():
    TRIG.off()
    time.sleep_us(2)
    TRIG.on()
    time.sleep_us(10)
    TRIG.off()
    
    while ECHO.value() == 0:
        start = time.ticks_us()
    while ECHO.value() == 1:
        end = time.ticks_us()
    
    duration = end - start
    distance = (duration * 0.0343) / 2  
    return round(distance, 2)

# Fungsi untuk mengirim data ke Ubidots
def send_data():
    client_id = ubinascii.hexlify(network.WLAN().config('mac')).decode()
    client = MQTTClient(client_id, MQTT_BROKER, user=TOKEN, password="", port=1883)
    client.connect()
    
    while True:
        suhu, kelembaban = get_dht_data()
        jarak = get_distance()
        
        if suhu is not None and kelembaban is not None and jarak is not None:
            payload = '{"' + VARIABLE_SUHU + '": ' + str(suhu) + ', "' + VARIABLE_KELEMBABAN + '": ' + str(kelembaban) + ', "' + VARIABLE_JARAK + '": ' + str(jarak) + '}'
            topic = "/v1.6/devices/" + DEVICE_LABEL
            client.publish(topic, payload)
            print("Data Sent:", payload)
        else:
            print("Sensor Error: Data tidak terkirim")

        time.sleep(5) 

# Jalankan program
connect_wifi()
send_data()
