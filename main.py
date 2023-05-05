import rp2
import network
import machine
import urequests as requests
import time
import lowpower
from secrets import ssid, ssid_pw, goti_token

GPIO_PIN = 17
DELAY_MS = const(50)

door_bell = machine.Pin(GPIO_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
elapsed_time = time.ticks_ms()

wlan = network.WLAN(network.STA_IF)
rp2.country('FR')
wlan.active(True)


def connect():
    # Load login data from different file for safety reasons

    wlan.connect(ssid, ssid_pw)
    timeout = 10
    while timeout > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        timeout -= 1
        print('Waiting for connection...')
        time.sleep(1)


def handle_interrupt(Pin):
    print("interrupt")
    machine.enable_irq(False)
    global elapsed_time
    if time.ticks_diff(time.ticks_ms(), elapsed_time) > DELAY_MS:
        dring()
        machine.enable_irq(True)

    elapsed_time = time.ticks_ms()


def dring():
    print("dring")
    try:
        connect()
        requests.post('https://goti.rvier.fr/message?token={}'.format(goti_token), json={
            "message": "Sonette !",
            "priority": 10,
            "title": "Sonnette !"
        })
    except Exception as err:
        print(err)
    finally:
        machine.reset()  # horrible, but that the fastest way to reactivate all things require to deep sleep again


door_bell.irq(trigger=machine.Pin.IRQ_FALLING, handler=handle_interrupt)
time.sleep(5)

while True:
    print("Entering lightsleep mode")
    lowpower.dormant_until_pin(GPIO_PIN, edge=True, high=False)
    print("Exited lightsleep mode")
    time.sleep(5)
