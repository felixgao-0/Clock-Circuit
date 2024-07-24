# A custom written api to fetch the weather easily

#import urequests


url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 52.52,
	"longitude": 13.41,
	"current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
	"timezone": "America/New_York",
	"forecast_days": 1
}


def http_get(url):
    import socket
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()


weather_str = None  # <= TODO: Weather info goes there

def get_weather():
  return weather_str

def fetch_weather():
  http_get(url)
