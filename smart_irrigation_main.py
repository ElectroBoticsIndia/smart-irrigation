import time
import network
import urequests
from machine import Pin, PWM, ADC
import BlynkLib
 
soil_sensor = ADC(26)
motor = Pin(0, Pin.OUT)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("TP-Link","chithugan")
BLYNK_AUTH = 'xIxT7R3KkzGjpdabX0XuYgclfv6n07I_'

last_alert_time = time.time()
 
# connect the network       
wait = 10
while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    print('waiting for connection...')
    time.sleep(1)
 
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    ip=wlan.ifconfig()[0]
    print('IP: ', ip)
    
 
"Connection to Blynk"
# Initialize Blynk - FORCE UNSECURED CONNECTION
blynk = BlynkLib.Blynk(BLYNK_AUTH, port=80, insecure=True)
 
# Register virtual pin handler
@blynk.on("V0")
def v0_write_handler(value):
    if value[0] == "1":
        print("Motor - ON")
        motor.on()
    else:
        print("Motor - OFF")
        motor.off()
    
def read_moisture():
    data = soil_sensor.read_u16()
    percentage = 100 - (data / 65535)*100
    return round(percentage,2)
        
while True:
    blynk.run()
    
    try:
        moisture = read_moisture()
        print(f"Moisture:{moisture}%")
        blynk.virtual_write(3, moisture)
        
        if moisture < 30:
            print("Low moisture - Please water the plants")
            blynk.log_event("low_moisture_alert", "Please water the plants")
            
    except OSError:
        print("Sensor error")
        
    time.sleep(2)