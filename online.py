import socket
import network

# Set up the Wi-Fi connection
ssid = "yourSSID"
password = "yourPassword"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connection
while not wlan.isconnected():
    pass

print("Connected to WiFi:", wlan.ifconfig())

# Start web server
def web_page():
    return """<!DOCTYPE HTML><html>
              <head><title>Pico Web Control</title></head>
              <body>
              <h1>Control Payloads</h1>
              <button onClick="window.location.href='/payload1'">Payload 1</button>
              <button onClick="window.location.href='/payload2'">Payload 2</button>
              <button onClick="window.location.href='/payload3'">Payload 3</button>
              <button onClick="window.location.href='/payload4'">Payload 4</button>
              </body></html>"""

def serve_web():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print("Web server is listening...")

    while True:
        conn, addr = s.accept()
        print("Connection from:", addr)
        request = conn.recv(1024)
        request = str(request)
        
        if "/payload1" in request:
            payload = "payload1.dd"
            runScript(payload)
        elif "/payload2" in request:
            payload = "payload2.dd"
            runScript(payload)
        elif "/payload3" in request:
            payload = "payload3.dd"
            runScript(payload)
        elif "/payload4" in request:
            payload = "payload4.dd"
            runScript(payload)
        
        response = web_page()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
        conn.close()
