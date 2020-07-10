from flask import Flask
from flask import jsonify
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient
from logging import getLogger
from logging import DEBUG
from os.path import exists

client_certificate_path="/var/lib/kafka/client.certificate.pem"
client_key_path="/var/lib/kafka/client.key"
root_certificate_path="/var/lib/certs/ca.crt"

logger = getLogger("APY")
logger.setLevel(DEBUG)

if not exists(client_certificate_path): logger.error("Certificate is missing.")
if not exists(client_key_path): logger.error("Key is missing.")
if not exists(root_certificate_path): logger.error("Root certificate is missing.")

p = Producer({
  'bootstrap.servers': 'kafka0:19093,kafka1:29093,kafka2:39093',
  'ssl.certificate.location': client_certificate_path,
  'ssl.key.location': client_key_path,
  'ssl.ca.location': root_certificate_path
  })
kadmin = AdminClient({
  'bootstrap.servers': 'kafka0:19093,kafka1:29093,kafka2:39093',
  'ssl.certificate.location':client_certificate_path,
  'ssl.key.location': client_key_path,
  'ssl.ca.location': root_certificate_path
  })
app = Flask(__name__)



def log_message(err, msg):
  if err is not None:
    logger.error(f"An error happened while sending message: {err}")
  else:
    logger.info(f"Message delivered: {msg}")

@app.route("/")
def index():
  return "To send a message use /send/:msg: path."

@app.route("/topics")
def topics():
  topics = kadmin.list_topics().topics
  return jsonify(topics)

@app.route("/send/<msg>")
def send(msg):
  p.produce("messages", msg.encode("utf-8"), callback=log_message)
  p.flush()
  return "ok"

if __name__ == "__main__":
    app.run()