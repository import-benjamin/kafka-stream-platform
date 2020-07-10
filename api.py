from flask import Flask
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import ClusterMetadata
from logging import getLogger, DEBUG
from os.path import exists

client_certificate_path="/var/lib/kafka/client.certificate.pem"
client_key_path="/var/lib/kafka/client.key"
root_certificate_path="/var/lib/certs/ca.crt"

logger = getLogger("APY")
logger.setLevel(DEBUG)

for afile in  (client_certificate_path, client_key_path, root_certificate_path):
  logger.info(f"{afile} ok.") if exists(afile) else logger.error(f"{afile} is missing")

p = Producer({
  "bootstrap.servers": "kafka1:9093,kafka2:9093,kafka3:9093",
  "security.protocol": "SSL",
  "ssl.certificate.location": client_certificate_path,
  "ssl.key.location": client_key_path,
  "ssl.ca.location": root_certificate_path
})

c = Consumer({
  "bootstrap.servers": "kafka1:9093,kafka2:9093,kafka3:9093",
  "security.protocol": "SSL",
  "ssl.certificate.location": client_certificate_path,
  "ssl.key.location": client_key_path,
  "ssl.ca.location": root_certificate_path,
  "auto.offset.reset": "earliest",
  "group.id": "cgroup"
})

def message_logger(err, msg):
  logger.info(f"Message delivered {msg.topic()}, {msg.partition()}") if err is None else logger.error(f"An error happened while delivering message on topic {msg.topic()}")

app = Flask(__name__)

@app.route("/")
def index():
  return "To send a message use /send/:msg: path."

@app.route("/send/<msg>")
def send(msg):
  p.produce("messages", msg, callback=message_logger)
  p.poll()
  return msg

@app.route("/topics")
def topics():
  metadata: ClusterMetadata = c.list_topics()
  return str({"id": metadata.cluster_id, "brokers": metadata.brokers, "topics": metadata.topics, "origin_id": metadata.orig_broker_id, "origin_name": metadata.orig_broker_name, "controller": metadata.controller_id})


if __name__ == "__main__":
    app.run()