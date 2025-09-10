# Integrating Third-Party Systems with CAP Composer

## Why integrate?

Connecting your platform to **CAP Composer** lets you ingest authoritative weather warnings in the **Common Alerting
Protocol (CAP)** format in near-real time:

* **Timeliness:** Receive official alerts quickly.
* **Standards-based:** Consume structured CAP XML consistently.
* **Flexibility:** Choose between pull (RSS), push (Webhooks), or streaming (MQTT).

---

## Integration options

### 1) RSS XML Feed (Pull)

Best for simple periodic polling, caching, and low-ops environments.

**Feed URL:**

```
{{ feed_url }}
```

Each RSS `<item>` links to a CAP XML document. Poll responsibly (e.g., every 30–120 seconds) and deduplicate by
`identifier` and `sent`.

**Python example (poll & fetch CAP):**

```python
# pip install feedparser requests
import feedparser, requests
from xml.etree import ElementTree as ET

RSS_URL = "{{ feed_url }}"

feed = feedparser.parse(RSS_URL)
for entry in feed.entries:
    cap_url = entry.link
    r = requests.get(cap_url, timeout=15)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    cap = {"ns": "urn:oasis:names:tc:emergency:cap:1.2"}
    identifier = root.findtext("{%(ns)s}identifier" % cap)
    sent = root.findtext("{%(ns)s}sent" % cap)
    print("CAP:", identifier, sent, cap_url)
```

> **Tip:** Use HTTP caching (ETag / If-Modified-Since) and exponential backoff on transient errors.

---

### 2) Webhooks (Push)

Best for immediate delivery without polling.

**What you provide:**

* **Webhook URL** (HTTPS, POST)
* **Optional header:** `CAP-Webhook-Auth: <your-shared-secret>`

Your endpoint should accept raw **CAP XML** in the request body and return **2xx** responses upon successful receipt.

**Python example (Flask receiver):**

```python
# pip install flask
from flask import Flask, request, abort

app = Flask(__name__)
EXPECTED_SECRET = "YOUR_SHARED_SECRET"  # set this on both sides


@app.post("/cap-webhook")
def cap_webhook():
    # Optional shared-secret check
    secret = request.headers.get("CAP-Webhook-Auth")
    if EXPECTED_SECRET and secret != EXPECTED_SECRET:
        abort(401)
    
    cap_xml = request.data  # raw CAP XML (bytes)
    if not cap_xml:
        abort(400, "Empty body")
    
    # TODO: enqueue for processing; dedupe by CAP identifier + sent
    return ("OK", 200)


if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
```

> **Security:** Use HTTPS, validate the `CAP-Webhook-Auth` header, and make handlers idempotent.

---

### 3) MQTT (Pub/Sub Streaming)

Best for near real-time distribution to many consumers.

**What you provide:**

* **Broker Details** (host/port/username/password)
* **Topic** (e.g., `alerts/cap/<channel>`)

Consumers can subscribe to the same topic. Choose QoS based on your reliability needs (e.g., QoS 1 with consumer-side
deduplication).

**Python example (subscriber with paho-mqtt):**

{% verbatim %}

```python
# pip install paho-mqtt
import paho.mqtt.client as mqtt
from xml.etree import ElementTree as ET

BROKER_HOST = "mqtt.example.org"
BROKER_PORT = 1883
USERNAME = "user"
PASSWORD = "pass"
TOPIC = "alerts/cap/#"  # wildcard to receive all CAP alerts
QOS = 1


def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected:", reason_code)
    client.subscribe(TOPIC, qos=QOS)


def on_message(client, userdata, msg):
    try:
        root = ET.fromstring(msg.payload)
        cap = {"ns": "urn:oasis:names:tc:emergency:cap:1.2"}
        identifier = root.findtext("{%(ns)s}identifier" % cap)
        sent = root.findtext("{%(ns)s}sent" % cap)
        print("[%s] CAP %s sent %s" % (msg.topic, identifier, sent))
    except Exception as e:
        print("Invalid CAP XML:", e)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
client.loop_forever()
```

{% endverbatim %}

> **Reliability:** Prefer TLS (port 8883 where available) and unique credentials per consumer.

---

## Quick tests

* **RSS:**

```bash
curl -s {{ feed_url }} | head
```

* **Webhook (simulate CAP Composer → you):**

```bash
curl -X POST https://your.app/cap-webhook \
  -H "Content-Type: application/cap+xml" \
  -H "CAP-Webhook-Auth: YOUR_SHARED_SECRET" \
  --data-binary @sample-alert.xml
```

* **MQTT (subscribe):**

```bash
mosquitto_sub -h mqtt.example.org -p 1883 -u user -P pass \
  -t 'alerts/cap/#' -q 1
```

---

## What to submit

* **RSS** → No submission needed if public. Just use the feed URL.
* **Webhook** → Provide your **Webhook URL** and optional **CAP-Webhook-Auth** header value.
* **MQTT** → Provide **Broker** (host/port), **Topic**, and **Credentials** (username/password).

---

All transports deliver the same **CAP XML**. Choose the method that best matches your reliability, latency, and
operational needs.
