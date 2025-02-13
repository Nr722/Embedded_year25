import requests, time
db = "https://dnstest-2487b-default-rtdb.europe-west1.firebasedatabase.app/"
path = "timeseries.json"
query = "?orderBy=\"rnd\"&startAt=0.5&endAt=1.0"
response = requests.get(db+path+query)
if response.ok:
    print(response.json())
else:
    raise ConnectionError("Could not access database: {}".format(response.text))

query = "?orderBy=\"$key\"&startAt=\"{}\"&endAt=\"{}\"".format(int(time.time()-3600), int(time.time()))
