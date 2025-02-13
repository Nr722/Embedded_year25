
import requests,time,random
db = "https://dnstest-2487b-default-rtdb.europe-west1.firebasedatabase.app/"
n = 0
while n < 10:
    path = "postlist.json"
    data = {"n":n, "time":time.time(), "rnd":random.random()}

    print("Writing {} to {}".format(data, path))
    response = requests.post(db+path, json=data)

    if response.ok:
        print("Created new node named {}".format(response.json()["name"]))
    else:
        raise ConnectionError("Could not write to database: {}".format(response.text))
    time.sleep(1)
    n += 1