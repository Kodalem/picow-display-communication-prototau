import network
import socket
import time
import rp2

# Setup the RP2040 wifi country mode
rp2.country('EE')

from machine import Pin, UART

# INPUT YOUR OWN SSID AND PASSWORD THROUGH A secret.py FILE FLASHED TO THE BOARD
from secret import ssid, password

## Set up the UART
uart = UART(1, 9600, parity=None, stop=1, bits=8, tx=Pin(8), rx=Pin(9))  # init with given baudrate

# Set up the wlan connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>%s</p>
    </body>
</html>
"""

### Set up the connection sequence
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

# Setup the socket address, WARNING: this will accept connections from anywhere
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

# Print the socket address and the wlan config
print('listening on', addr)
print(wlan.ifconfig())

# Setup and default the variables of the purge valve
purge_valve_status = False

# Listen for connections
while True:
    try:
        # Check if there is any data on the UART
        if uart.any():
            # Read the data from the UART
            data = (uart.read())
            # Print the data from the UART
            print(data)
            # Check if the valve state is ON or OFF
            if data == b'ON\r\n\n':
                print("Purge valve is open")
                purge_valve_status = True

            elif data == b'OFF\r\n\n':
                print("Purge valve is closed")
                purge_valve_status = False

            # Wait for the client to connect, and get and print the request
            cl, addr = s.accept()
            print('client connected from', addr)
            request = cl.recv(1024)
            print(request)
            request = str(request)

            # Check if the valve state is ON or OFF and set the stateis variable accordingly
            if purge_valve_status:
                print("Valve on")
                stateis = "Valve is ON"
            else:
                print("Valve off")
                stateis = "Valve is OFF"

            # Update the response in the html
            response = html % stateis

            # Send the response to the client and close the connection
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')
