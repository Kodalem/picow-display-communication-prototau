### Display Setup
import gc
import time
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB565

display = PicoGraphics(DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB565, rotate=0)
# set up constants for drawing
WIDTH, HEIGHT = display.get_bounds()
BLACK = display.create_pen(0, 0, 0)


def hsv_to_rgb(h, s, v):
    # From CPython Lib/colorsys.py
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q


h = 0


# sets up a handy function we can call to clear the screen
def clear():
    display.set_pen(BLACK)
    display.clear()
    display.update()


### Network Setup
import network
import time
from secret import ssid, password
import socket

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
wlan.ifconfig(('192.168.1.227', '255.255.255.0', '192.168.1.1', '192.168.1.1'))
while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    time.sleep(1)

# Should be connected and have an IP address
wlan.status()  # 3 == success
wlan.ifconfig()
print(wlan.ifconfig())

while True:
    ## Socket
    ai = socket.getaddrinfo("valve-control.pico", 80)  # Address of Web Server
    addr = ai[0][-1]

    # Create a socket and make a HTTP request
    s = socket.socket()  # Open socket
    s.connect(addr)
    s.send(b"GET Data")  # Send request
    ss = str(s.recv(512))  # Store reply
    # Print what we received
    print(ss)

    ### Get the substring from the packet
    substring_location = ss.find("Valve is")
    valve_status_string = ss[substring_location:(substring_location + 12)]

    ## Display packet
    clear()
    display.set_pen(BLACK)
    CYAN = display.create_pen(100, 200, 200)  # Create pen with converted HSV value
    display.set_pen(CYAN)
    display.set_font("bitmap8")
    display.text(valve_status_string, 0, 0, WIDTH, 3)
    display.update()

    print()
    s.close()  # Close socket
    time.sleep(0.2)  # wait

